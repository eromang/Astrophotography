---
title: "2026-04-01 Processing Session"
type: processing-session
date: 2026-04-01
software: "PixInsight"
targets_processed:
  - "[[NGC7000-North-America]]"
tags:
  - session/processing
---

# 2026-04-01 — NGC 7000 Reprocessing

Reprocessing of NGC 7000 (North America Nebula) using the [[RGB-Workflow]] with current PixInsight 1.9.3 tools.

## Source Data

- **Target:** [[NGC7000-North-America]]
- **Lights:** 197 after SFS approval (from 247 input, 6 nights at -10°C only)
- **Excluded from input:** Night 1 (9 frames, -20°C) and Night 3 (32 frames, -20°C) — no dark master at 300s -20°C
- **Rejected by SFS:** 50 frames (worst seeing, high eccentricity, twilight)
- **Exposure:** 300s × 197 = 59,100s (16.4h)
- **Filter:** [[Optolong-LPro]]
- **Gain:** 100
- **Temperature:** -10°C
- **Camera:** [[ASI2600MCPro]]
- **Telescope:** [[RedCat-51]] (250mm f/4.9)
- **Working copy:** `~/Desktop/NGC7000_Reprocessing/` (15 GB)
- **SSD source:** `/Volumes/T7/Astrophotography/Objects/Nebuleuses/ASI2600MC-REDCAT51/NGC_7000_North_America_Nebula/`

## Working Copy Structure

```
NGC7000_Reprocessing/
├── Lights/                 247 xisf (input, 6 nights at -10°C)
├── SFS/                    197 xisf (approved by SubFrameSelector)
├── Calibration/
│   ├── Dark/               1 master (300s, g100, -10°C)
│   ├── Flat/               50 raw flats (60ms, L-Pro) — WBPP will stack
│   ├── DarkFlat/           1 master (60ms)
│   └── Bias/               1 master (1ms, g100)
├── Docs/                   PixInsight process outputs and logs
└── Screenshots/            Screenshots for Claude analysis
```

## Calibration Frames

| Type | Exposure | Count | Format | File |
|------|----------|-------|--------|------|
| Dark | 300s, g100, -10°C | 1 | Master | `Calibration/Dark/masterDark_BIN-1_6248x4176_EXPOSURE-300.00s_DARK-300.0s.xisf` |
| Flat | L-Pro, 60ms, g100 | 50 | Raw | `Calibration/Flat/*.fit` — WBPP will generate master |
| Dark Flat | 60ms, g100 | 1 | Master | `Calibration/DarkFlat/masterDark_BIN-1_6248x4176_EXPOSURE-0.06s.xisf` |
| Bias | g100, 1ms | 1 | Master | `Calibration/Bias/masterBias_BIN-1_6248x4176_BIAS-1.0ms.xisf` |

> The -20°C nights were excluded to avoid calibration mismatch (no 300s -20°C dark master). If you acquire one in the future, reintegrate those 41 frames for the full 24h stack.

---

## Step-by-Step Reprocessing

### Phase 1: Evaluation & Stacking

#### Step 1 — SubFrameSelector (completed)

Evaluated all 247 lights from `~/Desktop/NGC7000_Reprocessing/Lights/`.

**Overall statistics:**

| Metric | Min | Avg | Median | Max |
|--------|-----|-----|--------|-----|
| FWHM | 4.81" | 6.96" | 6.82" | 8.94" |
| Eccentricity | 0.57 | 0.73 | 0.74 | 0.91 |
| Median | 0.0161 | 0.0190 | — | 0.0315 |
| SNR | 0.92 | 1.72 | — | 2.50 |

**Per-night averages:**

| Night | Frames | FWHM | Ecc | SNR | Notes |
|-------|--------|------|-----|-----|-------|
| 2024-08-13 | 32 | 5.48 | 0.71 | 2.12 | Best seeing |
| 2024-08-26 | 51 | 6.34 | 0.81 | 1.76 | Good, high eccentricity |
| 2024-09-28 | 13 | 6.93 | 0.74 | 1.95 | Decent |
| 2024-08-28 | 61 | 7.39 | 0.65 | 1.81 | Average FWHM, best eccentricity |
| 2024-08-29 | 50 | 7.71 | 0.77 | 1.43 | Below average |
| 2024-08-27 | 24 | 7.82 | 0.66 | 1.45 | Worst seeing |

