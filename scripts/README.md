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
| `--cfa green` | none | extract a full-res green channel from a raw Bayer frame before fitting |
| `--cfa-pattern` | RGGB | Bayer pattern for `--cfa` (ASI2600MC is RGGB) |
| `--psf-out FILE` | — | write synthetic PSF FITS (with FWHMX/FWHMY/BETA keys) |
| `--csv FILE` | — | per-star fits (cx,cy,fwhmx,fwhmy,fwhm,beta,ecc,rmad) |

**Output:** prints FWHM x/y, eccentricity, β, median FWHM, and `==> BXT PSF Diameter: N`.

> ⚠️ **For the BXT number, measure on the same image you'll deconvolve.** Best on a debayered/processed image. On a **raw Bayer frame**, the R/B mosaic biases the fit — use **`--cfa green`** (interpolates the full-res green channel, removing the mosaic at native scale). Validation on a Mel 111 light vs PixInsight SubFrameSelector (2.28 px): raw CFA **2.03 px** (11 % low) → **`--cfa green` 2.36 px** (~3.5 % — much closer). Synthetic (no CFA) recovery is exact. Also match the **image scale** — a PSF measured on the native master must not be reused on a drizzle-2× master (stars ~2× wider).

### Tests

```bash
python3 scripts/test_psf_image.py     # synthetic Moffat/Gaussian recovery + FITS round-trip
```

Synthetic recovery is exact (Moffat 3.20 → 3.200 px, Gaussian 2.80 → 2.800 px).

---

## set_filter.py — write the filter into frames/masters before WBPP

Manual filters (no EFW) mean the ASIAIR never records the filter in frame metadata — it only puts it in the **filename** (`…-9.6C_LPro_0001.fit`). That's why WBPP can't auto-match filter-specific flats, can't tell L-Pro from FQuad (all read `NoFilter`), and names masters `FILTER-NoFilter`. This reads the filter **from the filename** (or `--filter`) and writes it where WBPP actually looks. See [[../04_Processing/Calibration/Calibration-Strategy.md]].

It handles **two file types**, because WBPP reads filter from a *different* place in each:

| File type | What WBPP reads | What the script writes |
|---|---|---|
| **FITS** `.fit/.fits` (raw lights/flats) | the FITS **`FILTER`** keyword | sets the `FILTER` keyword |
| **XISF** `.xisf` (master flats) | the native **`Instrument:Filter:Name` property** (it **ignores** the FITS keyword here!) | sets the property (and the FITS keyword too) |

> ⚠️ **The XISF gotcha (paid for on Mel 111, 2026-06-01):** a master flat whose *filename* and FITS `FILTER` keyword both say `LPro` still grouped under **NoFilter** in WBPP, because its `Instrument:Filter:Name` **property** was empty/absent. Setting only the FITS keyword is not enough for `.xisf` masters — you must set the property. Older masters may lack the property entirely; the script **inserts** it.

Stdlib only. **Data-preserving on both paths:** FITS rewrites only the header region; XISF rewrites only the XML header and re-pads so the data block stays at its original absolute (alignment-padded) offset. Every write verifies the **data-block MD5 is unchanged** and aborts if not.

```bash
python3 scripts/set_filter.py <folder>                 # DRY RUN — preview only
python3 scripts/set_filter.py <folder> --apply         # write filter from filename
python3 scripts/set_filter.py <master.xisf> --filter FQuad --apply   # force a value
python3 scripts/set_filter.py <folder> --recursive --apply           # whole master library
```

| Option | Default | Meaning |
|---|---|---|
| `--apply` | off (dry run) | actually write; default just previews |
| `--filter VALUE` | auto from filename | force a filter (raw frames with no token, or to override) |
| `--recursive` | off | recurse into subfolders |

