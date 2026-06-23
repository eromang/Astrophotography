---
title: "PixInsight RGB Broadband Workflow"
type: processing-workflow
software: "PixInsight"
tags:
  - processing/pixinsight
---

# RGB Broadband Processing (OSC)

Processing workflow for broadband data captured with the [[Optolong-LPro]] filter on the [[ASI2600MCPro]] (color/OSC camera). Use this for galaxies and reflection nebulae.

> **For open star clusters** (star-dominated fields, no nebulosity), use the [[OpenCluster-Workflow]] instead.
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

> ⚠️ **NoFilter lights won't match a filter-labelled flat (e.g. L-Pro) → flat silently skipped.** Stamp the lights' filter before WBPP and **Clear + re-add** them if already loaded (WBPP caches metadata on add). Full procedure + verification in [[../Calibration/Calibration-Strategy#FITS FILTER keyword fix]].

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
  - ⚠️ **CRITICAL**: WBPP auto-changes the Image Solver default Pixel size from 3.76 → 1.88 after each run completes (presumably matching the drizzle-scaled output for "next" use). **Manually re-verify 3.76 µm before EVERY WBPP launch** — running with 1.88 makes the per-frame solver fail and produces `Astrometric solution: 1 solved, 3 failed` in the execution monitor. Empirical 2026-05-27 ([[../../05_Sessions/2026/Processing/2026-05-27-Processing|Mel 111 processing session]]).

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
- **Catalog — this is the #1 cause of solve failures, see warning below:**
  - For **local/offline** solving, the **Local XPSD server must be the *astrometric* Gaia DR3** (`gdr3-*.xpsd`), **NOT** the spectrophotometric **DR3/SP** (`gdr3sp-*.xpsd`). SP is for SPCC only — it's too sparse/biased to plate-solve. Astrometric catalog on T7: `Gaia DR3 (astrometric)/` (file `gdr3-1.0.0-01.xpsd`, ≤ mag 16.59; +`-02` to 17.61 for margin).
  - **Online fallback** (no astrometric XPSD installed): select **Online star catalog → Gaia DR2**, **uncheck "Automatic limit magnitude", set Limit magnitude 16** (a deep auto-limit truncates the VizieR query at its 50k-row cap → only a handful of in-frame stars → fail).
- **Do NOT check "Force values"** — let the solver use FITS header hints.
- **Image scale** — either path works, they're equivalent: **Focal 250 mm + Pixel 3.76 µm**, *or* **Resolution 3.10 ″/px** native (**1.548 ″/px** for Drizzle 2×). If the Resolution readout looks half-scale (1.55 when you expect 3.10), it's a stale-field artifact — re-type it; it is *not* what blocks a solve.
- **Advanced Parameters:**
  - Sensitivity: **0.30** (lower than default 0.50 — detects more stars for matching)
  - **Try with apparent coordinates on failure:** checked
  - **Try with exhaustive star matching on failure:** checked

> Since PI 1.8.9-1, astrometric solutions are calculated automatically during pre-processing. ImageSolver is needed if WBPP didn't solve the image or if the autocrop lost the solution.

> **Troubleshooting RANSAC failures — root cause is almost always the CATALOG, not the geometry.** Confirmed empirically on Mel 111 ([[../../05_Sessions/2026/Processing/2026-06-01-Astrometric-Diagnosis|2026-06-01 diagnosis]]): with **correct** scale, center, and clean stars, the solve still failed `RANSAC: Unable to find a valid set of star pair matches` — because the only local catalog installed was **Gaia DR3/SP**. The SP subset exhausts at ~6000 stars in a field (the magnitude search flatlines and maxes the limit at 25.56) and lacks the bright anchor stars a cluster field needs. **Fix, in order:** (1) use the **astrometric** Gaia DR3 XPSD locally, or online Gaia DR2 + manual limit-mag 16; (2) sensitivity 0.30 + exhaustive matching; (3) "Force values" unchecked; (4) scale right (3.76 µm native / 1.88 µm Drizzle 2×). Scale, rotation, and "force values" are **rarely** the real culprit — check the catalog first.

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
   - Load **MARS DR2 + u01** databases (Preferences → set default files) — DR2 doubles DR1 coverage (since 2026-06); see [[MGC-Reference#MARS Database]]
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

**BlurXTerminator** — Correct Only. ⚠️ **Linear data only** (AI4 deconvolves linear directly; don't run it on stretched data). See [[BlurXTerminator 2.0_AI4 Release]].
- ⚠️ Correct Only also **tightens** stars (reduces FWHM), not just shape — so re-measure the PSF on this output for the Sharpen pass; don't reuse a pre-BXT value.
- 🟢 **Best colour order (RC-Astro): Correct Only → SPCC → Sharpen.** Running Correct Only *before* SPCC gives more consistent colour calibration (better R/G, B/G dispersion); do the **Sharpen** pass *after* SPCC. I.e. split the two BXT passes around the colour-calibration step rather than running both back-to-back.

### 2.5 Star Sharpening

**BlurXTerminator**
- Model: `BlurXTerminator.4.mlpackage`
- 🔴 **Measure PSF Diameter on the Correct-Only output (step 2.4 result), NOT the raw/drizzle master** — Correct Only roughly halves the FWHM, so the pre-correction value over-sharpens. Use **PSFImage** in PI or offline `python3 scripts/psf_image.py <correct-only.xisf>` (see [[../../scripts/README.md#psf_image.py — offline PSF / FWHM measurement (PixInsight PSFImage equivalent)|scripts/README]]).
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

**StarXTerminator** — run on **linear** data, before any stretch. ⚠️ Never after arcsinh/GHS/HDR (alters star profiles → stars not recognised). See [[StarXTerminator Usage Notes]].
- Model: `StarXTerminator.lite.nonoise.11.mlpackage` (AI 11)
- Generate Star image: selected
- 🔴 **Unscreen stars: OFF** — Unscreen is for nonlinear images; on linear data use **subtraction** (best star colour). Pairs with screen-blend recombine (step 4.3).
- **Large Overlap: ON for bright-core / frame-filling objects** and wide/busy fields (tile overlap 20→50 %; clears bright-core remnants); off for ordinary fields (≈2× faster).
- ⚠️ **Don't STF-AutoStretch the star image** (destroys the STF SXT carried over).
- Save the star image for reintegration in Phase 4

### 2.10 Noise Reduction (Linear, on starless)

**NoiseXTerminator** — never before BXT (it's after ✓); run on the **combined colour image**, tune with **real-time preview**. See [[NoiseXTerminator 2_AI3 User Manual (PixInsight)]].
- Model: `NoiseXTerminator.3.mlpackage` (AI v3 — `iterations` v3-only; `detail` was v2-only)
- **Simple mode:** Denoise **0.85–0.9** (avoid 1.0), Iterations **2**
- 🟢 **Separation modes (NXT2/AI3):** reduce **color > intensity**; keep **LF low** to preserve dust. RC-Astro combined defaults: HF intensity **80–90 %**, HF color **90–100 %**, LF intensity **50–70 %**, LF color **100 %**; tune **HF/LF Scale** per object.
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

**PixelMath** (screen blend):
```
~(~starless * ~stars)
```

Screen blend is the correct partner for **subtraction**-extracted (Unscreen-off, linear) stars — recombine *after* stretching both starless and stars separately. See [[StarXTerminator Usage Notes]].

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
