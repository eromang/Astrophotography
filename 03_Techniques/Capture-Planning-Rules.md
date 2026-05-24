---
title: "Capture Planning Rules"
type: technique
tags:
  - technique
  - technique/planning
---

# Capture Planning Rules

Operational rules and lessons learned for planning capture sessions at Tuntange. These exist to keep both human operators and AI agents (Claude, Codex, etc.) consistent across sessions — the rules below were paid for in real mistakes; treat this note as authoritative.

This is a *workflow* note, not a recipe — it complements [[Seasonal-Calendar]] (what to image when), [[Dark-Sky-Sites]] (where), [[FOV-Atlas]] (does it fit), and [[Integration-Budget]] (how much exists).

---

## 1. The weather gate

**Do not draft a session plan when the forecast for the dark window is marginal or worse.** Report the NOGO with hourly cloud breakdown and stop there. Don't write a `-Capture.md` note "just in case" — that pollutes the session log with no-go artifacts and (if scheduled to MacBot) wastes telemetry storage.

**Rough thresholds for marginal/bad:**

| Condition | Verdict |
|---|---|
| High cloud > 60% for ≥ 50% of dark window | ⛔ NOGO |
| Low/mid cloud > 30% any time in dark window | ⛔ NOGO (low/mid kills more than high cloud) |
| Brief clear patch < 90 min when dark window > 2 h | ⛔ NOGO (setup overhead not worth it) |
| Scattered ≤ 30% throughout | ✅ plan |
| 0–10% throughout | ✅ plan |

**Acceptable exception:** the user explicitly asks for a contingent plan ("draft it anyway, I'll decide at session start"). Default = no plan on bad weather.

**Why:** establishes a hard signal between "the sky won't cooperate tonight" (skip, do calibration / reprocessing instead) and "set up". Avoids drafting plans that turn into emotional sunk-cost when conditions don't materialize.

## 2. Multi-night strategy for dead-window / faint targets

For targets the FOV catalog flags as challenging (low max altitude, faint, narrowband-only), assume **multi-night accumulation** rather than single-night burns. Specifically:

