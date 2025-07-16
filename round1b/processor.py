# processor.py
import re
from typing import List, Dict, Any
from models import DocumentSection

class PDFContentProcessor:
    def __init__(self):
        pass
    
    def _extract_pages_text(self, pdf_path: str) -> Dict[int, str]:
        """Extract text from each page"""
        pages_text = {}
        
        from langchain_community.document_loaders import PyPDFLoader
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        
        for i, doc in enumerate(documents):
            pages_text[i + 1] = doc.page_content
        
        return pages_text
    
    def _remove_heading_from_content(self, content: str, heading: str) -> str:
        """Remove heading text from beginning of content"""
        lines = content.split('\n')
        result_lines = []
        heading_found = False
        
        for line in lines:
            if not heading_found and heading.strip() in line:
                heading_found = True
                continue
            elif heading_found:
                result_lines.append(line)
        
        return '\n'.join(result_lines) if heading_found else content
    
    def _stop_before_heading(self, content: str, next_heading: str) -> str:
        """Stop content extraction before next heading"""
        lines = content.split('\n')
        result_lines = []
        
        for line in lines:
            if next_heading.strip() in line:
                break
            result_lines.append(line)
        
        return '\n'.join(result_lines)
    
    def _extract_section_content(
        self, 
        current_heading: Dict, 
        next_heading: Dict, 
        pages_text: Dict[int, str]
    ) -> str:
        """Extract content between current heading and next heading"""
        start_page = current_heading['page']
        end_page = next_heading['page'] if next_heading else max(pages_text.keys())
        
        content_parts = []
        
        for page_num in range(start_page, end_page + 1):
            if page_num in pages_text:
                page_content = pages_text[page_num]
                
                if page_num == start_page:
                    page_content = self._remove_heading_from_content(
                        page_content, current_heading['text']
                    )
                
                if page_num == end_page and next_heading:
                    page_content = self._stop_before_heading(
                        page_content, next_heading['text']
                    )
                
                content_parts.append(page_content)
        
        return ' '.join(content_parts).strip()