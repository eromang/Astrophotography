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

## psf_image.py — offline PSF / FWHM measurement (PixInsight PSFImage equivalent)

Offline replacement for PixInsight's **PSFImage** script (Hartmut V. Bornemann). Detects stars, fits an elliptical **Moffat/Gaussian** PSF to the best ~50, and reports the **median FWHM → the number you put in BlurXTerminator's PSF Diameter**. Optionally renders a synthetic PSF image (FITS, the "external PSF" use) and a per-star CSV. Referenced from [[../04_Processing/Pixinsight/RGB-Workflow.md#2.5 Star Sharpening]].

Stdlib + **numpy/scipy** only — no astropy/photutils. Reads **FITS** (`.fit/.fits`) and **uncompressed monolithic XISF** (`.xisf`, Float32/UInt16).

```bash
python3 scripts/psf_image.py <image>                       # FWHM -> BXT diameter
python3 scripts/psf_image.py img.xisf --beta 4             # fix Moffat beta (match SubFrameSelector)
python3 scripts/psf_image.py img.fit --psf-out psf.fits --csv stars.csv
```

| Option | Default | Meaning |
|---|---|---|
| `--function moffat\|gaussian` | moffat | PSF model |
| `--beta N` | free | fix Moffat β (PixInsight SubFrameSelector default is 4) |
| `--max-stars` / `--use-stars` | 200 / 50 | detect / keep (best by residual) |
| `--box N` | 10 | half-window (px) fit per star |
| `-k N` | 6.0 | detection threshold (σ above background) |
| `--psf-out FILE` | — | write synthetic PSF FITS (with FWHMX/FWHMY/BETA keys) |
| `--csv FILE` | — | per-star fits (cx,cy,fwhmx,fwhmy,fwhm,beta,ecc,rmad) |

**Output:** prints FWHM x/y, eccentricity, β, median FWHM, and `==> BXT PSF Diameter: N`.

> ⚠️ **Run it on the debayered/processed image you'll actually deconvolve, not raw CFA subs.** On a raw Bayer frame the mosaic sampling differs from PixInsight's CFA handling (~10 % low). Validation on a Mel 111 light: this script **2.03 px** vs PixInsight SubFrameSelector **2.28 px**, with **eccentricity 0.61 vs 0.63** (near-exact) — the offset is the CFA, the shape characterisation matches. Also match the **image scale**: a PSF measured on the native master must not be reused on a drizzle-2× master (stars ~2× wider).

### Tests

```bash
python3 scripts/test_psf_image.py     # synthetic Moffat/Gaussian recovery + FITS round-trip
```

Synthetic recovery is exact (Moffat 3.20 → 3.200 px, Gaussian 2.80 → 2.800 px).

---

## mount.py — CEM26 read-only diagnostics + safe config helpers

CLI for talking to the iOptron CEM26 over its WiFi-to-Serial bridge at `192.168.178.87:8899` (configured 2026-05-24 in APSTA mode — see [[../01_Equipment/Mount/iOptron-CEM26.md#WiFi Configuration]]). All subcommands are non-moving (except the slow sidereal tracking that `unpark` starts and `timesync` config writes which don't drive the motors). Useful for pre-session readiness checks, session-state logging, time sync, and quick diagnostics when ASIAIR isn't running.

```bash
python3 scripts/mount.py status        # quick state readout
python3 scripts/mount.py health        # pre-session readiness check; exit 0=pass, 1=fail
python3 scripts/mount.py firmware      # installed firmware versions + gap vs latest
python3 scripts/mount.py log           # NDJSON state logger written beside session note
```

Stdlib-only — no `pip install` required.

### Subcommands

| Subcommand | What it does |
|---|---|
| `status [--watch [N]]` | Print parsed mount state (RA/Dec, alt/az, tracking, parked/slewing). `--watch` repolls every N seconds (default 5). |
| `health` | Pre-session readiness: firmware, location, hemisphere, tracking, time drift, not-slewing. Exit 0 if all pass, 1 if any fail. |
| `firmware` | Show installed firmware (HC + RA + DEC) and compare against the latest documented release. |
| `unpark` | `:MP0#` + start sidereal tracking. The only "motion" is the slow ~15"/sec westward sidereal drift — no slew. |
| `timesync` | Push host's UTC + DST + UTC offset to mount. Config writes only, no motion. Reports before/after drift. |
| `log [--session FILE] [--interval N] [--quiet]` | Periodic state logger. Appends NDJSON to `05_Sessions/{year}/Capture/{date}-mount-log.json`. Three record kinds: `sample` (per-poll), `event` (state transitions: `mount_unreachable`, `tracking_stopped`, `meridian_flip`), `summary` (end-of-run). `--quiet` suppresses per-sample stdout for background subprocess use. Default interval 30 s. |

### Removed: `goto` and `park`

Both subcommands were removed 2026-05-24 after a chained `goto NGC7000` → `park` test sequence drove the bare mount into a hard mechanical limit. Root cause: the script had no way to verify that the mount's internal RA/Dec coords matched the OTA's actual physical position after repeated power cycles, and chained motion commands compounded the desync.

Slewing operations now belong to:
- **ASIAIR** (via USB-Serial) for guided imaging sessions, or
- **The 8409 hand controller** directly for manual GoTo.

See [[../03_Techniques/Mount-Diagnostics.md#Removed-goto-and-park]] for the full rationale and what safety gates would need to be added before re-introducing either subcommand.

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

The mount's WiFi-to-Serial bridge multiplexes a single 115200 8N1 serial link to the 8409 hand controller. Two clients writing at the same time produce garbled responses. **Do not run `mount.py` while ASIAIR is connected to the mount via the USB-Serial cable.** For the read-only subcommands it's mostly harmless but still discouraged.

### Tests

```bash
python3 -m unittest scripts.test_mount                     # unit + mock tests (no mount needed)
MOUNT_TEST_LIVE=1 python3 -m unittest scripts.test_mount   # + live integration tests
```

Live tests require the mount powered on and reachable at `192.168.178.87`. All live tests are read-only (or `timesync`, which writes config but does not move the mount).

### Reference docs

- iOptron RS-232 command spec: `01_Equipment/Manuals/CEM26/ASCOM-Driver/RS-232_Command_Language2014V310.pdf` (V3.10)
- Equipment note: [[../01_Equipment/Mount/iOptron-CEM26.md]] — WiFi/firmware setup
- Workflow guide: [[../03_Techniques/Mount-Diagnostics.md]] — when to use which subcommand
