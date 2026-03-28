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
- Shot with [[Antlia-FQuad]] but M45 is a reflection nebula (no emission lines) — [[Optolong-LPro]] would be more appropriate for future sessions
- At 110' fits well in the [[RedCat-51]] FOV (5.4° × 3.6°)
- Use [[RGB-Workflow]] if reshot with L-Pro, or [[QuadBand-OSC-Workflow]] for existing Quad Band data (though narrowband adds little to reflection nebulae)
