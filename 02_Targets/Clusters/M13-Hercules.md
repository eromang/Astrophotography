---
title: "M13 — Hercules Globular Cluster"
type: target
designation: "M13"
common_name: "Hercules Globular Cluster"
object_type: cluster
constellation: "Hercules"
magnitude: "5.8"
angular_size: "20'"
total_integration: "TBD"
sessions:
  - "2024-06-10"
  - "2024-06-24"
  - "2024-07-28"
  - "2024-10-20"
  - "[[2025-03-17-Capture]]"
  - "[[2025-03-18-Capture]]"
tags:
  - target/cluster
---

# M13 — Hercules Globular Cluster

![[M13-Hercules.jpg]]

## Capture History

### ASI2600MC Pro + RedCat 51

| Date | Exposure | Frames | Filter | Gain | Temp |
|------|----------|--------|--------|------|------|
| 2024-06-10 | 300s | 25 | [[Optolong-LPro]] | g100 | -10°C |
| 2024-06-24 | 300s | 9 | [[Optolong-LPro]] | g100 | -10°C |
| 2024-07-28 | 300s | 7 | [[Optolong-LPro]] | g100 | -20°C |
| 2024-10-20 | 300s | 25 | [[Optolong-LPro]] | g100 | -10°C |
| 2025-03-17 | 220s | 15 (SFS) | [[Antlia-FQuad]] | g100 | -10°C |
| 2025-03-18 | 220s | 7 (SFS) | [[Antlia-FQuad]] | g100 | -10°C |

**2024 total (L-Pro, 300s):** 66 frames = 5h 30m
**2025 total (Quad Band, 220s):** 22 frames (SFS approved) = 1h 21m

**Data location:** `/Volumes/T7/Astrophotography/Objects/Globular_Clusters/ASI2600MC-REDCAT51/M13_Cluster/`

## Processing

### 2024 single-night (Results, June 24 session)

- Drizzle 1x, autocropped
- Output: `2024/20240624-g100-300s-10/Results/master/`

### 2025 MultiNights (master1, most recent)

- 2025 sessions stacked (220s Quad Band data)
- Drizzle 2x, autocropped
- GraXpert gradient removal (two passes: `GraXpert_GraXpertImage_Temp.xisf`, `_Temp2.xisf`)
- Final: `integration_autocrop1_ADBE.jpg` / `.xisf`
- Output: `2025/MultiNights/master1/`

### 2025 MultiNights (master, earlier pass)

- Same data, alternative processing
- Output: `2025/MultiNights/master/`

## Notes

- Best globular cluster in the northern sky — 20' angular size, well-resolved at 250mm
- 6 sessions across 2024–2025, mixed filters and exposures
- Late-night target (rises late, best after midnight from Tuntange)
- Star colors well-resolved: blue-white core, orange/red giants in outer halo
- Use [[RGB-Workflow]] with [[Optolong-LPro]]

### Observations

- **Mixed filter data:** 2024 sessions used L-Pro (broadband, 300s), 2025 sessions used Quad Band (220s). These should not be stacked together — different spectral response. The 2025 MultiNights result only includes the Quad Band data.
- **Quad Band is suboptimal for clusters** — [[Optolong-LPro]] is more appropriate since there's no emission nebulosity to capture with narrowband
- **2024-06-24 Night 2 data appears duplicated** — the Light folder contains frames with the same filenames as Night 1 (both start with `20240625-002422`). Verify whether this is the same data copied, or genuinely different frames.
- **Night 3 (2024-07-28)** was at -20°C (summer, unusual) with only 7 frames — likely testing or poor conditions
- **2024 L-Pro data (5.5h) was never stacked as MultiNights** — only the June 24 single-night result exists. Consider stacking all 4 L-Pro nights together.

### Future Plans

- Stack all 2024 L-Pro data (66 frames, 5.5h) as a proper MultiNights project
- Reshoot with L-Pro + 180s (matching dark library) rather than 300s or Quad Band 220s
- Summer target — best May–September
