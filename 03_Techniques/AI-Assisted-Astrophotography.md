---
title: "AI-Assisted Astrophotography"
type: technique
created: 2026-04-02
tags:
  - technique/
---

# AI-Assisted Astrophotography

How AI tools like Claude Code can support astrophotographers throughout the entire imaging workflow — from equipment management to image processing. Based on real-world usage across multiple sessions.

---

## Equipment Management

### Inventory and Purchase Tracking

AI can maintain a structured equipment database with purchase dates, prices, stores, and cross-references between devices:

- Create and update equipment notes with standardized frontmatter (brand, model, status, purchase details)
- Cross-link accessories to their parent devices (filters to telescopes, adapters to optical trains)
- Track equipment status (active, retired, wishlist)
- Identify missing accessories or calibration frames based on the current setup

### Equipment Recommendations

When planning a capture session, AI can recommend the right equipment based on the target:

- Suggest the appropriate filter for a given target type (narrowband vs broadband)
- Cross-reference purchase dates with capture dates to verify which equipment was actually used
- Flag inconsistencies in session logs (e.g., a filter listed that wasn't purchased yet)

---

## Session Planning

### Capture Session Preparation

AI can assist with planning imaging sessions by:

- Identifying target visibility windows based on location and time of year
- Recommending camera settings (gain, temperature, exposure) based on past sessions
- Calculating total integration time from existing data
- Identifying missing calibration frames (darks, flats) before going out

### Data Organization

AI can inspect external storage (SSD drives) to:

- Inventory light frames across multiple nights
- Count SubFrameSelector-approved frames per session
- Identify naming inconsistencies in folder structures and fix them
- Create local working copies with the correct folder structure for processing

---

## Image Processing Guidance

### Step-by-Step Processing Plans

Based on documented workflows, AI generates target-specific reprocessing plans with:

- Pre-filled settings for the specific equipment setup (pixel size, focal length, filter)
- Calibration frame matching from the master library
- Warnings about missing calibration data
- Exact file paths for all input data

### SubFrameSelector Analysis

AI can parse SFS CSV exports to provide:

- Statistical summaries (FWHM, eccentricity, median, SNR distributions)
- Per-night quality breakdowns to identify the best and worst sessions
- Recommended approval expressions with frame counts at different thresholds
- Detection of twilight-contaminated frames and outliers

### WBPP Configuration

AI reviews WBPP settings through screenshots, identifying:

- Missing configurations (Drizzle not enabled, wrong rejection algorithm)
- Incorrect values (sigma too high for satellite trail rejection, Force values checked)
- Optimal settings per workflow (broadband vs narrowband)
- Complete documentation of all tabs and options for future reference

### Gradient Removal Tuning

For processes like MultiscaleGradientCorrection (MGC), AI provides:

- MARS database coverage assessment per target field
- Scale factor tuning guidance through iterative screenshot analysis (bright traces = too low, inverted = too high)
- Decision support for choosing between MGC and GraXpert based on data availability
- Channel-by-channel adjustment recommendations

### Color Calibration Review

AI analyzes SPFC and SPCC PDF reports to verify:

- Source counts and dispersion quality
- Scale factor reasonableness
- Filter and QE curve configuration correctness

### Stretching and Final Adjustments

Through real-time screenshot analysis, AI provides guidance on:

- Statistical Astro Stretching parameter selection
- CurvesTransformation channel-by-channel adjustments for specific target types
- LocalHistogramEqualization two-pass tuning (large structures, then small)
- ArcsinhStretch factor selection for star reintegration
- Before/after comparison and quality assessment

---

## Knowledge Management

### Vault Organization

AI maintains a structured knowledge base following consistent conventions:

- Standardized templates for equipment, targets, sessions, and workflows
- Tag taxonomy enforcement
- YAML frontmatter validation
- Cross-referencing between notes using wikilinks

### Processing Documentation

Every processing session is documented in detail, creating a reusable knowledge base:

- Complete settings for every PixInsight process applied
- Tuning logs showing how values were arrived at (e.g., MGC scale factor iterations)
- Lessons learned from each session, preventing the same mistakes from being repeated
- Reference documents for complex processes (WBPP, MGC, CurvesTransformation, LHE)

### Workflow Evolution

AI helps evolve processing workflows over time:

- Updates workflow documents with new techniques and corrected settings
- Incorporates lessons learned from actual processing sessions
- Creates dedicated reference documents from YouTube tutorial transcripts
- Maintains consistency between workflow descriptions and actual practice

### Lessons Learned Persistence

Critical processing knowledge is preserved across sessions:

- "Never check Force values" — discovered through failed plate solves
- "MARS broadband coverage varies by field" — learned from NGC 5746 failure vs NGC 7000 success
- "SPCC BN conflicts with DBE" — identified through color cast issues
- "Green cast with broadband L-Pro on emission nebulae" — fixed with SCNR/CurvesTransformation

---

## Real-Time Processing Support

### Screenshot Analysis

AI analyzes PixInsight screenshots in real-time to:

- Verify settings before applying a process
- Identify problems (nebula in gradient model, over-processed LHE)
- Suggest corrections with specific values
- Compare before/after results

### Iterative Tuning

For processes requiring visual tuning (MGC, CurvesTransformation, LHE), AI provides:

- Step-by-step guidance through the adjustment process
- Interpretation of what the current result means
- Specific next steps based on the current state
- Convergence detection (when the result is good enough to apply)

### Error Recovery

When things go wrong, AI assists with:

- Diagnosing PixInsight crashes and suggesting settings to change
- Identifying incorrect settings that led to poor results
- Recommending alternative approaches (e.g., GraXpert when MGC fails)
- Undo/redo guidance for iterative processing

---

## Limitations

AI-assisted astrophotography is not a replacement for learning the craft. Key limitations:

- **AI cannot see your screen in real-time** — it relies on screenshots you share, which may not capture all relevant information
- **Aesthetic judgments are subjective** — AI can suggest technically correct settings, but the final look is always your creative choice
- **Processing context matters** — the same settings don't work for every image. AI recommendations are starting points, not absolute rules
- **Hardware interaction is indirect** — AI cannot control PixInsight, ASIAIR, or your mount. It can only advise
- **Knowledge has limits** — AI may not know about the latest PixInsight updates, new plugins, or niche techniques

---

## Tools Used

| Tool | Role |
|------|------|
| **Claude Code** | AI assistant for knowledge management, processing guidance, screenshot analysis, and documentation |
| **PixInsight** | Primary image processing software |
| **ASIAIR** | Capture controller (writes FITS headers used for plate solving) |
| **Obsidian** | Knowledge base / vault management |
| **External SSD** | Data storage, inspected by AI for file inventory and organization |
