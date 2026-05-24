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

- **Single client at a time.** Don't run `mount.py` against the WiFi bridge while ASIAIR is on the USB-Serial. See [[iOptron-CEM26#How WiFi mount control actually works]] for the architectural reason.
- **No motion subcommands.** This script cannot slew the mount. Reach for ASIAIR or the 8409 hand controller for any GoTo / park / sky pointing.
- **After mid-slew power cycle** — the mount's internal coordinate model is reset to home but the OTA is wherever it physically stopped. Re-align the OTA to the home position and use "Set Zero Position" on the 8409 hand controller before any future slew (whether via ASIAIR or HC). This applies regardless of `mount.py`.

## Reference

- [[iOptron-CEM26]] — equipment specs + WiFi config + firmware reference
- [[ASIAIR]] — primary mount control (USB-Serial, separate from this script)
- [[../scripts/README.md]] — per-subcommand reference for `mount.py`
- iOptron RS-232 V3.10 spec — `01_Equipment/Manuals/CEM26/ASCOM-Driver/RS-232_Command_Language2014V310.pdf`
