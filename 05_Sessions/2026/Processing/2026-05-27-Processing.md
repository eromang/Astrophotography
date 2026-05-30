---
title: "2026-05-27 Processing Session — Mel 111 WBPP A/B tests → finished master"
type: processing-session
date: 2026-05-27
date_completed: 2026-05-30
software: "PixInsight 1.9.4 (arm64)"
targets_processed:
  - "[[Mel111-Coma]]"
tags:
  - session/processing
---

# 2026-05-27 — Processing Session

Processing the [[2026-05-25-Capture|2026-05-25 Mel 111 dataset]] (52 × 120 s L-Pro, first light). T7 SSD not connected — running preview pipeline with lights + darks only (no bias, no flat, no dark flat). Doing a series of WBPP A/B tests to characterize which settings affect the astrometric solve outcome.

## Objects Processed

### Mel 111 — Coma Star Cluster

- **Lights:** 52 (no SubFrameSelector rejection applied)
- **Exposure:** 120 s × 52 = 6240 s (104 min)
- **Filter:** [[Optolong-LPro]]
- **Gain:** 100
- **Temperature:** −9.6 °C (drift −9.5 to −9.8)

#### SubFrameSelector Stats (across 52 frames)

| Metric | Min | Median | Max |
|--------|---|---|---|
| FWHM | 6.38 | 7.07 | 7.70 |
| Eccentricity | 0.57 | 0.63 | 0.70 |
| Median | 0.0195 | 0.0213 | 0.0217 |
| Noise | 0.0024 | 0.0031 | 0.0033 |
| SNR | 1.20 | 1.30 | 1.31 |
| Stars | 848 | 1046 | 1207 |
| PSF Signal Weight | 0.0212 | 0.0257 | 0.0303 |

All 52 frames passed approval; no rejections. Frame 34 has a visible satellite trail but is middle-of-pack on noise (rank 19/52) — kept for WBPP rejection layer to handle.

---

## Calibration Frames Used

| Type | Exposure | Count | Master |
|---|---|---|---|
| Dark | 120 s | 25 raws | Built on-the-fly by WBPP from `/Users/ericromang/Desktop/Astro/Dark/` |
| Flat | — | — | Not available (T7 SSD unmounted) |
| Dark Flat | — | — | Not available (T7 SSD unmounted) |
| Bias | — | — | Not available (T7 SSD unmounted) |

---

## WBPP A/B Test Matrix

Goal: determine which WBPP settings affect the post-pipeline astrometric solve.

**Actual finding (after extensive debugging):** the ONLY WBPP variable that affects the astrometric outcome is **the Image Solver default Pixel size**, which **WBPP silently auto-changes from 3.76 → 1.88 µm after each completed run**. All "1 solved, 3 failed" results below were caused by the auto-reset; once pixel size was manually re-set to 3.76 before each launch, all runs achieved `4 solved ✓`.

| # | Pixel size at launch | Distortion Correction | Allow Clustered (Image Reg) | Cosmetic Correction | Master Dark mode | Optimize Master Dark | Full calibration | Drizzle Fast Mode | Astrometric result | Elapsed |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **3.76** (initial) | ON | OFF | Auto | 25 raws (WBPP stacks) | OFF | lights+darks only | OFF | **4 solved ✓** | 21:30 |
| 2a | 1.88 (auto-reset, not noticed) | ON | OFF | Template `WBPP_CC_Dark` | Pre-built master | OFF | lights+darks only | OFF | 1 solved, 3 failed | 23:53 |
| 2b | **3.76** (manually reset) | ON | OFF | Template `WBPP_CC_Dark` | Pre-built master | OFF | lights+darks only | OFF | **4 solved ✓** | 21:10 |
| 3 | **3.76** (manually reset) | ON | **ON** | Template `WBPP_CC_Dark` | Pre-built master | OFF | lights+darks only | OFF | **4 solved ✓** | 21:38 |
| **4 (PRODUCTION)** | **3.76** (manually reset) | ON | ON | Template `WBPP_CC_Dark` | Pre-built master | **ON** (now bias loaded) | **bias + flat + dark-flat + dark** | OFF | **4 solved ✓** | 21:31 |

