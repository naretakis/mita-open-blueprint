# Operations Management BCM Manual Construction Progress

## Status
- [x] Apply Mass Adjustment (pages 54-59) - 12 questions - RE-VERIFIED ✓
- [x] Calculate Spend-Down Amount (pages 38-46) - 15 questions - RE-VERIFIED ✓
- [x] Generate Remittance Advice (pages 1-6) - 10 questions - RE-VERIFIED ✓
- [x] Inquire Payment Status (pages 6-13) - 11 questions - RE-VERIFIED ✓
- [x] Manage Data (pages 18-24) - 10 questions - RE-VERIFIED ✓
- [x] Prepare Provider Payment (pages 13-18) - 10 questions - RE-VERIFIED ✓
- [x] Process Claim (pages 24-31) - 12 questions - RE-VERIFIED ✓
- [x] Process Encounter (pages 31-38) - 12 questions - RE-VERIFIED ✓
- [x] Submit Electronic Attachment (pages 46-54) - 13 questions - RE-VERIFIED ✓

## Reference
- Raw dump file: `tools/temp_om_bcm_dump.txt`
- Column thresholds: Q (0-155), L1 (155-261), L2 (261-371), L3 (371-487), L4 (487-597), L5 (597-800)

## Instructions for Verification
1. Read this file to see progress
2. Read `tools/temp_om_bcm_dump.txt` for the relevant page range
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