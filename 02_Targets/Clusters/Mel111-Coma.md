---
title: "Mel 111 — Coma Star Cluster"
type: target
designation: "Mel 111"
common_name: "Coma Star Cluster"
aliases:
  - "Cr 256"
  - "Coma Berenices Cluster"
object_type: cluster
constellation: "Coma Berenices"
magnitude: "1.8"
angular_size: "275'"
total_integration: "1.7 h"
sessions:
  - "[[2026-04-20-Capture]]"
  - "[[2026-04-21-Capture]]"
  - "[[2026-04-22-Capture]]"
  - "[[2026-04-23-Capture]]"
  - "[[2026-05-25-Capture]]"
tags:
  - target/cluster
---

# Mel 111 — Coma Star Cluster

## Capture History

### ASI2600MC Pro + RedCat 51

| Date | Exposure | Frames | Filter | Gain | Temp | Notes |
|------|----------|--------|--------|------|------|-------|
| 2026-04-20 | — | 0 | — | — | — | not executed |
| 2026-04-21 | — | 0 | — | — | — | not executed |
| 2026-04-22 | — | 0 | — | — | — | not executed |
| 2026-04-23 | — | 0 | — | — | — | not executed |
| **2026-05-25** | **120s** | **52** | **[[Optolong-LPro]]** | **g100** | **-9.6°C** | First light. 75% moon at 28° separation — test capture, see session note caveats. |

**Total realized integration:** 52 × 120s = **104 min (1.7 h)**

**Data location:** raw FITS currently on `~/Desktop/Astro/Mel 111/` (MacBook). To be moved to `/Volumes/T7/Astrophotography/Objects/Open_Star_Clusters/ASI2600MC-REDCAT51/Mel111_Coma/` per [[project-vault-structure|standard SSD layout]].

## Processing

- Multi-night campaign originally planned for Apr 2026 — none of the 4 April nights executed (weather / personal availability). First light delivered 2026-05-25 instead.
- [[RGB-Workflow]]
- Star reduction (BlurXTerminator) advised — bright cluster will saturate γ Com etc.
- For tonight's first-light data specifically: SPCC BN gradient correction will be critical due to elevated background from 75 % moon at 28°. Cluster stars themselves are bright enough to handle the penalty; faint context (IFN) is the casualty.

## Visibility from Tuntange Balcony

![[balcony-mel111-trajectory.png]]

*Mel 111 trajectory through the balcony sky on 2026-04-20 (nights Apr 21/22/23 are nearly identical, ~4 min earlier each). Colour gradient = time of night (blue early → pink dawn). The cluster enters visible sky at 22:42 in the SE at ~61° altitude, transits south at 00:02 CEST at 66° altitude, and exits in the WSW at 04:27 (twilight). All but the entry hour stays well clear of the balcony's altitude floor.*

---

## Notes

- Very large open cluster (~4.6° actual extent) — **larger than RedCat 51 FOV** (5.4° × 3.6°). Use ~45° camera rotation so cluster fits diagonally
- Bright stars (mag 1.8 average) — short subs (60–120s) prevent worst saturation
- Centred on γ Comae Berenices and surrounding ~50 stars of mag 5–10
- Open cluster, very loose, ~280 ly distant — one of the nearest open clusters
- Surrounded by faint galactic dust / IFN if integration goes deep (5h+)
- Best season: **March–May** (transits south during dark hours)
- Transit altitude from Tuntange: **66°** (very high, airmass 1.10 — optimal SNR)
- [[Optolong-LPro]] for broadband cluster work; Quad Band would suppress most cluster signal
- HDR not needed for typical cluster image; only for IFN context
