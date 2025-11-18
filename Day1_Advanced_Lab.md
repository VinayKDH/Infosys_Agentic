# Day 1 - Advanced Level Lab: Multi-Tool Agent with RAG Integration

## Lab Overview
**Duration:** 120 minutes  
**Objective:** Build an advanced conversational agent with RAG (Retrieval-Augmented Generation), multiple specialized tools, and sophisticated memory management.

## Prerequisites
- Completed Day 1 Medium Lab or equivalent experience
- Understanding of vector databases
- Familiarity with async/await in Python

## Learning Outcomes
By the end of this lab, you will:
- Implement RAG using FAISS vector store
- Create multiple specialized agent tools
- Use ConversationSummaryBufferMemory for optimal memory management
- Implement async agent execution
- Build a document-aware agent system
- Add observability with LangSmith

## Lab Setup

### Step 1: Enhanced Environment Setup
```bash
pip install langchain langchain-openai langchain-community langchain-experimental
pip install faiss-cpu chromadb tiktoken
pip install langsmith python-dotenv
pip install aiohttp asyncio
pip install pypdf beautifulsoup4
```

### Step 2: Project Structure
```
day1_advanced_lab/
├── main.py
├── tools/
│   ├── __init__.py
│   ├── calculator.py
│   ├── web_search.py
│   ├── code_executor.py
│   └── document_qa.py
├── rag/
│   ├── __init__.py
│   ├── vector_store.py
│   └── document_loader.py
├── config.py
├── .env
└── documents/
    └── sample_docs.pdf
```

## Lab Implementation

### Part 1: RAG Setup with FAISS (30 minutes)

**File: `rag/document_loader.py`**
```python
from langchain.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
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
```

**File: `rag/vector_store.py`**
```python
from langchain.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
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
```

### Part 2: Advanced Tools (40 minutes)

**File: `tools/document_qa.py`**
```python
from langchain.tools import Tool
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from rag.vector_store import VectorStoreManager
import os

class DocumentQATool:
    def __init__(self, vector_store_manager: VectorStoreManager):
        self.vector_store_manager = vector_store_manager
        self.llm = ChatOpenAI(model="gpt-4", temperature=0)
        self.qa_chain = None
        self._setup_qa_chain()
    
    def _setup_qa_chain(self):
        """Setup Retrieval QA chain"""
        if self.vector_store_manager.vector_store:
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.vector_store_manager.vector_store.as_retriever(
                    search_kwargs={"k": 3}
                ),
                return_source_documents=True
            )
    
    def query_documents(self, question: str) -> str:
        """Query documents using RAG"""
        if not self.qa_chain:
            return "Error: No documents loaded. Please load documents first."
        
        try:
            result = self.qa_chain.invoke({"query": question})
            answer = result["result"]
            sources = result.get("source_documents", [])
            
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
```

**File: `tools/code_executor.py`**
```python
from langchain.tools import Tool
from langchain_experimental.tools import PythonREPLTool
import subprocess
import sys

class CodeExecutor:
    def __init__(self):
        self.python_repl = PythonREPLTool()
    
    def execute_python(self, code: str) -> str:
        """Safely execute Python code"""
        try:
            # Basic safety check
            dangerous_keywords = ['import os', 'import sys', 'subprocess', 'eval', 'exec']
            if any(keyword in code.lower() for keyword in dangerous_keywords):
                return "Error: Potentially unsafe code detected. Use only safe Python operations."
            
            result = self.python_repl.run(code)
            return f"Execution result:\n{result}"
        except Exception as e:
            return f"Error executing code: {str(e)}"
    
    def get_tool(self) -> Tool:
        """Get LangChain tool"""
        return Tool(
            name="PythonExecutor",
            func=self.execute_python,
            description="""Useful for executing Python code and performing data analysis.
            Input should be valid Python code. Use this for calculations, data manipulation, or analysis.
            Do NOT use for file system operations or network requests."""
        )
```

