# Decoding Method Alternatives (Including SVD)

## Problem statement

Input: multichannel EEG epochs `X ∈ R^{trials × channels × time}`  
Output: discrete labels (2–4 direction words; later maybe phonemes)  
Constraints: low SNR, strong artifacts, small N, subject-specific calibration

Phase 0 should implement a **ladder of methods**, from transparent linear baselines to deep models. SVD belongs in that ladder as a dimensionality-reduction / subspace tool, not as a complete speech decoder by itself.

## Method ladder

### Tier A — Classical, inspectable (implement first)

| Method | Role | Why it matters |
|---|---|---|
| Band-power / filter-bank features + SVM / LDA | Sanity baseline | Matches the dataset tutorial path |
| **PCA / Truncated SVD** | Compress channels×time or spectral features | Removes redundant variance; stabilizes classifiers |
| **CSP / FBCSP** | Class-discriminative spatial filters | Standard BCI tool; usually stronger than PCA for discrimination |
| Riemannian / covariance features | Geometry-aware baseline | Competitive on small EEG sets |

### Tier B — SVD-related subspace methods

SVD (`X = U Σ Vᵀ`) is useful in several EEG recipes:

1. **PCA via SVD** on flattened epochs or PSD features → keep top-k components → SVM.
2. **Spatio-spectral SVD** on trial matrices to denoise before CSP.
3. **Canonical / PLS-style variants** that use SVD under the hood for supervised projection.
4. **Low-rank reconstruction** to suppress high-rank noise while retaining shared speech-related patterns.

What SVD is good at:

- Reducing dimensionality when channels×samples ≫ trials.
- Providing orthogonal bases for visualization and QC.
- Stabilizing linear classifiers on noisy EEG.

What SVD is **not**:

- A semantic speech model.
- A guarantee of muscle-independent inner-speech decoding.
- A substitute for artifact witnesses (EOG/EMG) and honest splits.

Recommended Phase 0 SVD experiment:

```text
features = flatten(bandpower(X)) or flatten(X[:,:,action_window])
U, S, Vt = svd(features, full_matrices=False)
Z = features @ Vt[:k].T
train SVM/LDA on Z
compare k ∈ {8,16,32,64} vs CSP+SVM vs raw SVM
```

### Tier C — Deep learning (implement after Tier A works)

| Model | Notes |
|---|---|
| EEGNet | Compact CNN; common EEG-BCI baseline |
| ShallowConvNet / DeepConvNet | Strong classical DL baselines |
| Transformer / spectro-temporal models | Higher capacity; easy to overfit on N=10 |

Literature context on the Nieto set often reports modest subject-dependent accuracies (sometimes ~30% for 4-class with EEGNet in reviewed work — near but above chance). Treat anything dramatically higher with suspicion until leave-session-out and artifact controls are shown.

### Tier D — Not Phase 0 decoder cores

| Approach | Why defer |
|---|---|
| TribeV2 fMRI encoder | Different modality; encoding not decoding |
| Large LLM open-vocabulary EEG→text | High risk of language-model hallucination masking weak neural signal |
| End-to-end speech synthesis from EEG | Premature; needs reliable discrete decoding first |

## Recommended evaluation protocol

For every method:

1. **Binary warm-up:** arriba vs abajo, inner-speech only.
2. **4-class:** all directions, inner-speech only.
3. **Negative controls:** visualized condition; shuffled labels (permutation).
4. **Artifact ablation:** train with/without high-EMG trials; EEG-only vs EEG+EXG.
5. **Split types:** within-session (optimistic), leave-session-out (required), leave-subject-out (hard).
6. **Metrics:** balanced accuracy, macro-F1, confusion matrix, calibration samples needed.

Go/no-go for “method works”:

- Above permutation chance with CI not overlapping chance.
- Survives leave-session-out.
- Does not collapse to sEMG-only performance when EMG is available as a witness.

## Practical recommendation

**Default Phase 0 stack:**

1. Filter-bank power + StandardScaler + SVM  
2. Truncated SVD/PCA + SVM  
3. CSP / FBCSP + LDA/SVM  
4. EEGNet  

Promote deeper models only if Tier A/B show a real, reproducible signal. Use SVD as a **feature compressor and QC tool**, not as the marketing story of the decoder.
