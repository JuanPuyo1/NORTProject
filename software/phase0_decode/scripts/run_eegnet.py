"""Phase 0 Tier C: subject-specific EEGNet (Lawhern et al. 2018).

Compact CNN on cropped EEG epochs. Leave-session-out within each subject.
Strong dropout + early stopping for small-N calibration.
"""

from __future__ import annotations

import argparse
import json
import sys
import warnings
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import mne
import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
)
from sklearn.model_selection import train_test_split
from sklearn.utils import check_random_state
from torch.utils.data import DataLoader, TensorDataset

CLASS_NAMES = {0: "arriba", 1: "abajo", 2: "derecha", 3: "izquierda"}


@dataclass
class RunConfig:
    data_root: str
    subjects: list
    condition: str
    task: str
    tmin: float
    tmax: float
    fmin: float
    fmax: float
    F1: int
    D: int
    dropout: float
    kern_length: int
    max_epochs: int
    patience: int
    batch_size: int
    lr: float
    weight_decay: float
    val_fraction: float
    n_permutations: int
    seed: int
    device: str
    run_id: str


class EEGNet(nn.Module):
    """EEGNet-8,2 style network (channels × time input)."""

    def __init__(
        self,
        n_channels: int,
        n_times: int,
        n_classes: int,
        F1: int = 8,
        D: int = 2,
        dropout: float = 0.5,
        kern_length: int = 64,
    ):
        super().__init__()
        F2 = F1 * D
        self.temporal = nn.Conv2d(
            1, F1, (1, kern_length), padding=(0, kern_length // 2), bias=False
        )
        self.bn1 = nn.BatchNorm2d(F1)
        self.spatial = nn.Conv2d(F1, F1 * D, (n_channels, 1), groups=F1, bias=False)
        self.bn2 = nn.BatchNorm2d(F1 * D)
        self.elu = nn.ELU()
        self.pool1 = nn.AvgPool2d((1, 4))
        self.drop1 = nn.Dropout(dropout)
        self.sep_depth = nn.Conv2d(
            F1 * D, F1 * D, (1, 16), padding=(0, 8), groups=F1 * D, bias=False
        )
        self.sep_point = nn.Conv2d(F1 * D, F2, (1, 1), bias=False)
        self.bn3 = nn.BatchNorm2d(F2)
        self.pool2 = nn.AvgPool2d((1, 8))
        self.drop2 = nn.Dropout(dropout)
        with torch.no_grad():
            n_features = self._features(torch.zeros(1, 1, n_channels, n_times)).numel()
        self.classifier = nn.Linear(n_features, n_classes)

    @staticmethod
    def _crop_time(x, target_len: int):
        if x.shape[-1] == target_len:
            return x
        if x.shape[-1] > target_len:
            start = (x.shape[-1] - target_len) // 2
            return x[..., start : start + target_len]
        return nn.functional.pad(x, (0, target_len - x.shape[-1]))

    def _features(self, x):
        t0 = x.shape[-1]
        x = self._crop_time(self.temporal(x), t0)
        x = self.bn1(x)
        x = self.elu(self.bn2(self.spatial(x)))
        x = self.drop1(self.pool1(x))
        t1 = x.shape[-1]
        x = self._crop_time(self.sep_depth(x), t1)
        x = self.elu(self.bn3(self.sep_point(x)))
        x = self.drop2(self.pool2(x))
        return x

    def forward(self, x):
        # x: (B, C, T) -> (B, 1, C, T)
        if x.dim() == 3:
            x = x.unsqueeze(1)
        return self.classifier(torch.flatten(self._features(x), 1))


def load_subject_sessions(data_root: Path, subject: int):
    sub = f"sub-{subject:02d}"
    X_list, y_list, meta = [], [], []
    sfreq = times = None
    for session in (1, 2, 3):
        ses = f"ses-{session:02d}"
        eeg_path = data_root / "derivatives" / sub / ses / f"{sub}_{ses}_eeg-epo.fif"
        events_path = data_root / "derivatives" / sub / ses / f"{sub}_{ses}_events.dat"
        epochs = mne.read_epochs(eeg_path, preload=True, verbose="ERROR")
        events = np.load(events_path, allow_pickle=True)
        X_list.append(epochs.get_data(copy=True))
        y_list.append(events)
        meta.extend([(subject, session)] * len(events))
        sfreq = float(epochs.info["sfreq"])
        times = epochs.times.copy()
    return (
        np.concatenate(X_list, axis=0),
        np.concatenate(y_list, axis=0),
        np.asarray(meta, dtype=int),
        sfreq,
        times,
    )


def filter_trials(X, Y, meta, condition: str, task: str):
    cond_map = {"pronounced": 0, "inner": 1, "visualized": 2}
    mask = Y[:, 2] == cond_map[condition]
    if task == "binary_up_down":
        mask &= np.isin(Y[:, 1], [0, 1])
        labels = Y[mask, 1].astype(int)
        label_names = [CLASS_NAMES[0], CLASS_NAMES[1]]
    else:
        labels = Y[mask, 1].astype(int)
        label_names = [CLASS_NAMES[i] for i in range(4)]
    return X[mask], labels, meta[mask], label_names


def preprocess_epochs(X, sfreq, times, tmin, tmax, fmin, fmax):
    start = int(np.searchsorted(times, tmin))
    end = int(np.searchsorted(times, tmax))
    segment = X[:, :, start:end]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        filtered = mne.filter.filter_data(
            segment, sfreq=sfreq, l_freq=fmin, h_freq=fmax, verbose="ERROR"
        )
    return filtered.astype(np.float32)


def standardize_channels(X_train, X_other):
    # Per-channel z-score using train trials only
    mean = X_train.mean(axis=(0, 2), keepdims=True)
    std = X_train.std(axis=(0, 2), keepdims=True) + 1e-6
    return (X_train - mean) / std, (X_other - mean) / std, mean, std


def class_weights(y: np.ndarray, n_classes: int) -> torch.Tensor:
    counts = np.bincount(y, minlength=n_classes).astype(np.float64)
    counts[counts == 0] = 1.0
    w = counts.sum() / (n_classes * counts)
    return torch.tensor(w, dtype=torch.float32)


def train_eegnet(
    X_train: np.ndarray,
    y_train: np.ndarray,
    cfg: RunConfig,
    n_classes: int,
    rng,
):
    n_channels, n_times = X_train.shape[1], X_train.shape[2]
    device = torch.device(cfg.device)

    # Hold out validation from train for early stopping
    if cfg.val_fraction > 0 and len(y_train) >= 20:
        X_tr, X_val, y_tr, y_val = train_test_split(
            X_train,
            y_train,
            test_size=cfg.val_fraction,
            random_state=cfg.seed,
            stratify=y_train if len(np.unique(y_train)) > 1 else None,
        )
    else:
        X_tr, y_tr = X_train, y_train
        X_val = y_val = None

    X_tr_n, X_rest_n, mean, std = standardize_channels(
        X_tr, X_val if X_val is not None else X_tr[:1]
    )
    if X_val is not None:
        X_val_n = (X_val - mean) / std
    else:
        X_val_n = None

    model = EEGNet(
        n_channels=n_channels,
        n_times=n_times,
        n_classes=n_classes,
        F1=cfg.F1,
        D=cfg.D,
        dropout=cfg.dropout,
        kern_length=cfg.kern_length,
    ).to(device)

    weights = class_weights(y_tr, n_classes).to(device)
    criterion = nn.CrossEntropyLoss(weight=weights)
    optim = torch.optim.Adam(
        model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay
    )

    ds = TensorDataset(
        torch.from_numpy(X_tr_n),
        torch.from_numpy(y_tr.astype(np.int64)),
    )
    bs = min(cfg.batch_size, len(ds))
    loader = DataLoader(
        ds,
        batch_size=bs,
        shuffle=True,
        drop_last=len(ds) > bs,
    )

    best_state = None
    best_val = float("inf")
    best_epoch = 0
    patience_left = cfg.patience
    history = {"train_loss": [], "val_loss": []}

    for epoch in range(cfg.max_epochs):
        model.train()
        total_loss, n_seen = 0.0, 0
        for xb, yb in loader:
            xb = xb.to(device)
            yb = yb.to(device)
            optim.zero_grad()
            logits = model(xb)
            loss = criterion(logits, yb)
            loss.backward()
            optim.step()
            total_loss += float(loss.item()) * len(yb)
            n_seen += len(yb)
        train_loss = total_loss / max(n_seen, 1)
        history["train_loss"].append(train_loss)

        if X_val_n is not None:
            model.eval()
            with torch.no_grad():
                logits = model(torch.from_numpy(X_val_n).to(device))
                val_loss = float(
                    criterion(
                        logits, torch.from_numpy(y_val.astype(np.int64)).to(device)
                    ).item()
                )
            history["val_loss"].append(val_loss)
            monitor = val_loss
        else:
            monitor = train_loss
            history["val_loss"].append(None)

        if monitor < best_val - 1e-4:
            best_val = monitor
            best_epoch = epoch + 1
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
            patience_left = cfg.patience
        else:
            patience_left -= 1
            if patience_left <= 0:
                break

    if best_state is not None:
        model.load_state_dict(best_state)

    return model, mean, std, {
        "best_epoch": best_epoch,
        "epochs_run": len(history["train_loss"]),
        "best_monitor_loss": float(best_val),
        "history": history,
    }


def predict_eegnet(model, X, mean, std, device):
    Xn = (X - mean) / std
    model.eval()
    with torch.no_grad():
        logits = model(torch.from_numpy(Xn.astype(np.float32)).to(device))
        pred = logits.argmax(dim=1).cpu().numpy()
    return pred


def leave_session_out_subject(X, y, meta, cfg: RunConfig, quiet: bool = False):
    n_classes = len(np.unique(y))
    sessions = sorted(np.unique(meta[:, 1]).tolist())
    folds = []
    y_true_all, y_pred_all = [], []
    rng = check_random_state(cfg.seed)

    for test_ses in sessions:
        test_mask = meta[:, 1] == test_ses
        train_mask = ~test_mask
        if len(np.unique(y[train_mask])) < 2 or test_mask.sum() == 0:
            continue
        torch.manual_seed(cfg.seed + int(test_ses) * 17)
        np.random.seed(cfg.seed + int(test_ses) * 17)
        model, mean, std, train_info = train_eegnet(
            X[train_mask], y[train_mask], cfg, n_classes, rng
        )
        pred = predict_eegnet(model, X[test_mask], mean, std, torch.device(cfg.device))
        yt = y[test_mask]
        folds.append(
            {
                "test_session": int(test_ses),
                "n_train": int(train_mask.sum()),
                "n_test": int(test_mask.sum()),
                "accuracy": float(accuracy_score(yt, pred)),
                "balanced_accuracy": float(balanced_accuracy_score(yt, pred)),
                "macro_f1": float(f1_score(yt, pred, average="macro")),
                "confusion_matrix": confusion_matrix(yt, pred).tolist(),
                "train_info": {
                    "best_epoch": train_info["best_epoch"],
                    "epochs_run": train_info["epochs_run"],
                    "best_monitor_loss": train_info["best_monitor_loss"],
                },
            }
        )
        y_true_all.append(yt)
        y_pred_all.append(pred)
        if not quiet:
            print(
                f"[eegnet]   fold test_ses={test_ses} "
                f"bal_acc={folds[-1]['balanced_accuracy']:.3f} "
                f"epochs={train_info['epochs_run']}",
                flush=True,
            )
        # free GPU/CPU graph
        del model
        if cfg.device.startswith("cuda"):
            torch.cuda.empty_cache()

    y_true = np.concatenate(y_true_all)
    y_pred = np.concatenate(y_pred_all)
    overall = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro")),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
        "n_trials": int(len(y_true)),
    }
    return folds, overall, y_true, y_pred


