---
title: "PixInsight RGB Broadband Workflow"
type: processing-workflow
software: "PixInsight"
tags:
  - processing/pixinsight
---

# RGB Broadband Processing (OSC)

Processing workflow for broadband data captured with the [[Optolong-LPro]] filter on the [[ASI2600MCPro]] (color/OSC camera). Use this for galaxies, clusters, and reflection nebulae.

> **For emission nebulae with the Quad Band filter**, use the [[QuadBand-OSC-Workflow]] instead.

## Resources

- https://www.youtube.com/watch?v=6cFRwgfXUN0&t=306s
- https://www.youtube.com/watch?v=XCotRiUIWtg&t=3325s
- https://www.youtube.com/watch?v=YcRItb__GcQ&t=1883s

---

## Phase 1: Evaluation & Stacking

### SubFrameSelector

**System Parameters:**

| Parameter | Value |
|---|---|
| Subframe scale | **3.10** arcsec/pixel |
| Camera gain | 1.0000 e⁻/ADU |
| Camera resolution | 16-bit [0,65535] |
| Site local midnight | **1** hours UTC (CET) / **2** hours UTC (CEST) |
| Scale unit | Arcseconds |
| Data unit | Normalized to [0,1] |

**Evaluate:** FWHM, Eccentricity, Median, Stars, Noise
**Keyword:** SSWEIGHT (postfix `_a`)

**Approval expression:**
```
Median < 0.028 && FWHM < 9.5 && Eccentricity < 0.80
```
Adjust thresholds per session — check for twilight-contaminated frames (high median/noise) and poor seeing (high FWHM).

**Weighting expression:**
```
(1/(FWHM*FWHM)) * SNR * (1 - Eccentricity)
```
Prioritizes tight stars (FWHM²), good signal, and round stars. FWHM squared because it has the biggest impact on image quality.

### WBPP (Weighted Batch Pre-Processing)

- Drizzle: **2** (strongly recommended over debayerization for color sensors — drizzle involves no data interpolation, while debayerization interpolates 3 out of 4 pixels per channel, introducing photometric errors)
- Dark master cosmetic correction
- Satellite trail removal:
  - Rejection Algorithm: Winsorized Sigma Clipping (or Auto)
  - Sigma High: ~1.9
  - Large Scale Pixel Rejection: **High** enabled, layers 2, growth 2
- Image Registration: **enable Distortion Correction** (max spline points 4000) — corrects [[RedCat-51]] field curvature at edges, improves Drizzle 2 quality
- Calibration: darks, flats, dark flats, bias (see [[Master-Library]])

> **Drizzle 2x changes pixel scale:** output resolution is 1.55"/px (half of native 3.1"/px), pixel size effectively 1.88 µm. This affects ImageSolver and any tool that needs the image scale. WBPP may not plate-solve the drizzled output automatically — run ImageSolver (step 2.2) on the drizzle master if SPFC fails with "no astrometric solution".

---

## Phase 2: Linear Processing

### 2.1 AutoStretch (visualization only)

**ScreenTransferFunction** — display-only, does not modify data. Image remains linear.

1. Click the **nuclear icon** (yellow/black, bottom-left) to AutoStretch in **linked** mode (chain link icon = linked)
2. **Unlink** channels (click chain link icon at top-left to break the link)
3. AutoStretch again — shows each channel independently, reveals color imbalances

> Never drag STF to HistogramTransformation until Phase 3 (stretching). All Phase 2 processing must be done on linear data.

### 2.2 ImageSolver

Plate-solve the image for SPFC/SPCC to work correctly.

- Provide approximate center coordinates, focal length (250mm), pixel size:
  - **3.76 µm** for standard stack (no drizzle or Drizzle 1x)
  - **1.88 µm** for Drizzle 2x (pixel size halved)
- **Enable Distortion Correction** for better star matching
- Catalog: **Gaia DR3** for plate solving (DR3/SP is only needed for SPCC spectroscopic data)
- **Do NOT check "Force values"** — let the solver use FITS header hints. Forcing values fails when the image has a non-standard rotation (e.g., 90° from camera angle).
- **Advanced Parameters:**
  - Sensitivity: **0.30** (lower than default 0.50 — detects more stars for matching)
  - **Try with apparent coordinates on failure:** checked
  - **Try with exhaustive star matching on failure:** checked

> Since PI 1.8.9-1, astrometric solutions are calculated automatically during pre-processing. ImageSolver is needed if WBPP didn't solve the image or if the autocrop lost the solution.

> **Troubleshooting RANSAC failures:** If the solve fails with "RANSAC: Unable to find a valid set of star pair matches", verify: (1) "Force values" is unchecked, (2) exhaustive star matching is enabled, (3) sensitivity is 0.30, (4) pixel size matches the stack (3.76 µm native, 1.88 µm Drizzle 2x). The most common cause is forcing values on a rotated image.

