---
name: session-plan
description: "Plan an astrophotography capture session for a given date"
shortcut: sp
category: sessions
version: "1.5"
argument-hint: "<date> [--stellarium] [--location <preset>] (e.g., tonight, tomorrow --stellarium --location burfelt)"
allowed-tools: WebFetch, Read, Write, Glob, Bash(date:*), Bash(python3:*), Bash(curl:*), Bash(mv:*), Bash(rm:*), Bash(mkdir:*), Bash(ls:*), Bash(find:*), Bash(cat:*)
---

# Session Planner

Plan an astrophotography capture session by fetching real astronomical and weather data, reading vault context, and generating a session file.

---

## Input

A date expression, optionally followed by flags:

- `tonight`, `today` → current date
- `tomorrow` → next day
- `YYYY-MM-DD` → specific date
- `next friday`, `saturday` → resolve to next occurrence
- `--stellarium` / `-s` → enable Stellarium API integration (cross-check altitudes + capture finder charts)
- `--location <preset>` / `-l <preset>` → use a named location preset (`balcony`, `schwebach`, `wahl`, `hoscheid`)

Examples:
- `/session-plan tonight`
- `/session-plan tomorrow --stellarium`
- `/session-plan 2026-06-12 -s --location wahl`
- `/session-plan saturday -l hoscheid -s`

If `--location` is omitted, the command uses the **last-used location** (persisted in state file). If no state exists, falls back to the location marked `default: true` in the config (currently `balcony`).

---

## Configuration (Fixed)

