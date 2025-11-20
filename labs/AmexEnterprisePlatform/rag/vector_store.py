"""Vector store management for banking documents"""
import os
from typing import List, Optional
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from app.config import settings


class VectorStoreManager:
    """Manage FAISS vector store for banking documents"""
    
    def __init__(self, persist_directory: str = "vector_store"):
        self.persist_directory = persist_directory
        if settings.OPENAI_API_KEY:
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=settings.OPENAI_API_KEY
            )
        else:
            self.embeddings = None
        self.vector_store: Optional[FAISS] = None
    
    def create_vector_store(self, documents: List[Document]) -> FAISS:
        """Create a new vector store from documents"""
        if not documents:
            raise ValueError("No documents provided")
        
        if not self.embeddings:
            raise ValueError("OpenAI API key not configured. Cannot create embeddings.")
        
        self.vector_store = FAISS.from_documents(
            documents=documents,
            embedding=self.embeddings
        )
        
        # Save to disk
        os.makedirs(self.persist_directory, exist_ok=True)
        self.vector_store.save_local(self.persist_directory)
        
        return self.vector_store
    
    def load_vector_store(self) -> Optional[FAISS]:
        """Load vector store from disk"""
        if os.path.exists(self.persist_directory):
            try:
                self.vector_store = FAISS.load_local(
                    self.persist_directory,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                return self.vector_store
            except Exception as e:
                print(f"Error loading vector store: {e}")
                return None
        return None
    
    def get_retriever(self, k: int = 4) -> BaseRetriever:
        """Get a retriever from the vector store"""
        if self.vector_store is None:
            self.vector_store = self.load_vector_store()
        
        if self.vector_store is None:
            # Return a dummy retriever that returns empty results
            # This allows the system to work even without documents loaded
            from langchain_core.retrievers import BaseRetriever
            from langchain_core.documents import Document
            
            class DummyRetriever(BaseRetriever):
                def _get_relevant_documents(self, query: str):
                    return [Document(page_content="No documents loaded. Please initialize RAG system.")]
            
            return DummyRetriever()
        
        return self.vector_store.as_retriever(search_kwargs={"k": k})
    
    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """Perform similarity search"""
        if self.vector_store is None:
            self.vector_store = self.load_vector_store()
        
        if self.vector_store is None:
            return []
        
        return self.vector_store.similarity_search(query, k=k)
    
    def similarity_search_with_score(self, query: str, k: int = 4) -> List[tuple]:
        """Perform similarity search with scores"""
        if self.vector_store is None:
            self.vector_store = self.load_vector_store()
        
        if self.vector_store is None:
            return []
        
        return self.vector_store.similarity_search_with_score(query, k=k)

