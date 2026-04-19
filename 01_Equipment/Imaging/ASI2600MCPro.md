---
title: "ASI2600MC Pro"
type: equipment
category: imaging
brand: "ZWO"
model: "ASI2600MC Pro"
status: active
purchase_date: 2023-10-23
purchase_price: "2,590.00 €"
purchase_store: "Astroshop"
purchase_url: "https://www.astroshop.eu"
tags:
  - equipment/imaging
---

# ZWO ASI2600MC Pro

Primary deep sky imaging camera. Cooled color (OSC) CMOS camera with the Sony IMX571 sensor.

- [ZWO product page](https://www.zwoastro.com/product/asi2600/)
- [Driver download](https://astronomy-imaging-camera.com/software-drivers)

---

## Configuration

| Parameter | Value |
|-----------|-------|
| Gain | 100 (Unity gain) |
| Cooling | -10°C year-round (standardized 2026-04-19 — see [[ASIAIR]] camera profile for rationale) |
| Output format | FITS 16-bit |

### Why Gain 100?

Gain 100 is the **unity gain** point for the IMX571 where 1 electron = 1 ADU. This provides:
- Lowest read noise (1.0–1.45 e-)
- Good dynamic range
- Full use of the 16-bit ADC
- Best trade-off between sensitivity and full well capacity

---

## Specifications

### Sensor

| Specification | Value |
|---------------|-------|
| Sensor | Sony IMX571 CMOS (back-illuminated) |
| Type | Color (Bayer RGGB) |
| Sensor size | 23.5 x 15.7 mm (APS-C) |
| Sensor diagonal | 28.3 mm |
| Resolution | 6248 x 4176 pixels (26 MP) |
| Pixel size | 3.76 µm |
| Bit depth | 16-bit |
| Full well capacity | 50,000 e- (at gain 0) |
| Read noise | 1.0–3.3 e- (gain dependent) |
| Read noise (gain 100) | ~1.45 e- |
| Gain (e-/ADU at gain 100) | 0.25 |
| QE peak | ~91% (back-illuminated) |

### Cooling

| Specification | Value |
|---------------|-------|
| Active cooling | Yes (TEC) |
| Max cooling delta | 35°C below ambient |
| Temperature regulation | ±0.1°C stability |
| Anti-dew heater | Built-in |

### Mechanical

| Specification | Value |
|---------------|-------|
| Telescope connection | T2 (M42 x 0.75) |
| Backfocus (flange to sensor) | 17.5 mm |
| Interface | USB 3.0 (USB 2.0 compatible) |
| Power | 12V DC |
| Buffer memory | 256 MB DDR3 RAM |
| Frame rate (full resolution) | 3.5 fps |

---

## Imaging Performance

### With [[RedCat-51]] (250mm f/4.9)

| Parameter | Value |
|-----------|-------|
| Image scale | 3.1"/pixel |
| Field of view | ~5.4° x 3.6° |
| Sampling | Well-matched for 2–4" seeing |
| Drizzle 2x output | 12496 x 8352 pixels |

### With [[Celestron-NexStar-90SLT]] (1250mm f/14)

| Parameter | Value |
|-----------|-------|
| Image scale | 0.62"/pixel |
| Field of view | ~0.28° x 0.19° |
| Sampling | Heavily oversampled |

---

## Gain & Read Noise

| Gain | Read Noise (e-) | Full Well (e-) | Dynamic Range | Use Case |
|------|-----------------|----------------|---------------|----------|
| 0 | ~3.3 | 50,000 | Highest | Bright objects, HDR |
| 100 | ~1.45 | ~12,500 | Balanced | **Standard deep sky (default)** |
| 200 | ~1.2 | ~6,250 | Lower | Very faint narrowband |
| 300 | ~1.0 | ~3,125 | Lowest | Extreme narrowband |

Gain 100 is the recommended default. Higher gains reduce full well capacity and risk clipping bright stars, but lower read noise benefits extremely faint narrowband signals.

---

## Calibration Requirements

Calibration frames must match the camera settings used during capture:

| Frame Type | Must Match | See |
|------------|------------|-----|
| Dark | Exposure, gain, temperature | [[Frames]] |
| Flat | Gain, optical train (filter + scope) | [[Frames]] |
| Dark flat | Flat exposure, gain | [[Frames]] |
| Bias | Gain | [[Frames]] |

Master calibration library: [[Master-Library]]

### Cooling Temperature Strategy

| Season | Ambient (typical) | Set Point | Reasoning |
|--------|-------------------|-----------|-----------|
| Summer | 15–25°C | **-10°C** | 35°C delta at 25°C ambient = sensor at -10°C |
| Winter | -5–10°C | **-20°C** | Lower ambient allows deeper cooling |
| Shoulder | 5–15°C | **-15°C** | Intermediate option |

Using consistent set points per season simplifies the dark frame library — one set of darks per exposure/temperature combination covers all sessions at that temperature.

---

## Color Camera Considerations

As a **color (OSC) camera**, the ASI2600MC Pro has a Bayer matrix (RGGB) over the sensor:

### Advantages
- Single exposure captures all color channels — simpler workflow
- No filter wheel needed for broadband imaging
- Faster data acquisition (no 3–4x exposure multiplier for LRGB)

### Limitations
- Each pixel only sees one color — effective resolution is lower than mono
- Narrowband data is mixed across Bayer channels (see [[QuadBand-OSC-Workflow]])
- Cannot do true SHO (Hubble palette) — requires mono camera
- Cannot do true LRGB — synthetic luminance only
- Debayering introduces interpolation artifacts

### With Narrowband Filters

The [[Antlia-FQuad]] passes Ha, OIII, Hb, SII onto the Bayer matrix:
- Red pixels: Ha (656nm) + SII (672nm)
- Green pixels: OIII (496/500nm) + Hb (486nm)
- Blue pixels: OIII (496/500nm)

See [[QuadBand-OSC-Workflow]] for the processing approach.

---

## Technical Charts

![ASI2600MC Pro — Full Well & Specifications](/01_Equipment/Manuals/ASI2600MCPro/ZWO-Camera-ASI-2600-MC-Pro-Color.jpg)

![ASI2600MC Pro — Wavelength Response](/01_Equipment/Manuals/ASI2600MCPro/228bdb512b1405e9e24a5349951fa748-1.jpg.webp)

![ASI2600MC Pro — Mechanical Dimensions](/01_Equipment/Manuals/ASI2600MCPro/ZWO-Camera-ASI-2600-MC-Pro-Color-Unitmm.jpg)

![ASI2600MC Pro — Camera Bag Contents](/01_Equipment/Manuals/ASI2600MCPro/Camera%20bag.jpg)

---

## Resources

- [ZWO ASI2600MC Pro](https://www.zwoastro.com/product/asi2600/)
- [ZWO Driver & Software](https://astronomy-imaging-camera.com/software-drivers)
- [Discovery Astrophotography with ZWO (PDF)](01_Equipment/Manuals/ASI2600MCPro/ASI2600%20Pro%20Series%20-%20Discovery%20Astrophotography%20with%20ZWO%20ASTRO.pdf)
