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
| 7624 | **Standard INDI server** | open | Already exposes `iOptronV3` device — full INDI control surface. **Cleanest integration path.** |
| 8888 | Proprietary ASIAIR app control | open | Silent on connect, RSTs on every structured probe (JSON-RPC, length-prefixed JSON, TLS, raw event JSON). Binary handshake; not reverse-engineered in public sources. |

---

## Port 7624 — the recommended path

Standard INDI XML protocol. Connect with `<getProperties version="1.7"/>\n` and the server immediately publishes its property tree:

```xml
<defSwitchVector device="iOptronV3" name="CONNECTION" label="Connection"
                 group="Main Control" state="Alert" perm="rw" rule="OneOfMany"
                 timeout="60" timestamp="2026-05-25T11:49:11">
    <defSwitch name="CONNECT" label="Connect">Off</defSwitch>
    <defSwitch name="DISCONNECT" label="Disconnect">On</defSwitch>
</defSwitchVector>
```

- `iOptronV3` is the [[iOptron-CEM26]] driver — the same driver KStars/Ekos uses
- `state="Alert"` + `DISCONNECT On` means the mount is enumerated but the INDI driver isn't actively holding the serial bridge (ASIAIR app probably uses its own internal channel when running)
- When the ASIAIR app session is live, additional devices register: camera, focuser, guide cam

**Why this is the right channel for future tooling:**

- Standard protocol — XML over TCP, documented at [indilib.org](https://www.indilib.org/develop/developer-manual/91-client-development-tutorial.html)
- Massive client ecosystem already exists: KStars/Ekos, CCDciel, N.I.N.A. (via INDIGO bridge), `pyindi-client`, any custom Python script
- No reverse engineering, no fragile dependencies on un-maintained jailbreak repos
- INDI's pub/sub model (server pushes `setXxxVector` on every state change) avoids the polling-collision problem that killed the MacBot mount integration — clients don't compete for the serial bus, the INDI server arbitrates

**Caveats not yet verified:**

- Does ASIAIR's internal channel and the INDI driver share the same physical mount serial bus? If yes, the [[Capture-Planning-Rules#4. Single-client invariant — `mount.py` vs ASIAIR|single-client invariant]] likely still applies — don't run INDI clients against `iOptronV3` while ASIAIR is actively imaging. Needs empirical test (probably with a passive `pyindi-client` listener during a no-op session).
- Whether the camera / focuser drivers expose write access while the app holds them is unknown.

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

Use case for legitimate tooling: probably none on this unit. The OTA channel exists for ZWO's own updater; everything else worth automating is on 7624 (INDI) or via the file share (Samba 139/445).

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

## Lessons applied from the MacBot teardown

The May 24 MacBot integration tried to monitor the [[iOptron-CEM26]] mount via the mount's own WiFi-to-Serial bridge at `192.168.178.87:8899`, in parallel with ASIAIR's connection to the same bridge. The bridge's broadcast architecture (responses go to every client) produced a 25 % false-event rate and the integration was torn down the same day — see [[Mount-Diagnostics#Historical note: Mac Mini / MacBot integration attempted + torn down 2026-05-24|the historical write-up]].

The right architecture for any future external-monitoring project is:

1. **Talk to the ASIAIR's INDI server on port 7624**, not the mount's WiFi bridge. Lets the ASIAIR remain the single arbiter of the physical bus.
2. **Subscribe to INDI property updates** (pub/sub) instead of polling — no broadcast collisions, no false unreachable events.
3. **Treat port 8888 as off-limits** unless someone publishes a proper protocol spec — the cost/benefit doesn't justify reverse engineering it.

---

## Reference

- [[ASIAIR]] — equipment spec (Network section documents the static IP)
- [[iOptron-CEM26]] — mount, with its own separate WiFi bridge on port 8899
- [[Mount-Diagnostics]] — `mount.py` operational notes + MacBot teardown writeup
- [[Capture-Planning-Rules]] — single-client invariant + multi-night planning rules
- [`joshumax/asiair`](https://github.com/joshumax/asiair) — original jailbreak source
- [`Oxofrimbl/asiair`](https://github.com/Oxofrimbl/asiair) — fork with backup + reverse shell additions
- [INDI client development tutorial](https://www.indilib.org/develop/developer-manual/91-client-development-tutorial.html)
