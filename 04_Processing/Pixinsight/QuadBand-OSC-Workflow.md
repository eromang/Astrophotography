---
title: "PixInsight Quad Band OSC Workflow"
type: processing-workflow
software: "PixInsight"
tags:
  - processing/pixinsight
---

# Quad Band OSC Processing

Processing workflow for narrowband data captured with the [[Antlia-FQuad]] filter on the [[ASI2600MCPro]] (color/OSC camera).

> **Key difference from broadband RGB:** The Quad Band filter passes Ha, OIII, Hb, and SII simultaneously onto a Bayer matrix sensor. SPCC can be used with combined filter curves (Sony CMOS + Antlia Quadband per Bayer channel) — see step 3.5. Channel manipulation is required to separate and balance the narrowband signal.

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
Prioritizes tight stars (FWHM²), good signal, and round stars.

### 1.2 WBPP (Weighted Batch Pre-Processing)

- Drizzle: **2**
- Dark master cosmetic correction
- Image Registration: **enable Distortion Correction** (max spline points 4000)
- Satellite trail removal:
  - Rejection Algorithm: Winsorized Sigma Clipping (or Auto)
  - Sigma High: ~1.9
  - Large Scale Pixel Rejection: **High** enabled, layers 2, growth 2
- Calibration: darks, flats, dark flats, bias (see [[Master-Library]])

---

## Phase 2: Linear Processing

### 2.0 ImageSolver (if needed)

Plate-solve the image for SPFC/SPCC to work correctly. Required if using **Option B (SPFC + MGC)** for gradient removal or **step 3.5 (SPCC)** for color calibration.

- Provide approximate center coordinates, focal length (250mm), pixel size:
  - **3.76 µm** for standard stack (no drizzle or Drizzle 1x)
  - **1.88 µm** for Drizzle 2x (pixel size halved)
- **Enable Distortion Correction** for better star matching
- Catalog: **Gaia DR3** for plate solving

> WBPP normally adds an astrometric solution automatically. ImageSolver is needed if the autocrop lost the solution or if WBPP didn't solve.

> If the first solve fails with "RANSAC: Unable to find a valid set of star pair matches", ImageSolver will automatically retry with mirrored coordinates. This is normal.

### 2.1 AutoStretch (visualization only)

**ScreenTransferFunction** — display-only, does not modify data. Image remains linear.

1. Click the **nuclear icon** (yellow/black, bottom-left) to AutoStretch in **linked** mode (chain link icon = linked)
2. **Unlink** channels (click chain link icon at top-left to break the link)
3. AutoStretch again — shows each channel independently, reveals color imbalances

> The image will look strongly tinted — this is normal for narrowband data on a color camera.
> Never drag STF to HistogramTransformation until Phase 4 (stretching). All Phase 2–3 processing must be done on linear data.

### 2.2 Gradient Removal

**Option A: GraXpert** (recommended for simplicity)

- AI mode handles narrowband gradients well
- No manual tuning required
- If using DBE as fallback: place sample points carefully avoiding nebula regions

**Option B: SPFC + MGC** (more control, image-dependent)

1. **SPFC** (SpectrophotometricFluxCalibration)
   - QE Curve: Sony IMX411/455/461/533/571
   - Filters: **Sony CMOS R/G/B + Antlia Quadband** (combined per-Bayer-channel curves)
   - Bandwidth: **3nm** for all channels
   - Wavelengths: Ha (656.3nm) red, OIII (500.7nm) green and blue
   - Catalog: Gaia DR3/SP
   - PSF growth: 1.75

2. **MGC** (MultiscaleGradientCorrection)
   - Use MARS DR1 database (v1.1+ includes both Ha and **O-III band** data)
   - Assign MARS bands: **Ha** to red channel, **O-III** to green and blue channels
   - Enable "Show gradient model" to verify (set STF precision to **24 bits**)
   - **Gradient scale**: 512–1024 (lower = finer correction, higher = safer)
   - **Structure separation**: **1** for narrowband images (more cohesion, less overcorrection of bright nebulae)
   - **Scale factor** tuning per channel on a preview:
     - If nebula traces remain → increase scale factor
     - If nebula appears inverted → decrease scale factor
     - Typical Ha (red) channel: **~0.2–0.5** (bright Ha nebulae need low values)
     - Typical O-III (green/blue) channels: **~1.4–1.8**
     - Hold **Ctrl** to move all sliders simultaneously

**Which to use:** Try both on a preview. Some images respond better to MGC (especially with strong vignetting), others to GraXpert (especially with complex nebula shapes). Results are image-dependent.

