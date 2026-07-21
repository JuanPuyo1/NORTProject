# Final Report: Phase 0 Classical Decoding Ladder

**Date:** 2026-07-20  
**Dataset:** OpenNeuro ds003626 (Nieto et al. Inner Speech EEG), subjects 01–08  
**Condition:** inner speech only  
**Split:** leave-session-out (train on 2 sessions, test on held-out session), per subject  
*(Band-power + SVM reported as pooled multi-subject LSO for historical comparison)*  
**Null:** 10 within-session label permutations per subject (CSP / FBCSP / Riemannian / SVD)  
**Window:** 1.5–3.5 s after cue  

---

## Verdict

Across **five classical methods** (band-power SVM, CSP, FBCSP, Riemannian, Truncated SVD+SVM), **leave-session-out inner-speech decoding remains at or near chance** on this setup. Filter Bank CSP is still the strongest binary mean (~0.54), but **no subject reaches a significant permutation result** under n=10, and 4-class stays indistinguishable from chance. Unsupervised SVD compression of band-power features does not help. Classical Tier A/B spatial / spectral / geometry / PCA pipelines are **not a usable offline command decoder** for NORT yet.

---

## Methods compared

| # | Method | Script | Key knobs |
|---|---|---|---|
| 1 | Log band-power + linear SVM | `run_bandpower_svm.py` | 5 bands × 128 ch; pooled LSO |
| 2 | Single-band CSP + LDA | `run_csp_lda.py` | 8–30 Hz; 6 CSP comps; subject LSO |
| 3 | FBCSP + SelectKBest + LDA | `run_fbcsp_lda.py` | 7×4 Hz bands (4–32 Hz); 4 CSP/band; top-10/16 features |
| 4 | Riemannian TS + LDA | `run_riemann.py` | PCA→20; OAS cov; tangent space + LDA |
| 5 | **Truncated SVD + SVM** | `run_svd_svm.py` | Band-power → TruncatedSVD(k=32) → linear SVM; k-sweep 8/16/32/64 |

---

## Results summary

### Binary (arriba vs abajo) — chance = 0.50

| Method | Mean subject bal.acc | Pooled bal.acc | Best subject |
|---|---:|---:|---|
| Band-power + SVM | — (pooled only) | 0.476 | — |
| CSP + LDA | 0.506 ± 0.045 | 0.502 | sub-03 = 0.611 (p≈0.09) |
| **FBCSP + LDA** | **0.541 ± 0.038** | **0.539** | sub-01 = 0.600 (p≈0.09) |
| Riemannian TS+LDA | 0.505 ± 0.040 | 0.505 | sub-08 = 0.570 (p≈0.09) |
| SVD + SVM (k=32) | 0.508 ± 0.058 | 0.505 | sub-08 = 0.570 (p≈0.09) |

### 4-class — chance = 0.25

| Method | Mean subject bal.acc | Pooled bal.acc | Best subject |
|---|---:|---:|---|
| Band-power + SVM | — | 0.243 | — |
| CSP + LDA | 0.267 ± 0.045 | 0.264 | sub-03 = 0.361 (p≈0.18) |
| FBCSP + LDA | 0.259 ± 0.022 | 0.259 | sub-02 = 0.296 (p≈0.18) |
| Riemannian TS+LDA | 0.253 ± 0.030 | 0.254 | sub-02 = 0.300 (p≈0.09) |
| SVD + SVM (k=32) | 0.253 ± 0.023 | 0.252 | sub-01 = 0.285 (p≈0.09) |

### SVD rank sweep (mean subject bal.acc)

| k | Binary | 4-class |
|---:|---:|---:|
| 8 | 0.531 ± 0.032 | 0.269 ± 0.028 |
| 16 | 0.491 ± 0.041 | 0.249 ± 0.038 |
| 32 | 0.508 ± 0.058 | 0.253 ± 0.023 |
| 64 | 0.513 ± 0.051 | 0.277 ± 0.020 |

At k=32, train-fold SVD retains ~84–95% of band-power feature variance — compression works; class separation does not.

### SVD per-subject detail (k=32)

**Binary**

| Subject | bal.acc | p (≥ observed) |
|---|---:|---:|
| 01 | 0.560 | 0.18 |
| 02 | 0.550 | 0.27 |
| 03 | 0.522 | 0.55 |
| 04 | 0.475 | 0.73 |
| 05 | 0.475 | 1.00 |
| 06 | 0.528 | 0.36 |
| 07 | 0.383 | 1.00 |
| 08 | 0.570 | 0.09 |

**4-class**

| Subject | bal.acc | p (≥ observed) |
|---|---:|---:|
| 01 | 0.285 | 0.09 |
| 02 | 0.258 | 0.36 |
| 03 | 0.239 | 0.64 |
| 04 | 0.208 | 0.91 |
| 05 | 0.271 | 0.45 |
| 06 | 0.273 | 0.18 |
| 07 | 0.233 | 0.64 |
| 08 | 0.255 | 0.45 |

Runs:

- `results/phase-0/runs/20260720T224604Z_svd_svm_k32_binary_up_down_sub1-2-3-4-5-6-7-8/`
- `results/phase-0/runs/20260720T224628Z_svd_svm_k32_4class_sub1-2-3-4-5-6-7-8/`

---

## Interpretation

1. **Failure is method-family-wide** among Tier A/B tools tried — not a single bad feature choice.
2. **FBCSP remains the best classical binary** (~+3–4 pp over CSP/SVD/Riemann), still non-significant.
3. **SVD QC conclusion:** unsupervised variance compression of band-power does not recover a decoder; the bottleneck is not collinear / high-dim features alone.
4. Likely bottlenecks remain: **weak / non-stationary inner-speech signal in scalp EEG**, session drift, and possible need for **artifact/EMG controls** before claiming neural decoding.
5. A ~0.54 binary mean is **not** evidence of a working product decoder.

---

## What this means for NORT

| Question | Answer from this ladder |
|---|---|
| Can classical EEG BCI recipes decode 4 direction words offline? | **Not yet** on ds003626 under honest LSO |
| Is more CSP / cov / PCA-SVD iteration justified? | **Low priority** — diminishing returns |
| Is Phase 1 (acquisition wearable) blocked? | **No** — Phase 1 success is stable streaming, not decoding |
| Is the classical Tier A/B ladder done enough? | **Yes** for go/no-go on these recipes |

---

## Recommended next steps (priority order)

1. ~~**Subject-specific EEGNet**~~ — **done** (near/below chance; see `2026-07-21-phase-0-eegnet.md`).
2. **Artifact / EXG ablations** — remove high-EMG trials; check if any lift collapses to muscle.
3. **Do not** expand dataset download as the next lever — data volume is not the current bottleneck.
4. Keep Phase 1 hardware work independent of decoder accuracy.

---

## Reproduce SVD + SVM

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

---

## Related logs

- Band-power multi-subject: `wiki/logs/2026-07-20-phase-0-5gb-multisubject.md`
- CSP + LDA: `wiki/logs/2026-07-20-phase-0-csp-lda.md`
- FBCSP findings (earlier snapshot): `wiki/logs/2026-07-20-phase-0-fbcsp-findings.md`
- Riemannian: `wiki/logs/2026-07-20-phase-0-riemann.md`
- SVD + SVM: `wiki/logs/2026-07-20-phase-0-svd-svm.md`
- Method ladder: `wiki/phase-0/03-decoding-methods-svd-alternatives.md`
