<!--
WordPress post draft
Title: Letting Claude Plan My Astrophotography Sessions
Slug: claude-astrophotography-session-planner
Excerpt: How a small Claude Code command turned an hour of pre-flight planning into a single line of input — and why the connective work between Stellarium, weather forecasts, and a target catalog is exactly what AI agents are actually useful for.
Tags: astrophotography, claude code, ai, automation, planning, obsidian
Categories: Astrophotography, Workflow
Status: draft
-->

# Letting Claude Plan My Astrophotography Sessions

Most clear nights in Luxembourg, I used to waste the first hour fighting with Stellarium, a weather forecast, and a half-remembered target list. By the time I'd figured out what was actually up, what filter to load, and whether the moon was going to ruin my plan, the sky was already half darker than it had to be. That hour belonged to imaging, and I was burning it on admin.

So I ended up building a small command-line workflow that does that work for me. The piece that makes it actually useful is Claude Code, Anthropic's terminal agent. It reads my notes, runs the math, talks to Stellarium over its REST API, and writes the session file straight into my Obsidian vault. One slash command, twenty seconds, and I'm cooling the camera instead of squinting at clearoutside.

This post is about what that looks like in practice, and what I think it tells us about where AI is genuinely useful for hobbyists.

## The boring problem nobody talks about

Planning a single imaging night is a stack of small, joyless decisions:

- When does astronomical twilight actually end tonight, and start again?
- What's the moon doing? How much will it ruin things?
- Is it really going to be clear, or just "mostly"?
- Which targets are above 30° altitude during the dark window?
- For my balcony specifically, which targets are inside the south-facing window between 135° and 225° azimuth?
- Is the target even big enough to frame in my RedCat 51's 5.4° × 3.6° field of view? (M51 is a famous galaxy. M51 is also 11 arcminutes wide. From a 250 mm focal length it's a smudge.)
- Quad Band filter or L-Pro?
- How much integration do I already have on it from previous nights?
- Should I drive somewhere darker, and if yes, which site, and how does the drive eat into the actual imaging window?

Each of those is trivial on its own. Stack them together and you've spent an hour you didn't have, deciding things you should have decided three days ago.

## What I wanted

One line of input. A complete session plan as output. Specifically:

Local twilight times. Moon phase and how badly it's going to interfere. A real weather verdict for the actual coordinates of where I'm shooting from, not "Luxembourg" averaged over 2,500 km². A filtered target list that respects my optical setup, instead of suggesting M51 because it's "famous". A recommended filter. Capture parameters. A finder chart per target showing exactly what the framing will look like through my sensor. And a warning if I should drive somewhere darker tonight, with an honest comparison of the cost.

I also wanted it written into my vault as a markdown file, so I could pull it up on the deck while setting up.

## The command

It looks like this:

```
/session-plan tomorrow --stellarium --location wahl
```

That's a Claude Code slash command. The full definition lives in a markdown file in my vault: `session-plan.md`. About 1,200 lines of structured instructions, an embedded catalog of around 50 targets, the computation rules, and the Stellarium integration logic.

The interesting part is that nothing about this is hardcoded into Claude. Everything the command knows about my equipment, my filters, my locations, my targets — it's all in that one file. If I add a new scope tomorrow, I edit one block. If I find a new dark site, I add a preset. There's no compilation step, no rebuild, no plugin to install. The command's behavior is its source code, and the source code is something I can read like documentation.

## What it actually does, in order

When I run the command, Claude works through these steps:

**1. Parses the date.** "tomorrow", "saturday", "next friday", "2026-06-14" — all valid, all resolve to the same internal date.

**2. Resolves the location.** I have five presets: my balcony (the default) plus four portable sites within 50 minutes by car. The command remembers the last preset I used so I don't have to retype it.

**3. Cross-checks the sky quality.** It hits clearoutside.com for the active location and warns me if the live SQM or Bortle class has drifted from what I have stored in the preset.

