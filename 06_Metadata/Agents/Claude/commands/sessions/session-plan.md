---
name: session-plan
description: "Plan an astrophotography capture session for a given date"
shortcut: sp
category: sessions
version: "1.0"
argument-hint: "<date> (e.g., tonight, tomorrow, 2025-04-15)"
allowed-tools: WebFetch, Read, Write, Glob, Bash(date:*), Bash(python3:*)
---

# Session Planner

Plan an astrophotography capture session by fetching real astronomical and weather data, reading vault context, and generating a session file.

---

## Input

A date expression:
- `tonight`, `today` → current date
- `tomorrow` → next day
- `YYYY-MM-DD` → specific date
- `next friday`, `saturday` → resolve to next occurrence

---

## Configuration (Fixed)

```yaml
location:
  name: "Tuntange, Luxembourg"
  latitude: 49.6
  longitude: 6.1
  altitude_m: 310
  bortle: 4
  timezone: "Europe/Luxembourg"

visibility_window:
  azimuth_min: 135  # SE
  azimuth_max: 225  # SW
  altitude_min: 10  # degrees above horizon

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
```

---

## Workflow

### Step 1: Parse Date

Resolve the input to an ISO date (YYYY-MM-DD). If ambiguous, ask the user.

### Step 2: Fetch Astronomical Data

Execute these WebFetch calls in parallel:

#### 2a. Twilight Times

```
GET https://api.sunrise-sunset.org/json?lat=49.6&lng=6.1&date={DATE}&formatted=0
```

Extract from response:
- `astronomical_twilight_end` → evening twilight (session start)
- `astronomical_twilight_begin` → morning twilight (session end)
- Convert from UTC to Europe/Luxembourg timezone

#### 2b. Weather Forecast

```
GET https://api.open-meteo.com/v1/forecast?latitude=49.6&longitude=6.1&hourly=cloud_cover,cloud_cover_low,cloud_cover_mid,cloud_cover_high,visibility,relative_humidity_2m,wind_speed_10m,temperature_2m&timezone=Europe/Luxembourg&start_date={DATE}&end_date={DATE_PLUS_1}
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

Filter objects:
- **Altitude > 10°** during at least 1 hour of the night
- **Azimuth between 135° and 225°** (SE to SW) during their best window
- **Not within 30° of moon** (if moon illumination > 50%)
- **Magnitude < 10** (visible with the setup)

Sort remaining objects by:
1. Hours available above 30° altitude (more = better)
2. Need for more integration (vault-aware priority)
3. Angular size suitable for FOV (prefer objects > 20')

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

### Step 6: Generate Session File

Write to `05_Sessions/{year}/{date}-Capture.md` using the CAPTURE_SESSION_TEMPLATE format.

Read the template from `06_Metadata/Templates/CAPTURE_SESSION_TEMPLATE.md` first, then fill:

**YAML frontmatter:**
```yaml
---
title: "{date} Capture Session"
type: capture-session
date: {date}
location: "Tuntange, Luxembourg"
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

**Body sections:**
- Conditions: twilight times, moon, weather summary, temperature
- Planning table: objects with times, exposure, frames, filter, gain, temp
- Calibration: checklist comparing needed darks/flats to Master-Library
- Notes: any concerns (moon proximity, cloud windows, guiding notes)

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

