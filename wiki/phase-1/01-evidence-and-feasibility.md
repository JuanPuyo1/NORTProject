# NORT Phase 1: Evidence and Feasibility Brief

## Purpose

NORT's long-term goal is a non-invasive assistive communication system that turns intended or inner speech into audible speech. Phase 1 has a narrower purpose: determine whether a small, repeatable temple/behind-ear wearable can acquire stable local biopotential signals and transmit them reliably.

Phase 1 is a research instrument. It is not a medical device, diagnostic system, ALS communication aid, or demonstration of thought-to-speech decoding.

## What the supplied paper establishes

The supplied reference is:

- Nieto et al., “Thinking out loud, an open-access EEG-based BCI dataset for inner speech recognition,” *Scientific Data* 9, 52 (2022), [DOI 10.1038/s41597-022-01147-2](https://doi.org/10.1038/s41597-022-01147-2).

Its acquisition setup and dataset include:

- 10 healthy, BCI-naive, native Spanish-speaking participants.
- A BioSemi ActiveTwo system with 128 active scalp EEG channels and 8 external EOG/EMG channels.
- 24-bit acquisition at 1024 samples/s in an electrically shielded room.
- Gel electrodes in a fixed high-density cap, with linked earlobes used for offline reference.
- Four prompted direction words: *arriba*, *abajo*, *derecha*, and *izquierda*.
- Three conditions: inner speech, overt speech, and visualized directional movement.
- 5,640 trials and more than nine hours of recordings.

The temple electrodes in the study were external EOG channels intended to capture horizontal eye movement. They were not validated as temple EEG channels for speech decoding. Mouth electrodes were used to detect EMG contamination.

The paper validates the dataset using attention checks, event-related responses, spectral analysis, and artifact controls. It does not report a classifier accuracy, online decoding result, information-transfer rate, or sparse-channel analysis. The authors explicitly note uncertainty about whether imagined and inner speech are distinguishable with current EEG and whether participants performed the intended mental activity consistently.

## What the paper does not justify

The reference cannot support any of the following claims:

- A few temple electrodes can decode inner speech.
- Free-form or continuous thought can be translated into text or speech.
- Inner-speech features can be separated from eye and muscle activity at the temple.
- Performance from 128-channel laboratory EEG will transfer to a small wearable.
- A model trained on healthy participants will work for people with ALS.

Any temple-only NORT result is therefore a new hypothesis, not a miniaturized reproduction of the paper.

## Current technical evidence

Non-invasive imagined-speech research shows above-chance results in constrained tasks, but generally relies on many channels, subject-specific calibration, controlled cues, and offline analysis. Cross-person and cross-session generalization remain weak. Open-vocabulary claims must be treated cautiously because language-model priors can produce plausible output from limited neural information.

Relevant context:

- The CHISCO imagined-speech dataset uses high-density EEG and extensive preprocessing: [Scientific Data, 2024](https://www.nature.com/articles/s41597-024-04114-1).
- A recent systematic review highlights inconsistent protocols, small datasets, artifact contamination, and limited generalization: [Sensors, 2024](https://www.mdpi.com/1424-8220/24/24/8168).
- Ear-centered EEG can capture useful signals but generally at lower amplitude and signal-to-noise ratio than scalp EEG: [Frontiers, 2017](https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2017.00163/full).
- A five-class speech-imagery comparison reported lower average performance for ear EEG than 32-channel scalp EEG, while remaining above chance: [Journal of Neural Engineering, 2021](https://iopscience.iop.org/article/10.1088/1741-2552/abd10e).

These results make ear/temple sensing a plausible low-bandwidth research direction, but not evidence for continuous speech reconstruction.

## Why EEG and sEMG must be recorded together

Signals near the temple contain a mixture of:

- Local scalp EEG.
- Horizontal eye movement and blink activity.
- Temporalis and masseter muscle activity.
- Facial and jaw movement.
- Motion artifacts, electrode movement, and mains interference.

Muscle signals are often much larger than scalp EEG. A successful classifier using temple signals could therefore be detecting subtle articulation rather than brain activity.

Phase 1 intentionally treats this mixture as a measurement problem:

- Local EEG channels test whether repeatable low-amplitude activity can be acquired.
- A dedicated temporalis/jaw sEMG channel acts as an artifact witness and possible assistive input.
- An inertial sensor records head and device motion.
- Later experiments must compare EEG-only, sEMG-only, and combined models.

sEMG may provide a useful silent-speech interface sooner than EEG, but it is not inner speech and may become unavailable as ALS progresses. It must not be mislabeled as neural decoding.

## Electrode and form-factor evidence

For the first build, pre-gelled Ag/AgCl contacts are preferred over dry electrodes because they provide lower and more stable skin-electrode impedance on hairless skin.

A practical architecture is:

- Reusable electronics pod positioned at the temple/behind the ear.
- Replaceable flexible adhesive tail carrying 4–6 Ag/AgCl hydrogel contacts.
- Local differential contacts around the temple/behind ear.
- Separate reference and bias/ground contacts.
- One lower contact or bipolar pair oriented toward temporalis or jaw activity.

Dry electrodes may reduce consumables later, but they introduce higher impedance, pressure sensitivity, motion artifacts, and greater analog-front-end requirements. They should be evaluated only after the hydrogel configuration establishes a signal baseline.

## Electronics feasibility

An ADS1299-class analog front end is a credible reference architecture:

- 4, 6, or 8 simultaneous 24-bit channels.
- Programmable gain and EEG-oriented input performance.
- 250 samples/s to 16 ksamples/s.
- Integrated lead-off and bias functions.
- Approximately 5 mW per enabled channel.

Reference: [Texas Instruments ADS1299](https://www.ti.com/product/ADS1299).

Important constraint: the ADS1299 analog supply requires approximately 5 V; 3.3 V is not a valid analog supply. The prototype power tree must therefore include a low-noise regulated/boosted analog rail and must be reviewed for switching noise.

At 4 channels, 1,000 samples/s, and 24 bits/sample, the raw sample payload is 96 kbit/s before packet overhead. BLE 5 can carry this when notifications, data-length extension, batching, sequence numbers, and suitable connection parameters are used. Local buffering remains necessary because phone BLE behavior is not deterministic.

## Safety and regulatory boundary

Body-connected biopotential electronics create electrical, thermal, battery, skin-contact, and data risks even when used only for research.

Phase 1 must be:

- Battery-powered while attached to a person.
- Electrically unable to record while charging or connected to USB/debug equipment.
- Bench-tested with shorted inputs and a biopotential simulator before body contact.
- Protected against electrode-input current, ESD, battery faults, and overheating.
- Built with skin-contact materials having supplier biocompatibility information.
- Reviewed by a qualified electrical/biomedical engineer before human use.

Future product development will need risk management and testing informed by IEC 60601-1, IEC 60601-1-2, IEC 80601-2-26, IEC 60601-1-11, IEC 62133-2, ISO 14971, and ISO 10993. Designing with these standards in mind does not make the prototype compliant.

## Phase 1 hypothesis and decision

The Phase 1 hypothesis is:

> A single reusable temple/behind-ear pod with a replaceable hydrogel electrode tail can record stable, distinguishable local EEG, sEMG, and artifact signatures for 30–60 minutes while streaming complete timestamped data over BLE.

The hypothesis is supported only if the device passes the objective acquisition tests defined in the Phase 1 requirements and review checklist.

Phase 1 deliberately does not test word decoding. Its result determines the next architecture:

- Retain one pod if signal stability and spatial information are adequate.
- Add a synchronized second pod if bilateral information is justified.
- Return to a wider scalp montage if local EEG is too weak or inseparable from artifacts.

Miniaturization must follow measured signal utility rather than precede it.
