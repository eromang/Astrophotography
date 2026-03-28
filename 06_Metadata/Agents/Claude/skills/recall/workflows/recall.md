# Recall Workflow

Load context from vault memory - temporal queries use native JSONL files, topic queries use QMD search.

## Step 1: Classify Query

Parse the user's input after `/recall` and classify:

- **Graph** - starts with "graph": "graph last week", "graph yesterday", "graph today"
  -> Go to Step 2C
- **Temporal** - mentions time: "yesterday", "today", "last week", "this week", a date, "what was I doing", "session history"
  -> Go to Step 2A → After Step 5, auto-trigger Step 6 if query resolves to a single date
- **Topic** - mentions a subject: "QMD video", "authentication", "lab content"
  -> Go to Step 2B
- **Both** - temporal + topic: "what did I do with QMD yesterday"
  -> Go to Step 2A first, then scan results for the topic → After Step 5, auto-trigger Step 6 if query resolves to a single date

## Step 2A: Temporal Recall (JSONL Timeline)

Run the recall-day script from the skill's scripts directory:

```bash
python3 .claude/skills/recall/scripts/recall_day.py list DATE_EXPR
```

Replace `DATE_EXPR` with the parsed date expression. Supported:
- `yesterday`, `today`
- `YYYY-MM-DD`
- `last monday` .. `last sunday`
- `this week`, `last week`
- `N days ago`, `last N days`

Options:
- `--min-msgs N` - filter noise (default: 3)
- `--all-projects` - scan all projects, not just current vault

Present the table to the user. If they pick a session to expand:

```bash
python3 .claude/skills/recall/scripts/recall_day.py expand SESSION_ID
```

This shows the conversation flow (user messages, assistant first lines, tool calls).

## Step 2B: Topic Recall (QMD Hybrid Search)

Uses `qmd query` (hybrid: BM25 + vector + reranking) for best recall quality. Searches all collections by default, not just sessions.

**Step 2B.1: Run hybrid search across all collections:**

```bash
qmd query "USER_QUERY" --files -n 10
```

This searches all collections (sessions, analysis, clippings, reference, projects) with query expansion and reranking. Results include relevance scores.

**Step 2B.2: If results are sparse or user needs session-specific recall**, also run targeted session search:

```bash
qmd query "USER_QUERY" -c sessions --files -n 5
```

**Step 2B.3: Deduplicate results** by document path. If same doc appears in multiple searches, keep the highest score. Present top 10 unique results, grouped by collection.

## Step 3: Fetch Full Documents (Topic path only)

For the top 3 most relevant results across all collections, get the full document:

```bash
qmd get "qmd://collection/path/to/file.md" -l 50
```

Use the paths returned from Step 2B searches. The `-l 50` flag limits to 50 lines (adjust if needed for very large files).

## Step 4: Present Structured Summary

**For temporal queries:** Present the session table and offer to expand any session.

**For topic queries:** Organize results by collection type:

**Sessions**
- What was worked on related to this topic
- Key dates and decisions
- Current status or next steps

**Notes**
- Relevant research findings
- Plans or proposals
- Content drafts

**Daily**
- Recent daily log entries mentioning this topic
- Timestamps and context

Keep this concise - it's context loading, not a full report.

## Step 5: Synthesize "One Thing"

After presenting recall results (temporal, topic, or graph), synthesize the single highest-leverage next action. This replaces generic "what would you like to work on?" with a concrete recommendation.

**How to pick the One Thing:**
1. Look at what has momentum - sessions with recent activity, things mid-flow
2. Look at what's blocked - removing a blocker unlocks downstream work
3. Look at what's closest to done - finishing > starting
4. Weigh urgency signals: deadlines in session titles, "blocked" status, time-sensitive content

**Format:** Bold line at the end of results:

> **One Thing: [specific, concrete action]**

