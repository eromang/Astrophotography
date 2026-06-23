---
title: "PixInsight HDR Workflow"
type: processing-workflow
software: "PixInsight"
tags:
  - processing/pixinsight
---

# HDR Processing (MAS + HDRMT)

Workflow for high dynamic range targets — objects with a **bright core surrounded by faint extended structure**. This replaces the **stretch phase** of either parent workflow; it is **generic** — the *method* is identical for nebulae and galaxies, only the **parameters differ by target class** (see [Parameter Reference](#parameter-reference)).

> **Not a standalone workflow.** Finish the *linear* phase of your parent workflow first ([[RGB-Workflow]] for galaxies/L-Pro, [[QuadBand-OSC-Workflow]] for emission nebulae/FQuad), do this for the stretch + HDR recovery, then return to the parent for star reintegration and export.

> **Updated 2026-06 to MAS-first**, corrected against [[Multiscale Adaptive Stretch – Das bietet die neue Stretch-Methode mit PixInsight 2026]] (M. Käßler, 2026-01) + Light Vortex / ChaoticNebula. Key corrections: **DRC is *low* for bright nebulae** (the core is HDRMT's job, not DRC's), and **HDRMT "Number of layers" is the critical control** (there is no HDRMT "intensity").

---

## When to Use

A standard stretch either clips the bright core or leaves the faint periphery invisible (brightness ratio ≥ 100:1 core-to-edge).

| Target class | Examples | Parent workflow |
|---|---|---|
| Bright-core **emission nebula** | [[M42-Orion]], M16, M17 | [[QuadBand-OSC-Workflow]] (FQuad, HOO) |
| **Galaxy** with bright nucleus | [[M31-Andromeda]], M81, M101, M64 | [[RGB-Workflow]] (L-Pro, RGB) |
| **Supernova remnant** | Veil (NGC 6960/6992) | [[QuadBand-OSC-Workflow]] |

> M42 ≠ M31. They differ at **two** levels: the **parent** (emission-nebula narrowband vs galaxy broadband — filter, channel work, SPCC reference) *and* the **HDR parameters** (Szenario B nebula vs A galaxy). This note owns only the second; the parent owns the first.

---

## Entry Point

Enter with a **linear, color-calibrated, starless, noise-reduced** image. ⚠️ **SPCC is mandatory *before* MAS** — MAS intensifies colour, so an un-calibrated image produces the classic green cast / washed-out reds (see [Troubleshooting](#troubleshooting)).

| Coming from | Enter after | (Must already be done) |
|---|---|---|
| [[RGB-Workflow]] | Step 2.10 — NXT on starless | gradient removed, **SPCC**, BXT, stars removed |
| [[QuadBand-OSC-Workflow]] | Phase 3.4 → **3.5 SPCC** (color-balanced HOO) | gradient removed, **SPCC**, BXT, stars removed, HOO reassembled |

MAS lives under **Process → Intensity Transformations → MultiscaleAdaptiveStretch** (added PI 1.9.3 build 1646, Dec 2025; if missing after an update: Process → Modules → Install Modules → **Search**).

---

## Method A: MAS + HDRMT (Recommended)

MAS delinearises with statistical, multiscale analysis — replacing the old 20–30 min GHS+masks+curves grind with a few minutes at ~90–95 % of the quality. HDRMT then physically compresses the bright **nebula/nucleus core** that MAS deliberately leaves bright.

### A.1 — STF: assess the linear image *(display only)*

1. Open **ScreenTransferFunction (STF)**.
2. Click the **nuclear/radioactive icon** (bottom-left) to **AutoStretch in linked mode** (chain-link icon engaged). This is **display-only — the data stays linear.**
3. Confirm: background is clean (no residual gradient), the faint outer structure *and* the bright core are both present. HOO data will look tinted — normal.
4. *(Optional)* click the chain-link to **unlink**, AutoStretch again → reveals per-channel imbalance. Re-**link** before continuing.

> STF only changes the *screen*, never the pixels. It's how you see linear data; MAS reads the real linear values underneath.

### A.2 — Background reference

With the STF stretch applied (so dark sky is visible), drag a small **preview onto an empty dark-sky region** free of nebulosity. MAS uses this region's median to anchor the delinearisation. Without it, the median includes nebula and the result comes out too dark.

### A.3 — MAS delinearisation

Open **MultiscaleAdaptiveStretch** and enable **Real-Time Preview** (drag the preview triangle onto the image, or preview the main view).

Set parameters **by target class** ([Parameter Reference](#parameter-reference)). For a **bright emission nebula (M42)**:

| Parameter | Value | Why |
|---|---|---|
| **Target Background** | **0.15 – 0.20** | higher than a galaxy — lifts the faint outer dust/IFN |
| **Aggressiveness** | **medium-low** | high aggressiveness clips the faint outer nebula and triggers ringing |
| **Dynamic Range Compression (DRC)** | **~0.20 (low)** | DRC protects *stars*; **too-high DRC flattens the nebula core** — leave the core for HDRMT |
| **Contrast Recovery** | **enabled, but watch** | at the Trapezium's hard edges it can cause **dark rings** → if so, **disable** |
| **Color Saturation** | **disabled** | add saturation later; aggressive stretch on bright areas makes colour artifacts |

Tune on the real-time preview, then **Apply to the main view.**

### A.4 — STF: **RESET after the stretch** ⚠️ *(don't skip)*

MAS just applied a **real, permanent stretch** — the data is now **non-linear**. The old linear-era STF would now **double-stretch** the screen (blown-out, panicky-looking).

1. In **ScreenTransferFunction**, click **Reset** (the ⟳ / reset button) to return STF to identity.
2. The screen now shows the **true** stretched data. Re-AutoStretch *only* if you want a gentle display tweak — but never assess the stretch through a stale linear STF.

> This is the single most common STF mistake: judging a just-stretched image through the old auto-stretch and thinking the tool blew it out.

### A.5 — HDRMT (the core compression)

On the **non-linear** image, open **HDRMultiscaleTransform**:

| Parameter | Value | Notes |
|---|---|---|
| **Number of layers** | **6–7** (try both) | **THE critical control** — ±1 layer changes the result dramatically. 7 keeps the Trapezium stars visible without a flat core |
| **Lightness mask** | **Enabled** | restricts the effect to the bright core; shadows untouched |
| **Deringing** | enable **small** values *if* dark rings appear around stars; or switch **Median transform** on (avoids ringing, slower) | |
| Iterations / To lightness | default | |

**Procedure:** create a preview over the core → apply at 6 and 7 layers on separate previews → pick the one that reveals core structure without flattening contrast → apply to the main view. *(Advanced: blend several runs at layers 5–9 for the best core.)*

### A.6 — Colour enhancement

- **CurvesTransformation (Saturation)** — steep rise on the left (boost the low-saturation highlights HDRMT just revealed), flat on the right (preserve already-saturated nebula).
- **BackgroundNeutralization** if a cast remains.
- **STF check (data is non-linear → STF at identity):** link + AutoStretch only to *verify* neutrality, then reset.

### A.7 — Return to parent

| Return to | Resume at |
|---|---|
| [[RGB-Workflow]] | Phase 4 — Star Processing & Reintegration |
| [[QuadBand-OSC-Workflow]] | Phase 5 — Star Processing |

---

## Method B: GHS + HDRMT (Alternative)

Use when you want manual midtone control, or MAS misbehaves on an unusual histogram.

1. **STF AutoStretch (linked)** to view the linear image (A.1).
2. **GeneralizedHyperbolicStretch** — Symmetry Point near the histogram peak; apply **several small** stretches, not one aggressive pass. No built-in DR compression, so the core *will* clip more than MAS.
3. **STF Reset** after stretching (A.4).
4. **HDRMT** as A.5 — but because GHS pre-compressed less, you may need **+1 layer** or a second pass.
5. Colour (A.6) → return to parent (A.7).

> **Why MAS is preferred:** MAS compresses dynamic range *during* the stretch, so HDRMT has more highlight data to work with. GHS stretches first and can clip the core before HDRMT sees it.

---

## Parameter Reference

Starting points by target class. The **bright-emission-nebula** and **galaxy** rows are sourced; SNR / star-field are extrapolated — refine and update.

### MAS (by class)

| Target class | Examples | Target Background | Aggressiveness | **DRC** | Contrast Recovery | Saturation |
|---|---|---|---|---|---|---|
| **Bright emission nebula** | M42, M16, M17 | **0.15–0.20** | medium-low | **0.20** (core → HDRMT) | check rings → disable if artifacts | **disabled** |
| **Galaxy (bright nucleus)** | M31, M81, M101, M64 | **0.12–0.14** | standard | **0.5–1.0** | enabled | enabled |
| Supernova remnant *(extrapolated)* | Veil | ~0.13–0.15 | standard | ~0.5 (moderate) | enabled | enabled |
| Dense star field *(extrapolated)* | Milky Way | 0.14–0.16 | high | **2.0+** (max — shrinks stars) | enabled | enabled |

> Default starting point (any object): Target Background **0.12**, DRC **0.5**, Contrast Recovery on, Saturation on. Then shift per the row above.

### HDRMT (by class)

| Target class | **Number of layers** | Lightness mask | Deringing |
|---|---|---|---|
| Bright emission nebula (M42) | **6–7** | enabled | small-scale, or Median transform, *if* star rings |
| Galaxy nucleus (M31) *(extrapolated)* | 5–6 (nucleus is small) | enabled | as needed |
| Supernova remnant *(extrapolated)* | 6 | enabled | as needed |

> HDRMT's effect is governed by **Number of layers + Iterations + (Median/Deringing)** — there is **no "intensity" slider**. More layers = stronger core compression over a larger scale.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| **Green cast** after MAS | colour not calibrated before the stretch (OSC RGGB green dominance) — MAS amplifies it | **SPCC *before* MAS**; if it persists, **SCNR** *after* the stretch |
| **Channel clipping** (red lost, OIII-dominant data) | Target Background too low (< 0.10) | raise Target Background to **≥ 0.12** |
| **Dark rings around stars** | Contrast Recovery / over-aggressive multiscale (Gibbs-like overshoot) | lower **Aggressiveness**, raise **DRC**, or **disable Contrast Recovery** |
| **Flat / grey core** | DRC too high (flattened the core) **or** wrong HDRMT layer count | lower DRC; re-do HDRMT at a different layer count |
| **Screen looks blown out right after MAS** | stale linear STF double-stretching | **Reset STF** (A.4) — the data is fine |

---

## Exit Point

After stretch + core recovery + colour, return to the parent workflow:

| Return to | Resume at |
|---|---|
| [[RGB-Workflow]] | Phase 4 — Star Processing & Reintegration |
| [[QuadBand-OSC-Workflow]] | Phase 5 — Star Processing |

---

## Future Addition

**Multi-exposure HDR composition** — combine short exposures (e.g. 30 s for the M42 Trapezium) with long exposures (300 s for outer nebulosity) via **HDRComposition** / EZ_HDR *before* entering this workflow, for a wider-DR master stack as input.

## Sources
- [[Multiscale Adaptive Stretch – Das bietet die neue Stretch-Methode mit PixInsight 2026]] (M. Käßler, 2026-01-04) — MAS architecture, Szenario A/B/C parameters, troubleshooting
- Light Vortex Astronomy (HDRMT Number-of-layers = critical, layers 5–9 blending), ChaoticNebula (HDRMT)
- PixInsight Dev — MultiscaleAdaptiveStretch tool thread
