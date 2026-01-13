#!/usr/bin/env python3
"""
MITA 2014 BPT (Business Process Table) PDF to JSON Extraction Tool

Extracts BPT data from the May 2014 MITA PDFs and converts to JSON format.

Usage:
    python tools/extract_bpt_2014.py --area "Care Management"
    python tools/extract_bpt_2014.py --area "Care Management" --with-images
    python tools/extract_bpt_2014.py --all
    python tools/extract_bpt_2014.py --all --force  # Overwrite existing files

Note: BCM extraction has been moved to extract_bcm_2014.py.archived
      The BCM JSON files were manually verified and should not be regenerated.
"""

import argparse
import fitz  # pymupdf
import json
import os
import re
from datetime import date
from pathlib import Path


# =============================================================================
# CONFIGURATION
# =============================================================================

SOURCE_BASE = "source-pdfs/may-2014-update"
OUTPUT_BASE = "data"

# Process codes by business area
AREA_CODES = {
    "Business Relationship Management": "BR",
    "Care Management": "CM",
    "Contractor Management": "CO",
    "Eligibility and Enrollment Management": "EE",
    "Financial Management": "FM",
    "Operations Management": "OM",
    "Performance Management": "PE",
    "Plan Management": "PL",
    "Provider Management": "PM",
}

# Bullet characters used in PDFs
BULLET_CHARS = ['\uf0b7', '\uf0fc', '•', '']

# Section headers for BPT
BPT_SECTIONS = [
    'Description',
    'Trigger Event',
    'Result',
    'Business Process Steps',
    'Shared Data',
    'Predecessor',
    'Successor',
    'Constraints',
    'Failures',
    'Performance Measures',
]


# =============================================================================
# TEXT CLEANING UTILITIES
# =============================================================================

def clean_text(text, preserve_indent=False):
    """Basic text cleaning - remove extra whitespace, normalize characters."""
    leading = ''
    if preserve_indent:
        match = re.match(r'^(\s*)', text)
        if match:
            leading = match.group(1)
    
    text = text.replace('\xa0', ' ')
    text = text.replace('‐', '-').replace('–', '-').replace('—', '-')
    text = text.replace('\uf0fc', '✓')
    text = re.sub(r' +', ' ', text)
    text = text.strip()
    
    if preserve_indent and leading:
        text = leading + text
    
    return text


def is_page_header(line):
    """Check if a line is a page header/footer to skip."""
    line_clean = line.replace('\xa0', ' ').replace('‐', '-').replace('–', '-').lower()
    
    skip_patterns = [
        'part i', 'part 1', 'appendix c', 'appendix d', 
        'may 2014', 'version 3.0', 'matrix details', 'model details'
    ]
    
    if re.search(r'page\s*\d+', line_clean):
        return True
    
    if 'business architecture' in line_clean and 'appendix' in line_clean:
        return True
    
    return any(pat in line_clean for pat in skip_patterns)


def clean_extracted_text(text, preserve_indent=False):
    """Remove any remaining page header artifacts from extracted text."""
    leading = ''
    if preserve_indent:
        match = re.match(r'^(\s*)', text)
        if match:
            leading = match.group(1)
    
    text = text.replace('‐', '-').replace('–', '-').replace('—', '-')
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    patterns = [
        r'Part I\s*-?\s*Business Architecture.*?Details',
        r'Part I,?\s*Appendix [CD]\s*-?\s*Page\s*\d+',
        r'May 2014\s*Version 3\.0',
        r'[A-Z]{2}\s+[A-Za-z\s]+\s+Item\s+Details',
    ]
    for pat in patterns:
        text = re.sub(pat, '', text, flags=re.IGNORECASE)
    
    result = clean_text(text, preserve_indent=preserve_indent)
    
    if preserve_indent and leading and not result.startswith(leading):
        result = leading + result.lstrip()
    
    return result


def join_wrapped_lines(lines, stop_patterns=None):
    """Join lines that were wrapped in the PDF."""
    if stop_patterns is None:
        stop_patterns = []
    
    result = []
    current = ""
    
    for line in lines:
        line = line.strip()
        
        if any(pat in line for pat in stop_patterns):
            if current:
                result.append(clean_text(current))
                current = ""
            break
        
        if not line:
            if current:
                result.append(clean_text(current))
                current = ""
            continue
        
        if current:
            current += " " + line
        else:
            current = line
    
    if current:
        result.append(clean_text(current))
    
    return result


