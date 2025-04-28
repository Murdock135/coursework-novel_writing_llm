import os
import glob
import textwrap
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import argparse
import re

#!/usr/bin/env python3

def create_pdf_from_txt(directory, output_pdf, title, verbose=False):
    if verbose:
        print(f"Creating PDF from .txt files in directory: {directory}")
        print(f"Output PDF: {output_pdf}")
        print(f"Title: {title}")

    c = canvas.Canvas(output_pdf, pagesize=letter)
    width, height = letter
    margin = inch

    # Draw title heading on first page
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2, height - margin, title)
    y_position = height - margin - 40
    c.setFont("Helvetica", 12)

    # Get sorted list of txt files in the directory
    def natural_sort_key(file):
        return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', file)]

    txt_files = sorted(glob.glob(os.path.join(directory, "*.txt")), key=natural_sort_key)
    if not txt_files:
        raise ValueError(f"No .txt files found in directory: {directory}")

    # Sequential part counter
    part_counter = 1

    for file in txt_files:
        if verbose:
            print(f"Processing file: {file}")
        # Generate sequential header (e.g., "Part I", "Part II", ...)
        header_text = f"Part {part_counter}"
        part_counter += 1

        # If space is low, create a new page
        if y_position < margin + 50:
            c.showPage()
            y_position = height - margin
            c.setFont("Helvetica", 12)
        # Draw part header
        c.setFont("Helvetica-Bold", 14)
        c.drawString(margin, y_position, header_text)
        y_position -= 20
        c.setFont("Helvetica", 12)

        # Read file content
        with open(file, "r") as f:
            content = f.read()
        # Split content lines and wrap long lines
        lines = content.splitlines()
        for line in lines:
            # Wrap line to fit the page width (adjust wrap width if needed)
            wrapped_lines = textwrap.wrap(line, width=90) if line else [""]
            for wrapped_line in wrapped_lines:
                if y_position < margin:
                    c.showPage()
                    y_position = height - margin
                    c.setFont("Helvetica", 12)
                c.drawString(margin, y_position, wrapped_line)
                y_position -= 15
        # Extra spacing between files
        y_position -= 20

    c.save()
    if verbose:
        print("PDF creation complete.")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Merge .txt files from a directory into a single PDF with a title heading."
    )
    parser.add_argument(
        "-d", "--directory", 
        required=True, 
        help="Directory containing .txt files"
    )
    parser.add_argument(
        "-o", "--output", 
        default="merged.pdf", 
        help="Output PDF file name (default: merged.pdf)"
    )
    parser.add_argument(
        "-t", "--title", 
        required=True, 
        help="Title heading for the PDF"
    )
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true", 
        help="Enable verbose output"
    )
    args = parser.parse_args()

    # Validate directory
    if not os.path.isdir(args.directory):
        raise ValueError(f"Directory does not exist: {args.directory}")

    create_pdf_from_txt(args.directory, args.output, args.title, args.verbose)