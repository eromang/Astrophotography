---
title: "Sh2-240 Simeis 147 — Autumn/Winter 2026 Campaign"
type: capture-session
date: 2026-10-01
location: "Tuntange, Luxembourg"
equipment:
  camera: "[[ASI2600MCPro]]"
  telescope: "[[RedCat-51]]"
  mount: "[[iOptron-CEM26]]"
  filter: "[[Antlia-FQuad]]"
  guider: "[[ASI385MC]]"
  guidescope: "[[UniGuide-32mm]]"
targets:
  - "[[Sh2-240-Simeis-147]]"
tags:
  - session/capture
---

# Sh2-240 Simeis 147 — Autumn/Winter 2026 Campaign

The ultimate faint-target challenge. A supernova remnant so dim it needs 25+ hours to reveal its delicate filamentary structure.

---

## Campaign Priority: MEDIUM-HIGH

First light on the faintest target suitable for this setup. Simeis 147 fills the entire FOV at 180' — a perfect match for the [[RedCat-51]]. No existing data.

---

## Target Summary

| Parameter | Value |
|-----------|-------|
| Object | [[Sh2-240-Simeis-147\|Sh2-240]] — Simeis 147 |
| RA / Dec | 05h 39m / +28deg 00' |
| Angular size | 180' (fills the FOV) |
| Transit altitude | ~68deg |
| Constellation | Taurus |
| Surface brightness | Extremely low — among the faintest visual targets |

---

## Campaign Goal

| Metric | Target |
|--------|--------|
| SNR on filaments | 15–20 (detect filamentary structure) |
| Total integration | 25–35h across 3 months |
| Processing workflow | [[QuadBand-OSC-Workflow]] |

> [!info] Why 25–35h?
> Simeis 147 has extremely low surface brightness. Even at 68deg altitude with full dark skies, the faint Ha filaments require enormous integration. See [[SNR#Integration Time Estimates]] — this falls in the "challenging" category due to intrinsic faintness, not altitude.

---

## Monthly Windows

### October — Early Start

| Parameter | Value |
|-----------|-------|
| Dark hours | ~10h |
| Camera temp | -20degC |
| Sh2-240 window | ~01:00–04:00 CEST (~3h, late night) |
| Conditions | Late-night target — rises after Cygnus sets |

**Strategy:** Shoot Cygnus targets early evening ([[Cygnus-Campaign-2026]]), then swing to Simeis 147 after midnight. Two campaigns in one night.

**Best nights:** New moon window (~Oct 6–16, verify with `/session-plan`)

**Monthly target:** 3–4 clear nights, ~7–9h integration.

---

### November — Prime Time

| Parameter | Value |
|-----------|-------|
| Dark hours | ~12h |
| Camera temp | -20degC |
| Sh2-240 window | ~22:00–01:00 CET (~3h) |
| Conditions | Long dark nights, well placed mid-evening |

**Strategy:** Simeis 147 mid-evening, then transition to M42/Rosette late night ([[Winter-Emission-Campaign-2026]]). The 12h dark window allows two full targets per night.

**Best nights:** New moon window (~Nov 5–15, verify with `/session-plan`)

**Monthly target:** 4–5 clear nights, ~10–12h integration.

---

### December — Final Push

| Parameter | Value |
|-----------|-------|
| Dark hours | ~13h |
| Camera temp | -20degC |
| Sh2-240 window | ~20:00–23:00 CET (~3h, early evening) |
| Conditions | Longest nights — Simeis 147 is well placed early, leaving the rest of the night for winter targets |

**Strategy:** Simeis 147 first (early evening), then M42/Rosette/NGC 2264 for the rest of the long night.

**Best nights:** New moon window (~Dec 4–14, verify with `/session-plan`)

**Monthly target:** 4–5 clear nights, ~10–12h integration.

---

## Cumulative Integration Plan

| Month | Nights | Integration/night | Monthly total | Cumulative | Est. SNR |
|-------|--------|-------------------|---------------|------------|----------|
| Oct | 3–4 | ~2.5h | ~7–9h | 7–9h | ~8–10 |
| Nov | 4–5 | ~2.5h | ~10–12h | 17–21h | ~13–15 |
| Dec | 4–5 | ~2.5h | ~10–12h | 27–33h | ~17–19 |

> [!warning] SNR reality check
> Even at 27–33h, SNR on the faintest filaments will be ~17–19. This is adequate to reveal the structure but will require careful processing — aggressive noise reduction and gentle stretching. The bright arcs will show well; the faintest wisps may need a second season (winter 2027) to push to SNR 25.

---

## Capture Settings

| Parameter | Value |
|-----------|-------|
| Filter | [[Antlia-FQuad]] |
| Exposure | 300s |
| Gain | 100 |
| Temperature | -20degC |
| Binning | 1x1 |
| Dithering | Enabled |

---

## Calibration Checklist

| Frame | Status |
|-------|--------|
| Dark 300s / -20degC | **Needed — acquire before October** |
| Flat (QB) | Per session |
| Dark flat 60ms | Available |
| Bias g100 | Available |

> [!danger] Critical: 300s/-20degC darks missing
> This is the single calibration gap blocking all winter QB campaigns. Acquire 25 frames (~140 min on a cloudy night). See [[Master-Library#Complete Needs Summary]].

---

## SubframeSelector Strategy

| Metric | Threshold |
|--------|-----------|
| FWHM | < 4.5 pixels |
| Eccentricity | < 0.4 |
| Sky background | < 1.3x session median |
| Rejection rate | ~10–15% |

At 68deg altitude with -20degC and long dark nights, expect consistently good subs.

---

## Processing Plan

1. **WBPP** — calibrate all 3 months together, drizzle 2x
2. **SubframeSelector** — reject across the full dataset
3. **ImageIntegration** — winsorized sigma clipping
4. **Processing** — [[QuadBand-OSC-Workflow]], but with extra care:
   - Gentle DBE for gradients
   - Conservative noise reduction (preserve faint filaments)
   - Multiple stretch passes — aggressive for bright arcs, gentle for faint structure
   - Consider StarXT + starless processing to maximize filament visibility

> [!tip] Intermediate stacks
> Stack October data alone as a progress check. If filaments are not detectable at ~8h, verify calibration and sky conditions before investing more nights.

---

## Session Log

| Date | Subs taken | Subs accepted | Integration | Conditions | Notes |
|------|-----------|---------------|-------------|------------|-------|
| | | | | | |

**Running total:** 0h / 30h goal