def extract_bulleted_list(lines, stop_patterns=None):
    """Extract a bulleted list from lines."""
    if stop_patterns is None:
        stop_patterns = BPT_SECTIONS
    
    items = []
    current_item = ""
    in_bullet = False
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if is_page_header(line):
            i += 1
            continue
        
        if any(line == pat or line.startswith(pat + ' ') for pat in stop_patterns):
            break
        
        if re.match(r'^\d+\.\s', line):
            break
        
        if line in BULLET_CHARS or line == '':
            if current_item:
                cleaned = clean_extracted_text(current_item)
                if cleaned:
                    items.append(cleaned)
                current_item = ""
            in_bullet = True
            i += 1
            continue
        
        if line.startswith('• ') or line.startswith('- '):
            if current_item:
                cleaned = clean_extracted_text(current_item)
                if cleaned:
                    items.append(cleaned)
            current_item = line[2:]
            in_bullet = True
            i += 1
            continue
        
        if in_bullet or current_item:
            if current_item:
                current_item += " " + line
            else:
                current_item = line
        
        i += 1
    
    if current_item:
        cleaned = clean_extracted_text(current_item)
        if cleaned:
            items.append(cleaned)
    
    return items


def extract_numbered_list(lines, stop_patterns=None):
    """Extract a numbered list (1., 2., etc.) from lines."""
    if stop_patterns is None:
        stop_patterns = BPT_SECTIONS
    
    roman_pattern = r'^(i{1,3}|iv|vi{0,3}|ix|x)\.\s*(.*)'
    
    items = []
    current_item_lines = []
    current_num = 0
    skip_until_number = False
    pending_alternate_path = None
    
    for line in lines:
        line = line.strip()
        
        if is_page_header(line):
            skip_until_number = True
            continue
        
        if re.match(r'^[A-Z]{2}\s+[A-Z]', line):
            skip_until_number = True
            continue
        
        if line in ['Item', 'Details', 'Item Details']:
            skip_until_number = True
            continue
        
        if any(line == pat or line.startswith(pat + ' ') for pat in stop_patterns):
            break
        
        alt_path_match = re.match(r'^Alternate Path[:\s]+(.+)', line, re.IGNORECASE)
        if alt_path_match:
            pending_alternate_path = alt_path_match.group(1).strip()
            continue
        
        match = re.match(r'^(\d+)\.\s*(.*)', line)
        if match:
            skip_until_number = False
            if current_item_lines:
                items.append(format_step_with_substeps(current_item_lines))
            
            current_num = int(match.group(1))
            
            if current_num == 1 and pending_alternate_path:
                items.append(f"--- Alternate Path: {pending_alternate_path} ---")
                pending_alternate_path = None
            
            current_item_lines = [f"{current_num}. {match.group(2)}"]
            continue
        
        if not line:
            continue
        
        if skip_until_number:
            continue
        
        roman_match = re.match(roman_pattern, line)
        if roman_match and current_item_lines:
            current_item_lines.append(f"    {roman_match.group(1)}. {roman_match.group(2)}")
            continue
        
        sub_match = re.match(r'^([a-z])\.\s*(.*)', line)
        if sub_match and current_item_lines:
            sub_content = sub_match.group(2)
            embedded_match = re.search(r'\s+(i{1,3}|iv|vi{0,3}|ix|x)\.\s+', sub_content)
            if embedded_match:
                parts = re.split(r'\s+(i{1,3}|iv|vi{0,3}|ix|x)\.\s+', sub_content)
                if len(parts) > 1:
                    current_item_lines.append(f"  {sub_match.group(1)}. {parts[0].rstrip()}")
                    idx = 1
                    while idx < len(parts):
                        if idx + 1 < len(parts):
                            current_item_lines.append(f"    {parts[idx]}. {parts[idx+1]}")
                            idx += 2
                        else:
                            idx += 1
                    continue
            current_item_lines.append(f"  {sub_match.group(1)}. {sub_content}")
            continue
        
        if line.startswith('NOTE:') or line.startswith('Note:'):
            if current_item_lines:
                current_item_lines.append(f"  {line}")
            continue
        
        if current_item_lines:
            alt_embedded = re.search(r'Alternate Path[:\s]+(.+)', line, re.IGNORECASE)
            if alt_embedded:
                pending_alternate_path = alt_embedded.group(1).strip()
                before_alt = re.sub(r'\s*Alternate Path[:\s]+.+', '', line, flags=re.IGNORECASE)
                if before_alt.strip():
                    current_item_lines[-1] += " " + before_alt.strip()
                continue
            
            combined = current_item_lines[-1] + " " + line
            embedded_match = re.search(r'\s+(i{1,3}|iv|vi{0,3}|ix|x)\.\s+', combined)
            if embedded_match:
                parts = re.split(r'\s+(i{1,3}|iv|vi{0,3}|ix|x)\.\s+', combined)
                if len(parts) > 1:
                    current_item_lines[-1] = parts[0].rstrip()
                    idx = 1
                    while idx < len(parts):
                        if idx + 1 < len(parts):
                            current_item_lines.append(f"    {parts[idx]}. {parts[idx+1]}")
                            idx += 2
                        else:
                            idx += 1
                    continue
            current_item_lines[-1] += " " + line
    
    if current_item_lines:
        items.append(format_step_with_substeps(current_item_lines))
    
    return items


