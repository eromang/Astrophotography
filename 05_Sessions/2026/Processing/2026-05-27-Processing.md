---
title: "2026-05-27 Processing Session — Mel 111 WBPP A/B tests"
type: processing-session
date: 2026-05-27
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

| # | Pixel size at launch | Distortion Correction | Allow Clustered (Image Reg) | Cosmetic Correction | Master Dark mode | Optimize Master Dark | Astrometric result | Elapsed |
|---|---|---|---|---|---|---|---|---|
| 1 | **3.76** (initial) | ON | OFF | Auto | 25 raws (WBPP stacks) | OFF | **4 solved ✓** | 21:30 |
| 2a | 1.88 (auto-reset, not noticed) | ON | OFF | Template `WBPP_CC_Dark` | Pre-built master | OFF | 1 solved, 3 failed | 23:53 |
| 2b | **3.76** (manually reset) | ON | OFF | Template `WBPP_CC_Dark` | Pre-built master | OFF | **4 solved ✓** | 21:10 |
| 3 | **3.76** (manually reset) | ON | **ON** | Template `WBPP_CC_Dark` | Pre-built master | OFF | **4 solved ✓** | 21:38 |

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

## Phase 2 — Linear Processing (TBD)

Pending: run standalone ImageSolver on the drizzle 2x autocrop master with **pixel size 1.88 µm** (correct for drizzle output, different from WBPP's pre-drizzle 3.76 µm), then continue with [[../../04_Processing/Pixinsight/RGB-Workflow#Phase 2 Linear Processing]].

---

## Notes

- All 5 WBPP test runs produced identical `1 solved, 3 failed` astrometric output. The "failed" entries are autocrop variants per [[../../04_Processing/Pixinsight/RGB-Workflow#2.2 ImageSolver]]; not a real bug.
- Phase 2 standalone ImageSolver is the path to embed the astrometric solution into the drizzle 2x autocrop master.
- T7 SSD must be connected for the full-calibration final run (bias + flat + dark flat) — current preview pipeline is lights+darks only, so masters retain vignetting and dust shadow artefacts that flats would correct.
- See [[2026-05-25-Capture]] for capture-side details (autorun log, AutoFocus events, end-of-session shutdown timing).
