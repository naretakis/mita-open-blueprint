# MITA 2012 vs 2014 Process Audit

Generated: January 12, 2026

## Summary

| Document Type | 2012 Count | 2014 Count | Change |
|---------------|------------|------------|--------|
| BPT | 72 | 76 | +4 |
| BCM | 72 | 74* | +2* |

*Note: BCM extraction may have minor parsing issues; will verify during conversion.

---

## BPT Changes (Business Process Templates)

### Eligibility and Enrollment Management: +4 NEW PROCESSES

The 2014 version adds **Member** processes alongside the existing Provider processes:

| 2012 (Provider Only) | 2014 (Provider + Member) |
|---------------------|--------------------------|
| Determine Provider Eligibility | Determine Provider Eligibility |
| Disenroll Provider | Disenroll Provider |
| Enroll Provider | Enroll Provider |
| Inquire Provider Information | Inquire Provider Information |
| — | **Determine Member Eligibility** (NEW) |
| — | **Disenroll Member** (NEW) |
| — | **Enroll Member** (NEW) |
| — | **Inquire Member Eligibility** (NEW) |

**Impact**: This is a significant addition reflecting the ACA/Marketplace integration requirements.

### Care Management: Minor Naming Change

- 2012: "Manage Treatment Plan**s** and Outcomes" (plural)
- 2014: "Manage Treatment Plan and Outcomes" (singular)

### All Other Areas: No Changes

- Business Relationship Management: 4 processes ✓
- Contractor Management: 9 processes ✓
- Financial Management: 19 processes ✓
- Operations Management: 9 processes ✓
- Performance Management: 5 processes ✓
- Plan Management: 8 processes ✓
- Provider Management: 5 processes ✓

---

## BCM Changes (Business Capability Matrix)

### Eligibility and Enrollment Management: +4 NEW PROCESSES

Same as BPT - adds Member processes:
- Determine Member Eligibility (NEW)
- Disenroll Member (NEW)
- Enroll Member (NEW)
- Inquire Member Eligibility (NEW)

### Performance Management: -1 PROCESS

- **Removed**: "Determine Adverse Action Incident"
- Remaining: 4 processes

### Plan Management: -2 PROCESSES

- **Removed**: "Manage Health Benefit Information"
- **Removed**: "Manage Health Plan Information"
- Remaining: 6 processes

### Financial Management: Parsing Issue

The audit detected "May 2014" as a process name - this is a parsing artifact, not a real process. Actual count should be 19 (same as 2012).

---

## Image/Diagram Analysis

| Business Area | BPT Diagrams | BCM Diagrams |
|---------------|--------------|--------------|
| Business Relationship Management | None | None |
| Care Management | None | None |
| Contractor Management | None | None |
| **Eligibility and Enrollment Management** | **76 images** | None |
| Financial Management | None | None |
| Operations Management | None | None |
| Performance Management | None | None |
| Plan Management | None | None |
| Provider Management | None | None |

Only Eligibility and Enrollment BPT contains process flow diagrams.

---

## Expected Final Counts (2014)

| Business Area | BCM | BPT |
|---------------|-----|-----|
| Business Relationship Management | 4 | 4 |
| Care Management | 9 | 9 |
| Contractor Management | 9 | 9 |
| Eligibility and Enrollment Management | 8 | 8 |
| Financial Management | 19 | 19 |
| Operations Management | 9 | 9 |
| Performance Management | 4 | 5 |
| Plan Management | 6 | 8 |
| Provider Management | 5 | 5 |
| **TOTAL** | **73** | **76** |

---

## Validation Checklist

Use this during extraction to verify completeness:

### BPT Extraction Validation
- [ ] Business Relationship Management: 4 processes
- [ ] Care Management: 9 processes
- [ ] Contractor Management: 9 processes
- [ ] Eligibility and Enrollment Management: 8 processes + diagrams
- [ ] Financial Management: 19 processes
- [ ] Operations Management: 9 processes
- [ ] Performance Management: 5 processes
- [ ] Plan Management: 8 processes
- [ ] Provider Management: 5 processes

### BCM Extraction Validation
- [ ] Business Relationship Management: 4 processes
- [ ] Care Management: 9 processes
- [ ] Contractor Management: 9 processes
- [ ] Eligibility and Enrollment Management: 8 processes
- [ ] Financial Management: 19 processes
- [ ] Operations Management: 9 processes
- [ ] Performance Management: 4 processes
- [ ] Plan Management: 6 processes
- [ ] Provider Management: 5 processes
