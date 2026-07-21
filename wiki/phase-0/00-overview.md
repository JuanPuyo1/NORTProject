# NORT Phase 0: Software Decoding Backbone

## Purpose

Phase 0 is a **code-only** workstream. It builds and tests the software that will later decode speech-related neural signals, before the wearable hardware from Phase 1 is ready.

Primary goals:

1. Confirm the scientific boundary: invasive speech BCIs can work; NORT remains non-invasive.
2. Stand up a reproducible pipeline on the Nieto Inner Speech EEG dataset.
3. Decide whether TribeV2 is useful, and how, for NORT.
4. Compare classical and deep decoding methods, including SVD-based approaches.
5. Keep durable project logs of decisions and experiment outcomes.

## Relation to Phase 1

| Track | Focus | Dependency |
|---|---|---|
| Phase 0 | Offline EEG decoding software | Open datasets only |
| Phase 1 | Wearable acquisition hardware | Signal quality first |
| Later | Wearable + decoder integration | Both phases must pass gates |

Phase 0 does **not** claim ALS-ready communication, real-time speech synthesis, or medical validation.

## Success criteria

- Reproducible download and load of Inner Speech derivatives.
- End-to-end training script with subject-wise and session-wise splits.
- Logged baseline accuracies for at least one classical and one deep model.
- Explicit decision on TribeV2: use, defer, or discard for Phase 0.
- Documented method comparison including SVD/PCA/CSP.

## Document index

- [01 Evidence and non-invasive boundary](01-evidence-neuralink-boundary.md)
- [02 Datasets and TribeV2 assessment](02-datasets-and-tribev2.md)
- [03 Decoding methods including SVD](03-decoding-methods-svd-alternatives.md)
- [04 Software backbone plan](04-software-backbone-plan.md)
- [05 First baseline run](05-first-baseline-run.md)
- Project logs: [`../logs/`](../logs/)
  - **Classical ladder final report:** `2026-07-20-phase-0-classical-ladder-final.md`
  - CSP+LDA: `2026-07-20-phase-0-csp-lda.md`
  - FBCSP findings report: `2026-07-20-phase-0-fbcsp-findings.md`
  - Riemannian TS+LDA: `2026-07-20-phase-0-riemann.md`
  - Truncated SVD+SVM: `2026-07-20-phase-0-svd-svm.md`
  - EEGNet: `2026-07-21-phase-0-eegnet.md`
