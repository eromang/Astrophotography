---
title: "2026-06-28 Processing Session — NGC 7000 reprocess"
type: processing-session
date: 2026-06-28
software: "PixInsight"
targets_processed:
  - "[[NGC7000-North-America]]"
tags:
  - session/processing
  - processing/pixinsight
---

# 2026-06-28 — NGC 7000 reprocess (24h L-Pro)

Full reprocess of [[NGC7000-North-America]] — **Priority A** in [[Reprocessing-Plan]]. All prior passes (2025-03 → 2026-04) predate the **BlurX Correct-only → SPCC → Sharpen split** and **Multiscale Adaptive Stretch**, so a clean run with the current [[RGB-Workflow]] is the best ROI in the vault.

> [!info] Working folder (prepared 2026-06-28)
> `/Users/ericromang/Desktop/Astro/NGC7000_Reprocess/`
> - `Lights/` — **288** SFS-accepted subs (`*_a.xisf`), copied from the 8 night folders on T7. **Now stamped `FILTER = LPro`** (verified with `frame_info.py`; raw lights were cleaned from T7 — these `_a.xisf` are the only surviving lights).
> - `Masters/` — `masterDark 300s`, `masterFlat LPro 10ms`, `masterDarkFlat 0.01s`, `masterBias 0.0ms` (copied from `T7/Templates/Masters/`).

## Objects Processed

### NGC 7000 — North America Nebula

- **Lights:** 288 (SFS-accepted, 8 nights 2024-07-29 → 2024-09-28)
- **Exposure:** 300s × 288 = 86 400s (**24.0h**)
- **Filter:** [[Optolong-LPro]] (`LPro`, freshly stamped)
- **Gain:** 100
- **Temperature:** ⚠️ **mixed** — see gotcha below

#### Subs per night / temperature

| Night | Date | Subs | Temp |
|---|---|---|---|
| 1 | 2024-07-29 | 9 | **−19.6 °C** |
| 3 | 2024-08-05 | 32 | **−16.8 °C** |
| 4 | 2024-08-13 | 33 | −9.8 °C |
| 5 | 2024-08-26 | 60 | −9.8 °C |
| 6 | 2024-08-27 | 26 | −9.9 °C |
| 7 | 2024-08-28 | 57 | −9.9 °C |
| 8 | 2024-08-29 | 54 | −9.8 °C |
| 9 | 2024-09-28 | 17 | −10.0 °C |

#### Workflow Applied — checklist

**Phase 0 — pre-flight ([[Capture-Planning-Rules]] / [[WBPP-Reference]])**
- [ ] 🔴 **Verify Image Solver pixel size = 3.76 µm BEFORE launching WBPP** — WBPP silently resets it to 1.88 after each run → per-frame solver fails ("1 solved, 3 failed"). The single toggle that actually breaks astrometry.
- [ ] Confirm lights regroup under **`LPro`** (not `NoFilter`) on the Calibration tab — they're stamped now, but **Clear + re-add** the Lights tab if WBPP cached old metadata.

