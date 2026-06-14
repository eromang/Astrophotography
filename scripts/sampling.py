#!/usr/bin/env python3
"""sampling.py — offline equivalent of the "HLP Sampling Analyzer".

Answers "does my pixel scale match the sky I'm shooting?" — image scale, the
seeing/star disk it's sampling, the ideal pixel-scale band, and an
undersampled / balanced / oversampled verdict.

Sampling is judged against a **reference disk FWHM** (arcsec). In order of
honesty:

  1. --fwhm-px   a DELIVERED FWHM you measured with psf_image.py (pixels). This
                 is optics + guiding + atmosphere combined — the real thing your
                 stars span. Converted to arcsec with this rig's image scale.
  2. --fwhm      a delivered FWHM you already have in arcsec.
  3. seeing band (--seeing / --seeing-quality). Raw ATMOSPHERE only; always
     finer than your delivered FWHM, so it over-states how undersampled you are.

The Nyquist-ish rule: stars are Gaussian, not band-limited, so aim for ~2.0-3.3
pixels across the FWHM (not the textbook 2x). Below 2.0 px is undersampled,
above 3.3 px is oversampled.

> Undersampling is NOT a defect. For a short widefield astrograph (e.g. the
> RedCat 51) it is the deliberate, correct trade for field of view, and a
> well-dithered undersampled set can be 2x drizzle-integrated to recover real
> resolution the raw pixel scale throws away.

Imaging-system modifiers (reducer/Barlow, binning) change only the image scale,
never the seeing/star FWHM in arcsec.

Pure stdlib; reuses the image-scale engine from guiding_impact.py. Run from the
repo root:

    python3 scripts/sampling.py --focal 250 --pixel 3.76
    python3 scripts/sampling.py --focal 250 --pixel 3.76 --fwhm-px 2.3

Reference: HLP Sampling Analyzer. See the vault doc
03_Techniques/Sampling-Analysis.md.
"""
from __future__ import annotations
import argparse
import json
import sys

from guiding_impact import image_scale, resolve_seeing, SEEING_BANDS

# Target sampling band: pixels across the FWHM. Stars are Gaussian (not
# band-limited), so the practical window is ~2.0-3.3 px/FWHM, not the textbook 2x.
SAMPLES_MIN = 2.0   # below this -> undersampled (scale too coarse)
SAMPLES_MAX = 3.3   # above this -> oversampled (scale too fine)

ARCSEC_PER_MM = 206.264806   # 206265 arcsec/rad, pixel in microns, focal in mm


# --------------------------------------------------------------------------- #
# Reference disk resolution                                                   #
# --------------------------------------------------------------------------- #
def resolve_reference(scale, fwhm_px=None, fwhm=None,
                      seeing=None, quality="ok"):
    """Return (reference_FWHM_arcsec, source_label).

    Priority: measured px -> measured arcsec -> seeing band.
    """
    if fwhm_px is not None:
        if fwhm_px <= 0:
            raise ValueError("--fwhm-px must be positive")
        return fwhm_px * scale, f"measured {fwhm_px:g} px (delivered FWHM)"
    if fwhm is not None:
        if fwhm <= 0:
            raise ValueError("--fwhm must be positive arcsec")
        return fwhm, f"measured {fwhm:g}\" (delivered FWHM)"
    ref = resolve_seeing(seeing, quality)
    src = (f"seeing {seeing:g}\"" if seeing is not None
           else f"seeing band '{quality}' ({ref:g}\", atmosphere only)")
    return ref, src


# --------------------------------------------------------------------------- #
# Verdict                                                                     #
# --------------------------------------------------------------------------- #
def sampling_verdict(samples: float) -> str:
    if samples < SAMPLES_MIN:
        return ("UNDERSAMPLED - pixel scale coarser than the disk. Normal and "
                "correct for short widefield rigs; drizzle 2x can recover detail")
    if samples > SAMPLES_MAX:
        return ("OVERSAMPLED - spreading the disk over more pixels than it holds "
                "detail; costs per-pixel SNR for no resolution gain")
    return "BALANCED - pixel scale matches the disk"


# --------------------------------------------------------------------------- #
# Analysis                                                                    #
# --------------------------------------------------------------------------- #
def analyze(focal_mm, pixel_um, ref_fwhm, reducer=1.0, binning=1):
    """Sampling analysis against a reference disk FWHM (arcsec)."""
    scale = image_scale(focal_mm, pixel_um, reducer, binning)
    samples = ref_fwhm / scale                      # pixels across the FWHM
    # ideal pixel-scale band: scale that lands samples in [MIN, MAX]
    ideal_scale_fine = ref_fwhm / SAMPLES_MAX       # finest sensible scale
    ideal_scale_coarse = ref_fwhm / SAMPLES_MIN     # coarsest sensible scale
    # focal length (effective) that would hit the balanced band, at this pixel
    eff_pixel = pixel_um * binning
    focal_min = ARCSEC_PER_MM * eff_pixel * SAMPLES_MIN / ref_fwhm
    focal_max = ARCSEC_PER_MM * eff_pixel * SAMPLES_MAX / ref_fwhm
    eff_focal = focal_mm * reducer
    return dict(
        scale=scale, ref_fwhm=ref_fwhm, samples=samples,
        regime=sampling_verdict(samples),
        ideal_scale_fine=ideal_scale_fine, ideal_scale_coarse=ideal_scale_coarse,
        eff_focal=eff_focal, balanced_focal_min=focal_min,
        balanced_focal_max=focal_max,
        balanced_factor_min=focal_min / eff_focal,
        balanced_factor_max=focal_max / eff_focal,
    )


