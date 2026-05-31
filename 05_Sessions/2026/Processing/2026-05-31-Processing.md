---
title: "2026-05-31 Processing Session — Mel 111 reprocess (halo fix, as-executed)"
type: processing-session
date: 2026-05-31
software: "PixInsight 1.9.4 (arm64)"
targets_processed:
  - "[[Mel111-Coma]]"
tags:
  - session/processing
---

# 2026-05-31 — Mel 111 Reprocess (as-executed)

Reprocess of the [[2026-05-25-Capture|2026-05-25 Mel 111 dataset]] to fix the **γ Com bloated-blue-halo** from the [[2026-05-27-Processing|first run]]. Followed [[OpenCluster-Workflow]] **with all enhancements applied** (this run validated them; they are now folded into that workflow). Started from the existing WBPP master (WBPP + DynamicCrop **not** re-run). Every setting below is the value actually used, with deviations from the base workflow flagged.

> **Validation (SubFrameSelector / PSF, on the master):** Ecc **0.63 → 0.35 → 0.38**, FWHM **3.105 → 2.184 px (−30%)** after Sharpen, stars detected 5967 → 6935, background median 0.021 → 0.0094 (gradient removed). See the metric tables at the end.

---

## 1. Pre-Processing & Initial Linear Cleanup

- **WBPP (Drizzle 2×):** *not re-run this session* — reused the existing production master (`…_drizzle_2x_autocrop.xisf`, astrometric solution already embedded). Original stack: 52 × 120 s L-Pro, Drizzle 2×.
- **Dynamic Crop:** *skipped* — the reused master was already cropped.
- **STF (Screen Transfer Function):** Nuclear button → **Unlink** → Nuclear again, to view without a colour cast (display only; data stays linear).
- **GraXpert (Background Extraction):** linear, **Subtraction** method, smoothing **0.7** *(↑ from the base 0.6 — chose higher smoothing to protect the faint Coma background galaxies under the moon gradient)*. **Run twice** to clear residual gradient. Result: background median 0.021 → 0.0094.

## 2. Linear Phase Correction & Denoising

- **BlurXTerminator — Pass 1 (Correct Only):** fixed star shapes / tracking while linear. **This is what corrected the systematic eccentricity** (0.63 → 0.35).
- **BlurXTerminator — Pass 2 (Sharpen):** deconvolution + sharpen, with the ★ halo control:
  - PSF Diameter: **Automatic** (measured median FWHM was 3.07 px — auto landed equivalently)
  - Sharpen Stars: **0.25**
  - **Adjust Star Halos: −0.15** *(★ enhancement — the primary γ Com halo fix at the source)*
  - Sharpen Nonstellar: **0.70** *(↓ from generic 0.90 — SNR was only 3.9; avoids amplifying background grain)*
  - Result: FWHM 3.105 → **2.184 px (−30%)**, Ecc still round (0.38), stars +968.
- **GraXpert Denoise (Linear):** strength **0.5** *(↓ from base 0.8 — ★ avoids double-denoise since NXT runs on the starless later)*. Recovered the ~20 % SNR lost to deconvolution.
- **Seti Astro FindBackground:** auto-located a neutral star-free region; preview kept for SPCC.

## 3. Color Calibration (SPCC)

- **ImageSolver:** *skipped* — the master already carried an embedded astrometric solution from WBPP, so SPCC used it directly.
- **SPCC (SpectrophotometricColorCalibration):** sensor **ASI2600MC Pro** (QE Sony IMX411/455/461/533/571), filter **Optolong L-Pro**, **White reference G2V Star** *(correct for a star cluster — subject is the stars)*, background reference = the FindBackground preview, catalog **Gaia DR3/SP**, Neutralize background on.
- **Reset STF:** Reset Screen Transfer Function, then a new **linked** AutoStretch to view the calibrated colours.

## 4. Stretching to Non-Linear

- **Bills_Stretch_Llinked_V6:** applied the **linked** PixelMath stretch to go non-linear, preserving the SPCC colour ratios.

## 5. Non-Linear Starless Processing