**4. Computes twilight and the moon.** Standard astronomy math, done so I don't have to: Local Sidereal Time, hour angles, moon illumination, transit altitudes.

**5. Pulls the weather.** For the actual coordinates of the chosen location, not for the country.

**6. Filters the target catalog.** This is where most of the value lives. From my embedded catalog of around 50 deep sky objects, it eliminates anything smaller than 30 arcminutes (too small to frame), anything outside my balcony's south window when shooting from home, anything within 30° of the moon when the moon is bright, and anything that doesn't get above 30° altitude during the dark window. What's left is sorted by visibility hours, by which target needs more integration based on what I've already shot, and by angular size.

**7. Picks a filter.** It counts how many of the survivors are emission targets versus broadband, and chooses Quad Band or L-Pro accordingly. If the moon is more than 75% illuminated, it shifts hard toward narrowband.

**8. Talks to Stellarium.** With the `--stellarium` flag, the command reaches into a running Stellarium instance over its REST API. For each target, it sets the time to peak altitude, focuses on the object, reads the alt/az, cross-checks against its own internal calculation, and triggers a screenshot at my actual FOV. The PNGs land in my Finder-Charts folder, named by date and target.

**9. Writes the session file.** A complete markdown note with frontmatter, conditions, target table, exposure plan, calibration checklist, and embedded finder charts. It goes into `05_Sessions/{year}/` and Obsidian indexes it automatically.

## The location work was the unexpected part

The piece of this I'm most happy with isn't the astronomy math. That's textbook stuff and you could write it yourself in an afternoon. It's the location presets.

Luxembourg is small but the light pollution gradient is real. From my balcony I read SQM 20.59 (Bortle 4, edge of 5). From a clearing on the Hoscheid plateau, 33 minutes north, I read SQM 21.23 — a factor of 1.6 in signal-to-noise on broadband targets. Four hours of integration there is roughly equivalent to ten hours from home. That's not a marginal improvement. That's the difference between a faint reflection nebula being visible at all and not.

For months I treated my drive-time estimates as fixed costs and used the closer dark site (Wahl, "30 minutes") as my default portable. Then over the course of one afternoon I drove every preset, GPS in hand, and verified the times by car. Twelve out of thirteen sites came in faster than my original estimates, by between 2 and 13 minutes. Hoscheid in particular went from 45 (estimated) to 33 (verified). One site, Wiltz Plateau, came in slower than expected because the route forces you through the town with its 30 km/h limit. These were the kinds of facts you only learn by actually driving.

I asked Claude to update the doc with the corrections. It propagated them through the ranking table, the per-site verdicts, the decision tree, the SNR multipliers section, the preset notes in the command file, and the user-facing usage guide. It also caught the second-order implications I'd missed. For example: Burfelt (verified 34 minutes, SQM 21.06) is now nearly tied with Hoscheid (33 minutes, SQM 21.23) on drive time but with worse sky. I'd kept Burfelt as my "easy first portable" preset because it had a designated parking lot and signage. With the corrected drive times, that preset is essentially redundant. Same drive, darker sky at Hoscheid. I'd never have noticed without the agent walking through the implications.

That's the part of working with an AI agent that I find genuinely useful. It doesn't just do what you ask. It thinks one step further about what else needs to change as a consequence, and it does it consistently in a way I'd never bother to do at midnight by hand.

## A real session, just for context

Last week I ran:

```
/sp 2026-06-14 -s
```

About twenty seconds later I had a markdown file telling me:

- Astronomical twilight: 23:42 to 03:18 CEST (3 hours 36 minutes of true dark)
- Moon: 1% waning crescent, sets at 21:08 — irrelevant
- Weather: clear from 22:00, light high cloud after 02:00
- Primary target: M16 Eagle Nebula, peak altitude **26.4°** at 01:14
- Filter: Antlia Quad Band
- Suggested integration: 30 × 300s for 2.5 hours total
- Finder chart embedded, showing M16 framed at the bottom of my balcony's south window

