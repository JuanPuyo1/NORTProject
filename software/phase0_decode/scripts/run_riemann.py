"""Phase 0 next method: Riemannian covariance geometry.

Spatial PCA (train-fold) → shrunk covariances → MDM or TangentSpace+LDA.
Subject-specific leave-session-out evaluation.
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
from pyriemann.classification import MDM
from pyriemann.estimation import Covariances
from pyriemann.tangentspace import TangentSpace
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.utils import check_random_state

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
    n_pca: int
    cov_estimator: str
    backend: str
    n_permutations: int
    seed: int
    run_id: str


class SpatialPCA(BaseEstimator, TransformerMixin):
    """Reduce channels with PCA fit on concatenated time samples (train only)."""

    def __init__(self, n_components: int = 20):
        self.n_components = n_components
        self.pca_ = None

    def fit(self, X, y=None):
        # X: (n_trials, n_ch, n_times)
        n_trials, n_ch, n_times = X.shape
        flat = X.transpose(0, 2, 1).reshape(-1, n_ch)
        k = min(self.n_components, n_ch, flat.shape[0])
        self.pca_ = PCA(n_components=k, random_state=0)
        self.pca_.fit(flat)
        return self

    def transform(self, X):
        n_trials, n_ch, n_times = X.shape
        flat = X.transpose(0, 2, 1).reshape(-1, n_ch)
        proj = self.pca_.transform(flat)
        k = proj.shape[1]
        return proj.reshape(n_trials, n_times, k).transpose(0, 2, 1)


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
    return filtered.astype(np.float64)


def make_pipeline(cfg: RunConfig):
    steps = [
        ("spatial_pca", SpatialPCA(n_components=cfg.n_pca)),
        ("cov", Covariances(estimator=cfg.cov_estimator)),
    ]
    if cfg.backend == "mdm":
        steps.append(("mdm", MDM(metric=dict(mean="riemann", distance="riemann"))))
    else:
        steps.extend(
            [
                ("ts", TangentSpace(metric="riemann")),
                ("scaler", StandardScaler()),
                ("clf", LinearDiscriminantAnalysis(solver="lsqr", shrinkage="auto")),
            ]
        )
    return Pipeline(steps)


def leave_session_out_subject(X, y, meta, cfg: RunConfig):
    sessions = sorted(np.unique(meta[:, 1]).tolist())
    folds = []
    y_true_all, y_pred_all = [], []
    for test_ses in sessions:
        test_mask = meta[:, 1] == test_ses
        train_mask = ~test_mask
        if len(np.unique(y[train_mask])) < 2 or test_mask.sum() == 0:
            continue
        pipe = make_pipeline(cfg)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            pipe.fit(X[train_mask], y[train_mask])
            pred = pipe.predict(X[test_mask])
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
        _, overall, _, _ = leave_session_out_subject(X, y_perm, meta, cfg)
        scores.append(overall["balanced_accuracy"])
        print(
            f"[riemann]   perm {i + 1}/{cfg.n_permutations} "
            f"bal_acc={overall['balanced_accuracy']:.3f}",
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
    parser.add_argument("--fmin", type=float, default=8.0)
    parser.add_argument("--fmax", type=float, default=30.0)
    parser.add_argument("--n-pca", type=int, default=20, help="Spatial PCA components before cov")
    parser.add_argument(
        "--cov-estimator",
        default="oas",
        choices=["oas", "lwf", "scm", "corr"],
    )
    parser.add_argument(
        "--backend",
        default="ts_lda",
        choices=["ts_lda", "mdm"],
        help="Tangent space + LDA, or Minimum Distance to Mean",
    )
    parser.add_argument("--n-permutations", type=int, default=10)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--out-dir",
        default=str(Path(__file__).resolve().parents[3] / "results" / "phase-0" / "runs"),
    )
    args = parser.parse_args()

    subjects = [int(s) for s in args.subjects.split(",") if s.strip()]
    run_id = (
        datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        + f"_riemann_{args.backend}_{args.task}_sub{'-'.join(map(str, subjects))}"
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
        n_pca=args.n_pca,
        cov_estimator=args.cov_estimator,
        backend=args.backend,
        n_permutations=args.n_permutations,
        seed=args.seed,
        run_id=run_id,
    )

    out_dir = Path(args.out_dir) / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[riemann] run_id={run_id}", flush=True)
    print(
        f"[riemann] backend={cfg.backend} n_pca={cfg.n_pca} cov={cfg.cov_estimator}",
        flush=True,
    )

    subject_rows = []
    all_true, all_pred, all_meta = [], [], []
    label_names = None

    for subject in subjects:
        print(f"[riemann] loading subject {subject:02d}", flush=True)
        X, Y, meta, sfreq, times = load_subject_sessions(Path(cfg.data_root), subject)
        X, y, meta, label_names = filter_trials(X, Y, meta, cfg.condition, cfg.task)
        X = preprocess_epochs(X, sfreq, times, cfg.tmin, cfg.tmax, cfg.fmin, cfg.fmax)
        print(f"[riemann] subject={subject:02d} trials={len(y)} shape={X.shape}", flush=True)
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
            f"[riemann] sub-{subject:02d} bal_acc={overall['balanced_accuracy']:.3f} p={p_value}",
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
        "method": f"riemann_{cfg.backend}",
        "config": asdict(cfg),
        "label_names": label_names,
        "chance_balanced_accuracy": chance,
        "subject_results": subject_rows,
        "mean_subject_balanced_accuracy": float(np.mean(per_subj)),
        "std_subject_balanced_accuracy": float(np.std(per_subj)),
        "pooled_concatenated": pooled,
        "notes": [
            "Spatial PCA (train fold) → OAS covariances → MDM or TangentSpace+LDA.",
            "Leave-session-out within each subject.",
            "Band-pass 8-30 Hz; action window 1.5-3.5 s.",
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
        f"method=riemann_{cfg.backend}\n"
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
