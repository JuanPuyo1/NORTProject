# Phase 0 results

Experiment outputs live under `runs/`.

## Final classical ladder report (2026-07-20)

Cross-method summary (band-power, CSP, FBCSP, Riemannian, **SVD+SVM**):  
[`wiki/logs/2026-07-20-phase-0-classical-ladder-final.md`](../../wiki/logs/2026-07-20-phase-0-classical-ladder-final.md)

**Verdict:** all five classical methods remain near chance under leave-session-out. FBCSP is best binary (~0.54); SVD compression does not rescue decoding.

## Latest: EEGNet-8,2 (subject-specific)

| Run | Task | Mean subject bal.acc | Chance | Pooled |
|---|---|---:|---:|---:|
| `20260720T232023Z_eegnet_binary_up_down_sub1-2-3-4-5-6-7-8` | binary | 0.486 ± 0.037 | 0.50 | 0.489 |
| `20260721T002728Z_eegnet_4class_sub1-2-3-4-5-6-7-8` | 4-class | 0.250 ± 0.010 | 0.25 | 0.250 |

At/below chance; does not beat FBCSP. Binary used 5 perms; 4-class observed-only (perm budget cut for wall-clock). Log: `wiki/logs/2026-07-21-phase-0-eegnet.md`

## Truncated SVD + SVM (band-power → SVD → SVM)

| Run | Task | Mean subject bal.acc | Chance | Pooled |
|---|---|---:|---:|---:|
| `20260720T224604Z_svd_svm_k32_binary_up_down_sub1-2-3-4-5-6-7-8` | binary | 0.508 ± 0.058 | 0.50 | 0.505 |
| `20260720T224628Z_svd_svm_k32_4class_sub1-2-3-4-5-6-7-8` | 4-class | 0.253 ± 0.023 | 0.25 | 0.252 |

At chance; k-sweep {8,16,32,64} does not escape chance. Log: `wiki/logs/2026-07-20-phase-0-svd-svm.md`

## Riemannian (PCA → OAS cov → TS + LDA)

| Run | Task | Mean subject bal.acc | Chance | Pooled |
|---|---|---:|---:|---:|
| `20260720T220457Z_riemann_ts_lda_binary_up_down_sub1-2-3-4-5-6-7-8` | binary | 0.505 ± 0.040 | 0.50 | 0.505 |
| `20260720T220609Z_riemann_ts_lda_4class_sub1-2-3-4-5-6-7-8` | 4-class | 0.253 ± 0.030 | 0.25 | 0.254 |

Log: `wiki/logs/2026-07-20-phase-0-riemann.md`

## FBCSP + SelectKBest + LDA

| Run | Task | Mean subject bal.acc | Chance | Pooled |
|---|---|---:|---:|---:|
| `20260720T214504Z_fbcsp_lda_binary_up_down_sub1-2-3-4-5-6-7-8` | binary | 0.541 ± 0.038 | 0.50 | 0.539 |
| `20260720T214706Z_fbcsp_lda_4class_sub1-2-3-4-5-6-7-8` | 4-class | 0.259 ± 0.022 | 0.25 | 0.259 |

Small binary lift vs CSP; still non-significant. Log: `wiki/logs/2026-07-20-phase-0-fbcsp-findings.md`

## CSP + LDA (subject-specific leave-session-out)

| Run | Task | Mean subject bal.acc | Chance | Pooled |
|---|---|---:|---:|---:|
| `20260720T210456Z_csp_lda_binary_up_down_sub1-2-3-4-5-6-7-8` | binary | 0.506 ± 0.045 | 0.50 | 0.502 |
| `20260720T210536Z_csp_lda_4class_sub1-2-3-4-5-6-7-8` | 4-class | 0.267 ± 0.045 | 0.25 | 0.264 |

Log: `wiki/logs/2026-07-20-phase-0-csp-lda.md`

## Size-capped multi-subject band-power + SVM (sub-01..08)

| Run | Task | Subjects | Balanced acc | Chance | p (perm) |
|---|---|---|---:|---:|---:|
| `20260720T201944Z_binary_up_down_sub1-2-3-4-5-6-7-8` | binary | 1–8 | 0.476 | 0.50 | 0.90 |
| `20260720T202016Z_4class_sub1-2-3-4-5-6-7-8` | 4-class | 1–8 | 0.243 | 0.25 | 0.77 |

## Earlier single-subject smoke (sub-01 only)

| Run | Task | Balanced acc | Chance | p (perm) |
|---|---|---:|---:|---:|
| `20260720T200639Z_binary_up_down_sub1` | binary | 0.550 | 0.50 | 0.157 |
| `20260720T200655Z_4class_sub1` | 4-class | 0.315 | 0.25 | 0.039 |

See also:

- `wiki/logs/2026-07-20-phase-0-5gb-multisubject.md`
- `wiki/logs/2026-07-20-phase-0-first-baseline.md`