That "26.4° peak" line is exactly the kind of thing I would have missed by eye. M16 is a famously low transit from this latitude and it scrapes my horizon. The command flagged it and suggested that unless I was OK with two-night accumulation, I should pick something else. I would otherwise have found that out the hard way around 02:00, with two hours of unusable subs in the bag.

## What I think AI agents are actually good for

There's a lot of breathless writing about what AI is going to do for hobbyists, and most of it is wrong. The model isn't going to discover a comet for you. It isn't going to process your data better than PixInsight. It isn't going to teach you what gradients look like.

What it's actually good at, in my experience, is the connective tissue between specialized tools. Stellarium, clearoutside, your equipment specs, your previous session notes, your target catalog — none of those things talk to each other natively. A small agent that reads your notes, calls the APIs, runs the math, and writes the result back to your vault eliminates the integration work that nobody enjoys.

It also doesn't forget. When I add a new dark site, the next time I plan a session, the command knows about it. When I correct a drive time, every reference to that drive time updates everywhere. That's a small thing but over months of sessions it compounds.

## If you want to try something similar

A few practical notes if you're thinking about wiring up your own version.

Keep the command definition in plain markdown, not buried in code. The fact that `session-plan.md` is just a long markdown file means I can edit it from any device, version it in git, and read it like documentation. There's no IDE-specific format, no runtime, no build step.

Put your equipment, filters, and locations in the same file as the command. Don't make Claude infer them from context. The block at the bottom of mine is basically a YAML profile of my rig, and it's the only place those facts live, so there's no chance of drift between what the agent thinks I have and what I actually have.

Build the catalog by hand once, then maintain it incrementally. I started with about 30 objects I cared about. It took an evening. Adding a new one is a single-row edit. The "is this target big enough for my FOV" flag is hand-curated per object, which sounds tedious but means the filter actually works.

Verify the things you can verify, in person. Drive times, horizon obstructions, parking, the position of streetlights — none of that is in the SQM model. I learned the hard way that one of my "candidate dark sites" was 80 metres from an ArcelorMittal steel mill with 24/7 sodium floodlights. The model said Bortle 5. The reality was "imaging next to a furnace". Satellite verification catches this. Raw clearoutside numbers do not.

Let the agent talk to other tools. The Stellarium integration was the part that took the longest to get right but pays off every single session. Being able to look at a real finder chart, framed at my actual sensor's FOV, before I leave the house, is the single biggest reason I waste fewer nights on poorly-framed targets.

## Closing

None of this replaces the thing astrophotography is actually about: sitting outside in the cold, watching faint photons accumulate on a sensor, occasionally cursing at a dew heater that's lost connection. The agent just removes the hour of pre-flight admin that used to eat into the imaging window.

That hour back, multiplied by maybe 30 sessions a year, is something like a full extra night of imaging. For free, in time you would have spent staring at forecasts.

If you want to see the actual command file, both the implementation and the user-facing guide are public in my Astrophotography vault on GitHub:

**Repo:** [github.com/eromang/Astrophotography](https://github.com/eromang/Astrophotography)

- [`06_Metadata/Agents/Claude/commands/sessions/session-plan.md`](https://github.com/eromang/Astrophotography/blob/main/06_Metadata/Agents/Claude/commands/sessions/session-plan.md) — the full prompt definition
- [`06_Metadata/Agents/Claude/commands/sessions/session-plan-USAGE.md`](https://github.com/eromang/Astrophotography/blob/main/06_Metadata/Agents/Claude/commands/sessions/session-plan-USAGE.md) — the user-facing reference guide
- [`03_Techniques/Dark-Sky-Sites.md`](https://github.com/eromang/Astrophotography/blob/main/03_Techniques/Dark-Sky-Sites.md) — the verified dark sites doc that the location presets pull from

Steal whatever's useful.
