---
title: "Optolong L-Pro Filter 2''"
type: equipment
category: filter
brand: "Optolong"
model: "L-Pro 2''"
status: active
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

## Resources

- [Optolong L-Pro](https://www.optolong.com/cms/document/detail/id/15.html)
