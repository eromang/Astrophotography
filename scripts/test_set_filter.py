#!/usr/bin/env python3
"""Tests for set_filter.py — correctness + the critical data-preserving guarantee.

Run from repo root:  python3 scripts/test_set_filter.py
Stdlib only.
"""
import hashlib
import os
import struct
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import set_filter as S

BLOCK, CARD = 2880, 80


def _make_fits(path, n_data_bytes=2880, with_filter=None, extra_cards=0):
    """Write a minimal valid FITS (1 header block) with optional FILTER card."""
    cards = [
        b"SIMPLE  =                    T".ljust(CARD),
        b"BITPIX  =                   16".ljust(CARD),
        b"NAXIS   =                    1".ljust(CARD),
        f"NAXIS1  = {n_data_bytes // 2:>20}".encode().ljust(CARD),
    ]
    for i in range(extra_cards):
        cards.append(f"PAD{i:<5}= {i:>20}".encode().ljust(CARD))
    if with_filter is not None:
        cards.append(S._filter_card(with_filter))
    cards.append(b"END".ljust(CARD))
    hdr = b"".join(cards)
    hdr += b" " * ((BLOCK - len(hdr) % BLOCK) % BLOCK)
    data = bytes((i * 7) % 256 for i in range(n_data_bytes))
    data += b"\x00" * ((BLOCK - len(data) % BLOCK) % BLOCK)
    with open(path, "wb") as fh:
        fh.write(hdr + data)
    return len(hdr)


def _data_md5(path, hdr_bytes):
    with open(path, "rb") as fh:
        fh.seek(hdr_bytes)
        return hashlib.md5(fh.read()).hexdigest()


def test_filename_autodetect():
    cases = {
        "Light_13 Comae Berenices_120.0s_Bin1_2600MC_gain100_20260525-234139_-9.6C_LPro_0001.fit": "LPro",
        "Flat_10.0ms_Bin1_2600MC_gain100_20260531-175208_-10.0C_LPro_0001.fit": "LPro",
        "Dark_220.0s_Bin1_2600MC_gain100_20250302-152354_-9.6C_0001.fit": None,
        "Flat_50.0ms_Bin1_2600MC_gain100_20241226-170806_-19.6C_0001.fit": None,
    }
    for name, exp in cases.items():
        got = S.filter_from_name(name)
        assert got == exp, f"{name}: expected {exp}, got {got}"
    print(f"  autodetect: {len(cases)} filenames parsed correctly (darks/untokened -> None)")


def test_insert_preserves_data():
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "x.fit")
        hdr0 = _make_fits(f, n_data_bytes=4000, with_filter=None)
        before = _data_md5(f, hdr0)
        status = S.set_filter_file(f, "LPro", apply=True)
        with open(f, "rb") as fh:
            cards, hdr1 = S._read_header_cards(fh)
        assert S.current_filter(cards) == "LPro", "FILTER not set"
        assert hdr1 == hdr0, "header size changed (should stay 1 block / data-preserving)"
        after = _data_md5(f, hdr1)
        assert after == before, "DATA CHANGED — must be header-only!"
        print(f"  insert: {status}; FILTER=LPro; data MD5 unchanged ({after[:8]}…) ✓")


def test_replace_blank_filter():
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "y.fit")
        hdr0 = _make_fits(f, with_filter="")     # blank FILTER present
        before = _data_md5(f, hdr0)
        S.set_filter_file(f, "FQuad", apply=True)
        with open(f, "rb") as fh:
            cards, _ = S._read_header_cards(fh)
        assert S.current_filter(cards) == "FQuad"
        assert _data_md5(f, hdr0) == before
        print("  replace blank FILTER -> FQuad; data unchanged ✓")


