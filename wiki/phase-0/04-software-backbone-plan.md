# Phase 0 Software Backbone Plan

## Target package layout (to implement next)

Proposed location (not created yet as runnable package — docs first):

```text
software/
  phase0_decode/
    data/           # loaders for ds003626 derivatives
    features/       # bandpower, SVD/PCA, CSP
    models/         # SVM, LDA, EEGNet wrappers
    eval/           # splits, metrics, permutation tests
    configs/        # YAML experiment configs
    scripts/        # download, train, report
results/phase-0/    # metrics, confusion matrices, plots
wiki/logs/          # decision and run logs
```

## Immediate next actions

1. Download Inner Speech **derivatives** (`eeg` + `events` + ideally `exg`) into `projects/ds003626/`.
2. Write a loader that returns `(X, y, subject, session, condition)` arrays.
3. Reproduce the notebook's binary SVM baseline with logged metrics.
4. Add Truncated SVD and CSP baselines behind the same eval harness.
5. Optionally run a TribeV2 speech-ROI prior notebook; store plots under `results/phase-0/tribev2/`.

## Experiment naming convention

```text
YYYYMMDD_subjectSplit_method_task
example: 20260720_loso_svd32_svm_4class_inner
```

Every run log must include:

- git commit / code path
- data revision (subjects/sessions present)
- preprocess settings
- split scheme
- chance / permutation result
- balanced accuracy ± CI if available
- artifact filters used

## Definition of done for Phase 0 v0.1

- [ ] Derivatives downloaded for ≥1 subject (smoke) and then all 10
- [ ] Loader unit-tested on one session
- [ ] Binary and 4-class SVM baselines logged
- [ ] SVD and CSP comparisons logged
- [ ] TribeV2 decision recorded as sidecar-only unless new evidence appears
- [ ] README in `results/phase-0/` summarizing best honest score
