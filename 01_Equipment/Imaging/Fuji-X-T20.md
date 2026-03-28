---
title: "Fuji X-T20"
type: equipment
category: imaging
brand: "Fujifilm"
model: "X-T20"
status: retired
tags:
  - equipment/imaging
---

# Fujifilm X-T20

Mirrorless camera previously used for wide-field astrophotography. Replaced by the [[ASI2600MCPro]] as primary imaging camera.

- [Fujifilm product page](https://fujifilm-x.com/global/products/cameras/x-t20/)
- [Firmware downloads](https://fujifilm-x.com/global/support/download/firmware/cameras/x-t20/)
- [Firmware update procedure](https://fujifilm-x.com/global/support/download/procedure-x-interchangeable-ver2/)

---

## Specifications

### Sensor

| Specification | Value |
|---------------|-------|
| Sensor | APS-C X-Trans CMOS III (23.6 x 15.6 mm) |
| Resolution | 6000 x 4000 pixels (24.3 MP) |
| Pixel size | 3.93 µm |
| ISO range | 200–12,800 (extended: 100–51,200) |
| Bit depth | 14-bit RAW |
| RAW format | RAF |
| Sensor pattern | X-Trans (unique 6x6 pattern, not standard Bayer RGGB) |

### Mechanical

| Specification | Value |
|---------------|-------|
| Mount | Fujifilm X-mount |
| Shutter | 30s – 1/32,000s (electronic), 30s – 1/4,000s (mechanical) |
| Bulb mode | Yes |
| Screen | 3.0" tilting touchscreen |
| Viewfinder | Electronic (EVF) |
| Battery life | ~350 shots |
| Weight | 383g (body only) |
| Interface | USB 2.0, HDMI micro |

---

## Imaging Performance

### With [[RedCat-51]] (250mm f/4.9)

| Parameter | Value |
|-----------|-------|
| Image scale | 3.2"/pixel |
| Field of view | ~5.5° x 3.7° |
| Connection | Fuji X-mount T-adapter (M48) |

---

## Astrophotography Considerations

### X-Trans Sensor

The X-T20 uses Fujifilm's **X-Trans** color filter array instead of a standard Bayer (RGGB) pattern. This has implications for astrophotography processing:

- **Debayering:** Most astrophotography stacking software (PixInsight WBPP, DeepSkyStacker, SIRIL) supports X-Trans, but some older tools may not
- **Star artifacts:** Some debayering algorithms produce artifacts on small stars with X-Trans data — test with your stacking software
- **Color calibration:** SPCC in PixInsight supports X-Trans sensors

### Limitations for Astrophotography

| Limitation | Impact |
|------------|--------|
| No cooling | Thermal noise increases with ambient temperature and long exposures |
| Max 30s mechanical shutter | Requires intervalometer or bulb mode for longer exposures |
| Battery life | ~350 shots; external power recommended for long sessions |
| No ST-4 guiding | Cannot trigger autoguiding directly |
| X-Trans pattern | Less software compatibility than Bayer sensors |
| No live sensor output | Cannot use for EAA or live stacking |

### Advantages Over DSLR

| Advantage | Detail |
|-----------|--------|
| Electronic shutter | Vibration-free exposures up to 1/32,000s (useful for solar with filter) |
| Tilting screen | Easier framing when scope is at awkward angles |
| Lightweight | 383g body — minimal payload impact |
| Silent mode | No mirror slap vibration |

---

## Status: Retired

Replaced by the [[ASI2600MCPro]] for all deep sky imaging. The dedicated astronomy camera offers:
- Active cooling (35°C below ambient)
- Direct USB control via [[ASIAIR]]
- 16-bit output (vs 14-bit)
- Autoguider integration
- No battery dependency

The X-T20 remains usable for:
- **Nightscape / wide-field** — with native Fuji lenses on a tripod or star tracker
- **Solar imaging** — electronic shutter + solar filter
- **Backup camera** — if the ASI2600MC Pro is unavailable

---

## Resources

- [Fujifilm X-T20](https://fujifilm-x.com/global/products/cameras/x-t20/)
- [Firmware downloads](https://fujifilm-x.com/global/support/download/firmware/cameras/x-t20/)
