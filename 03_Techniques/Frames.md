---
title: "Calibration Frames"
type: technique
tags:
  - technique
  - processing/calibration
---

# Calibration Frames

Calibration frames remove systematic noise and optical artifacts from light frames during stacking. Each type corrects a specific defect.

---

## Light Frames

The actual images of the sky containing the signal you want to capture.

| Parameter | Requirement |
|-----------|-------------|
| Shutter speed | Set for target (typically 160–300s for deep sky) |
| Gain/ISO | Fixed (Gain 100 for [[ASI2600MCPro]]) |
| Temperature | Controlled (cooled to -10°C or -20°C) |
| Filter | As needed ([[Antlia-FQuad]] or [[Optolong-LPro]]) |

**Temperature matters** — sensor thermal noise scales with temperature. Cooled cameras should be set to a consistent temperature across all sessions for a given target.

---

## Dark Frames

Capture the sensor's thermal noise (hot pixels, amp glow) for subtraction from lights.

| Parameter | Requirement |
|-----------|-------------|
| Lens/cover | **Capped** — no light reaching the sensor |
| Exposure | **Same as lights** |
| Gain/ISO | **Same as lights** |
| Temperature | **Same as lights** (critical) |
| Recommended count | 25–30 per exposure/temperature combination |

**How they work:** Dark frames record only the thermal signal (dark current + fixed-pattern noise). Subtracting them from lights removes these artifacts.

**With a cooled camera:** The [[ASI2600MCPro]] at -10°C produces very consistent darks. A master dark library at each exposure length eliminates the need to reshoot darks every session (see [[Master-Library]]).

> [Reference: How to take dark frames](https://astrobackyard.com/how-to-take-dark-frames/)

---

## Flat Frames

Correct for uneven illumination across the sensor caused by dust, vignetting, and optical path variations.

| Parameter | Requirement |
|-----------|-------------|
| Light source | Even illumination (twilight sky, white t-shirt over scope, flat panel) |
| Exposure | **Adjusted** — aim for histogram peak at ~40–50% (use A mode on DSLR, or auto-exposure in ASIAIR) |
| Gain/ISO | **Same as lights** |
| Filter | **Same as lights** (same optical train) |
| Focus | **Same as lights** — do not refocus between session and flats |
| Rotation | **Same as lights** — do not rotate camera |
| Temperature | Not critical |
| Recommended count | 30–50 |

**How they work:** Flat frames map the illumination pattern of the optical train. Dividing lights by the master flat normalizes the brightness across the field.

**Important:** The optical train must be identical to the lights — same scope, filter, camera orientation, and focus position. Any change invalidates the flats.

> [Reference: How to take flat frames](https://astrobackyard.com/how-to-take-flat-frames/)

---

## Dark Flat Frames

Remove thermal noise and bias from the flat frames themselves.

| Parameter | Requirement |
|-----------|-------------|
| Lens/cover | **Capped** |
| Exposure | **Same as flats** (typically very short, e.g. 60ms) |
| Gain/ISO | **Same as flats** |
| Temperature | Not critical (short exposures = negligible thermal noise) |
| Recommended count | 30–50 |

**How they work:** Dark flats are darks matched to the flat exposure. They remove the bias + minimal dark signal from the flat frames before the master flat is computed.

---

## Bias Frames

Capture the sensor's read noise — the fixed electronic pattern present in every exposure regardless of duration.

| Parameter | Requirement |
|-----------|-------------|
| Lens/cover | **Capped** |
| Exposure | **Shortest possible** (to capture only read noise, no thermal signal) |
| Gain/ISO | **Same as lights** |
| Temperature | Not critical |
| Recommended count | 50–100 |

**How they work:** Bias frames isolate the read noise floor. They are subtracted from darks and flats during calibration.

**Note:** Some stacking software (including PixInsight WBPP) can use dark flats instead of separate bias frames when matched darks are available. Check your workflow.

> [Reference: Bias frames in astrophotography](https://astrobackyard.com/bias-frames-astrophotography/)

---

## Calibration Summary

| Frame | Corrects | Cover | Exposure | Gain | Temp | Count |
|-------|----------|-------|----------|------|------|-------|
| Light | — (signal) | Open | Target | Same | Controlled | As many as possible |
| Dark | Thermal noise, hot pixels | Capped | = Light | = Light | = Light | 25–30 |
| Flat | Vignetting, dust, uneven illumination | Even light | Auto (~40-50%) | = Light | Any | 30–50 |
| Dark Flat | Bias + noise in flats | Capped | = Flat | = Flat | Any | 30–50 |
| Bias | Read noise | Capped | Shortest | = Light | Any | 50–100 |

---

## Calibration Flow

```
Light - Dark = (Signal + Noise) - Noise = Clean Signal
Flat - Dark Flat = Clean Flat
Clean Signal / Clean Flat = Calibrated Frame
```

Multiple calibrated frames are then **registered** (aligned) and **stacked** (integrated) in WBPP.

---

## Image Quality Metrics

Metrics used by SubFrameSelector to evaluate and reject sub-frames.

### FWHM (Full Width at Half Maximum)

Measures the "width" of stars in pixels. Indicates focus quality and atmospheric seeing.

- **Lower is better** — tighter stars mean better focus/seeing
- Depends on: camera resolution, optics quality, atmospheric turbulence
- At 3.1"/pixel ([[RedCat-51]] + [[ASI2600MCPro]]), typical good FWHM: 2–4 pixels

### Eccentricity

Measures how much stars are elongated vs perfectly circular. Values range from 0 (perfect circle) to 1 (line).

- **Lower is better** — circular stars indicate good tracking and optics
- Caused by: tracking errors, wind, optical tilt, poor polar alignment
- Target: < 0.5 (ideally < 0.3)

### Median

The median pixel intensity value across the image. Indicates background sky brightness.

- Used to compare sky conditions between sub-frames
- Higher median = brighter sky (clouds, moon, light pollution)
- Reject frames with significantly higher median than the set average

### Noise

The standard deviation of pixel values in the background. Indicates overall noise level.

- **Lower is better**
- High noise frames degrade the final stack
- Caused by: clouds, high humidity, light pollution, short exposures

### SNR Weight

Combined metric factoring signal, noise, FWHM, and eccentricity. Used by SubFrameSelector to rank frames.

- **Higher is better**
- Best single metric for overall frame quality
- Use as the primary rejection/weighting criterion in WBPP

---

## Drizzle

An advanced stacking technique that improves spatial resolution by combining dithered, undersampled images onto a finer output grid.

- **Drizzle factor 2** is used in both workflows (see [[RGB-Workflow]], [[QuadBand-OSC-Workflow]])
- Doubles the output resolution (e.g., 6248x4176 becomes 12496x8352)
- Requires **dithering** during capture — small random shifts between exposures (configured in ASIAIR guiding settings)
- Most beneficial when imaging scale is undersampled (pixels larger than seeing allows)
- At 3.1"/pixel with the RedCat 51, drizzle helps recover detail when seeing is good (< 3")
