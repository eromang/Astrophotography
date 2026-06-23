---
title: "NXT Advisor — NoiseXTerminator settings from noise structure"
type: processing-workflow
software: "PixInsight"
tags:
  - processing/pixinsight
---

# NXT Advisor

`scripts/nxt_advisor.py` — measure the **structure** of an image's noise and suggest **NoiseXTerminator separation-mode** settings. Companion to [[NoiseXTerminator 2_AI3 User Manual (PixInsight)]].

## What's measurable vs taste

| | |
|---|---|
| ❌ **Denoise amount** (~0.85) | **Taste** — "how smooth do you want it." Not a measured value; tune on the real-time preview. |
| ✅ **Colour vs intensity** | Measured: σ_colour / σ_intensity in a signal-free patch → how hard to push **HF/LF colour** vs intensity (the RC-Astro "reduce colour more" advice, quantified). |
| ✅ **HF/LF Scale** | Measured: the noise **correlation length** → what counts as "fine" vs "large" noise. White noise ≈ 1 px; drizzle/debayer noise is correlated and larger. |
| ✅ **Iterations** | From the noise level (1 for clean, 2 for noisy). |

It grabs a dark, signal-free ROI via [[Find-Background]], removes the large-scale component (so it measures *noise*, not nebula), and reports the measured structure + a suggested setup.

> The colour/intensity ratio is bounded near **√2 ≈ 1.41** for *independent* per-channel noise (it leaks into luminance via the mean). A ratio well above that means **true chrominance noise** (anti-correlated channels — e.g., an HOO G=B remap, or debayer artifacts) → push HF/LF colour to 1.0. A ratio near 1.0–1.4 is ordinary → moderate colour.

## Usage

```bash
python3 scripts/nxt_advisor.py <image.xisf> [--size 200] [--json]
```

| Option | Default | Meaning |
|---|---|---|
| `--size N` | 200 | background ROI side for noise measurement |
| `--json` | — | machine-readable |

## Reading the output

- **HF/LF amounts** — paste into NXT with both separation modes ON. Colour ≥ intensity always; LF intensity gentle to preserve dust/filaments.
- **HF/LF Scale** — set this on the NXT slider (the manual says tune per-image; this gives the measured starting value).
- **Denoise amount** — *your* call on the preview; the tool reports 0.85 as a placeholder.

> ⚠️ This measures **linear** noise (low in absolute terms even when it looks grainy after a hard stretch). For a **linear** NXT pass it correctly recommends a *moderate* setup — don't over-denoise linear data. The heavy *post-stretch* grain is cleaned by the **final** NXT pass; re-run the advisor on the stretched image for that pass.

## Worked example (M42 reprocess, 2026-06-23)

Natural-colour starless (pre-NXT): colour/intensity **1.35** (moderate), corr-scale **1.1 px**, σ_int **4.3e-5** (clean) → HF int 0.80 / HF colour 0.93 / LF int 0.55 / LF colour 1.00 / Scale 2 px / Iter 1. The moderate 1.35 ratio **quantitatively confirmed dropping HOO** — the HOO remap's G=B correlation would have measured a far higher chrominance ratio.

## Tests

```bash
python3 scripts/test_nxt_advisor.py
```

6 synthetic checks: chrominance-ratio detection, intensity-dominant case, white-vs-correlated scale, scale→suggestion, iterations-by-noise, mono handling. See [[../../scripts/README.md#nxt_advisor.py — NoiseXTerminator settings from noise structure|scripts/README]].
