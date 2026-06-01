---
title: "PixInsight Open Star Cluster Workflow"
type: processing-workflow
software: "PixInsight"
tags:
  - processing/pixinsight
---

# Open Star Cluster Processing (OSC)

Processing workflow for open star clusters captured with the [[Optolong-LPro]] broadband filter on the [[ASI2600MCPro]] (OSC camera). Optimised for **star-dominated fields with no extended nebulosity**: drizzle for clean stars, star/starless separation, dedicated bright-star halo control, and a colour-pop pass on the cluster members.

> Builds on the broadband [[RGB-Workflow]] but reorders the pipeline around stars as the subject. For galaxies and reflection nebulae use [[RGB-Workflow]]; for emission nebulae with the Quad Band filter use [[QuadBand-OSC-Workflow]].

> [!success] Validated end-to-end on [[Mel111-Coma]] — see [[2026-05-31-Processing]] (Ecc 0.63 → 0.38, FWHM −30 %, γ Com halo fixed). The settings below are the proven values from that run.

## Overview

![[Open_Star_Cluster_Processing_Workflow.png]]

*Visual summary — linear data → finished cluster. The phases below give the full per-step parameters.*

---

## Phase 1: Frame Selection, Stacking & Initial Linear Cleanup

### 1.1 Frame Selection (fresh captures)

On a cluster the **stars are the subject**, so cull bad subs *before* stacking — a single bloated/trailed/twilight sub degrades the integrated star shapes more than it would in nebula work. *(Skip when reprocessing an existing master.)*

