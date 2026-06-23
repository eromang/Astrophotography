---
title: "M42 — Orion Nebula"
type: target
designation: "M42"
common_name: "Orion Nebula"
object_type: nebula
constellation: "Orion"
magnitude: "4.0"
angular_size: "85' x 60'"
total_integration: "TBD"
sessions:
  - "2022-02-04"
  - "2022-02-07"
  - "2022-02-09"
  - "2022-02-12"
  - "2022-02-25"
  - "2022-03-03"
  - "2022-03-23"
  - "2023-02-08"
  - "2023-02-20"
  - "2023-02-25"
  - "2024-12-27"
  - "2025-03-02"
  - "2025-03-05"
  - "[[2025-03-17-Capture]]"
  - "[[2025-03-18-Capture]]"
  - "[[2025-03-27-Capture]]"
tags:
  - target/nebula
---

# M42 — Orion Nebula

### ASI2600MC Pro (2026-06, natural-colour HDR reprocess) — latest

![[M42-2026-natural.jpg]]
*100 × 160 s FQuad, **natural-colour** HDR (MAS + HDRMT). See [[#2026-06-23 HDR reprocess — natural colour, completed]].*

### ASI2600MC Pro (2025, HDR blend)

![[M42-ASI2600.jpg]]

### Nikon D5300 (2023-02-08)

![[M42-D5300.jpg]]
*D5300 result (2023-02-08, 102 × 30s, ISO 400)*

## Capture History

### ASI2600MC Pro + RedCat 51

| Date | Exposure | Frames (SFS) | Filter | Gain | Temp |
|------|----------|-------------|--------|------|------|
| 2024-12-27 | 180s | 20 | [[Antlia-FQuad]] | g100 | -20°C |
| 2025-03-02 | 160s | 12 | [[Antlia-FQuad]] | g100 | -10°C |
| 2025-03-05 | 160s | 15 | [[Antlia-FQuad]] | g100 | -10°C |
| 2025-03-17 | 160s | 21 | [[Antlia-FQuad]] | g100 | -10°C |
| 2025-03-18 | 160s | ~17 | [[Antlia-FQuad]] | g100 | -10°C |
| 2025-03-27 | 160s | 12 | [[Antlia-FQuad]] | g100 | -10°C |

**ASI2600MC total:** ~120 unique SFS frames, ~6h integration
**Data location:** `/Volumes/T7/Astrophotography/Objects/Nebuleuses/ASI2600MC-REDCAT51/M42_Orion/`

**Processing results:**
- `2024/MultiNights/Night1/master/Image30.jpg` — Night 1 only (Drizzle 2x)
- `2025/MultiNights/master/blend_Image26_cloned_Image26_HDR.jpg` — **Latest: HDR blend, multi-night** (shown above)
- `2025/MultiNights/master1/blend_Image23_cloned_Image23_HDR.jpg` — earlier HDR pass

### Nikon D5300 (legacy)

| Date | Exposure | Frames | ISO | Notes |
|------|----------|--------|-----|-------|
| 2022-02-04 | 4s | 194 | 1000–2500 | 5 ISO sub-sessions (multi-ISO HDR attempt) |
| 2022-02-07 | 4s | 70 | 2000–3200 | 3 ISO sub-sessions |
| 2022-02-09 | 20s | 58 | 1600 | |
| 2022-02-12 | 10s | 70 | 1250 | Heavily processed (Photoshop layers) |
| 2022-02-25 | 15s | 176 | 800 | Full calibration (107 biases, 102 darks, 31 flats) |
| 2022-02-25 | 20s | 153 | 1250 | Same night, second run |
| 2022-03-03 | 15s | 170 | 800 | |
| 2022-03-23 | 15s | 100 | 1600 | FLH filter |
| 2023-02-08 | 30s | 102 | 400 | Best D5300 result (`result2_m42.jpg`) |
| 2023-02-20 | 60s | 54 | 800 | |
| 2023-02-25 | 60s | 87 | 800 | |

**D5300 total lights: 1,234** across 11 sessions (2022–2023)
**Data location:** `/Volumes/T7/Astrophotography/Objects/Nebuleuses/D5300/M42_Orion/`

## Processing

### ASI2600MC Pro

- 27 lights after SubFrameSelector (Feb 2025 data)
- March 2025 data pending

#### 2026-06-23 HDR reprocess — natural colour, completed

Full reprocess of the 100 × 160 s FQuad stack on the **natural-colour (non-HOO)** path → `M42_FINAL_v2`: bright structured Trapezium core (HDR), neutral deep sky, the Running Man's blue reflection, natural Ha/OIII palette.

**Restack:** all 100 subs (5 nights, −10 °C) in WBPP → drizzle-2× master, solved, 1.552 ″/px. Raw-master PSF 4.54 px → **after BXT Correct Only 2.5 px / ecc 0.27** (CO tightens stars; measure the Sharpen PSF post-CO, not on the raw master).

**Pipeline (corrected order):** GraXpert 0.8 → BXT Correct Only → **SPCC (star-full)** → BXT Sharpen (Adjust Star Halos **−0.20**, Sharpen Stars 0.15, PSF 2.5) → SXT (Unscreen off, Large Overlap on) → NXT → **MAS → HDRMT** → BackgroundNeutralization → SCNR → saturation → screen-blend stars → deepen sky.

**Lessons (M42-specific):**
- 🔴 **Drop HOO for M42.** It's broadband-rich (strong Ha *and* OIII), so the **natural SPCC colour is already vivid**; the HOO remap (R=Ha, G=B=OIII) added **chromatic G=B colour noise for no benefit**. We ran HOO first, hit the noise, and restarted natural-colour — far cleaner. Reserve HOO/Foraxx for *faint dual-narrowband* targets. See [[../../04_Processing/Pixinsight/QuadBand-OSC-Workflow]] Phase 3.
- **SPCC needs stars → run it before StarXTerminator** (it photometers stars; can't run on the starless). Was a workflow-order bug — fixed at QuadBand §2.4.
- **HDRMT has an Intensity slider** (default 1.0 = max) — use **~0.5**, and keep **Deringing ~0.05** (the ~0.5 default greys the core to mush). See [[../../04_Processing/Pixinsight/HDR-Workflow]].
- **MAS low DRC (0.20)** for the bright core (the core is HDRMT's job, not DRC's); Aggressiveness ~0.5; Saturation off (add later).
- **BXT Adjust Star Halos −0.20** cut the bright-star halos **48.6 %** (measured via `star_halos.py`); the residual is partly inherent (covered at reintegration + targeted cleanup).
- **GraXpert 0.8 beat MGC+DR2** (retained): [[../../04_Processing/Pixinsight/Gradient-MGC-vs-GraXpert-M42]].

**QA scripts built during this reprocess:** [[../../04_Processing/Pixinsight/Find-Background]], [[../../04_Processing/Pixinsight/Star-Halos]], [[../../04_Processing/Pixinsight/NXT-Advisor]] (+ [[../../04_Processing/Pixinsight/Gradient-Check]]).

**Output:** `M42_FINAL_v2.xisf` / `.jpg` (T7: `…/M42_Orion/2026/`). Working set was staged at `~/Desktop/Astro/M42_HDR_Reprocess/` (intermediates reproducible from the master).

### D5300

- Most-processed target in the collection — many iterations across sessions
- 2022-02-04: Multi-ISO HDR attempt (4s at 5 different ISOs)
- 2022-02-12: Most post-processed — Photoshop layers, multiple exports
- 2022-02-25 (800/15s): Only D5300 session with full calibration (biases, darks, flats)
- 2023-02-08 (400/30s): Cleanest D5300 result

## Notes

- Classic HDR target — bright Trapezium core vs faint outer nebulosity. Use [[QuadBand-OSC-Workflow]] + [[HDR-Workflow]]
- Winter target (RA 5h 35m) — best December–March from Tuntange
- Visible early evening (20:30–22:30) in March sessions
- Your most-photographed object — 1,234 D5300 frames + ASI2600MC data
- The D5300 multi-ISO approach (2022-02-04/07) was an early HDR attempt — the [[HDR-Workflow]] with MAS + HDRMT is the proper solution
- Strong Ha and OIII emission — ideal for [[Antlia-FQuad]]
