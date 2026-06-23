#!/usr/bin/env python3
"""
star_halos.py — measure stars; suggest BlurXTerminator "Adjust Star Halos" + "Sharpen Stars" values.

Bright stars on some rigs (and after aggressive deconvolution) carry a faint
extended halo — scattered light / chromatic glow that StarXTerminator then leaves
behind as a residual ring in the starless image. BXT's "Adjust Star Halos" slider
(−0.5 … +0.5; negative shrinks halos) controls this, but picking a value is
normally eyeball-only.

This script quantifies it. For the brightest unsaturated stars it builds a
background-subtracted radial profile, finds the core half-width (HWHM), and
measures the **halo index** = mean normalised flux in the annulus 2.5–5× HWHM,
where a clean PSF is ~0 and a haloed star plateaus at several percent. The median
over stars is mapped to a suggested Adjust Star Halos starting value.

⚠️ The index→slider mapping is an empirical heuristic (calibrated to the M42
reprocess, where −0.25 tamed visible halos), not a BXT-internal calibration. Use
it as a data-driven STARTING point, then confirm visually. Its strongest use is
`--against`: run it before and after a BXT Sharpen pass to measure the actual
halo REDUCTION (%), turning "looks less visible" into a number.

It also reports the median core FWHM (px) and maps it to a suggested **Sharpen
Stars** value — tight stars want little sharpening (more makes hard dots/rings),
soft/bloated stars tolerate more. Measure that on the Correct-Only OUTPUT (the
Sharpen input), the same rule as the BXT PSF diameter.

Usage
-----
    python3 scripts/star_halos.py <image.xisf>                 # halo index + suggested value
    python3 scripts/star_halos.py before.xisf --against after.xisf   # measure reduction
    python3 scripts/star_halos.py img.xisf --stars 80 --json

Reuses psf_image.py (read_image / estimate_background / detect_stars).
Run from repo root. Doc: 04_Processing/Pixinsight/Star-Halos.md  ·  Tests: scripts/test_star_halos.py
"""

import argparse
import json
import sys

import numpy as np

import psf_image as pi

# Empirical halo-index -> Adjust Star Halos mapping (M42-calibrated). Lower index = cleaner.
HALO_TABLE = [(0.03, 0.00), (0.06, -0.10), (0.10, -0.15), (0.15, -0.20), (0.25, -0.25)]
HALO_FLOOR = -0.30

# FWHM(px) -> Sharpen Stars: tighter stars need less (more risks hard dots/rings);
# softer/bloated stars tolerate more. Capped low — aggressive star sharpening rarely helps.
# ⚠️ measure on the Correct-Only OUTPUT (the Sharpen input), like the PSF-diameter rule.
SHARPEN_TABLE = [(2.5, 0.10), (4.0, 0.15), (6.0, 0.20), (9.0, 0.25)]
SHARPEN_FLOOR = 0.25


def radial_profile(img, cx, cy, bg, rmax):
    """Background-subtracted mean flux at each integer radius around (cx, cy)."""
    x0, x1 = int(cx - rmax), int(cx + rmax) + 1
    y0, y1 = int(cy - rmax), int(cy + rmax) + 1
    if x0 < 0 or y0 < 0 or x1 > img.shape[1] or y1 > img.shape[0]:
        return None
    sub = img[y0:y1, x0:x1] - bg
    yy, xx = np.mgrid[y0:y1, x0:x1]
    r = np.hypot(xx - cx, yy - cy).astype(int).ravel()
    r = np.clip(r, 0, rmax)
    prof = np.zeros(rmax + 1)
    cnt = np.zeros(rmax + 1)
    np.add.at(prof, r, sub.ravel())
    np.add.at(cnt, r, 1)
    return prof / np.maximum(cnt, 1)


def halo_indices(img, stars, bg, n_use, rmax):
    """Per-star halo index + FWHM (px) for up to n_use brightest stars."""
    idx, fwhm = [], []
    for (cx, cy, peak, npix) in stars[:n_use]:
        amp = peak - bg
        if amp <= 0:
            continue
        prof = radial_profile(img, cx, cy, bg, rmax)
        if prof is None:
            continue
        p = prof / amp
        below = np.where(p < 0.5)[0]            # core half-width
        if len(below) == 0 or below[0] < 1:
            continue
        i = int(below[0])
        # sub-pixel HWHM: interpolate the 0.5 crossing between bins i-1 and i
        p0, p1 = p[i - 1], p[i]
        frac = (p0 - 0.5) / (p0 - p1) if p0 > p1 else 0.0
        hwhm_f = (i - 1) + frac
        r_lo, r_hi = int(2.5 * i), min(int(5 * i), rmax)
        if r_hi <= r_lo:
            continue
        idx.append(float(np.clip(p[r_lo:r_hi + 1], 0, None).mean()))
        fwhm.append(2.0 * hwhm_f)
    return np.array(idx), np.array(fwhm)


