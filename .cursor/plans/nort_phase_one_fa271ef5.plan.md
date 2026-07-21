---
name: NORT Phase One
overview: Define a research-only, module-based single temple/ear wearable that safely streams stable EEG+sEMG data, then produce a precise Blueprint prompt and engineering review checklist. This phase validates acquisition and form-factor assumptions; it does not attempt inner-speech decoding or make clinical claims.
todos:
  - id: evidence-brief
    content: Create the evidence and feasibility brief from the supplied paper and current wearable EEG constraints.
    status: completed
  - id: phase1-prd
    content: Write the single-pod module-based Prototype 1 requirements, architecture, safety boundaries, and acceptance criteria.
    status: completed
  - id: blueprint-prompt
    content: Generate the detailed copy-paste Blueprint prompt plus a shorter iteration prompt.
    status: completed
  - id: review-gate
    content: Create the engineering review, bench-test, and go/no-go checklist for evaluating Blueprint's output.
    status: completed
isProject: false
---

# NORT Phase 1: Signal-Quality Wearable

## Evidence and scope
- Summarize what [`/Users/estebanpuyo/NORT/raw/s41597-022-01147-2.pdf`](/Users/estebanpuyo/NORT/raw/s41597-022-01147-2.pdf) demonstrates: 128-channel gel EEG, 8 auxiliary channels, 1024 Hz acquisition, four prompted commands, and substantial uncertainty around distinguishable inner-speech features.
- Explicitly separate the long-term ALS communication vision from Prototype 1's claim: a research instrument for stable local EEG+sEMG acquisition, not a diagnostic or communication device.
- Record the central hypothesis: a single temple/behind-ear montage may provide useful local neural signals, but temple signals will also contain strong eye and temporalis/jaw muscle activity that must be measured rather than silently treated as EEG.

## Prototype requirements
- Specify one reusable temple/behind-ear electronics pod using off-the-shelf modules, attached to a replaceable flexible adhesive electrode tail.
- Use approximately 4–6 Ag/AgCl hydrogel contacts: local differential EEG contacts around the temple/behind ear, reference and bias contacts, and a lower temporalis/jaw contact for sEMG.
- Target a 24-bit EEG-oriented analog front end, 500–1000 samples/s per channel, local timestamps, BLE streaming, electrode-contact/lead-off indication, motion sensing, and optional local buffering.
- Define a rechargeable protected Li-ion/LiPo supply and smart-ring-style storage/charging case using dock contacts for the first build. Enforce battery-only operation while worn, a sensing/charging interlock, protected electrode inputs, and no USB or mains connection during body contact.
- Keep the communications protocol compatible with adding a second synchronized pod later without making bilateral hardware part of Prototype 1.

## Blueprint prompt package
- Produce a copy-paste Blueprint prompt describing the user goal, module-level architecture, signal chain, electrode layout, power tree, BLE packet contents, mechanical envelope, replaceable adhesive interface, charging dock, assembly sequence, and required outputs: BOM, wiring, mechanical concept, and verification steps.
- Tell Blueprint to prefer purchasable evaluation/modules over a custom PCB, show voltage and current budgets, identify unsupported assumptions, and avoid claiming medical-grade or speech-decoding capability.
- Include explicit exclusions: no stimulation, no charging while worn, no exposed mains path, no autonomous diagnosis, and no patient/ALS testing in this phase.

## Verification and decision gate
- Create a review checklist covering schematic correctness, ADS1299-class supply requirements, input protection/leakage risk, battery protection, RF coexistence, electrode materials, skin-contact risks, and BLE bandwidth.
- Define bench-first tests using an EEG/biopotential simulator before body contact, followed only after qualified review by limited healthy-adult feasibility work under an appropriate consent/ethics process.
- Set Phase 1 acceptance criteria: 30–60 minutes of continuous streaming, no dropped data beyond a stated threshold, synchronized timestamps and event markers, measurable contact quality, no unsafe heating, and separable recordings for rest, eye movement, jaw contraction, and overt speech. Inner-speech classification remains a later gate.
- Document the next decision: retain the single pod, add a second pod, or return to a broader scalp montage based on measured signal quality—not industrial-design preference.