# main.py
import json
from extraction import extract_sections_from_outline

# Your test data
pdf_path = "hackathon-task/sample-1a/Datasets/Pdfs/E0CCG5S312.pdf"
outline_json_path = "hackathon-task/sample-1a/Datasets/Output.json/E0CCG5S312.json"

# Load the JSON file
with open(outline_json_path, 'r') as f:
    outline_data = json.load(f)

# Extract sections
sections = extract_sections_from_outline(pdf_path, outline_data)

# Check results
for section in sections:
    print(f"Title: {section.section_title}")
    print(f"Content length: {len(section.content)}")
    print(f"Preview: {section.content}...")
    print("-" * 50)