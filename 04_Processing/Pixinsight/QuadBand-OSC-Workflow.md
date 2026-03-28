---
title: "PixInsight Quad Band OSC Workflow"
type: processing-workflow
software: "PixInsight"
tags:
  - processing/pixinsight
---

# Quad Band OSC Processing

Processing workflow for narrowband data captured with the [[Antlia-FQuad]] filter on the [[ASI2600MCPro]] (color/OSC camera).

> **Key difference from broadband RGB:** The Quad Band filter passes Ha, OIII, Hb, and SII simultaneously onto a Bayer matrix sensor. Standard color calibration (SPCC) does not apply — the light is not broadband. Channel manipulation is required to separate and balance the narrowband signal.

---

## Channel Distribution

With the Antlia Quad Band on a color camera, the narrowband signal distributes across the Bayer channels as follows:

| Bayer Channel | Narrowband Signal |
|---------------|-------------------|
| Red | Ha (656nm) + SII (672nm) |
| Green | OIII (496/500nm) + Hb (486nm) |
| Blue | OIII (496/500nm) |

Ha and SII are very close in wavelength — they cannot be separated with a color camera.
OIII appears in both green and blue channels but is stronger in blue.

---

## Phase 1: Evaluation & Stacking

### 1.1 SubFrameSelector

- Scale: 3.1"/pixel ([[RedCat-51]] + [[ASI2600MCPro]])
- Evaluate: FWHM, Eccentricity, Median, Stars, Noise
- Reject outliers (poor seeing, clouds, tracking errors)

### 1.2 WBPP (Weighted Batch Pre-Processing)

- Drizzle: 2
- Dark master cosmetic correction
- Satellite trail removal:
  - Rejection Algorithm: Winsorized Sigma Clipping
  - Sigma High: ~1.9
  - Large Scale Pixel Rejection: High
- Calibration: darks, flats, dark flats, bias (see [[Master-Library]])

---

## Phase 2: Linear Processing

### 2.1 AutoStretch (visualization only)

**ScreenTransferFunction**
1. Autostretch in linked mode
2. Unlink
3. Autostretch

> The image will look strongly tinted — this is normal for narrowband data on a color camera.

### 2.2 Gradient Removal

**GraXpert** (recommended) or **DBE**

- Do NOT use SPCC/SPFC at this stage — they assume broadband light
- GraXpert handles narrowband gradients well with AI mode
- If using DBE: place sample points carefully avoiding nebula regions

### 2.3 Star Correction

**BlurXTerminator** — Correct Only
- Fixes optical aberrations without changing star size

### 2.4 Star Sharpening

**BlurXTerminator**
- Evaluate PSF Diameter with **PSFImage** render script
  - Or use Automatic PSF
- Configuration:
  - Sharpen Stars: 0.20
  - Adjust Star Halos: -0.10
  - PSF Diameter: (FWHMx + FWHMy) / 2 from evaluation
  - Sharpen Nonstellar: 0.90

### 2.5 Star Removal

**StarXTerminator**
- Generate Star image: selected
- Large overlap if dense star fields
- Keep the star image for later reintegration

> From this point, work on the **starless** image. Stars are processed separately.

### 2.6 Noise Reduction (Linear)

**NoiseXTerminator** on starless image
- Denoise: 0.9
- Detail: 0.15
- Test on preview first

---

## Phase 3: Narrowband Color Balancing

This is the critical step unique to Quad Band + OSC processing.

### 3.1 Channel Extraction

**ChannelExtraction**
- Color space: RGB
- Produces three images: R (Ha+SII), G (OIII+Hb), B (OIII)

### 3.2 Evaluate Channels

View each channel independently:
- **R channel** should show Ha emission structures clearly
- **G channel** shows OIII + some Hb — often noisy
- **B channel** shows OIII — often the cleanest narrowband signal

### 3.3 Channel Combination Strategies

Choose based on desired color palette:

#### Option A: Natural-ish Color (HOO mapping)

Map Ha to Red, OIII to Green and Blue for a "Hubble-like" natural look:

**PixelMath:**
```
R: $T[0]    (Red channel = Ha)
G: $T[2]    (Blue channel = OIII — cleaner than green)
B: $T[2]    (Blue channel = OIII)
```

