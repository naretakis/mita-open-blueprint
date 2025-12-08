# Medicaid MITA Data - A BCM & BPT Data Repository

A comprehensive, machine-readable dataset of CMS MITA (Medicaid Information Technology Architecture) Business Process Templates (BPT) and Business Capability Models (BCM) in JSON format.

## Overview

This repository contains all 144 MITA v3.0 documents converted from PDF to structured JSON format:
- **72 BPT files** - Business Process Templates with detailed process steps and workflows
- **72 BCM files** - Business Capability Maturity models with 5-level maturity assessments

The data covers all 10 MITA business areas:
- Business Relationship Management
- Care Management
- Contractor Management
- Eligibility and Enrollment Management
- Financial Management
- Member Management
- Operations Management
- Performance Management
- Plan Management
- Provider Management

## Quick Start

### Use Data Directly from GitHub (Recommended)

You can fetch JSON files directly from GitHub without cloning the repository:

```python
import json
import urllib.request

# Base URL for raw GitHub content
BASE_URL = "https://raw.githubusercontent.com/YOUR-USERNAME/YOUR-REPO-NAME/main/data"

# Load a BCM file directly from GitHub
bcm_url = f"{BASE_URL}/bcm/care_management/CM_Establish_Case_BCM_v3.0.json"
with urllib.request.urlopen(bcm_url) as response:
    bcm = json.loads(response.read())

# Access maturity questions
for question in bcm['maturity_model']['capability_questions']:
    print(f"Question: {question['question']}")
    print(f"Level 1: {question['levels']['level_1']}")
```

```javascript
// JavaScript/Node.js example
const BASE_URL = "https://raw.githubusercontent.com/YOUR-USERNAME/YOUR-REPO-NAME/main/data";

// Load a BPT file directly from GitHub
const bptUrl = `${BASE_URL}/bpt/care_management/CM_Establish_Case_BPT_v3.0.json`;
const response = await fetch(bptUrl);
const bpt = await response.json();

// Access process steps
bpt.process_details.process_steps.forEach(step => {
    console.log(`Step: ${step}`);
});
```

### Browse the Data

All JSON files are organized in the `data/` directory:
```
data/
├── bcm/  - Business Capability Models
│   ├── business_relationship_management/
│   ├── care_management/
│   ├── contractor_management/
│   └── ...
└── bpt/  - Business Process Templates
    ├── business_relationship_management/
    ├── care_management/
    ├── contractor_management/
    └── ...
```

### Clone for Local Development (Optional)

If you prefer to work with local files:

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
cd YOUR-REPO-NAME
```

```python
import json

# Load from local file
with open('data/bcm/care_management/CM_Establish_Case_BCM_v3.0.json') as f:
    bcm = json.load(f)
```

## Use Cases

This dataset enables:

- **Maturity Assessment Tools** - Build applications that help state Medicaid agencies assess their MITA maturity levels
- **Process Documentation** - Generate human-readable process documentation from structured data
- **Workflow Automation** - Map MITA processes to automated workflows in your systems
- **Compliance Tracking** - Track implementation of MITA processes and capabilities
- **Research & Analysis** - Analyze patterns across Medicaid business processes
- **Training Materials** - Create interactive training tools for Medicaid staff
- **System Design** - Use as reference architecture for Medicaid system implementations

## Data Structure


### BPT (Business Process Template) Format

BPT files contain detailed process information:

```json
{
  "document_type": "BPT",
  "version": "3.0",
  "business_area": "Care Management",
  "process_name": "Establish Case",
  "process_details": {
    "description": "Full process description",
    "trigger_events": ["Event 1", "Event 2"],
    "results": ["Result 1", "Result 2"],
    "process_steps": ["Step 1", "Step 2"],
    "predecessor_processes": ["Prior Process"],
    "successor_processes": ["Next Process"],
    "shared_data": ["Data Source 1"],
    "constraints": "Process constraints",
    "failures": ["Failure condition 1"],
    "performance_measures": ["Measure 1"]
  }
}
```

### BCM (Business Capability Model) Format

BCM files contain maturity assessment questions with 5 levels of capability:

```json
{
  "document_type": "BCM",
  "version": "3.0",
  "business_area": "Care Management",
  "process_name": "Establish Case",
  "maturity_model": {
    "capability_questions": [
      {
        "category": "Business Capability Descriptions",
        "question": "Question text?",
        "levels": {
          "level_1": "Basic capability description",
          "level_2": "Improved capability description",
          "level_3": "Enhanced capability description",
          "level_4": "Advanced capability description",
          "level_5": "Optimized capability description"
        }
      }
    ]
  }
}
```

See [docs/DATA_STRUCTURE.md](docs/DATA_STRUCTURE.md) for complete schema documentation.

## Documentation

- **[Data Structure Guide](docs/DATA_STRUCTURE.md)** - Complete field definitions and schemas
- **[Conversion Methodology](docs/CONVERSION_METHODOLOGY.md)** - How PDFs were converted to JSON
- **[Usage Examples](docs/EXAMPLES.md)** - Common queries and usage patterns
- **[Source PDFs](source-pdfs/)** - Original CMS MITA PDF documents

## Validation

All JSON files have been validated for:
- Structural correctness
- Content completeness
- Accuracy against source PDFs

To validate the data yourself:

```bash
cd tools
python comprehensive_validation.py
```

See [tools/README.md](tools/README.md) for more information.

## Statistics

- **Total Files**: 144 (72 BCM + 72 BPT)
- **BCM Questions**: 729 capability questions
- **BCM Maturity Levels**: 3,645 level descriptions
- **BPT Process Steps**: 693 documented steps
- **Business Areas**: 10 complete domains

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:
- How to report data quality issues
- Guidelines for submitting corrections
- Process for adding new MITA versions

## Attribution & Disclaimer

This dataset is derived from the **CMS Medicaid Information Technology Architecture (MITA) Framework Version 3.0**, published by the Centers for Medicare & Medicaid Services (CMS).

**Original Source**: [CMS MITA Initiative](https://www.medicaid.gov/medicaid/data-systems/mita/index.html)

**Disclaimer**: This is an unofficial conversion of CMS MITA documents to JSON format. While every effort has been made to ensure accuracy, users should refer to the [official CMS MITA documentation](https://www.medicaid.gov/medicaid/data-systems/mita/index.html) for authoritative information. This repository is not affiliated with or endorsed by CMS.

The original MITA documents are in the public domain as works of the U.S. Government. The JSON conversion and repository structure are provided under the GNU General Public License v3.0.

## Future Enhancements

Potential additions we're considering:
- API-style documentation with detailed field descriptions
- Additional code examples in multiple languages
- Cross-reference mapping between related processes
- MITA version comparison tools

Suggestions welcome via [GitHub Issues](../../issues)!

## License

- **Original MITA Content**: Public domain (U.S. Government work)
- **JSON Conversion & Repository**: GNU General Public License v3.0

See [LICENSE](LICENSE) for full license text.

## Changelog

### Version 1.0.0 (December 2025)
- Initial release with all MITA v3.0 BCM and BPT documents
- 144 files converted and validated
- Complete documentation and validation tools

## Contact & Support

- **Issues**: Report bugs or data quality issues via [GitHub Issues](../../issues)
- **Discussions**: Ask questions or share ideas in [GitHub Discussions](../../discussions)
- **Pull Requests**: Submit corrections or enhancements via [Pull Requests](../../pulls)

---

**Last Updated**: December 2025  
**MITA Version**: 3.0 (February 2012)
