#!/usr/bin/env python3
"""Tests for frame_info.py — FITS + XISF metadata, scale, centre, WCS parsing.

Run from repo root:  python3 scripts/test_frame_info.py
Stdlib only.
"""
import math
import os
import struct
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import frame_info as F

BLOCK, CARD = 2880, 80


def _card(s):
    return s.ljust(CARD)[:CARD].encode("latin-1")


def _make_fits(path, cards, n_data=2880):
    body = b"".join(_card(c) for c in cards) + _card("END")
    body += b" " * ((BLOCK - len(body) % BLOCK) % BLOCK)
    data = bytes((i * 7) % 256 for i in range(n_data))
    data += b"\x00" * ((BLOCK - len(data) % BLOCK) % BLOCK)
    with open(path, "wb") as fh:
        fh.write(body + data)


def _make_xisf(path, geometry="100:80:3", filter_prop="LPro", astro=True,
               extra_fits=(), data_start=4096, n_data=4096):
    fits = "".join(f'<FITSKeyword name="{k}" value="{v}" comment="x"/>' for k, v in extra_fits)
    prop = f'<Property id="Instrument:Filter:Name" type="String">{filter_prop}</Property>' if filter_prop is not None else ""
    astrop = '<Property id="PCL:AstrometricSolution:Catalog" type="String">GaiaDR3</Property>' if astro else ""
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?><xisf version="1.0">'
        f'<Image geometry="{geometry}" sampleFormat="Float32" '
        f'location="attachment:{data_start}:{n_data}">'
        f'{fits}{prop}{astrop}</Image></xisf>')
    xb = xml.encode("utf-8")
    with open(path, "wb") as fh:
        fh.write(F.XISF_SIG + struct.pack("<I", len(xb)) + b"\x00\x00\x00\x00" + xb)
        fh.write(b"\x00" * (data_start - 16 - len(xb)))
        fh.write(bytes((i * 11) % 256 for i in range(n_data)))


def test_fits_cd_scale_and_center():
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "l.fit")
        # CD matrix encoding ~3.10"/px, 79deg rotation, centred near a known point
        _make_fits(f, [
            "SIMPLE  =                    T",
            "BITPIX  =                   16",
            "NAXIS   =                    2",
            "NAXIS1  =                 6248",
            "NAXIS2  =                 4176",
            "FILTER  = 'LPro    '",
            "EXPTIME =                120.0",
            "GAIN    =                  100",
            "CTYPE1  = 'RA---TAN-SIP'",
            "CRPIX1  =        3124.0",
            "CRPIX2  =        2088.0",
            "CRVAL1  =        186.0",
            "CRVAL2  =         26.2",
            "CD1_1   =    0.000164311",
            "CD1_2   =   -0.000843992",
            "CD2_1   =    0.000844160",
            "CD2_2   =    0.000164718",
        ])
        m = F.read_meta(f)
        assert m["format"] == "FITS"
        assert m["filter"] == "LPro", m["filter"]
        assert m["exposure"] == 120.0 and m["gain"] == 100
        assert m["solved"] is True
        assert abs(m["scale"] - 3.096) < 0.02, m["scale"]
        # CRPIX at centre → centre == CRVAL
        ra, dec = m["center"]
        assert abs(ra - 186.0) < 0.01 and abs(dec - 26.2) < 0.01, (ra, dec)
        assert abs(m["rotation"] - 79.0) < 1.0, m["rotation"]
        print(f"  FITS: filter LPro, scale {m['scale']:.3f}\"/px, centre OK, rot {m['rotation']:.1f}° ✓")


def test_xisf_property_geometry_astro():
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "m.xisf")
        _make_xisf(f, geometry="12110:7812:3", filter_prop="LPro", astro=True,
                   extra_fits=[("EXPTIME", "120.0"), ("XPIXSZ", "2.7"), ("FOCALLEN", "358.9"),
                               ("FILTER", "'NoFilter'")])
        m = F.read_meta(f)
        assert m["format"] == "XISF"
        assert m["dims"] == (12110, 7812, 3), m["dims"]
        # property (LPro) must win over the FITS keyword (NoFilter)
        assert m["filter"] == "LPro", m["filter"]
        assert m["filter_kw"] == "NoFilter"
        assert m["solved"] is True          # PCL:AstrometricSolution present
        assert abs(m["scale"] - 1.552) < 0.02, m["scale"]   # 206.265*2.7/358.9
        print(f"  XISF: property LPro wins over NoFilter keyword, scale {m['scale']:.3f}\"/px, astro=solved ✓")


def test_xisf_no_wcs():
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "n.xisf")
        _make_xisf(f, filter_prop=None, astro=False)
        m = F.read_meta(f)
        assert m["solved"] is False, "no astro property and no CD → unsolved"
        print("  XISF without astrometric solution → no WCS ✓")


def test_sexagesimal_and_format():
    assert abs(F._sex2deg("12 27 44.8", 15) - 186.9367) < 0.001
    assert abs(F._sex2deg("+12 54 02.6", 1) - 12.9007) < 0.001
    assert abs(F._sex2deg("-00 30 00", 1) + 0.5) < 0.001
    assert F._hms(186.0687).startswith("12:24:16")
    assert F._dms(26.2137).startswith("+26:12:49")
    assert F._dms(-5.5) == "-05:30:00.0"
    print("  sexagesimal parse + HMS/DMS format ✓")


def test_folder_iteration():
    with tempfile.TemporaryDirectory() as d:
        _make_xisf(os.path.join(d, "a.xisf"))
        _make_fits(os.path.join(d, "b.fit"), ["SIMPLE  =                    T", "BITPIX  =                   16", "NAXIS   =                    0"])
        open(os.path.join(d, "ignore.txt"), "w").close()
        open(os.path.join(d, "._a.xisf"), "w").close()       # macOS resource fork
        files = list(F.iter_files(d, recursive=False))
        names = sorted(os.path.basename(x) for x in files)
        assert names == ["a.xisf", "b.fit"], names
        print(f"  folder iteration picks .xisf/.fit, skips junk: {names} ✓")


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
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
