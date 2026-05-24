---
title: "iOptron CEM26"
type: equipment
category: mount
brand: "iOptron"
model: "CEM26"
status: active
purchase_date: 2022-09-16
purchase_price: "1,285.76 €"
purchase_store: "Astroshop"
purchase_url: "https://www.astroshop.eu"
tags:
  - equipment/mount
---

# iOptron CEM26

Center-balanced equatorial mount. Primary mount for deep sky imaging with the [[RedCat-51]] + [[ASI2600MCPro]] rig.

- [iOptron product page](https://www.ioptron.com/product-p/c261b1.htm)

---

## Specifications

### Mechanical

| Specification | Value |
|---------------|-------|
| Mount type | Center-Balanced Equatorial (CEM) |
| Payload capacity | 12 kg (26 lbs), excluding counterweight |
| Mount weight | 4.5 kg (10 lbs) |
| Payload/weight ratio | 2.60 |
| Structure | All metal, casting + CNC machined |
| Dovetail saddle | 3.8" Vixen-style, center adjustable |
| Counterweight | 4.5 kg (10 lbs) |
| Counterweight shaft | 20mm x 200mm + 120mm extension (M16, stainless steel) |
| Tripod | 1.5" stainless steel (5 kg) |
| Operating temperature | -10°C to 40°C |

### Drive System

| Specification | Value |
|---------------|-------|
| Motor | 1.8° stepper motor, 128x microdivision |
| Resolution | 0.17 arcsec |
| Transmission | Synchronous belt |
| Periodic error (PE) | < ±12 arcsec |
| PEC | Permanent PEC |
| Worm period | 600 sec |
| RA/DEC worm wheels | 88mm, 144 teeth, aluminum |
| RA/DEC worm gears | 15.2mm, brass |
| RA/DEC axis shafts | 35mm steel |
| RA/DEC bearings | 55mm ball bearings |

### Tracking & Slewing

| Specification | Value |
|---------------|-------|
| Tracking | Automatic (sidereal, lunar, solar, custom) |
| Slew speeds | 1x, 2x, 8x, 16x, 64x, 128x, 256x, 512x, MAX (6°/sec) |
| GoTo database | ~212,000 objects (Go2Nova 8409 hand controller) |

### Alignment

| Specification | Value |
|---------------|-------|
| Latitude adjustment | 0° to 60° |
| Azimuth adjustment | ±6° |
| Polar scope | AccuAlign optical polar scope |
| Level indicator | Bubble level |

### Connectivity

| Port | Type |
|------|------|
| WiFi | Built-in (APSTA mode — see [[#WiFi Configuration]]) |
| USB | Mount control (USB-Serial via Go2Nova 8409, 115200 8N1, no flow control — verified via WiFi module web admin 2026-05-24) |
| Autoguide | ST-4 compatible |
| Hand controller | Go2Nova 8409 |
| PC control | ASCOM compatible |

### Power

| Specification | Value |
|---------------|-------|
| Input | 12V DC, 5A |
| Tracking consumption | 0.5A |
| GoTo consumption | 0.8A |
| AC adapter | 100V–240V (included, indoor use only) |
| Power-down memory | Yes |

---

## Current Payload

| Component | Weight |
|-----------|--------|
| [[RedCat-51]] (OTA + ring + dovetail) | 1.76 kg |
| [[ASI2600MCPro]] | ~0.9 kg |
| [[ZWO-EAF]] | 0.28 kg |
| [[UniGuide-32mm]] + [[ASI385MC]] | ~0.5 kg |
| Filter + adapters | ~0.2 kg |
| **Total** | **~3.6 kg** |
| **Capacity remaining** | **~8.4 kg (70% headroom)** |

The imaging rig is well under the 12 kg limit, leaving significant margin for stability.

---

## Characteristics

### Strengths

- **Center-balanced design** — lower moment of inertia than German equatorial, better tracking and less vibration
- **Lightweight** — 4.5 kg mount head, portable for field use
- **High payload ratio** — 2.6:1 ratio, current rig uses only 30% of capacity
- **Built-in WiFi** — wireless control via ASIAIR or iOptron Commander
- **Permanent PEC** — periodic error correction survives power cycles
- **ST-4 autoguide port** — direct guiding connection for [[ASI385MC]]
- **0.17 arcsec resolution** — fine enough for any imaging scale

### Limitations

- **Periodic error ±12 arcsec** — requires autoguiding for exposures > 30s at 3.1"/pixel
- **Latitude range 0–60°** — Tuntange at 49.6°N is within range but near the upper limit
- **Alt-az head not included** — equatorial only
- **No encoder option on base model** — CEM26EC variant has encoders

---

## Guiding Performance

At 3.1"/pixel ([[RedCat-51]] + [[ASI2600MCPro]]):

| Parameter | Value |
|-----------|-------|
| Max acceptable guide error | ~1.5" RMS (half pixel) |
| Unguided PE | ±12" (unusable for long exposures) |
| Guided PE (typical) | < 1" RMS with [[ASI385MC]] + [[UniGuide-32mm]] |
| Worm period | 600s — guide loop must correct within this cycle |

Autoguiding is **mandatory** for deep sky imaging at this focal length.

---

## Setup Procedure

1. Level tripod (bubble level)
2. Rough polar alignment (AccuAlign polar scope or iPolar)
3. Attach counterweight, balance RA axis
4. Attach imaging rig, balance DEC axis
5. Precise polar alignment via plate solving ([[ASIAIR]])
6. Star alignment (2–3 star or plate solve)
7. Start autoguiding ([[ASI385MC]] + [[UniGuide-32mm]])
8. Verify tracking with test exposure

See also: [[EAF-Workflow]] for the complete imaging session procedure.

---

## WiFi Configuration

The mount's built-in WiFi (via the Go2Nova 8409 hand controller, HBX8409 module) is configured in **APSTA mode** — it simultaneously broadcasts its own access point AND joins the home WiFi as a station. This is configured via the module's hidden web admin (not exposed in iOptron's official UI).

> [!warning] Community knowledge — not iOptron-supported
> APSTA / STA configuration is done via the underlying USR-WIFI232-class module's web admin (Web Ver 1.0.14 as of 2026-05-24). iOptron's official manual only exposes AP mode. An iOptron firmware update *may* wipe these settings — re-apply if so. Worst-case recovery: 8409 hand controller § 5.4.10 → Wi-Fi Option → **Restore to Factory** reverts to AP-only on `10.10.100.254`.

### Current configuration (2026-05-24)

| Mode | Network | IP | Status |
|---|---|---|---|
| **AP (fallback)** | `HBX8409_DF5E72` (WPA2PSK / AES, secured 2026-05-24) | `10.10.100.254` | Always available — connect directly to this SSID if home WiFi is down |
| **STA (home)** | `BleiftDoheem` | **`192.168.178.87`** | DHCP reservation pinned on Fritz!Box → permanent. Signal 88%. |

WiFi module MACs: AP `30:EA:E7:DF:5E:72`, STA `34:EA:E7:DF:5E:72`.
Mount control port: **`8899`** (same on both interfaces).
TCP idle timeout: 300 s (5 min) — clients that go silent longer than this get disconnected and must reconnect.

### How WiFi mount control actually works

The WiFi module is a **TCP-to-Serial bridge** — it doesn't speak the mount protocol itself; it just forwards bytes:

```
[SkySafari / iOptron Commander] ──TCP :8899──> [WiFi Module] ──Serial 115200 8N1──> [Go2Nova 8409 HC] ──> [Mount]
```

A client opens a TCP connection to `192.168.178.87:8899` (or `10.10.100.254:8899` over the AP) and sends raw RS-232 commands like `:GLS#`, `:GUT#`, `:GAC#` exactly as documented in the iOptron RS-232 Command Language V3.10. Responses come back over the same TCP stream. No HTTP, no API key, no JSON — just byte-for-byte serial passthrough.

That's why **Other Setting** parameters must not be changed: the serial parameters (115200 8N1, no flow control) are fixed by the 8409 hand controller's firmware. Mismatching them breaks the WiFi bridge.

### Client app configuration

For control from any device on the home WiFi:

| App                   | Setting                                                                                                         |
| --------------------- | --------------------------------------------------------------------------------------------------------------- |
| **SkySafari Pro**     | Setup → IP `192.168.178.87`, Port `8899`, Scope Type `iOptron CEM-120`, Mount Type `Equatorial GoTo (German)`   |
| **iOptron Commander** | Connection Settings → Wi-Fi/Ethernet → Custom IP `192.168.178.87`, Port `8899`                                  |
| **ASIAIR**            | **N/A** — ASIAIR connects via USB-Serial 115200 8N1 (not WiFi). Mount profile: "iOptron CEM26 / GEM28 / HEM27". |

### Web admin access

The underlying WiFi module exposes a web admin (Web Ver 1.0.14) reachable from either interface:

| From | URL | Notes |
|---|---|---|
| Home WiFi (via STA) | `http://192.168.178.87/` | Works from any device on `BleiftDoheem` |
| Direct AP (fallback) | `http://10.10.100.254/` | Connect device to `HBX8409_DF5E72` first |

Default login: `admin / admin`.

> [!warning] Security — change the default admin credentials
> The default `admin / admin` login means anyone on `BleiftDoheem` who knows the IP can reach the WiFi module's admin and potentially break the mount's connectivity (or worse — reflash firmware via Upgrade SW). To lock it down: web admin → **Account** → set a strong password.
>
> ✅ **AP fallback now WPA2PSK-secured** (2026-05-24) — the `HBX8409_DF5E72` SSID requires a password to join. Web admin password lockdown is the remaining outstanding step.

### Re-applying APSTA configuration if lost

Reach the web admin via either IP above (use the AP `10.10.100.254` if STA is broken). Default login `admin / admin` unless changed.

1. **Work Mode** → select `AP+STA mode` → Save
2. **STA Setting** → Scan → pick `BleiftDoheem` → Encryption `WPA2PSK / AES` → enter password → DHCP `Enable` → Save
3. **(Optional) AP Setting** → add a WPA2 password to lock down `HBX8409_DF5E72` (currently open)
4. **(Optional) Account** → change web admin from `admin / admin`
5. **Restart** → ~30 s reboot → verify System page shows both AP Mode and STA Mode populated

Then on Fritz!Box (`http://fritz.box` → Heimnetz → Netzwerk), find MAC `34:EA:E7:DF:5E:72` and check "Diesem Netzwerkgerät immer die gleiche IPv4-Adresse zuweisen" to keep `192.168.178.87` permanently.

### When this WiFi setup matters

- **At home (Tuntange):** lets you control the mount directly from any device on home WiFi via SkySafari or iOptron Commander — bypasses ASIAIR if ASIAIR fails or for quick standalone diagnostics
- **Portable trips:** STA is moot away from home — only the `HBX8409_DF5E72` AP applies. Mount still reachable at `10.10.100.254` via that AP.
- **ASIAIR sessions:** WiFi is unused — ASIAIR uses USB-Serial 115200. Disabling WiFi entirely would save a few mA of mount power consumption but isn't necessary.

---

## Firmware & Software

### Firmware

- [CEM26/GEM28 Firmware updates](https://www.ioptron.com/Articles.asp?ID=333)
- After firmware upgrade: set mount to zero position using "Set Zero Position"
- CEM26EC/GEM28EC: perform encoder calibration after upgrade

#### Locally cached files (`01_Equipment/Manuals/CEM26/Firmware/`)

| File | Purpose |
|---|---|
| `CEM26_GEM28_FW241201.bin` | **Latest firmware** (Dec 2024) — HC V241201, RA V240518, DEC V230305. Fixes communication overflow. Cached 2026-05-24 from iOptron. |
| `CEM26_GEM28_FW210422.bin` | Legacy firmware (Apr 2021) — kept as rollback safety. HC V210422, RA/DEC V210420. |
| `CEM26_GEM28_FirmwareUpgradeInstruction.pdf` | iOptron's upgrade procedure (unchanged since 2021). |
| `CEM26_GEM28_FirmwareVersionHistory.pdf` | Full version change log V20201030 → V20241201. |
| `iOptronUpgradeUtility223.exe` | Upgrade tool V2.23 (still current per iOptron). |
| `FTDI_VCP21214_Setup_Win7_8_10.exe` | Required USB-Serial driver (Windows). |

#### Installed version (verified 2026-05-24 via `:FW1#` + `:FW2#` over WiFi TCP bridge)

| Component | Installed | Latest available | Gap |
|---|---|---|---|
| Hand Controller | **V230305** (2023-03-05) | V241201 | ~21 months — V241201 fixes communication overflow |
| Main board | V230305 | — | (returned by `:FW1#` second field) |
| RA motor | V210420 (2021-04-20) | V240518 | ~37 months — V240518 fixes "Go to SUN" (irrelevant) |
| DEC motor | V230305 | V230305 | ✅ already current |

Installed bundle matches the **V20230305 release** (HC V230305, RA V210420, DEC V230305). The locally-cached `FW210422.bin` was therefore never installed — V20230305 was applied instead at some point.

#### Update policy

iOptron's official stance: *"No firmware upgrade is needed if your mount works properly."* For this rig, the only meaningful gain from upgrading to V241201 is the **HC communication-overflow fix** (could affect ASCOM/serial reliability over long ASIAIR sessions). RA's "Go to SUN" fix is irrelevant for astro imaging; DEC is already current.

**Update procedure is Windows-only:**
1. Confirm installed version (already done — see table above)
2. Windows PC + FTDI driver + Upgrade Utility V2.23 + USB cable from PC to 8409 hand controller
3. Follow `CEM26_GEM28_FirmwareUpgradeInstruction.pdf` exactly
4. Post-upgrade: "Set Zero Position" via hand controller

To re-verify installed version any time (from any device on home WiFi):
```bash
python3 scripts/mount.py firmware   # parsed report + gap analysis vs latest
```

Or the raw equivalents (no Python required):
```bash
(printf ':FW1#'; sleep 3) | nc -w 5 192.168.178.87 8899   # → HC + Main board dates
(printf ':FW2#'; sleep 3) | nc -w 5 192.168.178.87 8899   # → RA + DEC motor dates
```

---

## Mount Control Script (`scripts/mount.py`)

Standalone CLI for **read-only diagnostics and safe config** over the WiFi-to-Serial bridge, independent of [[ASIAIR]]. **Cannot slew the mount** — `goto` and `park` were removed 2026-05-24 after an incident in which a chained slew sequence drove the bare mount into a hard mechanical limit (mount's internal coords had desynced from the OTA's physical position after repeated power cycles, and the script had no way to detect that). See [[../../03_Techniques/Mount-Diagnostics.md#Removed-goto-and-park]] for the full rationale and what safety gates would need to be added before either subcommand could be safely re-introduced.

For any slewing (GoTo, park, re-pointing), use **ASIAIR** (USB-Serial) or the **8409 hand controller** directly.

| Subcommand | Purpose | Moves mount? |
|---|---|---|
| `status [--watch [N]]` | Print parsed mount state (RA/Dec, alt/az, tracking, parked/slewing) | No |
| `health` | Pre-session readiness check; exit 0/1 | No |
| `firmware` | Installed firmware + gap analysis vs latest | No |
| `unpark` | Clear parked flag + start sidereal tracking | Only the slow ~15"/sec sidereal drift |
| `timesync` | Push host UTC/DST/offset to mount | No (config write only) |
| `log [--session FILE] [--interval N]` | NDJSON telemetry logger beside the capture-session note | No |

Run from repo root: `python3 scripts/mount.py <subcommand>`. See [[../../scripts/README.md]] for the per-subcommand reference and [[../../03_Techniques/Mount-Diagnostics.md]] for the workflow guide.

Stdlib-only (no `pip install` needed). Tested via `python3 -m unittest scripts.test_mount` (parser + mock tests, no mount needed) and `MOUNT_TEST_LIVE=1 python3 -m unittest scripts.test_mount` (live read-only integration).

### Mac Mini as logging station

The always-on Mac Mini (`192.168.178.91`) clones this repo and runs MacBot — see [[../../03_Techniques/Mount-Diagnostics.md#Session-driven-logging-via-MacBot]]. iMessage triggers expose `mount status`, `mount log start/stop`, and **session-driven scheduling** that reads the Start/End times from a capture-session note's Planning table and auto-runs `mount.py log` for that window. Three throttled iMessage alerts (`mount_unreachable`, `tracking_stopped`, `meridian_flip`) come from MacBot tailing the live NDJSON log for `kind: "event"` records. Since the MacBook is typically asleep during night sessions, the Mac Mini is the practical logging host.

### iPolar Software

- [iPolar download](https://www.ioptron.com/product-p/c261b1.htm)
- Electronic polar alignment tool (alternative to optical polar scope)

Software in `01_Equipment/Manuals/CEM26/iPolar-Software/`.

### ASCOM Driver & iOptron Commander

- [ASCOM Driver download](https://www.ioptron.com/Articles.asp?ID=332)
- Uses RS-232 command language 2014 V3.x
- Requirements: Windows 7 SP1+ with .NET Framework 4.8, ASCOM Platform 6.5 SP1+

Driver files in `01_Equipment/Manuals/CEM26/ASCOM-Driver/`.

---

## Accessories

| Accessory | Purpose |
|-----------|---------|
| [[iOptron-LiteRoc-Tripod\|iOptron LiteRoc Tripod]] | Dedicated tripod for CEM26/GEM28 |
| [[Omegon-Anti-Vibration-Pads\|Omegon Anti-Vibration Pads]] | Dampen vibrations under tripod legs |

---

## Resources

- [iOptron CEM26 product page](https://www.ioptron.com/product-p/c261b1.htm)
- [CEM26 manual (PDF)](01_Equipment/Manuals/CEM26/Manual/C26_CEM26_Manual.pdf)
- [CEM26 quick start guide (PDF)](01_Equipment/Manuals/CEM26/Manual/C26_CEM26_QSG.pdf)
- [iPolar operation manual (PDF)](01_Equipment/Manuals/CEM26/Manual/3339_iPolarOperationManual.pdf)
- [RS-232 command language (PDF)](01_Equipment/Manuals/CEM26/ASCOM-Driver/RS-232_Command_Language2014V310.pdf)
