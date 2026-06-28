---
title: "PixInsight Modules"
type: processing-workflow
software: "PixInsight"
tags:
  - processing/pixinsight
---

# PixInsight Modules

> **Installed version:** PixInsight Core 1.9.4 (arm64) build 1695 (2026-06-23)
> **Location:** `/Applications/PixInsight`
> **Update repositories:** source of truth is `~/Library/PixInsight/core-001-pxi.settings` (binary core settings, key `Repositories`). Managed via *Resources → Updates → Manage Repositories* — **not editable by hand**. The list in [[#Module Repositories]] below was extracted from this file on 2026-06-28.

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
| PSFImage | PSF diameter evaluation for BlurXTerminator (offline equivalent: `scripts/psf_image.py`, see [[../../scripts/README.md]]) | [[RGB-Workflow]], [[OpenCluster-Workflow]], [[QuadBand-OSC-Workflow]] |
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

The **17 third-party update repositories** in the **active list** (Manage Repositories — these check for updates), in repository order, verified against `~/Library/PixInsight/core-001-pxi.settings` (key `Repositories`, entries 7–23) on 2026-06-28. The 6 official Pleiades repos (`pixinsight.com/update/1.9.4/update-*.auth`, entries 1–6) are omitted.

> ⚠️ **Active list ≠ what's installed.** Packages have actually been installed from **41** repositories over time (many later removed from the active list — the script stays installed). See [[#Installed packages by repository 41]] below.

| # | Repository URL | Provides |
|---|----------------|----------|
| 07 | https://elveteek.ch/pixinsight-updates/ez-processing-suite/ | EZ Processing Suite (EZ_Decon / HDR / SoftStretch / StarReduction…) |
| 08 | https://www.rc-astro.com/BlurXTerminator/PixInsight | BlurXTerminator module |
| 09 | https://www.rc-astro.com/NoiseXTerminator/PixInsight | NoiseXTerminator module |
| 10 | https://www.rc-astro.com/StarXTerminator/PixInsight | StarXTerminator module |
| 11 | https://www.ghsastro.co.uk/updates/ | GeneralizedHyperbolicStretch |
| 12 | https://www.skypixels.at/HVB_Repository/ | Hartmut Bornemann (HVB) script collection |
| 13 | https://www.cosmicphotons.com/pi-scripts/bfke/ | CosmicPhotons — BFKE script |
| 14 | https://www.cosmicphotons.com/pi-modules/narrowbandnormalization/ | NarrowbandNormalization module |
| 15 | https://www.ideviceapps.de/PixInsight/Utilities/ | iDeviceApps utility scripts |
| 16 | https://www.rsastro.com/ReintegrateStars/PixInsight/ | ReintegrateStars |
| 17 | https://pixinsight.deepskyforge.com/update/graxpert-process/ | GraXpert process |
| 18 | https://raw.githubusercontent.com/setiastro/pixinsight-updates-194/main/ | Seti Astro Suite (PI **1.9.4**-specific build — note the `-194` suffix) |
| 19 | https://raw.githubusercontent.com/HiddenLightPhotography/HLPAstroScripts/main/ | Hidden Light Photography scripts |
| 20 | https://pixinsight-updates.astroswell.com/ | Astroswell scripts |
| 21 | https://ruuth.xyz/autointegrate/ | AutoIntegrate (J-P Ruuth) |
| 22 | https://foraxxpaletteutility.com/FPU/ | Foraxx Palette Utility |
| 23 | https://www.cosmicphotons.com/pi-scripts/screenstars/ | ScreenStars script (star reintegration by screen blend) |

> **Security flags** (same settings file): `AllowUnsignedRepositories = true`, `AllowUnsignedScriptExecution = true`, `AllowUnsignedModuleInstallation = false`.
> **Unsigned installed repos** (rely on `AllowUnsignedRepositories = true` to update): **#12 skypixels (HVB)** and **#22 Foraxx (FPU)**.

### Active list vs installed packages

The 17 above are the **active** repos. PixInsight has installed packages from **41 repositories** (68 packages) — source of truth: `repo=` attributes in `/Applications/PixInsight/etc/update/installed.xri`, read 2026-06-28.

- **16 of the 17** active repos also have installed packages. The exception is **#22 Foraxx (FPU)** — configured but **no package installed** from it yet.
- **25 repos have installed packages but are no longer in the active list** (🔻 below).

> 🟢 **OSC2 implication:** **DBXtract is already installed** (`dbxtract.astrocitas.com`), alongside ScreenStars, NarrowbandNormalization, NBtoRGBStars and PerfectPalettePicker. The [[QuadBand-OSC-Workflow]] OSC2 upgrade therefore needs **no new installs** — it's purely a documentation/workflow change.

## Installed packages by repository (41)

Every repository with a currently-installed package, from `installed.xri` `repo=` (Pkgs = package count). **Active?** ✓ = in the active 17-repo list, 🔻 = installed but removed from the active list. ⚠️ = unsigned (per operator).

| Repository | Pkgs | Active? |
|---|---|---|
| https://raw.githubusercontent.com/bitli/pixinsight-updates/main/ | 6 | 🔻 |
| https://pixinsight.astroprocessing.com/ | 6 | 🔻 |
| https://www.cosmicphotons.com/pi-scripts/nbcolourmapper/ | 4 | 🔻 |
| https://www.rc-astro.com/NoiseXTerminator/PixInsight | 3 | ✓ |
| https://www.rc-astro.com/StarXTerminator/PixInsight | 2 | ✓ |
| https://www.rc-astro.com/BlurXTerminator/PixInsight | 2 | ✓ |
| https://www.ideviceapps.de/PixInsight/Utilities/ | 2 | ✓ |
| https://www.ghsastro.co.uk/updates/ | 2 | ✓ |
| https://www.cosmicphotons.com/pi-scripts/starreduction/ | 2 | 🔻 |
| https://www.cosmicphotons.com/pi-scripts/pixelmathui/ | 2 | 🔻 |
| https://www.cosmicphotons.com/pi-scripts/imageblend/ | 2 | 🔻 |
| https://www.cosmicphotons.com/pi-modules/solartoolbox/ | 2 | 🔻 |
| https://www.cosmicphotons.com/pi-modules/narrowbandnormalization/ | 2 | ✓ |
| https://www.cosmicphotons.com/pi-modules/colourmask/ | 2 | 🔻 |
| https://raw.githubusercontent.com/setiastro/pixinsight-updates-194/main/ | 2 | ✓ |
| https://raw.githubusercontent.com/chickadeebird/Satellite-Line-Repair/main/ | 2 | 🔻 ⚠️ |
| https://www.skypixels.at/HVB_Repository/ | 1 | ✓ ⚠️ |
| https://www.rsastro.com/ReintegrateStars/PixInsight/ | 1 | ✓ |
| https://www.cosmicphotons.com/pi-scripts/screenstars/ | 1 | ✓ |
| https://www.cosmicphotons.com/pi-scripts/drawannotation/ | 1 | 🔻 |
| https://www.cosmicphotons.com/pi-scripts/copyastrometricsolution/ | 1 | 🔻 |
| https://www.cosmicphotons.com/pi-scripts/closeview/ | 1 | 🔻 |
| https://www.cosmicphotons.com/pi-scripts/bfke/ | 1 | ✓ |
| https://uridarom.com/pixinsight/scripts/iHDR/ | 1 | 🔻 |
| https://ruuth.xyz/autointegrate/ | 1 | ✓ |
| https://raw.githubusercontent.com/setiastro/cosmicclarity/main/ | 1 | 🔻 |
| https://raw.githubusercontent.com/kopersyn/kscripts/main/ | 1 | 🔻 |
| https://raw.githubusercontent.com/HiddenLightPhotography/HLPAstroScripts/main/ | 1 | ✓ |
| https://raw.githubusercontent.com/chickadeebird/RGBAlign/main/ | 1 | 🔻 ⚠️ |
| https://raw.githubusercontent.com/charleshagen/pixinsight/main/updates/ | 1 | 🔻 |
| https://pixinsight.starnetastro.com/ | 1 | 🔻 |
| https://pixinsight.furulando.com/ | 1 | 🔻 ⚠️ |
| https://pixinsight.deepsnrastro.com/ | 1 | 🔻 |
| https://pixinsight.deepskyforge.com/update/graxpert-process/ | 1 | ✓ |
| https://pixinsight.arcturus.ch/blink2/ | 1 | 🔻 |
| https://pixinsight-updates.astroswell.com/ | 1 | ✓ |
| https://norman123al.github.io/TGScripts/TGScripts_repository/ | 1 | 🔻 |
| https://elveteek.ch/pixinsight-updates/ez-processing-suite/ | 1 | ✓ |
| https://deepskyworkflows.com/pixinsight/ | 1 | 🔻 |
| https://dbxtract.astrocitas.com/ | 1 | 🔻 |
| https://autopalette.astrocitas.com/ | 1 | 🔻 |

> Total: **68 third-party packages** across **41 repos**. The 🔻 rows (25) are installed scripts/modules whose source repo is no longer in the active update list — they won't receive updates unless re-added via Manage Repositories.
>
> Not in `installed.xri` (never installed / removed): `paulymanastro.photography/OrtonGlow/`, `killerciao/VeraLuxPorting` (gone). The dead `…deepsnrastro.com/tensorflow/` and `…starnetastro.com/tensorflow/` sub-repos are also absent (only the base repos installed).