def format_step_with_substeps(lines):
    """Format a step with its sub-steps, preserving structure and indentation."""
    result_lines = []
    for line in lines:
        cleaned = clean_extracted_text(line, preserve_indent=True)
        if cleaned:
            result_lines.append(cleaned)
    return "\n".join(result_lines)


# =============================================================================
# PDF EXTRACTION
# =============================================================================

def extract_pdf_text(pdf_path):
    """Extract all text from a PDF, preserving page boundaries."""
    doc = fitz.open(pdf_path)
    pages = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        pages.append({
            'page_num': page_num + 1,
            'text': text,
            'lines': text.split('\n')
        })
    
    doc.close()
    return pages


def find_section_start(lines, section_name, start_idx=0):
    """Find the starting index of a section in the lines."""
    section_parts = section_name.split()
    
    for i in range(start_idx, len(lines)):
        line = lines[i].strip()
        
        if line == section_name:
            return i
        
        if len(section_parts) > 1 and line == section_parts[0]:
            remaining = ' '.join(section_parts[1:])
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line == remaining or next_line.startswith(remaining):
                    return i
    
    return -1


def find_next_section(lines, start_idx):
    """Find the next section header after start_idx."""
    section_markers = ['Trigger Event', 'Result', 'Business Process Steps', 'Business',
                       'Shared Data', 'Predecessor', 'Successor', 'Constraints', 
                       'Failures', 'Performance Measures', 'Performance']
    
    for i in range(start_idx, len(lines)):
        line = lines[i].strip()
        
        if is_page_header(line):
            continue
        
        if line in ['Item', 'Details', 'Item Details']:
            continue
        if re.match(r'^[A-Z]{2}\s+[A-Z]', line):
            continue
        
        if line in section_markers:
            return i
        
        if line == 'Business' and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if 'Process Steps' in next_line:
                return i
        
        if line == 'Description' and i > start_idx + 5:
            for j in range(i-1, max(start_idx, i-5), -1):
                if lines[j].strip() in ['Item', 'Details']:
                    return j - 2
    
    return len(lines)


# =============================================================================
# DESCRIPTION EXTRACTION
# =============================================================================

