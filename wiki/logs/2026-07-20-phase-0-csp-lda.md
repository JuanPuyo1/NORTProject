# Log: 2026-07-20 — CSP + LDA (next method)

## Goal

Run the first optimized alternative after band-power + SVM:

**subject-specific Common Spatial Patterns (CSP) → LDA**, leave-session-out.

## Implementation notes

- Initial MNE `CSP` hung on slow rank estimation with 128 channels.
- Replaced with classical NumPy CSP (`BinaryCSP` / one-vs-rest `MulticlassCSP`) in `software/phase0_decode/scripts/run_csp_lda.py`.
- Preprocess: band-pass 8–30 Hz, crop 1.5–3.5 s.
- 6 CSP components; LDA with shrinkage.
- 10 within-session label permutations per subject.

## Results (subjects 1–8, inner speech)

### Binary arriba vs abajo

| Metric | Value |
|---|---|
| Mean subject balanced accuracy | **0.506 ± 0.045** |
| Chance | 0.50 |
| Pooled balanced accuracy | 0.502 |
| Best subject | sub-03 = 0.611 (p≈0.09) |

Run: `results/phase-0/runs/20260720T210456Z_csp_lda_binary_up_down_sub1-2-3-4-5-6-7-8/`

### 4-class

| Metric | Value |
|---|---|
| Mean subject balanced accuracy | **0.267 ± 0.045** |
| Chance | 0.25 |
| Pooled balanced accuracy | 0.264 |
| Best subject | sub-03 = 0.361 (p≈0.18) |

Run: `results/phase-0/runs/20260720T210536Z_csp_lda_4class_sub1-2-3-4-5-6-7-8/`

## Comparison to previous baseline

| Method | Binary mean/pool | 4-class mean/pool |
|---|---|---|
| Band-power + SVM (pooled LSO) | — / 0.476 | — / 0.243 |
| CSP + LDA (subject-specific LSO) | 0.506 / 0.502 | 0.267 / 0.264 |

## Interpretation

1. CSP spatial-filter optimization did **not** produce a reliable decoder on this dataset under leave-session-out.
2. Results remain at/near chance; one subject (03) is slightly above chance but not significant under the small permutation budget.
3. Negative result is informative: the failure is not unique to fixed band-power features.
4. Next candidates: FBCSP + feature selection, SVD compression, subject-specific EEGNet, or stronger artifact controls — not more of the same CSP setup.

## Reproduce

```bash
source .venv/bin/activate
export PYTHONUNBUFFERED=1 MPLCONFIGDIR=/tmp/mpl-nort
python software/phase0_decode/scripts/run_csp_lda.py \
  --subjects 1,2,3,4,5,6,7,8 --task binary_up_down --n-permutations 10
python software/phase0_decode/scripts/run_csp_lda.py \
  --subjects 1,2,3,4,5,6,7,8 --task 4class --n-permutations 10
```
