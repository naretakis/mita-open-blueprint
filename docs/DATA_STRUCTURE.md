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
  "date": "February 2012",
  "business_area": "string",
  "process_name": "string",
  "process_code": "string",
  "sub_category": "string",
  "page_count": number,
  "metadata": {
    "source_file": "string",
    "extracted_date": "YYYY-MM-DD"
  }
}
```

### Field Definitions

- **document_type**: Either "BPT" or "BCM"
- **version**: MITA version (currently "3.0")
- **date**: Publication date from source document
- **business_area**: High-level business domain
- **process_name**: Specific process being described
- **process_code**: Two-letter abbreviation (BR, CM, CO, EE, FM, MM, OM, PE, PL, PM)
- **sub_category**: Process subcategory from source document
- **page_count**: Total pages in source PDF
- **metadata.source_file**: Relative path to source PDF
- **metadata.extracted_date**: Date of JSON extraction

## BPT Schema

Business Process Template files contain detailed process information.

### Complete BPT Structure

```json
{
  "document_type": "BPT",
  "version": "3.0",
  "date": "February 2012",
  "business_area": "Care Management",
  "process_name": "Establish Case",
  "process_code": "CM",
  "sub_category": "Case Management",
  "page_count": 5,
  "process_details": {
    "description": "Full process description text",
    "trigger_events": [
      "Event that initiates the process"
    ],
    "results": [
      "Expected outcome of the process"
    ],
    "process_steps": [
      "Step 1: Description",
      "Step 2: Description"
    ],
    "alternate_process_path": {
      "description": "Description of alternate flow",
      "reasons": [
        "Reason for alternate path"
      ]
    },
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
    "source_file": "BPT Vault v3.0/Care Management 3.0/CM_Establish_Case_BPT_v3.0.pdf",
    "extracted_date": "2025-12-05"
  }
}
```

### BPT-Specific Fields

**process_details.description** (string)
- Full text description of the process
- May contain multiple paragraphs
- Often includes notes and additional context

**process_details.trigger_events** (array of strings)
- Events that initiate the process
- Typically 1-10 trigger events
- Examples:
  - "Member requests case management services"
  - "Provider identifies member needing care coordination"

**process_details.results** (array of strings)
- Expected outcomes when process completes
- Typically 2-10 results
- Examples:
  - "Case established in system"
  - "Member assigned to case manager"

**process_details.process_steps** (array of strings)
- Ordered list of process steps
- Typically 5-20 steps
- Often numbered in the text (e.g., "1. Receive request")

**process_details.alternate_process_path** (object, optional)
- Describes alternate flows or exception handling
- Contains:
  - **description**: Text describing the alternate path
  - **reasons**: Array of reasons for taking alternate path

**process_details.shared_data** (array of strings)
- Data sources, stores, or systems used
- Examples:
  - "Member Information"
  - "Provider Directory"
  - "Case Management System"

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
  - "Time to establish case = within 5 business days"
  - "Percentage of cases established accurately"

### Optional BPT Fields

Some BPT files may include additional fields:

**process_details.provider_enrollment_variations** (array, optional)
- Only present in some enrollment-related processes
- Contains variations for different provider types
- Structure:
  ```json
  {
    "type": "Provider Type",
    "description": "Variation description",
    "information": "Required information fields"
  }
  ```

## BCM Schema

Business Capability Model files contain maturity assessment questions.

### Complete BCM Structure

```json
{
  "document_type": "BCM",
  "version": "3.0",
  "date": "February 2012",
  "business_area": "Care Management",
  "process_name": "Establish Case",
  "process_code": "CM",
  "sub_category": "Case Management",
  "page_count": 6,
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
        }
      }
    ]
  },
  "metadata": {
    "source_file": "BCM Vault v3.0/Care Management 3.0/CM_Establish_Case_BCM_v3.0.pdf",
    "extracted_date": "2025-12-05"
  }
}
```

### BCM-Specific Fields

**maturity_model.capability_questions** (array)
- Array of capability assessment questions
- Typically 4-15 questions per file
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

### Maturity Level Progression

Levels generally follow this pattern:

- **Level 1**: Manual, basic compliance, state-specific standards
- **Level 2**: Some automation, HIPAA standards, improved over Level 1
- **Level 3**: Significant automation, MITA Framework adoption, intrastate interoperability
- **Level 4**: Advanced automation, interstate interoperability
- **Level 5**: Optimized automation, national/international interoperability

## Process Codes

| Code | Business Area |
|------|---------------|
| BR | Business Relationship Management |
| CM | Care Management |
| CO | Contractor Management |
| EE | Eligibility and Enrollment Management |
| FM | Financial Management |
| MM | Member Management |
| OM | Operations Management |
| PE | Performance Management |
| PL | Plan Management |
| PM | Provider Management |

## Data Types

All JSON files use standard JSON data types:

- **string**: Text values
- **number**: Numeric values (page_count)
- **array**: Ordered lists
- **object**: Key-value structures
- **null**: Not used in current schema

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
