---
title: "M5 — Rose Globular Cluster"
type: target
designation: "M5"
common_name: "Rose Globular Cluster"
object_type: cluster
constellation: "Serpens"
magnitude: "5.7"
angular_size: "23'"
total_integration: "TBD"
sessions:
  - "2023-05-17"
  - "[[2025-03-18-Capture]]"
  - "[[2025-03-27-Capture]]"
tags:
  - target/cluster
---

# M5 — Rose Globular Cluster

### Nikon D5300 (2023-05-17)

![[M5-D5300.png]]
*D5300 result (2023-05-17, 144 × 30s, ISO 800, Siril processing)*

## Capture History

### ASI2600MC Pro + RedCat 51

| Date | Exposure | Frames | Filter | Gain | Temp |
|------|----------|--------|--------|------|------|
| 2025-03-18 | 220s | 50 | [[Antlia-FQuad]] | g100 | -10°C |
| 2025-03-27 | 220s | 50 | [[Antlia-FQuad]] | g100 | -10°C |

### Nikon D5300 (legacy)

| Date | Exposure | Frames | ISO | Notes |
|------|----------|--------|-----|-------|
| 2023-05-17 | 30s | 144 | 800 | Processed in Siril, star reduction attempted |

**D5300 session:** 144 × 30s = 1h 12m
**Data location:** `/Volumes/T7/Astrophotography/Objects/Globular_Clusters/D5300/M5_Cluster/`

## Processing

### D5300 (2023-05-17)

- 144 NEF raw frames at 30s / ISO 800
- Stacked → `result.fit` / `.tif` / `.png`
- Star reduction attempted:
  - `starless_starReduction.fit` — starless version
  - `starReduction.fit` — intermediate
  - `reducedStars_final.fit` / `.tif` — final with reduced stars

### ASI2600MC Pro (2025)

- Pending processing

## Notes

- One of the oldest and most beautiful globular clusters — 23' angular size, slightly larger than M13
- Late-night target (RA 15h 19m) — rises late, best after midnight from Tuntange
- D5300 result shows well-resolved core with bright star 5 Serpentis in field
- **Quad Band is suboptimal for clusters** — 2025 sessions used [[Antlia-FQuad]] but [[Optolong-LPro]] is more appropriate since there's no emission nebulosity
- Use [[RGB-Workflow]] with [[Optolong-LPro]], 120s subs
- Summer target — best May–August
