---
title: "NGC 2244 — Rosette Nebula"
type: target
designation: "NGC 2244"
common_name: "Rosette Nebula"
object_type: nebula
constellation: "Monoceros"
magnitude: "4.8"
angular_size: "80' x 60'"
total_integration: "TBD"
sessions:
  - "2022-02-25"
  - "2023-03-02"
  - "2025-02-02"
tags:
  - target/nebula
---

# NGC 2244 — Rosette Nebula

### ASI2600MC Pro (2025-03-02)

![[NGC2244-ASI2600.jpg]]

### Nikon D5300 (2022-02-25)

![[NGC2244-D5300.jpg]]
*D5300 result (2022-02-25, 74 × 90s, ISO 800)*

## Capture History

### ASI2600MC Pro + RedCat 51

| Date | Exposure | Frames (SFS) | Filter | Gain | Temp |
|------|----------|-------------|--------|------|------|
| 2025-03-02 | 220s | 28 | [[Antlia-FQuad]] | g100 | -10°C |

**ASI2600MC total:** 28 frames, ~1h 42m integration
**Processed on 2025-03-08**
**Data location:** `/Volumes/T7/Astrophotography/Objects/Nebuleuses/ASI2600MC-REDCAT51/NGC2244_Rosetta_Nebula/`

**Processing results:**
- `MultiNights/Night1/master/Image60.jpg` — Drizzle 2x (shown above)
- `MultiNights/Replay_Night1/master/` — reprocessed without drizzle

### Nikon D5300 (legacy)

| Date | Exposure | Frames | Darks | ISO | Notes |
|------|----------|--------|-------|-----|-------|
| 2022-02-25 | 90s | 74 | — | 800 | `result2.png` (shown above) |
| 2023-03-02 | 90s | 36 | 10 | 800 | No exported result |

**D5300 total lights:** 110 across 2 sessions
**Data location:** `/Volumes/T7/Astrophotography/Objects/Nebuleuses/D5300/NGC2244_Rosetta_Nebula/`

## Processing

### ASI2600MC Pro (2025)

- 28 lights after SubFrameSelector (from Feb 2 data)
- Processed on 2025-03-08

### D5300

- 2022-02-25: 74 frames stacked → `result2.png`
- 2023-03-02: 36 frames with 10 darks, no exported result

## Notes

- Large emission nebula at 80' × 60' — fills the [[RedCat-51]] FOV well
- Strong Ha and OIII emission — ideal for [[Antlia-FQuad]]
- Winter target (RA 6h 32m) — best December–March from Tuntange
- Use [[QuadBand-OSC-Workflow]]
- Only 28 ASI2600MC frames — needs more integration time
