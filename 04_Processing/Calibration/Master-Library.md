---
title: "Calibration Master Library"
type: calibration
created: 2025-03-08
tags:
  - processing/calibration
---

# Calibration Master Library

Full inventory of calibration frames for the [[ASI2600MCPro]] at Gain 100. Covers all exposure/temperature combinations needed by the [[RGB-Workflow]], [[OpenCluster-Workflow]], [[QuadBand-OSC-Workflow]], and [[HDR-Workflow]].

> See [[Calibration-Strategy]] for acquisition procedures and maintenance schedule.

> **Reorganized 2026-05-31** to reflect the filter-independence principle (below): **Bias / Dark / Dark-Flat are filter-independent → filed by type only; Flats are filter-dependent → filed by filter.** The old `Bias/FQuad/` and `Dark/FQuad/` subfolders (filter-independent frames misfiled under a filter name) are gone. Historical session notes that reference the old paths are left as-is.

**Storage root:** `/Volumes/T7/Astrophotography/Templates/`

```
Templates/
├── Masters/
│   ├── Bias/        ← filter-independent (0.0 / 1.0 / 10 / 100 ms)
│   ├── Dark/        ← filter-independent (30 / 60 / 120 / 160 / 180 / 220 / 300 s)
│   ├── DarkFlat/    ← filter-independent (10 / 50 / 60 ms)
│   └── Flat/        ← filter-DEPENDENT, by filter:
│       ├── LPro/        (60 ms)
│       ├── FQuad/       (50 ms, 60 ms)
│       └── NoFilter/    (10 ms)
├── Bias/        ← raw, filter-independent (BIAS1–3, exposure-named)
├── Dark/        ← raw, filter-independent (DARK2/3/4/7/8/9/11)  + _deprecated/ (−20 °C)
├── DarkFlat/    ← raw, filter-independent (DARK1/6/10)
└── Flat/        ← raw, by filter: LPro/  FQuad/(FLAT5,6)  NoFilter/(FLAT1,2,3)
```

---

## The filter-independence rule (why the structure is shaped this way)

| Frame | Filter-dependent? | Must match | Filed by |
|-------|-------------------|-----------|----------|
| **Bias** | ❌ No | gain | type |
| **Dark** | ❌ No | exposure + gain + **temperature** | type |
| **Dark Flat** | ❌ No | flat exposure + gain | type |
| **Flat** | ✅ **Yes** | filter + exact optical train | **filter** |

Bias, darks, and dark-flats are shot with the **sensor capped** — no light reaches it, so the filter in the train is irrelevant. **Flats are the only frame shot with light through the optical train**, so each filter's vignetting / dust shadows / transmission are baked in: **flats from one filter cannot be used for another.**

---

## Dark Frames

Filter-independent. Must match light frame **exposure + gain + temperature** exactly.

**Raw:** `Templates/Dark/`  ·  **Masters:** `Templates/Masters/Dark/`

| Exposure | Gain | Temp | Raws | Master | Raw folder | Status |
|----------|------|------|------|--------|-----------|--------|
| 30 s | g100 | −10 °C | — | ✅ | — | Available |
| 60 s | g100 | −10 °C | 50 | ✅ | `Dark/DARK3-BIN1-60s-10/` | Available |
| 120 s | g100 | −10 °C | 25 | ✅ | `Dark/DARK11-BIN1-120s-10/` | Available (2026-04-19) |
| 160 s | g100 | −10 °C | 10 | ✅ | `Dark/DARK9-BIN1-160s-10/` | Available |
| 180 s | g100 | −10 °C | 10 | ✅ | `Dark/DARK8-BIN1-180s-10/` | Available |
| 220 s | g100 | −10 °C | 10 | ✅ | `Dark/DARK7-BIN1-220s-10/` | Available |
| 300 s | g100 | −10 °C | 50 | ✅ | `Dark/DARK4-BIN1-300s-10/` | Available |
| 180 s | g100 | −20 °C | 20 | — | `Dark/_deprecated/DARK5-BIN1-180s-20/` | **Deprecated** (−20 °C, no master) |

> **Cooling standard (2026-04-19):** standardized on **−10 °C year-round** — see [[ASIAIR]] camera profile. −20 °C frames are kept under `Dark/_deprecated/` for legacy reprocessing only and won't be refreshed.

### Usage map

| Exposure | Used by | Filter | Workflow |
|----------|---------|--------|----------|
| 120 s | Clusters | [[Optolong-LPro]] | [[OpenCluster-Workflow]] |
| 180 s | Galaxies | [[Optolong-LPro]] | [[RGB-Workflow]] |
| 300 s | Emission nebulae | [[Antlia-FQuad]] | [[QuadBand-OSC-Workflow]] |
| 30 s / 60 s | Short / testing | — | — |
| 160 s / 220 s | Legacy sessions | various | reprocessing only |

