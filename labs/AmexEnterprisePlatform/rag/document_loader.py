"""Document loader for banking documents"""
import os
from typing import List, Dict, Any
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


class BankingDocumentLoader:
    """Load and process banking documents for RAG"""
    
    def __init__(self, documents_dir: str = "documents"):
        self.documents_dir = documents_dir
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
    
    def load_documents(self) -> List[Document]:
        """Load all documents from the documents directory"""
        documents = []
        
        if not os.path.exists(self.documents_dir):
            os.makedirs(self.documents_dir, exist_ok=True)
            return documents
        
        for filename in os.listdir(self.documents_dir):
            file_path = os.path.join(self.documents_dir, filename)
            
            if filename.endswith('.pdf'):
                loader = PyPDFLoader(file_path)
                docs = loader.load()
                # Add metadata
                for doc in docs:
                    doc.metadata['source'] = filename
                    doc.metadata['type'] = 'pdf'
                documents.extend(docs)
            
            elif filename.endswith('.txt'):
                loader = TextLoader(file_path)
                docs = loader.load()
                for doc in docs:
                    doc.metadata['source'] = filename
                    doc.metadata['type'] = 'text'
                documents.extend(docs)
        
        return documents
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks"""
        return self.text_splitter.split_documents(documents)
    
    def load_and_split(self) -> List[Document]:
        """Load and split documents in one step"""
        documents = self.load_documents()
        return self.split_documents(documents)

