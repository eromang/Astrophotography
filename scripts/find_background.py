#!/usr/bin/env python3
"""
find_background.py — fast optimal background ROI finder for linear astro images.

A numpy / integral-image reimplementation of the SetiAstro "FindBackground.js"
PixInsight script (Gerrit Erdt & Franklin Marek, 2024). Finds the darkest,
flattest `size`x`size` window in an image — the best background region to feed a
PixInsight process ROI: SPCC background neutralization, MultiscaleAdaptiveStretch
background reference, BackgroundNeutralization, or DBE sampling.

Why this is faster
------------------
FindBackground.js samples pixels one-by-one in PixInsight's JS engine
(O(N * window^2)) and then *approximates* the best spot with gradient descent
from a handful of seed points. This script computes the per-window mean and
standard deviation for EVERY candidate position in a single O(N) pass using
integral images (summed-area tables), then takes the EXACT global minimum — no
gradient descent, seconds instead of minutes on a ~96 MP drizzled master.

Scoring (faithful to FindBackground.js defaults: average + standard deviation)
------------------------------------------------------------------------------
A window is good when it is both DARK (low mean) and FLAT (low stddev). Per
window the script forms, exactly like the JS `getScore()` default path:

    invAvg = 1 / mean
    sdevTerm = min( invAvg * SDEV_CAP, sdevNorm / sdev )
    score = 1 / (invAvg + sdevTerm)          # MINIMISE this

`sdevNorm` is derived from the image's own tile statistics (the JS
`setupFilterNormalization`), so the stddev term is scaled to the image. One
deliberate fix vs the JS: brightness is the per-pixel channel MEAN throughout
(the JS mixes a channel-sum into the stddev term — a unit quirk); using a
consistent channel-mean is cleaner and gives the same dark+flat behaviour.

Usage
-----
    python3 scripts/find_background.py <image.xisf|.fit> [options]

Options:
    --size N            ROI side length in pixels (default 50)
    --exclude X,Y,W,H   Exclude a rectangle (repeatable) — e.g. the nebula core
    --scale N           Downsample by N before searching (default 1 = exact).
                        Coords are reported in FULL-resolution pixels regardless.
                        Use 2-4 to cut memory/time on very large masters.
    --top N             Also print the N best non-overlapping candidates (default 1)
    --png PATH          Write a stretched preview PNG with the ROI box drawn
    --json              Emit machine-readable JSON instead of the text report

Run from the repo root. Companion doc: 04_Processing/Pixinsight/Find-Background.md
Tests: scripts/test_find_background.py
"""

import argparse
import json
import re
import struct
import sys
import time

import numpy as np

SDEV_CAP = 1.0 / 3.0          # filterStandardDeviationCap in FindBackground.js
TILE = 500                    # normalization tile size (JS setupFilterNormalization)
TARGET_MEDIAN = 0.5           # JS targetMedian


# ---------------------------------------------------------------------------
# Image reading (XISF attached blocks; FITS via astropy if available)
# ---------------------------------------------------------------------------
def read_image(path):
    """Return (channels, height, width) float32 array, values normalised to [0,1]."""
    if path.lower().endswith((".xisf",)):
        arr = _read_xisf(path)
    else:
        arr = _read_fits(path)
    arr = arr.astype(np.float32)
    if arr.max() > 2.0:        # integer data (e.g. 0..65535) -> normalise
        arr = arr / float(np.iinfo(np.uint16).max)
    return arr


def _read_xisf(path):
    with open(path, "rb") as fh:
        if fh.read(8) != b"XISF0100":
            raise ValueError("Not an XISF monolithic file")
        header_len = struct.unpack("<I", fh.read(4))[0]
        fh.read(4)  # reserved
        xml = fh.read(header_len).decode("utf-8", "ignore")
        m = re.search(r"<Image\b[^>]*>", xml)
        if not m:
            raise ValueError("No <Image> element in XISF header")
        tag = m.group(0)
        geom = re.search(r'geometry="([^"]*)"', tag).group(1).split(":")
        w, h, ch = int(geom[0]), int(geom[1]), int(geom[2])
        fmt = re.search(r'sampleFormat="([^"]*)"', tag).group(1)
        loc = re.search(r'location="([^"]*)"', tag).group(1).split(":")
        if loc[0] != "attachment":
            raise ValueError("Only attachment-block XISF is supported (not %s)" % loc[0])
        offset, size = int(loc[1]), int(loc[2])
        dtype = {"Float32": "<f4", "Float64": "<f8",
                 "UInt16": "<u2", "UInt8": "<u1", "Int32": "<i4"}.get(fmt)
        if dtype is None:
            raise ValueError("Unsupported sampleFormat: %s" % fmt)
        fh.seek(offset)
        raw = np.frombuffer(fh.read(size), dtype=dtype)
        return raw.reshape(ch, h, w)


