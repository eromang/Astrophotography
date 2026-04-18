# scripts/

Utility scripts that generate charts and atlases for the vault. Run from the repo root.

## fov_atlas.py — RedCat 51 FOV atlas

Mollweide all-sky PNG showing a RedCat 51 frame (5.4° × 3.6°) at each catalogued target. Blue = balcony-reachable, red = blocked (Dec > 55° or too-high transit).

```bash
python3 -m pip install matplotlib numpy pyyaml
python3 scripts/fov_atlas.py
```

Output: `03_Techniques/images/fov-atlas-allsky.png`. Embedded in [[../03_Techniques/FOV-Atlas.md]].

### Extending the target list

- **Inline:** append a row to `CATALOG` in `fov_atlas.py`.
- **From vault:** add `ra_deg`, `dec_deg`, `size_arcmin` to a target's YAML frontmatter under `02_Targets/` — the script picks it up on the next run (vault entries win over the inline catalog when names match).
