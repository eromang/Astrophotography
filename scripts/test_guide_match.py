#!/usr/bin/env python3
"""Tests for guide_match.py — closed-form scale match, the centroiding model
that kills the 1:1 myth, and OAG-mode focal inheritance.

Run from repo root:  python3 scripts/test_guide_match.py
Pure stdlib — imports guiding_impact for image scale.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import guide_match as M


def _close(a, b, tol=1e-6):
    return abs(a - b) < tol


def test_redcat_uniguide_scales():
    # RedCat 250/3.76 imaging, UniGuide 120/3.75 guide -> 3.10 / 6.45, ratio 2.08
    r = M.analyze(250.0, 3.76, 3.75, guide_focal=120.0)
    print(f"  redcat+uniguide: img {r['img_scale']:.2f} guide {r['guide_scale']:.2f} "
          f"ratio {r['ratio']:.2f}x")
    assert _close(r["img_scale"], 3.102, 0.01)
    assert _close(r["guide_scale"], 6.446, 0.01)
    assert _close(r["ratio"], 2.078, 0.01)


def test_two_x_ratio_is_good_not_bad():
    # THE point: a 2x coarser guide pixel must read GOOD, not fail the 1:1 myth.
    r = M.analyze(250.0, 3.76, 3.75, guide_focal=120.0, centroid=0.1)
    # min motion = 0.1 * 6.45 = 0.645" = 0.208 imaging px
    assert _close(r["min_motion_arcsec"], 0.1 * r["guide_scale"], 1e-9)
    assert _close(r["min_motion_img_px"], 0.1 * r["ratio"], 1e-9)
    assert 0.18 < r["min_motion_img_px"] < 0.24
    assert "GOOD" in r["verdict"]
    print(f"  2x ratio: min motion {r['min_motion_img_px']:.2f} img px -> "
          f"{r['verdict'][:4]}")


def test_min_motion_equals_centroid_times_ratio():
    # identity that anchors the verdict on physics, not the raw ratio
    r = M.analyze(500.0, 3.0, 4.0, guide_focal=200.0, centroid=0.15)
    assert _close(r["min_motion_img_px"], r["centroid"] * r["ratio"], 1e-12)
    print(f"  identity: min_px {r['min_motion_img_px']:.3f} == "
          f"centroid*ratio {r['centroid']*r['ratio']:.3f}")


def test_poor_match_flagged():
    # tiny guide focal + big guide pixel -> very coarse guide scale
    r = M.analyze(1000.0, 3.0, 6.0, guide_focal=60.0, centroid=0.1)
    print(f"  coarse guider: ratio {r['ratio']:.1f}x, min {r['min_motion_img_px']:.2f}"
          f" img px -> {r['verdict'][:4]}")
    assert r["min_motion_img_px"] > 2.0
    assert "POOR" in r["verdict"]


def test_dim_star_centroid_degrades():
    # same rig, worse centroiding (dim star) -> worse min motion
    good = M.analyze(250.0, 3.76, 3.75, guide_focal=120.0, centroid=0.1)
    dim = M.analyze(250.0, 3.76, 3.75, guide_focal=120.0, centroid=0.4)
    assert dim["min_motion_img_px"] > good["min_motion_img_px"]
    assert _close(dim["min_motion_img_px"], 4 * good["min_motion_img_px"], 1e-9)
    print(f"  dim star: 0.1px {good['min_motion_img_px']:.2f} -> "
          f"0.4px {dim['min_motion_img_px']:.2f} img px")


def test_oag_inherits_imaging_focal():
    # OAG: guide scale uses the imaging focal length, not a guide scope's
    img_focal, img_pixel, guide_pixel = 800.0, 3.76, 2.9
    r = M.analyze(img_focal, img_pixel, guide_pixel, oag=True)
    from guiding_impact import image_scale
    expect_guide = image_scale(img_focal, guide_pixel)  # focal inherited
    assert _close(r["guide_scale"], expect_guide, 1e-9)
    assert _close(r["eff_guide_focal"], img_focal, 1e-9)
    assert r["mode"] == "oag"
    print(f"  oag: guide scale {r['guide_scale']:.2f} at inherited "
          f"{r['eff_guide_focal']:.0f} mm")


def test_oag_reducer_inherited():
    # an imaging reducer shifts the OAG guide scale too (pickoff after reducer)
    base = M.analyze(800.0, 3.76, 2.9, oag=True)
    red = M.analyze(800.0, 3.76, 2.9, oag=True, img_reducer=0.8)
    assert _close(red["guide_scale"], base["guide_scale"] / 0.8, 1e-9)
    assert _close(red["eff_guide_focal"], 800.0 * 0.8, 1e-9)
    print(f"  oag reducer: {base['guide_scale']:.2f} -> {red['guide_scale']:.2f} "
          f"with 0.8x")


def test_guide_binning_changes_scale_only():
    base = M.analyze(250.0, 3.76, 3.75, guide_focal=120.0)
    binned = M.analyze(250.0, 3.76, 3.75, guide_focal=120.0, guide_binning=2)
    assert _close(binned["guide_scale"], base["guide_scale"] * 2.0, 1e-9)
    assert _close(binned["img_scale"], base["img_scale"], 1e-9)  # imaging untouched
    print(f"  guide bin2: guide {base['guide_scale']:.2f} -> "
          f"{binned['guide_scale']:.2f}, imaging fixed")


def test_centroid_bounds():
    try:
        M.analyze(250.0, 3.76, 3.75, guide_focal=120.0, centroid=0.0)
        assert False, "centroid 0 should raise"
    except ValueError:
        pass
    try:
        M.analyze(250.0, 3.76, 3.75, guide_focal=120.0, centroid=1.5)
        assert False, "centroid >1 should raise"
    except ValueError:
        pass
    print("  centroid bounds: (0,1] enforced")


def test_guidescope_needs_focal():
    try:
        M.analyze(250.0, 3.76, 3.75)  # no guide focal, not OAG
        assert False, "should raise"
    except ValueError:
        pass
    print("  guide-scope mode requires --guide-focal")


def test_cli_scope_and_oag():
    assert M.main(["--img-focal", "250", "--img-pixel", "3.76",
                   "--guide-focal", "120", "--guide-pixel", "3.75"]) == 0
    assert M.main(["--img-focal", "800", "--img-pixel", "3.76",
                   "--guide-pixel", "2.9", "--oag"]) == 0
    print("  cli: scope + oag exit 0")


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