**Can be shot outside a session: Yes** — capped sensor + matching exposure/gain/temperature. No optical train needed.

---

## Dark Flat Frames

Filter-independent. Match the **flat exposure + gain** (temperature not critical).

**Raw:** `Templates/DarkFlat/`  ·  **Masters:** `Templates/Masters/DarkFlat/`

| Exposure | Gain | Raws | Master | Raw folder | Pairs with |
|----------|------|------|--------|-----------|-----------|
| 10 ms | g100 | 10 | ✅ | `DarkFlat/DARK1-BIN1-10ms-10/` | 10 ms flats |
| 50 ms | g100 | 29 | ✅ | `DarkFlat/DARK6-BIN1-50ms-20/` | 50 ms FQuad flats |
| 60 ms | g100 | 50 | ✅ | `DarkFlat/DARK10-BIN1-60ms-10/` | 60 ms flats (L-Pro / FQuad) |

**Can be shot outside a session: Yes.**

---

## Bias Frames

Filter-independent. Read noise only — independent of exposure, temperature, and filter. One master per base exposure.

**Raw:** `Templates/Bias/`  ·  **Masters:** `Templates/Masters/Bias/`

| Exposure | Gain | Master | Raw folder(s) | Notes |
|----------|------|--------|--------------|-------|
| 0.0 ms | g100 | ✅ | — | True 0-exposure bias (Dec 2024) — purest read noise |
| 1 ms | g100 | ✅ | `Bias/BIAS1-BIN1-1ms-10/`, `BIAS1-BIN1-1ms-20/`, `BIAS2-BIN1-1ms-10/` | Recommended default |
| 10 ms | g100 | ✅ | `Bias/BIAS2-BIN1-10ms-10/` | |
| 100 ms | g100 | ✅ | `Bias/BIAS3-BIN1-100ms-10/` | |

> A duplicate 100 ms bias master (formerly `Bias/FQuad/`) was MD5-verified identical and removed in the 2026-05-31 reorg.

**Can be shot outside a session: Yes.**

---

## Flat Frames

**Filter-dependent — the only calibration frame that is.** Each filter needs its own set; they are not interchangeable. Must match the **exact optical train** (scope, filter, focus, rotation) of the lights.

**Raw:** `Templates/Flat/{LPro,FQuad,NoFilter}/`  ·  **Masters:** `Templates/Masters/Flat/{LPro,FQuad,NoFilter}/`

| Filter | Exposure | Temp | Raws | Master | Raw folder |
|--------|----------|------|------|--------|-----------|
| [[Optolong-LPro]] | 10 ms | −10 °C | 50 | ⏳ **raws shot 2026-05-31 — master to build** | `Flat/LPro/FLAT7-BIN1-10ms-10/` |
| [[Antlia-FQuad]] | 50 ms | −20 °C | 60 | ✅ `Flat/FQuad/masterFlat_…FILTER-FQuad_CFA_FLAT-50ms.xisf` | `Flat/FQuad/FLAT5-BIN1-50ms-20/` |
| [[Antlia-FQuad]] | 60 ms | −10 °C | 50 | ✅ `Flat/FQuad/masterFlat_…FILTER-FQuad_CFA_FLAT-60ms.xisf` | `Flat/FQuad/FLAT6-BIN1-60ms-10/` |
| No filter | 10 ms | — | 150 | ✅ `Flat/NoFilter/masterFlat_…FILTER-NoFilter_CFA_FLAT-10ms.xisf` | `Flat/NoFilter/FLAT1-BIN1-10ms-10/` |
| No filter | 20 ms / 100 ms | — | 9 / 30 | — | `Flat/NoFilter/FLAT2…/`, `FLAT3…/` |

