#!/usr/bin/env python3
"""set_filter.py — write the filter into raw frames / masters before WBPP.

Manual filters (no EFW) → the ASIAIR never records the filter in frame
metadata; it only puts it in the FILENAME (…-9.6C_LPro_0001.fit). The empty
filter is why WBPP can't auto-match filter-specific flats and names masters
NoFilter.

This reads the filter from the filename (or --filter) and writes it:
  * FITS  (.fit/.fits) — into the FITS `FILTER` header keyword.
  * XISF  (.xisf)      — into the native `Instrument:Filter:Name` PROPERTY,
                         which is what WBPP groups by for .xisf masters (it
                         ignores the FITS keyword there). The FITS `FILTER`
                         keyword is updated too, for consistency.

Data-preserving: the pixel / attachment data is never touched — verified by an
unchanged data-block MD5 on every write. Stdlib only.

    python3 scripts/set_filter.py <file-or-folder> [--filter LPro] [--apply] [--recursive]

Default is a DRY RUN (prints planned changes, writes nothing). Darks / bias /
dark-flats have no filename token and are skipped (they are filter-independent).
See scripts/README.md.
"""
from __future__ import annotations
import argparse
import hashlib
import os
import re
import struct
import sys

BLOCK = 2880
CARD = 80
# raw-frame token between the temperature and the index: …_-9.6C_LPro_0001.fit
_TOKEN = re.compile(
    r"_-?\d+(?:\.\d+)?C_([A-Za-z][\w]*)_\d+\.(?:fit|fits|fts|xisf)$", re.IGNORECASE)
# master token (WBPP-built masters): …_FILTER-LPro_…
_MASTER_TOKEN = re.compile(r"FILTER-([A-Za-z][A-Za-z0-9]*)", re.IGNORECASE)

XISF_SIG = b"XISF0100"


def filter_from_name(path: str):
    base = os.path.basename(path)
    m = _TOKEN.search(base)
    if m:
        return m.group(1)
    m = _MASTER_TOKEN.search(base)
    if m:
        return m.group(1)
    return None


# ---------------------------------------------------------------------------
# FITS (.fit/.fits) — write the FILTER header keyword
# ---------------------------------------------------------------------------
def _read_header_cards(fh):
    """Return (list_of_80-byte_cards_up_to_END, header_byte_length)."""
    cards = []
    nbytes = 0
    while True:
        block = fh.read(BLOCK)
        if len(block) < BLOCK:
            raise ValueError("truncated FITS header")
        nbytes += BLOCK
        done = False
        for i in range(0, BLOCK, CARD):
            c = block[i:i + CARD]
            if c[:8].rstrip() == b"END":
                done = True
                break
            cards.append(c)
        if done:
            break
        if nbytes > 64 * BLOCK:
            raise ValueError("no END card found (not a FITS header?)")
    return cards, nbytes


def _filter_card(value: str) -> bytes:
    """Build an 80-byte FITS string-valued FILTER card."""
    v = value[:60]
    if len(v) < 8:
        v = v + " " * (8 - len(v))      # FITS string values are >= 8 chars
    card = f"FILTER  = '{v}'"
    card = (card + " " * (CARD - len(card)))[:CARD]
    # add a comment if there's room
    if len(card.rstrip()) <= 47:
        card = card[:33] + "/ Filter name".ljust(CARD - 33)
    return card[:CARD].encode("latin-1")


def current_filter(cards):
    for c in cards:
        if c[:8].rstrip() == b"FILTER":
            txt = c.decode("latin-1")
            m = re.search(r"=\s*'([^']*)'", txt)
            return (m.group(1).strip() if m else "")
    return None


def set_filter_file(path: str, target: str, apply: bool):
    """FITS path. Only the header is rewritten when room exists."""
    with open(path, "rb") as fh:
        cards, hdr_bytes = _read_header_cards(fh)
    cur = current_filter(cards)
    if cur == target:
        return f"already {target}"
    # build new card list (replace existing FILTER or insert)
    new_cards = [c for c in cards if c[:8].rstrip() != b"FILTER"]
    new_cards.append(_filter_card(target))
    slots = hdr_bytes // CARD                 # total card slots in current header
    needed = len(new_cards) + 1               # + END
    if not apply:
        return (f"DRY set FILTER={target}" + (f" (was '{cur}')" if cur is not None else " (was absent)"))
    if needed <= slots:
        # data-preserving: overwrite only the header region
        body = b"".join(new_cards) + b"END".ljust(CARD)
        body += b" " * (hdr_bytes - len(body))
        assert len(body) == hdr_bytes
        with open(path, "r+b") as fh:
            fh.seek(0)
            fh.write(body)
        return f"set FILTER={target} (header-only)"
    # fallback: header block full -> full rewrite (header + data)
    with open(path, "rb") as fh:
        fh.seek(hdr_bytes)
        data = fh.read()
    nblocks = (needed * CARD + BLOCK - 1) // BLOCK
    body = b"".join(new_cards) + b"END".ljust(CARD)
    body += b" " * (nblocks * BLOCK - len(body))
    tmp = path + ".tmp"
    with open(tmp, "wb") as fh:
        fh.write(body)
        fh.write(data)
    os.replace(tmp, path)
    return f"set FILTER={target} (full rewrite)"


# ---------------------------------------------------------------------------
# XISF (.xisf) — write the Instrument:Filter:Name property (+ FITS keyword)
# ---------------------------------------------------------------------------
# matches the whole property element, self-closing or with content
_XISF_FILTER_PROP = re.compile(
    r'<Property\s+id="Instrument:Filter:Name".*?(?:/>|</Property>)', re.DOTALL)


