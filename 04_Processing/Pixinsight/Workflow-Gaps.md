---
title: "Processing Workflow Knowledge Gaps"
type: processing-workflow
software: "PixInsight"
tags:
  - processing/pixinsight
---

# Workflow Knowledge Gaps

Topics to clarify via PixInsight YouTube channel videos or empirical testing. When a gap is filled, integrate the content into the relevant workflow and move the topic to Resolved.

**Search keywords for the PixInsight channel** are listed with each topic.

---

## High Priority — Missing from Workflows

### MAS on OSC / Color Camera

**Search:** `MAS OSC`, `MAS color camera`, `MultiscaleAdaptiveStretch color`

[[HDR-Workflow]] references MAS but only mono camera examples have been reviewed. Need OSC-specific confirmation of parameter behavior — does color saturation disabled behave the same on Bayer data?

### SPCC Combined Filter Curves for Quad Band — Partially Resolved

**Search:** `SPCC combined filter curves`, `SPCC dual band`, `SPCC quad band OSC`

**Update (2026-03-28):** Process icon analysis confirmed the SPCC_Quad icon uses combined filter curves (Sony CMOS × Antlia Quadband per Bayer channel), NOT narrowband mode. Workflow step 3.5 updated to match. Filter curve CSVs found on SSD at `/Volumes/T7/Astrophotography/Filters/Antlia Quadband PI filters/`. Remaining question: is there ever a case where narrowband mode would be preferable on OSC + quad band data?

### DBXtract for Emission Line Separation

**Search:** `DBXtract`, `emission line separation`, `dual band separation`

Alternative to the PixelMath approach in step 2.7 of [[QuadBand-OSC-Workflow]]. May provide ready-made scale factors for common camera+filter combinations, avoiding the manual calibration step.

### ~~NoiseXTerminator OSC-Specific Settings~~ — Resolved (2026-06-23)

Resolved against the [[NoiseXTerminator 2_AI3 User Manual (PixInsight)]]. Both workflows now document: never before BXT, run on the **combined colour image**, simple Denoise 0.85–0.9 / Iter 2, **plus the NXT2/AI3 separation modes** (color > intensity, low LF for dust; HF int 80–90, HF color 90–100, LF int 50–70, LF color 100). See QuadBand-OSC §2.6 / RGB §2.10.

### ~~BlurXTerminator OSC-Specific Settings~~ — Resolved (2026-06-23)

Resolved against the [[BlurXTerminator 2.0_AI4 Release]]. Documented: **linear-only**; **Correct Only → SPCC → Sharpen** colour order (broadband); narrowband = deconvolve **before** channel mixing; AI4 handles M42 DR + drizzle-2×; and the **measure-PSF-on-Correct-Only-output** gotcha (CO tightens stars ~½). See QuadBand-OSC §2.3–2.4 / RGB §2.4–2.5.

### ~~StarXTerminator on Narrowband OSC~~ — Resolved (2026-06-23)

Resolved against the [[StarXTerminator Usage Notes]]. Documented: SXT on **linear** (before any stretch — never after HDR/arcsinh/GHS), **Unscreen OFF on linear → subtraction** (pairs with screen-blend recombine), **Large Overlap ON for bright-core/frame-filling nebulae** (M42 = the named case), don't STF the star image. See QuadBand-OSC §2.5 / §6.1.

---

## Medium Priority — Refine Existing Steps

### WBPP CFA Drizzle Specifics

**Search:** `WBPP CFA drizzle`, `drizzle OSC`, `CFA drizzle color sensor`

Workflows use Drizzle 2 but don't cover CFA drizzle details for OSC sensors.

### ~~SubframeSelector Weighting Formulas~~ — Resolved

Approval and weighting expressions added to both workflows. Weighting: `(1/(FWHM*FWHM)) * SNR * (1 - Eccentricity)`. Tested on NGC 5746 data.

### BackgroundNeutralization Timing for Narrowband

**Search:** `BackgroundNeutralization narrowband`, `BackgroundNeutralization when`

