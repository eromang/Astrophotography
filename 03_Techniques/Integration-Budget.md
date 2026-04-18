---
title: "Integration Budget per Target"
type: technique
tags:
  - technique
---

# Integration Budget per Target

Accumulated integration (hours) per target across all capture sessions, rendered live from `integrations:` frontmatter via [Dataview](https://github.com/blacksmithgu/obsidian-dataview).

> [!info] Data source
> Each capture session in `05_Sessions/` carries an `integrations:` array — one entry per target/filter, with `minutes` for that night. This page sums those entries.

---

## Hours per target (all filters combined)

```dataviewjs
const BAR_WIDTH = 30;
const MAX_GOAL_H = 25;

const bar = (h) => {
  const filled = Math.max(0, Math.min(BAR_WIDTH, Math.round((h / MAX_GOAL_H) * BAR_WIDTH)));
  return "█".repeat(filled) + "░".repeat(BAR_WIDTH - filled);
};

const sessions = dv.pages('"05_Sessions"')
  .where(p => p.type === "capture-session" && p.integrations);

const byTarget = {};
for (const s of sessions) {
  for (const i of s.integrations) {
    const key = String(i.target || "").trim();
    if (!key) continue;
    if (!byTarget[key]) byTarget[key] = { minutes: 0, filters: new Set(), nights: new Set() };
    byTarget[key].minutes += Number(i.minutes) || 0;
    if (i.filter) byTarget[key].filters.add(String(i.filter));
    byTarget[key].nights.add(String(s.file.name));
  }
}

const rows = Object.entries(byTarget)
  .map(([t, d]) => {
    const h = d.minutes / 60;
    return {
      target: t,
      hours: h,
      hoursFmt: h.toFixed(1) + " h",
      nights: d.nights.size,
      filters: [...d.filters].join(", "),
      bar: bar(h),
    };
  })
  .sort((a, b) => b.hours - a.hours);

dv.table(
  ["Target", "Hours", "Nights", "Filter(s)", `Budget (0–${MAX_GOAL_H} h)`],
  rows.map(r => [r.target, r.hoursFmt, r.nights, r.filters, r.bar])
);

const totalH = rows.reduce((acc, r) => acc + r.hours, 0);
dv.paragraph(`**Grand total:** ${totalH.toFixed(1)} h across ${rows.length} targets.`);
```

---

## Hours split by filter

```dataviewjs
const BAR_WIDTH = 30;
const MAX_GOAL_H = 25;

const qbBlock = "█";
const lpBlock = "▓";
const empty   = "░";

const sessions = dv.pages('"05_Sessions"')
  .where(p => p.type === "capture-session" && p.integrations);

const byTarget = {};
for (const s of sessions) {
  for (const i of s.integrations) {
    const key = String(i.target || "").trim();
    if (!key) continue;
    const f = String(i.filter || "");
    const bucket = f.includes("FQuad") || f.includes("Quad") ? "qb" : "lp";
    if (!byTarget[key]) byTarget[key] = { qb: 0, lp: 0 };
    byTarget[key][bucket] += Number(i.minutes) || 0;
  }
}

const scale = (min) => Math.max(0, Math.round((min / 60 / MAX_GOAL_H) * BAR_WIDTH));

const rows = Object.entries(byTarget)
  .map(([t, d]) => {
    const qbH = d.qb / 60;
    const lpH = d.lp / 60;
    const totalH = qbH + lpH;
    const qbW = scale(d.qb);
    const lpW = scale(d.lp);
    const remaining = Math.max(0, BAR_WIDTH - qbW - lpW);
    const stackedBar = qbBlock.repeat(qbW) + lpBlock.repeat(lpW) + empty.repeat(remaining);
    return {
      target: t,
      totalH,
      qbFmt: qbH > 0 ? qbH.toFixed(1) + " h" : "—",
      lpFmt: lpH > 0 ? lpH.toFixed(1) + " h" : "—",
      bar: stackedBar,
    };
  })
  .sort((a, b) => b.totalH - a.totalH);

dv.table(
  ["Target", "Quad Band", "L-Pro", `Stacked (█ QB, ▓ LP · 0–${MAX_GOAL_H} h)`],
  rows.map(r => [r.target, r.qbFmt, r.lpFmt, r.bar])
);
```

---

## How to update

Each capture session should carry an `integrations:` array in its frontmatter — one entry per target captured that night:

```yaml
integrations:
  - target: "[[M42-Orion]]"
    filter: "[[Antlia-FQuad]]"
    minutes: 80
  - target: "[[M44-Beehive]]"
    filter: "[[Antlia-FQuad]]"
    minutes: 140
```

Rules:

- `minutes` = realized integration time (exposure × realized subs ÷ 60), rounded to integer.
- For future/planned sessions, use the planned figure; refresh to realized after capture.
- Multi-filter nights → add one entry per filter used.
- Filter wikilink can be `[[Antlia-FQuad]]` or `[[Optolong-LPro]]` — any other filter will fall in the L-Pro bucket of the filter-split table; tweak the classifier in the dataviewjs block if you add more filters.

## Related

- [[Campaign-Timeline]] — Markwhen session timeline (same data, time-axis view)
- [[Seasonal-Calendar]] — monthly target-selection guide
- [[SNR]] — why integration time matters
