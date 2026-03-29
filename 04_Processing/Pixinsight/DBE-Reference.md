---
title: "DynamicBackgroundExtraction Reference"
type: processing-workflow
software: "PixInsight"
tags:
  - processing/pixinsight
---

# DynamicBackgroundExtraction (DBE) Reference

Fallback gradient removal tool when GraXpert or MGC don't fully correct the background. DBE gives manual control over sample placement for stubborn or localized gradients.

> Used in [[RGB-Workflow]] and [[QuadBand-OSC-Workflow]] as a fallback when GraXpert leaves residual gradients.

---

## When to Use

| Situation | Tool |
|---|---|
| Simple gradients, first attempt | GraXpert (AI mode) |
| MARS has coverage for your field | SPFC + MGC |
| GraXpert leaves residual gradient | **DBE** |
| Localized color gradient (e.g., one side reddish) | **DBE** |
| Vignetting (optical, not corrected by flats) | **DBE** (Division mode) |

---

## Correction Mode

| Mode | Use for |
|---|---|
| **Subtraction** | Light pollution gradients, sky glow, color gradients |
| **Division** | Vignetting, optical artifacts (equipment-caused) |

> If you need both: always apply **Division first**, then **Subtraction**.

---

## Sample Placement

### Manual Method (recommended for complex fields)

Place samples by clicking on empty background areas:
- **Avoid:** the target object, bright stars, star halos, nebulosity, artifacts
- **Place on:** dark, empty background between stars
- **Distribution:** cover the entire image, especially areas with gradient problems
- **Extra points:** add more in the gradient-affected region

### Auto-Generate Method

- Set **Samples per row** (15–20 for better coverage)
- Click **Generate**
- Manually delete samples on objects and bright stars (Ctrl+click to delete)
- Add points in problem areas (Shift+click)

---

## Key Parameters

### Model Parameters (1)

| Parameter | Default | Adjustment |
|---|---|---|
| **Tolerance** | 0.500 | **Increase to 0.750** if too many samples are rejected. Higher = accepts more dark pixels in samples. |
| **Shadows relaxation** | 3.000 | Increase (4–6) if dark samples are being ignored due to being atypical compared to brighter areas. |
| **Smoothing factor** | 0.250 | **Increase (0.5–0.8)** for smooth, broad gradients (light pollution). **Decrease (0.1–0.2)** for sharp transitions (vignetting). |

### Sample Generation

| Parameter | Default | Adjustment |
|---|---|---|
| **Default sample radius** | 10 | Increase for wide-field (250mm), decrease for crowded fields. Range: 10–30. |
| **Samples per row** | 10 | **Increase to 15–20** for better gradient modeling coverage. |
| **Minimum sample weight** | 0.750 | **Decrease to 0.500** if too many samples are rejected ("Less than three samples" error). |

---

## Sample Quality Check

After placing samples, inspect each one:
- **Weights (Wr, Wg, Wb):** should be > 0.5. Low weights = sample is on a dark or atypical area.
- **Color preview:** the sample's color grid should be mostly pale/uniform. Dark spots = stars or objects contaminating the sample.
- Navigate samples with the arrow buttons in DBE to check each one.

---

## Troubleshooting

| Error / Issue | Solution |
|---|---|
| "Less than three samples generated" | Increase tolerance (0.750), decrease minimum sample weight (0.500), increase samples per row (15–20) |
| Gradient still visible after DBE | Add more samples in the gradient area, run a second pass |
| Over-correction (dark patches where gradient was) | Reduce tolerance, increase smoothing factor, remove samples from affected area |
| Nebulosity reduced/removed | Remove samples that overlap with nebulosity |
| Color gradient (one side tinted) | Ensure samples are evenly distributed across the color boundary with extra points in the tinted region |

---

## Vignetting Removal (Axial Mode)

For circular vignetting not corrected by flats:

1. Set sample on the vignetting transition ring
2. Switch to **Axial** mode
3. Set corners to **24** (approximates a circle)
4. Adjust the center point to match the vignetting center (may not be image center)
5. Place additional circular samples at inner and outer transitions
6. Increase shadow relaxation to 6 (outer dark samples may be atypical)
7. Correction: **Division** (not subtraction)
8. Keep smoothing factor low (0.25) — vignetting has sharp transitions

---

## NGC 5746 Processing Notes (2026-03-29)

Specific findings from reprocessing:
- GraXpert × 2 passes could not fully remove a reddish color gradient on the right side
- DBE with manual samples (130 points, tolerance 0.750, weight 0.500, samples per row 15) corrected the gradient
- Extra sample points placed in the reddish right-side area were key to success
- SPCC Background Neutralization conflicted with DBE correction — disable BN in SPCC when DBE has already been applied
