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
| 7624 | **Standard INDI server** | open | Exposes **only** the `iOptronV3` mount driver (no camera / focuser / guide cam). Pre-configured as a TCP proxy to `192.168.178.87:8899` — same broadcast-bridge endpoint as `mount.py`. See § Port 7624. |
| 8888 | Proprietary ASIAIR app control | open | Silent on connect, RSTs on every structured probe (JSON-RPC, length-prefixed JSON, TLS, raw event JSON). Binary handshake; not reverse-engineered in public sources. |

---

## Port 7624 — INDI server, scope limited

Standard INDI XML protocol. `<getProperties version="1.7"/>\n` returns a 7.9 KB property tree on the dormant unit (ASIAIR app not running). Enumeration result:

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

### The critical twist: INDI is a proxy, not a separate path

`DEVICE_ADDRESS = 192.168.178.87:8899` is the same TCP WiFi-to-Serial bridge that `mount.py` and the ASIAIR app talk to directly. Sending `CONNECT=On` to the INDI server causes the ASIAIR to open **its own** TCP connection to the mount bridge — making any INDI client a *third* peer on the broadcast bridge alongside `mount.py` and the ASIAIR app.

So the May-24 [[Capture-Planning-Rules#4. Single-client invariant — `mount.py` vs ASIAIR|single-client invariant]] does **not** evaporate by switching to INDI. The protocol layer is cleaner (XML pub/sub instead of polling raw `:GLS#`), but the transport collision is the same — the iOS app, `mount.py`, and an INDI client could all receive each other's broadcast responses if they're running simultaneously.

**The actually-useful win** of going through INDI: pub/sub means we *don't* poll the bridge, so we don't *cause* collisions even if we'd suffer them. That's still an improvement over `mount.py log`'s 30 s polling loop. But it doesn't make us safe to coexist with an active ASIAIR session — only an empirical test can confirm.

### What INDI can give us, realistically

Once `CONNECT=On` populates the runtime tree, an external client (e.g. `pyindi-client`) gets reactive access to:

- **Live mount state**: RA/Dec (J2000 + JNow), alt/az, tracking on/off, parked, pier side, UTC, geographic coords
- **Slew / park / abort commands**: writable, same hazards as `mount.py`'s removed `goto` / `park` — these stay off-limits
- **Time / location set**: same convergence with ASIAIR's overwrites as `mount.py timesync`

What it does **not** give us:
- Camera control — `ASI2600MC Pro`, `ASI385MC` not registered with the INDI server
- Focuser control — no `ZWO EAF` device
- Anything the app does internally — sequence engine, plate solver, polar align routine, autofocus V-curve

**Bottom line on 7624**: usable as a mount-state telemetry source, equivalent functional surface to `mount.py status / log` but reactive instead of polling. Not the "clean alternative path" first impression suggested — it shares the same broadcast bridge, just from a different angle.

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

## Empirical questions still open

Two tests would close the remaining unknowns about port 7624. Both require the **mount powered on** (and the [[feedback-ask-rig-state-first|rig-state checklist]] cleared beforehand), and ideally piggyback on a real session rather than a special trip:

1. **Does INDI `CONNECT=On` work when ASIAIR app is NOT running?** With mount on, app closed, send `<newSwitchVector device="iOptronV3" name="CONNECTION"><oneSwitch name="CONNECT">On</oneSwitch>...` to 7624. Watch whether `state` transitions Alert → Ok and the runtime properties (`EQUATORIAL_EOD_COORD`, `TRACK_STATE`, etc.) populate. This is the existence proof that INDI is a viable read path at all.
2. **Does it coexist with an active ASIAIR session?** With mount on AND ASIAIR app actively connected (e.g. during a normal capture window), connect a passive `pyindi-client` listener and watch the property update stream. Good outcome: properties update at the app's rate (suggests the app multiplexes through INDI internally). Bad outcome: properties stall, give garbage, or trigger the same 25 % parse failure rate as `mount.py` did on the WiFi bridge.

Both tests are read-only on the INDI side (no slew, no park — those remain off-limits per [[Capture-Planning-Rules#5. Mount safety — what `mount.py` will NOT do, and why|mount safety]]). The risk is purely transport-layer: test #1 puts the ASIAIR onto the WiFi bridge as a TCP client, which is fine if no one else is on it. Test #2 deliberately overlaps with an active session — only run it on a low-stakes night.

If both pass, the natural follow-up project is a Mac Mini INDI subscriber that logs mount state to NDJSON — same role as the torn-down `mount.py log` integration but transport-correct (pub/sub via INDI instead of poll-and-collide via raw `:GLS#` on the broadcast bridge).

---

## Lessons applied from the MacBot teardown

The May 24 MacBot integration tried to monitor the [[iOptron-CEM26]] mount via the mount's own WiFi-to-Serial bridge at `192.168.178.87:8899`, in parallel with ASIAIR's connection to the same bridge. The bridge's broadcast architecture (responses go to every client) produced a 25 % false-event rate and the integration was torn down the same day — see [[Mount-Diagnostics#Historical note: Mac Mini / MacBot integration attempted + torn down 2026-05-24|the historical write-up]].

Architectural lessons that survive this round of probing:

1. **INDI on 7624 is *cleaner*, not *separate*.** The ASIAIR's INDI server proxies to the same `192.168.178.87:8899` bridge as `mount.py`. Pub/sub eliminates *our* contribution to collisions (we don't poll), but doesn't eliminate the other clients' contributions. The single-client invariant still applies to the *whole system* — at most one of (ASIAIR app, `mount.py`, INDI client) actively connected at a time, until the empirical test in the section above proves otherwise.
2. **Polling the bridge from a competing client is the architecture mistake**, not the choice of protocol. `mount.py log` polling `:GLS#` from the Mac Mini was wrong; an `mount.py log` polling `:GLS#` from anywhere else would be wrong too. The fix is pub/sub (INDI) on the same bridge with no other clients, OR a passive listener that doesn't issue any commands.
3. **Treat port 8888 as off-limits** unless someone publishes a proper protocol spec — the cost/benefit doesn't justify reverse engineering it from scratch via iOS app capture.
4. **Camera / focuser / guide-cam external control is not available** at all on this firmware. The app holds those USB devices directly and doesn't bridge them through INDI. Plan around it: external tooling is mount-only.

---

## Reference

- [[ASIAIR]] — equipment spec (Network section documents the static IP)
- [[iOptron-CEM26]] — mount, with its own separate WiFi bridge on port 8899
- [[Mount-Diagnostics]] — `mount.py` operational notes + MacBot teardown writeup
- [[Capture-Planning-Rules]] — single-client invariant + multi-night planning rules
- [`joshumax/asiair`](https://github.com/joshumax/asiair) — original jailbreak source
- [`Oxofrimbl/asiair`](https://github.com/Oxofrimbl/asiair) — fork with backup + reverse shell additions
- [INDI client development tutorial](https://www.indilib.org/develop/developer-manual/91-client-development-tutorial.html)
