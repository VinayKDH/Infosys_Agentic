from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from pathlib import Path

class DocumentLoader:
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
        self.embeddings = OpenAIEmbeddings()
    
    def load_pdf(self, file_path: str):
        """Load and split PDF document"""
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        return self.text_splitter.split_documents(documents)
    
    def load_text(self, file_path: str):
        """Load and split text document"""
        loader = TextLoader(file_path)
        documents = loader.load()
        return self.text_splitter.split_documents(documents)
    
    def create_embeddings(self, documents):
        """Create embeddings for documents"""
        return self.embeddings.embed_documents([doc.page_content for doc in documents])