**Observations:**
- Eccentricity is high across the board (avg 0.73, min 0.57) — systematic tilt or flexure, not random tracking. BlurXTerminator should help.
- Two dawn twilight frames at ~05:23 (Median 0.0315 and 0.0276) should be rejected.

**Applied approval expression (quality-over-quantity):**
```
FWHM < 8.5 && Eccentricity < 0.85 && Median < 0.025
```
Result: **197 frames approved** (~16.4h) — 50 rejected (worst seeing, high eccentricity, twilight).
Output: `~/Desktop/NGC7000_Reprocessing/SFS/` (197 xisf with `_a` postfix).

**Weighting expression** (keyword: SSWEIGHT, postfix `_a`):
```
(1/(FWHM*FWHM)) * SNR * (1 - Eccentricity)
```
Heavily favors the Aug 13 night (best FWHM) while downweighting poor seeing nights.

#### Step 2 — WBPP (Weighted Batch Pre-Processing) (completed)

**Input:**
- Lights: `~/Desktop/NGC7000_Reprocessing/SFS/` (197 approved xisf)
- Bias tab: bias master (1ms) + dark flat master (60ms)
- Darks tab: dark master (300s, g100, -10°C)
- Flats tab: 50 raw L-Pro flats (60ms)

**WBPP Settings Applied:**
- Post-Calibration: Drizzle **2x**, Drop shrink 0.90, Fast mode off
- Lights: Subframe Weighting (PSF Signal Weight), Image Registration (Distortion Correction, 4000 spline points), Local Normalization enabled, Image Integration (Winsorized Sigma Clipping, σ high 1.9, Large-scale rejection High layers 2 growth 2)
- Astrometric Solution: Force values unchecked, 250mm, 3.76 µm
- Cosmetic Correction: Automatic, High sigma 10
- CFA: VNG debayer

**Results:**
- Master flat generated from 50 flats (calibrated with bias only — dark flat not matched)
- 197 lights calibrated (dark + flat)
- Best reference frame: `20240813-025221` (Aug 13 — best seeing night)
- Fast integration: 195/197 integrated (2 rejected)
- Drizzle 2x integration: completed
- Autocrop: applied to both fast and drizzle masters
- Astrometric solution: completed

**Output files in `~/Desktop/NGC7000_Reprocessing/Results/master/`:**
- `masterLight_BIN-1_6248x4176_EXPOSURE-300.00s_FILTER-NoFilter_RGB_drizzle_2x_autocrop.xisf` — **main working file for Phase 2**
- `masterLight_..._RGB_fastIntegration_autocrop.xisf` — quick preview
- `masterFlat_BIN-1_6248x4176_FILTER-NoFilter_CFA.xisf` — generated flat master
- Logs: `Results/logs/`

---

### Phase 2: Linear Processing

#### Step 3 — AutoStretch (visualization only)

1. **ScreenTransferFunction** — linked mode (chain link icon), click nuclear icon
2. Unlink channels, AutoStretch again — check for color imbalances
3. Do NOT apply STF to the image — data must remain linear

#### Step 4 — ImageSolver (plate solve)

1. Set approximate center: RA 20h 59m 17s, Dec +44° 31' 44"
2. Date: **2024-08-13** (best reference frame date)
3. Focal length: 250mm
4. Pixel size: **1.88 µm** (Drizzle 2x)
5. Catalog: **Gaia DR3**
6. **Do NOT check "Force values"**
7. Advanced:
   - Sensitivity: **0.30**
   - Try with apparent coordinates on failure: checked
   - Try with exhaustive star matching on failure: checked
8. Enable Distortion Correction

#### Step 5a — SPFC (completed)

**SpectrophotometricFluxCalibration** — flux-calibrate before gradient removal.

| Setting | Value |
|---------|-------|
| QE Curve | Sony IMX411/455/461/533/571 |
| Red filter | Optolong L-Pro R |
| Green filter | Optolong L-Pro G |
| Blue filter | Optolong L-Pro B |
| Catalog | Gaia DR3/SP |
| PSF growth | 1.75 |

**Results:** R:9696 G:9835 B:9880 sources. Scale factors R:0.1898 G:0.2744 B:0.2504. Dispersions all <1.7%.

#### Step 5b — MGC (Gradient Removal)

MARS has broadband R/G/B coverage for the NGC 7000 field. Using SPFC + MGC (not GraXpert). See [[MGC-Reference]] for full tuning guide.

**MGC Settings for NGC 7000:**

| Setting | Value |
|---------|-------|
| MARS databases | MARS-DR1-1.1.1.xmars + MARS-DR1-u01-1.0.1.xmars |
| Gray filter | L |
| Red filter | R |
| Green filter | G |
| Blue filter | B |

