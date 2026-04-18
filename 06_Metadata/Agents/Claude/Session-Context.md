---
title: "Claude Session Context"
type: reference
tags:
  - technique
---

# Claude Session Context

Quick-reference for Claude to load at the start of a new session. Read this note first to understand the vault state and active work.

---

## Vault Overview

Astrophotography knowledge base. See `CLAUDE.md` at root for full conventions.

**Equipment:** ASI2600MC Pro (OSC color camera) + RedCat 51 (250mm f/4.9) + iOptron CEM26 + ASIAIR. Two filters: Antlia Quad Band (narrowband), Optolong L-Pro (broadband). Location: Tuntange, Luxembourg, Bortle 4.

**Key limitation:** OSC camera — no mono workflows (SHO, LRGB). Narrowband via Quad Band dual/quad-band filter on Bayer sensor.

---

## Processing Workflows

| Workflow | File | Use for |
|---|---|---|
| RGB Broadband | `04_Processing/Pixinsight/RGB-Workflow.md` | Galaxies, clusters, reflection nebulae (L-Pro) |
| QuadBand Narrowband | `04_Processing/Pixinsight/QuadBand-OSC-Workflow.md` | Emission nebulae (Quad Band) |
| HDR | `04_Processing/Pixinsight/HDR-Workflow.md` | Bright-core targets (M42, M16, M31 nucleus) |
| DBE Reference | `04_Processing/Pixinsight/DBE-Reference.md` | Gradient removal fallback |
| Workflow Gaps | `04_Processing/Pixinsight/Workflow-Gaps.md` | Topics still to clarify |
| Process Icons | `04_Processing/Pixinsight/Icon-Review.md` | PI icon inventory and updates needed |
| Modules | `04_Processing/Pixinsight/Modules.md` | Installed PI modules and scripts |

---

## Calibration

| File | Content |
|---|---|
| `04_Processing/Calibration/Master-Library.md` | Full frame inventory with SSD paths and status |
| `04_Processing/Calibration/Calibration-Strategy.md` | Dark frame building plan, filter dependency |

---

## Active Work

| Item | File | Status |
|---|---|---|
| Reprocessing Plan | `04_Processing/Reprocessing-Plan.md` | 5 priority targets |
| NGC 5746 reprocess | Priority 1 | Mid-process: stretched, BN applied, needs NXT final + curves + star reintegration |

---

## SSD Data

External SSD: `/Volumes/T7/Astrophotography/`

| Path | Content |
|---|---|
| `Objects/` | Imaging data by type → by rig |
| `Templates/Masters/` | Master calibration frames (Dark, Flat, Bias) |
| `XMARS/` | MARS databases for MGC |
| `Gaia DR3:SP/` | Gaia catalog for SPCC/SPFC |
| `Filters/` | PI filter curve CSVs |

---

## Key Lessons (from processing sessions)

1. **ImageSolver:** Never force values — fails on rotated images. Use sensitivity 0.30, exhaustive matching.
2. **MGC broadband:** MARS has no R/G/B data — use GraXpert for broadband, MGC only for narrowband.
3. **SPCC + DBE conflict:** Disable SPCC Background Neutralization when DBE was used for gradient removal.
4. **NXT v3:** No Detail parameter (removed from v2). Only Denoise + Iterations.
5. **Drizzle 2x:** Pixel size halves to 1.88 µm. ImageSolver and WBPP may need manual plate solving on drizzled output.

---

## Clippings Folder

`04_Processing/Clippings/` is a temporary inbox for:
- YouTube video transcripts clipped from Obsidian
- PI screenshots during processing sessions

**Processing rule:** Assess relevance to OSC setup → integrate into workflows if useful → delete. Mono camera content (SHO, LRGB) does not apply.

---

## Target Notes

20 objects documented in `02_Targets/` with capture history, SSD paths, and result images. See each target note for session details and processing status.

---

## Data Views & Atlases

Live, derived views — don't duplicate, route analytics questions here.

| Note | What it shows | Source of truth |
|---|---|---|
| `03_Techniques/Integration-Budget.md` | Hours per target, split by filter, as unicode bars | `integrations:` array in `05_Sessions/**/*.md` |
| `03_Techniques/Campaign-Timeline.md` | Mermaid Gantt per target + Dataview chronological log of every capture session | Same `integrations:` array |
| `03_Techniques/FOV-Atlas.md` | RedCat 51 FOV rectangles overlaid on the full sky (balcony-reachable vs blocked), plus Stellarium Oculars workflow | `scripts/fov_atlas.py` — inline `CATALOG` + `ra_deg`/`dec_deg` from `02_Targets/` |
| `03_Techniques/Seasonal-Calendar.md` | Month-by-month target selection, yearly visibility heatmap, dark-window calendar | Static; charts regenerated via matplotlib |

**Conventions:**
- Adding/updating integration hours → edit `integrations:` in the relevant session file; Dataview views refresh live.
- Adding a new target to the FOV atlas → either inline to `scripts/fov_atlas.py::CATALOG` or add `ra_deg`/`dec_deg`/`size_arcmin` to `02_Targets/{Name}.md` frontmatter, then run `python3 scripts/fov_atlas.py`.
- `/session-plan --stellarium {date}` cross-checks altitudes against Stellarium's API (localhost:8090) and captures per-target finder charts at 5.4° FOV into `05_Sessions/{year}/Finder-Charts/`.