def _read_fits(path):
    try:
        from astropy.io import fits
    except ImportError:
        raise SystemExit("FITS input needs astropy (pip install astropy), or pass an .xisf file")
    data = fits.getdata(path)
    data = np.asarray(data)
    if data.ndim == 2:
        data = data[None, :, :]
    return data


# ---------------------------------------------------------------------------
# Core: integral-image window statistics
# ---------------------------------------------------------------------------
def box_mean_std(B, size):
    """Per-window mean and std for every top-left position via summed-area tables.

    Returns (mean, std), each shape (H-size+1, W-size+1); element [y, x] is the
    statistic over B[y:y+size, x:x+size]. O(H*W) regardless of `size`.
    """
    H, W = B.shape
    if size > H or size > W:
        raise ValueError("size (%d) larger than image (%dx%d)" % (size, W, H))
    B = B.astype(np.float64)
    I1 = np.zeros((H + 1, W + 1), dtype=np.float64)
    I2 = np.zeros((H + 1, W + 1), dtype=np.float64)
    np.cumsum(np.cumsum(B, axis=0), axis=1, out=I1[1:, 1:])
    np.cumsum(np.cumsum(B * B, axis=0), axis=1, out=I2[1:, 1:])
    s1 = I1[size:, size:] + I1[:-size, :-size] - I1[size:, :-size] - I1[:-size, size:]
    s2 = I2[size:, size:] + I2[:-size, :-size] - I2[size:, :-size] - I2[:-size, size:]
    n = float(size * size)
    mean = s1 / n
    var = np.maximum(s2 / n - mean * mean, 0.0)
    return mean, np.sqrt(var)


