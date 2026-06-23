#!/usr/bin/env python3
"""Tests for gradient_check.py — synthetic gradient + nebula recovery.

Builds a scene = pedestal + linear gradient + (bright core + faint wing) nebula
+ noise, then checks that the metrics correctly distinguish:
  * a GOOD correction (true gradient removed -> flat bg, wings intact)
  * a BAD  correction (model also ate the nebula -> wings lost, center deficit)
and that model-imprint flags a model that contains the object.

Run from repo root:  python3 scripts/test_gradient_check.py
Pure numpy (+ scipy if present, same as the script).
"""
import os
import sys
import tempfile
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gradient_check as G
import psf_image as P

SHAPE = (400, 600)
PED = 0.020
RNG = np.random.default_rng(7)


def _gradient(shape, amp=0.010):
    yy, xx = np.mgrid[0:shape[0], 0:shape[1]]
    return amp * (xx / shape[1]) + 0.5 * amp * (yy / shape[0])


def _gauss(shape, cy, cx, sigma, amp):
    yy, xx = np.mgrid[0:shape[0], 0:shape[1]]
    return amp * np.exp(-(((yy - cy) ** 2 + (xx - cx) ** 2) / (2 * sigma ** 2)))


def _scene():
    cy, cx = SHAPE[0] // 2, SHAPE[1] // 2
    grad = _gradient(SHAPE)
    core = _gauss(SHAPE, cy, cx, 18, 0.40)       # bright core
    wing = _gauss(SHAPE, cy, cx, 80, 0.010)      # faint extended wing
    nebula = core + wing
    noise = RNG.normal(0, 0.0008, SHAPE)
    scene = PED + grad + nebula + noise
    return scene.astype(np.float32), grad, nebula, (cy, cx)


def test_flatness_detects_gradient():
    scene, grad, _, _ = _scene()
    corrected = (scene - grad).astype(np.float32)      # true gradient removed
    f_raw = G.background_flatness(scene)
    f_cor = G.background_flatness(corrected)
    print(f"  flatness rel_spread: raw {f_raw['rel_spread']:.4f} -> corrected {f_cor['rel_spread']:.4f}")
    assert f_cor["rel_spread"] < 0.4 * f_raw["rel_spread"], "correction did not flatten the background"


def test_wing_preserved_vs_eaten():
    scene, grad, nebula, cen = _scene()
    good = (scene - grad).astype(np.float32)
    # BAD model = true gradient + a broad bump co-located with the nebula
    bad_model = grad + _gauss(SHAPE, cen[0], cen[1], 90, 0.012)
    bad = (scene - bad_model).astype(np.float32)
    wg = G.wing_signal(good, cen, bg=G.background_flatness(good)["tile_bg_median"])
    wb = G.wing_signal(bad, cen, bg=G.background_flatness(bad)["tile_bg_median"])
    print(f"  wing mean-above-bg: good {wg['wing_mean_above_bg']:.5f}  bad {wb['wing_mean_above_bg']:.5f}")
    assert wg["wing_mean_above_bg"] > wb["wing_mean_above_bg"], "wing-eating not detected"


def test_model_imprint():
    scene, grad, nebula, cen = _scene()
    corrected = (scene - grad).astype(np.float32)
    good_model = (PED + grad).astype(np.float32)                 # smooth, no object
    bad_model = (PED + grad + _gauss(SHAPE, cen[0], cen[1], 90, 0.012)).astype(np.float32)
    ig = G.model_imprint(good_model, corrected)
    ib = G.model_imprint(bad_model, corrected)
    print(f"  imprint corr: good-model {ig:.3f}  bad-model {ib:.3f}")
    assert ib > ig, "bad model should correlate with object more than good model"
    assert ib > 0.30, "bad model imprint should trip the flag"
    assert ig < 0.30, "good model should not trip the imprint flag"


def test_object_center():
    scene, _, _, cen = _scene()
    cy, cx = G.object_center(scene)
    print(f"  object center: true {cen} -> found ({cy},{cx})")
    assert abs(cy - cen[0]) < 30 and abs(cx - cen[1]) < 30, "object center off"


def test_compare_end_to_end():
    scene, grad, nebula, cen = _scene()
    good = (scene - grad).astype(np.float32)
    bad_model = grad + _gauss(SHAPE, cen[0], cen[1], 90, 0.012)
    bad = (scene - bad_model).astype(np.float32)
    with tempfile.TemporaryDirectory() as d:
        fg = os.path.join(d, "good.fits")
        fb = os.path.join(d, "bad.fits")
        P.write_fits(fg, good)
        P.write_fits(fb, bad)
        a = G.analyze(fg, _keep_img=True)   # good
        b = G.analyze(fb, _keep_img=True)   # bad
        c = G.compare(a, b)
    print(f"  compare winner: {os.path.basename(c['winner'])}  ({c['reason']})")
    assert c["winner"] == fg, "compare should pick the wing-preserving correction"
    assert c["more_wing_signal"] == fg


def main():
    fns = [test_flatness_detects_gradient, test_wing_preserved_vs_eaten,
           test_model_imprint, test_object_center, test_compare_end_to_end]
    for fn in fns:
        print(f"- {fn.__name__}")
        fn()
    print(f"\nAll {len(fns)} gradient_check tests passed.")


if __name__ == "__main__":
    main()
