---
title: "Cygnus Complex — Autumn 2026 Campaign"
type: capture-session
date: 2026-09-01
location: "Tuntange, Luxembourg"
equipment:
  camera: "[[ASI2600MCPro]]"
  telescope: "[[RedCat-51]]"
  mount: "[[iOptron-CEM26]]"
  filter: "[[Antlia-FQuad]]"
  guider: "[[ASI385MC]]"
  guidescope: "[[UniGuide-32mm]]"
targets:
  - "[[NGC7000-North-America]]"
  - "[[IC5070-Pelican]]"
  - "[[NGC6960-Western-Veil]]"
  - "[[NGC6992-Eastern-Veil]]"
tags:
  - session/capture
---

# Cygnus Complex — Autumn 2026 Campaign

Last window for Cygnus targets before they set for the season. Priority: NGC 7000 Quad Band data.

---

## Campaign Priority: HIGH

[[NGC7000-North-America]] has 23h of L-Pro data but the [[Seasonal-Calendar]] flags QB data as the **top priority** for August. September is the last good month. The Veil Nebula has **zero data** — first light opportunity.

---

## Targets

| Object | Size | Alt | Window | Existing Data | Goal |
|--------|------|-----|--------|---------------|------|
| [[NGC7000-North-America]] | 120' | 85deg | ~2h | 23h (L-Pro only) | 8–10h QB |
| [[IC5070-Pelican]] | 60' | 85deg | ~2h | None | 8–10h QB |
| [[NGC6960-Western-Veil]] | 70' | 71deg | ~3h | None | 10–12h |
| [[NGC6992-Eastern-Veil]] | 60' | 72deg | ~3h | None | 10–12h |

> [!info] NGC 7000 and IC 5070
> Adjacent objects — depending on framing, both may fit in a single FOV (5.4deg x 3.6deg). The 2deg gap between centers is within the field. Consider a mosaic of two panels if you want both fully framed.

---

## Monthly Windows

### September — Prime Time

| Parameter | Value |
|-----------|-------|
| Dark hours | ~9h (full astronomical darkness) |
| Camera temp | -10degC |
| NGC 7000 / IC 5070 window | ~20:30–22:30 CEST (~2h in south corridor) |
| Veil Nebula window | ~20:30–23:30 CEST (~3h) |
| Conditions | Excellent — full dark, targets well placed early evening |

**Strategy:** Start with NGC 7000/IC 5070 (transits early, brief window), then swing to Veil for the rest of the early night. After ~23:30, Cygnus targets set — switch to late-night targets ([[M33-Triangulum]], [[M45-Pleiades]] with L-Pro, or [[M42-Orion]] late).

**Best nights:** New moon window (~Sep 7–17, verify with `/session-plan`)

**Monthly target:** 4–5 clear nights. ~8h on NGC 7000/IC 5070, ~12h on Veil.

---

### October — Last Chance

| Parameter | Value |
|-----------|-------|
| Dark hours | ~10h (longest useful dark) |
| Camera temp | -20degC |
| NGC 7000 / IC 5070 window | ~19:30–21:30 CEST (~2h, early evening) |
| Veil Nebula window | ~19:30–22:30 CEST (~3h) |
| Conditions | Good — targets shift to early evening, setting earlier each week |

**Strategy:** Cygnus first (before it sets), then transition to late-night winter targets. By late October NGC 7000 is too low — focus on Veil in early October.

**Best nights:** New moon window (~Oct 6–16, verify with `/session-plan`)

**Monthly target:** 2–3 clear nights. Finish Veil data. Any NGC 7000 bonus is welcome.

---

## Cumulative Integration Plan

### NGC 7000 / IC 5070 (Quad Band)

| Month | Nights | Integration/night | Monthly total | Cumulative | Est. SNR |
|-------|--------|-------------------|---------------|------------|----------|
| Sep | 4–5 | ~2h | ~8–10h | 8–10h | ~20–22 |
| Oct | 1–2 | ~1.5h | ~2–3h | 10–13h | ~22–25 |

> [!tip] SNR context
> NGC 7000 transits at 85deg (near zenith) — brief window but excellent signal per sub. The high altitude compensates for short sessions. SNR 22–25 at 10–13h is achievable because airmass is ~1.0.

### Veil Nebula (NGC 6960 + NGC 6992)

| Month | Nights | Integration/night | Monthly total | Cumulative | Est. SNR |
|-------|--------|-------------------|---------------|------------|----------|
| Sep | 4–5 | ~2.5h | ~10–12h | 10–12h | ~22–25 |
| Oct | 2–3 | ~2h | ~4–6h | 14–18h | ~26–30 |

> [!success] Veil SNR projection
> At 71deg altitude with full darkness, the Veil responds well. 14–18h should produce SNR 26–30 — excellent for the delicate filaments. Split integration roughly evenly between Western and Eastern arcs, or shoot both in a wider framing.

---

## Capture Settings

| Parameter | Value |
|-----------|-------|
| Filter | [[Antlia-FQuad]] |
| Exposure | 300s |
| Gain | 100 |
| Temperature | -10degC (Sep) / -20degC (Oct) |
| Binning | 1x1 |
| Dithering | Enabled |

> [!warning] Temperature change at October boundary
> September uses -10degC, October switches to -20degC. These require **separate dark masters** in calibration. 300s/-10degC darks are available. 300s/-20degC darks are **needed** — see [[Master-Library#Complete Needs Summary]]. Acquire before October sessions.

---

## Calibration Checklist

| Frame | -10degC (Sep) | -20degC (Oct) |
|-------|---------------|---------------|
| Dark 300s | Available | **Needed — priority** |
| Flat (QB) | Per session | Per session |
| Dark flat 60ms | Available | Available |
| Bias g100 | Available | Available |

---

## SubframeSelector Strategy

| Metric | NGC 7000/IC 5070 (85deg) | Veil (71deg) |
|--------|--------------------------|--------------|
| FWHM | < 4 pixels | < 4.5 pixels |
| Eccentricity | < 0.4 | < 0.4 |
| Sky background | < 1.3x session median | < 1.3x session median |
| Rejection rate | ~10–15% | ~10–15% |

High-altitude targets — expect good quality subs with low rejection.

---

## Processing Plan

Process each target separately after data collection:

- **NGC 7000 QB:** [[QuadBand-OSC-Workflow]] — first QB result. Compare with existing L-Pro data
- **IC 5070:** [[QuadBand-OSC-Workflow]] — may combine with NGC 7000 for a wide mosaic
- **NGC 6960 + NGC 6992:** [[QuadBand-OSC-Workflow]] — process each arc independently, consider a mosaic panel

---

## Session Log

| Date | Target | Subs taken | Subs accepted | Integration | Conditions | Notes |
|------|--------|-----------|---------------|-------------|------------|-------|
| | | | | | | |

**Running totals:**
- NGC 7000 QB: 0h / 10h goal
- IC 5070: 0h / 10h goal
- NGC 6960: 0h / 8h goal
- NGC 6992: 0h / 8h goal
