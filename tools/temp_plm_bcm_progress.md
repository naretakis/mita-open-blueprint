# Plan Management BCM Manual Construction Progress

## Status
- [x] Develop Agency Goals and Objectives (pages 1-8) - 12 questions - RE-VERIFIED ✓
- [x] Maintain Program Policy (pages 8-14) - 12 questions - RE-VERIFIED ✓
- [x] Maintain Reference Information (pages 40-46) - 10 questions - RE-VERIFIED ✓
- [x] Maintain State Plan (pages 14-21) - 12 questions - RE-VERIFIED ✓
- [x] Manage Health Benefit Information (pages 34-40) - 11 questions - RE-VERIFIED ✓
- [x] Manage Health Plan Information (pages 21-27) - 10 questions - RE-VERIFIED ✓
- [x] Manage Performance Measures (pages 27-34) - 12 questions - RE-VERIFIED ✓
- [x] Manage Rate Setting (pages 46-51) - 10 questions - RE-VERIFIED ✓

## Reference
- Raw dump file: `tools/temp_plm_bcm_dump.txt`
- Column thresholds: Q (0-155), L1 (155-261), L2 (261-371), L3 (371-487), L4 (487-597), L5 (597-800)

## Instructions for Verification
1. Read this file to see progress
2. Read `tools/temp_plm_bcm_dump.txt` for the relevant page range
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