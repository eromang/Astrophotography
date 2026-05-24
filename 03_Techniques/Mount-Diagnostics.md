---
title: "Mount Diagnostics — scripts/mount.py workflow"
type: technique
tags:
  - technique
  - technique/mount-control
---

# Mount Diagnostics

Workflow guide for `scripts/mount.py` — the standalone CLI that talks directly to the [[iOptron-CEM26]] over its WiFi-to-Serial bridge at `192.168.178.87:8899`. Use this when ASIAIR isn't running, when you want telemetry to enrich session notes, or when you need to diagnose mount issues independent of ASIAIR.

See [[../scripts/README.md]] for the per-subcommand reference. This note focuses on **when and why** rather than mechanics.

## When to use this script

| Situation | Subcommand | Why |
|---|---|---|
| Before starting an imaging session | `health` | Catches misconfigured location, hemisphere, drifted clock, or unexpected park state before you commit time setting up ASIAIR |
| Want to see RA/Dec right now | `status` | Faster than opening the ASIAIR app — three lines in your terminal |
| Monitoring the mount during a session | `status --watch 30` | Live tail of mount state without opening another GUI |
| Capturing telemetry for a session | `log --interval 30` | Writes NDJSON beside the capture-session note; lets you post-mortem timing of slews, meridian flips, tracking interruptions |
| End of session, ready to teardown | `park` | One command — stops tracking, slews to park, confirms parked. Replaces the "stop autorun → park via app" dance |
| Mount clock drifted (DST switch, no GPS) | `timesync` | Pushes host's NTP-synced UTC to mount in one command |
| Checking firmware status | `firmware` | No Windows needed — compares against the bundled `CEM26_GEM28_FirmwareVersionHistory.pdf` |
| Quick visual / focus / framing check without ASIAIR | `goto M16` then `goto NGC7000` | Bypass ASIAIR for one-off slews |
| ASIAIR seems flaky mid-session | `status` | Verify whether the mount is actually responding or if ASIAIR is the broken link |

## Pre-session workflow

Before powering up ASIAIR for the night:

```bash
python3 scripts/mount.py health
```

Each check prints a `✓` or `✗`. Common failure modes and fixes:

| Failure | Fix |
|---|---|
| `time sync` drift > 60 s | `python3 scripts/mount.py timesync` |
| `location` off | Mount lost its location (probably no GPS module). Re-enter via 8409 hand controller, or set via `:SLO#` / `:SLA#` (not currently exposed as a `mount.py` subcommand — would need to be added) |
| `hemisphere` set to S | Set on 8409 hand controller; can also push via `:SHE1#` |
| `not slewing` failing | Wait for current slew to complete, or `python3 scripts/mount.py status` to see what it's doing |
| `mount identified` failing — `MountUnreachable` | Mount off, WiFi not joined, or wrong IP. Check `ping 192.168.178.87` and the [[iOptron-CEM26#WiFi Configuration|CEM26 WiFi section]] |

Once `health` exits 0, proceed to ASIAIR setup as normal. **At that point, disconnect from the mount via the WiFi bridge** — ASIAIR will take over via USB-Serial.

## End-of-session workflow

After the imaging sequence completes:

1. In ASIAIR: stop the current autorun, disconnect from the mount (Settings → Telescope → Disconnect)
2. From your Mac terminal: `python3 scripts/mount.py park`

The script will:
- Stop sidereal tracking (`:ST0#`)
- Read the stored park position (`:GPC#`)
- Issue `:MP1#` to slew to park
- Poll `:GLS#` once per second until system state = 6 (parked) or 60 s timeout

If the mount times out before parking, check that it has a valid park position stored (set via 8409 hand controller → Mount Settings → Park Position). The script doesn't override an unset park position.

Power the mount down once parked.

## Per-session telemetry

For nights where you want post-session evidence of what the mount actually did:

```bash
# Start before kicking off the ASIAIR session (or right after; it's idempotent)
python3 scripts/mount.py log --interval 60 &

# … run your imaging session …

# At end: stop with Ctrl-C (or kill the background process)
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

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `MountUnreachable: could not connect to 192.168.178.87:8899` | Mount off, on AP fallback, or WiFi not joined | `ping 192.168.178.87` — if fails, connect to `HBX8409_DF5E72` AP and use `10.10.100.254` instead (override with `--ip 10.10.100.254`) |
| `MountTimeout: mount did not respond within 5 s` | ASIAIR is connected via USB-Serial, blocking the serial bus | Disconnect ASIAIR from the mount, retry |
| Garbled responses, occasional parse errors | Single-client invariant violation — two clients writing at once | Same: only one client at a time |
| `health` says `time sync` is failing every session | Mount lacks GPS module; HC clock drifts over weeks | Run `mount.py timesync` at session start (becoming a habit) |
| `goto` says target unknown | Designation not in `TARGET_CATALOG` and no matching `02_Targets/` note with `ra_deg`/`dec_deg` | Add the target to `TARGET_CATALOG` in `mount.py`, or populate `ra_deg`/`dec_deg` in the target note's frontmatter |

## Safety notes

- **Single client at a time.** Don't run `mount.py` against the WiFi bridge while ASIAIR is on the USB-Serial. See [[iOptron-CEM26#How WiFi mount control actually works]] for the architectural reason.
- **`goto` requires the mount to be unparked.** It errors if state = 6. Run `unpark` first.
- **`park` is the only mover called automatically by the script.** Slews go to the stored park position only — they don't aim at the sky or arbitrary coordinates. As long as the park position is set safely (counterweight down, OTA horizontal or pointed at the pole), the slew is risk-free.
- **`goto` does aim at arbitrary coordinates.** Always verify the target's altitude is above the balcony horizon profile (the script doesn't check). Below-horizon slews are rejected by the mount (`:MS1#` returns `0`), but a slew to a target *just above* the horizon may collide with the balcony wall.
- **No `stop` / emergency abort subcommand in v1.** If something goes wrong mid-slew, the fastest stop is the physical power switch on the mount. (Adding `stop` is in the deferred Tier 4 backlog.)

## Reference

- [[iOptron-CEM26]] — equipment specs + WiFi config + firmware reference
- [[ASIAIR]] — primary mount control (USB-Serial, separate from this script)
- [[../scripts/README.md]] — per-subcommand reference for `mount.py`
- iOptron RS-232 V3.10 spec — `01_Equipment/Manuals/CEM26/ASCOM-Driver/RS-232_Command_Language2014V310.pdf`
