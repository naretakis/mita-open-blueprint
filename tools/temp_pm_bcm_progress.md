# Performance Management BCM Manual Construction Progress

## Status
- [x] Determine Adverse Action Incident (pages 21-29) - 11 questions - RE-VERIFIED ✓
- [x] Establish Compliance Incident (pages 7-14) - 11 questions - RE-VERIFIED ✓
- [x] Identify Utilization Anomalies (pages 1-7) - 11 questions - RE-VERIFIED ✓
- [x] Manage Compliance Incident Information (pages 14-21) - 11 questions - RE-VERIFIED ✓
- [x] Prepare REOMB (pages 29-35) - 10 questions - RE-VERIFIED ✓

## Reference
- Raw dump file: `tools/temp_pm_bcm_dump.txt`
- Column thresholds: Q (0-155), L1 (155-261), L2 (261-371), L3 (371-487), L4 (487-597), L5 (597-800)

## Instructions for Verification
1. Read this file to see progress
2. Read `tools/temp_pm_bcm_dump.txt` for the relevant page range
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