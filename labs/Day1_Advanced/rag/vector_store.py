from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from typing import List
import os

class VectorStoreManager:
    def __init__(self, persist_directory: str = "./vector_store"):
        self.embeddings = OpenAIEmbeddings()
        self.persist_directory = persist_directory
        self.vector_store = None
    
    def create_vector_store(self, documents: List[Document]):
        """Create FAISS vector store from documents"""
        self.vector_store = FAISS.from_documents(
            documents=documents,
            embedding=self.embeddings
        )
        return self.vector_store
    
    def load_vector_store(self):
        """Load existing vector store"""
        if os.path.exists(self.persist_directory):
            self.vector_store = FAISS.load_local(
                self.persist_directory,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
        return self.vector_store
    
    def save_vector_store(self):
        """Save vector store to disk"""
        if self.vector_store:
            self.vector_store.save_local(self.persist_directory)
    
    def similarity_search(self, query: str, k: int = 4):
        """Search for similar documents"""
        if not self.vector_store:
            return []
        return self.vector_store.similarity_search(query, k=k)
    
    def similarity_search_with_score(self, query: str, k: int = 4):
        """Search with relevance scores"""
        if not self.vector_store:
            return []
        return self.vector_store.similarity_search_with_score(query, k=k)

