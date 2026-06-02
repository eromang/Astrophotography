#!/usr/bin/env python3
"""frame_info.py — inspect FITS / XISF frame metadata and astrometric status.

A one-stop header reader for the vault: filter (FITS keyword *and* XISF
property), exposure / gain / temperature, dimensions, plate scale, whether the
frame carries a WCS (and its centre), and optionally channel statistics.

Header-only by default — never loads pixel data, so it's instant on multi-GB
masters. `--stats` reads the data block (needs numpy) for median / max / clip.

    python3 scripts/frame_info.py <file>                 # detailed readout
    python3 scripts/frame_info.py <folder> [--recursive]  # one-row-per-file table (WCS triage)
    python3 scripts/frame_info.py <file> --stats          # + channel median/max/clip

Folder mode is the reprocessing-triage view: the WCS column shows which masters
lack an astrometric solution (the ones a re-solve unblocks). Stdlib only
(numpy only for --stats).
"""
from __future__ import annotations
import argparse
import math
import os
import re
import struct
import sys

BLOCK, CARD = 2880, 80
XISF_SIG = b"XISF0100"

# FITS keywords we surface (others ignored)
_WANT = ("OBJECT", "FILTER", "EXPTIME", "EXPOSURE", "GAIN", "EGAIN",
         "CCD-TEMP", "SET-TEMP", "NAXIS1", "NAXIS2", "NAXIS3", "BITPIX",
         "XPIXSZ", "FOCALLEN", "RA", "DEC", "OBJCTRA", "OBJCTDEC",
         "CRVAL1", "CRVAL2", "CRPIX1", "CRPIX2",
         "CD1_1", "CD1_2", "CD2_1", "CD2_2", "CDELT1", "CDELT2",
         "CTYPE1", "DATE-OBS")


# ---------------------------------------------------------------------------
# Header parsing (no pixel data)
# ---------------------------------------------------------------------------
def _parse_card_value(card: str):
    """Return the value of a FITS card as float, int or stripped string."""
    if "=" not in card[:10]:
        return None
    body = card[10:]
    # strip trailing comment (outside quotes)
    if body.lstrip().startswith("'"):
        m = re.match(r"\s*'([^']*)'", body)
        return m.group(1).strip() if m else None
    body = body.split("/", 1)[0].strip()
    if body in ("T", "F"):
        return body == "T"
    try:
        return int(body)
    except ValueError:
        pass
    try:
        return float(body)
    except ValueError:
        return body or None


def _fits_keywords(path):
    kw = {}
    with open(path, "rb") as fh:
        nbytes = 0
        done = False
        while not done:
            block = fh.read(BLOCK)
            if len(block) < BLOCK:
                break
            nbytes += BLOCK
            for i in range(0, BLOCK, CARD):
                c = block[i:i + CARD].decode("latin-1")
                key = c[:8].strip()
                if key == "END":
                    done = True
                    break
                if key in _WANT and key not in kw:
                    kw[key] = _parse_card_value(c)
            if nbytes > 256 * BLOCK:
                break
    return kw, ("FITS", None, None)


def _fits_data_offset(path):
    """Byte offset where the FITS pixel data begins (after END, BLOCK-padded)."""
    with open(path, "rb") as fh:
        nb = 0
        while True:
            block = fh.read(BLOCK)
            if len(block) < BLOCK:
                return nb
            nb += BLOCK
            for i in range(0, BLOCK, CARD):
                if block[i:i + CARD][:8].rstrip() == b"END":
                    return nb
            if nb > 256 * BLOCK:
                return nb


