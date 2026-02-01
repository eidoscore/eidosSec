# Plan: Convert MasterPlan.md to Proper Markdown Format

## Overview
Convert the existing MasterPlan.md (3,493 lines) from its current pseudo-plaintext format to properly formatted Markdown for better readability, navigation, and professional presentation.

---

## File Structure Analysis

**File:** `/home/jukir/eidosSec/MasterPlan.md`
- **Lines:** 3,493
- **Sections:** 10 major sections
- **Issues Found:**
  1. Document header lacks proper markdown formatting
  2. Table of Contents is plain text without links
  3. Section headers use plain text instead of markdown (# syntax)
  4. Bullet lists lack proper markdown (- or *) markers
  5. ASCII diagrams not wrapped in code blocks
  6. Code examples not in fenced blocks
  7. Broken table at line 124 (Competitive Landscape)

---

## Detailed Implementation Steps

### Phase 1: Header & Metadata (Lines 1-22)

| Current | Proposed |
|---------|----------|
| Plain text title "MASTERPLAN.md" | `# eidosSec - Master Plan Document` |
| Plain metadata lines | Bold labels with line breaks |
| Plain text TOC | Linked markdown TOC with anchor links |

### Phase 2: Section Headers (Throughout)

Convert all section headers to proper markdown hierarchy:

```markdown
## 1. Executive Summary        (was: "1. Executive Summary")
### 1.1 Product Definition     (was: "1.1 Product Definition")
### 1.2 Problem Statement      (was: "1.2 Problem Statement")
```

**Pattern:** Replace `X.Y Title` with `### X.Y Title`

### Phase 3: Bullet Lists

Convert plain text lists to markdown bullet lists:

```markdown
**For Developers:**

- Commercial security scanners cost $500-$5,000/month...
- Open-source tools exist but require complex manual integration
- Results from multiple tools are difficult to correlate...
```

### Phase 4: ASCII Diagrams (Lines ~792-820, ~2005-2195)

Wrap box-drawing character diagrams in code blocks:

<pre>
```
+--------------------------------------------------+
|  USER'S INFRASTRUCTURE                           |
|  (Local Machine / Server)                        |
+--------------------------------------------------+
```
</pre>

### Phase 5: Code Examples

Wrap JSON, commands, and code snippets in fenced blocks:

```markdown
```json
{
  "scan_id": "xyz789",
  "status": "completed"
}
```
```

### Phase 6: Tables

Fix the Competitive Landscape table at line 124:

```markdown
| Feature | eidosSec | SonarQube Community | Snyk | Checkmarx | GitHub Advanced Security |
|---------|----------|---------------------|------|-----------|--------------------------|
| Pricing | FREE | FREE (limited) | $98-600/dev/year | $$$$ (quote) | $49/user/month |
```

---

## Acceptance Criteria

- [ ] Document renders correctly in GitHub/GitLab markdown preview
- [ ] Table of Contents links navigate to correct sections
- [ ] All lists display as proper bullet/numbered lists
- [ ] ASCII diagrams preserve formatting in code blocks
- [ ] Code examples have syntax highlighting
- [ ] Tables display with proper column alignment
- [ ] No content is lost or altered (only formatting changes)

---

## Implementation Approach

Given the file size (3,493 lines), use `multi_edit` tool with batches of related changes:

1. **Batch 1:** Header, TOC, Section 1 (Lines 1-160)
2. **Batch 2:** Sections 2-3 (Product Vision, Market Analysis)
3. **Batch 3:** Section 4 (Product Overview - longest section)
4. **Batch 4:** Sections 5-6 (Architecture, Features)
5. **Batch 5:** Sections 7-10 (UI, Security, Business, Metrics)

---

## Estimated Effort

- **Time:** 30-45 minutes
- **Batches:** 5-7 multi_edit calls
- **Risk:** Low (formatting only, no content changes)
