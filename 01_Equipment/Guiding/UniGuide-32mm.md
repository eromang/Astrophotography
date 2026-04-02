---
title: "UniGuide 32mm"
type: equipment
category: guiding
brand: "William Optics"
model: "UniGuide 32mm"
status: active
purchase_date: 2022-09-16
purchase_price: "146.02 €"
purchase_store: "Astroshop"
purchase_url: "https://www.astroshop.eu"
tags:
  - equipment/guiding
---

# William Optics UniGuide 32mm

Compact guide scope paired with the [[ASI385MC]] for autoguiding during deep sky imaging sessions.

- [William Optics product page](https://williamoptics.com/products/telescope/guider/all-new-slide-base-uniguide-32mm-scope)
- [AstroShop listing](https://www.astroshop.eu/guidescopes/william-optics-guidescope-uniguide-32mm-red/p,69213)

---

## Specifications

| Specification | Value |
|---------------|-------|
| Lens diameter | 32mm |
| Focal length | 120mm |
| Focal ratio | f/3.75 |
| Eyepiece connection | 1.25" |
| Camera connection | M42 x 0.75 |
| Mounting | Prism rail (slide base) |
| Weight | 240g |
| Length | 147mm |
| Color | Red |

---

## Guiding Performance

### With [[ASI385MC]] (3.75 µm pixels)

| Parameter | Value |
|-----------|-------|
| Image scale | 6.4"/pixel |
| Field of view | ~3.4° x 1.9° |
| Limiting magnitude | ~10–11 mag (typical, gain 200–300, 2s exposure) |
| Guide star density | 5–20 usable stars in most fields |

### Scale Relationship to Imaging Rig

| | Guide scope | Imaging scope |
|--|------------|---------------|
| Focal length | 120mm | 250mm ([[RedCat-51]]) |
| Image scale | 6.4"/pixel | 3.1"/pixel |
| Ratio | 2.1x coarser | — |

The guide scope resolves at roughly half the imaging scale. This means a 1-pixel guide error (6.4") translates to ~2 pixels on the imaging camera — within acceptable limits when guide RMS is < 1".

---

## Characteristics

### Strengths

- **Fast f/3.75** — bright guide stars even in sparse fields, enabling short 1–2s guide exposures
- **Wide 3.4° FOV** — virtually guarantees multiple guide stars in any pointing direction
- **Lightweight** — 240g adds minimal payload to the [[iOptron-CEM26]]
- **Compact** — 147mm length; doesn't extend far from the imaging rig
- **Prism rail** — slide base allows quick attachment and adjustment without tools
- **M42 connection** — direct thread to [[ASI385MC]] without adapters

### Limitations

- **No focus adjustment** — fixed focus (parfocal by design); if stars are out of focus, adjust by sliding the camera in the M42 adapter
- **32mm aperture** — limited light gathering; may struggle with very faint guide stars in sparse fields at high galactic latitude
- **Flexure risk** — as with any guide scope, differential flexure between guide and imaging scope can cause star trailing. Check for flexure periodically.

---

## Flexure Management

Differential flexure between the guide scope and imaging telescope is the main risk with a separate guide scope setup (vs off-axis guider).

### Symptoms
- Guide graph looks good but imaging stars are elongated
- Elongation worsens toward horizon (gravity-induced flexure)
- Stars trail in a consistent direction unrelated to RA/DEC

### Prevention
- **Tighten all connections** — prism rail clamp, guide camera thread, dovetail
- **Avoid excessive overhang** — mount guide scope close to the imaging scope center of gravity
- **Check periodically** — compare guide RMS to actual star elongation in subs
- **Short sub-exposures** — 160–220s exposures (as used in current sessions) limit flexure accumulation

At 3.1"/pixel with 160–300s exposures on the [[RedCat-51]], flexure is unlikely to be visible unless connections are loose.

---

## Mounting

The UniGuide attaches to the imaging telescope via its prism rail and a guide scope ring or shoe:

1. Slide the UniGuide into the prism rail shoe on the [[RedCat-51]] dovetail
2. Tighten the locking screw
3. Thread the [[ASI385MC]] into the M42 connection
4. Roughly align the guide scope with the imaging scope (doesn't need to be precise — the wide FOV compensates)

---

## Resources

- [William Optics UniGuide 32mm](https://williamoptics.com/products/telescope/guider/all-new-slide-base-uniguide-32mm-scope)
