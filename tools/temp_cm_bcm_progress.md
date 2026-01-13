# Care Management BCM Manual Construction Progress

## Status - RE-VERIFICATION (2026-01-13)
- [x] Establish Case (pages 1-7) - 10 questions - RE-VERIFIED ✓
- [x] Manage Case Information (pages 7-15) - 10 questions - RE-VERIFIED ✓
- [x] Manage Population Health Outreach (pages 15-21) - 10 questions - RE-VERIFIED ✓
- [x] Manage Registry (pages 21-26) - 10 questions - RE-VERIFIED ✓
- [x] Perform Screening and Assessment (pages 26-33) - 10 questions - RE-VERIFIED ✓
- [x] Manage Treatment Plans and Outcomes (pages 33-39) - 10 questions - RE-VERIFIED ✓
- [x] Authorize Referral (pages 39-45) - 11 questions - RE-VERIFIED ✓
- [x] Authorize Service (pages 45-53) - 11 questions - RE-VERIFIED ✓
- [x] Authorize Treatment Plan (pages 53-58) - 11 questions - RE-VERIFIED ✓

## Re-Verification Notes (2026-01-13)

### Cost Question Variations
The CM BCMs have intentional variations in the cost question wording that match the PDF:
- "What is the cost to perform the process compared to the benefits of the results?" (Establish Case, Manage Case Information, Manage Population Health Outreach, Manage Registry)
- "What is the cost of the process compared to the benefits of its results?" (Perform Screening and Assessment, Manage Treatment Plans and Outcomes, Authorize Referral)
- "What is the cost to support the process to the benefits of the result?" (Authorize Service, Authorize Treatment Plan)

These variations are correct per the source PDF - verified against dump file.

### All BCMs Verified
- All 9 BCMs have correct question counts
- All categories are correctly assigned
- All level content matches the dump
- No issues found during re-verification

## Validation
- All 9 BCMs passed validation: `.venv/bin/python3 tools/validate_2014.py`
- Re-verification completed: 2026-01-13

## Previous Verification (2026-01-12)
- Fixed process name appearing in level_2 content
- Fixed category for "How accurate are the results" questions

## Reference
- Raw dump file: `tools/temp_cm_bcm_dump.txt`
- Column thresholds: Q (0-155), L1 (155-261), L2 (261-371), L3 (371-487), L4 (487-597), L5 (597-800)
