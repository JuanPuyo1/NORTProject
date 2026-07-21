# Findings Report: Phase 0 Classical Decoding Ladder

**Date:** 2026-07-20  
**Dataset:** OpenNeuro ds003626 (Nieto et al. Inner Speech EEG), subjects 01–08  
**Condition:** inner speech only  
**Split:** leave-session-out (train on 2 sessions, test on held-out session), per subject  
**Null:** 10 within-session label permutations per subject (CSP/FBCSP)  
**Window:** 1.5–3.5 s after cue  

---

## Verdict

Across four classical methods (band-power, CSP, FBCSP, Riemannian), **leave-session-out inner-speech decoding remains at or near chance** on this setup. Filter Bank CSP gives the best binary mean so far, but **no subject reaches a significant permutation result**, and 4-class stays indistinguishable from chance. Classical spatial/spectral/geometry pipelines are not yet a usable decoder for NORT’s offline command task.

> **Update:** Truncated SVD+SVM was run later the same day and is also near chance. Superseding summary: [`2026-07-20-phase-0-classical-ladder-final.md`](2026-07-20-phase-0-classical-ladder-final.md).

---

## Methods compared

| # | Method | Script | Key knobs |
|---|---|---|---|
| 1 | Log band-power + linear SVM | `run_bandpower_svm.py` | 5 bands × 128 ch; pooled LSO |
| 2 | Single-band CSP + LDA | `run_csp_lda.py` | 8–30 Hz; 6 CSP comps; subject LSO |
| 3 | FBCSP + SelectKBest + LDA | `run_fbcsp_lda.py` | 7×4 Hz bands (4–32 Hz); 4 CSP/band; top-10/16 features |
| 4 | **Riemannian TS + LDA** | `run_riemann.py` | PCA→20; OAS cov; tangent space + LDA |

---

## Results summary

### Binary (arriba vs abajo) — chance = 0.50

| Method | Mean subject bal.acc | Pooled bal.acc | Best subject |
|---|---:|---:|---|
| Band-power + SVM | — (pooled only) | 0.476 | — |
| CSP + LDA | 0.506 ± 0.045 | 0.502 | sub-03 = 0.611 (p≈0.09) |
| **FBCSP + LDA** | **0.541 ± 0.038** | **0.539** | sub-01 = 0.600 (p≈0.09) |
| Riemannian TS+LDA | 0.505 ± 0.040 | 0.505 | sub-08 = 0.570 (p≈0.09) |

### 4-class — chance = 0.25

| Method | Mean subject bal.acc | Pooled bal.acc | Best subject |
|---|---:|---:|---|
| Band-power + SVM | — | 0.243 | — |
| CSP + LDA | 0.267 ± 0.045 | 0.264 | sub-03 = 0.361 (p≈0.18) |
| FBCSP + LDA | 0.259 ± 0.022 | 0.259 | sub-02 = 0.296 (p≈0.18) |
| Riemannian TS+LDA | 0.253 ± 0.030 | 0.254 | sub-02 = 0.300 (p≈0.09) |

### FBCSP per-subject detail

**Binary**

| Subject | bal.acc | p (≥ observed) |
|---|---:|---:|
| 01 | 0.600 | 0.09 |
| 02 | 0.550 | 0.27 |
| 03 | 0.567 | 0.27 |
| 04 | 0.467 | 0.82 |
| 05 | 0.508 | 0.64 |
| 06 | 0.546 | 0.55 |
| 07 | 0.558 | 0.36 |
| 08 | 0.530 | 0.45 |

**4-class**

| Subject | bal.acc | p (≥ observed) |
|---|---:|---:|
| 01 | 0.265 | 0.36 |
| 02 | 0.296 | 0.18 |
| 03 | 0.278 | 0.36 |
| 04 | 0.263 | 0.36 |
| 05 | 0.221 | 0.73 |
| 06 | 0.241 | 0.55 |
| 07 | 0.267 | 0.27 |
| 08 | 0.245 | 0.64 |

Runs:

- `results/phase-0/runs/20260720T214504Z_fbcsp_lda_binary_up_down_sub1-2-3-4-5-6-7-8/`
- `results/phase-0/runs/20260720T214706Z_fbcsp_lda_4class_sub1-2-3-4-5-6-7-8/`

---

## Interpretation

1. **FBCSP is the strongest classical binary so far** (~+3–4 pp over CSP mean), but still ~4 pp above chance and **not permutation-significant** for any subject under n=10.
2. **4-class does not improve** with FBCSP vs CSP; variance is smaller, mean closer to chance — consistent with no recoverable class structure under LSO.
3. Failure is **method-family-wide** among Tier A spatial/spectral tools tried (band-power, CSP, FBCSP), not a single bad feature choice.
4. Likely bottlenecks remain: **weak / non-stationary inner-speech signal in scalp EEG**, session drift, and possible need for **artifact/EMG controls** before claiming neural decoding.
5. A ~0.54 binary mean is **not** evidence of a working product decoder; treat as a negative but informative ladder step.

---

## What this means for NORT

| Question | Answer from this ladder |
|---|---|
| Can classical EEG BCI recipes decode 4 direction words offline? | **Not yet** on ds003626 under honest LSO |
| Is more of the same (another CSP variant) justified? | **Low priority** — diminishing returns |
| Is Phase 1 (acquisition wearable) blocked? | **No** — Phase 1 success is stable streaming, not decoding |
| What should software try next? | See below |

---

## Recommended next steps (priority order)

1. ~~**Truncated SVD on band-power → SVM**~~ — **done** (near chance; see `2026-07-20-phase-0-svd-svm.md` and final report `2026-07-20-phase-0-classical-ladder-final.md`).
2. **Subject-specific EEGNet** (small, regularized) — Tier A/B remain near chance; watch overfitting.
3. **Artifact / EXG ablations** — train with high-EMG trials removed; check if any lift collapses to muscle.
4. **Do not** expand dataset download as the next lever — data volume is not the current bottleneck.
5. Riemannian log: `wiki/logs/2026-07-20-phase-0-riemann.md`

---

## Reproduce FBCSP

```bash
source .venv/bin/activate
export PYTHONUNBUFFERED=1 MPLCONFIGDIR=/tmp/mpl-nort
python software/phase0_decode/scripts/run_fbcsp_lda.py \
  --subjects 1,2,3,4,5,6,7,8 --task binary_up_down --n-permutations 10
python software/phase0_decode/scripts/run_fbcsp_lda.py \
  --subjects 1,2,3,4,5,6,7,8 --task 4class --n-permutations 10
```

---

## Related logs

- Band-power multi-subject: `wiki/logs/2026-07-20-phase-0-5gb-multisubject.md`
- CSP + LDA: `wiki/logs/2026-07-20-phase-0-csp-lda.md`
- Method ladder: `wiki/phase-0/03-decoding-methods-svd-alternatives.md`
