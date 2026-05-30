---
title: "PixInsight Open Star Cluster Workflow"
type: processing-workflow
software: "PixInsight"
tags:
  - processing/pixinsight
---

# Open Star Cluster Processing (OSC)

Processing workflow for open star clusters captured with the [[Optolong-LPro]] broadband filter on the [[ASI2600MCPro]] (OSC camera). Optimised for **star-dominated fields with no extended nebulosity**: drizzle for clean stars, star/starless separation, and a colour-pop pass on the cluster members. First used on [[Mel111-Coma]] — see [[2026-05-27-Processing]].

> Builds on the broadband [[RGB-Workflow]] but reorders the pipeline around stars as the subject. For galaxies and reflection nebulae use [[RGB-Workflow]]; for emission nebulae with the Quad Band filter use [[QuadBand-OSC-Workflow]].

## Overview

![[Open_Star_Cluster_Processing_Workflow.png]]

*Visual summary — linear data → finished cluster. The phases below give the full per-step parameters.*

---

## Phase 1: Stacking & Initial Linear Cleanup

### 1.1 WBPP — Drizzle 2×

- Calibrate and stack per [[WBPP-Reference]], loading masters from [[Master-Library]] (bias + dark + flat + dark-flat).
- **Drizzle 2×** to stop stars looking "blocky" from sensor undersampling — clusters are point-source-dominated, so drizzle resolves tight pairs cleanly.
- ⚠️ Re-verify the Image Solver default **Pixel size = 3.76 µm** before *every* launch — WBPP silently resets it to 1.88 µm after each run, which makes the per-frame solver fail (`1 solved, 3 failed`). See [[RGB-Workflow#WBPP (Weighted Batch Pre-Processing)|the WBPP pixel-size warning]].

### 1.2 DynamicCrop

- Trim stacking artefacts and uneven edges from the borders of the master frame.

### 1.3 STF — Unlinked View

- Click the **nuclear button** → **Unlink** → **nuclear button** again, to view the image clearly without a permanent colour cast. Display-only; the data stays linear.

### 1.4 GraXpert — Background Extraction (linear)

- Run [[GraXpert]] in the linear state, method **Subtraction**, smoothing factor **0.6**, to remove gradients.
- **Run a second pass** if stubborn or residual gradients remain after the first.

---

## Phase 2: Linear Correction & Denoise

### 2.1 BlurXTerminator — Correct Only

- First pass with **Correct Only** checked — fixes star shapes and tracking error while the image is still linear.

### 2.2 BlurXTerminator — Sharpen

- Second pass with **Automatic PSF** to deconvolve and sharpen the cluster stars.
- To set the PSF diameter manually instead, measure the median stellar FWHM and enter it — see [[Star-Console-Reference]] (or a PSF table). **Match the image scale**: a PSF measured on the native master must not be reused on the drizzle 2× master (stars are ~2× wider there).

### 2.3 GraXpert — Denoise (linear)

- Apply the AI denoise in the **linear** phase (strength **0.8**) to clean background grain before colour calibration.

### 2.4 FindBackground (Seti Astro)

- Run to automatically locate a neutral, star-free region for the calibration reference. Keep the preview for SPCC.

---

## Phase 3: Colour Calibration

### 3.1 ImageSolver

- Plate-solve so SPCC can match the field against Gaia. Pixel size must match the stack (**1.88 µm** for Drizzle 2×). See [[RGB-Workflow#2.2 ImageSolver]] for RANSAC troubleshooting.

### 3.2 SPCC (SpectrophotometricColorCalibration)

- Sensor **ASI2600MC Pro** (QE Sony IMX411/455/461/533/571), filter **Optolong L-Pro**.
- **White reference: G2V Star** — the correct choice for a star cluster (the subject is the stars, rendered blue → white → orange relative to the Sun). See [[RGB-Workflow#2.7 Color Calibration]].
- Background reference: the FindBackground preview from step 2.4.
- Catalog: **Gaia DR3/SP**.

### 3.3 Reset STF + Linked View

- Click **Reset Screen Transfer Function** to clear the temporary stretch, then apply a new **linked** AutoStretch to view the accurate, calibrated colours.

---

## Phase 4: Stretch to Non-Linear

### 4.1 Bills_Stretch (linked)

- Apply **Bills_Stretch_Llinked_V6** (PixelMath icon from the [[Icon-Review|icon set]]) to transition to non-linear. The **linked** stretch is essential to preserve the colour ratios established by SPCC.

---

## Phase 5: Non-Linear Starless & Star Processing

### 5.1 Star Separation

- **StarXTerminator** (or StarNet2) → a **starless** image and a **stars** image. Save both.

### 5.2 Starless Background

- **SCNR + inversion trick:** CMD+I (invert) → **SCNR (Green)** → CMD+I (re-invert). Removes both green and magenta tints.
- **NoiseXTerminator** on the starless — smooth, uniform background without touching star detail.
- **CurvesTransformation** — darken the sky and raise cluster contrast. See [[CurvesTransformation-Reference]].

### 5.3 Star Colour

- **SCNR + inversion trick** (same invert → SCNR Green → invert) applied to the stars image.
- **Star colour-pop:** drag the star mask onto the stars view — the image turns **red**, indicating the mask is active (CMD+K shows/hides the mask).
- **CurvesTransformation (Saturation)** with the mask active — boost the natural blue, orange, and white colours of the stars.

---

## Phase 6: Recombination & Final Polish

### 6.1 Recombine

- **PixelMath:** `Starless + Stars` to add the colourful stars back onto the clean, denoised background.
- For unscreened bright cluster stars, the **screen** form `~(~Starless * ~Stars)` avoids highlight clipping — see [[RGB-Workflow#4.3 Star Reintegration]].

### 6.2 LocalHistogramEqualization (LHE)

- Final LHE pass to enhance the local contrast of cluster members so individual stars stand out. See [[LHE-Reference]] — keep **Amount 0.3–0.5** (1.0 is too strong).

### 6.3 Export

- Final black-point adjustment; save as 16-bit TIFF or high-quality JPEG.
