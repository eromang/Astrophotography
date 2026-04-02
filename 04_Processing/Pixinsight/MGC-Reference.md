---
title: "MultiscaleGradientCorrection (MGC) Reference"
type: processing-workflow
software: "PixInsight"
tags:
  - processing/pixinsight
---

# MultiscaleGradientCorrection (MGC) — Settings Reference

MGC uses the MARS databases to model and remove gradients from astrophotography images. It is the most accurate gradient removal method when MARS has reference data for your field.

> **Prerequisite:** Run SPFC (SpectrophotometricFluxCalibration) before MGC. The image must be flux-calibrated.

> **MARS coverage:** MGC requires MARS reference data matching your field and filters. Check coverage first — if MARS lacks data for your field/filters, use **GraXpert** instead. Coverage varies: some broadband fields have R/G/B data (e.g., NGC 7000), some don't (e.g., NGC 5746).

---

## MARS Database

| Setting | Description |
|---------|-------------|
| MARS-DR1-1.1.1.xmars | Main MARS database (includes Ha, O-III, L, and some R/G/B broadband) |
| MARS-DR1-u01-1.0.1.xmars | User-contributed database (additional coverage) |

Load both databases. Set default files in Preferences to avoid reloading each session.

**SSD location:** `/Volumes/T7/Astrophotography/XMARS/`

---

## Filter Configuration

### Broadband (RGB-Workflow with [[Optolong-LPro]])

| Setting | Value |
|---------|-------|
| Gray filter | L |
| Red filter | R |
| Green filter | G |
| Blue filter | B |

### Narrowband HOO Palette (Ha in R, OIII in G+B)

| Setting | Value |
|---------|-------|
| Red filter | Halpha |
| Green filter | Oxygen 3 |
| Blue filter | Oxygen 3 |

### Narrowband SHO/Hubble Palette

| Setting | Value |
|---------|-------|
| Red filter | Halpha (for SII channel) |
| Green filter | Halpha |
| Blue filter | Oxygen 3 |

> Enable **Narrowband filters mode** in SPFC for narrowband palettes.

---

## Gradient Model Settings

| Setting | Default | Range | Description |
|---------|---------|-------|-------------|
| **Gradient scale** | 1024 | 128–2048 | Size of the gradient model in pixels. Higher = smoother, only corrects large-scale gradients. Lower = more aggressive, corrects smaller-scale gradients but risks eating objects |
| **Structure separation** | 1 | 1–3 | Separates objects from gradients. Lower = more cohesion, less overcorrection of bright objects. Higher = more aggressive separation |
| **Model smoothness** | 1.00 | 0–2 | Smoothness of the gradient model |
| **Show gradient model** | — | checkbox | Display the gradient model instead of the corrected image. **Essential for tuning.** |

### Gradient Scale Guidelines

| Scale | Use case |
|-------|----------|
| **2048** | Simple, gentle gradients (first try) |
| **1024** | Default — most images |
| **512–384** | Complex gradients |
| **256** | Severe gradients, or temporarily for scale factor tuning |
| **128** | Extreme cases only (severe LP, failed flats) — very risky, object traces likely |

> **Rule:** Always use the **highest scale that still corrects well** to minimize reference data dependency and object contamination.

---

## Scale Factors

Scale factors control how much of the MARS reference signal is subtracted per channel. Adjusted independently for R, G, B.

| Setting | Default | Range | Description |
|---------|---------|-------|-------------|
| R/K | 0.80 | 0.2–1.8 | Red channel scale factor |
| G | 0.80 | 0.2–1.8 | Green channel scale factor |
| B | 0.80 | 0.2–1.8 | Blue channel scale factor |

> Hold **Ctrl** to move all 3 channel sliders simultaneously.

### How to Read Scale Factors

