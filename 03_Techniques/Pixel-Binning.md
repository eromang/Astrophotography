---
title: "Pixel Binning"
type: technique
tags:
  - technique
---

# Pixel Binning

Pixel binning combines adjacent pixels into a single larger pixel, trading resolution for sensitivity and speed.

> [Reference: Everything you need to know about pixel binning](https://astronomy-imaging-camera.com/tutorials/everything-you-need-to-know-about-astrophotography-pixel-binning-the-fundamentals.html)

---

## How It Works

In 2x2 binning, a group of 4 pixels (2x2) is read as a single pixel. The charge from all 4 pixels is combined before readout.

```
1x1 (no binning)     2x2 binning          3x3 binning
┌──┬──┬──┬──┐        ┌─────┬─────┐        ┌────────┐
│  │  │  │  │        │     │     │        │        │
├──┼──┼──┼──┤        │ 4px │ 4px │        │  9px   │
│  │  │  │  │        │     │     │        │        │
├──┼──┼──┼──┤        ├─────┼─────┤        └────────┘
│  │  │  │  │        │     │     │
├──┼──┼──┼──┤        │ 4px │ 4px │
│  │  │  │  │        │     │     │
└──┴──┴──┴──┘        └─────┴─────┘
16 pixels             4 superpixels        1 superpixel
```

---

## Hardware vs Software Binning

| Type | How | Read noise | Benefit |
|------|-----|------------|---------|
| **Hardware binning** | Charge combined on-chip before readout | Read noise applied **once** per superpixel | True sensitivity gain — more signal per read noise event |
| **Software binning** | Pixels read individually, combined in software | Read noise applied **per pixel**, then averaged | No sensitivity gain — just downscaling |

**The [[ASI2600MCPro]] (CMOS) only supports software binning.** True hardware binning is a CCD feature. On CMOS sensors, "binning" in capture software is equivalent to capturing at 1x1 and downscaling afterward.

---

## Effect on Imaging Parameters

For the [[RedCat-51]] (250mm) + [[ASI2600MCPro]] (3.76 µm pixels):

| Binning | Effective pixel size | Image scale | Resolution | File size |
|---------|---------------------|-------------|------------|-----------|
| 1x1 | 3.76 µm | 3.1"/pixel | 6248 x 4176 | Full |
| 2x2 | 7.52 µm | 6.2"/pixel | 3124 x 2088 | 1/4 |
| 3x3 | 11.28 µm | 9.3"/pixel | 2083 x 1392 | 1/9 |

---

## When to Use Binning

### Binning is useful when:

- **Oversampled** — your image scale is much finer than seeing allows. If seeing is 3" and you're at 3.1"/pixel, you're well-matched and don't need binning. But at 0.64"/pixel ([[Celestron-NexStar-90SLT]] + [[Nikon-D5300]]), you're heavily oversampled and 2x2 binning would help.
- **Guiding camera** — the [[ASI385MC]] often benefits from 2x2 binning for brighter guide stars and faster exposure response.
- **Quick preview** — bin 2x2 for faster download and quick framing checks.
- **Narrowband with poor seeing** — when seeing is 4"+ and resolution is wasted, binning reduces file size and processing time without losing real detail.

### Binning is NOT useful when:

- **Already well-sampled** — at 3.1"/pixel with the RedCat 51, you're near the optimal range for typical seeing (2–4"). Binning would throw away real resolution.
- **Drizzle planned** — drizzle (used in both workflows at factor 2) reconstructs sub-pixel detail. Binning before capture removes the dithered sub-pixel information drizzle needs.
- **CMOS sensor** — since the ASI2600MC Pro only does software binning, there's no SNR advantage. You get the same result by capturing at 1x1 and downscaling in post if needed.

---

## Recommendation for Current Setup

| Scenario | Binning | Reason |
|----------|---------|--------|
| Deep sky with RedCat 51 + ASI2600MC Pro | **1x1** | Well-sampled at 3.1"/pixel, drizzle 2x in WBPP, CMOS = no hardware binning benefit |
| Guiding with ASI385MC | **2x2** | Brighter guide stars, faster response |
| Planetary with NexStar 90SLT + D5300 | **N/A** | DSLR does not support binning; use ROI crop instead |
| Quick framing check | **2x2** | Faster download, acceptable for composition verification |

---

## Binning vs Drizzle

Binning and drizzle are opposite operations:

| | Binning | Drizzle |
|--|---------|---------|
| Direction | Combines pixels → lower resolution | Reconstructs sub-pixel detail → higher resolution |
| When | During capture or post | During stacking (WBPP) |
| Requires | Nothing | Dithering between exposures |
| Effect on SNR | Improves (hardware only) or neutral (software) | Slight noise increase, significant detail gain |

Using both together is counterproductive — don't bin during capture if you plan to drizzle during stacking.
