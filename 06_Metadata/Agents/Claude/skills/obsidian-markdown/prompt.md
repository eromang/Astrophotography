# Obsidian Flavored Markdown — Reasoning Guidance

## Purpose

Ensure consistent, vault-compliant Obsidian Markdown output across all notes. This skill provides vault-specific conventions, template patterns, and formatting rules that go beyond generic Obsidian syntax.

---

## Vault Formatting Conventions

### Link selection

| Context | Format | Example |
|---------|--------|---------|
| Internal vault note | Wikilink | `[[ASI2600MCPro]]` |
| Internal note with display text | Wikilink alias | `[[M42-Orion\|M42]]` |
| Section reference in same note | Heading link | `[[#Configuration]]` |
| Section reference in other note | Cross-note heading | `[[ASI2600MCPro#Configuration]]` |
| Equipment in YAML | Wikilink in quotes | `"[[ASI2600MCPro]]"` |
| Target in YAML | Wikilink in quotes | `"[[M42-Orion]]"` |
| External URL | Markdown link | `[ZWO](https://www.zwoastro.com/)` |
| URL in YAML field | Plain string | `source: "https://..."` |
| Embed note or section | Wikilink embed | `![[ASI2600MCPro#Product Description]]` |

**Rules:**
- Internal references always use `[[wikilinks]]`
- External URLs always use standard `[text](url)` markdown
- URLs inside YAML properties are plain strings, never markdown-formatted
- Wikilinks inside YAML must be quoted: `"[[Note Name]]"`

### Heading structure

| Mode | Pattern | Example |
|------|---------|---------|
| Equipment/Target notes | Descriptive headings | `## Configuration`, `## Capture History` |
| Session notes | Descriptive headings | `## Planning`, `## Calibration` |
| Maximum depth | 4 levels | `#` through `####` |
| Section dividers | Horizontal rule | `---` between major sections |

**Rules:**
- Never exceed `####` depth
- Always place `---` between major `##` sections
- Title heading uses `#`; body sections use `##` and below

### List formatting

| Type | Syntax | Used in |
|------|--------|---------|
| Unordered | `- item` | All notes |
| Ordered | `1. item` | Processing workflows |
| Task list | `- [ ] item` / `- [x] item` | Session calibration checklists, TODO notes |
| Nested | 2-space indent | Subsection lists |

**Rules:**
- Always use `-` for unordered lists (not `*` or `+`)
- Maintain consistent 2-space indent for nesting
- Task lists used in session calibration tracking and TODO notes

---

## YAML Frontmatter Patterns

### Common fields across all templates

| Field | Type | Format | Example |
|-------|------|--------|---------|
| `title` | string | Quoted | `"M42 — Orion Nebula"` |
| `type` | enum | Lowercase | `equipment`, `target`, `capture-session`, `processing-session` |
| `created` | date | ISO | `2025-03-08` |
| `status` | enum | Lowercase | `active`, `retired`, `wishlist` |
| `tags` | list | No `#` prefix | See below |

### Tags in YAML

```yaml
# CORRECT — no # prefix, YAML list syntax
tags:
  - equipment/imaging
  - target/nebula
  - session/capture

# WRONG — never use # in YAML tags
tags:
  - "#equipment/imaging"
```

### Wikilinks in YAML

```yaml
# CORRECT — wikilinks must be quoted in YAML
equipment:
  camera: "[[ASI2600MCPro]]"
  telescope: "[[RedCat-51]]"
targets:
  - "[[M42-Orion]]"
  - "[[M44-Beehive]]"

# WRONG — unquoted wikilinks break YAML parsing
targets:
  - [[M42-Orion]]
```

### Date formatting

```yaml
# CORRECT — always YYYY-MM-DD
date: 2025-03-17
created: 2025-03-08

# WRONG — other date formats
date: 17/03/2025
```

---

## Template-Specific YAML Schemas

YAML schemas are defined authoritatively in the template files:

| Document Type | Template |
|---------------|----------|
| Capture session | `06_Metadata/Templates/CAPTURE_SESSION_TEMPLATE.md` |
| Processing session | `06_Metadata/Templates/PROCESSING_SESSION_TEMPLATE.md` |
| Equipment | `06_Metadata/Templates/EQUIPMENT_TEMPLATE.md` |
| Target | `06_Metadata/Templates/TARGET_TEMPLATE.md` |

---

## Body Structure Patterns

### Equipment metadata blockquote

```markdown
> **Sensor:** Sony IMX571 CMOS
> **Resolution:** 6248 × 4176
> **Pixel size:** 3.76 µm
```

### Session planning table

```markdown
| Object | Type | Start | End | Exposure | Frames | Filter | Gain | Temp |
|--------|------|-------|-----|----------|--------|--------|------|------|
| M42 | Nebula | 20:29 | 22:30 | 160s | 50 | FQuad | g100 | -10°C |
```

### Capture history table (target notes)

```markdown
| Date | Exposure | Frames | Filter | Gain | Temp |
|------|----------|--------|--------|------|------|
| 2025-03-17 | 160s | 30 | FQuad | g100 | -10°C |
```

### Calibration inventory table

```markdown
| Type | Exposure | Count | Master |
|------|----------|-------|--------|
| Dark | 220s | 25 | Yes |
| Flat | 60ms | 50 | Yes |
```

---

## Common Mistakes

### YAML errors

| Mistake | Correct | Why |
|---------|---------|-----|
| Tags with `#` prefix in YAML | `- equipment/imaging` | `#` starts a YAML comment |
| Unquoted wikilinks in YAML | `"[[ASI2600MCPro]]"` | Unquoted `[[` breaks YAML |
| Wrong date format | `2025-03-17` | Always `YYYY-MM-DD` |
| Missing quotes on strings with colons | `title: "M42: Overview"` | Colons need quoting |
| Tabs in YAML indentation | Use 2 spaces | YAML forbids tabs |

### Structural errors

| Mistake | Correct | Why |
|---------|---------|-----|
| Missing `---` between sections | Always add `---` before `##` sections | Vault convention |
| Using `*` or `+` for lists | Always use `-` | Vault consistency |
| Heading level skip | Go `##` then `###` then `####` | Outline structure |

### Wikilink errors

| Mistake | Correct | Why |
|---------|---------|-----|
| Using `.md` extension in wikilinks | `[[ASI2600MCPro]]` not `[[ASI2600MCPro.md]]` | Obsidian resolves without extension |
| Pipe in table wikilink | `[[Note\|Display]]` needs `\|` escape | Unescaped `\|` breaks table column |

---

## Output Discipline

This skill is **advisory only**.
- Do not generate tags, YAML, or file changes
- Do not invent YAML fields not defined in templates
- Ensure all formatting decisions follow vault templates exactly
