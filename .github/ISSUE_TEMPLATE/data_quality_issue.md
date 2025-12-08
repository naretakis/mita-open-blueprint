---
name: Data Quality Issue
about: Report an error or omission in the JSON data
title: '[DATA] '
labels: data-quality
assignees: ''
---

## Affected File(s)

- File path: `data/[bcm|bpt]/[business_area]/[filename].json`
- Source PDF: `source-pdfs/[bcm|bpt]/[business_area]/[filename].pdf`

## Issue Type

- [ ] Missing content
- [ ] Incorrect content
- [ ] Formatting issue
- [ ] Structural issue
- [ ] Other (please describe)

## Description

Clear description of the data quality issue.

## Source Reference

- **PDF Page Number**: [e.g., Page 3]
- **Section**: [e.g., Process Steps, Maturity Level 3]

## Expected Content

What the JSON should contain based on the source PDF:

```json
{
  "expected": "content here"
}
```

## Actual Content

What the JSON currently contains:

```json
{
  "actual": "content here"
}
```

## Source Quote

Quote the relevant text from the source PDF:

> "Exact text from PDF here..."

## Additional Context

Any other information that would help resolve this issue.

## Verification

- [ ] I have checked the source PDF
- [ ] I have verified this is not already reported
- [ ] I have included page numbers and specific references
