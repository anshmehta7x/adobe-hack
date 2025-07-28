import uuid
from typing import List

def add_sections_to_chroma(sections, collection):
    """
    Add extracted sections to ChromaDB with improved error handling.
    :param sections: List of extracted sections.
    :param collection: ChromaDB collection instance.
    """
    if not sections:
        print("No sections to add to ChromaDB.")
        return
    
    documents = []
    metadatas = []
    ids = []
    
    for i, section in enumerate(sections):
        try:
            # Ensure content is not empty
            if not section.content or not section.content.strip():
                print(f"Skipping empty section: {section.section_title}")
                continue
            
            # Create unique ID
            section_id = f"{section.document_name}_{section.page_number}_{i}_{uuid.uuid4().hex[:8]}"
            
            documents.append(section.content)
            metadatas.append({
                "title": section.section_title or "Untitled",
                "content_length": len(section.content),
                "document_name": section.document_name or "Unknown",
                "page_number": section.page_number or 0,
                "heading_level": getattr(section, 'heading_level', 'unknown'),
                "section_index": i
            })
            ids.append(section_id)
            
        except Exception as e:
            print(f"Error processing section {i}: {e}")
            continue
    
    if not documents:
        print("No valid documents to add after filtering.")
        return
    
    try:
        # Add to ChromaDB in batches if needed
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i+batch_size]
            batch_metas = metadatas[i:i+batch_size]
            batch_ids = ids[i:i+batch_size]
            
            collection.add(
                documents=batch_docs,
                metadatas=batch_metas,
                ids=batch_ids
            )
            
        print(f"Successfully added {len(documents)} sections to ChromaDB.")
        
    except Exception as e:
        print(f"Error adding sections to ChromaDB: {e}")

def query_chroma(query, collection, top_k=5):
    """
    Query ChromaDB for the most relevant sections with improved formatting.
    :param query: Query text (e.g., persona + job-to-be-done).
    :param collection: ChromaDB collection instance.
    :param top_k: Number of top results to retrieve.
    """
    try:
        # Perform similarity search
        results = collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        if not results['documents'] or not results['documents'][0]:
            print("No relevant documents found for the query.")
            return
        
        # Format and print results
        documents = results['documents'][0]
        metadatas = results['metadatas'][0]
        distances = results.get('distances', [[]])[0]
        
        print(f"Found {len(documents)} relevant sections:\n")
        
        for i, (doc, meta, distance) in enumerate(zip(documents, metadatas, distances if distances else [None]*len(documents))):
            print(f"RESULT {i+1}")
            print(f"Title: {meta.get('title', 'Untitled')}")
            print(f"Document: {meta.get('document_name', 'Unknown')}")
            print(f"Page: {meta.get('page_number', 'Unknown')}")
            print(f"Content Length: {meta.get('content_length', 0)} characters")
            if distance is not None:
                print(f"Similarity Score: {1 - distance:.4f}")
            
            # Show preview of content
            preview_length = 300
            content_preview = doc[:preview_length]
            if len(doc) > preview_length:
                content_preview += "..."
            
            print(f"Content Preview:\n{content_preview}")
            print("─" * 80)
            
    except Exception as e:
        print(f"Error querying ChromaDB: {e}")

def search_by_metadata(collection, document_name=None, page_number=None, title_contains=None):
    """
    Search by metadata filters
    """
    try:
        where_clause = {}
        
        if document_name:
            where_clause["document_name"] = document_name
        if page_number:
            where_clause["page_number"] = page_number
        if title_contains:
            # ChromaDB doesn't support contains, so we'll get all and filter
            pass
        
        if where_clause:
            results = collection.get(where=where_clause)
            print(f"Found {len(results['documents'])} documents matching criteria")
            return results
        else:
            print("No search criteria provided")
            return None
            
    except Exception as e:
        print(f"Error searching by metadata: {e}")
        return None