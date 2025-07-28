# extraction.py (or the file where extract_sections_from_outline is defined)

from typing import List, Dict, Any
from models import DocumentSection
from processor import PDFContentProcessor # Make sure this import is correct

def extract_sections_from_outline(
    pdf_path: str,
    outline_data: Dict[str, Any]
) -> List[DocumentSection]:
    """
    Takes a PDF path and outline data, extracts actual content for each section.
    Adds metadata like document name and page number.
    """
    # Create processor instance
    processor = PDFContentProcessor()

    sections = []
    outline = outline_data['outline']
    document_name = pdf_path.split('/')[-1]  # Extract document name from file path

    # This is crucial: Extract all pages text ONCE
    pages_text = processor._extract_pages_text(pdf_path)

    for i, heading in enumerate(outline):
        # Get the next heading (to know where current section ends)
        # This part of the logic is correct as per your initial design
        next_heading = outline[i+1] if i+1 < len(outline) else None

        # Call the internal processor method with the necessary arguments
        # The fix for content extraction goes INSIDE this _extract_section_content method
        section_content = processor._extract_section_content(
            current_heading=heading,
            next_heading=next_heading,
            pages_text=pages_text # Pass the full pages_text here
        )

        section = DocumentSection(
            document_name=document_name,
            section_title=heading['text'],
            content=section_content,
            page_number=heading['page'],
            heading_level=heading['level'],
            parent_sections=[] # This might need to be populated if you build a hierarchy
        )

        sections.append(section)

    return sections