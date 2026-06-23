#!/usr/bin/env python3
"""
nxt_advisor.py — suggest NoiseXTerminator separation-mode settings from the noise structure.

NXT's *Denoise amount* (~0.85) is taste — "how smooth do you want it." What IS
measurable, and what this script reports, is the **structure** of the noise, which
drives the separation-mode parameters:

- **Colour vs intensity** — NXT (and RC-Astro) advise reducing colour noise more
  than intensity. This measures the actual ratio (σ_colour / σ_intensity) in a
  signal-free background patch and maps it to HF/LF *colour* amounts.
- **Noise correlation scale** — sets the **HF/LF Scale** (what counts as "fine"
  vs "large" noise). White noise ≈ 1 px; drizzle/debayer noise is correlated and
  larger, so the scale should follow the data, not a guess.
- **Noise level** — whether to use 1 or 2 iterations.

It grabs a dark, signal-free ROI via find_background.py, removes the large-scale
component (so it measures noise, not nebula), and reports measured values + a
suggested NXT setup. The base Denoise amount stays YOUR call (~0.85).

Usage
-----
    python3 scripts/nxt_advisor.py <image.xisf> [--size 200] [--json]

Run from repo root. Doc: 04_Processing/Pixinsight/NXT-Advisor.md
Tests: scripts/test_nxt_advisor.py
"""

import argparse
import json
import sys

import numpy as np
from scipy.ndimage import gaussian_filter

import find_background as fbg


def _autocorr_scale(L):
    """Lag (px) at which the noise autocorrelation drops to 0.5 — the correlation length."""
    L = L - L.mean()
    var = float((L * L).mean()) + 1e-20
    acf = []
    for lag in range(1, 8):
        # average the lag-shifted product over both axes
        ax = float((L[:, :-lag] * L[:, lag:]).mean())
        ay = float((L[:-lag, :] * L[lag:, :]).mean())
        acf.append(0.5 * (ax + ay) / var)
    # first lag where acf < 0.5 (interpolate); >=1
    for i, v in enumerate(acf, start=1):
        if v < 0.5:
            prev = acf[i - 2] if i >= 2 else 1.0
            frac = (prev - 0.5) / (prev - v) if prev > v else 0.0
            return max(1.0, (i - 1) + frac)
    return 7.0


def measure_noise(roi):
    """roi: (C,H,W) background patch in [0,1]. Returns measured noise structure."""
    ch = roi.shape[0]
    # per-channel noise = channel minus its large-scale (>~8px) component
    resid = np.stack([roi[c] - gaussian_filter(roi[c], 8.0) for c in range(ch)])
    if ch >= 3:
        L = resid.mean(0)                          # luminance noise
        chroma = resid - L[None]                   # chrominance noise per channel
        sig_int = float(L.std())
        sig_col = float(np.sqrt(np.mean([chroma[c].std() ** 2 for c in range(ch)])))
    else:
        L = resid[0]
        sig_int = float(L.std())
        sig_col = 0.0
    hf = L - gaussian_filter(L, 1.0)
    lf = gaussian_filter(L, 1.0) - gaussian_filter(L, 4.0)
    return {
        "sigma_intensity": sig_int,
        "sigma_color": sig_col,
        "color_intensity_ratio": (sig_col / sig_int) if sig_int > 0 else 0.0,
        "sigma_hf": float(hf.std()),
        "sigma_lf": float(lf.std()),
        "corr_scale_px": float(_autocorr_scale(L)),
    }


def suggest(m, mono=False):
    ratio = m["color_intensity_ratio"]
    noisy = m["sigma_intensity"] > 5e-4
    s = {
        "denoise_amount": 0.85,                    # taste — not measured
        "iterations": 2 if noisy else 1,
        "hf_intensity": 0.85 if noisy else 0.80,
        "lf_intensity": 0.55,                      # gentle: preserve dust/filaments
        "hf_lf_scale_px": int(round(np.clip(m["corr_scale_px"] * 1.5, 2, 8))),
    }
    if not mono:
        s["hf_color"] = round(float(np.clip(0.90 + 0.10 * (ratio - 1.0), 0.90, 1.0)), 2)
        s["lf_color"] = 1.00
    return s


def analyze(path, size=200, k=6.0):
    arr = fbg.read_image(path)
    bg = fbg.find_background(arr, size=size)        # dark, signal-free ROI
    x, y, s=  bg["x"], bg["y"], bg["size"]
    roi = arr[:, y:y + s, x:x + s]
    m = measure_noise(roi)
    mono = arr.shape[0] < 3
    return {"path": path, "roi": [x, y, s], "channels": int(arr.shape[0]),
            "measured": m, "suggested": suggest(m, mono), "mono": mono}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Suggest NoiseXTerminator separation settings from noise structure")
    ap.add_argument("image")
    ap.add_argument("--size", type=int, default=200, help="background ROI side for noise measurement (default 200)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    r = analyze(args.image, size=args.size)
    m, s = r["measured"], r["suggested"]

    if args.json:
        print(json.dumps(r, indent=2, default=float))
        return

    print("NXT advisor — %s  (%d ch)" % (args.image, r["channels"]))
    print("  noise patch ROI: %s" % r["roi"])
    print("  measured: sigma_int %.2e  sigma_col %.2e  colour/intensity %.2f  corr-scale %.1f px"
          % (m["sigma_intensity"], m["sigma_color"], m["color_intensity_ratio"], m["corr_scale_px"]))
    print("\n  Suggested NoiseXTerminator (separation modes ON):")
    print("    Denoise amount      : %.2f   (TASTE — your call; 0.85 typical)" % s["denoise_amount"])
    print("    Iterations          : %d" % s["iterations"])
    print("    HF intensity        : %.2f" % s["hf_intensity"])
    if not r["mono"]:
        print("    HF colour           : %.2f   (colour/intensity ratio %.2f -> %s)"
              % (s["hf_color"], m["color_intensity_ratio"],
                 "push colour hard" if s["hf_color"] >= 0.95 else "moderate"))
    print("    LF intensity        : %.2f   (gentle — preserves dust/filaments)" % s["lf_intensity"])
    if not r["mono"]:
        print("    LF colour           : %.2f" % s["lf_color"])
    print("    HF/LF Scale         : %d px  (from the noise correlation length)" % s["hf_lf_scale_px"])
    print("\n  Tune the Denoise amount on the real-time preview; the rest is from the measured noise.")


if __name__ == "__main__":
    main()
