# Contractor Management BCM Manual Construction Progress

## Status
- [x] Award Contract (pages 45-54) - 12 questions - VERIFIED ✓ (7 process name removals + category fix)
- [x] Close Out Contract (pages 62-68) - 12 questions - VERIFIED ✓ (4 process name removals + category fix)
- [x] Inquire Contractor Information (pages 7-13) - 12 questions - VERIFIED ✓ (6 process name removals + category fix)
- [x] Manage Contract (pages 54-62) - 12 questions - VERIFIED ✓ (8 process name removals + category fix)
- [x] Manage Contractor Communication (pages 13-20) - 11 questions - VERIFIED ✓ (7 process name removals + category fix)
- [x] Manage Contractor Grievance and Appeal (pages 28-36) - 12 questions - VERIFIED ✓ (8 process name removals + category fix)
- [x] Manage Contractor Information (pages 1-7) - 11 questions - VERIFIED ✓ (5 process name removals + category fix)
- [x] Perform Contractor Outreach (pages 20-28) - 11 questions - VERIFIED ✓ (5 process name removals + category fix + cleaned merged question)
- [x] Produce Solicitation (pages 36-45) - 12 questions - VERIFIED ✓ (8 process name removals + category fix)

## Reference
- Raw dump file: `tools/temp_ctm_bcm_dump.txt`
- Column thresholds: Q (0-155), L1 (155-261), L2 (261-371), L3 (371-487), L4 (487-597), L5 (597-800)

## Instructions for Verification
1. Read this file to see progress
2. Read `tools/temp_ctm_bcm_dump.txt` for the relevant page range
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