#!/usr/bin/env python3
"""moving_object.py — find comets/asteroids in a sequence of light frames.

A real solar-system mover drifts along a roughly linear track across MANY frames
against the fixed stars; a satellite is a streak in ONE frame only. This detects
the former and excludes the latter.

Runs on **raw .fit lights** — each carries its own ASIAIR plate solution
(CD matrix + CRVAL/CRPIX + DATE-OBS), so detections are mapped to RA/Dec per
frame and movers are found in sky coordinates (pointing-independent). Detection
is done on the de-mosaiced green channel.

Two passes:
  * per-frame linking   — movers bright enough to clear the threshold per frame
  * shift-and-stack     — synthetic tracking that recovers faint sub-threshold
                          movers (the CEM26 is equatorial → no field rotation
                          between frames, so registration is a pure translation)

Outputs (to --out): a text report, a crop-stack montage + annotated PNG per
candidate, and a DS9/PixInsight region file.

    python3 scripts/moving_object.py <lights-folder> [options]

Reuses scripts/psf_image.py (I/O, green extraction, detection). numpy + scipy;
matplotlib only for the PNGs. No astropy. SIP distortion is ignored (sub-arcsec,
irrelevant at mover scale). Magnitudes are instrumental/relative.
"""
from __future__ import annotations
import argparse
import datetime as _dt
import os
import sys

import numpy as np
from scipy import ndimage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import psf_image as P
import frame_info as FI

DEG = np.pi / 180.0


# --------------------------------------------------------------------------- #
# WCS — TAN gnomonic with a linear CD matrix (SIP ignored)                     #
# --------------------------------------------------------------------------- #
def _cd(kw):
    return np.array([[kw["CD1_1"], kw["CD1_2"]], [kw["CD2_1"], kw["CD2_2"]]], float)


def has_wcs(kw):
    return all(isinstance(kw.get(k), (int, float)) for k in
               ("CD1_1", "CD1_2", "CD2_1", "CD2_2", "CRVAL1", "CRVAL2", "CRPIX1", "CRPIX2"))


def pix2world(x, y, kw):
    """0-based array pixel (x,y) -> (ra, dec) in degrees."""
    cd = _cd(kw)
    dx = (x + 1) - kw["CRPIX1"]          # FITS pixels are 1-based
    dy = (y + 1) - kw["CRPIX2"]
    xi = (cd[0, 0] * dx + cd[0, 1] * dy) * DEG     # tangent-plane coords (rad)
    eta = (cd[1, 0] * dx + cd[1, 1] * dy) * DEG
    ra0, dec0 = kw["CRVAL1"] * DEG, kw["CRVAL2"] * DEG
    rho = np.hypot(xi, eta)
    rho_safe = np.where(rho == 0, 1.0, rho)
    c = np.arctan(rho)
    sinc, cosc = np.sin(c), np.cos(c)
    dec = np.arcsin(cosc * np.sin(dec0) + eta * sinc * np.cos(dec0) / rho_safe)
    ra = ra0 + np.arctan2(xi * sinc,
                          rho_safe * np.cos(dec0) * cosc - eta * np.sin(dec0) * sinc)
    ra = np.where(rho == 0, ra0, ra)
    dec = np.where(rho == 0, dec0, dec)
    return np.degrees(ra) % 360.0, np.degrees(dec)


def world2pix(ra, dec, kw):
    """(ra, dec) in degrees -> 0-based array pixel (x, y)."""
    ra0, dec0 = kw["CRVAL1"] * DEG, kw["CRVAL2"] * DEG
    a, d = np.asarray(ra) * DEG, np.asarray(dec) * DEG
    da = a - ra0
    F = np.sin(dec0) * np.sin(d) + np.cos(dec0) * np.cos(d) * np.cos(da)
    xi = np.cos(d) * np.sin(da) / F
    eta = (np.cos(dec0) * np.sin(d) - np.sin(dec0) * np.cos(d) * np.cos(da)) / F
    cdinv = np.linalg.inv(_cd(kw))
    vx = np.degrees(xi)
    vy = np.degrees(eta)
    dx = cdinv[0, 0] * vx + cdinv[0, 1] * vy
    dy = cdinv[1, 0] * vx + cdinv[1, 1] * vy
    return dx + kw["CRPIX1"] - 1, dy + kw["CRPIX2"] - 1


