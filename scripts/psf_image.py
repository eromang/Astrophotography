#!/usr/bin/env python3
"""psf_image.py — offline equivalent of PixInsight's PSFImage (HVB) script.

Detects stars in an astro image, fits an elliptical Moffat/Gaussian PSF to the
best ones, and reports the median FWHM — i.e. the number you feed into
BlurXTerminator's PSF Diameter. Optionally renders a synthetic PSF image (FITS)
for use as an external PSF in deconvolution, and a per-star CSV.

Pure numpy + scipy. Reads FITS (.fit/.fits) and uncompressed monolithic XISF
(.xisf, Float32/UInt16 Gray or multi-channel). Run from the repo root:

    python3 scripts/psf_image.py <image> [options]

Reference: PixInsight PSFImage by Hartmut V. Bornemann. See the vault doc
04_Processing/Pixinsight/PSFImage-Offline.md.
"""
from __future__ import annotations
import argparse
import re
import struct
import sys
import numpy as np
from scipy import ndimage, optimize


# --------------------------------------------------------------------------- #
# Image readers (no astropy)                                                  #
# --------------------------------------------------------------------------- #
def read_fits(path: str) -> np.ndarray:
    """Minimal FITS reader → 2D float32 array (first image HDU)."""
    with open(path, "rb") as fh:
        cards = {}
        while True:
            block = fh.read(2880)
            if len(block) < 2880:
                raise ValueError("truncated FITS header")
            end = False
            for i in range(0, 2880, 80):
                card = block[i:i + 80].decode("latin-1")
                key = card[:8].strip()
                if key == "END":
                    end = True
                    break
                if card[8:10] == "= ":
                    val = card[10:].split("/")[0].strip().strip("'").strip()
                    cards[key] = val
            if end:
                break
        naxis1, naxis2 = int(cards["NAXIS1"]), int(cards["NAXIS2"])
        bitpix = int(cards["BITPIX"])
        bzero = float(cards.get("BZERO", 0.0))
        bscale = float(cards.get("BSCALE", 1.0))
        dt = {8: ">u1", 16: ">i2", 32: ">i4", -32: ">f4", -64: ">f8"}[bitpix]
        n = naxis1 * naxis2
        raw = np.frombuffer(fh.read(n * abs(bitpix) // 8), dtype=dt, count=n)
        data = raw.astype(np.float64) * bscale + bzero
        return data.reshape(naxis2, naxis1).astype(np.float32)


def read_xisf(path: str) -> np.ndarray:
    """Minimal reader for uncompressed monolithic XISF → 2D float32 array.

    Uses the first <Image> element; if multi-channel, averages to luminance.
    Raises on compressed blocks (not supported by this lightweight reader).
    """
    with open(path, "rb") as fh:
        sig = fh.read(8)
        if sig != b"XISF0100":
            raise ValueError("not a monolithic XISF file")
        hdr_len = struct.unpack("<I", fh.read(4))[0]
        fh.read(4)  # reserved
        xml = fh.read(hdr_len).decode("utf-8", "ignore")
        m = re.search(r"<Image\b[^>]*>", xml)
        if not m:
            raise ValueError("no <Image> element in XISF header")
        img = m.group(0)

        def attr(name):
            a = re.search(name + r'="([^"]*)"', img)
            return a.group(1) if a else None

        geom = attr("geometry").split(":")        # w:h:channels
        w, h, ch = int(geom[0]), int(geom[1]), int(geom[2])
        fmt = attr("sampleFormat")
        loc = attr("location")                    # attachment:offset:size
        if attr("compression"):
            raise ValueError("compressed XISF not supported by this reader")
        if not loc.startswith("attachment:"):
            raise ValueError("only attachment-located XISF data supported")
        _, off, size = loc.split(":")
        off, size = int(off), int(size)
        dt = {"Float32": "<f4", "Float64": "<f8",
              "UInt8": "<u1", "UInt16": "<u2", "UInt32": "<u4"}[fmt]
        fh.seek(off)
        raw = np.frombuffer(fh.read(size), dtype=dt)
        arr = raw.astype(np.float32).reshape(ch, h, w)
        return arr.mean(axis=0) if ch > 1 else arr[0]


def read_image(path: str) -> np.ndarray:
    p = path.lower()
    if p.endswith(".xisf"):
        return read_xisf(path)
    if p.endswith((".fit", ".fits", ".fts")):
        return read_fits(path)
    raise ValueError(f"unsupported extension: {path}")


# --------------------------------------------------------------------------- #
# CFA (Bayer) green-channel extraction                                        #
# --------------------------------------------------------------------------- #
def extract_green(img: np.ndarray, pattern: str = "RGGB") -> np.ndarray:
    """Full-resolution green channel from a raw Bayer frame.

    Keeps native pixel scale: green pixels are kept; the R/B positions are filled
    with the 4-neighbour green average (which are all green for a quincunx). This
    removes the R/B mosaic modulation so star profiles fit cleanly, without the
    resolution loss of 2x2 super-pixel binning. Default RGGB (ASI2600MC).
    """
    # green-pixel positions per pattern (row%2, col%2)
    greens = {"RGGB": [(0, 1), (1, 0)], "BGGR": [(0, 1), (1, 0)],
              "GRBG": [(0, 0), (1, 1)], "GBRG": [(0, 0), (1, 1)]}
    if pattern not in greens:
        raise ValueError(f"unknown CFA pattern: {pattern}")
    g = img.astype(np.float64)
    is_green = np.zeros(img.shape, bool)
    for r, c in greens[pattern]:
        is_green[r::2, c::2] = True
    k = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]], float) / 4.0
    interp = ndimage.convolve(g, k, mode="nearest")   # 4-neighbour avg
    return np.where(is_green, g, interp).astype(np.float32)


