---
title: "Reprocessing Plan"
type: processing-workflow
tags:
  - processing/pixinsight
---

# Reprocessing Plan

Targets with existing data that would benefit from reprocessing with the current PI 1.9 workflows. Ranked by expected improvement.

---

## New priorities (2026-06-28) — promoted by recent workflow gains

> Promoted from *Not Worth Reprocessing* because three improvements now postdate their last processing: the **BlurX Correct-only → SPCC → Sharpen split** ([[RGB-Workflow]] / [[QuadBand-OSC-Workflow]]), **Multiscale Adaptive Stretch**, and **DBXtract** (clean Ha/OIII without manual crosstalk). Capture inventory verified against the T7 archive 2026-06-28.

### ⭐ Priority A: NGC 7000 — Full reprocess (biggest dataset)

**Effort:** Medium-High | **Gain:** High — 24h of L-Pro under a pre-June-2026 workflow

[[NGC7000-North-America]] — **~24h L-Pro** (8 nights, 2024-07→09, 300s, g100, mostly −10 °C). All 9 prior passes (2025-03 → 2026-04) predate the BlurX/SPCC split and Multiscale Adaptive Stretch. Best ROI of any target.

- **SSD:** `/Volumes/T7/Astrophotography/Objects/Nebuleuses/ASI2600MC-REDCAT51/NGC_7000_North_America_Nebula/2024/`
- Steps: WBPP (Drizzle 2) → [[RGB-Workflow]] linear with **Correct-only → SPCC → Sharpen** order → **Multiscale Adaptive Stretch** → final.
- 🟢 **Future HORGB anchor:** L-Pro only today. Once a Quad Band night is added, this becomes the prime [[RGB-Narrowband-Combine-Workflow]] (HORGB) target — natural RGB stars + Ha/OIII boost.

### Priority B: NGC 2244 Rosette — first proper dual-band process

**Effort:** Low-Medium | **Gain:** Medium — emission target, never run through the OSC2/DBXtract path

[[NGC2244-Rosette]] — **Quad Band, 1 night** (2025-03-02, 220s, g100, −10 °C). Strong Ha + OIII (the OSC5 reference target). Modest integration → result will be decent, not deep.

- **SSD:** `/Volumes/T7/Astrophotography/Objects/Nebuleuses/ASI2600MC-REDCAT51/NGC2244_Rosetta_Nebula/2025/Night_1_20250302-g100-220s-10-FQuad/`
- Steps: WBPP → [[QuadBand-OSC-Workflow]] linear (SPCC star-full) → **DBXtract** (3.1 Option A) → PPP/HOO → **Multiscale Adaptive Stretch** → final. Good candidate to validate the DBXtract integration.

### Priority C: M45 Pleiades — best-effort reprocess (filter caveat)

**Effort:** Low | **Gain:** Low-Medium — limited by a filter mismatch

[[M45-Pleiades]] — **Quad Band, 2 nights** (2024-12-26/27, 180s, −20 °C). ⚠️ M45 is a **reflection** nebula: the Quad Band passes Ha but **blocks the blue continuum** that *is* the Pleiades nebulosity → reprocessing can't recover what the filter didn't transmit.

- **SSD:** `/Volumes/T7/Astrophotography/Objects/Nebuleuses/ASI2600MC-REDCAT51/M45_Pleiades/2024/`
- Steps: WBPP → current tools (BlurX/NoiseX/StarX + MAS) for a cleaner stars+dust rendition; keep expectations modest.
- 🔴 **Real fix = recapture in [[Optolong-LPro]]** (broadband) — the reflection nebulosity needs the blue. Log an L-Pro session in the plan.

---

## ~~Priority 1: M13~~ — Demoted (duplicate data)

> [!warning] SFS analysis confirmed all 3 night folders contain the **same 25 frames** from 2024-06-25. No multi-night data exists. Only 25 unique L-Pro frames (2h 05m). Reprocessing with current workflow would be a modest improvement (MGC, Drizzle 2, SPCC) but not the massive gain originally expected. **Priority: reshoot with L-Pro, 180s subs, target 4–6h integration.**

---

## Priority 1 (was 2): NGC 5746 — Full Reprocess

**Effort:** Medium | **Gain:** High — current tools replace ABE×3, Drizzle 2 doubles resolution

