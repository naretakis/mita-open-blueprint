#!/usr/bin/env python3
"""
Validation Script for MITA 2014 PDF to JSON Conversions

Validates all extracted JSON files against the 2014 schema and checks
for data quality issues.

Usage:
    .venv/bin/python3 tools/validate_2014.py
    .venv/bin/python3 tools/validate_2014.py --verbose
    .venv/bin/python3 tools/validate_2014.py --area "Care Management"
"""

import argparse
import json
import os
from collections import defaultdict
from datetime import datetime


# =============================================================================
# SCHEMA VALIDATION
# =============================================================================

def validate_bcm_schema(data, filepath):
    """Validate BCM file against 2014 schema."""
    issues = []
    warnings = []
    
    # Required top-level fields
    required = [
        "document_type", "version", "version_date", "business_area",
        "sub_category", "process_name", "process_code", "maturity_model", "metadata"
    ]
    
    for field in required:
        if field not in data:
            issues.append(f"Missing required field: {field}")
    
    # Validate document_type
    if data.get("document_type") != "BCM":
        issues.append(f"Invalid document_type: {data.get('document_type')}")
    
    # Validate version
    if data.get("version") != "3.0":
        warnings.append(f"Unexpected version: {data.get('version')}")
    
    # Validate maturity_model
    mm = data.get("maturity_model", {})
    if "capability_questions" not in mm:
        issues.append("Missing maturity_model.capability_questions")
    else:
        questions = mm["capability_questions"]
        if not questions:
            issues.append("No capability questions found")
        elif len(questions) < 5:
            warnings.append(f"Only {len(questions)} questions (expected 8-12)")
        
        # Validate each question
        for i, q in enumerate(questions):
            if "question" not in q:
                issues.append(f"Question {i+1}: Missing 'question' field")
            elif len(q["question"]) < 10:
                warnings.append(f"Question {i+1}: Very short question text")
            
            if "category" not in q:
                warnings.append(f"Question {i+1}: Missing 'category' field")
            
            if "levels" not in q:
                issues.append(f"Question {i+1}: Missing 'levels' field")
            else:
                levels = q["levels"]
                empty_count = 0
                for lvl in ["level_1", "level_2", "level_3", "level_4", "level_5"]:
                    if lvl not in levels:
                        issues.append(f"Question {i+1}: Missing {lvl}")
                    elif not levels[lvl]:
                        empty_count += 1
                
                if empty_count >= 3:
                    warnings.append(f"Question {i+1}: {empty_count} empty levels")
    
    # Validate metadata
    meta = data.get("metadata", {})
    if "source_file" not in meta:
        warnings.append("Missing metadata.source_file")
    if "source_page_range" not in meta:
        warnings.append("Missing metadata.source_page_range")
    if "extracted_date" not in meta:
        warnings.append("Missing metadata.extracted_date")
    
    return issues, warnings


def validate_bpt_schema(data, filepath):
    """Validate BPT file against 2014 schema."""
    issues = []
    warnings = []
    
    # Required top-level fields
    required = [
        "document_type", "version", "version_date", "business_area",
        "sub_category", "process_name", "process_code", "process_details", "metadata"
    ]
    
    for field in required:
        if field not in data:
            issues.append(f"Missing required field: {field}")
    
    # Validate document_type
    if data.get("document_type") != "BPT":
        issues.append(f"Invalid document_type: {data.get('document_type')}")
    
    # Validate process_details
    pd = data.get("process_details", {})
    
    # Description
    desc = pd.get("description", "")
    if not desc:
        issues.append("Empty description")
    elif len(desc) < 100:
        warnings.append(f"Very short description ({len(desc)} chars)")
    
    # Trigger events (2014 schema: object with environment_based and interaction_based)
    te = pd.get("trigger_events", {})
    if not isinstance(te, dict):
        issues.append("trigger_events should be an object")
    else:
        if "environment_based" not in te:
            warnings.append("Missing trigger_events.environment_based")
        if "interaction_based" not in te:
            warnings.append("Missing trigger_events.interaction_based")
        
        env_count = len(te.get("environment_based", []))
        int_count = len(te.get("interaction_based", []))
        if env_count == 0 and int_count == 0:
            warnings.append("No trigger events found")
    
    # Process steps
    steps = pd.get("process_steps", [])
    if not steps:
        issues.append("No process steps found")
    elif len(steps) < 3:
        warnings.append(f"Only {len(steps)} process steps")
    
    # Results
    results = pd.get("results", [])
    if not results:
        warnings.append("No results found")
    
    # Other arrays (optional but expected)
    for field in ["shared_data", "predecessor_processes", "successor_processes"]:
        if field not in pd:
            warnings.append(f"Missing {field}")
    
    # Constraints and failures
    if not pd.get("constraints"):
        warnings.append("Empty constraints")
    if not pd.get("failures"):
        warnings.append("No failures listed")
    
    # Diagrams (optional, mainly for EE area)
    # No validation needed - empty array is fine
    
    # Validate metadata
    meta = data.get("metadata", {})
    if "source_file" not in meta:
        warnings.append("Missing metadata.source_file")
    if "source_page_range" not in meta:
        warnings.append("Missing metadata.source_page_range")
    
    return issues, warnings


