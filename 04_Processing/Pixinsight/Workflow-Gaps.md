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

### NoiseXTerminator OSC-Specific Settings

**Search:** `NoiseXTerminator OSC`, `NoiseXTerminator color camera`

Both workflows use generic NXT parameters (0.9/0.15 linear, 0.7–0.8/0.20–0.25 non-linear). Official OSC-specific guidance may differ.

### BlurXTerminator OSC-Specific Settings

**Search:** `BlurXTerminator OSC`, `BlurXTerminator color camera`

BXT settings (Sharpen Stars 0.20, Halos -0.10, Nonstellar 0.90) are reasonable but not validated against official guidance for color cameras.

### StarXTerminator on Narrowband OSC

**Search:** `StarXTerminator narrowband`, `StarXTerminator OSC`

Star removal behavior may differ on narrowband OSC data vs broadband. Confirm whether the same settings (Large overlap for dense fields) apply.

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
