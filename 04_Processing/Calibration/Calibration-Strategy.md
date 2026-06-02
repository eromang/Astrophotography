---
title: "Calibration Strategy"
type: calibration
tags:
  - processing/calibration
---

# Calibration Strategy

Strategy for building and maintaining the [[Master-Library]] for the [[ASI2600MCPro]] at Gain 100.

---

## Frame Independence

Not all calibration frames require an imaging session. Some can be generated anytime.

| Frame | Session required? | Dependencies | Shelf life |
|---|---|---|---|
| **Dark** | No | Exposure + gain + temperature | Indefinite (if camera unchanged) |
| **Bias** | No | Gain only | Indefinite |
| **Dark flat** | No | Flat exposure + gain | Indefinite |
| **Flat** | **Yes** | Optical train state (focus, rotation, filter) | Until optical train changes |

---

## Filter Dependency

Only one calibration frame type depends on the filter:

| Frame | Filter-dependent? | Reason |
|---|---|---|
| **Flat** | **Yes** | Each filter has different thickness, coating, dust pattern, and vignetting profile. Flats from one filter are **not** interchangeable with another. |
| Dark | No | Sensor is capped — no light passes through any filter. |
| Dark flat | No | Sensor is capped — matches flat exposure timing only. |
| Bias | No | Purely electronic read noise — no optical path involved. |

> **Critical:** The [[Antlia-FQuad]] and [[Optolong-LPro]] require separate flat sets. Using L-Pro flats for Quad Band data introduces incorrect vignetting correction — the two filters have different optical properties.

> **Folder structure (T7, reorganized 2026-05-31):** this rule is now reflected on disk — Bias / Dark / Dark-Flat are filed **by type** (no filter subfolders), Flats **by filter** (`Flat/{LPro,FQuad,NoFilter}/`). Full layout in [[Master-Library]].

> **FITS FILTER keyword fix:** with manual filters (no EFW) the ASIAIR leaves the FITS `FILTER` keyword blank — only the filename carries the filter — so WBPP can't auto-match flats and you must hand-load one flat at a time. **Run `python3 scripts/set_filter.py <folder> --apply` on the lights + flats before WBPP** to write `FILTER` from the filename token; WBPP then groups flats by filter automatically. Data-preserving (header-only edit). See `scripts/README.md`.

---

## Dark Frame Library Plan

Darks are the highest-value frames to pre-build: time-consuming (25 × exposure per set) and completely independent of the optical train. Shoot on any cloudy night, rainy evening, or during the day with the lens cap on.

### Target Matrix (Gain 100, -10°C year-round)

| Exposure | Use case | Status |
|---|---|---|
| 120s | Clusters / bright Quad targets ([[Optolong-LPro]] / [[Antlia-FQuad]]) | ✅ Have 25 (built 2026-04-19) |
| 160s | Legacy reprocessing | ✅ Have 26 |
| 180s | Galaxies ([[Optolong-LPro]]) / shoulder Quad | ✅ Have 25 |
| 220s | Legacy reprocessing | ✅ Have 25 |
| 300s | Emission nebulae ([[Antlia-FQuad]]) | ✅ Have master |

> **Cooling standard (2026-04-19):** Standardized on **-10°C year-round** — see [[ASIAIR]] camera profile for rationale. At Bortle 4 the dark-current penalty vs -20°C is below the sky-noise floor; the operational simplicity of a single dark library wins. -20°C entries in [[Master-Library]] are kept for legacy reprocessing only and will not be refreshed.

### Status

Dark library is **complete** for all standard sub lengths (10ms, 30s, 60s, 120s, 160s, 180s, 220s, 300s) at -10°C / Gain 100. No outstanding captures needed under the current cooling standard.

### Time Estimates (for reference / future re-shoots)

| Set | Frames | Time |
|---|---|---|
| 25 × 120s | 25 | ~55 min |
| 25 × 180s | 25 | ~85 min |
| 25 × 300s | 25 | ~140 min |

### Procedure