def is_xisf(path: str) -> bool:
    try:
        with open(path, "rb") as fh:
            return fh.read(8) == XISF_SIG
    except OSError:
        return False


def _xisf_header(blob: bytes):
    if blob[:8] != XISF_SIG:
        raise ValueError("not a monolithic XISF (bad signature)")
    hlen = struct.unpack("<I", blob[8:12])[0]
    return hlen, blob[16:16 + hlen].decode("utf-8")


def _xisf_data_start(xml: str) -> int:
    offs = [int(m) for m in re.findall(r'location="attachment:(\d+):\d+"', xml)]
    if not offs:
        raise ValueError("no attached data blocks (compressed/embedded XISF unsupported)")
    return min(offs)


def xisf_current_filter(xml: str):
    m = _XISF_FILTER_PROP.search(xml)
    if not m:
        return None
    elem = m.group(0)
    mc = re.search(r'>([^<]*)</Property>', elem)   # text-content form
    if mc:
        return mc.group(1).strip()
    mv = re.search(r'\bvalue="([^"]*)"', elem)      # value-attribute form
    if mv:
        return mv.group(1).strip()
    return ""                                       # self-closing, empty


def _set_filter_in_xml(xml: str, target: str) -> str:
    new_elem = ('<Property id="Instrument:Filter:Name" type="String">'
                f'{target}</Property>')
    new, n = _XISF_FILTER_PROP.subn(lambda _m: new_elem, xml)
    if n > 1:
        raise ValueError("multiple Instrument:Filter:Name properties")
    if n == 0:
        # property absent (older masters) -> insert as first child of <Image>
        m = re.search(r'<Image\b[^>]*>', xml)
        if not m:
            raise ValueError("no <Image> element found to host the filter property")
        if m.group(0).rstrip().endswith("/>"):
            raise ValueError("<Image> is self-closing; cannot insert a child property")
        new = xml[:m.end()] + new_elem + xml[m.end():]
    # keep the FITS FILTER keyword consistent if present (FITS style, >= 8 chars)
    fits_val = target if len(target) >= 8 else target.ljust(8)
    new = re.sub(
        r'(<FITSKeyword name="FILTER" value=)"[^"]*"',
        lambda m: f"{m.group(1)}\"'{fits_val}'\"",
        new)
    return new


def set_filter_xisf(path: str, target: str, apply: bool):
    """Set the XISF filter property. Data block stays byte-identical.

    The header XML is rewritten and the header-length field updated; the data
    block is kept at its original (alignment-padded) absolute offset, so the
    pixel data is never moved or touched.
    """
    with open(path, "rb") as fh:
        blob = fh.read()
    hlen, xml = _xisf_header(blob)
    data_start = _xisf_data_start(xml)
    cur = xisf_current_filter(xml)
    if cur == target:
        return f"already {target}"
    new_xml = _set_filter_in_xml(xml, target).encode("utf-8")
    new_hlen = len(new_xml)
    if 16 + new_hlen > data_start:
        raise ValueError(
            f"edited header ({16 + new_hlen} B) would overrun the data block at {data_start}")
    if not apply:
        return (f"DRY set FILTER={target}" +
                (f" (was '{cur}')" if cur is not None else " (property absent)"))
    md5_before = hashlib.md5(blob[data_start:]).hexdigest()
    out = bytearray()
    out += XISF_SIG
    out += struct.pack("<I", new_hlen)
    out += blob[12:16]                               # reserved bytes, preserved
    out += new_xml
    out += b"\x00" * (data_start - 16 - new_hlen)    # re-pad so data stays put
    out += blob[data_start:]                         # data block — byte-identical
    if hashlib.md5(bytes(out[data_start:])).hexdigest() != md5_before:
        raise RuntimeError("data block changed — aborting without writing")
    tmp = path + ".tmp"
    with open(tmp, "wb") as fh:
        fh.write(out)
    os.replace(tmp, path)
    how = "inserted" if cur is None else "property"
    return f"set FILTER={target} (XISF {how})"


def set_filter_any(path: str, target: str, apply: bool):
    """Dispatch on file type (XISF vs FITS)."""
    if is_xisf(path):
        return set_filter_xisf(path, target, apply)
    return set_filter_file(path, target, apply)


def iter_frames(target, recursive):
    if os.path.isfile(target):
        yield target
        return
    walker = os.walk(target) if recursive else [(target, [], os.listdir(target))]
    for root, _dirs, files in walker:
        for f in sorted(files):
            if f.lower().endswith((".fit", ".fits", ".fts", ".xisf")) and not f.startswith("._"):
                yield os.path.join(root, f)


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Write the filter (FITS keyword for .fit, XISF property for .xisf) from the filename or --filter.")
    ap.add_argument("path", help="a .fit/.xisf file or a folder of frames")
    ap.add_argument("--filter", help="force this filter value (else auto-detect from filename)")
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry run)")
    ap.add_argument("--recursive", action="store_true", help="recurse into subfolders")
    args = ap.parse_args(argv)

    n_set = n_skip = n_same = 0
    for p in iter_frames(args.path, args.recursive):
        target = args.filter or filter_from_name(p)
        name = os.path.basename(p)
        if not target:
            print(f"  skip   {name}  (no filter in name; use --filter)")
            n_skip += 1
            continue
        try:
            status = set_filter_any(p, target, args.apply)
        except (ValueError, RuntimeError) as e:
            print(f"  ERROR  {name}: {e}")
            n_skip += 1
            continue
        print(f"  {status:30} {name}")
        if status.startswith("already"):
            n_same += 1
        else:
            n_set += 1
    mode = "APPLIED" if args.apply else "DRY RUN (use --apply to write)"
    print(f"\n{mode}: {n_set} to set, {n_same} already correct, {n_skip} skipped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
