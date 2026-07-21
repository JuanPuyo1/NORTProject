# Log: 2026-07-21 — EEGNet (Tier C)

## Goal

Run subject-specific **EEGNet-8,2** (Lawhern 2018 style) after classical Tier A/B stayed near chance.

## Implementation notes

- Script: `software/phase0_decode/scripts/run_eegnet.py`
- Dependency: PyTorch 2.8 (CPU/MPS wheel installed in `.venv`)
- Preprocess: band-pass 4–40 Hz, crop 1.5–3.5 s (128 ch × 512 samples @ 256 Hz)
- Model: F1=8, D=2, dropout=0.5, kernLength=64 (~3.7k params)
- Train: Adam lr=1e-3, weight decay=1e-4, batch 16, early stopping (patience 10, max 60 epochs), 20% stratified val from train
- Features: train-fold per-channel z-score; class-weighted cross-entropy
- Split: leave-session-out within subject

**Runtime note:** Full binary with 5 permutations took ~51 min on MPS. 4-class with permutations was too slow (~1h+ for one subject); restarted **4-class with n_permutations=0** (~20 min).

## Results (subjects 1–8, inner speech)

### Binary arriba vs abajo (5 within-session permutations)

| Metric | Value |
|---|---|
| Mean subject balanced accuracy | **0.486 ± 0.037** |
| Chance | 0.50 |
| Pooled balanced accuracy | 0.489 |
| Best subject | sub-02 = 0.533 (p≈0.17) |

Run: `results/phase-0/runs/20260720T232023Z_eegnet_binary_up_down_sub1-2-3-4-5-6-7-8/`

| Subject | bal.acc | p (≥ observed) |
|---|---:|---:|
| 01 | 0.460 | 1.00 |
| 02 | 0.533 | 0.17 |
| 03 | 0.489 | 0.67 |
| 04 | 0.508 | 0.50 |
| 05 | 0.525 | 0.33 |
| 06 | 0.481 | 0.83 |
| 07 | 0.483 | 0.50 |
| 08 | 0.410 | 1.00 |

### 4-class (no permutations — wall-clock cut)

| Metric | Value |
|---|---|
| Mean subject balanced accuracy | **0.250 ± 0.010** |
| Chance | 0.25 |
| Pooled balanced accuracy | 0.250 |
| Best subject | sub-04 = 0.267 |

Run: `results/phase-0/runs/20260721T002728Z_eegnet_4class_sub1-2-3-4-5-6-7-8/`

## Comparison to classical ladder

| Method | Binary mean/pool | 4-class mean/pool |
|---|---|---|
| Band-power + SVM (pooled) | — / 0.476 | — / 0.243 |
| CSP + LDA | 0.506 / 0.502 | 0.267 / 0.264 |
| FBCSP + LDA | 0.541 / 0.539 | 0.259 / 0.259 |
| Riemannian TS + LDA | 0.505 / 0.505 | 0.253 / 0.254 |
| SVD + SVM | 0.508 / 0.505 | 0.253 / 0.252 |
| **EEGNet** | **0.486 / 0.489** | **0.250 / 0.250** |

## Interpretation

1. Subject-specific EEGNet does **not** beat chance under leave-session-out; binary is slightly **below** FBCSP and near/under 0.50.
2. 4-class sits on chance with very low subject variance — consistent with no recoverable class structure.
3. Small-N + session drift + strong regularization → model collapses toward prior; DL capacity does not invent a signal classical methods missed.
4. Next software priority shifts away from “another decoder architecture” toward **artifact/EXG ablations** and Phase 1 acquisition quality — not more EEGNet hyperparameter sweeps.

## Reproduce

```bash
source .venv/bin/activate
export PYTHONUNBUFFERED=1 MPLCONFIGDIR=/tmp/mpl-nort
# Binary (with null)
python software/phase0_decode/scripts/run_eegnet.py \
  --subjects 1,2,3,4,5,6,7,8 --task binary_up_down \
  --n-permutations 5 --max-epochs 60 --patience 10 --device mps
# 4-class (observed only; add --n-permutations 5 if overnight)
python software/phase0_decode/scripts/run_eegnet.py \
  --subjects 1,2,3,4,5,6,7,8 --task 4class \
  --n-permutations 0 --max-epochs 60 --patience 10 --device mps
```