[[QuadBand-OSC-Workflow]] applies BN after stretch (Phase 4.3), [[RGB-Workflow]] applies before. Official guidance on optimal timing for each type.

### GHS Narrowband-Specific Settings

**Search:** `GHS narrowband`, `GeneralizedHyperbolicStretch narrowband`

[[QuadBand-OSC-Workflow]] uses GHS but no narrowband-optimized parameters are documented.

### ArcsinhStretch for Narrowband Star Colors

**Search:** `ArcsinhStretch stars`, `star stretch narrowband`

Star stretch step (Phase 5.1) is minimal — optimal settings for preserving star color in narrowband data.

### CorrectMagentaStars on OSC Narrowband

**Search:** `CorrectMagentaStars OSC`, `magenta stars dual band`

Magenta stars on OSC narrowband have a different root cause than mono SHO. May need a different correction approach.

---

## Low Priority — Nice to Have

### LocalHistogramEqualization Parameters

**Search:** `LocalHistogramEqualization`

Listed in [[QuadBand-OSC-Workflow]] Phase 6.2 but no settings documented.

### DarkStructureEnhance Parameters

**Search:** `DarkStructureEnhance`

Listed in both workflows but no guidance on when/how to use.

### Satellite Trail Rejection Optimization

**Search:** `WBPP satellite`, `satellite trail rejection`

WBPP settings present (Winsorized Sigma Clipping, Sigma High ~1.9) but could be refined.

### MLDenoise — evaluate vs NoiseXTerminator

**Search:** `MLDenoise`, `Core ML denoise`

PixInsight's **first-party ML denoiser** (Technology Preview, announced 2026-06). A native alternative to [[NoiseXTerminator]]. **Runnable now:** requires **1.9.4 Lockhart build 1693+** (have **1695** ✓) and **macOS ARM64** (Apple Silicon ✓); GPU-accelerated via Apple Core ML. Install via regular update channel, then download the `.xmlm` model from `pixinsight.com/dist/` → set in MLDenoise Preferences. Best on **color-calibrated, linear** images; refine on reduced previews; linear masks as local support.

**Status:** Technology Preview — no real-time preview yet, caching "not ideal." **Full Linux/macOS/Windows release ~July 2026.**

**Evaluation plan (revisit after July release):** A/B against NXT at the linear denoise step ([[QuadBand-OSC-Workflow#2.6 Noise Reduction]] / [[RGB-Workflow]]) on the same preview — compare faint-nebula detail vs background-noise floor. ⚠️ It wants **color-calibrated** input, so for a fair narrowband test run it *after* the HOO/SPCC color step, not on the raw linear master. Don't switch the production workflow off NXT until the full release is out and the A/B is done.

---

## Resolved

- ~~MGC for OSC dual-band~~ → Integrated into [[QuadBand-OSC-Workflow]] step 2.2 Option B
- ~~Ha emission line separation~~ → Integrated into [[QuadBand-OSC-Workflow]] step 2.7
- ~~SPCC narrowband mode~~ → Integrated into [[QuadBand-OSC-Workflow]] step 3.5
- ~~MAS + HDRMT for HDR~~ → Integrated into [[HDR-Workflow]]
- ~~MGC parameter tuning~~ → Integrated into both workflows (gradient scale, scale factor, structure separation)
- ~~SPCC QE curve for color sensors~~ → Fixed in [[RGB-Workflow]] step 2.7 (Sony IMX QE, confirmed from process icon)
- ~~SPCC combined filter curves~~ → Confirmed from process icon: uses Sony CMOS × Antlia Quadband per Bayer channel. Step 3.5 updated. Filter CSVs on SSD.
- ~~Drizzle vs debayerization~~ → Added to [[RGB-Workflow]] Phase 1
- ~~Gaia DR3/SP catalog requirement~~ → Added to [[RGB-Workflow]] step 2.2
- ~~BXT/STX/NXT model versions and parameters~~ → Aligned both workflows with actual process icons
- ~~Drizzle vs debayerization~~ → Added to [[RGB-Workflow]] Phase 1
- ~~Gaia DR3/SP catalog requirement~~ → Added to [[RGB-Workflow]] step 2.2
