---
title: "Star Console (Hidden Light Photography) Reference"
type: processing-workflow
software: "PixInsight"
script: "Star Console"
author: "Hidden Light Photography (Tony)"
source:
  - "https://www.youtube.com/watch?v=DdtkM2t_Mss"   # original release
  - "https://www.youtube.com/watch?v=n6-f8zGgQWI"   # 2025-01-13 update
repository: "https://hiddenlight-photography.com/pixinsight-scripts"
requires:
  - "PixInsight 1.9.1+"
  - "BlurXTerminator"
  - "StarXTerminator or StarNet++ (for Star Removal)"
tags:
  - processing/pixinsight
---

# Star Console — Settings Reference

Star Console is a PixInsight script by [Hidden Light Photography](https://www.youtube.com/watch?v=DdtkM2t_Mss) that automates the manual "full BlurXTerminator" loop and batches subframe FWHM checks. It replaces the tedious sequence of *extract luminance → ImageAnalysis FWHM → round to nearest 0.01 → paste into BXT PSF diameter → run* with a single click.

> **Prerequisites:** PixInsight 1.9.1+, **BlurXTerminator** (required for Full Star Correction) and **StarXTerminator** *or* **StarNet++** (for Star Removal — the 2025-01 update added StarNet++ as an alternative). For OSC images the script extracts luminance automatically; greyscale images are measured directly.

> [!info] Reflects the 2025-01-13 update
> This doc includes the update's new features: eccentricity + star count in SubFrame Star Check, BXT stellar/non-stellar sharpening sliders, StarNet++ star removal, and the New Instance batch icon.

First used in this vault on [[Mel111-Coma]] — see [[2026-05-27-Processing#Phase 2/3 — Actual Processing (completed 2026-05-30)]].

---

## Install

1. `Resources → Updates → Manage Repositories → Add` and paste the HLP repository link (from the [video description](https://www.youtube.com/watch?v=DdtkM2t_Mss) / [scripts page](https://hiddenlight-photography.com/pixinsight-scripts)). The repo contains all of HLP's scripts.
2. `Resources → Updates → Check for Updates` → Select All → OK.
3. Exit PixInsight (allow the installer to make changes if prompted); it restarts automatically.
4. Open via `Script → HLP → Star Console`.

---

## Three Modes

| Mode | Tool used | What it does |
|------|-----------|--------------|
| **SubFrame Star Check** | — | Batch-measures FWHM of selected light subframes (pre-WBPP frame culling) |
| **Full Star Correction** | BlurXTerminator | Measures median FWHM, rounds it, loads it into BXT PSF diameter, runs full BXT |
| **Star Removal** | StarXTerminator **or** StarNet++ | Removes stars → starless + stars image (SXT: unscreen or stars-only; StarNet: linear/nonlinear) |

`SubFrame Star Check` is mutually exclusive with the view-based modes (selecting it disables the view dropdown and the two correction modes).

### SubFrame Star Check (pre-WBPP frame culling)

1. Select the mode → **Add light subframe files** → pick the night's lights.
2. The script lists each frame with its measured **FWHM, eccentricity, and stars-detected** (the 2025-01 update added eccentricity + star count — originally FWHM-only) — no need to check frames individually.
3. Select outliers (e.g. high-FWHM frames late in the night) → **Save Selected** to a `bad frames` folder for inspection in Blink, or **Delete Selected** to drop them from the list.
4. **Save Remaining** → a `good frames` folder, then feed that folder straight into WBPP without worrying about FWHM.

### Full Star Correction (automated BXT)

1. Select the target view from the dropdown → check **Full Star Correction**.
2. **Measure FWHM** — for OSC the script auto-extracts luminance, then computes FWHM, eccentricity, and detected-star count, rounds FWHM, plugs it into BXT **PSF diameter**, and runs the full process.
3. The worked image is renamed with an `_StarConsole` suffix. **Back once** undoes the rename; **back again** undoes the BXT (verify the applied PSF diameter via `View → Explore → Windows History Explorer → BlurXTerminator`).
4. **Sharpening sliders (2025-01 update):** adjust BXT **Stellar** and **Non-Stellar** sharpening directly in the script — both default to **0.5** (BXT's defaults) and span BXT's full range. The process console echoes the **PSF diameter + stellar/non-stellar values** actually applied.

### Star Removal (SXT or StarNet++)

- Check **Full Star Correction + Star Removal** together → **Measure FWHM**: runs BXT, then the chosen remover, leaving a **starless image** and a **stars image**. Process each separately from there.
- **StarXTerminator:** radio choice of **unscreen stars** or **stars-only image**.
- **StarNet++ (2025-01 update):** alternative if you don't have SXT — choose **StarNet linear** (linear image) or **StarNet nonlinear** (stretched image).
- The two checkboxes are independent: run **Star Removal without** Full Star Correction (remove stars only), or **Full Star Correction without** removal (BXT only).

### New Instance — batch processing (2025-01 update)

Set your preferred options (e.g. Full Star Correction + StarXTerminator unscreen), then drag the **triangle / new-instance icon** onto the workspace to save them as an instance. **Drop that icon onto any image** and the script runs the whole chain — full BXT (with your stellar/non-stellar values) → star removal — leaving a corrected starless + stars image with no dialog. Repeatable across many frames with one drag each; the console logs the PSF diameter and sharpening values used.

---

## Notes for this rig

- On [[Mel111-Coma]] the Full Star Correction + Star Removal path was used after [[RGB-Workflow#2.7 Color Calibration|SPCC]]; the bright cluster member γ Com retained a soft blue halo on the **stars** layer — address halo/morphology on the separated stars image, not the starless.
- **SubFrame Star Check** is not yet part of the standard pre-WBPP step here — candidate to adopt so FWHM culling happens before stacking rather than via SubFrameSelector after. See [[WBPP-Reference]].
