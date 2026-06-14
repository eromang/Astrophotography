#!/usr/bin/env python3
"""Tests for guiding_impact.py — closed-form physics + the seeing-quadrature
properties that separate a correct translator from a misleading one.

Run from repo root:  python3 scripts/test_guiding_impact.py
Pure stdlib (math) — same deps as the script.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import guiding_impact as G


def _close(a, b, tol=1e-6):
    return abs(a - b) < tol


def test_image_scale_redcat():
    # ASI2600MC (3.76 um) on RedCat 51 (250 mm) -> 3.10 arcsec/px
    s = G.image_scale(250.0, 3.76)
    print(f"  image_scale RedCat: {s:.3f} arcsec/px (expect ~3.10)")
    assert abs(s - 3.103) < 0.01


def test_image_scale_modifiers_only_change_sampling():
    # reducer shortens focal -> bigger arcsec/px; binning enlarges pixel likewise
    base = G.image_scale(800.0, 3.76)
    red = G.image_scale(800.0, 3.76, reducer=0.8)
    binned = G.image_scale(800.0, 3.76, binning=2)
    assert _close(red, base / 0.8, 1e-9)
    assert _close(binned, base * 2.0, 1e-9)
    print(f"  modifiers: base {base:.3f}  reducer0.8 {red:.3f}  bin2 {binned:.3f}")


def test_rms_to_fwhm_factor():
    # the whole point: FWHM = 2.355 x RMS
    assert _close(G.rms_to_fwhm(1.0), 2.3548, 1e-3)
    assert _close(G.rms_to_fwhm(0.65), 1.5306, 1e-3)
    print(f"  rms_to_fwhm(0.65) = {G.rms_to_fwhm(0.65):.4f}\" (expect 1.531)")


def test_basic_quadrature_closed_form():
    # focal/pixel irrelevant to the arcsec verdict; check the quadrature math.
    # total 1.0" -> axis 1/sqrt2 = 0.7071 -> blur 2.355*0.7071 = 1.6651"
    # with seeing 3.0": total = sqrt(3^2 + 1.6651^2) = 3.4318"
    r = G.analyze_basic(250.0, 3.76, total_rms=1.0, seeing_fwhm=3.0)
    assert _close(r["guiding_fwhm"], 1.6651, 1e-3)
    assert _close(r["total_fwhm"], math.hypot(3.0, 1.6651), 1e-3)
    print(f"  basic: guiding {r['guiding_fwhm']:.4f}\"  total {r['total_fwhm']:.4f}\" "
          f"(+{r['degradation']*100:.0f}%)")


def test_seeing_drowns_out_ra_dec_imbalance():
    # THE key property. RA 0.8 / DEC 0.4 is a 2:1 RMS imbalance. A naive
    # ratio-only tool predicts ~50% ellipticity. With seeing folded into BOTH
    # axes, realised ellipticity must be small (~0.11), not alarming.
    r = G.analyze_advanced(250.0, 3.76, ra_rms=0.8, dec_rms=0.4, seeing_fwhm=3.0)
    naive = 1.0 - 0.4 / 0.8  # 0.50
    print(f"  advanced: ellipticity {r['ellipticity']:.3f} "
          f"(naive ratio would scream {naive:.2f})")
    assert r["dominant_axis"] == "RA"
    assert 0.08 < r["ellipticity"] < 0.14, r["ellipticity"]
    assert r["ellipticity"] < naive / 3  # seeing must crush it well below naive


def test_equal_axes_give_round_stars():
    # RA == DEC -> zero ellipticity regardless of seeing
    r = G.analyze_advanced(250.0, 3.76, ra_rms=0.6, dec_rms=0.6, seeing_fwhm=2.5)
    assert _close(r["ellipticity"], 0.0, 1e-9)
    print(f"  equal axes: ellipticity {r['ellipticity']:.6f} (round)")


def test_basic_advanced_consistency():
    # Basic(total) must equal Advanced(RA=DEC=total/sqrt2) on the blur figures.
    total = 1.0
    axis = total / math.sqrt(2.0)
    b = G.analyze_basic(250.0, 3.76, total_rms=total, seeing_fwhm=3.0)
    a = G.analyze_advanced(250.0, 3.76, ra_rms=axis, dec_rms=axis, seeing_fwhm=3.0)
    assert _close(b["total_fwhm"], a["mean_fwhm"], 1e-9)
    assert _close(b["total_fwhm"], a["major_fwhm"], 1e-9)
    print(f"  consistency: basic total {b['total_fwhm']:.4f}\" == "
          f"advanced mean {a['mean_fwhm']:.4f}\"")


def test_perfect_guiding_no_degradation():
    r = G.analyze_basic(250.0, 3.76, total_rms=0.0, seeing_fwhm=3.0)
    assert _close(r["total_fwhm"], 3.0, 1e-9)
    assert _close(r["degradation"], 0.0, 1e-9)
    assert "NEGLIGIBLE" in r["verdict"]
    print(f"  zero RMS: total {r['total_fwhm']:.2f}\" verdict={r['verdict'][:11]}")


def test_bad_guiding_is_flagged_dominant():
    # huge RMS in great seeing -> guiding dominates
    r = G.analyze_basic(250.0, 3.76, total_rms=4.0, seeing_fwhm=1.5)
    assert r["degradation"] > 0.30
    assert "DOMINANT" in r["verdict"]
    print(f"  bad guiding: +{r['degradation']*100:.0f}% -> {r['verdict'][:8]}")


def test_seeing_band_resolution():
    assert _close(G.resolve_seeing(None, "ok"), 3.0)
    assert _close(G.resolve_seeing(2.2, "ok"), 2.2)  # explicit overrides band
    print("  seeing band: ok->3.0, explicit 2.2 overrides")


def test_rms_in_pixels():
    # 1.0" total at 3.10 arcsec/px -> 0.32 px
    r = G.analyze_basic(250.0, 3.76, total_rms=1.0, seeing_fwhm=3.0)
    assert _close(r["rms_px"], 1.0 / r["scale"], 1e-9)
    assert 0.30 < r["rms_px"] < 0.34
    print(f"  rms_px: 1.0\" -> {r['rms_px']:.3f} px (sub-pixel on RedCat)")


def test_cli_basic(capture=True):
    rc = G.main(["--focal", "250", "--pixel", "3.76", "--rms", "0.8"])
    assert rc == 0
    print("  cli basic: exit 0")


def test_cli_advanced():
    rc = G.main(["--focal", "250", "--pixel", "3.76",
                 "--ra", "0.8", "--dec", "0.4", "--seeing", "3.0"])
    assert rc == 0
    print("  cli advanced: exit 0")


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
