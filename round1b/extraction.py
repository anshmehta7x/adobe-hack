# extraction.py
import re
from typing import List, Dict, Any
from models import DocumentSection
from processor import PDFContentProcessor

def extract_sections_from_outline(
    pdf_path: str, 
    outline_data: Dict[str, Any]
) -> List[DocumentSection]:
    """
    Takes 1a outline and extracts actual content for each section
    """
    # Create processor instance
    processor = PDFContentProcessor()
    
    sections = []
    outline = outline_data['outline']
    
    # Step 1: Extract all text from PDF by pages
    pages_text = processor._extract_pages_text(pdf_path)
    
    # Step 2: Process each heading in the outline
    for i, heading in enumerate(outline):
        # Get the next heading (to know where current section ends)
        next_heading = outline[i+1] if i+1 < len(outline) else None
        
        # Extract content between current and next heading
        section_content = processor._extract_section_content(
            current_heading=heading,
            next_heading=next_heading,
            pages_text=pages_text
        )
        
        # Create DocumentSection object (no parent hierarchy)
        section = DocumentSection(
            document_name=pdf_path.split('/')[-1],  # Just filename
            section_title=heading['text'],
            content=section_content,
            page_number=heading['page'],
            heading_level=heading['level'],
            parent_sections=[]  # Empty for now
        )
        
        sections.append(section)
    
    return sections