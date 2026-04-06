---
title: "Jackery Explorer 500 Portable Power Station"
type: equipment
category: accessory
brand: "Jackery"
model: "Explorer 500 (518Wh)"
status: active
purchase_date: 2024-07-21
purchase_price: "334.28 €"
purchase_store: "Amazon.de"
purchase_url: "https://www.amazon.de"
created: 2026-04-01
tags:
  - equipment/accessory
---

# Jackery Explorer 500 Portable Power Station

Portable power station providing AC and DC power for field astrophotography sessions. Powers the [[iOptron-CEM26]], [[ASIAIR]], and [[ASI2600MCPro]] away from mains electricity.

---

## Specifications

| Specification | Value |
|---------------|-------|
| Type | Portable power station |
| Battery type | Lithium-ion |
| Capacity (nominal) | 518 Wh |
| AC output | 230V / 500W (peak 1000W) |
| Waveform | Pure sine wave |
| DC output | 12V car port + USB-A ports |

---

## Effective Capacity (real-world)

The 518 Wh nominal value is reduced by several real-world factors:

| Loss factor | Reduction | Reason |
|-------------|-----------|--------|
| Inverter efficiency (AC out) | -10% to -15% | DC→AC→DC conversion when using AC adapters |
| Cold temperature derating | -10% to -25% | Lithium-ion loses capacity below 10°C |
| Don't deep-discharge below 10% | -10% | Preserves cycle life |
| Aging (after ~2 years) | -5% to -10% | Bought 2024-07-21 |

| Realistic scenario | Effective Wh |
|--------------------|--------------|
| Summer DC-only (12V car port, best case) | ~450 Wh |
| Summer AC-powered (typical) | ~390 Wh |
| Winter AC-powered (worst case) | ~310 Wh |

---

## Compatibility with Imaging Rig

### Per-Device Power Draw

| Device | Voltage | Current | Power | Notes |
|--------|---------|---------|-------|-------|
| [[iOptron-CEM26]] tracking | 12V | 0.5 A | **6 W** | Sustained sidereal tracking |
| [[iOptron-CEM26]] slewing | 12V | 0.8 A | **9.6 W** | Brief peaks during GoTo / meridian flip |
| [[ASI2600MCPro]] cooling -10°C (summer) | 12V | ~1.0–1.5 A | **12–18 W** | Scales with delta-T |
| [[ASI2600MCPro]] cooling -20°C (winter) | 12V | ~1.5–2.5 A | **18–30 W** | Larger delta = more power |
| [[ASI2600MCPro]] sensor + readout only | 12V | ~0.3 A | **~4 W** | Without TEC active |
| [[ASIAIR]] | 12V | ~0.4 A | **~5 W** | Idle + WiFi |
| [[ZWO-EAF]] | USB 5V | ~0.1 A peak | **~0.5 W avg** | Only active during focus runs |
| [[ASI385MC]] guide camera | USB 5V | ~0.4 A | **~2 W** | Continuous during guiding |
| [[COOWOO-Dew-Heater]] Low | USB 5V | ~0.5 A | **~3.5 W** | Documented 7W max |
| [[COOWOO-Dew-Heater]] Medium | USB 5V | ~1.0 A | **~5 W** | |
| [[COOWOO-Dew-Heater]] High | USB 5V | 1.4 A | **7 W** | Max output |

> [!info] Single 12V load through ASIAIR
> The [[ASIAIR]] distributes 12V to the mount via its 4x DC outputs and provides USB 5V to the camera, EAF, guide camera, and dew heater. The Jackery only sees **one main 12V load** (the ASIAIR feeding everything else).

### Total System Draw Scenarios

| Scenario | CEM26 | Camera | ASIAIR | EAF | Guide | Dew | **Total** |
|----------|-------|--------|--------|-----|-------|-----|-----------|
| Summer, dry, no dew heater | 6 | 15 | 5 | 0.5 | 2 | 0 | **~28.5 W** |
| Summer, humid, dew Low | 6 | 15 | 5 | 0.5 | 2 | 3.5 | **~32 W** |
| Summer, very humid, dew Medium | 6 | 15 | 5 | 0.5 | 2 | 5 | **~33.5 W** |
| Winter, dew off | 6 | 24 | 5 | 0.5 | 2 | 0 | **~37.5 W** |
| Winter, frost, dew High | 6 | 28 | 5 | 0.5 | 2 | 7 | **~48.5 W** |

### Session Duration vs Battery

| Scenario | Draw | Effective Wh | **Hours** |
|----------|------|--------------|-----------|
| Summer dry, DC-only (best) | 28.5 W | 450 | **~15.8 h** |
| Summer dry, AC mode | 28.5 W | 390 | **~13.7 h** |
| Summer humid | 33 W | 390 | **~11.8 h** |
| Winter, no dew | 37.5 W | 310 | **~8.3 h** |
| Winter frost (worst case) | 48.5 W | 310 | **~6.4 h** |

---

## Verdict by Season

| Season | Max dark hours | Power-limited hours | Verdict |
|--------|---------------|---------------------|---------|
| **Summer (Jun)** | ~4 h | 11.8 h | ✓ **3x margin** — totally fine |
| **Summer (Jul)** | ~5 h | 11.8 h | ✓ **2.4x margin** |
| **Summer (Aug)** | ~7 h | 11.8 h | ✓ **1.7x margin** — comfortable |
| **Autumn (Sep)** | ~9 h | ~10 h | ⚠️ **tight** — only 10% margin |
| **Autumn (Oct)** | ~10 h | ~9 h | ❌ **insufficient by ~1 h** |
| **Winter (Nov)** | ~12 h | ~8 h | ❌ **insufficient by 4 h** |
| **Winter (Dec)** | ~13 h | ~6.4 h (frost) | ❌ **half a night max** |

> [!success] Best fit: Summer M16/M17 campaign
> The Jackery 500 perfectly covers the [[M16-Campaign-2026|M16 Summer Campaign]] window (June–August) with 1.7–3x safety margin. After August, dark hours exceed battery capacity unless an upgrade is made.

> [!warning] Insufficient for autumn/winter portable sessions
> From October onwards, dark hours exceed what the Jackery 500 can supply. **Use mains power on the balcony for autumn/winter campaigns** ([[Cygnus-Campaign-2026]], [[Simeis147-Campaign-2026]], [[Winter-Emission-Campaign-2026]]).

---

## Optimization Tips

To stretch the battery further on portable sessions:

1. **Use the 12V car port directly** — bypass the inverter, save ~10% (mount and ASIAIR both run on 12V)
2. **Skip the dew heater** when humidity < 70% — saves ~5 W
3. **Pre-cool the camera on mains** before transport, then plug into Jackery only when arriving on site
4. **Reduce cooling delta** — summer at -5°C instead of -10°C saves ~5 W
5. **Top up the battery** between consecutive nights using car charger or solar panel

---

## Upgrade Options (if needed)

| Option | Capacity | Adds | Cost (approx) | Use case |
|--------|----------|------|---------------|----------|
| Add Jackery Explorer 240 | +240 Wh | ~3.5 kg | ~€200 | Extends to ~12 h winter sessions |
| Upgrade to Jackery Explorer 1000 | 1002 Wh | replaces current | ~€800 | Any-season full nights |
| Solar panel SolarSaga 60W | regen | ~3 kg | ~€200 | Multi-night camping (4–6h sun = full recharge) |
| Solar panel SolarSaga 100W | regen | ~5 kg | ~€350 | Faster recharge for longer trips |

---

## Resources

- [Jackery Explorer 500](https://www.jackery.com)
