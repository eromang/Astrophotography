---
title: "PixInsight HDR Workflow"
type: processing-workflow
software: "PixInsight"
tags:
  - processing/pixinsight
---

# HDR Processing

Workflow for high dynamic range targets — objects with a bright core surrounded by faint extended structure. This workflow replaces the stretch phase of either parent workflow.

> **This is not a standalone workflow.** Complete the linear processing phase of your parent workflow first, then use this for the stretch + HDR recovery steps, then return to the parent workflow for star reintegration and export.

---

## When to Use

Use this workflow when a standard stretch either clips the bright core or leaves faint outer regions invisible. Typical HDR targets have a brightness ratio of 100:1 or more between core and periphery.

| Target Type | Example | HDR Challenge |
|---|---|---|
| Bright core emission nebula | [[M42-Orion]], M16, M17 | Bright ionized core vs faint outer Ha |
| Galaxy with bright nucleus | M31, [[M64]] | Nucleus saturates before spiral arms appear |
| Supernova remnant | NGC 6960/6992 (Veil) | Bright filaments vs faint diffuse emission |

---

## Entry Point

Start with a **linear, starless, noise-reduced RGB image** (stars already removed and saved separately).

| Coming from | Enter after |
|---|---|
| [[RGB-Workflow]] | Step 2.10 — NoiseXTerminator on starless |
| [[QuadBand-OSC-Workflow]] | Phase 3.4 — Channel reassembly (ChannelCombination) |

---

## Method A: MAS + HDRMT (Recommended)

MAS (MultiscaleAdaptiveStretch) compresses dynamic range *during* the stretch, preserving highlight detail that HDRMT can then recover. This produces cleaner results than stretching first and recovering after.

### A.1 Background Reference

Select a preview on a dark sky area free of nebulosity. MAS uses this region to compute the median for delinearization. Without a reference, the median includes nebula pixels, producing a darker result.

### A.2 MAS Delinearization

**MultiscaleAdaptiveStretch**

| Parameter | Value | Notes |
|---|---|---|
| Color saturation | **Disabled** | Mandatory — prevents out-of-gamut artifacts that HDRMT amplifies |
| Target background | 0.15 | Default, works for most images |
| Contrast recovery | Enabled | Compensates for DR compression flattening faint regions |

**Tuning intensity + aggressiveness:**

These two parameters work as a pair:

1. Increase **dynamic range compression** until bright core structures are visible
2. Set contrast recovery **intensity** to 0.5 as starting point
3. Increase **aggressiveness** for more shadow contrast
4. Decrease **intensity** to compensate (aggressiveness and intensity are inversely related)
5. Watch for shadow clipping — if the faintest structures disappear, aggressiveness is too high

> **Test on previews.** Create 4–5 previews with different intensity/aggressiveness pairs before applying to the main view.

Apply to main view when satisfied.

### A.3 HDRMT (HDR Multiscale Transform)

**HDRMultiscaleTransform**

| Parameter | Value | Notes |
|---|---|---|
| Lightness mask | **Enabled** | Restricts effect to highlights — no processing in shadows |
| Deringing | **Enabled, 0.05** | Controls ringing artifacts from multiscale algorithm |
| Intensity | 0.5–0.75 | Start at 0.5, increase if core detail is still clipped |

**Workflow:**
1. Create previews of the bright core region
2. Apply HDRMT at intensity 0.25, 0.5, 0.75, and 1.0 on separate previews
3. Compare — choose the value that reveals core structure without flattening contrast
4. Apply to main view

> **Deringing caution:** Values above 0.05 can cause artifacts. These are easy to spot — if you see dark halos around bright structures, reduce deringing. For most images 0.03–0.05 is sufficient.

### A.4 Color Enhancement

**CurvesTransformation** — Saturation channel

Draw a curve that:
- **Boosts** low-saturation colors (highlight regions where HDRMT revealed detail)
- **Preserves** already-saturated regions (nebulosity that didn't need recovery)

This means a steep rise on the left side of the saturation curve, flattening toward the right.

**BackgroundNeutralization** if a color cast remains after the stretch.

### A.5 Return to Parent Workflow

| Return to | Resume at |
|---|---|
| [[RGB-Workflow]] | Phase 4 — Star Processing & Reintegration |
| [[QuadBand-OSC-Workflow]] | Phase 5 — Star Processing |

---

## Method B: GHS + HDRMT (Alternative)

Use when GHS is preferred for finer midtone control, or when the target has moderate (not extreme) dynamic range.

> **Why MAS is preferred:** MAS compresses dynamic range *during* the stretch, so HDRMT has more data to work with. GHS stretches first, potentially clipping highlights before HDRMT can recover them. GHS + HDRMT is a fallback.

### B.1 Background Reference

Same as A.1.

### B.2 GHS Stretch

**GeneralizedHyperbolicStretch**

- Set Symmetry Point (SP) near the histogram peak
- Apply multiple small stretches rather than one aggressive pass
- No built-in dynamic range compression — the bright core will clip more than with MAS

### B.3 HDRMT

Same process as A.3, but with higher intensity:

| Parameter | Value | Notes |
|---|---|---|
| Lightness mask | **Enabled** | Same as Method A |
| Deringing | **Enabled, 0.05** | Same as Method A |
| Intensity | **0.75–1.0** | Higher than Method A — compensates for GHS not pre-compressing DR |

### B.4 Color Enhancement

Same as A.4.

### B.5 Return to Parent Workflow

Same as A.5.

---

## Parameter Reference

Starting points by target class. Adjust per image based on preview comparisons.

### MAS Parameters

| Target Class | Example | Aggressiveness | Intensity | DR Compression |
|---|---|---|---|---|
| Bright core nebula | M42, M16, M17 | 0.85 | 0.35 | High |
| Supernova remnant | Veil Nebula | 0.70 | 0.50 | Moderate |
| Galaxy with bright nucleus | M31, M64 | 0.60 | 0.50 | Low–Moderate |

### HDRMT Parameters

| Target Class | HDRMT Intensity (after MAS) | HDRMT Intensity (after GHS) | Deringing |
|---|---|---|---|
| Bright core nebula | 0.50–0.75 | 0.75–1.00 | 0.05 |
| Supernova remnant | 0.25–0.50 | 0.50–0.75 | 0.03 |
| Galaxy with bright nucleus | 0.25–0.50 | 0.50–0.75 | 0.03 |

> Bright core nebula values sourced from PixInsight official MAS video (M42 example). Other target classes are extrapolated starting points — update these as you process more targets.

---

## Exit Point

After completing the HDR stretch + recovery + color enhancement, return to the parent workflow:

| Return to | Resume at |
|---|---|
| [[RGB-Workflow]] | Phase 4 — Star Processing & Reintegration |
| [[QuadBand-OSC-Workflow]] | Phase 5 — Star Processing |

---

## Future Addition

**Multi-exposure HDR composition** — combining short exposures (e.g., 30s for M42 trapezium) with long exposures (e.g., 300s for outer nebulosity) using HDRComposition or EZ_HDR *before* entering this workflow. This produces a wider dynamic range master stack as input.
