---
title: "Find Background — fast background ROI finder"
type: processing-workflow
software: "PixInsight"
tags:
  - processing/pixinsight
---

# Find Background

`scripts/find_background.py` — locate the **darkest, flattest region** of a linear image and report the ROI coordinates to type into a PixInsight process. A fast, offline numpy reimplementation of the SetiAstro **FindBackground.js** script (Gerrit Erdt & Franklin Marek, 2024).

Run it on the saved `.xisf`/`.fit`; it prints the ROI `X / Y / Width / Height` to paste into the process that needs a background region.

---

## Why it exists / why it's faster

We repeatedly need a clean **background reference / ROI** during the linear phase:

| Process | Where it's used | What it needs |
|---|---|---|
| **SPCC** — Background Neutralization | [[QuadBand-OSC-Workflow#2.4 Color Calibration (SPCC) — star-full, BEFORE star removal\|QuadBand §2.4]] / [[RGB-Workflow#2.7 Color Calibration\|RGB §2.7]] | a dark, nebula-free ROI |
| **MultiscaleAdaptiveStretch** — Background Reference | [[HDR-Workflow]] (MAS step) | a dark ROI to anchor the stretch |
| **BackgroundNeutralization** | post-stretch colour | a neutral-sky ROI |
| **DynamicBackgroundExtraction** | gradient removal (fallback) | sample placement on sky |

On M42 (and any frame-filling nebula) eyeballing a truly empty patch is hard — the field is full of faint Ha. FindBackground.js automates it but is **slow**: it samples pixels one-by-one in PixInsight's JS engine (O(N·window²)) and *approximates* the optimum with gradient descent from a few seed points — minutes on a drizzled master.

`find_background.py` computes the per-window mean and standard deviation for **every** candidate position in a single O(N) pass using **integral images** (summed-area tables), then takes the **exact global minimum** — no gradient descent. **~2 s on the 96 MP M42 drizzle master.**

---

## Usage

```bash
# basic — ROI coords + per-channel background brightness + colour-correction constants
python3 scripts/find_background.py <image.xisf>

# 100 px ROI, list the 5 best non-overlapping spots, write a preview to verify
python3 scripts/find_background.py img.xisf --size 100 --top 5 --png roi.png

# keep it off the nebula core explicitly
python3 scripts/find_background.py img.xisf --exclude 5000,3500,2500,2000
```

| Option | Default | Meaning |
|---|---|---|
| `--size N` | 50 | ROI side length (px). Use 100 on drizzled masters |
| `--exclude X,Y,W,H` | — | exclude a rectangle (repeatable) |
| `--scale N` | 1 (exact) | downsample before searching; coords still reported in full-res px. Use 2–4 to cut memory/time on very large frames |
| `--top N` | 1 | also print N best non-overlapping candidates |
| `--png PATH` | — | stretched preview with the ROI box drawn |
| `--json` | — | machine-readable output |

---

## Reading the output

```
ROI to enter in PixInsight (SPCC / MAS / BN / DBE):
  Left (X): 9074   Top (Y): 4833   Width: 100   Height: 100

Background brightness:  mean 0.001708  stddev 0.000046  score 0.00128
  R   brightness 0.001689   additive correction +0.000034
  G   brightness 0.001713   additive correction +0.000010
  B   brightness 0.001723   additive correction +0.000000
```

- **Left / Top / Width / Height** → paste straight into the process ROI fields (SPCC, MAS Background Reference, BN, DBE).
- **mean / stddev** → how dark and how flat the chosen window is (lower both = better sky). `score` is the internal objective (lower = better).
- **additive correction** = `max_channel − channel`. The amount to *add* to each channel to neutralise the background manually (the brightest channel gets 0) — useful as a sanity check or for a manual PixelMath neutralization.
- ⚠️ **Always glance at `--png`** — confirm the box sits on dark sky, not a faint Ha wisp the metric rated "flat enough."

### Scoring

Faithful to FindBackground's default path (**average + standard deviation**, image-normalised via the same tile statistic). A window is good when it is both **dark** (low mean) and **flat** (low stddev); the stddev term is **capped** once a window is flat enough, so among equally-dark flat windows the result can sit near a boundary — pass `--top N` and pick the one your `--png` likes. One deliberate fix vs the JS: brightness is a consistent per-pixel channel **mean** throughout (the JS folds a channel-*sum* into the stddev term — a unit quirk).

---

## Worked example (M42 reprocess, 2026-06-23)

On `MasterLight_FQuad_GraXpert…xisf` (12048×8000, drizzle 2×), `--size 100`: ROI **(9074, 4833)**, mean **0.0017**, stddev **4.6e-5** — a clean dark gap right of the core, below the Running Man. **read 0.19 s + search 1.90 s.** Used as the SPCC/MAS background reference instead of hand-placing a preview.

---

## Tests

```bash
python3 scripts/test_find_background.py
```

7 synthetic checks: integral-image stats vs brute force, bright-blob avoidance, flat-over-noisy preference, darkest-corner-under-gradient, exclusion regions, `--scale` agreement, and RGB colour-correction. See [[../../scripts/README.md#find_background.py — find the optimal background ROI (fast)|scripts/README]].
