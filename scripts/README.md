# scripts/

Utility scripts for the vault. Run from the repo root.

## fov_atlas.py — RedCat 51 FOV atlas

Mollweide all-sky PNG showing a RedCat 51 frame (5.4° × 3.6°) at each catalogued target. Blue = balcony-reachable, red = blocked (Dec > 55° or too-high transit).

```bash
python3 -m pip install matplotlib numpy pyyaml
python3 scripts/fov_atlas.py
```

Output: `03_Techniques/images/fov-atlas-allsky.png`. Embedded in [[../03_Techniques/FOV-Atlas.md]].

### Extending the target list

- **Inline:** append a row to `CATALOG` in `fov_atlas.py`.
- **From vault:** add `ra_deg`, `dec_deg`, `size_arcmin` to a target's YAML frontmatter under `02_Targets/` — the script picks it up on the next run (vault entries win over the inline catalog when names match).

---

## mount.py — CEM26 mount control via WiFi TCP bridge

Standalone CLI for talking directly to the iOptron CEM26 over its WiFi-to-Serial bridge at `192.168.178.87:8899` (configured 2026-05-24 in APSTA mode — see [[../01_Equipment/Mount/iOptron-CEM26.md#WiFi Configuration]]). Bypasses ASIAIR entirely; useful for pre-session readiness checks, end-of-session park, session-state logging, and standalone diagnostics when ASIAIR isn't running.

```bash
python3 -m pip install pyyaml          # only needed for `goto` vault target lookup
python3 scripts/mount.py status        # quick state readout
python3 scripts/mount.py health        # pre-session readiness check; exit 0=pass, 1=fail
python3 scripts/mount.py firmware      # installed firmware versions + gap vs latest
python3 scripts/mount.py log           # NDJSON state logger written beside session note
```

### Subcommands

| Subcommand | What it does |
|---|---|
| `status [--watch [N]]` | Print parsed mount state (RA/Dec, alt/az, tracking, parked/slewing). `--watch` repolls every N seconds (default 5). |
| `health` | Pre-session readiness: firmware, location, hemisphere, tracking, time drift, not-slewing. Exit 0 if all pass, 1 if any fail. |
| `firmware` | Show installed firmware (HC + RA + DEC) and compare against the latest documented release. |
| `park` | End-of-session: stop tracking, slew to stored park position, confirm system state = 6 (parked). |
| `unpark` | `:MP0#` + start sidereal tracking. |
| `timesync` | Push host's UTC + DST + UTC offset to mount. Reports before/after drift. |
| `goto <designation>` | Look up target in `02_Targets/` (or fallback catalog), slew there. **ASIAIR must be disconnected.** Designation normalization is case-insensitive and strips spaces/hyphens: `M16`, `m 16`, `M-16` all match. |
| `log [--session FILE] [--interval N]` | Periodic state logger. Appends NDJSON to `05_Sessions/{year}/Capture/{date}-mount-log.json` (one record per sample), plus a final summary line on Ctrl-C. Default interval 30 s. |

### Sample output

```
$ python3 scripts/mount.py status
--- mount status @ 2026-05-24T15:03:48 ---
  position    RA  189.1292°    Dec +90.0000°    pier=?  normal
              alt +49.717°  az     0.000°
  state       stopped at zero/home position  (tracking: sidereal)
  location    +49.71694° N    +6.00833° E    hemisphere=N
  GPS         0 (no data / module absent)
  time src    hand controller    mount UTC: 2026-05-24T14:03:44+00:00    offset: +60 min  DST: no
```

### Single-client invariant

The mount's WiFi-to-Serial bridge multiplexes a single 115200 8N1 serial link to the 8409 hand controller. Two clients writing at the same time produce garbled responses. **Do not run `mount.py` while ASIAIR is connected to the mount via the USB-Serial cable.** The script's `goto` and `park` subcommands enforce this implicitly (you'd see corrupted responses); for read-only diagnostics it's mostly harmless but still discouraged.

### Tests

```bash
python3 -m unittest scripts.test_mount                     # unit + mock tests (no mount needed)
MOUNT_TEST_LIVE=1 python3 -m unittest scripts.test_mount   # + live integration tests
```

Live tests require the mount powered on and reachable at `192.168.178.87`. They cover read-only verification and `timesync` (which writes but only to set the clock to host time). Park / goto are **not** in the live test set — those move the mount and require manual supervision.

### Reference docs

- iOptron RS-232 command spec: `01_Equipment/Manuals/CEM26/ASCOM-Driver/RS-232_Command_Language2014V310.pdf` (V3.10)
- Equipment note: [[../01_Equipment/Mount/iOptron-CEM26.md]] — WiFi/firmware setup
- Workflow guide: [[../03_Techniques/Mount-Diagnostics.md]] — when to use which subcommand

### Extending the target catalog (for `goto`)

Same model as `fov_atlas.py`:

- **Inline:** append a row to `TARGET_CATALOG` in `mount.py`.
- **From vault:** add `designation`, `ra_deg`, `dec_deg` to a target's YAML frontmatter under `02_Targets/`. Vault entries win over the inline catalog. (Most current target notes don't carry these fields yet — populate as needed.)