# =============================================================================
# CONTENT QUALITY CHECKS
# =============================================================================

def check_content_quality(data, doc_type):
    """Check for common content quality issues."""
    warnings = []
    
    # Check for page header artifacts in text
    artifacts = [
        "Part I", "Appendix C", "Appendix D", "Page ", "May 2014",
        "Version 3.0", "Model Details", "Matrix Details"
    ]
    
    def check_text(text, field_name):
        for artifact in artifacts:
            if artifact in text:
                warnings.append(f"{field_name} contains artifact: '{artifact}'")
                break
    
    if doc_type == "BPT":
        pd = data.get("process_details", {})
        
        # Check description
        check_text(pd.get("description", ""), "description")
        
        # Check process steps
        for i, step in enumerate(pd.get("process_steps", [])):
            if "Item" in step or "Details" in step:
                warnings.append(f"Process step {i+1} may contain artifacts")
                break
    
    elif doc_type == "BCM":
        mm = data.get("maturity_model", {})
        for i, q in enumerate(mm.get("capability_questions", [])):
            # Check for "Capability Question" prefix in question text
            if q.get("question", "").startswith("Capability Question"):
                warnings.append(f"Question {i+1} has 'Capability Question' prefix artifact")
                break
    
    return warnings


# =============================================================================
# MAIN VALIDATION
# =============================================================================

