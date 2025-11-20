"""Document Q&A tool using RAG"""
from langchain.tools import tool
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from typing import Dict, Any
from rag.vector_store import VectorStoreManager
from app.config import settings


# Lazy initialization of vector store manager
_vector_store_manager = None

def get_vector_store_manager():
    """Get or create vector store manager"""
    global _vector_store_manager
    if _vector_store_manager is None:
        _vector_store_manager = VectorStoreManager()
    return _vector_store_manager


@tool
def query_banking_documents(question: str) -> Dict[str, Any]:
    """
    Query banking documents (terms, policies, regulations) using RAG.
    
    Args:
        question: Question about banking policies, terms, or regulations
    
    Returns:
        Dictionary with answer and source documents
    """
    try:
        # Get vector store manager
        vector_store_manager = get_vector_store_manager()
        
        # Get retriever
        retriever = vector_store_manager.get_retriever(k=3)
        
        # Create LLM
        llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.3,
            api_key=settings.OPENAI_API_KEY
        )
        
        # Create prompt template
        prompt_template = """Use the following pieces of context to answer the question about banking policies, terms, or regulations.
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        
        Context: {context}
        
        Question: {question}
        
        Answer:"""
        
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        # Create QA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True
        )
        
        # Query
        result = qa_chain.invoke({"query": question})
        
        # Extract sources
        sources = []
        if "source_documents" in result:
            for doc in result["source_documents"]:
                sources.append({
                    "content": doc.page_content[:200] + "...",
                    "source": doc.metadata.get("source", "unknown")
                })
        
        return {
            "question": question,
            "answer": result.get("result", "Unable to find answer"),
            "sources": sources,
            "confidence": "high" if sources else "low"
        }
    
    except Exception as e:
        return {
            "question": question,
            "answer": f"Error querying documents: {str(e)}",
            "sources": [],
            "confidence": "error"
        }