def test_idempotent_and_dryrun():
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "z.fit")
        _make_fits(f, with_filter=None)
        assert S.set_filter_file(f, "LPro", apply=False).startswith("DRY")  # dry run
        with open(f, "rb") as fh:
            cards, _ = S._read_header_cards(fh)
        assert S.current_filter(cards) is None, "dry run must not write"
        S.set_filter_file(f, "LPro", apply=True)
        assert S.set_filter_file(f, "LPro", apply=True) == "already LPro"   # idempotent
        print("  dry-run writes nothing; second apply -> 'already LPro' ✓")


def test_full_rewrite_fallback():
    # fill the header block so insert needs a new block (full-rewrite path)
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "full.fit")
        # 1 block = 36 cards; SIMPLE..NAXIS1 (4) + END (1) -> 31 free; pad 31 -> no room
        hdr0 = _make_fits(f, n_data_bytes=2880, with_filter=None, extra_cards=31)
        before = _data_md5(f, hdr0)
        status = S.set_filter_file(f, "LPro", apply=True)
        with open(f, "rb") as fh:
            cards, hdr1 = S._read_header_cards(fh)
        assert S.current_filter(cards) == "LPro"
        assert hdr1 == hdr0 + BLOCK, "should have grown by one header block"
        assert _data_md5(f, hdr1) == before, "data changed in full rewrite!"
        print(f"  full-rewrite fallback: {status}; +1 block; data unchanged ✓")


# --------------------------------------------------------------------------
# XISF tests
# --------------------------------------------------------------------------
def _make_xisf(path, filter_value="NoFilter", self_closing=False, with_prop=True,
               n_data=8192, data_start=4096):
    """Write a minimal monolithic XISF with a Filter:Name property + data block."""
    if not with_prop:
        prop = ""                       # older masters: property absent entirely
    elif self_closing:
        prop = '<Property id="Instrument:Filter:Name" type="String"/>'
    else:
        prop = f'<Property id="Instrument:Filter:Name" type="String">{filter_value}</Property>'
    fits_filter = (filter_value or "").ljust(8) if filter_value else "        "
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<xisf version="1.0" xmlns="http://www.pixinsight.com/xisf">'
        f'<Image geometry="64:64:1" sampleFormat="Float32" colorSpace="Gray" '
        f'location="attachment:{data_start}:{n_data}">'
        '<FITSKeyword name="IMAGETYP" value="\'Master Flat\'" comment="Type of image"/>'
        f'<FITSKeyword name="FILTER" value="\'{fits_filter}\'" comment="Filter used when taking image"/>'
        '<Property id="Instrument:Camera:Name" type="String">ZWO ASI2600MC Pro</Property>'
        f'{prop}'
        '</Image>'
        '</xisf>')
    xml_b = xml.encode("utf-8")
    hlen = len(xml_b)
    assert 16 + hlen <= data_start, "synthetic header too big"
    data = bytes((i * 13) % 256 for i in range(n_data))
    with open(path, "wb") as fh:
        fh.write(S.XISF_SIG)
        fh.write(struct.pack("<I", hlen))
        fh.write(b"\x00\x00\x00\x00")
        fh.write(xml_b)
        fh.write(b"\x00" * (data_start - 16 - hlen))
        fh.write(data)
    return data_start


def _xisf_data_md5(path, data_start):
    with open(path, "rb") as fh:
        fh.seek(data_start)
        return hashlib.md5(fh.read()).hexdigest()


def _xisf_prop(path):
    with open(path, "rb") as fh:
        blob = fh.read()
    _, xml = S._xisf_header(blob)
    return S.xisf_current_filter(xml)


def test_xisf_master_autodetect():
    cases = {
        "masterFlat_BIN-1_6248x4176_FILTER-LPro_CFA_FLAT-10ms.xisf": "LPro",
        "masterFlat_BIN-1_6248x4176_FILTER-FQuad_CFA_FLAT-60ms.xisf": "FQuad",
        "masterFlat_BIN-1_6248x4176_FILTER-NoFilter_CFA_FLAT-10.0ms.xisf": "NoFilter",
        "masterDark_BIN-1_6248x4176_EXPOSURE-120.00s.xisf": None,
    }
    for name, exp in cases.items():
        got = S.filter_from_name(name)
        assert got == exp, f"{name}: expected {exp}, got {got}"
    print(f"  master-filename autodetect: {len(cases)} names parsed (darks -> None) ✓")


