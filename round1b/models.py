# models.py
from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime

@dataclass
class DocumentSection:
    document_name: str
    section_title: str
    content: str
    page_number: int
    heading_level: str
    parent_sections: List[str]

@dataclass
class PersonaJobInput:
    persona: str
    job_to_be_done: str
    documents: List[str]

@dataclass
class ExtractedSection:
    document: str
    section_title: str
    importance_rank: int
    page_number: int
    relevance_score: float = 0.0

# You can also add utility functions here
def create_section_id(document_name: str, page: int, index: int) -> str:
    """Create unique ID for a section"""
    return f"{document_name}_{page}_{index}"