- **Star Console** (fast path): `Script → HLP → Star Console` → **SubFrame Star Check** → add the night's lights → it lists each frame's FWHM → save high-FWHM outliers to a `bad frames` folder (or delete) → **Save Remaining** to `good frames` → feed that into WBPP. See [[Star-Console-Reference]].
- **SubFrameSelector** (full control): as [[RGB-Workflow#SubFrameSelector]] but tighten the star metrics — approval `Median < 0.028 && FWHM < 8.5 && Eccentricity < 0.75` (vs the broadband 9.5 / 0.80; cluster stars expose softness/elongation nebulosity hides), weighting `(1/(FWHM*FWHM)) * SNR * (1 - Eccentricity)`.

### 1.2 WBPP — Drizzle 2×

- Calibrate and stack per [[WBPP-Reference]], loading masters from [[Master-Library]] (bias + dark + flat + dark-flat).
- **Drizzle 2×** to stop stars looking "blocky" from sensor undersampling — clusters are point-source-dominated, so drizzle resolves tight pairs cleanly.
- ⚠️ Re-verify the Image Solver default **Pixel size = 3.76 µm** before *every* launch — WBPP silently resets it to 1.88 µm after each run, which makes the per-frame solver fail (`1 solved, 3 failed`). See [[RGB-Workflow#WBPP (Weighted Batch Pre-Processing)|the WBPP pixel-size warning]].

### 1.3 DynamicCrop

- Trim stacking artefacts and uneven edges from the borders of the master frame.

### 1.4 STF — Unlinked View

- Click the **nuclear button** → **Unlink** → **nuclear button** again, to view the image clearly without a colour cast. Display-only; the data stays linear.

### 1.5 GraXpert — Background Extraction (linear)

- Run [[GraXpert]] in the linear state, method **Subtraction**, smoothing **0.6–0.7**. **Use 0.7 for moon-affected fields** — the higher smoothing keeps faint background galaxies out of the gradient model (validated on Mel 111).
- **Run a second pass** if stubborn or residual gradients remain after the first.
- Verify the background *model* shows no stars/galaxies before accepting; if it does, raise smoothing.

---

## Phase 2: Linear Correction & Denoise

### 2.1 BlurXTerminator — Correct Only

- First pass with **Correct Only** checked — fixes star shapes and tracking error while linear. **This corrects field eccentricity** (Mel 111: 0.63 → 0.35).

### 2.2 BlurXTerminator — Sharpen

Second pass — deconvolve and sharpen, with explicit halo control (the primary bright-star/halo fix):

| Parameter | Value | Note |
|---|---|---|
| PSF Diameter | **Automatic** | or the measured median FWHM — offline via `python3 scripts/psf_image.py <image>` (see [[../../scripts/README.md#psf_image.py — offline PSF / FWHM measurement (PixInsight PSFImage equivalent)|scripts/README]]). ⚠️ match image scale — a PSF measured on the native master must not be reused on the drizzle 2× master (stars ~2× wider) |
| Sharpen Stars | **0.25** | moderate; soft data + bright members artefact first if pushed high |
| **Adjust Star Halos** | **−0.15** | ⭐ the key knob — pulls in the bloated blue halo at the source (−0.10 for milder fields) |
| Sharpen Nonstellar | **0.70** | ↓ from the generic 0.90 — modest cluster SNR; avoids amplifying background grain |

> Validated: FWHM 3.10 → 2.18 px (−30 %), stars stayed round (Ecc 0.38). After running, inspect the brightest stars at 1:1 — if dark rings appear, ease Halos to −0.10 / Stars to 0.20 and redo (BXT is single-shot).

### 2.3 GraXpert — Denoise (linear)

- AI denoise in the **linear** phase, strength **0.5** — kept light because NXT runs again on the starless in Phase 5 (avoid double-denoising a sparse field). Recovers the ~20 % SNR that deconvolution costs.

### 2.4 FindBackground (Seti Astro)

- Run to automatically locate a neutral, star-free region for the calibration reference. **Keep the preview** for SPCC.

---

## Phase 3: Colour Calibration

### 3.1 SPFC (optional)

- Optional flux calibration before SPCC — harmless and improves the photometric footing. QE Sony IMX571, filter L-Pro, Gaia DR3/SP, PSF growth 1.75. **Required only** if you switch gradient removal to [[MGC-Reference|MGC]].

### 3.2 ImageSolver (skip if already solved)

- Only needed if the master lacks an astrometric solution. WBPP normally embeds one, so SPCC reads it directly — **skip this step** unless SPCC complains. If needed: pixel size matches the stack (1.88 µm for Drizzle 2×), sensitivity 0.30, don't force values. See [[RGB-Workflow#2.2 ImageSolver]].
- ⚠️ **Cluster fields fail to solve if the local catalog is Gaia DR3/SP.** A dense cluster needs the **astrometric** Gaia DR3 XPSD (`gdr3-*.xpsd`) — the SP subset lacks the bright anchor stars and the solve dies with `RANSAC: Unable to find a valid set of star pair matches` even when scale/center are perfect. If you lack the astrometric XPSD, use **Online → Gaia DR2 + limit-mag 16**. Full root cause: [[../../05_Sessions/2026/Processing/2026-06-01-Astrometric-Diagnosis]].

### 3.3 SPCC (SpectrophotometricColorCalibration)

- Sensor **ASI2600MC Pro** (QE Sony IMX411/455/461/533/571), filter **Optolong L-Pro**.
- **White reference: G2V Star** — the correct choice for a star cluster (subject is the stars, rendered blue → white → orange relative to the Sun). See [[RGB-Workflow#2.7 Color Calibration]].
- Background reference: the FindBackground preview from step 2.4.
- Catalog: **Gaia DR3/SP**. Neutralize background on.

### 3.4 Reset STF + Linked View

- Click **Reset Screen Transfer Function** to clear the temporary stretch, then apply a new **linked** AutoStretch to view the accurate, calibrated colours.

---

## Phase 4: Stretch to Non-Linear

### 4.1 Bills_Stretch (linked)

- Apply **Bills_Stretch_Llinked_V6** (PixelMath icon from the [[Icon-Review|icon set]]) to transition to non-linear. The **linked** stretch is essential to preserve the colour ratios established by SPCC.

---

## Phase 5: Non-Linear Starless & Star Processing

### 5.1 Star Separation

- **StarXTerminator** (or StarNet2) → a **starless** image and a **stars** image. Save both — the stars image is also a star-mask source.

### 5.2 Starless Background

- **SCNR + inversion trick:** CMD+I (invert) → **SCNR (Green)** → CMD+I (re-invert). Removes green and magenta tints.
- **NoiseXTerminator** on the starless — **Iterations 1** (light; you already denoised in linear). Over-denoising flattens low-SNR galaxy cores into the background.
- **Galaxy-protected CurvesTransformation** — cluster fields (e.g. Coma) are scattered with faint background galaxies; darkening the sky naively erases them. So:
  1. Build a **background mask** — `RangeSelection` on the starless (Lightness on, **Upper Limit ≈ 0.22**, lower the limit until the faint galaxies turn black while the empty sky stays white; Fuzziness ≈ 0.2, Smoothness ≈ 15). Apply it — **red overlay must land on the galaxies** (protected), sky clear. *(Don't invert — the area you want to darken must NOT be red.)*
  2. **CurvesTransformation (RGB/K):** a shallow sag in the lower third only, anchored so the shadows don't collapse — e.g. points **(0,0) · (0.10, 0.085) · (0.25, 0.23) · (1,1)**. **Keep the background median ≈ 0.08–0.12 — do NOT clip the black point.** That's what saves the faint galaxy halos the mask can't catch.
  3. **Mask → Remove Mask** afterward.

### 5.3 Star Colour & Bright-Star Reduction

Work on the **stars** image:

1. **SCNR + inversion trick** (same invert → SCNR Green → invert) to clear green/magenta star fringes.
2. **Bright-star reduction** (2nd half of the halo fix) — shrink only the bloated bright members:
   - **StarMask** on the stars image, biased to bright stars: Noise threshold **0.15**, Scale **6**, Large-scale growth **3**, Smoothness **16**, Mask Preprocessing **Shadows 0.30** (clips faint stars to black), **Invert off**. Result: white = bright members, black = faint/background. *(Alternatively use the SXT stars image directly as a mask if you want to affect all stars.)*
   - Apply it — **red on the faint stars** (protected) — then **MorphologicalTransformation:** Operator **Erosion (Minimum)**, **Interlacing 1**, structuring element **3×3 (9 elements, solid)**, Iterations **1**, Amount **0.50**. Shrinks γ Com-class stars. Bump to 5×5 / 2 iterations if not enough; drop Amount to 0.30 if stars look pinched. **Remove Mask**.
3. **Star colour-pop:** **CurvesTransformation → Saturation (S)** — a gentle upper-mid boost. Keep it subtle; colour is already SPCC-calibrated. No mask needed (stars-only image).

---

## Phase 6: Recombination & Final Polish

### 6.1 Recombine

- **PixelMath:** screen form **`~(~Starless * ~Stars)`** — avoids clipping the bright cluster members (preferred over additive `Starless + Stars`). See [[RGB-Workflow#4.3 Star Reintegration]].

### 6.2 LocalHistogramEqualization (LHE)

- **Optional / use sparingly on clusters.** A star field is mostly empty sky + tiny galaxies, so LHE mainly risks amplifying background noise and re-introducing star halos. If used: **Amount 0.3**, Kernel Radius ~100, Contrast Limit ~1.8, and **mask the background** so it only touches the cluster/galaxy regions. See [[LHE-Reference]]. Otherwise skip.

### 6.3 Colour-Space Conversion

- **ICCProfileTransformation → sRGB IEC61966-2.1**, rendering intent Relative Colorimetric — correct colour for web/JPEG export (without it, exports can look desaturated/shifted).

### 6.4 Export

- Final black-point adjustment; save as 16-bit TIFF and/or high-quality JPEG.

---

## Notes & awareness

- **Cumulative denoising:** GraXpert Denoise (1.4 here is *extraction*; 2.3 is *denoise*) + NXT on the starless (5.2) is two denoise passes — keep both light on a sparse field.
- **Background neutralization:** this flow relies on SPCC's internal *Neutralize background* + the SCNR-invert trick; there's no standalone BackgroundNeutralization like [[RGB-Workflow#3.2 Background Neutralization]].
- **Residual eccentricity** across the field (Mel 111 ~0.11 mean deviation) is a capture-side **sensor-tilt** signature BXT can't fully undo — chase tilt/spacing before the next cluster.
