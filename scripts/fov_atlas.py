#!/usr/bin/env python3
"""
FOV Atlas — RedCat 51 FOV (5.4° × 3.6°) drawn on the full sky.

Output: 03_Techniques/images/fov-atlas-allsky.png  (Mollweide projection)

Blue rectangles  = balcony-reachable (Dec < 55° AND transit altitude > 10°).
Red  rectangles  = blocked from the Tuntange south-facing balcony.

Requirements:
    python3 -m pip install matplotlib numpy pyyaml

Run from the repo root:
    python3 scripts/fov_atlas.py
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

LAT_DEG = 49.71731
FOV_W_DEG = 5.4
FOV_H_DEG = 3.6
DEC_NORTH_LIMIT = 55.0

# (name, RA deg, Dec deg, size arcmin). Extend inline, or add ra_deg/dec_deg to
# a target's frontmatter under 02_Targets/ and it will be merged in automatically.
CATALOG: list[tuple[str, float, float, float]] = [
    ("M42 Orion",             83.82,  -5.39,  85),
    ("M45 Pleiades",          56.75,  24.12, 110),
    ("NGC 2244 Rosette",      97.98,   4.93,  80),
    ("IC 443 Jellyfish",      94.35,  22.57,  50),
    ("NGC 2264 Cone",        100.27,   9.87,  60),
    ("NGC 1499 California",   60.38,  36.40, 145),
    ("Sh2-240 Simeis 147",    84.50,  28.00, 180),
    ("M44 Beehive",          130.10,  19.67,  95),
    ("Mel 111 Coma",         186.00,  26.00, 275),
    ("M16 Eagle",            274.70, -13.78,  35),
    ("M17 Omega",            275.20, -16.18,  46),
    ("NGC 6888 Crescent",    303.00,  38.35,  18),
    ("NGC 6960 W Veil",      311.12,  30.72,  70),
    ("NGC 6992 E Veil",      313.18,  31.72,  60),
    ("NGC 7000 N. America",  314.75,  44.52, 120),
    ("IC 5070 Pelican",      312.68,  44.35,  60),
    ("M31 Andromeda",         10.68,  41.27, 178),
    ("M33 Triangulum",        23.46,  30.66,  73),
    ("NGC 869/884 Double",    35.60,  57.13,  60),
    ("IC 1805 Heart",         38.18,  61.47, 100),
    ("IC 1848 Soul",          44.90,  60.44,  60),
    ("IC 1396 Elephant",     325.10,  57.50, 170),
    ("Sh2-129 Flying Bat",   327.50,  60.50,  90),
    ("M81 Ursa Major",       148.88,  69.07,  26),
    ("M82 Cigar",            148.97,  69.68,  11),
]


@dataclass
class Target:
    name: str
    ra_deg: float
    dec_deg: float
    size_arcmin: float

    @property
    def reachable(self) -> bool:
        transit_alt = 90 - abs(LAT_DEG - self.dec_deg)
        return transit_alt > 10 and self.dec_deg < DEC_NORTH_LIMIT


def load_from_vault(targets_dir: Path) -> list[Target]:
    try:
        import yaml
    except ImportError:
        return []
    found: list[Target] = []
    for md in targets_dir.rglob("*.md"):
        text = md.read_text(encoding="utf-8")
        if not text.startswith("---"):
            continue
        try:
            fm = yaml.safe_load(text.split("---", 2)[1])
        except yaml.YAMLError:
            continue
        if not fm or "ra_deg" not in fm or "dec_deg" not in fm:
            continue
        found.append(Target(
            name=str(fm.get("title", md.stem)),
            ra_deg=float(fm["ra_deg"]),
            dec_deg=float(fm["dec_deg"]),
            size_arcmin=float(fm.get("size_arcmin", 0)),
        ))
    return found


def collect_targets(repo_root: Path) -> list[Target]:
    from_vault = load_from_vault(repo_root / "02_Targets")
    seen = {t.name.lower() for t in from_vault}
    merged = list(from_vault)
    for name, ra, dec, sz in CATALOG:
        if name.lower() not in seen:
            merged.append(Target(name, ra, dec, sz))
    return merged


def draw_fov(ax, t: Target) -> None:
    ra_rad = np.deg2rad(-((t.ra_deg + 180) % 360 - 180))
    dec_rad = np.deg2rad(t.dec_deg)
    w = np.deg2rad(FOV_W_DEG)
    h = np.deg2rad(FOV_H_DEG)
    col = "#4d9eff" if t.reachable else "#ff6b6b"
    ax.add_patch(plt.Rectangle(
        (ra_rad - w / 2, dec_rad - h / 2), w, h,
        fill=False, edgecolor=col, linewidth=1.0, alpha=0.95,
    ))
    ax.text(
        ra_rad, dec_rad + h / 2 + np.deg2rad(2),
        t.name, fontsize=5.5, ha="center", va="bottom", color=col,
    )


def plot_allsky(targets: list[Target], out: Path) -> None:
    fig, ax = plt.subplots(
        subplot_kw={"projection": "mollweide"},
        figsize=(14, 8), facecolor="black",
    )
    ax.set_facecolor("black")
    ax.grid(True, color="0.25", linewidth=0.4)
    ax.tick_params(colors="#aaa")
    for t in targets:
        draw_fov(ax, t)
    ax.set_title(
        "RedCat 51 FOV atlas — blue = balcony-reachable, red = blocked (Dec > 55°)",
        color="white", fontsize=11, pad=18,
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor="black")
    plt.close(fig)
    print(f"wrote {out}")


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parent.parent
    targets = collect_targets(repo_root)
    print(f"plotting {len(targets)} targets")
    plot_allsky(targets, repo_root / "03_Techniques" / "images" / "fov-atlas-allsky.png")