# --------------------------------------------------------------------------- #
# Star detection                                                              #
# --------------------------------------------------------------------------- #
def estimate_background(img: np.ndarray):
    """Sigma-clipped median + robust sigma (via MAD)."""
    v = img.ravel()
    med = np.median(v)
    for _ in range(3):
        mad = np.median(np.abs(v - med)) * 1.4826
        keep = np.abs(v - med) < 3 * mad
        if keep.sum() < v.size // 2:
            break
        v = v[keep]
        med = np.median(v)
    mad = np.median(np.abs(v - med)) * 1.4826
    return float(med), float(max(mad, 1e-12))


def detect_stars(img, bg, sigma, k=6.0, min_pix=4, max_pix=400):
    """Threshold + connected components → candidate star list (peak-sorted)."""
    thresh = bg + k * sigma
    mask = img > thresh
    lbl, n = ndimage.label(mask)
    if n == 0:
        return []
    slices = ndimage.find_objects(lbl)
    h, w = img.shape
    sat = float(img.max())
    stars = []
    for i, sl in enumerate(slices, start=1):
        if sl is None:
            continue
        sub = img[sl]
        m = lbl[sl] == i
        npix = int(m.sum())
        if npix < min_pix or npix > max_pix:
            continue
        ys, xs = np.nonzero(m)
        peak = float(sub[m].max())
        # weighted centroid
        wsum = sub[m].sum()
        cy = float((ys * sub[m]).sum() / wsum) + sl[0].start
        cx = float((xs * sub[m]).sum() / wsum) + sl[1].start
        if cx < 12 or cy < 12 or cx > w - 12 or cy > h - 12:
            continue
        if peak >= 0.99 * sat:          # saturated → unreliable PSF
            continue
        stars.append((cx, cy, peak, npix))
    stars.sort(key=lambda s: s[2], reverse=True)
    return stars


# --------------------------------------------------------------------------- #
# PSF fitting                                                                 #
# --------------------------------------------------------------------------- #
def _moffat(coords, B, A, x0, y0, sx, sy, theta, beta):
    x, y = coords
    ct, st = np.cos(theta), np.sin(theta)
    xr = (x - x0) * ct + (y - y0) * st
    yr = -(x - x0) * st + (y - y0) * ct
    return B + A * (1 + (xr / sx) ** 2 + (yr / sy) ** 2) ** (-beta)


def _gauss(coords, B, A, x0, y0, sx, sy, theta):
    x, y = coords
    ct, st = np.cos(theta), np.sin(theta)
    xr = (x - x0) * ct + (y - y0) * st
    yr = -(x - x0) * st + (y - y0) * ct
    return B + A * np.exp(-0.5 * ((xr / sx) ** 2 + (yr / sy) ** 2))


