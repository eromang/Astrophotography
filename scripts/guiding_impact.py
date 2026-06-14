#!/usr/bin/env python3
"""guiding_impact.py — offline equivalent of the "HLP Guiding RMS Translator".

Translates guiding RMS (arcsec) into real imaging impact: how many imaging
pixels the error smears a star across, and — folding seeing in quadrature —
whether guiding is actually limiting resolution or the atmosphere still
dominates. Two modes mirror the web tool's tabs:

    basic     : one Total Guiding RMS -> round-star blur + verdict
    advanced  : RA RMS + DEC RMS      -> star shape (ellipticity) + dominant axis

The physics the web tool gets right and this reproduces:

  * Imaging-system modifiers (reducer/Barlow, binning) DO NOT change guiding RMS
    in arcseconds. They only change how that fixed angular error is *sampled* by
    the camera (the image scale).
  * A guiding RMS of sigma arcsec smears a star by FWHM = 2.355 x sigma (a
    Gaussian sigma->FWHM conversion).
  * Seeing is isotropic and adds the SAME round blur to every axis. It must be
    combined with guiding in quadrature BEFORE judging impact, otherwise a
    per-axis RMS imbalance vastly over-predicts star elongation.

        total_FWHM = sqrt(seeing^2 + (2.355 * RMS)^2)

Pure stdlib + math (no numpy needed). Run from the repo root:

    python3 scripts/guiding_impact.py --focal 250 --pixel 3.76 --rms 0.8
    python3 scripts/guiding_impact.py --focal 250 --pixel 3.76 --ra 0.8 --dec 0.4

Reference: HLP Guiding RMS Translator. See the vault doc
03_Techniques/Guiding-RMS-Impact.md.
"""
from __future__ import annotations
import argparse
import json
import math
import sys

# Gaussian standard-deviation -> full-width-half-maximum: 2*sqrt(2*ln2) ~ 2.3548
SIGMA_TO_FWHM = 2.0 * math.sqrt(2.0 * math.log(2.0))

# Arcsec subtended by 1 mm at the focal plane, times 1000 (microns): the
# image-scale constant 206264.8 arcsec/radian / 1000.
ARCSEC_PER_RADIAN = 206264.806

# Seeing-quality bands -> representative FWHM (arcsec). Midpoints of the ranges
# the web tool exposes in its "Seeing Quality" dropdown. Override with --seeing.
SEEING_BANDS = {
    "excellent": 1.5,   # < 2.0  - pristine high-altitude / rare lowland night
    "good":      2.0,   # ~2.0
    "ok":        3.0,   # 2.0-4.0  (the tool's default band)
    "poor":      4.5,   # 4.0-5.0
    "bad":       6.0,   # > 5.0
}


# --------------------------------------------------------------------------- #
# Core physics                                                                #
# --------------------------------------------------------------------------- #
def image_scale(focal_mm: float, pixel_um: float,
                reducer: float = 1.0, binning: int = 1) -> float:
    """Arcsec per pixel.

    Reducer/Barlow scales the effective focal length (a 0.8 reducer shortens it,
    so each pixel covers MORE sky); binning enlarges the effective pixel. Neither
    touches guiding RMS in arcsec — only the sampling.
    """
    eff_focal = focal_mm * reducer
    eff_pixel = pixel_um * binning
    if eff_focal <= 0 or eff_pixel <= 0:
        raise ValueError("focal length and pixel size must be positive")
    return ARCSEC_PER_RADIAN * eff_pixel / (eff_focal * 1000.0)


def rms_to_fwhm(rms_arcsec: float) -> float:
    """Per-axis Gaussian blur FWHM (arcsec) from a per-axis guiding RMS (sigma)."""
    return SIGMA_TO_FWHM * rms_arcsec


def quadrature(seeing_fwhm: float, guiding_fwhm: float) -> float:
    """Combine two independent blur sources (arcsec FWHM) in quadrature."""
    return math.hypot(seeing_fwhm, guiding_fwhm)


def resolve_seeing(seeing: float | None, quality: str) -> float:
    """Explicit --seeing arcsec wins; else map the quality band to a FWHM."""
    if seeing is not None:
        if seeing <= 0:
            raise ValueError("--seeing must be positive arcsec FWHM")
        return seeing
    if quality not in SEEING_BANDS:
        raise ValueError(f"unknown seeing quality: {quality}")
    return SEEING_BANDS[quality]


