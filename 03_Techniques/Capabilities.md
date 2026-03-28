---
title: "Equipment Capabilities Reference"
type: technique
tags:
  - technique
---

# Equipment Capabilities Reference

Overview of imaging capabilities based on current equipment.

---

## Primary Rig: RedCat 51 + ASI2600MC Pro

| Parameter | Value |
|-----------|-------|
| Resolution | 3.1"/pixel |
| Field of View | ~5.4° x 3.6° |
| Sensor | APS-C, 26MP, 16-bit, cooled (-10°C / -20°C) |
| Image circle | 44mm (full APS-C coverage) |
| Focal ratio | f/4.9 |
| Focal length | 250mm |

### Best For

- Large emission nebulae (Orion, North America, Rosette, Veil, Heart/Soul)
- Wide galaxy group fields (Virgo Cluster, Leo Triplet)
- Large open clusters (Beehive, Double Cluster)
- Milky Way mosaic panels

### Less Suited For

- Small planetary nebulae (Ring, Dumbbell — too small at 250mm)
- Small galaxies (Whirlpool, Pinwheel — workable but small in frame)
- Planets (far too short focal length)

---

## Secondary Rig: NexStar 90SLT + Nikon D5300

| Parameter | Value |
|-----------|-------|
| Resolution | 0.64"/pixel (likely oversampled for typical seeing) |
| Field of View | ~0.28° x 0.19° |
| Focal ratio | f/14 |
| Focal length | 1250mm |

### Best For

- Lunar photography (excellent detail)
- Planetary (Jupiter, Saturn — short exposure / lucky imaging)
- Small bright targets (globular cluster cores, bright planetary nebulae)

### Limitations

- f/14 is extremely slow for deep sky — impractical for faint nebulae
- Alt-azimuth mount cannot track for long exposures (field rotation)
- No sensor cooling on D5300 — more thermal noise in long exposures

---

## Guiding & Tracking

| Capability | Details |
|------------|---------|
| Guided tracking | [[ASI385MC]] + [[UniGuide-32mm]] — multi-minute exposures |
| Mount capacity | [[iOptron-CEM26]] carries 12kg — RedCat rig (~3kg) well under limit |
| Periodic error | <±12" with PEC — manageable with guiding |
| Autofocus | [[ZWO-EAF]] — temperature-compensated focus through the night |
| GoTo | CEM26 with 212,000 objects + plate solving via [[ASIAIR]] |

At 3.1"/pixel, guiding errors under ~3" RMS are acceptable.

---

## Filter Capabilities

| Filter | Type | Best For |
|--------|------|----------|
| [[Antlia-FQuad]] | Narrowband (Ha, OIII, Hb, SII) | Emission nebulae, effective through moonlight |
| [[Optolong-LPro]] | Broadband light pollution | Galaxies, clusters, reflection nebulae |

The Quad Band filter allows imaging **through moonlit nights** — effectively doubling usable nights per month for emission nebulae at a Bortle 4 site.

---

## Sweet Spot

**Wide-field emission nebulae with the Quad Band filter.** The 250mm f/4.9 + cooled 26MP sensor + narrowband filter + guided CEM26 is optimized for large emission targets:

- NGC 7000 (North America Nebula) — 23h integration achieved
- IC 1396 (Elephant's Trunk)
- Sh2-129 (Flying Bat)
- IC 1805 / IC 1848 (Heart & Soul)
- Cygnus Wall region
- Sh2-240 (Simeis 147 — challenging but fits FOV)
- NGC 6960/6992 (Veil Nebula)
- IC 2177 (Seagull Nebula)

---

## Current Limitations

| Limitation | Reason | What Would Unlock It |
|------------|--------|----------------------|
| No narrowband channel separation | Color camera captures all bands simultaneously | Mono camera + dedicated Ha/OIII/SII filters |
| No true LRGB | LRGB workflow requires mono camera for dedicated luminance | Mono camera |
| No SHO palettes | Hubble palette needs separate narrowband channels | Mono camera + narrowband filters |
| No high-resolution deep sky | 250mm only; no long FL option with tracking | Longer focal length scope (500–1000mm) on CEM26 |
| No planetary imaging | RedCat too short, NexStar on alt-az mount | Equatorial mount + Barlow + high-speed camera |
