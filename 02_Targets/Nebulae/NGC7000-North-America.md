---
title: "NGC 7000 — North America Nebula"
type: target
designation: "NGC 7000"
common_name: "North America Nebula"
object_type: nebula
constellation: "Cygnus"
magnitude: "4.0"
angular_size: "120' x 100'"
total_integration: "83700s (23h 15m)"
sessions:
  - "2023-08-10"
  - "2023-08-13"
  - "2023-08-21"
  - "2023-08-22"
  - "2024-07 to 2024-09"
tags:
  - target/nebula
---

# NGC 7000 — North America Nebula

### ASI2600MC Pro (2026 reprocessing, 16.4h integration)

![[NGC7000-2026-Results10.jpg]]

### ASI2600MC Pro (2024 processing, 24h integration)

![[NGC7000-ASI2600.jpg]]

### Nikon D5300 (2023, multi-night)

![[NGC7000-D5300.jpg]]
*D5300 result (2023-08 combined, recomposition with Ha/OIII extraction)*

## Capture History

### ASI2600MC Pro + RedCat 51

| Date | Exposure | Frames (SFS) | Filter | Gain | Temp |
|------|----------|---------------|--------|------|------|
| 2024-07-29 | 300s | 9 | L-Pro | g100 | -20°C |
| 2024-08-05 | 300s | 32 | L-Pro | g100 | -20°C |
| 2024-08-13 | 300s | 33 | L-Pro | g100 | -10°C |
| 2024-08-26 | 300s | 60 | L-Pro | g100 | -10°C |
| 2024-08-27 | 300s | 26 | L-Pro | g100 | -10°C |
| 2024-08-28 | 300s | 57 | L-Pro | g100 | -10°C |
| 2024-08-29 | 300s | 54 | L-Pro | g100 | -10°C |
| 2024-09-28 | 300s | 17 | L-Pro | g100 | -10°C |
| **Total** | | **288** | | | |

**Total integration: ~24 hours** (288 × 300s) across 8 nights. Processed on 2025-03-09.

**Processing results (10 passes):**
- `Results1/master/NGC7000-202408-RGB.jpg` — early processing
- `Results8/master/NGC7000.jpg` — previous best, Drizzle 2x, starless/stars separation
- `Results9/` — GraXpert gradient experiment
- `Results10/NGC7000-2026-Results10.jpg` — **latest (2026-04-01)**, PI 1.9.3, SPFC+MGC gradient removal, 197 frames (16.4h, -10°C only), Drizzle 2x. See [[2026-04-01-Processing]]

**Data location:** `/Volumes/T7/Astrophotography/Objects/Nebuleuses/ASI2600MC-REDCAT51/NGC_7000_North_America_Nebula/`

### Nikon D5300 (legacy)

| Date | Exposure | Frames | Darks | Biases | ISO | Notes |
|------|----------|--------|-------|--------|-----|-------|
| 2023-08-10 | 300s | 8 | 10 | — | 1600 | First attempt, few frames |
| 2023-08-13 | 180s | 35 | 20 | 20 | 1600 | Ha/OIII extraction in results |
| 2023-08-21 | 180s | 43 | 20 | 20 | 1600 | |
| 2023-08-22 | 180s | 38 | 20 | — | 1600 | |
| **13–21 combined** | 180s | 78 | 40 | 20 | 1600 | Most processed — starless, recomposition |
| **13–22 combined** | mixed | 116 | 60 | 20 | 1600 | Largest combined set |

**D5300 total individual lights:** 124 (+ combined stacks)
**Data location:** `/Volumes/T7/Astrophotography/Objects/Nebuleuses/D5300/NGC_7000_North_America_Nebula/`

## Processing

### ASI2600MC Pro (2024)

- 279 lights after SubFrameSelector across 8 nights
- Processed on 2025-03-09

### D5300 (2023)

Best results from the **13–21 combined** stack:
- Master light stacked → `masterLight.png` / `.xisf`
- Narrowband channel extractions: `result_Ha_14037s.fit`, `result_OIII_14037s.fit`
- Starless processing → `starless_result.tif`, `starless_result2.tif` / `.jpg`
- Recomposition → `recomposition.tif` / `.jpg` (final result)
- PSF analysis: `2023-08-22T13.58.09_result_PSF.tif`

Most advanced D5300 processing — Ha/OIII channel extraction with recomposition, starless processing.

## Notes

- Your deepest integrated target — 23h 15m with ASI2600MC Pro
- Largest emission nebula in the northern sky at 120' × 100' — fills the [[RedCat-51]] FOV
- Summer target (RA 20h 59m) — best July–October from Tuntange
- Used [[Optolong-LPro]] filter for the ASI2600MC sessions
- Strong Ha emission — ideal for [[Antlia-FQuad]] or Ultimate filter
- Use [[RGB-Workflow]] (L-Pro data) or [[QuadBand-OSC-Workflow]] (if re-shot with [[Antlia-FQuad]])
- The D5300 sessions showed impressive calibration discipline — darks and biases in most sessions, plus advanced narrowband extraction from DSLR data
- No flats in any D5300 session
