---
name: related-notes
description: Find semantically related notes for a given note. Use when user says "find related", "similar notes", "what's related to this", "related notes".
user-invocable: true
argument-hint: <note-path>
allowed-tools: Bash(qmd:*), Bash(PATH=*qmd:*), Read
---

# Related Notes Skill

Find semantically related notes for a given note using QMD hybrid search.

## What It Does

- Reads the target note's title and opening content
- Constructs a semantic query from the note's topic
- Searches all collections for related content
- Excludes the target note from results
- Returns a ranked list with paths and scores

## Usage

```
/related-notes 03_Analysis/01_Govern/Legislation/EU/NIS2/NIS2 Directive — Overview.md
/related-notes [[POST Cyberattack - Analysis]]
```

## Workflow

### Step 1: Read Target Note

Read the specified note. Extract:
- YAML `title` field
- YAML `tags` (first 5)
- First 200 characters of body content
- `document_type` if present

### Step 2: Construct Query

Build a search query from the extracted topic. Combine title keywords + key tags into a natural query string.

Example: Note titled "NIS2 Directive — Overview" with tags `law/eu/nis2`, `geo/eu` → query: `"NIS2 directive cybersecurity EU legislation"`

### Step 3: Run QMD Search

```bash
qmd query "<constructed query>" --files -n 12
```

### Step 4: Filter and Present

- Remove the target note from results
- Present top 10 as a ranked list:

| # | Score | Type | Title | Path |
|---|-------|------|-------|------|
| 1 | 0.91 | legislation-analysis | ... | ... |
| 2 | 0.85 | clipping-analysis | ... | ... |

### Step 5: Offer Follow-up

Ask if the user wants to read any of the related notes or add wikilinks between them.
