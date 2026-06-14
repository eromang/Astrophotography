#!/usr/bin/env python3
"""Tests for sampling.py — closed-form sampling math + the input-priority and
regime boundaries that make the verdict honest.

Run from repo root:  python3 scripts/test_sampling.py
Pure stdlib — same deps as the script (imports guiding_impact for image scale).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sampling as S


def _close(a, b, tol=1e-6):
    return abs(a - b) < tol


def test_redcat_is_undersampled():
    # RedCat 250mm + ASI2600 3.76um, OK seeing 3.0" -> ~0.97 px/FWHM
    scale = S.image_scale(250.0, 3.76)
    ref, src = S.resolve_reference(scale, quality="ok")
    r = S.analyze(250.0, 3.76, ref)
    print(f"  redcat: {r['samples']:.2f} px/FWHM -> {r['regime'][:11]}")
    assert _close(r["scale"], 3.102, 0.01)
    assert 0.90 < r["samples"] < 1.05
    assert "UNDERSAMPLED" in r["regime"]


def test_ideal_band_matches_nyquist_convention():
    # ideal pixel scale = FWHM/3.3 (fine) .. FWHM/2.0 (coarse)
    r = S.analyze(250.0, 3.76, ref_fwhm=3.0)
    assert _close(r["ideal_scale_fine"], 3.0 / 3.3, 1e-6)
    assert _close(r["ideal_scale_coarse"], 3.0 / 2.0, 1e-6)
    print(f"  ideal band: {r['ideal_scale_fine']:.2f}-{r['ideal_scale_coarse']:.2f}"
          f" arcsec/px (expect 0.91-1.50)")


def test_balanced_setup():
    # pick a scale that lands mid-band: ~2.65 px/FWHM at FWHM 3.0 -> scale ~1.13
    # focal so that scale = 1.13: focal = 206.265*3.76/1.13 ~ 686 mm
    r = S.analyze(686.0, 3.76, ref_fwhm=3.0)
    print(f"  balanced: scale {r['scale']:.2f}, {r['samples']:.2f} px/FWHM "
          f"-> {r['regime'][:8]}")
    assert S.SAMPLES_MIN <= r["samples"] <= S.SAMPLES_MAX
    assert "BALANCED" in r["regime"]


def test_oversampled_setup():
    # long focal / tiny disk -> many px across the FWHM
    r = S.analyze(2000.0, 3.76, ref_fwhm=2.0)
    print(f"  oversampled: {r['samples']:.2f} px/FWHM -> {r['regime'][:11]}")
    assert r["samples"] > S.SAMPLES_MAX
    assert "OVERSAMPLED" in r["regime"]


def test_regime_boundaries():
    # exactly at 2.0 and 3.3 px/FWHM are inclusive -> balanced
    assert "BALANCED" in S.sampling_verdict(2.0)
    assert "BALANCED" in S.sampling_verdict(3.3)
    assert "UNDERSAMPLED" in S.sampling_verdict(1.99)
    assert "OVERSAMPLED" in S.sampling_verdict(3.31)
    print("  boundaries: [2.0,3.3] balanced inclusive")


def test_fwhm_px_priority_and_conversion():
    # measured px must win and convert via the rig's image scale
    scale = S.image_scale(250.0, 3.76)  # 3.102
    ref, src = S.resolve_reference(scale, fwhm_px=2.3, seeing=3.0, quality="ok")
    assert _close(ref, 2.3 * scale, 1e-9)   # px wins over seeing
    assert "px" in src
    print(f"  fwhm-px: 2.3 px -> {ref:.2f}\" ({src})")


def test_fwhm_arcsec_priority():
    scale = S.image_scale(250.0, 3.76)
    ref, src = S.resolve_reference(scale, fwhm=2.8, quality="ok")
    assert _close(ref, 2.8, 1e-9)
    assert "2.8" in src
    print(f"  fwhm arcsec: {ref:.2f}\" wins over band")


def test_seeing_band_fallback():
    scale = S.image_scale(250.0, 3.76)
    ref, src = S.resolve_reference(scale, quality="ok")
    assert _close(ref, 3.0, 1e-9)
    assert "band" in src
    print(f"  fallback: band ok -> {ref:.1f}\"")


def test_delivered_fwhm_less_undersampled_than_atmosphere():
    # delivered FWHM (coarser) should give MORE px/FWHM than raw seeing -> the
    # honest input makes the rig look less undersampled than the atmosphere band.
    scale = S.image_scale(250.0, 3.76)
    ref_see, _ = S.resolve_reference(scale, quality="ok")          # 3.0"
    ref_meas, _ = S.resolve_reference(scale, fwhm_px=3.4)          # 3.4 px ~ delivered
    r_see = S.analyze(250.0, 3.76, ref_see)
    r_meas = S.analyze(250.0, 3.76, ref_meas)
    print(f"  honesty: atmosphere {r_see['samples']:.2f} vs delivered "
          f"{r_meas['samples']:.2f} px/FWHM")
    assert r_meas["samples"] > r_see["samples"]


def test_balanced_factor_for_redcat():
    # to balance the RedCat you need ~2-3.4x the focal length
    r = S.analyze(250.0, 3.76, ref_fwhm=3.0)
    lo = min(r["balanced_factor_min"], r["balanced_factor_max"])
    hi = max(r["balanced_factor_min"], r["balanced_factor_max"])
    print(f"  to balance: x{lo:.1f}-{hi:.1f} focal")
    assert 1.9 < lo < 2.2 and 3.2 < hi < 3.5


def test_reducer_and_binning_change_scale_only():
    base = S.analyze(800.0, 3.76, ref_fwhm=3.0)
    red = S.analyze(800.0, 3.76, ref_fwhm=3.0, reducer=0.8)
    binned = S.analyze(800.0, 3.76, ref_fwhm=3.0, binning=2)
    assert red["ref_fwhm"] == base["ref_fwhm"] == 3.0   # disk unchanged
    assert _close(red["scale"], base["scale"] / 0.8, 1e-9)
    assert _close(binned["scale"], base["scale"] * 2.0, 1e-9)
    print(f"  modifiers: scale base {base['scale']:.2f} red {red['scale']:.2f} "
          f"bin {binned['scale']:.2f}, disk fixed 3.0\"")


def test_cli_default_and_fwhm_px():
    assert S.main(["--focal", "250", "--pixel", "3.76"]) == 0
    assert S.main(["--focal", "250", "--pixel", "3.76", "--fwhm-px", "2.3"]) == 0
    print("  cli: default + --fwhm-px exit 0")


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
