# Care Management BPT Manual Verification Progress

## Status
- [x] Establish Case - VERIFIED
- [x] Manage Case Information - VERIFIED
- [x] Manage Population Health Outreach - VERIFIED (fixed truncated step 4)
- [x] Manage Registry - VERIFIED
- [x] Perform Screening and Assessment - VERIFIED
- [x] Manage Treatment Plans and Outcomes - VERIFIED (fixed garbage text in trigger event)
- [x] Authorize Referral - VERIFIED (fixed split result item)
- [x] Authorize Service - VERIFIED (fixed truncated step 15, garbage text in trigger)
- [x] Authorize Treatment Plan - VERIFIED (fixed truncated step 3)

## Reference
- Raw dump file: `tools/temp_cm_bpt_dump.txt`
- JSON files: `data/bpt/care_management/`

## Verification Checklist
For each BPT, verify:
1. Description - complete and accurate
2. Trigger Events - environment_based and interaction_based lists
3. Results - all bullet points captured
4. Process Steps - all numbered steps with sub-steps
5. Shared Data - all items listed
6. Predecessor Processes - all items listed
7. Successor Processes - all items listed
8. Constraints - complete text
9. Failures - all bullet points captured
10. Performance Measures - all items listed

## Verification Notes

### Establish Case
- All fields verified against PDF dump pages 1-4
- Complex description with nested bullet points verified
- 12 process steps verified

### Manage Case Information
- All fields verified against PDF dump pages 4-7
- 4 process steps with sub-steps verified

### Manage Population Health Outreach
- FIXED: Step 4 was truncated ("email, mail, publication," → "email, mail, publication, mobile device, facsimile, telephone, web or EDI)")
- All other fields verified against PDF dump pages 7-9

### Manage Registry
- All fields verified against PDF dump pages 9-10
- Includes alternate path for health outcome requests

### Perform Screening and Assessment
- All fields verified against PDF dump pages 10-12
- 9 process steps verified

### Manage Treatment Plans and Outcomes
- FIXED: First environment trigger had garbage text ("CM Case Management Manage Treatment Plan and Outcomes Item Details")
- All other fields verified against PDF dump pages 12-14
- Includes alternate path

### Authorize Referral
- FIXED: Last result item was split into two array elements
- All fields verified against PDF dump pages 14-18
- 19 process steps verified

### Authorize Service
- FIXED: Step 15 was truncated (missing "medically necessary. Go to step 13.")
- FIXED: Second environment trigger had garbage text
- All fields verified against PDF dump pages 18-21

### Authorize Treatment Plan
- FIXED: Step 3 was truncated (missing "required fields.")
- All fields verified against PDF dump pages 21-24
- 20 process steps verified
