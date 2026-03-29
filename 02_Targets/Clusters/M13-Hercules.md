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
  - "2024-06-25"
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
| 2024-06-25 | 300s | 25 | [[Optolong-LPro]] | g100 | -10°C |
| 2025-03-17 | 220s | 15 (SFS) | [[Antlia-FQuad]] | g100 | -10°C |
| 2025-03-18 | 220s | 7 (SFS) | [[Antlia-FQuad]] | g100 | -10°C |

**2024 L-Pro (300s):** 25 unique frames = 2h 05m
**2025 Quad Band (220s):** 22 frames (SFS approved) = 1h 21m

**Data location:** `/Volumes/T7/Astrophotography/Objects/Globular_Clusters/ASI2600MC-REDCAT51/M13_Cluster/`

> [!warning] Duplicate data on SSD
> The 2024 data was duplicated across 3 folders (`20240610`, `20240624`, `20241020`) — all contained the same 25 frames from 2024-06-25. Duplicates and empty SFS folder deleted. Canonical folder renamed to `20240625-g100-300s-10`.

> [!note] Deleted data
> Night 3 (2024-07-28, -20°C, 7 frames) was deleted from SSD — no matching darks, insufficient frames.

## Processing

### 2024 single-night (Results, June 24 folder)

- Drizzle 1x, autocropped
- Output: `2024/20240624-g100-300s-10/Results/master/`

### 2025 MultiNights (master1, most recent)

- 2025 sessions stacked (220s Quad Band data)
- Drizzle 2x, autocropped
- GraXpert gradient removal (two passes)
- Final: `integration_autocrop1_ADBE.jpg` / `.xisf`
- Output: `2025/MultiNights/master1/`

## Notes

- Best globular cluster in the northern sky — 20' angular size, well-resolved at 250mm
- Late-night target (rises late, best after midnight from Tuntange)
- Star colors well-resolved: blue-white core, orange/red giants in outer halo
- Use [[RGB-Workflow]] with [[Optolong-LPro]]

### Observations

- **Only 25 unique L-Pro frames** — the apparent 3-night dataset was duplicated data. No multi-night stacking benefit.
- **Quad Band is suboptimal for clusters** — [[Optolong-LPro]] is more appropriate since there's no emission nebulosity
- **2024 L-Pro data could be reprocessed** with current workflow (MGC instead of ABE, Drizzle 2 instead of 1x, SPCC) but gain is modest with only 25 frames
- Consider cleaning up duplicate folders on SSD to avoid confusion

### Future Capture

- **Priority: reshoot with L-Pro** — need substantially more integration time (target 4–6h)
- Use 180s subs (matching dark library) rather than 300s
- Summer target — best May–September
