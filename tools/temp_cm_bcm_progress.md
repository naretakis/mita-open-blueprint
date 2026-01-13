# Care Management BCM Manual Construction Progress

## Status
- [x] Establish Case (pages 1-7) - 10 questions - VERIFIED ✓
  - Fixed 5 issues: removed "Establish Case" from Q3 L2, Q5 L2, Q6 L2, Q8 L2, Q10 L2
  - Fixed category for Q9 from "Data Access and Accuracy" to "Accuracy of Process Results"
- [x] Manage Case Information (pages 7-15) - 10 questions - VERIFIED ✓
  - Fixed 4 issues: removed "Manage Case Information" from Q1 L2, Q4 L2, Q5 L2, Q7 L2
  - Fixed category for Q9 from "Data Access and Accuracy" to "Accuracy of Process Results"
- [x] Manage Population Health Outreach (pages 15-21) - 10 questions - VERIFIED ✓
  - Fixed 5 issues: removed "Manage Population Health Outreach" from Q2 L2, Q4 L2, Q5 L2, Q7 L2, Q8 L2
  - Fixed category for Q9 from "Data Access and Accuracy" to "Accuracy of Process Results"
- [x] Manage Registry (pages 21-26) - 10 questions - VERIFIED ✓
  - Fixed 5 issues: removed "Manage Registry" from Q3 L2, Q5 L2, Q6 L2, Q8 L2, Q10 L2
  - Fixed category for Q9 from "Data Access and Accuracy" to "Accuracy of Process Results"
- [x] Perform Screening and Assessment (pages 26-33) - 10 questions - VERIFIED ✓
  - Fixed 4 issues: removed "Perform Screening and Assessment" from Q1 L2, Q6 L2, Q7 L2, Q9 L2
  - Fixed category for Q9 from "Data Access and Accuracy" to "Accuracy of Process Results"
- [x] Manage Treatment Plans and Outcomes (pages 33-39) - 10 questions - VERIFIED ✓
  - Fixed 4 issues: removed "Manage Treatment Plans and Outcomes" from Q4 L2, Q5 L2, Q7 L2, Q10 L2
  - Fixed category for Q9 from "Data Access and Accuracy" to "Accuracy of Process Results"
- [x] Authorize Referral (pages 39-45) - 11 questions - VERIFIED ✓
  - Fixed 2 issues: removed "Authorize Referral" from Q1 L2, Q5 L2
  - Fixed category for Q10 from "Data Access and Accuracy" to "Accuracy of Process Results"
- [x] Authorize Service (pages 45-53) - 11 questions - VERIFIED ✓
  - Fixed 2 issues: removed "Authorize Service" from Q6 L2, Q9 L2
  - Fixed category for Q10 from "Data Access and Accuracy" to "Accuracy of Process Results"
- [x] Authorize Treatment Plan (pages 53-58) - 11 questions - VERIFIED ✓
  - Fixed 4 issues: removed "Authorize Treatment Plan" from Q5 L2, Q6 L2, Q8 L2, Q10 L2
  - Fixed category for Q10 from "Data Access and Accuracy" to "Accuracy of Process Results"

## Validation
- All 9 BCMs passed validation: `.venv/bin/python3 tools/validate_2014.py --area care_management`
- Completed: 2026-01-12

## Reference
- Raw dump file: `tools/temp_cm_bcm_dump.txt`
- Column thresholds: Q (0-155), L1 (155-261), L2 (261-371), L3 (371-487), L4 (487-597), L5 (597-800)

## Instructions for Verification
1. Read this file to see progress
2. Read `tools/temp_cm_bcm_dump.txt` for the relevant page range
3. Compare the dump to the JSON file - verify:
   - All questions are present (not merged)
   - Categories are correctly assigned
   - Level content is complete and accurate
4. Fix any issues by editing the JSON file
5. Mark as verified in this file

## Expected Categories
Each BCM should have questions in these categories:
- Business Capability Descriptions (varies by process)
- Business Capability Quality: Timeliness of Process
- Business Capability Quality: Data Access and Accuracy
- Business Capability Quality: Cost Effectiveness
- Business Capability Quality: Effort to Perform; Efficiency
- Business Capability Quality: Utility or Value to Stakeholders
- (Some also have: Business Capability Quality: Accuracy of Process Results)

## Common Issues Found in Financial Management
- Questions merged together that should be separate
- Missing quality category questions (extraction stopped early)
- Wrong category assignments (e.g., Data Access question labeled as Timeliness)
- Process name appearing in level text (extraction artifact)