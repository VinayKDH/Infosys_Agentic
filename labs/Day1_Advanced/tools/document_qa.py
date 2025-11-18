from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from rag.vector_store import VectorStoreManager
import os

class DocumentQATool:
    def __init__(self, vector_store_manager: VectorStoreManager):
        self.vector_store_manager = vector_store_manager
        self.llm = ChatOpenAI(model="gpt-4", temperature=0)
        self.qa_chain = None
        self._setup_qa_chain()
    
    def _setup_qa_chain(self):
        """Setup Retrieval QA chain using LCEL"""
        if self.vector_store_manager.vector_store:
            retriever = self.vector_store_manager.vector_store.as_retriever(
                search_kwargs={"k": 3}
            )
            
            # Create prompt template
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a helpful assistant that answers questions based on the provided context.
                Use only the information from the context to answer. If the answer is not in the context, say so."""),
                ("human", "Context: {context}\n\nQuestion: {question}")
            ])
            
            # Create chain using LCEL
            def format_docs(docs):
                return "\n\n".join(doc.page_content for doc in docs)
            
            self.qa_chain = (
                {
                    "context": retriever | format_docs,
                    "question": RunnablePassthrough()
                }
                | prompt
                | self.llm
                | StrOutputParser()
            )
            self.retriever = retriever
    
    def query_documents(self, question: str) -> str:
        """Query documents using RAG"""
        if not self.qa_chain:
            return "Error: No documents loaded. Please load documents first."
        
        try:
            # Get answer
            answer = self.qa_chain.invoke(question)
            
            # Get source documents
            sources = self.retriever.invoke(question)
            
            response = f"Answer: {answer}\n\n"
            if sources:
                response += "Sources:\n"
                for i, doc in enumerate(sources[:2], 1):
                    response += f"{i}. {doc.page_content[:200]}...\n"
            
            return response
        except Exception as e:
            return f"Error querying documents: {str(e)}"
    
    def get_tool(self) -> Tool:
        """Get LangChain tool"""
        return Tool(
            name="DocumentQA",
            func=self.query_documents,
            description="""Useful for answering questions based on loaded documents.
            Use this when the user asks about information that might be in the documents.
            Input should be a clear question about the document content."""
        )