| Designation | Name | RA (h:m) | DEC (d:m) | Mag | Size (') | Constellation |
|-------------|------|----------|-----------|-----|----------|---------------|
| M42 | Orion Nebula | 05:35 | -05:23 | 4.0 | 85x60 | Orion |
| M43 | De Mairan's Nebula | 05:36 | -05:16 | 9.0 | 20x15 | Orion |
| NGC7000 | North America Nebula | 20:59 | +44:32 | 4.0 | 120x100 | Cygnus |
| IC5070 | Pelican Nebula | 20:51 | +44:24 | 8.0 | 60x50 | Cygnus |
| NGC2244 | Rosette Nebula | 06:32 | +04:52 | 4.8 | 80x60 | Monoceros |
| IC1396 | Elephant's Trunk | 21:39 | +57:30 | 3.5 | 170x140 | Cepheus |
| IC1805 | Heart Nebula | 02:33 | +61:27 | 6.5 | 150x150 | Cassiopeia |
| IC1848 | Soul Nebula | 02:51 | +60:25 | 6.5 | 150x75 | Cassiopeia |
| NGC6960 | Western Veil | 20:46 | +30:43 | 7.0 | 70x6 | Cygnus |
| NGC6992 | Eastern Veil | 20:56 | +31:43 | 7.0 | 60x8 | Cygnus |
| NGC6888 | Crescent Nebula | 20:12 | +38:21 | 7.4 | 18x12 | Cygnus |
| NGC7380 | Wizard Nebula | 22:47 | +58:08 | 7.2 | 25x30 | Cepheus |
| M16 | Eagle Nebula | 18:19 | -13:47 | 6.0 | 35x28 | Serpens |
| M17 | Omega Nebula | 18:21 | -16:11 | 6.0 | 46x37 | Sagittarius |
| NGC2264 | Cone Nebula / Christmas Tree | 06:41 | +09:53 | 3.9 | 60x30 | Monoceros |
| IC443 | Jellyfish Nebula | 06:17 | +22:31 | 12.0 | 50x40 | Gemini |
| Sh2-129 | Flying Bat Nebula | 21:12 | +59:55 | — | 200x120 | Cepheus |
| NGC281 | Pacman Nebula | 00:53 | +56:37 | 7.4 | 35x30 | Cassiopeia |
| Sh2-240 | Simeis 147 | 05:39 | +28:00 | — | 180 | Taurus |
| NGC1499 | California Nebula | 04:04 | +36:25 | 5.0 | 145x40 | Perseus |

### Galaxies (L-Pro)

| Designation | Name | RA (h:m) | DEC (d:m) | Mag | Size (') | Constellation |
|-------------|------|----------|-----------|-----|----------|---------------|
| M31 | Andromeda Galaxy | 00:43 | +41:16 | 3.4 | 178x63 | Andromeda |
| M33 | Triangulum Galaxy | 01:34 | +30:39 | 5.7 | 73x45 | Triangulum |
| M51 | Whirlpool Galaxy | 13:30 | +47:12 | 8.4 | 11x7 | Canes Venatici |
| M81 | Bode's Galaxy | 09:56 | +69:04 | 6.9 | 27x14 | Ursa Major |
| M82 | Cigar Galaxy | 09:56 | +69:41 | 8.4 | 11x5 | Ursa Major |
| M101 | Pinwheel Galaxy | 14:03 | +54:21 | 7.9 | 29x27 | Ursa Major |
| M104 | Sombrero Galaxy | 12:40 | -11:37 | 8.0 | 9x4 | Virgo |
| M106 | | 12:19 | +47:18 | 8.4 | 19x8 | Canes Venatici |
| NGC4565 | Needle Galaxy | 12:36 | +25:59 | 9.6 | 16x2 | Coma Berenices |
| M86 | | 12:26 | +12:57 | 8.9 | 9x7 | Virgo |
| NGC4435 | The Eyes | 12:28 | +13:05 | 10.8 | 3x2 | Virgo |
| M64 | Black Eye Galaxy | 12:57 | +21:41 | 8.5 | 10x5 | Coma Berenices |
| M63 | Sunflower Galaxy | 13:16 | +42:02 | 8.6 | 13x8 | Canes Venatici |
| NGC891 | | 02:23 | +42:21 | 9.9 | 14x3 | Andromeda |

### Clusters (L-Pro)

| Designation | Name | RA (h:m) | DEC (d:m) | Mag | Size (') | Constellation |
|-------------|------|----------|-----------|-----|----------|---------------|
| M13 | Hercules Cluster | 16:42 | +36:28 | 5.8 | 20 | Hercules |
| M44 | Beehive Cluster | 08:40 | +19:59 | 3.7 | 95 | Cancer |
| M5 | Rose Cluster | 15:19 | +02:05 | 5.7 | 23 | Serpens |
| M3 | | 13:42 | +28:23 | 6.2 | 18 | Canes Venatici |
| M92 | | 17:17 | +43:08 | 6.4 | 14 | Hercules |
| M15 | | 21:30 | +12:10 | 6.2 | 18 | Pegasus |
| M45 | Pleiades | 03:47 | +24:07 | 1.6 | 110 | Taurus |
| NGC869 | Double Cluster (h) | 02:19 | +57:09 | 5.3 | 30 | Perseus |
| NGC884 | Double Cluster (chi) | 02:22 | +57:07 | 6.1 | 30 | Perseus |
| M35 | | 06:09 | +24:20 | 5.3 | 28 | Gemini |

### Planetary Nebulae (Quad Band preferred)

| Designation | Name | RA (h:m) | DEC (d:m) | Mag | Size (') | Constellation |
|-------------|------|----------|-----------|-----|----------|---------------|
| M27 | Dumbbell Nebula | 19:60 | +22:43 | 7.5 | 8x6 | Vulpecula |
| M57 | Ring Nebula | 18:54 | +33:02 | 8.8 | 1.4x1.0 | Lyra |
| NGC7293 | Helix Nebula | 22:30 | -20:50 | 7.6 | 25x20 | Aquarius |
| M76 | Little Dumbbell | 01:42 | +51:34 | 10.1 | 3x2 | Perseus |

---

## Calibration Logic

Compare planned exposures against `04_Processing/Calibration/Master-Library.md`:

For each unique exposure + temperature combination in the plan:
1. Check if matching darks exist in the library
2. If yes → "Dark frames: available (master)"
3. If no → "Dark frames: NEEDED — {exposure}s at {temp}°C, 25 frames"

For flats:
1. Check if flats exist for the selected filter
2. If yes → "Flat frames: available (master)"
3. If no → "Flat frames: NEEDED — 50 frames with {filter}"

Always include dark flats and bias as checklist items.

---

## Error Handling

| Error | Response |
|-------|----------|
| API timeout / failure | Warn user, continue with calculable data (twilight can be estimated, weather unknown) |
| No visible objects | Report "no suitable targets visible" with reason (wrong season, moon too bright, etc.) |
| All targets fully integrated | Report status, offer to suggest targets for additional integration time |
| Cloud cover > 80% all night | Warn "poor conditions forecast" but generate plan anyway (forecast may change) |
| Date in the past | Warn but allow (useful for post-session documentation) |