def pixel_scale(kw):
    """arcsec/px from the CD matrix."""
    cd = _cd(kw)
    return float(np.hypot(cd[0, 0], cd[1, 0]) * 3600.0)


def angsep(ra1, dec1, ra2, dec2):
    """Angular separation (deg) — haversine."""
    r1, d1, r2, d2 = (np.asarray(v) * DEG for v in (ra1, dec1, ra2, dec2))
    h = np.sin((d2 - d1) / 2) ** 2 + np.cos(d1) * np.cos(d2) * np.sin((r2 - r1) / 2) ** 2
    return np.degrees(2 * np.arcsin(np.minimum(1, np.sqrt(h))))


# --------------------------------------------------------------------------- #
# Frame loading + per-frame detection                                         #
# --------------------------------------------------------------------------- #
def _parse_time(s):
    try:
        return _dt.datetime.fromisoformat(str(s).strip().strip("'").strip())
    except Exception:
        return None


def load_frames(folder, cfa_pattern="RGGB", k=6.0, max_per_frame=600,
                recursive=False, log=print):
    """Return list of frame dicts with green data, kw, time, and detections.

    Per-frame detections are capped to the brightest `max_per_frame` — raw
    (uncalibrated) subs throw thousands of hot-pixel/noise sources that would
    swamp the linker; real stars + movers dominate the bright end.
    """
    paths = [p for p in FI.iter_files(folder, recursive)
             if p.lower().endswith((".fit", ".fits", ".fts"))]
    frames = []
    for p in sorted(paths):
        kw = FI.read_meta(p)["kw"]
        if not has_wcs(kw):
            log(f"  skip (no WCS): {os.path.basename(p)}")
            continue
        t = _parse_time(kw.get("DATE-OBS"))
        if t is None:
            log(f"  skip (no DATE-OBS): {os.path.basename(p)}")
            continue
        raw = P.read_image(p)
        green = P.extract_green(raw, cfa_pattern)
        bg, sigma = P.estimate_background(green)
        dets = P.detect_stars(green, bg, sigma, k=k)[:max_per_frame]
        frames.append(dict(path=p, name=os.path.basename(p), kw=kw, t=t,
                           green=green, bg=bg, sigma=sigma, dets=dets,
                           shape=green.shape))
    frames.sort(key=lambda f: f["t"])
    if frames:
        t0 = frames[0]["t"]
        for f in frames:
            f["tmin"] = (f["t"] - t0).total_seconds() / 60.0   # minutes from start
    return frames


def detections_sky(frames):
    """Flatten all detections into sky-tagged records."""
    recs = []
    for fi, f in enumerate(frames):
        for (cx, cy, peak, npix) in f["dets"]:
            ra, dec = pix2world(cx, cy, f["kw"])
            recs.append(dict(fi=fi, name=f["name"], tmin=f["tmin"],
                             x=float(cx), y=float(cy), ra=float(ra), dec=float(dec),
                             peak=float(peak), npix=int(npix)))
    return recs


# --------------------------------------------------------------------------- #
# Static-source (star) rejection                                              #
# --------------------------------------------------------------------------- #
def _cluster(recs, posfn, distfn, tol, n_frames, min_frac):
    """Greedy cluster recs by position. Return (member-index set of clusters seen
    in >= min_frac of frames, total cluster count)."""
    order = sorted(range(len(recs)), key=lambda i: -recs[i]["peak"])
    clusters = []
    for i in order:
        p = posfn(recs[i])
        best = None
        for cl in clusters:
            if distfn(p, cl["p"]) <= tol:
                best = cl
                break
        if best is None:
            clusters.append(dict(p=p, frames={recs[i]["fi"]}, members=[i]))
        else:
            best["frames"].add(recs[i]["fi"])
            best["members"].append(i)
    need = max(2, int(round(min_frac * n_frames)))
    big = set()
    for cl in clusters:
        if len(cl["frames"]) >= need:
            big.update(cl["members"])
    return big, len(clusters)


