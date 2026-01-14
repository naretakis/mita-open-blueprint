# Proposed JSON Schema for 2014 MITA Data

This document proposes schema updates for the May 2014 MITA conversion.

## Key Changes from 2012 Schema

1. **Trigger Events**: Now categorized as environment-based vs interaction-based
2. **Sub-Categories**: Added explicit sub_category field (e.g., "Case Management", "Authorization Determination")
3. **Diagrams**: New field for process flow diagram references (EE area only)
4. **Metadata**: Enhanced with source page range and version info
5. **Date**: Updated to "May 2014"

---

## BPT Schema (2014)

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
    "description": "Full process description text...",
    
    "trigger_events": {
      "environment_based": [
        "Periodic review to scan for new cases is due.",
        "Request to look into a specific case."
      ],
      "interaction_based": [
        "An alert triggered by other events...",
        "Receive enrollment of member from Enroll Member business process."
      ]
    },
    
    "results": [
      "List of members associated with cases and programs.",
      "Assessment of the needs of the member for care management."
    ],
    
    "process_steps": [
      "1. START: Identify candidates for new cases...",
      "2. Identify information requirements and parameters..."
    ],
    
    "diagrams": [
      {
        "filename": "EE_Determine_Member_Eligibility_flow.png",
        "description": "Process flow diagram for eligibility determination",
        "page_reference": 2
      }
    ],
    
    "shared_data": [
      "Member data store including demographics",
      "Health Information Exchange (HIE) data store..."
    ],
    
    "predecessor_processes": [
      "Receive Inbound Transaction",
      "Enroll Member"
    ],
    
    "successor_processes": [
      "Send Outbound Transaction",
      "Manage Case Information"
    ],
    
    "constraints": "States and programs within States use different criteria...",
    
    "failures": [
      "Details of the case are inconsistent with criteria; discontinued case."
    ],
    
    "performance_measures": [
      "Time required to establish a case.",
      "Effectiveness of selection criteria in determining real cases."
    ]
  },
  
  "metadata": {
    "source_file": "source-pdfs/may-2014-update/bpt/Care Management/Care Management BPT.pdf",
    "source_page_range": "18-21",
    "extracted_date": "2026-01-12"
  }
}
```

---

## BCM Schema (2014)

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
          "level_1": "The process consists primarily of manual activity...",
          "level_2": "SMA uses a mix of manual and automatic processes...",
          "level_3": "SMA automates process to the full extent possible within the intrastate...",
          "level_4": "SMA automates process to the full extent possible within the region...",
          "level_5": "SMA automates process to the full extent possible nationally..."
        }
      }
    ]
  },
  
  "metadata": {
    "source_file": "source-pdfs/may-2014-update/bcm/Care Management/Care Management BCM.pdf",
    "source_page_range": "41-47",
    "extracted_date": "2026-01-12"
  }
}
```

---

## Schema Changes Summary

| Field | 2012 | 2014 | Notes |
|-------|------|------|-------|
| `version_date` | `date: "February 2012"` | `version_date: "May 2014"` | Renamed for clarity |
| `sub_category` | Existed but inconsistent | Required field | e.g., "Case Management", "Authorization Determination" |
| `trigger_events` | Flat array | Object with `environment_based` and `interaction_based` arrays | Breaking change |
| `diagrams` | N/A | Array of diagram objects | New field, optional |
| `metadata.source_page_range` | N/A | String like "18-21" | New field |

---

## Directory Structure

```
data/
├── bcm/
│   ├── business_relationship_management/
│   │   └── BR_*.json
│   ├── care_management/
│   │   └── CM_*.json
│   └── ...
├── bpt/
│   ├── eligibility_and_enrollment_management/
│   │   ├── EE_*.json
│   │   └── images/
│   │       └── EE_Determine_Member_Eligibility_flow.png
│   └── ...
```

---

## Resolved Questions

1. **Diagrams at process level**: Yes, keep at process level. Each process may have 0-N diagrams.
2. **Image naming**: `[CODE]_[Process_Name]_[type].png` (e.g., `EE_Determine_Member_Eligibility_flow.png`)
3. **Image dimensions**: Not stored in JSON (not useful for consumers)

---

## Text Formatting Preservation

### Challenge
PDF extraction loses formatting context:
- Bullet points (`\uf0b7`) appear on separate lines from content
- Multi-line paragraphs get split
- Numbered lists need to be rejoined

### Solution
The extraction tool will:

1. **Detect bullet characters** (`\uf0b7`, `\uf0fc`, `•`) and join with following content
2. **Preserve numbered lists** (1., 2., etc.) with their content
3. **Join wrapped lines** within the same logical paragraph
4. **Output clean arrays** with proper bullet formatting:

```json
"results": [
  "• List of members associated with cases and programs.",
  "• Assessment of the needs of the member for care management.",
  "• Treatment Plan for member."
]
```

```json
"process_steps": [
  "1. START: Identify candidates for new cases with specific criteria.",
  "2. Identify information requirements and parameters.",
  "3. Identify new case(s) for care management based on requirements."
]
```

### Field-Specific Handling

| Field | Format | Notes |
|-------|--------|-------|
| `description` | Single string | Paragraphs joined, line breaks as `\n` |
| `trigger_events.*` | Array of strings | Each item prefixed with `•` |
| `results` | Array of strings | Each item prefixed with `•` |
| `process_steps` | Array of strings | Each item prefixed with step number |
| `shared_data` | Array of strings | Each item is a data store name |
| `predecessor_processes` | Array of strings | Process names only |
| `successor_processes` | Array of strings | Process names only |
| `constraints` | Single string | May contain multiple paragraphs |
| `failures` | Array of strings | Each item prefixed with `•` |
| `performance_measures` | Array of strings | Each item prefixed with `•` |
