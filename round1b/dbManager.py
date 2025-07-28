# db_manager.py - Centralized ChromaDB configuration
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
import os

class ChromaDBManager:
    def __init__(self, persist_directory="chroma_db", collection_name="document_sections"):
        """
        Initialize ChromaDB with persistent storage
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Ensure the directory exists
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client with proper settings
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize embedding function
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name, 
            embedding_function=self.embedding_function
        )
        
        print(f"ChromaDB initialized with persistent storage at: {os.path.abspath(persist_directory)}")
    
    def get_collection(self):
        """Return the collection instance"""
        print(f"collection = {self.collection}\n")
        return self.collection
    
    def reset_collection(self):
        """Reset the collection (delete all data)"""
        try:
            self.client.delete_collection(name=self.collection_name)
            print(f"Collection '{self.collection_name}' deleted.")
        except Exception as e:
            print(f"Collection may not exist: {e}")
        
        # Recreate collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name, 
            embedding_function=self.embedding_function
        )
        print(f"Collection '{self.collection_name}' recreated.")
    
    def get_collection_stats(self):
        """Get statistics about the collection"""
        count = self.collection.count()
        print(f"Collection '{self.collection_name}' contains {count} documents")
        return count