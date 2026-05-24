---
title: "ASIAIR Plus"
type: equipment
category: accessory
brand: "ZWO"
model: "ASIAIR Plus"
status: active
purchase_date: 2022-04-10
purchase_price: "$299.00"
purchase_store: "ZWO ASI"
purchase_url: "https://www.zwoasi.com"
tags:
  - equipment/accessory
---
		
# ZWO ASIAIR Plus

Dedicated astrophotography computer that controls the entire imaging rig wirelessly from a phone or tablet. Central hub connecting the [[ASI2600MCPro]], [[ASI385MC]], [[ZWO-EAF]], and [[iOptron-CEM26]].

- [ZWO ASIAIR product page](https://www.zwoastro.com/product/asiair/)

Purchased in 2022.

---

## Specifications

| Specification | Value |
|---------------|-------|
| Model | ASIAIR Plus (2nd generation) |
| Serial number | BCAAF0B1 |
| Processor | Quad-core ARM Cortex-A53 |
| RAM | 2 GB |
| Storage | 64 GB internal + external USB storage |
| WiFi | 2.4 GHz + 5 GHz dual-band (built-in hotspot) |
| Ethernet | Yes (10/100 Mbps) |
| USB ports | 4x USB 2.0 |
| DC power ports | 4x 12V DC outputs (for mount, camera, accessories) |
| Power input | 12V DC |
| Dimensions | 127 x 82 x 28 mm |
| Weight | ~250g |
| Operating temperature | -20°C to 40°C |

---

## Connected Equipment

| USB Port | Device | Function |
|----------|--------|----------|
| USB 1 | [[ASI2600MCPro]] | Imaging camera — capture, cooling, gain control |
| USB 2 | [[ASI385MC]] | Guide camera — autoguiding |
| USB 3 | [[ZWO-EAF]] | Autofocuser — focus control |
| USB 4 | Available | Spare (e.g., filter wheel, dew heater controller) |

| DC Port | Device | Function |
|---------|--------|----------|
| DC 1 | [[iOptron-CEM26]] | Mount power (12V) |
| Output 1 | Dew heater | 12V dew heater strip — runs at 100% |
| Output 2–4 | Available | Spare 12V outputs |

| Connection | Device | Method |
|------------|--------|--------|
| WiFi | Phone/tablet | ASIAIR app control |
| ST-4 / USB | [[iOptron-CEM26]] | Mount GoTo and tracking commands |

---

## Core Functions

### Capture

| Function | Description |
|----------|-------------|
| Single exposure | Manual single-frame capture |
| Sequence planning | Automated multi-target capture with timing |
| Exposure control | Gain, exposure time, cooling temperature, binning |
| Dithering | Random sub-pixel shifts between exposures for drizzle |
| Meridian flip | Automatic flip and re-center when target crosses meridian |
| Live preview | Real-time stretched preview during capture |

### Autoguiding

| Function | Description |
|----------|-------------|
| Internal guider | Built-in PHD2-based guiding engine |
| Calibration | Auto-calibrate guide camera to mount response |
| Multi-star guiding | Track multiple guide stars for better accuracy |
| Guide graph | Real-time RA/DEC error graph |
| Dither control | Pause guiding during dither, resume after settling |

### Autofocus

| Function | Description |
|----------|-------------|
| V-curve autofocus | Automated focus routine via [[ZWO-EAF]] |
| Periodic autofocus | Re-focus at set intervals during sequence |
| Temperature trigger | Re-focus when temperature drops beyond threshold |
| Filter offset | Store focus offsets per filter for automatic adjustment |

### Plate Solving

| Function | Description |
|----------|-------------|
| Blind solve | Identify sky position from any pointing |
| GoTo correction | Solve, correct, re-slew for precise centering |
| Polar alignment | Precise polar alignment via plate solve routine |
| Mosaic planning | Frame mosaic panels with plate-solved coordinates |

### Planning

| Function | Description |
|----------|-------------|
| Object database | Built-in catalog of deep sky objects |
| Altitude chart | Object altitude through the night |
| FOV overlay | Show camera field of view on sky map |
| Session planning | Schedule targets with start/end times |

---

## Camera Profile (Main Camera)

Configured in the ASIAIR app for [[ASI2600MCPro]]:

| Setting | Value |
|---|---|
| Camera | ZWO ASI2600MC Pro |
| Connection | USB 3.0 |
| Gain preset | Medium (M) |
| Gain value | 100 |
| Main scope focal length | 249 mm ([[RedCat-51]]) |
| Cooling target | -10 °C year-round (standardized 2026-04-19 — see note below) |
| Cooling preset buttons | -20 °C / -10 °C / 0 °C |
| Anti-dew | ON |

> **Cooling standard (2026-04-19):** -10 °C year-round, replacing the prior "-10 °C summer / -20 °C winter" rule. At Bortle 4, dark current at -10 °C is ~3 % of the LPro sky background and ~10 % of the Quad sky background — well below sky-limited noise. -20 °C bought ~1–2 % SNR and required a parallel dark library; not worth the complexity. Standardizing on -10 °C means a single dark library, faster cool-downs, and no ambient-temperature surprises.

### File Name Convention

Customized FITS file name fields enabled in the ASIAIR app:

| Field | Enabled |
|---|---|
| ASI Camera Model | ON |
| Gain | ON |
| Temperature | ON |
| Camera Angle | OFF (disabled 2026-04-19 — no Camera Angle Adjuster (CAA) in the train, so the value would be static and adds filename noise) |
| Custom Suffix | `LPro` (set 2026-04-19 for upcoming [[Optolong-LPro]] sessions; swap to `Quad` when using [[Antlia-FQuad]]) |

Resulting file name pattern (current config — angle disabled, `LPro` suffix):

```
Light_<target>_<exposure>s_Bin1_<filter>_<camera>_gain<n>_<YYYYMMDD-HHMMSS>_<temp>C_LPro_<index>.fit
```

Example shown in the app (with angle still enabled):

```
Light_M81_10s_Bin1_R_6200MM_gain100_20200327-141610_180deg_28.2C_0001.fit
```

### Advanced Camera Settings

| Setting | State | Notes |
|---|---|---|
| Auto White Balance on Screen | OFF | Preview shown without on-the-fly WB |
| Mono Bin | ON | Bin without debayering — sharper guide/preview on OSC |
| Continuous Preview | OFF | Preview only on demand |
| Turn on Cooling after Main Camera Connected | ON | Cooler ramps automatically at session start |
| Turn on Anti-dew while cooling | ON | Sensor window heater follows cooler state |

---

## Guide Profile

Configured in the ASIAIR app for [[ASI385MC]] on the [[UniGuide-32mm]]:

| Setting | Value |
|---|---|
| Guide camera | ZWO ASI385MC |
| Gain preset | High (H) |
| Gain value | 300 |
| Guide scope focal length | 120 mm (UniGuide 32 mm aperture, f/3.75) |
| Calibration Step | 1000 ms (lowered from 2000 ms on 2026-04-19 — better-sized step for [[iOptron-CEM26]]) |
| Max DEC Duration | 1500 ms (lowered from 2000 ms on 2026-04-19 — reduces DEC backlash overshoot) |
| Max RA Duration | 2000 ms |
| Auto Restore Calibration | OFF |

### Guiding Advanced Settings

| Setting | Value | Meaning |
|---|---|---|
| Guide Stability | 2" — 5 s — 60 s | Settle threshold 2", must be stable 5 s, 60 s timeout |
| Dither | 5 pixel — 1 | 5 px dither distance (raised from 2 px on 2026-04-19 — better breaks OSC walking-noise patterns); presets: 1 / 2 / 5 / 10 / 30; every 1 frame (interval customizable) |
| Dither only in RA | OFF | Dither happens in both RA and DEC (correct for OSC) |
| Dark Library | ON | Built 2026-04-19 for [[ASI385MC]], stored at `eMMC/GuidingDarkLibrary`. Rebuild only if guide camera is swapped |
| Guide Camera Bin 2 | ON | Bins guide cam 2×2 for sensitivity (effective scale ≈ 12.9 "/px) |
| Corrected Trigger Acc. (min-move) | 0.2 px | Raised from 0.1 px on 2026-04-19 — avoids chasing seeing at Bortle 4. No correction issued if guide star offset < 0.2 px |

---

## Mount Profile

Configured in the ASIAIR app for [[iOptron-CEM26]]:

| Setting | Value |
|---|---|
| Mount profile | iOptron CEM26 / GEM28 / HEM27 |
| Interface | **TCP** via the mount's WiFi-to-Serial bridge (changed 2026-05-24 from USB-Serial) |
| IP | `192.168.178.87` (mount's home-WiFi APSTA STA IP — see [[iOptron-CEM26#WiFi Configuration]]) |
| Port | `8899` TCP |
| Baud rate | n/a at ASIAIR side — the WiFi module's internal serial bridge to the 8409 HC runs 115200 8N1 (per [[iOptron-CEM26#How WiFi mount control actually works]]) |
| GoTo Auto-Center | ON (plate-solves after each GoTo for accurate framing) |
| Center EXP Time | 2 s (raise to 5–10 s for faint fields where 2 s won't solve) |
| Guiding Speed | 0.75× sidereal (higher than typical 0.5× default; watch RA RMS on calm nights) |

**Time / DST handling:** ASIAIR pushes the mount UTC offset as **+60 min (CET)** with **DST = no** *regardless of the season* and lets its own UI handle the daylight-saving display offset. The mount's stored UTC is correct — only the stored offset is normalised. ASIAIR's UI shows a "Ensure DST is disabled on Mount Hand Controller; it's normal that the time on the Mount is 1 hour earlier than local time" warning to confirm this is intentional.

> [!info] If you've been using `mount.py timesync`
> `mount.py timesync` pushes the live local offset (e.g. CEST = +120 min in summer) which ASIAIR will then overwrite back to +60 min on next connect. UTC stays correct in both cases; only the offset field differs. Don't fight this — let ASIAIR's value stand on imaging nights.

### Concurrent access with mount.py (single-client invariant — UPDATED 2026-05-24)

The previous USB-Serial setup put ASIAIR on the cable and `mount.py` on TCP — two transports converging at the 8409 hand controller's serial bus, so concurrent use produced garbled commands.

The new TCP setup puts **both clients on the same TCP port 8899**. Empirically tested 2026-05-24:

| Behaviour | Observation |
|---|---|
| Bridge accepts multiple TCP connections | ✓ confirmed |
| Commands are serialised on the serial bus | ✓ confirmed (8409 processes one at a time) |
| **Responses are broadcast to every connected TCP client** | ✓ confirmed via raw `nc` — saw ASIAIR's polls in my client's stream |
| Same-command parallel polling (both query `:GLS#`) | Usually works — both parsers succeed on either client's response |
| Different-command parallel polling (one queries `:FW1#`, other queries `:GLS#`) | Parser fails — read-until-`#` returns the wrong response format |
| Set commands (`:SG`, `:SUT`, etc.) | Last writer wins on the mount; cosmetic collisions only |

**Operational rule:** don't run `mount.py status / health / log` while ASIAIR holds the connection during an active imaging session. The mount is fine, the data stream isn't. Reserve `mount.py` for ASIAIR-off windows (pre-session check, post-session diagnostics). See [[../03_Techniques/Capture-Planning-Rules#4 MacBot operational rules]] for the full operational rule.

---

## Filter Wheel Profile

| Setting | Value |
|---|---|
| Filter wheel | None (no electronic filter wheel (EFW) in the train) |

Filters ([[Antlia-FQuad]], [[Optolong-LPro]]) are swapped manually in the imaging train between sessions or targets. The ASIAIR Custom Suffix in the file-name convention should be updated to match.

---

## Focuser Profile

Configured in the ASIAIR app for [[ZWO-EAF]] on the [[RedCat-51]]:

| Setting | Value |
|---|---|
| Focuser | EAF |
| EAF temperature (snapshot) | 30.6 °C |
| Step — Fine | 10 |
| Step — Coarse | 30 |
| Step — Limit | 13000 (max travel) |
| Step — Backlash | 90 |
| Current position (snapshot) | 9888 |
| Reverse direction | ON |

### Auto Focus Settings

| Setting | Value |
|---|---|
| Auto Focus EXP | 2 s |
| Step Size | 50 (raised from 30 on 2026-04-19 — faster V-curve at f/4.9 with no accuracy loss) |

**Run Auto Focus in Autorun / Plan:**

| Trigger | State |
|---|---|
| Before Autorun / Each Target Start | ON (enabled 2026-04-19 — guarantees fresh focus at session start) |
| After Switching Filter | ON |
| After Auto Meridian Flipped | ON (enabled 2026-04-19 — focus shift from post-flip flexure is real on the RedCat 51) |
| Every X Hours | OFF |
| X °C Change | ON — threshold 2 °C (presets: 1 / 2 / 5) |

**Run Auto Focus in Live:**

| Trigger | State |
|---|---|
| Before Live Start | OFF |
| Every X Hours | OFF |
| X °C Change | OFF |

> Note from the app: "Before Autorun / Each Target Start" does not take effect after resume from shooting. "X °C Change" and "Every X hour" reference the last EAF record.

---

## Files & Storage

Snapshot from the ASIAIR app on 2026-04-19:

| Storage | Capacity | Used | Notes |
|---|---|---|---|
| eMMC (internal) | 29.1 GB | 9.1 GB (~31%) | Holds ASIAIR OS, capture buffer, `GuidingDarkLibrary/` |
| SD Card | 238.3 GB | 0.0 GB | Inserted but shows lock icon — write protection or unformatted; investigate before relying on it |

External USB SSD/HDD remains the primary capture target — eMMC is used as a buffer and for the ASIAIR's own files (OS, dark libraries, logs).

**Other Files-tab items:** Images Management, Capture Logs (Autorun & Plan), and post-stacking presets (Solar Surface / Lunar Surface / Planet / DSO Stacking) for quick on-device previews.

---

## App / Firmware

Snapshot from the ASIAIR **About** tab on 2026-04-19:

| Item | Value |
|---|---|
| Firmware version | 2.5.2 (13.41) |
| Firmware status | Up to Date |
| All Sky Polar Align (experimental) | ON |
| New Plate Solve (experimental) | ON |

**All Sky Polar Align** is enabled — does plate-solve-driven polar alignment without needing to point near Polaris. Critical for the [[Dark-Sky-Sites|Tuntange balcony]] when Polaris is blocked by the building.

**New Plate Solve** uses ASIAIR's updated solver — faster and more reliable than the legacy engine, especially in star-poor fields.

---

## Imaging Workflow

The ASIAIR orchestrates the entire session after initial setup:

1. **Power on** — connect via ASIAIR app on phone/tablet
2. **Cool camera** — set [[ASI2600MCPro]] to target temperature (-10°C or -20°C)
3. **Polar alignment** — plate-solve assisted polar alignment
4. **GoTo target** — slew to first target, plate solve, center
5. **Autofocus** — run V-curve autofocus via [[ZWO-EAF]]
6. **Start guiding** — calibrate and start autoguiding with [[ASI385MC]]
7. **Start sequence** — automated capture with dithering
8. **Monitor** — check guide graph, preview subs on phone
9. **Target change** — ASIAIR slews, re-centers, re-focuses, re-guides automatically
10. **Meridian flip** — automatic when target crosses meridian

---

## Data Storage

| Storage | Use |
|---------|-----|
| Internal 64 GB | Session data buffer — transfer to external after session |
| USB SSD/HDD | Primary storage — FITS files written directly |
| MicroSD | Not available on Plus model |

FITS files are stored organized by date and target. Transfer to PC for processing in PixInsight (see [[RGB-Workflow]] or [[QuadBand-OSC-Workflow]]).

### File Sizes (ASI2600MC Pro)

| Format | Per frame | 100 frames |
|--------|-----------|------------|
| FITS 16-bit | ~50 MB | ~5 GB |
| FITS 16-bit + drizzle data | ~50 MB | ~5 GB |

A typical session (150–200 frames) generates 7–10 GB of data.

---

## WiFi Configuration

| Mode | SSID | Use Case |
|------|------|----------|
| Hotspot (default) | `ASIAIR_bcaaf0b1` (2.4 GHz) | ASIAIR creates its own WiFi network — connect phone directly |
| Station mode | `BleiftDoheem` (home) | ASIAIR joins home WiFi — accessible from any device on network |

**Hotspot mode** is standard for field use. **Station mode** is configured for balcony imaging at home (Tuntange) — allows control from inside while the rig is on the balcony.

### Typical Power Draw

Observed at the panel during imaging with mount + camera + dew heater at 100%:

| Metric | Value |
|---|---|
| Input voltage | 11.6 V |
| Input current | 1.7 A |
| Total power | 19.7 W |
| CPU temperature | 33.1 °C |

---

## Characteristics

### Strengths

- **All-in-one control** — replaces laptop + multiple software packages
- **Wireless operation** — control from phone/tablet, no cables to trip over
- **Integrated power distribution** — 4x 12V DC outputs reduce cable clutter
- **Automated workflow** — sequence, guide, focus, dither, meridian flip all handled
- **Low power** — runs on 12V, no laptop battery drain
- **Cold-weather resistant** — operates to -20°C

### Limitations

- **ZWO ecosystem** — best with ZWO cameras; third-party camera support is limited
- **USB 2.0 only** — slower file transfer than USB 3.0 (adequate for imaging, slow for bulk transfer)
- **No advanced processing** — capture only; all processing done on PC in PixInsight
- **Phone app only** — no desktop app; must use phone/tablet for control
- **WiFi range** — hotspot range ~10–15m; walls reduce this significantly
- **No ASCOM** — uses its own protocol; not compatible with ASCOM-based software chains

---

## Resources

- [ZWO ASIAIR](https://www.zwoastro.com/product/asiair/)
- [ASIAIR user manual (PDF)](01_Equipment/Manuals/ASIAIR/Manuals/ZWO_ASIAIR_PRO_User_Manual.pdf)
- [ASIAIR quick guide (PDF)](01_Equipment/Manuals/ASIAIR/Manuals/ZWO_ASIAIR_Quick_Guide.pdf)
- [ASIAIR user manual (original) (PDF)](01_Equipment/Manuals/ASIAIR/Manuals/ZWO_ASIAIR_User_Manual.pdf)
- [How to restore ASIAIR OS (PDF)](01_Equipment/Manuals/ASIAIR/Manuals/How_to_Restore_ASIAIR_OS.pdf)
