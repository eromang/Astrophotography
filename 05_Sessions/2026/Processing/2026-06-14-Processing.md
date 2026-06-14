---
title: "2026-06-14 Processing Session — M31 Andromeda reprocess (plan)"
type: processing-session
date: 2026-06-14
software: "PixInsight"
targets_processed:
  - "[[M31-Andromeda]]"
tags:
  - session/processing
---

# 2026-06-14 — M31 Andromeda Reprocess (PLAN)

> [!info] This is a reprocess PLAN, not an as-executed log
> Convert each step to as-executed (stats, decisions, files) once run. Pivoted here from NGC 7000 because M31 was shot through the **correct filter** (L-Pro broadband for a galaxy → pure upside), whereas NGC 7000 is emission shot broadband (filter-limited; re-capture with FQuad is its real fix).

## Why reprocess

- **Biggest dataset you have** — 254 raw subs, and it's a showpiece galaxy that fits the RedCat FOV (178′ < 216′).
- **Processed in 2024 (Result1 / Result2), pre-lessons** — before the May–June workflow improvements (astrometric re-solve, WBPP pixel-size discipline, MARS/MGC gradient strategy, SPCC/genuine-flat fixes from the [[2026-06-01-Processing|Mel 111 saga]]).
- **Correct filter** ([[Optolong-LPro]], broadband) — so a modern pass is all upside, no filter ceiling.

## Source data

| Field | Value |
|---|---|
| Lights | 254 raw (~197 used per [[M31-Andromeda]]) × **60 s** ≈ **3.3–4.2 h** |
| Filter | [[Optolong-LPro]] (broadband) — *blank in FITS keyword + filename; confirmed via target note* |
| Gain / Temp | 100 / −10 °C (−9.8 to −9.9 °C actual) |
| Nights | 2024-09-28, 2024-10-23, 2024-11-03 |
| Existing master | `…/M31_Andromeda/2024/MultiNights/Result2/master/…RGB_drizzle_2x_autocrop.xisf` — **already plate-solved**, 1.552″/px (drizzle 2×), 11656×7256 |

## Starting point — decide first

1. **Fast path:** reprocess from the existing **solved drizzle-2× master** (integration already done). Good if a quick `frame_info`/Blink check shows the stack is clean.
2. **Thorough path (recommended):** **re-stack via WBPP** with current discipline — better rejection + Local Normalization + the calibration validation below. 60 s subs over 3 nights benefit from a fresh, well-weighted integration.

> [!warning] WBPP pixel-size trap (if re-stacking)
> WBPP silently resets the ImageSolver **Pixel size 3.76 → 1.88 µm** after each run. **Re-verify 3.76 µm before every launch** or per-frame solving fails (1 solved / N failed). See [[WBPP-Reference]].

## Calibration (validate before stacking)

| Type | Exposure | Master | Check |
|---|---|---|---|
| Dark | 60 s | `Masters/Dark/masterDark_…EXPOSURE-60.00s.xisf` | ✅ exists |
| Flat | — | `Masters/Flat/LPro/…` | confirm L-Pro flats match the 2024 train |
| Dark-flat | 60 ms | `Masters/DarkFlat/…` | ✅ |
| Bias | — | [[Master-Library]] | ✅ |

```bash
# validate calibration matches the lights BEFORE WBPP (new --match mode)
python3 scripts/frame_info.py "<M31 lights>" --match lights-darks --against "<60s darks>"
python3 scripts/frame_info.py "<L-Pro flats>" --match flats-flatdarks --against "<60ms flat-darks>"
```

## Workflow — [[RGB-Workflow]] (broadband OSC), modern pass

**Phase 2 (linear):**
1. **ImageSolver** — master is already solved; re-verify it carries WCS (`frame_info <master>`) so SPCC/MGC work. Re-solve if `--match`/re-stack produced a fresh, unsolved master.
2. **Gradient removal — MARS/MGC** (not the old ABE/GraXpert): SPFC → MGC, scale 512–1024, per-channel scale-factor tuning on a preview; BackgroundNeutralization for residual cast. See [[MGC-Reference]].
3. **BlurXTerminator — Correct Only**, then **Sharpen** — measure the PSF first:
   ```bash
   python3 scripts/psf_image.py "<M31 master>" --beta 4   # FWHM → BXT PSF diameter
   ```
4. **FindBackground** reference → **SPCC** with **L-Pro filter curves** (Sony CMOS + L-Pro), then BN.

**Phase 3 (non-linear):**
5. Stretch, BackgroundNeutralization, NoiseReduction on the starless.

**Phase 4:** star processing + reintegration.

## M31-specific guidance

- **HDR core:** the nucleus is bright vs the faint outer disk — use **HDRMultiscaleTransform** (or dual-stretch + blend) to recover core/dust-lane detail without crushing the arms.
- **Colour:** preserve the **blue OB associations + red Ha knots** (NGC 206) and the **dust lanes**; push saturation carefully post-SPCC.
- **Companions:** **M32 and M110** sit in the wide field — frame/stretch so they're not clipped.
- **Depth expectation (be realistic):** 60 s subs protect the core but the **faint outer halo/IFN is noise-limited** at ~4 h from Bortle 4 — aim for a clean, sharp main disk, not deep faint structure. More integration (or longer subs on the outskirts) is the future upgrade, not reprocessing.
- **Stars:** RedCat star halos + a dense Andromeda starfield → BXT + modest star reduction after separation.

## Success criteria

- [ ] Sharper core/dust-lane detail than Result2 (BXT + HDR)
- [ ] Flat background, neutral (MARS/MGC + SPCC + BN) — no ABE-style residual gradient
- [ ] M32 + M110 retained, natural galaxy colour
- [ ] Update [[M31-Andromeda]] capture-history "accepted" counts + link this session

## Calibration Frames Used

| Type | Exposure | Count | Master |
|------|----------|-------|--------|
| Dark | 60 s | | `masterDark_…60.00s.xisf` |
| Flat | — | | `Flat/LPro/…` |
| Dark Flat | 60 ms | | |
| Bias | — | | [[Master-Library]] |

## Notes

- Tools: [[RGB-Workflow]], [[MGC-Reference]], `scripts/psf_image.py` (BXT PSF), `scripts/frame_info.py --match` (calibration check), [[Star-Console-Reference]] (BXT + star removal batch).
- The old Result1/Result2 masters are kept as before/after comparison — don't overwrite.
