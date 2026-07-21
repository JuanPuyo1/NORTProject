"""Phase 0: Truncated SVD on band-power → linear SVM.

Feature compressor QC: log band-power (5 bands × channels) → train-fold
TruncatedSVD → SVM. Subject-specific leave-session-out evaluation.
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
from sklearn.decomposition import TruncatedSVD
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
    n_components: int
    C: float
    kernel: str
    n_permutations: int
    seed: int
    run_id: str


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


def bandpower_features(X: np.ndarray, sfreq: float, times: np.ndarray, tmin: float, tmax: float):
    start = int(np.searchsorted(times, tmin))
    end = int(np.searchsorted(times, tmax))
    if end <= start:
        raise ValueError("Invalid time window")
    segment = X[:, :, start:end]
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


def make_pipeline(cfg: RunConfig, n_features: int, n_train: int):
    # TruncatedSVD needs n_components < n_features and <= n_train - 1 for stability.
    k = min(cfg.n_components, n_features - 1, max(n_train - 1, 1))
    k = max(k, 1)
    return Pipeline(
        [
            ("scaler", StandardScaler()),
            (
                "svd",
                TruncatedSVD(n_components=k, random_state=cfg.seed, algorithm="randomized"),
            ),
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


def leave_session_out_subject(F, y, meta, cfg: RunConfig):
    sessions = sorted(np.unique(meta[:, 1]).tolist())
    folds = []
    y_true_all, y_pred_all = [], []
    for test_ses in sessions:
        test_mask = meta[:, 1] == test_ses
        train_mask = ~test_mask
        if len(np.unique(y[train_mask])) < 2 or test_mask.sum() == 0:
            continue
        pipe = make_pipeline(cfg, F.shape[1], int(train_mask.sum()))
        pipe.fit(F[train_mask], y[train_mask])
        pred = pipe.predict(F[test_mask])
        svd = pipe.named_steps["svd"]
        explained = float(np.sum(svd.explained_variance_ratio_))
        yt = y[test_mask]
        folds.append(
            {
                "test_session": int(test_ses),
                "n_train": int(train_mask.sum()),
                "n_test": int(test_mask.sum()),
                "n_svd_components": int(svd.n_components),
                "explained_variance_ratio_sum": explained,
                "accuracy": float(accuracy_score(yt, pred)),
                "balanced_accuracy": float(balanced_accuracy_score(yt, pred)),
                "macro_f1": float(f1_score(yt, pred, average="macro")),
                "confusion_matrix": confusion_matrix(yt, pred).tolist(),
            }
        )
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
        "mean_explained_variance_ratio_sum": float(
            np.mean([f["explained_variance_ratio_sum"] for f in folds])
        ),
    }
    return folds, overall, y_true, y_pred


def permutation_subject(F, y, meta, cfg: RunConfig):
    if cfg.n_permutations <= 0:
        return None
    rng = check_random_state(cfg.seed)
    scores = []
    for i in range(cfg.n_permutations):
        y_perm = y.copy()
        for ses in np.unique(meta[:, 1]):
            idx = np.where(meta[:, 1] == ses)[0]
            y_perm[idx] = rng.permutation(y_perm[idx])
        _, overall, _, _ = leave_session_out_subject(F, y_perm, meta, cfg)
        scores.append(overall["balanced_accuracy"])
        print(
            f"[svd]   perm {i + 1}/{cfg.n_permutations} bal_acc={overall['balanced_accuracy']:.3f}",
            flush=True,
        )
    return {
        "n_permutations": cfg.n_permutations,
        "mean_balanced_accuracy": float(np.mean(scores)),
        "std_balanced_accuracy": float(np.std(scores)),
        "p95_balanced_accuracy": float(np.percentile(scores, 95)),
        "scores": [float(s) for s in scores],
    }


def evaluate_k_sweep(F, y, meta, cfg: RunConfig, k_list: list):
    """Optional QC sweep over SVD rank; does not run permutations."""
    rows = []
    for k in k_list:
        cfg_k = RunConfig(**{**asdict(cfg), "n_components": int(k), "n_permutations": 0})
        folds, overall, _, _ = leave_session_out_subject(F, y, meta, cfg_k)
        rows.append(
            {
                "n_components": int(k),
                "balanced_accuracy": overall["balanced_accuracy"],
                "macro_f1": overall["macro_f1"],
                "mean_explained_variance_ratio_sum": overall["mean_explained_variance_ratio_sum"],
                "folds": folds,
            }
        )
        print(
            f"[svd]   k={k} bal_acc={overall['balanced_accuracy']:.3f} "
            f"var={overall['mean_explained_variance_ratio_sum']:.3f}",
            flush=True,
        )
    return rows


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
    parser.add_argument("--n-components", type=int, default=32, help="TruncatedSVD rank")
    parser.add_argument(
        "--sweep-k",
        default="",
        help="Optional comma-separated ranks to sweep before main run (e.g. 8,16,32,64)",
    )
    parser.add_argument("--C", type=float, default=1.0)
    parser.add_argument("--kernel", default="linear")
    parser.add_argument("--n-permutations", type=int, default=10)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--out-dir",
        default=str(Path(__file__).resolve().parents[3] / "results" / "phase-0" / "runs"),
    )
    args = parser.parse_args()

    subjects = [int(s) for s in args.subjects.split(",") if s.strip()]
    sweep_k = [int(x) for x in args.sweep_k.split(",") if x.strip()]
    run_id = (
        datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        + f"_svd_svm_k{args.n_components}_{args.task}_sub{'-'.join(map(str, subjects))}"
    )
    cfg = RunConfig(
        data_root=args.data_root,
        subjects=subjects,
        condition=args.condition,
        task=args.task,
        tmin=args.tmin,
        tmax=args.tmax,
        n_components=args.n_components,
        C=args.C,
        kernel=args.kernel,
        n_permutations=args.n_permutations,
        seed=args.seed,
        run_id=run_id,
    )

    out_dir = Path(args.out_dir) / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[svd] run_id={run_id}", flush=True)
    print(f"[svd] n_components={cfg.n_components} kernel={cfg.kernel}", flush=True)

    subject_rows = []
    all_true, all_pred, all_meta = [], [], []
    label_names = None

    for subject in subjects:
        print(f"[svd] loading subject {subject:02d}", flush=True)
        X, Y, meta, sfreq, times = load_subject_sessions(Path(cfg.data_root), subject)
        X, y, meta, label_names = filter_trials(X, Y, meta, cfg.condition, cfg.task)
        F = bandpower_features(X, sfreq, times, cfg.tmin, cfg.tmax)
        print(
            f"[svd] subject={subject:02d} trials={len(y)} features={F.shape[1]}",
            flush=True,
        )

        k_sweep = None
        if sweep_k:
            print(f"[svd] sweeping k={sweep_k} subject={subject:02d}", flush=True)
            k_sweep = evaluate_k_sweep(F, y, meta, cfg, sweep_k)

        folds, overall, y_true, y_pred = leave_session_out_subject(F, y, meta, cfg)
        null = permutation_subject(F, y, meta, cfg)
        p_value = None
        if null:
            observed = overall["balanced_accuracy"]
            p_value = float(
                (1 + np.sum(np.asarray(null["scores"]) >= observed))
                / (1 + cfg.n_permutations)
            )
        print(
            f"[svd] sub-{subject:02d} bal_acc={overall['balanced_accuracy']:.3f} "
            f"var={overall['mean_explained_variance_ratio_sum']:.3f} p={p_value}",
            flush=True,
        )
        subject_rows.append(
            {
                "subject": subject,
                "n_features": int(F.shape[1]),
                "folds": folds,
                "overall": overall,
                "k_sweep": k_sweep,
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
        "method": "bandpower_truncated_svd_svm",
        "config": asdict(cfg),
        "label_names": label_names,
        "chance_balanced_accuracy": chance,
        "bands": BANDS,
        "subject_results": subject_rows,
        "mean_subject_balanced_accuracy": float(np.mean(per_subj)),
        "std_subject_balanced_accuracy": float(np.std(per_subj)),
        "pooled_concatenated": pooled,
        "notes": [
            "Log band-power → train-fold TruncatedSVD → linear SVM.",
            "Leave-session-out within each subject.",
            "Action window 1.5-3.5 s; SVD fit on train fold only.",
            "SVD is a compressor/QC tool, not a semantic speech decoder.",
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
        f"method=bandpower_truncated_svd_svm\n"
        f"task={cfg.task} subjects={subjects} n_components={cfg.n_components}\n"
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
