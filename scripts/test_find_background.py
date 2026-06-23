#!/usr/bin/env python3
"""
test_find_background.py — synthetic tests for find_background.py

Run from repo root:  python3 scripts/test_find_background.py
No pytest needed; prints PASS/FAIL per case and exits non-zero on any failure.
"""

import numpy as np

import find_background as fb


def _box_mean_std_bruteforce(B, size):
    H, W = B.shape
    m = np.zeros((H - size + 1, W - size + 1))
    s = np.zeros_like(m)
    for y in range(m.shape[0]):
        for x in range(m.shape[1]):
            w = B[y:y + size, x:x + size]
            m[y, x] = w.mean()
            s[y, x] = w.std()
    return m, s


def _in_rect(res, rx, ry, rw, rh):
    cx, cy = res["x"] + res["size"] // 2, res["y"] + res["size"] // 2
    return rx <= cx <= rx + rw and ry <= cy <= ry + rh


def test_integral_matches_bruteforce():
    rng = np.random.default_rng(0)
    B = rng.random((60, 80))
    m1, s1 = fb.box_mean_std(B, 16)
    m2, s2 = _box_mean_std_bruteforce(B, 16)
    assert np.allclose(m1, m2, atol=1e-9), "mean map mismatch"
    assert np.allclose(s1, s2, atol=1e-9), "std map mismatch"


def test_avoids_bright_blob():
    # dark flat field with a bright nebula blob in the centre
    img = np.full((1, 400, 400), 0.02, np.float32)
    yy, xx = np.mgrid[0:400, 0:400]
    blob = np.exp(-(((xx - 200) ** 2 + (yy - 200) ** 2) / (2 * 40.0 ** 2)))
    img[0] += (0.6 * blob).astype(np.float32)
    res = fb.find_background(img, size=50)
    # ROI must be dark (far from the bright core)
    assert res["mean"] < 0.05, "ROI landed on bright signal (mean %.3f)" % res["mean"]
    assert not _in_rect(res, 150, 150, 100, 100), "ROI sits on the blob"


def test_prefers_flat_over_noisy():
    # two equally-dark regions: left is flat, right is noisy -> pick the flat half.
    # (FindBackground caps the stddev term, so it lands in the flat half but can
    # sit near the boundary; assert it's clearly flatter than the noisy region.)
    rng = np.random.default_rng(1)
    img = np.full((1, 200, 400), 0.03, np.float32)
    img[0, :, 200:] += rng.normal(0, 0.05, (200, 200)).astype(np.float32)
    res = fb.find_background(img, size=40)
    assert res["x"] + res["size"] // 2 < 200, "ROI chose the noisy half"
    assert res["std"] < 0.03, "ROI not clearly flatter than the noisy region (std %.4f)" % res["std"]


def test_darkest_corner_under_gradient():
    # linear gradient bright->dark left to right; darkest is the right edge
    grad = np.linspace(0.5, 0.02, 300, dtype=np.float32)
    img = np.tile(grad, (300, 1))[None, :, :]
    res = fb.find_background(img, size=40)
    assert res["x"] > 150, "ROI not in the dark (right) half (x=%d)" % res["x"]


def test_exclude_region():
    # darkest spot is top-left; exclude it -> must move elsewhere
    img = np.full((1, 300, 300), 0.1, np.float32)
    img[0, 0:60, 0:60] = 0.01  # darkest patch top-left
    res_free = fb.find_background(img, size=40)
    assert _in_rect(res_free, 0, 0, 60, 60), "did not find the obvious dark patch"
    res_excl = fb.find_background(img, size=40, exclude=[(0, 0, 80, 80)])
    assert not _in_rect(res_excl, 0, 0, 60, 60), "exclusion was ignored"


def test_scale_close_to_exact():
    img = np.full((1, 400, 400), 0.02, np.float32)
    yy, xx = np.mgrid[0:400, 0:400]
    img[0] += (0.6 * np.exp(-(((xx - 300) ** 2 + (yy - 100) ** 2) / (2 * 30.0 ** 2)))).astype(np.float32)
    exact = fb.find_background(img, size=50, scale=1)
    fast = fb.find_background(img, size=50, scale=4)
    # both should land in a dark region (mean low); coords within a few scale-steps
    assert fast["mean"] < 0.05, "scaled search landed on signal"
    assert abs(exact["x"] - fast["x"]) <= 40 and abs(exact["y"] - fast["y"]) <= 40, \
        "scaled ROI far from exact (%d,%d vs %d,%d)" % (fast["x"], fast["y"], exact["x"], exact["y"])


def test_rgb_color_correction():
    # green-biased background -> additive correction should lift R and B toward G
    img = np.zeros((3, 200, 200), np.float32)
    img[0] = 0.03  # R
    img[1] = 0.05  # G (brightest)
    img[2] = 0.035  # B
    res = fb.find_background(img, size=50)
    cc = res["color_correction"]
    assert abs(cc[1]) < 1e-6, "brightest channel correction should be ~0"
    assert cc[0] > cc[1] and cc[2] > cc[1], "corrections should lift dimmer channels"


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
