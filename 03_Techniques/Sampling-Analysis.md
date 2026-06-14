---
title: "Sampling Analysis"
type: technique
tags:
  - technique
---

# Sampling Analysis — Pixel Scale vs the Sky

Does the pixel grid match the sky being shot? `scripts/sampling.py` is the offline reference behind the web "HLP Sampling Analyzer" — image scale, the disk it's sampling, the ideal pixel-scale band, and an undersampled / balanced / oversampled verdict.

---

## The rule

$$\text{scale} = \frac{206265 \times (\text{pixel}_{\mu m} \times \text{bin})}{\text{focal}_{mm} \times \text{reducer}} \quad [\text{arcsec/px}]$$

Aim for **2.0–3.3 pixels across the FWHM** of the disk you're sampling. Stars are Gaussian, not band-limited, so this is the practical window — not the textbook 2× Nyquist:

| Pixels across FWHM | Regime |
|---|---|
| `< 2.0` | undersampled — pixel scale coarser than the disk |
| `2.0 – 3.3` | balanced |
| `> 3.3` | oversampled — disk spread over more pixels than it holds detail |

For [[RedCat-51]] + [[ASI2600MCPro]] the scale is **3.10 arcsec/px**. Reducer/Barlow and binning move only the scale; they never change the disk FWHM in arcsec.

---

## The key distinction: two FWHMs, two questions

This is the part the web tool glosses, and the reason `sampling.py` takes a `--fwhm-px` input. **What you compare the pixel scale against changes the meaning of the verdict.**

> [!abstract] Atmosphere disk vs delivered PSF
> - **Seeing band (atmosphere only)** — the *potential* disk if everything else were perfect. For the RedCat: 3.0″ → **0.97 px/FWHM → undersampled.** Reading: *"your pixel scale would be the limiting factor if your stars were as tight as the sky allows."*
> - **Delivered FWHM** (measured with `psf_image.py`, optics + guiding + atmosphere combined) — the disk your stars *actually* span. For the RedCat that's ~**2.3 px** → **balanced.** Reading: *"your pixels are matched to your real stars — the pixel grid is NOT your current bottleneck; the PSF is."*

Both are true. They are not in conflict:

- The atmosphere-band verdict says there is **headroom you can't reach** at this focal length — finer native sampling would help *only if* your PSF tightened toward the seeing limit.
- The delivered-FWHM verdict says that **today**, your blur comes from focus / guiding / optics / seeing-worse-than-ideal, not from coarse pixels. Chase the PSF (and drizzle), not the pixel scale.

> [!warning] Don't feed a sub-2 px measurement back as truth
> Below ~2 px the FWHM fit is itself sampling-limited and reads high — the back-conversion to arcsec overstates the true disk. A measured value **above** 2 px (like the RedCat's 2.3 px) is past the aliasing floor and meaningful; below it, the only honest verdict is "undersampled — dither + drizzle." The script flags this.

---

## Using the script

```bash
# Atmosphere-only (planning): potential sampling vs a seeing band
python3 scripts/sampling.py --focal 250 --pixel 3.76 --seeing-quality ok

# Best: judge against your REAL stars (psf_image.py gives FWHM in px)
python3 scripts/sampling.py --focal 250 --pixel 3.76 --fwhm-px 2.3

# Or a delivered FWHM you already have in arcsec
python3 scripts/sampling.py --focal 250 --pixel 3.76 --fwhm 7.1
```

| Flag | Default | Meaning |
|---|---|---|
| `--focal` / `--pixel` | — | focal length (mm) / pixel size (µm) |
| `--fwhm-px` | — | **delivered** FWHM in pixels (from [[#See also]] `psf_image.py`) — best input |
| `--fwhm` | — | delivered FWHM in arcsec |
| `--seeing` / `--seeing-quality` | ok | atmosphere-only fallback (`excellent`…`bad`) |
| `--reducer` / `--binning` | 1.0 / 1 | sampling-only modifiers |
| `--json` | — | machine-readable result |

Input priority: `--fwhm-px` → `--fwhm` → seeing band.

---

## What it means for this rig

The RedCat is **undersampled against the atmosphere and that is correct** — it's the deliberate trade for a 5.4°×3.6° field, not a defect. Two things follow:

1. **Don't "fix" it by binning.** The ASI2600 is OSC; binning destroys the Bayer matrix ([[Pixel-Binning]]), and you're undersampled, so it's the wrong direction anyway.
2. **Drizzle is the lever.** A well-dithered undersampled set, 2× drizzle-integrated, reclaims real resolution the native scale throws away.

And against your **delivered** ~2.3 px stars you're already balanced — so on any given night the gain is in tighter focus / better guiding ([[Guiding-RMS-Impact]]) and drizzle, not a different pixel scale.

---

## See also

- [[Guiding-RMS-Impact]] — the sibling tool; shares the image-scale engine
- [[Pixel-Binning]] — why OSC binning is a trap
- [[SNR]] — oversampling's cost is per-pixel SNR
- `scripts/README.md` → psf_image.py — measures the delivered FWHM you feed here
