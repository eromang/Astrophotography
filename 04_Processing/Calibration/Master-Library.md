---
title: "Calibration Master Library"
type: calibration
created: 2025-03-08
tags:
  - processing/calibration
---

# Calibration Master Library

Full inventory of calibration frames for the [[ASI2600MCPro]] at Gain 100. Covers all exposure/temperature combinations needed by the [[RGB-Workflow]], [[QuadBand-OSC-Workflow]], and [[HDR-Workflow]].

> See [[Calibration-Strategy]] for acquisition procedures and maintenance schedule.

**Storage:** `/Volumes/T7/Astrophotography/Templates/`

---

## Dark Frames

Dark frames must match light frame **exposure + gain + temperature** exactly. Filter-independent (sensor is capped).

**Raw frames:** `/Volumes/T7/Astrophotography/Templates/Dark/`
**Masters:** `/Volumes/T7/Astrophotography/Templates/Masters/Dark/`

### Inventory

| Exposure | Gain | Temp | Raws | Master? | Date | Location | Status |
|----------|------|------|------|---------|------|----------|--------|
| 10ms | g100 | -10°C | — | Yes | — | `Masters/Dark/` | Available |
| 30s | g100 | -10°C | — | Yes | — | `Masters/Dark/` | Available |
| 60s | g100 | -10°C | — | Yes | — | `Masters/Dark/` | Available |
| 120s | g100 | -10°C | — | — | — | — | Needed |
| 120s | g100 | -20°C | — | — | — | — | Needed |
| 160s | g100 | -10°C | 26 | Yes | 2025-03 | `Dark/FQuad/DARK9` | Available |
| 160s | g100 | -20°C | — | — | — | — | Needed |
| 180s | g100 | -10°C | 25 | Yes | 2025-03 | `Dark/FQuad/DARK8` | Available |
| 180s | g100 | -20°C | 20 | No | 2024-12 | `Dark/FQuad/DARK5` | **Incomplete (20/25 raws, no master)** |
| 220s | g100 | -10°C | 25 | Yes | 2025-03 | `Dark/FQuad/DARK7` | Available |
| 220s | g100 | -20°C | — | — | — | — | Needed |
| 300s | g100 | -10°C | — | Yes | — | `Masters/Dark/` | Available |
| 300s | g100 | -20°C | — | — | — | — | **Needed (priority)** |

### Usage Map

| Exposure | Used by | Filter | Workflow |
|----------|---------|--------|----------|
| 120s | Clusters | [[Optolong-LPro]] | [[RGB-Workflow]] |
| 180s | Galaxies | [[Optolong-LPro]] | [[RGB-Workflow]] |
| 300s | Emission nebulae | [[Antlia-FQuad]] | [[QuadBand-OSC-Workflow]] |
| 10ms, 30s, 60s | Short exposures / testing | — | — |
| 160s, 220s | Legacy sessions | Various | Reprocessing only |

### Can be done outside a session: **Yes**

Only requires: capped sensor, matching exposure + gain + temperature. No optical train needed. Shoot on cloudy nights, rainy evenings, or during the day.

---

## Flat Frames

Flat frames must match the **optical train state** of the lights: same scope, filter, focus position, camera rotation.

> **Filter-dependent:** Flats are the only calibration frame that depends on the filter. Each filter produces different vignetting, dust shadows, and illumination patterns. **Flats from one filter cannot be used for another.** Darks, dark flats, and bias are all filter-independent (sensor is capped).

**Raw frames:** `/Volumes/T7/Astrophotography/Templates/Flat/`
**Masters:** `/Volumes/T7/Astrophotography/Templates/Masters/Flat/`

### Inventory

| Filter | Exposure | Gain | Raws | Master? | Date | Location | Status |
|--------|----------|------|------|---------|------|----------|--------|
| No filter | 10ms | g100 | — | Yes | — | `Masters/Flat/` | Available |
| [[Antlia-FQuad]] | 50ms | g100 | 30 | Yes | 2024-12 | `Flat/FLAT5-BIN1-50ms-20-FQuad/` | Available (-20°C session) |
| [[Antlia-FQuad]] | 60ms | g100 | 50 | Yes | 2025-03 | `Flat/FLAT6-BIN1-60ms-10-FQuad/` | Available (-10°C session) |
| [[Optolong-LPro]] | 60ms | g100 | 50 | Yes | 2025-03 | `Flat/FLAT6` (shared dir) | Available |

> **Quad Band flats exist!** Two sets: 50ms from Dec 2024 (-20°C session) and 60ms from Mar 2025 (-10°C session). Master flats in `Masters/Flat/FQuad/`. Revalidate if the optical train has changed since those dates.

### Can be done outside a session: **No**

Must match the exact optical train state (focus, rotation, filter) of the lights. Capture at the end of each session before dismounting, or at twilight with the same setup.

---

## Dark Flat Frames

