# Log: 2026-07-20 — Riemannian covariance (TS + LDA)

## Goal

Run the next classical candidate after FBCSP:

**Spatial PCA → OAS covariances → Tangent Space → shrinkage LDA**

Subject-specific leave-session-out.

## Setup

- Script: `software/phase0_decode/scripts/run_riemann.py`
- Dependency: `pyriemann` 0.11
- Band-pass 8–30 Hz; window 1.5–3.5 s
- Train-fold spatial PCA to 20 components (128-ch covs are too large for TS/LDA)
- Covariance estimator: OAS
- Backend: `ts_lda` (Tangent Space + LDA)
- 10 within-session label permutations per subject

## Results (subjects 1–8, inner speech)

### Binary arriba vs abajo

| Metric | Value |
|---|---|
| Mean subject balanced accuracy | **0.505 ± 0.040** |
| Chance | 0.50 |
| Pooled balanced accuracy | 0.505 |
| Best subject | sub-08 = 0.570 (p≈0.09) |

Run: `results/phase-0/runs/20260720T220457Z_riemann_ts_lda_binary_up_down_sub1-2-3-4-5-6-7-8/`

### 4-class

| Metric | Value |
|---|---|
| Mean subject balanced accuracy | **0.253 ± 0.030** |
| Chance | 0.25 |
| Pooled balanced accuracy | 0.254 |
| Best subject | sub-02 = 0.300 (p≈0.09) |

Run: `results/phase-0/runs/20260720T220609Z_riemann_ts_lda_4class_sub1-2-3-4-5-6-7-8/`

## Ladder comparison (so far)

| Method | Binary mean/pool | 4-class mean/pool |
|---|---|---|
| Band-power + SVM | — / 0.476 | — / 0.243 |
| CSP + LDA | 0.506 / 0.502 | 0.267 / 0.264 |
| FBCSP + LDA | **0.541 / 0.539** | 0.259 / 0.259 |
| Riemannian TS+LDA | 0.505 / 0.505 | 0.253 / 0.254 |

## Interpretation

1. Riemannian geometry does **not** beat chance under leave-session-out on this dataset.
2. It underperforms FBCSP on binary and matches chance on 4-class.
3. Negative result strengthens the Tier-A conclusion: spatial/spectral classical BCI tools are not recovering a reliable inner-speech command signal here.
4. Next software levers with different failure modes: Truncated SVD+SVM (QC compressor), subject-specific EEGNet, or EXG/artifact ablations — not more covariance variants.

## Reproduce

```bash
source .venv/bin/activate
pip install pyriemann  # if needed
export PYTHONUNBUFFERED=1 MPLCONFIGDIR=/tmp/mpl-nort
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python software/phase0_decode/scripts/run_riemann.py \
  --subjects 1,2,3,4,5,6,7,8 --task binary_up_down --n-permutations 10
python software/phase0_decode/scripts/run_riemann.py \
  --subjects 1,2,3,4,5,6,7,8 --task 4class --n-permutations 10
```
