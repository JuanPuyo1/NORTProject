# Phase 0 Process: First Method Run

## Goal

Stand up and execute the first decoding baseline on real Inner Speech EEG data:

**log band-power features → StandardScaler → linear SVM**, evaluated with leave-session-out.

## What went wrong initially

The dataset folder under `projects/Inner_Speech_Dataset/dataset/ds003626/` looked complete (all subjects/sessions present), but files were **broken git-annex links**. No EEG content was on disk.

Lesson: always verify file size / MNE load before claiming the dataset is ready.

## Fix

1. Installed a project venv (`.venv`) with `mne`, `scikit-learn`, `numpy`, `pandas`, `awscli`.
2. Downloaded real files from OpenNeuro public S3 into `projects/ds003626/`.
3. Started with **sub-01** only (~560 MB) to validate the pipeline quickly.

## Pipeline implemented

`software/phase0_decode/scripts/run_bandpower_svm.py`

Steps:

1. Load `*_eeg-epo.fif` + `*_events.dat` for selected subjects/sessions.
2. Keep condition = inner speech.
3. Select task labels:
   - binary: arriba(0) vs abajo(1)
   - 4-class: all four directions
4. Crop action window 1.5–3.5 s.
5. Compute log mean power in five bands × 128 channels.
6. Train/test with leave-session-out SVM.
7. Estimate a permutation null (shuffle labels within session).
8. Write `metrics.json`, `predictions.npz`, and `summary.txt` under `results/phase-0/runs/`.

## Results (sub-01)

- Binary balanced accuracy: 0.55 (chance 0.50, p≈0.16)
- 4-class balanced accuracy: 0.315 (chance 0.25, p≈0.039)

Detailed log: [`../logs/2026-07-20-phase-0-first-baseline.md`](../logs/2026-07-20-phase-0-first-baseline.md)

## Next recommended steps

1. Download remaining subjects' `eeg-epo.fif` + `events.dat`.
2. Add Truncated SVD feature compression before SVM.
3. Add CSP / FBCSP baseline.
4. Keep the same leave-session-out + permutation harness for fair comparison.
