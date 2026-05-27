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

> Full settings reference: [[WBPP-Reference]]. Settings below are the key values for broadband RGB. Adjust per session as needed.

#### Calibration Tab

- Load calibration frames per [[Master-Library]]:
  - **Bias tab:** bias master + dark flat master (WBPP matches by exposure)
  - **Darks tab:** dark master matching light exposure and temperature
  - **Flats tab:** flat frames matching filter and optical train
- Calibration Settings (Light row): Dark Auto, Flat Auto
- Cosmetic Correction: **Automatic**, High sigma 10
- CFA Settings: CFA Images checked, Mosaic pattern Auto, DeBayer method **VNG**

#### Post-Calibration Tab

- **Drizzle:** Enabled, Scale **2**, Fast mode **unchecked**, Drop shrink **0.90**, Function Square
- Channels: Combined RGB
- Fast Integration: Enabled (for preview)

#### Lights Tab

- **Subframe Weighting:** PSF Signal Weight
- **Image Registration:** Enabled
  - **Distortion Correction:** Enabled (max spline points **4000**) — corrects [[RedCat-51]] field curvature at edges, improves Drizzle 2x quality
- **Local Normalization:** Enabled (critical for multi-night stacks)
- **Image Integration:**
  - Combination: Average
  - Rejection Algorithm: **Winsorized Sigma Clipping**
  - Sigma High: **1.9** (for satellite trail rejection)
  - Large Scale Pixel Rejection: **High** enabled, layers **2**, growth **2**
- **Astrometric Solution:**
  - Coordinates: target RA/DEC (approximate)
  - Focal distance: **250 mm**
  - Pixel size: **3.76 µm** (native — Drizzle is applied post-registration)
  - **Force values: Unchecked** — ASIAIR writes RA/DEC to FITS headers

#### Pipeline Tab

- Output directory: set explicitly
- Active steps: Subframe Weighting, Image Registration, Local Normalization, Image Integration (all checked)
- Linear Defects Correction: unchecked

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

> **SPFC + MGC vs GraXpert:** MGC requires MARS reference data covering your field in matching filters. MARS coverage varies by field — some have broadband R/G/B (e.g., NGC 7000), some don't (e.g., NGC 5746). Always try MGC first; if it fails with "No reference data found for filter 'R'", use **GraXpert** instead. See [[MGC-Reference]] for full tuning guide.

**Option A: GraXpert** (recommended when MARS lacks broadband coverage)

- AI mode — no manual tuning required
- Works on any field regardless of MARS coverage
- Apply after SPFC (flux calibration is still beneficial for SPCC later)

**Option B: SPFC + MGC** (when MARS has coverage)

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
- Unscreen stars: enabled (produces a better star layer for screen-mode blending in step 4.2)
- Overlap: 0.20
- Save the star image for reintegration in Phase 4

### 2.10 Noise Reduction (Linear, on starless)

**NoiseXTerminator**
- Model: `NoiseXTerminator.3.mlpackage` (AI v3 — no Detail parameter; v2 had Detail: 0.15)
- Denoise: 0.9
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
- Iterations: 1 (lighter pass on non-linear data)
- Test on preview first

---

## Phase 4: Star Processing & Reintegration

### 4.1 Star Reduction (Optional)

**MorphologicalTransformation** — if stars are still too prominent after BXT
- Operator: Erosion (Minimum)
- Iterations: 1
- Size: 5 elements, circular kernel
- Amount: **0.50** (do not go to 1.0 — stars were already reduced by BXT)

### 4.2 Star Stretch

**ArcsinhStretch** on the star image from step 2.9
- Protect highlights: enabled
- Test stretch factor — stars should look natural

### 4.3 Star Reintegration

**PixelMath:**
```
~(~starless * ~stars)
```

### 4.4 Final Adjustments

- **CurvesTransformation** — see [[CurvesTransformation-Reference]] for full guide
  - Order: Luminance → Saturation → R → G → B (apply after each group)
  - Interpolation: Akima subsplines
  - L: S-curve for contrast (up 1/3 from top, down 1/4 from bottom)
  - S: Shallow boost in upper 1/3
  - G: Pull down lower 1/3 to fix green cast (common with broadband L-Pro on emission fields)
  - R: Boost middle for Ha emission targets
  - B: Pull down lower 1/4 to neutralize space
- **SCNR** — if green cast persists after CurvesTransformation:
  - Channel: Green, Amount: 0.5, Protection: Average Neutral
- **LocalHistogramEqualization** — see [[LHE-Reference]] for full guide. Two-pass approach recommended:
  - Pass 1 (large structures): Kernel Radius 120–160, Contrast Limit 1.5–2.0, Amount **0.3–0.5**
  - Pass 2 (small structures): Kernel Radius 40–80, Contrast Limit 1.5–2.0, Amount **0.3–0.5**
  - Consider masking background with RangeSelection
  - **Amount at 1.0 is too much** — always reduce to 0.3–0.5
- **DarkStructureEnhance** script — optional, for dark nebula lanes
- **ICCProfileTransformation** — convert to sRGB for export
