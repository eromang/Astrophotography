---
title: "ZWO EAF"
type: equipment
category: accessory
brand: "ZWO"
model: "EAF 5V"
status: active
tags:
  - equipment/accessory
---

# ZWO EAF (Electronic Auto Focuser)

Motorized electronic focuser attached to the [[RedCat-51]] helical focuser. Enables automated focus routines via [[ASIAIR]] to maintain sharp focus throughout imaging sessions as temperature changes.

- [ZWO product page](https://astronomy-imaging-camera.com/product/eaf-5v)
- [EAF compatibility list](https://www.yuque.com/zwopkb/hardware/eaf-support-list#849ff4f3e9eb4f0207b251a91129ff7a)
- [ASIAIR focus documentation](https://www.yuque.com/zwopkb/asiair/focus)
- [Driver & firmware download](https://astronomy-imaging-camera.com/software-drivers)

---

## Specifications

| Specification | Value |
|---------------|-------|
| Motor | Stepper motor, 35mm diameter, 7.5° step angle |
| Reduction ratio | 120:1 |
| Capacity | 5 kg |
| Dimensions | 59 x 52 x 41 mm |
| Weight | 277g |
| Power / Data | USB 2.0 Type-B (power and control over USB) |
| Firmware update | Requires Windows + VS2008 SP1 redistributable |

---

## Configuration

Current settings for the [[RedCat-51]]:

| Parameter | Value | Purpose |
|-----------|-------|---------|
| Fine step | 10 | Small focus adjustments during autofocus routine |
| Coarse step | 30 | Large movements for initial positioning |
| Step limit | 13000 | Maximum travel range — prevents overrun |
| Backlash | 90 | Compensates mechanical play in the gear train |

### Backlash

The EAF gear train has mechanical play (backlash) that causes a dead zone when reversing direction. The backlash setting (90 steps) tells the controller to overshoot by this amount when reversing, then approach from the same direction.

> See EAF manual page 37 for backlash calibration procedure. Manual in `01_Equipment/Manuals/EAF/Manual/`.

---

## How Autofocus Works

The ASIAIR runs an autofocus routine that:

1. **Moves the focuser** through a range of positions (coarse steps)
2. **Captures a short exposure** at each position
3. **Measures star FWHM** at each position
4. **Plots a V-curve** — FWHM decreases toward focus, then increases past it
5. **Finds the minimum** — the position with the smallest FWHM is best focus
6. **Moves to the optimal position** (fine steps for precision)

### V-Curve Example

```
FWHM
  │  *                          *
  │    *                      *
  │      *                  *
  │        *              *
  │          *          *
  │            *      *
  │              *  *
  │               *  ← Best focus
  └──────────────────────────── Step position
```

### When to Autofocus

| Trigger | Reason |
|---------|--------|
| Start of session | Initial focus after setup |
| Temperature drop > 1–2°C | Thermal contraction shifts focus |
| Filter change | Different filter thickness changes backfocus |
| Between targets (optional) | Minor thermal drift during long sequences |
| After meridian flip | Flexure may shift focus slightly |

The ASIAIR can be configured to **autofocus automatically** at set intervals or temperature thresholds during a sequence.

---

## Initial Setup (First Time)

The EAF must be calibrated to know the correct focus position for the optical train:

1. **Daytime setup** — align using a distant target (building, tree line) with plenty of light
2. **Find focus manually** — use a Bahtinov mask on a bright object for precise focus
3. **Note the step count** — record the EAF position number at correct focus
4. This becomes the **reference position** for all future autofocus routines

### Zero Position

The EAF tracks position as a step count from the last zero position. After initial calibration:
- The "in focus" position is typically between 3000–10000 steps (varies by setup)
- The ASIAIR stores this position and returns to it at session start
- Temperature compensation adjusts from this baseline

---

## Installation on RedCat 51

The EAF connects to the RedCat 51's helical focuser via a ProAstroGear adapter bracket:

1. **Without EAF** — manual focus with Bahtinov mask, lock helical focuser
2. **Attach ProAstroGear** bracket to the RedCat 51 focus ring
3. **Mount the EAF** motor to the bracket
4. **Connect USB** to [[ASIAIR]]
5. **Rebalance** the mount — the EAF adds 277g to the scope end

> See [[EAF-Workflow]] for the complete session setup procedure including EAF.

---

## Temperature Compensation

As the optical train cools during a session, metal components contract and focus shifts. The EAF compensates:

| Temperature Change | Typical Focus Shift | EAF Response |
|-------------------|--------------------|----|
| -1°C | ~5–15 steps | Minor — within autofocus tolerance |
| -3°C | ~15–45 steps | Noticeable — autofocus recommended |
| -5°C | ~25–75 steps | Significant — autofocus required |

The exact steps-per-degree depends on the telescope's thermal characteristics. The RedCat 51's aluminum tube contracts with cooling, requiring inward focus adjustment.

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Autofocus fails — no V-curve | Step range too small | Increase coarse step or total range |
| Autofocus finds wrong minimum | Backlash too high | Recalibrate backlash value |
| Focus shifts between subs | Temperature drift | Enable periodic autofocus or temp trigger |
| EAF doesn't respond | USB connection | Check cable, try different USB port on ASIAIR |
| Stars donut-shaped after autofocus | Overshot focus | Reduce fine step size, verify V-curve minimum |
| Inconsistent focus position | Helical focuser slipping | Tighten the ProAstroGear coupling |

---

## Resources

- [ZWO EAF product page](https://astronomy-imaging-camera.com/product/eaf-5v)
- [ASIAIR focus guide](https://www.yuque.com/zwopkb/asiair/focus)
- [EAF manual V2.4 (PDF)](01_Equipment/Manuals/EAF/Manual/EAF_Manual_EN_V2.4.pdf)
- [EAF manual V2.7 (PDF)](01_Equipment/Manuals/EAF/Manual/EAF_Manual_EN_V2.7.pdf)
