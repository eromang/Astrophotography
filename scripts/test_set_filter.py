#!/usr/bin/env python3
"""Tests for set_filter.py — correctness + the critical data-preserving guarantee.

Run from repo root:  python3 scripts/test_set_filter.py
Stdlib only.
"""
import hashlib
import os
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
