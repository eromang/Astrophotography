#!/usr/bin/env python3
"""
test_star_halos.py — synthetic tests for star_halos.py

Run from repo root:  python3 scripts/test_star_halos.py
"""

import numpy as np

import star_halos as sh


def _star(img, cx, cy, peak, fwhm, halo_frac=0.0, halo_scale=8.0):
    """Add a Gaussian core + optional broad Gaussian halo (halo_frac of peak)."""
    h, w = img.shape
    yy, xx = np.mgrid[0:h, 0:w]
    r2 = (xx - cx) ** 2 + (yy - cy) ** 2
    sigma = fwhm / 2.3548
    img += peak * np.exp(-r2 / (2 * sigma ** 2))
    if halo_frac > 0:
        img += halo_frac * peak * np.exp(-r2 / (2 * halo_scale ** 2))


def _field(haloed, fwhm=4.0, halo_frac=0.0):
    rng = np.random.default_rng(3)
    img = np.full((400, 400), 0.02, np.float64)
    img += rng.normal(0, 0.001, img.shape)
    # varying peaks so none sit at the saturation ceiling (detect_stars excludes those)
    stars = [(80, 90, 0.70), (200, 120, 0.55), (300, 300, 0.45),
             (150, 280, 0.60), (330, 80, 0.40), (120, 200, 0.50)]
    for (x, y, pk) in stars:
        _star(img, x, y, pk, fwhm, halo_frac=halo_frac if haloed else 0.0)
    return img.astype(np.float32)


def _analyze_array(img, n_use=20, rmax=40, k=5.0):
    bg, sigma = (0.02, 0.001)
    import psf_image as pi
    bg, sigma = pi.estimate_background(img)
    stars = pi.detect_stars(img, bg, sigma, k=k, max_pix=2500)
    idx, fwhm = sh.halo_indices(img, stars, bg, n_use, rmax)
    return idx, fwhm


def test_haloed_higher_index():
    clean_idx, _ = _analyze_array(_field(False))
    halo_idx, _ = _analyze_array(_field(True, halo_frac=0.30))
    assert len(clean_idx) >= 3 and len(halo_idx) >= 3, "not enough stars detected"
    assert np.median(halo_idx) > np.median(clean_idx) + 0.02, \
        "haloed field should score higher (%.4f vs %.4f)" % (np.median(halo_idx), np.median(clean_idx))


def test_clean_index_low():
    idx, _ = _analyze_array(_field(False))
    assert np.median(idx) < 0.03, "clean stars should have low halo index (%.4f)" % np.median(idx)


def test_fwhm_recovery():
    _, fwhm = _analyze_array(_field(False, fwhm=4.0))
    assert abs(np.median(fwhm) - 4.0) < 1.2, "FWHM recovery off (%.2f vs 4.0)" % np.median(fwhm)


def test_suggest_halo_monotonic():
    vals = [sh.suggest_value(i) for i in (0.01, 0.05, 0.08, 0.12, 0.20, 0.40)]
    assert vals == sorted(vals, reverse=True), "halo suggestion should be non-increasing: %s" % vals
    assert vals[0] == 0.0 and vals[-1] == sh.HALO_FLOOR


def test_suggest_sharpen_monotonic():
    vals = [sh.suggest_sharpen(f) for f in (2.0, 3.0, 5.0, 8.0, 12.0)]
    assert vals == sorted(vals), "sharpen suggestion should be non-decreasing with FWHM: %s" % vals
    assert vals[0] == 0.10


def test_fixed_annulus_fwhm_independent():
    # the confound fix: same physical halo, two core FWHMs. A FIXED-pixel annulus
    # (where the core is negligible) must give ~the same halo index regardless of
    # FWHM — that's what makes before/after-BXT comparison honest.
    import psf_image as pi

    def fixed_idx(fwhm):
        img = _field(True, fwhm=fwhm, halo_frac=0.15)
        bg, sig = pi.estimate_background(img)
        stars = pi.detect_stars(img, bg, sig, k=5.0, max_pix=2500)
        idx, _ = sh.halo_indices(img, stars, bg, 20, 40, annulus_px=(6, 12))
        return float(np.median(idx))

    a, b = fixed_idx(2.0), fixed_idx(4.0)
    assert a > 0 and b > 0, "no halo measured in fixed annulus"
    assert abs(a - b) / max(a, b) < 0.25, \
        "fixed annulus should be ~FWHM-independent (%.4f vs %.4f)" % (a, b)


def test_reduction_direction():
    before, _ = _analyze_array(_field(True, halo_frac=0.40))
    after, _ = _analyze_array(_field(True, halo_frac=0.10))
    red = 100 * (1 - np.median(after) / max(np.median(before), 1e-9))
    assert red > 20, "reducing the halo amplitude should drop the index (got %.1f%%)" % red


def run():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print("PASS  %s" % t.__name__)
        except AssertionError as e:
            failed += 1
            print("FAIL  %s: %s" % (t.__name__, e))
        except Exception as e:  # noqa
            failed += 1
            print("ERROR %s: %s" % (t.__name__, e))
    print("\n%d/%d passed" % (len(tests) - failed, len(tests)))
    return failed


if __name__ == "__main__":
    raise SystemExit(1 if run() else 0)