[[NGC5746]] was processed before PI 1.9 workflows existed: ABE×3, Drizzle 1x, no SubFrameSelector, no SPCC.

### Data

- 34 raw → 32 SFS-approved → 28 stacked = 2h 20m, single night (2024-06-10), -10°C, L-Pro
- **SSD:** `/Volumes/T7/Astrophotography/Objects/Galaxies/ASI2600MC-REDCAT51/NGC5746/2024/20240610-g100-300s-10/`
- **Results:** `Results_2026/master/masterLight_..._drizzle_2x_autocrop.xisf`

### Steps

- [x] SubFrameSelector: 34 → 32 approved (2 twilight frames rejected)
- [x] WBPP: Drizzle 2x, distortion correction, 28/32 stacked (2 failed local normalization)
- [ ] SPFC + MGC (replaces ABE×3)
- [ ] BXT → STX → NXT
- [ ] SPCC (Optolong L-Pro, Sony IMX QE)
- [ ] Full [[RGB-Workflow]] through stretch and final

### Calibration

| Frame | Status |
|-------|--------|
| Darks 300s/-10°C | Available (master) |
| Flats L-Pro | Available (60ms master) |
| Bias | Available |

---

## Priority 2 (was 3): M42 ASI2600 — Apply HDR Workflow

**Effort:** Medium | **Gain:** High — proper HDR replaces manual blend, first test of step 2.7

[[M42-Orion]] has ~120 SFS frames (~6h) with a manual HDR blend. The [[HDR-Workflow]] (MAS + HDRMT) should produce cleaner results. Also the ideal target to calibrate Ha emission separation scale factors (step 2.7).

### Data

| Year | Nights | Frames | Exposure | Temp |
|------|--------|--------|----------|------|
| 2024 | 1 | 20 | 180s | -20°C |
| 2025 | 5 | ~100 | 160s | -10°C |

**SSD:** `/Volumes/T7/Astrophotography/Objects/Nebuleuses/ASI2600MC-REDCAT51/M42_Orion/`

### Steps

- [ ] Decide: stack 2024+2025 together (mixed exposure/temp) or process separately
- [ ] WBPP with Drizzle 2
- [ ] [[QuadBand-OSC-Workflow]] through Phase 2 (linear)
- [ ] **Step 2.7: Calibrate Ha emission separation scale factors** — first time! Determine `scale_G` and `scale_B` for ASI2600MC Pro + Antlia Quad Band. Update workflow with discovered values.
- [ ] Phase 3: Channel extraction, HOO remapping
- [ ] **[[HDR-Workflow]] Method A: MAS + HDRMT** — Trapezium core recovery
  - MAS: aggressiveness 0.85, intensity 0.35, DR compression High, color saturation disabled
  - HDRMT: lightness mask, deringing 0.05, intensity 0.5–0.75
- [ ] Phase 5-6: Star processing, reintegration, final

### Calibration

| Frame | Status |
|-------|--------|
| Darks 180s/-20°C | Incomplete (20/25 raws, no master) |
| Darks 160s/-10°C | Available (master + 26 raws) |
| Flats Quad Band | Available (50ms + 60ms masters) |
| Bias | Available |

> **Bonus:** This reprocessing session will produce the Ha emission separation scale factors needed for step 2.7 of the [[QuadBand-OSC-Workflow]]. Update the TBD values in the workflow after calibration.

---

## Priority 3 (was 4): M31 — Add HDR for Nucleus

**Effort:** Medium | **Gain:** Medium — nucleus detail recovery

[[M31-Andromeda]] has 197 accepted frames (3h17m) with a good Result2 stack. Adding [[HDR-Workflow]] would reveal detail in the bright nucleus.

### Data

- 197 frames × 60s = 3h 17m across 3 nights, -10°C, L-Pro
- **SSD:** `/Volumes/T7/Astrophotography/Objects/Galaxies/ASI2600MC-REDCAT51/M31_Andromeda/`

### Steps

- [ ] Use existing Result2 master if stacked properly (Drizzle 2x confirmed)
- [ ] Or re-stack if debayerized instead of drizzled
- [ ] [[RGB-Workflow]] linear processing: SPFC + MGC → BXT → STX → NXT → SPCC
- [ ] **[[HDR-Workflow]] Method A: MAS + HDRMT** — nucleus recovery
  - MAS: aggressiveness 0.60, intensity 0.50, DR compression Low–Moderate
  - HDRMT: lightness mask, deringing 0.03, intensity 0.25–0.50
