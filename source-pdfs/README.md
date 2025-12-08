# MITA Source PDFs

This directory contains the original CMS MITA v3.0 PDF documents that were converted to JSON format.

## Attribution

**Source**: Centers for Medicare & Medicaid Services (CMS)  
**Framework**: Medicaid Information Technology Architecture (MITA)  
**Version**: 3.0  
**Publication Date**: February 2012  
**Official Website**: https://www.medicaid.gov/medicaid/data-systems/mita/index.html

## Disclaimer

These PDF documents are works of the U.S. Government and are in the public domain. They are provided here for reference and verification purposes.

**Important**: This repository is not affiliated with or endorsed by CMS. For the most current and authoritative MITA documentation, please visit the [official CMS MITA website](https://www.medicaid.gov/medicaid/data-systems/mita/index.html).

## Structure

```
source-pdfs/
├── bcm/  - Business Capability Model PDFs
│   ├── business_relationship_management/
│   ├── care_management/
│   ├── contractor_management/
│   ├── eligibility_and_enrollment_management/
│   ├── financial_management/
│   ├── operations_management/
│   ├── performance_management/
│   ├── plan_management/
│   └── provider_management/
└── bpt/  - Business Process Template PDFs
    ├── business_relationship_management/
    ├── care_management/
    ├── contractor_management/
    ├── eligibility_and_enrollment_management/
    ├── financial_management/
    ├── operations_management/
    ├── performance_management/
    ├── plan_management/
    └── provider_management/
```

## Purpose

These source PDFs serve multiple purposes:

1. **Verification**: Validate the accuracy of JSON conversions
2. **Reference**: Consult original formatting and context
3. **Historical Record**: Preserve the original source material
4. **Transparency**: Allow users to verify conversion accuracy

## Using Source PDFs

### Verify a Conversion

To verify a JSON file against its source PDF:

1. Locate the JSON file in `data/[bcm|bpt]/[business_area]/`
2. Find the corresponding PDF in `source-pdfs/[bcm|bpt]/[business_area]/`
3. Compare the JSON content against the PDF content
4. Report any discrepancies via [GitHub Issues](../../issues)

### Report Data Quality Issues

If you find differences between the JSON and source PDF:

1. Note the specific page number(s) in the PDF
2. Quote the relevant text from the PDF
3. Reference the JSON file path
4. Create a "Data Quality Issue" in GitHub Issues

## File Correspondence

Each JSON file in `data/` has a corresponding PDF in `source-pdfs/`:

| JSON File | Source PDF |
|-----------|------------|
| `data/bcm/care_management/CM_Establish_Case_BCM_v3.0.json` | `source-pdfs/bcm/care_management/CM_Establish_Case_BCM_v3.0.pdf` |
| `data/bpt/care_management/CM_Establish_Case_BPT_v3.0.json` | `source-pdfs/bpt/care_management/CM_Establish_Case_BPT_v3.0.pdf` |

## MITA Framework Overview

The MITA Framework provides:

- **Business Architecture**: Business processes and capabilities
- **Information Architecture**: Data and information flows
- **Technical Architecture**: Technology standards and infrastructure
- **Maturity Model**: 5-level capability maturity assessment

This repository focuses on the **Business Architecture** components (BCM and BPT).

## Additional MITA Resources

- **MITA Framework Overview**: https://www.medicaid.gov/medicaid/data-systems/mita/mita-30/index.html
- **MITA State Self-Assessment**: https://www.medicaid.gov/medicaid/data-systems/mita/mita-state-self-assessment/index.html
- **MITA 3.0 Toolkit**: Available from CMS

## Copyright & License

**Original MITA Documents**: Public domain as works of the U.S. Government

**No Copyright Restrictions**: These documents may be freely reproduced, distributed, and used without permission.

**Citation Recommended**: When using these documents, please cite:
> Centers for Medicare & Medicaid Services. (2012). Medicaid Information Technology Architecture (MITA) Framework, Version 3.0. Retrieved from https://www.medicaid.gov/medicaid/data-systems/mita/index.html

## Version History

### MITA v3.0 (February 2012)
- Current version in this repository
- 144 BCM and BPT documents
- 10 business areas covered

### Future Versions

When CMS releases new MITA versions, they will be added to this repository with appropriate version directories.

## Questions?

For questions about:
- **MITA Framework**: Contact CMS or visit the official MITA website
- **This Repository**: Open a [GitHub Issue](../../issues) or [Discussion](../../discussions)
- **JSON Conversions**: See [../docs/CONVERSION_METHODOLOGY.md](../docs/CONVERSION_METHODOLOGY.md)

---

**Last Updated**: December 2025  
**MITA Version**: 3.0  
**Document Count**: 144 PDFs (72 BCM + 72 BPT)