def reject_fixed(recs, n_frames, scale, sky_tol_px=2.5, pix_tol_px=1.5, min_frac=0.5):
    """Flag detections fixed in SKY (stars) and fixed in PIXEL/sensor (hot pixels).

    Under dithering a hot pixel drifts in sky coords (so it would fake a mover) but
    stays put on the sensor — so we reject both fixed-sky and fixed-pixel sources.
    Sets rec['static'] (star) and rec['hot'] (hot pixel) in place.
    """
    sky_tol = sky_tol_px * scale / 3600.0
    stars, _ = _cluster(recs, lambda r: (r["ra"], r["dec"]),
                        lambda a, b: angsep(a[0], a[1], b[0], b[1]),
                        sky_tol, n_frames, min_frac)
    hot, _ = _cluster(recs, lambda r: (r["x"], r["y"]),
                      lambda a, b: float(np.hypot(a[0] - b[0], a[1] - b[1])),
                      pix_tol_px, n_frames, min_frac)
    for i, r in enumerate(recs):
        r["static"] = i in stars
        r["hot"] = i in hot
    return len(stars), len(hot)


# --------------------------------------------------------------------------- #
# Bright-mover linking (per-frame-detectable)                                 #
# --------------------------------------------------------------------------- #
def link_tracks(recs, frames, scale, min_frames=4, tol_px=3.0):
    """Link transient detections into linear sky tracks (constant velocity)."""
    tol_deg = tol_px * scale / 3600.0
    trans = [r for r in recs if not r["static"] and not r.get("hot")]
    trans.sort(key=lambda r: -r["peak"])
    trans = trans[:400]                     # bound the O(D^2) seed search
    by_frame = {}
    for r in trans:
        by_frame.setdefault(r["fi"], []).append(r)
    seeds = sorted(trans, key=lambda r: r["fi"])
    used = set()
    tracks = []
    for a in seeds:
        if id(a) in used:
            continue
        for b in trans:
            if b["fi"] <= a["fi"] or abs(b["tmin"] - a["tmin"]) < 1e-6:
                continue
            dt = b["tmin"] - a["tmin"]
            vra = (b["ra"] - a["ra"]) / dt          # deg/min
            vdec = (b["dec"] - a["dec"]) / dt
            # predict in every frame; gather supporting detections
            members = []
            for fi, f in enumerate(frames):
                pra = a["ra"] + vra * (f["tmin"] - a["tmin"])
                pdec = a["dec"] + vdec * (f["tmin"] - a["tmin"])
                cand = by_frame.get(fi, [])
                if not cand:
                    continue
                best, bestd = None, tol_deg
                for c in cand:
                    d = angsep(c["ra"], c["dec"], pra, pdec)
                    if d < bestd:
                        best, bestd = c, d
                if best is not None:
                    members.append(best)
            # dedup members by frame (keep closest already ensured)
            seen_fi = {}
            for m in members:
                seen_fi[m["fi"]] = m
            members = list(seen_fi.values())
            if len(members) >= min_frames:
                tr = _fit_track(members)
                if tr and tr["rms_px"] * 1 <= max(1.5, 2.0):   # px residual gate
                    tracks.append(tr)
                    for m in members:
                        used.add(id(m))
                    break
    # dedup overlapping tracks: keep the longest / lowest-rms, drop those sharing members
    tracks.sort(key=lambda t: (-len(t["members"]), t["rms_px"]))
    kept, claimed = [], set()
    for t in tracks:
        ids = {id(m) for m in t["members"]}
        if len(ids & claimed) >= 2:
            continue
        kept.append(t)
        claimed |= ids
    return kept


def _fit_track(members):
    """Least-squares linear fit of ra(t), dec(t); return track summary."""
    m = sorted(members, key=lambda r: r["tmin"])
    t = np.array([r["tmin"] for r in m])
    ra = np.unwrap(np.array([r["ra"] for r in m]) * DEG) / DEG
    dec = np.array([r["dec"] for r in m])
    A = np.vstack([t, np.ones_like(t)]).T
    (vra, ra0), *_ = np.linalg.lstsq(A, ra, rcond=None)
    (vdec, dec0), *_ = np.linalg.lstsq(A, dec, rcond=None)
    res_ra = ra - (vra * t + ra0)
    res_dec = dec - (vdec * t + dec0)
    cosd = np.cos(np.median(dec) * DEG)
    rms_deg = float(np.sqrt(np.mean((res_ra * cosd) ** 2 + res_dec ** 2)))
    span = t[-1] - t[0]
    if span <= 0:
        return None
    rate = float(np.hypot(vra * cosd, vdec) * 3600.0)         # arcsec/min
    pa = float((np.degrees(np.arctan2(vra * cosd, vdec))) % 360.0)
    return dict(members=m, vra=vra, vdec=vdec, rate=rate, pa=pa,
                span_min=float(span), n=len(m),
                rms_px=rms_deg * 3600.0 / max(_scale_hint(m), 1e-6),
                method="link")


