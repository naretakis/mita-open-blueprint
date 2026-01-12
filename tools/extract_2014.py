#!/usr/bin/env python3
"""
MITA 2014 PDF to JSON Extraction Tool

Extracts BPT and BCM data from the May 2014 MITA PDFs and converts to JSON format.

Usage:
    python tools/extract_2014.py --area "Care Management" --type bpt
    python tools/extract_2014.py --all
    python tools/extract_2014.py --area "Eligibility and Enrollment Management" --type bpt --with-images
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

def clean_text(text):
    """Basic text cleaning - remove extra whitespace, normalize characters."""
    # Replace non-breaking spaces
    text = text.replace('\xa0', ' ')
    # Normalize dashes
    text = text.replace('‐', '-').replace('–', '-').replace('—', '-')
    # Remove multiple spaces
    text = re.sub(r' +', ' ', text)
    return text.strip()


def is_page_header(line):
    """Check if a line is a page header/footer to skip."""
    # Normalize the line first
    line_clean = line.replace('\xa0', ' ').replace('‐', '-').replace('–', '-').lower()
    
    # These are definite page headers
    skip_patterns = [
        'part i', 'part 1', 'appendix c', 'appendix d', 
        'may 2014', 'version 3.0', 'matrix details', 'model details'
    ]
    
    # Check for page number patterns
    if re.search(r'page\s*\d+', line_clean):
        return True
    
    # Check for header patterns, but not if it's content
    if 'business architecture' in line_clean and 'appendix' in line_clean:
        return True
    
    return any(pat in line_clean for pat in skip_patterns)


def clean_extracted_text(text):
    """Remove any remaining page header artifacts from extracted text."""
    # Normalize dashes first
    text = text.replace('‐', '-').replace('–', '-').replace('—', '-')
    
    # Normalize spaces (but preserve newlines)
    # Replace multiple spaces with single space
    text = re.sub(r'[ \t]+', ' ', text)
    # Normalize multiple newlines to max 2
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Patterns to remove
    patterns = [
        r'Part I\s*-?\s*Business Architecture.*?Details',
        r'Part I,?\s*Appendix [CD]\s*-?\s*Page\s*\d+',
        r'May 2014\s*Version 3\.0',
        r'[A-Z]{2}\s+[A-Za-z\s]+\s+Item\s+Details',  # "CM Case Management Establish Case Item Details"
    ]
    for pat in patterns:
        text = re.sub(pat, '', text, flags=re.IGNORECASE)
    return clean_text(text)


def join_wrapped_lines(lines, stop_patterns=None):
    """
    Join lines that were wrapped in the PDF.
    Stop when hitting a stop pattern or empty line.
    """
    if stop_patterns is None:
        stop_patterns = []
    
    result = []
    current = ""
    
    for line in lines:
        line = line.strip()
        
        # Check for stop patterns
        if any(pat in line for pat in stop_patterns):
            if current:
                result.append(clean_text(current))
                current = ""
            break
        
        # Skip empty lines (they indicate paragraph breaks)
        if not line:
            if current:
                result.append(clean_text(current))
                current = ""
            continue
        
        # Join with previous line
        if current:
            current += " " + line
        else:
            current = line
    
    if current:
        result.append(clean_text(current))
    
    return result


def extract_bulleted_list(lines, stop_patterns=None):
    """
    Extract a bulleted list from lines.
    Handles bullets on separate lines from content.
    Returns clean text without bullet characters (let the consumer format).
    """
    if stop_patterns is None:
        stop_patterns = BPT_SECTIONS
    
    items = []
    current_item = ""
    in_bullet = False
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip page headers
        if is_page_header(line):
            i += 1
            continue
        
        # Check for stop patterns
        if any(line == pat or line.startswith(pat + ' ') for pat in stop_patterns):
            break
        
        # Check for numbered items (indicates we've hit process steps)
        if re.match(r'^\d+\.\s', line):
            break
        
        # Check if this is a bullet character
        if line in BULLET_CHARS or line == '':
            # Save previous item
            if current_item:
                cleaned = clean_extracted_text(current_item)
                if cleaned:
                    items.append(cleaned)
                current_item = ""
            in_bullet = True
            i += 1
            continue
        
        # Check for inline bullet
        if line.startswith('• ') or line.startswith('- '):
            if current_item:
                cleaned = clean_extracted_text(current_item)
                if cleaned:
                    items.append(cleaned)
            current_item = line[2:]
            in_bullet = True
            i += 1
            continue
        
        # If we're after a bullet, this is content
        if in_bullet or current_item:
            if current_item:
                current_item += " " + line
            else:
                current_item = line
        
        i += 1
    
    # Don't forget the last item
    if current_item:
        cleaned = clean_extracted_text(current_item)
        if cleaned:
            items.append(cleaned)
    
    return items


def extract_numbered_list(lines, stop_patterns=None):
    """
    Extract a numbered list (1., 2., etc.) from lines.
    Preserves sub-steps (a., b., c.) and NOTE: blocks with proper formatting.
    """
    if stop_patterns is None:
        stop_patterns = BPT_SECTIONS
    
    items = []
    current_item_lines = []
    current_num = 0
    skip_until_number = False
    
    for line in lines:
        line = line.strip()
        
        # Skip page headers
        if is_page_header(line):
            skip_until_number = True
            continue
        
        # Skip process header repeats (CM Case Management, etc.)
        if re.match(r'^[A-Z]{2}\s+[A-Z]', line):
            skip_until_number = True
            continue
        
        # Skip Item/Details markers
        if line in ['Item', 'Details', 'Item Details']:
            skip_until_number = True
            continue
        
        # Check for stop patterns
        if any(line == pat or line.startswith(pat + ' ') for pat in stop_patterns):
            break
        
        # Check for main numbered item (1., 2., etc.)
        match = re.match(r'^(\d+)\.\s*(.*)$', line)
        if match:
            skip_until_number = False
            # Save previous item
            if current_item_lines:
                items.append(format_step_with_substeps(current_item_lines))
            current_num = int(match.group(1))
            current_item_lines = [f"{current_num}. {match.group(2)}"]
            continue
        
        # Skip empty lines
        if not line:
            continue
        
        # If we're skipping until next number, continue
        if skip_until_number:
            continue
        
        # Check for sub-step (a., b., c., etc.)
        sub_match = re.match(r'^([a-z])\.\s*(.*)$', line)
        if sub_match and current_item_lines:
            current_item_lines.append(f"  {sub_match.group(1)}. {sub_match.group(2)}")
            continue
        
        # Check for NOTE: at start of line
        if line.startswith('NOTE:') or line.startswith('Note:'):
            if current_item_lines:
                current_item_lines.append(f"  {line}")
            continue
        
        # Continue previous line (wrapped text)
        if current_item_lines:
            # Append to the last line in current_item_lines
            current_item_lines[-1] += " " + line
    
    # Don't forget the last item
    if current_item_lines:
        items.append(format_step_with_substeps(current_item_lines))
    
    return items


def format_step_with_substeps(lines):
    """Format a step with its sub-steps, preserving structure."""
    result_lines = []
    for line in lines:
        cleaned = clean_extracted_text(line)
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
    # Handle multi-line section names (e.g., "Business \nProcess Steps")
    section_parts = section_name.split()
    
    for i in range(start_idx, len(lines)):
        line = lines[i].strip()
        
        # Direct match
        if line == section_name:
            return i
        
        # Check for split across lines
        if len(section_parts) > 1 and line == section_parts[0]:
            # Check if next lines complete the section name
            remaining = ' '.join(section_parts[1:])
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line == remaining or next_line.startswith(remaining):
                    return i
    
    return -1


# =============================================================================
# BPT EXTRACTION
# =============================================================================

def extract_bpt_processes(pdf_path, area_name):
    """Extract all BPT processes from a business area PDF."""
    pages = extract_pdf_text(pdf_path)
    
    # Combine all text
    all_lines = []
    page_map = {}  # line_idx -> page_num
    
    for page in pages:
        start_idx = len(all_lines)
        all_lines.extend(page['lines'])
        for i in range(start_idx, len(all_lines)):
            page_map[i] = page['page_num']
    
    # Find process boundaries by looking for "Description" after process headers
    processes = []
    process_code = AREA_CODES.get(area_name, "XX")
    
    # Find all process starts
    process_starts = []
    for i, line in enumerate(all_lines):
        if line.strip() == 'Description':
            # Look backwards for process name and sub_category
            process_name = None
            sub_category = None
            
            for j in range(i - 1, max(0, i - 10), -1):
                candidate = all_lines[j].strip()
                
                # Skip empty and header lines
                if not candidate or len(candidate) < 3:
                    continue
                if 'Part I' in candidate or 'Page' in candidate or 'Version' in candidate:
                    continue
                if candidate in ['Item', 'Details', 'Item Details']:
                    continue
                if 'May 2014' in candidate:
                    continue
                
                # Check if this looks like a category line (contains process code with space)
                # Format: "CM Case Management" or "CM Authorization Determination"
                if process_code in candidate and ' ' in candidate:
                    # Make sure it's not just the process name repeated
                    if not process_name or candidate != process_name:
                        sub_category = candidate
                    continue
                
                # This should be the process name (not containing the process code pattern)
                if not process_name and candidate[0].isupper() and process_code not in candidate:
                    process_name = candidate
                    # Don't break - keep looking for sub_category
                elif not process_name and candidate[0].isupper():
                    # Process name might contain the code if it's repeated
                    process_name = candidate
            
            if process_name:
                process_starts.append({
                    'name': process_name,
                    'sub_category': sub_category,
                    'start_line': i,
                    'start_page': page_map.get(i, 1)
                })
    
    # Extract each process
    for idx, proc in enumerate(process_starts):
        # Determine end line
        if idx + 1 < len(process_starts):
            end_line = process_starts[idx + 1]['start_line'] - 5
        else:
            end_line = len(all_lines)
        
        process_lines = all_lines[proc['start_line']:end_line]
        
        # Extract process data
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
    
    # Parse sub_category to get clean name
    sub_cat_clean = ""
    if sub_category:
        # Format: "CM Case Management" or "EE Member Enrollment"
        parts = sub_category.replace('–', ' ').split()
        if len(parts) > 1:
            sub_cat_clean = ' '.join(parts[1:])  # Skip the code
    
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
    
    # Find each section and extract content
    
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
        # Try finding "Business" followed by "Process" and "Steps" on separate lines
        steps_start = find_section_start(lines, 'Business')
        if steps_start >= 0:
            # Check if next line(s) complete "Process Steps"
            found_steps = False
            if steps_start + 1 < len(lines):
                next_line = lines[steps_start + 1].strip()
                if next_line == 'Process Steps' or 'Process Steps' in next_line:
                    found_steps = True
                elif next_line == 'Process' and steps_start + 2 < len(lines):
                    # Check for "Steps" on the third line
                    if lines[steps_start + 2].strip() == 'Steps':
                        found_steps = True
                        steps_start = steps_start  # Keep the same start, but we'll skip 3 lines
            if not found_steps:
                steps_start = -1
    
    if steps_start >= 0:
        # Determine how many lines to skip for the header
        skip_lines = 1  # Default: "Business Process Steps" on one line
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
        perf_end = min(len(lines), perf_start + 50)  # Performance measures are usually at the end
        perf_lines = lines[perf_start + 2:perf_end]
        data["process_details"]["performance_measures"] = extract_bulleted_list(perf_lines)
    
    return data


def find_next_section(lines, start_idx):
    """Find the next section header after start_idx."""
    # All section markers that indicate a new section
    section_markers = ['Trigger Event', 'Result', 'Business Process Steps', 'Business',
                       'Shared Data', 'Predecessor', 'Successor', 'Constraints', 
                       'Failures', 'Performance Measures', 'Performance']
    
    for i in range(start_idx, len(lines)):
        line = lines[i].strip()
        
        # Skip page headers
        if is_page_header(line):
            continue
        
        # Skip process header repeats
        if line in ['Item', 'Details', 'Item Details']:
            continue
        if re.match(r'^[A-Z]{2}\s+[A-Z]', line):  # CM Case Management, etc.
            continue
        
        # Check for actual section markers
        if line in section_markers:
            return i
        
        # Check for "Business" followed by "Process Steps" on next line
        if line == 'Business' and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if 'Process Steps' in next_line:
                return i
        
        # Check for next process (new Description section)
        if line == 'Description' and i > start_idx + 5:
            # Look back to see if this is a new process
            for j in range(i-1, max(start_idx, i-5), -1):
                if lines[j].strip() in ['Item', 'Details']:
                    return j - 2  # Return before the new process header
    
    return len(lines)


def extract_description(lines):
    """
    Extract a description, preserving paragraph structure and bullet lists.
    
    Returns text with:
    - Paragraphs separated by double newlines
    - Bullet items on their own lines with "• " prefix
    - Sub-bullets with "  - " prefix (indented)
    """
    result_lines = []
    current_text = ""
    pending_bullet = None  # None, 'main', 'sub', 'nested'
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip page headers
        if is_page_header(line):
            i += 1
            continue
        
        # Skip section markers - we've hit the next section
        if line in BPT_SECTIONS:
            break
        
        # Empty line = paragraph break
        if not line:
            if current_text:
                result_lines.append(current_text)
                current_text = ""
            pending_bullet = None
            i += 1
            continue
        
        # Check if this is a bullet character on its own line
        if line in BULLET_CHARS:
            # Save current text first
            if current_text:
                result_lines.append(current_text)
                current_text = ""
            pending_bullet = 'main'
            i += 1
            continue
        
        # Check for sub-bullet markers (o, ○)
        if line in ['o', 'O', '○', '◦']:
            if current_text:
                result_lines.append(current_text)
                current_text = ""
            pending_bullet = 'sub'
            i += 1
            continue
        
        # Check for nested bullet markers on their own
        if line in ['', '▪', '■', '□']:
            if current_text:
                result_lines.append(current_text)
                current_text = ""
            pending_bullet = 'nested'
            i += 1
            continue
        
        # Check for inline bullet at start of line (main bullets)
        if line.startswith('• ') or line.startswith('- ') or line.startswith('\uf0b7 '):
            if current_text:
                result_lines.append(current_text)
            clean_line = line[2:] if line.startswith('• ') or line.startswith('- ') else line[2:]
            current_text = "• " + clean_line
            pending_bullet = None
            i += 1
            continue
        
        # Check for inline sub-bullet (o markers)
        if line.startswith('o ') or line.startswith('○ '):
            if current_text:
                result_lines.append(current_text)
            current_text = "  - " + line[2:]
            pending_bullet = None
            i += 1
            continue
        
        # Check for inline nested bullet (\uf0fc is checkmark/nested bullet in PDFs)
        if line.startswith('\uf0fc ') or line.startswith(' '):
            if current_text:
                result_lines.append(current_text)
            clean_line = line[2:] if line.startswith('\uf0fc ') else line[2:]
            current_text = "    · " + clean_line
            pending_bullet = None
            i += 1
            continue
        
        # If we have a pending bullet, this line is the bullet content
        if pending_bullet:
            if current_text:
                result_lines.append(current_text)
            if pending_bullet == 'main':
                current_text = "• " + line
            elif pending_bullet == 'sub':
                current_text = "  - " + line
            else:  # nested
                current_text = "    · " + line
            pending_bullet = None
            i += 1
            continue
        
        # Check for NOTE: which should start a new paragraph
        if line.startswith('NOTE:') or line.startswith('Note:'):
            if current_text:
                result_lines.append(current_text)
            current_text = line
            i += 1
            continue
        
        # Regular continuation of current text
        if current_text:
            current_text += " " + line
        else:
            current_text = line
        
        i += 1
    
    # Don't forget the last part
    if current_text:
        result_lines.append(current_text)
    
    # Join with appropriate newlines
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
        
        # Skip page headers
        if is_page_header(line):
            continue
        
        # Check for category headers
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
        
        # Skip empty lines
        if not line:
            continue
        
        # Check for bullet
        if line in BULLET_CHARS:
            if current_item and current_category:
                if current_category == 'environment':
                    environment.append(clean_text(current_item))
                else:
                    interaction.append(clean_text(current_item))
            current_item = ""
            continue
        
        # Skip section markers
        if line in BPT_SECTIONS:
            break
        
        # Strip leading bullet if present
        if line.startswith('• ') or line.startswith('- '):
            line = line[2:]
        
        # Add to current item
        if current_item:
            current_item += " " + line
        else:
            current_item = line
    
    # Don't forget last item
    if current_item and current_category:
        if current_category == 'environment':
            environment.append(clean_text(current_item))
        else:
            interaction.append(clean_text(current_item))
    
    # If no categorization found, put all in interaction (default)
    if not environment and not interaction and current_item:
        interaction.append(clean_text(current_item))
    
    return environment, interaction


def is_process_header_artifact(line, process_code=None, process_name=None):
    """Check if a line is a process header artifact that should be filtered from lists."""
    line = line.strip()
    
    # Known artifacts
    artifacts = ['Item', 'Details', 'Item Details']
    if line in artifacts:
        return True
    
    # Skip if it matches the current process name
    if process_name and line == process_name:
        return True
    
    # Pattern: [CODE] [Category] (e.g., "OM Claims Adjudication", "CM Case Management")
    if process_code and line.startswith(process_code + ' '):
        return True
    
    # Generic pattern: 2-letter code followed by space and capitalized words
    if re.match(r'^[A-Z]{2}\s+[A-Z][a-z]+(\s+[A-Z][a-z]+)*$', line):
        return True
    
    return False


def extract_simple_list(lines, process_code=None, process_name=None):
    """Extract a simple list (one item per line, no bullets)."""
    items = []
    current = ""
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines
        if not line:
            if current:
                items.append(clean_text(current))
                current = ""
            continue
        
        # Skip page headers
        if is_page_header(line):
            continue
        
        # Skip process header artifacts
        if is_process_header_artifact(line, process_code, process_name):
            continue
        
        # Skip section markers
        if line in BPT_SECTIONS:
            break
        
        # Check if this looks like a new item (starts with capital, previous ended)
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
# BCM EXTRACTION
# =============================================================================

def extract_bcm_processes(pdf_path, area_name):
    """Extract all BCM processes from a business area PDF."""
    pages = extract_pdf_text(pdf_path)
    
    # Combine all text
    all_lines = []
    page_map = {}
    
    for page in pages:
        start_idx = len(all_lines)
        all_lines.extend(page['lines'])
        for i in range(start_idx, len(all_lines)):
            page_map[i] = page['page_num']
    
    processes = []
    process_code = AREA_CODES.get(area_name, "XX")
    
    # Known category headers that should NOT be treated as process names
    # These are section headers that group related processes
    category_headers = {
        # Financial Management categories
        'Accounts Receivable Management',
        'Accounts Payable Management', 
        'Fiscal Management',
        # Provider Management categories
        'Provider Information Management',
        'Provider Support',
        # Plan Management categories
        'Health Plan Administration',
        'Health Benefits Administration',
        'Plan Administration',
        # Contractor Management categories
        'Contract Management',
        'Contractor Information Management',
        'Contractor Support',
        # Operations Management categories
        'Claims Adjudication',
        'Payment and Reporting',
        # Performance Management categories
        'Compliance Management',
        # Care Management categories
        'Authorization Determination',
        'Case Management',
        # Eligibility and Enrollment categories
        'Provider Enrollment',
        # Business Relationship Management categories
        'Standards Management',
        # Top-level business area names (should never be process names)
        'Member Management',
        'Provider Management',
        'Care Management',
        'Plan Management',
        'Operations Management',
        'Performance Management',
        'Contractor Management',
        'Business Relationship Management',
        'Eligibility and Enrollment Management',
        'Financial Management',
    }
    
    # Find process boundaries by looking for process names
    # Process names appear on their own line, often preceded by the category line (e.g., "FM – Accounts Payable Management")
    process_starts = []
    seen_names = set()
    
    for i, line in enumerate(all_lines):
        line_stripped = line.strip()
        
        # Skip empty lines and headers
        if not line_stripped or len(line_stripped) < 3:
            continue
        if 'Part I' in line_stripped or 'Page' in line_stripped or 'Version' in line_stripped:
            continue
        if 'May 2014' in line_stripped:
            continue
        if line_stripped in ['Details', 'Item', 'Item Details', 'Capability', 'Question', 'Capability Question']:
            continue
        if line_stripped.startswith('Level '):
            continue
        if 'Business Capability' in line_stripped:
            continue
        if 'Appendix' in line_stripped:
            continue
        
        # Skip known category headers
        if line_stripped in category_headers:
            continue
        
        # Check if this looks like a process name
        # Process names are title case, don't contain '–' (that's the category line), 
        # and are followed by either a category line or a "Capability" header
        if '–' in line_stripped:
            continue
        if '?' in line_stripped:  # Questions, not process names
            continue
        
        # Check if this could be a process name by looking at context
        # A process name should be followed by either:
        # 1. A category line (e.g., "FM – Accounts Payable Management")
        # 2. A "Capability" header
        # 3. Another process name (for the next process)
        is_process_name = False
        sub_category = None
        
        # Look ahead for context
        for j in range(i + 1, min(i + 5, len(all_lines))):
            next_line = all_lines[j].strip()
            if not next_line:
                continue
            # Category line follows process name
            if '–' in next_line and process_code in next_line:
                is_process_name = True
                sub_category = next_line
                break
            # Capability header follows (sometimes directly)
            if next_line == 'Capability' or next_line.startswith('Capability Question'):
                is_process_name = True
                break
            # Another title-case line might be the category or next process
            if next_line[0].isupper() and '?' not in next_line:
                # Check if it's a category line
                if '–' in next_line:
                    is_process_name = True
                    sub_category = next_line
                    break
        
        if is_process_name and line_stripped not in seen_names:
            # Verify it looks like a process name (title case, reasonable length)
            words = line_stripped.split()
            if len(words) >= 2 and all(w[0].isupper() or w in ['the', 'and', 'or', 'of', 'to', 'for', 'in', 'a', 'an'] for w in words if w):
                seen_names.add(line_stripped)
                process_starts.append({
                    'name': line_stripped,
                    'sub_category': sub_category,
                    'start_line': i,
                    'start_page': page_map.get(i, 1)
                })
    
    # Extract each process
    for idx, proc in enumerate(process_starts):
        # Determine end line - use the start of the next process
        if idx + 1 < len(process_starts):
            end_line = process_starts[idx + 1]['start_line']
        else:
            end_line = len(all_lines)
        
        # Determine end page
        end_page = page_map.get(end_line - 1, proc['start_page'])
        
        process_lines = all_lines[proc['start_line']:end_line]
        
        process_data = extract_bcm_process_data(
            process_lines,
            proc['name'],
            proc['sub_category'],
            area_name,
            process_code,
            proc['start_page'],
            end_page,
            pdf_path  # Pass PDF path for position-based extraction
        )
        
        if process_data:
            processes.append(process_data)
    
    return processes


def extract_bcm_process_data(lines, process_name, sub_category, area_name, process_code, start_page, end_page, pdf_path=None):
    """Extract structured data from a BCM process section."""
    
    # Parse sub_category
    sub_cat_clean = ""
    if sub_category:
        # Format: "CM – Case Management" 
        parts = sub_category.split('–')
        if len(parts) > 1:
            sub_cat_clean = parts[1].strip()
        else:
            parts = sub_category.split()
            if len(parts) > 1:
                sub_cat_clean = ' '.join(parts[1:])
    
    data = {
        "document_type": "BCM",
        "version": "3.0",
        "version_date": "May 2014",
        "business_area": area_name,
        "sub_category": sub_cat_clean or area_name,
        "process_name": process_name,
        "process_code": process_code,
        "maturity_model": {
            "capability_questions": []
        },
        "metadata": {
            "source_file": "",
            "source_page_range": f"{start_page}-{end_page}",
            "extracted_date": date.today().isoformat()
        }
    }
    
    # Try position-based extraction first (more accurate for table data)
    if pdf_path:
        try:
            questions = extract_bcm_with_positions(pdf_path, process_name, start_page, end_page)
            if questions:
                data["maturity_model"]["capability_questions"] = questions
                return data
        except Exception as e:
            print(f"    Warning: Position-based extraction failed: {e}")
    
    # Fallback to text-based extraction
    questions = extract_capability_questions(lines)
    data["maturity_model"]["capability_questions"] = questions
    
    return data


def extract_bcm_with_positions(pdf_path, process_name, start_page, end_page):
    """
    Extract BCM capability questions using position-based parsing.
    This uses x-coordinates to determine which column text belongs to.
    
    Returns list of capability questions with proper level separation.
    """
    doc = fitz.open(pdf_path)
    
    # Column x-coordinate thresholds (based on PDF analysis)
    # Header positions: Question ~100, L1 ~209, L2 ~313, L3 ~429, L4 ~545, L5 ~649
    # Thresholds are midpoints between column headers
    COL_THRESHOLDS = [
        (0, 155, 'question'),
        (155, 261, 'level_1'),
        (261, 371, 'level_2'),
        (371, 487, 'level_3'),
        (487, 597, 'level_4'),
        (597, 800, 'level_5'),
    ]
    def get_column(x):
        for low, high, name in COL_THRESHOLDS:
            if low <= x < high:
                return name
        return None
    
    questions = []
    current_category = "Business Capability Descriptions"
    
    # Process each page in the range
    all_rows = []
    
    # Track when we've found our target process (to skip content from previous process on first page)
    found_process = False
    process_name_lower = process_name.lower()
    
    for page_num in range(start_page - 1, min(end_page, len(doc))):
        page = doc[page_num]
        blocks = page.get_text('dict')['blocks']
        
        # Collect text items with positions
        items = []
        for block in blocks:
            if 'lines' not in block:
                continue
            for line in block['lines']:
                for span in line['spans']:
                    text = span['text'].strip()
                    if not text:
                        continue
                    
                    # Check if this is our target process name (marks the start of our content)
                    if not found_process and process_name_lower in text.lower():
                        found_process = True
                    
                    # Skip page header text
                    if is_page_header(text):
                        continue
                    # Skip level labels in content (table header row)
                    if text in ['Level 1', 'Level 2', 'Level 3', 'Level 4', 'Level 5']:
                        continue
                    # Skip table header text (appears at top of each page)
                    if text in ['Capability', 'Question', 'Capability Question', 'Details', 'Item', 'Item Details']:
                        continue
                    
                    # On the first page, only collect items after we've found our process name
                    # This skips content from the previous process that spills onto this page
                    if page_num == start_page - 1 and not found_process:
                        continue
                    
                    bbox = span['bbox']
                    x, y = bbox[0], bbox[1]
                    col = get_column(x)
                    if col:
                        items.append({
                            'x': x, 'y': y, 'text': text, 'col': col,
                            'page': page_num + 1
                        })
        
        # Sort by y position
        items.sort(key=lambda i: i['y'])
        
        # Group items into rows (items within 15 pixels vertically)
        current_row = {'y': -100, 'items': []}
        for item in items:
            if abs(item['y'] - current_row['y']) < 15:
                current_row['items'].append(item)
            else:
                if current_row['items']:
                    all_rows.append(current_row)
                current_row = {'y': item['y'], 'items': [item], 'page': page_num + 1}
        if current_row['items']:
            all_rows.append(current_row)
    
    doc.close()
    
    # Now process rows to extract questions and levels
    current_category = "Business Capability Descriptions"
    current_levels = {'level_1': [], 'level_2': [], 'level_3': [], 'level_4': [], 'level_5': []}
    pending_levels = {'level_1': [], 'level_2': [], 'level_3': [], 'level_4': [], 'level_5': []}  # Buffer for levels before ? is seen
    question_text_parts = []
    current_note_parts = []  # Buffer for NOTE content
    in_question = False
    seen_first_question = False  # Track if we've processed at least one question
    
    for row in all_rows:
        # Separate items by column
        row_by_col = {'question': [], 'level_1': [], 'level_2': [], 'level_3': [], 'level_4': [], 'level_5': []}
        for item in row['items']:
            row_by_col[item['col']].append(item['text'])
        
        question_text = ' '.join(row_by_col['question'])
        has_level_content = any(row_by_col[f'level_{i}'] for i in range(1, 6))
        
        # Skip category headers like "FM – Accounts Payable Management" that repeat on each page
        if question_text and '–' in question_text:
            continue
        
        # Skip table headers that repeat on each page (must be before stop condition check)
        if question_text in ['Capability', 'Question', 'Capability Question']:
            continue
        if question_text.startswith('Capability Question Level'):
            continue
        if 'Level 1' in question_text and 'Level 2' in question_text:
            continue
        
        # Check if we've hit a new process (stop condition)
        # A new process is indicated by its name appearing in the question column
        # This happens after we've already seen at least one question
        # Skip this check for Business Capability headers (they're category headers, not process names)
        if seen_first_question and question_text and not has_level_content:
            if 'Business Capability' not in question_text:
                # Check if this looks like a process name (not a question)
                # Process names don't end with ? and often contain "Management" or match known patterns
                if '?' not in question_text and not question_text.startswith('NOTE'):
                    # Check if it looks like a different process name
                    # Process names are typically title case and don't start with question words
                    question_starters = ['Is ', 'How ', 'What ', 'Does ', 'Are ', 'Can ', 'Will ']
                    if not any(question_text.startswith(w) for w in question_starters):
                        # This might be a new process name - check if it's different from ours
                        if process_name_lower not in question_text.lower():
                            # Looks like we've hit the next process, stop here
                            break
        
        # Check for category headers
        if 'Business Capability' in question_text:
            # Save previous question if exists
            if question_text_parts and in_question:
                q_text = ' '.join(question_text_parts)
                if '?' in q_text:
                    q_obj = {
                        'category': current_category,
                        'question': clean_text(q_text),
                        'levels': {k: format_bcm_level_text(v) for k, v in current_levels.items()}
                    }
                    if current_note_parts:
                        q_obj['note'] = clean_text(' '.join(current_note_parts))
                    questions.append(q_obj)
                question_text_parts = []
                current_note_parts = []
                current_levels = {'level_1': [], 'level_2': [], 'level_3': [], 'level_4': [], 'level_5': []}
                pending_levels = {'level_1': [], 'level_2': [], 'level_3': [], 'level_4': [], 'level_5': []}
                in_question = False
            
            # Update category
            if 'Descriptions' in question_text:
                current_category = "Business Capability Descriptions"
            elif 'Timeliness' in question_text:
                current_category = "Business Capability Quality: Timeliness of Process"
            elif 'Data Access' in question_text or 'Accuracy' in question_text:
                current_category = "Business Capability Quality: Data Access and Accuracy"
            elif 'Cost' in question_text:
                current_category = "Business Capability Quality: Cost Effectiveness"
            elif 'Effort' in question_text or 'Efficiency' in question_text:
                current_category = "Business Capability Quality: Effort to Perform; Efficiency"
            elif 'Utility' in question_text or 'Value' in question_text:
                current_category = "Business Capability Quality: Utility or Value to Stakeholders"
            elif 'Accuracy' in question_text:
                current_category = "Business Capability Quality: Accuracy of Process Results"
            continue
        
        # Skip "Capability Question" prefix text (appears in question column but is a header)
        if question_text.startswith('Capability Question'):
            # Strip the prefix if there's more text after it
            remainder = question_text.replace('Capability Question', '').strip()
            if remainder:
                question_text = remainder
            else:
                continue
        
        # Skip rows that look like table headers (have "Capability" or "Question" with level content)
        # This catches cases where the header spans multiple rows
        if question_text in ['Capability', 'Question'] and has_level_content:
            continue
        
        # Handle NOTE: blocks in question column - capture them for the next question
        if question_text.startswith('NOTE:') or question_text.startswith('Note:'):
            # Start or continue capturing NOTE content
            note_content = re.sub(r'^NOTE:\s*', '', question_text, flags=re.IGNORECASE)
            current_note_parts.append(note_content)
            continue
        
        # If we're in a NOTE block (have note parts but no question yet), continue capturing
        if current_note_parts and not question_text_parts and not has_level_content:
            # This might be continuation of the NOTE
            # Check if it looks like question content
            question_starters = ['Is ', 'How ', 'What ', 'Does ', 'Are ', 'Can ', 'Will ']
            has_question_word = any(question_text.startswith(w) for w in question_starters)
            if not has_question_word and '?' not in question_text:
                # Continuation of NOTE
                current_note_parts.append(question_text)
                continue
        
        # Skip page headers and process name repeats
        if is_page_header(question_text):
            continue
        if question_text and '–' in question_text:  # Category header like "CM – Case Management"
            continue
        
        # Check if question text contains an embedded NOTE that should be separated
        # Pattern: "Some text NOTE: note content Is the process...?"
        if 'NOTE:' in question_text and '?' in question_text:
            # Split out the NOTE and keep only the question part
            # Find where the actual question starts (look for common question patterns)
            note_match = re.search(r'(.*?)(NOTE:.*?)(\s*(?:Is the|How |What |Does |Are ).*\?.*)', question_text, re.IGNORECASE | re.DOTALL)
            if note_match:
                # Keep only the question part
                question_text = note_match.group(3).strip()
        
        # If we have a question ending with ?, this completes the question text
        if '?' in question_text:
            question_text_parts.append(question_text)
            in_question = True
            # Merge pending levels (collected before ?) with current levels
            for level in ['level_1', 'level_2', 'level_3', 'level_4', 'level_5']:
                current_levels[level].extend(pending_levels[level])
                pending_levels[level] = []
                if row_by_col[level]:
                    current_levels[level].extend(row_by_col[level])
        
        elif in_question and question_text and not has_level_content:
            # New question starting (no level content) - save the previous one
            q_text = ' '.join(question_text_parts)
            if '?' in q_text:
                q_obj = {
                    'category': current_category,
                    'question': clean_text(q_text),
                    'levels': {k: format_bcm_level_text(v) for k, v in current_levels.items()}
                }
                if current_note_parts:
                    q_obj['note'] = clean_text(' '.join(current_note_parts))
                questions.append(q_obj)
                seen_first_question = True
            # Start new question - reset note parts too
            question_text_parts = [question_text]
            current_note_parts = []
            current_levels = {'level_1': [], 'level_2': [], 'level_3': [], 'level_4': [], 'level_5': []}
            pending_levels = {'level_1': [], 'level_2': [], 'level_3': [], 'level_4': [], 'level_5': []}
            in_question = False  # Will become True when we see the ?
        
        elif in_question and question_text and has_level_content:
            # Check if this looks like a new question starting (has question starter words)
            # If so, save the previous question and start a new one
            question_starters = ['Is ', 'How ', 'What ', 'Does ', 'Are ', 'Can ', 'Will ']
            if any(question_text.startswith(w) for w in question_starters):
                # New question starting - save the previous one
                q_text = ' '.join(question_text_parts)
                if '?' in q_text:
                    q_obj = {
                        'category': current_category,
                        'question': clean_text(q_text),
                        'levels': {k: format_bcm_level_text(v) for k, v in current_levels.items()}
                    }
                    if current_note_parts:
                        q_obj['note'] = clean_text(' '.join(current_note_parts))
                    questions.append(q_obj)
                    seen_first_question = True
                # Start new question
                question_text_parts = [question_text]
                current_note_parts = []
                current_levels = {'level_1': [], 'level_2': [], 'level_3': [], 'level_4': [], 'level_5': []}
                pending_levels = {'level_1': [], 'level_2': [], 'level_3': [], 'level_4': [], 'level_5': []}
                in_question = False
                # Collect level content for this new question
                for level in ['level_1', 'level_2', 'level_3', 'level_4', 'level_5']:
                    if row_by_col[level]:
                        pending_levels[level].extend(row_by_col[level])
            else:
                # Continue collecting level content for current question
                for level in ['level_1', 'level_2', 'level_3', 'level_4', 'level_5']:
                    if row_by_col[level]:
                        current_levels[level].extend(row_by_col[level])
                        
        elif in_question and has_level_content:
            # Continue collecting level content for current question (no question text)
            for level in ['level_1', 'level_2', 'level_3', 'level_4', 'level_5']:
                if row_by_col[level]:
                    current_levels[level].extend(row_by_col[level])
        elif question_text and not in_question:
            # Building up question text before the ?
            # Skip rows that are clearly not part of a question:
            # - Process/area name headers
            # - NOTE blocks
            # - Text that doesn't look like question content
            
            # Skip NOTE blocks
            if question_text.startswith('NOTE:') or question_text.startswith('Note:'):
                continue
            
            # Skip if this looks like a process/area header (contains "Management" but no question words)
            question_starters = ['Is ', 'How ', 'What ', 'Does ', 'Are ', 'Can ', 'Will ']
            has_question_word = any(question_text.startswith(w) or f' {w}' in question_text for w in question_starters)
            
            # If we already have question parts that look like a question, keep building
            # Otherwise, only add if this looks like question content
            if question_text_parts or has_question_word or '?' in question_text:
                question_text_parts.append(question_text)
                # Also buffer any level content we see on these rows
                for level in ['level_1', 'level_2', 'level_3', 'level_4', 'level_5']:
                    if row_by_col[level]:
                        pending_levels[level].extend(row_by_col[level])
    
    # Don't forget the last question
    if question_text_parts and in_question:
        q_text = ' '.join(question_text_parts)
        if '?' in q_text:
            q_obj = {
                'category': current_category,
                'question': clean_text(q_text),
                'levels': {k: format_bcm_level_text(v) for k, v in current_levels.items()}
            }
            if current_note_parts:
                q_obj['note'] = clean_text(' '.join(current_note_parts))
            questions.append(q_obj)
    
    return questions


def format_bcm_level_text(text_parts):
    """
    Format BCM level text, preserving NOTE: blocks on separate lines.
    """
    if not text_parts:
        return ""
    
    # Join all parts with spaces first
    text = ' '.join(text_parts)
    
    # Insert newline before NOTE: (case-insensitive)
    text = re.sub(r'\s+(NOTE:)', r'\n\1', text, flags=re.IGNORECASE)
    
    return clean_text(text)
    
    return questions


def extract_capability_questions(lines):
    """Extract capability questions and their maturity levels from BCM content."""
    questions = []
    current_category = "Business Capability Descriptions"
    
    # BCM tables have: Question | Level 1 | Level 2 | Level 3 | Level 4 | Level 5
    # But in extracted text, they come as separate lines
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Check for category headers
        if 'Business Capability' in line:
            if 'Descriptions' in line:
                current_category = "Business Capability Descriptions"
            elif 'Timeliness' in line:
                current_category = "Business Capability Quality: Timeliness of Process"
            elif 'Data Access' in line or 'Accuracy' in line:
                current_category = "Business Capability Quality: Data Access and Accuracy"
            elif 'Cost' in line:
                current_category = "Business Capability Quality: Cost Effectiveness"
            elif 'Effort' in line or 'Efficiency' in line:
                current_category = "Business Capability Quality: Effort to Perform; Efficiency"
            i += 1
            continue
        
        # Look for questions (end with ?)
        if line.endswith('?') or (i + 1 < len(lines) and lines[i + 1].strip().endswith('?')):
            # This might be a question
            question_text = line
            
            # Check if question continues on next line
            j = i + 1
            while j < len(lines) and not lines[j].strip().endswith('?'):
                next_line = lines[j].strip()
                if not next_line or 'Level' in next_line:
                    break
                question_text += " " + next_line
                j += 1
            
            # Include the line with ?
            if j < len(lines) and lines[j].strip().endswith('?'):
                question_text += " " + lines[j].strip()
                j += 1
            
            question_text = clean_text(question_text)
            
            # Now extract the 5 levels
            levels = extract_maturity_levels(lines[j:])
            
            if question_text and levels:
                questions.append({
                    "category": current_category,
                    "question": question_text,
                    "levels": levels
                })
            
            # Skip past the levels we just processed
            i = j + 20  # Approximate skip
            continue
        
        i += 1
    
    return questions


def extract_maturity_levels(lines):
    """Extract the 5 maturity levels from BCM table content."""
    levels = {
        "level_1": "",
        "level_2": "",
        "level_3": "",
        "level_4": "",
        "level_5": ""
    }
    
    # The levels come as continuous text blocks
    # We need to identify where each level starts/ends
    
    # Combine lines into text blocks
    text = " ".join(line.strip() for line in lines[:100] if line.strip())
    
    # Look for patterns that indicate level boundaries
    # Often levels mention "Level 1", "Level 2", etc. or have distinct patterns
    
    # Simple heuristic: split roughly into 5 parts
    # This is imperfect but we'll refine based on actual content
    
    # For now, collect all text and we'll improve the parsing
    content_lines = []
    for line in lines[:50]:
        line = line.strip()
        if not line:
            continue
        if 'Part I' in line or 'Page' in line or 'May 2014' in line:
            continue
        if 'Business Capability' in line:
            break
        if line.endswith('?'):
            break
        content_lines.append(line)
    
    # Join and try to split into levels
    full_text = " ".join(content_lines)
    
    # If we have content, distribute it (this is a simplified approach)
    if full_text:
        # For now, put all in level_1 - we'll need to improve this
        # based on actual table structure analysis
        levels["level_1"] = clean_text(full_text[:500]) if len(full_text) > 500 else clean_text(full_text)
    
    return levels


# =============================================================================
# IMAGE EXTRACTION
# =============================================================================

def extract_images(pdf_path, output_dir, process_name, process_code):
    """Extract meaningful images from a PDF page range."""
    doc = fitz.open(pdf_path)
    
    extracted = []
    MIN_SIZE = 200  # Minimum dimension to be considered meaningful
    LOGO_SIZES = [(198, 76)]  # Known logo sizes to skip
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        images = page.get_images()
        
        for img_idx, img in enumerate(images):
            xref = img[0]
            try:
                base_image = doc.extract_image(xref)
                w, h = base_image['width'], base_image['height']
                
                # Skip small images and logos
                if w < MIN_SIZE or h < MIN_SIZE:
                    continue
                if (w, h) in LOGO_SIZES:
                    continue
                
                # Generate filename
                safe_name = process_name.replace(' ', '_').replace('/', '_')
                ext = base_image['ext']
                filename = f"{process_code}_{safe_name}_diagram_{page_num + 1}_{img_idx + 1}.{ext}"
                
                # Save image
                filepath = os.path.join(output_dir, filename)
                with open(filepath, 'wb') as f:
                    f.write(base_image['image'])
                
                extracted.append({
                    "filename": filename,
                    "description": f"Process diagram from page {page_num + 1}",
                    "page_reference": page_num + 1
                })
                
            except Exception as e:
                print(f"  Warning: Could not extract image: {e}")
    
    doc.close()
    return extracted


# =============================================================================
# FILE OUTPUT
# =============================================================================

def save_process_json(process_data, output_dir, doc_type):
    """Save a process to a JSON file."""
    # Generate filename
    code = process_data['process_code']
    name = process_data['process_name'].replace(' ', '_').replace('/', '_')
    filename = f"{code}_{name}_{doc_type.upper()}_v3.0.json"
    
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(process_data, f, indent=2, ensure_ascii=False)
    
    return filepath


def get_output_dir(area_name, doc_type):
    """Get the output directory for a business area."""
    # Normalize area name for directory
    dir_name = area_name.lower().replace(' ', '_')
    output_dir = os.path.join(OUTPUT_BASE, doc_type, dir_name)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def get_pdf_path(area_name, doc_type):
    """Get the PDF path for a business area."""
    # Handle variations in folder/file naming
    pdf_dir = os.path.join(SOURCE_BASE, doc_type, area_name)
    
    if not os.path.exists(pdf_dir):
        return None
    
    # Find the PDF file
    for f in os.listdir(pdf_dir):
        if f.endswith('.pdf'):
            return os.path.join(pdf_dir, f)
    
    return None


# =============================================================================
# MAIN EXTRACTION FUNCTIONS
# =============================================================================

def extract_area(area_name, doc_type, with_images=False):
    """Extract all processes from a business area."""
    print(f"\n{'='*60}")
    print(f"Extracting {doc_type.upper()}: {area_name}")
    print('='*60)
    
    # Get paths
    pdf_path = get_pdf_path(area_name, doc_type)
    if not pdf_path:
        print(f"  ERROR: PDF not found for {area_name}")
        return []
    
    output_dir = get_output_dir(area_name, doc_type)
    
    # Update source file in metadata
    rel_pdf_path = pdf_path  # Keep relative path
    
    # Extract processes
    if doc_type == 'bpt':
        processes = extract_bpt_processes(pdf_path, area_name)
    else:
        processes = extract_bcm_processes(pdf_path, area_name)
    
    print(f"  Found {len(processes)} processes")
    
    # Handle images for BPT if requested
    if doc_type == 'bpt' and with_images:
        images_dir = os.path.join(output_dir, 'images')
        os.makedirs(images_dir, exist_ok=True)
        
        # Extract images for each process based on page range
        doc = fitz.open(pdf_path)
        process_code = AREA_CODES.get(area_name, "XX")
        
        for proc in processes:
            # Get page range from metadata
            page_range = proc['metadata'].get('source_page_range', '')
            if '-' in page_range:
                start_page, end_page = map(int, page_range.split('-'))
            else:
                continue
            
            # Extract images from this page range
            extracted_images = []
            MIN_SIZE = 200  # Minimum dimension to be considered meaningful
            
            for page_num in range(start_page - 1, min(end_page, len(doc))):
                page = doc[page_num]
                images = page.get_images()
                
                for img_idx, img in enumerate(images):
                    xref = img[0]
                    try:
                        base_image = doc.extract_image(xref)
                        w, h = base_image['width'], base_image['height']
                        
                        # Skip small images (logos, borders, etc.)
                        if w < MIN_SIZE or h < MIN_SIZE:
                            continue
                        
                        # Generate filename
                        safe_name = proc['process_name'].replace(' ', '_').replace('/', '_')
                        ext = base_image['ext']
                        filename = f"{process_code}_{safe_name}_diagram_{page_num + 1}_{img_idx + 1}.{ext}"
                        
                        # Save image
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
            
            # Add extracted images to process data
            proc['process_details']['diagrams'] = extracted_images
        
        doc.close()
    
    # Save each process
    saved_files = []
    for proc in processes:
        proc['metadata']['source_file'] = rel_pdf_path
        filepath = save_process_json(proc, output_dir, doc_type)
        saved_files.append(filepath)
        print(f"  ✓ {proc['process_name']}")
    
    return saved_files


def extract_all():
    """Extract all business areas."""
    all_files = []
    
    for area_name in AREA_CODES.keys():
        # Skip Member Management (empty)
        if area_name == "Member Management":
            continue
        
        # Extract BPT
        files = extract_area(area_name, 'bpt', with_images=(area_name == "Eligibility and Enrollment Management"))
        all_files.extend(files)
        
        # Extract BCM
        files = extract_area(area_name, 'bcm')
        all_files.extend(files)
    
    return all_files


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description='Extract MITA 2014 PDF data to JSON')
    parser.add_argument('--area', type=str, help='Business area name (e.g., "Care Management")')
    parser.add_argument('--type', type=str, choices=['bpt', 'bcm'], help='Document type')
    parser.add_argument('--all', action='store_true', help='Extract all areas')
    parser.add_argument('--with-images', action='store_true', help='Extract images (BPT only)')
    
    args = parser.parse_args()
    
    if args.all:
        files = extract_all()
        print(f"\n{'='*60}")
        print(f"COMPLETE: Extracted {len(files)} files")
    elif args.area and args.type:
        files = extract_area(args.area, args.type, args.with_images)
        print(f"\n{'='*60}")
        print(f"COMPLETE: Extracted {len(files)} files")
    else:
        parser.print_help()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
