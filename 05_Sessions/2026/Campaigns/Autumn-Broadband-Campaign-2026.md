---
title: "Autumn Broadband — 2026 Campaign"
type: capture-session
date: 2026-09-15
location: "Tuntange, Luxembourg"
equipment:
  camera: "[[ASI2600MCPro]]"
  telescope: "[[RedCat-51]]"
  mount: "[[iOptron-CEM26]]"
  filter: "[[Optolong-LPro]]"
  guider: "[[ASI385MC]]"
  guidescope: "[[UniGuide-32mm]]"
targets:
  - "[[M33-Triangulum]]"
  - "[[M31-Andromeda]]"
  - "[[M45-Pleiades]]"
tags:
  - session/capture
---

# Autumn Broadband — 2026 Campaign

L-Pro broadband targets for moonless autumn nights. Galaxies and reflection nebulae that don't benefit from narrowband.

---

## Campaign Priority: MEDIUM

These targets require dark, moonless skies and the [[Optolong-LPro]] filter. They compete for the same clear nights as QB campaigns, so schedule them during new moon windows when QB targets are less critical, or on nights where Cygnus/winter targets aren't optimally placed.

> [!warning] Filter constraint
> Single filter per session. An L-Pro night means no QB targets that night. Plan L-Pro nights deliberately — don't default to it.

---

## Targets

| Object | Size | Alt | Window | Existing Data | Goal | Priority |
|--------|------|-----|--------|---------------|------|----------|
| [[M33-Triangulum]] | 73' | 71deg | ~3h | 0h (ASI) | 10–12h | HIGH |
| [[M31-Andromeda]] | 178' | 82deg | ~1.5h | 3.3h (ASI) | 10–12h total | MEDIUM |
| [[M45-Pleiades]] | 110' | 65deg | ~4h | ~4h (ASI, QB) | 8–10h (L-Pro) | MEDIUM |

> [!info] M45 reshoot rationale
> Existing M45 data was shot with [[Antlia-FQuad]] (Dec 2024). The Pleiades are a reflection nebula — narrowband misses the blue nebulosity. L-Pro data will show the characteristic dust lanes and Merope nebula properly.

---

## Monthly Windows

### September — M33 and M31

| Parameter | Value |
|-----------|-------|
| Dark hours | ~9h |
| Camera temp | -10degC |
| M33 window | ~23:00–02:00 CEST (~3h) |
| M31 window | ~22:00–23:30 CEST (~1.5h, near zenith) |

**Strategy:** M31 first (brief south window, transit near zenith ~82deg), then M33 (longer window at 71deg). Both are in the same sky region — minimal slewing.

**Best nights:** Moonless nights (~Sep 7–17). Dedicate 2–3 nights to L-Pro.

**Monthly target:** 2–3 clear nights. ~3h on M31, ~6h on M33.

---

### October — Peak Month for M33

| Parameter | Value |
|-----------|-------|
| Dark hours | ~10h |
| Camera temp | -20degC |
| M33 window | ~21:00–00:00 CEST (~3h) |
| M31 window | ~20:00–21:30 CEST (~1.5h) |
| M45 window | ~00:00–04:00 CEST (~4h) |

**Strategy:** M31 early (setting), M33 mid-evening, then M45 after midnight. October is the best month for M33 — prioritize it. M45 rises late and fills the rest of the night.

**Best nights:** Moonless nights (~Oct 6–16). Dedicate 2–3 nights to L-Pro.

**Monthly target:** 2–3 clear nights. ~3h on M31, ~4h on M33, ~6h on M45.

---

### November — M45 and Wrap-Up

| Parameter | Value |
|-----------|-------|
| Dark hours | ~12h |
| Camera temp | -20degC |
| M33 window | ~19:00–22:00 CET (~3h, early evening, last good month) |
| M45 window | ~21:00–01:00 CET (~4h) |

**Strategy:** Last M33 data early evening, then M45 for the mid-evening window. After M45, switch to QB filter for winter emission targets.

**Best nights:** Moonless nights (~Nov 5–15). Dedicate 1–2 nights to L-Pro.

**Monthly target:** 1–2 clear nights. ~3h on M33 (final), ~4h on M45.

