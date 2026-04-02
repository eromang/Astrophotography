---
title: "ASIAIR Plus"
type: equipment
category: accessory
brand: "ZWO"
model: "ASIAIR Plus"
status: active
purchase_date: 2022-04-10
purchase_price: "$299.00"
purchase_store: "ZWO ASI"
purchase_url: "https://www.zwoasi.com"
tags:
  - equipment/accessory
---

# ZWO ASIAIR Plus

Dedicated astrophotography computer that controls the entire imaging rig wirelessly from a phone or tablet. Central hub connecting the [[ASI2600MCPro]], [[ASI385MC]], [[ZWO-EAF]], and [[iOptron-CEM26]].

- [ZWO ASIAIR product page](https://www.zwoastro.com/product/asiair/)

Purchased in 2022.

---

## Specifications

| Specification | Value |
|---------------|-------|
| Model | ASIAIR Plus (2nd generation) |
| Processor | Quad-core ARM Cortex-A53 |
| RAM | 2 GB |
| Storage | 64 GB internal + external USB storage |
| WiFi | 2.4 GHz + 5 GHz dual-band (built-in hotspot) |
| Ethernet | Yes (10/100 Mbps) |
| USB ports | 4x USB 2.0 |
| DC power ports | 4x 12V DC outputs (for mount, camera, accessories) |
| Power input | 12V DC |
| Dimensions | 127 x 82 x 28 mm |
| Weight | ~250g |
| Operating temperature | -20°C to 40°C |

---

## Connected Equipment

| USB Port | Device | Function |
|----------|--------|----------|
| USB 1 | [[ASI2600MCPro]] | Imaging camera — capture, cooling, gain control |
| USB 2 | [[ASI385MC]] | Guide camera — autoguiding |
| USB 3 | [[ZWO-EAF]] | Autofocuser — focus control |
| USB 4 | Available | Spare (e.g., filter wheel, dew heater controller) |

| DC Port | Device | Function |
|---------|--------|----------|
| DC 1 | [[iOptron-CEM26]] | Mount power (12V) |
| DC 2–4 | Available | Dew heaters, other accessories |

| Connection | Device | Method |
|------------|--------|--------|
| WiFi | Phone/tablet | ASIAIR app control |
| ST-4 / USB | [[iOptron-CEM26]] | Mount GoTo and tracking commands |

---

## Core Functions

### Capture

| Function | Description |
|----------|-------------|
| Single exposure | Manual single-frame capture |
| Sequence planning | Automated multi-target capture with timing |
| Exposure control | Gain, exposure time, cooling temperature, binning |
| Dithering | Random sub-pixel shifts between exposures for drizzle |
| Meridian flip | Automatic flip and re-center when target crosses meridian |
| Live preview | Real-time stretched preview during capture |

### Autoguiding

| Function | Description |
|----------|-------------|
| Internal guider | Built-in PHD2-based guiding engine |
| Calibration | Auto-calibrate guide camera to mount response |
| Multi-star guiding | Track multiple guide stars for better accuracy |
| Guide graph | Real-time RA/DEC error graph |
| Dither control | Pause guiding during dither, resume after settling |

### Autofocus

| Function | Description |
|----------|-------------|
| V-curve autofocus | Automated focus routine via [[ZWO-EAF]] |
| Periodic autofocus | Re-focus at set intervals during sequence |
| Temperature trigger | Re-focus when temperature drops beyond threshold |
| Filter offset | Store focus offsets per filter for automatic adjustment |

### Plate Solving

| Function | Description |
|----------|-------------|
| Blind solve | Identify sky position from any pointing |
| GoTo correction | Solve, correct, re-slew for precise centering |
| Polar alignment | Precise polar alignment via plate solve routine |
| Mosaic planning | Frame mosaic panels with plate-solved coordinates |

### Planning

| Function | Description |
|----------|-------------|
| Object database | Built-in catalog of deep sky objects |
| Altitude chart | Object altitude through the night |
| FOV overlay | Show camera field of view on sky map |
| Session planning | Schedule targets with start/end times |

---

## Imaging Workflow

The ASIAIR orchestrates the entire session after initial setup:

1. **Power on** — connect via ASIAIR app on phone/tablet
2. **Cool camera** — set [[ASI2600MCPro]] to target temperature (-10°C or -20°C)
3. **Polar alignment** — plate-solve assisted polar alignment
4. **GoTo target** — slew to first target, plate solve, center
5. **Autofocus** — run V-curve autofocus via [[ZWO-EAF]]
6. **Start guiding** — calibrate and start autoguiding with [[ASI385MC]]
7. **Start sequence** — automated capture with dithering
8. **Monitor** — check guide graph, preview subs on phone
9. **Target change** — ASIAIR slews, re-centers, re-focuses, re-guides automatically
10. **Meridian flip** — automatic when target crosses meridian

---

## Data Storage

| Storage | Use |
|---------|-----|
| Internal 64 GB | Session data buffer — transfer to external after session |
| USB SSD/HDD | Primary storage — FITS files written directly |
| MicroSD | Not available on Plus model |

FITS files are stored organized by date and target. Transfer to PC for processing in [[PixInsight|Modules]].

### File Sizes (ASI2600MC Pro)

| Format | Per frame | 100 frames |
|--------|-----------|------------|
| FITS 16-bit | ~50 MB | ~5 GB |
| FITS 16-bit + drizzle data | ~50 MB | ~5 GB |

A typical session (150–200 frames) generates 7–10 GB of data.

---

## WiFi Configuration

| Mode | Use Case |
|------|----------|
| Hotspot (default) | ASIAIR creates its own WiFi network — connect phone directly |
| Station mode | ASIAIR joins home WiFi — accessible from any device on network |

**Hotspot mode** is standard for field use. **Station mode** is convenient for balcony imaging at home (Tuntange) — allows control from inside while the rig is on the balcony.

---

## Characteristics

### Strengths

- **All-in-one control** — replaces laptop + multiple software packages
- **Wireless operation** — control from phone/tablet, no cables to trip over
- **Integrated power distribution** — 4x 12V DC outputs reduce cable clutter
- **Automated workflow** — sequence, guide, focus, dither, meridian flip all handled
- **Low power** — runs on 12V, no laptop battery drain
- **Cold-weather resistant** — operates to -20°C

### Limitations

- **ZWO ecosystem** — best with ZWO cameras; third-party camera support is limited
- **USB 2.0 only** — slower file transfer than USB 3.0 (adequate for imaging, slow for bulk transfer)
- **No advanced processing** — capture only; all processing done on PC in PixInsight
- **Phone app only** — no desktop app; must use phone/tablet for control
- **WiFi range** — hotspot range ~10–15m; walls reduce this significantly
- **No ASCOM** — uses its own protocol; not compatible with ASCOM-based software chains

---

## Resources

- [ZWO ASIAIR](https://www.zwoastro.com/product/asiair/)
- [ASIAIR user manual (PDF)](01_Equipment/Manuals/ASIAIR/Manuals/ZWO_ASIAIR_PRO_User_Manual.pdf)
- [ASIAIR quick guide (PDF)](01_Equipment/Manuals/ASIAIR/Manuals/ZWO_ASIAIR_Quick_Guide.pdf)
- [ASIAIR user manual (original) (PDF)](01_Equipment/Manuals/ASIAIR/Manuals/ZWO_ASIAIR_User_Manual.pdf)
- [How to restore ASIAIR OS (PDF)](01_Equipment/Manuals/ASIAIR/Manuals/How_to_Restore_ASIAIR_OS.pdf)