**Conclusion**: The WBPP toggles tested (Distortion Correction, Allow Clustered Sources in Image Registration, CC template vs Automatic, 25 raws vs pre-built master dark) do NOT affect the astrometric solve outcome when pixel size is correct (3.76 µm).

**The pixel-size auto-reset is a silent footgun** — WBPP updates the Image Solver default to 1.88 µm after each run (presumably matching the drizzle-scaled output for the next solve). The per-frame astrometric solver in the next WBPP run then fails because pre-drizzle inputs are at native 3.76 µm. **Pre-launch checklist:** verify Image Solver default Pixel size = 3.76 BEFORE clicking Run.

See memory [[feedback-wbpp-pixel-size-autoresets]] for the full incident write-up.

### Cumulative validated settings for this rig

Based on Tests 1-3 above:

- **Image Solver default → Pixel size**: **3.76 µm** (re-verify before EVERY run)
- **Image Registration → Distortion Correction**: ON (default rec; no negative effect observed)
- **Image Registration → Allow Clustered Sources**: ON (helpful for dense clusters like Mel 111)
- **Local Normalization → Allow Clustered Sources**: ON (default)
- **Cosmetic Correction**: Template `WBPP_CC_Dark` (Sigma 8, Qty 200, Master-Dark-based) — preserves dim cluster stars better than Automatic
- **Darks tab**: pre-built master OR raw stack (equivalent results)
- **Optimize Master Dark**: OFF until bias master is loaded
- All other settings per Test 1 documentation below.

---

## Test 1 — Detailed Settings

Baseline run. Settings captured 2026-05-27 09:05 CEST.

### Darks tab

| Section | Setting | Value |
|---|---|---|
| File List | Binning 1, 120.00 s | **25 frames** — `Dark_120.0s_Bin1_2600MC_gain100_20260419-{121138..130004}_-9.{6,7,8}C_LPro_{0001..0025}.fit` from `/Users/ericromang/Desktop/Astro/Dark/` |
| Top settings | Optimization threshold | 3.0000 |
| | Exposure tolerance | 10 s |
| Image Integration | Combination | Average |
| | Rejection algorithm | Auto |
| | Percentile low / high | 0.20 / 0.10 |
| | Sigma low / high | 4.00 / 3.00 |
| | Linear fit low / high | 5.00 / 3.50 |
| | ESD outliers / significance | 0.30 / 0.05 |
| | RCR limit | 0.10 |

### Lights tab

| Section | Setting | Value |
|---|---|---|
| File List | Binning 1, NoFilter, 120.00 s | **52 frames** — `Light_13 Comae Berenices_120.0s_Bin1_2600MC_gain100_20260525-23{4139..5952}_…fit` ↦ `20260526-01{3437..}_…fit` |
| Top settings | Calibration exposure tolerance | 2 s |
| Linear Defects Correction | Enable | **Unchecked** |
| Subframe Weighting | Enable | ✓ Checked |
| | Weights | PSF Signal Weight |
| Frame Selection | Enable | Unchecked (Interactive checked but irrelevant) |
| Image Registration | Enable | ✓ Checked |
| | Reuse last reference frames | Unchecked |
| Local Normalization | Enable | ✓ Checked |
| | Reuse last reference frames | Unchecked |
| Image Integration | Enable | ✓ Checked |
| | Autocrop | ✓ Checked |
| | Automatic integration mode | ✓ Checked |
| Astrometric Solution | Enable | ✓ Checked |
| | Interactive in case of failure | ✓ Checked |

### Image Registration sub-settings