**Good examples:**
- **One Thing: Finish the QMD video outline - sections 3-5 are drafted, just needs the closing CTA**
- **One Thing: Unblock the lab deploy - the DNS config is the only remaining blocker, everything else is ready**
- **One Thing: Record the video intro - the script and thumbnail are done, recording is the bottleneck**

**Bad examples (too generic):**
- "Continue working on the video"
- "Pick up where you left off"
- "Review recent progress"

If the recall results don't have enough signal to pick a clear One Thing (e.g. user just browsed old sessions with no active work), skip it and ask "What would you like to work on from here?" instead.

### Auto-trigger Step 6

After presenting the One Thing, check:
1. Was the query Temporal or Both?
2. Does the date resolve to a **single date**?
   - Single: `yesterday`, `today`, `YYYY-MM-DD`, `N days ago`, `last monday`
   - Range (skip): `last week`, `this week`, `last N days` (N > 1)

If both true → proceed to Step 6.

## Fallback: No Results Found

If no results are found:

```
No results found for "QUERY". Try:
- Different search terms
- Broader keywords / different date range
- --min-msgs 1 to include short sessions
```

## Step 2C: Graph Visualization

Strip "graph" prefix from query to get the date expression. Run:

```bash
python3 .claude/skills/recall/scripts/session-graph.py DATE_EXPR
```

Options:
- `--min-files N` - only show sessions touching N+ files (default: 2, use 5+ for cleaner graphs)
- `--min-msgs N` - filter noise (default: 3)
- `--all-projects` - scan all projects
- `-o PATH` - custom output path (default: .claude/skills/recall/output/session-graph.html)
- `--no-open` - don't auto-open browser

Opens interactive HTML in browser. Session nodes colored by day, file nodes colored by folder.
Tell the user the node/edge counts and what to look for (clusters, shared files).

## Step 6: Daily Recall Note Generation (Auto-triggered)

This step is auto-triggered after Step 5 when the query resolves to a single date. It is NOT triggered for multi-day ranges.

### Guard

1. Compute target path: `01_Projects/Claude-Recalls/{YYYY}/{MM}/{YYYY-MM-DD} - Daily Recall.md`
2. If the file already exists → **skip silently** (no message to user)

### Gather

Use the session data already available from Step 2A output. No additional queries needed.

### Create directory

```bash
mkdir -p 01_Projects/Claude-Recalls/{YYYY}/{MM}/
```

### Write note

Follow `06_Metadata/Templates/DAILY_RECALL_TEMPLATE.md` exactly:
- **YAML:** `title`, `date`, `document_type: recall-daily`, `sessions` (count), `tags: [lifecycle/recall]`
- **Session Overview:** table from Step 2A data (time, msgs, topic per session)
- **Work Streams:** cluster sessions by title similarity into logical streams
- **Key Decisions & Artifacts:** notable outputs from session summaries
- **One Thing:** reuse the One Thing from Step 5

### Update master index

Edit `01_Projects/Claude-Recalls/Claude-Recalls - Master Index.md`:
1. Prepend row to the **Recent Daily Recalls** table
2. Update **Statistics** counts (total notes, date range)

### Announce

Single line after all writes:

```
> Daily recall note created: [[YYYY-MM-DD - Daily Recall]]
```

No changes to `recall_day.py`, `extract-sessions.py`, or `session-graph.py` — they remain read-only query tools.

## Notes

- Temporal queries go through `recall_day.py` (native JSONL, no QMD needed)
- Graph queries go through `session-graph.py` (NetworkX + pyvis)
- Topic queries use hybrid search (`qmd query`) for best recall — searches all collections with reranking
- Fallback to BM25 (`qmd search`) only if `qmd query` is unavailable or times out
- If a result is truncated or you need more context, fetch with `-l 100` or higher
- Daily recall output path: `01_Projects/Claude-Recalls/{YYYY}/{MM}/{YYYY-MM-DD} - Daily Recall.md`
- Session recall output path: `01_Projects/Claude-Recalls/Sessions/{ProjectName}/{YYYY-MM-DD} - Session N - Topic.md`
