---
title: "M16 Eagle Nebula — Summer 2026 Campaign"
type: capture-session
date: 2026-06-01
location: "Tuntange, Luxembourg"
equipment:
  camera: "[[ASI2600MCPro]]"
  telescope: "[[RedCat-51]]"
  mount: "[[iOptron-CEM26]]"
  filter: "[[Antlia-FQuad]]"
  guider: "[[ASI385MC]]"
  guidescope: "[[UniGuide-32mm]]"
targets:
  - "[[M16-Eagle]]"
tags:
  - session/capture
---

# M16 Eagle Nebula — Summer 2026 Campaign

Multi-month accumulation campaign to reach publishable SNR on a low-altitude target.

---

## Target Summary

| Parameter | Value |
|-----------|-------|
| Object | [[M16-Eagle\|M16]] — Eagle Nebula (Pillars of Creation) |
| RA / Dec | 18h 19m / -13deg 47' |
| Angular size | 35' x 28' |
| Max transit altitude | ~27deg (airmass 2.2) |
| Constellation | Serpens |

---

## Campaign Goal

| Metric | Target |
|--------|--------|
| SNR on nebula | 25–30 (publishable quality on Pillars) |
| Total integration | 20–30h across 3 months |
| Processing workflow | [[QuadBand-OSC-Workflow]] + [[HDR-Workflow]] |

