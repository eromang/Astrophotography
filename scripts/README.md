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

## gradient_check.py — did gradient removal flatten the sky without eating the object?

QA for a gradient-correction step (**GraXpert / MGC / DBE**). Quantifies the two things that matter on a frame-filling nebula like M42: did it **flatten the background**, and did it **avoid eating the faint outer wings** (the over-subtraction failure). Reads the corrected image (and optionally the background model), or A/B-compares two corrected images of the same field to pick a winner. Reuses `psf_image.py`'s XISF/FITS readers. Full guide + interpretation in [[../04_Processing/Pixinsight/Gradient-Check.md]].

```bash
python3 scripts/gradient_check.py corrected.xisf --model bg.xisf --png /tmp/gc   # single + model
python3 scripts/gradient_check.py M42_MGC.xisf --against M42_GraXpert.xisf        # A/B verdict
python3 scripts/gradient_check.py corrected.xisf --json                           # machine-readable
```

| Metric | Meaning |
|---|---|
| **rel_spread** (flatness) | percentile spread of local sky across an N×N grid, normalised to the median — **lower = flatter**; directly comparable between methods |
| **negatives / dark-tile deficit** | over-subtraction: % negative pixels + how far the darkest region fell below the median region (in MAD) |
| **wing mean-above-bg** | retained flux in an annulus around the object — the faint outer nebulosity; **higher = more wings preserved** |
| **model imprint_corr** | correlation of the background MODEL with the object; **> 0.30 ⇒ the model contains the nebula** (it's about to subtract real signal) |

| Option | Default | Meaning |
|---|---|---|
| `--model PATH` | — | also analyse the background model (contrast + imprint) |
| `--against PATH` | — | A/B compare vs a second corrected image (same registered field) → winner + reason |
| `--png PREFIX` | — | write asinh previews (`_corrected.png`, `_model.png`, `_B_*`) |
| `--grid` / `--pct` | 4 / 10 | flatness grid size / per-tile sky percentile |
| `--json` | — | machine-readable output |

**Worked example (M42 reprocess, 2026-06-22):** GraXpert @ 0.8 → rel_spread **0.018**, **0%** negatives, model **imprint_corr 0.003** (no nebula in the model) — a clean baseline. Compare against MGC+DR2 with `--against` and let the wing-signal delta decide. The `--against` verdict prefers **more wing signal as long as flatness is within 2× of the flatter method** — so it won't reward a method that "wins" flatness by over-flattening the nebula away.

### Tests

```bash
python3 scripts/test_gradient_check.py   # synthetic gradient+nebula: flatness, wing-eating, imprint, center, A/B (5 tests)
```

---

## find_background.py — find the optimal background ROI (fast)

A numpy / integral-image reimplementation of the SetiAstro **FindBackground.js** PixInsight script. Finds the **darkest, flattest `size`×`size` window** — the background region to feed an SPCC neutralization ROI, a MultiscaleAdaptiveStretch background reference, BackgroundNeutralization, or DBE sampling. Reuses `psf_image.py`-style XISF/FITS reading. Full guide in [[../04_Processing/Pixinsight/Find-Background.md]].

**Faster than the JS:** FindBackground.js samples pixels one-by-one in PixInsight's JS engine (O(N·window²)) then *approximates* with gradient descent. This computes per-window mean+stddev for **every** position in one O(N) pass via **integral images**, then takes the **exact** global minimum — **~2 s on a 96 MP drizzled master vs minutes**.

```bash
python3 scripts/find_background.py <image.xisf>                 # ROI coords + per-channel bg + colour-correction
python3 scripts/find_background.py img.xisf --size 100 --top 5  # 5 best non-overlapping spots
python3 scripts/find_background.py img.xisf --exclude 5000,3000,2000,2000 --png roi.png
```

| Option | Default | Meaning |
|---|---|---|
| `--size N` | 50 | ROI side length (px) |
| `--exclude X,Y,W,H` | — | exclude a rectangle (repeatable) — e.g. the nebula core |
| `--scale N` | 1 (exact) | downsample before searching; coords still reported full-res. Use 2–4 to cut memory on huge masters |
| `--top N` | 1 | also print N best non-overlapping candidates |
| `--png PATH` | — | stretched preview with the ROI box drawn (verify it's not on nebula) |
| `--json` | — | machine-readable output |

Scoring is faithful to FindBackground's default (average + standard deviation, image-normalised), with one fix: brightness is a consistent per-pixel channel mean throughout (the JS mixes a channel-sum into the stddev term).

### Tests

```bash
python3 scripts/test_find_background.py   # integral vs brute-force, blob/gradient/noise avoidance, exclude, scale, colour (7 tests)
```

---

## star_halos.py — measure star halos; suggest BXT Sharpen values

Turns "the halos look less visible" into a **number**, and suggests BlurXTerminator **Adjust Star Halos** + **Sharpen Stars** starting values. For the brightest unsaturated stars it builds a background-subtracted radial profile, measures the **halo index** (mean normalised flux at 2.5–5× the core HWHM, where a clean PSF ≈ 0), and takes the **bright-star p90** (halos are a bright-star phenomenon — the median is dominated by faint clean stars). FWHM comes from `psf_image.py`'s Moffat fit; both readers/detection are reused from `psf_image`. Full guide: [[../04_Processing/Pixinsight/Star-Halos.md]].

```bash
python3 scripts/star_halos.py img.xisf                       # halo index + suggested Adjust Star Halos / Sharpen Stars
python3 scripts/star_halos.py before.xisf --against after.xisf   # measure the actual halo REDUCTION (%)
```

| Option | Default | Meaning |
|---|---|---|
| `--against PATH` | — | second image (post-BXT) → halo-reduction % — the strongest use |
| `--stars N` | 60 | brightest N stars to measure |
| `--rmax N` | 40 | radial-profile half-box (px) |
| `-k N` | 6.0 | detection threshold (σ) |
| `--json` | — | machine-readable |

⚠️ The index→slider mapping is an **empirical heuristic** (M42-calibrated), a data-driven *starting* value — confirm visually, and use `--against` to verify the reduction. Measure the **Sharpen Stars** value on the **Correct-Only output** (the Sharpen input), same rule as the BXT PSF diameter.

### Tests

```bash
python3 scripts/test_star_halos.py   # haloed>clean, clean-low, FWHM recovery, monotonic suggestions, reduction direction (6 tests)
```

---

## guiding_impact.py — is guiding limiting my resolution?

Offline rebuild of the web **"HLP Guiding RMS Translator"**. Turns a guiding RMS (arcsec) into real imaging impact: the error in **pixels**, the **total FWHM** once seeing is folded in **in quadrature**, and a verdict on whether guiding is actually limiting resolution or the atmosphere still dominates. Full physics + this rig's numbers in [[../03_Techniques/Guiding-RMS-Impact.md]].

Two modes mirror the web tool's tabs:

```bash
python3 scripts/guiding_impact.py --focal 250 --pixel 3.76 --rms 0.8          # basic: total RMS
python3 scripts/guiding_impact.py --focal 250 --pixel 3.76 --ra 0.8 --dec 0.4 # advanced: star shape
python3 scripts/guiding_impact.py --focal 250 --pixel 3.76 --rms 0.8 --seeing 2.2 --json
```

| Option | Default | Meaning |
|---|---|---|
| `--focal` / `--pixel` | — | focal length (mm) / pixel size (µm) |
| `--rms` | — | total guiding RMS (arcsec) → **basic mode** |
| `--ra` / `--dec` | — | per-axis RMS (arcsec) → **advanced mode** (star shape) |
| `--seeing` | — | explicit seeing FWHM (arcsec); overrides the band |
| `--seeing-quality` | ok | `excellent` / `good` / `ok` (2–4″) / `poor` / `bad` |
| `--reducer` / `--binning` | 1.0 / 1 | sampling-only modifiers (do **not** change arcsec RMS) |
| `--json` | — | machine-readable result (for session notes) |

Two things separate this from a naïve calculator, both done correctly here: guiding blur uses **FWHM = 2.355 × RMS** (the Gaussian σ→FWHM factor), and **seeing is added in quadrature to every axis before judging shape** — so a 2:1 RA/DEC imbalance reads as ~11% ellipticity (round stars), not the ~50% a raw ratio screams. Modifiers (reducer, binning) only change image scale, never the arcsec RMS.

### Tests

```bash
python3 scripts/test_guiding_impact.py    # closed-form physics + seeing-quadrature properties (13 tests)
```

---

## sampling.py — is my pixel scale matched to the sky?

Offline rebuild of the web **"HLP Sampling Analyzer"**. Image scale, the disk it's sampling, the ideal pixel-scale band (2.0–3.3 px across the FWHM), and an **undersampled / balanced / oversampled** verdict. Shares the `image_scale()` engine with `guiding_impact.py`. Full physics + the two-FWHM distinction in [[../03_Techniques/Sampling-Analysis.md]].

```bash
python3 scripts/sampling.py --focal 250 --pixel 3.76                  # atmosphere band (planning)
python3 scripts/sampling.py --focal 250 --pixel 3.76 --fwhm-px 2.3    # judge vs your REAL stars
python3 scripts/sampling.py --focal 250 --pixel 3.76 --fwhm 7.1 --json
```

| Option | Default | Meaning |
|---|---|---|
| `--focal` / `--pixel` | — | focal length (mm) / pixel size (µm) |
| `--fwhm-px` | — | **delivered** FWHM in pixels (from `psf_image.py`) — best input |
| `--fwhm` | — | delivered FWHM in arcsec |
| `--seeing` / `--seeing-quality` | ok | atmosphere-only fallback band |
| `--reducer` / `--binning` | 1.0 / 1 | sampling-only modifiers (do **not** change the disk) |
| `--json` | — | machine-readable result |

**The distinction that matters:** judging against the **seeing band** (atmosphere only) the RedCat reads *undersampled* (0.97 px/FWHM) — potential headroom you can't reach at 250 mm. Judging against your **delivered** ~2.3 px stars it reads *balanced* — pixels aren't your bottleneck, the PSF is. The script feeds `psf_image.py`'s measured FWHM directly via `--fwhm-px` and labels which question it answered. Undersampling on a short widefield rig is the correct trade, not a defect; the lever is dither + 2× drizzle, never OSC binning.

### Tests

```bash
python3 scripts/test_sampling.py    # closed-form sampling + input-priority + regime boundaries (12 tests)
```

---

## guide_match.py — can the guider resolve the motion?

Offline rebuild of the web **"HLP Guide System Match Analyzer"**. Guide scale vs imaging scale, and — crucially — the **minimum motion the guider can resolve** via sub-pixel centroiding. Kills the "guide scale must be ≤ imaging scale" myth. Shares `image_scale()` with `guiding_impact.py`. Full physics + the flexure caveat in [[../03_Techniques/Guide-System-Match.md]].

```bash
python3 scripts/guide_match.py --img-focal 250 --img-pixel 3.76 --guide-focal 120 --guide-pixel 3.75   # guide scope
python3 scripts/guide_match.py --img-focal 800 --img-pixel 3.76 --guide-pixel 2.9 --oag                # OAG
python3 scripts/guide_match.py --img-focal 250 --img-pixel 3.76 --guide-focal 120 --guide-pixel 3.75 --centroid 0.4 --json
```

| Option | Default | Meaning |
|---|---|---|
| `--img-focal` / `--img-pixel` | — | imaging focal (mm) / pixel (µm) |
| `--guide-pixel` | — | guide camera pixel (µm) |
| `--guide-focal` | — | guide scope focal (mm); omit in `--oag` |
| `--oag` | off | off-axis guider — inherits imaging focal + reducer |
| `--centroid` | 0.1 | guide centroid accuracy (guide px); ~0.25–0.5 for a dim star |
| `--img-reducer` / `--img-binning` / `--guide-reducer` / `--guide-binning` | 1.0 / 1 | scale modifiers |
| `--json` | — | machine-readable result |

**Why it's right where calculators are wrong:** the verdict is anchored on `min motion = centroid × guide_scale` (≈ `centroid × ratio` imaging px), not the raw ratio — so this rig's 2.08× guide ratio reads **GOOD** (resolves ~0.21 imaging px), not "fail the 1:1 rule." **The blind spot it states explicitly:** it judges *resolution* only, never **differential flexure** — a guide scope can pass this and still trail stars when the tubes shift mid-sub. That's the real guide-scope failure mode; an OAG removes it.

### Tests

```bash
python3 scripts/test_guide_match.py    # scale match + centroiding model + OAG inheritance (11 tests)
```

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

### `--match` — calibration frame matching

Offline rebuild of the HLP **"Astro Frame Match Analysis"** script: compare two frame sets and confirm they match for calibration *before* WBPP, catching the under/over-correction caused by mismatched frames. Compares one set (`path`) against a second (`--against`):

```bash
# lights vs darks — gain, offset, exposure (exact) + temperature (±0.5°C)
python3 scripts/frame_info.py <lights> --match lights-darks --against <darks>
# flats vs flat-darks — same checks
python3 scripts/frame_info.py <flats> --match flats-flatdarks --against <flatdarks>
# darks vs flat-darks — gain/offset/temp + mean brightness (±1.5%), NOT exposure
python3 scripts/frame_info.py <darks> --match darks-flatdarks --against <flatdarks> --bright-sample 5
```

| Pairing | Exact (no tol) | Temp ±0.5°C | Mean brightness ±1.5% |
|---|---|---|---|
| `lights-darks` | gain, offset, exposure | ✓ | — |
| `flats-flatdarks` | gain, offset, exposure | ✓ | — |
| `darks-flatdarks` | gain, offset | ✓ | ✓ (sampled) |

- Prints `MATCH` / `MISMATCH (param…)` and **exits non-zero on a mismatch** (scriptable as a pre-WBPP gate).
- Flags a set that isn't internally uniform (e.g. a wrong-gain frame dropped in the folder).
- `--temp-tol` / `--bright-tol` / `--bright-sample` are tunable. Brightness reads pixel data (needs numpy); the rest is header-only/instant.
- Darks↔flat-darks brightness matches despite huge exposure differences **because the cooled (−10 °C) sensor's dark current is negligible** — both sit on the OFFSET pedestal; a real mismatch means stray light or amp glow. Validated on T7: 300 s darks vs 60 ms flat-darks → Δ0.31%. See [[../04_Processing/Calibration/Calibration-Strategy.md]].

### Tests

```bash
python3 scripts/test_frame_info.py     # CD-scale/centre/rotation, XISF property-vs-keyword, WCS flag, sexagesimal, folder iteration, --match matching/tolerances/exit-code
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
- **two-clump tracks** — a fixed source detected in a *burst* of frames plus one coincidental distant detection fits a line but isn't a continuous moving object. Tracks with a large time gap (one clump + an outlier) are rejected; a real mover is continuous.

It surfaces what survives for **visual review** (the montage/annotated PNGs) rather than auto-rejecting marginal cases — over-filtering would drop real movers entering/leaving the frame.

Tracks slower than `--min-rate` are also dropped as effectively stationary (bright corner stars wobble at ~0.1–0.2 ″/min because SIP distortion is ignored).

| Option | Default | Meaning |
|---|---|---|
| `--out DIR` | `<folder>/moving-objects` | output dir |
| `--min-frames N` | 4 | min frames a track must span |
| `--min-rate R` | 0.5 | min motion to count as a mover (″/min); slower = stationary |
| `-k N` | 6.0 | per-frame detection threshold (σ) |
| `--max-per-frame N` | 600 | cap on detections kept per frame (brightest); raise it (+ lower `-k`) to chase faint movers in dense fields |
| `--max-transients N` | 1500 | seed-pool cap for linking; raise to chase faint movers in dense (cluster / ecliptic) fields |
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