- **Star Separation:** **StarXTerminator** → starless + stars images (both saved).
- **SCNR & Inversion:** on the starless — CMD+I → **SCNR (Green)** → CMD+I. Removes green and magenta.
- **NoiseXTerminator (on starless):** **Iterations 1** *(★ lighter — already denoised in linear)*.
- **Background Refinement — ★ galaxy-protected CurvesTransformation:**
  - Built a **background mask** with **RangeSelection** (Upper Limit **0.22**, Lower 0, Lightness on, feathered) — white = empty sky, black = galaxy cores / bright structure. Applied to the starless (red overlay on the galaxies = protected).
  - **CurvesTransformation (RGB/K):** gentle sky-deepen anchored to protect the shadows — points ≈ **(0,0) · (0.10, 0.085) · (0.25, 0.23) · (1,1)**. **Background median kept ≈ 0.10, NOT clipped to black** *(★ keeps the faint Coma galaxies alive)*. Mask removed afterward.

## 6. Non-Linear Star Processing

- **SCNR & Inversion:** on the stars image — CMD+I → SCNR (Green) → CMD+I.
- **★ Bright-star reduction (2nd half of the halo fix):**
  - **StarMask** on the *stars* image to isolate **only the bright members**: Noise threshold **0.15**, Scale **6**, Large-scale growth **3**, Smoothness **16**, Mask Preprocessing **Shadows 0.30** (clips faint stars to black), Invert **off**. White = bright stars, black = faint/background.
  - Applied (red overlay on the faint stars = protected) → **MorphologicalTransformation:** Operator **Erosion (Minimum)**, **Interlacing 1**, structuring element **3×3 (9 elements, solid)**, Iterations **1**, Amount **0.50**. Shrinks the bloated bright stars (γ Com). Mask removed.
- **Star Colour Pop:** **CurvesTransformation (Saturation)** — gentle upper-mid boost on the stars-only image (no mask needed) to bring out the blue/orange/white star colours.

## 7. Recombination

- **PixelMath:** screen recombine **`~(~starless * ~stars)`** *(↑ from the base `Starless + Stars` — screen avoids clipping the bright cluster members)* to add the stars back onto the clean background.

## 8. Final Polish

- **LocalHistogramEqualization (LHE):** applied (light) for local contrast on the cluster members.
- **ICCProfileTransformation → sRGB** *(★ correct colour space for web/JPEG export)*.
- **Export:** final black-point adjustment; saved 16-bit TIFF / high-quality JPEG.

---

## Deviations from the base workflow (summary)

| Step | Base | This run | Reason |
|---|---|---|---|
| WBPP / DynamicCrop | run | **skipped** | reused existing solved master |
| GraXpert smoothing | 0.6 | **0.7** | protect faint Coma galaxies |
| BXT Sharpen halos | — | **−0.15** | γ Com halo fix (★) |
| BXT Nonstellar | 0.90 | **0.70** | low SNR (3.9) |
| GraXpert Denoise | 0.8 | **0.5** | avoid double-denoise (★) |
| ImageSolver | run | **skipped** | solution already embedded |
| Starless curve | plain darken | **masked + bg floor ≈0.10** | protect galaxies (★) |
| Star reduction | — | **StarMask Shadows 0.30 → MT Erosion 3×3, interlace 1, amt 0.50** | shrink bright members (★ #2b) |
| Recombine | `Starless + Stars` | **`~(~starless * ~stars)`** | avoid clipping bright stars |
| Export | TIFF/JPEG | **+ ICCProfileTransformation → sRGB** | colour-correct export (★) |

## Validation metrics (SubFrameSelector / PSF, on the master)

| Metric | Baseline subs (median) | After GraXpert + BXT Correct | After BXT Sharpen |
|---|---|---|---|
| FWHM | 2.28 px (7.06″) | 3.105 px | **2.184 px (−30%)** |
| Eccentricity | 0.630 | 0.349 | 0.379 |
| Stars | ~1045 / sub | 5967 | **6935** |
| SNR | 1.30 / sub | 3.90 | 3.14 (deconvolution cost) |
| Background median | 0.0211 | 0.0094 | 0.0094 |

**Outcome:** systematic eccentricity (0.63) corrected to ~0.38; residual cross-field eccentricity variation (~0.11) persists → capture-side lead is **sensor tilt** for the next cluster. γ Com halo addressed via BXT −0.15 + MorphologicalTransformation erosion (visual confirmation pending). See [[Mel111-Coma]].