# --------------------------------------------------------------------------- #
# Verdicts                                                                    #
# --------------------------------------------------------------------------- #
def verdict_blur(seeing_fwhm: float, total_fwhm: float):
    """Fractional FWHM growth from guiding -> a 'is guiding limiting?' verdict."""
    degradation = total_fwhm / seeing_fwhm - 1.0
    if degradation < 0.05:
        label = "NEGLIGIBLE - atmosphere dominates; guiding is not limiting"
    elif degradation < 0.15:
        label = "MINOR - guiding adds a little; seeing still dominates"
    elif degradation < 0.30:
        label = "SIGNIFICANT - guiding is meaningfully limiting resolution"
    else:
        label = "DOMINANT - guiding is the limiting blur source"
    return degradation, label


def verdict_shape(ellipticity: float) -> str:
    """Map ellipticity (1 - minor/major) to a star-shape verdict."""
    if ellipticity < 0.10:
        return "ROUND - elongation not visible"
    if ellipticity < 0.20:
        return "SLIGHT - mild elongation, usually acceptable"
    if ellipticity < 0.35:
        return "VISIBLE - noticeable egg-shaped stars"
    return "BAD - strongly elongated stars"


# --------------------------------------------------------------------------- #
# Analysis                                                                    #
# --------------------------------------------------------------------------- #
def analyze_basic(focal_mm, pixel_um, total_rms, seeing_fwhm,
                  reducer=1.0, binning=1) -> dict:
    """Basic mode: one total RMS -> round-star blur + verdict.

    The total (2D radial) RMS is split isotropically into equal per-axis sigmas
    (axis = total / sqrt(2)), so the round-star blur FWHM = 2.355 * total/sqrt(2).
    This keeps Basic a special case of Advanced with RA == DEC, and is the honest
    single-number answer when the per-axis split is unknown. If your guiding is
    RA-dominant (the usual case), use advanced mode for the true major axis.
    """
    scale = image_scale(focal_mm, pixel_um, reducer, binning)
    axis_rms = total_rms / math.sqrt(2.0)
    guiding_fwhm = rms_to_fwhm(axis_rms)
    total_fwhm = quadrature(seeing_fwhm, guiding_fwhm)
    degradation, label = verdict_blur(seeing_fwhm, total_fwhm)
    return dict(
        mode="basic", scale=scale, total_rms=total_rms,
        rms_px=total_rms / scale, seeing_fwhm=seeing_fwhm,
        guiding_fwhm=guiding_fwhm, total_fwhm=total_fwhm,
        total_fwhm_px=total_fwhm / scale, degradation=degradation, verdict=label,
    )


def analyze_advanced(focal_mm, pixel_um, ra_rms, dec_rms, seeing_fwhm,
                     reducer=1.0, binning=1) -> dict:
    """Advanced mode: per-axis RMS -> star shape (ellipticity) + dominant axis.

    Each axis is blurred by its own guiding sigma, then seeing (isotropic) is
    added in quadrature to BOTH axes. The shared seeing term is what drowns out a
    raw RA:DEC ratio into a much smaller realised ellipticity.
    """
    scale = image_scale(focal_mm, pixel_um, reducer, binning)
    ra_fwhm = rms_to_fwhm(ra_rms)
    dec_fwhm = rms_to_fwhm(dec_rms)
    ax_ra = quadrature(seeing_fwhm, ra_fwhm)
    ax_dec = quadrature(seeing_fwhm, dec_fwhm)
    major, minor = max(ax_ra, ax_dec), min(ax_ra, ax_dec)
    dom_axis = "RA" if ax_ra >= ax_dec else "DEC"
    ellipticity = 1.0 - minor / major if major > 0 else 0.0
    total_rms = math.hypot(ra_rms, dec_rms)
    # mean (geometric) blur for the same limiting verdict as basic mode
    mean_fwhm = math.sqrt(major * minor)
    degradation, blur_label = verdict_blur(seeing_fwhm, mean_fwhm)
    return dict(
        mode="advanced", scale=scale, ra_rms=ra_rms, dec_rms=dec_rms,
        total_rms=total_rms, total_rms_px=total_rms / scale,
        seeing_fwhm=seeing_fwhm, dominant_axis=dom_axis,
        major_fwhm=major, minor_fwhm=minor,
        major_fwhm_px=major / scale, minor_fwhm_px=minor / scale,
        ellipticity=ellipticity, shape_verdict=verdict_shape(ellipticity),
        mean_fwhm=mean_fwhm, degradation=degradation, blur_verdict=blur_label,
    )


# --------------------------------------------------------------------------- #
# Reporting                                                                   #
# --------------------------------------------------------------------------- #
def _scale_line(r, reducer, binning):
    mod = []
    if reducer != 1.0:
        mod.append(f"reducer/barlow x{reducer:g}")
    if binning != 1:
        mod.append(f"bin {binning}x{binning}")
    suffix = f"   [{', '.join(mod)}]" if mod else ""
    return f"Image scale : {r['scale']:.3f} arcsec/px{suffix}"


