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


# ---------------------------------------------------------------------------
# --match calibration matching
# ---------------------------------------------------------------------------
def _cal_fits(path, gain=100, offset=50, temp=-10.0, exp=120.0, imagetyp="Light"):
    _make_fits(path, [
        "SIMPLE  =                    T",
        "BITPIX  =                   16",
        "NAXIS   =                    2",
        "NAXIS1  =                   40",
        "NAXIS2  =                   40",
        f"GAIN    = {gain:>20}",
        f"OFFSET  = {offset:>20}",
        f"CCD-TEMP= {temp:>20}",
        f"EXPTIME = {exp:>20}",
        f"IMAGETYP= '{imagetyp:<8}'",
    ])


def _make_set(d, prefix, n, **kw):
    paths = []
    for i in range(n):
        p = os.path.join(d, f"{prefix}_{i:03d}.fit")
        _cal_fits(p, **kw)
        paths.append(p)
    return paths


def test_match_offset_keyword_read():
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "x.fit")
        _cal_fits(f, gain=100, offset=50, temp=-9.9, exp=300.0, imagetyp="Dark")
        m = F.read_meta(f)
        assert m["offset"] == 50 and m["imagetyp"] == "Dark", (m["offset"], m["imagetyp"])
        print("  OFFSET/IMAGETYP keywords surfaced ✓")


def test_match_all_match():
    with tempfile.TemporaryDirectory() as d:
        a = _make_set(d, "light", 3, imagetyp="Light", exp=120.0, temp=-10.0)
        b = _make_set(d, "dark", 3, imagetyp="Dark", exp=120.0, temp=-9.8)  # Δ0.2 < 0.5
        r = F.match_sets(a, b, "lights-darks")
        assert r["match"] and not r["bad"], r["bad"]
        print(f"  lights-darks all-match (temp Δ0.2 within tol) ✓")


def test_match_exposure_mismatch():
    with tempfile.TemporaryDirectory() as d:
        a = _make_set(d, "light", 3, exp=120.0)
        b = _make_set(d, "dark", 3, exp=300.0)
        r = F.match_sets(a, b, "lights-darks")
        assert not r["match"] and r["bad"] == ["exposure"], r["bad"]
        print(f"  exposure mismatch flagged (120 vs 300) ✓")


def test_match_offset_mismatch():
    with tempfile.TemporaryDirectory() as d:
        a = _make_set(d, "light", 2, offset=50)
        b = _make_set(d, "dark", 2, offset=30)
        r = F.match_sets(a, b, "lights-darks")
        assert "offset" in r["bad"], r["bad"]
        print("  offset mismatch flagged (50 vs 30) ✓")


def test_match_temp_tolerance_boundary():
    with tempfile.TemporaryDirectory() as d:
        a = _make_set(d, "light", 2, temp=-10.0)
        within = _make_set(d, "d1", 2, temp=-9.6)   # Δ0.4 ≤ 0.5
        outside = _make_set(d, "d2", 2, temp=-9.2)   # Δ0.8 > 0.5
        assert F.match_sets(a, within, "lights-darks")["match"]
        r = F.match_sets(a, outside, "lights-darks")
        assert not r["match"] and r["bad"] == ["temp"], r["bad"]
        print("  temp tolerance: Δ0.4 matches, Δ0.8 fails ✓")


def test_match_nonuniform_set():
    # a set with mixed gains must fail even if the other set is uniform
    with tempfile.TemporaryDirectory() as d:
        bad = [os.path.join(d, "m0.fit"), os.path.join(d, "m1.fit")]
        _cal_fits(bad[0], gain=100)
        _cal_fits(bad[1], gain=0)            # someone dropped a wrong-gain frame in
        b = _make_set(d, "dark", 2, gain=100)
        r = F.match_sets(bad, b, "lights-darks")
        assert "gain" in r["bad"], r["bad"]
        gp = next(p for p in r["params"] if p["name"] == "gain")
        assert "mixed" in gp["detail"], gp["detail"]
        print(f"  non-uniform set flagged: {gp['detail']} ✓")


def test_match_darks_flatdarks_brightness():
    # monkeypatch _frame_mean so the brightness path is deterministic (no numpy)
    with tempfile.TemporaryDirectory() as d:
        a = _make_set(d, "dark", 2, imagetyp="Dark", temp=-10.0)
        b = _make_set(d, "fdark", 2, imagetyp="Dark", temp=-10.0)
        means = {p: 0.00770 for p in a + b}
        orig = F._frame_mean
        F._frame_mean = lambda m: means[m["path"]]
        try:
            r = F.match_sets(a, b, "darks-flatdarks")
            assert r["match"], r["bad"]                 # equal means → match
            for p in b:
                means[p] = 0.00850                      # ~10% brighter → mismatch
            r2 = F.match_sets(a, b, "darks-flatdarks")
            assert not r2["match"] and "brightness" in r2["bad"], r2["bad"]
        finally:
            F._frame_mean = orig
        print("  darks-flatdarks brightness: equal matches, +10% fails ✓")


def test_match_exit_code_via_main():
    with tempfile.TemporaryDirectory() as d:
        da, db = os.path.join(d, "A"), os.path.join(d, "B")
        os.makedirs(da); os.makedirs(db)
        _make_set(da, "light", 2, exp=120.0)
        _make_set(db, "dark", 2, exp=300.0)
        assert F.main([da, "--match", "lights-darks", "--against", db]) == 1
        _make_set(db + "_ok", "dark", 2, exp=120.0) if False else None
        dc = os.path.join(d, "C"); os.makedirs(dc)
        _make_set(dc, "dark", 2, exp=120.0, temp=-9.9)
        assert F.main([da, "--match", "lights-darks", "--against", dc]) == 0
        print("  main() exit code: 1 on mismatch, 0 on match ✓")


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
