---
title: "Guiding RMS Impact"
type: technique
tags:
  - technique
---

# Guiding RMS Impact — Is Guiding Limiting My Resolution?

Guiding software (PHD2 / ASIAIR) reports tracking error as **RMS in arcseconds**, but arcseconds are abstract. The practical question is: *does that error actually blur my stars, or is the atmosphere still the dominant blur source?* This note is the offline reference behind `scripts/guiding_impact.py` — a local, auditable rebuild of the web "HLP Guiding RMS Translator".

---

## The physics

Three relationships do all the work:

1. **Image scale (sampling).** How many arcsec each pixel covers:

   $$\text{scale} = \frac{206265 \times (\text{pixel}_{\mu m} \times \text{bin})}{\text{focal}_{mm} \times \text{reducer}} \quad [\text{arcsec/px}]$$

   For the [[RedCat-51]] + [[ASI2600MCPro]]: $206265 \times 3.76 / 250000 = 3.10$ arcsec/px.

2. **RMS → blur FWHM.** A guiding RMS of $\sigma$ arcsec smears a star by a Gaussian of that width:

   $$\text{FWHM}_\text{guiding} = 2.355 \times \text{RMS}$$

   The $2.355 = 2\sqrt{2\ln 2}$ is the Gaussian $\sigma \to$ FWHM factor. Skipping it is the most common error in naïve calculators.

3. **Seeing in quadrature.** Atmospheric blur is *isotropic* — it adds the same round blur to every axis — and combines with guiding as independent variances:

   $$\text{FWHM}_\text{total} = \sqrt{\text{seeing}^2 + \text{FWHM}_\text{guiding}^2}$$

> [!warning] The modifiers do NOT change guiding RMS in arcseconds
> Reducer/Barlow and binning only change **how that fixed angular error is sampled** by the camera (the image scale). They never change the arcsec RMS — that is a property of the mount + guide loop alone. Any tool that inflates your arcsec RMS when you bin is wrong.

---

## Why seeing must be folded in *before* judging shape

This is the subtle part the Advanced mode exists for. Guiding error is rarely symmetric — RA usually dominates (periodic error lives on the RA worm). With **RA RMS 0.8″, DEC RMS 0.4″** a naïve ratio screams *50% ellipticity* ($1 - 0.4/0.8$). But seeing adds a large round term to **both** axes and drowns the imbalance:

$$\text{major} = \sqrt{3.0^2 + (2.355 \times 0.8)^2} = 3.54''$$
$$\text{minor} = \sqrt{3.0^2 + (2.355 \times 0.4)^2} = 3.14''$$
$$\text{ellipticity} = 1 - \frac{3.14}{3.54} = 0.11 \;(\sim 11\%)$$

At 3.10 arcsec/px those are **1.14 × 1.01 px** stars — effectively round. The short focal length is forgiving; a naïve ratio over-states the alarm by ~4×.

> [!note] The axis is mount-frame, not sensor-frame
> The tool reports elongation along "RA". Because camera rotation is manual on this rig (no CAA — the angle is set by hand per session), the RA axis lands on the sensor at whatever rotation was dialled in. The model predicts elongation *exists* and its mount-frame axis; it cannot tell you which way the eggs point in the final framing. Match that against the rotation angle in the session note.

---

## Using the script

```bash
# Basic: one total guiding RMS
python3 scripts/guiding_impact.py --focal 250 --pixel 3.76 --rms 0.8

# Advanced: per-axis RA/DEC -> star shape
python3 scripts/guiding_impact.py --focal 250 --pixel 3.76 --ra 0.8 --dec 0.4

# Explicit seeing instead of the quality band
python3 scripts/guiding_impact.py --focal 250 --pixel 3.76 --rms 0.8 --seeing 2.2
```

| Flag | Default | Meaning |
|---|---|---|
| `--focal` | — | telescope focal length (mm) |
| `--pixel` | — | camera pixel size (µm) |
| `--rms` | — | total guiding RMS (arcsec) → **basic mode** |
| `--ra` / `--dec` | — | per-axis RMS (arcsec) → **advanced mode** |
| `--seeing` | — | explicit seeing FWHM (arcsec); overrides the band |
| `--seeing-quality` | `ok` | `excellent` / `good` / `ok` (2–4″) / `poor` / `bad` |
| `--reducer` | `1.0` | reducer/Barlow focal factor |
| `--binning` | `1` | imaging binning N×N |
| `--json` | — | machine-readable result for session notes |

The verdict reports the FWHM growth from guiding: **<5%** negligible, **5–15%** minor, **15–30%** significant, **≥30%** dominant.

> [!tip] Leave `--binning 1` on the ASI2600MC
> It is a one-shot-colour sensor; hardware binning destroys the Bayer matrix. See [[Pixel-Binning]]. The flag exists for mono workflows.

---

## What it means for this rig

At 250 mm / 3.10 arcsec/px the [[iOptron-CEM26]]'s typical 0.7–1.0″ RMS is **sub-pixel** (~0.3 px) and contributes <15% FWHM growth in OK seeing — guiding is essentially never the limiting factor here. The translator's real value is diagnostic: when stars look bloated, the math tells you to **stop blaming the mount** and look at focus, seeing, or sampling instead. The margin shrinks on longer focal lengths, where this becomes a real planning input.

---

## See also

- [[SNR]] — the other half of "is this sub good?"
- [[Pixel-Binning]] — why OSC binning is a trap
- [[Capture-Planning-Rules]] — operational rules paid for in real mistakes
- `scripts/README.md` → guiding_impact.py — CLI + test reference
