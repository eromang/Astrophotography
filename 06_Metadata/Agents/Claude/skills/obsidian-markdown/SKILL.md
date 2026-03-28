---
name: obsidian-markdown
description: Create and edit Obsidian Flavored Markdown with wikilinks, embeds, callouts, properties, and other Obsidian-specific syntax. Use when working with .md files in Obsidian, or when the user mentions wikilinks, callouts, frontmatter, tags, embeds, or Obsidian notes.
version: "1.0"
user-invocable: true
auto-invoked: true
trigger: markdown-file-creation
activation: Automatically loaded before any .md file is created or written in the vault
scope:
  - Obsidian Flavored Markdown syntax
  - YAML frontmatter and properties
  - Wikilinks, embeds, and callouts
  - Vault-specific formatting conventions
boundaries:
  - Syntax reference and reasoning guidance only
  - Does not perform tagging or tag validation
  - Does not enforce document_type rules
  - Does not replace template-specific commands
---

# Obsidian Flavored Markdown — Quick Reference

Compact reference for Obsidian-specific syntax extensions. For generic Markdown (basic formatting, lists, code blocks, tables, math, Mermaid diagrams), see `advanced-reference.md` in this skill folder.

## Internal Links (Wikilinks)

```markdown
[[Note Name]]                          Basic link
[[Note Name|Display Text]]             Aliased link
[[Note Name#Heading]]                  Link to heading
[[Note Name#Heading|Custom Text]]      Heading + alias
[[#Heading in same note]]              Same-note heading
[[Note Name#^block-id]]                Link to block
[[Note Name#^block-id|Custom Text]]    Block + alias
```

Block IDs are defined at the end of a paragraph:
```markdown
This paragraph can be linked to. ^my-block-id
```

For lists and quotes, add block ID on a separate line after a blank line:
```markdown
> Quote text

^quote-id
```

## Embeds

```markdown
![[Note Name]]                   Embed full note
![[Note Name#Heading]]           Embed section
![[Note Name#^block-id]]         Embed block
![[image.png]]                   Embed image
![[image.png|300]]               Image with width
![[image.png|640x480]]           Image with dimensions
![[document.pdf]]                Embed PDF
![[document.pdf#page=3]]         PDF at page
![[audio.mp3]]                   Embed audio
```

External images use standard Markdown: `![Alt text](https://example.com/image.png)`

## Properties (YAML Frontmatter)

Properties use YAML frontmatter at the very start of a note:

```yaml
---
title: My Note Title
date: 2024-01-15
tags:
  - project
  - nested/tag
aliases:
  - Alternative Name
cssclasses:
  - custom-class
status: in-progress
completed: false
---
```

| Type | Example |
|------|---------|
| Text | `title: My Title` |
| Number | `rating: 4.5` |
| Checkbox | `completed: true` |
| Date | `date: 2024-01-15` |
| Date & Time | `due: 2024-01-15T14:30:00` |
| List | `tags: [one, two]` or YAML list |
| Links | `related: "[[Other Note]]"` |

## Tags

```markdown
#tag                    Inline tag (body text)
#nested/tag             Hierarchical tag
#tag-with-dashes        Hyphenated tag
```

In frontmatter (preferred in this vault):
```yaml
tags:
  - tag1
  - nested/tag2
```

Tags can contain: letters, numbers (not first), underscores, hyphens, forward slashes.

## Callout Types

```markdown
> [!note]
> Basic callout.

> [!info] Custom Title
> Callout with custom title.

> [!faq]- Collapsed by default
> Foldable callout (collapsed).

> [!faq]+ Expanded by default
> Foldable callout (expanded).
```

| Type | Aliases |
|------|---------|
| `note` | - |
| `abstract` | `summary`, `tldr` |
| `info` | - |
| `todo` | - |
| `tip` | `hint`, `important` |
| `success` | `check`, `done` |
| `question` | `help`, `faq` |
| `warning` | `caution`, `attention` |
| `failure` | `fail`, `missing` |
| `danger` | `error` |
| `bug` | - |
| `example` | - |
| `quote` | `cite` |

Nested callouts use additional `>` prefix:
```markdown
> [!question] Outer
> > [!note] Inner
> > Nested content
```

## Comments

```markdown
Visible %%hidden%% text.

%%
Hidden block (not rendered in reading view).
%%
```

## Escaping Special Characters

Use backslash: `\*`, `\_`, `\#`, `` \` ``, `\|`, `\~`

## Critical Formatting Rules

| Rule | Detail |
|------|--------|
| Blank line before headings | Required for correct rendering |
| Blank line before tables | Required to avoid merging with text |
| Blank line before `---` | Without it, may parse as setext heading |
| Table header separator | Always include `|---|---|` row |
| Consistent table columns | Same number of `|` in every row |
| No heading level skip | `##` then `###` then `####`, never skip |
| Pipe in table wikilink | Escape: `[[Note\|Display]]` |
| Wikilinks in YAML | Must be quoted: `"[[Note Name]]"` |
| No `#` prefix in YAML tags | Write `- analysis` not `- #analysis` |
| Spaces in Markdown links | URL-encode as `%20` |
