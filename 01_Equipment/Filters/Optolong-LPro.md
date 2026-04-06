---
title: "Optolong L-Pro Filter 2''"
type: equipment
category: filter
brand: "Optolong"
model: "L-Pro 2''"
status: active
purchase_date: 2022-10-10
purchase_price: "179.00 €"
purchase_store: "Astroshop"
purchase_url: "https://www.astroshop.eu"
tags:
  - equipment/filter
---

# Optolong L-Pro Filter 2"

Broadband light pollution filter for galaxies, clusters, and reflection nebulae. Blocks artificial light sources while passing the full visible spectrum including nebula emission lines.

- [Optolong product page](https://www.optolong.com/cms/document/detail/id/15.html)

---

## Specifications

| Specification | Value |
|---------------|-------|
| Type | Broadband light pollution filter |
| Frame size | 2" (48mm) |
| Spectrum | 380–750nm |
| Transmission | 95% (in passband) |
| Surface accuracy | 1/4 wavelength |
| Coating | Multi-layer dielectric, anti-reflection |

---

## Passband Characteristics

The L-Pro is a **broadband** filter — it passes most of the visible spectrum while cutting specific artificial light pollution wavelengths.

### What It Blocks

| Light Source | Wavelength | Blocked? |
|-------------|-----------|----------|
| Sodium vapor (LPS) | 589nm | Yes — notch cut |
| Mercury vapor | 546nm | Yes — notch cut |
| Sodium (HPS) broadband | 570–620nm | Partially — wide notch |

### What It Passes

| Signal | Wavelength | Passed? |
|--------|-----------|---------|
| H-alpha (Ha) | 656nm | Yes |
| H-beta (Hb) | 486nm | Yes |
| Oxygen III (OIII) | 496/500nm | Yes |
| Nitrogen II (NII) | 654/658nm | Yes |
| Sulfur II (SII) | 672nm | Yes |
| Broadband starlight | 380–750nm | Yes (except notches) |
| Galaxy continuum | Full visible | Yes (except notches) |

---

## Transmission Charts

![Optolong L-Pro — Transmission Curve](/01_Equipment/Manuals/Optolong-LPro/eb917cc4efb4f6591d2d660c9922c256.jpg)

How to read the chart:
- Horizontal axis: wavelength in nanometers (nm)
- Vertical axis: transmission in %
- **Red line** — filter transmission curve
- **Orange lines** — artificial light pollution emission lines (blocked)
- **Green lines** — nebula emission lines (passed)

![Optolong L-Pro — Detailed Transmission](/01_Equipment/Manuals/Optolong-LPro/0ff2d7f395c427aa390ff53daf333cec.jpg)

---

## Broadband vs Narrowband Comparison

| | Optolong L-Pro (broadband) | [[Antlia-FQuad]] (narrowband) |
|--|---------------------------|-------------------------------|
| Bandpass | 380–750nm with notches | ~5nm at 4 specific lines |
| Light passed | Most visible light | Only Ha, Hb, OIII, SII |
| Star colors | Natural | Muted/monochromatic |
| Background sky | Reduced (notch cuts) | Nearly eliminated |
| Moon tolerance | Moderate — some glow remains | Excellent — nearly immune |
| Color calibration | SPCC works normally | SPCC not applicable |
| Processing | Standard [[RGB-Workflow]] | [[QuadBand-OSC-Workflow]] |

---

## When to Use

| Scenario | Filter |
|----------|--------|
| Galaxies | **L-Pro** — broadband continuum light |
| Star clusters | **L-Pro** — natural star colors |
| Reflection nebulae | **L-Pro** — reflected broadband starlight |
| Mixed fields (galaxy + emission) | **L-Pro** — captures both |
| Emission nebulae (dark sky, no moon) | L-Pro works, but [[Antlia-FQuad]] preferred |
| Emission nebulae (moonlit nights) | [[Antlia-FQuad]] — L-Pro lets too much moonlight through |

### Signal Strength by Target Type

| Target | Performance | Reason |
|--------|-------------|--------|
| Galaxies (M86, NGC4435) | Excellent | Broadband continuum fully passed |
| Star clusters (M13, M44, M5) | Excellent | Full star color spectrum |
| Reflection nebulae (M45) | Excellent | Reflected starlight is broadband |
| Emission nebulae (M42, NGC7000) | Good | Passes emission lines + continuum, but sky glow reduces contrast |
| Planetary nebulae | Moderate | Small, faint; narrowband preferred |

---

## Moon Tolerance

| Moon Phase | Usability with L-Pro |
|------------|---------------------|
| New moon | Excellent |
| Quarter (50%) | Good |
| Gibbous (75%) | Fair — increased sky glow, shorter usable window |
| Full (95%+) | Poor — strong sky background, use [[Antlia-FQuad]] instead |

The L-Pro reduces light pollution but passes moonlight (broadband). For moonlit nights, switch to the [[Antlia-FQuad]] for emission targets.

---

## Performance at Bortle 4 (Tuntange)

At Bortle 4, the L-Pro provides moderate improvement:

| Condition | Without filter | With L-Pro |
|-----------|---------------|------------|
| Sky background | Moderate LP glow | Reduced — sodium/mercury cut |
| Contrast on galaxies | Good | Better — cleaner background |
| Contrast on emission nebulae | Good | Slightly better |
| Star colors | Natural | Natural (minimal color shift) |

At Bortle 4, the benefit is less dramatic than at Bortle 6–8. The filter is most valuable when:
- Imaging toward the horizon (higher LP column)
- Nearby sodium street lights affect the sky
- Targeting faint galaxies where background noise matters

---

## Optical Train Position

```
RedCat 51 → M48 adapter → Optolong L-Pro → spacers → ASI2600MC Pro
```

Same position as the [[Antlia-FQuad]]. Filter thickness must be accounted for in the 59.7mm backfocus distance of the [[RedCat-51]].

---

## Filter Orientation

Filter orientation matters. The filter is asymmetric: one side carries the dichroic (interference) coating that performs the light pollution rejection, the other is anti-reflective (AR) coated.

### The Rule

> **Coated/dichroic side faces the telescope (light source).**
> **Anti-reflective side faces the camera/sensor.**

### Why It Matters

The camera sensor reflects ~5–10% of incoming light. If that reflected light hits the dichroic coating, it bounces back to the sensor and creates **halos and ghost reflections around bright stars** (Vega, Deneb, Sirius, etc.). This is particularly visible on broadband targets like [[M45-Pleiades]] where many bright stars are present.

With the AR side facing the sensor, only ~0.3% of light reflects back — the halo loop is broken.

| Side | Faces | Reflection back to sensor | Effect |
|------|-------|---------------------------|--------|
| Coated (dichroic) | Telescope | — | Filters incoming light correctly |
| Anti-reflective | Camera | ~0.3% | Halos eliminated |

### How to Identify the Coated Side (this specific filter)

Both faces of the L-Pro show colored reflections — visual identification is **not symmetric like narrowband filters**, but the colors differ:

| Side | Dominant color under angled light | Identification |
|------|----------------------------------|----------------|
| **Yellow / gold** (warm sheen) | Reflects sodium (~589nm) and mercury (~546nm) — the wavelengths the filter rejects | **COATED (dichroic)** → faces TELESCOPE |
| **Purple / blue / magenta** (cool sheen) | Residual AR coating reflection in the passband | **AR-coated** → faces CAMERA |

> [!info] Why yellow = coated side
> The L-Pro is a light pollution rejection filter. It blocks sodium-vapor (yellow, 589nm) and mercury-vapor (green-yellow, 546nm). The dichroic coating *reflects* what it rejects — so the surface appearing **yellow under ambient light is reflecting sodium light back at you**. This is the coated face.

### Marking the Filter

Both sides show reflections, so it's easy to forget which is which after handling. Recommended:

1. Mark the **yellow/coated side** with a tiny dot of permanent marker on the **metal cell ring** (never on the glass)
2. Store reference photos of both faces in `01_Equipment/Manuals/Optolong-LPro/`
3. The marked side always faces the telescope

### Installation in the EFW

When mounting in the [[ZWO-EFW-5x2]]:

1. Place the wheel face-down (telescope side down)
2. Screw filter in with the **purple/blue (AR) side facing up** — toward where the camera will mount
3. The yellow (coated) side ends up facing down — toward the telescope when the wheel is installed in the train
4. Verify the marked side faces the telescope before closing the wheel cover

```
   Optical train (L-Pro):
   ══════════════════════
   
   RedCat 51                                    ASI2600MC Pro
       │                                              ▲
       ▼                                              │
   ┌──────────────────────────────────────────────────┐
   │     M48 adapter → spacers → FILTER → spacers     │
   │                              ║║║                 │
   │                          ┌───╨╨╨───┐             │
   │                          │ YELLOW  │ ◄── faces   │
   │                          │  side   │     scope   │
   │                          ├─────────┤             │
   │                          │ PURPLE  │ ◄── faces   │
   │                          │  side   │     camera  │
   │                          └─────────┘             │
   └──────────────────────────────────────────────────┘
```

> [!warning] Symptom of reversed filter
> Faint diffuse halos around bright stars — particularly noticeable on M45 Pleiades, M44 Beehive, and any field with bright stars. If you see these, check filter orientation before blaming optics or processing.

---

## PixInsight Filter Curves

Filter transmission curves for SPFC/SPCC:

| File | Channel |
|------|---------|
| `Curves/OPTOLONG-L-PRO-Light-Pollution.csv` | Gray (full filter) |
| `Curves/Optolong-L-Pro-R.csv` | Red |
| `Curves/Optolong-L-Pro-G.csv` | Green |
| `Curves/Optolong-L-Pro-B.csv` | Blue |

**Also on SSD:** `/Volumes/T7/Astrophotography/Filters/Pi Filter 2024/`

---

## Resources

- [Optolong L-Pro](https://www.optolong.com/cms/document/detail/id/15.html)
