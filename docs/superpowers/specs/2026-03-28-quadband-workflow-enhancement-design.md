# QuadBand-OSC-Workflow Enhancement Design Spec

**Date:** 2026-03-28
**Status:** Draft
**Target file:** `04_Processing/Pixinsight/QuadBand-OSC-Workflow.md`

---

## Summary

Enhance the existing QuadBand-OSC-Workflow with three improvements sourced from PixInsight's official MGC Dual-Band OSC videos: Ha emission line separation, MGC as an alternative gradient tool, and corrected SPCC guidance. All changes are edits to the existing workflow document — no new files.

---

## Scope

### In scope

- New step 2.7: Ha emission line separation (PixelMath)
- Updated step 2.2: MGC + SPFC as alternative to GraXpert
- Corrected Quick Reference table: SPCC narrowband mode is an option, not "skip"
- New optional SPCC narrowband calibration note after Phase 3.4
- Delete both MGC Dual-Band OSC clippings (content absorbed)

### Out of scope

- Restructuring the workflow phases
- Changing the recommended tools (GraXpert remains primary for gradient removal)
- Quad-band-specific scale factors for emission separation (user determines these empirically)

---

## Change 1: New Step 2.7 — Ha Emission Line Separation

**Insert after:** Step 2.6 (Noise Reduction)
**Insert before:** Phase 3 (Narrowband Color Balancing)

### Content

**Step 2.7: Ha Emission Line Separation (Optional)**

Remove Ha crosstalk from the green and blue Bayer channels. On the ASI2600MC Pro, green and blue pixels are partially sensitive to Ha (656nm), contaminating the OIII signal. This step subtracts the scaled Ha contribution, producing cleaner OIII for channel extraction in Phase 3.

**PixelMath** (uncheck "Use a single expression"):

```
R: $T
G: $T - ($T[0] - med($T[0])) * scale_G
B: $T - ($T[0] - med($T[0])) * scale_B
```

Where `scale_G` and `scale_B` are camera+filter-specific constants.

**Finding the scale factors (one-time calibration):**

1. Select a preview containing visible Ha nebulosity
2. Start with a high scale factor (e.g., 0.5) — Ha structures will appear inverted
3. Decrease gradually until the inversion just disappears
4. The correct value minimizes Ha traces without overcorrecting
5. Repeat for each channel (G and B typically need different values)

Once determined, these factors are reusable for all images from the same camera + filter combination. Save the PixelMath process icon for reuse.

**ASI2600MC Pro + Antlia Quad Band scale factors:**

| Channel | Scale Factor |
|---------|-------------|
| Green (scale_G) | TBD — determine on first processing session |
| Blue (scale_B) | TBD — determine on first processing session |

> Update this table after determining your scale factors. They should remain constant unless atmospheric conditions are anomalous.

---

## Change 2: Updated Step 2.2 — MGC Alternative for Gradient Removal

**Replace current step 2.2 content.**

### Current content

```
**GraXpert** (recommended) or **DBE**

- Do NOT use SPCC/SPFC at this stage — they assume broadband light
- GraXpert handles narrowband gradients well with AI mode
- If using DBE: place sample points carefully avoiding nebula regions
```

### New content

```
**Option A: GraXpert** (recommended for simplicity)

- AI mode handles narrowband gradients well
- No manual tuning required
- If using DBE as fallback: place sample points carefully avoiding nebula regions

**Option B: SPFC + MGC** (more control, image-dependent)

1. **SPFC** (SpectrophotometricFluxCalibration)
   - Enable narrowband filters mode
   - Sensor: IMX571
   - Set bandwidths to ~5nm for all channels
   - Default wavelengths (Ha, OIII) are correct for Quad Band

2. **MGC** (MultiscaleGradientCorrection)
   - Use MARS DR1 database only (contains Ha and OIII bands)
   - Assign MARS bands: Ha to red channel, OIII to green and blue channels
   - Enable "Show gradient model" to verify
   - Tune scale factors per channel on a preview:
     - If nebula traces remain → increase scale factor
     - If nebula appears inverted → decrease scale factor
   - Gradient scale: 512–1024 depending on gradient complexity (lower = finer, but more risk of nebula interference)

**Which to use:** Try both on a preview. Some images respond better to MGC (especially with strong vignetting), others to GraXpert (especially with complex nebula shapes). Results are image-dependent.
```

---

## Change 3: Corrected SPCC Guidance

### 3a. Quick Reference Table Update

**Current row:**

| Step | Broadband (L-Pro) | Quad Band |
|------|-------------------|-----------|
| Color calibration | SPCC with G2V reference | Skip — not applicable |

**New row:**

| Step | Broadband (L-Pro) | Quad Band |
|------|-------------------|-----------|
| Color calibration | SPCC with G2V reference | SPCC narrowband mode (optional) — see step 3.5 |

### 3b. New Step 3.5 — SPCC Narrowband Calibration (Optional)

**Insert after:** Step 3.4 (Reassemble)
**Insert before:** Phase 4 (Non-Linear Processing)

### Content

**Step 3.5: Color Calibration (Optional)**

After reassembling channels into an HOO composite, SPCC can calibrate the color balance in narrowband filters mode:

**SPCC** (SpectrophotometricColorCalibration):
- Enable narrowband filters mode
- Filter wavelengths: Ha (656nm) red, OIII (496/500nm) green and blue
- Bandwidth: ~5nm for all filters
- White reference: **Photon flux** (preserves relative emission intensities as observed in the sky)
- Select a background reference area free of nebulosity

> This is optional — manual color balancing via CurvesTransformation (Phase 4.2) remains the alternative. SPCC narrowband mode provides a physically-calibrated starting point that can reduce manual tweaking.

---

## Change 4: Delete Clippings

Delete both files (untracked, content absorbed into workflow):
- `04_Processing/Clippings/MultiscaleGradientCorrection — Dual-Band OSC Images (I).md`
- `04_Processing/Clippings/MultiscaleGradientCorrection — Dual-Band OSC Images (II).md`

---

## Changes Summary

| # | Type | Location | Description |
|---|------|----------|-------------|
| 1 | Insert | After step 2.6 | New step 2.7: Ha emission line separation |
| 2 | Replace | Step 2.2 | GraXpert + MGC alternative for gradient removal |
| 3a | Update | Quick Reference table | Fix "Skip" → "SPCC narrowband mode (optional)" |
| 3b | Insert | After step 3.4 | New step 3.5: SPCC narrowband calibration |
| 4 | Delete | Clippings folder | Both MGC Dual-Band OSC clippings |