def _xisf_keywords(path):
    with open(path, "rb") as fh:
        fh.read(8)
        hlen = struct.unpack("<I", fh.read(4))[0]
        fh.read(4)
        xml = fh.read(hlen).decode("utf-8", "replace")
    kw = {}
    for m in re.finditer(r'<FITSKeyword name="([^"]+)" value="([^"]*)"', xml):
        k = m.group(1).strip()
        if k in _WANT and k not in kw:
            kw[k] = _coerce(m.group(2))
    geom = None
    mg = re.search(r'<Image\b[^>]*geometry="([^"]+)"', xml)
    if mg:
        geom = mg.group(1)
    # XISF native filter property
    mp = re.search(r'<Property id="Instrument:Filter:Name"[^>]*>([^<]*)</Property>', xml)
    if not mp:
        mp = re.search(r'<Property id="Instrument:Filter:Name"[^>]*\bvalue="([^"]*)"', xml)
    filt_prop = mp.group(1).strip() if mp else None
    astro = "PCL:AstrometricSolution" in xml
    # sample format / data offset (for --stats)
    fmt = re.search(r'<Image\b[^>]*sampleFormat="(\w+)"', xml)
    loc = re.search(r'location="attachment:(\d+):(\d+)"', xml)
    extra = {"geometry": geom, "filter_prop": filt_prop, "astro": astro,
             "sampleFormat": fmt.group(1) if fmt else None,
             "data_off": int(loc.group(1)) if loc else None,
             "data_size": int(loc.group(2)) if loc else None}
    return kw, ("XISF", geom, extra)


def _coerce(raw):
    raw = raw.strip()
    if raw.startswith("'"):
        return raw.strip("'").strip()
    if raw in ("T", "F"):
        return raw == "T"
    try:
        return int(raw)
    except ValueError:
        pass
    try:
        return float(raw)
    except ValueError:
        return raw or None


def read_meta(path):
    with open(path, "rb") as fh:
        sig = fh.read(8)
    kw, (fmt, geom, extra) = (_xisf_keywords(path) if sig == XISF_SIG
                              else _fits_keywords(path))
    m = {"path": path, "format": fmt, "kw": kw, "extra": extra or {}}
    # dimensions
    if geom:
        w, h, *c = [int(x) for x in geom.split(":")]
        m["dims"] = (w, h, c[0] if c else 1)
    else:
        m["dims"] = (kw.get("NAXIS1"), kw.get("NAXIS2"), kw.get("NAXIS3", 1))
    # filter — XISF property wins (that's what WBPP groups by); fall back to keyword
    m["filter"] = (m["extra"].get("filter_prop") or kw.get("FILTER") or None)
    m["filter_kw"] = kw.get("FILTER")
    m["exposure"] = kw.get("EXPTIME", kw.get("EXPOSURE"))
    m["gain"] = kw.get("GAIN", kw.get("EGAIN"))
    m["temp"] = kw.get("CCD-TEMP", kw.get("SET-TEMP"))
    m["object"] = kw.get("OBJECT")
    _wcs(m)
    return m


