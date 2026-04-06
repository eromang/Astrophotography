# Astrophotography

Personal astrophotography knowledge base managed with [Obsidian](https://obsidian.md/). Documents equipment, imaging sessions, processing workflows, and deep sky targets.

## Setup

| Component | Model |
|-----------|-------|
| Camera | ZWO ASI2600MC Pro |
| Telescope | William Optics RedCat 51 (250mm f/4.9) |
| Mount | iOptron CEM26 |
| Guide camera | ZWO ASI385MC |
| Guide scope | William Optics UniGuide 32mm |
| Autofocuser | ZWO EAF |
| Filters | Antlia Quad Band, Optolong L-Pro |
| Controller | ZWO ASIAIR |
| Wishlist | ZWO EFW 5×2" filter wheel (2026 revision), COOWOO Dew Heater |

**Location:** Tuntange, Luxembourg (Bortle 4)

## Vault Structure

```
01_Equipment/     Hardware specs organized by role (imaging, guiding, optics, filters, mount, accessories)
02_Targets/       Deep sky objects — nebulae, clusters, galaxies
03_Techniques/    Guides on calibration frames, pixel binning, autofocuser workflow
04_Processing/    Post-processing workflows for PixInsight and SIRIL, calibration library
05_Sessions/      Capture and processing session logs
06_Metadata/      Templates, Claude Code skills/commands, administrative files
```

## Targets

### Captured (with integration data)

| Object | Type | Integration | Filter |
|--------|------|-------------|--------|
| NGC 7000 (North America Nebula) | Nebula | 23h 15m | L-Pro |
| M44 (Beehive Cluster) | Cluster | ~7h | Quad Band |
| M42 (Orion Nebula) | Nebula | ~6h + 1,234 D5300 frames | Quad Band |
| M45 (Pleiades) | Cluster | ~4h | Quad Band |
| M31 (Andromeda) | Galaxy | 3h 17m | L-Pro |
| NGC 2244 (Rosette Nebula) | Nebula | 1h 42m | Quad Band |

### Planned Campaigns (2026)

| Campaign | Months | Filter | Primary Targets |
|----------|--------|--------|-----------------|
| [M16 Eagle](05_Sessions/2026/Campaigns/M16-Campaign-2026.md) | Jun–Aug | Quad Band | M16 (Pillars of Creation) |
| [Cygnus Complex](05_Sessions/2026/Campaigns/Cygnus-Campaign-2026.md) | Sep–Oct | Quad Band | NGC 7000 (QB), IC 5070, Veil Nebula |
| [Autumn Broadband](05_Sessions/2026/Campaigns/Autumn-Broadband-Campaign-2026.md) | Sep–Nov | L-Pro | M33, M31, M45 |
| [Simeis 147](05_Sessions/2026/Campaigns/Simeis147-Campaign-2026.md) | Oct–Dec | Quad Band | Sh2-240 (supernova remnant) |
| [Winter Emission](05_Sessions/2026/Campaigns/Winter-Emission-Campaign-2026.md) | Oct–Dec | Quad Band | M42, Rosette, NGC 2264, IC 443, NGC 1499 |

See [`03_Techniques/Seasonal-Calendar.md`](03_Techniques/Seasonal-Calendar.md) for the full monthly target calendar.

## Techniques

- **[Signal-to-Noise Ratio (SNR)](03_Techniques/SNR.md)** — Noise model, quality benchmarks, integration planning
- **[Seasonal Target Calendar](03_Techniques/Seasonal-Calendar.md)** — Month-by-month targets for the RedCat 51 from Luxembourg
- **[Calibration Frames](03_Techniques/Frames.md)** — Darks, flats, bias, and image quality metrics
- **[Equipment Capabilities](03_Techniques/Capabilities.md)** — What the current rig can and cannot do
- **[EAF Autofocus Workflow](03_Techniques/EAF-Workflow.md)**
- **[Pixel Binning](03_Techniques/Pixel-Binning.md)**

## Processing Workflows

- **PixInsight Quad Band OSC** — Narrowband pipeline for emission nebulae
- **PixInsight RGB** — Full OSC pipeline with SubFrameSelector, WBPP, BlurXTerminator, NoiseXTerminator
- **PixInsight HDR** — For bright core + faint nebulosity blending (M42, M16, M17, M31)
- **SIRIL** — 7-step RGB post-processing pipeline
- **[Calibration Master Library](04_Processing/Calibration/Master-Library.md)** — Dark/flat/bias inventory

## Claude Code Integration

This vault includes [Claude Code](https://claude.ai/claude-code) infrastructure for AI-assisted knowledge management:

- **5 skills** — Obsidian markdown formatting, vault search, related notes, session recall, session sync
- **2 commands** — Vault health check, metadata validation
- **5 templates** — Capture session, processing session, equipment, target, todo

See [`CLAUDE.md`](CLAUDE.md) for conventions and [`06_Metadata/README.md`](06_Metadata/README.md) for full documentation.

## License

Personal knowledge base. Content shared for reference.