### 2.3 Star Correction

**BlurXTerminator** — Correct Only
- Fixes optical aberrations without changing star size

### 2.4 Star Sharpening

**BlurXTerminator**
- Model: `BlurXTerminator.4.mlpackage`
- Evaluate PSF Diameter with **PSFImage** render script
  - Or use Automatic PSF
- Configuration:
  - Sharpen Stars: 0.20
  - Adjust Star Halos: -0.10
  - PSF Diameter: **2.30** (or (FWHMx + FWHMy) / 2 from evaluation)
  - Sharpen Nonstellar: 0.90

### 2.5 Star Removal

**StarXTerminator**
- Model: `StarXTerminator.lite.nonoise.11.mlpackage`
- Generate Star image: selected
- Overlap: 0.20
- Keep the star image for later reintegration

> From this point, work on the **starless** image. Stars are processed separately.

### 2.6 Noise Reduction (Linear)

**NoiseXTerminator** on starless image
- Model: `NoiseXTerminator.2.mlpackage`
- Denoise: 0.9
- Detail: 0.15
- Iterations: **2**
- Test on preview first

### 2.7 Ha Emission Line Separation (Optional)

Remove Ha crosstalk from the green and blue Bayer channels. On the [[ASI2600MCPro]], green and blue pixels are partially sensitive to Ha (656nm), contaminating the OIII signal. This step subtracts the scaled Ha contribution, producing cleaner OIII for channel extraction in Phase 3.

**PixelMath** (uncheck "Use a single expression"):

```
R: $T
G: $T - ($T[0] - med($T[0])) * scale_G
B: $T - ($T[0] - med($T[0])) * scale_B
```

Where `scale_G` and `scale_B` are camera+filter-specific constants determined once and reused.

**Finding the scale factors (one-time calibration):**

1. Select a preview containing visible Ha nebulosity
2. Start with a high scale factor (e.g., 0.5) — Ha structures will appear inverted
3. Decrease gradually until the inversion just disappears
4. The correct value minimizes Ha traces without overcorrecting
5. Repeat for each channel (G and B typically need different values)

Once determined, save the PixelMath process icon. These factors are reusable for all images from the [[ASI2600MCPro]] + [[Antlia-FQuad]] combination.

**ASI2600MC Pro + Antlia Quad Band scale factors:**

| Channel | Scale Factor |
|---------|-------------|
| Green (scale_G) | TBD — determine on first processing session |
| Blue (scale_B) | TBD — determine on first processing session |

> Update this table after calibrating. Factors should remain constant unless atmospheric conditions are anomalous.

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

### 3.5 Color Calibration (Optional)

After reassembling channels into an HOO composite, SPCC can calibrate the color balance using combined filter curves.

**SPCC** (SpectrophotometricColorCalibration):
- Filters: **Sony CMOS R/G/B + Antlia Quadband** (combined per-Bayer-channel curves, not narrowband mode)
- QE Curve: **Sony IMX411/455/461/533/571**
- White reference: **G2V Star**
- Bandwidth: **3nm** for all filters
- Clustered sources: enabled
- PSF growth: 1.25
- Target source count: 8000
- Neutralize background: enabled (select background ROI free of nebulosity)
- Catalog: **Gaia DR3/SP**

> This uses combined filter curves (sensor QE × filter transmission per Bayer channel) rather than pure narrowband mode. This is the correct approach for OSC + quad-band filters — the Bayer matrix mixes the narrowband signals across channels, so combined curves model the actual sensor response more accurately.

> Optional — manual color balancing via CurvesTransformation (Phase 4.2) remains the alternative.

---

## Phase 4: Non-Linear Processing (Stretching)

### 4.1 Stretch

> **HDR targets** (bright core nebulae like M42, M16, M17): Use [[HDR-Workflow]] instead of GHS.

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
- **LocalHistogramEqualization** — optional, increases local contrast in nebula structure:
  - Radius: 64
  - Slope limit: 2.0
  - Histogram bins: 8-bit
  - Circular kernel: enabled
- **ICCProfileTransformation** — convert to sRGB for export

### 6.3 Export

- TIFF 16-bit for archival
- JPEG/PNG for sharing

---

## Quick Reference: Broadband vs Quad Band

| Step | Broadband (L-Pro) | Quad Band |
|------|-------------------|-----------|
| Color calibration | SPCC with G2V reference | SPCC with combined filter curves (optional) — see step 3.5 |
| Gradient removal | SPFC/MGC (PI 1.9) or DBE | GraXpert or SPFC/MGC — see step 2.2 |
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