def extract_description(lines):
    """Extract a description, preserving paragraph structure and bullet lists."""
    result_lines = []
    current_text = ""
    pending_bullet = None
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if is_page_header(line):
            i += 1
            continue
        
        if line in BPT_SECTIONS:
            break
        
        if not line:
            if current_text:
                result_lines.append(current_text)
                current_text = ""
            pending_bullet = None
            i += 1
            continue
        
        if line == '\uf0fc':
            if current_text:
                result_lines.append(current_text)
                current_text = ""
            pending_bullet = 'checkmark'
            i += 1
            continue
        
        if line in BULLET_CHARS:
            if current_text:
                result_lines.append(current_text)
                current_text = ""
            pending_bullet = 'main'
            i += 1
            continue
        
        if line in ['o', 'O', '○', '◦']:
            if current_text:
                result_lines.append(current_text)
                current_text = ""
            pending_bullet = 'sub'
            i += 1
            continue
        
        if line in ['', '▪', '■', '□']:
            if current_text:
                result_lines.append(current_text)
                current_text = ""
            pending_bullet = 'nested'
            i += 1
            continue
        
        if line.startswith('• ') or line.startswith('- ') or line.startswith('\uf0b7 '):
            if current_text:
                result_lines.append(current_text)
            clean_line = line[2:] if line.startswith('• ') or line.startswith('- ') else line[2:]
            current_text = "• " + clean_line
            pending_bullet = None
            i += 1
            continue
        
        if line.startswith('o ') or line.startswith('○ '):
            if current_text:
                result_lines.append(current_text)
            current_text = "  - " + line[2:]
            pending_bullet = None
            i += 1
            continue
        
        if line.startswith('\uf0fc ') or line.startswith(' '):
            if current_text:
                result_lines.append(current_text)
            clean_line = line[2:] if line.startswith('\uf0fc ') else line[2:]
            current_text = " ✓ " + clean_line
            pending_bullet = None
            i += 1
            continue
        
        if pending_bullet:
            if current_text:
                result_lines.append(current_text)
            if pending_bullet == 'main':
                current_text = "• " + line
            elif pending_bullet == 'sub':
                current_text = "  - " + line
            elif pending_bullet == 'checkmark':
                current_text = " ✓ " + line
            else:
                current_text = " ✓ " + line
            pending_bullet = None
            i += 1
            continue
        
        if line.startswith('NOTE:') or line.startswith('Note:'):
            if current_text:
                result_lines.append(current_text)
            current_text = line
            i += 1
            continue
        
        if current_text:
            current_text += " " + line
        else:
            current_text = line
        
        i += 1
    
    if current_text:
        result_lines.append(current_text)
    
    result = "\n".join(result_lines)
    return clean_extracted_text(result)


def extract_trigger_events(lines):
    """Extract trigger events, categorizing into environment and interaction based."""
    environment = []
    interaction = []
    current_category = None
    current_item = ""
    
    for line in lines:
        line = line.strip()
        
        if is_page_header(line):
            continue
        
        if 'Environment-based' in line or 'Environment based' in line:
            if current_item and current_category:
                if current_category == 'environment':
                    environment.append(clean_text(current_item))
                else:
                    interaction.append(clean_text(current_item))
            current_category = 'environment'
            current_item = ""
            continue
        
        if 'Interaction-based' in line or 'Interaction based' in line:
            if current_item and current_category:
                if current_category == 'environment':
                    environment.append(clean_text(current_item))
                else:
                    interaction.append(clean_text(current_item))
            current_category = 'interaction'
            current_item = ""
            continue
        
        if not line:
            continue
        
        if line in BULLET_CHARS:
            if current_item and current_category:
                if current_category == 'environment':
                    environment.append(clean_text(current_item))
                else:
                    interaction.append(clean_text(current_item))
            current_item = ""
            continue
        
        if line in BPT_SECTIONS:
            break
        
        if line.startswith('• ') or line.startswith('- '):
            line = line[2:]
        
        if current_item:
            current_item += " " + line
        else:
            current_item = line
    
    if current_item and current_category:
        if current_category == 'environment':
            environment.append(clean_text(current_item))
        else:
            interaction.append(clean_text(current_item))
    
    if not environment and not interaction and current_item:
        interaction.append(clean_text(current_item))
    
    return environment, interaction


def is_process_header_artifact(line, process_code=None, process_name=None):
    """Check if a line is a process header artifact that should be filtered."""
    line = line.strip()
    
    artifacts = ['Item', 'Details', 'Item Details']
    if line in artifacts:
        return True
    
    if process_name and line == process_name:
        return True
    
    if process_code and line.startswith(process_code + ' '):
        return True
    
    if re.match(r'^[A-Z]{2}\s+[A-Z][a-z]+(\s+[A-Z][a-z]+)*', line):
        return True
    
    return False


def extract_simple_list(lines, process_code=None, process_name=None):
    """Extract a simple list (one item per line, no bullets)."""
    items = []
    current = ""
    
    for line in lines:
        line = line.strip()
        
        if not line:
            if current:
                items.append(clean_text(current))
                current = ""
            continue
        
        if is_page_header(line):
            continue
        
        if is_process_header_artifact(line, process_code, process_name):
            continue
        
        if line in BPT_SECTIONS:
            break
        
        if current and line[0].isupper() and not current.endswith(','):
            items.append(clean_text(current))
            current = line
        elif current:
            current += " " + line
        else:
            current = line
    
    if current:
        items.append(clean_text(current))
    
    return items


# =============================================================================
# BPT EXTRACTION
# =============================================================================