**ChannelCombination** to merge back to RGB.

#### Option B: Enhanced HOO with Blended Green

Adds some Ha into green for warmer nebula tones:

**PixelMath:**
```
R: $T[0]
G: 0.3 * $T[0] + 0.7 * $T[2]
B: $T[2]
```

#### Option C: Dynamic HOO (Foraxx palette)

Popular for Quad Band + OSC. Uses the Foraxx script or manual PixelMath:

**PixelMath (Foraxx method):**
```
R: $T[0]
G: max($T[1], $T[2]) * 0.9 + $T[0] * 0.1
B: $T[2]
```

This preserves OIII detail in green while preventing magenta stars.

#### Option D: Keep Original RGB (minimal manipulation)

Skip channel extraction entirely. Simply stretch and color-balance manually with CurvesTransformation. Quickest approach, less control.

### 3.4 Reassemble

**ChannelCombination**
- Combine the remapped channels back into an RGB image
- Color space: RGB

---

## Phase 4: Non-Linear Processing (Stretching)

### 4.1 Stretch

**GeneralizedHyperbolicStretch (GHS)** — recommended for narrowband
- Offers more control over midtone transfer than HistogramTransformation
- Start with Symmetry Point (SP) near the histogram peak
- Apply in small increments

Alternative: **HistogramTransformation**
- Drag midtone slider to the right of the histogram peak
- Multiple small stretches are better than one aggressive stretch

### 4.2 Color Curves Adjustment

**CurvesTransformation**
- Adjust per-channel curves to balance Ha (red) vs OIII (teal/blue-green)
- Use Saturation curve to boost or restrain color intensity
- Use Luminance curve for contrast

### 4.3 Background Neutralization

**BackgroundNeutralization**
- Select a preview on a dark area free of nebulosity
- Neutralizes background color cast

### 4.4 Final Noise Reduction

**NoiseXTerminator** on the stretched starless image
- Denoise: 0.7–0.8 (lighter than linear pass)
- Detail: 0.20–0.25

---

## Phase 5: Star Processing

Work on the star image saved from step 2.5.

### 5.1 Star Stretch

**ArcsinhStretch**
- Protect highlights: enabled
- Test stretch factor — stars should look natural, not blown out

### 5.2 Star Color

**ColorSaturation**
- Boost star color slightly if desired
- Narrowband star colors are often muted — this is normal

---

## Phase 6: Reintegration & Final

### 6.1 Star Reintegration

**PixelMath:**
```
~(~starless * ~stars)
```

This is a screen blend — combines starless nebula with the star field.

### 6.2 Final Adjustments

- **CurvesTransformation** — final contrast and saturation tweaks
- **DarkStructureEnhance** script — optional, enhances dark nebula lanes
- **LocalHistogramEqualization** — optional, increases local contrast in nebula structure
- **ICCProfileTransformation** — convert to sRGB for export

### 6.3 Export

- TIFF 16-bit for archival
- JPEG/PNG for sharing

---

## Quick Reference: Broadband vs Quad Band

| Step | Broadband (L-Pro) | Quad Band |
|------|-------------------|-----------|
| Color calibration | SPCC with G2V reference | Skip — not applicable |
| Gradient removal | SPFC/MGC (PI 1.9) or DBE | GraXpert or DBE |
| Channel work | None (natural RGB) | Extract, remap Ha/OIII channels |
| Color palette | Natural | HOO / Foraxx / manual |
| Background neutralization | Before stretch | After stretch |
| Stretch | Statistical Astro Stretching | GHS or HistogramTransformation |

---

## Applicable Targets

All emission nebulae shot with the [[Antlia-FQuad]] filter:

- [[M42-Orion]] — strong Ha and OIII
- [[NGC7000-North-America]] — primarily Ha
- [[NGC2244-Rosette]] — strong Ha and OIII
- IC 1396 (Elephant's Trunk) — Ha dominant
- IC 1805 / IC 1848 (Heart & Soul) — Ha dominant
- NGC 6960/6992 (Veil Nebula) — strong OIII and Ha
- Sh2-129 (Flying Bat) — faint, needs deep integration

> **Note:** For galaxies and clusters, switch to the [[Optolong-LPro]] filter and use the [[RGB-Workflow]] instead.
