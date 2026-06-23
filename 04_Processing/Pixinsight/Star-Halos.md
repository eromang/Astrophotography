---
title: "Star Halos — measure & set BXT Sharpen star values"
type: processing-workflow
software: "PixInsight"
tags:
  - processing/pixinsight
---

# Star Halos

`scripts/star_halos.py` — quantify **star-halo strength** and the median **core FWHM** of an image, and map them to **BlurXTerminator Sharpen** starting values: **Adjust Star Halos** and **Sharpen Stars**. Replaces eyeballing the sliders with a measurement, and `--against` measures how much a BXT pass actually reduced the halos.

Born out of the M42 reprocess, where SXT kept leaving **soft halo residuals** in the starless (the bright stars' scattered-light glow that BXT's halo control reduces — see [[QuadBand-OSC-Workflow#2.5 Star Sharpening]] and [[StarXTerminator Usage Notes]]).

---

## What it measures

For the brightest unsaturated stars:

- **Halo index** = mean background-subtracted, peak-normalised flux in the annulus **2.5–5× the core HWHM**, where a clean PSF is ~0 and a haloed star plateaus at several percent.
- **Bright-star p90** of that index drives the **Adjust Star Halos** suggestion. *Why p90, not median:* halos are a **bright-star phenomenon** — most (faint) stars are clean, so the median washes out exactly the stars that cause SXT residuals. (On the M42 master: median **0.008** "clean" but p90 **0.065** — the bright stars are haloed.)
- **Median FWHM** (from [[../../scripts/README.md#psf_image.py — offline PSF / FWHM measurement (PixInsight PSFImage equivalent)|psf_image.py]]'s Moffat fit) drives the **Sharpen Stars** suggestion — tight stars want little (more → hard dots / rings), soft stars tolerate more.

### Suggestion mappings (empirical, M42-calibrated)

| Bright-star halo p90 | Adjust Star Halos | | Median FWHM (px) | Sharpen Stars |
|---|---|---|---|---|
| < 0.03 | 0.00 | | < 2.5 | 0.10 |
| 0.03–0.06 | −0.10 | | 2.5–4.0 | 0.15 |
| 0.06–0.10 | −0.15 | | 4.0–6.0 | 0.20 |
| 0.10–0.15 | −0.20 | | 6.0–9.0 | 0.25 |
| 0.15–0.25 | −0.25 | | > 9.0 | 0.25 |
| > 0.25 | −0.30 | | | |

⚠️ These are **data-driven starting points, not a BXT-internal calibration** — confirm visually, and use `--against` to verify the actual reduction. Push more negative if the reduction is weak; back off if stars look over-pinched / dark-ringed.

---

## Usage

```bash
# suggest values for the current image
python3 scripts/star_halos.py img.xisf

# the strongest use: measure the actual halo reduction a BXT pass achieved
python3 scripts/star_halos.py before_BXT.xisf --against after_BXT.xisf
```

| Option | Default | Meaning |
|---|---|---|
| `--against PATH` | — | post-BXT image → halo-reduction % |
| `--stars N` | 60 | brightest N stars measured |
| `--rmax N` | 40 | radial-profile half-box (px) |
| `--annulus-px LO,HI` | auto | force a fixed-pixel halo annulus |
| `-k N` | 6.0 | detection σ threshold |
| `--json` | — | machine-readable |

> 🔴 **The annulus confound (and the fix).** Single-image mode measures the halo in **2.5–5× each star's core HWHM** — scale-invariant across different images/rigs. But BXT **shrinks the core**, so for a before/after comparison an HWHM-relative annulus would slide *inward* (toward more flux) and **understate** the reduction. So **`--against` automatically uses a fixed-pixel annulus** (derived from the reference's HWHM, applied to both images) → an honest, FWHM-independent number. Override with `--annulus-px LO,HI`. *(M42: the HWHM-relative read showed only −15%; the fixed annulus revealed the true **48.6%** reduction.)*

> Measure the **Sharpen Stars** value on the **Correct-Only output** (the Sharpen input) — the same "measure on the CO output" rule as the BXT PSF diameter ([[QuadBand-OSC-Workflow#2.3 Star Correction]]). The CO pass tightens stars, so measuring the raw master over-states the needed sharpening.

---

## Worked example (M42 reprocess, 2026-06-23)

`MasterLight_FQuad_GraXpert…xisf` (drizzle 2×), 79 stars: median FWHM **2.50 px**, halo index median **0.008** / p90 **0.065** → suggested **Adjust Star Halos −0.15, Sharpen Stars 0.15**. The Sharpen value matches what the workflow used; the −0.15 is a conservative start (we pushed to −0.25 by eye to tame visible halos — confirm with `--against` and go more negative if the reduction is weak).

---

## Tests

```bash
python3 scripts/test_star_halos.py
```

6 synthetic checks: haloed > clean index, clean stays low, FWHM recovery, monotonic halo + sharpen suggestions, and reduction-direction. See [[../../scripts/README.md#star_halos.py — measure star halos; suggest BXT Sharpen values|scripts/README]].
