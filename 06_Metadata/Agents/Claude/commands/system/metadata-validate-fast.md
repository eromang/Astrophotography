---
name: metadata-validate-fast
description: "Validate YAML frontmatter structure and required fields"
shortcut: mvf
category: system
version: "1.0"
---

# Metadata Validation

## Objective

Validate YAML frontmatter structure across vault notes. Diagnostic only — no modifications unless `--fix` flag is used.

---

## Required Fields by Document Type

### Equipment (`type: equipment`)

| Field | Required | Type |
|-------|----------|------|
| `title` | Yes | string |
| `type` | Yes | `equipment` |
| `category` | Yes | enum: imaging, guiding, optics, filter, mount, accessory |
| `brand` | Yes | string |
| `model` | Yes | string |
| `status` | Yes | enum: active, retired, wishlist |
| `tags` | Yes | list |

### Target (`type: target`)

| Field | Required | Type |
|-------|----------|------|
| `title` | Yes | string |
| `type` | Yes | `target` |
| `designation` | Yes | string |
| `common_name` | Yes | string |
| `object_type` | Yes | enum: nebula, cluster, galaxy |
| `constellation` | Yes | string |
| `tags` | Yes | list |

### Capture Session (`type: capture-session`)

| Field | Required | Type |
|-------|----------|------|
| `title` | Yes | string |
| `type` | Yes | `capture-session` |
| `date` | Yes | date (YYYY-MM-DD) |
| `location` | Yes | string |
| `targets` | Yes | list |
| `tags` | Yes | list |

### Processing Session (`type: processing-session`)

| Field | Required | Type |
|-------|----------|------|
| `title` | Yes | string |
| `type` | Yes | `processing-session` |
| `date` | Yes | date (YYYY-MM-DD) |
| `software` | Yes | string |
| `tags` | Yes | list |

---

## Validation Checks

1. **YAML structure**: Valid YAML between `---` delimiters
2. **Required fields**: All required fields present per document type
3. **Date format**: All dates are `YYYY-MM-DD`
4. **Tag format**: No `#` prefix, valid taxonomy paths
5. **Wikilinks**: Quoted in YAML values
6. **Type enum**: Valid document type value

---

## Output Format

```markdown
## Metadata Validation Report

**Notes scanned:** {{count}}
**Valid:** {{n}}
**Issues:** {{n}}

| Note | Issue | Field | Details |
|------|-------|-------|---------|
| {{note}} | Missing field | `brand` | Required for equipment type |
```

**This command does not modify files unless `--fix` is used.**