def _scale_hint(members):
    return 3.1   # nominal native arcsec/px; only used to express rms in px


# --------------------------------------------------------------------------- #
# Shift-and-stack (faint movers) — translation registration (equatorial rig)  #
# --------------------------------------------------------------------------- #
def shift_and_stack(frames, scale, bin_=4, vmax=5.0, vstep=0.5, k=5.0, log=print):
    """Synthetic tracking on binned, translation-aligned green frames.

    Returns a list of candidate dicts {x,y,ra,dec,rate,pa,method='shift-stack'}.
    Stars are aligned (v=0 stack); a faint mover coheres at its matching v.
    """
    if len(frames) < 4:
        return []
    ref = frames[len(frames) // 2]
    ref_kw = ref["kw"]
    refc = (ref_kw["CRVAL1"], ref_kw["CRVAL2"])
    # bin + translation-align each frame to the reference grid
    aligned, tmins = [], []
    for f in frames:
        g = _bin(f["green"], bin_)
        # pixel offset of the ref sky point between this frame and ref (full-res), /bin
        px_f = world2pix(refc[0], refc[1], f["kw"])
        px_r = world2pix(refc[0], refc[1], ref_kw)
        off = ((px_f[1] - px_r[1]) / bin_, (px_f[0] - px_r[0]) / bin_)   # (dy,dx)
        aligned.append(ndimage.shift(g, (-off[0], -off[1]), order=1, mode="constant", cval=np.nan))
        tmins.append(f["tmin"])
    tmins = np.array(tmins)
    t0 = tmins[np.argmin(np.abs(tmins - np.median(tmins)))]
    bscale = scale * bin_                       # arcsec per binned px
    span = float(tmins.max() - tmins.min())
    vpx_max = vmax / bscale                      # binned px per min
    # span-adaptive step: keep end-to-end smear <~0.7 binned px; also honour --vstep
    vpx_step = max(0.7 / max(span, 1.0), vstep / bscale, 1e-3)
    n = int(np.floor(vpx_max / vpx_step))
    MAXN = 40                                    # cap grid at (2*40+1)^2
    if n > MAXN:
        vpx_step = vpx_max / MAXN
        n = MAXN
        log(f"  shift-stack: velocity grid capped at {2*MAXN+1}^2 "
            f"(step raised to {vpx_step*bscale:.2f} \"/min — coverage still |v|<= {vmax})")
    grid = np.arange(-n, n + 1) * vpx_step
    log(f"  shift-stack: bin {bin_}, {len(grid)}x{len(grid)} velocity grid "
        f"(|v|<= {vmax} \"/min, step {vpx_step*bscale:.2f} \"/min); {len(aligned)} frames")
    # v=0 star stack — for rejecting fixed sources
    arr = np.stack(aligned)
    star_stack = np.nanmedian(arr, axis=0)
    smed = np.nanmedian(star_stack)
    sbg, ssig = P.estimate_background(np.nan_to_num(star_stack, nan=smed))
    star_set = _detect_set(star_stack, sbg, ssig, k)
    # max-projection across the velocity cube: for each pixel keep the brightest
    # coherent stack value and the velocity that produced it. One detection pass
    # at the end → a real faint mover stands out; noise doesn't cohere.
    H, W = arr.shape[1:]
    max_map = np.full((H, W), -np.inf)
    vx_map = np.zeros((H, W))
    vy_map = np.zeros((H, W))
    for vy in grid:
        for vx in grid:
            if abs(vx) < 1e-9 and abs(vy) < 1e-9:
                continue
            shifted = np.empty_like(arr)
            for i in range(len(aligned)):
                dt = tmins[i] - t0
                shifted[i] = ndimage.shift(arr[i], (-vy * dt, -vx * dt),
                                           order=1, mode="constant", cval=np.nan)
            stack = np.nanmedian(shifted, axis=0)
            better = np.nan_to_num(stack, nan=-np.inf) > max_map
            max_map = np.where(better, stack, max_map)
            vx_map = np.where(better, vx, vx_map)
            vy_map = np.where(better, vy, vy_map)
    max_map = np.nan_to_num(max_map, nan=smed, neginf=smed)
    bg, sig = P.estimate_background(max_map)
    vmin_keep = max(0.5, 1.5 * vpx_step)          # ignore ~static (residual stars)
    cands = []
    for (cx, cy, peak, npix) in P.detect_stars(max_map, bg, sig, k=k):
        if _near_any((cx, cy), star_set, 2.0):
            continue                               # fixed source (in v=0 stack)
        vx, vy = vx_map[int(round(cy)), int(round(cx))], vy_map[int(round(cy)), int(round(cx))]
        if np.hypot(vx, vy) < vmin_keep:
            continue
        fx, fy = cx * bin_, cy * bin_
        ra, dec = pix2world(fx, fy, ref_kw)
        cands.append(dict(x=fx, y=fy, ra=float(ra), dec=float(dec),
                          rate=float(np.hypot(vx, vy) * bscale),
                          pa=float(np.degrees(np.arctan2(vx, -vy)) % 360.0),
                          peak=float(peak), method="shift-stack", ref_name=ref["name"]))
    return _merge_candidates(cands, scale, bin_)


def _bin(img, b):
    if b <= 1:
        return img.astype(np.float64)
    h, w = img.shape
    img = img[:h // b * b, :w // b * b].astype(np.float64)
    return img.reshape(h // b, b, w // b, b).mean(axis=(1, 3))


def _detect_set(stack, bg, sig, k):
    return [(cx, cy) for (cx, cy, _p, _n) in P.detect_stars(stack, bg, sig, k=k)]


def _near_any(pt, pts, tol):
    return any(abs(pt[0] - q[0]) <= tol and abs(pt[1] - q[1]) <= tol for q in pts)


def _merge_candidates(cands, scale, bin_):
    """Collapse near-duplicate shift-stack hits (same object, neighbouring v)."""
    out = []
    for c in sorted(cands, key=lambda c: -c["peak"]):
        if any(abs(c["x"] - o["x"]) < 4 * bin_ and abs(c["y"] - o["y"]) < 4 * bin_ for o in out):
            continue
        out.append(c)
    return out


# --------------------------------------------------------------------------- #
# Outputs                                                                      #
# --------------------------------------------------------------------------- #
def _utc(frames, tmin):
    return (frames[0]["t"] + _dt.timedelta(minutes=tmin)).isoformat()


def write_report(path, frames, tracks, ss_cands, scale, params):
    lines = []
    lines.append("# Moving-object report")
    lines.append(f"# folder : {params['folder']}")
    lines.append(f"# frames : {len(frames)}  ·  scale {scale:.3f} \"/px (native)  ·  span "
                 f"{frames[-1]['tmin']:.1f} min" if frames else "# frames: 0")
    lines.append(f"# params : min-frames={params['min_frames']}, k={params['k']}, "
                 f"shift-stack={'on' if params['shift_stack'] else 'off'} "
                 f"(vmax={params['vmax']}\"/min, bin={params['bin']})")
    lines.append("# NOTE   : magnitudes relative/instrumental; SIP ignored; "
                 "shift-stack v-grid bounded at vmax (no silent truncation).")
    lines.append("")
    if not tracks and not ss_cands:
        lines.append("No moving-object candidates (linear multi-frame tracks). "
                     "Single-frame transients (satellites/cosmic rays) excluded.")
    for i, tr in enumerate(tracks, 1):
        m = tr["members"]
        lines.append(f"## Candidate L{i}  [linked, {tr['n']} frames]")
        lines.append(f"   motion : {tr['rate']:.2f} \"/min   PA {tr['pa']:.0f}°   "
                     f"span {tr['span_min']:.1f} min   rms {tr['rms_px']:.2f} px")
        lines.append(f"   start  : RA {FI._hms(m[0]['ra'])}  Dec {FI._dms(m[0]['dec'])}  "
                     f"@ {_utc(frames, m[0]['tmin'])}")
        lines.append(f"   end    : RA {FI._hms(m[-1]['ra'])}  Dec {FI._dms(m[-1]['dec'])}  "
                     f"@ {_utc(frames, m[-1]['tmin'])}")
        lines.append("   track  : frame  t(min)   x       y       RA            Dec         peak")
        for r in m:
            lines.append(f"          {r['fi']:>3}  {r['tmin']:>6.1f}  {r['x']:>7.1f} {r['y']:>7.1f}  "
                         f"{FI._hms(r['ra'])}  {FI._dms(r['dec'])}  {r['peak']:.0f}")
        lines.append("")
    for i, c in enumerate(ss_cands, 1):
        lines.append(f"## Candidate S{i}  [shift-stack, faint]")
        lines.append(f"   motion : {c['rate']:.2f} \"/min   PA {c['pa']:.0f}°")
        lines.append(f"   approx : x {c['x']:.0f}  y {c['y']:.0f}   "
                     f"RA {FI._hms(c['ra'])}  Dec {FI._dms(c['dec'])}  (on {c['ref_name']})")
        lines.append("")
    with open(path, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    return "\n".join(lines)


def write_region(path, tracks, ss_cands):
    """DS9 region file (image coords, 1-based)."""
    out = ["# Region file format: DS9", "image"]
    for i, tr in enumerate(tracks, 1):
        m = tr["members"]
        for r in m:
            out.append(f"circle({r['x']+1:.1f},{r['y']+1:.1f},8) # color=green")
        out.append(f"line({m[0]['x']+1:.1f},{m[0]['y']+1:.1f},"
                   f"{m[-1]['x']+1:.1f},{m[-1]['y']+1:.1f}) # color=green text={{L{i}}}")
    for i, c in enumerate(ss_cands, 1):
        out.append(f"circle({c['x']+1:.1f},{c['y']+1:.1f},10) # color=yellow text={{S{i}}}")
    with open(path, "w") as fh:
        fh.write("\n".join(out) + "\n")


def write_montage(path, frames, track, half=24):
    """Crop-stack montage: the candidate neighbourhood from each frame, tiled."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    m = track["members"]
    n = len(m)
    cols = min(n, 8)
    rows = int(np.ceil(n / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(1.6 * cols, 1.7 * rows), squeeze=False)
    for ax in axes.ravel():
        ax.axis("off")
    for j, r in enumerate(m):
        f = frames[r["fi"]]
        g = f["green"]
        x, y = int(round(r["x"])), int(round(r["y"]))
        sub = g[max(0, y - half):y + half, max(0, x - half):x + half]
        ax = axes[j // cols][j % cols]
        if sub.size:
            v = np.percentile(sub, [10, 99.5])
            ax.imshow(sub, cmap="gray", vmin=v[0], vmax=v[1], origin="lower")
            ax.plot(sub.shape[1] / 2, sub.shape[0] / 2, "o", mfc="none", mec="lime", ms=14, mew=1.2)
        ax.set_title(f"f{r['fi']} {r['tmin']:.0f}m", fontsize=7)
    fig.suptitle(f"Moving-object candidate — {track['rate']:.2f} \"/min, PA {track['pa']:.0f}°", fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)


def write_annotated(path, frames, track):
    """Annotated reference frame with the track drawn."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    m = track["members"]
    f = frames[m[len(m) // 2]["fi"]]
    g = f["green"]
    fig, ax = plt.subplots(figsize=(9, 6))
    v = np.percentile(g, [30, 99.6])
    ax.imshow(g, cmap="gray", vmin=v[0], vmax=v[1], origin="lower")
    xs = [r["x"] for r in m]
    ys = [r["y"] for r in m]
    ax.plot(xs, ys, "-", color="lime", lw=0.8)
    ax.plot(xs, ys, "o", mfc="none", mec="lime", ms=9, mew=1.0)
    ax.set_title(f"Track: {track['rate']:.2f} \"/min, PA {track['pa']:.0f}°, {track['n']} frames")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


# --------------------------------------------------------------------------- #
# Driver                                                                       #
# --------------------------------------------------------------------------- #
def detect(folder, out_dir=None, min_frames=4, k=6.0, shift_stack=True,
           vmax=5.0, vstep=0.5, bin_=4, max_per_frame=600, min_rate=0.5,
           cfa_pattern="RGGB", recursive=False, make_png=True, log=print):
    frames = load_frames(folder, cfa_pattern, k, max_per_frame, recursive, log)
    if len(frames) < min_frames:
        log(f"Only {len(frames)} usable frames (need >= {min_frames}). Stop.")
        return dict(frames=frames, tracks=[], shift_stack=[])
    scale = pixel_scale(frames[0]["kw"])
    recs = detections_sky(frames)
    nstar, nhot = reject_fixed(recs, len(frames), scale)
    ntrans = sum(1 for r in recs if not r["static"] and not r["hot"])
    log(f"{len(frames)} frames · scale {scale:.3f} \"/px · {len(recs)} detections · "
        f"{nstar} stars (fixed sky) · {nhot} hot pixels (fixed sensor) · {ntrans} transient")
    tracks = link_tracks(recs, frames, scale, min_frames=min_frames)
    slow = [t for t in tracks if t["rate"] < min_rate]
    tracks = [t for t in tracks if t["rate"] >= min_rate]
    log(f"linked tracks (>= {min_frames} frames, linear): {len(tracks)} "
        f"(dropped {len(slow)} below {min_rate}\"/min — effectively stationary, "
        f"corner/SIP wobble)")
    ss = []
    if shift_stack:
        ss = shift_and_stack(frames, scale, bin_=bin_, vmax=vmax, vstep=vstep,
                             k=max(4.0, k - 1.0), log=log)
        ss = [c for c in ss if c["rate"] >= min_rate]
        # drop shift-stack hits that coincide with a linked track
        ss = [c for c in ss if not any(
            abs(c["x"] - tr["members"][len(tr["members"]) // 2]["x"]) < 30 and
            abs(c["y"] - tr["members"][len(tr["members"]) // 2]["y"]) < 30 for tr in tracks)]
        log(f"shift-stack faint candidates: {len(ss)}")
    params = dict(folder=folder, min_frames=min_frames, k=k, shift_stack=shift_stack,
                  vmax=vmax, bin=bin_)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        report = write_report(os.path.join(out_dir, "report.txt"), frames, tracks, ss, scale, params)
        write_region(os.path.join(out_dir, "candidates.reg"), tracks, ss)
        if make_png:
            for i, tr in enumerate(tracks, 1):
                try:
                    write_montage(os.path.join(out_dir, f"candidate_L{i}_montage.png"), frames, tr)
                    write_annotated(os.path.join(out_dir, f"candidate_L{i}_annotated.png"), frames, tr)
                except Exception as e:
                    log(f"  (png L{i} failed: {e})")
        log(f"\nwrote report.txt, candidates.reg" + (", PNGs" if make_png and tracks else "") +
            f" -> {out_dir}")
        log("")
        log(report)
    return dict(frames=frames, tracks=tracks, shift_stack=ss, scale=scale)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Detect comets/asteroids across a light-frame sequence (excludes satellites).")
    ap.add_argument("folder", help="folder of raw .fit lights (each with an ASIAIR WCS)")
    ap.add_argument("--out", help="output dir (default <folder>/moving-objects)")
    ap.add_argument("--min-frames", type=int, default=4, help="min frames a track must span")
    ap.add_argument("-k", type=float, default=6.0, help="per-frame detection threshold (sigma)")
    ap.add_argument("--vmax", type=float, default=5.0, help="max searched motion (arcsec/min)")
    ap.add_argument("--vstep", type=float, default=0.5, help="shift-stack velocity step (arcsec/min)")
    ap.add_argument("--bin", type=int, default=4, help="binning for the shift-stack search")
    ap.add_argument("--max-per-frame", type=int, default=600, help="cap on detections kept per frame (brightest)")
    ap.add_argument("--min-rate", type=float, default=0.5, help="min motion to count as a mover (arcsec/min); slower = stationary")
    ap.add_argument("--no-shift-stack", action="store_true", help="skip the faint-mover synthetic-tracking pass")
    ap.add_argument("--no-png", action="store_true", help="skip the montage/annotated PNGs")
    ap.add_argument("--recursive", action="store_true")
    ap.add_argument("--cfa-pattern", default="RGGB", choices=["RGGB", "BGGR", "GRBG", "GBRG"])
    args = ap.parse_args(argv)
    out = args.out or os.path.join(args.folder.rstrip("/"), "moving-objects")
    detect(args.folder, out_dir=out, min_frames=args.min_frames, k=args.k,
           shift_stack=not args.no_shift_stack, vmax=args.vmax, vstep=args.vstep,
           bin_=args.bin, max_per_frame=args.max_per_frame, min_rate=args.min_rate,
           cfa_pattern=args.cfa_pattern, recursive=args.recursive, make_png=not args.no_png)
    return 0


if __name__ == "__main__":
    sys.exit(main())