def test_xisf_set_preserves_data():
    # NoFilter (8) -> LPro (4): XML shrinks, padding grows; data must be identical
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "m.xisf")
        ds = _make_xisf(f, filter_value="NoFilter")
        before = _xisf_data_md5(f, ds)
        status = S.set_filter_xisf(f, "LPro", apply=True)
        assert _xisf_prop(f) == "LPro", f"property not LPro: {_xisf_prop(f)!r}"
        after = _xisf_data_md5(f, ds)
        assert after == before, "DATA CHANGED — must be header-only!"
        # FITS keyword updated too
        with open(f, "rb") as fh:
            _, xml = S._xisf_header(fh.read())
        assert "value=\"'LPro    '\"" in xml, "FITS FILTER keyword not updated"
        print(f"  xisf set NoFilter->LPro: {status}; data MD5 unchanged ({after[:8]}…) ✓")


def test_xisf_empty_to_longer_value():
    # self-closing empty property -> FQuad (XML grows); data must be identical
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "e.xisf")
        ds = _make_xisf(f, self_closing=True)
        before = _xisf_data_md5(f, ds)
        assert _xisf_prop(f) == "", "synthetic empty prop not empty"
        S.set_filter_xisf(f, "FQuad", apply=True)
        assert _xisf_prop(f) == "FQuad"
        assert _xisf_data_md5(f, ds) == before, "data changed on grow path!"
        print("  xisf empty->FQuad (XML grows): property set; data unchanged ✓")


def test_xisf_insert_when_absent():
    # older masters (e.g. FQuad) have NO Filter:Name property -> must insert it
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "old.xisf")
        ds = _make_xisf(f, filter_value="NoFilter", with_prop=False)
        before = _xisf_data_md5(f, ds)
        assert _xisf_prop(f) is None, "synthetic should have no property"
        status = S.set_filter_xisf(f, "FQuad", apply=True)
        assert "inserted" in status, status
        assert _xisf_prop(f) == "FQuad"
        assert _xisf_data_md5(f, ds) == before, "data changed on insert!"
        # FITS keyword corrected too (was 'NoFilter ')
        with open(f, "rb") as fh:
            _, xml = S._xisf_header(fh.read())
        assert "value=\"'FQuad   '\"" in xml, "FITS FILTER not corrected"
        print(f"  xisf insert (property absent): {status}; data unchanged ✓")


def test_xisf_dryrun_and_idempotent():
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "z.xisf")
        ds = _make_xisf(f, filter_value="NoFilter")
        before = _xisf_data_md5(f, ds)
        assert S.set_filter_xisf(f, "LPro", apply=False).startswith("DRY")
        assert _xisf_prop(f) == "NoFilter", "dry run must not write"
        assert _xisf_data_md5(f, ds) == before
        S.set_filter_xisf(f, "LPro", apply=True)
        assert S.set_filter_xisf(f, "LPro", apply=True) == "already LPro"
        print("  xisf dry-run writes nothing; second apply -> 'already LPro' ✓")


def test_xisf_dispatch_and_filesize_offset():
    # the data attachment offset must remain reachable (data_start unchanged)
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "d.xisf")
        ds = _make_xisf(f, filter_value="NoFilter")
        assert S.is_xisf(f), "is_xisf should detect the synthetic XISF"
        S.set_filter_any(f, "LPro", apply=True)   # dispatch should pick XISF path
        with open(f, "rb") as fh:
            blob = fh.read()
        _, xml = S._xisf_header(blob)
        assert S._xisf_data_start(xml) == ds, "data offset moved!"
        print("  set_filter_any dispatches XISF; data offset preserved ✓")


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
