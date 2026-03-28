---
title: "ASI385MC"
type: equipment
category: guiding
brand: "ZWO"
model: "ASI385MC"
status: active
tags:
  - equipment/guiding
---

# ZWO ASI385MC

Uncooled color guide camera. Paired with the [[UniGuide-32mm]] for autoguiding during deep sky imaging sessions.

- [ZWO product page](https://www.zwoastro.com/product/asi385mc/)
- [Driver download](https://astronomy-imaging-camera.com/software-drivers)

---

## Guiding Configuration

Settings used with [[ASIAIR]] for autoguiding on the [[iOptron-CEM26]]:

| Parameter | Value |
|-----------|-------|
| Gain | 200–300 |
| Exposure | 1–2s |
| Calibration step | 2000ms |
| Max RA duration | 2000ms |
| Max DEC duration | 2000ms |

### Guiding Performance

With the [[UniGuide-32mm]] (120mm f/3.75):

| Parameter | Value |
|-----------|-------|
| Image scale | 6.4"/pixel |
| Field of view | ~3.4° x 1.9° |
| Guide star density | Usually 5–20 usable stars |
| Typical RMS | < 1" (at mount level) |

The 6.4"/pixel scale is well-suited for guiding — large enough to always find guide stars, fine enough to correct sub-arcsecond errors.

### Gain Selection

| Gain | Use Case |
|------|----------|
| 200 | Default — good balance of star brightness and noise |
| 250 | Sparse star fields or poor transparency |
| 300 | Very sparse fields, short guide exposures |

Higher gain increases guide star brightness but also increases noise. Stay at the lowest gain that reliably detects guide stars.

### Exposure Selection

| Exposure | Use Case |
|----------|----------|
| 1s | Good seeing, bright guide stars — faster correction loop |
| 2s | Faint guide stars, sparse fields — more signal per frame |

Shorter exposures give faster guide corrections but need brighter stars. The [[iOptron-CEM26]] worm period is 600s, so guide corrections at 1–2s intervals provide ~300–600 corrections per worm cycle.

---

## Specifications

### Sensor

| Specification | Value |
|---------------|-------|
| Sensor | Sony IMX385 CMOS (1/2") |
| Sensor diagonal | 8.35 mm |
| Resolution | 1936 x 1096 pixels (2.12 MP) |
| Pixel size | 3.75 µm |
| Bit depth | 12-bit ADC |
| Shutter | Rolling |
| Exposure range | 32 µs – 2000s |
| ROI | Supported |

### Performance

| Mode | Resolution | Frame Rate |
|------|------------|------------|
| 10-bit ADC | 1936 x 1096 | 120 fps |
| 12-bit ADC | 1936 x 1096 | 67 fps |

> High frame rates are relevant for planetary/lunar use, not for guiding (which runs at 0.5–1 fps).

### Mechanical

| Specification | Value |
|---------------|-------|
| Dimensions | 62mm diameter x 36mm |
| Weight | 120g |
| Backfocus (flange to sensor) | 12.5mm |
| Adapters | 2", 1.25", M42 x 0.75 |
| Protect window | AR coated |
| Interface | USB 3.0 (USB 2.0 compatible) |
| ST-4 guider port | Yes |

### Environmental

| Specification | Value |
|---------------|-------|
| Operating temperature | -5°C to 45°C |
| Storage temperature | -20°C to 60°C |
| Operating humidity | 20%–80% |
| Cooling | None (uncooled) |

---

## Connection Options

| Method | Connection | Used For |
|--------|------------|---------|
| USB to [[ASIAIR]] | USB 3.0 cable | Primary — ASIAIR controls guiding |
| ST-4 to [[iOptron-CEM26]] | ST-4 cable | Direct pulse guiding (backup) |
| USB to PC | USB 3.0 cable | PHD2 guiding from laptop |

The ASIAIR handles guiding internally — USB connection to ASIAIR is the standard configuration.

---

## Alternative Use Cases

While primarily a guide camera, the ASI385MC can also be used for:

| Use Case | Setup | Notes |
|----------|-------|-------|
| Planetary imaging | Direct on [[Celestron-NexStar-90SLT]] | 0.62"/pixel at 1250mm, 120fps for lucky imaging |
| EAA (live stacking) | On any telescope | Real-time viewing via [[ASIStudio]] ASILive |
| All-sky camera | Wide-angle lens | Meteor detection with ASIMeteorCap |

---

## Technical Charts

![ASI385MC — Resolution](/01_Equipment/Manuals/ASI385MC/Resolution.jpg)

![ASI385MC — Mechanical Dimensions](/01_Equipment/Manuals/ASI385MC/Unitmm.jpg)

![ASI385MC — Full Well Capacity](/01_Equipment/Manuals/ASI385MC/Full%20Well%20(e-).jpg)

![ASI385MC — Wavelength Response](/01_Equipment/Manuals/ASI385MC/228bdb512b1405e9e24a5349951fa748-1.jpg.webp.jpeg)

---

## Resources

- [ZWO ASI385MC](https://www.zwoastro.com/product/asi385mc/)
- [ZWO Driver & Software](https://astronomy-imaging-camera.com/software-drivers)
- [ASI385MC manual (PDF)](01_Equipment/Manuals/ASI385MC/ASI385_Manual_EN_V1.2.pdf)
