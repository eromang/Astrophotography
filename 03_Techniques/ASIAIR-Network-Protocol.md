---
title: "ASIAIR Network Protocol"
type: technique
tags:
  - technique
  - technique/networking
---

# ASIAIR Network Protocol

Reverse-engineering notes for the [[ASIAIR]] Plus (firmware 2.5.2 / 13.41) LAN surface. Captured 2026-05-25 from active probing against the unit at `192.168.178.84` on the home network. Purpose: identify which ports are usable for custom tooling so any future "external logging / monitoring" project picks the right door instead of fighting the proprietary app channel like the torn-down MacBot integration did.

This note complements [[ASIAIR]] (the equipment spec) and [[Mount-Diagnostics]] (the operational counterpart that runs against the mount's WiFi bridge, not the ASIAIR).

---

## Open ports — full picture

`nmap -Pn -sV` against the top 1000 ports shows 22, 139, 445, 4900, 8888 — but the ZWO-specific RPC and INDI services sit on high ports outside that range. Targeted scan of 4350/4360/4400/4500/7624/8888 reveals the actual control surface:

| Port | Service | State | Use |
|---|---|---|---|
| 22 | SSH (OpenSSH 7.9p1 Raspbian) | open | Password auth removed by ZWO. Legitimate access requires SD-card SSH key injection. |
| 139 / 445 | Samba (smbd 3.x/4.x, WORKGROUP) | open | File share for retrieving captured FITS via SMB. Standard mount from macOS Finder works. |
| 4350 | **ZWO JSON-RPC 2.0** (OTA / updater channel) | open | Documented in `joshumax/asiair` and `Oxofrimbl/asiair`. Used by firmware updates. |
| 4360 | Binary OTA file upload | open | Companion to 4350 — receives the raw firmware blob. |
| 4400 | Unknown ZWO service | open | Not probed. |
| 4500 | Unknown ZWO service | open | Not probed. |
| 4900 | **ZWO usage statistics push** | open | One-way push: server sends `{"Event":"Version","name":"zwoair_usage_statistics_handler",...}` JSON lines unsolicited. Telemetry-only. |
| 7624 | **Standard INDI server** | open while mount profile active | Exposes **only** the `iOptronV3` mount driver (no camera / focuser / guide cam). **The ASIAIR app uses this INDI server internally** — proven 2026-05-25 by observing app arrow-press events on a passive listener. INDI is the single arbiter of the mount bus. **Server stays running for the full session window** even when the app is closed, as long as the mount profile is active. See § Port 7624. |
| 8888 | Proprietary ASIAIR app control | open | Silent on connect, RSTs on every structured probe (JSON-RPC, length-prefixed JSON, TLS, raw event JSON). Binary handshake; not reverse-engineered in public sources. |

---

## Port 7624 — INDI server (the actual mount control plane)

Standard INDI XML protocol. `<getProperties version="1.7"/>\n` returns a 7.9 KB property tree on the dormant unit (ASIAIR app not running) or a 20.8 KB tree when the iOptronV3 driver is connected to the mount (after the app activates the mount profile).

**Devices exposed: 1.** Only `iOptronV3`. No camera, no focuser, no guide cam. The ZWO devices (ASI2600MC, ASI385MC, ZWO-EAF) are held by the ASIAIR app directly via USB — they don't register with the INDI server even when the app is running.

**iOptronV3 property tree (17 vectors)**, captured with `CONNECT=Off`:

| Property | Group | Type | Perm | State | Value |
|---|---|---|---|---|---|
| `CONNECTION` | Main Control | Switch | rw | **Alert** | CONNECT=Off, DISCONNECT=On |
| `DRIVER_INFO` | Connection | Text | ro | Idle | name=`iOptronV3`, exec=`indi_ioptronv3_telescope`, v1.1, interface=5 |
| `CONNECTION_MODE` | Connection | Switch | rw | Ok | **TCP=On**, SERIAL=Off |
| `DEVICE_ADDRESS` | Connection | Text | rw | Ok | **`192.168.178.87:8899`** |
| `CONNECTION_TYPE` | Connection | Switch | rw | Ok | TCP=On, UDP=Off |
| `POLLING_PERIOD` | Options | Number | rw | Ok | 1000 ms |
| `DEBUG` | Options | Switch | rw | Ok | DISABLE=On |
| `SIMULATION` | Options | Switch | rw | Idle | DISABLE=On |
| `CONFIG_PROCESS` | Options | Switch | rw | Idle | (load/save/default/purge) |
| `ACTIVE_DEVICES` | Options | Text | rw | Ok | ACTIVE_GPS=GPS Simulator, ACTIVE_DOME=Dome Simulator |
| `DOME_POLICY` | Options | Switch | rw | Ok | NO_ACTION=On |
| `TELESCOPE_INFO` | Options | Number | rw | Ok | APERTURE=0, FOCAL=0, GUIDER_APERTURE=0, GUIDER_FOCAL=0 *(not pre-populated)* |
| `SCOPE_CONFIG_NAME` | Options | Text | rw | Ok | *(empty)* |

The actual mount-state properties (`EQUATORIAL_EOD_COORD`, `HORIZONTAL_COORD`, `TRACK_STATE`, `MOUNT_PARK`, `PIER_SIDE`, `TIME_UTC`, `GEOGRAPHIC_COORD`) only appear **after** `CONNECT=On` is sent — INDI drivers don't publish runtime properties until connected.

### Test #1 result (2026-05-25): CONNECT=On works when no other client is on the bridge

With the ASIAIR app closed, sending `<newSwitchVector device="iOptronV3" name="CONNECTION"><oneSwitch name="CONNECT">On</oneSwitch>...` to port 7624 succeeded cleanly:

- `CONNECTION` state transitioned **Alert → Ok**
- Driver emitted `[INFO]` messages: *"Connecting to 192.168.178.87@8899"*, *"iOptronV3 is online"*, *"Mount UTC: 2022-03-01T00:03:19"* (RTC drift — see § Notable findings), *"Mount Location: Lat 49:43:02 - Long 6:00:30"* ✓, *"Mount is unparked"*
- Property tree expanded from **17 vectors → 43 unique vectors** — full runtime mount control surface published
- `DISCONNECT=On` cleanly returned to Idle

The new runtime vectors include the actually-useful mount state: `EQUATORIAL_EOD_COORD` (RA/Dec JNow), `TELESCOPE_TRACK_STATE`, `TELESCOPE_PARK`, `TELESCOPE_PIER_SIDE`, `TIME_UTC`, `GEOGRAPHIC_COORD`, `TELESCOPE_TIMED_GUIDE_NS/WE` (pulse guide), `TELESCOPE_MOTION_NS/WE` (continuous jog), `TELESCOPE_ABORT_MOTION`, `TELESCOPE_SLEW_RATE`, `TELESCOPE_TRACK_MODE`, `GUIDE_RATE`, `CWState` (counterweight up/normal), `Slew Type`, `HEMISPHERE`, `HOME`, `GPS_STATUS`, `Firmware Info`.

### Test #2 result (2026-05-25): the ASIAIR app uses this INDI server internally

This was the architecturally critical question — and it answered cleanly in INDI's favour.

A passive INDI listener attached during an active app session captured the user's arrow-press events in real time:

```
[12:30:40] TELESCOPE_MOTION_WE  MOTION_EAST=On    (Busy)  ← app: East arrow pressed
[12:30:45] TELESCOPE_MOTION_WE  all Off           (Idle)  ← app: released
[12:30:46] TELESCOPE_MOTION_NS  MOTION_SOUTH=On   (Busy)  ← app: South arrow
[12:30:53] both MOTION vectors  all Off                   ← app: released
[12:30:56] TELESCOPE_MOTION_NS  MOTION_NORTH=On   (Busy)  ← app: North arrow
```

Driver messages matched exactly: *"Moving toward East"*, *"East motion stopped"*, *"Moving toward South"*, *"Moving toward North"*. Every button-press in the app surfaced as an INDI property change at the passive listener within ~1 second.

**The ASIAIR app does not have a separate channel to the mount.** It goes through the same INDI server that any external client can attach to.

### Architecture (corrected)

| Layer | Reality |
|---|---|
| **Mount WiFi bridge `.87:8899`** | Exactly ONE TCP client active: the ASIAIR's INDI server. No broadcast collisions at this layer when the app is running. |
| **INDI server `.84:7624`** | Multiplexes many INDI clients (the app + any external client) cleanly via pub/sub. The server is the arbiter. |
| **External INDI client** (e.g. `pyindi-client`) | Peer-clean — sees the same property stream the app produces, without competing for the serial bus. |
| **`mount.py`** | Opens its OWN TCP socket to `.87:8899`. Becomes a *second* client on the WiFi bridge alongside the INDI server → re-creates the broadcast-bridge collision problem. Single-client invariant still applies *to this transport-layer path*. |

The earlier draft of this note ("INDI is just a proxy that competes with the app") was wrong. The proxy framing collapsed the moment test #2 showed the app's events arriving in INDI — the app and the INDI server are the same TCP client on the bridge.

### INDI server lifecycle (corrected 2026-05-25 after app-closed test)

The INDI server on port 7624 is **not always-on**, but its lifecycle is tied to the **mount profile state**, not to whether the app is foregrounded. Empirically observed lifecycle:

| Event | INDI server (port 7624) | iOptronV3 driver |
|---|---|---|
| ASIAIR power-on, app never opened | Down / on-demand spawn only | Not loaded |
| User opens app + connects mount profile | **Spawned** | **CONNECT=On**, polling mount every 1000 ms |
| User closes the app (mount profile stays active) | **Stays running** ✓ | **Stays CONNECT=On** ✓ |
| User reopens the app | Same server, app re-attaches as INDI client | Continues uninterrupted |
| User toggles mount profile OFF in app | Likely exits when the last INDI client disconnects | DISCONNECT=On |
| External client sends DISCONNECT=On then closes socket (test #1 cleanup) | Server exits | DISCONNECT=Off, driver unloaded |
| ASIAIR power cycle | Down until next mount-profile activation | — |

**The critical correction:** the *app being open* is not the predicate for INDI availability — the *mount profile being active* is. The user's real workflow (open app at session start to slew + configure, close app, ASIAIR runs autonomously for hours, reopen briefly to check, finally toggle off + shutdown) keeps the mount profile active for the entire session window. INDI is alive and the driver is connected for that whole span, including the long "app closed" stretches.

**Practical implication for an external monitor**: a Mac Mini `pyindi-client` subscriber works for the full session duration — *not* limited to brief windows when the user has the app foregrounded. The retry-with-backoff is only needed at session start (waiting for the user to activate the mount profile for the first time, which spawns INDI).

### What this unlocks

A Mac Mini external mount logger using `pyindi-client` becomes the **architecturally-correct replacement** for the torn-down [[Mount-Diagnostics#Historical note: Mac Mini / MacBot integration attempted + torn down 2026-05-24|May-24 MacBot mount integration]]. Properties to subscribe to:

- `TELESCOPE_TRACK_STATE` — detect unexpected tracking stop
- `TELESCOPE_PARK` — detect park events
- `TELESCOPE_PIER_SIDE` — detect meridian flips (West ↔ East transitions)
- `CONNECTION` — detect mount-driver disconnect (probably == mount comm loss)
- `EQUATORIAL_EOD_COORD` — record position changes (slews) without polling
- `TELESCOPE_TIMED_GUIDE_NS/WE` — observe guiding pulse rate (a live signal of guider activity)

Event-driven via pub/sub. No polling. No competition for the WiFi bridge. The previously-discovered 25% false-event rate from `mount.py log` collisions does not re-occur because there is no second TCP client on the bridge.

### What INDI does NOT give us

- **No camera control**. ZWO ASI cameras are USB-attached and held by the app directly; no `ASI2600MC` device registers with INDI.
- **No focuser control**. ZWO EAF same story.
- **No guide camera control**. ASI385MC same.
- **No sequence engine / plate solver / polar align / autofocus**. Those are app-internal logic on top of the mount channel.
- **No always-on availability** between sessions. INDI exits when the mount profile is toggled off. See the lifecycle table above.

External tooling is **mount-only** and **session-window-only** — but the session window is the full duration the user has the mount profile active, not just when the app is foregrounded.

### When NOT to use INDI clients

If `mount.py` (raw `:GLS#` on `.87:8899`) is needed for a specific diagnostic (e.g. firmware version read with no app running), the [[Capture-Planning-Rules#4. Single-client invariant — `mount.py` vs ASIAIR|single-client invariant]] applies at the WiFi-bridge layer: don't run `mount.py` while the INDI server is also connected to the mount (which happens whenever the app's mount profile is on). The clean window is "app fully disconnected from mount" — then `mount.py` has the bridge to itself.

---

## Port 4350 — JSON-RPC for ASIAIR-specific operations

Confirmed working. Open a TCP socket and the server greets:

```
{"Event":"Version","Timestamp":"2024.786866013","name":"ASI AIR updater","svr_ver_string":"1.6","svr_ver_int":6}\r\n
```

The service identifies as **ASI AIR updater** — this is the OTA / firmware-update RPC, not the main app control. Methods follow JSON-RPC 2.0 with `\r\n` framing. Sending an unknown method returns a clean structured error:

```
→ {"id":1,"method":"get_version","params":[]}\r\n
← {"jsonrpc":"2.0","Timestamp":"2024.792111508","error":"method not found","code":103,"id":1}\r\n
```

Known working methods (from `joshumax/asiair/jailbreak.py`):

| Method | Purpose |
|---|---|
| `begin_recv` | Initiates firmware blob upload; expects `params:[{file_len, file_name, run_update, md5}]`, then the blob is pushed over the parallel 4360/4361 binary socket |

`begin_recv` triggers `run_update: true` execution which runs the uploaded `update_package.sh` as root — this is the jailbreak vector (write `pi:raspberry` to /etc/shadow). **Do not invoke** outside controlled experimentation on a known-restorable unit.

### Method enumeration result (2026-05-25)

20 plausible method names probed (introspection patterns + ZWO-specific guesses) — **all 20 returned `code:103, "method not found"`**:

```
system.listMethods, rpc.discover, list_methods, get_methods, help,
version, get_status, status, ping, get_device_info, get_version_info,
get_disk_info, get_app_state, get_setting, scan_air, get_air_devices,
get_camera_info, get_mount_info, get_focuser_info, list_devices
```

No introspection method exists either (so the full method list can't be enumerated without source-level access — the iOS app's traffic would have to be captured to discover what it actually calls). The greeting's "ASI AIR updater" self-identification is literal: this endpoint exists for ZWO's firmware updater and nothing else.

**Use case for legitimate tooling: none.** Everything actionable is on 7624 (mount via INDI) or 139/445 (Samba file share for captured FITS).

---

## Port 8888 — the proprietary app channel

Black box. Probe results from 2026-05-25:

| Probe | Result |
|---|---|
| Connect + passive read 3s | 0 bytes (silent server) |
| `nc` with random text | 0 bytes |
| Newline-terminated JSON-RPC (same format as 4350) | **TCP RST** |
| 4-byte length-prefixed JSON (big-endian) | **TCP RST** |
| 4-byte length-prefixed JSON (little-endian) | **TCP RST** |
| ZWO-style `{"Event":"..."}` JSON | **TCP RST** |
| TLS ClientHello | **TCP RST** |

Pattern: server accepts the TCP handshake then validates the first bytes of the application payload. Anything that isn't its expected magic / framing → immediate connection reset. Behaviour consistent with a custom binary protocol with a magic header (common for proprietary mobile-app channels — keeps third-party clients off the wire).

**Why it's not worth cracking:**

- No public reverse engineering — `joshumax/asiair`, `Oxofrimbl/asiair`, and the various Cloudy Nights threads all focus on 4350/4360 (the jailbreak vectors), not 8888
- Closed-source iOS app — would need mitmproxy / Frida instrumentation against the live app to capture the framing
- Significant effort for marginal benefit — 7624 (INDI) already provides full equipment control with documented protocol

If a real need emerges (e.g. wanting to script the app's sequence engine specifically), the entry point is iOS app traffic capture, not blind probing of 8888.

---

## Notable findings (out-of-band)

- **Mount RTC drift**: when test #1 first connected via INDI, the mount reported `UTC = 2022-03-01T00:03:19` — a **4-year drift**. Firm signal that the CEM26's RTC backup battery (CR2032) is failing. Normally masked because the ASIAIR app pushes time on every connect. Fixed during the same session with `scripts/mount.py timesync` (drift -133,618,402 s → -2.3 s ✓). Battery swap recommended at next bench opportunity. See [[iOptron-CEM26]].
- **Time offset overwrite confirmed**: `mount.py timesync` pushed `OFFSET = +120 min` (CEST). After the user opened the ASIAIR app and connected the mount profile, INDI's `TIME_UTC` showed `OFFSET = +1.00` (CET = +60 min) — confirms the long-documented ASIAIR-overwrites-offset behavior in [[ASIAIR#Mount Profile]].
- **Firmware self-identification**: `Firmware Info / Model` returns `CEM25-EC`, not `CEM26`. The iOptronV3 driver doesn't distinguish — the CEM26 ships with firmware that internally identifies as CEM25-EC because the line shares a firmware base. Not an error; just naming carry-over to be aware of.

---

## Lessons applied from the MacBot teardown

The May 24 MacBot integration tried to monitor the [[iOptron-CEM26]] mount via the mount's own WiFi-to-Serial bridge at `192.168.178.87:8899`, in parallel with ASIAIR's connection to the same bridge. The bridge's broadcast architecture (responses go to every client) produced a 25 % false-event rate and the integration was torn down the same day — see [[Mount-Diagnostics#Historical note: Mac Mini / MacBot integration attempted + torn down 2026-05-24|the historical write-up]].

Architectural lessons after the 2026-05-25 INDI investigation:

1. **INDI on 7624 IS the single arbiter**, not a competing peer. The ASIAIR app talks to the mount through its own INDI server (proven empirically by test #2). External INDI clients attach as peers of the same server — pub/sub, no bridge-layer contention. The previous draft of this note's *"INDI is a proxy that competes"* framing was wrong; corrected in the test #2 result section above.
2. **The transport-layer collision problem is real but localised**: it applies only when *two TCP clients* are open on `.87:8899` simultaneously. With the app running, the INDI server holds that one client. Running `mount.py` (raw `:GLS#` on `.87:8899`) at the same time re-creates the collision; running an INDI subscriber on `.84:7624` does not.
3. **Polling the WiFi bridge from a competing TCP client is the architecture mistake** that killed MacBot, not the choice of protocol. The fix is to be a peer-client of the INDI server, not a peer-client of the WiFi bridge.
4. **An INDI-based replacement for the torn-down `mount.py log` MacBot integration is now feasible** — `pyindi-client` subscriber on Mac Mini, NDJSON log of pub/sub stream, iMessage alerts on state transitions. Same role, transport-correct this time. Subject to the ephemeral-server caveat: only available during sessions when the app is connected to the mount profile.
5. **Treat port 8888 as off-limits** unless someone publishes a proper protocol spec — there's no need now that INDI is the proven control plane.
6. **Camera / focuser / guide-cam external control is not available** at all on this firmware. The app holds those USB devices directly and doesn't bridge them through INDI. External tooling is mount-only, session-window-only.

---

## Reference

- [[ASIAIR]] — equipment spec (Network section documents the static IP)
- [[iOptron-CEM26]] — mount, with its own separate WiFi bridge on port 8899
- [[Mount-Diagnostics]] — `mount.py` operational notes + MacBot teardown writeup
- [[Capture-Planning-Rules]] — single-client invariant + multi-night planning rules
- [`joshumax/asiair`](https://github.com/joshumax/asiair) — original jailbreak source
- [`Oxofrimbl/asiair`](https://github.com/Oxofrimbl/asiair) — fork with backup + reverse shell additions
- [INDI client development tutorial](https://www.indilib.org/develop/developer-manual/91-client-development-tutorial.html)
