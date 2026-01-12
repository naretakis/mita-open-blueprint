# MITA 2014 Migration Project

## Project Overview

**Objective**: Replace the 2012 MITA v3.0 data with the May 2014 updated versions while preserving the 2012 data for historical reference.

**Start Date**: January 12, 2026  
**Status**: 🟡 In Progress

---

## Background

### Why This Migration?

The original MITA data in this repository was extracted from the February 2012 version of MITA v3.0. CMS released an updated version in May 2014 ("3.0 Update") which is now the current standard. This project updates our JSON data to reflect the 2014 versions.

### Key Differences: 2012 vs 2014 Source Files

| Aspect | 2012 Version | 2014 Version |
|--------|--------------|--------------|
| File Structure | Individual PDF per process (144 files) | Two master PDFs (one for all BPTs, one for all BCMs) |
| Split Structure | N/A | Split into per-business-area PDFs |
| Total BCM Processes | 72 | TBD (to be verified) |
| Total BPT Processes | 72 | TBD (to be verified) |
| Publication Date | February 2012 | May 2014 |

### Source File Locations

- **2012 (Archived)**: `source-pdfs/archived-2012-versions/`
- **2014 Master PDFs**: `source-pdfs/may-2014-update/`
  - `Part I Appendix C Business Process Model Details 3 0 Update.pdf` (all BPTs)
  - `Part I Appendix D Business Capability Matrix Details 3 0 Final V1 0.pdf` (all BCMs)
- **2014 Split PDFs**: 
  - `source-pdfs/may-2014-update/bcm/[Business Area]/` 
  - `source-pdfs/may-2014-update/bpt/[Business Area]/`
  - `source-pdfs/may-2014-update/business-architecture/` (overviews)

---

## Implementation Phases

### Phase 1: Archive Current Data ✅ COMPLETE
- [x] Move `data/` → `data-archived-2012/`
- [x] Create fresh `data/` folder structure
- [x] Create project tracking document

### Phase 2: Analyze 2014 PDF Structure ✅ COMPLETE
- [x] Extract and analyze sample BCM PDF (Care Management)
- [x] Extract and analyze sample BPT PDF (Care Management)
- [x] Document process boundary markers
- [x] Identify any new metadata fields
- [x] Identify any structural changes
- [x] Compare process list: 2012 vs 2014

### Phase 3: Schema Review & Design ✅ COMPLETE
- [x] Review current JSON schema
- [x] Identify new fields needed for 2014 content
- [x] Decide: per-process vs per-business-area JSON files (per-process)
- [x] Finalize schema (user approved)
- [x] Document text formatting preservation strategy
- [ ] Update `docs/DATA_STRUCTURE.md` (will do after extraction)

**Schema finalized**: `docs/PROPOSED_SCHEMA_2014.md`

### Phase 4: Build Extraction Tools 🟡 READY TO START
- [ ] Create text cleaning/formatting utilities
- [ ] Create BPT extraction module
- [ ] Create BCM extraction module  
- [ ] Create image extraction module (for EE area)
- [ ] Test on Care Management (9 processes, no diagrams)
- [ ] Test on Eligibility & Enrollment (8 processes + diagrams)

### Phase 5: Extract & Convert All Data 🔴 NOT STARTED
- [ ] Process all BCM business areas (10 areas)
- [ ] Process all BPT business areas (10 areas)
- [ ] Generate all JSON files

### Phase 6: Validation & QA 🔴 NOT STARTED
- [ ] Update validation script for new schema
- [ ] Run comprehensive validation
- [ ] Manual spot-check samples
- [ ] Compare 2012 vs 2014 content (document changes)

### Phase 7: Documentation Updates 🔴 NOT STARTED
- [ ] Update `docs/CONVERSION_METHODOLOGY.md`
- [ ] Update `data/README.md`
- [ ] Update `source-pdfs/README.md`
- [ ] Update root `README.md`
- [ ] Archive/update `docs/EXAMPLES.md`

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-12 | Archive 2012 data (not delete) | Preserve for historical reference |
| 2026-01-12 | Re-evaluate JSON schema | 2014 may have new fields; opportunity to improve |
| 2026-01-12 | Keep per-process JSON files | Simpler edits, better git diffs, matches user workflows; extraction tool will split from per-area PDFs |
| 2026-01-12 | Add trigger_event sub-categories to schema | 2014 explicitly categorizes triggers as environment-based vs interaction-based |
| 2026-01-12 | Add image/diagram extraction support | Eligibility & Enrollment BPTs contain process flow diagrams; other areas don't have diagrams |
| 2026-01-12 | Use pymupdf (fitz) for PDF processing | Better image extraction support than pypdf; can render pages and extract embedded images |
| 2026-01-12 | Schema approved | User approved proposed schema with trigger event categorization, diagrams support, and formatting preservation |
| 2026-01-12 | No image dimensions in JSON | Not useful for consumers; keep schema simple |

---

## Open Questions

