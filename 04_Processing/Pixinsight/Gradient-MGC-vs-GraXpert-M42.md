---
title: "Gradient Removal — MGC+DR2 vs GraXpert (M42 field study)"
type: processing-workflow
software: "PixInsight"
tags:
  - processing/pixinsight
---

# Gradient Removal — MGC+DR2 vs GraXpert (M42 field study)

Controlled A/B/sweep run during the [[M42-Orion]] HDR reprocess (2026-06-23) to decide the gradient step, using the new **MARS DR2** database. Scored objectively with `scripts/gradient_check.py` ([[Gradient-Check]]). **Result: GraXpert wins for this field**, across the *entire* MGC parameter space — and the reason is declination-dependent, so the rule generalises.

> **TL;DR:** On **near-equatorial fields (Dec ≲ 0°)** MGC+DR2's reference fit is ~2× less flat than GraXpert no matter how you tune it — use **GraXpert**. Reserve **MGC+DR2 for high-northern, deep-coverage fields**. DR2 *does* now cover Dec −5° (DR1 didn't), so re-test previously-uncovered fields.

---

## Setup

- **Image:** M42 drizzle-2× FQuad master (100×160 s, Dec −5°23′), linear, plate-solved.
- **GraXpert:** Subtraction, Smoothing **0.8** (high — correct for a frame-filling nebula).
- **MGC:** DR2 + u01, bands **Ha / O-III / O-III**, SPFC applied first. Swept gradient scale, structure separation, scale factors.
- **Metric:** `gradient_check.py` — `rel_spread` (background flatness, lower=flatter), `wing` (retained outer nebulosity), `imprint` (does the gradient model contain the object).

## Results

| Method | rel_spread (flatness) | wing | model imprint | model contrast |
|---|---|---|---|---|
| **GraXpert @ 0.8** | **0.0184** ✅ | 0.00105 | 0.003 | 0.130 |
| MGC gs1024 | 0.0401 | 0.00120 ⚠️ | **−0.176** | 0.363 |
| MGC gs2048 | 0.0396 *(MGC best)* | 0.00108 | −0.017 | 0.131 |
| MGC gs4096 | 0.0452 | 0.00107 | −0.007 | 0.098 |
| MGC gs2048 + ss2 | 0.0390 | 0.00108 | −0.026 | 0.134 |
| MGC gs2048 + sf 0.5/1.8/1.8 | 0.0534 | 0.00110 | −0.034 | 0.161 |

## What the data proves

1. **The gs1024 "core hole" is an artifact.** At gradient scale 1024, MGC's structure-separation carved a dark hole at M42's core (model imprint **−0.176**, contrast 0.363 — visible as a black blob in the model). It **closes by gs2048** (imprint → −0.017, contrast → 0.131, smooth model). Lesson: *for a bright frame-filling object, don't use a low gradient scale.*
2. **The hole faked a wing advantage.** gs1024 showed +14 % "wing signal", but it was the hole boosting the annulus. Once the hole closes (gs2048+), wing collapses to **≈ GraXpert's** — MGC preserves the *same* real nebula, not more.
3. **No parameter closes the flatness gap.** Across gradient scale (1024→4096), structure separation (1→2), and scale factors (0.3/1.5 → 0.5/1.8), MGC is **pinned at ~0.039–0.045** — always ~2× less flat than GraXpert. Over-smoothing (gs4096) and over-correcting (sf 0.5/1.8) both make it *worse*. The MGC optimum is **gs2048, ss1, sf 0.3/1.5/1.5** (≈0.039) — still a 2× loss.
4. **It's a reference-fit ceiling, not a tuning miss.** The MGC model is *as smooth as GraXpert's* (contrast 0.131≈0.130) yet leaves 2× the residual → its reference model doesn't *fit* this field's gradient as well as GraXpert's AI. Most likely because **M42 at Dec −5° is at the southern edge of DR2's coverage**, where reference depth is thinnest.

## The rule (generalised)

| Field declination | Gradient tool |
|---|---|
| **High-northern, deep DR2 coverage** | **MGC + DR2** (reference-based; best on extended objects *with* good coverage) |
| **Near-equatorial / low (Dec ≲ 0°)** | **GraXpert** (high smoothing for frame-filling nebulae) — MGC's reference fit degrades at the coverage edge |
| **No DR2 coverage** (MGC errors "No reference data") | **GraXpert** |

> **MGC tuning, when you do use it:** gradient scale **2048** (not the 512–1024 the old workflow suggested — that holes bright objects), structure separation **1**, scale factors **Ha 0.3 / O-III 1.5**. Always confirm the model has no object imprint via `gradient_check.py --model`.

## Decision for M42 (2026 reprocess)

**GraXpert @ 0.8** is the gradient step. See [[M42-Orion]].

## Related
- [[MGC-Reference]] · [[Gradient-Check]] · [[QuadBand-OSC-Workflow#2.2 Gradient Removal]]
- [[Master-Library#Additional SSD Resources]] — MARS DR2 path