def suggest_value(halo_index):
    for thr, val in HALO_TABLE:
        if halo_index < thr:
            return val
    return HALO_FLOOR


def suggest_sharpen(fwhm_px):
    for thr, val in SHARPEN_TABLE:
        if fwhm_px < thr:
            return val
    return SHARPEN_FLOOR


def analyze(path, n_use=60, rmax=40, k=6.0, max_pix=2500):
    img = pi.read_image(path)
    bg, sigma = pi.estimate_background(img)
    # max_pix raised from psf_image's default (400): bright HALOED stars have larger
    # above-threshold blobs and must not be size-excluded. The nebula core (far bigger)
    # is still rejected; extended nebula knots are filtered by the tight-core HWHM check.
    stars = pi.detect_stars(img, bg, sigma, k=k, max_pix=max_pix)
    idx, fwhm_radial = halo_indices(img, stars, bg, n_use, rmax)
    if len(idx) == 0:
        raise SystemExit("No usable bright stars found in %s (try lowering -k)" % path)
    # FWHM from psf_image's Moffat fit (authoritative); the radial estimate runs ~15%
    # low and straddles the 0.10/0.15 Sharpen threshold. Fall back to radial if the fit fails.
    try:
        med_fwhm = float(pi.measure(path, k=k, verbose=False)["fwhm"])
    except Exception:
        med_fwhm = float(np.median(fwhm_radial))
    p90 = float(np.percentile(idx, 90))
    # Halos live on BRIGHT stars (and they cause the SXT residuals). The median is
    # dominated by faint clean stars and under-calls it, so drive the suggestion off
    # the bright-star percentile (p90).
    return {
        "path": path,
        "stars_used": int(len(idx)),
        "median_fwhm_px": med_fwhm,
        "halo_index": float(np.median(idx)),
        "halo_index_p90": p90,
        "suggested_adjust_star_halos": suggest_value(p90),
        "suggested_sharpen_stars": suggest_sharpen(med_fwhm),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="Measure star halos; suggest BXT Adjust Star Halos value")
    ap.add_argument("image")
    ap.add_argument("--against", help="second image (e.g. post-BXT) to measure halo reduction")
    ap.add_argument("--stars", type=int, default=60, help="brightest N stars to measure (default 60)")
    ap.add_argument("--rmax", type=int, default=40, help="profile half-box radius px (default 40)")
    ap.add_argument("-k", type=float, default=6.0, help="detection threshold sigma (default 6)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    a = analyze(args.image, args.stars, args.rmax, args.k)
    b = analyze(args.against, args.stars, args.rmax, args.k) if args.against else None

    if args.json:
        out = {"image": a}
        if b:
            out["against"] = b
            out["halo_reduction_pct"] = round(100 * (1 - b["halo_index"] / max(a["halo_index"], 1e-9)), 1)
        print(json.dumps(out, indent=2))
        return

    def show(d):
        print("  %s" % d["path"])
        print("    stars measured     : %d   (median FWHM %.2f px)" % (d["stars_used"], d["median_fwhm_px"]))
        print("    halo index         : median %.4f  |  bright-star p90 %.4f   [clean ~0.01-0.03, haloed >0.10]"
              % (d["halo_index"], d["halo_index_p90"]))
        print("      (halos sit on BRIGHT stars -> the Adjust value targets p90, not the median)")
        print("    suggested BXT Sharpen:  Adjust Star Halos %+.2f   |   Sharpen Stars %.2f"
              % (d["suggested_adjust_star_halos"], d["suggested_sharpen_stars"]))

    print("Star halos / sharpening —")
    show(a)
    if b:
        print()
        show(b)
        red = 100 * (1 - b["halo_index"] / max(a["halo_index"], 1e-9))
        print("\n  >>> halo reduction: %.1f%%  (index %.4f -> %.4f)" % (red, a["halo_index"], b["halo_index"]))
        if red < 15:
            print("      weak — push Adjust Star Halos more negative or check BXT actually ran")
        elif red > 70:
            print("      strong — watch for over-pinched/dark-ringed stars")
    else:
        print("\n  Start BXT Sharpen at:  Adjust Star Halos %+.2f,  Sharpen Stars %.2f"
              % (a["suggested_adjust_star_halos"], a["suggested_sharpen_stars"]))
        print("  (measure on the Correct-Only output for the Sharpen-Stars value; re-run --against after to verify halo reduction)")


if __name__ == "__main__":
    main()
