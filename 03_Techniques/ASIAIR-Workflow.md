---
title: "ASIAIR Capture Workflow"
type: technique
tags:
  - technique
---

# ASIAIR Capture Workflow

End-to-end ASIAIR session workflow for the active rig: [[ASI2600MCPro]] on [[RedCat-51]], guided by [[ASI385MC]] on [[UniGuide-32mm]], focused with [[ZWO-EAF]], on the [[iOptron-CEM26]] mount, controlled by [[ASIAIR]].

This is a separate-guide-camera workflow. Duo-camera rotation issues do not apply.

---

## Pre-flight (indoors / before dusk)

1. Charge [[Jackery-Explorer-500]], confirm tablet has updated lat/lon (open ASIAIR app at home before traveling).
2. Bring rig outside **30–60 min before first light** so the OTA equilibrates with ambient temperature — prevents focus drift in the first hour.
3. Power on ASIAIR, connect tablet to its Wi-Fi (default password `12345678`).
4. In `Wi-Fi → Power settings`, verify the four 12V ports are enabled and labelled (mount on DC1, etc.).
5. In gear settings, confirm camera, EAF, guide camera, and mount are all detected.
6. Verify `Lat/Lon` matches actual location. If `Go To` ever slews wildly off-target, fix this first.

---

## Six-step night workflow

### 1. Focus

