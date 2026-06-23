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

**Data location:** archived to T7 SSD on 2026-05-30 — `/Volumes/T7/Astrophotography/Objects/Open_Star_Clusters/ASI2600MC-REDCAT51/Mel111_Coma/` (52 raw lights + the session 120 s dark master + the production master `masterLight_…RGB_drizzle_2x_autocrop.xisf`, all MD5-verified) per [[project-vault-structure|standard SSD layout]]. Desktop working copies (lights, intermediate masters, `.pxiproject`, `Results/`) deleted after verification; only `log/` remains on the MacBook.

**Calibration archive status (verified 2026-05-30):** bias (1 ms), flat (L-Pro 60 ms), and dark-flat (60 ms) masters are **MD5-identical** to the [[Master-Library]] copies on T7. The 120 s dark master was *rebuilt in-session* (differs from the Apr-19 library master), so the exact session build was archived next to the lights in `Mel111_Coma/`; its 25 raws are also on T7 (`Templates/Dark/DARK11-BIN1-120s-10/`, MD5-identical).

## Processed Result

![[Mel111-ASI2600.jpg]]

*First-light master, 52 × 120 s (1.7 h) L-Pro. **Production master 2026-06-01** — the first stack with the **genuine L-Pro flat** and a working **astrometric solution** (drizzle 2×, 4/4 solved offline). Full [[OpenCluster-Workflow]] as-executed: [[2026-06-01-Processing]]. Clean neutral background (R/G/B medians within 0.0006), tight round star cores (Ecc 0.37→**0.26**, FWHM 4.36→**1.85 px** on the drizzle master), clean blue/orange colour separation, and the background Coma galaxies preserved. **γ Com halo resolved** — the genuine L-Pro flat removed the underlying filter reflection that left a soft blue residual on the [[2026-05-31-Processing|2026-05-31 reprocess]], and BXT Halos −0.25 + a masked MorphologicalTransformation erosion finished the bright members.*

## Processing

**Production master:** `Results/master/masterLight_…_FILTER-LPro_RGB_drizzle_2x_autocrop.xisf` (2026-06-01 — genuine L-Pro flat, drizzle 2×, **4/4 astrometric solved offline**). Full as-executed log: [[2026-06-01-Processing]]. *(History: [[2026-05-27-Processing]] WBPP Test 4 and the [[2026-05-31-Processing]] reprocess used FQuad flats + an unsolved master — superseded.)*

> [!success] Resolved 2026-06-01 — the two issues flagged below are fixed
> **γ Com halo:** the soft blue residual was an uncorrected **L-Pro filter reflection** (the old stack used FQuad flats). Re-stacked with the **genuine L-Pro flat** → reflection gone; BXT Halos −0.25 + morphological erosion finished the bright members. **FILTER metadata:** lights now carry the FITS `FILTER` keyword and the master flat its XISF `Instrument:Filter:Name` property (both `LPro`) via `set_filter.py` — WBPP groups and applies the flat automatically. **Eccentricity** (capture-side, ~0.11 field deviation = sensor tilt) is still worth chasing before the next cluster.

- Multi-night campaign originally planned for Apr 2026 — none of the 4 April nights executed (weather / personal availability). First light delivered 2026-05-25 instead.
- [[OpenCluster-Workflow]]; drizzle 2× at integration (cluster is point-source-dominated, drizzle resolves tight pairs cleanly).
- **Gradient:** planned MGC/MARS path was abandoned — MARS **DR1** lacked broadband coverage for this field; **GraXpert + ABE** used instead (gradient from 75 % moon at 28° handled well). ⚠️ Predates [[../../04_Processing/Pixinsight/MGC-Reference#MARS Database|MARS DR2]] (2026-06, doubles coverage) — re-test MGC here before assuming GraXpert is still needed.
- **Colour:** SPFC (flux) then SPCC — Gaia DR3/SP, G2V white reference, WB factors 1.000 / 0.722 / 0.800, R/G σ 0.30 / B/G σ 0.46. Clean fit.
- **Stars:** handled with [[Star-Console-Reference|Star Console]] (Hidden Light Photography PI script) — auto-measures FWHM → runs BlurXTerminator at that PSF diameter → StarXTerminator star removal, giving a starless + stars pair processed separately. **γ Com halo — reduced, residual remains** (2026-05-31 reprocess): BXT Halos −0.15 + a masked MorphologicalTransformation erosion shrank the bright members and removed the worst bloat, but a soft blue halo with a faint asymmetric wing persists at 1:1. Likely partly **filter-reflection not flat-corrected** (the stack used FQuad flats, not L-Pro — see [[Master-Library]]). **Next-step options:** re-stack once a real L-Pro flat exists; or push BXT Halos to −0.20/−0.25 / a dedicated halo-reduction pass on γ Com only.
- **Capture quality (SubFrameSelector, 52 frames):** very uniform stack — FWHM median **7.06″** (σ 0.30), SNR 1.30, background rock-stable; all 52 passed and were kept (weighted by PSF Signal Weight, frame #11 sharpest/reference). **Systematic flaw — eccentricity 0.57–0.70 (median 0.63) on *every* frame**, i.e. consistent star elongation rather than random softness. Likely cause: field tilt, guiding drift, or polar alignment. BXT Correct-Only fixed it in post, but for the next cluster — where stars *are* the subject — investigate the [[2026-05-25-Capture|PHD2 guide log]] / sensor tilt / polar alignment to get rounder stars *before* BXT. Softness (7″) itself was moon + descending airmass + the 30→26 °C thermal drift.
- **Filter — confirmed L-Pro:** the lights' FITS `FILTER` keyword is **blank**, which is why WBPP labelled the stack `NoFilter`. The ASIAIR filenames embed `_LPro_`, and SPCC/SPFC both modelled Optolong L-Pro R/G/B — so the capture was through the [[Optolong-LPro]]; only the header was unpopulated. No discrepancy, just a missing keyword.

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
