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
| ~~2024-07-28~~ | ~~300s~~ | ~~7~~ | ~~L-Pro~~ | ~~g100~~ | ~~-20°C~~ |
| 2024-10-20 | 300s | 25 | [[Optolong-LPro]] | g100 | -10°C |
| 2025-03-17 | 220s | 15 (SFS) | [[Antlia-FQuad]] | g100 | -10°C |
| 2025-03-18 | 220s | 7 (SFS) | [[Antlia-FQuad]] | g100 | -10°C |

**2024 usable L-Pro (300s, -10°C):** 59 frames = 4h 55m (Nights 1, 2, 4 — Night 3 excluded, see below)
**2024 excluded:** ~~Night 3 (7 frames, -20°C)~~ — deleted from SSD. No matching 300s/-20°C darks in [[Master-Library]]
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

- **Mixed filter data:** 2024 sessions used L-Pro (broadband, 300s), 2025 sessions used Quad Band (220s). These cannot be stacked together — different spectral response.
- **Quad Band is suboptimal for clusters** — [[Optolong-LPro]] is more appropriate since there's no emission nebulosity to capture with narrowband
- **Night 2 data may be duplicated** — the Light folder contains frames with the same filenames as Night 1 (both start with `20240625-002422`). Verify before stacking.
- **Night 3 deleted** — 2024-07-28, -20°C, 7 frames. No 300s/-20°C darks in [[Master-Library]]. Data removed from SSD.
- **59 L-Pro frames (4h 55m) were never stacked as MultiNights** — only a single-night result exists. This is the #1 reprocessing priority in [[Reprocessing-Plan]].

### Reprocessing Plan

See [[Reprocessing-Plan]] **Priority 1** for detailed steps.

- Stack Nights 1 + 2 + 4 (59 frames, 4h 55m, all -10°C) as MultiNights
- Full [[RGB-Workflow]]: SPFC + MGC → BXT → STX → NXT → SPCC → Stretch → BN
- All calibration frames available (300s/-10°C darks, L-Pro flats, bias)
- **Ready to process** — no missing dependencies

### Future Capture

- Reshoot with L-Pro + 180s (matching dark library) rather than 300s or Quad Band 220s
- Summer target — best May–September
