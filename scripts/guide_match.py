#!/usr/bin/env python3
"""guide_match.py — offline equivalent of the "HLP Guide System Match Analyzer".

Compares the guiding system to the imaging system: can the guide camera resolve
motion finely enough for the image scale you're asking the rig to capture? Two
modes:

    guide scope : guide scale from its own focal length + camera
    OAG         : guide camera inherits the imaging focal length (and reducer)

The physics most "guide match" calculators get WRONG — and this gets right:

  * The obsolete myth says guide scale must be <= imaging scale (or "within 2x").
    False by an order of magnitude. PHD2 centroids a guide star to ~0.1 guide
    pixel, so the guider resolves motion far finer than one guide pixel:

        min detectable motion (arcsec) = centroid_fraction * guide_scale
        min detectable motion (img px) = centroid_fraction * guide_ratio

  * Imaging-system / guide-system modifiers (reducer, Barlow, binning) change the
    effective SCALE only.

> [!warning] This tool is blind to differential flexure.
> It measures resolution match, not stability. A guide SCOPE can pass this test
> and still ruin subs if the guide tube and the imaging tube shift relative to
> each other mid-exposure - the guider holds its star while imaging stars walk.
> Flexure, not the scale ratio, is the real guide-scope failure mode. An OAG
> eliminates it (shared light path) at the cost of finding a guide star.

Pure stdlib; reuses image_scale() from guiding_impact.py. Run from repo root:

    # guide scope: RedCat 250mm + ASI2600, UniGuide 120mm + ASI385
    python3 scripts/guide_match.py --img-focal 250 --img-pixel 3.76 \\
        --guide-focal 120 --guide-pixel 3.75
    # OAG: guide camera through the imaging optics
    python3 scripts/guide_match.py --img-focal 800 --img-pixel 3.76 \\
        --guide-pixel 2.9 --oag

Reference: HLP Guide System Match Analyzer. See the vault doc
03_Techniques/Guide-System-Match.md.
"""
from __future__ import annotations
import argparse
import json
import sys

from guiding_impact import image_scale

DEFAULT_CENTROID = 0.1   # PHD2 sub-pixel centroid accuracy (~0.05-0.25, SNR-dep.)


# --------------------------------------------------------------------------- #
# Analysis                                                                    #
# --------------------------------------------------------------------------- #
def analyze(img_focal, img_pixel, guide_pixel, *, oag=False, guide_focal=None,
            centroid=DEFAULT_CENTROID, img_reducer=1.0, img_binning=1,
            guide_reducer=1.0, guide_binning=1):
    """Guide-vs-imaging scale match + minimum detectable motion."""
    if centroid <= 0 or centroid > 1:
        raise ValueError("--centroid must be in (0, 1]")
    img_scale = image_scale(img_focal, img_pixel, img_reducer, img_binning)
    if oag:
        # guide camera sees through the imaging optics: shares focal length and
        # any reducer ahead of the pickoff.
        guide_scale = image_scale(img_focal, guide_pixel,
                                  img_reducer * guide_reducer, guide_binning)
        eff_guide_focal = img_focal * img_reducer * guide_reducer
    else:
        if guide_focal is None:
            raise ValueError("guide-scope mode needs --guide-focal")
        guide_scale = image_scale(guide_focal, guide_pixel,
                                  guide_reducer, guide_binning)
        eff_guide_focal = guide_focal * guide_reducer
    ratio = guide_scale / img_scale
    min_motion_arcsec = centroid * guide_scale
    min_motion_img_px = min_motion_arcsec / img_scale
    return dict(
        mode="oag" if oag else "guidescope",
        img_scale=img_scale, guide_scale=guide_scale,
        eff_guide_focal=eff_guide_focal, ratio=ratio, centroid=centroid,
        min_motion_arcsec=min_motion_arcsec, min_motion_img_px=min_motion_img_px,
        verdict=match_verdict(min_motion_img_px),
    )