Dark flats match the **flat frame exposure + gain**. Remove bias and thermal noise from flats. Filter-independent.

**Raw frames:** `/Volumes/T7/Astrophotography/Templates/Dark/FQuad/`
**Masters:** `/Volumes/T7/Astrophotography/Templates/Masters/Dark/FQuad/`

### Inventory

| Exposure | Gain | Raws | Master? | Date | Location | Status |
|----------|------|------|---------|------|----------|--------|
| 50ms | g100 | 20 | Yes | 2024-12 | `Dark/FQuad/DARK6` | Available (matches 50ms FQuad flats) |
| 60ms | g100 | 50 | Yes | 2025-03 | `Dark/FQuad/DARK10` | Available (matches 60ms flats) |

### Can be done outside a session: **Yes**

Only requires: capped sensor, matching flat exposure + gain. Temperature not critical.

---

## Bias Frames

Bias captures read noise only — independent of exposure, temperature, and filter. One master per gain setting.

**Masters:** `/Volumes/T7/Astrophotography/Templates/Masters/Bias/`

### Inventory

| Gain | Exposure | Master? | Date | Location | Status |
|------|----------|---------|------|----------|--------|
| g100 | 1ms | Yes | — | `Masters/Bias/` | Available |
| g100 | 10ms | Yes | — | `Masters/Bias/` | Available |
| g100 | 100ms | Yes | — | `Masters/Bias/FQuad/` | Available |

Multiple bias masters at different base exposures. The 1ms master is the most correct (shortest exposure = purest read noise).

### Can be done outside a session: **Yes**

Only requires: capped sensor, shortest exposure, matching gain. Temperature not critical.

---

## Complete Needs Summary

### Frames to acquire outside sessions (priority order)

| # | Frame | Exposure | Temp | Raws needed | Time | Priority |
|---|-------|----------|------|-------------|------|----------|
| 1 | Dark | 180s | -20°C | **5 more** (have 20, need 25) + stack master | ~15 min | **High** — complete existing set |
| 2 | Dark | 300s | -20°C | 25 | ~140 min | **High** — winter Quad Band sessions |
| 3 | Dark | 120s | -10°C | 25 | ~55 min | Medium — summer cluster sessions |
| 4 | Dark | 120s | -20°C | 25 | ~55 min | Medium — winter cluster sessions |
| 5 | Dark | 160s | -20°C | 25 | ~70 min | Low — legacy reprocessing |
| 6 | Dark | 220s | -20°C | 25 | ~100 min | Low — legacy reprocessing |

**Total time for priority 1–4:** ~4.5 hours

### Frames that are complete

| Frame | Status |
|-------|--------|
| Bias (g100, multiple masters) | Complete |
| Dark flat 50ms (g100) | Complete |
| Dark flat 60ms (g100) | Complete |
| Dark 160s, -10°C | Complete (master + 26 raws) |
| Dark 180s, -10°C | Complete (master + 25 raws) |
| Dark 220s, -10°C | Complete (master + 25 raws) |
| Dark 300s, -10°C | Complete (master) |
| Dark 10ms, 30s, 60s, -10°C | Complete (masters) |
| Flat [[Antlia-FQuad]] 50ms | Complete (30 raws + master, Dec 2024) |
| Flat [[Antlia-FQuad]] 60ms | Complete (50 raws + master, Mar 2025) |
| Flat [[Optolong-LPro]] 60ms | Complete (50 raws + master, Mar 2025) |

---

## Additional SSD Resources

| Resource | Location | Purpose |
|----------|----------|---------|
| MARS DR1 database | `/Volumes/T7/Astrophotography/XMARS/MARS-DR1-1.1.1.xmars` | MGC gradient correction |
| MARS-U database | `/Volumes/T7/Astrophotography/XMARS/MARS-DR1-u01-1.0.1.xmars` | MGC (user contributed) |
| Gaia DR3/SP catalog | `/Volumes/T7/Astrophotography/Gaia DR3:SP (complete set)/` (20 files) | SPCC/SPFC astrometry |
| Antlia Quadband filter curves | `/Volumes/T7/Astrophotography/Filters/Antlia Quadband PI filters/` | SPFC/SPCC combined curves |
| PixInsight processing templates | `/Volumes/T7/Astrophotography/Templates/PixInsight_templates/` | WBPP folder structure |
| Siril processing templates | `/Volumes/T7/Astrophotography/Templates/Siril_templates/` | Siril folder structure |

---

## Notes

- All frames shot with [[ASI2600MCPro]] at Gain 100
- Dark frames must match light frame temperature and exposure exactly — filter is irrelevant
- Flat frames must match the exact optical train (scope + filter + focus + rotation)
- Each filter requires its own flat set — [[Antlia-FQuad]] and [[Optolong-LPro]] are not interchangeable
- "FQuad" in folder names is organizational only — darks in those folders are filter-independent
- See [[Calibration-Strategy]] for acquisition procedures and maintenance schedule
