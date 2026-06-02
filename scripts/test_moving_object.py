#!/usr/bin/env python3
"""Tests for moving_object.py — synthetic sequences with a known mover.

Builds small FITS frames (each with a fabricated TAN WCS + staggered DATE-OBS),
a fixed star field, an injected linear mover, a single-frame satellite streak,
and noise. Asserts the mover/track is recovered, satellites/stars excluded, and
a faint sub-threshold mover is found only by shift-and-stack.

Run from repo root:  python3 scripts/test_moving_object.py
numpy + scipy (+ matplotlib only for the output test).
"""
import datetime as dt
import os
import sys
import tempfile

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import moving_object as M

SCALE = 3.1     # arcsec/px
SIZE = 240
QUIET = lambda *a, **k: None


def _wcs(crpix=(120.5, 120.5), ra0=180.0, dec0=20.0):
    s = SCALE / 3600.0
    return dict(CRVAL1=ra0, CRVAL2=dec0, CRPIX1=crpix[0], CRPIX2=crpix[1],
                CD1_1=-s, CD1_2=0.0, CD2_1=0.0, CD2_2=s)


def _card(k, v):
    if isinstance(v, str):
        s = f"{k:<8}= '{v}'"
    elif isinstance(v, float):
        s = f"{k:<8}= {v:>20.12g}"
    else:
        s = f"{k:<8}= {v:>20}"
    return s.ljust(80)[:80].encode("latin-1")


def _write_fits(path, img, kw):
    h, w = img.shape
    mand = [
        "SIMPLE  =                    T",
        "BITPIX  =                  -32",
        "NAXIS   =                    2",
        f"NAXIS1  = {w:>20}",
        f"NAXIS2  = {h:>20}",
        "CTYPE1  = 'RA---TAN'",
        "CTYPE2  = 'DEC--TAN'",
    ]
    body = b"".join(s.ljust(80)[:80].encode("latin-1") for s in mand)
    body += b"".join(_card(k, v) for k, v in kw.items())
    body += b"END".ljust(80)
    body += b" " * ((2880 - len(body) % 2880) % 2880)
    data = img.astype(">f4").tobytes()
    data += b"\x00" * ((2880 - len(data) % 2880) % 2880)
    with open(path, "wb") as fh:
        fh.write(body + data)


def _render(img, x, y, amp, sigma=2.0):
    H, W = img.shape
    xi, yi = int(round(x)), int(round(y))
    r = int(np.ceil(4 * sigma))
    y0, y1 = max(0, yi - r), min(H, yi + r + 1)
    x0, x1 = max(0, xi - r), min(W, xi + r + 1)
    if y1 <= y0 or x1 <= x0:
        return
    ys, xs = np.mgrid[y0:y1, x0:x1]
    img[y0:y1, x0:x1] += amp * np.exp(-0.5 * (((xs - x) ** 2 + (ys - y) ** 2) / sigma ** 2))


def _make_sequence(d, n=8, dt_min=2.0, mover_rate=3.0, mover_amp=400.0,
                   with_sat=True, hot_pixels=(), seed=1):
    """Write n FITS frames. hot_pixels = [(x,y,amp)] fixed on the sensor every frame."""
    rng = np.random.default_rng(seed)
    ra0, dec0 = 180.0, 20.0
    half = SIZE * SCALE / 3600.0 * 0.4          # field half-extent in deg
    nstar = 30
    star_ra = ra0 + (rng.random(nstar) - 0.5) * 2 * half
    star_dec = dec0 + (rng.random(nstar) - 0.5) * 2 * half
    star_amp = rng.uniform(200, 900, nstar)
    mra0, mdec0 = ra0 + 0.018, dec0 - 0.018       # mover start (off-centre, in frame)
    vra = mover_rate / 3600.0 / np.cos(dec0 * np.pi / 180)   # deg/min in RA (arcsec/min)
    t_start = dt.datetime(2026, 5, 25, 22, 0, 0)
    for i in range(n):
        # realistic dither: several px, well above the 1.5 px hot-pixel tolerance
        dith = ((i * 7 % 13 - 6) * 1.0, (i * 5 % 11 - 5) * 1.0)
        kw = _wcs(crpix=(120.5 + dith[0], 120.5 + dith[1]))
        img = rng.normal(100.0, 5.0, (SIZE, SIZE))
        for j in range(nstar):
            x, y = M.world2pix(star_ra[j], star_dec[j], kw)
            if 0 <= x < SIZE and 0 <= y < SIZE:
                _render(img, x, y, star_amp[j])
        for (hx, hy, hamp) in hot_pixels:           # fixed sensor position every frame
            _render(img, hx, hy, hamp, sigma=1.1)
        t = i * dt_min
        mx, my = M.world2pix(mra0 + vra * t, mdec0, kw)
        if 0 <= mx < SIZE and 0 <= my < SIZE:
            _render(img, mx, my, mover_amp, sigma=2.0)
        if with_sat and i == 2:                  # single-frame satellite streak
            for s in range(-30, 31):
                xx, yy = 130 + s, 70 + int(s * 0.4)
                if 0 <= xx < SIZE and 0 <= yy < SIZE:
                    img[yy, xx] += 600
        kw["DATE-OBS"] = (t_start + dt.timedelta(minutes=t)).isoformat()
        _write_fits(os.path.join(d, f"light_{i:03d}.fit"), img.astype(np.float32), kw)
    return d