def match_verdict(min_motion_img_px: float) -> str:
    """Verdict from the smallest motion the guider can resolve, in imaging px.

    Anchored on the physical quantity, NOT the raw scale ratio - so a 2x coarser
    guide pixel still reads GOOD (it resolves ~0.2 imaging px).
    """
    if min_motion_img_px < 0.5:
        return ("GOOD - guider resolves well below one imaging pixel; the guide "
                "camera is not your limit")
    if min_motion_img_px < 1.0:
        return "ADEQUATE - sub-imaging-pixel resolution, but getting coarse"
    if min_motion_img_px < 2.0:
        return ("MARGINAL - guider resolution is near one imaging pixel; "
                "corrections are coarse")
    return ("POOR - guide camera too coarse to resolve imaging-pixel motion; "
            "longer guide focal length or a finer guide camera")


# --------------------------------------------------------------------------- #
# Reporting                                                                   #
# --------------------------------------------------------------------------- #
def report(r):
    mode = "OAG (inherits imaging optics)" if r["mode"] == "oag" else "guide scope"
    print(f"Mode        : {mode}")
    print(f"Imaging     : {r['img_scale']:.3f} arcsec/px")
    print(f"Guiding     : {r['guide_scale']:.3f} arcsec/px "
          f"(eff focal {r['eff_guide_focal']:.0f} mm)")
    print(f"Guide ratio : {r['ratio']:.2f}x the imaging scale")
    print(f"Centroiding : {r['centroid']:.2f} guide px "
          f"-> min motion {r['min_motion_arcsec']:.2f}\"  "
          f"= {r['min_motion_img_px']:.2f} imaging px")
    print(f"==> {r['verdict']}")
    if r["mode"] == "oag":
        print("  note: OAG shares the imaging light path - no differential "
              "flexure (its main advantage); trade-off is finding a guide star.")
    else:
        print("  caveat: this judges RESOLUTION only. A guide scope can pass and "
              "still trail stars via DIFFERENTIAL FLEXURE (guide tube vs OTA "
              "shifting mid-sub) - the failure mode no scale-ratio can see.")


# --------------------------------------------------------------------------- #
# Main                                                                        #
# --------------------------------------------------------------------------- #
def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Guide-vs-imaging scale match (offline HLP Guide System "
                    "Match Analyzer). Rejects the 1:1 myth via sub-pixel "
                    "centroiding.")
    ap.add_argument("--img-focal", type=float, required=True,
                    help="imaging focal length (mm)")
    ap.add_argument("--img-pixel", type=float, required=True,
                    help="imaging pixel size (microns)")
    ap.add_argument("--guide-pixel", type=float, required=True,
                    help="guide camera pixel size (microns)")
    ap.add_argument("--guide-focal", type=float, default=None,
                    help="guide scope focal length (mm); omit in --oag mode")
    ap.add_argument("--oag", action="store_true",
                    help="off-axis guider: inherit the imaging focal length")
    ap.add_argument("--centroid", type=float, default=DEFAULT_CENTROID,
                    help="guide centroid accuracy in guide px (default 0.1; "
                         "use ~0.25-0.5 for a dim star / poor transparency)")
    ap.add_argument("--img-reducer", type=float, default=1.0,
                    help="imaging reducer/Barlow factor (default 1.0)")
    ap.add_argument("--img-binning", type=int, default=1,
                    help="imaging binning NxN (default 1)")
    ap.add_argument("--guide-reducer", type=float, default=1.0,
                    help="guide reducer/Barlow factor (default 1.0)")
    ap.add_argument("--guide-binning", type=int, default=1,
                    help="guide-camera binning NxN (default 1)")
    ap.add_argument("--json", action="store_true",
                    help="emit the result dict as JSON instead of a report")
    args = ap.parse_args(argv)

    if args.oag and args.guide_focal is not None:
        ap.error("--guide-focal is inherited in --oag mode; drop it")
    if not args.oag and args.guide_focal is None:
        ap.error("guide-scope mode needs --guide-focal (or pass --oag)")
    if args.img_binning < 1 or args.guide_binning < 1:
        ap.error("binning must be >= 1")

    try:
        r = analyze(args.img_focal, args.img_pixel, args.guide_pixel,
                    oag=args.oag, guide_focal=args.guide_focal,
                    centroid=args.centroid, img_reducer=args.img_reducer,
                    img_binning=args.img_binning, guide_reducer=args.guide_reducer,
                    guide_binning=args.guide_binning)
    except ValueError as e:
        ap.error(str(e))

    if args.json:
        print(json.dumps(r, indent=2))
        return 0
    report(r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
