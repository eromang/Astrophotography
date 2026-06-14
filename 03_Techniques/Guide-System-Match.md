---
title: "Guide System Match"
type: technique
tags:
  - technique
---

# Guide System Match — Can the Guider Resolve the Motion?

Can the guide camera measure motion finely enough for the image scale you're capturing? `scripts/guide_match.py` is the offline reference behind the web "HLP Guide System Match Analyzer" — guide scale vs imaging scale, and the smallest motion the guider can actually resolve.

---

## The myth this kills

> "Guide scale must be ≤ imaging scale" (or "within ~2×").

**False, by an order of magnitude.** A guide pixel is not the resolution limit — PHD2 **centroids** a guide star to roughly **0.1 guide pixel** (SNR-dependent, ~0.05–0.25). So the quantity that matters is:

$$\text{min detectable motion} = \text{centroid} \times \text{guide\_scale} \;[\text{arcsec}] = \text{centroid} \times \text{ratio}\;[\text{imaging px}]$$

| min motion (imaging px) | Verdict |
|---|---|
| `< 0.5` | GOOD — guider resolves well below one imaging pixel |
| `0.5 – 1.0` | ADEQUATE — sub-pixel but getting coarse |
| `1.0 – 2.0` | MARGINAL — guider resolution near one imaging pixel |
| `> 2.0` | POOR — guide camera too coarse |

Anchoring the verdict on **min motion**, not the raw ratio, is the whole point — a 2× coarser guide pixel still resolves ~0.2 imaging px and reads GOOD.

---

## This rig

[[UniGuide-32mm]] (120 mm f/3.75) + [[ASI385MC]] (3.75 µm) guiding the [[RedCat-51]] + [[ASI2600MCPro]]:

| | Scale |
|---|---|
| Imaging | 3.10″/px |
| Guiding | 6.45″/px |
| Guide ratio | **2.08×** |
| Min motion @ centroid 0.1 | 0.64″ = **0.21 imaging px → GOOD** |

The guide pixel is 2× coarser yet resolves motion ~5× finer than an imaging pixel. The guide camera is **not** your limit — consistent with the [[ASI385MC]] note ("6.4″/pixel… fine enough to correct sub-arcsecond errors").

---

## ⚠️ What this tool cannot see: differential flexure

> [!warning] Resolution match ≠ guiding solved
> This judges whether the guide camera can *resolve* the motion. It is blind to whether the two optical tubes *stay aligned*. With a **guide scope**, the guide tube and the RedCat can shift relative to each other mid-exposure — PHD2 holds its star perfectly while the imaging stars walk. **Differential flexure**, not the scale ratio, is the real guide-scope failure mode, and no scale calculator will ever flag it. An **OAG** eliminates it (shared light path), at the cost of finding a guide star in a smaller field.

So a GOOD verdict here means "the guide camera is fine" — round stars still depend on flexure, mount ([[Guiding-RMS-Impact]]), and seeing.

---

## Using the script

```bash
# Guide scope (this rig)
python3 scripts/guide_match.py --img-focal 250 --img-pixel 3.76 \
    --guide-focal 120 --guide-pixel 3.75

# Dim guide star / poor transparency -> degrade the centroid accuracy
python3 scripts/guide_match.py --img-focal 250 --img-pixel 3.76 \
    --guide-focal 120 --guide-pixel 3.75 --centroid 0.4

# OAG: guide camera inherits the imaging focal length
python3 scripts/guide_match.py --img-focal 800 --img-pixel 3.76 \
    --guide-pixel 2.9 --oag
```

| Flag | Default | Meaning |
|---|---|---|
| `--img-focal` / `--img-pixel` | — | imaging focal (mm) / pixel (µm) |
| `--guide-pixel` | — | guide camera pixel (µm) |
| `--guide-focal` | — | guide scope focal (mm); **omit** in `--oag` |
| `--oag` | off | off-axis guider — inherit imaging focal + reducer |
| `--centroid` | 0.1 | guide centroid accuracy (guide px); use ~0.25–0.5 for a dim star |
| `--img-reducer` / `--img-binning` | 1.0 / 1 | imaging modifiers |
| `--guide-reducer` / `--guide-binning` | 1.0 / 1 | guide modifiers |
| `--json` | — | machine-readable result |

---

## See also

- [[Guiding-RMS-Impact]] — once resolution is fine, does the *actual* RMS limit you?
- [[Sampling-Analysis]] — sibling tool; shared image-scale engine
- [[ASI385MC]] / [[UniGuide-32mm]] — the guide rig
- `scripts/README.md` → guide_match.py
