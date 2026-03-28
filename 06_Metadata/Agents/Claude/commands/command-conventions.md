# Command Conventions — AstroVault

## Tag Taxonomy

All tags in this vault follow a hierarchical structure:

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

### Rules

- Tags are lowercase, slash-separated hierarchies
- No `#` prefix in YAML
- Tags must come from the taxonomy above
- New tags require updating this document first

---

## Routing Rules

| Document Type | Expected Location |
|---------------|-------------------|
| Equipment | `01_Equipment/{category}/` |
| Target | `02_Targets/{object_type}/` |
| Technique | `03_Techniques/` |
| Processing workflow | `04_Processing/{software}/` |
| Calibration | `04_Processing/Calibration/` |
| Capture session | `05_Sessions/{year}/` |
| Processing session | `05_Sessions/{year}/` |
| Template | `06_Metadata/Templates/` |
| Skill/Command | `06_Metadata/Agents/Claude/` |

---

## YAML Frontmatter Convention

All notes must have YAML frontmatter with at minimum:
- `title` (string)
- `type` (enum)
- `tags` (list)

Additional required fields vary by document type — see templates in `06_Metadata/Templates/`.

---

## Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Equipment | Device name | `ASI2600MCPro.md` |
| Target | `{Designation}-{Name}` | `M42-Orion.md` |
| Session | `{YYYY-MM-DD}-{Type}` | `2025-03-17-Capture.md` |
| Processing | `{Workflow}-Workflow` | `RGB-Workflow.md` |
