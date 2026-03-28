# Obsidian Markdown — Advanced Reference

Extended reference for generic Markdown syntax within Obsidian. This file is NOT auto-loaded — read it only when advanced formatting (Mermaid, LaTeX, code nesting) is needed.

## Basic Formatting

### Paragraphs and Line Breaks

Blank line between paragraphs. Two spaces at end of line for line break within paragraph.

### Text Formatting

| Style | Syntax |
|-------|--------|
| Bold | `**text**` |
| Italic | `*text*` |
| Bold + Italic | `***text***` |
| Strikethrough | `~~text~~` |
| Highlight | `==text==` |
| Inline code | `` `code` `` |

## Lists

```markdown
- Unordered item          (always use - in this vault)
  - Nested (2-space indent)
1. Ordered item
- [ ] Incomplete task
- [x] Completed task
```

## Quotes

```markdown
> Blockquote.
> > Nested quote.
```

## Code Blocks

````markdown
```language
code here
```
````

Nest code blocks using more backticks for the outer fence:

`````markdown
````markdown
```js
console.log("Hello")
```
````
`````

## Tables

```markdown
| Left     | Center   | Right    |
|:---------|:--------:|---------:|
| Left     | Center   | Right    |
```

## Math (LaTeX)

Inline: `$e^{i\pi} + 1 = 0$`

Block:
```markdown
$$
\frac{a}{b} = c
$$
```

Common: `$x^2$` superscript, `$x_i$` subscript, `$\frac{a}{b}$` fraction, `$\sqrt{x}$` root, `$\sum_{i=1}^{n}$` sum, `$\alpha, \beta$` Greek.

## Diagrams (Mermaid)

### Flowchart

````markdown
```mermaid
graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Do this]
    B -->|No| D[Do that]
```
````

Direction: `TD` top-down, `LR` left-right, `BT` bottom-top, `RL` right-left.
Shapes: `[Rectangle]`, `(Rounded)`, `{Diamond}`, `([Stadium])`, `[(Database)]`, `((Circle))`.

### Sequence Diagram

````markdown
```mermaid
sequenceDiagram
    participant A as Alice
    participant B as Bob
    A->>B: Synchronous
    B-->>A: Dashed reply
    A-)B: Async
    Note over A,B: Shared note
```
````

### Gantt Chart

````markdown
```mermaid
gantt
    title Timeline
    dateFormat YYYY-MM-DD
    section Phase 1
        Task A :a1, 2025-01-01, 30d
        Task B :after a1, 20d
```
````

### State Diagram

````markdown
```mermaid
stateDiagram-v2
    [*] --> Draft
    Draft --> Review
    Review --> Final
    Final --> [*]
```
````

### Entity Relationship

````markdown
```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ LINE-ITEM : contains
```
````

Cardinality: `||` exactly one, `o{` zero or more, `|{` one or more, `o|` zero or one.

### Pie Chart

````markdown
```mermaid
pie title Distribution
    "A" : 45
    "B" : 30
    "C" : 25
```
````

### Linking in Diagrams

Use `class A,B internal-link;` to enable clickable links to Obsidian notes.

## Footnotes

```markdown
Text with footnote[^1].
[^1]: Footnote content.
Inline footnote.^[Content here.]
```

## Horizontal Rules

```markdown
---
```

## HTML in Obsidian

```html
<details>
  <summary>Click to expand</summary>
  Hidden content.
</details>
<kbd>Ctrl</kbd> + <kbd>C</kbd>
```
