---
title: "GraXpert"
type: equipment
category: accessory
brand: "GraXpert"
model: "GraXpert"
status: active
tags:
  - equipment/accessory
---

# GraXpert

> **Installed version:** 3.0.2 Umbriel
> **Location:** `/Applications/GraXpert.app`

AI-powered gradient extraction and denoising tool for astrophotography.

https://www.graxpert.com/

---

## Features

- **Background Extraction** — AI-based gradient removal, alternative to PixInsight DBE/MGC
- **Denoising** — AI noise reduction (standalone or via PixInsight integration)

---

## Integration

GraXpert is available both as a standalone application and as a PixInsight module:

| Mode | Usage |
|------|-------|
| Standalone | Process FITS/TIFF directly in GraXpert UI |
| PixInsight module | Available as `GraXpert` process in PI (see [[Modules]]) |
| PixInsight script | `GraXpertDenoise` script also installed |

---

## Used In

- [[QuadBand-OSC-Workflow]] — recommended for gradient removal on narrowband data
- [[RGB-Workflow]] — alternative to SPFC/MGC for gradient removal
