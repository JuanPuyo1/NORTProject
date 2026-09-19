# Log: 2026-08-04 — Project status, Phase 0/1 review, new literature, and next paths

**Author:** status synthesis (agent-assisted)  
**Scope:** Phase 0 decoding results, Phase 1 hardware docs, `raw/new/` papers, SVD options, `projects/Rethinking-Methods-Inner-Speech/`

---

## 1. Current project status (verdict)

| Track | Status | Gate |
|---|---|---|
| **Phase 0 — offline EEG decoding** | Classical ladder + EEGNet **done**; all near chance under leave-session-out | Decoder go/no-go on this recipe: **NO** |
| **Phase 1 — acquisition wearable** | Docs complete (evidence, PRD, Blueprint prompts, review gates); **no hardware build log yet** | Blueprint → engineering review → bench; decoding not required |
| **Integration** | Blocked on neither track alone | Needs Phase 1 signal quality *and* a later honest decoder |

**Bottom line:** NORT is correctly split. Software has shown that standard scalp-EEG inner-speech recipes on Nieto (ds003626, subjects 01–08, LSO) do not yield a usable command decoder. Hardware work can and should continue independently. The next *software* lever is not “another classifier on the same features,” but controls, alternate data, and different feature assumptions (including SSA-style SVD, not more TruncatedSVD on band-power).

---

## 2. Phase 0 — what was run and what we can summarize

### 2.1 Protocol (honest evaluation)

- Dataset: OpenNeuro **ds003626** (Nieto Inner Speech), subjects **01–08**
- Condition: **inner speech only**
- Split: **leave-session-out** (train 2 sessions, test held-out session), subject-specific except early pooled band-power
- Window: **1.5–3.5 s** after cue
- Null: within-session label permutations (typically n=10 classical; n=5 EEGNet binary)

### 2.2 Results table

| Method | Binary bal.acc (mean / pool) | 4-class (mean / pool) | vs chance |
|---|---:|---:|---|
| Band-power + SVM (pooled) | — / 0.476 | — / 0.243 | at/below |
| CSP + LDA | 0.506 / 0.502 | 0.267 / 0.264 | near |
| **FBCSP + LDA** | **0.541 / 0.539** | 0.259 / 0.259 | best binary; still non-sig |
| Riemannian TS + LDA | 0.505 / 0.505 | 0.253 / 0.254 | near |
| Truncated SVD + SVM (k=32) | 0.508 / 0.505 | 0.253 / 0.252 | near |
| EEGNet-8,2 | 0.486 / 0.489 | 0.250 / 0.250 | at/below |

Sources: `results/phase-0/README.md`, `wiki/logs/2026-07-20-phase-0-classical-ladder-final.md`, `wiki/logs/2026-07-21-phase-0-eegnet.md`.

### 2.3 What this summary means

1. **Failure is method-family-wide**, not one bad script. Spatial filters, geometry, unsupervised compression, and a compact CNN all land near chance under LSO.
2. **FBCSP ~0.54 binary** is the only mild lift; no subject cleared a significant permutation test under the logged n.
3. **SVD compression worked as compression** (~84–95% variance at k=32) but **not as discrimination**. Rank sweep {8,16,32,64} did not escape chance.
4. **EEGNet did not invent signal** classical methods missed; capacity + regularization collapsed toward chance.
5. Early single-subject smoke (sub-01) looked slightly optimistic; multi-subject LSO killed that optimism — correct protocol discipline.

### 2.4 Explicitly *not* yet done on Phase 0 (open levers)

From the ladder final report and method plan:

- [ ] **EXG / EMG artifact ablations** (high-EMG trial removal; EEG-only vs EEG+EXG)
- [ ] **Visualized-condition negative control**
- [ ] **Overt / pronounced speech positive control** (sanity: if this also fails, pipeline/data issues; if it works, inner-speech SNR is the issue)
- [ ] Within-session optimistic split only as a *signal-existence* diagnostic (not as product evidence)
- [ ] Subjects 09–10 if derivatives available
- [ ] TribeV2 ROI sidecar (optional; not a decoder)
- [ ] Alternate datasets / tasks (see §6)

---

## 3. Phase 1 — status and Blueprint relation to NORT goal

### 3.1 Deliverables present

| Doc | Role |
|---|---|
| `wiki/phase-1/01-evidence-and-feasibility.md` | Why temple EEG ≠ 128-ch lab; EEG+sEMG co-recording |
| `wiki/phase-1/02-prototype-requirements.md` | Single-pod recorder PRD |
| `wiki/phase-1/03-blueprint-prompts.md` | Copy-paste Blueprint design prompts |
| `wiki/phase-1/04-engineering-review-and-tests.md` | Gates: completeness → safety → bench → body |

Plan todos in `.cursor/plans/nort_phase_one_fa271ef5.plan.md` are marked **completed** for docs; physical build / Blueprint export review is **not** logged.

### 3.2 Is `03-blueprint-prompts.md` related to the NORT goal?

