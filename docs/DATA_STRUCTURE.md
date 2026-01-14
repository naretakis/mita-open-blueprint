# MITA Data Structure Reference

This document provides detailed schema definitions for BCM and BPT JSON files.

## Overview

All JSON files follow consistent schemas based on document type:
- **BPT** (Business Process Template) - Detailed process workflows and steps
- **BCM** (Business Capability Model) - Maturity assessment questions with 5 levels

## Common Fields

Both BPT and BCM files share these top-level fields:

```json
{
  "document_type": "BPT" | "BCM",
  "version": "3.0",
  "version_date": "May 2014",
  "business_area": "string",
  "process_name": "string",
  "process_code": "string",
  "sub_category": "string",
  "metadata": {
    "source_file": "string",
    "source_page_range": "string",
    "extracted_date": "YYYY-MM-DD"
  }
}
```

### Field Definitions

- **document_type**: Either "BPT" or "BCM"
- **version**: MITA version (currently "3.0")
- **version_date**: Publication date from source document (e.g., "May 2014")
- **business_area**: High-level business domain
- **process_name**: Specific process being described
- **process_code**: Two-letter abbreviation (BR, CM, CO, EE, FM, OM, PE, PL, PM)
- **sub_category**: Process subcategory from source document
- **metadata.source_file**: Relative path to source PDF
- **metadata.source_page_range**: Page range in source PDF (e.g., "1-4")
- **metadata.extracted_date**: Date of JSON extraction

## BPT Schema

Business Process Template files contain detailed process information.

### Complete BPT Structure

```json
{
  "document_type": "BPT",
  "version": "3.0",
  "version_date": "May 2014",
  "business_area": "Care Management",
  "sub_category": "Case Management",
  "process_name": "Establish Case",
  "process_code": "CM",
  "process_details": {
    "description": "Full process description text",
    "trigger_events": {
      "environment_based": [
        "Periodic review to scan for new cases is due."
      ],
      "interaction_based": [
        "Receive enrollment of member from Enroll Member business process."
      ]
    },
    "results": [
      "Expected outcome of the process"
    ],
    "process_steps": [
      "1. START: First step description",
      "2. Second step description"
    ],
    "diagrams": [],
    "shared_data": [
      "Data source or store used"
    ],
    "predecessor_processes": [
      "Process that comes before"
    ],
    "successor_processes": [
      "Process that follows"
    ],
    "constraints": "Process constraints and limitations",
    "failures": [
      "Failure condition"
    ],
    "performance_measures": [
      "Performance metric"
    ]
  },
  "metadata": {
    "source_file": "source-pdfs/may-2014-update/bpt/Care Management/Care Management BPT.pdf",
    "source_page_range": "1-4",
    "extracted_date": "2026-01-12"
  }
}
```

### BPT-Specific Fields

**process_details.description** (string)
- Full text description of the process
- May contain multiple paragraphs
- Often includes notes and additional context

**process_details.trigger_events** (object)
- Events that initiate the process, categorized by type
- Contains two sub-arrays:
  - **environment_based**: Events triggered by schedules, timers, or system conditions
  - **interaction_based**: Events triggered by external inputs, alerts, or other processes
- Either array may be empty if no triggers of that type exist

**process_details.results** (array of strings)
- Expected outcomes when process completes
- Typically 2-10 results
- Examples:
  - "Case established in system"
  - "Member assigned to case manager"

**process_details.process_steps** (array of strings)
- Ordered list of process steps
- Typically 5-20 steps
- Often numbered in the text (e.g., "1. START: Receive request")
- May include sub-steps with lettered items (e.g., "a.", "b.")

**process_details.diagrams** (array)
- Process flow diagrams extracted from source PDFs
- Usually empty (`[]`) for most business areas
- When present (primarily in Eligibility & Enrollment BPTs), contains objects with:
  - **filename**: Image filename (e.g., "EE_Determine_Member_Eligibility_diagram_2_2.png")
  - **description**: Brief description of the diagram
  - **page_reference**: Page number in source PDF

**process_details.shared_data** (array of strings)
- Data sources, stores, or systems used
- Examples:
  - "Member data store including demographics"
  - "Health Information Exchange (HIE) data store"
  - "Provider data store including provider network information"

**process_details.predecessor_processes** (array of strings)
- Processes that typically occur before this one
- Process names from other BPT documents

