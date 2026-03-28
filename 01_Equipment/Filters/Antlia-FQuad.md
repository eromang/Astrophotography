---
title: "Antlia Quad Band Filter"
type: equipment
category: filter
brand: "Antlia"
model: "ALP-T Quad Band Filter"
status: active
tags:
  - equipment/filter
---

# Antlia ALP-T Quad Band Filter

Primary narrowband filter for emission nebula imaging. Passes four narrowband wavelengths simultaneously through a single filter, enabling narrowband imaging with the [[ASI2600MCPro]] color camera.

- [Antlia product page](https://www.intl.antliafilter.com/alp-t-quad-band-narrowband-filter)

---

## Specifications

| Specification | Value |
|---------------|-------|
| Type | Quad narrowband (multi-bandpass) |
| Bandpass 1 | H-alpha (Ha) — 656nm |
| Bandpass 2 | H-beta (Hb) — 486nm |
| Bandpass 3 | Oxygen III (OIII) — 496/500nm |
| Bandpass 4 | Sulfur II (SII) — 672nm |
| Bandpass width | ~5nm per line (narrowband) |
| Substrate | Optical glass |
| Coating | Multi-layer dielectric |
| Size | 2" (48mm) or M48 threaded |

---

## Bandpass Distribution on Color Camera

When used with the [[ASI2600MCPro]] (Bayer RGGB sensor), the narrowband signals distribute across the color channels:

| Bayer Channel | Narrowband Signal | Wavelength |
|---------------|-------------------|------------|
| Red | **Ha** + **SII** | 656nm + 672nm |
| Green | **OIII** + **Hb** | 496/500nm + 486nm |
| Blue | **OIII** | 496/500nm |

Ha and SII are only 16nm apart — they **cannot be separated** with a color camera. Both land in the red channel.

OIII appears in both green and blue channels, but is stronger in blue (closer to the blue Bayer filter's peak transmission).

> See [[QuadBand-OSC-Workflow]] for the processing approach specific to this channel distribution.

---

## Why a Quad Band Filter?

### The Problem

A color (OSC) camera cannot use individual narrowband filters (Ha, OIII, SII) like a mono camera can. Each Bayer pixel only sees one color, so a single Ha filter would illuminate only 25% of pixels (the red ones), wasting 75% of the sensor.

### The Solution

The quad band filter passes **all four narrowband lines simultaneously**. Every Bayer pixel receives narrowband light in its color:
- Red pixels see Ha + SII
- Green pixels see OIII + Hb
- Blue pixels see OIII

This is the most efficient way to capture narrowband data with a one-shot color camera.

### Trade-offs vs Mono + Individual Filters

| | Quad Band + OSC | Mono + Individual NB |
|--|-----------------|---------------------|
| Channels separated | No — mixed in Bayer | Yes — one filter per exposure |
| Ha/SII separation | Impossible | Full separation |
| SHO palette | Not possible | Full Hubble palette |
| Data acquisition speed | 1x (single filter) | 3–4x slower (one filter at a time) |
| Hardware complexity | Simple (no filter wheel) | Filter wheel + mono camera |
| Processing complexity | Channel remapping needed | Straightforward channel assignment |
| Cost | Lower | Significantly higher |

---

## Performance

### Moon Tolerance

The narrow ~5nm bandpasses reject nearly all broadband moonlight and light pollution. This filter is effective at:

| Moon Phase | Usability |
|------------|-----------|
| New moon | Excellent |
| Quarter (50%) | Excellent |
| Gibbous (75%) | Good — slight sky glow increase |
| Full (95%+) | Usable — Ha/SII still strong, OIII slightly affected |

This effectively **doubles usable imaging nights per month** compared to broadband-only imaging.

### Light Pollution Rejection

At Bortle 4 (Tuntange), the Quad Band filter blocks:
- Sodium vapor (589nm) — between Ha and OIII, fully rejected
- Mercury vapor (546nm) — between OIII and Ha, fully rejected
- LED broadband — most emission rejected, some leakage possible

### Signal Strength by Target Type

| Target | Ha | OIII | SII | Filter Performance |
|--------|----|----|-----|-------------------|
| Emission nebulae (HII regions) | Strong | Moderate | Moderate | Excellent |
| Planetary nebulae | Moderate | Strong | Weak | Good |
| Supernova remnants | Moderate | Strong | Strong | Excellent |
| Reflection nebulae | None | None | None | Poor — use [[Optolong-LPro]] |
| Galaxies | Very weak | Very weak | None | Poor — use [[Optolong-LPro]] |
| Star clusters | None | None | None | Poor — use [[Optolong-LPro]] |

---

## When to Use

| Scenario | Filter |
|----------|--------|
| Emission nebulae (M42, NGC7000, Rosette, Veil, Heart/Soul) | **Antlia Quad Band** |
| Supernova remnants (Veil, Simeis 147) | **Antlia Quad Band** |
| Any target during moonlit nights | **Antlia Quad Band** |
| Galaxies (M86, NGC4435, Leo Triplet) | [[Optolong-LPro]] |
| Star clusters (M13, M44, M5) | [[Optolong-LPro]] |
| Reflection nebulae (M45 Pleiades) | [[Optolong-LPro]] |

---

## Optical Train Position

The filter sits in the optical train between the telescope and the camera:

```
RedCat 51 → M48 adapter → Antlia Quad Band → spacers → ASI2600MC Pro
```

The filter is part of the backfocus chain — its thickness must be accounted for in the 59.7mm backfocus distance of the [[RedCat-51]].

---

## Color Palettes

With this filter on a color camera, several color palette options are available in processing:

| Palette | Mapping | Look |
|---------|---------|------|
| HOO (natural) | R=Ha, G=OIII, B=OIII | Teal and red — natural appearance |
| Enhanced HOO | R=Ha, G=0.3Ha+0.7OIII, B=OIII | Warmer nebula tones |
| Foraxx | R=Ha, G=max(G,B)×0.9+R×0.1, B=OIII | Popular for OSC narrowband |
| Minimal | Keep original RGB, manual curves | Quickest, least control |

See [[QuadBand-OSC-Workflow]] for detailed PixelMath formulas.

---

## Resources

- [Antlia ALP-T Quad Band Filter](https://www.intl.antliafilter.com/alp-t-quad-band-narrowband-filter)
