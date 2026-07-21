# Log: 2026-07-20 — Cap-5GB multi-subject baseline

## Constraint

User limit: do **not** download the full dataset; keep ≤ **5 GB** of trial data.

## Why not Raw_data_download_tutorial.py for this pull

`Raw_data_download_tutorial.py` uses `get_raw_eeg()` (DataLad) to fetch raw `.bdf` files.

- Each raw session is ~0.65–0.77 GB.
- Full raw set (~30 files) is ~20 GB.
- Within 5 GB, raw would cover only ~6–7 sessions (~2 subjects).
- Phase 0 classification needs epoched derivatives (`*_eeg-epo.fif` + `*_events.dat`), so raw would also require a full preprocess pass.
- `git-annex` could not be installed via Homebrew (permissions), so the DataLad path was blocked.

Decision for this run: download **preprocessed derivatives** from the same OpenNeuro dataset (`ds003626`) with a hard size cap.

Script: `software/phase0_decode/scripts/download_derivatives_capped.py`

## Download result

| Item | Value |
|---|---|
| Destination | `projects/ds003626/` |
| Subjects materialized | **sub-01 … sub-08** |
| Stopped before | sub-09 (would exceed budget) |
| Final on-disk size | **~5.1 GB** (slightly over due to S3 size estimate vs GiB) |
| Files | 24 `eeg-epo.fif` + matching `events.dat` |

## Tests run

Method unchanged: log band-power (1.5–3.5 s) + linear SVM, leave-session-out, inner speech only.

### Pooled subjects 1–8

| Task | Trials | Balanced acc | Chance | Perm p |
|---|---:|---:|---:|---:|
| Binary up/down | 878 | **0.476** | 0.50 | 0.90 |
| 4-class | 1756 | **0.243** | 0.25 | 0.77 |

Runs:

- `results/phase-0/runs/20260720T201944Z_binary_up_down_sub1-2-3-4-5-6-7-8/`
- `results/phase-0/runs/20260720T202016Z_4class_sub1-2-3-4-5-6-7-8/`

## Interpretation

1. Size-capped multi-subject data is available and the pipeline scales.
2. Pooled band-power + linear SVM is **at chance** across 8 subjects.
3. Earlier single-subject weak/edge results do **not** generalize under this pooled leave-session-out setup.
4. Next methods (SVD, CSP, subject-specific models) are now justified; more raw/full-data download is not the bottleneck.

## Reproduce

```bash
source .venv/bin/activate
python software/phase0_decode/scripts/download_derivatives_capped.py --max-gb 5.0
python software/phase0_decode/scripts/run_bandpower_svm.py \
  --subjects 1,2,3,4,5,6,7,8 --task binary_up_down --n-permutations 30
python software/phase0_decode/scripts/run_bandpower_svm.py \
  --subjects 1,2,3,4,5,6,7,8 --task 4class --n-permutations 30
```
