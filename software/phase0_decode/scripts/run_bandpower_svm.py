"""Phase 0 first baseline: band-power features + linear SVM.

Uses Nieto et al. Inner Speech derivatives (ds003626).
Default task: binary arriba vs abajo, inner-speech condition,
leave-session-out on subject 01.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import mne
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.utils import check_random_state

CLASS_NAMES = {0: "arriba", 1: "abajo", 2: "derecha", 3: "izquierda"}
CONDITION_NAMES = {0: "pronounced", 1: "inner", 2: "visualized"}
BANDS = {
    "delta": (1.0, 4.0),
    "theta": (4.0, 8.0),
    "alpha": (8.0, 13.0),
    "beta": (13.0, 30.0),
    "gamma": (30.0, 45.0),
}


@dataclass
class RunConfig:
    data_root: str
    subjects: list
    condition: str
    task: str
    tmin: float
    tmax: float
    C: float
    kernel: str
    n_permutations: int
    seed: int
    run_id: str


def load_subject_sessions(data_root: Path, subject: int):
    sub = f"sub-{subject:02d}"
    X_list, y_list, meta = [], [], []
    for session in (1, 2, 3):
        ses = f"ses-{session:02d}"
        eeg_path = data_root / "derivatives" / sub / ses / f"{sub}_{ses}_eeg-epo.fif"
        events_path = data_root / "derivatives" / sub / ses / f"{sub}_{ses}_events.dat"
        if not eeg_path.exists() or not events_path.exists():
            raise FileNotFoundError(f"Missing files for {sub} {ses}: {eeg_path}")
        epochs = mne.read_epochs(eeg_path, preload=True, verbose="ERROR")
        events = np.load(events_path, allow_pickle=True)
        if len(epochs) != len(events):
            raise ValueError(
                f"Epoch/event mismatch for {sub} {ses}: {len(epochs)} vs {len(events)}"
            )
        X_list.append(epochs.get_data(copy=True))
        y_list.append(events)
        meta.extend([(subject, session)] * len(events))
        sfreq = float(epochs.info["sfreq"])
        times = epochs.times.copy()
    X = np.concatenate(X_list, axis=0)
    Y = np.concatenate(y_list, axis=0)
    meta = np.asarray(meta, dtype=int)
    return X, Y, meta, sfreq, times


def filter_trials(X, Y, meta, condition: str, task: str):
    cond_map = {"pronounced": 0, "inner": 1, "visualized": 2}
    if condition not in cond_map:
        raise ValueError(f"Unknown condition {condition}")
    mask = Y[:, 2] == cond_map[condition]
    if task == "binary_up_down":
        mask &= np.isin(Y[:, 1], [0, 1])
        labels = Y[mask, 1].astype(int)
        label_names = [CLASS_NAMES[0], CLASS_NAMES[1]]
    elif task == "4class":
        labels = Y[mask, 1].astype(int)
        label_names = [CLASS_NAMES[i] for i in range(4)]
    else:
        raise ValueError(f"Unknown task {task}")
    return X[mask], labels, meta[mask], label_names


def bandpower_features(X: np.ndarray, sfreq: float, times: np.ndarray, tmin: float, tmax: float):
    start = int(np.searchsorted(times, tmin))
    end = int(np.searchsorted(times, tmax))
    if end <= start:
        raise ValueError("Invalid time window")
    segment = X[:, :, start:end]
    # Welch PSD per trial/channel
    # Use rfft magnitude-squared averaged into bands.
    n_times = segment.shape[-1]
    freqs = np.fft.rfftfreq(n_times, d=1.0 / sfreq)
    spectra = np.abs(np.fft.rfft(segment, axis=-1)) ** 2
    feats = []
    for lo, hi in BANDS.values():
        idx = (freqs >= lo) & (freqs < hi)
        if not np.any(idx):
            raise ValueError(f"No frequency bins in band {lo}-{hi}")
        band = spectra[:, :, idx].mean(axis=-1)
        feats.append(band)
    F = np.concatenate(feats, axis=1)
    return np.log10(F + 1e-12)


def leave_session_out_scores(F, y, meta, cfg: RunConfig):
    sessions = sorted(np.unique(meta[:, 1]).tolist())
    fold_rows = []
    y_true_all, y_pred_all = [], []
    for test_ses in sessions:
        test_mask = meta[:, 1] == test_ses
        train_mask = ~test_mask
        if len(np.unique(y[train_mask])) < 2 or len(np.unique(y[test_mask])) < 1:
            continue
        clf = Pipeline(
            [
                ("scaler", StandardScaler()),
                (
                    "svm",
                    SVC(
                        C=cfg.C,
                        kernel=cfg.kernel,
                        class_weight="balanced",
                        random_state=cfg.seed,
                    ),
                ),
            ]
        )
        clf.fit(F[train_mask], y[train_mask])
        pred = clf.predict(F[test_mask])
        yt = y[test_mask]
        row = {
            "test_session": int(test_ses),
            "n_train": int(train_mask.sum()),
            "n_test": int(test_mask.sum()),
            "accuracy": float(accuracy_score(yt, pred)),
            "balanced_accuracy": float(balanced_accuracy_score(yt, pred)),
            "macro_f1": float(f1_score(yt, pred, average="macro")),
            "confusion_matrix": confusion_matrix(yt, pred).tolist(),
        }
        fold_rows.append(row)
        y_true_all.append(yt)
        y_pred_all.append(pred)
    y_true = np.concatenate(y_true_all)
    y_pred = np.concatenate(y_pred_all)
    overall = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro")),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
        "n_trials": int(len(y_true)),
    }
    return fold_rows, overall, y_true, y_pred


def permutation_null(F, y, meta, cfg: RunConfig):
    rng = check_random_state(cfg.seed)
    scores = []
    for _ in range(cfg.n_permutations):
        y_perm = y.copy()
        # Shuffle labels within each session to preserve session structure.
        for ses in np.unique(meta[:, 1]):
            idx = np.where(meta[:, 1] == ses)[0]
            y_perm[idx] = rng.permutation(y_perm[idx])
        _, overall, _, _ = leave_session_out_scores(F, y_perm, meta, cfg)
        scores.append(overall["balanced_accuracy"])
    return {
        "n_permutations": cfg.n_permutations,
        "mean_balanced_accuracy": float(np.mean(scores)),
        "std_balanced_accuracy": float(np.std(scores)),
        "p95_balanced_accuracy": float(np.percentile(scores, 95)),
        "scores": [float(s) for s in scores],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-root",
        default=str(Path(__file__).resolve().parents[3] / "projects" / "ds003626"),
    )
    parser.add_argument("--subjects", default="1")
    parser.add_argument("--condition", default="inner", choices=list(CONDITION_NAMES.values()))
    parser.add_argument("--task", default="binary_up_down", choices=["binary_up_down", "4class"])
    parser.add_argument("--tmin", type=float, default=1.5)
    parser.add_argument("--tmax", type=float, default=3.5)
    parser.add_argument("--C", type=float, default=1.0)
    parser.add_argument("--kernel", default="linear")
    parser.add_argument("--n-permutations", type=int, default=50)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--out-dir",
        default=str(Path(__file__).resolve().parents[3] / "results" / "phase-0" / "runs"),
    )
    args = parser.parse_args()

    subjects = [int(s) for s in args.subjects.split(",") if s.strip()]
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + f"_{args.task}_sub{'-'.join(map(str, subjects))}"
    cfg = RunConfig(
        data_root=args.data_root,
        subjects=subjects,
        condition=args.condition,
        task=args.task,
        tmin=args.tmin,
        tmax=args.tmax,
        C=args.C,
        kernel=args.kernel,
        n_permutations=args.n_permutations,
        seed=args.seed,
        run_id=run_id,
    )

    data_root = Path(cfg.data_root)
    out_dir = Path(args.out_dir) / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[phase0] run_id={run_id}")
    print(f"[phase0] data_root={data_root}")

    X_all, y_all, meta_all = [], [], []
    sfreq = times = None
    for subject in subjects:
        X, Y, meta, sfreq, times = load_subject_sessions(data_root, subject)
        X, labels, meta, label_names = filter_trials(X, Y, meta, cfg.condition, cfg.task)
        print(
            f"[phase0] subject={subject:02d} trials={len(labels)} "
            f"label_counts={ {CLASS_NAMES[i]: int((labels==i).sum()) for i in np.unique(labels)} }"
        )
        X_all.append(X)
        y_all.append(labels)
        meta_all.append(meta)

    X = np.concatenate(X_all, axis=0)
    y = np.concatenate(y_all, axis=0)
    meta = np.concatenate(meta_all, axis=0)

    print(f"[phase0] extracting band-power features window=[{cfg.tmin},{cfg.tmax}] s")
    F = bandpower_features(X, sfreq, times, cfg.tmin, cfg.tmax)
    print(f"[phase0] feature matrix shape={F.shape}")

    folds, overall, y_true, y_pred = leave_session_out_scores(F, y, meta, cfg)
    print("[phase0] leave-session-out overall:", overall)

    null = permutation_null(F, y, meta, cfg)
    observed = overall["balanced_accuracy"]
    p_value = (1 + np.sum(np.asarray(null["scores"]) >= observed)) / (1 + cfg.n_permutations)
    print(
        f"[phase0] permutation null mean={null['mean_balanced_accuracy']:.3f} "
        f"p95={null['p95_balanced_accuracy']:.3f} p={p_value:.4f}"
    )

    chance = 1.0 / len(label_names)
    report = {
        "run_id": run_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "method": "bandpower_log_svm",
        "config": asdict(cfg),
        "label_names": label_names,
        "chance_balanced_accuracy": chance,
        "n_channels": int(X.shape[1]),
        "n_features": int(F.shape[1]),
        "bands": BANDS,
        "folds": folds,
        "overall": overall,
        "permutation": {**null, "p_value_ge_observed": float(p_value)},
        "notes": [
            "First Phase 0 baseline.",
            "Leave-session-out evaluation.",
            "Does not prove inner-speech decoding beyond artifacts.",
        ],
    }

    metrics_path = out_dir / "metrics.json"
    metrics_path.write_text(json.dumps(report, indent=2))
    np.savez_compressed(out_dir / "predictions.npz", y_true=y_true, y_pred=y_pred, meta=meta)

    summary = (
        f"run_id={run_id}\n"
        f"method=bandpower_log_svm\n"
        f"task={cfg.task} condition={cfg.condition} subjects={subjects}\n"
        f"balanced_accuracy={overall['balanced_accuracy']:.4f} "
        f"(chance={chance:.4f})\n"
        f"accuracy={overall['accuracy']:.4f} macro_f1={overall['macro_f1']:.4f}\n"
        f"permutation_mean={null['mean_balanced_accuracy']:.4f} "
        f"p95={null['p95_balanced_accuracy']:.4f} p={p_value:.4f}\n"
        f"metrics={metrics_path}\n"
    )
    (out_dir / "summary.txt").write_text(summary)
    print(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
