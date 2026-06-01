---
title: "2026-06-01 Processing Session — Mel 111 production master (genuine L-Pro flat, as-executed)"
type: processing-session
date: 2026-06-01
software: "PixInsight 1.9.4 (arm64)"
targets_processed:
  - "[[Mel111-Coma]]"
tags:
  - session/processing
  - processing/pixinsight
---

# 2026-06-01 — Mel 111 Production Master (as-executed)

Full re-stack + reprocess of the [[2026-05-25-Capture|2026-05-25 Mel 111 dataset]] (51 × 120 s L-Pro) — the **first stack with the genuine L-Pro flat** and a working **astrometric solution**. Supersedes the [[2026-05-31-Processing|2026-05-31 reprocess]] (which used FQuad flats and an unsolved master). Followed [[OpenCluster-Workflow]] end-to-end.

> [!success] Outcome
> Clean production master: genuine L-Pro flat applied, **drizzle 2×**, **4/4 astrometric solutions embedded (offline)**, FWHM **4.36 → 1.85 px**, ecc **0.37 → 0.26**, neutral background (R/G/B medians within 0.0006), faint Coma galaxies preserved, **γ Com halo resolved**. Result image updated on [[Mel111-Coma]].

This run was unblocked by two fixes diagnosed the same day — see [[2026-06-01-Astrometric-Diagnosis]] (catalog) and the FILTER-property fix below.

---

## 0. Pre-requisites fixed this session

- **Genuine L-Pro flat** — the prior "L-Pro flat" was a mislabeled FQuad flat (deleted). Shot a real one 2026-05-31 (`masterFlat_…FILTER-LPro_…10ms.xisf`).
- **FILTER metadata** — lights got the FITS `FILTER` keyword (`set_filter.py`); the **XISF master flat** needed its native **`Instrument:Filter:Name` property** set to `LPro` (WBPP ignores the FITS keyword for `.xisf` and was grouping the flat as `NoFilter` → unmatched → unapplied). Fixed and folded into `set_filter.py` XISF mode.
- **Astrometric catalog** — installed the **astrometric Gaia DR3 XPSD** (only the SP subset was present). See [[2026-06-01-Astrometric-Diagnosis]].

## 1. WBPP (full calibration + drizzle 2×)

- **Lights:** 51 × 120 s L-Pro (frame 0052 dropped — missing RA/DEC, captured at session end).
- **Calibration:** master Bias (1 ms), Dark **120 s** (exact match → **Optimize Master Dark OFF**), DarkFlat 10 ms, **Flat L-Pro 10 ms** (grouped `LPro` ✓ after the property fix). Cosmetic Correction **Auto** (master dark present).
- **Debayer** VNG, Combined RGB. Registration / LN at defaults. **Drizzle 2×** (drop shrink 0.90, Square).
- **Astrometric Solution ON**, Image Solver pixel **3.76 µm** (WBPP scales for drizzle internally; re-verified — it resets to 1.88).
- **Result:** `51 calibrated` (no flat warning), `Drizzle Integration (2x) success`, **`Astrometric solution → 4 solved`** (was `1 solved, 3 failed` before the catalog fix). 19:39 total.
- Production master: `masterLight_…_FILTER-LPro_RGB_drizzle_2x_autocrop.xisf` (12110×7812).

## 2. Linear correction & denoise

- **GraXpert background extraction** (linear, Subtraction, smoothing **0.7**) ×2 — moon-affected field; background model star-free.
- **BlurXTerminator — Correct Only:** FWHM 4.36 → **2.61 px**, ecc 0.37 → **0.232**.
- **BlurXTerminator — Sharpen:** PSF Diameter auto (~2.61 post-correct), Sharpen Stars 0.25, **Adjust Star Halos −0.25** (pushed from −0.15 for γ Com), Sharpen Nonstellar 0.70 → FWHM **1.85 px**, ecc 0.26, β 2.63, no over-sharpening (max-star FWHM 2.40 px, tight spread). γ Com at 1:1: BXT at its limit on the saturated core — finished surgically in §6.
- **GraXpert Denoise** (linear, 0.5). **FindBackground** (Seti Astro) preview kept for SPCC.

## 3. Colour calibration (SPCC)

- **SPCC** read the embedded WCS directly (**no ImageSolver needed** — the astrometric fix in action). ASI2600MC Pro / Optolong L-Pro, **White reference G2V Star**, background = FindBackground preview, Gaia DR3/SP, Neutralize background on.
- Reset STF → **linked AutoStretch**: blue/white/orange stars over neutral sky.

## 4. Stretch to non-linear

- **Bills_Stretch_Llinked_V6** (linked — preserves SPCC colour ratios).

## 5. Starless branch

- **StarXTerminator** → `starless` + `stars`.
- **SCNR-invert** (invert → SCNR Green → invert), **NXT Iterations 1** (light).
- **Galaxy-protected curve:** RangeSelection background mask (Lightness, Upper Limit tuned so faint galaxies → black, sky → white; red overlay on galaxies = protected) → CurvesTransformation shallow lower-third sag `(0,0)·(0.10,0.085)·(0.25,0.23)·(1,1)`. **Background median 0.10, black point untouched** → faint Coma galaxies preserved.

## 6. Star branch — γ Com reduction

- **SCNR-invert** on `stars`.
- **Bright-star StarMask** (Noise threshold 0.15, Scale 6, Large-scale growth 3, Smoothness 16, Shadows 0.30 → white = bright members) → **MorphologicalTransformation Erosion** (3×3 solid, Interlacing 1, 1 iteration, Amount 0.50). Shrank γ Com-class members; faint stars protected. **γ Com halo resolved** (vs. the soft blue residual that persisted on 2026-05-31 — the genuine L-Pro flat removed the underlying filter reflection).
- **Saturation curve** (gentle upper-mid) for star colour-pop.

## 7. Recombination

- **PixelMath** screen form `~(~starless * ~stars)` (no clipping of bright cores). Verified: neutral background (R/G/B median ≈ 0.117, within 0.0006), **clipping 0.001%** (only the brightest star cores).

## 8. Final polish

- **ICCProfileTransformation → sRGB IEC61966-2.1** (Relative Colorimetric).
- LHE **skipped** (sparse cluster — would amplify noise / re-introduce halos).
- Export 16-bit TIFF + JPEG → vault result image.

---

## Validation metrics (PSF, drizzle master)

| Stage | FWHM (px) | Ecc | Note |
|---|---|---|---|
| Pre-BXT | 4.36 | 0.370 | drizzle 2× native |
| Correct Only | 2.61 | 0.232 | |
| Sharpen (−0.25 halos) | **1.85** | 0.260 | β 2.63; max-star 2.40 px (tight) |
| Recombined background | — | — | R/G/B median 0.117 ±0.0006; clip 0.001% |

## Deviations / lessons vs. base workflow

- **Adjust Star Halos −0.25** (not −0.15) for γ Com — but BXT is limited on saturated cores; the morphological erosion (§6) does the real work. Documented as a dominant-bright-star tip candidate.
- **Optimize Master Dark OFF** — exact-exposure (120 s) darks need no scaling; bias cancels out.
- The whole run validated that the **astrometric catalog** and **XISF filter-property** fixes work end-to-end in a full WBPP + SPCC pipeline.
