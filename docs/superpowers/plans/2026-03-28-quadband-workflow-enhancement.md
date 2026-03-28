# QuadBand Workflow Enhancement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enhance the QuadBand-OSC-Workflow with Ha emission line separation, MGC as an alternative gradient tool, and corrected SPCC guidance.

**Architecture:** Four targeted edits to the existing `QuadBand-OSC-Workflow.md` — one new step (2.7), one replaced step (2.2), one new optional step (3.5), and one table row update. Two clipping files deleted after absorption. Also update the intro paragraph to remove the blanket "SPCC does not apply" claim.

**Tech Stack:** Obsidian-flavored Markdown, YAML frontmatter

**Spec:** `docs/superpowers/specs/2026-03-28-quadband-workflow-enhancement-design.md`

---

### Task 1: Update step 2.2 — Add MGC as alternative gradient tool

**Files:**
- Modify: `04_Processing/Pixinsight/QuadBand-OSC-Workflow.md:64-69`

- [ ] **Step 1: Replace step 2.2 content**

In `04_Processing/Pixinsight/QuadBand-OSC-Workflow.md`, find:

```markdown
### 2.2 Gradient Removal

**GraXpert** (recommended) or **DBE**

- Do NOT use SPCC/SPFC at this stage — they assume broadband light
- GraXpert handles narrowband gradients well with AI mode
- If using DBE: place sample points carefully avoiding nebula regions
```

Replace with:

```markdown
### 2.2 Gradient Removal

**Option A: GraXpert** (recommended for simplicity)

- AI mode handles narrowband gradients well
- No manual tuning required
- If using DBE as fallback: place sample points carefully avoiding nebula regions

**Option B: SPFC + MGC** (more control, image-dependent)

1. **SPFC** (SpectrophotometricFluxCalibration)
   - Enable narrowband filters mode
   - Sensor: IMX571
   - Set bandwidths to ~5nm for all channels
   - Default wavelengths (Ha, OIII) are correct for Quad Band

2. **MGC** (MultiscaleGradientCorrection)
   - Use MARS DR1 database only (contains Ha and OIII bands)
   - Assign MARS bands: Ha to red channel, OIII to green and blue channels
   - Enable "Show gradient model" to verify
   - Tune scale factors per channel on a preview:
     - If nebula traces remain → increase scale factor
     - If nebula appears inverted → decrease scale factor
   - Gradient scale: 512–1024 depending on gradient complexity (lower = finer, but more risk of nebula interference)

**Which to use:** Try both on a preview. Some images respond better to MGC (especially with strong vignetting), others to GraXpert (especially with complex nebula shapes). Results are image-dependent.
```

- [ ] **Step 2: Verify the edit**

Confirm the new content appears between step 2.1 and step 2.3. Check no surrounding content was altered.

- [ ] **Step 3: Commit**

```bash
git add 04_Processing/Pixinsight/QuadBand-OSC-Workflow.md
git commit -m "docs: add MGC as alternative gradient tool in QuadBand workflow"
```

---

### Task 2: Insert new step 2.7 — Ha Emission Line Separation

**Files:**
- Modify: `04_Processing/Pixinsight/QuadBand-OSC-Workflow.md` (insert after step 2.6, before Phase 3)

- [ ] **Step 1: Insert step 2.7 before Phase 3**

In `04_Processing/Pixinsight/QuadBand-OSC-Workflow.md`, find:

```markdown
- Test on preview first

---

## Phase 3: Narrowband Color Balancing
```

Replace with:

```markdown
- Test on preview first

### 2.7 Ha Emission Line Separation (Optional)

Remove Ha crosstalk from the green and blue Bayer channels. On the [[ASI2600MCPro]], green and blue pixels are partially sensitive to Ha (656nm), contaminating the OIII signal. This step subtracts the scaled Ha contribution, producing cleaner OIII for channel extraction in Phase 3.

**PixelMath** (uncheck "Use a single expression"):

```
R: $T
G: $T - ($T[0] - med($T[0])) * scale_G
B: $T - ($T[0] - med($T[0])) * scale_B
```

Where `scale_G` and `scale_B` are camera+filter-specific constants determined once and reused.

**Finding the scale factors (one-time calibration):**

1. Select a preview containing visible Ha nebulosity
2. Start with a high scale factor (e.g., 0.5) — Ha structures will appear inverted
3. Decrease gradually until the inversion just disappears
4. The correct value minimizes Ha traces without overcorrecting
5. Repeat for each channel (G and B typically need different values)

Once determined, save the PixelMath process icon. These factors are reusable for all images from the [[ASI2600MCPro]] + [[Antlia-FQuad]] combination.

**ASI2600MC Pro + Antlia Quad Band scale factors:**

| Channel | Scale Factor |
|---------|-------------|
| Green (scale_G) | TBD — determine on first processing session |
| Blue (scale_B) | TBD — determine on first processing session |

> Update this table after calibrating. Factors should remain constant unless atmospheric conditions are anomalous.

---

## Phase 3: Narrowband Color Balancing
```