### 2.3 Gradient Removal

1. **SPFC** (SpectrophotometricFluxCalibration)
   - QE Curve: Sony IMX411/455/461/533/571
   - Filter: Optolong L-Pro
   - Catalog: Gaia DR3/SP
   - PSF growth: 1.75

2. **MGC** (MultiscaleGradientCorrection)
   - Load MARS DR1 + MARS-U databases (Preferences → set default files)
   - MARS bands: R, G, B (broadband)
   - Enable "Show gradient model" to verify (set STF precision to **24 bits** to see posterized model)
   - **Gradient scale** (most important parameter):
     - Simple gradients: 1024 or 2048
     - Complex gradients: 512 or 384
     - Extreme cases (severe LP, failed flats): 256 or 128 (use sparingly)
     - Rule: always use the **highest scale that still corrects well** to minimize reference data dependency
   - **Scale factor** (per-channel, adjust independently):
     - Default: 1.0
     - If object traces remain in gradient model → increase
     - If objects appear inverted → decrease
     - Typical range: 0.2–1.5 depending on object brightness
     - Hold **Ctrl** to move all 3 channel sliders simultaneously
   - **Structure separation**: 1–3 (lower = more cohesion, less overcorrection of bright objects)
   - After MGC: may need **BackgroundNeutralization** to fix residual color cast

### 2.4 Star Correction

**BlurXTerminator** — Correct Only

### 2.5 Star Sharpening

**BlurXTerminator**
- Model: `BlurXTerminator.4.mlpackage`
- Evaluate PSF Diameter with **PSFImage** render script
  - Or use Automatic PSF to skip the long evaluation
- Configuration:
  - Sharpen Stars: 0.20
  - Adjust Star Halos: -0.10
  - PSF Diameter: **2.30** (or (FWHMx + FWHMy) / 2 from evaluation)
  - Sharpen Nonstellar: 0.90

### 2.6 Background Reference

**FindBackground** script
- Exclude dark nebulosity if necessary

### 2.7 Color Calibration

**SPCC** (SpectrophotometricColorCalibration)
- Filters: **Optolong L-Pro** (R, G, B individually)
- QE Curve: **Sony IMX411/455/461/533/571**
- White reference: **G2V Star** (unless galaxy is the target)
- Clustered sources: enabled
- PSF growth: 1.25
- Target source count: 8000
- Neutralize background: enabled
- If dark region available: select as background region of interest
- Catalog: **Gaia DR3/SP**

### 2.8 AutoStretch After Calibration

**ScreenTransferFunction** — verify color calibration result.

1. **Link** channels (chain link icon)
2. AutoStretch (nuclear icon) — image should show natural, balanced colors
3. If colors look off, SPCC may need adjustment

### 2.9 Star Removal

**StarXTerminator**
- Model: `StarXTerminator.lite.nonoise.11.mlpackage`
- Generate Star image: selected
- Overlap: 0.20
- Save the star image for reintegration in Phase 4

### 2.10 Noise Reduction (Linear, on starless)

**NoiseXTerminator**
- Model: `NoiseXTerminator.2.mlpackage`
- Denoise: 0.9
- Detail: 0.15
- Iterations: **2**
- Test on preview first

---

## Phase 3: Non-Linear Processing

### 3.1 Stretch

> **HDR targets** (bright galaxy nuclei, M31 core): Use [[HDR-Workflow]] instead of Statistical Astro Stretching.

**Statistical Astro Stretching** script
- Boost: 0.15
- Refer to script manual for parameter guidance

### 3.2 Background Neutralization

**BN** (BackgroundNeutralization)
- Select dark background region of interest if available

**ScreenTransferFunction** — verify background is neutral.

1. **Link** channels (chain link icon)
2. AutoStretch (nuclear icon) — background should appear neutral gray, not tinted
3. **Unlink** and AutoStretch again — channels should be similar; if one is brighter, BN may need a different background reference

### 3.3 Final Noise Reduction (on starless)

**NoiseXTerminator**
- Denoise: 0.9
- Detail: 0.20
- Test on preview first

---

## Phase 4: Star Processing & Reintegration

### 4.1 Star Stretch

**ArcsinhStretch** on the star image from step 2.9
- Protect highlights: enabled
- Test stretch factor — stars should look natural

### 4.2 Star Reintegration

**PixelMath:**
```
~(~starless * ~stars)
```

### 4.3 Final Adjustments

- **CurvesTransformation** — contrast, saturation, color balance (Akima subsplines interpolation)
- **LocalHistogramEqualization** — optional, increases local contrast:
  - Radius: 64
  - Slope limit: 2.0
  - Histogram bins: 8-bit
  - Circular kernel: enabled
- **DarkStructureEnhance** script — optional, for dark nebula lanes
- **ICCProfileTransformation** — convert to sRGB for export
