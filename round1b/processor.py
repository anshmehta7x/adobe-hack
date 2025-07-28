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
            pages_text[i] = doc.page_content
        
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
        """
        Extracts text starting from current_heading's page and heading,
        and continues until the next_heading is found — even if it spans multiple pages.
        """
        start_page = current_heading['page']
        end_page = next_heading['page'] if next_heading else max(pages_text.keys())

        content_parts = []
        heading_found = False

        for page_num in range(start_page, end_page + 1):
            if page_num not in pages_text:
                continue

            page_content = pages_text[page_num]
            lines = [line.strip() for line in page_content.split('\n') if line.strip()]

            if page_num == start_page:
                # Find the heading line and start after it
                try:
                    heading_index = next(i for i, line in enumerate(lines)
                                        if current_heading['text'].strip() == line.strip())
                    lines = lines[heading_index + 1:]
                    heading_found = True
                except StopIteration:
                    # If heading not found, take full page (fallback)
                    pass
            elif not heading_found:
                # If somehow heading wasn't found on its page, skip collecting content
                continue

            if next_heading:
                # Check if next heading is present on this page
                try:
                    next_index = next(i for i, line in enumerate(lines)
                                    if next_heading['text'].strip() == line.strip())
                    lines = lines[:next_index]
                    content_parts.append("\n".join(lines))
                    break  # Stop at next heading
                except StopIteration:
                    pass  # Keep full page if next heading not found

            content_parts.append("\n".join(lines))

        return "\n".join(content_parts).strip()
