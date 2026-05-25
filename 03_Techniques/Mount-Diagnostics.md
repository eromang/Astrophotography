---
title: "Mount Diagnostics — scripts/mount.py workflow"
type: technique
tags:
  - technique
  - technique/mount-control
---

# Mount Diagnostics

Workflow guide for `scripts/mount.py` — the standalone CLI that talks to the [[iOptron-CEM26]] over its WiFi-to-Serial bridge at `192.168.178.87:8899`. **Read-only diagnostics and safe config helpers only — `goto` and `park` have been removed (see [[#Removed: goto and park]] below).** Use this when ASIAIR isn't running, when you want telemetry to enrich session notes, or when you need to diagnose mount issues independent of ASIAIR.

See [[../scripts/README.md]] for the per-subcommand reference. This note focuses on **when and why** rather than mechanics.

## When to use this script

| Situation | Subcommand | Why |
|---|---|---|
| Before starting an imaging session | `health` | Catches misconfigured location, hemisphere, drifted clock, or unexpected park state before you commit time setting up ASIAIR |
| Want to see RA/Dec right now | `status` | Faster than opening the ASIAIR app — three lines in your terminal |
| Monitoring the mount during a session | `status --watch 30` | Live tail of mount state without opening another GUI |
| Capturing telemetry for a session | `log --interval 30` | Writes NDJSON beside the capture-session note; lets you post-mortem timing of slews, meridian flips, tracking interruptions |
| Mount clock drifted (DST switch, no GPS) | `timesync` | Pushes host's NTP-synced UTC to mount in one command |
| Checking firmware status | `firmware` | No Windows needed — compares against the bundled `CEM26_GEM28_FirmwareVersionHistory.pdf` |
| Re-enable tracking after manual park | `unpark` | Clears the parked flag + starts sidereal tracking. Slow drift only (~15"/sec westward) — no slew. |
| ASIAIR seems flaky mid-session | `status` | Verify whether the mount is actually responding or if ASIAIR is the broken link |

For anything that **moves the mount on a slew** (GoTo, end-of-session park, re-pointing), use **ASIAIR** (USB-Serial) or the **8409 hand controller** directly. See [[#Removed: goto and park]] for why those were taken out of this script.

## Pre-session workflow

Before powering up ASIAIR for the night:

```bash
python3 scripts/mount.py health
```

Each check prints a `✓` or `✗`. Common failure modes and fixes:

| Failure | Fix |
|---|---|
| `time sync` drift > 60 s | `python3 scripts/mount.py timesync` |
| `location` off | Mount lost its location (probably no GPS module). Re-enter via 8409 hand controller |
| `hemisphere` set to S | Set on 8409 hand controller |
| `not slewing` failing | Wait for current slew to complete, or run `status` to see what it's doing |
| `mount identified` failing — `MountUnreachable` | Mount off, WiFi not joined, or wrong IP. Check `ping 192.168.178.87` and the [[iOptron-CEM26#WiFi Configuration|CEM26 WiFi section]] |

Once `health` exits 0, proceed to ASIAIR setup as normal. **At that point, disconnect from the mount via the WiFi bridge** — ASIAIR will take over via USB-Serial.

## End-of-session workflow

`mount.py` cannot park the mount (removed). Use either:

- **ASIAIR app** → Settings → Telescope → Park (preferred)
- **8409 hand controller** → Menu → Park
- After parking, you can verify via `python3 scripts/mount.py status` (should show system_state = 6 "parked")

## Per-session telemetry

For nights where you want post-session evidence of what the mount actually did:

```bash
python3 scripts/mount.py log --interval 60 &
# … run your imaging session …
# At end: Ctrl-C (or kill the background process)
```

**Important caveat:** The single-client invariant applies. If `mount.py log` is polling the mount via WiFi at the same time ASIAIR is sending USB-Serial commands, responses will collide. **Either** use logging without ASIAIR (rare — telemetry of a manual session), **or** accept that some sample lines will have parsing errors during ASIAIR's busy periods.

A safer pattern for ASIAIR sessions: skip per-second telemetry and instead run `mount.py status` opportunistically when you want a snapshot.

### Reading the log

Logs are NDJSON — one JSON record per line. Typical record:

```json
{"ts":"2026-05-24T22:30:15+00:00","kind":"sample","ra_deg":274.7,"dec_deg":-13.78,"pier_side":"E","pointing_state":"normal","system_state":1,"system_state_name":"tracking (PEC off)","tracking_rate":0,"tracking_rate_name":"sidereal","is_parked":false,"is_slewing":false,"is_tracking":true}
```

Useful `jq` queries:

```bash
LOG=05_Sessions/2026/Capture/2026-05-24-mount-log.json

# When did slews happen?
jq -c 'select(.is_slewing == true) | {ts, ra_deg, dec_deg}' "$LOG"

# Did tracking ever stop unexpectedly?
jq -c 'select(.kind == "sample" and .is_tracking == false and .is_parked == false) | {ts, system_state_name}' "$LOG"

# Meridian flip detection — when pier_side changes
jq -s '. | map(select(.kind == "sample")) | [.[] | {ts, pier_side}] | . as $all | range(1; length) | . as $i | {now: $all[$i], prev: $all[$i-1]} | select(.now.pier_side != .prev.pier_side)' "$LOG"

# Final summary line
jq -c 'select(.kind == "summary")' "$LOG"
```

Logs are gitignored (`*-mount-log.json` in [[../.gitignore]]) — telemetry accumulates locally without bloating the repo. If a particular log is interesting enough to keep as session evidence, you can `git add -f` it.

## Removed: `goto` and `park`

Both subcommands existed in the first version of `mount.py` and were **removed 2026-05-24** after a real incident:

- I ran `goto NGC7000` followed immediately by `park` to "race" a known WiFi-drop-after-slew pattern.
- The mount's internal RA/Dec coords had drifted from the OTA's actual physical position over the course of the session (multiple power cycles, including one mid-slew).
- The script had no way to detect this desync.
- The chained slew sequence drove the bare mount into a hard mechanical limit. User shut down for the third time and reported the limit hit.
- Hard-stop hits at slew speed on the CEM26 risk stripped worm-wheel teeth, displaced gear mesh, and damaged limit cams.

The script wasn't fundamentally unsafe — it dutifully sent valid iOptron commands. But the **operator** (Claude, in this case) had no situational awareness of the mount's physical state, and the script had no guard rails to compensate. Specifically:

| Safety gap | Why it mattered here |
|---|---|
| No way to verify internal coords match physical OTA position | The desync after power cycles was invisible to the script |
| No "are you sure?" prompt before `:MS1#`/`:MP1#` | Easy to trigger by accident |
| No `:Q#` emergency-stop subcommand | Couldn't abort the runaway slew via the script |
| No settle/idle check between motion commands | Allowed back-to-back slews that compounded stress |
| No horizon-profile check | Mount only knows its altitude limit, not balcony walls or indoor obstructions |
| No environmental awareness | Script didn't know if OTA was attached or where it physically pointed |

### What would need to be in place before re-adding either subcommand

If you ever want `goto`/`park` back in `mount.py`:

1. **Require a `--i-have-verified-physical-position` flag** (deliberately ugly, no short form) on every invocation. The flag is the operator's promise that the mount's internal coords match the OTA's actual physical position. Forces a deliberate pause.
2. **Add a `stop` subcommand** sending `:Q#` so a runaway slew can be aborted from the same CLI.
3. **Add a settle guard** — refuse to issue `:MS1#`/`:MP1#` if the mount has changed system_state in the last 15 s.
4. **Implement the `:GAL#` altitude-limit check** in `health` (the plan said it'd be there; the first implementation forgot).
5. **Document the post-power-cycle re-anchoring procedure** — after any mid-slew power cycle, the operator MUST physically re-align the OTA to the home position and use "Set Zero Position" on the 8409 hand controller before any subsequent slew.

Until those are in place, slewing belongs to ASIAIR or the 8409 hand controller.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `MountUnreachable: could not connect to 192.168.178.87:8899` | Mount off, on AP fallback, or WiFi not joined | `ping 192.168.178.87` — if fails, connect to `HBX8409_DF5E72` AP and use `10.10.100.254` instead (override with `--ip 10.10.100.254`) |
| `MountTimeout: mount did not send any bytes` | ASIAIR is connected via USB-Serial, blocking the serial bus | Disconnect ASIAIR from the mount, retry |
| Garbled responses, occasional parse errors | Single-client invariant violation — two clients writing at once | Same: only one client at a time |
| `health` says `time sync` is failing every session | Mount lacks GPS module; HC clock drifts and resets on power-off | Run `mount.py timesync` at session start (becoming a habit) |
| WiFi drops shortly after a slew (ASIAIR-driven) | Observed pattern — HBX8409 WiFi module appears to disassociate during/after motor activity. Not investigated in depth. | Wait ~30 s and re-ping. If persistent, fall back to USB-Serial (ASIAIR-only). |

## Safety notes

- **Single client at a time.** Both `mount.py` and (since 2026-05-24) ASIAIR use the same TCP endpoint `192.168.178.87:8899`. The WiFi bridge accepts multiple TCP connections but **broadcasts every response to every connected client** — so `mount.py status` polled during an active ASIAIR session sees ASIAIR's poll responses interleaved with its own. Parsers may pick the wrong record format and fail. Reserve `mount.py` queries for ASIAIR-off windows. Verified empirically 2026-05-24. See [[../01_Equipment/Accessories/ASIAIR#Concurrent access with mount.py (single-client invariant — UPDATED 2026-05-24)|ASIAIR § Concurrent access]] for the test results.
- **No motion subcommands.** This script cannot slew the mount. Reach for ASIAIR or the 8409 hand controller for any GoTo / park / sky pointing.
- **After mid-slew power cycle** — the mount's internal coordinate model is reset to home but the OTA is wherever it physically stopped. Re-align the OTA to the home position and use "Set Zero Position" on the 8409 hand controller before any future slew (whether via ASIAIR or HC). This applies regardless of `mount.py`.

## NDJSON record types written by `mount.py log`

```json
{"ts":"…","kind":"sample","ra_deg":274.7,"dec_deg":-13.78,"pier_side":"E","is_tracking":true,…}
{"ts":"…","kind":"event","event_type":"meridian_flip","detail":"pier side changed E → W"}
{"ts":"…","kind":"event","event_type":"tracking_stopped","detail":"tracking transitioned to off (state now: stopped (non-zero position))"}
{"ts":"…","kind":"event","event_type":"mount_unreachable","detail":"could not connect to 192.168.178.87:8899: …"}
{"ts":"…","kind":"summary","duration_s":7300.5,"samples_written":240,"events_written":1,"interval_s":30.0}
```

Event detection happens between consecutive samples in `cli_log`. Useful for post-session analysis of when slews happened, when tracking stopped unexpectedly, or whether meridian flips occurred.

## Historical note: Mac Mini / MacBot integration attempted + torn down 2026-05-24

A separate integration was built that exposed `mount.py` via iMessage to MacBot running on the always-on Mac Mini, with session-driven scheduling that read capture-session note Planning tables and auto-fired `mount log` jobs. The build was complete and end-to-end smoke-tested green.

**It was torn down the same day** after discovering the WiFi-to-Serial bridge's actual architecture: it accepts multiple TCP connections but **broadcasts every response to every connected client**. Concurrent polling between `mount.py` and ASIAIR (when ASIAIR is in TCP-mount-control mode) produced ~25% false `mount_unreachable` events — `mount.py`'s `:GEP#` query would frequently receive ASIAIR's `:GLS#` response (wrong format) and the parser would correctly reject it as malformed.

Net: `mount.py` is best used as a **local-only MacBook tool** for ad-hoc diagnostics during ASIAIR-off windows (pre-session check, post-session diagnostics, dead-window logging). See [[Capture-Planning-Rules#Single-client invariant — mount.py vs ASIAIR]] for the operational rule.

## INDI on ASIAIR as a known-good external monitoring path (2026-05-25)

Active probing of the ASIAIR's LAN service surface on 2026-05-25 (full writeup: [[ASIAIR-Network-Protocol]]) discovered that **the ASIAIR runs a standard INDI server on port 7624** which exposes the `iOptronV3` mount driver — and crucially, **the ASIAIR iOS app uses that INDI server internally for mount control**. Confirmed by passive observation: every arrow-key press in the app surfaced as a `TELESCOPE_MOTION_*` property change at a passive listener within ~1 s.

This is the architectural detail that makes a future external mount logger feasible (which the MacBot integration was not):

| Path | Architecture | Verdict |
|---|---|---|
| `mount.py` polling `:GLS#` on `192.168.178.87:8899` | Second TCP client on the WiFi bridge alongside the INDI server → broadcast-bridge collisions | ❌ killed the May-24 MacBot build |
| External `pyindi-client` subscribing to `192.168.178.84:7624` | Peer-client of the same INDI server that the app uses; INDI is the single arbiter on the WiFi bridge | ✅ no transport-layer contention; pub/sub, event-driven |

### Rebuild status: LIVE on Mac Mini (2026-05-25)

The architecturally-correct replacement for the torn-down `mount.py log` integration is **built and end-to-end verified** on the always-on Mac Mini (`192.168.178.91`). Implementation lives in the **Local1 vault** at `04_Personal/House-Automation/scripts/macbot/` and is deployed to `~/Documents/MacBot/` on the Mac Mini.

**Architecture** (stdlib only — no `pyindi-client` dependency, ~250 lines of raw XML/TCP):

- `mount_indi.py` — INDI XML/TCP subscriber + StateTracker (detects mount_disconnected, tracking_stopped/started, meridian_flip, parked, unparked, position_change). CLI: `status` (one-shot snapshot) + `log --output PATH --session DATE` (NDJSON subscriber).
- `mount_commands.py` — MacBot intent handlers wrapping the above as a long-running subprocess.
- `session_note_parser.py` — reads `planned_start:` / `planned_end:` YAML from capture-session notes, returns UTC datetimes for the scheduler.

**iMessage intents** (live — text MacBot at familleromang@icloud.com):

| Intent | NL trigger | What it does |
|---|---|---|
| Status | `mount status` / `telescope status` | One-shot mount snapshot (Tracking, Park, Pier, RA/DEC, Time, FW) |
| Log start | `start mount log` / `begin mount logging` | Spawn `mount_indi.py log` as background subprocess, record pid in SQLite |
| Log stop | `stop mount log` / `end mount logging` | SIGTERM the active pid, summarize the NDJSON |
| Schedule | `schedule mount log for tonight` / `for 2026-05-25` | Read session-note YAML → add 2 cron jobs (start −15m, stop +30m) |
| Schedule list | `show mount schedule` / `list mount jobs` | Active `mount_log_*` jobs + next-run times |
| Schedule cancel | `cancel mount schedule for <date>` | Delete the scheduled jobs |

**Subscribed properties** (event-driven via INDI pub/sub, written to `~/Documents/MacBot/mount-logs/{date}-mount-log.json`):

- `TELESCOPE_TRACK_STATE` — alert on unexpected tracking stop (10 min cooldown)
- `TELESCOPE_PARK` — record park events + alert if mid-session (15 min cooldown)
- `TELESCOPE_PIER_SIDE` — detect meridian flips (30 min cooldown — flip takes ~2 min)
- `CONNECTION` — alert on mount-driver disconnect (5 min cooldown)
- `EQUATORIAL_EOD_COORD` — record position changes > 0.5° (no alert — informational)
- Lifecycle reconnect-burst detector → alert if > 5 reconnects in 10 min

**Verification 2026-05-25**:
- Local: 126 unit tests pass (70 new)
- Stage 2 live INDI smoke from MacBook: `status` + `log` + SIGTERM-responsive (caught and fixed a stop-flag-blocking-on-recv bug; regression-tested)
- Stage 3 Mac Mini deploy: imports clean, `mount_indi.py status` runs from Mac Mini, weekly Astrophotography `git pull` cron set
- Stage 4 iMessage end-to-end: all 6 intents verified via the MacBot chat — status/log start/log stop/schedule/list/cancel each round-tripped correctly

**Astrophotography repo dependency**: the YAML schema `planned_start:` / `planned_end:` was added to capture-session notes for this purpose (see [[../CLAUDE.md|CLAUDE.md § Capture-session-specific: planned_start / planned_end]]). For a session note to be schedulable, those fields must be populated.

**Mac Mini setup state** (live as of 2026-05-25):
- `~/Documents/git-repos/Astrophotography` (shallow clone, weekly `git pull` cron at Sun 03:00 → keeps session notes fresh)
- `~/Documents/MacBot/mount-logs/` (NDJSON output dir)
- `~/Documents/MacBot/{mount_indi,mount_commands,session_note_parser}.py` (deployed via `post-pull-deploy.sh`)
- SQLite tracking via `mount_log_runs` table in `~/Documents/MacBot/macbot.db`
- iMessage cooldowns in `notifications.py`'s COOLDOWNS dict

### Operational caveat: INDI server lifecycle (corrected)

The INDI server on port 7624 is **not always-on**, but its uptime is tied to the **mount profile state**, not to whether the app is foregrounded. Verified empirically 2026-05-25:

- **ASIAIR power-on + mount on, app never opened that session** → INDI server is **up at boot** and `iOptronV3` is `CONNECT=On`, polling the mount. The mount profile state persists across ASIAIR reboots, so the driver auto-reconnects.
- **ASIAIR up, mount up, app fully shut down** → INDI server still reachable, driver still CONNECT=On (same state).
- The trigger for INDI exiting is **the mount profile being toggled off** in the app — not "app closed", not "ASIAIR power-cycled".

**Why this matters for the user's real workflow:** during a real capture session the user opens the app only briefly (start of session to slew + configure + start autorun, occasionally during to check, end of session to shut down). The mount profile is active the entire time. INDI is alive the entire time — and is already alive *before* the user opens the app, as long as the ASIAIR booted with a previously-active mount profile.

A Mac Mini `pyindi-client` subscriber can therefore attach immediately when the ASIAIR comes online — no retry-with-backoff, no dependency on app foreground state. The scheduler just needs to know when imaging starts (machine-readable in the capture-session note's YAML `planned_start:` / `planned_end:` fields — see [[../CLAUDE.md|CLAUDE.md § Capture-session-specific: planned_start / planned_end]]).

### Why this doesn't change `mount.py`'s scope

`mount.py` remains useful in the specific scenario where INDI is NOT running:

- Bench diagnostics with no app open
- Pre-session firmware version check
- Time-sync rescue when the RTC has drifted and you need to push UTC without booting the app first (RTC battery is suspected weak — see [[iOptron-CEM26]])

For those, `mount.py` on raw `:GLS#` works fine because no other client is on the WiFi bridge. The single-client invariant from [[Capture-Planning-Rules#4. Single-client invariant — `mount.py` vs ASIAIR|Capture-Planning-Rules § 4]] still applies: don't run `mount.py` while the INDI server is also connected to the mount (i.e. while the app has the mount profile on).

## Reference

- [[iOptron-CEM26]] — equipment specs + WiFi config + firmware reference
- [[ASIAIR]] — primary mount control (TCP via WiFi bridge since 2026-05-24)
- [[ASIAIR-Network-Protocol]] — LAN service surface, INDI test results, INDI rebuild blueprint
- [[Capture-Planning-Rules]] — operational rules including the mount.py/ASIAIR concurrent-access caveat
- [[../scripts/README.md]] — per-subcommand reference for `mount.py`
- iOptron RS-232 V3.10 spec — `01_Equipment/Manuals/CEM26/ASCOM-Driver/RS-232_Command_Language2014V310.pdf`