---

## Cumulative Integration Plan

### M33 — Triangulum Galaxy

| Month | Nights | Integration/night | Monthly total | Cumulative | Est. SNR |
|-------|--------|-------------------|---------------|------------|----------|
| Sep | 2–3 | ~2.5h | ~5–6h | 5–6h | ~16–18 |
| Oct | 2–3 | ~2.5h | ~5–6h | 10–12h | ~22–25 |
| Nov | 1 | ~2.5h | ~2.5h | 12–14h | ~25–27 |

> [!success] M33 SNR projection
> At 71deg altitude with L-Pro on moonless nights, expect good signal. 12–14h should give SNR 25–27 — enough to reveal spiral arms and HII regions. First ASI2600MC data on this target.

### M31 — Andromeda Galaxy

| Month | New data | Cumulative (incl. existing 3.3h) | Est. SNR |
|-------|----------|----------------------------------|----------|
| Sep | ~3h | ~6.3h | ~16–18 |
| Oct | ~3h | ~9.3h | ~20–22 |

> [!tip] M31 framing
> M31 at 178' exceeds the 5.4deg x 3.6deg FOV in one dimension. Consider centering on the galaxy core for single-frame, or a 2-panel mosaic for the full extent including M32 and M110.

### M45 — Pleiades (L-Pro reshoot)

| Month | New data | Cumulative (L-Pro only) | Est. SNR |
|-------|----------|-------------------------|----------|
| Oct | ~6h | ~6h | ~18–20 |
| Nov | ~4h | ~10h | ~24–26 |

---

## Capture Settings

| Parameter | Value |
|-----------|-------|
| Filter | [[Optolong-LPro]] |
| Exposure | 180s (galaxies, clusters) |
| Gain | 100 |
| Temperature | -10degC (Sep) / -20degC (Oct–Nov) |
| Binning | 1x1 |
| Dithering | Enabled |

> [!important] 180s exposure for broadband
> L-Pro targets use 180s subs (not 300s). This matches the [[RGB-Workflow]] defaults and existing dark library entries.

---

## Calibration Checklist

| Frame | -10degC (Sep) | -20degC (Oct–Nov) |
|-------|---------------|-------------------|
| Dark 180s | Available | **Incomplete (20/25 raws, no master)** |
| Flat (L-Pro) | Per session (master available from Mar 2025) | Per session |
| Dark flat 60ms | Available | Available |
| Bias g100 | Available | Available |

> [!warning] 180s/-20degC darks incomplete
> Only 20 raws exist, no master stacked. Need 5 more raws + master integration. See [[Master-Library]]. **Do this before October.**

---

## Moon Scheduling

L-Pro targets are sensitive to moonlight. Only shoot on nights with:

| Condition | Acceptable |
|-----------|-----------|
| Moon illumination | < 25% |
| Moon distance from target | > 40deg |
| Moon below horizon | Ideal |

In practice: **shoot L-Pro during the new moon week only** (±5 days from new moon). Use the rest of the month for QB campaigns.

---

## SubframeSelector Strategy

| Object | FWHM limit | Eccentricity | Sky background | Expected rejection |
|--------|-----------|--------------|----------------|-------------------|
| M33 | < 4.5 pixels | < 0.4 | < 1.2x median | ~10% |
| M31 | < 4 pixels | < 0.4 | < 1.2x median | ~10% |
| M45 | < 4.5 pixels | < 0.4 | < 1.2x median | ~10% |

Tighter sky background threshold than QB campaigns — broadband is more sensitive to LP variations.

---

## Processing Plan

- **M33:** [[RGB-Workflow]] — spiral structure, HII regions
- **M31:** [[RGB-Workflow]] — dust lanes, core detail. Consider mosaic if 2-panel
- **M45:** [[RGB-Workflow]] — reflection nebulosity, blue dust around Merope

---

## Session Log

| Date | Target | Subs taken | Subs accepted | Integration | Conditions | Notes |
|------|--------|-----------|---------------|-------------|------------|-------|
| | | | | | | |

**Running totals:**
- M33: 0h / 12h goal
- M31: 3.3h existing + 0h new / 12h goal
- M45: 0h L-Pro / 10h goal
