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

| Object | Type | Integration |
|--------|------|-------------|
| NGC 7000 (North America Nebula) | Nebula | 23h 15m |
| M42 (Orion Nebula) | Nebula | In progress |
| NGC 2244 (Rosette Nebula) | Nebula | In progress |
| M13 (Hercules Cluster) | Cluster | In progress |
| M44 (Beehive Cluster) | Cluster | In progress |
| M5 (Rose Cluster) | Cluster | In progress |
| M86 | Galaxy | In progress |
| NGC 4435 (The Eyes) | Galaxy | In progress |

## Processing Workflows

- **PixInsight RGB** — Full OSC pipeline with SubFrameSelector, WBPP, BlurXTerminator, NoiseXTerminator
- **PixInsight LRGB** — Two workflows: classic DBE and modern GraXpert approaches
- **SIRIL** — 7-step RGB post-processing pipeline

## Claude Code Integration

This vault includes [Claude Code](https://claude.ai/claude-code) infrastructure for AI-assisted knowledge management:

- **5 skills** — Obsidian markdown formatting, vault search, related notes, session recall, session sync
- **2 commands** — Vault health check, metadata validation
- **5 templates** — Capture session, processing session, equipment, target, todo

See [`CLAUDE.md`](CLAUDE.md) for conventions and [`06_Metadata/README.md`](06_Metadata/README.md) for full documentation.

## License

Personal knowledge base. Content shared for reference.