**Yes — as the correct *near-term* hardware workstream, not as the long-term decoder.**

Long-term NORT goal (from Phase 1 evidence brief): non-invasive assistive communication from intended/inner speech → audible speech.

Blueprint prompt scope: **one temple/behind-ear EEG+sEMG+IMU acquisition pod**, BLE streaming, charging interlock, bench-first safety. Explicit non-goals: no word/thought decoding, no stimulation, no medical/ALS claims.

| Alignment | Assessment |
|---|---|
| Supports eventual NORT product? | **Yes** — you cannot validate temple-sparse decoding without a stable, safe recorder and an sEMG witness |
| Is it the full goal? | **No** — it deliberately *defers* ISR |
| Risk if skipped? | High — Phase 0 already shows weak class signal on lab EEG; without measured local SNR + muscle controls, wearable decoding claims would be unfounded |
| Risk if overclaimed? | High — Blueprint output is a concept plan, not a clinical device |

**Opinion:** Blueprint P1 is the right next engineering investment given Phase 0 failures. Treating P1 as “building the speech decoder” would be a category error; treating it as optional because decoding failed would also be wrong — acquisition quality and artifact witnesses are now the primary scientific bottleneck.

---

## 4. Analysis of `raw/new/` (this iteration’s literature)

| File | What it is | Relevance to NORT |
|---|---|---|
| **`fnhum-19-1637174.pdf`** | Chowdhury et al. 2025, *Front. Hum. Neurosci.* — SoA review: ML for **inner speech recognition (ISR)** | **Primary.** Frames weak accuracies, CSP/EEGNet dominance, artifact/generalization limits; cites Nieto ~chance-level CNN results |
| **`applsci-14-07720-v2.pdf`** | Qin et al. 2024 — EEG **+ fMRI** cross-perception ISR; uses **SVD inside Singular Spectrum Analysis (SSA)** on EEG trajectory matrices | **High for SVD path.** Different SVD use than NORT’s TruncatedSVD-on-bandpower |
| **`2205.09456v1.pdf`** | Ollerenshaw et al. — neural representations in **end-to-end ASR** (audio speech) | **Low** for EEG ISR; useful only as “how speech models layer” intuition |
| **`frobt-07-00016.pdf`** | Chella et al. 2020 — robot **self-awareness via inner speech** (cognitive robotics) | **Conceptual only**; not a signal-processing paper |
| Video analytics / face expression book (PDF + `.crdownload`) | Face/expression recognition LNCS volume | **Out of scope** for ISR EEG (possible later multimodal UI; not Phase 0/1 core) |

### 4.1 Takeaways from the ISR SoA (`fnhum-19-1637174`)

- ISR remains hard: many published 4-class EEG word results sit **near chance** (e.g. ~29–30% for 4 words; review cites Berg/Nieto-class CNN numbers).
- Dominant tools in the review match what NORT already tried: **CSP/FBCSP, SVM, EEGNet/CNN**.
- Review stresses signal quality, preprocessing, limited generalizability, and muscle/eye confounds — aligning with NORT’s planned EXG gates and Phase 1 sEMG witness.
- **No emphasis on TruncatedSVD-as-classifier** as a breakthrough; literature does not contradict NORT’s null SVD result.
- Reported high accuracies elsewhere often differ in task (vowels, fewer classes, optimistic splits, multimodal fMRI, or unclear session control) — treat with the same skepticism Phase 0 already applied.

### 4.2 SVD-related work in `raw/new/`

| SVD flavor | Where | Already tried in NORT? | Worth exploring? |
|---|---|---|---|
| Truncated SVD / PCA on band-power → SVM | Phase 0 `run_svd_svm.py` | **Yes — failed** | Low priority to repeat |
| **Singular Spectrum Analysis (SSA)** = embedding + **SVD** + component reconstruction, then richer features (e.g. MTF images) | `applsci-14-07720-v2` | **No** | **Yes — distinct hypothesis** |
| Multimodal / low-rank fusion involving SVD ideas | Appl. Sci. refs; needs **fMRI** | No | Poor fit for wearable NORT |
| Spatio-spectral SVD denoise before CSP; supervised PLS/CCA (SVD under the hood) | Phase 0 method doc Tier B (not fully run) | Partial | Medium, after SSA or EXG |

**SVD conclusion for this iteration:** Do not re-run unsupervised TruncatedSVD on the same band-power features. If SVD stays on the roadmap, pivot to **time-series SSA** (trajectory SVD) and/or **supervised subspace** methods — and pair them with artifact controls.

---

## 5. Alternatives left after Phase 0 null results

User observation confirmed: **no Phase 0 approach reached a valid (significant, LSO-surviving) result.** Remaining paths, ordered by leverage:

### A. Keep ds003626, change the *question* (highest priority)

1. **Artifact / EXG ablations** — does any residual lift collapse when high-EMG trials are removed?
2. **Visualized negative control** — if “decoding” works equally on visualized motion, class signal is not inner speech.
3. **Pronounced/overt speech positive control** — establishes that the pipeline can recover *some* speech-related structure.
4. Stop architecture shopping on inner-speech LSO until A1–A3 are logged.

