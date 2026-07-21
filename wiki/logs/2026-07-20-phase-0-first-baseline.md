# Log: 2026-07-20 — First band-power + SVM baseline

## Context

Attempted to run Phase 0 Method 1 (band-power features + linear SVM) on the Inner Speech dataset.

## Data status discovery

The tree under `projects/Inner_Speech_Dataset/dataset/ds003626/` contained **git-annex symlinks with missing annex objects** (broken links). That is metadata only, not usable EEG.

Action taken:

- Created a real local copy at `projects/ds003626/derivatives/`.
- Downloaded subject 01 EEG + events for ses-01/02/03 from OpenNeuro S3:

```bash
aws s3 cp --no-sign-request \
  s3://openneuro.org/ds003626/derivatives/sub-01/ses-0X/... \
  projects/ds003626/derivatives/sub-01/ses-0X/...
```

Verified with MNE: 128 channels, 256 Hz, times [-0.5, 4.0] s.

Environment:

- Local venv: `.venv/`
- Packages: mne 1.8.0, scikit-learn 1.6.1, numpy 2.0.2

## Method run

Script: `software/phase0_decode/scripts/run_bandpower_svm.py`

Protocol:

- Condition: inner speech only
- Window: 1.5–3.5 s
- Features: log band-power in delta/theta/alpha/beta/gamma over all 128 channels (640 features)
- Classifier: StandardScaler + linear SVM (`C=1`, balanced class weights)
- Split: leave-session-out
- Null: 50 within-session label permutations

### Binary arriba vs abajo (sub-01, 100 trials)

| Metric | Value |
|---|---|
| Balanced accuracy | **0.550** |
| Chance | 0.500 |
| Macro-F1 | 0.509 |
| Permutation mean / p95 | 0.503 / 0.556 |
| p (null ≥ observed) | **0.157** (not significant) |

Run: `results/phase-0/runs/20260720T200639Z_binary_up_down_sub1/`

### 4-class (sub-01, 200 trials)

| Metric | Value |
|---|---|
| Balanced accuracy | **0.315** |
| Chance | 0.250 |
| Macro-F1 | 0.288 |
| Permutation mean / p95 | 0.253 / 0.303 |
| p (null ≥ observed) | **0.039** (weakly above null) |

Run: `results/phase-0/runs/20260720T200655Z_4class_sub1/`

## Interpretation

1. The pipeline works end-to-end.
2. On one subject, simple band-power + SVM is near chance for binary and only weakly above chance for 4-class.
3. This is expected for a first linear baseline on inner speech EEG and does **not** yet support a wearable decoding claim.
4. Next methods should be Truncated SVD + SVM and CSP/FBCSP, then expand to more subjects after downloading their derivatives.

## Reproduce

```bash
cd /Users/estebanpuyo/NORT
source .venv/bin/activate
export MPLCONFIGDIR=/tmp/mpl-nort
python software/phase0_decode/scripts/run_bandpower_svm.py --task binary_up_down --subjects 1
python software/phase0_decode/scripts/run_bandpower_svm.py --task 4class --subjects 1
```