- [ ] **Step 2: Verify the edit**

Confirm step 2.7 appears after step 2.6 and before the Phase 3 heading. Check the PixelMath code block renders correctly (triple backticks inside the content — ensure proper nesting).

- [ ] **Step 3: Commit**

```bash
git add 04_Processing/Pixinsight/QuadBand-OSC-Workflow.md
git commit -m "docs: add Ha emission line separation step to QuadBand workflow"
```

---

### Task 3: Insert step 3.5 and update Quick Reference — SPCC narrowband calibration

**Files:**
- Modify: `04_Processing/Pixinsight/QuadBand-OSC-Workflow.md` (two locations)

- [ ] **Step 1: Insert step 3.5 after step 3.4**

Find:

```markdown
### 3.4 Reassemble

**ChannelCombination**
- Combine the remapped channels back into an RGB image
- Color space: RGB

---

## Phase 4: Non-Linear Processing (Stretching)
```

Replace with:

```markdown
### 3.4 Reassemble

**ChannelCombination**
- Combine the remapped channels back into an RGB image
- Color space: RGB

### 3.5 Color Calibration (Optional)

After reassembling channels into an HOO composite, SPCC can calibrate the color balance in narrowband filters mode.

**SPCC** (SpectrophotometricColorCalibration):
- Enable narrowband filters mode
- Filter wavelengths: Ha (656nm) red, OIII (496/500nm) green and blue
- Bandwidth: ~5nm for all filters
- White reference: **Photon flux** (preserves relative emission intensities as observed in the sky)
- Select a background reference area free of nebulosity

> This is optional — manual color balancing via CurvesTransformation (Phase 4.2) remains the alternative. SPCC narrowband mode provides a physically-calibrated starting point that can reduce manual tweaking.

---

## Phase 4: Non-Linear Processing (Stretching)
```

- [ ] **Step 2: Update the Quick Reference table**

Find:

```markdown
| Color calibration | SPCC with G2V reference | Skip — not applicable |
| Gradient removal | SPFC/MGC (PI 1.9) or DBE | GraXpert or DBE |
```

Replace with:

```markdown
| Color calibration | SPCC with G2V reference | SPCC narrowband mode (optional) — see step 3.5 |
| Gradient removal | SPFC/MGC (PI 1.9) or DBE | GraXpert or SPFC/MGC — see step 2.2 |
```

- [ ] **Step 3: Update the intro paragraph**

Find:

```markdown
> **Key difference from broadband RGB:** The Quad Band filter passes Ha, OIII, Hb, and SII simultaneously onto a Bayer matrix sensor. Standard color calibration (SPCC) does not apply — the light is not broadband. Channel manipulation is required to separate and balance the narrowband signal.
```

Replace with:

```markdown
> **Key difference from broadband RGB:** The Quad Band filter passes Ha, OIII, Hb, and SII simultaneously onto a Bayer matrix sensor. Standard broadband SPCC does not apply directly, but SPCC narrowband mode can be used after channel remapping (see step 3.5). Channel manipulation is required to separate and balance the narrowband signal.
```

- [ ] **Step 4: Verify all three edits**

Confirm:
- Step 3.5 appears between 3.4 and Phase 4
- Quick Reference table row is updated
- Intro paragraph no longer says "does not apply"

- [ ] **Step 5: Commit**

```bash
git add 04_Processing/Pixinsight/QuadBand-OSC-Workflow.md
git commit -m "docs: add SPCC narrowband calibration and update Quick Reference"
```

---

### Task 4: Delete absorbed clippings

**Files:**
- Delete: `04_Processing/Clippings/MultiscaleGradientCorrection — Dual-Band OSC Images (I).md`
- Delete: `04_Processing/Clippings/MultiscaleGradientCorrection — Dual-Band OSC Images (II).md`

- [ ] **Step 1: Delete both clipping files**

```bash
rm "04_Processing/Clippings/MultiscaleGradientCorrection — Dual-Band OSC Images (I).md"
rm "04_Processing/Clippings/MultiscaleGradientCorrection — Dual-Band OSC Images (II).md"
```

- [ ] **Step 2: Verify deletion**

```bash
ls 04_Processing/Clippings/
```

Expected: directory should be empty (or not exist).

- [ ] **Step 3: Commit (if files were tracked)**

If the files were tracked by git:
```bash
git add "04_Processing/Clippings/MultiscaleGradientCorrection — Dual-Band OSC Images (I).md" "04_Processing/Clippings/MultiscaleGradientCorrection — Dual-Band OSC Images (II).md"
git commit -m "docs: remove MGC dual-band clippings (absorbed into QuadBand workflow)"
```

If untracked (not in git), no commit needed — just delete.
