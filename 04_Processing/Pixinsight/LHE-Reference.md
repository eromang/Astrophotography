---
title: "LocalHistogramEqualization (LHE) Reference"
type: processing-workflow
software: "PixInsight"
tags:
  - processing/pixinsight
---

# LocalHistogramEqualization (LHE) — Settings Reference

Enhances local contrast to bring out structures in nebulae and galaxies. Apply after stretching, CurvesTransformation, and noise reduction (Phase 4).

> **Warning:** LHE is very easy to overdo. Subtle is better. Less is more.

---

## Settings

| Setting | Default | Range | Description |
|---------|---------|-------|-------------|
| **Kernel Radius** | 64 | 8–512 | Size of structures to enhance. Lower = smaller structures (star-level detail). Higher = larger structures (nebula clouds, spiral arms) |
| **Contrast Limit** | 2.0 | 1.0–64 | How much contrast to add. **Ultra sensitive** — values 1.2–3.0 are the useful range. Higher = more noise |
| **Amount** | 1.000 | 0.0–1.0 | Blend between original (0) and processed (1) image. **Always reduce from 1.0** |
| Histogram Resolution | 8-bit (256) | — | Leave at default (PixInsight recommendation) |
| Circular Kernel | checked | — | Leave at default (PixInsight recommendation) |

---

## Kernel Radius Guidelines

| Radius | Structure size | Use case |
|--------|---------------|----------|
| 20–50 | Small | Fine filaments, small dark lanes, galaxy dust lanes |
| 64–100 | Medium | Medium nebula structures, individual knots |
| 100–180 | Large | Large nebula clouds, spiral arms, major dark regions |
| 200–360 | Very large | Whole nebula structures, galaxy cores |

> **Rule of thumb:** Below 100 = small structures, above 100 = large structures.

---

## Two-Pass Approach (Recommended)

Apply LHE **twice** — once for large structures, once for small structures.

### Pass 1 — Large Structures

| Setting | Value |
|---------|-------|
| Kernel Radius | **100–180** (adjust to match your target's major structures) |
| Contrast Limit | **1.5–2.0** |
| Amount | **0.3–0.5** |

### Pass 2 — Small Structures

| Setting | Value |
|---------|-------|
| Kernel Radius | **20–80** (adjust to match fine detail) |
| Contrast Limit | **1.5–2.0** |
| Amount | **0.3–0.5** |

> Use a **preview** on a detail-rich area for Pass 2 — small structure changes are hard to see at full image scale.

---

## Tuning Procedure

1. **Set Amount to 1.0** initially — this exaggerates the effect so you can clearly see what's being enhanced
2. **Adjust Kernel Radius** — find the right structure size. Toggle preview on/off to compare
3. **Set Contrast Limit** — start at 2.0. Go lower (1.3–1.5) for subtle enhancement, higher (2.5–3.0) for more aggressive (more noise risk)
4. **Reduce Amount** — dial back to 0.3–0.5 until the effect is subtle but visible
5. Toggle preview on/off for final check
6. Apply

---

## Masking

**Always consider masking the background** to prevent LHE from making it blotchy.

### When to mask:
- Image has significant dark background around the target
- Background is smooth and you want to keep it that way

### When masking is optional:
- Target fills most of the frame (e.g., NGC 7000)
- You want to bring out faint nebulosity hiding in the background

### How to create the mask:
1. Use **RangeSelection** tool
2. Adjust lower limit until the mask covers only the target (nebula/galaxy)
3. Add fuzziness for soft edges
4. Apply the mask to the image before running LHE

---

## Target-Specific Settings

### Emission Nebulae (NGC 7000, M42, Rosette)

**Pass 1 — Large nebula structures:**

| Setting | Value |
|---------|-------|
| Kernel Radius | **120–160** |
| Contrast Limit | **1.5–2.0** |
| Amount | **0.3–0.5** |

**Pass 2 — Fine filaments and dark lane edges:**

| Setting | Value |
|---------|-------|
| Kernel Radius | **40–80** |
| Contrast Limit | **1.5–2.0** |
| Amount | **0.3–0.5** |

### Galaxies (M31, M51, NGC 5746)

**Pass 1 — Spiral arms, major structures:**

| Setting | Value |
|---------|-------|
| Kernel Radius | **140–256** |
| Contrast Limit | **1.5–2.0** |
| Amount | **0.3–0.5** |

**Pass 2 — Dust lanes, fine spiral detail:**

| Setting | Value |
|---------|-------|
| Kernel Radius | **40–80** |
| Contrast Limit | **1.5–2.0** |
| Amount | **0.3–0.5** |

---

## Common Mistakes

| Mistake | Symptom | Fix |
|---------|---------|-----|
| Amount too high (1.0) | Over-processed, crunchy, HDR look | Reduce to 0.3–0.5 |
| Contrast Limit too high | Excessive noise, harsh transitions | Reduce to 1.3–1.5 |
| Kernel Radius too small | Star halos, noise amplification | Increase radius |
| No mask on background | Blotchy, noisy background | Apply RangeSelection mask |
| Too many passes | Cumulative over-processing | Limit to 2 passes max |
| Saturation loss | Desaturated areas after LHE | Apply slight saturation boost with CurvesTransformation after |

---

## Post-LHE

After applying LHE, you may notice slight desaturation. A small saturation bump with [[CurvesTransformation-Reference|CurvesTransformation]] (S channel) can compensate.

---

## Resources

- [LHE Process Tutorial — PixInsight A-Z](https://www.youtube.com/watch?v=UeofpRmsAxc) — Detailed walkthrough with mask creation
- [LHE Subtle to Stunning — Hidden Light Photography](https://www.youtube.com/watch?v=wkmOPOxCEos) — Multi-size approach (20, 80, 256)
- [LHE for Nebulae and Galaxies — Ancient Photons](https://www.youtube.com/watch?v=hTW3KM8hccw) — Two-pass technique with examples
- Clippings: `04_Processing/Clippings/`
