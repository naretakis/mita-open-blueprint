# MITA Data Directory

This directory contains all MITA v3.0 documents converted to JSON format.

## Structure

```
data/
├── bcm/  - Business Capability Models (72 files)
│   ├── business_relationship_management/  (4 files)
│   ├── care_management/                   (9 files)
│   ├── contractor_management/             (9 files)
│   ├── eligibility_and_enrollment_management/ (4 files)
│   ├── financial_management/              (19 files)
│   ├── member_management/                 (0 files - not in source)
│   ├── operations_management/             (9 files)
│   ├── performance_management/            (5 files)
│   ├── plan_management/                   (8 files)
│   └── provider_management/               (5 files)
└── bpt/  - Business Process Templates (72 files)
    ├── business_relationship_management/  (4 files)
    ├── care_management/                   (9 files)
    ├── contractor_management/             (9 files)
    ├── eligibility_and_enrollment_management/ (4 files)
    ├── financial_management/              (19 files)
    ├── member_management/                 (0 files - not in source)
    ├── operations_management/             (9 files)
    ├── performance_management/            (5 files)
    ├── plan_management/                   (8 files)
    └── provider_management/               (5 files)
```

## File Naming Convention

Files follow the original CMS naming convention:

- **Format**: `[ProcessCode]_[Process_Name]_[BCM|BPT]_v3.0.json`
- **Example**: `CM_Establish_Case_BCM_v3.0.json`

### Process Codes

- **BR** - Business Relationship Management
- **CM** - Care Management
- **CO** - Contractor Management
- **EE** - Eligibility and Enrollment Management
- **FM** - Financial Management
- **MM** - Member Management
- **OM** - Operations Management
- **PE** - Performance Management
- **PL** - Plan Management
- **PM** - Provider Management

## Business Areas

### Business Relationship Management (4 BCM + 4 BPT)
Processes for establishing and managing relationships with business partners, trading partners, and other agencies.

### Care Management (9 BCM + 9 BPT)
Processes for case management, treatment authorization, population health, and care coordination.

### Contractor Management (9 BCM + 9 BPT)
Processes for managing contracts with vendors, MCOs, and other contractors.

### Eligibility and Enrollment Management (4 BCM + 4 BPT)
Processes for determining and managing provider eligibility and enrollment.

### Financial Management (19 BCM + 19 BPT)
Processes for budgeting, payments, claims processing, accounting, and financial reporting.

### Member Management (0 BCM + 0 BPT)
Note: Member Management processes were not included in the source MITA v3.0 vault.

### Operations Management (9 BCM + 9 BPT)
Processes for claims processing, encounters, payments, and operational data management.

### Performance Management (5 BCM + 5 BPT)
Processes for compliance monitoring, fraud detection, and performance reporting.

### Plan Management (8 BCM + 8 BPT)
Processes for managing state plans, policies, benefits, and rates.

### Provider Management (5 BCM + 5 BPT)
Processes for provider communication, grievances, outreach, and information management.

## Data Quality

All files have been:
- ✓ Validated for structural correctness
- ✓ Verified against source PDFs
- ✓ Checked for completeness
- ✓ Tested with validation scripts

See [../tools/README.md](../tools/README.md) for validation details.

## Usage

### Load All Files in a Business Area

```python
import json
import os
from pathlib import Path

def load_business_area(area_name, doc_type='bcm'):
    """Load all BCM or BPT files for a business area."""
    area_path = Path(f'data/{doc_type}/{area_name}')
    files = {}
    
    for json_file in area_path.glob('*.json'):
        with open(json_file) as f:
            files[json_file.stem] = json.load(f)
    
    return files

# Example: Load all Care Management BCMs
care_bcms = load_business_area('care_management', 'bcm')
print(f"Loaded {len(care_bcms)} Care Management BCM files")
```

### Find Files by Process Code

```python
import json
from pathlib import Path

def find_by_process_code(process_code, doc_type='bcm'):
    """Find all files matching a process code."""
    data_path = Path(f'data/{doc_type}')
    matching_files = []
    
    for json_file in data_path.rglob(f'{process_code}_*.json'):
        with open(json_file) as f:
            matching_files.append({
                'path': str(json_file),
                'data': json.load(f)
            })
    
    return matching_files

# Example: Find all Care Management (CM) processes
cm_processes = find_by_process_code('CM', 'bcm')
for process in cm_processes:
    print(process['data']['process_name'])
```

### Compare BCM and BPT for Same Process

```python
import json

def compare_bcm_bpt(process_file_name):
    """Load both BCM and BPT for the same process."""
    # Remove _BCM or _BPT suffix to get base name
    base_name = process_file_name.replace('_BCM_v3.0', '').replace('_BPT_v3.0', '')
    
    # Determine business area from file structure
    # This is simplified - you'd need to search for the actual file
    with open(f'data/bcm/[area]/{base_name}_BCM_v3.0.json') as f:
        bcm = json.load(f)
    
    with open(f'data/bpt/[area]/{base_name}_BPT_v3.0.json') as f:
        bpt = json.load(f)
    
    return {
        'bcm': bcm,
        'bpt': bpt,
        'process_name': bcm['process_name']
    }
```

## Statistics

- **Total Files**: 144
- **BCM Files**: 72
- **BPT Files**: 72
- **Business Areas**: 10 (9 with data)
- **Total Questions (BCM)**: 729
- **Total Maturity Levels (BCM)**: 3,645
- **Total Process Steps (BPT)**: 693

## Schema Reference

See [../docs/DATA_STRUCTURE.md](../docs/DATA_STRUCTURE.md) for complete schema documentation.

## Source Attribution

All data derived from CMS MITA Framework v3.0 (February 2012).

Original PDFs available in [../source-pdfs/](../source-pdfs/).
