# Datasets and TribeV2 Assessment

## Primary dataset: Inner Speech (Nieto et al., 2022)

Local code checkout:

- [`projects/Inner_Speech_Dataset/`](../../projects/Inner_Speech_Dataset/)

Source paper / data:

- Paper: [Scientific Data, 2022](https://www.nature.com/articles/s41597-022-01147-2)
- OpenNeuro: [ds003626](https://openneuro.org/datasets/ds003626)
- Companion repo: [N-Nieto/Inner_Speech_Dataset](https://github.com/N-Nieto/Inner_Speech_Dataset)

### What we have today

| Asset | Status (2026-07-20) |
|---|---|
| Processing / download scripts | Present under `projects/Inner_Speech_Dataset/` |
| Exploration notebook with basic SVM tutorial | Present (`Database_exploration_tutorial.ipynb`) |
| Actual `ds003626` EEG files | **Not downloaded yet** |

The scripts expect data beside or above the repo as `ds003626/` with raw and/or `derivatives/`. Until derivatives are downloaded, no classification numbers can be trusted as project baselines.

### Recommended first download

From `projects/Inner_Speech_Dataset/`, use the derivatives helper for ML work:

```bash
conda env create -f environment.yml
conda activate inner_speech
# Prefer EEG + events only for the first ML pass
python Derivatives_download_tutorial.py   # edit to file_types=["eeg","events"]
```

Target structure after download:

```text
projects/ds003626/derivatives/sub-XX/ses-YY/
  sub-XX_ses-YY_eeg-epo.fif
  sub-XX_ses-YY_events.dat
  sub-XX_ses-YY_exg-epo.fif   # EOG/EMG witnesses — keep for artifact gates
```

### Task definition for Phase 0

Use the paper's labels:

- Conditions: inner speech (primary), pronounced speech, visualized
- Classes: arriba / abajo / derecha / izquierda
- Action window often used for features: ~1.5–3.5 s after cue
- Chance for 4-class balanced: 25%; binary: 50%

Mandatory evaluation rules:

- Prefer **leave-session-out** or **leave-subject-out**, not random trial splits of neighboring epochs.
- Always report a **visualized-condition negative control** and an **sEMG/EOG contamination check**.
- Log balanced accuracy, confusion matrix, and permutation chance.

The repo notebook already shows a simple SVM path and mentions CSP as a next feature method. That is the correct starting point for Phase 0 code.

## Secondary import: TribeV2

Local checkout:

- [`projects/tribev2/`](../../projects/tribev2/)

What TribeV2 actually is ([Meta TRIBE v2](https://ai.meta.com/blog/tribe-v2-brain-predictive-foundation-model/), [GitHub](https://github.com/facebookresearch/tribev2)):

- A **multimodal fMRI encoding** model: stimulus (video/audio/text) → predicted cortical fMRI responses.
- Not an EEG decoder.
- Not trained to classify the Nieto inner-speech classes.
- License: **CC BY-NC 4.0** (non-commercial research use).

### Can we test with TribeV2?

Yes, but only for **encoding / region-prior experiments**, not as the Phase 0 classifier.

Practical tests that are useful:

1. **Speech-ROI prior:** feed the four Spanish direction words (as text/audio) into TribeV2 and inspect which cortical vertices/ROIs activate most. Use that as a soft prior when selecting EEG channel subsets later.
2. **Condition contrast sanity check:** compare predicted responses for speech-like text versus non-speech control text; confirm language/auditory ROIs dominate.
3. **Bridge experiment (advanced):** project EEG spatial patterns onto approximate scalp/ROI maps and ask whether high-weight EEG channels overlap TribeV2 speech ROIs. This is hypothesis generation only.

What TribeV2 cannot do for Phase 0:

- Ingest `eeg-epo.fif` and output word labels.
- Replace CSP/EEGNet/SVM baselines on ds003626.
- Prove temple-EEG sufficiency.
- Provide a commercial product component without license review (NC license).

### Is TribeV2 an advantage?

**Conditional yes — as a neuroscience prior tool, not as the decoder backbone.**

| Use | Advantage | Cost / risk |
|---|---|---|
| ROI / language-network priors | Better channel-selection hypotheses | GPU, HF auth for some encoders, NC license |
| Demo of “brain response to speech stimuli” | Good internal intuition / investor science story | Easy to overclaim |
| Direct EEG decoding | None | Misleading architecture choice |

**Phase 0 decision:** keep TribeV2 as an optional **prior/analysis sidecar**. Build the speech-decoding backbone on Inner Speech EEG + classical/deep EEG methods. Revisit TribeV2 after a first honest 4-class baseline exists.

## Other datasets to consider later

Not required for the first backbone, but useful for generalization:

- CHISCO imagined-speech EEG (high density, sentence-level)
- Earlier imagined-speech open sets reviewed in the 2024 systematic review literature

Do not expand datasets until the Nieto pipeline is reproducible end-to-end.
