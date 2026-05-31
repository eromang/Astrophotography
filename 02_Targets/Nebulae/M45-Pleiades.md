---
title: "M45 — Pleiades"
type: target
designation: "M45"
common_name: "Pleiades"
object_type: "cluster"
constellation: "Taurus"
magnitude: "1.6"
angular_size: "110'"
total_integration: "TBD"
sessions:
  - "2022-02-13"
  - "2023-02-08"
  - "2023-02-13"
  - "2024-12-26"
  - "2024-12-27"
tags:
  - target/cluster
---

# M45 — Pleiades

### Nikon D5300 (2023-02-13)

![[M45-D5300.jpg]]
*D5300 result (2023-02-13, recomposition with starless processing)*

## Capture History

| Date | Exposure | Frames | Filter | Gain | Temp |
|------|----------|--------|--------|------|------|
| 2024-12-26 | 180s | 60 | [[Antlia-FQuad]] | g100 | -20°C |
| 2024-12-27 | 180s | 20 | [[Antlia-FQuad]] | g100 | -20°C |

**Total frames:** 80 (stacked in MultiNights)
**Total integration:** ~4h
**Data location:** `/Volumes/T7/Astrophotography/Objects/Nebuleuses/ASI2600MC-REDCAT51/M45_Pleiades/`

### Nikon D5300 (legacy)

| Date | Exposure | Frames | ISO | Notes |
|------|----------|--------|-----|-------|
| 2022-02-13 | 120s | 20 | 800 | `result-16b.tif` |
| 2023-02-08 | 60s | 57 | 800 | `result2.png`, `result2.jpg` |
| 2023-02-13 | 60s | 37 | 800 | Starless processing, `recomposition.jpg` (shown above) |

**D5300 total lights:** 114 across 3 sessions
**Data location:** `/Volumes/T7/Astrophotography/Objects/Open_Star_Clusters/D5300/M45 _Pleiades/`

## Processing

### ASI2600MC Pro (2024)

- 2 nights stacked as MultiNights
- Two processing passes: ResultNight1, ResultNight2

### D5300

- 2023-02-13: Most advanced — starless processing with star/starless recomposition

## Notes

- Open star cluster with reflection nebulosity — primarily broadband target
- ⚠️ **Filter — Quad Band, and uniquely wrong here.** The 2024-12 ASI2600 data was shot with [[Antlia-FQuad]], but M45 is a **reflection nebula** — it scatters broadband starlight (continuum/blue) with **no emission lines**, so the Quad Band's narrow Hα/Hβ/OIII passbands let through almost none of the nebulosity. The Quad Band master gives the stars but **essentially deletes the blue dust — the whole subject.** Worse than the [[M44-Beehive|M44]] Quad-Band case (which only lost star colour); no reprocessing recovers it. (Data also at −20 °C, predating the −10 °C [[Master-Library|cooling standard]].)
- **The legacy D5300 broadband data currently holds the nebulosity** (2023-02-13 recomposition, shown above) — for the dust, the old DSLR data is the better dataset than the newer ASI2600 Quad Band frames.
- **Recapture in [[Optolong-LPro]]** — winter Taurus target (~Nov–Feb), at −10 °C — is the only path to a proper M45.
- At 110' fits well in the [[RedCat-51]] FOV (5.4° × 3.6°)
- **Workflow (when reshot in L-Pro):** M45 is a **hybrid**, not a pure cluster. Use the [[OpenCluster-Workflow]] *star handling* for the bright, bloat-prone Pleiades stars (Merope etc. — BXT Halos −0.15 + MorphologicalTransformation reduction), but treat the **reflection nebula with gentle [[RGB-Workflow]] structure work** (preserve the faint blue dust, don't crush it). [[QuadBand-OSC-Workflow]] on the existing Quad Band data adds little — narrowband ≠ reflection nebula.