- **Low-altitude S transit targets** (M16, M17 at ~26°): per-night SNR is capped by airmass; accumulate ≥ 6 h across multiple nights before stopping.
- **Faint extended emission** (Sh2-240 Simeis 147, IFN): 20+ h is normal.
- **Spring "dead window"** (early May → early June): if a target qualifies during this window (only Mel 111 in practice — see [[Seasonal-Calendar#Early May → Early June — Dead Window]]), batch 3–4 partial nights of 60–100 min each before the zero-dark gap (~June 5 to early July).

When drafting a multi-night plan, **cross-link** the per-night session notes (`See [[YYYY-MM-DD-Capture]]`) and ideally seed a `05_Sessions/{year}/Campaigns/{Target}-Campaign-{year}.md` note as soon as the second night completes.

## 3. Balcony horizon — actual obstruction vs preset

The [[Dark-Sky-Sites|balcony preset]] uses an AR-anchored per-azimuth altitude floor. **Some azimuth bands are more optimistic than reality:**

| Azimuth band | Preset floor (interpolated) | Add safety margin | Why |
|---|---|---|---|
| **az 130°–150°** (SE-rising low-Dec targets) | 10–15° | **+5 to +7°** | OTA line-of-sight at actual rig position is higher than naked-eye AR check suggested. Verified empirically 2026-05-24 when 2026-05-23 M16 session aborted at 00:30 CEST — M16 at calculated alt 17° vs floor 14.3° (3° margin) was still physically blocked. |
| az 120° (left building peak) | 25° | ✓ accurate | Spica check confirms |
| az 180°–240° (open S/SSW) | 3–5° | ✓ accurate | Adhara/Sirius checks confirm |
| az 270°–302° (W tree line) | 10–15° | ✓ accurate | Pleiades check confirms |

**Practical implication for SE-rising targets** (M16, M17):
- For M16 (Dec −14°), the realistic imaging start is when alt ≥ ~22° at az ≈ 134° — currently means ≥ 02:00 CEST in late May. The plan's `01:00 → 04:00 CEST` window collapses to ~02:00 → 04:00.
- For M17 (Dec −16°), even lower; the balcony window may be effectively unusable.
- **TODO:** re-do the Stellarium AR horizon check for the 120°–150° band specifically with the OTA at its actual setup position, and update the [[Dark-Sky-Sites|preset profile]] with `(135°, 20°)` or `(140°, 20°)` instead of the current optimistic `(135°, 15°)`.

## 4. MacBot operational rules

[[Mount-Diagnostics#Session-driven logging via MacBot]] describes the integration; these are the operational rules that govern when/how to use it.

### 4a. Sync Mac Mini before `mount schedule`

Before sending `schedule mount log for <date>` via iMessage to MacBot, **ensure the Mac Mini's clone of the Astrophotography repo has the session note for that date**. The MacBot scheduler reads `~/Documents/git-repos/Astrophotography/05_Sessions/{year}/Capture/{date}-Capture.md` on the Mac Mini, not on the MacBook.

Required pre-flight:
```bash
# from MacBook, after writing the session note locally
git add 05_Sessions/...
git commit -m "..."
git push
ssh macbot@192.168.178.91 'cd ~/Documents/git-repos/Astrophotography && git pull --quiet'
# then send the iMessage trigger
```

Auto-refresh cron on Mac Mini runs **Sunday 3 AM only** — without an explicit `git pull`, Mac Mini can be days behind.

**Intents that don't require this pre-flight** (they don't read vault content): `mount status`, `mount log start`, `mount log stop`, `mount schedule list`, `mount schedule cancel`.

### 4b. Single-client invariant (updated 2026-05-24)

**Both `mount.py` and ASIAIR now use the same TCP endpoint** `192.168.178.87:8899` — ASIAIR was reconfigured from USB-Serial to TCP/WiFi on 2026-05-24. Empirical testing that day revealed the WiFi bridge architecture:

- The bridge **accepts multiple TCP connections** (not exclusive)
- The 8409 hand controller serialises command processing (no physical collision on the serial bus)
- BUT **every response is broadcast to every connected TCP client** — there's no per-client filtering

**Practical consequence:**
- Same-command parallel polling (both query `:GLS#`) usually works because both parsers can handle either response
- Different-command parallel polling fails — `mount.py`'s read-until-`#` returns whatever response arrives first, which may be ASIAIR's poll of a different command, breaking the parser
- Set commands (`:SG`, `:SUT`) get last-writer-wins on the mount — ASIAIR routinely overwrites `mount.py timesync`'s offset to its preferred CET (+60 min); UTC itself stays correct in both cases

**Rule:** during an active ASIAIR session, **don't run `mount.py status / health / log`** and **don't let MacBot fire scheduled `mount log` jobs**. Reserve `mount.py` for ASIAIR-off windows (pre-session checks, post-session diagnostics, dead-window logging). If logging during a real session is critical, switch ASIAIR back to USB-Serial for that night (manual cable swap) so `mount.py` has the TCP bridge to itself.

For MacBot session-driven scheduling specifically: **cancel the scheduled `mount log start/stop` jobs on imaging nights** (`cancel mount schedule for tonight` via iMessage), or schedule logging only on non-imaging diagnostic nights. See [[../01_Equipment/Accessories/ASIAIR#Concurrent access with mount.py]] for the test results.

### 4c. Post-slew WiFi-drop pattern

Observed 2026-05-24: the mount's WiFi module drops connectivity for 30–60 s after motor activity (slew, park) on at least three consecutive tests. `mount.py` and the MacBot log subprocess both handle this gracefully (mount_unreachable events are recorded; the next sample after WiFi returns picks back up). **Don't panic-power-cycle the mount** when this happens during ASIAIR sessions — wait 60 s and re-ping before deciding it's a real failure.

## 5. Mount safety — what `mount.py` will NOT do, and why

The Mac Mini-deployed `mount.py` (read-only diagnostics + safe config + logging) deliberately **does not** include slew commands (`goto`, `park`). These were removed 2026-05-24 after a chained `goto NGC7000 → park` sequence drove the bare mount into a hard mechanical limit. The mount has no encoder memory; once internal coords desync from physical OTA position (e.g., after a mid-slew power cycle), any subsequent slew can move the mount along an unpredictable path.

**For slewing operations:**
- Use **ASIAIR** (USB-Serial) for guided imaging sessions
- Use the **8409 hand controller** directly for manual GoTo or end-of-session park
- **Never** chain motion commands back-to-back to "race" some pattern (the WiFi-drop, network instability, etc.) — let the mount settle ≥ 15 s between any two motion commands

**If a slew has been interrupted (power cycle mid-slew):**
- Manually re-anchor the OTA to the home position
- Use the 8409 hand controller's "Set Zero Position" to update the mount's internal coord system
- Only then proceed with any further slew

See [[Mount-Diagnostics#Removed: goto and park]] for the full incident write-up and the checklist of safety gates that would need to be in place before either subcommand could be safely re-introduced.

## 6. iOptron RS-232 protocol gotcha (relevant to anyone extending mount.py)

Spec strings in the form `:SdsTTTTTTTT#` parse as `:Sd` (command) + `s` (sign character: `+` or `-`) + 8 digits. The `s` between command letters and digit placeholders is the sign, not part of the command name. Sending `:Sds<sign><digits>#` injects a redundant literal `s` that firmware silently swallows — set commands appear to succeed (return `1`) but the value isn't applied, and a subsequent slew uses the wrong target.

Same convention for `:SLO`, `:SLA`, `:SAL`, `:SG`. Only `:Sd` is dangerous (the trailing `d` looks like it could be part of the command name); the others are unambiguous because they end with non-letter characters.

Regression tests for this live in `scripts/test_mount.py::TestGotoCommandFormat` (kept even though `goto` is removed, in case it's ever re-added).

## 7. Session note authoring checklist

When drafting a `-Capture.md` note (manually or via `/session-plan`), it must contain:

- [ ] **YAML frontmatter** with `date`, `twilight_evening`/`twilight_morning`, `moon_phase`/`moon_illumination`, `equipment` block, `targets:` array, `integrations:` array, `tags`
- [ ] **Conditions** section (weather, moon, temperature, humidity, wind) with explicit **Verdict: GO / MARGINAL / NOGO**
- [ ] **Location** table (matches the preset used)
- [ ] **Planning** table (Object | Type | Start | End | Exposure | Frames (planned) | Frames (realized) | Filter | Gain | Temp | Workflow) — MacBot's `mount schedule` parses Start/End from this table
- [ ] **Altitude profile** for each target through the dark window
- [ ] **Calibration** checklist (darks/flats/dark flats/bias availability per [[Master-Library]])
- [ ] **Notes** with: cross-references to related session notes, rotator calibration reminder (if relevant), multi-night plan context

If any field is uncertain (e.g., realistic frame count under marginal cloud), state the assumption explicitly.

## 8. Post-session bookkeeping

After a session (whether it ran or not):

| Outcome | Update |
|---|---|
| Frames captured | Refresh `frames (realized)`, `integrations: minutes:`, and the [[02_Targets|target file]]'s capture history table. If multi-night, also update the campaign note's Session Log. |
| Session skipped or partially executed | Add `> [!warning] Not executed` callout, set `integrations: minutes: 0`, record what blocked it (weather / horizon / hardware / personal). Don't delete the planning content — keep as historical reference. |
| Operator learned something new | Update the relevant rule in this note + write a feedback memory if Claude-discoverable knowledge is useful. |

---

## Reference

- [[Seasonal-Calendar]] — what's imageable each month from the balcony
- [[Dark-Sky-Sites]] — horizon profiles per location
- [[FOV-Atlas]] — which targets fit the RedCat 51's 5.4° × 3.6° FOV
- [[Integration-Budget]] — how much total integration exists per target
- [[Master-Library]] — calibration master inventory
- [[Mount-Diagnostics]] — `mount.py` workflow + MacBot integration
- [[iOptron-CEM26]] — mount specs + WiFi/firmware setup
- [[ASIAIR]] — primary imaging controller (separate from MacBot/mount.py)