```yaml
# State persistence file (last-used location, etc.)
state_file: "06_Metadata/Agents/Claude/state/session-plan-state.json"

# Location presets — selectable via --location flag
locations:
  balcony:
    name: "Tuntange Balcony"
    latitude: 49.71731
    longitude: 6.00823
    altitude_m: 317
    bortle: 4               # verified via clearoutside.com 2026-04-06
    sqm: 20.59              # mag/arcsec² (from clearoutside)
    artificial_mcd: 0.455   # μcd/m² (from clearoutside)
    timezone: "Europe/Luxembourg"
    horizon:
      type: "constrained"
      azimuth_min: 135   # SE
      azimuth_max: 225   # SW
      altitude_min: 10
    setup_time_min: 15
    teardown_time_min: 15
    power_source: "mains"
    notes: "South-facing balcony, SE-SW window, mains power available"
    default: true

  schwebach:
    name: "Schwebach Forest Edge"
    latitude: 49.745
    longitude: 5.945
    altitude_m: 296         # Open-Elevation API verified
    bortle: 4               # verified via clearoutside.com 2026-04-06
    sqm: 20.81              # mag/arcsec² — best close site
    artificial_mcd: 0.340   # 339.95 μcd/m²
    timezone: "Europe/Luxembourg"
    horizon:
      type: "open"
      altitude_min: 15      # forest clearings — slight elevation needed to clear treeline
    setup_time_min: 25
    teardown_time_min: 20
    power_source: "jackery"
    notes: "Best CLOSE portable site (12 min drive). 25% darker than balcony (SQM 20.81 vs 20.59). Forest clearings — scout in daytime to find an actual open clearing with horizon clearance. Replaces the previous Quatre-Vents preset which was Bortle 5 (worse than balcony)."

  wahl:
    name: "Plateau de Wahl (Groussbus-Wal)"
    latitude: 49.840
    longitude: 5.918
    altitude_m: 449         # Open-Elevation API verified
    bortle: 4               # verified via clearoutside.com 2026-04-06 — top of Bortle 4 range
    sqm: 21.10              # mag/arcsec²
    artificial_mcd: 0.221   # 220.6 μcd/m²
    timezone: "Europe/Luxembourg"
    horizon:
      type: "open"
      altitude_min: 15      # forest patches E and S add ~10-15° obstruction in those quadrants — refine after first visit
    setup_time_min: 45
    teardown_time_min: 30
    power_source: "jackery"
    notes: |
      BEST VALUE dark site (30 min drive, 52% less LP than balcony, SQM 21.10).
      Located between Grosbous and Wahl villages — Plus Code: RWR9+262 Groussbus-Wal.
      Open agricultural plateau ~449m, large open area extending N/NE.
      CAVEAT: small Kinigshaff hamlet ~300-500m W (~15-20 houses) — partial forest buffer mitigates but does not eliminate local LP.
      Forest patches E and S of pin provide partial wind shelter but obstruct horizon ~10-15° in those directions.
      Larger villages (Wahl, Grosbous) are >1 km away.
      Access via small rural roads: Bousserwee (S), Ringbaach (N), Rue Nicolas Grang (W) — minimal night traffic.
      First visit: scout the exact rig location. Pin is at field edge near forest. A more central spot
      ~200m N (around 49.842, 5.920) would be further from Kinigshaff hamlet and have a cleaner horizon.
      Find a roadside parking spot or designated pullout — pin location is in agricultural fields.
      Verified via Google Maps satellite 2026-04-06 (terrain confirmed open plateau, hamlet caveat noted).

  burfelt:
    name: "Burfelt Viewpoint (Rastplatz mit Aussicht)"
    latitude: 49.913
    longitude: 5.926
    altitude_m: 407         # Open-Elevation API verified
    bortle: 4               # verified via clearoutside.com 2026-04-06
    sqm: 21.06              # mag/arcsec²
    artificial_mcd: 0.235   # 234.76 μcd/m²
    timezone: "Europe/Luxembourg"
    horizon:
      type: "open"
      altitude_min: 10
    setup_time_min: 35
    teardown_time_min: 25
    power_source: "jackery"
    notes: |
      DESIGNATED VIEWPOINT site (40 min drive, 48% less LP than balcony, SQM 21.06).
      Located on a forested ridge above Esch-sur-Sûre lake — Plus Code: WW7G+695 Esch-sur-Sûre.
      THREE labeled viewpoint features in the immediate area:
        - Rastplatz mit Aussicht (rest area with view) — designated parking
        - Esch-sur-Sûre Veduta dall'alto (panoramic viewpoint)
        - View Spot
      Pin lands in a small open clearing surrounded by forest. Built-in horizon clearance — no scouting required.
      ACCESS: CR316 (Um Knupp) provides road access, designated parking at the rest area.
      HORIZON: Open S/SW (toward lake and Esch-sur-Sûre), forest backdrop on N/E (blocks northern LP).
      CAVEAT: Esch-sur-Sûre town (~250 inhabitants) is in the valley directly S — most direct light blocked
      by terrain, but some sky glow above the town. Minor impact on low-altitude S targets (M16/M17 transit ~26°).
      Hydroelectric dam visible to S — typically not lit at night.
      USE WHEN: First portable sessions, when reliable infrastructure matters more than absolute darkness,
      when targets transit at >30° altitude (sky glow from town stays below the target).
      DON'T USE WHEN: Imaging M16/M17 (low S transits) — prefer Wahl's clearer S horizon for those.
      Verified via Google Maps satellite + clearoutside 2026-04-06.

  hoscheid:
    name: "Plateau de Hoscheid (Parc Hosingen)"
    latitude: 49.967
    longitude: 6.080
    altitude_m: 452         # Open-Elevation API verified
    bortle: 4               # verified via clearoutside.com 2026-04-06 — DARKEST site within reach
    sqm: 21.23              # mag/arcsec² — just shy of Bortle 3 (~21.30 threshold)
    artificial_mcd: 0.178   # 177.92 μcd/m² — 61% less than balcony
    timezone: "Europe/Luxembourg"
    horizon:
      type: "open"
      altitude_min: 10      # forest perimeter on N/E adds ~5-15° obstruction in those quadrants — refine after first visit
    setup_time_min: 45
    teardown_time_min: 30
    power_source: "jackery"
    notes: |
      DARKEST site within reach (45 min drive, 61% less LP than balcony, SQM 21.23, just shy of Bortle 3).
      Located inside Parc Hosingen Naturpark — Plus Code: X38J+Q2R. 
      Terrain: large open clearing (~400×200m) with what appears to be a grass airstrip in the centre — ideal level ground.
      Oval perimeter access road suggests vehicle parking at the SE corner where the pin sits.
      Forest backdrop N and E (advantageous: blocks stray light from any nearby settlement).
      Open S and W — productive transit window completely clear.
      Far from villages (Hoscheid ~1 km N, separated by forest).
      Use for dedicated dark-sky projects (faint reflection nebulae, Sh2-240 Simeis 147, faint galaxies)
      where the extra 15 min drive vs Wahl is justified by the ×1.6 SNR gain over balcony.
      First visit: scout the exact rig location — pin is at SE parking spot, but moving ~50m into the
      clearing centre (~49.9678, 6.0782) gives a cleaner horizon if needed.
      Verified via Google Maps satellite 2026-04-06.

equipment:
  camera: "ASI2600MC Pro"
  sensor_size: "23.5 x 15.7 mm"
  pixel_size_um: 3.76
  resolution_px: "6248 x 4176"
  gain: 100
  telescope: "RedCat 51"
  focal_length_mm: 250
  focal_ratio: 4.9
  image_scale_arcsec: 3.1
  fov_deg: "5.4 x 3.6"
  guider: "ASI385MC + UniGuide 32mm"
  mount: "iOptron CEM26"
  focuser: "ZWO EAF"

cooling:
  summer: -10  # April–September
  winter: -20  # October–March

exposure_defaults:
  emission_nebula: 300   # seconds, Quad Band
  galaxy: 180            # seconds, L-Pro
  cluster: 120           # seconds, L-Pro
  planetary_nebula: 180  # seconds, Quad Band
  supernova_remnant: 300 # seconds, Quad Band

filter_rules:
  single_filter_per_session: true
  emission_nebula: "Antlia Quad Band"
  galaxy: "Optolong L-Pro"
  cluster: "Optolong L-Pro"
  planetary_nebula: "Antlia Quad Band"
  supernova_remnant: "Antlia Quad Band"
  reflection_nebula: "Optolong L-Pro"

workflow_rules:
  emission_nebula: "[[QuadBand-OSC-Workflow]]"
  galaxy: "[[RGB-Workflow]]"
  cluster: "[[RGB-Workflow]]"
  planetary_nebula: "[[QuadBand-OSC-Workflow]]"
  supernova_remnant: "[[QuadBand-OSC-Workflow]]"
  reflection_nebula: "[[RGB-Workflow]]"
  hdr_targets:
    - M42    # Trapezium core
    - M16    # Eagle Nebula pillars
    - M17    # Omega Nebula bar
    - M31    # Andromeda nucleus
    - M64    # Black Eye nucleus
  hdr_suffix: " + [[HDR-Workflow]]"  # append to base workflow for HDR targets

stellarium:
  api_url: "http://localhost:8090"
  fov_deg: 5.4               # RedCat 51 horizontal FOV
  screenshot_dir: "~/Pictures/Stellarium"  # default macOS location
  altitude_warning_deg: 1.0  # warn if internal vs Stellarium altitude differs by more than this
  finder_chart_dir: "05_Sessions/{year}/Finder-Charts"
```

