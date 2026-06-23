#!/usr/bin/env python3
"""gradient_check.py — QA for gradient-correction results (GraXpert / MGC / DBE).

Measures how well a gradient-removal step flattened the sky background **without
eating extended-object signal** — the classic over-subtraction failure on
frame-filling nebulae like M42, where the tool mistakes the nebula for
background and subtracts its faint outer wings.

Works on a single corrected image (optionally with its background model), and
can A/B two corrected images (e.g. GraXpert vs MGC+DR2) to pick the winner.

Metrics
  * background flatness — percentile spread of local sky across an NxN grid,
                          normalised to the median (comparable across images)
  * over-subtraction    — negative-pixel fraction + darkest-tile deficit (in MAD)
  * wing signal         — mean flux above sky in an annulus around the object
                          (the faint outer nebulosity a gradient step can eat)
  * model imprint       — correlation of a background MODEL with the object
                          structure; high => the model contains the nebula (bad)

Reads .xisf (uncompressed monolithic) and .fit/.fits via psf_image's readers.
Pure numpy; scipy used if present (graceful fallback); PIL only for --png.
Run from the repo root:

    python3 scripts/gradient_check.py corrected.xisf --model bg.xisf --png out
    python3 scripts/gradient_check.py methodB.xisf --against methodA.xisf --json

See 04_Processing/Pixinsight/Gradient-Check.md and the gradient sections of the
QuadBand-OSC / RGB workflows.
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from psf_image import read_image  # noqa: E402  (shared XISF/FITS readers)


def _down(a, factor):
    return a[::factor, ::factor] if factor > 1 else a


def _smooth(a, size):
    try:
        from scipy.ndimage import uniform_filter
        return uniform_filter(a, size=max(1, size))
    except Exception:
        return a


# --------------------------------------------------------------------------- #
# Metrics                                                                      #
# --------------------------------------------------------------------------- #
def background_flatness(img, grid=4, pct=10.0):
    """P-th percentile of each NxN tile = local sky; spread normalised to median.

    A flat background -> every tile reports the same local sky -> small spread.
    rel_spread is scale-independent so two corrections can be compared directly.
    """
    H, W = img.shape
    ys = np.linspace(0, H, grid + 1).astype(int)
    xs = np.linspace(0, W, grid + 1).astype(int)
    tiles = []
    for i in range(grid):
        for j in range(grid):
            t = img[ys[i]:ys[i + 1], xs[j]:xs[j + 1]]
            tiles.append(float(np.percentile(t, pct)))
    tiles = np.array(tiles)
    med = float(np.median(tiles))
    spread = float(tiles.max() - tiles.min())
    return {
        "tile_bg_min": float(tiles.min()),
        "tile_bg_max": float(tiles.max()),
        "tile_bg_median": med,
        "spread": spread,
        "rel_spread": spread / (abs(med) + 1e-12),
        "std": float(tiles.std()),
    }


def oversubtraction(img, flat):
    """Negative-pixel fraction + how far the darkest tile fell below the median tile (MAD)."""
    neg = float((img < 0).mean())
    mad = float(np.median(np.abs(img - np.median(img))) * 1.4826) + 1e-12
    deficit = (flat["tile_bg_median"] - flat["tile_bg_min"]) / mad
    return {"neg_fraction": neg, "dark_tile_deficit_mad": float(deficit)}


def object_center(img, down=8, smooth=3):
    """Pixel coords of the brightest large-scale structure (the object core)."""
    s = _smooth(_down(img, down).astype(np.float64), smooth)
    iy, ix = np.unravel_index(int(np.argmax(s)), s.shape)
    return int(iy * down), int(ix * down)


def wing_signal(img, center, r_in=0.10, r_out=0.30, bg=None, down=4):
    """Mean flux above sky in an annulus around the object = retained outer nebulosity."""
    s = _down(img, down).astype(np.float64)
    H, W = s.shape
    cy, cx = center[0] / down, center[1] / down
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt((yy - cy) ** 2 + (xx - cx) ** 2)
    rmax = min(H, W) / 2.0
    ann = (r >= r_in * rmax) & (r <= r_out * rmax)
    if bg is None:
        bg = float(np.percentile(s, 10))
    vals = s[ann] - bg
    return {
        "wing_mean_above_bg": float(vals.mean()),
        "wing_median_above_bg": float(np.median(vals)),
        "annulus_px": int(ann.sum()),
    }


def model_imprint(model, corrected, down=16):
    """Pearson corr between a background MODEL and the object structure.

    The model should be smooth and contain NO object. We correlate the
    downsampled, smoothed model against the corrected image's positive
    (object) signal: a high |corr| means the model followed the nebula -> the
    gradient step is about to subtract real signal.
    """
    m = _smooth(_down(model, down).astype(np.float64), 5)
    c = _smooth(_down(corrected, down).astype(np.float64), 5)
    h = min(m.shape[0], c.shape[0])
    w = min(m.shape[1], c.shape[1])
    m = m[:h, :w]
    c = np.clip(c[:h, :w], 0, None)
    mf = (m - m.mean()).ravel()
    cf = (c - c.mean()).ravel()
    denom = np.sqrt((mf ** 2).sum()) * np.sqrt((cf ** 2).sum()) + 1e-12
    return float((mf * cf).sum() / denom)


# --------------------------------------------------------------------------- #
# Rendering                                                                    #
# --------------------------------------------------------------------------- #
def render_png(img, out, down=8, strength=40.0, self_norm=False):
    from PIL import Image
    s = _down(img, down).astype(np.float64)
    if self_norm:                      # reveal a model's own (subtle) structure
        v = (s - s.min()) / (s.max() - s.min() + 1e-12)
    else:                              # asinh autostretch for sky images
        blk = np.percentile(s, 5)
        v = np.clip(s - blk, 0, None)
        v = v / (np.percentile(v, 99.7) + 1e-12)
        v = np.arcsinh(v * strength) / np.arcsinh(strength)
        v = np.clip(v, 0, 1)
    Image.fromarray((v * 255).astype(np.uint8)).save(out)
    return out


# --------------------------------------------------------------------------- #
# Assembly                                                                     #
# --------------------------------------------------------------------------- #
def analyze(path, grid=4, pct=10.0, model=None, png=None, _keep_img=False):
    img = read_image(path)
    flat = background_flatness(img, grid, pct)
    over = oversubtraction(img, flat)
    cen = object_center(img)
    wing = wing_signal(img, cen, bg=flat["tile_bg_median"])
    rep = {"path": path, "shape": [int(img.shape[0]), int(img.shape[1])],
           "center": list(cen), "flatness": flat, "oversub": over, "wing": wing}
    if model:
        mimg = read_image(model)
        rep["model"] = {
            "contrast": float((mimg.max() - mimg.min()) / (abs(np.median(mimg)) + 1e-12)),
            "imprint_corr": model_imprint(mimg, img),
        }
        if png:
            render_png(mimg, png + "_model.png", self_norm=True)
    if png:
        render_png(img, png + "_corrected.png")
    if _keep_img:
        rep["_img"] = img
    return rep


def compare(a, b):
    """A/B verdict between two corrected images of the same (registered) field."""
    cen = a["center"]
    wa = wing_signal(a["_img"], cen, bg=a["flatness"]["tile_bg_median"])
    wb = wing_signal(b["_img"], cen, bg=b["flatness"]["tile_bg_median"])
    fa = a["flatness"]["rel_spread"]
    fb = b["flatness"]["rel_spread"]
    flatter = a["path"] if fa <= fb else b["path"]
    more_wing = a["path"] if wa["wing_mean_above_bg"] >= wb["wing_mean_above_bg"] else b["path"]
    # verdict: prefer more wing signal as long as flatness is within 2x of the flatter one
    if flatter == more_wing:
        winner = more_wing
        why = "flatter background AND more wing signal"
    elif max(fa, fb) <= 2.0 * min(fa, fb):
        winner = more_wing
        why = "comparable flatness; kept more wing signal"
    else:
        winner = flatter
        why = "markedly flatter background (other method over-flattened/ate signal)"
    return {"flatter": flatter, "more_wing_signal": more_wing,
            "rel_spread_a": fa, "rel_spread_b": fb,
            "wing_a": wa["wing_mean_above_bg"], "wing_b": wb["wing_mean_above_bg"],
            "winner": winner, "reason": why}


def _print_report(r):
    f, o, w = r["flatness"], r["oversub"], r["wing"]
    print(f"== {os.path.basename(r['path'])} ==  shape {r['shape']}  object@{r['center']}")
    print(f"  flatness : tile-bg median {f['tile_bg_median']:.6g}  spread {f['spread']:.3g}"
          f"  rel_spread {f['rel_spread']:.4f}  (lower = flatter)")
    print(f"  oversub  : negatives {o['neg_fraction']*100:.2f}%  darkest-tile deficit {o['dark_tile_deficit_mad']:.2f} MAD")
    print(f"  wing     : mean-above-bg {w['wing_mean_above_bg']:.6g}  median {w['wing_median_above_bg']:.6g}  ({w['annulus_px']} px)")
    if "model" in r:
        m = r["model"]
        flag = "  <-- IMPRINT: model contains the object!" if abs(m["imprint_corr"]) > 0.30 else ""
        print(f"  model    : contrast {m['contrast']:.3f}  imprint_corr {m['imprint_corr']:.3f}{flag}")


def _strip(r):
    r = dict(r)
    r.pop("_img", None)
    return r


def main(argv=None):
    ap = argparse.ArgumentParser(description="Gradient-correction QA (flatness / over-subtraction / wing / model imprint).")
    ap.add_argument("image", help="corrected image (.xisf/.fit)")
    ap.add_argument("--model", help="its background model (.xisf/.fit) — adds contrast + imprint check")
    ap.add_argument("--against", help="second corrected image to A/B compare (same field)")
    ap.add_argument("--png", help="write preview PNG(s) with this path prefix")
    ap.add_argument("--grid", type=int, default=4, help="flatness grid N (default 4)")
    ap.add_argument("--pct", type=float, default=10.0, help="per-tile sky percentile (default 10)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args(argv)

    need_img = args.against is not None
    a = analyze(args.image, args.grid, args.pct, args.model,
                args.png, _keep_img=need_img)
    out = {"primary": _strip(a)}
    if args.against:
        b = analyze(args.against, args.grid, args.pct, None,
                    (args.png + "_B") if args.png else None, _keep_img=True)
        out["against"] = _strip(b)
        out["compare"] = compare(a, b)

    if args.json:
        print(json.dumps(out, indent=2))
    else:
        _print_report(a)
        if args.against:
            _print_report(b)
            c = out["compare"]
            print(f"\n>> flatter: {os.path.basename(c['flatter'])}"
                  f"   more wing signal: {os.path.basename(c['more_wing_signal'])}")
            print(f">> WINNER: {os.path.basename(c['winner'])}  ({c['reason']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
