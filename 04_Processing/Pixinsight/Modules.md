---
title: "PixInsight Modules"
type: processing-workflow
software: "PixInsight"
tags:
  - processing/pixinsight
---

# PixInsight Modules

> **Installed version:** PixInsight Core 1.9.3 Lockhart (x64) build 1646 (2025-04-02)
> **Location:** `/Applications/PixInsight`

---

## Third-Party Modules (installed)

Modules are binary plugins (`*-pxm.dylib`) in `/Applications/PixInsight/bin/`.

| Module | Purpose | Repository |
|--------|---------|------------|
| BlurXTerminator | Star/nonstellar sharpening, optical correction | [RC-Astro](https://www.rc-astro.com/BlurXTerminator/PixInsight) |
| NoiseXTerminator | AI noise reduction | [RC-Astro](https://www.rc-astro.com/NoiseXTerminator/PixInsight) |
| StarXTerminator | AI star removal | [RC-Astro](https://www.rc-astro.com/StarXTerminator/PixInsight) |
| GeneralizedHyperbolicStretch | Advanced stretch with midtone control | [GHS Astro](https://www.ghsastro.co.uk/updates/) |
| GraXpert | AI gradient extraction | [DeepSkyForge](https://pixinsight.deepskyforge.com/update/graxpert-process/) |
| NarrowbandNormalization | Normalize narrowband channels | [Cosmic Photons](https://www.cosmicphotons.com/pi-modules/narrowbandnormalization/) |
| GradientCorrection | Gradient removal | Built-in (PI 1.9+) |

### AI Model Files (library/)

| Model | Version |
|-------|---------|
| BlurXTerminator | v4 |
| NoiseXTerminator | v2, v3 |
| StarXTerminator | v11 (full + lite + lite-nonoise) |

---

## Third-Party Scripts (installed)

Key scripts in `/Applications/PixInsight/src/scripts/`. Only listing those relevant to the workflows.

### Used in Workflows

| Script | Purpose | Used in |
|--------|---------|---------|
| WBPP | Weighted Batch Pre-Processing (stacking) | [[RGB-Workflow]], [[QuadBand-OSC-Workflow]] |
| SubframeSelector | Evaluate and select sub-frames | [[RGB-Workflow]], [[QuadBand-OSC-Workflow]] |
| ImageSolver | Plate solving | [[RGB-Workflow]] |
| FindBackground | Background reference selection | [[RGB-Workflow]] |
| PSFImage | PSF diameter evaluation for BlurXTerminator | [[RGB-Workflow]], [[QuadBand-OSC-Workflow]] |
| statisticalstretch | Statistical Astro Stretching | [[RGB-Workflow]] |
| DarkStructureEnhance | Enhance dark nebula lanes | [[RGB-Workflow]], [[QuadBand-OSC-Workflow]] |
| ReintegrateStars | Star reintegration after StarXTerminator | [[RGB-Workflow]], [[QuadBand-OSC-Workflow]] |
| AutoStretch | Quick visualization stretch | Both workflows |
| AutoDBE | Automated background extraction | Backup option |

### Narrowband / Color

| Script | Purpose |
|--------|---------|
| NBRGBCombination | Narrowband to RGB combination |
| CombineHaToRGB | Blend Ha into RGB |
| CombineRGBAndNarrowband | Combine broadband RGB with narrowband |
| CreateHubblePaletteFromOSC | SHO palette from OSC data |
| NarrowbandHueCombination | Narrowband hue mapping |
| NBtoRGBStars | Natural star colors in narrowband images |
| NBStarColorsFromRGB | Extract star colors from broadband for narrowband |
| PerfectPalettePicker | Color palette selection |

### Processing Utilities

| Script | Purpose |
|--------|---------|
| EZ_Decon | Simplified deconvolution |
| EZ_HDR | HDR combination |
| EZ_SoftStretch | Gentle stretch |
| EZ_StarReduction | Star size reduction |
| EZ_LiveStack | Live stacking |
| CosmicClarity_SASpro | Set Astro statistical stretch |
| star_stretch_v2.1 | Star-specific stretch |
| GraXpertDenoise | AI denoising via GraXpert |
| Halo-B-Gon | Star halo removal |
| StarHaloReducer | Alternative halo reduction |
| RepairStarCores | Fix overexposed star cores |
| CorrectMagentaStars | Fix magenta star artifacts |

### Analysis & Planning

| Script | Purpose |
|--------|---------|
| NoiseEvaluation | Measure image noise |
| SNR / SNRmax | Signal-to-noise measurement |
| CelestialSNR | Celestial object SNR calculator |
| CalculateSkyLimitedExposure | Optimal exposure calculator |
| AberrationSpotter | Detect optical aberrations |
| WhatsInMyImage | Identify objects in FOV |
| MosaicPlanner | Plan mosaic panels |
| Ephemerides | Celestial object positions |

### Astrometry & Photometry

| Script | Purpose |
|--------|---------|
| AnnotateImage | Label objects in image |
| AperturePhotometry | Measure star brightness |
| CatalogStarGenerator | Generate star catalogs |
| BlindSolver2000 | Blind plate solving |
| FindingChart | Generate finding charts |

---

## Module Repositories

Update URLs for the PixInsight repository manager:

- https://www.rc-astro.com/BlurXTerminator/PixInsight
- https://www.rc-astro.com/NoiseXTerminator/PixInsight
- https://www.rc-astro.com/StarXTerminator/PixInsight
- https://www.ghsastro.co.uk/updates/
- https://elveteek.ch/pixinsight-updates/ez-processing-suite/
- https://www.skypixels.at/HVB_Repository/
- https://www.cosmicphotons.com/pi-scripts/bfke/
- https://www.cosmicphotons.com/pi-modules/narrowbandnormalization/
- https://raw.githubusercontent.com/setiastro/pixinsight-updates/main/
- https://www.ideviceapps.de/PixInsight/Utilities/
- https://www.rsastro.com/ReintegrateStars/PixInsight/
- https://pixinsight.deepskyforge.com/update/graxpert-process/
