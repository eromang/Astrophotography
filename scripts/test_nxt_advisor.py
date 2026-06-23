#!/usr/bin/env python3
"""
test_nxt_advisor.py — synthetic tests for nxt_advisor.py

Run from repo root:  python3 scripts/test_nxt_advisor.py
"""

import numpy as np
from scipy.ndimage import gaussian_filter

import nxt_advisor as nx


def test_color_ratio_detected():
    # true CHROMINANCE noise: anti-correlated across channels (R+n, B-n) -> cancels in
    # luminance, large in chroma -> high ratio. (Independent per-channel noise caps at
    # ~sqrt(2) because it leaks into luminance via the mean.)
    rng = np.random.default_rng(0)
    H = W = 120
    L = rng.normal(0, 0.0003, (H, W))      # small shared luminance noise
    n = rng.normal(0, 0.0012, (H, W))      # chroma noise
    roi = np.stack([0.05 + L + n, 0.05 + L, 0.05 + L - n]).astype(np.float32)
    m = nx.measure_noise(roi)
    assert m["color_intensity_ratio"] > 1.3, "should detect colour-dominant noise (%.2f)" % m["color_intensity_ratio"]
    assert nx.suggest(m)["hf_color"] >= 0.95, "colour-dominant -> push HF colour hard"


def test_intensity_dominant():
    # luminance noise large, colour noise tiny -> ratio < 1
    rng = np.random.default_rng(2)
    H = W = 120
    L = rng.normal(0, 0.001, (H, W))
    roi = np.stack([0.05 + L + rng.normal(0, 0.0001, (H, W)) for _ in range(3)]).astype(np.float32)
    m = nx.measure_noise(roi)
    assert m["color_intensity_ratio"] < 1.0, "should be intensity-dominant (%.2f)" % m["color_intensity_ratio"]
    assert nx.suggest(m)["hf_color"] == 0.90, "low ratio -> colour stays at floor 0.90"


def test_corr_scale_white_vs_correlated():
    rng = np.random.default_rng(1)
    white = rng.normal(0, 1, (150, 150))
    assert nx._autocorr_scale(white) < 1.6, "white noise should have ~1px scale"
    corr = gaussian_filter(rng.normal(0, 1, (150, 150)), 2.0)
    assert nx._autocorr_scale(corr) > 2.0, "blurred noise should have a larger scale"


def test_scale_into_suggestion():
    base = {"color_intensity_ratio": 1.5, "sigma_intensity": 1e-3}
    small = nx.suggest({**base, "corr_scale_px": 1.0})["hf_lf_scale_px"]
    large = nx.suggest({**base, "corr_scale_px": 4.0})["hf_lf_scale_px"]
    assert large > small, "larger correlation scale -> larger HF/LF Scale"


def test_iterations_by_noise():
    base = {"color_intensity_ratio": 1.2, "corr_scale_px": 1.5}
    assert nx.suggest({**base, "sigma_intensity": 1e-3})["iterations"] == 2
    assert nx.suggest({**base, "sigma_intensity": 1e-4})["iterations"] == 1


def test_mono_no_color_keys():
    m = {"color_intensity_ratio": 0.0, "sigma_intensity": 1e-3, "corr_scale_px": 1.5}
    s = nx.suggest(m, mono=True)
    assert "hf_color" not in s and "lf_color" not in s, "mono image should not get colour suggestions"
    assert "hf_intensity" in s


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
