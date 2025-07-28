# main.py - Docker-compatible version for Round 1B challenge
import json
import os
import time
import glob
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

import llm
from extraction import extract_sections_from_outline
from chroma import add_sections_to_chroma, query_chroma
from dbManager import ChromaDBManager
from models import DocumentSection, PersonaJobInput, ExtractedSection

class Round1BProcessor:
    def __init__(self, persist_directory="/tmp/chroma_db_1b"):
        """Initialize the Round 1B processor with its own ChromaDB instance"""
        self.db_manager = ChromaDBManager(
            persist_directory=persist_directory,
            collection_name="round1b_sections"
        )
        self.collection = self.db_manager.get_collection()
        
    def load_input_json(self, input_path: str) -> PersonaJobInput:
        """Load and parse the input JSON file"""
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return PersonaJobInput(
                persona=data.get('persona', ''),
                job_to_be_done=data.get('job_to_be_done', ''),
                documents=data.get('documents', [])
            )
        except Exception as e:
            raise Exception(f"Error loading input JSON: {e}")
    
    def process_documents(self, input_data: PersonaJobInput, input_dir: str = "/app/input") -> List[DocumentSection]:
        """Process all documents and extract sections"""
        all_sections = []
        
        for doc_info in input_data.documents:
            pdf_path = doc_info.get('pdf_path', '')
            outline_path = doc_info.get('outline_path', '')
            
            # Convert relative paths to absolute paths within the input directory
            if not os.path.isabs(pdf_path):
                pdf_path = os.path.join(input_dir, pdf_path)
            if not os.path.isabs(outline_path):
                outline_path = os.path.join(input_dir, outline_path)
            
            print(f"Processing document: {pdf_path}")
            print(f"Using outline: {outline_path}")
            
            # Check if files exist
            if not os.path.exists(pdf_path):
                print(f"Warning: PDF file not found at {pdf_path}")
                continue
                
            if not os.path.exists(outline_path):
                print(f"Warning: Outline JSON file not found at {outline_path}")
                continue
            
            try:
                # Load outline data
                with open(outline_path, 'r', encoding='utf-8') as f:
                    outline_data = json.load(f)
                
                # Extract sections from this document
                sections = extract_sections_from_outline(pdf_path, outline_data)
                all_sections.extend(sections)
                
                print(f"Extracted {len(sections)} sections from {os.path.basename(pdf_path)}")
                
            except Exception as e:
                print(f"Error processing {pdf_path}: {e}")
                continue
        
        return all_sections
    
    def build_query_from_persona_job(self, persona: str, job_to_be_done: str) -> str:
        """Build a comprehensive query from persona and job-to-be-done"""
        return f"Persona: {persona}. Task: {job_to_be_done}"
    
    def rank_sections_by_relevance(self, query: str, top_k: int = 20) -> List[Dict]:
        """Query ChromaDB and return ranked sections"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k
            )
            
            if not results['documents'] or not results['documents'][0]:
                print("No relevant sections found.")
                return []
            
            documents = results['documents'][0]
            metadatas = results['metadatas'][0]
            distances = results.get('distances', [[]])[0]
            
            ranked_sections = []
            
            for i, (doc, meta, distance) in enumerate(zip(documents, metadatas, distances if distances else [None]*len(documents))):
                section_data = {
                    "document": os.path.basename(meta.get('document_name', 'Unknown')),
                    "page_number": meta.get('page_number', 0),
                    "section_title": meta.get('title', 'Untitled'),
                    "importance_rank": i + 1,
                    "relevance_score": 1 - distance if distance is not None else 0.0,
                    "content": doc
                }
                ranked_sections.append(section_data)
            
            return ranked_sections
            
        except Exception as e:
            print(f"Error ranking sections: {e}")
            return []
    
    def extract_subsections(self, sections: List[Dict], persona: str, max_subsections: int = 10) -> List[Dict]:
        """Extract and rank subsections from top sections"""
        subsections = []
        
        for section in sections[:5]:  # Take top 5 sections for subsection analysis
            content = section['content']
            
            # Simple subsection extraction based on paragraph breaks
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            
            for i, paragraph in enumerate(paragraphs[:3]):  # Top 3 paragraphs per section
                if len(paragraph) > 100:  # Only consider substantial paragraphs
                    try:
                        refined_text = llm.get_response(paragraph, persona)
                    except Exception as e:
                        print(f"Error processing paragraph with LLM: {e}")
                        refined_text = paragraph[:200] + "..." if len(paragraph) > 200 else paragraph
                    
                    subsection = {
                        "document": section['document'],
                        "page_number": section['page_number'],
                        "section_title": f"{section['section_title']} - Part {i+1}",
                        "refined_text": refined_text,
                        "importance_rank": len(subsections) + 1
                    }
                    subsections.append(subsection)
                    
                    if len(subsections) >= max_subsections:
                        break
            
            if len(subsections) >= max_subsections:
                break
        
        return subsections
    
    def generate_output(self, input_data: PersonaJobInput, sections: List[Dict], 
                       subsections: List[Dict], processing_time: float) -> Dict:
        """Generate the final output JSON"""
        return {
            "metadata": {
                "input_documents": [os.path.basename(doc.get('pdf_path', '')) for doc in input_data.documents],
                "persona": input_data.persona,
                "job_to_be_done": input_data.job_to_be_done,
                "processing_timestamp": datetime.now().isoformat(),
                "processing_time_seconds": round(processing_time, 2),
                "total_sections_found": len(sections)
            },
            "extracted_sections": [
                {
                    "document": section["document"],
                    "page_number": section["page_number"],
                    "section_title": section["section_title"],
                    "importance_rank": section["importance_rank"]
                }
                for section in sections
            ],
            "subsection_analysis": [
                {
                    "document": subsection["document"],
                    "page_number": subsection["page_number"],
                    "section_title": subsection["section_title"],
                    "refined_text": subsection["refined_text"],
                    "importance_rank": subsection["importance_rank"]
                }
                for subsection in subsections
            ]
        }
    
    def process_challenge(self, input_path: str, output_path: str, input_dir: str = "/app/input"):
        """Main processing function for the challenge"""
        start_time = time.time()
        
        try:
            print("=== Round 1B Processing Started ===")
            
            # Load input
            print(f"Loading input from: {input_path}")
            input_data = self.load_input_json(input_path)
            print(f"Persona: {input_data.persona}")
            print(f"Job to be done: {input_data.job_to_be_done}")
            print(f"Documents to process: {len(input_data.documents)}")
            
            # Process documents and extract sections
            print("\nExtracting sections from documents...")
            sections = self.process_documents(input_data, input_dir)
            
            if not sections:
                raise Exception("No sections were extracted from any documents")
            
            # Add sections to ChromaDB
            print(f"\nAdding {len(sections)} sections to ChromaDB...")
            add_sections_to_chroma(sections, self.collection)
            
            # Build query and rank sections
            query = self.build_query_from_persona_job(input_data.persona, input_data.job_to_be_done)
            print(f"\nQuerying with: {query}")
            
            ranked_sections = self.rank_sections_by_relevance(query, top_k=15)
            
            if not ranked_sections:
                raise Exception("No relevant sections found for the given persona and job")
            
            # Extract subsections
            print(f"\nExtracting subsections from top {min(5, len(ranked_sections))} sections...")
            subsections = self.extract_subsections(ranked_sections, input_data.persona)
            
            # Generate output
            processing_time = time.time() - start_time
            output_data = self.generate_output(input_data, ranked_sections, subsections, processing_time)
            
            # Save output
            print(f"\nSaving output to: {output_path}")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            print(f"=== Processing completed in {processing_time:.2f} seconds ===")
            print(f"Found {len(ranked_sections)} relevant sections")
            print(f"Extracted {len(subsections)} subsections")
            
        except Exception as e:
            print(f"Error during processing: {e}")
            # Create error output
            error_output = {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "processing_time_seconds": time.time() - start_time,
                "metadata": {
                    "input_documents": [],
                    "persona": "",
                    "job_to_be_done": "",
                    "processing_timestamp": datetime.now().isoformat(),
                    "processing_time_seconds": time.time() - start_time,
                    "total_sections_found": 0
                },
                "extracted_sections": [],
                "subsection_analysis": []
            }
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(error_output, f, indent=2)


def main():
    """Main function for Docker container execution"""
    input_dir = "/app/input"
    output_dir = "/app/output"
    
    # Find all JSON input files in the input directory
    input_pattern = os.path.join(input_dir, "*.json")
    input_files = glob.glob(input_pattern)
    
    if not input_files:
        print(f"No JSON input files found in {input_dir}")
        print("Please ensure input JSON files are mounted in the /app/input directory")
        return
    
    # Process each input file
    for input_file in input_files:
        try:
            print(f"\n{'='*60}")
            print(f"Processing: {os.path.basename(input_file)}")
            print(f"{'='*60}")
            
            # Generate output filename based on input filename
            input_basename = os.path.splitext(os.path.basename(input_file))[0]
            output_file = os.path.join(output_dir, f"{input_basename}_output.json")
            
            # Initialize processor and run
            processor = Round1BProcessor()
            processor.process_challenge(input_file, output_file, input_dir)
            
            print(f"Successfully processed {input_file}")
            print(f"Output saved to {output_file}")
            
        except Exception as e:
            print(f"Failed to process {input_file}: {e}")
            continue


if __name__ == "__main__":
    main()