| Gradient model shows... | Meaning | Action |
|------------------------|---------|--------|
| Object traces (nebula visible) | Scale factor too low — MGC treats object as gradient | **Increase** scale factor |
| Object appears **inverted** (dark where it should be bright) | Scale factor too high | **Decrease** scale factor |
| Clean, smooth gradient only | Correct setting | Apply |

### Typical Scale Factor Ranges by Object Type

| Object type | Typical R | Typical G | Typical B | Notes |
|-------------|-----------|-----------|-----------|-------|
| Small nebula (doesn't fill field) | 0.8–1.0 | 0.8–1.0 | 0.8–1.0 | Default usually works |
| Large emission nebula (fills field) | 1.2–1.5 | 1.0–1.3 | 1.0–1.3 | Ha emission in R needs higher factor |
| Galaxy | 1.0–1.3 | 1.0–1.4 | 1.0–1.2 | Nucleus may leave traces at any setting |
| Severe LP / failed flats | 0.2–0.6 | 0.2–0.6 | 0.2–0.6 | Lower factors reduce halos around stars |

---

## Tuning Procedure

### Step 1 — Show gradient model at low scale

1. Check **Show gradient model**
2. Set gradient scale to **256** (temporarily — to see traces clearly)
3. Set STF precision to **24 bits** to see the posterized gradient model properly

### Step 2 — Adjust scale factors per channel

Work one channel at a time:

1. **Red channel:** Increase R scale factor until nebula disappears from the gradient model. If it inverts, back off. Find the sweet spot.
2. **Green channel:** Same process. Watch for overcorrection.
3. **Blue channel:** Same process.

> **Tip from PixInsight tutorials:** For large emission nebulae with strong Ha, the R channel typically needs a higher scale factor (1.2–1.5+) than G and B.

### Step 3 — Set final gradient scale

1. Return gradient scale to **2048** (or **1024** if gradients remain)
2. Verify the gradient model is clean (no object traces, no inversions)
3. Adjust structure separation if needed (lower = fewer residual traces)

### Step 4 — Apply

1. Uncheck **Show gradient model**
2. Apply to the image
3. Run **BackgroundNeutralization** if residual color cast remains

---

## Post-MGC

After MGC, the image may need:
- **BackgroundNeutralization** — fix residual color cast from gradient correction
- If using SPCC later: be aware that SPCC's built-in BN may conflict with MGC's correction. See [[RGB-Workflow]] step 2.7.

---

## When to Use MGC vs GraXpert

| Condition | Use |
|-----------|-----|
| MARS has coverage for your field and filters | **MGC** — most accurate |
| MARS lacks coverage (MGC fails or shows garbage) | **GraXpert** (AI mode) |
| Color-only gradients (reddish cast on one side) | Try MGC first, fall back to **DBE** if stubborn |
| Quick processing, no time to tune | **GraXpert** — no manual tuning needed |

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| "No reference data found for filter R" | MARS has no broadband data for this field | Use GraXpert instead |
| Nebula appears in gradient model | Scale factor too low | Increase scale factor per channel |
| Nebula inverted in gradient model | Scale factor too high | Decrease scale factor |
| Gradients not fully corrected | Gradient scale too high | Lower gradient scale (1024 → 512 → 256) |
| Star halos in corrected image | Scale factor too high at low gradient scale | Decrease scale factor (try 0.2–0.6) |
| Residual color cast after MGC | Normal | Apply BackgroundNeutralization |
| Green tint with MARS-U | MARS-U can introduce color shifts | Use MARS DR1 alone, or adjust |

---

## Resources

- [MGC Processing Examples Part 1](https://www.youtube.com/watch?v=7ATdR8KpySc) — NGC 6543, Horsehead, Cone nebula
- [MGC Processing Examples Part 2](https://www.youtube.com/watch?v=YKFW1HElQI0) — IC 1805, M33
- Clippings: `04_Processing/Clippings/MultiscaleGradientCorrection — Processing Examples (I).md`
- Clippings: `04_Processing/Clippings/MultiscaleGradientCorrection — Processing Examples (II).md`
