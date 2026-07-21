# Evidence: Invasive Speech Restoration Works — NORT Stays Non-Invasive

## Confirmed public evidence

Neuralink is running a clinical speech-restoration program:

- Product/trial page: [Neuralink Speech Restoration](https://neuralink.com/trials/speech-restoration/)
- ClinicalTrials.gov: [VOICE / NCT07224256](https://clinicaltrials.gov/study/NCT07224256)

What that establishes for NORT:

1. **Speech restoration from cortical signals is a real clinical objective**, not science fiction.
2. The N1 implant is designed to help people with severe speech impairment output verbal thought as **text or speech**.
3. The VOICE study targets adults with severe speech impairment and impaired upper-limb function from ALS, PLS, spinal cord injury, or stroke.
4. Public demos and reporting describe decoding toward phonemes/words and synthesized speech in implanted participants. This is early feasibility work, not a finished product.

Useful framing of how invasive systems work:

- Spoken language activates cortical speech networks that normally drive mouth, tongue, and larynx.
- When those motor pathways fail, a BCI can still read cortically generated intent signals.
- High-bandwidth implanted electrodes give spatial and temporal resolution that scalp EEG does not have.

## What this does *not* prove for NORT

| Claim | Status for NORT |
|---|---|
| Thought-to-speech is possible with invasive BCI | Supported directionally by invasive clinical work |
| The same performance is available from temple EEG | **Not supported** |
| Open-vocabulary continuous speech from non-invasive EEG is solved | **Not supported** |
| Neuralink methods/data can be reused directly | **No** — proprietary implant, different signal modality |

Invasive success raises the **ceiling of the problem class**. It does not transfer SNR, channel count, or spatial resolution to a non-invasive temple device.

## NORT scope boundary (locked for Phase 0 / Phase 1)

- **Modality:** non-invasive only (EEG ± sEMG witnesses).
- **Near-term software target:** offline classification of constrained inner-speech commands on public EEG data.
- **Near-term hardware target:** Phase 1 signal-quality wearable, not decoding claims.
- **Clinical claims:** none until ethics-approved studies and honest held-out evaluation exist.

## Implication for software design

Phase 0 should learn from invasive speech BCI *architecture ideas* (phoneme/word targets, calibration, latency budgets, confidence gating) while optimizing for the non-invasive reality:

- Low SNR
- Strong eye/muscle confounds
- Subject-specific models
- Small vocabularies first (2–4 commands), not open vocabulary