**Gradient Model:**

| Setting              | Value    | Notes                                                   |
| -------------------- | -------- | ------------------------------------------------------- |
| Gradient scale       | **2048** | Gentle gradients — use highest scale that corrects well |
| Structure separation | **1**    | Default                                                 |
| Model smoothness     | 1.00     | Default                                                 |

**Scale Factors** (tuned per channel at scale 256, then verified at 2048):

| Channel | Final value | Notes |
|---------|-------------|-------|
| R | **1.10** | Ha emission — 1.0 left bright traces, 1.2 inverted. 1.1 is the sweet spot |
| G | **1.20** | OIII signal — 0.8 left green traces, 1.2 cleared them |
| B | **1.20** | OIII signal — 0.8 left blue traces, 1.2 cleared them |

**Tuning log:**
1. Scale 256, R:1.2 G:0.8 B:0.8 → nebula inverted (dark blob) in R
2. Scale 256, R:1.0 G:0.8 B:0.8 → nebula bright in R (too low)
3. Scale 256, R:1.1 G:1.0 B:1.0 → R good, green patch remaining
4. Scale 256, R:1.1 G:1.2 B:1.0 → R+G good, blue trace remaining
5. Scale 256, R:1.1 G:1.2 B:1.2 → faint residual traces only
6. Scale 2048, R:1.1 G:1.2 B:1.2 → smooth gradient model, minimal traces. Applied.

**Post-MGC:** Run **BackgroundNeutralization** if residual color cast remains

#### Step 6 — BlurXTerminator (Star Correction)

1. Model: `BlurXTerminator.4.mlpackage`
2. **Correct Only** mode (no sharpening yet)

#### Step 7 — BlurXTerminator (Sharpening)

**PSFImage evaluation results:**

| Parameter | Value |
|-----------|-------|
| Stars | 50 (from 835) |
| FWHMx | 2.37 |
| FWHMy | 2.27 |
| PSF Diameter | **(2.37 + 2.27) / 2 = 2.32** |
| Eccentricity (r) | 0.955 |
| Beta (Moffat) | 2.13 |

**BlurXTerminator settings:**

| Setting | Value |
|---------|-------|
| Sharpen Stars | 0.20 |
| Adjust Star Halos | -0.10 |
| PSF Diameter | **2.32** |
| Sharpen Nonstellar | 0.90 |

#### Step 8 — FindBackground

1. Run **FindBackground** script
2. Exclude dark nebulosity regions if necessary
3. Note the background reference for SPCC

#### Step 9 — SPCC (Color Calibration) (completed)

**Settings applied:**

| Setting | Value |
|---------|-------|
| Filters | Optolong L-Pro R, G, B |
| QE Curve | Sony IMX411/455/461/533/571 |
| White reference | G2V Star |
| Catalog | Gaia DR3/SP |
| Clustered sources | enabled |
| PSF growth | 1.25 |
| Target source count | 8000 |
| Neutralize background | enabled |

**Results:**

| Parameter | Value |
|-----------|-------|
| Total sources | 2,458 |
| White balance factors | R: 1.0000, G: 0.7184, B: 0.8051 |
| R/G fit | y = +1.487x - 0.064, σ = 0.144 |
| B/G fit | y = +1.265x - 0.018, σ = 0.122 |

#### Step 10 — Verify Color Calibration

1. **ScreenTransferFunction** — link channels, AutoStretch
2. Image should show natural, balanced colors
3. If colors are off, revisit SPCC settings

#### Step 11 — StarXTerminator (Star Removal)

1. Model: `StarXTerminator.lite.nonoise.11.mlpackage`
2. Generate Star image: **selected**
3. Overlap: 0.20
4. **Save the star image** — you will need it in Phase 4

#### Step 12 — NoiseXTerminator (Linear, on starless)

1. Model: `NoiseXTerminator.3.mlpackage` (AI v3)
2. Denoise: 0.9
3. Iterations: **2**
4. Test on a preview first

---

### Phase 3: Non-Linear Processing

#### Step 13 — Stretch (on starless) (completed)

**Statistical Astro Stretching** v2.3 settings:

| Setting | Value |
|---------|-------|
| Target Median | 0.25 |
| Blackpoint Sigma | 5.00 |
| HDR Compress | unchecked |
| Luma Only | unchecked |
| Luma Mode | rec709 |
| Luma Blend | 0.60 |
| Linked Stretch | checked |
| **Curves Boost** | **0.20** |