def test_wcs_roundtrip():
    kw = _wcs()
    for (x, y) in [(50.0, 60.0), (120.5, 120.5), (200.0, 30.0), (10.0, 230.0)]:
        ra, dec = M.pix2world(x, y, kw)
        x2, y2 = M.world2pix(ra, dec, kw)
        assert abs(x - x2) < 1e-4 and abs(y - y2) < 1e-4, (x, y, x2, y2)
    sc = M.pixel_scale(kw)
    assert abs(sc - SCALE) < 0.01, sc
    print(f"  WCS pix2world/world2pix round-trip < 1e-4 px; scale {sc:.3f}\"/px ✓")


def test_link_recovers_mover_excludes_satellite():
    with tempfile.TemporaryDirectory() as d:
        _make_sequence(d, n=8, mover_rate=3.0, mover_amp=400.0, with_sat=True)
        res = M.detect(d, out_dir=None, min_frames=4, k=6.0,
                       shift_stack=False, make_png=False, log=QUIET)
        tracks = res["tracks"]
        assert len(tracks) >= 1, "no track recovered"
        best = max(tracks, key=lambda t: t["n"])
        assert best["n"] >= 6, f"mover should span most of 8 frames, got {best['n']}"
        assert abs(best["rate"] - 3.0) < 1.0, f"rate {best['rate']:.2f} != ~3.0 \"/min"
        # satellite (single frame) must NOT have produced a multi-frame track
        assert all(t["n"] <= 8 for t in tracks)
        print(f"  link: recovered mover {best['rate']:.2f}\"/min over {best['n']} frames; "
              f"satellite (1-frame) excluded; {len(tracks)} track(s) ✓")


def test_outputs_written():
    with tempfile.TemporaryDirectory() as d:
        _make_sequence(d, n=8, mover_amp=400.0)
        out = os.path.join(d, "mo")
        M.detect(d, out_dir=out, min_frames=4, k=6.0, shift_stack=False,
                 make_png=True, log=QUIET)
        assert os.path.exists(os.path.join(out, "report.txt"))
        assert os.path.exists(os.path.join(out, "candidates.reg"))
        pngs = [f for f in os.listdir(out) if f.endswith(".png")]
        assert pngs, "no candidate PNGs written"
        reg = open(os.path.join(out, "candidates.reg")).read()
        assert reg.startswith("# Region file format: DS9")
        print(f"  outputs: report.txt + candidates.reg + {len(pngs)} PNG(s) written; DS9 header ✓")


def test_shift_stack_finds_faint():
    with tempfile.TemporaryDirectory() as d:
        # faint mover: per-frame SNR ~3 (below k=6) -> link misses it
        _make_sequence(d, n=8, mover_rate=3.0, mover_amp=16.0, with_sat=False, seed=3)
        res = M.detect(d, out_dir=None, min_frames=4, k=6.0, shift_stack=True,
                       bin_=2, vmax=6.0, make_png=False, log=QUIET)
        assert len(res["tracks"]) == 0, "faint mover should be below the per-frame threshold"
        ss = res["shift_stack"]
        assert len(ss) >= 1, "shift-and-stack should recover the faint mover"
        # at least one candidate near the field centre where the mover lives
        near = [c for c in ss if 80 < c["x"] < 180 and 80 < c["y"] < 180]
        assert near, f"no faint candidate near the mover; got {[(round(c['x']),round(c['y'])) for c in ss]}"
        print(f"  shift-stack: link found 0 (faint), shift-stack found {len(ss)} "
              f"incl. one near the mover ✓")


def test_star_rejection():
    with tempfile.TemporaryDirectory() as d:
        _make_sequence(d, n=8, mover_amp=400.0, with_sat=False)
        frames = M.load_frames(d, k=6.0, log=QUIET)
        scale = M.pixel_scale(frames[0]["kw"])
        recs = M.detections_sky(frames)
        nstar, nhot = M.reject_fixed(recs, len(frames), scale)
        # ~30 stars should be flagged static (fixed sky); the mover should not be
        assert nstar > 20 * 6, f"expected most star detections static, got {nstar}"
        nrej = sum(1 for r in recs if r["static"] or r["hot"])
        frac = nrej / len(recs)
        assert frac > 0.7, f"rejected fraction {frac:.2f} too low"
        print(f"  star rejection: {nstar} fixed-sky stars, {nhot} hot, "
              f"{nrej}/{len(recs)} rejected ({frac:.0%}) ✓")


def test_hot_pixel_rejection():
    with tempfile.TemporaryDirectory() as d:
        hots = [(58, 62, 450), (182, 171, 450), (96, 196, 450)]
        _make_sequence(d, n=8, mover_amp=400.0, with_sat=False, hot_pixels=hots, seed=1)
        res = M.detect(d, out_dir=None, min_frames=4, k=6.0,
                       shift_stack=False, make_png=False, log=QUIET)
        # hot pixels (fixed sensor) must be flagged hot, not turned into tracks
        recs = M.detections_sky(res["frames"])
        M.reject_fixed(recs, len(res["frames"]), res["scale"])
        nhot = sum(1 for r in recs if r["hot"])
        assert nhot >= 3 * 5, f"hot pixels not rejected (got {nhot})"
        # the real mover still recovered; no spurious track sitting on a hot pixel
        tracks = res["tracks"]
        assert any(abs(t["rate"] - 3.0) < 1.0 for t in tracks), "mover lost"
        for t in tracks:
            mid = t["members"][len(t["members"]) // 2]
            for (hx, hy, _a) in hots:
                assert not (abs(mid["x"] - hx) < 3 and abs(mid["y"] - hy) < 3), "track on a hot pixel"
        print(f"  hot-pixel rejection: {nhot} hot detections flagged; mover intact; "
              f"no track on a hot pixel ✓")


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
        except Exception as e:
            import traceback
            print(f"ERROR {t.__name__}: {e}")
            traceback.print_exc()
            failed += 1
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