### B. Change the *data* (parallel track)

1. **Pressel Coretto imagined speech** via `projects/Rethinking-Methods-Inner-Speech/` (see §6) — 6-ch, vowels + 6 direction words, processed `.mat` ready.
2. Full Nieto subjects 09–10 / EXG derivatives if not already used.
3. Later: CHISCO / other high-density sets only if A and B1 still fail and a new hypothesis needs denser coverage.

### C. Change the *features* (including SVD) without claiming a product decoder

1. **SSA + SVD reconstruction** (from Appl. Sci. 2024) on epoch time series.
2. Supervised projections (PLS / CCA / LDA-guided subspaces).
3. Language-ROI / channel priors (TribeV2 sidecar) only as channel selection hypothesis — not as accuracy theater.

### D. Change the *product path* (strategic)

1. **Phase 1 hardware** continues regardless — measure local SNR, contact stability, BLE integrity.
2. **sEMG silent-speech / jaw witness** as an intermediate assistive channel (not “brain decoding”).
3. If temple EEG is inseparable from muscle/eye: **broader scalp montage** decision gate already written in Phase 1 docs.
4. Accept constrained vocab + subject calibration + offline-first; do not chase open-vocabulary EEG→LLM yet.

### E. Deprioritize

- More CSP / Riemannian / TruncatedSVD / EEGNet hyperparameter loops on the same LSO inner-speech setup.
- Expanding download volume as the main lever (already called out in the classical final report).
- Claiming TribeV2 or ASR papers as EEG decoders.

---

## 6. `projects/Rethinking-Methods-Inner-Speech/` — usable data check

**Paper:** Simistira Liwicki et al., bioRxiv 2022 — *Rethinking the Methods and Algorithms for Inner Speech Decoding*.  
**Raw source (external):** Pressel Coretto et al. imagined speech DB — http://fich.unl.edu.ar/sinc/downloads/imagined_speech/

### What is in the repo (testable without re-downloading raw)

| Asset | Content |
|---|---|
| `Preprocessing/vowel_processed_data_downsampled128/` | 15 subjects × vowels `{a,e,i,o,u}`; trials × **3072** float features |
| `Preprocessing/words_processed_data_downsampled128/` | 15 subjects × `{up,down,left,right,forward,backward}`; trials × **3072** |
| `*_NoDownsampled/` | Same labels; feature dim **24576** |
| `Training_and_functions/` | MATLAB CNN training (6 electrodes × 4 s @ 128 Hz → image `[6, 512]`) |
| `Testing_TrainedModels/` | Trained models + test scripts |

**Shape interpretation:** `3072 = 6 × 512` = 6 electrodes × 4 s × 128 Hz (matches training script). Not Nieto 128-ch epochs — a **sparse-channel** imagined-speech set closer to NORT’s eventual wearable channel count.

### Can we test now?

**Yes, for offline ML experiments**, with caveats:

- Processed `.mat` files are present and loadable (verified on S01).
- Native scripts are **MATLAB**; NORT Phase 0 stack is **Python** — either run MATLAB or write a thin `scipy.io.loadmat` loader into `software/phase0_decode/`.
- Reproducibility paper warns about method fragility; apply the **same LSO / permutation discipline** as ds003626 — do not trust random trial splits.
- Raw continuous EEG is *not* bundled; only preprocessed vectors/matrices. Fine for classifier bake-offs; limited for custom filter redesign unless raw is fetched separately.
- `.gitignore` currently truncates to `projects/Rethinking-Met` (incomplete line) — clean up when committing so the tree is intentionally tracked or ignored.

**Suggested first NORT experiment on this data:** binary up/down and 5-class vowels with band-power / CSP / SSA-SVD / small CNN under subject-wise held-out folds; compare to published scripts’ optimistic settings.

---

## 7. Recommended next actions (priority)

1. Log EXG + visualized + overt controls on ds003626 (close the scientific story on Nieto inner speech).
2. Stand up a Python loader for Rethinking processed vowels/words; run one honest baseline.
3. Prototype **SSA (trajectory SVD)** on one dataset as the remaining SVD hypothesis.
4. Proceed Phase 1: run Blueprint prompt → export → fill `04-engineering-review-and-tests.md` gates (no body contact).
5. Keep long-term ISR claims gated on artifact-surviving, above-chance LSO results — which do not exist yet.

---

## 8. Related logs and docs

- Classical ladder final: `wiki/logs/2026-07-20-phase-0-classical-ladder-final.md`
- SVD+SVM: `wiki/logs/2026-07-20-phase-0-svd-svm.md`
- EEGNet: `wiki/logs/2026-07-21-phase-0-eegnet.md`
- Results index: `results/phase-0/README.md`
- Method ladder (SVD alternatives): `wiki/phase-0/03-decoding-methods-svd-alternatives.md`
- Blueprint: `wiki/phase-1/03-blueprint-prompts.md`