# ---------------------------------------------------------------------------
# Scale / centre / WCS
# ---------------------------------------------------------------------------
def _wcs(m):
    kw = m["kw"]
    cd = [kw.get(k) for k in ("CD1_1", "CD1_2", "CD2_1", "CD2_2")]
    has_cd = all(isinstance(x, (int, float)) for x in cd)
    astro = m["extra"].get("astro", False) or has_cd or (kw.get("CTYPE1") and "TAN" in str(kw["CTYPE1"]))
    m["solved"] = bool(astro)
    # plate scale (arcsec/px)
    scale = rot = None
    if has_cd:
        scale = math.hypot(cd[0], cd[2]) * 3600
        rot = math.degrees(math.atan2(cd[2], cd[0]))
        m["scale_src"] = "CD"
    elif isinstance(kw.get("CDELT1"), (int, float)):
        scale = abs(kw["CDELT1"]) * 3600
        m["scale_src"] = "CDELT"
    elif isinstance(kw.get("XPIXSZ"), (int, float)) and isinstance(kw.get("FOCALLEN"), (int, float)) and kw["FOCALLEN"]:
        scale = 206.265 * kw["XPIXSZ"] / kw["FOCALLEN"]
        m["scale_src"] = "pixel/focal"
    m["scale"] = scale
    m["rotation"] = rot
    # centre
    ra = dec = None
    w, h, _ = m["dims"]
    if has_cd and all(isinstance(kw.get(k), (int, float)) for k in ("CRVAL1", "CRVAL2", "CRPIX1", "CRPIX2")) and w and h:
        dx, dy = w / 2 - kw["CRPIX1"], h / 2 - kw["CRPIX2"]
        xi = cd[0] * dx + cd[1] * dy
        eta = cd[2] * dx + cd[3] * dy
        dec = kw["CRVAL2"] + eta
        ra = kw["CRVAL1"] + xi / math.cos(math.radians(dec)) if abs(dec) < 89.9 else kw["CRVAL1"]
    elif isinstance(kw.get("RA"), (int, float)) and isinstance(kw.get("DEC"), (int, float)):
        ra, dec = kw["RA"], kw["DEC"]
    elif kw.get("OBJCTRA") and kw.get("OBJCTDEC"):
        ra, dec = _sex2deg(kw["OBJCTRA"], 15), _sex2deg(kw["OBJCTDEC"], 1)
    m["center"] = (ra, dec)
    if scale and w and h:
        m["fov"] = (w * scale / 3600, h * scale / 3600)
    else:
        m["fov"] = None


def _sex2deg(s, mult):
    try:
        parts = [float(x) for x in str(s).replace(":", " ").split()]
        sign = -1 if str(s).strip().startswith("-") else 1
        d = abs(parts[0]) + (parts[1] if len(parts) > 1 else 0) / 60 + (parts[2] if len(parts) > 2 else 0) / 3600
        return sign * d * mult
    except Exception:
        return None


def _hms(ra):
    if ra is None:
        return "—"
    ra %= 360
    h = ra / 15
    return f"{int(h):02d}:{int(h*60)%60:02d}:{(h*3600)%60:04.1f}"


def _dms(dec):
    if dec is None:
        return "—"
    s = "-" if dec < 0 else "+"
    dec = abs(dec)
    return f"{s}{int(dec):02d}:{int(dec*60)%60:02d}:{(dec*3600)%60:04.1f}"


