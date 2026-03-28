# 06_Metadata

Vault configuration, templates, and Claude Code infrastructure.

**Version:** 1.0.0

---

## Purpose

The `06_Metadata/` folder provides:

- Templates for consistent note creation
- Claude Code skills, commands, and configuration
- Administrative files (shopping list, etc.)

---

## Structure

```
06_Metadata/
├── Agents/Claude/
│   ├── claude_config.json      # Command/skill registry
│   ├── Claude-Sessions/        # Session transcripts (gitignored)
│   ├── skills/
│   │   ├── obsidian-markdown/  # Obsidian syntax reference
│   │   ├── vault-search/       # Semantic vault search
│   │   ├── related-notes/      # Find related notes
│   │   ├── recall/             # Session/context recall
│   │   └── sync-claude-sessions/ # Session sync
│   └── commands/
│       ├── command-conventions.md
│       └── system/
│           ├── vault-health-fast.md
│           └── metadata-validate-fast.md
├── Templates/
│   ├── CAPTURE_SESSION_TEMPLATE.md
│   ├── PROCESSING_SESSION_TEMPLATE.md
│   ├── EQUIPMENT_TEMPLATE.md
│   ├── TARGET_TEMPLATE.md
│   └── TODO_TEMPLATE.md
├── ToBuy.md
└── README.md
```

---

## Templates

| Template | Purpose | Document Type |
|----------|---------|---------------|
| `CAPTURE_SESSION_TEMPLATE.md` | Imaging session log | `capture-session` |
| `PROCESSING_SESSION_TEMPLATE.md` | Post-processing session log | `processing-session` |
| `EQUIPMENT_TEMPLATE.md` | Hardware specifications | `equipment` |
| `TARGET_TEMPLATE.md` | Deep sky object tracking | `target` |
| `TODO_TEMPLATE.md` | Task tracking | `todo` |

---

## Skills

| Skill | Type | Purpose |
|-------|------|---------|
| `obsidian-markdown` | Auto-invoked | Obsidian syntax and formatting |
| `vault-search` | User-invocable | Semantic search across vault |
| `related-notes` | User-invocable | Find related notes |
| `recall` | User-invocable | Load context from past sessions |
| `sync-claude-sessions` | User-invocable | Export sessions to Obsidian |

---

## Commands

| Command | Shortcut | Purpose |
|---------|----------|---------|
| `/vault-health-fast` | `vhf` | Vault health check |
| `/metadata-validate-fast` | `mvf` | YAML validation |

---

## Tag Taxonomy

```
equipment/
  imaging, guiding, optics, filter, mount, accessory
target/
  nebula, cluster, galaxy
session/
  capture, processing
processing/
  pixinsight, siril, calibration
technique/
```

---

## Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| Equipment | PascalCase or kebab-case | `ASI2600MCPro.md`, `iOptron-CEM26.md` |
| Target | Designation-Name | `M42-Orion.md`, `NGC7000-North-America.md` |
| Session | ISO date + type | `2025-03-17-Capture.md` |
| Template | UPPER_SNAKE_CASE | `CAPTURE_SESSION_TEMPLATE.md` |

---

## Maintenance

Templates are normative — notes must conform to templates.
