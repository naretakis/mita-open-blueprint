#!/usr/bin/env python3
"""
Dump BPT PDFs to text files for manual verification.

This script extracts raw text from BPT PDFs with position information
to help verify the JSON extraction accuracy.

Usage:
    python tools/dump_bpt_pdfs.py --area "Business Relationship Management"
    python tools/dump_bpt_pdfs.py --all
"""

import argparse
import fitz  # pymupdf
import os
from pathlib import Path


SOURCE_BASE = "source-pdfs/may-2014-update/bpt"
OUTPUT_DIR = "tools"

BUSINESS_AREAS = [
    "Business Relationship Management",
    "Care Management",
    "Contractor Management",
    "Eligibility and Enrollment Management",
    "Financial Management",
    "Operations Management",
    "Performance Management",
    "Plan Management",
    "Provider Management",
]

AREA_CODES = {
    "Business Relationship Management": "brm",
    "Care Management": "cm",
    "Contractor Management": "ctm",
    "Eligibility and Enrollment Management": "eem",
    "Financial Management": "fm",
    "Operations Management": "om",
    "Performance Management": "pm",
    "Plan Management": "plm",
    "Provider Management": "prm",
}


def dump_pdf_to_text(pdf_path, output_path, area_name):
    """Dump PDF content to a text file with position information."""
    doc = fitz.open(pdf_path)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("=" * 100 + "\n")
        f.write(f"{area_name.upper()} BPT - RAW DUMP FOR MANUAL JSON VERIFICATION\n")
        f.write("=" * 100 + "\n\n")
        f.write("This file contains raw text extracted from the PDF with position information.\n")
        f.write("Use this to verify the BPT JSON files are accurate.\n\n")
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            f.write("\n" + "=" * 80 + "\n")
            f.write(f"PAGE {page_num + 1}\n")
            f.write("=" * 80 + "\n")
            
            # Get text blocks with position info
            blocks = page.get_text("dict")["blocks"]
            
            for block in blocks:
                if block["type"] == 0:  # Text block
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"].strip()
                            if text:
                                x = span["bbox"][0]
                                y = span["bbox"][1]
                                f.write(f"[x={x:6.1f} y={y:6.1f}] {text}\n")
            
            # Also get plain text for easier reading
            f.write("\n--- Plain Text ---\n")
            plain_text = page.get_text()
            f.write(plain_text)
            f.write("\n")
    
    doc.close()
    print(f"  Dumped: {output_path}")


def process_area(area_name):
    """Process a single business area."""
    pdf_dir = Path(SOURCE_BASE) / area_name
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"  No PDF files found in {pdf_dir}")
        return
    
    # Use the first (and usually only) PDF file
    pdf_path = pdf_files[0]
    area_code = AREA_CODES.get(area_name, "unknown")
    output_path = Path(OUTPUT_DIR) / f"temp_{area_code}_bpt_dump.txt"
    
    dump_pdf_to_text(str(pdf_path), str(output_path), area_name)


def main():
    parser = argparse.ArgumentParser(description="Dump BPT PDFs to text files")
    parser.add_argument("--area", help="Business area to process")
    parser.add_argument("--all", action="store_true", help="Process all areas")
    args = parser.parse_args()
    
    if args.all:
        for area in BUSINESS_AREAS:
            print(f"\nProcessing: {area}")
            process_area(area)
    elif args.area:
        if args.area in BUSINESS_AREAS:
            print(f"\nProcessing: {args.area}")
            process_area(args.area)
        else:
            print(f"Unknown area: {args.area}")
            print(f"Valid areas: {', '.join(BUSINESS_AREAS)}")
    else:
        print("Please specify --area or --all")
        print(f"Valid areas: {', '.join(BUSINESS_AREAS)}")


if __name__ == "__main__":
    main()
