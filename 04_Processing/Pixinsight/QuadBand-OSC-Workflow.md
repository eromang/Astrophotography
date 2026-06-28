---
title: "PixInsight Quad Band OSC Workflow"
type: processing-workflow
software: "PixInsight"
tags:
  - processing/pixinsight
---

# Quad Band OSC Processing

Processing workflow for narrowband data captured with the [[Antlia-FQuad]] filter on the [[ASI2600MCPro]] (color/OSC camera).

> **Key difference from broadband RGB:** The Quad Band filter passes Ha, OIII, Hb, and SII simultaneously onto a Bayer matrix sensor. SPCC can be used with combined filter curves (Sony CMOS + Antlia Quadband per Bayer channel) — see step 2.4 (run on the star-full image, before star removal). Channel manipulation is required to separate and balance the narrowband signal.

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

> Full settings reference: [[WBPP-Reference]]. Settings below are the key values for narrowband quad band. Adjust per session as needed.

#### Calibration Tab

- Load calibration frames per [[Master-Library]]:
  - **Bias tab:** bias master + dark flat master (WBPP matches by exposure)
  - **Darks tab:** dark master matching light exposure and temperature
  - **Flats tab:** flat frames matching **[[Antlia-FQuad]]** filter and optical train

> ⚠️ **NoFilter lights won't match a FQuad flat → flat silently skipped.** Manual filters (no EFW) mean lights group as `NoFilter` while the FQuad flat groups as `FQuad`, so WBPP applies **no flat**. Before WBPP, stamp the lights: `python3 scripts/set_filter.py <Lights> --filter FQuad --recursive --apply` (use `--filter` because reprocess/SFS `.xisf` filenames have no filter token; it writes the XISF filter *property* WBPP reads). **WBPP caches metadata on add — if lights were already loaded, Clear the Lights tab and re-add them** so they regroup under `FQuad`. Verify before Run: every light group shows **`Flat ✓`** on the Calibration tab, or the **Calibration Diagram** shows a `÷ MASTER Flat` node. See [[../Calibration/Calibration-Strategy#FITS FILTER keyword fix]]. (Learned 2026-06-22, M42 reprocess.)

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
  - **Distortion Correction:** Enabled (max spline points **4000**) — corrects [[RedCat-51]] field curvature
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

> **Drizzle 2x changes pixel scale:** output resolution is 1.55"/px (half of native 3.1"/px), pixel size effectively 1.88 µm. WBPP may not plate-solve the drizzled output — run ImageSolver (step 2.0) on the drizzle master if SPFC fails with "no astrometric solution".

---

## Phase 2: Linear Processing

### 2.0 ImageSolver (if needed)

Plate-solve the image for SPFC/SPCC to work correctly. Required if using **Option B (SPFC + MGC)** for gradient removal or **step 2.4 (SPCC)** for color calibration (star-full, before star removal).

- Provide approximate center coordinates, focal length (250mm), pixel size:
  - **3.76 µm** for standard stack (no drizzle or Drizzle 1x)
  - **1.88 µm** for Drizzle 2x (pixel size halved)
- **Enable Distortion Correction** for better star matching
- Catalog: **Gaia DR3** for plate solving
- **Do NOT check "Force values"** — let the solver use FITS header hints. Forcing values fails when the image has a non-standard rotation.
- **Advanced Parameters:**
  - Sensitivity: **0.30** (lower than default 0.50)
  - **Try with apparent coordinates on failure:** checked
  - **Try with exhaustive star matching on failure:** checked

> WBPP normally adds an astrometric solution automatically. ImageSolver is needed if the autocrop lost the solution or if WBPP didn't solve.