---

## Workflow

### Step 1: Parse Date, Flags, and Resolve Location

Parse the argument string for:

1. **`--stellarium` / `-s` flag** — set `stellarium_enabled = true`. Strip from input.
2. **`--location <name>` / `-l <name>` flag** — set `location_arg = <name>`. Strip the flag and its value from input.
3. **Date expression** — what remains. Resolve to an ISO date (YYYY-MM-DD). If ambiguous, ask the user.

#### Resolve the active location

Order of precedence:

1. If `--location <name>` was provided → use that preset
2. Otherwise, read state file `06_Metadata/Agents/Claude/state/session-plan-state.json`:
   ```bash
   STATE_FILE="06_Metadata/Agents/Claude/state/session-plan-state.json"
   if [ -f "$STATE_FILE" ]; then
     LAST_LOC=$(python3 -c "import json; print(json.load(open('$STATE_FILE')).get('last_location', ''))")
   fi
   ```
   If `last_location` exists and is a valid preset → use it
3. Otherwise, fall back to the location in the `locations:` config marked `default: true`

Validate the resolved location exists in the `locations:` config. If the user passed an unknown name → error: "Unknown location preset 'X'. Available: balcony, schwebach, wahl, burfelt, hoscheid".

#### Persist last-used location

After the location is resolved (and BEFORE the rest of the workflow runs), write the state file:

```bash
mkdir -p "06_Metadata/Agents/Claude/state"
python3 -c "
import json, datetime
state = {
    'last_location': '${RESOLVED_LOCATION}',
    'last_used': datetime.datetime.now().isoformat(),
    'last_command': '/session-plan ${ORIGINAL_ARGS}'
}
with open('${STATE_FILE}', 'w') as f:
    json.dump(state, f, indent=2)
"
```

#### Bind active location to runtime variables