- Run [[EAF-Workflow]] autofocus routine in the **Focus** menu.
- Do not use a Bahtinov mask with the EAF — diffraction spikes confuse the V-curve.
- Refocus is needed whenever ambient temperature drops noticeably (see [[#Focus drift|Focus drift]] below).

### 2. Polar alignment

- Rough alignment: crouch under the OTA, sight Polaris over the top of the tube; level the tripod legs first.
- In `Preview → PA`, run the routine. With the [[Antlia-FQuad|Quad Band]] installed, exposures may need to be raised to **5–10 s** because the filter blocks too much light for fast plate-solves.
- Look only at the **arrows + numbers in the upper right**, ignore the on-screen circles.
- Target accuracy: **smiley face (~2 arc-min total error)**. This is sufficient for ≤600 mm focal length, so the [[RedCat-51]] at 250 mm has large margin — do not chase zero.
- If a screw runs out of travel, lift the tripod and rotate the whole setup; reset and re-tighten.
- For azimuth: turn **both** screws in the same direction simultaneously.

### 3. Find target & confirm composition

- Sky Atlas → search by name or catalog ID (M, NGC, IC) → `Go To`.
- Take a 2–5 minute preview at full gain to see faint targets, then `Solve → Sync Mount` to make the Sky Atlas show the true current orientation.
- If composition needs rotation, loosen the camera-to-OTA screw, rotate, retighten, re-solve, re-sync.
- **Note which side of the meridian the target is on (E or W)** — required for step 4.

### 4. Guiding calibration

> The most common ASIAIR workflow mistake is calibrating in a poor location or with the wrong step size. The technique below gives a reliable calibration every night.

**Where to calibrate**

- In Sky Atlas, find the **green meridian line** and the **blue ecliptic-like arc** that crosses it near the south.
- Move the slew target to the **same side of the meridian as your subject** (target in the W → calibrate in the W).
- Stay a comfortable distance from the meridian — close enough to be near the celestial equator, far enough that the OTA is not at risk of striking a tripod leg.

**Guide settings (one-time, verify each session)**

| Setting | Value | Why |
|---|---|---|
| `Auto restore calibration` | **OFF** | Stale calibration causes mysterious tracking failures later in the night. |
| Guide camera gain | ~75% of slider | Brighter star detection on the [[ASI385MC]]. |
| Guide exposure | 2–3 s for the [[iOptron-CEM26]] | Harmonic mounts (AM5) want shorter; CEM26 likes longer. |
| Bin | 1 (raise to 2 only if narrowband filter starves the guide camera) | |

**Calibration step setting** (mount settings → calibration step, default ~2000)

The east/west steps should count up to **roughly 12** with **~2 px/step** of motion. Tune as follows:

| Symptom | Fix |
|---|---|
| West step counts past ~15–20 before reversing | Increase calibration step (steps too small). |
| West step reverses at 4–5 (too few steps) | Decrease calibration step (steps too large). |
| Yellow crosshair stays yellow / fails | Re-check focus on guide camera, confirm enough stars in frame. |

When calibration succeeds, the crosshair turns **green** and the RA/Dec graph becomes live. If the graph looks bad, the easiest fix is `Stop guiding → Begin looping → Begin guiding` again — the autoguider will pick a different star set.

### 5. Re-center target

- Back to Sky Atlas, re-`Go To` the target. Camera rotation is preserved from step 3, so composition is unchanged.

### 6. Configure AutoRun & shoot

- `Preview → AutoRun → schedule (three-dots-three-lines icon)`.
- Add a Lights block: exposure (typically 300 s on the QuadBand from Bortle 4), count, gain (HCG — see below), bin 1, interval 0.
- **File name**: clear the default and enter `{Target}{Night#}{Filter}` — e.g. `Orion1Quad`. This is non-negotiable for organisation in [[WBPP-Reference|WBPP]] later.
- **Gain**: in main camera settings, tap the small `M` next to the gain slider. This auto-selects the camera's HCG breakpoint (Gain 100 for the [[ASI2600MCPro]]). Below HCG → banding artefacts; well above HCG → highlight clipping.
- **Cooling**: -20 °C (winter) or -10 °C (summer) per [[ASI2600MCPro]] notes. In hot conditions where the TEC fan saturates, **prefer a stable warmer setpoint over an unstable cold one** — calibration frames must match the lights' actual sensor temperature, not the requested one.
- **Meridian flip**: see [[#Meridian flip safety|safety section]] below.
- Hit the circle button. After the first sub completes, **zoom in on stars** to verify focus before walking away.

---

## Meridian flip safety

The flip is the highest-risk moment of the night: the OTA crosses to the opposite side of the mount, often unattended at 02:00, with cables that can snag on the tripod, dew heaters, or the ASIAIR itself.

- In `Mount settings → Meridian flip`, **increase the time-before and time-after** the meridian. The default tolerance is tight; extra leeway gives the rig room to swing without striking anything.
- Note the meridian time displayed at the bottom of the AutoRun panel before bed.
- For balcony sessions where SE→SW windows are short, consider **disabling the flip** and stopping the sequence at the meridian — you sacrifice an hour of integration but eliminate collision risk.
- Manage cables proactively before the flip: route the camera USB and 12 V leads with enough slack on the side the OTA is moving to.

---

## Focus drift

| Condition | Action |
|---|---|
| First 30–60 min after setup | Focus will drift as OTA cools. Re-run EAF after the first 2–3 subs. |
| Temperature drop > 3–5 °C during night | Re-run EAF (manually pause AutoRun, run focus, resume). |
| Stable temperature all night | One mid-session refocus is usually enough. |
| EAF unavailable | Pause AutoRun → Preview → Bahtinov mask → re-focus → resume. |

For unattended runs, configure the EAF to refocus on temperature delta or interval — see [[ZWO-EAF]] settings.

---

## Common failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| `Go To` slews to wildly wrong sky region | Stale lat/lon on tablet, or wrong mount park | Connect tablet to Wi-Fi to refresh GPS, verify lat/lon, send mount to home, redo. |
| Polar alignment plate-solve fails | QuadBand installed + short exposure + soft focus | Increase PA exposure to 5–10 s; refine focus first; remove filter if filter drawer available. |
| Guide calibration counts wrong number of steps | Calibration step parameter mismatch | Tune mount calibration step value (see step 4 table). |
| Random tracking failures hours into a session | `Auto restore calibration` is ON | Turn it OFF in guide settings. |
| All subs blurry next morning | Focus shifted overnight, no EAF temp trigger | Enable temperature-triggered refocus on EAF, or schedule periodic refocus. |
| Sub names like `FOV_15h32m...` in WBPP | AutoRun file name field was not cleared | Always set `{Target}{Night}{Filter}` before starting AutoRun. |

---

## Related

- [[ASIAIR]] — equipment spec sheet for the controller
- [[EAF-Workflow]] — detailed autofocus routine
- [[ZWO-EAF]] — autofocuser specs and settings
- [[ASI2600MCPro]] — gain, cooling, HCG details
- [[ASI385MC]] — guide camera specs
- [[iOptron-CEM26]] — mount calibration step reference
- [[Antlia-FQuad]] — narrowband exposure considerations
- [[Frames]] — light/dark/flat/bias frame types
- [[Calibration-Strategy]] — how cooling stability affects calibration frame validity