- Auto-detects the filter from raw tokens (`…_-9.6C_LPro_0001.fit`) **and** master tokens (`…_FILTER-LPro_…xisf`).
- **Darks / bias / dark-flats are skipped** — no filename token, filter-independent (don't force `--filter` on them).
- **Run on the lights + flats (and master flats) before WBPP.** Then WBPP matches flats to lights by filter automatically — no more "only one flat" workaround.
- A motorized EFW would write the filter directly and make this unnecessary.

### Tests

```bash
python3 scripts/test_set_filter.py     # FITS + XISF: autodetect, insert/replace/grow, data-MD5-unchanged, full-rewrite fallback
```

The key safety tests assert the **pixel/attachment data block is byte-identical** after the edit — across the FITS header-only path, FITS full-rewrite, and all three XISF paths (replace, grow, insert-when-absent).

---

## frame_info.py — inspect FITS / XISF metadata + astrometric status

One-stop header reader for FITS **and** XISF (file or folder). Surfaces **filter** (FITS keyword *and* the XISF `Instrument:Filter:Name` property — and shows when they disagree), exposure / gain / temp, dimensions, **plate scale** (from the CD matrix, CDELT, or focal/pixel), **WCS solved? + centre coords + rotation**, and optionally channel stats. **Header-only by default** — never loads pixel data, so it's instant on multi-GB masters.

Stdlib only (numpy only for `--stats`).

```bash
python3 scripts/frame_info.py <file>                 # detailed readout
python3 scripts/frame_info.py <folder> [--recursive]  # one-row-per-file table (WCS triage)
python3 scripts/frame_info.py <file> --stats          # + channel median/max/clip%
```

- **Folder mode is the reprocessing-triage view** — the `WCS` column flags masters that lack an astrometric solution (the ones a re-solve unblocks; see [[../05_Sessions/2026/Processing/2026-06-01-Astrometric-Diagnosis.md]]).
- **Filter:** the XISF *property* wins over the FITS keyword (that's what WBPP groups by) — so this is the quick check for the "master flat reads NoFilter" trap that `set_filter.py` fixes.
- Use it to confirm scale before BXT/ImageSolver (native 3.10 vs drizzle 1.548 ″/px), verify a master is solved before SPCC, or audit which filter a stack was really shot through.

### Tests

```bash
python3 scripts/test_frame_info.py     # CD-scale/centre/rotation, XISF property-vs-keyword, WCS flag, sexagesimal, folder iteration
```

---

## moving_object.py — find comets/asteroids in a light-frame sequence

Detects **moving objects** (asteroids, comets, NEOs) across a night's lights and **excludes satellites**. The discriminator: a real solar-system mover drifts along a roughly linear track across **many** frames against the fixed stars; a satellite is a streak in **one** frame only.

Runs on **`.fit` or `.xisf` lights** — each must carry its own plate solution (CD matrix + CRVAL/CRPIX + DATE-OBS), so detections are mapped to **RA/Dec per frame** and movers are found in sky coordinates (pointing-independent; dithering is fine). Single-channel frames are treated as CFA (de-mosaiced green); multi-channel as already-debayered luminance. Reuses `psf_image.py`.

**Multi-night aware:** frames are grouped into nights (gap > `--night-gap` h, default 6) and linked **within** each night — a real mover crosses degrees per day, so cross-night linking is meaningless. Duplicate-timestamp frames (reprocessed `_a_a` etc.) are dropped automatically.

```bash
python3 scripts/moving_object.py <lights-folder>                 # fast: per-frame linking (default)
python3 scripts/moving_object.py <folder> --shift-stack          # + faint-mover synthetic tracking (slow)
python3 scripts/moving_object.py <folder> --vmax 8 --min-frames 5 --out DIR
```

Two passes:
- **Per-frame linking** (default) — movers bright enough to clear the threshold in individual subs; linked into a constant-velocity sky track (≥ `--min-frames`, default 4). Fast.
- **Shift-and-stack** (`--shift-stack`, opt-in) — synthetic tracking that recovers **faint sub-threshold** movers: bins + translation-aligns the frames (the CEM26 is equatorial → no field rotation, only dither), then max-projects across a bounded velocity grid (`--vmax` ″/min). The slow pass (thousands of velocity stacks) — enable it only when you want the deep search.

It rejects three things that would otherwise fake a mover:
- **stars** (fixed in sky);
- **hot pixels / sensor defects** (fixed on the *sensor* — but they drift in sky coords under dithering, so they're caught by *pixel*-position clustering, flagged if pinned to one pixel in ≥ 4 frames);
- **fixed-pixel + pointing-drift artifacts** — a stuck bright pixel whose sky coordinate is swept *linearly* by the night's cumulative mount drift looks exactly like a fast linear mover. A real mover must travel in **pixel** space too, so any track whose sky rate implies a large pixel motion but whose source barely moved on the sensor is rejected.

Tracks slower than `--min-rate` are also dropped as effectively stationary (bright corner stars wobble at ~0.1–0.2 ″/min because SIP distortion is ignored).

| Option | Default | Meaning |
|---|---|---|
| `--out DIR` | `<folder>/moving-objects` | output dir |
| `--min-frames N` | 4 | min frames a track must span |
| `--min-rate R` | 0.5 | min motion to count as a mover (″/min); slower = stationary |
| `-k N` | 6.0 | per-frame detection threshold (σ) |
| `--max-per-frame N` | 600 | cap on detections kept per frame (brightest; bounds runtime on hot-pixel-heavy raw subs) |
| `--vmax` / `--vstep` | 5.0 / 0.5 | searched motion range / step (″/min) |
| `--bin` | 4 | binning for the shift-stack search |
| `--jobs N` | 0 (all cores) | parallel workers for the per-frame read+detect pass; `1` = serial |
| `--night-gap H` | 6 | hours of gap that splits frames into separate nights (linked within each) |
| `--shift-stack` | off | also run the slow faint-mover pass |
| `--no-png` | off | skip the candidate PNGs |

**Performance:** the per-frame pass (read → green → background → detect) is parallelised across cores (`--jobs`), and the clustering/linking are O(N) grid + vectorised + velocity-pruned — a 6-frame link run dropped from ~100 s to ~3 s. The optional `--shift-stack` pass is the slow one (thousands of velocity stacks). Working on **calibrated** subs (dark-subtracted) is also much faster than raw, since raw subs throw thousands of hot-pixel detections.

**Outputs** (to `--out`): `report.txt` (per candidate: track table, motion rate ″/min + PA, RA/Dec, frames spanned, relative brightness), a crop-stack **montage** + **annotated** PNG per linked candidate, and a DS9/PixInsight `candidates.reg`.

> Caveats (also in the report): SIP ignored (linear CD — fine at mover scale); magnitudes are relative/instrumental; very slow movers (drift < match tolerance over the session) may be missed; the shift-stack velocity grid is **bounded** at `--vmax` and logs if it caps the grid (no silent truncation). Needs frames to share pointing (a large mid-session re-slew breaks linking).

### Tests

```bash
python3 scripts/test_moving_object.py     # synthetic sequence: mover recovery, satellite exclusion, faint-only-via-shift-stack, WCS round-trip, star rejection
```

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