def normalization(B, size):
    """Reproduce setupFilterNormalization: scale the stddev term to this image."""
    H, W = B.shape
    avgs, sdevs = [], []
    for y in range(0, max(1, H - TILE + 1), TILE):
        for x in range(0, max(1, W - TILE + 1), TILE):
            tile = B[y:y + TILE, x:x + TILE]
            avgs.append(float(tile.mean()))
            sdevs.append(float(tile.std()))
    if not avgs:
        avgs = [float(B.mean())]
        sdevs = [float(B.std())]
    avgs = np.asarray(avgs)
    sdevs = np.asarray(sdevs)
    order = np.argsort(avgs)                       # sort by darkness
    keep = max(1, len(order) // 4)                 # darkest quarter of tiles
    idx = order[:keep]
    mid_avg = max(np.median(avgs[idx]), 1e-9)
    mid_sdev = max(np.median(sdevs[idx]), 1e-12)
    # sdevNorm = (targetMedian * cap * (1/mid_avg)) / (1/mid_sdev)
    return (TARGET_MEDIAN * SDEV_CAP * mid_sdev) / mid_avg


def score_map(mean, std, sdev_norm):
    """FindBackground default getScore() (avg + sdev), vectorised. Lower = better."""
    inv_avg = 1.0 / np.maximum(mean, 1e-12)
    inv_sdev = 1.0 / np.maximum(std, 1e-12)
    sdev_term = np.minimum(inv_avg * SDEV_CAP, sdev_norm * inv_sdev)
    return 1.0 / (inv_avg + sdev_term)


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------
def find_background(arr, size=50, exclude=None, scale=1):
    """Return dict with best ROI (full-res coords) + stats. arr is (C,H,W) [0,1]."""
    B_full = arr.mean(axis=0)                       # per-pixel channel-mean brightness
    B = B_full[::scale, ::scale] if scale > 1 else B_full
    ssize = max(1, size // scale)

    sdev_norm = normalization(B, ssize)
    mean, std = box_mean_std(B, ssize)
    scores = score_map(mean, std, sdev_norm)

    # Exclude windows whose top-left falls in any excluded rect (FindBackground rule)
    if exclude:
        for (ex, ey, ew, eh) in exclude:
            ex_s, ey_s = ex // scale, ey // scale
            ew_s, eh_s = max(1, ew // scale), max(1, eh // scale)
            y0, y1 = ey_s, min(scores.shape[0], ey_s + eh_s)
            x0, x1 = ex_s, min(scores.shape[1], ex_s + ew_s)
            if y1 > y0 and x1 > x0:
                scores[y0:y1, x0:x1] = np.inf

    flat = np.argmin(scores)
    by, bx = np.unravel_index(flat, scores.shape)
    X, Y = int(bx * scale), int(by * scale)         # back to full-res top-left

    bright = [float(arr[c, Y:Y + size, X:X + size].mean()) for c in range(arr.shape[0])]
    max_b = max(bright)
    return {
        "x": X, "y": Y, "size": size,
        "score": float(scores[by, bx]),
        "mean": float(mean[by, bx]),
        "std": float(std[by, bx]),
        "channel_brightness": bright,
        "color_correction": [max_b - b for b in bright],
        "_scores": scores, "_scale": scale,
    }


def top_candidates(result, n):
    """Greedy non-overlapping top-N from the score map (full-res coords)."""
    scores = result["_scores"].copy()
    scale = result["_scale"]
    size = result["size"]
    win = max(1, size // scale)
    out = []
    for _ in range(n):
        flat = int(np.argmin(scores))
        sy, sx = np.unravel_index(flat, scores.shape)
        if not np.isfinite(scores[sy, sx]):
            break
        out.append({"x": int(sx * scale), "y": int(sy * scale),
                    "score": float(scores[sy, sx])})
        y0, y1 = max(0, sy - win), min(scores.shape[0], sy + win)
        x0, x1 = max(0, sx - win), min(scores.shape[1], sx + win)
        scores[y0:y1, x0:x1] = np.inf
    return out


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
def write_png(arr, result, path):
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("  (skipped PNG: Pillow not installed)", file=sys.stderr)
        return
    d = max(1, max(arr.shape[1], arr.shape[2]) // 1400)
    s = arr[:, ::d, ::d].astype(np.float64)
    blk = np.percentile(s, 2)
    s = np.clip(s - blk, 0, None)
    s = s / (np.percentile(s, 99.7) + 1e-9)
    s = np.arcsinh(s * 30) / np.arcsinh(30)
    rgb = np.clip(np.transpose(s if s.shape[0] == 3 else np.repeat(s[:1], 3, 0), (1, 2, 0)), 0, 1)
    im = Image.fromarray((rgb * 255).astype(np.uint8))
    draw = ImageDraw.Draw(im)
    x0, y0 = result["x"] // d, result["y"] // d
    x1, y1 = (result["x"] + result["size"]) // d, (result["y"] + result["size"]) // d
    draw.rectangle([x0, y0, x1, y1], outline=(0, 255, 0), width=2)
    im.save(path)
    print("  ROI preview written to %s" % path)


def main():
    ap = argparse.ArgumentParser(description="Fast optimal background ROI finder (numpy port of FindBackground.js)")
    ap.add_argument("image")
    ap.add_argument("--size", type=int, default=50)
    ap.add_argument("--exclude", action="append", default=[], help="X,Y,W,H (repeatable)")
    ap.add_argument("--scale", type=int, default=1)
    ap.add_argument("--top", type=int, default=1)
    ap.add_argument("--png")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    exclude = []
    for e in args.exclude:
        try:
            ex, ey, ew, eh = (int(v) for v in e.split(","))
            exclude.append((ex, ey, ew, eh))
        except ValueError:
            ap.error("--exclude must be X,Y,W,H integers, got %r" % e)

    t0 = time.time()
    arr = read_image(args.image)
    t_read = time.time() - t0
    t0 = time.time()
    res = find_background(arr, size=args.size, exclude=exclude, scale=args.scale)
    t_search = time.time() - t0

    if args.json:
        out = {k: v for k, v in res.items() if not k.startswith("_")}
        if args.top > 1:
            out["candidates"] = top_candidates(res, args.top)
        out["read_s"] = round(t_read, 2)
        out["search_s"] = round(t_search, 2)
        print(json.dumps(out, indent=2))
    else:
        ch = arr.shape[0]
        print("Find Background — %s  (%dx%d, %d ch)" % (args.image, arr.shape[2], arr.shape[1], ch))
        print("  read %.2fs | search %.2fs%s" %
              (t_read, t_search, "" if args.scale == 1 else " (scale %d)" % args.scale))
        print("\n  ROI to enter in PixInsight (SPCC / MAS / BN / DBE):")
        print("    Left (X): %d   Top (Y): %d   Width: %d   Height: %d"
              % (res["x"], res["y"], res["size"], res["size"]))
        print("\n  Background brightness:  mean %.6f  stddev %.6f  score %.5f"
              % (res["mean"], res["std"], res["score"]))
        labels = ["R", "G", "B"] if ch == 3 else ["[%d]" % i for i in range(ch)]
        for lab, b, cc in zip(labels, res["channel_brightness"], res["color_correction"]):
            print("    %-3s brightness %.6f   additive correction %+.6f" % (lab, b, cc))
        if args.top > 1:
            print("\n  Top %d non-overlapping candidates:" % args.top)
            for i, c in enumerate(top_candidates(res, args.top), 1):
                print("    %2d. X %5d  Y %5d   score %.5f" % (i, c["x"], c["y"], c["score"]))

    if args.png:
        write_png(arr, res, args.png)


if __name__ == "__main__":
    main()
