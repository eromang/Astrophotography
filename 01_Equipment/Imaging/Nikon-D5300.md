---
title: "Nikon D5300"
type: equipment
category: imaging
brand: "Nikon"
model: "D5300"
status: active
tags:
  - equipment/imaging
---

# Nikon D5300

DSLR camera used for astrophotography with the [[Celestron-NexStar-90SLT]]. Paired with the NexStar for lunar and planetary imaging.

- [Nikon product page](https://imaging.nikon.com/lineup/dslr/d5300/index.htm)
- [Firmware download](https://downloadcenter.nikonimglib.com/en/download/fw/285.html)
- [Nikon DSLR basics](https://imaging.nikon.com/lineup/dslr/basics/)

Firmware in `01_Equipment/Manuals/Nikon-D5300/`.

---

## Specifications

### Sensor

| Specification | Value |
|---------------|-------|
| Sensor | APS-C CMOS (Bayer RGGB) |
| Sensor size | 23.5 x 15.6 mm |
| Resolution | 6000 x 4000 pixels (24.2 MP) |
| Pixel size | 3.89 µm |
| ISO range | 100–25,600 |
| RAW format | NEF 14-bit |
| Color space | Adobe RGB (astrophotography setting) |

### Exposure

| Specification | Value |
|---------------|-------|
| Shutter speed | 1/4000s to 30s (+ Bulb) |
| Aperture range | f/3.5 to f/22 (lens dependent) |
| Exposure compensation | ±5 EV |
| EV step | 1/3 or 1/2 EV |
| Metering modes | Matrix, Center-weighted, Spot |

### Connectivity

| Feature | Detail |
|---------|--------|
| WiFi | Built-in (via Wireless Mobile Utility app) |
| USB | Mini-B USB 2.0 |
| Remote control | [dslrDashboard](https://dslrdashboard.info/camera-control-camera-properties-display/) or Nikon ML-L3 IR remote |
| Mount | Nikon F-mount |

---

## Astrophotography Settings

Settings to disable all in-camera processing that interferes with calibration and stacking:

| Setting | Value | Why |
|---------|-------|-----|
| Image quality | NEF (RAW) + JPEG fine | RAW for stacking, JPEG for quick review |
| NEF bit depth | 14-bit | Maximum dynamic range |
| Auto distortion control | **Off** | Alters pixel data — breaks flat calibration |
| Color space | Adobe RGB | Wider gamut than sRGB |
| Active D-Lighting | **Off** | Tone mapping alters data non-uniformly |
| Long exposure noise reduction | **Off** | Takes a dark after each light — halves session time; use separate darks instead |
| High ISO noise reduction | **Off** | Alters pixel data — breaks calibration |
| Auto ISO | **Off** | ISO must stay fixed across all lights |
| White balance | Daylight | Consistent WB across session; corrected in processing |
| AF-C priority | Release | Prevents shutter lock from focus failure |

> **Note:** If using a white balance (WB) filter, photograph a white surface to set custom WB before the session.

---

## Imaging Performance

### With [[Celestron-NexStar-90SLT]] (1250mm f/14)

| Parameter | Value |
|-----------|-------|
| Image scale | 0.64"/pixel |
| Field of view | ~0.28° x 0.19° |
| Sampling | Heavily oversampled (~4x for typical seeing) |
| Best for | Lunar, planetary (lucky imaging) |

### With [[RedCat-51]] (250mm f/4.9)

| Parameter | Value |
|-----------|-------|
| Image scale | 3.2"/pixel |
| Field of view | ~5.5° x 3.7° |
| Sampling | Well-matched for 2–4" seeing |
| Best for | Wide-field deep sky (backup to [[ASI2600MCPro]]) |

---

## Limitations for Astrophotography

| Limitation | Impact | Workaround |
|------------|--------|------------|
| No cooling | Thermal noise increases with temperature and exposure length | Shoot in winter; limit exposures to 60–120s |
| 30s max shutter | Cannot do multi-minute exposures natively | Use Bulb mode + intervalometer |
| Battery life | ~600 shots; drains faster in cold | External battery grip or AC adapter |
| No ST-4 port | Cannot connect autoguider | Guide through mount ([[iOptron-CEM26]]) instead |
| Mirror slap | Vibration on shutter actuation | Use Mirror Lock-Up (MLU) + remote trigger |
| IR/UV cut filter | Stock camera blocks Ha (656nm) partially | ~25% Ha transmission; consider astro-mod for nebulae |

### Ha Sensitivity (Stock Camera)

The stock D5300 has an IR-cut filter that blocks most infrared light, including a significant portion of the Ha (656nm) emission line:

- **~25% Ha transmission** — emission nebulae appear faint and desaturated
- Broadband targets (galaxies, clusters, reflection nebulae) are unaffected
- An astro-modification (IR filter removal) would restore full Ha sensitivity but is irreversible

For nebulae, the [[ASI2600MCPro]] + [[Antlia-FQuad]] is vastly superior. The D5300 is best used for **broadband targets** or with the **NexStar for lunar/planetary**.

---

## Focus Modes

| Mode | Description | Astro Use |
|------|-------------|-----------|
| MF | Full manual focus | **Primary** — use Live View + zoom for precise star focus |
| AF-S | Single servo AF | Not useful for astro |
| AF-C | Continuous servo AF | Not useful for astro |
| AF-A | Auto switching | Not useful for astro |

### Focusing Procedure

1. Switch lens/adapter to **MF**
2. Enable **Live View**
3. Point at a bright star
4. Zoom to **maximum** in Live View
5. Adjust focus until star is smallest point
6. Optionally use a **Bahtinov mask** for precise focus confirmation

---

## Resources

- [Nikon D5300](https://imaging.nikon.com/lineup/dslr/d5300/index.htm)
- [Firmware updates](https://downloadcenter.nikonimglib.com/en/download/fw/285.html)
- [dslrDashboard remote control](https://dslrdashboard.info/camera-control-camera-properties-display/)