def fit_star(img, cx, cy, box, func, fixed_beta):
    """Fit one star window. Returns dict of params + FWHM, or None on failure."""
    x0i, y0i = int(round(cx)), int(round(cy))
    sub = img[y0i - box:y0i + box + 1, x0i - box:x0i + box + 1].astype(np.float64)
    if sub.shape != (2 * box + 1, 2 * box + 1):
        return None
    yy, xx = np.mgrid[0:sub.shape[0], 0:sub.shape[1]]
    coords = (xx.ravel(), yy.ravel())
    z = sub.ravel()
    B0 = np.median(sub)
    A0 = sub.max() - B0
    if A0 <= 0:
        return None
    cxb, cyb = box + (cx - x0i), box + (cy - y0i)
    try:
        if func == "gaussian":
            p0 = [B0, A0, cxb, cyb, 2.0, 2.0, 0.0]
            lb = [-np.inf, 0, cxb - 3, cyb - 3, 0.3, 0.3, -np.pi]
            ub = [np.inf, np.inf, cxb + 3, cyb + 3, box, box, np.pi]
            popt, _ = optimize.curve_fit(_gauss, coords, z, p0=p0,
                                         bounds=(lb, ub), maxfev=4000)
            B, A, x0, y0, sx, sy, th = popt
            kx = ky = 2.0 * np.sqrt(2.0 * np.log(2.0))
            fwhmx, fwhmy, beta = sx * kx, sy * ky, np.nan
            model = _gauss(coords, *popt)
        else:
            if fixed_beta is not None:
                def mf(c, B, A, x0, y0, sx, sy, theta):
                    return _moffat(c, B, A, x0, y0, sx, sy, theta, fixed_beta)
                p0 = [B0, A0, cxb, cyb, 2.0, 2.0, 0.0]
                lb = [-np.inf, 0, cxb - 3, cyb - 3, 0.3, 0.3, -np.pi]
                ub = [np.inf, np.inf, cxb + 3, cyb + 3, box, box, np.pi]
                popt, _ = optimize.curve_fit(mf, coords, z, p0=p0,
                                             bounds=(lb, ub), maxfev=4000)
                B, A, x0, y0, sx, sy, th = popt
                beta = fixed_beta
                model = mf(coords, *popt)
            else:
                p0 = [B0, A0, cxb, cyb, 2.0, 2.0, 0.0, 3.0]
                lb = [-np.inf, 0, cxb - 3, cyb - 3, 0.3, 0.3, -np.pi, 1.0]
                ub = [np.inf, np.inf, cxb + 3, cyb + 3, box, box, np.pi, 10.0]
                popt, _ = optimize.curve_fit(_moffat, coords, z, p0=p0,
                                             bounds=(lb, ub), maxfev=6000)
                B, A, x0, y0, sx, sy, th, beta = popt
                model = _moffat(coords, *popt)
            kf = 2.0 * np.sqrt(2.0 ** (1.0 / beta) - 1.0)
            fwhmx, fwhmy = sx * kf, sy * kf
    except (RuntimeError, ValueError):
        return None
    resid = z - model
    mad = float(np.median(np.abs(resid - np.median(resid))))
    rmad = mad / max(A, 1e-9)               # normalized residual
    sma, smi = max(fwhmx, fwhmy), min(fwhmx, fwhmy)
    ecc = float(np.sqrt(1 - (smi / sma) ** 2)) if sma > 0 else 0.0
    return dict(cx=x0 + x0i - box, cy=y0 + y0i - box, fwhmx=fwhmx, fwhmy=fwhmy,
                fwhm=0.5 * (fwhmx + fwhmy), beta=beta, ecc=ecc, rmad=rmad)


# --------------------------------------------------------------------------- #
# Synthetic PSF render                                                        #
# --------------------------------------------------------------------------- #
def render_psf(fwhm, beta, size=None):
    """Render a normalized circular synthetic PSF (Moffat, or Gaussian if beta
    is NaN) with the given mean FWHM. Returns a float32 [0,1] image."""
    if size is None:
        size = int(2 * np.ceil(3 * fwhm) + 1)
    c = size // 2
    yy, xx = np.mgrid[0:size, 0:size]
    if np.isnan(beta):
        s = fwhm / (2 * np.sqrt(2 * np.log(2)))
        img = np.exp(-0.5 * (((xx - c) ** 2 + (yy - c) ** 2) / s ** 2))
    else:
        s = fwhm / (2 * np.sqrt(2 ** (1 / beta) - 1))
        img = (1 + (((xx - c) ** 2 + (yy - c) ** 2) / s ** 2)) ** (-beta)
    return (img / img.max()).astype(np.float32)


def write_fits(path, img, keywords=None):
    """Write a float32 FITS (BITPIX -32)."""
    h, w = img.shape
    cards = [("SIMPLE", "T"), ("BITPIX", "-32"), ("NAXIS", "2"),
             ("NAXIS1", str(w)), ("NAXIS2", str(h))]
    for k, v in (keywords or {}).items():
        cards.append((k, str(v)))
    hdr = b""
    for k, v in cards:
        hdr += f"{k:<8}= {v:>20}".ljust(80).encode("latin-1")
    hdr += b"END".ljust(80)
    hdr += b" " * ((2880 - len(hdr) % 2880) % 2880)
    data = img.astype(">f4").tobytes()
    data += b"\x00" * ((2880 - len(data) % 2880) % 2880)
    with open(path, "wb") as fh:
        fh.write(hdr + data)