**File: `tools/web_search.py`**
```python
from langchain.tools import Tool
from langchain_community.utilities import DuckDuckGoSearchRun
from langchain.agents import Tool
import asyncio
from typing import List

class AdvancedWebSearch:
    def __init__(self):
        self.search = DuckDuckGoSearchRun()
    
    def search_web(self, query: str) -> str:
        """Search the web and return results"""
        try:
            results = self.search.run(query)
            return f"Search results for '{query}':\n{results}"
        except Exception as e:
            return f"Error searching: {str(e)}"
    
    async def async_search(self, queries: List[str]) -> List[str]:
        """Perform multiple searches asynchronously"""
        tasks = [asyncio.to_thread(self.search_web, query) for query in queries]
        return await asyncio.gather(*tasks)
    
    def get_tool(self) -> Tool:
        """Get LangChain tool"""
        return Tool(
            name="WebSearch",
            func=self.search_web,
            description="""Useful for searching the internet for current information, 
            news, facts, or any information not in the loaded documents.
            Input should be a clear search query."""
        )
```

### Part 3: Advanced Agent with RAG (30 minutes)

**File: `main.py`**
```python
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationSummaryBufferMemory
from langchain.callbacks import LangChainTracer
from tools.document_qa import DocumentQATool
from tools.code_executor import CodeExecutor
from tools.web_search import AdvancedWebSearch
from tools.calculator import get_calculator_tool
from rag.vector_store import VectorStoreManager
from rag.document_loader import DocumentLoader
from config import Config
import os
from dotenv import load_dotenv

load_dotenv()

class AdvancedAgent:
    def __init__(self):
        # Initialize LLM
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize RAG components
        self.vector_store_manager = VectorStoreManager()
        self.document_loader = DocumentLoader()
        
        # Initialize tools
        self.tools = []
        self._setup_tools()
        
        # Initialize memory
        self.memory = ConversationSummaryBufferMemory(
            llm=self.llm,
            memory_key="chat_history",
            return_messages=True,
            max_token_limit=2000
        )
        
        # Initialize agent
        self.agent = self._create_agent()
    
    def _setup_tools(self):
        """Setup all available tools"""
        # Calculator
        self.tools.append(get_calculator_tool())
        
        # Web Search
        web_search = AdvancedWebSearch()
        self.tools.append(web_search.get_tool())
        
        # Code Executor
        code_executor = CodeExecutor()
        self.tools.append(code_executor.get_tool())
        
        # Document QA (will be added after documents are loaded)
        self.document_qa_tool = None
    
    def load_documents(self, file_path: str, file_type: str = "pdf"):
        """Load documents into vector store"""
        try:
            if file_type == "pdf":
                documents = self.document_loader.load_pdf(file_path)
            else:
                documents = self.document_loader.load_text(file_path)
            
            self.vector_store_manager.create_vector_store(documents)
            self.vector_store_manager.save_vector_store()
            
            # Add Document QA tool
            doc_qa = DocumentQATool(self.vector_store_manager)
            self.document_qa_tool = doc_qa.get_tool()
            
            # Recreate agent with new tool
            if self.document_qa_tool:
                self.tools.append(self.document_qa_tool)
                self.agent = self._create_agent()
            
            return f"Successfully loaded {len(documents)} document chunks."
        except Exception as e:
            return f"Error loading documents: {str(e)}"
    
    def _create_agent(self):
        """Create agent with tools and memory"""
        # Setup LangSmith tracing (optional)
        tracer = None
        if os.getenv("LANGCHAIN_TRACING_V2"):
            tracer = LangChainTracer()
        
        agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5,
            early_stopping_method="generate"
        )
        
        return agent
    
    def query(self, user_input: str):
        """Process user query"""
        try:
            response = self.agent.invoke({"input": user_input})
            return response['output']
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_conversation_summary(self):
        """Get summary of conversation"""
        return self.memory.predict_new_summary(
            self.memory.chat_memory.messages,
            ""
        )

# Main execution
if __name__ == "__main__":
    agent = AdvancedAgent()
    
    print("=" * 60)
    print("Advanced AgentAI with RAG Capabilities")
    print("=" * 60)
    print("\nAvailable capabilities:")
    print("- Document Q&A (load documents first)")
    print("- Web Search")
    print("- Python Code Execution")
    print("- Mathematical Calculations")
    print("- Conversational Memory")
    print("\nCommands:")
    print("- 'load <file_path>' - Load a document")
    print("- 'summary' - Get conversation summary")
    print("- 'exit' - Exit the agent")
    print("=" * 60)
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("\nAgentAI: Goodbye! Here's a summary of our conversation:")
            print(agent.get_conversation_summary())
            break
        
        if user_input.lower().startswith('load '):
            file_path = user_input[5:].strip()
            result = agent.load_documents(file_path)
            print(f"AgentAI: {result}")
            continue
        
        if user_input.lower() == 'summary':
            summary = agent.get_conversation_summary()
            print(f"\nConversation Summary:\n{summary}")
            continue
        
        response = agent.query(user_input)
        print(f"\nAgentAI: {response}")
```