| Setting | Value |
|---|---|
| Pixel interpolation | Auto |
| Clamping threshold | 0.30 |
| Maximum stars | \<Auto\> |
| **Distortion correction** | **✓ Checked** |
| Maximum spline points | 4000 |
| Rigid transformations | Unchecked |
| Detection scales | 5 |
| Minimum structure size | \<Auto\> |
| Hot pixel removal | 1 |
| Noise reduction | \<Disabled\> |
| Sensitivity | 0.50 |
| Peak response | 0.50 |
| Bright threshold | 3.00 |
| Maximum distortion | 0.60 |
| Allow clustered sources | Unchecked |
| Use triangle similarity | Unchecked |

### Local Normalization sub-settings

| Setting | Value |
|---|---|
| Generate Images | ✓ Checked |
| Reference frame generation | Integration of best frames |
| Maximum integrated frames | 20 |
| Evaluation criteria | PSF Signal Weight |
| Grid size | 4.00 |
| Scale evaluation method | PSF flux evaluation |
| PSF type | Auto |
| Growth factor | 1.00 |
| Maximum stars | 24576 |
| Minimum detection SNR | 40 |
| Allow clustered sources | ✓ **Checked** (different from Image Registration's same-name parameter) |
| Low clipping level | 4.50e-05 |
| High clipping level | 0.85 |

### Image Integration sub-settings

| Setting | Value |
|---|---|
| Combination | Average |
| Minimum weight | 0.050000 |
| Rejection algorithm | **Winsorized Sigma Clipping** |
| Percentile low / high | 0.20 / 0.10 (greyed, not used by WSC) |
| Sigma low | 4.00 |
| Sigma high | **1.90** |
| Linear fit low / high | 5.00 / 3.50 (greyed) |
| ESD outliers / significance | 0.30 / 0.05 (greyed) |
| RCR limit | 0.10 (greyed) |
| Large-scale pixel rejection High | ✓ Checked |
| Large-scale pixel rejection Low | Unchecked |
| Large-scale layers | 2 |
| Large-scale growth | 2 |

### Astrometric Solution (Image Solver default parameters)

| Setting | Value |
|---|---|
| Right Ascension | 12 h 25 m 46.000 s |
| Declination | +25° 57' 23.76" |
| Date and time | 2026 Y / 5 M / 25 d / 23 h / 1 m / 46 s |
| Focal distance | 250 mm |
| **Pixel size** | **3.76 µm** |
| Force values | Unchecked |

### Calibration tab — LIGHT row settings

| Section | Setting | Value |
|---|---|---|
| Calibration Settings | Dark | ✓ Auto |
| | Flat | Unchecked (no master available) |
| | Optimize Master Dark | **Unchecked** |
| Output Pedestal | Mode | Automatic |
| | Limit | 0.00010 |
| Cosmetic Correction | Automatic | ✓ Checked |
| | High sigma | 10 |
| | Template | \<none\> |
| CFA Settings | CFA Images | ✓ Checked |
| | Mosaic pattern | Auto |
| | DeBayer method | VNG |

Calibration tab summary row:
- BIAS: empty
- DARK: 1 group, 25 frames, 6248×4176, 1×1, 120.00 s
- FLAT: empty
- LIGHT: 1 group, 52 frames, 6248×4176, 1×1, 120.00 s, NoFilter

### Post-Calibration tab

| Section | Setting | Value |
|---|---|---|
| LIGHT row | 52 frames, 1×1, 120 s, NoFilter, RGB, integration time 1 h 44 m 0 s | Drizzle 2x, 0.90, Square |
| Channels | Debayer | Combined RGB |
| | Active channels | R, G, B |
| | Recombine RGB | Unchecked |
| Drizzle | Enable | ✓ Checked |
| | Fast mode | Unchecked |
| | Scale | 2 |
| | Drop shrink | 0.90 |
| | Function | Square |
| | Grid size | 16 |
| Fast Integration | Enable | Unchecked |
| | Save images | Unchecked |
| | Weighting | None |

---

## Phase 2 — Linear Processing

**Production master:** `Results/master/masterLight_BIN-1_6248x4176_EXPOSURE-120.00s_FILTER-NoFilter_RGB_drizzle_2x_autocrop.xisf` (Test 4 output)

Per the Test 4 WBPP log, **all 4 masters got astrometric solutions embedded** (including the drizzle 2x autocrop):
```
Astrometric solution completed: ...RGB.xisf                      ✓
Astrometric solution completed: ...RGB_autocrop.xisf             ✓
Astrometric solution completed: ...RGB_drizzle_2x.xisf           ✓
Astrometric solution completed: ...RGB_drizzle_2x_autocrop.xisf  ✓
```

Per [[../../04_Processing/Pixinsight/RGB-Workflow#2.2 ImageSolver]]: *"ImageSolver is needed if WBPP didn't solve the image or if the autocrop lost the solution."* Neither applies — **skip Phase 2 step 2.2** and proceed directly to:
- 2.1 AutoStretch (visual sanity)
- 2.3 Gradient Removal (MGC with MARS DR1 now that T7 is plugged in; GraXpert fallback if MARS lacks broadband coverage for this field)
- 2.4 BlurXTerminator Correct Only
- 2.5 BlurXTerminator full sharpen
- 2.6 Background Reference
- 2.7 SPCC
- 2.8-2.10 per workflow

**Calibration masters used** (archive status MD5-verified 2026-05-30):
- Bias: `masterBias_…BIAS-1.0ms.xisf` — **MD5-identical** to T7 `Templates/Masters/Bias/`
- Dark: `Results/master/masterDark_…120.00s.xisf` — **rebuilt in-session** from 25 raws; differs from the Apr-19 T7 library master, so this exact build was archived to T7 `Objects/…/Mel111_Coma/` next to the lights (raws also on T7 `Templates/Dark/DARK11-BIN1-120s-10/`, MD5-identical)
- Flat: `masterFlat_…FILTER-LPro_CFA_FLAT-60ms.xisf` — **MD5-identical** to T7 `Templates/Masters/Flat/`
- Dark Flat: `masterDark_…0.06s.xisf` (60 ms) — **MD5-identical** to T7 `Templates/Masters/Dark/FQuad/`; matched via WBPP's Bias tab auto-match

**Reference frame for registration**: frame 0011 (`...0011_c_cc_d.xisf`) — auto-picked by WBPP as the top PSF Signal Weight frame, consistent with the SubFrameSelector analysis at the top of this note (frame 11 had PSW 0.0303, the best of 52).

**Local Normalization reference**: built from 17 of 52 frames (best by PSF Signal Weight, capped at 20).

---

## Phase 2/3 — Actual Processing (completed 2026-05-30)

Reconstructed from the SPFC/SPCC reports (`log/SPFC.pdf`, `log/SPCC.pdf`) and process-icon set; final export `Results/Mel-111.jpg` + `Results/master/Image43.fit` written 2026-05-30 15:54.

### Realized step order

1. **WBPP Test 4** → production master `…_drizzle_2x_autocrop.xisf` (full calibration: bias + flat + dark-flat + dark; astrometric solution embedded).
2. **SPFC** (Spectrophotometric Flux Calibration) on `MasterLight_NoFilter` — 2026-05-27 12:59 UTC.
3. **GraXpert + ABE** gradient removal → `MasterLight_NoFilter_GraXpert_ABE`. **The planned MGC/MARS path was dropped** — MARS DR1 lacks usable broadband coverage for this field, so the GraXpert fallback (noted in the Phase 2 plan) became the actual path.
4. **SPCC** (Spectrophotometric Colour Calibration) — 2026-05-27 14:10 UTC.
5. **Star handling via [[Star-Console-Reference|Star Console]]** (Hidden Light Photography script, `Script → HLP → Star Console`). The script: extracts luminance from the OSC image → measures median FWHM/eccentricity → rounds FWHM and auto-loads it into **BlurXTerminator** PSF diameter and runs full BXT → then **Star Removal (StarXTerminator)**, unscreening the stars. Output is a **starless + stars pair** processed separately. Full settings: [[Star-Console-Reference]].
6. Stretch (Bill's Stretch from the icon set), recombine stars, final cosmetic/colour work → JPEG export.

### SPFC result (`log/SPFC.pdf`)

| Field | Value |
|---|---|
| Catalog | Gaia DR3/SP |
| Filters | Optolong L-Pro R/G/B |
| QE curve | Sony IMX571 (IMX411/455/461/533/571 family) |
| Total sources | R 278 / G 276 / B 279 |
| Scale factors | R 8.85e-02 · G 1.380e-01 · B 1.261e-01 |
| Dispersions | R 1.87e-03 · G 2.64e-03 · B 2.56e-03 (tight) |

### SPCC result (`log/SPCC.pdf`)

| Field | Value |
|---|---|
| Catalog | Gaia DR3/SP |
| White reference | G2V Star |
| Total sources | 763 |
| R/G linear fit | y = 1.2986·x + 0.0382, σ = 0.300 |
| B/G linear fit | y = 1.2871·x − 0.0246, σ = 0.457 |
| White balance factors | 1.0000 / 0.7218 / 0.8003 |

Clean colour solution; B/G a touch more scattered (σ 0.46) as expected for broadband from Bortle 4 under a 75 % moon.

### Filter — confirmed L-Pro (resolved 2026-05-30)

WBPP labelled the stack `NoFilter` and that string propagated into the master filenames. Root cause confirmed by inspecting a raw light: the FITS **`FILTER` keyword is blank/absent**, so WBPP defaulted to `NoFilter`. The capture was genuinely through the **Optolong L-Pro** — the ASIAIR filenames embed `_LPro_` (`Light_13 Comae Berenices_…_LPro_0001.fit`), the flat master is L-Pro, and SPCC/SPFC both modelled Optolong L-Pro R/G/B. No real mismatch; the calibration is self-consistent. The `NoFilter` master filenames are cosmetic only.

### Result assessment

Final: `Results/Mel-111.jpg` (12088×7814) — copied to vault as [[Mel111-Coma#Processed Result|`Mel111-ASI2600.jpg`]].

- **Stars:** round and tight across the full frame, corners included — RedCat 51 flat field + BXT, no coma/elongation.
- **Colour:** strong blue-white (B−V cluster members) vs orange field-star separation; neutral background overall.
- **Background galaxies:** preserved with structure — face-on spiral (right-of-centre), edge-on/lenticular pairs in the SE corner, several fainter smudges. Strong for 1.7 h broadband.
- **Open items:** (1) γ Com and the brightest members show a **bloated soft blue halo**. Stars were already separated via Star Console / StarXTerminator, so this is in the **stars-image** processing — tackle it on the stars layer next time (gentler star stretch, halo/morphological reduction, or SCNR-green-then-curves before re-screening); (2) faint warm chroma mottle + a few colour speckles in the corners (limited integration, no dithered chroma cleanup beyond CC) — more integration or a light chroma-denoise would clear it; (3) no IFN/dust context at 1.7 h (expected — needs 5 h+).

---

## Notes

- All 5 WBPP test runs produced identical `1 solved, 3 failed` astrometric output. The "failed" entries are autocrop variants per [[../../04_Processing/Pixinsight/RGB-Workflow#2.2 ImageSolver]]; not a real bug.
- Phase 2 standalone ImageSolver is the path to embed the astrometric solution into the drizzle 2x autocrop master.
- T7 SSD must be connected for the full-calibration final run (bias + flat + dark flat) — current preview pipeline is lights+darks only, so masters retain vignetting and dust shadow artefacts that flats would correct.
- See [[2026-05-25-Capture]] for capture-side details (autorun log, AutoFocus events, end-of-session shutdown timing).