> **Two distinct FQuad flat sets** (50 ms Dec 2024 −20 °C, 60 ms Mar 2025 −10 °C). The 60 ms master was formerly the misnamed `…CFA copy.xisf` — confirmed a separate flat, not a duplicate, and renamed in the reorg.
>
> ⚠️ **FQuad flat filenames still read `FILTER-NoFilter` *inside* the XISF** (manual-filter blank-keyword quirk — the file was renamed to `FILTER-FQuad`, but the internal keyword wasn't edited). WBPP matches by header, so it treats them as `NoFilter`; this is harmless because the FQuad lights also carry a blank keyword and match. The folder (`Flat/FQuad/`) is the authoritative filter marker.
>
> 🚩 **L-Pro flat provenance — RESOLVED 2026-05-31: there is no genuine L-Pro flat.** The "L-Pro 60 ms master" was built from the **`FLAT6` raws, which are FQuad flats** (shot 2025-03-08 through the Quad Band filter — the [[2025-03-08-Processing]] session was FQuad-only: *"Flat frames avec FQuad — 60 ms"*). Proof: the L-Pro master's internal `DATE-OBS` (`2025-03-08T19:02:36.688`) is **identical** to both the FQuad 60 ms master and the FLAT6 raw frames — same source data, just integrated twice and one copy **mislabeled `L-Pro`**. No L-Pro-tagged raw flat folder exists anywhere on T7.
>
> **Implication:** every L-Pro session calibrated with the old master ([[Mel111-Coma|Mel 111]], the 2026-04 galaxy/NGC 7000 L-Pro work) was flat-calibrated with **FQuad flats** — mis-correcting the L-Pro filter's own dust/reflections. The mislabeled relabel master was **deleted 2026-05-31**.
>
> ✅ **Genuine L-Pro flats shot 2026-05-31** (50 × **10 ms**, −10 °C, gain 100, flat panel) → `Flat/LPro/FLAT7-BIN1-10ms-10/`. **Master still to build** in WBPP (flats + the 10 ms dark-flat master → `Masters/Flat/LPro/`). ⚠️ The raws' FITS `FILTER` keyword is **absent** (manual filter — `LPro` is in the filename only), so WBPP will name the master `FILTER-NoFilter` → **rename to `…FILTER-LPro_CFA_FLAT-10ms.xisf`** after building. Re-stacking [[Mel111-Coma|Mel 111]] with the real L-Pro flat is the candidate fix for the residual γ Com halo.

**Can be shot outside a session: No** — must match the exact optical train.

---

## Complete Needs Summary

Darks, dark-flats, and bias are complete. **L-Pro flats now shot (2026-05-31) — master just needs building.** All standard dark sub lengths (10 ms, 30 s, 60 s, 120 s, 160 s, 180 s, 220 s, 300 s) have masters.

| Frame                                    | Status                                                                          |
| ---------------------------------------- | ------------------------------------------------------------------------------- |
| Bias (0.0 / 1 / 10 / 100 ms)             | Complete                                                                        |
| Dark-flats (10 / 50 / 60 ms)             | Complete                                                                        |
| Darks 30 s … 300 s, −10 °C               | Complete                                                                        |
| Flats — FQuad 50 + 60 ms, NoFilter 10 ms | Complete                                                                        |
| Flat — **L-Pro 10 ms**                   | ⏳ **Raws shot** 2026-05-31 (50 × 10 ms, `Flat/LPro/FLAT7…`) — **build the master** (flats + 10 ms dark-flat → `Masters/Flat/LPro/`, rename to FILTER-LPro) |

---

## Additional SSD Resources

| Resource | Location | Purpose |
|----------|----------|---------|
| MARS DR1 database | `/Volumes/T7/Astrophotography/XMARS/MARS-DR1-1.1.1.xmars` | MGC gradient correction |
| MARS-U database | `/Volumes/T7/Astrophotography/XMARS/MARS-DR1-u01-1.0.1.xmars` | MGC (user contributed) |
| Gaia DR3/SP catalog | `/Volumes/T7/Astrophotography/Gaia DR3:SP (complete set)/` | SPCC/SPFC |
| Antlia Quadband filter curves | `/Volumes/T7/Astrophotography/Filters/Antlia Quadband PI filters/` | SPFC/SPCC |
| PixInsight templates | `/Volumes/T7/Astrophotography/Templates/PixInsight_templates/` | WBPP folder structure |
| Siril templates | `/Volumes/T7/Astrophotography/Templates/Siril_templates/` | Siril folder structure |

---

## Notes

- All frames shot with [[ASI2600MCPro]] at Gain 100.
- **Filing rule:** Bias / Dark / Dark-Flat by **type** (filter-independent); Flat by **filter**. Do not re-introduce filter subfolders under Bias/Dark/DarkFlat.
- **WBPP rebuilds re-emit default names** (`_DARK-` suffix on darks; `FILTER-NoFilter` for blank-keyword filters). After a rebuild, re-file the master into the right type/filter folder and rename to match this convention. Better: set the filter label in the ASIAIR capture plan so the keyword is populated at the source.
- Darks must match light **temperature** and exposure exactly — filter irrelevant.
- See [[Calibration-Strategy]] for acquisition procedures and maintenance schedule.
