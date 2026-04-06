---
title: "Session-Plan Command — Usage Guide"
type: documentation
version: "1.3"
related:
  - "[[session-plan]]"
tags:
  - documentation
  - sessions
---

# `/session-plan` — Usage Guide

User-facing documentation for the session-plan command (also aliased as `/sp`).

The full command specification lives in [`session-plan.md`](session-plan.md). This file is the **quick reference** — what the user types, what they get back, and when to use each option.

---

## Quick Reference

```
/session-plan <date> [--stellarium] [--location <preset>]
/sp <date> [-s] [-l <preset>]
```

| Argument | Required? | Description |
|----------|-----------|-------------|
| `<date>` | Yes | Date expression — see [Date Formats](#date-formats) |
| `--stellarium` / `-s` | No | Enable Stellarium API integration (alt cross-check + finder charts) |
| `--location <preset>` / `-l <preset>` | No | Use a named location preset (defaults to last-used, then `balcony`) |

---

## Date Formats

| Input | Resolves to |
|-------|-------------|
| `tonight`, `today` | Current date |
| `tomorrow` | Next day |
| `2026-06-14` | Specific ISO date |
| `next friday`, `saturday` | Next occurrence of that weekday |

---

## Location Presets

Two presets are configured. The active location is resolved in this order:

1. `--location <name>` flag, if provided
2. Last-used location (read from `06_Metadata/Agents/Claude/state/session-plan-state.json`)
3. The location marked `default: true` in the config (currently `balcony`)

After every successful run, the resolved location is saved to the state file so the next call defaults to it.

### `balcony` (default)

| | |
|---|---|
| **Site** | Tuntange Balcony |
| **Coordinates** | 49.71731, 6.00823 |
| **Altitude** | 317 m |
| **Bortle** | 4 (SQM 20.59) |
| **Horizon** | Constrained: az 135°–225° (SE–SW), alt > 10° |
| **Setup time** | 15 min |
| **Power** | Mains |
| **Use when** | Default for most sessions. South-facing targets only. |

### `schwebach`

| | |
|---|---|
| **Site** | Schwebach Forest Edge |
| **Coordinates** | 49.745, 5.945 |
| **Altitude** | 296 m |
| **Bortle** | 4 (SQM 20.81) — 25% darker than balcony |
| **Horizon** | Open clearings (alt > 15°, find a true clearing) |
| **Setup time** | 25 min |
| **Power** | [[Jackery-Explorer-500]] |
| **Use when** | Quick portable session, need open horizon for high-Dec targets, only 12 min from home |

### `wahl` ⭐ (recommended for routine portable)

| | |
|---|---|
| **Site** | Plateau de Wahl |
| **Coordinates** | 49.840, 5.918 |
| **Altitude** | 449 m |
| **Bortle** | 4 (SQM 21.10) — 52% darker than balcony |
| **Horizon** | Open: full 360°, alt > 10° |
| **Setup time** | 45 min |
| **Power** | [[Jackery-Explorer-500]] |
| **Use when** | **Best value dark site**. ~30 min drive for ×1.44 SNR vs balcony. Routine portable choice. |

### `hoscheid`

| | |
|---|---|
| **Site** | Plateau de Hoscheid |
| **Coordinates** | 49.967, 6.080 |
| **Altitude** | 452 m |
| **Bortle** | 4 (SQM 21.23) — 61% darker than balcony, just shy of Bortle 3 |
| **Horizon** | Open: full 360°, alt > 10° |
| **Setup time** | 45 min |
| **Power** | [[Jackery-Explorer-500]] |
| **Use when** | Maximum darkness within reach. Faint reflection nebulae, Sh2-240 Simeis 147, faint galaxies. The extra 15 min vs Wahl is worth it for ×1.6 SNR projects. |

---

## Common Workflows

### 1. Plan tonight's session at the balcony (simplest)

```
/session-plan tonight
```

- Uses last-used location (or balcony on first run)
- Skips Stellarium integration
- Output: text plan + session file in `05_Sessions/{year}/`

### 2. Plan tomorrow with Stellarium verification

```
/session-plan tomorrow --stellarium
```

Same as above, plus:
- Cross-checks all target altitudes against the Stellarium API
- Captures a finder chart per target (saved to `05_Sessions/{year}/Finder-Charts/`)
- Embeds the charts in the session file

**Pre-requisite:** Stellarium must be running with the Remote Control plugin enabled (F2 → Plugins → Remote Control → Configure → Server enabled).

### 3. Plan a Wahl portable session

```
/session-plan saturday --location wahl --stellarium
```

- Switches to the Plateau de Wahl preset (best value dark site)
- Persists `wahl` as the new last-used location
- All subsequent calls (without `--location`) default to Wahl until you switch back
- Adds Jackery power budget warning to the output

### 4. Switch back to balcony

```
/session-plan tonight --location balcony
```

Sets balcony as last-used. Subsequent calls default to balcony again.

### 5. Plan a future campaign night

```
/session-plan 2026-06-14 -s
```

Useful for the [[M16-Campaign-2026]], [[Cygnus-Campaign-2026]], etc. Generates a full session file with the planned target, capture settings, and finder chart that you can review weeks in advance.

> Weather forecast may be unreliable beyond ~7 days out. The command will warn but proceed.

---

## Output

The command produces three things:

### 1. In-conversation summary

- Resolved location (with mismatch warnings if clearoutside differs from preset)
- Twilight times in CEST/CET
- Moon phase and illumination
- Weather verdict (clear / partly cloudy / cloudy hours)
- Selected targets with planning table
- ASCII altitude chart through the night
- Stellarium cross-check table (if `-s` used)
- Concerns and recommendations

### 2. Session file

Written to `05_Sessions/{year}/{date}-Capture.md` with this structure:

```yaml
---
title: "{date} Capture Session"
type: capture-session
date: {date}
location: "{LOC_NAME}"
location_preset: "{location_id}"
location_coords: "{lat}, {lon}"
location_altitude_m: {alt}
bortle: {bortle}
power_source: "{mains|jackery}"
twilight_evening: "{HH:MM}"
twilight_morning: "{HH:MM}"
moon_phase: "..."
moon_illumination: "..."
equipment:
  camera: "[[ASI2600MCPro]]"
  ...
targets:
  - "[[...]]"
tags:
  - session/capture
---
```

Body sections:
- Conditions
- Location (with site details, horizon type, power source)
- Planning table (object × time × exposure × frames × filter)
- Stellarium cross-check (if `-s` used)
- Finder Charts (if `-s` used)
- Calibration checklist
- Notes

### 3. Finder charts (only with `--stellarium`)

PNG files saved to `05_Sessions/{year}/Finder-Charts/{date}-{target}-finder.png`. One per target, captured at peak altitude time, with FOV set to the [[RedCat-51]] field of view (5.4°).

---

## Behavior Details

### Location resolution and persistence

```
parse_args():
    if "--location <X>" in args:
        active = X
    elif state_file exists and last_location is valid:
        active = state.last_location
    else:
        active = locations[default == true]

after_session():
    write state_file with last_location = active
```

The state file is **gitignored** (`06_Metadata/Agents/Claude/state/`) so it's purely local — won't pollute commits or sync across machines.

### Bortle auto-verification (clearoutside.com)

After binding the location, the command fetches the current Bortle/SQM from clearoutside.com:

| Outcome | Action |
|---------|--------|
| Match (within ±1 class) | Use stored value, no message |
| Live differs by ≥1 class | Warn, use live value, suggest preset update |
| API failure | Fall back to stored preset value |

This catches drift if the underlying light pollution data is updated, or if a preset was misconfigured.

### Horizon-aware visibility

Constrained horizon (`balcony`):
- Targets must be in az 135°–225° during the dark window
- High-Dec targets (>55°) likely rejected (brief south window)

Open horizon (`quatre-vents`):
- Full 360° azimuth — high-Dec targets unlocked
- Heart/Soul, IC 1396, M81/M82, Double Cluster become viable

### Stellarium integration (with `-s`)

1. Probe API at `http://localhost:8090/api/main/status` — fall back gracefully if unreachable
2. Save Stellarium's current time and FOV
3. For each target: set time → focus → wait 1 second → read alt/az → cross-check with internal calculation
4. Set FOV to 5.4° → trigger screenshot → move PNG to `Finder-Charts/`
5. Restore time to "now" and FOV to original

If the API fails mid-loop, that single target is skipped but the rest continue. The session file notes which targets are missing finder charts.

---

## Pre-Flight Checklist

Before running with `--stellarium`:

- [ ] Stellarium is running
- [ ] Remote Control plugin enabled (F2 → Plugins → Remote Control)
- [ ] Server enabled in plugin config (port 8090 default)
- [ ] Stellarium location matches the active preset (use API: `POST /api/location/setlocationfields`)

Before running with `--location quatre-vents`:

- [ ] Jackery Explorer 500 is charged to ≥80% (see [[Jackery-Explorer-500]] for runtime estimates)
- [ ] Transport rig is ready (mount, scope, camera, cables, polar align tools)
- [ ] You have ~45 min for setup at the site
- [ ] Site is accessible at planned departure time

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| "Unknown location preset 'X'" | Typo or undefined preset | List valid presets, fix or add to `locations:` config |
| "Stellarium API unreachable" | Plugin not loaded or wrong port | Enable Remote Control plugin, restart Stellarium |
| Wrong altitudes in cross-check | Stellarium location ≠ preset | Push location via `POST /api/location/setlocationfields` (see session-plan.md Step 5d) |
| Finder chart missing for one target | Screenshot timeout or focus lag | Re-run with `-s` — single failures don't abort the workflow |
| "No suitable targets visible" | Off-season or moon too bright | Check [[Seasonal-Calendar]], try a different date or wait for new moon |
| Bortle mismatch warning | clearoutside has updated data | Update the preset's `bortle:` value in `session-plan.md` |
| State file corrupted | Manual edit or partial write | Delete `06_Metadata/Agents/Claude/state/session-plan-state.json` — first run will recreate with defaults |

---

## Examples by Scenario

### M16 campaign session

```
/session-plan 2026-06-14 -s
```

Quad Band, balcony (default), with Stellarium cross-check. Generates the M16 session for the new moon Saturday in June.

### NGC 7000 from Wahl (dark site portable)

```
/session-plan 2026-09-12 -l wahl -s
```

Switches to Plateau de Wahl (last-used persists), narrowband filter selected for emission targets, finder charts captured. Wahl gives ×1.44 SNR vs balcony — significantly improves NGC 7000 outer faint nebulosity. Note: Jackery power budget for September is tight (~10h available, ~9h needed) — see [[Jackery-Explorer-500#Verdict by Season|verdict]].

### Faint reflection nebula at Hoscheid (maximum darkness)

```
/session-plan 2026-08-09 -l hoscheid -s
```

For projects where you need the absolute darkest sky within reach (e.g., M78 reflection nebula, Iris Nebula, faint dust around bright stars). Hoscheid gives ×1.6 SNR vs balcony.

### Quick "should I shoot tonight?" check

```
/sp tonight
```

Bare minimum — no Stellarium, just visibility + weather + targets.

### Test the integration without committing to a session

```
/session-plan 2026-12-25 -s -l quatre-vents
```

Plans Christmas night at Quatre-Vents with Stellarium. The session file is written but you can delete it after reviewing.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-04 | Initial version — date parsing, twilight, weather, target selection |
| 1.1 | 2026-04-06 | Added `--stellarium` flag (cross-check + finder charts) |
| 1.2 | 2026-04-06 | Added `--location` flag, location presets, last-used persistence |
| 1.3 | 2026-04-06 | Added clearoutside.com Bortle/SQM auto-verification |
| 1.4 | 2026-04-06 | Verified 12 candidate locations, added `schwebach`/`wahl`/`hoscheid` presets, removed `quatre-vents` (was Bortle 5) |

---

## Related Documentation

- [`session-plan.md`](session-plan.md) — Full command specification
- [[Seasonal-Calendar]] — Monthly target calendar
- [[SNR]] — Signal-to-noise reference for integration planning
- [[Jackery-Explorer-500]] — Power budget for portable sessions
- [[Master-Library]] — Calibration frame inventory
- [[Session-Context]] — Quick vault overview for new sessions
