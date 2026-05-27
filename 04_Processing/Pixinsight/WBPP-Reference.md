---
title: "WBPP Settings Reference"
type: processing-workflow
software: "PixInsight"
tags:
  - processing/pixinsight
---

# WBPP (Weighted Batch Pre-Processing) — Settings Reference

Complete reference for all WBPP settings. Based on PixInsight 1.9.2+ WBPP script.

> See [[RGB-Workflow]] and [[QuadBand-OSC-Workflow]] for target-specific configurations.

---

## Tabs

WBPP has 7 main tabs: **Bias** | **Darks** | **Flats** | **Lights** | **Calibration** | **Post-Calibration** | **Pipeline**

---

## Lights Tab

The Lights tab is the most complex. It contains the file list (left) and settings sections (right).

### File List (left panel)

- Groups frames by: Binning → Exposure → Filter/Keyword
- Shows frame count and file paths
- Toolbar: Clear | Remove Selected | Hide Astrometry | Invert Selection

### Calibration Exposure Tolerance

| Setting | Default | Description |
|---------|---------|-------------|
| Calibration exposure tolerance | **2** | Maximum difference (in seconds) between light and dark exposure for matching. Increase if darks don't match exactly. |

### Linear Defects Correction

Corrects hot/cold columns and rows. Usually not needed when using dark frames.

| Setting | Default | Description |
|---------|---------|-------------|
| Enable | **Unchecked** | Enable/disable linear defect correction |
| Rejection limit | — | Threshold for detecting defective columns/rows |
| Correction type | — | Type of correction to apply |

### Subframe Weighting

Controls how frames are weighted during integration.

| Setting | Default | Recommended | Description |
|---------|---------|-------------|-------------|
| Enable | **Checked** | Checked | Weight frames by quality metric |
| Weights | **PSF Signal Weight** | PSF Signal Weight | Metric used for weighting. Options: PSF Signal Weight, PSF SNR, FWHM, Eccentricity, SNR, Stars, Noise |

**PSF Signal Weight** is the best general-purpose option — it combines star shape quality and signal strength.

### Frame Selection

Allows interactive frame rejection within WBPP (alternative to running SubFrameSelector separately).

| Setting | Default | Description |
|---------|---------|-------------|
| Enable | **Unchecked** | Enable frame selection within WBPP |
| Interactive | — | Opens interactive dialog for manual frame inspection |

> When frames are pre-selected via SubFrameSelector (as in the current workflow), leave this **unchecked**.

### Image Registration

Aligns all frames to a reference frame.

| Setting | Default | Recommended | Description |
|---------|---------|-------------|-------------|
| Enable | **Checked** | Checked | Enable image registration |
| Reuse last reference frames | Unchecked | — | Reuse reference from a previous WBPP run |

