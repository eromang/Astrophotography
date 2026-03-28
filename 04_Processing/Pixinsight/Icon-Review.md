---
title: "Process Icon Review"
type: processing-workflow
software: "PixInsight"
tags:
  - processing/pixinsight
---

# Process Icon Review

Changes and clarifications needed for the process icons in `icons-2024-2.xpsm`. Compared against the documented workflows on 2026-03-28.

---

## Icons Matching Workflows (No Changes Needed)

| Icon | Key Settings | Status |
|------|-------------|--------|
| BTX_instance | Sharpen Stars 0.20, Halos -0.10, PSF 2.30, Nonstellar 0.90 | Matches workflow |
| NEX_instance | Denoise 0.9, Detail 0.15, Iterations 2 | Matches workflow |
| STX_instance | lite.nonoise.11 model, stars=true, overlap 0.20 | Matches workflow |
| PM_instance | `~(~starless*~stars)` screen blend | Matches workflow |
| BN_instance | Target background 0.001, RescaleAsNeeded | Matches workflow |
| LHE_instance | Radius 64, slope 2.0, Bit8 | Matches workflow |
| CT_instance | Default/template (Akima subsplines) | Matches — interactive use |
| SPCC_LPro_instance | Optolong L-Pro filters, Sony IMX QE, G2V, DR3/SP | Matches workflow |
| SPCC_Quad_instance | Sony CMOS + Antlia Quadband combined curves, Sony IMX QE, G2V, DR3/SP | Matches workflow |

---

## Icons Needing Updates

### MGC_instance — Update for Narrowband Use

**Current state:** Configured for broadband (R/G/B MARS bands, scale factor 0.8 all channels, gradient scale 2048).

**Clarification needed:** This icon works for L-Pro broadband images. For Quad Band narrowband, you need a **second MGC icon** with:

| Parameter | Broadband (current) | Narrowband (needed) |
|---|---|---|
| MARS bands | R, G, B | **Ha, O-III, O-III** |
| Gradient scale | 2048 | **512–1024** |
| Scale factor R | 0.8 | **0.2–0.5** (Ha channel) |
| Scale factor G | 0.8 | **1.4–1.8** (O-III channel) |
| Scale factor B | 0.8 | **1.4–1.8** (O-III channel) |
| Structure separation | 1 | 1 (same) |

**Action:** Duplicate MGC_instance → rename to `MGC_NB_instance`. Change MARS bands to Ha/O-III/O-III. Adjust scale factors per channel.

### SPFC_instance — Verify Narrowband Mode

**Current state:** `narrowbandMode = false`, uses combined Sony CMOS + Antlia Quadband per-Bayer-channel filter curves with 3nm bandwidth.

**Clarification needed:** The workflow Option B (SPFC + MGC) previously said to enable narrowband mode. Your icon does NOT use narrowband mode — it uses combined filter curves. The workflow has been updated to match, but verify this is intentional:

- **Combined curves (current):** Models actual sensor response (Bayer channel × filter transmission). More accurate for OSC.
- **Narrowband mode:** Treats each channel as a pure narrowband signal. Simpler but less accurate for OSC where Bayer channels mix signals.

**Action:** No change if combined curves give good results. If gradient correction struggles, try enabling narrowband mode as an alternative.

### WBPP_CC_Auto_instance / WBPP_CC_Dark_instance — Verify CFA Setting

**Current state:** `cfa = false` in cosmetic correction.

**Clarification needed:** For color sensors using CFA drizzle, the CFA flag may need to be enabled for proper hot pixel detection on the Bayer pattern. Verify whether WBPP handles this automatically.

**Action:** Test — if cosmetic correction misses hot pixels on one Bayer channel, enable `cfa = true`.

---

## Missing Icons (Consider Creating)

| Icon | Purpose | Base on |
|------|---------|---------|
| MGC_NB_instance | MGC for narrowband Quad Band data | MGC_instance with Ha/O-III bands |
| SPFC_LPro_instance | SPFC for L-Pro broadband | SPFC_instance with Optolong L-Pro filter |
| MAS_instance | MultiscaleAdaptiveStretch for HDR | New — see [[HDR-Workflow]] |
| HDRMT_instance | HDR Multiscale Transform | New — see [[HDR-Workflow]] |
| BXT_correct_instance | BlurXTerminator correct-only (step 2.3/2.4 first pass) | BTX_instance with `correct_only = true` |

---

## Icon Inventory

Source: `icons-2024-2.xpsm` (generated 2025-03-26, PI 1.9.3)

| Instance ID | Process | Used in |
|---|---|---|
| WBPP_CC_Auto_instance | CosmeticCorrection (auto detect) | Phase 1 |
| WBPP_CC_Dark_instance | CosmeticCorrection (dark master) | Phase 1 |
| STF_instance | ScreenTransferFunction | Visualization |
| BTX_instance | BlurXTerminator | Steps 2.4/2.5 |
| NEX_instance | NoiseXTerminator | Steps 2.6/2.10 |
| DynamicCrop_instance | DynamicCrop | Manual |
| SCNR_instance | SCNR | Manual |
| STX_instance | StarXTerminator | Step 2.5/2.9 |
| HT_instance | HistogramTransformation | Step 3.1 alt |
| ABE_instance | AutomaticBackgroundExtractor | Legacy (use MGC) |
| DBE_instance | DynamicBackgroundExtraction | Legacy fallback |
| CT_instance | CurvesTransformation | Steps 4.2/4.3 |
| SPFC_instance | SpectrophotometricFluxCalibration | Step 2.2/2.3 |
| RS_instance | RangeSelection | Manual masking |
| LHE_instance | LocalHistogramEqualization | Step 6.2/4.3 |
| PM_instance | PixelMath (star recombination) | Step 6.1/4.2 |
| MGC_instance | MultiscaleGradientCorrection | Step 2.2/2.3 |
| SPCC_LPro_instance | SPCC for L-Pro broadband | Step 2.7 |
| SPCC_Quad_instance | SPCC for Quad Band | Step 3.5 |
| BN_instance | BackgroundNeutralization | Step 3.2/4.3 |