# --------------------------------------------------------------------------- #
# Main                                                                        #
# --------------------------------------------------------------------------- #
def measure(path, function="moffat", max_stars=200, use_stars=50,
            box=10, k=6.0, fixed_beta=None, cfa=None, cfa_pattern="RGGB",
            verbose=True):
    img = read_image(path)
    if cfa == "green":
        img = extract_green(img, cfa_pattern)
    bg, sigma = estimate_background(img)
    cands = detect_stars(img, bg, sigma, k=k)[:max_stars]
    fits = []
    for cx, cy, peak, npix in cands:
        f = fit_star(img, cx, cy, box, function, fixed_beta)
        if f and 0.8 < f["fwhm"] < box and f["rmad"] < 0.1 and f["ecc"] < 0.85:
            fits.append(f)
    if not fits:
        raise RuntimeError("no usable star fits — try lowering -k or another image")
    # keep the best `use_stars` by lowest normalized residual
    fits.sort(key=lambda f: f["rmad"])
    fits = fits[:use_stars]
    fx = np.array([f["fwhmx"] for f in fits])
    fy = np.array([f["fwhmy"] for f in fits])
    fw = np.array([f["fwhm"] for f in fits])
    betas = [f["beta"] for f in fits if not np.isnan(f["beta"])]
    beta = float(np.median(betas)) if betas else float("nan")
    res = dict(n=len(fits), fwhm=float(np.median(fw)),
               fwhmx=float(np.median(fx)), fwhmy=float(np.median(fy)),
               fwhm_std=float(np.std(fw)), beta=float(beta),
               ecc=float(np.median([f["ecc"] for f in fits])),
               bg=bg, sigma=sigma, fits=fits)
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description="Offline PixInsight PSFImage equivalent.")
    ap.add_argument("image", help="FITS (.fit/.fits) or uncompressed XISF")
    ap.add_argument("--function", choices=["moffat", "gaussian"], default="moffat")
    ap.add_argument("--beta", type=float, default=None,
                    help="fix Moffat beta (e.g. 4); default = free")
    ap.add_argument("--max-stars", type=int, default=200)
    ap.add_argument("--use-stars", type=int, default=50)
    ap.add_argument("--box", type=int, default=10, help="half-window (px) per star")
    ap.add_argument("-k", type=float, default=6.0, help="detection threshold (sigma)")
    ap.add_argument("--cfa", choices=["none", "green"], default="none",
                    help="green: extract full-res green channel from a raw Bayer frame")
    ap.add_argument("--cfa-pattern", choices=["RGGB", "BGGR", "GRBG", "GBRG"],
                    default="RGGB", help="Bayer pattern for --cfa (default RGGB)")
    ap.add_argument("--psf-out", help="write synthetic PSF image to this FITS path")
    ap.add_argument("--csv", help="write per-star fits to this CSV path")
    args = ap.parse_args(argv)

    r = measure(args.image, function=args.function, max_stars=args.max_stars,
                use_stars=args.use_stars, box=args.box, k=args.k,
                fixed_beta=args.beta,
                cfa=(None if args.cfa == "none" else args.cfa),
                cfa_pattern=args.cfa_pattern)

    print(f"Image      : {args.image}")
    print(f"Function   : {args.function}" +
          (f" (beta fixed {args.beta})" if args.beta else "") +
          (f"  [CFA green {args.cfa_pattern}]" if args.cfa == "green" else ""))
    print(f"Stars used : {r['n']}  (bg {r['bg']:.5g}, sigma {r['sigma']:.3g})")
    print(f"FWHM x/y   : {r['fwhmx']:.3f} / {r['fwhmy']:.3f} px   (ecc {r['ecc']:.3f})")
    if not np.isnan(r["beta"]):
        print(f"Moffat beta: {r['beta']:.2f}")
    print(f"Median FWHM: {r['fwhm']:.3f} px   (sigma {r['fwhm_std']:.3f})")
    print(f"==> BXT PSF Diameter: {round(r['fwhm'], 2)}")

    if args.csv:
        with open(args.csv, "w") as fh:
            fh.write("cx,cy,fwhmx,fwhmy,fwhm,beta,ecc,rmad\n")
            for f in r["fits"]:
                fh.write(f"{f['cx']:.2f},{f['cy']:.2f},{f['fwhmx']:.3f},"
                         f"{f['fwhmy']:.3f},{f['fwhm']:.3f},{f['beta']:.3f},"
                         f"{f['ecc']:.3f},{f['rmad']:.4f}\n")
        print(f"Per-star CSV -> {args.csv}")

    if args.psf_out:
        psf = render_psf(r["fwhm"], r["beta"])
        write_fits(args.psf_out, psf,
                   {"FWHMX": round(r["fwhmx"], 3), "FWHMY": round(r["fwhmy"], 3),
                    "BETA": round(r["beta"], 3) if not np.isnan(r["beta"]) else 0})
        print(f"Synthetic PSF ({psf.shape[0]}x{psf.shape[1]}) -> {args.psf_out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
