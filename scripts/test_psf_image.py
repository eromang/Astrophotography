#!/usr/bin/env python3
"""Tests for psf_image.py — synthetic-star recovery + I/O round-trips.

Run from repo root:  python3 scripts/test_psf_image.py
No external deps beyond numpy/scipy (same as the script).
"""
import os
import sys
import tempfile
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import psf_image as P


def _inject_moffat(shape, stars, fwhm, beta, bg=100.0, noise=2.0, seed=0):
    """Build a synthetic image with Moffat stars of known FWHM (px)."""
    rng = np.random.default_rng(seed)
    img = np.full(shape, bg, np.float64)
    s = fwhm / (2 * np.sqrt(2 ** (1 / beta) - 1))
    yy, xx = np.mgrid[0:shape[0], 0:shape[1]]
    for (x0, y0, amp) in stars:
        img += amp * (1 + (((xx - x0) ** 2 + (yy - y0) ** 2) / s ** 2)) ** (-beta)
    img += rng.normal(0, noise, shape)
    return img.astype(np.float32)


def test_moffat_recovery():
    fwhm_true, beta_true = 3.20, 3.0
    rng = np.random.default_rng(1)
    stars = [(rng.uniform(20, 480), rng.uniform(20, 480), rng.uniform(2000, 9000))
             for _ in range(40)]
    img = _inject_moffat((500, 500), stars, fwhm_true, beta_true)
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "syn.fits")
        P.write_fits(f, img)
        r = P.measure(f, function="moffat")
    err = abs(r["fwhm"] - fwhm_true)
    print(f"  moffat: true {fwhm_true:.2f} -> measured {r['fwhm']:.3f} px "
          f"({r['n']} stars, beta {r['beta']:.2f}, err {err:.3f})")
    assert err < 0.20, f"FWHM error too large: {err:.3f}"
    assert r["n"] >= 20, f"too few stars fit: {r['n']}"


def test_gaussian_recovery():
    fwhm_true = 2.80
    s = fwhm_true / (2 * np.sqrt(2 * np.log(2)))
    rng = np.random.default_rng(2)
    stars = [(rng.uniform(20, 480), rng.uniform(20, 480), rng.uniform(3000, 9000))
             for _ in range(40)]
    yy, xx = np.mgrid[0:500, 0:500]
    img = np.full((500, 500), 80.0)
    for (x0, y0, amp) in stars:
        img += amp * np.exp(-0.5 * (((xx - x0) ** 2 + (yy - y0) ** 2) / s ** 2))
    img = (img + rng.normal(0, 2, (500, 500))).astype(np.float32)
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "g.fits")
        P.write_fits(f, img)
        r = P.measure(f, function="gaussian")
    err = abs(r["fwhm"] - fwhm_true)
    print(f"  gaussian: true {fwhm_true:.2f} -> measured {r['fwhm']:.3f} px (err {err:.3f})")
    assert err < 0.20, f"Gaussian FWHM error too large: {err:.3f}"


def test_fits_roundtrip():
    img = (np.random.default_rng(3).random((64, 48)) * 1000).astype(np.float32)
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "rt.fits")
        P.write_fits(f, img)
        back = P.read_fits(f)
    assert back.shape == (64, 48)
    assert np.allclose(back, img, atol=1e-3)
    print(f"  fits round-trip: shape {back.shape} OK")


def test_cfa_green_extraction():
    # smooth function sampled by a green quincunx -> extraction recovers it
    yy, xx = np.mgrid[0:64, 0:64]
    smooth = (1000 + 5 * xx + 3 * yy).astype(np.float32)
    mosaic = smooth.copy()
    # corrupt the non-green (R/B) positions; RGGB greens at (0,1) & (1,0)
    is_green = np.zeros((64, 64), bool)
    is_green[0::2, 1::2] = True
    is_green[1::2, 0::2] = True
    mosaic[~is_green] = -9999.0
    out = P.extract_green(mosaic, "RGGB")
    # green positions preserved exactly
    assert np.allclose(out[is_green], smooth[is_green])
    # interpolated positions close to the underlying smooth function (interior)
    interior = np.zeros((64, 64), bool)
    interior[2:-2, 2:-2] = True
    sel = interior & ~is_green
    err = np.max(np.abs(out[sel] - smooth[sel]))
    print(f"  cfa green: max interior interp error {err:.2f} ADU (smooth gradient)")
    assert err < 2.0


def test_cfa_green_fwhm_consistency():
    # a star sampled on a green quincunx; --cfa green should recover ~same FWHM
    fwhm_true, beta = 3.0, 4.0
    rng = np.random.default_rng(7)
    stars = [(rng.uniform(20, 480), rng.uniform(20, 480), rng.uniform(3000, 9000))
             for _ in range(40)]
    img = _inject_moffat((500, 500), stars, fwhm_true, beta, noise=1.0)
    is_green = np.zeros((500, 500), bool)
    is_green[0::2, 1::2] = True
    is_green[1::2, 0::2] = True
    # simulate a mild R/B offset (mosaic): drop non-green by 30% toward bg
    mosaic = img.copy()
    mosaic[~is_green] = 100 + 0.7 * (img[~is_green] - 100)
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "cfa.fits")
        P.write_fits(f, mosaic.astype(np.float32))
        r = P.measure(f, function="moffat", fixed_beta=beta, cfa="green")
    err = abs(r["fwhm"] - fwhm_true)
    print(f"  cfa green fwhm: true {fwhm_true:.2f} -> {r['fwhm']:.3f} px (err {err:.3f})")
    assert err < 0.30


def test_render_psf():
    psf = P.render_psf(3.0, 3.0)
    assert abs(psf.max() - 1.0) < 1e-6 and psf.shape[0] == psf.shape[1]
    # measure the rendered PSF's own FWHM ~ half-max width across center
    c = psf.shape[0] // 2
    row = psf[c]
    above = np.where(row >= 0.5)[0]
    fwhm = above[-1] - above[0] + 1
    print(f"  render_psf: {psf.shape[0]}px, half-max width ~{fwhm}px (target ~3)")
    assert 2 <= fwhm <= 5


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    print(f"Running {len(tests)} tests...")
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except AssertionError as e:
            print(f"FAIL {t.__name__}: {e}")
            failed += 1
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
