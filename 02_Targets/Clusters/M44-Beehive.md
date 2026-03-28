---
title: "M44 — Beehive Cluster"
type: target
designation: "M44"
common_name: "Beehive Cluster"
aliases:
  - "Praesepe"
object_type: cluster
constellation: "Cancer"
magnitude: "3.7"
angular_size: "95'"
total_integration: "TBD"
sessions:
  - "2022-02-25"
  - "2022-03-09"
  - "2022-03-23"
  - "2023-02-08"
  - "[[2025-03-17-Capture]]"
  - "[[2025-03-18-Capture]]"
  - "[[2025-03-27-Capture]]"
tags:
  - target/cluster
---

# M44 — Beehive Cluster (Praesepe)

### Nikon D5300 (2023-02-08)

![[M44-D5300.jpg]]
*D5300 result (2023-02-08, 100 × 30s, ISO 400)*

## Capture History

### ASI2600MC Pro + RedCat 51

| Date | Exposure | Frames (SFS) | Filter | Gain | Temp |
|------|----------|-------------|--------|------|------|
| 2025-03-17 | 160s | 40 | [[Antlia-FQuad]] | g100 | -10°C |
| 2025-03-18 | 160s | 79 | [[Antlia-FQuad]] | g100 | -10°C |
| 2025-03-27 | 160s | 37 | [[Antlia-FQuad]] | g100 | -10°C |

**ASI2600MC total:** 156 SFS frames, ~6h 56m integration
**Data location:** `/Volumes/T7/Astrophotography/Objects/Open_Star_Clusters/ASI2600MC-REDCAT51/M44_Cluster/`

**Processing results:**
- `MultiNights/master/` — Drizzle 2x, GraXpert gradient removal, annotated
- `MultiNights/master1/M44_ADBE.xisf` — latest processing pass

### Nikon D5300 (legacy)

| Date | Exposure | Frames | ISO | Notes |
|------|----------|--------|-----|-------|
| 2022-02-25 | 15s | 94 | 800 | `m44.TIF` |
| 2022-03-09 | 15s | 208 | 800 | `save.TIF` |
| 2022-03-23 | 15s | 106 | 1600 | FLH filter, `result.tif` |
| 2023-02-08 | 30s | 100 | 400 | `result2.png` (shown above) |

**D5300 total lights:** 508 across 4 sessions
**Data location:** `/Volumes/T7/Astrophotography/Objects/Open_Star_Clusters/D5300/M44_Beehive_Open_Star_Cluster/`

## Processing

### ASI2600MC Pro (2025)

- 3 nights stacked as MultiNights
- GraXpert gradient removal
- Drizzle 2x, autocropped

### D5300

- 2023-02-08: Best D5300 result (`result2.png`)
- 2022-03-23: Shot with FLH filter

## Notes

- Large open cluster at 95' — fills the [[RedCat-51]] FOV
- Mid-evening target (22:30–01:30)
- Nearby galaxies in FOV: IC2407, IC2406, IC2409
- **Quad Band is suboptimal for open clusters** — [[Optolong-LPro]] is more appropriate
- Use [[RGB-Workflow]]