For the rest of the workflow, use these variables (extracted from the chosen location's config block):

```
LOC_NAME       = locations[active].name
LOC_LAT        = locations[active].latitude
LOC_LON        = locations[active].longitude
LOC_ALT        = locations[active].altitude_m
LOC_BORTLE     = locations[active].bortle
LOC_SQM        = locations[active].sqm
LOC_ARTIFICIAL = locations[active].artificial_mcd
LOC_HORIZON    = locations[active].horizon
LOC_SETUP      = locations[active].setup_time_min
LOC_TEARDOWN   = locations[active].teardown_time_min
LOC_POWER      = locations[active].power_source
```

#### Auto-fetch sky quality from clearoutside.com (verification)

After binding the location, fetch the **current** Bortle/SQM values from clearoutside as a sanity check against the stored preset values:

```bash
# Coordinates rounded to 2 decimal places (clearoutside accepts low precision)
LAT2=$(printf "%.2f" "${LOC_LAT}")
LON2=$(printf "%.2f" "${LOC_LON}")

CO_HTML=$(curl -sf -m 10 "https://clearoutside.com/forecast/${LAT2}/${LON2}?view=current")

# Extract: SQM, Bortle class, total brightness, artificial brightness
LIVE_DATA=$(echo "$CO_HTML" | python3 -c "
import sys, re, json
html = sys.stdin.read()
m = re.search(r'<strong>([0-9.]+)</strong> Magnitude\.\s*&nbsp;<strong>Class\s*(\d+)</strong>\s*Bortle\.\s*&nbsp;<strong>([0-9.]+)</strong>\s*mcd/m<sup>2</sup>\s*Brightness\.\s*&nbsp;<strong>([0-9.]+)</strong>\s*μcd/m<sup>2</sup>\s*Artificial Brightness', html)
if m:
    print(json.dumps({'sqm': float(m.group(1)), 'bortle': int(m.group(2)), 'total_mcd': float(m.group(3)), 'artificial_mcd_um': float(m.group(4))}))
else:
    print('{}')
")
```

##### Comparison logic

```
LIVE_BORTLE = parsed.bortle
LIVE_SQM = parsed.sqm

if LIVE_BORTLE != LOC_BORTLE:
    print warning:
      "⚠️ Bortle mismatch for {LOC_NAME}: preset says {LOC_BORTLE}, clearoutside says {LIVE_BORTLE}.
       Using live value ({LIVE_BORTLE}) for this session.
       Consider updating the preset in session-plan.md."
    LOC_BORTLE = LIVE_BORTLE  # use the live value

if abs(LIVE_SQM - LOC_SQM) > 0.3:
    print info:
      "ℹ️ SQM drift: preset {LOC_SQM}, live {LIVE_SQM}. Light pollution model may have updated."
```

##### Failure handling

- **Network failure / timeout** → log warning, fall back to stored `LOC_BORTLE` from the preset
- **Regex parse failure** (clearoutside HTML format changed) → same fallback, log error
- **Missing SQM/Bortle in preset** → require live fetch; if it fails, abort with clear error

##### Why clearoutside?

- Free, no API key required
- Uses the [Falchi 2016 World Atlas](http://cires1.colorado.edu/artificial-sky/) light pollution data (same source as lightpollutionmap.info)
- Returns SQM, Bortle class, total brightness, and artificial brightness in one HTML response
- Bonus: also returns astro/nautical/civil twilight, moon rise/set, and a 7-day cloud forecast — could replace sunrise-sunset.org in a future version

#### Example parsing

| Input | date | stellarium | location |
|-------|------|------------|----------|
| `tonight` | today | false | last-used (or balcony if first run) |
| `tomorrow --stellarium` | tomorrow | true | last-used |
| `2026-06-12 -s --location quatre-vents` | 2026-06-12 | true | quatre-vents |
| `saturday -l balcony` | next Sat | false | balcony |

### Step 2: Fetch Astronomical Data

Execute these WebFetch calls in parallel:

#### 2a. Twilight Times

```
GET https://api.sunrise-sunset.org/json?lat={LOC_LAT}&lng={LOC_LON}&date={DATE}&formatted=0
```

Extract from response:
- `astronomical_twilight_end` → evening twilight (session start)
- `astronomical_twilight_begin` → morning twilight (session end)
- Convert from UTC to Europe/Luxembourg timezone

#### 2b. Weather Forecast

```
GET https://api.open-meteo.com/v1/forecast?latitude={LOC_LAT}&longitude={LOC_LON}&hourly=cloud_cover,cloud_cover_low,cloud_cover_mid,cloud_cover_high,visibility,relative_humidity_2m,wind_speed_10m,temperature_2m&timezone=Europe/Luxembourg&start_date={DATE}&end_date={DATE_PLUS_1}
```

Extract hourly data for the night window (twilight to twilight):
- Cloud cover (total, low, mid, high)
- Visibility (meters)
- Humidity (%)
- Wind speed (km/h)
- Temperature (°C)

Summarize as: clear/partly cloudy/cloudy, temperature range, humidity, wind.

**If cloud cover > 70% for most of the night, warn the user but continue planning.**

#### 2c. Moon Phase (Calculate)

Calculate moon illumination from the date using the synodic period:

```
Known new moon reference: 2024-01-11
Synodic period: 29.53059 days
Days since reference = (target_date - 2024-01-11).days
Phase angle = ((days_since_ref % 29.53059) / 29.53059) * 360
Illumination = (1 - cos(phase_angle_radians)) / 2 * 100
```

Determine phase name: new / waxing crescent / first quarter / waxing gibbous / full / waning gibbous / last quarter / waning crescent.

Estimate moon rise/set times and position (approximate from phase — full moon rises at sunset, new moon is absent).

### Step 3: Read Vault Context

#### 3a. Target Integration Status

Read all files in `02_Targets/` using Glob + Read:
- Extract `total_integration` from YAML frontmatter
- Extract `sessions` list
- Build a table: `{ designation, type, total_integration, sessions_count }`
- Flag targets with "TBD" or "In progress" as needing data

#### 3b. Calibration Library

Read `04_Processing/Calibration/Master-Library.md`:
- Extract available dark frame exposures and temperatures
- Extract available flat/dark flat/bias inventory

#### 3c. Camera Temperature

Determine from the month of the target date:
- April–September → -10°C
- October–March → -20°C

### Step 4: Calculate Object Visibility

Use the built-in catalog (Section: Object Catalog below).

For each object, calculate altitude at 30-minute intervals from evening twilight to morning twilight:

```
Algorithm:
1. Compute Local Sidereal Time (LST) for each time step
   LST = 100.46 + 0.985647 * d + longitude + 15 * UT_hours
   (where d = Julian days since J2000.0)
2. Hour Angle (HA) = LST - RA (in degrees)
3. Altitude = arcsin(sin(lat) * sin(dec) + cos(lat) * cos(dec) * cos(HA))
4. Azimuth = arctan2(-sin(HA), tan(dec)*cos(lat) - sin(lat)*cos(HA))
```

Filter objects (horizon constraints come from `LOC_HORIZON` of the active location):

- **Angular size ≥ 30'** — objects smaller than 30' are too small for the RedCat 51 FOV (5.4° × 3.6°). Exclude them entirely. See [[Seasonal-Calendar]] for the full list of suitable targets.
- **Altitude > LOC_HORIZON.altitude_min** during at least 1 hour of the night
- **Azimuth filter:**
  - If `LOC_HORIZON.type == "constrained"` → require `azimuth_min ≤ az ≤ azimuth_max` (e.g., balcony: 135°–225°)
  - If `LOC_HORIZON.type == "open"` → no azimuth restriction (full 360° access, e.g., dark site)
- **Not within 30° of moon** (if moon illumination > 50%)
- **Magnitude < 10** (visible with the setup)
- **Declination check (constrained horizon only):** Objects at Dec > 55° have very brief south window time (<1h) from latitude 49.6°. Objects at Dec 35°–50° transit near zenith but still get ~1.5–2.5h — viable with multi-night accumulation. **Skip this check at open-horizon locations** — high-declination targets (Heart/Soul, IC 1396, M81/M82) become viable.

Sort remaining objects by:
1. Hours available above 30° altitude (more = better)
2. Need for more integration (vault-aware priority)
3. Angular size (larger = better framing)

**If no objects ≥ 30' are visible** in the azimuth window for the given date, report "no suitable targets for this setup" and suggest calibration frames or reprocessing instead. Do not propose small galaxies/clusters as targets.

### Step 5: Select Targets and Filter

#### 5a. Determine Best Filter

Count candidate objects by filter type:
- If more narrowband targets (emission nebulae, SNR) are available → **Antlia Quad Band**
- If more broadband targets (galaxies, clusters) are available → **Optolong L-Pro**
- If moon > 75% illuminated → strongly prefer **Antlia Quad Band**

Lock the filter for the entire session.

#### 5b. Select 2–4 Objects

From objects matching the selected filter, choose 2–4 that:
- **Tile the night chronologically** — first object is highest early, second peaks mid-night, etc.
- **Avoid meridian flip** — prefer objects approaching transit from the east (HA slightly negative)
- **Maximize time on target** — fill the available window
- **Prioritize vault needs** — objects with less existing integration get preference

#### 5c. Calculate Frames Per Target

For each target:
```
available_minutes = (end_time - start_time).minutes
dithering_overhead = 0.10  # 10%
effective_minutes = available_minutes * (1 - dithering_overhead)
frames = floor(effective_minutes * 60 / exposure_seconds)
total_exposure = frames * exposure_seconds
```

#### 5d. Stellarium Integration (only if `--stellarium` flag is set)

**Skip this entire step if `stellarium_enabled` is false.**

##### 5d.1 Probe Stellarium API

```bash
curl -sf -m 3 http://localhost:8090/api/main/status
```

If the call fails:
- Print warning: "⚠️ Stellarium API unreachable on http://localhost:8090. Skipping cross-check and finder charts. Start Stellarium and enable Remote Control plugin (F2 → Plugins → Remote Control → Configure → Server enabled)."
- Set `stellarium_enabled = false` and continue with normal flow.

If the call succeeds:
- Parse the response and **save the original state**:
  ```
  original_jday = response.time.jday
  original_isTimeNow = response.time.isTimeNow
  original_fov = response.view.fov
  ```
- These will be restored at the end of step 5d.

##### 5d.2 Cross-Check Altitude Per Target

For each selected target (1 to N), at its **peak altitude time** (mid-window):

1. Convert peak time to Julian Day:
   ```python
   from datetime import datetime, timezone
   dt_utc = peak_time_local.astimezone(timezone.utc)
   jday = (dt_utc.timestamp() / 86400.0) + 2440587.5
   ```

2. Set Stellarium time:
   ```bash
   curl -sf -m 3 -X POST http://localhost:8090/api/main/time --data "time=${jday}"
   ```

3. Focus on target:
   ```bash
   curl -sf -m 3 -X POST http://localhost:8090/api/main/focus --data "target=${designation}"
   ```

4. Read object info:
   ```bash
   sleep 1.0  # CRITICAL: Stellarium needs ~1s to settle after focus,
              # otherwise alt/az may reflect a previous selection
   curl -sf -m 3 "http://localhost:8090/api/objects/info?format=json"
   ```

5. Compare:
   ```
   delta = abs(internal_altitude - stellarium.altitude)
   if delta > altitude_warning_deg (1.0°):
       warn user about discrepancy with both values
   else:
       use stellarium.altitude as authoritative for the report
   
   record stellarium.airmass for the planning table
   record stellarium.above-horizon as sanity check
   ```

##### 5d.3 Capture Finder Chart Per Target

For each target:

1. Set FOV to the RedCat 51 field of view:
   ```bash
   curl -sf -m 3 -X POST http://localhost:8090/api/main/fov --data "fov=5.4"
   ```

2. Note the highest existing screenshot number BEFORE capture:
   ```bash
   ls ~/Pictures/Stellarium/stellarium-*.png 2>/dev/null | sort | tail -1
   ```

3. Trigger screenshot:
   ```bash
   curl -sf -m 3 -X POST http://localhost:8090/api/stelaction/do --data "id=actionSave_Screenshot_Global"
   sleep 1.5  # screenshot is async, wait for file write
   ```

4. Find the new file (highest number not in the pre-capture list):
   ```bash
   find ~/Pictures/Stellarium -name "stellarium-*.png" -mmin -1 | sort | tail -1
   ```

5. Move/rename to the finder charts directory:
   ```bash
   FINDER_DIR="05_Sessions/${year}/Finder-Charts"
   mkdir -p "${FINDER_DIR}"
   mv "${captured_file}" "${FINDER_DIR}/${date}-${designation}-finder.png"
   ```

##### 5d.4 Restore Stellarium State

After all targets are processed:

1. Restore time to "now" (real-time tracking):
   ```bash
   curl -sf -m 3 -X POST http://localhost:8090/api/stelaction/do --data "id=actionReturn_To_Current_Time"
   ```

2. Restore the original FOV:
   ```bash
   curl -sf -m 3 -X POST http://localhost:8090/api/main/fov --data "fov=${original_fov}"
   ```

##### 5d.5 Error Handling

If any single curl call fails mid-loop:
- Log the failure for that specific target
- Continue with the next target (don't abort the entire integration)
- At the end, summarize which targets failed Stellarium queries

If the screenshot file isn't found after the timeout:
- Skip the finder chart for that target but keep the cross-check data
- Note in the session file that the chart is unavailable

### Step 6: Generate Session File

Write to `05_Sessions/{year}/{date}-Capture.md` using the CAPTURE_SESSION_TEMPLATE format.

Read the template from `06_Metadata/Templates/CAPTURE_SESSION_TEMPLATE.md` first, then fill:

**YAML frontmatter:**
```yaml
---
title: "{date} Capture Session"
type: capture-session
date: {date}
location: "{LOC_NAME}"
location_preset: "{location_id}"   # e.g., balcony or quatre-vents
location_coords: "{LOC_LAT}, {LOC_LON}"
location_altitude_m: {LOC_ALT}
bortle: {LOC_BORTLE}
power_source: "{LOC_POWER}"
twilight_evening: "{HH:MM}"
twilight_morning: "{HH:MM}"
moon_phase: "{phase_name}"
moon_illumination: "{illumination}%"
equipment:
  camera: "[[ASI2600MCPro]]"
  telescope: "[[RedCat-51]]"
  mount: "[[iOptron-CEM26]]"
  filter: "[[{selected_filter}]]"
  guider: "[[ASI385MC]]"
  guidescope: "[[UniGuide-32mm]]"
targets:
  - "[[{target_1}]]"
  - "[[{target_2}]]"
tags:
  - session/capture
---
```

**Location section** (always included, just after Conditions):

```markdown
## Location

| Parameter | Value |
|-----------|-------|
| **Site** | {LOC_NAME} |
| **Coordinates** | {LOC_LAT}, {LOC_LON} |
| **Altitude** | {LOC_ALT} m |
| **Bortle class** | {LOC_BORTLE} |
| **Horizon** | {open / constrained az_min-az_max} |
| **Setup time** | {LOC_SETUP} min |
| **Teardown time** | {LOC_TEARDOWN} min |
| **Power source** | {LOC_POWER} |
| **Notes** | {LOC_NOTES} |

{LOC_NOTES_AS_TEXT}
```

If `LOC_POWER == "jackery"`, append a power budget warning section linking to [[Jackery-Explorer-500]] with the season-appropriate runtime estimate from that note.

**Body sections:**
- Conditions: twilight times, moon, weather summary, temperature
- Planning table: objects with times, exposure, frames, filter, gain, temp, recommended workflow
- **Stellarium cross-check** (only if `--stellarium` was used): table comparing internal vs Stellarium altitudes per target, with deltas
- **Finder charts** (only if `--stellarium` was used): one section per target with the captured PNG embedded
- Calibration: checklist comparing needed darks/flats to Master-Library
- Notes: any concerns (moon proximity, cloud windows, guiding notes)

**Finder chart embed format** (only if charts were captured):

```markdown
## Finder Charts

### M42 — Orion Nebula
![[2026-06-12-M42-finder.png]]
*Captured at 22:30 CEST — alt 35.2°, az 195.4°, FOV 5.4° (RedCat 51 framing)*

### NGC 7000 — North America Nebula
![[2026-06-12-NGC7000-finder.png]]
*Captured at 23:45 CEST — alt 84.1°, az 180.2°, FOV 5.4°*
```

**Stellarium cross-check table format:**

```markdown
## Stellarium Cross-Check

| Target | Internal alt | Stellarium alt | Δ | Stellarium az | Airmass | Status |
|--------|-------------|----------------|---|---------------|---------|--------|
| M42 | 35.0° | 35.21° | 0.21° | 195.4° | 1.74 | ✓ |
| NGC 7000 | 83.5° | 84.10° | 0.60° | 180.2° | 1.01 | ✓ |
```

If any delta exceeds 1°, mark with ⚠️ and add a note explaining the likely cause (timezone, epoch, or location discrepancy).

### Step 7: Report to User

Display in the conversation:

1. **Session summary** — date, twilight window, moon, weather verdict
2. **Target table** — same as in the file
3. **Altitude chart** — ASCII visualization of selected objects through the night:

```
Alt(°)
 80│          ╱──M42──╲
 60│      ╱──╱        ╲──╲──NGC2244──╲
 40│  ╱──╱                            ╲──╲
 20│╱                                      ╲
 10│─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
   └──────────────────────────────────────────
   20:30  21:30  22:30  23:30  00:30  01:30  04:30
```

4. **Concerns** — cloud windows to avoid, moon proximity warnings, calibration gaps
5. **File path** — where the session file was written

---

## Object Catalog

Embedded catalog of ~50 deep sky objects suitable for the RedCat 51 FOV.

### Emission Nebulae (Quad Band)

| Designation | Name | RA (h:m) | DEC (d:m) | Mag | Size (') | FOV | Constellation |
|-------------|------|----------|-----------|-----|----------|-----|---------------|
| M42 | Orion Nebula | 05:35 | -05:23 | 4.0 | 85x60 | YES | Orion |
| M43 | De Mairan's Nebula | 05:36 | -05:16 | 9.0 | 20x15 | no | Orion |
| NGC7000 | North America Nebula | 20:59 | +44:32 | 4.0 | 120x100 | YES | Cygnus |
| IC5070 | Pelican Nebula | 20:51 | +44:24 | 8.0 | 60x50 | YES | Cygnus |
| NGC2244 | Rosette Nebula | 06:32 | +04:52 | 4.8 | 80x60 | YES | Monoceros |
| IC1396 | Elephant's Trunk | 21:39 | +57:30 | 3.5 | 170x140 | YES | Cepheus |
| IC1805 | Heart Nebula | 02:33 | +61:27 | 6.5 | 150x150 | YES | Cassiopeia |
| IC1848 | Soul Nebula | 02:51 | +60:25 | 6.5 | 150x75 | YES | Cassiopeia |
| NGC6960 | Western Veil | 20:46 | +30:43 | 7.0 | 70x6 | YES | Cygnus |
| NGC6992 | Eastern Veil | 20:56 | +31:43 | 7.0 | 60x8 | YES | Cygnus |
| NGC6888 | Crescent Nebula | 20:12 | +38:21 | 7.4 | 18x12 | no | Cygnus |
| NGC7380 | Wizard Nebula | 22:47 | +58:08 | 7.2 | 25x30 | no | Cepheus |
| M16 | Eagle Nebula | 18:19 | -13:47 | 6.0 | 35x28 | YES | Serpens |
| M17 | Omega Nebula | 18:21 | -16:11 | 6.0 | 46x37 | YES | Sagittarius |
| NGC2264 | Cone Nebula / Christmas Tree | 06:41 | +09:53 | 3.9 | 60x30 | YES | Monoceros |
| IC443 | Jellyfish Nebula | 06:17 | +22:31 | 12.0 | 50x40 | YES | Gemini |
| Sh2-129 | Flying Bat Nebula | 21:12 | +59:55 | — | 200x120 | YES | Cepheus |
| NGC281 | Pacman Nebula | 00:53 | +56:37 | 7.4 | 35x30 | YES | Cassiopeia |
| Sh2-240 | Simeis 147 | 05:39 | +28:00 | — | 180 | YES | Taurus |
| NGC1499 | California Nebula | 04:04 | +36:25 | 5.0 | 145x40 | YES | Perseus |

### Galaxies (L-Pro)

> **Most galaxies are too small for the RedCat 51.** Only M31 and M33 have angular sizes ≥ 30'. The others are kept in the catalog for reference but must NOT be proposed as session targets.

| Designation | Name | RA (h:m) | DEC (d:m) | Mag | Size (') | FOV | Constellation |
|-------------|------|----------|-----------|-----|----------|-----|---------------|
| M31 | Andromeda Galaxy | 00:43 | +41:16 | 3.4 | 178x63 | YES | Andromeda |
| M33 | Triangulum Galaxy | 01:34 | +30:39 | 5.7 | 73x45 | YES | Triangulum |
| M51 | Whirlpool Galaxy | 13:30 | +47:12 | 8.4 | 11x7 | no | Canes Venatici |
| M81 | Bode's Galaxy | 09:56 | +69:04 | 6.9 | 27x14 | no | Ursa Major |
| M82 | Cigar Galaxy | 09:56 | +69:41 | 8.4 | 11x5 | no | Ursa Major |
| M101 | Pinwheel Galaxy | 14:03 | +54:21 | 7.9 | 29x27 | no | Ursa Major |
| M104 | Sombrero Galaxy | 12:40 | -11:37 | 8.0 | 9x4 | no | Virgo |
| M106 | | 12:19 | +47:18 | 8.4 | 19x8 | no | Canes Venatici |
| NGC4565 | Needle Galaxy | 12:36 | +25:59 | 9.6 | 16x2 | no | Coma Berenices |
| M86 | | 12:26 | +12:57 | 8.9 | 9x7 | no | Virgo |
| NGC4435 | The Eyes | 12:28 | +13:05 | 10.8 | 3x2 | no | Virgo |
| M64 | Black Eye Galaxy | 12:57 | +21:41 | 8.5 | 10x5 | no | Coma Berenices |
| M63 | Sunflower Galaxy | 13:16 | +42:02 | 8.6 | 13x8 | no | Canes Venatici |
| NGC891 | | 02:23 | +42:21 | 9.9 | 14x3 | no | Andromeda |

### Clusters (L-Pro)

> **Only M44 (Beehive), M45 (Pleiades), and NGC 869/884 (Double Cluster) are large enough** for the RedCat 51. Globular clusters (M13, M3, M5, etc.) are too small.

| Designation | Name | RA (h:m) | DEC (d:m) | Mag | Size (') | FOV | Constellation |
|-------------|------|----------|-----------|-----|----------|-----|---------------|
| M13 | Hercules Cluster | 16:42 | +36:28 | 5.8 | 20 | no | Hercules |
| M44 | Beehive Cluster | 08:40 | +19:59 | 3.7 | 95 | YES | Cancer |
| M5 | Rose Cluster | 15:19 | +02:05 | 5.7 | 23 | no | Serpens |
| M3 | | 13:42 | +28:23 | 6.2 | 18 | no | Canes Venatici |
| M92 | | 17:17 | +43:08 | 6.4 | 14 | no | Hercules |
| M15 | | 21:30 | +12:10 | 6.2 | 18 | no | Pegasus |
| M45 | Pleiades | 03:47 | +24:07 | 1.6 | 110 | YES | Taurus |
| NGC869 | Double Cluster (h) | 02:19 | +57:09 | 5.3 | 30 | YES | Perseus |
| NGC884 | Double Cluster (chi) | 02:22 | +57:07 | 6.1 | 30 | YES | Perseus |
| M35 | | 06:09 | +24:20 | 5.3 | 28 | no | Gemini |

### Planetary Nebulae (Quad Band preferred)

> **All planetary nebulae are too small** for the RedCat 51. None should be proposed as session targets.

| Designation | Name | RA (h:m) | DEC (d:m) | Mag | Size (') | FOV | Constellation |
|-------------|------|----------|-----------|-----|----------|-----|---------------|
| M27 | Dumbbell Nebula | 19:60 | +22:43 | 7.5 | 8x6 | no | Vulpecula |
| M57 | Ring Nebula | 18:54 | +33:02 | 8.8 | 1.4x1.0 | no | Lyra |
| NGC7293 | Helix Nebula | 22:30 | -20:50 | 7.6 | 25x20 | no | Aquarius |
| M76 | Little Dumbbell | 01:42 | +51:34 | 10.1 | 3x2 | no | Perseus |

---

## Calibration Logic

Compare planned exposures against `04_Processing/Calibration/Master-Library.md`:

For each unique exposure + temperature combination in the plan:
1. Check if matching darks exist in the library
2. If yes → "Dark frames: available (master)"
3. If no → "Dark frames: NEEDED — {exposure}s at {temp}°C, 25 frames"

For flats:
1. Check if flats exist for the selected filter in the library
2. If yes → "Flat frames: available (master)"
3. If no → "Flat frames: **NEEDED** — 50 frames with {filter}. Capture at end of session before dismounting."
4. **Important:** Each filter requires its own flat set. Flats from one filter cannot be used for another (different vignetting and dust patterns). Flag prominently if the selected filter has no flats.

Always include dark flats and bias as checklist items.

---

## Error Handling

| Error | Response |
|-------|----------|
| Sunrise/Open-Meteo API timeout/failure | Warn user, continue with calculable data (twilight can be estimated, weather unknown) |
| No visible objects | Report "no suitable targets visible" with reason (wrong season, moon too bright, etc.) |
| All targets fully integrated | Report status, offer to suggest targets for additional integration time |
| Cloud cover > 80% all night | Warn "poor conditions forecast" but generate plan anyway (forecast may change) |
| Date in the past | Warn but allow (useful for post-session documentation) |
| Stellarium API unreachable (with `--stellarium`) | Print activation hint, disable Stellarium step, continue normally |
| Stellarium screenshot file not found | Skip the chart for that target, keep cross-check data, note in session file |
| Altitude delta > 1° between internal and Stellarium | Mark with ⚠️ in cross-check table, suggest checking timezone/location |
| `actionReturn_To_Current_Time` fails | Set time explicitly via `POST /api/main/time` with current JD as fallback |
| Unknown `--location` preset | Error: list valid presets from `locations:` config and abort |
| State file missing | First-run: use the location marked `default: true`, create state file after success |
| State file corrupted | Warn user, use default location, overwrite state with current selection |
| `--location` provided but preset has missing fields | Validate required fields (lat, lon, alt, bortle, horizon); abort if any missing |
| clearoutside.com unreachable / parse fails | Warn user, fall back to stored `bortle`/`sqm` from the preset config |
| Live Bortle differs from preset by ≥1 class | Warn in output, use live value, suggest updating the preset |
