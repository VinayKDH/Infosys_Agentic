"""Initialize RAG system with banking documents"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.document_loader import BankingDocumentLoader
from rag.vector_store import VectorStoreManager


def main():
    """Initialize RAG system"""
    print("Loading banking documents...")
    
    # Load documents
    loader = BankingDocumentLoader(documents_dir="documents")
    documents = loader.load_and_split()
    
    if not documents:
        print("No documents found in documents/ directory.")
        print("Please add PDF or TXT files to the documents/ directory.")
        return
    
    print(f"Loaded {len(documents)} document chunks")
    
    # Create vector store
    print("Creating vector store...")
    vector_store_manager = VectorStoreManager()
    vector_store = vector_store_manager.create_vector_store(documents)
    
    print(f"Vector store created successfully!")
    print(f"Documents indexed: {len(documents)} chunks")
    print("RAG system is ready to use.")


if __name__ == "__main__":
    main()

