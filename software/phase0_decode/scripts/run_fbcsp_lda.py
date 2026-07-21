"""Phase 0 next method: Filter Bank CSP (FBCSP) + feature selection + LDA.

Classic FBCSP ladder step after single-band CSP:
  multi-band bandpass → CSP per band → SelectKBest → LDA/SVM
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
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif
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

# Ang et al. style filter bank (Hz)
DEFAULT_BANDS = (
    (4.0, 8.0),
    (8.0, 12.0),
    (12.0, 16.0),
    (16.0, 20.0),
    (20.0, 24.0),
    (24.0, 28.0),
    (28.0, 32.0),
)


@dataclass
class RunConfig:
    data_root: str
    subjects: list
    condition: str
    task: str
    tmin: float
    tmax: float
    bands: list
    n_components: int
    n_features: int
    selector: str
    classifier: str
    n_permutations: int
    seed: int
    run_id: str


class BinaryCSP:
    """Binary Common Spatial Patterns (log-variance features)."""

    def __init__(self, n_components: int = 4, reg: float = 1e-3):
        self.n_components = n_components
        self.reg = reg
        self.filters_ = None

    def fit(self, X, y):
        classes = np.unique(y)
        if len(classes) != 2:
            raise ValueError("BinaryCSP requires exactly 2 classes")
        c0, c1 = classes
        cov0 = self._mean_cov(X[y == c0])
        cov1 = self._mean_cov(X[y == c1])
        composite = cov0 + cov1
        composite += self.reg * np.eye(composite.shape[0])
        evals, evecs = np.linalg.eigh(np.linalg.pinv(composite) @ cov0)
        order = np.argsort(evals)[::-1]
        evecs = evecs[:, order]
        n = self.n_components // 2
        selected = np.hstack([evecs[:, :n], evecs[:, -n:]])
        self.filters_ = selected.T
        return self

    def transform(self, X):
        projected = np.einsum("kc,nct->nkt", self.filters_, X)
        var = np.var(projected, axis=-1)
        return np.log(var + 1e-10)

    def fit_transform(self, X, y):
        return self.fit(X, y).transform(X)

    def _mean_cov(self, X):
        n_trials, n_ch, _ = X.shape
        cov = np.zeros((n_ch, n_ch), dtype=float)
        for trial in X:
            c = trial @ trial.T
            c /= np.trace(c) + 1e-12
            cov += c
        cov /= max(n_trials, 1)
        return cov


class MulticlassCSP:
    """One-vs-rest CSP; concatenate features from each binary CSP."""

    def __init__(self, n_components: int = 4, reg: float = 1e-3):
        self.n_components = n_components
        self.reg = reg
        self.models_ = []
        self.classes_ = None

    def fit(self, X, y):
        self.classes_ = np.unique(y)
        self.models_ = []
        for c in self.classes_:
            y_bin = (y == c).astype(int)
            if len(np.unique(y_bin)) < 2:
                continue
            model = BinaryCSP(n_components=self.n_components, reg=self.reg)
            model.fit(X, y_bin)
            self.models_.append(model)
        return self

    def transform(self, X):
        feats = [m.transform(X) for m in self.models_]
        return np.concatenate(feats, axis=1)

    def fit_transform(self, X, y):
        return self.fit(X, y).transform(X)


class FilterBankCSP:
    """CSP independently in each precomputed frequency band, then concatenate."""

    def __init__(self, n_components: int = 4, n_classes: int = 2):
        self.n_components = n_components
        self.n_classes = n_classes
        self.models_ = []

    def fit(self, X_banks, y):
        # X_banks: list of arrays, each (n_trials, n_ch, n_times)
        self.models_ = []
        for Xb in X_banks:
            if self.n_classes == 2:
                model = BinaryCSP(n_components=self.n_components)
            else:
                model = MulticlassCSP(n_components=self.n_components)
            model.fit(Xb, y)
            self.models_.append(model)
        return self

    def transform(self, X_banks):
        feats = [m.transform(Xb) for m, Xb in zip(self.models_, X_banks)]
        return np.concatenate(feats, axis=1)

    def fit_transform(self, X_banks, y):
        return self.fit(X_banks, y).transform(X_banks)


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


def crop_epochs(X, times, tmin, tmax):
    start = int(np.searchsorted(times, tmin))
    end = int(np.searchsorted(times, tmax))
    return X[:, :, start:end]


def build_filter_bank(X, sfreq, bands):
    banks = []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for fmin, fmax in bands:
            filtered = mne.filter.filter_data(
                X, sfreq=sfreq, l_freq=fmin, h_freq=fmax, verbose="ERROR"
            )
            banks.append(filtered.astype(np.float64))
    return banks


def index_banks(banks, mask):
    return [b[mask] for b in banks]


def make_selector(cfg: RunConfig, n_features_in: int):
    k = min(cfg.n_features, n_features_in)
    if cfg.selector == "mutual_info":

        def score_func(X, y):
            return mutual_info_classif(X, y, random_state=cfg.seed)

        return SelectKBest(score_func=score_func, k=k)
    return SelectKBest(score_func=f_classif, k=k)


def make_classifier(cfg: RunConfig):
    if cfg.classifier == "lda":
        return LinearDiscriminantAnalysis(solver="lsqr", shrinkage="auto")
    return SVC(kernel="linear", C=1.0, class_weight="balanced", random_state=cfg.seed)


def fit_predict_fold(X_banks_train, y_train, X_banks_test, cfg: RunConfig, n_classes: int):
    fbcsp = FilterBankCSP(n_components=cfg.n_components, n_classes=n_classes)
    feats_train = fbcsp.fit_transform(X_banks_train, y_train)
    feats_test = fbcsp.transform(X_banks_test)
    selector = make_selector(cfg, feats_train.shape[1])
    pipe = Pipeline(
        [
            ("select", selector),
            ("scaler", StandardScaler()),
            ("clf", make_classifier(cfg)),
        ]
    )
    pipe.fit(feats_train, y_train)
    return pipe.predict(feats_test)


def leave_session_out_subject(X_banks, y, meta, cfg: RunConfig):
    n_classes = len(np.unique(y))
    sessions = sorted(np.unique(meta[:, 1]).tolist())
    folds = []
    y_true_all, y_pred_all = [], []
    for test_ses in sessions:
        test_mask = meta[:, 1] == test_ses
        train_mask = ~test_mask
        if len(np.unique(y[train_mask])) < 2 or test_mask.sum() == 0:
            continue
        pred = fit_predict_fold(
            index_banks(X_banks, train_mask),
            y[train_mask],
            index_banks(X_banks, test_mask),
            cfg,
            n_classes,
        )
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


def permutation_subject(X_banks, y, meta, cfg: RunConfig):
    if cfg.n_permutations <= 0:
        return None
    rng = check_random_state(cfg.seed)
    scores = []
    for i in range(cfg.n_permutations):
        y_perm = y.copy()
        for ses in np.unique(meta[:, 1]):
            idx = np.where(meta[:, 1] == ses)[0]
            y_perm[idx] = rng.permutation(y_perm[idx])
        _, overall, _, _ = leave_session_out_subject(X_banks, y_perm, meta, cfg)
        scores.append(overall["balanced_accuracy"])
        print(f"[fbcsp]   perm {i + 1}/{cfg.n_permutations} bal_acc={overall['balanced_accuracy']:.3f}", flush=True)
    return {
        "n_permutations": cfg.n_permutations,
        "mean_balanced_accuracy": float(np.mean(scores)),
        "std_balanced_accuracy": float(np.std(scores)),
        "p95_balanced_accuracy": float(np.percentile(scores, 95)),
        "scores": [float(s) for s in scores],
    }


def parse_bands(text: str):
    bands = []
    for part in text.split(";"):
        part = part.strip()
        if not part:
            continue
        lo, hi = part.split("-")
        bands.append((float(lo), float(hi)))
    return bands


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
    parser.add_argument(
        "--bands",
        default="4-8;8-12;12-16;16-20;20-24;24-28;28-32",
        help="Semicolon-separated fmin-fmax pairs in Hz",
    )
    parser.add_argument("--n-components", type=int, default=4, help="CSP components per band")
    parser.add_argument("--n-features", type=int, default=10, help="Selected features after FBCSP")
    parser.add_argument("--selector", default="f_classif", choices=["f_classif", "mutual_info"])
    parser.add_argument("--classifier", default="lda", choices=["lda", "svm"])
    parser.add_argument("--n-permutations", type=int, default=10)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--out-dir",
        default=str(Path(__file__).resolve().parents[3] / "results" / "phase-0" / "runs"),
    )
    args = parser.parse_args()

    subjects = [int(s) for s in args.subjects.split(",") if s.strip()]
    bands = parse_bands(args.bands) or list(DEFAULT_BANDS)
    # For 4-class, keep a few more selected features by default if user left default 10
    n_features = args.n_features
    if args.task == "4class" and args.n_features == 10:
        n_features = 16

    run_id = (
        datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        + f"_fbcsp_{args.classifier}_{args.task}_sub{'-'.join(map(str, subjects))}"
    )
    cfg = RunConfig(
        data_root=args.data_root,
        subjects=subjects,
        condition=args.condition,
        task=args.task,
        tmin=args.tmin,
        tmax=args.tmax,
        bands=[list(b) for b in bands],
        n_components=args.n_components,
        n_features=n_features,
        selector=args.selector,
        classifier=args.classifier,
        n_permutations=args.n_permutations,
        seed=args.seed,
        run_id=run_id,
    )

    out_dir = Path(args.out_dir) / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[fbcsp] run_id={run_id}", flush=True)
    print(f"[fbcsp] bands={bands} n_components={cfg.n_components} n_features={cfg.n_features}", flush=True)

    subject_rows = []
    all_true, all_pred, all_meta = [], [], []
    label_names = None

    for subject in subjects:
        print(f"[fbcsp] loading subject {subject:02d}", flush=True)
        X, Y, meta, sfreq, times = load_subject_sessions(Path(cfg.data_root), subject)
        X, y, meta, label_names = filter_trials(X, Y, meta, cfg.condition, cfg.task)
        X = crop_epochs(X, times, cfg.tmin, cfg.tmax)
        print(f"[fbcsp] building filter bank subject={subject:02d} trials={len(y)}", flush=True)
        X_banks = build_filter_bank(X, sfreq, bands)
        print(
            f"[fbcsp] subject={subject:02d} trials={len(y)} banks={len(X_banks)} shape={X_banks[0].shape}",
            flush=True,
        )
        folds, overall, y_true, y_pred = leave_session_out_subject(X_banks, y, meta, cfg)
        null = permutation_subject(X_banks, y, meta, cfg)
        p_value = None
        if null:
            observed = overall["balanced_accuracy"]
            p_value = float(
                (1 + np.sum(np.asarray(null["scores"]) >= observed))
                / (1 + cfg.n_permutations)
            )
        print(
            f"[fbcsp] sub-{subject:02d} bal_acc={overall['balanced_accuracy']:.3f} p={p_value}",
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
        "method": f"fbcsp_{cfg.selector}_{cfg.classifier}",
        "config": asdict(cfg),
        "label_names": label_names,
        "chance_balanced_accuracy": chance,
        "subject_results": subject_rows,
        "mean_subject_balanced_accuracy": float(np.mean(per_subj)),
        "std_subject_balanced_accuracy": float(np.std(per_subj)),
        "pooled_concatenated": pooled,
        "notes": [
            "Filter Bank CSP: CSP per 4 Hz band (4-32 Hz), SelectKBest, LDA/SVM.",
            "Leave-session-out within each subject.",
            "Action window 1.5-3.5 s; features selected on train fold only.",
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
        f"method=fbcsp_{cfg.selector}_{cfg.classifier}\n"
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
