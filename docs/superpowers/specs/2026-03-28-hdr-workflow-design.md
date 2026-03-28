# HDR Workflow Design Spec

**Date:** 2026-03-28
**Status:** Draft
**Output file:** `04_Processing/Pixinsight/HDR-Workflow.md`

---

## Summary

A standalone PixInsight processing workflow for high dynamic range astrophotography targets — objects with bright cores surrounded by faint extended structure (e.g., M42 trapezium, galaxy nuclei). The workflow plugs into both existing parent workflows (RGB-Workflow and QuadBand-OSC-Workflow) at the stretch phase.

---

## Scope

### In scope

- HDR stretch and recovery techniques for a **single master stack**
- Two methods: MAS + HDRMT (primary), GHS + HDRMT (alternative)
- Parameter reference table by target class
- Entry/exit points linking to both parent workflows
- Applicable target list from the vault catalog

### Out of scope (future addition)

- Multi-exposure HDR composition (combining short + long exposure stacks via HDRComposition or EZ_HDR)

---

## Entry / Exit Points

### Entry

Pick up after the linear processing phase of either parent workflow. The input is a **linear, starless, noise-reduced RGB image** (stars already removed and saved).

| From | Entry after |
|------|------------|
| [[RGB-Workflow]] | Step 2.10 — NoiseXTerminator on starless |
| [[QuadBand-OSC-Workflow]] | Phase 3.4 — Channel reassembly (ChannelCombination) |

### Exit

After HDR stretch + recovery + color enhancement, return to the parent workflow for:

| To | Resume at |
|----|-----------|
| [[RGB-Workflow]] | Phase 4 — Star Processing & Reintegration |
| [[QuadBand-OSC-Workflow]] | Phase 5 — Star Processing |

---

## Primary Method: MAS + HDRMT

### Step 1: Background Reference

- Select a preview on a dark sky area free of nebulosity
- MAS uses this to compute the median for delinearization
- Without a reference, the median is calculated over the entire image, producing a darker result

### Step 2: MAS Delinearization

- **Color saturation: disabled** (mandatory for HDR — prevents out-of-gamut artifacts that HDRMT would amplify later)
- Target background: 0.15 (default)
- Enable contrast recovery
- Tuning approach:
  1. Increase dynamic range compression to reveal bright core structures
  2. Enable contrast recovery — intensity 0.5 as starting point
  3. Increase aggressiveness for more shadow contrast
  4. Decrease intensity to compensate for added aggressiveness
  5. Watch for shadow clipping — aggressiveness too high loses faint detail
- Apply to main view

### Step 3: HDRMT (HDR Multiscale Transform)

- **Lightness mask: enabled** (restricts effect to highlights only — no processing in shadows)
- **Deringing: enabled, 0.05** (controls ringing from multiscale algorithm — too high causes artifacts, but artifacts are easy to spot)
- Intensity: 0.5–0.75 typical range
- Workflow: test on previews at different intensity values (0.25, 0.5, 0.75, 1.0) before applying to main view

### Step 4: Color Enhancement

- CurvesTransformation on saturation channel
- Draw a curve that boosts low-saturation colors (in the highlights) while preserving already-saturated regions (in the nebulosity)
- BackgroundNeutralization if color cast remains

### Step 5: Return to Parent Workflow

Return to parent workflow for star reintegration (PixelMath screen blend), final adjustments (curves, DarkStructureEnhance), and export.

---

## Alternative Method: GHS + HDRMT

For when GHS is preferred (familiarity, finer midtone control).

### Differences from Primary Method

| Step | MAS method | GHS method |
|------|-----------|------------|
| Stretch | MAS with DR compression built in | GHS with SP near histogram peak, multiple small stretches |
| HDRMT intensity | 0.5–0.75 | 0.75–1.0 (higher — GHS doesn't pre-compress DR) |
| Result quality | Cleaner — DR compressed before stretch | More artifacts — HDRMT recovers already-clipped data |

### When to Use

GHS + HDRMT is a fallback, not the preferred path. MAS compresses dynamic range *during* the stretch, so HDRMT has more data to work with. GHS stretches first, potentially clipping highlights before HDRMT can recover them.

Use GHS + HDRMT when:
- The target has moderate (not extreme) dynamic range
- You want more manual control over midtone transfer
- MAS produces unsatisfactory results on a specific image

---

## Parameter Reference

Starting points by target class (adjust per image):

| Target Class | Example | MAS Aggressiveness | MAS Intensity | MAS DR Compression | HDRMT Intensity | HDRMT Deringing |
|---|---|---|---|---|---|---|
| Bright core nebula | M42, M16, M17 | 0.85 | 0.35 | High | 0.5–0.75 | 0.05 |
| Supernova remnant | Veil Nebula | 0.70 | 0.50 | Moderate | 0.25–0.50 | 0.03 |
| Galaxy with bright nucleus | M31 core, M64 | 0.60 | 0.50 | Low–Moderate | 0.25–0.50 | 0.03 |

> Bright core nebula values sourced from PixInsight official MAS HDR video (M42 example). Other classes are extrapolated starting points.

---

## Applicable Targets

| Target | Type | Filter | HDR Challenge |
|---|---|---|---|
| [[M42-Orion]] | Emission nebula | Quad Band | Trapezium core — classic HDR target |
| M16 Eagle Nebula | Emission nebula | Quad Band | Bright central pillars region |
| M17 Omega Nebula | Emission nebula | Quad Band | Bright bar structure |
| M31 Andromeda | Galaxy | L-Pro | Bright nucleus vs faint spiral arms |
| M64 Black Eye | Galaxy | L-Pro | Bright nucleus |

---

## Changes to Existing Documents

1. **RGB-Workflow.md** — Add note at Phase 3.1 (Stretch): "For HDR targets, use [[HDR-Workflow]] instead of Statistical Astro Stretching"
2. **QuadBand-OSC-Workflow.md** — Add note at Phase 4.1 (Stretch): "For HDR targets, use [[HDR-Workflow]] instead of GHS"
3. **Session planner command** — Link recommended workflow per target in the planning table (separate task)
