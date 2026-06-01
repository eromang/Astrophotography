#!/usr/bin/env python3
"""set_filter.py — write the FITS FILTER keyword into raw frames before WBPP.

Manual filters (no EFW) → the ASIAIR never writes the FITS FILTER keyword; it
only puts the filter in the FILENAME (…-9.6C_LPro_0001.fit). The empty keyword
is why WBPP can't auto-match filter-specific flats and names masters
FILTER-NoFilter. This reads the filter from the filename (or --filter) and
writes it into each frame's header.

Data-preserving: when the header has a free card slot (the normal case) only the
header region is rewritten — the pixel data is never touched. Stdlib only.

    python3 scripts/set_filter.py <file-or-folder> [--filter LPro] [--apply] [--recursive]

Default is a DRY RUN (prints planned changes, writes nothing). Add --apply to
write. Darks/bias/dark-flats have no filename token and are skipped (they are
filter-independent). See scripts/README.md.
"""
from __future__ import annotations
import argparse
import os
import re
import sys

BLOCK = 2880
CARD = 80
# filename token between the temperature and the index: …_-9.6C_LPro_0001.fit
_TOKEN = re.compile(r"_-?\d+(?:\.\d+)?C_([A-Za-z][\w]*)_\d+\.fit$", re.IGNORECASE)


def filter_from_name(path: str):
    m = _TOKEN.search(os.path.basename(path))
    return m.group(1) if m else None


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
    """Returns a status string. Only the header is rewritten when room exists."""
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


def iter_fits(target, recursive):
    if os.path.isfile(target):
        yield target
        return
    walker = os.walk(target) if recursive else [(target, [], os.listdir(target))]
    for root, _dirs, files in walker:
        for f in sorted(files):
            if f.lower().endswith((".fit", ".fits", ".fts")) and not f.startswith("._"):
                yield os.path.join(root, f)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Write the FITS FILTER keyword from the filename (or --filter).")
    ap.add_argument("path", help="a .fit file or a folder of frames")
    ap.add_argument("--filter", help="force this filter value (else auto-detect from filename)")
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry run)")
    ap.add_argument("--recursive", action="store_true", help="recurse into subfolders")
    args = ap.parse_args(argv)

    n_set = n_skip = n_same = 0
    for p in iter_fits(args.path, args.recursive):
        target = args.filter or filter_from_name(p)
        name = os.path.basename(p)
        if not target:
            print(f"  skip   {name}  (no filter in name; use --filter)")
            n_skip += 1
            continue
        try:
            status = set_filter_file(p, target, args.apply)
        except ValueError as e:
            print(f"  ERROR  {name}: {e}")
            n_skip += 1
            continue
        print(f"  {status:28} {name}")
        if status.startswith("already"):
            n_same += 1
        else:
            n_set += 1
    mode = "APPLIED" if args.apply else "DRY RUN (use --apply to write)"
    print(f"\n{mode}: {n_set} to set, {n_same} already correct, {n_skip} skipped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