def extract_bpt_processes(pdf_path, area_name):
    """Extract all BPT processes from a business area PDF."""
    pages = extract_pdf_text(pdf_path)
    
    all_lines = []
    page_map = {}
    
    for page in pages:
        start_idx = len(all_lines)
        all_lines.extend(page['lines'])
        for i in range(start_idx, len(all_lines)):
            page_map[i] = page['page_num']
    
    processes = []
    process_code = AREA_CODES.get(area_name, "XX")
    
    process_starts = []
    for i, line in enumerate(all_lines):
        if line.strip() == 'Description':
            process_name = None
            sub_category = None
            
            for j in range(i - 1, max(0, i - 10), -1):
                candidate = all_lines[j].strip()
                
                if not candidate or len(candidate) < 3:
                    continue
                if 'Part I' in candidate or 'Page' in candidate or 'Version' in candidate:
                    continue
                if candidate in ['Item', 'Details', 'Item Details']:
                    continue
                if 'May 2014' in candidate:
                    continue
                
                if process_code in candidate and ' ' in candidate:
                    if not process_name or candidate != process_name:
                        sub_category = candidate
                    continue
                
                if not process_name and candidate[0].isupper() and process_code not in candidate:
                    process_name = candidate
                elif not process_name and candidate[0].isupper():
                    process_name = candidate
            
            if process_name:
                process_starts.append({
                    'name': process_name,
                    'sub_category': sub_category,
                    'start_line': i,
                    'start_page': page_map.get(i, 1)
                })
    
    for idx, proc in enumerate(process_starts):
        if idx + 1 < len(process_starts):
            end_line = process_starts[idx + 1]['start_line'] - 5
        else:
            end_line = len(all_lines)
        
        process_lines = all_lines[proc['start_line']:end_line]
        
        process_data = extract_bpt_process_data(
            process_lines, 
            proc['name'],
            proc['sub_category'],
            area_name,
            process_code,
            proc['start_page'],
            page_map.get(end_line - 1, proc['start_page'])
        )
        
        if process_data:
            processes.append(process_data)
    
    return processes