#### Step 14 — BackgroundNeutralization + SCNR

**BN result:** BackgroundNeutralization had no visible effect — image remained greenish despite selecting a background preview. The green cast comes from SPCC + broadband L-Pro on an emission nebula field (background and faint areas go green where there's no strong narrowband signal).

**Fix: SCNR** (SubtractiveChromaticNoiseReduction) to remove green cast:
1. Open **SCNR** (Process → NoiseReduction → SCNR)
2. Settings:
   - Channel: **Green**
   - Amount: **0.5** (start conservative, increase to 0.7–0.8 if needed)
   - Protection method: **Average Neutral**
3. Test on a preview first
4. Apply to the starless image
5. Fine-tune remaining color balance with CurvesTransformation in Step 18

#### Step 15 — NoiseXTerminator (Final, on starless)

1. Denoise: 0.9
2. Iterations: **1** (lighter pass on non-linear data)
3. Test on a preview first

---

### Phase 4: Star Processing & Reintegration

#### Step 16 — ArcsinhStretch (on star image) (completed)

| Setting | Value |
|---------|-------|
| Stretch factor | **1.63** |
| Black point | 0.000000 |
| Protect highlights | enabled |

#### Step 17 — Star Reintegration

1. **PixelMath:**
   ```
   ~(~starless * ~stars)
   ```
   Where `starless` = stretched starless image, `stars` = stretched star image

#### Step 18 — Final Adjustments

See [[CurvesTransformation-Reference]] for full guide.

**CurvesTransformation for NGC 7000** (apply each group separately, use Real-Time Preview):

**18a. Luminance (L):**
- S-curve: drag upper 1/3 **up** to brighten nebula
- Drag lower 1/4 **down** to deepen the Gulf of Mexico dark lanes and space
- Bring up midtones slightly to reveal faint Ha filaments
- Don't blow out the brightest nebula regions

**18b. Saturation (S):**
- Shallow S-curve: drag upper 1/3 **up** slightly
- Keep subtle — L-Pro Ha data is already reddish

**18c. Color channels:**
- **G:** Pull down lower 1/3 to remove green cast. Optional slight upper boost for yellow warmth in bright nebula areas
- **R:** Boost middle to enrich Ha reds. Pull down lower 1/4 to neutralize red in space
- **B:** Pull down lower 1/4 to neutralize space, keep background black

**18d. SCNR** (if green cast persists):
- Channel: Green, Amount: 0.5, Protection: Average Neutral

**18e. LocalHistogramEqualization** (completed — see [[LHE-Reference]]):

**Pass 1 — Large structures:**

| Setting | Value |
|---------|-------|
| Kernel Radius | **140** |
| Contrast Limit | **1.5** |
| Amount | **0.40** |

**Pass 2 — Small structures:**

| Setting | Value |
|---------|-------|
| Kernel Radius | **60** |
| Contrast Limit | **1.5** |
| Amount | **0.30** |

**18f. DarkStructureEnhance** (completed):

| Setting | Value |
|---------|-------|
| Layers to remove | 8 |
| Scaling function | 3×3 B3 Spline |
| Amount | 0.40 |
| Iterations | 1 |

**18g. ICCProfileTransformation** (completed) — converted to sRGB for export

#### Step 19 — Save & Export (completed)

- Final result: `~/Desktop/NGC7000_Reprocessing/Results/master/NGC7000-2026-Results10.jpg`
- Copy to SSD: `/Volumes/T7/Astrophotography/Objects/Nebuleuses/ASI2600MC-REDCAT51/NGC_7000_North_America_Nebula/2024/MultiNights/Results10/`

---

## Notes

- This is reprocessing pass #10 (previous best: Results8)
- Compared to 2025-03-09 processing: using current PI 1.9.3 tools, AI v3 NoiseXTerminator, corrected filter identification (L-Pro, not Ultimate)
- NGC 7000 is a strong Ha emitter — consider re-shooting with [[Antlia-FQuad]] in summer 2026 for narrowband data
- DarkStructureEnhance is particularly useful for the "Gulf of Mexico" dark lane region
- MARS has broadband R/G/B coverage for NGC 7000 — MGC worked well (scale factors R:1.1, G:1.2, B:1.2)
- Green cast from SPCC + broadband L-Pro on emission field — fixed with CurvesTransformation green channel pull-down
- ArcsinhStretch at 1.63 was too mild for Cygnus star field — 9.50 produced natural star density