1. Cap the telescope (or disconnect camera and use body cap)
2. Set ASIAIR to the target temperature (-10°C or -20°C) and wait for stabilization
3. Set exposure and gain to match the target combination
4. Capture 25 frames
5. Move to next exposure/temperature combination
6. Stack in WBPP to create master dark
7. Update [[Master-Library]] with new entries

> **Tip:** Batch multiple dark sets in one session. Start with the longest exposure (300s) while the camera is already cooled, then work down to shorter exposures.

---

## Bias Frames

One master bias at Gain 100 is sufficient — bias does not change with exposure or temperature. The current master is adequate.

**When to reshoot:**
- After a firmware update to the camera
- If noise patterns change (unlikely with cooled CMOS)
- If the current master was made with fewer than 50 frames (reshoot with 100 for cleaner master)

---

## Dark Flat Frames

Current 60ms dark flats at Gain 100 are good. Only reshoot if the flat exposure time changes.

**When to reshoot:**
- If switching to a different flat panel or method that requires a different exposure
- If gain changes (unlikely — fixed at 100)

---

## Flat Frames

Cannot be pre-built — must match the exact optical train state of the lights.

### When Flats Are Valid

Flats remain valid as long as **nothing changes** in the optical train:
- Same telescope + camera combination
- Same filter in the same position
- Same focus position (do not refocus between lights and flats)
- Same camera rotation angle

### Recommended Strategy

**Per session:** Capture flats at the end of each imaging session before dismounting:
- 50 frames per filter used that night
- Use ASIAIR's auto-flat function or a flat panel
- Flat exposure: auto-adjusted to histogram peak at ~40–50%

**Reuse across sessions:** If the optical train is undisturbed between sessions (e.g., permanent setup), flats from a previous session remain valid. Mark in session notes whether the train was changed.

### Per-Filter Flat Status

| Filter | Flat available? | Notes |
|---|---|---|
| [[Optolong-LPro]] | ✅ 10 ms master (2026-05-31, **0° rotation**) | First genuine L-Pro flat — shot + built 2026-05-31 (the old "L-Pro master" was a mislabeled FQuad flat, deleted). `Masters/Flat/LPro/`. 0°-rotation flat → matches 0° captures only. |
| [[Antlia-FQuad]] | 50ms master (2024-12) + 60ms master (2025-03) | Two sets available — verify still valid if train changed |

> **Important:** Each filter requires its own flat set. The Quad Band and L-Pro filters have different thicknesses and coatings, producing different vignetting and dust shadow patterns.

> [!success] L-Pro flat — done (2026-05-31), Mel 111 re-stacked (2026-06-01)
> All three filters now have flat masters. The L-Pro flat was shot at **0° camera rotation**; [[Mel111-Coma]] was also captured at **0°**, so the dust-shadow correction is an **exact match**. Mel 111 **re-stacked 2026-06-01** with it (drizzle 2×, 4/4 solved) → **γ Com halo resolved** (was an uncorrected L-Pro filter reflection). See [[2026-06-01-Processing]].
>
> ⚠️ **0°-rotation flat — validity is rotation-specific.** Dust shadows rotate with the camera, so this flat only cleanly corrects L-Pro lights also shot at 0°. Other L-Pro captures at different rotations need their own flat (or accept imperfect dust correction) — relevant to any L-Pro reprocessing candidate.

---

## Master Library Maintenance

### After Each Dark Session

1. Stack new darks in WBPP → master dark
2. Store master in calibration folder
3. Update the [[Master-Library]] table with: exposure, gain, temperature, count, date

### Seasonal Review

At the start of each season (April for summer, October for winter):
- Verify dark masters exist for the target temperature
- Check which exposure times are planned (session planner defaults)
- Build any missing dark sets before the first clear night

### Annual Review

Once per year:
- Reshoot bias (100 frames) if older than 2 years
- Verify flat dark matches current flat exposure
- Consider reshooting darks if camera behavior has changed (firmware, hardware service)
