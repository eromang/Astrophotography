---
title: "M33 — Triangulum Galaxy"
type: target
designation: "M33"
common_name: "Triangulum Galaxy"
object_type: "galaxy"
constellation: "Triangulum"
magnitude: "5.7"
angular_size: "73' x 45'"
total_integration: "TBD"
sessions:
  - "2022-02-09"
  - "2022-11-13"
tags:
  - target/galaxy
---

# M33 — Triangulum Galaxy

### Nikon D5300 (2022-02-09)

![[M33-D5300.jpg]]

### Nikon D5300 (2022-11-13)

No result image available.

## Capture History

### Nikon D5300 (legacy)

| Date | Exposure | Frames | ISO | Camera | Notes |
|------|----------|--------|-----|--------|-------|
| 2022-02-09 | 20s | — | 1600 | D5300 | Processed in Siril + Photoshop |
| 2022-11-13 | 30s (Bin2) | 200 | — | D5300 | Processed in PixInsight |

**Data locations:**
- `to post-process/M33_Pinwheel_20220209_1600_20s/` — 2022-02-09 session
- `to post-process/M33/` — 2022-11-13 session (200 lights + thumbnails + info files)

### 2022-02-09 Processing

- Stacked in Siril → `deep.TIF`
- Post-processed in Siril → `siril-post.tif`
- Background extraction in Photoshop → `background.psd`
- Final result: `process.tif`
- Alternative: `result.tif` (earlier version)

### 2022-11-13 Processing

- 200 frames at 30s, Bin2
- Each frame has `.fit` + `_thn.jpg` (thumbnail) + `.Info.txt` (metadata)
- Stacked → `Autosave.tif` + `m31-20221113.TIF`

> [!note] Filename anomaly
> The result file is named `m31-20221113.TIF` but the lights are M33 — likely a copy/rename error from the M31 session the same night.

## Notes

- Face-on spiral galaxy at 73' × 45' — second largest galaxy after M31, fills the [[RedCat-51]] FOV well
- Contains NGC 604, one of the largest HII regions in the Local Group — visible as a bright blue-white knot in the spiral arms
- Fall target (RA 1h 34m) — best October–December from Tuntange
- Use [[RGB-Workflow]] with [[Optolong-LPro]]
- **No ASI2600MC Pro data yet** — good candidate for the current rig. 73' angular size is well-suited for the 5.4° × 3.6° FOV.
- Low surface brightness despite mag 5.7 — needs deep integration (aim 6–10h)

### Future Plans

- Capture with ASI2600MC Pro + RedCat 51 + L-Pro, 180s subs
- Fall 2026 target (September–November)
