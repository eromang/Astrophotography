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
| RGB Broadband | `04_Processing/Pixinsight/RGB-Workflow.md` | Galaxies, reflection nebulae (L-Pro) |
| Open Star Cluster | `04_Processing/Pixinsight/OpenCluster-Workflow.md` | Star clusters — drizzle, star/starless separation, colour-pop (L-Pro) |
| QuadBand Narrowband | `04_Processing/Pixinsight/QuadBand-OSC-Workflow.md` | Emission nebulae (Quad Band) |
| HDR | `04_Processing/Pixinsight/HDR-Workflow.md` | Bright-core targets (M42, M16, M31 nucleus) |
| DBE Reference | `04_Processing/Pixinsight/DBE-Reference.md` | Gradient removal fallback |
| Workflow Gaps | `04_Processing/Pixinsight/Workflow-Gaps.md` | Topics still to clarify |
| Process Icons | `04_Processing/Pixinsight/Icon-Review.md` | PI icon inventory and updates needed |
| Modules | `04_Processing/Pixinsight/Modules.md` | Installed PI modules and scripts |
| Star Console | `04_Processing/Pixinsight/Star-Console-Reference.md` | HLP script — auto FWHM→BXT + SXT star removal; SubFrame Star Check |

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
| Mel 111 first light | `05_Sessions/2026/Processing/2026-05-31-Processing.md` | **Reprocessed 2026-05-31** (BXT Halos −0.15 + MorphologicalTransformation; Ecc 0.63→0.38, FWHM −30%); new export is the vault result image. **γ Com halo reduced, soft blue residual remains** → re-stack candidate once a real L-Pro flat is shot (residual is likely uncorrected L-Pro filter reflection) |
| Calibration library reorg | `04_Processing/Calibration/Master-Library.md` | **Done 2026-05-31** — T7 `Templates/` reorganized by filter-independence (Bias/Dark/DarkFlat by type, Flat by filter); 17 masters + 881 raws verified; dup + mislabeled-L-Pro masters removed; 0 ms bias & two FQuad flats clarified |
| L-Pro flat | `04_Processing/Calibration/Master-Library.md` | **✅ Done 2026-05-31** — first genuine L-Pro flat shot + built (50 × 10 ms → `Masters/Flat/LPro/`); calibration library now complete. **Follow-up: re-stack Mel 111** with the real flat (candidate γ Com halo fix) |
| Astrometric solve failure | `05_Sessions/2026/Processing/2026-06-01-Astrometric-Diagnosis.md` | **✅ Resolved 2026-06-01** — WBPP/ImageSolver RANSAC failures root-caused to the catalog: only Gaia DR3/**SP** (SPCC-only) was installed. Installed the **astrometric** Gaia DR3 XPSD (`gdr3-1.0.0-01.xpsd` → T7 `Gaia DR3 (astrometric)/`); WBPP in-pipeline solve now **2 solved** (was 2 failed). Scale/drizzle/force-values were red herrings |

---

## SSD Data

External SSD: `/Volumes/T7/Astrophotography/`

| Path | Content |
|---|---|
| `Objects/` | Imaging data by type → by rig |
| `Templates/Masters/` | Master calibration frames — Bias / Dark / DarkFlat (by type), Flat/{LPro,FQuad,NoFilter} (by filter); see [[Master-Library]] |
| `XMARS/` | MARS databases for MGC |
| `Gaia DR3:SP/` | Gaia **spectrophotometric** catalog — **SPCC/SPFC only** (too sparse to plate-solve) |
| `Gaia DR3 (astrometric)/` | Gaia **astrometric** catalog (`gdr3-*.xpsd`) for **plate-solving** (ImageSolver/WBPP) — added 2026-06-01 |
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