def permutation_subject(X, y, meta, cfg: RunConfig):
    if cfg.n_permutations <= 0:
        return None
    rng = check_random_state(cfg.seed)
    scores = []
    for i in range(cfg.n_permutations):
        y_perm = y.copy()
        for ses in np.unique(meta[:, 1]):
            idx = np.where(meta[:, 1] == ses)[0]
            y_perm[idx] = rng.permutation(y_perm[idx])
        _, overall, _, _ = leave_session_out_subject(X, y_perm, meta, cfg, quiet=True)
        scores.append(overall["balanced_accuracy"])
        print(
            f"[eegnet]   perm {i + 1}/{cfg.n_permutations} bal_acc={overall['balanced_accuracy']:.3f}",
            flush=True,
        )
    return {
        "n_permutations": cfg.n_permutations,
        "mean_balanced_accuracy": float(np.mean(scores)),
        "std_balanced_accuracy": float(np.std(scores)),
        "p95_balanced_accuracy": float(np.percentile(scores, 95)),
        "scores": [float(s) for s in scores],
    }


def main():
    mne.set_log_level("ERROR")
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-root",
        default=str(Path(__file__).resolve().parents[3] / "projects" / "ds003626"),
    )
    parser.add_argument("--subjects", default="1,2,3,4,5,6,7,8")
    parser.add_argument("--condition", default="inner")
    parser.add_argument("--task", default="binary_up_down", choices=["binary_up_down", "4class"])
    parser.add_argument("--tmin", type=float, default=1.5)
    parser.add_argument("--tmax", type=float, default=3.5)
    parser.add_argument("--fmin", type=float, default=4.0)
    parser.add_argument("--fmax", type=float, default=40.0)
    parser.add_argument("--F1", type=int, default=8)
    parser.add_argument("--D", type=int, default=2)
    parser.add_argument("--dropout", type=float, default=0.5)
    parser.add_argument("--kern-length", type=int, default=64)
    parser.add_argument("--max-epochs", type=int, default=80)
    parser.add_argument("--patience", type=int, default=12)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--val-fraction", type=float, default=0.2)
    parser.add_argument("--n-permutations", type=int, default=5)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--device", default="cpu")
    parser.add_argument(
        "--out-dir",
        default=str(Path(__file__).resolve().parents[3] / "results" / "phase-0" / "runs"),
    )
    args = parser.parse_args()

    subjects = [int(s) for s in args.subjects.split(",") if s.strip()]
    if args.device == "cuda" and not torch.cuda.is_available():
        args.device = "cpu"
    if args.device == "mps" and not torch.backends.mps.is_available():
        args.device = "cpu"

    run_id = (
        datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        + f"_eegnet_{args.task}_sub{'-'.join(map(str, subjects))}"
    )
    cfg = RunConfig(
        data_root=args.data_root,
        subjects=subjects,
        condition=args.condition,
        task=args.task,
        tmin=args.tmin,
        tmax=args.tmax,
        fmin=args.fmin,
        fmax=args.fmax,
        F1=args.F1,
        D=args.D,
        dropout=args.dropout,
        kern_length=args.kern_length,
        max_epochs=args.max_epochs,
        patience=args.patience,
        batch_size=args.batch_size,
        lr=args.lr,
        weight_decay=args.weight_decay,
        val_fraction=args.val_fraction,
        n_permutations=args.n_permutations,
        seed=args.seed,
        device=args.device,
        run_id=run_id,
    )

    out_dir = Path(args.out_dir) / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[eegnet] run_id={run_id}", flush=True)
    print(
        f"[eegnet] device={cfg.device} F1={cfg.F1} D={cfg.D} dropout={cfg.dropout} "
        f"band={cfg.fmin}-{cfg.fmax} Hz",
        flush=True,
    )

    subject_rows = []
    all_true, all_pred, all_meta = [], [], []
    label_names = None

    for subject in subjects:
        print(f"[eegnet] loading subject {subject:02d}", flush=True)
        X, Y, meta, sfreq, times = load_subject_sessions(Path(cfg.data_root), subject)
        X, y, meta, label_names = filter_trials(X, Y, meta, cfg.condition, cfg.task)
        X = preprocess_epochs(X, sfreq, times, cfg.tmin, cfg.tmax, cfg.fmin, cfg.fmax)
        print(
            f"[eegnet] subject={subject:02d} trials={len(y)} shape={X.shape}",
            flush=True,
        )
        folds, overall, y_true, y_pred = leave_session_out_subject(X, y, meta, cfg)
        null = permutation_subject(X, y, meta, cfg)
        p_value = None
        if null:
            observed = overall["balanced_accuracy"]
            p_value = float(
                (1 + np.sum(np.asarray(null["scores"]) >= observed))
                / (1 + cfg.n_permutations)
            )
        print(
            f"[eegnet] sub-{subject:02d} bal_acc={overall['balanced_accuracy']:.3f} p={p_value}",
            flush=True,
        )
        subject_rows.append(
            {
                "subject": subject,
                "folds": folds,
                "overall": overall,
                "permutation": null,
                "p_value_ge_observed": p_value,
            }
        )
        all_true.append(y_true)
        all_pred.append(y_pred)
        all_meta.append(meta)

    y_true = np.concatenate(all_true)
    y_pred = np.concatenate(all_pred)
    pooled = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro")),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
        "n_trials": int(len(y_true)),
    }
    per_subj = [r["overall"]["balanced_accuracy"] for r in subject_rows]
    chance = 1.0 / len(label_names)

    report = {
        "run_id": run_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "method": "eegnet",
        "config": asdict(cfg),
        "label_names": label_names,
        "chance_balanced_accuracy": chance,
        "torch_version": torch.__version__,
        "subject_results": subject_rows,
        "mean_subject_balanced_accuracy": float(np.mean(per_subj)),
        "std_subject_balanced_accuracy": float(np.std(per_subj)),
        "pooled_concatenated": pooled,
        "notes": [
            "Subject-specific EEGNet-8,2 (Lawhern 2018 style) with early stopping.",
            "Leave-session-out within each subject; train-channel z-score.",
            "Band-pass 4-40 Hz; action window 1.5-3.5 s; dropout 0.5.",
            "Permutation budget reduced vs classical (DL cost); same training protocol.",
        ],
    }
    metrics_path = out_dir / "metrics.json"
    metrics_path.write_text(json.dumps(report, indent=2))
    np.savez_compressed(
        out_dir / "predictions.npz",
        y_true=y_true,
        y_pred=y_pred,
        meta=np.concatenate(all_meta),
    )
    summary = (
        f"run_id={run_id}\n"
        f"method=eegnet\n"
        f"task={cfg.task} subjects={subjects}\n"
        f"mean_subject_balanced_accuracy={np.mean(per_subj):.4f} "
        f"+/- {np.std(per_subj):.4f} (chance={chance:.4f})\n"
        f"pooled_balanced_accuracy={pooled['balanced_accuracy']:.4f}\n"
        f"metrics={metrics_path}\n"
    )
    (out_dir / "summary.txt").write_text(summary)
    print(summary, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
