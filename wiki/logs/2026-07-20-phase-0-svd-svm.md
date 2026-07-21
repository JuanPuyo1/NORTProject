# Log: 2026-07-20 — Truncated SVD + SVM

## Goal

Run the Tier B compressor QC step after Riemannian:

**log band-power → train-fold TruncatedSVD → linear SVM**, leave-session-out per subject.

## Implementation notes

- Script: `software/phase0_decode/scripts/run_svd_svm.py`
- Features: same 5-band log band-power as the SVM baseline (640 dims = 5 × 128 ch)
- Pipeline (fit on train fold only): `StandardScaler → TruncatedSVD(k) → SVC(linear)`
- Default rank **k=32**; also swept k ∈ {8, 16, 32, 64} without permutations
- Window: 1.5–3.5 s; condition: inner speech; 10 within-session label permutations
- Explained variance at k=32 typically ~0.84–0.95 of band-power feature variance

## Results (subjects 1–8, inner speech, k=32)

### Binary arriba vs abajo

| Metric | Value |
|---|---|
| Mean subject balanced accuracy | **0.508 ± 0.058** |
| Chance | 0.50 |
| Pooled balanced accuracy | 0.505 |
| Best subject | sub-08 = 0.570 (p≈0.09) |

Run: `results/phase-0/runs/20260720T224604Z_svd_svm_k32_binary_up_down_sub1-2-3-4-5-6-7-8/`

| Subject | bal.acc | p (≥ observed) | mean explained var |
|---|---:|---:|---:|
| 01 | 0.560 | 0.18 | 0.940 |
| 02 | 0.550 | 0.27 | 0.901 |
| 03 | 0.522 | 0.55 | 0.939 |
| 04 | 0.475 | 0.73 | 0.937 |
| 05 | 0.475 | 1.00 | 0.954 |
| 06 | 0.528 | 0.36 | 0.896 |
| 07 | 0.383 | 1.00 | 0.887 |
| 08 | 0.570 | 0.09 | 0.944 |

### 4-class

| Metric | Value |
|---|---|
| Mean subject balanced accuracy | **0.253 ± 0.023** |
| Chance | 0.25 |
| Pooled balanced accuracy | 0.252 |
| Best subject | sub-01 = 0.285 (p≈0.09) |

Run: `results/phase-0/runs/20260720T224628Z_svd_svm_k32_4class_sub1-2-3-4-5-6-7-8/`

### Rank sweep (mean subject bal.acc, no permutations)

| k | Binary | 4-class |
|---:|---:|---:|
| 8 | 0.531 ± 0.032 | 0.269 ± 0.028 |
| 16 | 0.491 ± 0.041 | 0.249 ± 0.038 |
| 32 | 0.508 ± 0.058 | 0.253 ± 0.023 |
| 64 | 0.513 ± 0.051 | 0.277 ± 0.020 |

No rank escapes chance by a meaningful margin; k=8 / k=64 bumps are small and non-significant under the same protocol.

## Comparison to previous methods

| Method | Binary mean/pool | 4-class mean/pool |
|---|---|---|
| Band-power + SVM (pooled LSO) | — / 0.476 | — / 0.243 |
| CSP + LDA | 0.506 / 0.502 | 0.267 / 0.264 |
| FBCSP + LDA | 0.541 / 0.539 | 0.259 / 0.259 |
| Riemannian TS + LDA | 0.505 / 0.505 | 0.253 / 0.254 |
| **SVD + SVM (k=32)** | **0.508 / 0.505** | **0.253 / 0.252** |

## Interpretation

1. Truncated SVD preserves most band-power variance but **does not create class signal** — compression ≠ discrimination.
2. Results match band-power / CSP / Riemannian near-chance levels; **below FBCSP** on binary.
3. Confirms the failure mode is not “too many correlated features for SVM”; unsupervised rank reduction does not rescue LSO decoding.
4. Classical Tier A/B ladder is complete enough to stop iterating covariance/spectral/PCA variants as the main lever.

## Reproduce

```bash
source .venv/bin/activate
export PYTHONUNBUFFERED=1 MPLCONFIGDIR=/tmp/mpl-nort
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
python software/phase0_decode/scripts/run_svd_svm.py \
  --subjects 1,2,3,4,5,6,7,8 --task binary_up_down \
  --n-components 32 --sweep-k 8,16,32,64 --n-permutations 10
python software/phase0_decode/scripts/run_svd_svm.py \
  --subjects 1,2,3,4,5,6,7,8 --task 4class \
  --n-components 32 --sweep-k 8,16,32,64 --n-permutations 10
```
