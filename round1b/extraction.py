from typing import List, Dict, Any
from models import DocumentSection
from processor import PDFContentProcessor

def extract_sections_from_outline(
    pdf_path: str, 
    outline_data: Dict[str, Any]
) -> List[DocumentSection]:
    """
    Takes 1a outline and extracts actual content for each section.
    Adds metadata like document name and page number.
    """
    # Create processor instance
    processor = PDFContentProcessor()
    
    sections = []
    outline = outline_data['outline']
    document_name = pdf_path.split('/')[-1]  # Extract document name from file path
    
    pages_text = processor._extract_pages_text(pdf_path)
    
    for i, heading in enumerate(outline):
        # Get the next heading (to know where current section ends)
        next_heading = outline[i+1] if i+1 < len(outline) else None
        
        section_content = processor._extract_section_content(
            current_heading=heading,
            next_heading=next_heading,
            pages_text=pages_text
        )
        
        section = DocumentSection(
            document_name=document_name,  
            section_title=heading['text'], 
            content=section_content, 
            page_number=heading['page'],  
            heading_level=heading['level'],  
            parent_sections=[]  
        )
        
        sections.append(section)
    
    return sections