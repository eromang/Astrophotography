---
title: "C/2023 A3 — Tsuchinshan–ATLAS"
type: target
designation: "C/2023 A3"
common_name: "Tsuchinshan–ATLAS"
object_type: "comet"
constellation: ""
magnitude: ""
angular_size: ""
total_integration: "1470s (24m 30s)"
sessions:
  - "2024-10-23"
tags:
  - target/comet
---

# C/2023 A3 — Tsuchinshan–ATLAS

![[C2023A3-Tsuchinshan-ATLAS.jpg]]

## Capture History

| Date | Exposure | Frames | Filter | Gain | Temp |
|------|----------|--------|--------|------|------|
| 2024-10-23 | 30s | 49 | No filter | g100 | -10°C |

**Total frames:** 49
**Total integration:** 24m 30s
**Data location:** `/Volumes/T7/Astrophotography/Objects/Comettes/ASI2600MC-REDCAT51/2024/C:2023 A3 (Tsuchinshan–ATLAS)/`

## Processing

- Calibrated with matching darks (30s), bias, and flats (masters in Results folder)
- Comet-registered stacking (star-aligned + comet-aligned)
- Master lights available: RGB composite + individual R, G, B channels + autocropped versions
- Star field extracted separately (`stars.xisf`)

**Processing folders:**
- `Results/` — first processing pass (star-registered + comet-registered)
- `Results2/` — second processing pass
- `SFS/` — SubFrameSelector output

## Notes

- Great Comet of 2024 — reached naked-eye visibility (mag ~0) in October 2024
- Short exposures (30s) to freeze comet motion at 250mm focal length
- No filter used — broadband capture to maximize signal on the comet's dust tail and ion tail
- Comet stacking requires special registration mode in PixInsight (CometAlignment or WBPP comet mode) to produce both a sharp comet and sharp star field separately
- One-time event — comet has a ~80,000 year orbital period