# ---------------------------------------------------------------------------
# Channel statistics (optional, numpy)
# ---------------------------------------------------------------------------
def _stats(m):
    import numpy as np
    p, kw, ex = m["path"], m["kw"], m["extra"]
    w, h, ch = m["dims"]
    if m["format"] == "XISF":
        dt = {"Float32": np.float32, "Float64": np.float64, "UInt16": np.uint16, "UInt8": np.uint8}[ex["sampleFormat"]]
        with open(p, "rb") as fh:
            fh.seek(ex["data_off"])
            a = np.frombuffer(fh.read(ex["data_size"]), dtype=dt)
        a = a.reshape(ch, h, w) if ch > 1 else a.reshape(h, w)
    else:
        bit = kw.get("BITPIX")
        dt = {16: ">i2", -32: ">f4", 8: "u1"}.get(bit, ">f4")
        hbytes = _fits_data_offset(p)
        with open(p, "rb") as fh:
            fh.seek(hbytes)
            a = np.frombuffer(fh.read(), dtype=np.dtype(dt))
        n = (ch or 1) * h * w
        a = a[:n].astype(np.float32)
        if bit == 16:
            a = (a + kw.get("BZERO", 32768)) / 65535.0
        a = a.reshape(ch, h, w) if ch and ch > 1 else a.reshape(h, w)
    names = "RGB" if (ch or 1) == 3 else "K"
    out = []
    for i in range(ch or 1):
        c = a[i] if (ch or 1) > 1 else a
        c = c.astype("float64")
        out.append((names[i], float(c.mean()), float(np.median(c)), float(c.max()), 100.0 * float((c >= 0.999).mean())))
    return out


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
def print_detail(m, stats=False):
    w, h, ch = m["dims"]
    print(f"File       : {m['path']}")
    print(f"Format     : {m['format']}  |  {w}x{h}x{ch}" + (f"  {m['extra'].get('sampleFormat')}" if m["extra"].get("sampleFormat") else ""))
    if m["object"]:
        print(f"Object     : {m['object']}")
    fp = m["extra"].get("filter_prop")
    fkw = m["filter_kw"]
    if m["format"] == "XISF":
        print(f"Filter     : {m['filter']}   (property: {fp!r}  ·  FITS keyword: {fkw!r})")
    else:
        print(f"Filter     : {m['filter']!r}")
    exp = f"{m['exposure']} s" if m["exposure"] is not None else "?"
    print(f"Exposure   : {exp}   Gain {m['gain']}   Temp {m['temp']}")
    if m["scale"]:
        fov = f"   FOV {m['fov'][0]:.2f} x {m['fov'][1]:.2f} deg" if m["fov"] else ""
        rot = f"   rot {m['rotation']:.1f}°" if m["rotation"] is not None else ""
        print(f"Plate scale: {m['scale']:.3f} \"/px  (from {m.get('scale_src')}){rot}{fov}")
    ra, dec = m["center"]
    src = "SOLVED" if m["solved"] else "no WCS"
    if m["format"] == "XISF" and m["extra"].get("astro"):
        src += " (PCL:AstrometricSolution)"
    print(f"WCS        : {src}")
    if ra is not None:
        print(f"Center     : RA {_hms(ra)}  Dec {_dms(dec)}   ({ra:.4f}, {dec:.4f})")
    if stats:
        try:
            print("Channels   :")
            for name, mean, med, mx, clip in _stats(m):
                print(f"   {name}: median {med:.4f}  mean {mean:.4f}  max {mx:.4f}  clip≥0.999 {clip:.3f}%")
        except Exception as e:
            print(f"   (stats failed: {e})")


def print_row(m):
    w, h, ch = m["dims"]
    wcs = "OK " if m["solved"] else "no!"
    sc = f"{m['scale']:.3f}" if m["scale"] else "  ?  "
    ra, dec = m["center"]
    ctr = f"{_hms(ra)} {_dms(dec)}" if ra is not None else "—"
    exp = f"{m['exposure']}s" if m["exposure"] is not None else "?"
    dims = f"{w}x{h}" + (f"x{ch}" if ch and ch > 1 else "")
    print(f"{wcs}  {str(m['filter'] or '—'):10} {dims:13} {sc:>6} {exp:>7}  {ctr:24} {os.path.basename(m['path'])[:48]}")


def iter_files(target, recursive):
    if os.path.isfile(target):
        yield target
        return
    walker = os.walk(target) if recursive else [(target, [], sorted(os.listdir(target)))]
    for root, _d, files in walker:
        for f in sorted(files):
            if f.lower().endswith((".fit", ".fits", ".fts", ".xisf")) and not f.startswith("._"):
                yield os.path.join(root, f)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Inspect FITS/XISF metadata, plate scale and WCS status.")
    ap.add_argument("path", help="a .fit/.xisf file or a folder")
    ap.add_argument("--recursive", action="store_true", help="recurse into subfolders")
    ap.add_argument("--stats", action="store_true", help="also compute channel median/max/clip (reads data; needs numpy)")
    args = ap.parse_args(argv)

    if os.path.isfile(args.path):
        print_detail(read_meta(args.path), stats=args.stats)
        return 0
    # folder → table
    print("WCS  Filter     Dims          Scale     Exp  Center(RA/Dec)           Name")
    n = solved = 0
    for p in iter_files(args.path, args.recursive):
        try:
            m = read_meta(p)
        except Exception as e:
            print(f"ERR  {os.path.basename(p)}: {e}")
            continue
        print_row(m)
        n += 1
        solved += m["solved"]
    print(f"\n{n} frames · {solved} solved · {n - solved} without WCS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