**File: `config.py`**
```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false")
    LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY", "")
    LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "agentic-ai-lab")
    
    # Vector Store
    VECTOR_STORE_DIR = "./vector_store"
    
    # Model Configuration
    MODEL_NAME = "gpt-4"
    TEMPERATURE = 0.7
    MAX_TOKENS = 2000
```

### Part 4: Async Agent Execution (20 minutes)

**File: `async_agent.py`**
```python
import asyncio
from langchain.agents import AgentExecutor
from langchain.agents.conversational_chat.base import ConversationalChatAgent
from langchain.callbacks import AsyncCallbackHandler
from main import AdvancedAgent

class AsyncAgentHandler(AsyncCallbackHandler):
    """Custom async callback handler"""
    def __init__(self):
        self.tool_calls = []
    
    async def on_tool_start(self, serialized, input_str, **kwargs):
        self.tool_calls.append({"tool": serialized.get("name"), "input": input_str})
        print(f"[Async] Tool started: {serialized.get('name')}")

async def async_query_agent(agent: AdvancedAgent, query: str):
    """Execute agent query asynchronously"""
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None,
        lambda: agent.query(query)
    )
    return response

async def main():
    agent = AdvancedAgent()
    
    # Example: Process multiple queries concurrently
    queries = [
        "What is 2+2?",
        "Search for latest AI news",
        "Calculate the factorial of 5 using Python"
    ]
    
    tasks = [async_query_agent(agent, query) for query in queries]
    results = await asyncio.gather(*tasks)
    
    for query, result in zip(queries, results):
        print(f"\nQuery: {query}")
        print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Lab Exercises

### Exercise 1: Multi-Document RAG (20 minutes)
- Load multiple PDF documents
- Implement document source tracking
- Create a tool that can search across all documents
- Add document filtering by metadata

### Exercise 2: Tool Chaining (15 minutes)
- Create a tool that chains multiple tools together
- Example: "Analyze data from web search using Python"
- Implement error handling for tool chains

### Exercise 3: Advanced Memory (15 minutes)
- Implement entity memory to track specific entities
- Add conversation summarization at intervals
- Create a memory export/import feature

### Exercise 4: Observability (15 minutes)
- Set up LangSmith tracing
- Add custom metrics tracking
- Create a dashboard for agent performance

## Testing Scenarios

### Scenario 1: Document Q&A
1. Load a technical document (PDF)
2. Ask questions about the document content
3. Verify RAG retrieval is working
4. Check source citations

### Scenario 2: Multi-Tool Workflow
1. Ask: "Search for Python best practices, then write a Python function to demonstrate one"
2. Verify web search executes
3. Verify code executor runs the generated code
4. Check memory retains context

### Scenario 3: Complex Reasoning
1. Load financial data document
2. Ask: "Based on the document, calculate the ROI if we invest $10,000"
3. Verify agent uses DocumentQA tool first
4. Verify calculator tool for computation

## Deliverables

1. Complete implementation with all components
2. Test suite with at least 10 test cases
3. Documentation including:
   - Architecture diagram
   - Tool descriptions
   - Usage examples
4. Performance report:
   - Response times
   - Token usage
   - Tool usage statistics

## Advanced Challenges

### Challenge 1: Custom Embeddings
- Implement custom embedding model
- Compare performance with OpenAI embeddings
- Optimize for specific domain

### Challenge 2: Tool Learning
- Implement a tool that learns from past interactions
- Store tool usage patterns
- Suggest tool improvements

### Challenge 3: Multi-Modal RAG
- Add image processing capabilities
- Integrate vision models
- Create image + text RAG system

## Troubleshooting

**Issue:** FAISS installation errors
- Solution: Use `pip install faiss-cpu` for CPU-only systems

**Issue:** Memory token limit exceeded
- Solution: Adjust `max_token_limit` or use `ConversationSummaryMemory`

**Issue:** Slow RAG queries
- Solution: Reduce `k` in similarity search, use smaller chunk sizes

## Resources

- [LangChain RAG Documentation](https://python.langchain.com/docs/use_cases/question_answering/)
- [FAISS Documentation](https://github.com/facebookresearch/faiss)
- [LangSmith Tracing](https://docs.smith.langchain.com/)
- [Async LangChain](https://python.langchain.com/docs/guides/async/)