# --------------------------------------------------------------------------- #
# Reporting                                                                   #
# --------------------------------------------------------------------------- #
def report(r, source, reducer, binning):
    mod = []
    if reducer != 1.0:
        mod.append(f"reducer/barlow x{reducer:g}")
    if binning != 1:
        mod.append(f"bin {binning}x{binning}")
    suffix = f"   [{', '.join(mod)}]" if mod else ""
    print(f"Image scale : {r['scale']:.3f} arcsec/px{suffix}")
    print(f"Reference   : {r['ref_fwhm']:.2f}\" FWHM  [{source}]")
    print(f"Sampling    : {r['samples']:.2f} px across the FWHM "
          f"(balanced is {SAMPLES_MIN:g}-{SAMPLES_MAX:g})")
    print(f"Ideal scale : {r['ideal_scale_fine']:.2f}-{r['ideal_scale_coarse']:.2f}"
          f" arcsec/px for this disk")
    print(f"==> {r['regime']}")
    # what would reach balanced — the reducer/barlow-impact angle
    lo, hi = sorted((r["balanced_factor_min"], r["balanced_factor_max"]))
    fl_lo, fl_hi = sorted((r["balanced_focal_min"], r["balanced_focal_max"]))
    if r["samples"] < SAMPLES_MIN:
        print(f"    to balance: focal {fl_lo:.0f}-{fl_hi:.0f} mm "
              f"(x{lo:.1f}-{hi:.1f}) - a longer scope/Barlow, or drizzle "
              f"the widefield data instead")
    elif r["samples"] > SAMPLES_MAX:
        print(f"    to balance: focal {fl_lo:.0f}-{fl_hi:.0f} mm "
              f"(x{lo:.2f}-{hi:.2f}) - a reducer, or bin (mono only)")


# --------------------------------------------------------------------------- #
# Main                                                                        #
# --------------------------------------------------------------------------- #
def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Pixel-scale / sampling analysis (offline HLP Sampling "
                    "Analyzer). Judge against a measured FWHM when you have one.")
    ap.add_argument("--focal", type=float, required=True,
                    help="telescope focal length (mm)")
    ap.add_argument("--pixel", type=float, required=True,
                    help="camera pixel size (microns)")
    ap.add_argument("--fwhm-px", type=float, default=None,
                    help="DELIVERED FWHM in pixels (from psf_image.py) - best input")
    ap.add_argument("--fwhm", type=float, default=None,
                    help="delivered FWHM in arcsec (if you already have it)")
    ap.add_argument("--seeing", type=float, default=None,
                    help="explicit seeing FWHM (arcsec); atmosphere-only fallback")
    ap.add_argument("--seeing-quality", choices=list(SEEING_BANDS), default="ok",
                    help="seeing band when no FWHM/seeing given (default: ok)")
    ap.add_argument("--reducer", type=float, default=1.0,
                    help="reducer/Barlow focal factor (default 1.0)")
    ap.add_argument("--binning", type=int, default=1,
                    help="imaging binning NxN (default 1)")
    ap.add_argument("--json", action="store_true",
                    help="emit the result dict as JSON instead of a report")
    args = ap.parse_args(argv)

    if args.fwhm_px is not None and args.fwhm is not None:
        ap.error("give either --fwhm-px or --fwhm, not both")
    if args.binning < 1:
        ap.error("--binning must be >= 1")

    try:
        scale = image_scale(args.focal, args.pixel, args.reducer, args.binning)
        ref, source = resolve_reference(scale, args.fwhm_px, args.fwhm,
                                        args.seeing, args.seeing_quality)
        r = analyze(args.focal, args.pixel, ref, args.reducer, args.binning)
    except ValueError as e:
        ap.error(str(e))

    if args.json:
        r["source"] = source
        print(json.dumps(r, indent=2))
        return 0

    report(r, source, args.reducer, args.binning)
    if args.binning > 1:
        print("  note: binning an OSC (Bayer) sensor destroys the CFA - leave "
              "1x1 on the ASI2600MC.")
    measured = args.fwhm_px is not None or args.fwhm is not None
    if measured:
        if r["samples"] < SAMPLES_MIN:
            print("  warn: stars span <2 px - the FWHM fit itself is sampling-"
                  "limited and reads high; you are undersampled, dither + drizzle.")
        else:
            print("  read: this judges your DELIVERED PSF (atmosphere+optics+"
                  "guiding) vs the pixels - 'balanced' here means pixels are not "
                  "your bottleneck, not that you are atmosphere-limited.")
    else:
        print("  tip: this is ATMOSPHERE-only (potential sampling). Feed "
              "--fwhm-px from psf_image.py to judge against your real stars.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
