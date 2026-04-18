---
title: "FOV Atlas"
type: technique
tags:
  - technique
---

# FOV Atlas — RedCat 51 on the Full Sky

Two complementary ways to answer *"does this DSO fit the [[RedCat-51]] FOV, and is it reachable from the balcony?"* The static atlas is for yearly planning; Stellarium is for candidate vetting on a real sky background.

---

## Static all-sky atlas (matplotlib)

![[fov-atlas-allsky.png]]

*Mollweide projection. Each rectangle = one RedCat 51 frame (5.4° × 3.6°) at the target's J2000 coordinates. **Blue** = balcony-reachable (Dec < 55° AND transit altitude > 10°). **Red** = blocked from Tuntange's south-facing balcony (120°–302° azimuth window, see [[Dark-Sky-Sites]]).*

Regenerate after adding or moving targets:

```bash
python3 scripts/fov_atlas.py
```

Source + catalog: `scripts/fov_atlas.py`. Extend via the inline `CATALOG` list or by adding `ra_deg` / `dec_deg` / `size_arcmin` to any `02_Targets/*.md` frontmatter.

---

## Per-target framing (Stellarium Oculars)

For candidate vetting on an unfamiliar target with an authentic sky background.

**One-time setup** — Stellarium → F2 → Oculars → configure:
- Telescope: `RedCat 51` (250 mm focal length, 51 mm aperture)
- Sensor: `ASI2600MC Pro` (23.5 × 15.7 mm, 6248 × 4176 px, 3.76 µm pixels)

**Per-target check:**
1. `F3` → search the target → Stellarium centres on it
2. `Ctrl-B` toggles the sensor frame — the exact RedCat 51 rectangle overlays the live sky
3. Read star density, neighbouring DSOs, framing margins

**Session-driven capture** — `/session-plan --stellarium {date}` already captures per-target finder charts at 5.4° FOV into `05_Sessions/{year}/Finder-Charts/`. Those are the RedCat framing rendered over DSS imagery at the planned observation time.

---

## When to use which

| Need | Use |
|---|---|
| Yearly planning — what fits, what's blocked across all seasons | Atlas PNG |
| Vetting an unfamiliar candidate — real sky, star density, neighbours | Stellarium Oculars (Ctrl-B) |
| Logged with a specific session plan | `/session-plan --stellarium` finder chart |

## Related

- [[Seasonal-Calendar]] — which targets are worth plotting this month
- [[Campaign-Timeline]] — when each target was actually captured
- [[Integration-Budget]] — how many hours each target has already
- [[RedCat-51]] — the scope driving this FOV
- [[Dark-Sky-Sites]] — the balcony horizon profile used for reachability
