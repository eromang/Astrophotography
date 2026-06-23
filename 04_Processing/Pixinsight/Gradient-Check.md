---
title: "Gradient-Check — gradient-correction QA tool"
type: processing-workflow
software: "PixInsight"
tags:
  - processing/pixinsight
---

# Gradient-Check

Offline QA for a gradient-correction step (**[[GraXpert-Reference|GraXpert]] / [[MGC-Reference|MGC]] / DBE**). Answers the two questions that decide whether the correction was good, especially on a **frame-filling nebula** like [[M42-Orion]] where the tool can mistake the object for background:

1. **Did it flatten the sky?** — residual large-scale gradient left behind
2. **Did it eat the object?** — over-subtraction of the faint outer wings

Run by `scripts/gradient_check.py` (pure numpy; reuses `psf_image.py`'s XISF/FITS readers). It is the objective companion to the eyeball check — *"does the background model contain the nebula?"* becomes a number.

> Built 2026-06-22 during the [[M42-Orion]] HDR reprocess, to pick between GraXpert and MGC+DR2. See `scripts/README.md#gradient_check.py`.

---

## What it measures

| Metric | What it tells you | Good |
|---|---|---|
| **rel_spread** (background flatness) | percentile spread of local sky across an N×N grid, normalised to the median sky | **low** (flat) — directly comparable between methods |
| **neg_fraction** | % of pixels driven below zero | low (unless the correction left no pedestal — then read the deficit instead) |
| **dark_tile_deficit** | how far the *darkest* region's sky fell below the median region, in MAD | low — a big deficit at the object location = wings eaten |
| **wing mean-above-bg** | flux retained in an annulus around the object | **high** = more outer nebulosity preserved |
| **model imprint_corr** | correlation of a background **model** with the object structure | **< 0.30** — above that, the model contains the nebula and is about to subtract real signal |

The image is read as **luminance** (channels averaged) — fine for gradient/background work. Feed it the **linear, unstretched** result; never a stretched export.

---

## Usage

```bash
# single corrected image + its background model
python3 scripts/gradient_check.py corrected.xisf --model bg.xisf --png /tmp/gc

# A/B: which method wins on the SAME registered field
python3 scripts/gradient_check.py M42_MGC.xisf --against M42_GraXpert.xisf

# machine-readable
python3 scripts/gradient_check.py corrected.xisf --json
```

The `--against` verdict prefers the method with **more wing signal, as long as its flatness is within 2× of the flatter method**. That guard stops a method from "winning" flatness by over-flattening the nebula into the background — exactly the failure we're testing for.

---

## How to read it (decision guide)

- **rel_spread** an order of magnitude lower after correction → the gradient is gone. Compare the two methods' rel_spread directly.
- **imprint_corr > 0.30** on the background model → that model traced the nebula; lower the aggressiveness (GraXpert: raise **Smoothing**; MGC: lower the channel **scale factor**) and re-check.
- **wing mean-above-bg**: the decider between two clean-background methods. Higher = the faint Ha/OIII wings survived. MGC (real sky references) *should* beat GraXpert (models from the image) here on extended objects — if it doesn't, GraXpert at high smoothing is fine.
- **dark_tile_deficit** spiking while wing signal drops → over-subtraction localised at the object.

---

## Worked example — M42 reprocess (2026-06-22)

GraXpert @ Smoothing **0.8**, on the drizzle-2× FQuad master:

```
flatness : rel_spread 0.018   (dead flat)
oversub  : negatives 0.00%    dark-tile deficit 0.14 MAD
wing     : mean-above-bg 0.00105
model    : contrast 0.130     imprint_corr 0.003   <- no nebula in the model
```

A clean baseline — the 0.8 smoothing kept M42's wings (imprint 0.003 ≈ zero). The MGC+DR2 candidates are then compared with `--against M42_GraXpert.xisf`, and the **wing-signal delta** picks the winner. The full A/B/sweep (GraXpert won across the entire MGC parameter space) is written up in [[Gradient-MGC-vs-GraXpert-M42]] — a worked demonstration of every metric this tool produces, including how the `imprint_corr` caught the gs1024 core-hole.

---

## Related

- [[MGC-Reference]] — MultiscaleGradientCorrection + MARS DR2 setup
- [[QuadBand-OSC-Workflow#2.2 Gradient Removal]] / [[RGB-Workflow]] — where the gradient step lives
- [[Master-Library#Additional SSD Resources]] — MARS DR2 database path
- `scripts/psf_image.py` — shares the image readers