- [ ] RGB-Workflow Phase 4: star reintegration, final

### Calibration

| Frame | Status |
|-------|--------|
| Darks 60s/-10°C | Available (master) |
| Flats L-Pro | Available (60ms master) |
| Bias | Available |

> **Note:** 60s subs are short for galaxy imaging. This is a "best effort" reprocess. A future reshoot at 180s will be the real improvement.

---

## Priority 4 (was 5): NGC 2264 D5300 — PI Reprocess with Full Calibration

**Effort:** Low | **Gain:** Medium — full calibration in PI, rare for D5300 data

[[NGC2264-Cone]] has 103 frames with **complete calibration** (118 biases, 103 darks, 112 flats) — unique among D5300 sessions. Currently only has a Siril `final.TIF`.

### Data

- 103 frames × 15s = 25m 45s, ISO 800, 2022-03-03
- Full calibration on SSD
- **SSD:** `/Volumes/T7/Astrophotography/Objects/Open_Star_Clusters/D5300/NGC2264-Christmas_Tree_Open_Star_Cluster/`

### Steps

- [ ] Import all lights, darks, flats, biases into WBPP
- [ ] Stack with Drizzle 2
- [ ] Process with adapted [[RGB-Workflow]] (D5300 sensor, no SPFC/MGC — use GraXpert)
- [ ] NGC 2264 has strong Ha — in red channel curves, boost to bring out the Cone Nebula

### Calibration

All available on SSD in the session folder.

---

## Priority 5 (was 6): M42 D5300 2023 — Combine 60s Nights

**Effort:** Low | **Gain:** Medium — 2h 21m combined from 2 nights

[[M42-Orion]] D5300 2023 sessions at 60s were processed separately. Combining the two 60s nights (54 + 87 = 141 frames) doubles the integration.

### Data

| Night | Frames | Exposure | ISO |
|-------|--------|----------|-----|
| 2023-02-20 | 54 | 60s | 800 |
| 2023-02-25 | 87 | 60s | 800 |
| **Total** | **141** | | **2h 21m** |

**SSD:** `/Volumes/T7/Astrophotography/Objects/Nebuleuses/D5300/M42_Orion/2023/`

### Steps

- [ ] Combine both 60s sessions in WBPP
- [ ] Stack with Drizzle 2
- [ ] Process with adapted workflow (GraXpert for gradients, manual color)
- [ ] Compare with individual night results

### Calibration

No D5300 calibration frames available for these sessions. Process without darks/flats.

---

## Not Worth Reprocessing

| Object | Reason |
|---|---|
| ~~NGC 7000 ASI2600~~ | **Promoted → Priority A** — BlurX/SPCC split + MAS postdate all passes; future HORGB anchor. |
| ~~NGC 2244 ASI2600~~ | **Promoted → Priority B** — never run through OSC2/DBXtract; emission target. |
| ~~M45 ASI2600~~ | **Promoted → Priority C** (best-effort; filter mismatch — reflection nebula needs L-Pro). |
| M44 ASI2600 | Wrong filter (Quad Band on an open cluster). Reprocessing won't fix filter choice; recapture in L-Pro. |
| M51 Whirlpool | 17 frames — insufficient data |
| M27 Dumbbell | 16 frames — insufficient data |
| M67, M5, M3 | Too few ASI2600 frames or D5300 only with limited data |
| NGC 2175 D5300 | 154 unprocessed frames — worth a first-pass Siril stack, not a PI reprocess |

---

## Reprocessing Checklist Template

For each reprocessing session, verify before starting:

- [ ] Raw lights accessible on SSD
- [ ] Matching darks in [[Master-Library]] (exposure + temperature)
- [ ] Matching flats in [[Master-Library]] (filter)
- [ ] Dark flats available
- [ ] Bias available
- [ ] WBPP folder template ready (`/Volumes/T7/Astrophotography/Templates/PixInsight_templates/`)
- [ ] Target workflow identified ([[RGB-Workflow]], [[QuadBand-OSC-Workflow]], [[HDR-Workflow]])
- [ ] Process icons loaded (`icons-2024-2.xpsm`)
