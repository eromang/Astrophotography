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

- Scale: 3.1"/pixel ([[RedCat-51]] + [[ASI2600MCPro]])
- Evaluate: FWHM, Eccentricity, Median, Stars, Noise
- Reject outliers

### WBPP (Weighted Batch Pre-Processing)

- Drizzle: **2** (strongly recommended over debayerization for color sensors — drizzle involves no data interpolation, while debayerization interpolates 3 out of 4 pixels per channel, introducing photometric errors)
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

### 2.2 ImageSolver

Plate-solve the image for SPCC to work correctly.

- Provide approximate center coordinates, focal length (250mm), pixel size (3.76µm)
- **Enable Distortion Correction** for better star matching
- Requires **Gaia DR3/SP** catalog (not DR3 — DR3/SP has the spectroscopic data SPCC needs)

> Since PI 1.8.9-1, astrometric solutions are calculated automatically during pre-processing. ImageSolver is needed only if WBPP didn't solve the image.

### 2.3 Gradient Removal

1. **SPFC** (SpectrophotometricFluxCalibration)
   - Sensor: IMX571
   - Filter: Optolong L-Pro

2. **MGC** (MultiscaleGradientCorrection)
   - Load MARS DR1 database (Preferences → set default files)
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
- Evaluate PSF Diameter with **PSFImage** render script
  - Or use Automatic PSF to skip the long evaluation
- Configuration:
  - Sharpen Stars: 0.20
  - Adjust Star Halos: -0.10
  - PSF Diameter: (FWHMx + FWHMy) / 2 from evaluation
  - Sharpen Nonstellar: 0.90

### 2.6 Background Reference

**FindBackground** script
- Exclude dark nebulosity if necessary

### 2.7 Color Calibration

**SPCC** (SpectrophotometricColorCalibration)
- Filters: **Sony color sensor filters with UV/IR cut** (R, G, B individually)
- QE Curve: **Ideal Quantum Efficiency** (not IMX571 — Bayer filter array includes QE implicitly for color sensors)
- White reference: G2V Star (unless galaxy is the target)
- If dark region available: select as background region of interest
- Catalog: requires **Gaia DR3/SP** (with spectroscopic data)

### 2.8 AutoStretch After Calibration

**ScreenTransferFunction**
1. Link
2. Autostretch

### 2.9 Star Removal

**StarXTerminator**
- Generate Star image: selected
- Large overlap if dense star fields
- Save the star image for reintegration in Phase 4

### 2.10 Noise Reduction (Linear, on starless)

**NoiseXTerminator**
- Denoise: 0.9
- Detail: 0.15
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

**ScreenTransferFunction**
1. Link
2. Autostretch
3. Unlink

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

- **CurvesTransformation** — contrast, saturation, color balance
- **DarkStructureEnhance** script — optional, for dark nebula lanes
- **ICCProfileTransformation** — convert to sRGB for export