def report_basic(r, reducer, binning):
    print(_scale_line(r, reducer, binning))
    print(f"Seeing      : {r['seeing_fwhm']:.2f}\" FWHM (assumed atmosphere)")
    print(f"Guiding RMS : {r['total_rms']:.2f}\"  =  {r['rms_px']:.2f} px")
    print(f"  guiding blur          : {r['guiding_fwhm']:.2f}\" FWHM "
          f"(2.355 x RMS, isotropic)")
    print(f"  total FWHM (quadrature): {r['total_fwhm']:.2f}\"  "
          f"=  {r['total_fwhm_px']:.2f} px")
    print(f"  seeing-only would be   : {r['seeing_fwhm']:.2f}\"  "
          f"(+{r['degradation'] * 100:.0f}% from guiding)")
    print(f"==> {r['verdict']}")


def report_advanced(r, reducer, binning):
    print(_scale_line(r, reducer, binning))
    print(f"Seeing      : {r['seeing_fwhm']:.2f}\" FWHM (assumed atmosphere)")
    print(f"Guiding RMS : RA {r['ra_rms']:.2f}\"  DEC {r['dec_rms']:.2f}\"  "
          f"(total {r['total_rms']:.2f}\" = {r['total_rms_px']:.2f} px)")
    print(f"  dominant axis : {r['dominant_axis']}")
    print(f"  major FWHM    : {r['major_fwhm']:.2f}\"  = {r['major_fwhm_px']:.2f} px")
    print(f"  minor FWHM    : {r['minor_fwhm']:.2f}\"  = {r['minor_fwhm_px']:.2f} px")
    print(f"  ellipticity   : {r['ellipticity']:.3f}  "
          f"(seeing-folded; raw RA:DEC ratio would over-state this)")
    print(f"  mean FWHM     : {r['mean_fwhm']:.2f}\"  "
          f"(+{r['degradation'] * 100:.0f}% from guiding)")
    print(f"==> shape : {r['shape_verdict']}")
    print(f"==> blur  : {r['blur_verdict']}")


# --------------------------------------------------------------------------- #
# Main                                                                        #
# --------------------------------------------------------------------------- #
def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Translate guiding RMS into imaging impact (offline HLP "
                    "Guiding RMS Translator).")
    ap.add_argument("--focal", type=float, required=True,
                    help="telescope focal length (mm)")
    ap.add_argument("--pixel", type=float, required=True,
                    help="camera pixel size (microns)")
    ap.add_argument("--rms", type=float,
                    help="total guiding RMS (arcsec) -> basic mode")
    ap.add_argument("--ra", type=float,
                    help="RA guiding RMS (arcsec) -> advanced mode (needs --dec)")
    ap.add_argument("--dec", type=float,
                    help="DEC guiding RMS (arcsec) -> advanced mode (needs --ra)")
    ap.add_argument("--seeing", type=float, default=None,
                    help="explicit seeing FWHM (arcsec); overrides --seeing-quality")
    ap.add_argument("--seeing-quality", choices=list(SEEING_BANDS), default="ok",
                    help="seeing band when --seeing is not given (default: ok)")
    ap.add_argument("--reducer", type=float, default=1.0,
                    help="reducer/Barlow focal factor (default 1.0; e.g. 0.8 reducer)")
    ap.add_argument("--binning", type=int, default=1,
                    help="imaging binning NxN (default 1)")
    ap.add_argument("--json", action="store_true",
                    help="emit the result dict as JSON instead of a report")
    args = ap.parse_args(argv)

    advanced = args.ra is not None or args.dec is not None
    if advanced and (args.ra is None or args.dec is None):
        ap.error("advanced mode needs both --ra and --dec")
    if not advanced and args.rms is None:
        ap.error("give --rms (basic) or both --ra and --dec (advanced)")
    if advanced and args.rms is not None:
        ap.error("--rms is for basic mode; do not combine it with --ra/--dec")
    if args.binning < 1:
        ap.error("--binning must be >= 1")

    try:
        seeing = resolve_seeing(args.seeing, args.seeing_quality)
        if advanced:
            r = analyze_advanced(args.focal, args.pixel, args.ra, args.dec,
                                 seeing, args.reducer, args.binning)
        else:
            r = analyze_basic(args.focal, args.pixel, args.rms,
                              seeing, args.reducer, args.binning)
    except ValueError as e:
        ap.error(str(e))

    if args.json:
        print(json.dumps(r, indent=2))
        return 0

    (report_advanced if advanced else report_basic)(r, args.reducer, args.binning)
    if args.binning > 1:
        print("  note: binning an OSC (Bayer) sensor destroys the CFA - leave "
              "1x1 on the ASI2600MC.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