def extract_bpt_process_data(lines, process_name, sub_category, area_name, process_code, start_page, end_page):
    """Extract structured data from a BPT process section."""
    
    sub_cat_clean = ""
    if sub_category:
        parts = sub_category.replace('–', ' ').split()
        if len(parts) > 1:
            sub_cat_clean = ' '.join(parts[1:])
    
    data = {
        "document_type": "BPT",
        "version": "3.0",
        "version_date": "May 2014",
        "business_area": area_name,
        "sub_category": sub_cat_clean or area_name,
        "process_name": process_name,
        "process_code": process_code,
        "process_details": {
            "description": "",
            "trigger_events": {
                "environment_based": [],
                "interaction_based": []
            },
            "results": [],
            "process_steps": [],
            "diagrams": [],
            "shared_data": [],
            "predecessor_processes": [],
            "successor_processes": [],
            "constraints": "",
            "failures": [],
            "performance_measures": []
        },
        "metadata": {
            "source_file": "",
            "source_page_range": f"{start_page}-{end_page}",
            "extracted_date": date.today().isoformat()
        }
    }
    
    # Description
    desc_start = find_section_start(lines, 'Description')
    if desc_start >= 0:
        desc_end = find_next_section(lines, desc_start + 1)
        desc_lines = lines[desc_start + 1:desc_end]
        data["process_details"]["description"] = extract_description(desc_lines)
    
    # Trigger Event
    trigger_start = find_section_start(lines, 'Trigger Event')
    if trigger_start >= 0:
        trigger_end = find_next_section(lines, trigger_start + 1)
        trigger_lines = lines[trigger_start + 1:trigger_end]
        env, inter = extract_trigger_events(trigger_lines)
        data["process_details"]["trigger_events"]["environment_based"] = env
        data["process_details"]["trigger_events"]["interaction_based"] = inter
    
    # Result
    result_start = find_section_start(lines, 'Result')
    if result_start >= 0:
        result_end = find_next_section(lines, result_start + 1)
        result_lines = lines[result_start + 1:result_end]
        data["process_details"]["results"] = extract_bulleted_list(result_lines)
    
    # Business Process Steps
    steps_start = find_section_start(lines, 'Business Process Steps')
    if steps_start < 0:
        steps_start = find_section_start(lines, 'Business')
        if steps_start >= 0:
            found_steps = False
            if steps_start + 1 < len(lines):
                next_line = lines[steps_start + 1].strip()
                if next_line == 'Process Steps' or 'Process Steps' in next_line:
                    found_steps = True
                elif next_line == 'Process' and steps_start + 2 < len(lines):
                    if lines[steps_start + 2].strip() == 'Steps':
                        found_steps = True
            if not found_steps:
                steps_start = -1
    
    if steps_start >= 0:
        skip_lines = 1
        if steps_start + 1 < len(lines) and lines[steps_start + 1].strip() == 'Process Steps':
            skip_lines = 2
        elif steps_start + 2 < len(lines) and lines[steps_start + 1].strip() == 'Process' and lines[steps_start + 2].strip() == 'Steps':
            skip_lines = 3
        
        steps_end = find_next_section(lines, steps_start + skip_lines)
        steps_lines = lines[steps_start + skip_lines:steps_end]
        data["process_details"]["process_steps"] = extract_numbered_list(steps_lines)
    
    # Shared Data
    shared_start = find_section_start(lines, 'Shared Data')
    if shared_start >= 0:
        shared_end = find_next_section(lines, shared_start + 1)
        shared_lines = lines[shared_start + 1:shared_end]
        data["process_details"]["shared_data"] = extract_simple_list(shared_lines, process_code, process_name)
    
    # Predecessor
    pred_start = find_section_start(lines, 'Predecessor')
    if pred_start >= 0:
        pred_end = find_next_section(lines, pred_start + 1)
        pred_lines = lines[pred_start + 1:pred_end]
        data["process_details"]["predecessor_processes"] = extract_simple_list(pred_lines, process_code, process_name)
    
    # Successor
    succ_start = find_section_start(lines, 'Successor')
    if succ_start >= 0:
        succ_end = find_next_section(lines, succ_start + 1)
        succ_lines = lines[succ_start + 1:succ_end]
        data["process_details"]["successor_processes"] = extract_simple_list(succ_lines, process_code, process_name)
    
    # Constraints
    const_start = find_section_start(lines, 'Constraints')
    if const_start >= 0:
        const_end = find_next_section(lines, const_start + 1)
        const_lines = lines[const_start + 1:const_end]
        data["process_details"]["constraints"] = extract_description(const_lines)
    
    # Failures
    fail_start = find_section_start(lines, 'Failures')
    if fail_start >= 0:
        fail_end = find_next_section(lines, fail_start + 1)
        fail_lines = lines[fail_start + 1:fail_end]
        data["process_details"]["failures"] = extract_bulleted_list(fail_lines)
    
    # Performance Measures
    perf_start = find_section_start(lines, 'Performance Measures')
    if perf_start < 0:
        perf_start = find_section_start(lines, 'Performance')
        if perf_start >= 0 and perf_start + 1 < len(lines):
            if 'Measures' not in lines[perf_start + 1]:
                perf_start = -1
    
    if perf_start >= 0:
        perf_end = min(len(lines), perf_start + 50)
        perf_lines = lines[perf_start + 2:perf_end]
        data["process_details"]["performance_measures"] = extract_bulleted_list(perf_lines)
    
    return data


# =============================================================================
# IMAGE EXTRACTION
# =============================================================================

def extract_images_for_process(doc, proc, images_dir, process_code):
    """Extract images for a specific process based on page range."""
    page_range = proc['metadata'].get('source_page_range', '')
    if '-' not in page_range:
        return []
    
    start_page, end_page = map(int, page_range.split('-'))
    extracted_images = []
    MIN_SIZE = 200
    
    for page_num in range(start_page - 1, min(end_page, len(doc))):
        page = doc[page_num]
        images = page.get_images()
        
        for img_idx, img in enumerate(images):
            xref = img[0]
            try:
                base_image = doc.extract_image(xref)
                w, h = base_image['width'], base_image['height']
                
                if w < MIN_SIZE or h < MIN_SIZE:
                    continue
                
                safe_name = proc['process_name'].replace(' ', '_').replace('/', '_')
                ext = base_image['ext']
                filename = f"{process_code}_{safe_name}_diagram_{page_num + 1}_{img_idx + 1}.{ext}"
                
                filepath = os.path.join(images_dir, filename)
                with open(filepath, 'wb') as f:
                    f.write(base_image['image'])
                
                extracted_images.append({
                    "filename": filename,
                    "description": f"Process diagram from page {page_num + 1}",
                    "page_reference": page_num + 1
                })
                
                print(f"    📷 Extracted: {filename}")
                
            except Exception as e:
                print(f"    Warning: Could not extract image: {e}")
    
    return extracted_images


