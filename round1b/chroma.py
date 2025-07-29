import uuid
from typing import List

def add_sections_to_chroma(sections, collection):
    if not sections:
        print("No sections to add to ChromaDB.")
        return
    
    documents = []
    metadatas = []
    ids = []
    
    for i, section in enumerate(sections):
        try:
            if not section.content or not section.content.strip():
                print(f"Skipping empty section: {section.section_title}")
                continue
            
            section_id = f"{section.document_name}_{section.page_number}_{i}_{uuid.uuid4().hex[:8]}"
            
            documents.append(f"{section.section_title}\n{section.content}")
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
    try:
        results = collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        if not results['documents'] or not results['documents'][0]:
            print("No relevant documents found for the query.")
            return
        
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
            
            preview_length = 300
            content_preview = doc[:preview_length]
            if len(doc) > preview_length:
                content_preview += "..."
            
            print(f"Content Preview:\n{content_preview}")
            print("─" * 80)
            
    except Exception as e:
        print(f"Error querying ChromaDB: {e}")

def search_by_metadata(collection, document_name=None, page_number=None, title_contains=None):
    try:
        where_clause = {}
        
        if document_name:
            where_clause["document_name"] = document_name
        if page_number:
            where_clause["page_number"] = page_number
        if title_contains:
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