from dbManager import ChromaDBManager
import os

def inspect_database():
    db_manager = ChromaDBManager()
    collection = db_manager.get_collection()
    
    print("=" * 120)
    print("COMPLETE CHROMADB DATABASE INSPECTION")
    print("=" * 120)
    
    count = db_manager.get_collection_stats()
    
    if count == 0:
        print("Database is empty.")
        return
    
    try:
        all_results = collection.get()
        
        print(f"\nTotal documents in database: {len(all_results['documents'])}")
        print("\nFULL DATABASE CONTENTS:")
        print("=" * 120)
        
        header = f"{'ID':<40} | {'Title':<30} | {'Doc Name':<20} | {'Page':<5} | {'Length':<8} | {'Preview':<30}"
        print(header)
        print("-" * 120)
        
        for i, (doc, meta, doc_id) in enumerate(zip(
            all_results['documents'], 
            all_results['metadatas'], 
            all_results['ids']
        )):
            title = str(meta.get('title', 'N/A'))[:28] + ('...' if len(str(meta.get('title', 'N/A'))) > 28 else '')
            doc_name = str(meta.get('document_name', 'N/A'))[:18] + ('...' if len(str(meta.get('document_name', 'N/A'))) > 18 else '')
            page = str(meta.get('page_number', 'N/A'))
            length = str(meta.get('content_length', 0))
            preview = doc[:28].replace('\n', ' ') + ('...' if len(doc) > 28 else '')
            
            row = f"{doc_id[:38]:<40} | {title:<30} | {doc_name:<20} | {page:<5} | {length:<8} | {preview:<30}"
            print(row)
            
    except Exception as e:
        print(f"Error retrieving documents: {e}")

def view_full_document():
    db_manager = ChromaDBManager()
    collection = db_manager.get_collection()
    
    count = db_manager.get_collection_stats()
    if count == 0:
        print("Database is empty.")
        return
    
    try:
        all_results = collection.get()
        print("\nAvailable Document IDs:")
        print("-" * 50)
        for i, (meta, doc_id) in enumerate(zip(all_results['metadatas'], all_results['ids'])):
            print(f"{i+1:3}. {doc_id} - {meta.get('title', 'N/A')}")
        
        choice = input(f"\nEnter document number (1-{len(all_results['ids'])}): ").strip()
        
        try:
            doc_index = int(choice) - 1
            if 0 <= doc_index < len(all_results['documents']):
                doc = all_results['documents'][doc_index]
                meta = all_results['metadatas'][doc_index]
                doc_id = all_results['ids'][doc_index]
                
                print("\n" + "=" * 100)
                print("FULL DOCUMENT CONTENT")
                print("=" * 100)
                print(f"ID: {doc_id}")
                print(f"Title: {meta.get('title', 'N/A')}")
                print(f"Document: {meta.get('document_name', 'N/A')}")
                print(f"Page: {meta.get('page_number', 'N/A')}")
                print(f"Content Length: {meta.get('content_length', 0)} characters")
                print("-" * 100)
                print("CONTENT:")
                print("-" * 100)
                print(doc)
                print("=" * 100)
            else:
                print("Invalid selection.")
        except ValueError:
            print("Please enter a valid number.")
            
    except Exception as e:
        print(f"Error retrieving documents: {e}")


def reset_database():
    response = input("Are you sure you want to delete all data? (yes/no): ")
    if response.lower() == 'yes':
        db_manager = ChromaDBManager()
        db_manager.reset_collection()
        print("Database has been reset.")
    else:
        print("Reset cancelled.")

def test_query():
    db_manager = ChromaDBManager()
    collection = db_manager.get_collection()
    
    count = db_manager.get_collection_stats()
    if count == 0:
        print("Database is empty. Please add some documents first.")
        return
    
    query = input("Enter your query: ")
    if query.strip():
        from chroma import query_chroma
        query_chroma(query, collection, top_k=8)
    else:
        print("Empty query provided.")

def check_storage_location():
    persist_dir = "chroma_db"
    abs_path = os.path.abspath(persist_dir)
    
    print(f"ChromaDB storage location: {abs_path}")
    
    if os.path.exists(abs_path):
        print("✅ Storage directory exists")
        
        contents = os.listdir(abs_path)
        if contents:
            print("Contents:")
            for item in contents:
                item_path = os.path.join(abs_path, item)
                if os.path.isfile(item_path):
                    size = os.path.getsize(item_path)
                    print(f"  📄 {item} ({size} bytes)")
                else:
                    print(f"  📁 {item}/")
        else:
            print("Directory is empty")
    else:
        print("❌ Storage directory does not exist yet")

def main():
    while True:
        print("\n" + "=" * 50)
        print("CHROMADB UTILITIES - COMPLETE DATABASE VIEWER")
        print("=" * 50)
        print("1. View complete database (table format)")
        print("3. View full content of specific document")
        print("4. Check storage location") 
        print("5. Test query")
        print("6. Reset database")
        print("9. Exit")
        
        choice = input("\nEnter your choice (1-9): ").strip()
        
        if choice == '1':
            inspect_database()
        elif choice == '3':
            view_full_document()
        elif choice == '4':
            check_storage_location()
        elif choice == '5':
            test_query()
        elif choice == '6':
            reset_database()
        elif choice == '9':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()