> [!info] Why 20–30h?
> At 27deg altitude with limited astronomical darkness, SNR accumulates ~3x slower than a well-placed winter target. See [[SNR#Integration Time Estimates]].

---

## Monthly Windows

### June — Marginal Start

| Parameter | Value |
|-----------|-------|
| Dark hours | ~4h (no astronomical darkness — sun stays above -18deg) |
| Camera temp | -10degC |
| M16 window | ~23:30–04:30 CEST (~5h above 10deg) |
| Usable window | ~00:30–03:30 CEST (~3h during darkest sky) |
| Max subs/night | ~32 (300s, accounting for dithering overhead) |
| Expected quality | Noisiest subs — elevated sky background, high airmass |

**Best nights:** New moon window (~June 8–18, verify with `/session-plan`)

> [!warning] June limitations
> No true astronomical darkness at latitude 49.6degN. The sky never fully darkens. Narrowband [[Antlia-FQuad]] is essential — broadband would be unusable. Expect 30–40% of subs to be rejected in SubframeSelector due to sky background.

**Monthly target:** 3–4 clear nights, ~6–8h usable integration after rejection.

---

### July — Improving

| Parameter | Value |
|-----------|-------|
| Dark hours | ~5h (brief astronomical darkness returns mid-month) |
| Camera temp | -10degC |
| M16 window | ~22:30–03:30 CEST (~5h above 10deg) |
| Usable window | ~23:30–03:00 CEST (~3.5h during darkest sky) |
| Max subs/night | ~38 (300s) |
| Expected quality | Better than June — some true darkness, same airmass |

**Best nights:** New moon window (~July 7–17, verify with `/session-plan`)

> [!tip] July strategy
> M16 is best placed in early July (still near opposition). Prioritize early July nights over late July. Consider pairing with [[M17-Omega]] (similar RA, 2.4deg lower in Dec at ~24deg altitude).

**Monthly target:** 3–4 clear nights, ~8–10h usable integration after rejection.

---

### August — Best Month

| Parameter | Value |
|-----------|-------|
| Dark hours | ~7h (full astronomical darkness) |
| Camera temp | -10degC |
| M16 window | ~21:00–01:30 CEST (~4.5h above 10deg) |
| Usable window | ~22:00–01:00 CEST (~3h, M16 sets earlier) |
| Expected quality | Best sky darkness, but M16 is setting earlier in the evening |

**Best nights:** New moon window (~Aug 5–15, verify with `/session-plan`)

> [!warning] August timing
> M16 sets earlier each week. By late August it is too low after twilight. Prioritize early August. After M16 sets, switch to [[NGC6960]] or [[NGC7000-North-America]] to fill the rest of the night.

**Monthly target:** 3–4 clear nights, ~6–8h usable integration after rejection.

---

## Cumulative Integration Plan

| Month | Nights (goal) | Integration/night | Monthly total | Cumulative | Est. SNR |
|-------|---------------|-------------------|---------------|------------|----------|
| June | 3–4 | ~2–2.5h usable | ~6–8h | 6–8h | ~10–12 |
| July | 3–4 | ~2.5–3h usable | ~8–10h | 14–18h | ~16–20 |
| August | 3–4 | ~2–2.5h usable | ~6–8h | 20–26h | ~22–28 |

> [!success] SNR Projection
> At 20–26h total integration, expected SNR 22–28 on the nebula emission. The Pillars of Creation should be clearly resolved with good contrast. Reaching 30h would push SNR above 30.

---

## Capture Settings

Consistent across all sessions:

| Parameter | Value |
|-----------|-------|
| Filter | [[Antlia-FQuad]] |
| Exposure | 300s |
| Gain | 100 |
| Temperature | -10degC |
| Binning | 1x1 |
| Dithering | Enabled (required for drizzle) |
| Guiding | [[ASI385MC]] + [[UniGuide-32mm]] |

> [!important] Do not change these settings between sessions
> Cross-session stacking requires identical gain, temperature, and filter. Changing any parameter creates a separate calibration group and complicates integration.

---

## Calibration Checklist

### Darks

- [x] 300s / Gain 100 / -10degC — **available** in [[Master-Library]]

### Flats

- [ ] Capture new flats **each session** with [[Antlia-FQuad]] before dismounting
- Existing Quad Band flats (50ms and 60ms masters) may work if optical train unchanged
- Revalidate at start of campaign — check for dust, rotation changes since March 2025

### Dark Flats

- [x] 60ms / Gain 100 — **available** in [[Master-Library]]
- Match to flat exposure — if flat exposure changes, new dark flats needed

### Bias

- [x] Gain 100 — **available** in [[Master-Library]]

---

## SubframeSelector Strategy

Be aggressive with rejection — quality over quantity at this airmass.

| Metric | Reject if |
|--------|-----------|
| FWHM | > 6 pixels (seeing is worse at 27deg altitude) |
| Eccentricity | > 0.6 |
| Sky background (Median) | > 1.5x the session median (clouds, twilight contamination) |
| SNR Weight | Bottom 20% of each session |

Expect to reject 25–40% of June subs, 15–25% of July/August subs.

---

## Processing Plan

After all data is collected (September 2026):

1. **WBPP** — calibrate and register all sessions together
   - Use per-session flats
   - Shared darks from [[Master-Library]]
   - Drizzle 2x
2. **SubframeSelector** — reject poor subs across the full dataset
3. **ImageIntegration** — winsorized sigma clipping (handles varying sky backgrounds)
4. **Processing** — [[QuadBand-OSC-Workflow]] through to final image
5. **HDR** — [[HDR-Workflow]] for Pillars vs bright cluster region

> [!tip] Intermediate stacks
> Consider processing June-only and June+July stacks as progress checks. This helps verify data quality and catch issues (wrong flats, registration problems) before accumulating 3 months of data.

---

## Session Log

Track actual sessions as they happen:

| Date | Subs taken | Subs accepted | Integration | Conditions | Notes |
|------|-----------|---------------|-------------|------------|-------|
| | | | | | |

**Running total:** 0h / 25h goal

---

## Companion Targets

On M16 nights, after M16 sets or before it rises:

| Object | Window | Filter | Notes |
|--------|--------|--------|-------|
| [[M17-Omega]] | Same as M16 (2.4deg lower) | [[Antlia-FQuad]] | Pair target — shoot both on the same night |
| [[NGC6960]] Western Veil | After M16 sets (~01:30+) | [[Antlia-FQuad]] | July/August — fills rest of the night |
| [[NGC7000-North-America]] | After M16 sets (~01:00+) | [[Antlia-FQuad]] | August — high and well placed late night |