**process_details.successor_processes** (array of strings)
- Processes that typically follow this one
- Process names from other BPT documents

**process_details.constraints** (string)
- Limitations, requirements, or rules
- May include regulatory requirements
- May include timing constraints

**process_details.failures** (array of strings)
- Conditions that cause process failure
- Error scenarios
- Examples:
  - "Member not eligible for case management"
  - "Required information not available"

**process_details.performance_measures** (array of strings)
- Metrics for measuring process performance
- May contain placeholders (e.g., "within __ days")
- Examples:
  - "Time to establish case = within __ business days"
  - "Accuracy with which rules are applied = __%"

## BCM Schema

Business Capability Model files contain maturity assessment questions.

### Complete BCM Structure

```json
{
  "document_type": "BCM",
  "version": "3.0",
  "version_date": "May 2014",
  "business_area": "Care Management",
  "sub_category": "Case Management",
  "process_name": "Establish Case",
  "process_code": "CM",
  "maturity_model": {
    "capability_questions": [
      {
        "category": "Business Capability Descriptions",
        "question": "Is the process primarily manual or automatic?",
        "levels": {
          "level_1": "Description of basic capability",
          "level_2": "Description of improved capability",
          "level_3": "Description of enhanced capability",
          "level_4": "Description of advanced capability",
          "level_5": "Description of optimized capability"
        },
        "note": "Optional explanatory note (not present in all questions)"
      }
    ]
  },
  "metadata": {
    "source_file": "source-pdfs/may-2014-update/bcm/Care Management/Care Management BCM.pdf",
    "source_page_range": "1-7",
    "extracted_date": "2026-01-12"
  }
}
```

### BCM-Specific Fields

**maturity_model.capability_questions** (array)
- Array of capability assessment questions
- Typically 10-11 questions per file
- Each question has 5 maturity levels

**capability_questions[].category** (string)
- Question category/grouping
- Common categories:
  - "Business Capability Descriptions"
  - "Business Capability Quality: Timeliness of Process"
  - "Business Capability Quality: Data Access and Accuracy"
  - "Business Capability Quality: Cost Effectiveness"
  - "Business Capability Quality: Effort to Perform; Efficiency"
  - "Business Capability Quality: Accuracy of Process Results"
  - "Business Capability Quality: Utility or Value to Stakeholders"

**capability_questions[].question** (string)
- The capability question being assessed
- Always ends with "?"
- Examples:
  - "Is the process primarily manual or automatic?"
  - "How timely is this end-to-end process?"
  - "How accurate is the information in the process?"

**capability_questions[].levels** (object)
- Contains 5 maturity level descriptions
- Keys: level_1, level_2, level_3, level_4, level_5
- Each level describes increasing capability maturity

**capability_questions[].note** (string, optional)
- Additional explanatory information for the question
- Not present in all questions
- Found primarily in Eligibility & Enrollment and Operations Management BCMs

### Maturity Level Progression

Levels generally follow this pattern:

- **Level 1**: Manual, basic compliance, state-specific standards
- **Level 2**: Some automation, HIPAA standards, improved over Level 1
- **Level 3**: Significant automation, MITA Framework adoption, intrastate interoperability
- **Level 4**: Advanced automation, interstate/regional interoperability
- **Level 5**: Optimized automation, national/international interoperability

## Process Codes

| Code | Business Area |
|------|---------------|
| BR | Business Relationship Management |
| CM | Care Management |
| CO | Contractor Management |
| EE | Eligibility and Enrollment Management |
| FM | Financial Management |
| OM | Operations Management |
| PE | Performance Management |
| PL | Plan Management |
| PM | Provider Management |

> **Note**: Member Management (MM) is defined in the MITA framework but has no published BCM/BPT documents.

## Data Types

All JSON files use standard JSON data types:

- **string**: Text values
- **array**: Ordered lists
- **object**: Key-value structures

## Validation Rules

Valid JSON files must:

1. Be well-formed JSON
2. Include all required top-level fields
3. Have correct document_type ("BCM" or "BPT")
4. Include type-specific content (maturity_model or process_details)
5. Have populated metadata fields
6. Match content from source PDF

## Usage Examples

See [EXAMPLES.md](EXAMPLES.md) for code examples using these schemas.

## Schema Evolution

Future versions may add:
- Additional optional fields
- New process codes
- Extended metadata
- Cross-reference links

Breaking changes will be versioned appropriately.
