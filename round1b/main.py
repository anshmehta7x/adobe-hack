# main.py - Fixed version with proper ChromaDB configuration
import json
import time
import os
from extraction import extract_sections_from_outline
from chroma import add_sections_to_chroma, query_chroma
from dbManager import ChromaDBManager

def main():
    # Initialize ChromaDB with persistent storage
    db_manager = ChromaDBManager(
        persist_directory="chroma_db",
        collection_name="document_sections"
    )
    collection = db_manager.get_collection()
    print(collection)
    
    existing_count = db_manager.get_collection_stats()
    
    # Test data paths
    pdf_path = "../hackathon-task/sample-1a/Datasets/Pdfs/E0CCG5S312.pdf"
    outline_json_path = "../hackathon-task/sample-1a/Datasets/Output.json/E0CCG5S312.json"
    
    # Check if files exist
    if not os.path.exists(pdf_path):
        print(f"Warning: PDF file not found at {pdf_path}")
        return
    
    if not os.path.exists(outline_json_path):
        print(f"Warning: JSON file not found at {outline_json_path}")
        return
    
    # Load outline data
    with open(outline_json_path, 'r') as f:
        outline_data = json.load(f)
    
    # Extract sections
    print("Extracting sections from PDF...")
    start_time = time.time()
    sections = extract_sections_from_outline(pdf_path, outline_data)
    extraction_time = time.time() - start_time
    print(f"Section extraction took {extraction_time:.2f} seconds.")
    print(f"Extracted {len(sections)} sections")
    
    # Add sections to ChromaDB only if we have new sections
    if sections:
        print("Adding sections to ChromaDB...")
        start_time = time.time()
        add_sections_to_chroma(sections, collection)
        add_time = time.time() - start_time
        print(f"Adding sections to ChromaDB took {add_time:.2f} seconds.")
        
        # Verify data was added
        db_manager.get_collection_stats()
    

if __name__ == "__main__":
    main()