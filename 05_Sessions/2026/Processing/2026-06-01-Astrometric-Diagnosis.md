---
title: "2026-06-01 — Astrometric Solution Failure: Root-Cause Diagnosis (Mel 111)"
type: processing-session
date: 2026-06-01
software: "PixInsight 1.9.4 (arm64) / ImageSolver 6.4.1"
targets_processed:
  - "[[Mel111-Coma]]"
tags:
  - session/processing
  - processing/pixinsight
---

# 2026-06-01 — Astrometric Solution Failure: Root-Cause Diagnosis

WBPP kept failing the **astrometric solution** on the [[2026-05-25-Capture|Mel 111]] master (`RANSAC: Unable to find a valid set of star pair matches`). This session isolated the cause step by step and produced a **permanent offline fix**.

> [!success] Root cause: the plate-solving catalog, not scale/drizzle/calibration
> The only Gaia XPSD installed was the **spectrophotometric DR3/SP** subset (`gdr3sp-*.xpsd`, for SPCC). It is too sparse and lacks bright cluster anchor stars, so RANSAC never finds consensus — even with perfect scale, center, and clean stars. **Fix:** install the **astrometric** Gaia DR3 XPSD (`gdr3-*.xpsd`) — or, online, **Gaia DR2 + manual limit-mag 16**.

---

## What was ruled OUT (and how)

| Suspect | Verdict | Evidence |
|---|---|---|
| Drizzle scale | ❌ not it | Test 1 = native, no drizzle → still `2 failed` |
| Pixel size 1.88 vs 3.76 | ❌ not it | failed at correct 3.76 native scale |
| Frame 0052 (missing RA/DEC) | ❌ not it | removed → still failed |
| Calibration (uncalibrated stack) | ❌ not it | `psf_image.py` on the master: FWHM **2.28 px**, ecc **0.45** (clean, round stars) |
| Image scale / 1.551 readout | ❌ red herring | the ASIAIR CD matrix gives **3.096 ″/px**; the 1.551 display was a stale field. Setting 3.10 did **not** fix the solve |
| Seed center | ❌ correct | computed image center from the frame WCS = **12h24m16.5s / +26°12′49″** = what we gave ImageSolver |
| **Catalog (Gaia DR3/SP)** | ✅ **root cause** | magnitude search **flatlines at 6003 stars**, maxes limit at **25.56**; switching to a full catalog solves instantly |

**Ground truth from the raw frame's ASIAIR WCS** (CD matrix): scale **3.096 ″/px**, rotation **79°**, center **12h24m16.5s / +26°12′49″**, FOV 5.37° × 3.59°. All matched our ImageSolver seed — proving the seed was never the problem.

---

## The fix (validated three ways)

1. **Online Gaia DR2, auto limit-mag (25.56):** ❌ — VizieR truncated at its **50,000-row cap**; only **24** in-frame reference stars → fail.
2. **Online Gaia DR2, manual limit-mag 16:** ✅ — 30,665 objects, 2,879 ref stars → **1,210 RANSAC inliers, RMS 0.104 px**.
3. **Local astrometric Gaia DR3 XPSD (offline):** ✅ — magnitude search behaves (target reached at **mag 15.85**, not 25.56) → **3,901 control points, RMS 0.101 px**. This is the permanent fix.

### Image scale — two equivalent ways (both validated)
`Focal 250 mm + Pixel 3.76 µm` **≡** `Resolution 3.10 ″/px` (native), linked by `206.265 × 3.76 / 250 = 3.10`. Drizzle 2× = **1.548 ″/px** (or pixel 1.88 µm). The solve's own output reports `Focal 250.41 mm`. **250 mm works** — confirmed empirically.

---

## Permanent setup (done 2026-06-01)

- Downloaded **`gdr3-1.0.0-01.xpsd`** (≤ mag 16.59, 2.8 GB) to `/Volumes/T7/Astrophotography/Gaia DR3 (astrometric)/`. (Add `-02` for margin on sparse fields.)
- Registered in **Process → Gaia → Data release: Gaia DR3 → add files**.
- **SP set kept** under data release **Gaia DR3SP** — SPCC still needs it.
- See [[Master-Library#Additional SSD Resources]].

## WBPP implication — confirmed end-to-end
WBPP's in-pipeline Astrometric Solution uses the local XPSD with automatic magnitude and **no catalog/limit override** — so it failed whenever only SP was installed. **Validated by a controlled before/after** (identical run: 51 lights, no calibration, drizzle off):

| Run | Catalog installed | Astrometric solution result |
|---|---|---|
| Test 1 (earlier) | DR3/SP only | ❌ **2 failed** |
| Test 1 redux | + DR3 astrometric XPSD | ✅ **2 solved** (46 s, offline) |

So **leave WBPP's Astrometric Solution ON** for production (offline, T7 mounted). If ever solving without the XPSD, turn WBPP's astrometric step off and solve standalone with online Gaia DR2 + limit-mag 16.

## Lessons folded into the workflows
- [[RGB-Workflow#2.2 ImageSolver]] — catalog is the #1 RANSAC cause; SP ≠ plate-solving; scale is a red herring.
- [[OpenCluster-Workflow]] §3.2 — cluster fields fail on SP.
- [[Master-Library]] — astrometric vs SP catalog, registration steps.