**Sub-settings** (accessible via the Image Registration expandable panel — see [[#Image Registration Panel]]):

| Setting | Default | Recommended | Description |
|---------|---------|-------------|-------------|
| Distortion Correction | Unchecked | **Enabled** | Corrects field distortion (important for [[RedCat-51]] edge stars) |
| Max Spline Points | 2000 | **4000** | Higher = more accurate distortion model |

### Local Normalization

Equalizes background levels across frames before integration. Critical for multi-night stacks.

| Setting | Default | Recommended | Description |
|---------|---------|-------------|-------------|
| Enable | **Checked** | Checked (multi-night) | Enable local normalization |
| Interactive | Unchecked | — | Opens interactive dialog |
| Reuse last reference frames | Unchecked | — | Reuse reference from a previous run |

**Sub-settings** (accessible via the Local Normalization expandable panel — see [[#Local Normalization Panel]]):

| Setting | Default | Description |
|---------|---------|-------------|
| Generate Images | Checked | Generate local normalization data |
| Reference frame generation | Integration of best frames | How to build the normalization reference |
| Maximum integrated frames | 20 | Max frames used for reference |
| Evaluation criteria | PSF Signal Weight | Metric for selecting best frames |
| Grid size | 4.00 | Grid cell size for normalization |
| Scale evaluation method | PSF flux evaluation | Method for evaluating scale differences |
| PSF type | Auto | PSF model type |
| Growth factor | 1.00 | PSF growth factor |
| Maximum stars | 24576 | Max stars for evaluation |
| Minimum detection SNR | 40 | Minimum star SNR for detection |
| Allow clustered sources | Checked | Include clustered stars |
| Low clipping level | 4.50e-05 | Lower clipping bound |
| High clipping level | 0.85 | Upper clipping bound |

### Image Integration

Stacks all registered frames into the final master.

| Setting | Default | Recommended | Description |
|---------|---------|-------------|-------------|
| Enable | **Checked** | Checked | Enable image integration |
| Autocrop | **Checked** | Checked | Crop to the overlapping region |
| Automatic integration mode | **Checked** | Checked | Automatically determine integration parameters |

**Sub-settings** (accessible via the Image Integration expandable panel — see [[#Image Integration Panel]]):

| Setting | Default | Recommended | Description |
|---------|---------|-------------|-------------|
| Combination | Average | Average | Combination method |
| Minimum weight | 0.050000 | 0.050000 | Minimum relative weight for a frame to be included |
| **Rejection algorithm** | Auto | **Winsorized Sigma Clipping** | Pixel rejection method. Use WSC for satellite trail removal |
| Percentile low | 0.20 | 0.20 | Low percentile for percentile clipping |
| Percentile high | 0.10 | 0.10 | High percentile for percentile clipping |
| Sigma low | 4.00 | 4.00 | Low sigma for sigma/WSC clipping |
| **Sigma high** | 4.00 | **1.90** | High sigma — lower to reject satellite trails |
| Linear fit low | 5.00 | 5.00 | Low threshold for linear fit clipping |
| Linear fit high | 3.50 | 3.50 | High threshold for linear fit clipping |
| ESD outliers | 0.30 | 0.30 | Generalized ESD outlier fraction |
| ESD significance | 0.05 | 0.05 | Generalized ESD significance level |
| RCR limit | 0.10 | 0.10 | Robust Chauvenet rejection limit |
| **Large-scale pixel rejection High** | Unchecked | **Checked** | Enable large-scale rejection on high side (satellite trails) |
| Large-scale pixel rejection Low | Unchecked | Unchecked | Enable large-scale rejection on low side |
| **Large-scale layers** | 2 | **2** | Number of wavelet layers for large-scale rejection |
| **Large-scale growth** | 2 | **2** | Growth radius for large-scale rejection |

### Astrometric Solution

Plate-solves each frame for distortion correction and alignment.

| Setting | Default | Recommended | Description |
|---------|---------|-------------|-------------|
| Enable | **Checked** | Checked | Enable astrometric solving |
| Interactive in case of failure | Unchecked | — | Opens dialog if plate solve fails |
| Right Ascension | — | Target RA | Approximate target coordinates |
| Declination | — | Target Dec | Approximate target coordinates |
| Date and time | — | Approx session date | Approximate observation date |
| Focal distance | — | **250 mm** | Telescope focal length ([[RedCat-51]]) |
| Pixel size | — | **3.76 µm** | Native pixel size ([[ASI2600MCPro]]). Use native even with Drizzle — Drizzle is applied post-registration |
| **Force values** | Unchecked | **Unchecked** | **Never check** — fails on rotated images. ASIAIR writes RA/DEC to FITS headers, solver uses those hints. See [[#Lessons Learned]] |

---

## Bias Tab

Holds bias frames and dark flats for calibrating lights and flats.

### File List

Load both the bias master and dark flat master here. WBPP matches by exposure:
- Bias master (shortest exposure) → calibrates lights
- Dark flat master (matching flat exposure) → calibrates flats

### Settings

| Setting | Default | Description |
|---------|---------|-------------|
| **Overscan** | | |
| Apply | Unchecked | Apply overscan correction (for CCD cameras with overscan regions) |
| Overscan parameters | — | Configure overscan regions |
| **Image Integration** | | |
| Combination | Average | Combination method (only used when stacking raw bias frames) |
| Rejection algorithm | Auto | Pixel rejection method |
| Percentile low/high | 0.20 / 0.10 | Percentile clipping thresholds |
| Sigma low/high | 4.00 / 3.00 | Sigma clipping thresholds |
| Linear fit low/high | 5.00 / 3.50 | Linear fit clipping thresholds |
| ESD outliers | 0.30 | Generalized ESD outlier fraction |
| ESD significance | 0.05 | Generalized ESD significance level |
| RCR limit | 0.10 | Robust Chauvenet rejection limit |

> Image Integration settings are only relevant when loading raw bias frames. When loading pre-built masters, these are ignored.

---

## Darks Tab

Holds dark frames for calibrating lights.

### Settings

| Setting | Default | Description |
|---------|---------|-------------|
| Optimization threshold | **3.0000** | Threshold for dark frame optimization |
| Exposure tolerance | **10** | Maximum exposure difference (seconds) for matching darks to lights |
| **Image Integration** | | Same settings as Bias tab — only used when stacking raw darks |

> When loading a pre-built master dark, the Image Integration settings are ignored.

---

## Flats Tab

Holds flat frames for calibrating lights.

### Settings

| Setting | Default | Description |
|---------|---------|-------------|
| **Image Integration** | | |
| Combination | Average | Combination method |
| Rejection algorithm | Auto | Pixel rejection method |
| Sigma low/high | 4.00 / 3.00 | Sigma clipping thresholds |
| Large-scale pixel rejection | Unchecked | Not needed for flats |
| Large-scale layers | — | — |
| Large-scale growth | — | — |

---

## Calibration Tab

Overview of the entire calibration chain. Shows all frame groups and their relationships.

### Summary Table

Displays 4 rows: BIAS, DARK, FLAT, LIGHT with columns showing how each is calibrated.

### Per-row settings (click a row to see its settings)

#### When clicking DARK/FLAT row:

| Setting | Default | Description |
|---------|---------|-------------|
| **Calibration Settings** | | |
| Dark | Auto | Automatic dark matching |
| Optimize Master Dark | Unchecked | Optimize dark scaling |
| **CFA Settings** | | |
| CFA Images | Checked | Recognize CFA (color) data |
| Apply to all flat frames | — | Apply CFA setting to all flats |

#### When clicking LIGHT row:

| Setting | Default | Recommended | Description |
|---------|---------|-------------|-------------|
| **Calibration Settings** | | | |
| Dark | Auto | Auto | Automatic dark matching |
| Flat | Auto | Auto | Automatic flat matching |
| Optimize Master Dark | Unchecked | Unchecked | Dark frame scaling optimization |
| **Output Pedestal Settings** | | | |
| Mode | Automatic | Automatic | Prevents clipping of near-zero values |
| Value (DN) | — | — | Manual pedestal value |
| Limit | 0.00010 | 0.00010 | Pedestal limit |
| **Cosmetic Correction** | | | |
| Automatic | Checked | **Checked** | Use dark master for hot pixel detection |
| High sigma | 10 | 10 | Detection threshold |
| Template | — | — | Custom cosmetic correction template |
| **CFA Settings** | | | |
| CFA Images | Checked | Checked | Recognize CFA data |
| Mosaic pattern | Auto | Auto | Bayer pattern detection |
| DeBayer method | **VNG** | **VNG** | Debayering algorithm (Variable Number of Gradients) |

### Right-side links

- Overscan Settings
- Calibration Settings
- Output Pedestal Settings
- Cosmetic Correction
- CFA Settings
- Show Calibration Diagram

---

## Post-Calibration Tab

Settings applied after calibration but before registration.

### Summary Table

Shows: LIGHT frames, Binning, Exposures, Filter, Color Space, Integration Time, Fast Integration, Drizzle, Status.

### Channels Configuration

| Setting | Default | Recommended | Description |
|---------|---------|-------------|-------------|
| Debayer | Combined RGB | Combined RGB | How to handle debayered channels |
| Active channels | R, G, B | R, G, B | Which channels to process |
| Recombine RGB | — | — | Recombine channels after processing |

### Drizzle Configuration

| Setting | Default | Recommended | Description |
|---------|---------|-------------|-------------|
| **Enable** | Unchecked | **Checked** | Enable drizzle integration |
| **Fast mode** | Unchecked | **Unchecked** | Skip quality steps for speed — disable for final processing |
| **Scale** | 1 | **2** | Drizzle scale factor |
| **Drop shrink** | 0.90 | **0.90** | Drop shrink factor (smaller = sharper but noisier) |
| Function | Square | Square | Drop function shape |
| Grid size | 16 | 16 | Drizzle grid size |

### Drizzle Scale Reference

| Value | Output pixel scale | Effective pixel size | Notes |
|-------|-------------------|---------------------|-------|
| 1x | 3.10"/px | 3.76 µm | Native resolution |
| **2x** | **1.55"/px** | **1.88 µm** | **Recommended** — better than debayerization for OSC |
| 3x | 1.03"/px | 1.25 µm | Rarely needed |
| 4x | 0.78"/px | 0.94 µm | Overkill for most setups |

> **Drizzle 2x is strongly recommended** over standard debayerization for color sensors. Drizzle involves no data interpolation, while debayerization interpolates 3 out of 4 pixels per channel, introducing photometric errors.

### Fast Integration

| Setting | Default | Recommended | Description |
|---------|---------|-------------|-------------|
| Enable | Checked | Checked | Quick preview integration (non-drizzle) |
| Save images | Unchecked | Unchecked | Save fast integration result |
| Weighting | None | None | Weighting for fast integration |

---

## Pipeline Tab

Shows the full processing pipeline with estimated disk space and active steps.

### Pipeline Steps (typical for 197 lights + 50 flats)

| # | Operation | Description |
|---|-----------|-------------|
| 0 | Calibration (Flats) | Calibrate flat frames with bias/dark flat |
| 1 | Integration (Flats) | Stack flats into master flat |
| 2 | Calibration (Lights) | Calibrate lights with bias, dark, flat |
| 3 | Debayer | Debayer CFA light frames |
| 4 | Measurements | Measure star metrics (FWHM, eccentricity, etc.) |
| 5 | Reference frame selection | Select best frame as alignment reference |
| 6 | Fast Integration | Quick preview stack (non-drizzle) |
| 7 | Drizzle Integration (2x) | Final drizzle stack |
| 8 | Autocrop | Crop to overlapping region |
| 9 | Astrometric solution | Plate-solve the final stack |

### Active Steps (checkboxes)

| Step | Default | Recommended |
|------|---------|-------------|
| Linear Defects Correction | Unchecked | Unchecked |
| **Subframe Weighting** | Checked | **Checked** |
| **Image Registration** | Checked | **Checked** |
| **Local Normalization** | Checked | **Checked** |
| **Image Integration** | Checked | **Checked** |

### Global Options

| Setting | Default | Recommended | Description |
|---------|---------|-------------|-------------|
| FITS orientation | Global Pref. | Global Pref. | FITS image orientation handling |
| Compact GUI | — | — | Compact interface mode |
| Detect masters from path | — | — | Auto-detect master frames in directories |
| Generate maps | — | — | Generate rejection/weight maps |
| Preserve white balance | — | — | Preserve camera white balance |
| Save groups on exit | — | — | Save frame grouping on script exit |
| Smart naming override | — | — | Override output file naming |
| Purge cache | — | — | Clear cached data |
| **Registration Reference Image** | Mode: auto | auto | How to select the reference frame |
| **Output Directory** | — | Set explicitly | Where to save all output files |

---

## Lessons Learned

- **Force values:** Never check in astrometric solution — ASIAIR FITS headers contain RA/DEC. Forcing fails on rotated images (NGC 5746 incident).
- **Satellite trails:** Use Winsorized Sigma Clipping + Sigma High 1.9 + Large-scale pixel rejection High (layers 2, growth 2).
- **Multi-night data:** Enable Local Normalization to equalize sky backgrounds across nights.
- **Drizzle 2x:** Changes pixel scale — remember to use 1.88 µm (not 3.76) in ImageSolver post-stack.
- **Distortion correction:** Always enable for [[RedCat-51]] — improves edge star alignment, especially with Drizzle 2x.

---

## Quick Setup by Workflow

### RGB Broadband ([[RGB-Workflow]])

| Setting | Value |
|---------|-------|
| Drizzle | 2x |
| Rejection | Winsorized Sigma Clipping, σ high 1.9 |
| Large-scale rejection | High enabled, layers 2, growth 2 |
| Distortion correction | Enabled, 4000 spline points |
| Local normalization | Enabled (multi-night) |
| Subframe weighting | PSF Signal Weight |
| Force values | Unchecked |

### QuadBand Narrowband ([[QuadBand-OSC-Workflow]])

| Setting | Value |
|---------|-------|
| Drizzle | 2x |
| Rejection | Winsorized Sigma Clipping, σ high 1.9 |
| Large-scale rejection | High enabled, layers 2, growth 2 |
| Distortion correction | Enabled, 4000 spline points |
| Local normalization | Enabled (multi-night) |
| Subframe weighting | PSF Signal Weight |
| Force values | Unchecked |

---

## Resources

- [PixInsight WBPP documentation](https://pixinsight.com/doc/scripts/WBPP/WBPP.html)
