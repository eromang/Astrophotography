---
title: "iOptron CEM26"
type: equipment
category: mount
brand: "iOptron"
model: "CEM26"
status: active
purchase_date: 2022-09-16
purchase_price: "1,285.76 €"
purchase_store: "Astroshop"
purchase_url: "https://www.astroshop.eu"
tags:
  - equipment/mount
---

# iOptron CEM26

Center-balanced equatorial mount. Primary mount for deep sky imaging with the [[RedCat-51]] + [[ASI2600MCPro]] rig.

- [iOptron product page](https://www.ioptron.com/product-p/c261b1.htm)

---

## Specifications

### Mechanical

| Specification | Value |
|---------------|-------|
| Mount type | Center-Balanced Equatorial (CEM) |
| Payload capacity | 12 kg (26 lbs), excluding counterweight |
| Mount weight | 4.5 kg (10 lbs) |
| Payload/weight ratio | 2.60 |
| Structure | All metal, casting + CNC machined |
| Dovetail saddle | 3.8" Vixen-style, center adjustable |
| Counterweight | 4.5 kg (10 lbs) |
| Counterweight shaft | 20mm x 200mm + 120mm extension (M16, stainless steel) |
| Tripod | 1.5" stainless steel (5 kg) |
| Operating temperature | -10°C to 40°C |

### Drive System

| Specification | Value |
|---------------|-------|
| Motor | 1.8° stepper motor, 128x microdivision |
| Resolution | 0.17 arcsec |
| Transmission | Synchronous belt |
| Periodic error (PE) | < ±12 arcsec |
| PEC | Permanent PEC |
| Worm period | 600 sec |
| RA/DEC worm wheels | 88mm, 144 teeth, aluminum |
| RA/DEC worm gears | 15.2mm, brass |
| RA/DEC axis shafts | 35mm steel |
| RA/DEC bearings | 55mm ball bearings |

### Tracking & Slewing

| Specification | Value |
|---------------|-------|
| Tracking | Automatic (sidereal, lunar, solar, custom) |
| Slew speeds | 1x, 2x, 8x, 16x, 64x, 128x, 256x, 512x, MAX (6°/sec) |
| GoTo database | ~212,000 objects (Go2Nova 8409 hand controller) |

### Alignment

| Specification | Value |
|---------------|-------|
| Latitude adjustment | 0° to 60° |
| Azimuth adjustment | ±6° |
| Polar scope | AccuAlign optical polar scope |
| Level indicator | Bubble level |

### Connectivity

| Port | Type |
|------|------|
| WiFi | Built-in |
| USB | Mount control |
| Autoguide | ST-4 compatible |
| Hand controller | Go2Nova 8409 |
| PC control | ASCOM compatible |

### Power

| Specification | Value |
|---------------|-------|
| Input | 12V DC, 5A |
| Tracking consumption | 0.5A |
| GoTo consumption | 0.8A |
| AC adapter | 100V–240V (included, indoor use only) |
| Power-down memory | Yes |

---

## Current Payload

| Component | Weight |
|-----------|--------|
| [[RedCat-51]] (OTA + ring + dovetail) | 1.76 kg |
| [[ASI2600MCPro]] | ~0.9 kg |
| [[ZWO-EAF]] | 0.28 kg |
| [[UniGuide-32mm]] + [[ASI385MC]] | ~0.5 kg |
| Filter + adapters | ~0.2 kg |
| **Total** | **~3.6 kg** |
| **Capacity remaining** | **~8.4 kg (70% headroom)** |

The imaging rig is well under the 12 kg limit, leaving significant margin for stability.

---

## Characteristics

### Strengths

- **Center-balanced design** — lower moment of inertia than German equatorial, better tracking and less vibration
- **Lightweight** — 4.5 kg mount head, portable for field use
- **High payload ratio** — 2.6:1 ratio, current rig uses only 30% of capacity
- **Built-in WiFi** — wireless control via ASIAIR or iOptron Commander
- **Permanent PEC** — periodic error correction survives power cycles
- **ST-4 autoguide port** — direct guiding connection for [[ASI385MC]]
- **0.17 arcsec resolution** — fine enough for any imaging scale

### Limitations

- **Periodic error ±12 arcsec** — requires autoguiding for exposures > 30s at 3.1"/pixel
- **Latitude range 0–60°** — Tuntange at 49.6°N is within range but near the upper limit
- **Alt-az head not included** — equatorial only
- **No encoder option on base model** — CEM26EC variant has encoders

---

## Guiding Performance

At 3.1"/pixel ([[RedCat-51]] + [[ASI2600MCPro]]):

| Parameter | Value |
|-----------|-------|
| Max acceptable guide error | ~1.5" RMS (half pixel) |
| Unguided PE | ±12" (unusable for long exposures) |
| Guided PE (typical) | < 1" RMS with [[ASI385MC]] + [[UniGuide-32mm]] |
| Worm period | 600s — guide loop must correct within this cycle |

Autoguiding is **mandatory** for deep sky imaging at this focal length.

---

## Setup Procedure

1. Level tripod (bubble level)
2. Rough polar alignment (AccuAlign polar scope or iPolar)
3. Attach counterweight, balance RA axis
4. Attach imaging rig, balance DEC axis
5. Precise polar alignment via plate solving ([[ASIAIR]])
6. Star alignment (2–3 star or plate solve)
7. Start autoguiding ([[ASI385MC]] + [[UniGuide-32mm]])
8. Verify tracking with test exposure

See also: [[EAF-Workflow]] for the complete imaging session procedure.

---

## Firmware & Software

### Firmware

- [CEM26/GEM28 Firmware updates](https://www.ioptron.com/Articles.asp?ID=333)
- After firmware upgrade: set mount to zero position using "Set Zero Position"
- CEM26EC/GEM28EC: perform encoder calibration after upgrade

Firmware files in `01_Equipment/Manuals/CEM26/Firmware/`.

### iPolar Software

- [iPolar download](https://www.ioptron.com/product-p/c261b1.htm)
- Electronic polar alignment tool (alternative to optical polar scope)

Software in `01_Equipment/Manuals/CEM26/iPolar-Software/`.

### ASCOM Driver & iOptron Commander

- [ASCOM Driver download](https://www.ioptron.com/Articles.asp?ID=332)
- Uses RS-232 command language 2014 V3.x
- Requirements: Windows 7 SP1+ with .NET Framework 4.8, ASCOM Platform 6.5 SP1+

Driver files in `01_Equipment/Manuals/CEM26/ASCOM-Driver/`.

---

## Accessories

| Accessory | Purpose |
|-----------|---------|
| [[iOptron-LiteRoc-Tripod\|iOptron LiteRoc Tripod]] | Dedicated tripod for CEM26/GEM28 |
| [[Omegon-Anti-Vibration-Pads\|Omegon Anti-Vibration Pads]] | Dampen vibrations under tripod legs |

---

## Resources

- [iOptron CEM26 product page](https://www.ioptron.com/product-p/c261b1.htm)
- [CEM26 manual (PDF)](01_Equipment/Manuals/CEM26/Manual/C26_CEM26_Manual.pdf)
- [CEM26 quick start guide (PDF)](01_Equipment/Manuals/CEM26/Manual/C26_CEM26_QSG.pdf)
- [iPolar operation manual (PDF)](01_Equipment/Manuals/CEM26/Manual/3339_iPolarOperationManual.pdf)
- [RS-232 command language (PDF)](01_Equipment/Manuals/CEM26/ASCOM-Driver/RS-232_Command_Language2014V310.pdf)
