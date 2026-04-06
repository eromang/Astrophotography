---
title: "ZWO EFW 5×2\""
type: equipment
category: accessory
brand: "ZWO"
model: "EFW 5×2\""
status: wishlist
created: 2026-04-05
tags:
  - equipment/accessory
---

# ZWO EFW 5×2" (Electronic Filter Wheel)

Motorized 5-position filter wheel for 2" (48mm) filters. Enables automated filter switching via [[ASIAIR]] during imaging sequences — no manual intervention needed for multi-filter or two-filter nights.

---

## New vs Old Model (2026 Revision)

ZWO quietly released an updated EFW in early 2026 with no marketing push. The changes are significant — ensure you buy the **new version** (USB-C, rubber gaskets).

> Source: [View into Space review](https://www.youtube.com/watch?v=OSAaSDsPMk0) (2026-01-19)

| Change | Old Model | New Model (2026) |
|--------|-----------|------------------|
| Connector | USB Type-B | **USB-C** (USB 2.0 Type-A to Type-C cable included) |
| Light leak protection | Flat plate cover, potential for leaks at seams | **Slot-fit chassis** with dual light-blocking pads on both lateral connection points |
| Motor compartment | Exposed | **Fully enclosed** — improved light isolation and environmental resistance |
| Dust sealing | Open seams | Sealed design — dust cannot settle in the light path |
| Internal layout | Exposed cables, motor visible | Clean PCB, fully encapsulated motor, no loose cables |
| Body | Standard machining | **CNC-machined aluminum alloy**, 6061 alloy internal carousel |
| Motor | Standard | **High-precision stepper motor**, bidirectional drive with position indexing |
| Finish | Standard | Laser-engraved finish, cleaner logo detailing |

### Flat Frame Reuse

The sealed design means **flats can be reused for months** as long as the optical train is not disassembled. No dust enters between sessions. This eliminates per-session flat capture — a significant time saving across multi-month campaigns.

> [!tip] Purchasing note
> ZWO did not widely promote the revision. When ordering, verify USB-C connector and rubber gaskets to confirm you have the 2026 model, not old stock.

---

## Specifications

| Specification | Value |
|---------------|-------|
| Model | EFW-5×2-25 |
| Filter positions | 5 |
| Filter size | 2" (48mm) mounted |
| Back focus | 20mm |
| Native connection | **M54** (both sides) |
| Body material | CNC-machined aluminum alloy |
| Carousel material | 6061 aluminum alloy |
| Motor | High-precision stepper motor, bidirectional |
| Power | 120 mA at 5V — USB-powered only, no external PSU |
| Connector | USB-C (USB 2.0 Type-A to Type-C cable included) |
| Positioning accuracy | 1/3600 (improved in 2026 revision) |
| Driver | Driver-free, plug-and-play |
| Software | [[ASIAIR]], ASIStudio, ASCOM, ZWO SDK |

## Included Accessories

| Item | Description |
|------|-------------|
| M54M-M48F | M54 male → M48 female adapter (telescope side) |
| M54M-M42F | M54 male → M42 (T2) female adapter (camera side) |
| M54M-M48F-2 | M54 male → M48 female adapter (second variant) |
| USB-C cable (0.5m) | Short cable for close ASIAIR connection |
| USB-C cable (2m) | Longer cable option |
| Filter masks | 10 pcs — light-blocking masks for unused filter positions |
| M2.5×6 screws | 6 pcs — filter retaining screws |
| M2×4 screws | 26 pcs — filter cell screws |
| Phillips screwdriver | 3×75mm — for filter installation |

---

## Filter Constraints

From the EFW Quick Guide:

| Constraint | Limit |
|------------|-------|
| Filter thickness (glass only) | < 7mm |
| Thread thickness | < 3mm |
| M42 adapter protrusion | Must not protrude into the wheel cavity — can jam the carousel |

> [!warning] Carousel balance
> With only 2 filters in a 5-position wheel, distribute them to maintain balance. Place filters in **positions 1 and 3** (or 1 and 4) rather than adjacent slots. Use the included filter masks on empty positions.

---

## Planned Filter Configuration

| Position | Filter | Use |
|----------|--------|-----|
| 1 | [[Antlia-FQuad]] | Emission nebulae (narrowband) |
| 2 | Filter mask | — |
| 3 | [[Optolong-LPro]] | Galaxies, clusters, reflection nebulae (broadband) |
| 4 | Filter mask | — |
| 5 | — | Free slot for future filter |

> Positions 1 and 3 chosen for carousel balance with only 2 filters installed. Three slots remain for future filters (e.g., Optolong L-eXtreme, Antlia ALP-T, or dedicated OIII/Ha).

---

## Optical Train Integration

**Current train (no EFW):**
[[RedCat-51]] → Filter (manual) → [[ASI2600MCPro]]

**Planned train (with EFW):**
[[RedCat-51]] (M48) → M48 spacers (~11mm) → M48F-M54M adapter (included) → **EFW 5×2"** → M54M-M42F adapter (included) → [[ASI2600MCPro]] (T2/M42)

### Back Focus Calculation

The [[RedCat-51]] requires **59.7mm** total back focus from the M48 thread to the sensor.

| Component | Thread | Distance |
|-----------|--------|----------|
| M48 spacers | M48 | **~11mm** (to verify) |
| M54M-M48F adapter (included) | M48→M54 | ~6mm (measure with calipers) |
| EFW 5×2" body | M54 | 20mm |
| M54M-M42F adapter (included) | M54→T2 | ~5mm (measure with calipers) |
| ASI2600MC Pro (flange to sensor) | T2/M42 | 17.5mm |
| **Total** | | **~59.5mm** → adjust spacers to reach 59.7mm |

**Spacers available:**
- [[ASToptics-M48-Extension-5mm]] (5mm, owned) — covers half the gap
- Need: ~6mm additional M48 spacer(s) — e.g., 5mm + 1mm or a single 6mm ring (~€10–20 from Astroshop)

> **Measure the exact adapter optical path lengths with calipers before buying spacers.** The included adapter lengths may differ from typical values. Incorrect back focus causes star elongation in the corners. Test with a star field and check all four corners after assembly.

### EAF and EFW Together

Both the [[ZWO-EAF]] and EFW connect to the [[ASIAIR]] via USB. The ASIAIR manages both:
- **EAF** adjusts focus when changing filters (different filter thickness shifts back focus)
- **EFW** switches filters on command or per-target in the sequence plan

> **Autofocus after filter change:** Each filter has a slightly different optical thickness. Configure the ASIAIR to run autofocus after every filter switch to maintain sharp focus.

---

## ASIAIR Integration

The EFW appears as a connected device in ASIAIR:

1. **Connect** via USB to ASIAIR
2. **Name each position** in the EFW settings (Quad Band, L-Pro, etc.)
3. **Assign filter per target** in the capture plan — ASIAIR switches automatically
4. **Flat frames:** ASIAIR knows which filter was used and matches flats accordingly

### Two-Filter Night Workflow

With the EFW, a session can use both filters in one night:

1. Start with Quad Band on emission nebulae (e.g., NGC 7000)
2. ASIAIR switches to L-Pro for broadband targets (e.g., M33)
3. Autofocus runs after the switch
4. Each target's lights are tagged with the correct filter in FITS headers

> This is particularly useful in **September–October** when both emission nebulae and broadband targets are available in the same night. See [[Seasonal-Calendar]].

---

## Calibration Impact

Each filter requires its own flat set. With the EFW:

- **Flat frames per filter:** Capture separate flats for each filter after initial EFW installation
- **Flat reuse:** The sealed 2026 design prevents dust ingress — flats remain valid for months as long as the optical train is not disassembled. No need to reshoot flats every session
- **Revalidate flats when:** the EFW is removed, camera is detached, or any spacer/adapter is changed
- **WBPP matching:** WBPP matches flats to lights by filter keyword in FITS headers
- Current flat masters available: [[Antlia-FQuad]] (50ms, 60ms) and [[Optolong-LPro]] (60ms). See [[Master-Library]]. New masters will be needed after EFW installation changes the optical train.

---

## Troubleshooting

From the EFW Quick Guide V2.1:

| Problem | Cause | Fix |
|---------|-------|-----|
| Wheel tries to move but gets stuck | Filter too thick (>7mm) or thread too thick (>3mm) | Check filter dimensions |
| Wheel jams | M2 retaining screw too long | Use shorter screws |
| Wheel jams | M42 adapter protrudes into cavity, hitting filter/carousel | Shorten adapter or add spacer |
| Wheel spins but never stops / wrong position | IR position sensor malfunction | Recalibrate via ASCOM driver ("ReCalibrate" button, takes up to 60s) |
| Carousel slipping or blocked error | Unbalanced filter distribution | Distribute filters evenly across positions (e.g., 1, 3, 5 — not 1, 2, 3) |

> Position sensing uses an **infrared sensor**. If positions drift after a firmware update or power issue, recalibrate first before opening the wheel.

---

## Resources

- [ZWO EFW product page](https://www.zwoastro.com/product/efw-filter-wheels/)
- [ZWO EFW manual](https://astronomy-imaging-camera.com/software-drivers)
- [ASIAIR filter wheel guide](https://www.yuque.com/zwopkb/asiair)
- [View into Space review (2026)](https://www.youtube.com/watch?v=OSAaSDsPMk0) — new vs old model comparison

> **Note (2026-04-05):** EFW-5×2-25 temporarily out of stock on the ZWO store.
