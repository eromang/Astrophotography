---
name: vault-search
description: Semantic search across the entire vault using QMD. Use when user says "search vault", "find notes about", "what do I have on", "vault search".
user-invocable: true
argument-hint: <query> [-c collection]
allowed-tools: Bash(qmd:*), Bash(PATH=*qmd:*), Read
---

# Vault Search Skill

Semantic search across all vault collections using QMD hybrid search (BM25 + vector + reranking).

## What It Does

- Searches all QMD collections (clippings, analysis, sessions, reference, projects) by default
- Optional collection filter with `-c <collection>`
- Returns ranked results with relevance scores
- Offers to read top results

## Usage

```
/vault-search NIS2 supply chain
/vault-search incident reporting -c analysis
/vault-search PQC transition -c projects
```

## Workflow

See below for step-by-step process.

### Step 1: Parse Input

Extract:
- **query**: everything before `-c` flag (or entire input if no flag)
- **collection**: value after `-c` (optional, defaults to all collections)

### Step 2: Run QMD Search

```bash
qmd query "<query>" --files -n 10
```

Or with collection filter:
```bash
qmd query "<query>" -c <collection> --files -n 10
```

### Step 3: Format Results

Present results as a table:

| # | Score | Collection | Title | Path |
|---|-------|------------|-------|------|
| 1 | 0.93 | analysis | ... | ... |
| 2 | 0.87 | clippings | ... | ... |

### Step 4: Offer Follow-up

Ask if the user wants to:
- Read any of the top results
- Refine the search
- Search a specific collection
