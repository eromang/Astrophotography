# CLAUDE.md — AstroVault

Astrophotography knowledge base managed with Obsidian and Claude Code.

**Version:** 1.0.0

---

## Vault Structure

```
01_Equipment/     Hardware specs organized by role (imaging, guiding, optics, filters, mount, accessories)
02_Targets/       Deep sky objects organized by type (nebulae, clusters, galaxies)
03_Techniques/    Conceptual guides (frame types, pixel binning, workflows)
04_Processing/    Post-processing workflows (PixInsight, SIRIL) and calibration library
05_Sessions/      Capture and processing session logs, organized by year
06_Metadata/      Templates, Claude Code skills/commands, administrative files
```

Manuals, firmware, drivers, and images are in `01_Equipment/Manuals/{device}/`.

---

## Document Types

| Type | Location | Template |
|------|----------|----------|
| `equipment` | `01_Equipment/{category}/` | `EQUIPMENT_TEMPLATE.md` |
| `target` | `02_Targets/{object_type}/` | `TARGET_TEMPLATE.md` |
| `technique` | `03_Techniques/` | — |
| `processing-workflow` | `04_Processing/{software}/` | — |
| `calibration` | `04_Processing/Calibration/` | — |
| `capture-session` | `05_Sessions/{year}/` | `CAPTURE_SESSION_TEMPLATE.md` |
| `processing-session` | `05_Sessions/{year}/` | `PROCESSING_SESSION_TEMPLATE.md` |

Templates are in `06_Metadata/Templates/`.

---

## Tag Taxonomy

```
equipment/imaging, equipment/guiding, equipment/optics, equipment/filter, equipment/mount, equipment/accessory
target/nebula, target/cluster, target/galaxy
session/capture, session/processing
processing/pixinsight, processing/siril, processing/calibration
technique/
```

Tags are lowercase, slash-separated. No `#` prefix in YAML. Only use tags from this taxonomy.

---

## Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Equipment | Device name | `ASI2600MCPro.md`, `iOptron-CEM26.md` |
| Target | `{Designation}-{Name}` | `M42-Orion.md`, `NGC7000-North-America.md` |
| Session | `{YYYY-MM-DD}-{Type}` | `2025-03-17-Capture.md` |
| Workflow | `{Type}-Workflow` | `RGB-Workflow.md` |
| Template | `UPPER_SNAKE_CASE` | `CAPTURE_SESSION_TEMPLATE.md` |

---

## YAML Frontmatter

All notes must have YAML frontmatter with at minimum: `title`, `type`, `tags`.

- Dates: `YYYY-MM-DD`
- Wikilinks in YAML: must be quoted — `"[[ASI2600MCPro]]"`
- Tags: no `#` prefix — `- equipment/imaging`
- Lists: use `-` (not `*` or `+`)

---

## Language

Content is mixed English and French. Preserve original language of existing content. New content defaults to English.

---

## Equipment Context

Active imaging setup:
- **Camera:** ZWO ASI2600MC Pro (Gain 100, -10°C summer / -20°C winter)
- **Telescope:** William Optics RedCat 51 (250mm f/4.9)
- **Mount:** iOptron CEM26
- **Guide camera:** ZWO ASI385MC
- **Guide scope:** William Optics UniGuide 32mm
- **Autofocuser:** ZWO EAF
- **Filters:** Antlia Quad Band, Optolong L-Pro
- **Controller:** ASIAIR

Location: Tuntange, Luxembourg (Bortle 4), south-facing balcony (SE to SW).

---

## Session Context

At the start of a new session, read `06_Metadata/Agents/Claude/Session-Context.md` for a quick overview of the vault state, active work, key files, and processing lessons.

---

## Claude Code Configuration

- Config: `06_Metadata/Agents/Claude/claude_config.json`
- Skills: `06_Metadata/Agents/Claude/skills/`
- Commands: `06_Metadata/Agents/Claude/commands/`
- Session logs: `06_Metadata/Agents/Claude/Claude-Sessions/` (gitignored)

### Available Commands

| Command | Shortcut | Purpose |
|---------|----------|---------|
| `/session-plan` | `sp` | Plan a capture session for a given date |
| `/vault-health-fast` | `vhf` | Vault health check |
| `/metadata-validate-fast` | `mvf` | YAML frontmatter validation |

### Available Skills

| Skill | Trigger | Purpose |
|-------|---------|---------|
| `obsidian-markdown` | Auto on `.md` creation | Obsidian formatting reference |
| `vault-search` | `/vault-search <query>` | Semantic search |
| `related-notes` | `/related-notes <path>` | Find related notes |
| `recall` | `/recall <query>` | Load context from past sessions |
| `sync-claude-sessions` | `/sync-claude-sessions` | Export sessions to Obsidian |

---

## Rules

1. Follow templates exactly when creating new notes
2. Only use tags from the taxonomy above
3. Use `[[wikilinks]]` for internal references, `[text](url)` for external
4. Place notes in the correct folder per the routing table
5. Do not commit files in `.gitignore` (Claude-Sessions, scripts, settings)
