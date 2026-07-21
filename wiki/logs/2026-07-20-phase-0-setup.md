# Log: 2026-07-20 — Phase 0 setup

## Actions taken

- Created `wiki/phase-0/` for the software decoding backbone workstream.
- Created `wiki/logs/` for durable project decision logs.
- Created `results/phase-0/` for future experiment outputs.
- Documented Neuralink speech-restoration evidence and locked NORT as non-invasive.
- Inspected `projects/Inner_Speech_Dataset/` and `projects/tribev2/`.
- Recorded that OpenNeuro `ds003626` files are **not yet downloaded**.
- Assessed TribeV2 as an fMRI encoding model (stimulus→brain), not an EEG decoder.
- Documented decoding alternatives including SVD/PCA/CSP/EEGNet and a method ladder.

## Key decisions

1. Phase 0 is code-only and uses public EEG data before wearable integration.
2. Primary dataset = Nieto Inner Speech (ds003626).
3. TribeV2 = optional neuroscience prior / ROI sidecar; not the Phase 0 classifier.
4. SVD is useful for dimensionality reduction and QC; CSP + classical classifiers + EEGNet form the main ladder.
5. First engineering step after docs: download derivatives and reproduce a logged SVM baseline.

## Evidence cited

- https://neuralink.com/trials/speech-restoration/
- https://clinicaltrials.gov/study/NCT07224256
- https://www.nature.com/articles/s41597-022-01147-2
- https://openneuro.org/datasets/ds003626
- https://github.com/facebookresearch/tribev2
- https://ai.meta.com/blog/tribe-v2-brain-predictive-foundation-model/

## Open items (updated later same day)

- Initial annex tree was incomplete; real sub-01 derivatives downloaded to `projects/ds003626/`.
- First baseline implemented and run: see `2026-07-20-phase-0-first-baseline.md`.
- Still need remaining subjects and SVD/CSP comparisons.
