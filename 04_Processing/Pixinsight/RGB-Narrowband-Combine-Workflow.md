---
title: "PixInsight RGB + Narrowband Combine Workflow (HORGB)"
type: processing-workflow
software: "PixInsight"
tags:
  - processing/pixinsight
---

# RGB + Narrowband Combine (HORGB) — OSC

Combine **two OSC data sets of the same target** — a broadband **RGB** stack ([[Optolong-LPro]]) and a **dual-band Ha-OIII** stack ([[Antlia-FQuad]]) — into one image with **natural-colour RGB stars** plus **narrowband nebula detail**.

> **When to use:** you have (or plan) both an L-Pro night and a Quad Band night on the same object. The RGB data supplies true star colours and continuum; the dual-band data boosts Ha/OIII nebulosity. Prime candidate: [[NGC7000-North-America]] (existing L-Pro data + planned QB), Rosette, Veil.
>
> **For a single data set:** use [[RGB-Workflow]] (L-Pro only) or [[QuadBand-OSC-Workflow]] (Quad Band only) instead.

**The key idea:** keep the **RGB stars** (the dual-band stars are *discarded*), and use the narrowband **only for the nebula signal**, blended via **CombineRGBAndNarrowband**. SPCC runs on the RGB branch only (star-full, linear) — consistent with the SPCC-first order in the other workflows.

## External reference

astro-photographie.fr **OSC5** — "Processing of OSC RGB and dualband Ha-OIII images" (`astro-photographie.fr/traitement_pixinsight.html`, diagram v2.2E). This note adapts that dual-branch pipeline to the vault's conventions. All tools are already installed (CombineRGBAndNarrowband, DBXtract, Screen Stars — see [[Modules.md]]).

---

## Phase 1: Acquisition & Stacking (two stacks)

Produce **two separate masters** of the same target:

1. **RGB master** — L-Pro, stacked per [[RGB-Workflow#Phase 1: Evaluation & Stacking]].
2. **Dual-band master** — Quad Band, stacked per [[QuadBand-OSC-Workflow#Phase 1: Evaluation & Stacking]].

> 🔴 **Critical — co-registration.** The two masters were shot on different nights (different framing/rotation), so they must be registered to a **common reference frame** before they can be combined pixel-aligned:
> - Pick one master as reference (usually the RGB).
> - Run **StarAlignment** with the other master as target → registered copy.
> - Verify both are plate-solved and identical in dimensions/orientation. **A misalignment of even a few pixels ruins the combine** (coloured fringes on stars, doubled nebula edges).
> - Same camera/scope/pixel scale, so no rescaling — only register/rotate.

---

## Phase 2: RGB Branch (linear)

Process the RGB master through the standard broadband linear steps — see [[RGB-Workflow]] for all parameters:

1. **Gradient Correction** (or GraXpert / SPFC+MGC) + BackgroundNeutralization
2. **BlurXTerminator — Correct Only** ([[RGB-Workflow#2.4 Star Correction]])
3. **ImageSolver** (plate solve)
4. **SPCC** — star-full, L-Pro filters, G2V reference ([[RGB-Workflow#2.6 Color Calibration]])
5. **BlurXTerminator — Sharpen** ([[RGB-Workflow#2.8 Star Sharpening]])
6. **StarXTerminator** — generate star image. **Keep both outputs:**
   - **Stars RGB** → set aside for Phase 6 (these become the final stars)
   - **RGB starless** → continues below
7. **NoiseXTerminator** on the RGB starless ([[RGB-Workflow#2.10 Noise Reduction (Linear, on starless)]])

→ Output: **RGB starless (linear)** + **Stars RGB**.

---

## Phase 3: Dual-band Branch (linear)

Process the Quad Band master, then split into Ha and OIII:

1. **Gradient Correction** + BackgroundNeutralization
2. **BlurXTerminator** (Correct Only → Sharpen as usual). No SPCC on this branch — it carries only narrowband nebula signal.
3. **StarXTerminator** — **discard the narrowband star image** (stars come from the RGB branch). Keep the **HOO starless**.
4. **NoiseXTerminator** on the HOO starless.
5. **DBXtract** (DualBand Extract, Ha + OIII) on the HOO starless → **Extract Ha** + **Extract OIII** (two clean mono images). See [[QuadBand-OSC-Workflow#3.1 Channel Extraction (Ha / OIII)]].

→ Output: **Ha (linear)** + **OIII (linear)**.

---

## Phase 4: Stretch (non-linear) — three channels independently

Stretch the **RGB starless**, **Ha**, and **OIII** images **separately** so each can be balanced before the combine:

- **Multiscale Adaptive Stretch** on each (recommended — the PI 2026 method; see [[Multiscale Adaptive Stretch – Das bietet die neue Stretch-Methode mit PixInsight 2026]]).
- **GHS** is preferred for fine-tuning individual channels (per the OSC5 reference) if a channel needs a different transfer curve.
- Aim for comparable brightness/contrast across the three so the combine is predictable.

→ Output: **RGB non-linear**, **Ha non-linear**, **OIII non-linear**.

---

## Phase 5: Combination & Boost (non-linear)

1. **CombineRGBAndNarrowband** (installed script) — blend the broadband RGB with the Ha and OIII narrowband:
   - RGB = base (star colour + continuum)
   - **Ha** injected into the **red** nebula signal
   - **OIII** injected into **green/blue**
   - Tune the per-channel blend / lightness-vs-chrominance controls on a **preview**; push narrowband only as far as the nebula needs without overwhelming the broadband colour.
   - → **Mix (RGB, Ha, OIII)**
2. **NoiseXTerminator** — light pass on the combined image (it now sees the final colour).
3. **Boost dynamic & colours** — **CurvesTransformation** (saturation + contrast); see [[CurvesTransformation-Reference]]. → **HORGB Boost**.

---

## Phase 6: Stars & Final

1. **Star Stretch** the **Stars RGB** image (ArcsinhStretch, protect highlights) → natural-colour stars.
2. **Screen Stars** (CosmicPhotons, mode *Star replacement*) to recombine **HORGB Boost** + **Stars RGB** — screen blend. Equivalent PixelMath: `~(~starless * ~stars)`.
3. Final adjustments — CurvesTransformation / [[LHE-Reference|LocalHistogramEqualization]] as needed.
4. **ICCProfileTransformation** → sRGB for export.

→ **Final image** — RGB stars + narrowband-boosted nebula.

---

## Critical notes

- 🔴 **Co-register the two masters first** (Phase 1) — the #1 failure mode.
- 🟢 **Stars come from RGB only** — discard the dual-band star image; this is the whole point (natural star colour).
- 🟢 **SPCC on the RGB branch only**, star-full, before star removal — never on the narrowband.
- The three channels are stretched **independently** before combining — balance them first.
- Everything is already installed; this is a documentation/workflow addition, no new modules.

## Applicable targets

Same-target L-Pro **and** Quad Band data:

- [[NGC7000-North-America]] — L-Pro data exists; add Quad Band for Ha boost
- [[NGC2244-Rosette]] — strong Ha + OIII (the OSC5 reference example)
- NGC 6960/6992 Veil — strong OIII + Ha
- Any emission nebula where you want true star colour **and** narrowband nebula detail

> For galaxies/clusters (no narrowband), use [[RGB-Workflow]]. For a pure narrowband look, use [[QuadBand-OSC-Workflow]].
