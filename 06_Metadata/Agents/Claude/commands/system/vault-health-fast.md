---
name: vault-health-fast
description: "Comprehensive vault health check (orphans, broken links, routing)"
shortcut: vhf
category: system
version: "1.0"
---

# Vault Health Check

## Objective

Perform a comprehensive health check of the vault structure. Diagnostic only — no modifications.

---

## Health Check Categories

### 1. Orphan Notes
Notes with no incoming links (backlinks).

**Exclusions:** README files, template files, files in `06_Metadata/`.

### 2. Broken Links
Internal links pointing to non-existent notes.

### 3. Routing Violations
Notes in incorrect folders:

| Document Type | Expected Location |
|---------------|-------------------|
| Equipment | `01_Equipment/**` |
| Target | `02_Targets/**` |
| Technique | `03_Techniques/` |
| Processing workflow | `04_Processing/**` |
| Session | `05_Sessions/**` |
| Template/config | `06_Metadata/**` |

### 4. Frontmatter Issues
- Missing frontmatter entirely
- Missing required fields (`title`, `type`, `tags`)
- Invalid `type` values

### 5. Naming Violations

| Type | Convention |
|------|-----------|
| Target | `{Designation}-{Name}.md` |
| Session | `{YYYY-MM-DD}-{Type}.md` |
| Equipment | Device name, no spaces |

---

## Output Format

```markdown
## Vault Health Report

**Notes scanned:** {{count}}
**Date:** {{YYYY-MM-DD}}

### Health Summary

| Category | Status | Count |
|----------|--------|-------|
| Orphan notes | | {{n}} |
| Broken links | | {{n}} |
| Routing violations | | {{n}} |
| Missing frontmatter | | {{n}} |
| Naming violations | | {{n}} |

### Overall Health Score: {{score}}/100
```

---

## Health Score

```
Score = 100 - (Critical x 5) - (Warnings x 2) - (Info x 0.5)
```

| Score | Rating |
|-------|--------|
| 90-100 | Excellent |
| 75-89 | Good |
| 60-74 | Fair |
| <60 | Needs Attention |

---

## File Operations

1. SCAN all notes
2. BUILD link graph
3. CHECK routing rules
4. CHECK frontmatter
5. CHECK naming conventions
6. REPORT findings

**This command does not modify any files.**