1. **JSON Granularity**: Should we keep one JSON file per process (current approach) or switch to one JSON file per business area (matching 2014 PDF structure)?
   - Pro per-process: Simpler edits, smaller files, matches 2012 approach
   - Pro per-area: Matches source structure, fewer files to manage
   - **RECOMMENDATION**: Keep per-process (see Decision Log)

2. ~~**Schema Changes**: What new fields exist in 2014 that weren't in 2012?~~
   - **ANSWERED**: Trigger events now have sub-categories (Environment-based vs Interaction-based)
   - Content is more detailed but structure is largely the same

3. ~~**Process Changes**: Are there new processes added or processes removed in 2014?~~
   - **ANSWERED**: Care Management has same 9 processes; full audit needed for all areas

4. ~~**Member Management**: The 2012 version had no Member Management data. Does 2014 include it?~~
   - **ANSWERED**: No, Member Management folder is still empty in 2014

---

## Notes & Findings

### Phase 2 Findings (2026-01-12)

#### PDF Structure Analysis

**BCM PDFs (2014)**
- One PDF per business area containing all processes for that area
- Process boundary marker: `[CODE] – [Sub-Category]\n[Process Name]\nCapability`
- Example: `CM – Case Management\nEstablish Case\nCapability`
- Table format with columns: Capability Question, Level 1-5
- Categories within each process (same as 2012):
  - Business Capability Descriptions
  - Business Capability Quality: Timeliness of Process
  - Business Capability Quality: Data Access and Accuracy
  - Business Capability Quality: Cost Effectiveness
  - Business Capability Quality: Effort to Perform; Efficiency
  - (and others)

**BPT PDFs (2014)**
- One PDF per business area containing all processes for that area
- Process boundary marker: `[CODE] [Sub-Category]\n[Process Name]\nItem Details`
- Example: `CM Case Management\nEstablish Case\nItem Details`
- Fields in each process (same as 2012):
  - Description
  - Trigger Event (now split into "Environment-based" and "Interaction-based")
  - Result
  - Business Process Steps
  - Shared Data
  - Predecessor
  - Successor
  - Constraints
  - Failures
  - Performance Measures

#### Key Observations

1. **Sub-Categories Exist**: Within Care Management, there are sub-categories:
   - "CM Case Management" (6 processes)
   - "CM Authorization Determination" (3 processes: Authorize Referral, Service, Treatment Plan)

2. **Process Count Matches**: Care Management has 9 processes in both 2012 and 2014

3. **Trigger Events Enhanced**: 2014 explicitly categorizes triggers as:
   - "Environment-based Trigger Events"
   - "Interaction-based Trigger Events"

4. **Member Management Still Empty**: The folder exists but contains no PDFs (same as 2012)

5. **Page References**: Each page includes "Part I, Appendix [C/D] - Page XX" and "May 2014 Version 3.0"

6. **Content Changes**: Descriptions appear more detailed in 2014 (e.g., Establish Case description includes specific claim indicators like "PWK - Attachments", "NTE - Notes", etc.)

#### Image/Diagram Analysis

**Eligibility and Enrollment BPTs contain process flow diagrams!**
- Page 2 of EE BPT has ~42 large images (>400px) that form process flow diagrams
- These appear to be visual representations of the Business Process Steps
- Largest images are ~663x615 and ~695x503 pixels
- Other business areas (Care Management, Financial Management) do NOT have diagrams

**Image Extraction Strategy:**
- Use pymupdf (fitz) library for image extraction
- Filter for meaningful images (>200x200 pixels to exclude borders/lines)
- Store images in `data/bpt/[area]/images/` folder
- Reference images in JSON via `process_details.diagrams` array

#### Business Areas Confirmed (2014)

| Business Area | BCM PDF | BPT PDF |
|---------------|---------|---------|
| Business Relationship Management | ✅ | ✅ |
| Care Management | ✅ | ✅ |
| Contractor Management | ✅ | ✅ |
| Eligibility and Enrollment Management | ✅ | ✅ |
| Financial Management | ✅ | ✅ |
| Member Management | ❌ (empty) | ❌ (empty) |
| Operations Management | ✅ | ✅ |
| Performance Management | ✅ | ✅ |
| Plan Management | ✅ | ✅ |
| Provider Management | ✅ | ✅ |

---

## Files Modified/Created

| File | Action | Date |
|------|--------|------|
| `data/` | Moved to `data-archived-2012/` | 2026-01-12 |
| `data/bcm/` | Created (empty) | 2026-01-12 |
| `data/bpt/` | Created (empty) | 2026-01-12 |
| `docs/2014_MIGRATION_PROJECT.md` | Created | 2026-01-12 |
| `docs/PROPOSED_SCHEMA_2014.md` | Created | 2026-01-12 |
| `docs/2014_PROCESS_AUDIT.md` | Created | 2026-01-12 |

---

## Team

- **Lead**: User + Kiro AI Assistant
- **Repository**: mita-open-blueprint