> **Troubleshooting RANSAC failures:** Verify: (1) "Force values" is unchecked, (2) exhaustive star matching is enabled, (3) sensitivity is 0.30, (4) pixel size matches the stack (3.76 µm native, 1.88 µm Drizzle 2x).

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
   - Use **MARS DR2** database (`MARS-DR2-1.0.3-s08.xmars`, + `u01`) — includes Ha and **O-III band** data; doubles DR1 coverage (since 2026-06). See [[MGC-Reference#MARS Database]]
   - Assign MARS bands: **Ha** to red channel, **O-III** to green and blue channels
   - Enable "Show gradient model" to verify (set STF precision to **24 bits**)
   - **Gradient scale**: **2048** for bright frame-filling nebulae (M42/M16/M17) — lower values (≤1024) let structure-separation carve a *dark hole* at the object core; 512–1024 only for small objects on open sky. See [[Gradient-MGC-vs-GraXpert-M42]].
   - **Structure separation**: **1** for narrowband images (more cohesion, less overcorrection of bright nebulae)
   - ⚠️ **On near-equatorial fields (Dec ≲ 0°), GraXpert usually beats MGC even with DR2 coverage** — MGC's reference fit degrades at the coverage edge. Compare with `scripts/gradient_check.py --against` before committing; on M42 (Dec −5°) GraXpert was ~2× flatter across the entire MGC parameter space.
   - **Scale factor** tuning per channel on a preview:
     - If nebula traces remain → increase scale factor
     - If nebula appears inverted → decrease scale factor
     - Typical Ha (red) channel: **~0.2–0.5** (bright Ha nebulae need low values)
     - Typical O-III (green/blue) channels: **~1.4–1.8**
     - Hold **Ctrl** to move all sliders simultaneously

**Which to use:** Try both on a preview. Some images respond better to MGC (especially with strong vignetting), others to GraXpert (especially with complex nebula shapes). Results are image-dependent.

> **Decide objectively, not by eye:** save each candidate as a **linear** `.xisf` and run `python3 scripts/gradient_check.py methodB.xisf --against methodA.xisf` — it scores background flatness + **wing preservation** (the over-subtraction failure on frame-filling nebulae) and names a winner. Add `--model bg.xisf` to confirm a background model carries no nebula imprint. See [[Gradient-Check]]. On extended objects (M42/M16/M17), MGC should preserve the outer wings better than GraXpert — this is how you verify it actually did.

### 2.3 Star Correction

**BlurXTerminator** — Correct Only. ⚠️ **Linear data only** (AI4 processes linear directly — *"processing a stretched image is not recommended; results cannot be considered deconvolution"*). AI4 also handles **M42's extreme dynamic range and drizzle-2× upsampling artifacts**. See [[BlurXTerminator 2.0_AI4 Release]].
- Corrects optical aberrations (coma, elongation, field curvature) — stars come out rounder.
- ⚠️ **Correct Only also *tightens* stars** — it noticeably reduces FWHM, not just shape (M42 drizzle-2× example: **4.54 → 2.50 px**, ecc 0.42 → 0.27). So **do not reuse a pre-BXT PSF measurement for the Sharpen pass** — re-measure on this corrected output (step 2.5).
- 🟡 **Narrowband order (RC-Astro):** deconvolve in **distinct-channel form (the debayered OSC RGB) BEFORE any HOO channel mixing** (Phase 3) — mixing/boosting channels before BXT alters the PSF and gives inconsistent results on bright stars. Our order (BXT here, HOO in Phase 3) already does this. ✓
- 🟢 **Order:** Correct Only (here) → **SPCC (2.4)** → Sharpen (2.5) → star removal (2.6). Splitting the BXT passes around SPCC gives more consistent colour calibration (RC-Astro).

### 2.4 Color Calibration (SPCC) — star-full, BEFORE star removal

🔴 **SPCC must run here, while the image still has stars.** SPCC computes colour from **stellar photometry** vs the Gaia spectrophotometric catalog — **it cannot run on a starless image** (the old "SPCC at 3.5, after star removal" order was a bug). Run it on the **star-full debayered OSC RGB**, *before* the HOO channel remap; the HOO remap (Phase 3) is an artistic step on the already-calibrated data.

**SPCC** (SpectrophotometricColorCalibration):
- Filters: **Sony CMOS R/G/B + Antlia Quadband** (combined per-Bayer-channel curves, **not** narrowband mode)
- QE Curve: **Sony IMX411/455/461/533/571**
- White reference: **G2V Star** · Bandwidth **3 nm** all filters
- Clustered sources: enabled · PSF growth 1.25 · Target sources 8000
- Neutralize background: enabled (ROI on empty dark sky)
- Catalog: **Gaia DR3/SP** · image must be **plate-solved** (2.0)

> Combined filter curves (sensor QE × filter transmission per Bayer channel), not narrowband mode — the Bayer matrix mixes the narrowband signals across channels, so combined curves model the real OSC response.
> **If you only realise stars are gone *after* removal** (starless HOO already built): SPCC is no longer possible — **balance manually** instead (BackgroundNeutralization + CurvesTransformation in the colour phase). Acceptable for an artificial HOO palette; just not as repeatable.

### 2.5 Star Sharpening

**BlurXTerminator**
- Model: `BlurXTerminator.4.mlpackage`
- 🔴 **Measure PSF Diameter on the *Correct-Only output* (step 2.3 result), NOT the raw/drizzle master.** Correct Only roughly halves the FWHM, so the pre-correction value over-sharpens. Use **PSFImage** in PI, or offline `python3 scripts/psf_image.py <correct-only.xisf>` (see [[../../scripts/README.md#psf_image.py — offline PSF / FWHM measurement (PixInsight PSFImage equivalent)|scripts/README]]) → use the reported `BXT PSF Diameter`.
  - Or use Automatic PSF
- Configuration:
  - Sharpen Stars: 0.20
  - Adjust Star Halos: -0.10
  - PSF Diameter: **measured value** (post-correction; ~2.3–2.6 px typical for this rig at drizzle-2× — e.g. 2.5 on the M42 reprocess)
  - Sharpen Nonstellar: 0.90

### 2.6 Star Removal

⚠️ **SPCC (2.4) must already be done before this** — it needs stars. Once removed here, colour calibration is no longer possible (fall back to manual balancing).

**StarXTerminator** (v2.4.12 / AI 11 as of 2026-06). Run on **linear** data (where we are) — RC-Astro recommends SXT as early as possible, before any stretch. ⚠️ **Never run SXT after the HDR stretch / arcsinh / GHS** — those alter star profiles so the AI no longer recognises stars. See [[StarXTerminator Usage Notes]] (`rc-astro.com/starxterminator-usage-notes`).
- Select AI: AI version **11**
- Generate Star image: selected
- 🔴 **Unscreen stars: OFF** — Unscreen is for *nonlinear (stretched)* images. On **linear** data use **simple subtraction** (Unscreen off) → best star colour. (Pairs with screen-blend recombine in step 6.1.)
- **Large Overlap: ON for bright-core / frame-filling nebulae** (M42, M16, M17) and wide/busy star fields — raises tile overlap 20 %→50 %, which is what removes the bright-core nebula remnant (the M42 "Trapezium blob"). Leave **off** for ordinary fields (≈2× faster). *RC-Astro names M42 as the textbook Large-Overlap case.*
- ⚠️ **Don't STF-AutoStretch the resulting star image** — SXT carries the original's STF to the star image; auto-stretch destroys it and fakes faint residuals.
- Keep the star image for later reintegration

> From this point, work on the **starless** image. Stars are processed separately.

### 2.7 Noise Reduction (Linear)

**NoiseXTerminator** on starless image. ⚠️ **Never denoise before deconvolution** — NXT comes *after* BXT (it does ✓). NXT handles per-channel noise differences, so run it on the **combined color image**, not per-channel. Use the **real-time preview** to tune. See [[NoiseXTerminator 2_AI3 User Manual (PixInsight)]].
- Model: `NoiseXTerminator.3.mlpackage` (AI v3 — `iterations` is v3-only; `detail` was v2-only, removed)
- **Simple mode:** Denoise **0.85–0.9** (don't go to 1.0 — over-smooths), Iterations **2** (more iterations retain detail in noisy areas but can add artifacts)
- 🟢 **Better — separation modes (NXT2/AI3):** color noise is the objectionable part, so **reduce color > intensity**, and **less LF reduction** to preserve dust/nebula structure. RC-Astro's recommended combined settings:
  - HF intensity **80–90 %** · HF color **90–100 %**
  - LF intensity **50–70 %** · LF color **100 %**
  - tune **HF/LF Scale** per object (set Denoise-LF = 0 temporarily in real-time preview to find it)
- Test on a preview first. *(A final, lighter NXT pass on the stretched image — Phase 4.4 — sees the final HOO colour and is the one the "after channel combination" guidance most favours.)*

### 2.8 Ha Emission Line Separation (Optional)

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

> 🟡 **HOO is optional — and often wrong for *broadband-rich* emission nebulae (M42, M8).** Targets with strong Ha **and** OIII already show rich, balanced colour straight from the SPCC'd natural-colour image (red Ha, teal OIII, blue reflection). Forcing HOO (R=Ha, G=B=OIII) there gains little and **introduces chromatic G=B colour noise**. Reserve HOO/Foraxx for **faint dual-narrowband** targets that need the separation. For M42-class objects, consider **keeping the natural SPCC colour** and getting the Ha/OIII pop from a **saturation curve + SCNR** instead. (M42 reprocess, 2026-06-23 — HOO added noise for no benefit; natural colour was better.)

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

**ScreenTransferFunction** — verify HOO reassembly.

1. **Link** channels, AutoStretch — should show the HOO color palette (red Ha, teal OIII)
2. **Unlink**, AutoStretch — check channel balance

### 3.5 Color — already calibrated at 2.4 (SPCC), or balance manually

🔴 **SPCC was moved to step 2.4** (the linear, *star-full* phase) — it photometers stars and **cannot run here on the starless HOO composite**. Don't try to run SPCC at this point.

- **If you ran SPCC at 2.4:** the OSC RGB is already colour-calibrated; the HOO remap inherited that. Proceed to the stretch — just verify the background is neutral (BackgroundNeutralization if needed).
- **If stars were already removed without SPCC:** balance the HOO manually — **BackgroundNeutralization** (neutral sky) + **CurvesTransformation** (Ha/OIII balance to taste), done in the colour phase. Fine for an artificial HOO palette.

---

## Phase 4: Non-Linear Processing (Stretching)

### 4.1 Stretch

> **HDR targets** (bright core nebulae like M42, M16, M17): Use [[HDR-Workflow]] instead of GHS.

**Option A: Multiscale Adaptive Stretch** (modern, recommended)
- The PI 2026 method — stretches faint and bright structures at independent scales, lifting nebula detail without crushing bright cores; well-suited to the strong dynamic range of dual-band emission fields. See [[Multiscale Adaptive Stretch – Das bietet die neue Stretch-Methode mit PixInsight 2026]].
- Apply to the **starless** HOO composite; tune on a preview, then clean with the final NoiseXTerminator pass (4.4).

**Option B: GeneralizedHyperbolicStretch (GHS)**
- Offers more control over midtone transfer than HistogramTransformation
- Start with Symmetry Point (SP) near the histogram peak
- Apply in small increments

**Option C: HistogramTransformation**
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

**ScreenTransferFunction** — verify background is neutral.

1. **Link** channels, AutoStretch — background should appear neutral, not tinted
2. **Unlink**, AutoStretch — channels should be similar in the background areas

### 4.4 Final Noise Reduction

**NoiseXTerminator** on the stretched starless image
- Denoise: 0.7–0.8 (lighter than linear pass)
- Iterations: 1

---

## Phase 5: Star Processing

Work on the star image saved from step 2.5.

### 5.1 Star Reduction (Optional)

**MorphologicalTransformation** — if stars are still too prominent after BXT
- Operator: Erosion (Minimum)
- Iterations: 1
- Size: 5 elements, circular kernel
- Amount: **0.50** (do not go to 1.0 — stars were already reduced by BXT)

### 5.2 Star Stretch

**ArcsinhStretch**
- Protect highlights: enabled
- Test stretch factor — stars should look natural, not blown out

### 5.3 Star Color

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

This is a **screen blend** — combines the starless nebula with the star field. Per [[StarXTerminator Usage Notes]], this is the correct partner for **subtraction**-extracted (Unscreen-off, linear) stars: *recombine after stretching both, using screen blending.* So the linear flow is **subtraction-extract → stretch starless & stars separately → screen-blend here** (do **not** switch to additive — RC-Astro pairs subtraction with screen blend).

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
| Color calibration | SPCC with G2V reference | SPCC with combined filter curves — see step 2.4 (before star removal) |
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