**Phase 1 — WBPP** ([[RGB-Workflow#WBPP (Weighted Batch Pre-Processing)]])
- [ ] Calibration: Dark `masterDark 300s`, Flat `masterFlat LPro 10ms`, Bias/DarkFlat `masterDarkFlat 0.01s` + `masterBias 0.0ms`
- [ ] Master Dark **Optimize = OFF** (mixed-temp handling — see detailed section below)
- [ ] Cosmetic Correction: **Automatic, Hot σ 3.0 · Cold σ 3.0** (tightened for the 41 cold subs) · DeBayer **VNG**
- [ ] Drizzle **2×**, Drop shrink 0.90, Function Square
- [ ] Subframe Weighting: PSF Signal Weight · Image Registration + **Distortion Correction** (4000 spline pts) · Local Normalization ON
- [ ] Integration: Winsorized Sigma Clipping, Sigma High 1.9, Large-Scale rejection High (layers 2, growth 2)
- [ ] Astrometric: Focal 250 mm, **Pixel 3.76 µm**, Force values **unchecked**

**Phase 2 — Linear** ([[RGB-Workflow]], corrected order)
- [ ] Gradient Correction (or GraXpert / SPFC+MGC) + BackgroundNeutralization
- [ ] **BlurXTerminator — Correct Only**
- [ ] ImageSolver (1.88 µm for the Drizzle-2× master; astrometric Gaia DR3 catalog)
- [ ] FindBackground → **SPCC** (L-Pro, G2V) → AutoStretch verify
- [ ] **BlurXTerminator — Sharpen** (PSF measured on the Correct-Only output)
- [ ] StarXTerminator (Unscreen OFF, keep star image) → NoiseXTerminator on starless

**Phase 3 — Non-linear**
- [ ] **Multiscale Adaptive Stretch** (Option A) on the starless
- [ ] BN → NoiseX (light) → CurvesTransformation (G cast, Ha boost)
- [ ] Stars: ArcsinhStretch → screen-blend reintegrate (`~(~starless*~stars)`)
- [ ] LHE / final, ICCProfileTransformation → sRGB

#### Result Notes

-

## Calibration Frames Used

| Frame | Master | Status |
|---|---|---|
| Dark 300s | `masterDark_..._EXPOSURE-300.00s` | ✅ no temp keyword → assumed −10 °C; Optimize OFF (see mixed-temp section) |
| Flat L-Pro | `masterFlat_..._FILTER-LPro_..._10ms` | ✅ matches stamped lights |
| Dark-Flat 10ms | `masterDarkFlat_..._0.01s` | ✅ |
| Bias | `masterBias_..._0.0ms` | ✅ |

## Notes

### 🔴 Mixed-temperature darks — WBPP settings

Only one `masterDark 300s` exists, with **no temperature keyword** (`frame_info` → `Temp None`) → assumed **−10 °C** (the year-round cooling standard, and 247/288 subs are at −10). The **41 cold subs** (Night 1 −19.6 °C, Night 3 −16.8 °C) are the mismatch: a −10 dark has *more* dark current / hot-pixel signal than a colder sub needs → it **over-subtracts** (leaves dark "holes" at hot-pixel sites).

> **CMOS note:** dark *optimization* (dark scaling) is a CCD-era technique. On the ASI2600 (cooled CMOS, very low dark current, hot-pixel-dominated dark at 300s) it can inject noise and its assumptions break down. **Cosmetic Correction is the right tool here, not optimization.**

**✅ Option A (recommended) — no optimization + Cosmetic Correction**
- Master Dark `300s`, **Optimize = OFF** (plain Calibrate).
- **Cosmetic Correction: Automatic** (uses the master dark to detect defects), **Hot σ 3.0 · Cold σ 3.0** — tighter than default; this is what catches residual hot pixels *and* the over-subtraction holes on the cold subs.
- Integration safety net: Winsorized Sigma Clipping, **Sigma High 1.9 · Sigma Low ~2.5–3.0** (rejects the cold-sub dark holes). With 288 frames the few mis-calibrated pixels are rejected anyway.
- Rationale: only 41/288 subs affected, CMOS low dark current → triple safety net (CC → integration rejection → low relative weight).

**Option B — dark optimization ON** (only if curious): Master Dark → Optimize ON, threshold ~3.0 (lower = more aggressive). Needs the separate bias (present). ⚠️ Watch for added noise on the cold subs vs Option A (blink-compare).

**Option C — isolate/exclude the cold nights** (cleanest if artifacts appear): exclude **Night 1 + Night 3** (−3.4h → keeps **20.6h** perfectly temp-matched at −10), or process them as a separate calibration group and compare.

**Order of battle:** start with **A** → after calibration, **blink the calibrated Night 1/3 subs**; if dark holes / residual hot pixels show → switch to **C** (exclude). Only try B out of curiosity.
- Lights are the **SFS-accepted `_a.xisf`** (raw lights cleaned from T7). They already passed SubFrameSelector, so a second SFS pass is optional — WBPP can weight them directly.
- This is also the future **HORGB** base ([[RGB-Narrowband-Combine-Workflow]]) once a Quad Band night is added — keep the L-Pro master.