def validate_file(filepath, verbose=False):
    """Validate a single JSON file."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return ["Invalid JSON: " + str(e)], []
    except Exception as e:
        return ["Error reading file: " + str(e)], []
    
    doc_type = data.get("document_type", "UNKNOWN")
    
    if doc_type == "BCM":
        issues, warnings = validate_bcm_schema(data, filepath)
    elif doc_type == "BPT":
        issues, warnings = validate_bpt_schema(data, filepath)
    else:
        return [f"Unknown document_type: {doc_type}"], []
    
    # Content quality checks
    quality_warnings = check_content_quality(data, doc_type)
    warnings.extend(quality_warnings)
    
    return issues, warnings


def collect_statistics(data_dir):
    """Collect statistics about the extracted data."""
    stats = {
        'bpt': defaultdict(lambda: {'count': 0, 'steps': 0, 'triggers': 0}),
        'bcm': defaultdict(lambda: {'count': 0, 'questions': 0, 'levels_filled': 0}),
    }
    
    for doc_type in ['bpt', 'bcm']:
        type_dir = os.path.join(data_dir, doc_type)
        if not os.path.exists(type_dir):
            continue
        
        for area in os.listdir(type_dir):
            area_path = os.path.join(type_dir, area)
            if not os.path.isdir(area_path):
                continue
            
            for filename in os.listdir(area_path):
                if not filename.endswith('.json'):
                    continue
                
                filepath = os.path.join(area_path, filename)
                with open(filepath) as f:
                    data = json.load(f)
                
                business_area = data.get('business_area', area)
                
                if doc_type == 'bpt':
                    stats['bpt'][business_area]['count'] += 1
                    pd = data.get('process_details', {})
                    stats['bpt'][business_area]['steps'] += len(pd.get('process_steps', []))
                    te = pd.get('trigger_events', {})
                    stats['bpt'][business_area]['triggers'] += len(te.get('environment_based', []))
                    stats['bpt'][business_area]['triggers'] += len(te.get('interaction_based', []))
                else:
                    stats['bcm'][business_area]['count'] += 1
                    mm = data.get('maturity_model', {})
                    questions = mm.get('capability_questions', [])
                    stats['bcm'][business_area]['questions'] += len(questions)
                    for q in questions:
                        levels = q.get('levels', {})
                        filled = sum(1 for v in levels.values() if v)
                        stats['bcm'][business_area]['levels_filled'] += filled
    
    return stats


def main():
    parser = argparse.ArgumentParser(description='Validate MITA 2014 JSON extractions')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show all warnings')
    parser.add_argument('--area', type=str, help='Validate only specific business area')
    parser.add_argument('--type', type=str, choices=['bpt', 'bcm'], help='Validate only BPT or BCM')
    args = parser.parse_args()
    
    print("=" * 80)
    print("MITA 2014 EXTRACTION VALIDATION")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    data_dir = "data"
    
    # Collect all files to validate
    files_to_validate = []
    
    for doc_type in ['bpt', 'bcm']:
        if args.type and args.type != doc_type:
            continue
        
        type_dir = os.path.join(data_dir, doc_type)
        if not os.path.exists(type_dir):
            continue
        
        for area in os.listdir(type_dir):
            if args.area and args.area.lower().replace(' ', '_') != area:
                continue
            
            area_path = os.path.join(type_dir, area)
            if not os.path.isdir(area_path):
                continue
            
            for filename in os.listdir(area_path):
                if filename.endswith('.json'):
                    files_to_validate.append(os.path.join(area_path, filename))
    
    print(f"Found {len(files_to_validate)} files to validate\n")
    
    # Validate files
    results = {
        'passed': 0,
        'warnings': 0,
        'failed': 0,
    }
    
    issues_report = []
    warnings_report = []
    
    for filepath in sorted(files_to_validate):
        issues, warnings = validate_file(filepath, args.verbose)
        
        filename = os.path.basename(filepath)
        
        if issues:
            results['failed'] += 1
            issues_report.append((filename, issues, warnings))
            print(f"✗ {filename}")
            if args.verbose:
                for issue in issues:
                    print(f"    ERROR: {issue}")
        elif warnings:
            results['warnings'] += 1
            results['passed'] += 1
            warnings_report.append((filename, warnings))
            if args.verbose:
                print(f"⚠ {filename}")
                for warning in warnings:
                    print(f"    WARN: {warning}")
        else:
            results['passed'] += 1
            if args.verbose:
                print(f"✓ {filename}")
    
    # Print summary
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    print(f"Total files:     {len(files_to_validate)}")
    print(f"✓ Passed:        {results['passed']}")
    print(f"⚠ With warnings: {results['warnings']}")
    print(f"✗ Failed:        {results['failed']}")

    # Print statistics
    print("\n" + "=" * 80)
    print("EXTRACTION STATISTICS")
    print("=" * 80)
    
    stats = collect_statistics(data_dir)
    
    print("\nBPT Summary by Business Area:")
    print("-" * 60)
    total_bpt = 0
    total_steps = 0
    for area in sorted(stats['bpt'].keys()):
        s = stats['bpt'][area]
        avg_steps = s['steps'] / s['count'] if s['count'] > 0 else 0
        print(f"  {area}: {s['count']} processes, avg {avg_steps:.1f} steps")
        total_bpt += s['count']
        total_steps += s['steps']
    print(f"  TOTAL: {total_bpt} BPT files, {total_steps} total steps")
    
    print("\nBCM Summary by Business Area:")
    print("-" * 60)
    total_bcm = 0
    total_questions = 0
    for area in sorted(stats['bcm'].keys()):
        s = stats['bcm'][area]
        avg_q = s['questions'] / s['count'] if s['count'] > 0 else 0
        avg_levels = s['levels_filled'] / s['questions'] if s['questions'] > 0 else 0
        print(f"  {area}: {s['count']} processes, avg {avg_q:.1f} questions, avg {avg_levels:.1f}/5 levels filled")
        total_bcm += s['count']
        total_questions += s['questions']
    print(f"  TOTAL: {total_bcm} BCM files, {total_questions} total questions")
    
    # Report issues
    if issues_report:
        print("\n" + "=" * 80)
        print("FILES WITH ERRORS")
        print("=" * 80)
        for filename, issues, warnings in issues_report[:10]:
            print(f"\n{filename}:")
            for issue in issues:
                print(f"  ✗ {issue}")
        if len(issues_report) > 10:
            print(f"\n... and {len(issues_report) - 10} more files with errors")
    
    # Report warnings summary
    if warnings_report and not args.verbose:
        print("\n" + "=" * 80)
        print("FILES WITH WARNINGS (use --verbose to see details)")
        print("=" * 80)
        # Group warnings by type
        warning_types = defaultdict(int)
        for filename, warnings in warnings_report:
            for w in warnings:
                # Extract warning type
                warning_types[w.split(':')[0] if ':' in w else w] += 1
        
        print("\nWarning summary:")
        for wtype, count in sorted(warning_types.items(), key=lambda x: -x[1]):
            print(f"  {count}x {wtype}")
    
    # Final result
    print("\n" + "=" * 80)
    if results['failed'] == 0:
        print("✓ VALIDATION PASSED")
        if results['warnings'] > 0:
            print(f"  ({results['warnings']} files have warnings that may need review)")
        return 0
    else:
        print(f"✗ VALIDATION FAILED - {results['failed']} files have errors")
        return 1


if __name__ == "__main__":
    exit(main())
