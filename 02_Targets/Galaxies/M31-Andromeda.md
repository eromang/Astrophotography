---
title: "M31 — Andromeda Galaxy"
type: target
designation: "M31"
common_name: "Andromeda Galaxy"
object_type: "galaxy"
constellation: "Andromeda"
magnitude: "3.4"
angular_size: "178' x 63'"
total_integration: "11820s (3h 17m)"
sessions:
  - "2024-09-28"
  - "2024-10-23"
  - "2024-11-03"
tags:
  - target/galaxy
---

# M31 — Andromeda Galaxy

![[M31-Andromeda.jpg]]

## Capture History

### ASI2600MC Pro + RedCat 51

| Date | Exposure | Frames (raw) | Frames (accepted) | Filter | Gain | Temp |
|------|----------|-------------|-------------------|--------|------|------|
| 2024-09-28 | 60s | 22 | — | [[Optolong-LPro]] | g100 | -10°C |
| 2024-10-23 | 60s | 123 | — | [[Optolong-LPro]] | g100 | -10°C |
| 2024-11-03 | 60s | 109 | — | [[Optolong-LPro]] | g100 | -10°C |
| **Total** | | **254** | **197** (77% acceptance) | | | |

**Total integration (accepted):** 197 × 60s = 3h 17m

### Nikon D5300 (legacy)

| Date | Exposure | Frames | ISO | Notes |
|------|----------|--------|-----|-------|
| 2022-02-25 | 15s | — | 800 | Processed in Siril |
| 2022-11-13 | 30s (Bin2) | 200 | — | Processed in PixInsight (Autosave.tif) |

![[M31-D5300.jpg]]
*D5300 result (2022-02-25, 15s × ISO 800, Siril processing)*

**2022-02-25 session:**
- Short untracked 15s exposures at ISO 800
- Processed in Siril → `deep.TIF` → post-processed → `siril-post.png`
- Core and inner structure visible, faint outer arms lost to short exposure

**2022-11-13 session:**
- 200 frames at 30s, Bin2
- Full calibration data set on SSD: `data/` folder with lights, darks, flats, biases, rejects subfolders (darks/flats/biases folders currently empty — calibration may have been done inline)
- Processed in PixInsight → `Autosave.tif` + `m31-20221113.TIF`

**Data location:** `/Volumes/T7/Astrophotography/Objects/Galaxies/ASI2600MC-REDCAT51/M31_Andromeda/`
**Legacy data:** `/Volumes/T7/Astrophotography/to post-process/M31/` and `M31_Andromeda_800_15s_20220225/`

## Processing

### Result2 (MultiNights, most recent)

1. SubFrameSelector: 254 raw → 197 accepted (57 rejected, 23% rejection rate)
2. Calibrated: 197 frames
3. Debayered → Registered (592 channel files)
4. Stacked with Drizzle 2x
5. Autocropped
6. Final: `M31.jpg` / `M31.xisf`

**Output:** `MultiNights/Result2/master/`
**PixInsight project:** `MultiNights/Result2/untitled.pxiproject`

### Result1 (earlier processing pass)

Alternative processing with `final.jpg` / `final.xisf` output.

## Notes

- Largest galaxy in the sky at 178' × 63' — fills the [[RedCat-51]] FOV (5.4° × 3.6°) well
- **HDR target** — bright nucleus vs faint spiral arms. Use [[RGB-Workflow]] + [[HDR-Workflow]]
- Fall target (RA 0h 43m) — best September–November from Tuntange
- **60s exposures are short** for galaxy imaging — workflow default is 180s with [[Optolong-LPro]]. The 60s subs limit SNR on the faint outer arms. Consider reshooting with 180s for better depth.
- Night 1 had low yield (22 frames) — likely cut short by weather or setup issues
- Filter not tagged in ASIAIR filenames (`FILTER-NoFilter`) — configure ASIAIR to record filter name
- 23% frame rejection rate — some nights had subpar conditions

### Future Plans

- Reshoot with **180s subs** for deeper integration on outer spiral arms
- Add short subs (30–60s) for **multi-exposure HDR composition** of the bright nucleus (future [[HDR-Workflow]] addition)
- Target: 6–10h total integration for a strong result