# =============================================================================
# FILE OUTPUT
# =============================================================================

def save_process_json(process_data, output_dir, force=False):
    """Save a process to a JSON file. Returns (filepath, was_written)."""
    code = process_data['process_code']
    name = process_data['process_name'].replace(' ', '_').replace('/', '_')
    filename = f"{code}_{name}_BPT_v3.0.json"
    
    filepath = os.path.join(output_dir, filename)
    
    # Check if file exists and we're not forcing
    if os.path.exists(filepath) and not force:
        return filepath, False
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(process_data, f, indent=2, ensure_ascii=False)
    
    return filepath, True


def get_output_dir(area_name):
    """Get the output directory for a business area."""
    dir_name = area_name.lower().replace(' ', '_')
    output_dir = os.path.join(OUTPUT_BASE, 'bpt', dir_name)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def get_pdf_path(area_name):
    """Get the PDF path for a business area."""
    pdf_dir = os.path.join(SOURCE_BASE, 'bpt', area_name)
    
    if not os.path.exists(pdf_dir):
        return None
    
    for f in os.listdir(pdf_dir):
        if f.endswith('.pdf'):
            return os.path.join(pdf_dir, f)
    
    return None


# =============================================================================
# MAIN EXTRACTION FUNCTIONS
# =============================================================================

def extract_area(area_name, with_images=False, force=False):
    """Extract all BPT processes from a business area."""
    print(f"\n{'='*60}")
    print(f"Extracting BPT: {area_name}")
    print('='*60)
    
    pdf_path = get_pdf_path(area_name)
    if not pdf_path:
        print(f"  ERROR: PDF not found for {area_name}")
        return []
    
    output_dir = get_output_dir(area_name)
    rel_pdf_path = pdf_path
    
    processes = extract_bpt_processes(pdf_path, area_name)
    print(f"  Found {len(processes)} processes")
    
    # Handle images if requested
    if with_images:
        images_dir = os.path.join(output_dir, 'images')
        os.makedirs(images_dir, exist_ok=True)
        
        doc = fitz.open(pdf_path)
        process_code = AREA_CODES.get(area_name, "XX")
        
        for proc in processes:
            extracted_images = extract_images_for_process(doc, proc, images_dir, process_code)
            proc['process_details']['diagrams'] = extracted_images
        
        doc.close()
    
    # Save each process
    saved_files = []
    skipped_files = []
    
    for proc in processes:
        proc['metadata']['source_file'] = rel_pdf_path
        filepath, was_written = save_process_json(proc, output_dir, force=force)
        
        if was_written:
            saved_files.append(filepath)
            print(f"  ✓ {proc['process_name']}")
        else:
            skipped_files.append(filepath)
            print(f"  ⏭ {proc['process_name']} (exists, use --force to overwrite)")
    
    if skipped_files:
        print(f"\n  Skipped {len(skipped_files)} existing files")
    
    return saved_files


def extract_all(force=False):
    """Extract all business areas."""
    all_files = []
    
    for area_name in AREA_CODES.keys():
        if area_name == "Member Management":
            continue
        
        files = extract_area(area_name, with_images=False, force=force)
        all_files.extend(files)
    
    return all_files


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Extract MITA 2014 BPT (Business Process Table) data from PDFs to JSON',
        epilog='Note: BCM extraction is in extract_bcm_2014.py.archived (BCMs were manually verified)'
    )
    parser.add_argument('--area', type=str, help='Business area name (e.g., "Care Management")')
    parser.add_argument('--all', action='store_true', help='Extract all areas')
    parser.add_argument('--with-images', action='store_true', help='Extract process diagrams')
    parser.add_argument('--force', action='store_true', help='Overwrite existing files')
    
    args = parser.parse_args()
    
    if args.all:
        files = extract_all(force=args.force)
        print(f"\n{'='*60}")
        print(f"COMPLETE: Extracted {len(files)} BPT files")
    elif args.area:
        files = extract_area(args.area, args.with_images, force=args.force)
        print(f"\n{'='*60}")
        print(f"COMPLETE: Extracted {len(files)} BPT files")
    else:
        parser.print_help()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
