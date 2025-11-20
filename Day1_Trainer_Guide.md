# Day 1 Labs - Trainer's Guide: Core Components & Architecture

## Overview
This guide provides trainers with a comprehensive breakdown of the Day 1 labs (Medium and Advanced), focusing on core components and how they work together to build functional AI agents.

---

## Module/Class/Function Reference

This section provides a quick reference guide to all classes, functions, and modules in both labs.

---

### Day 1 Medium Lab: Module Reference

#### **Module: `main.py`**
Main entry point for the Medium lab agent application.

**Global Variables:**
- `llm` (ChatOpenAI): The language model instance used for generating responses
- `conversation_history` (list): In-memory storage for conversation context
- `tools_dict` (dict): Dictionary mapping tool names to tool objects for quick lookup

**Functions:**

##### `process_input(user_input: str) -> str`
**Purpose:** Main input processing function that routes user queries to appropriate handlers.

**What it does:**
- Analyzes user input using pattern matching
- Detects calculator requests (mathematical expressions)
- Detects web search requests (keywords like "search", "find")
- Routes to appropriate tool or falls back to LLM for general conversation
- Manages conversation history (adds exchanges, maintains last 10 turns)
- Returns formatted response string

**Key Logic:**
- Uses regex patterns to extract mathematical expressions
- Uses keyword matching for search intent detection
- Builds context from conversation history for LLM calls
- Truncates history to prevent token overflow

---

#### **Module: `tools.py`**
Defines custom tools that extend the agent's capabilities.

**Functions:**

##### `calculator(expression: str) -> str`
**Purpose:** Safely evaluates mathematical expressions.

**What it does:**
- Validates input to allow only safe mathematical characters (digits, operators, parentheses)
- Prevents code injection by restricting allowed characters
- Evaluates the expression using Python's `eval()` function
- Returns formatted result string or error message

**Safety Features:**
- Character whitelist validation
- Exception handling for invalid expressions

##### `tools` (list)
**Purpose:** List of Tool objects available to the agent.

**Contains:**
- `Calculator` tool: Wraps the `calculator()` function with description
- `WebSearch` tool: Wraps DuckDuckGoSearchRun with description

**Tool Structure:**
Each tool has:
- `name`: Identifier for the tool
- `func`: The function to execute
- `description`: Natural language description used by LLM to decide when to use the tool

---

### Day 1 Advanced Lab: Module Reference

#### **Module: `main.py`**
Main entry point for the Advanced lab agent application with RAG and multi-tool support.

**Global Variables:**
- `AGENT_TYPE` (str): Type of agent framework available ("openai_tools", "react", or "simple")
- `AGENT_AVAILABLE` (bool): Whether agent framework is available
- `MEMORY_AVAILABLE` (bool): Whether advanced memory is available

**Classes:**

##### `AdvancedAgent`
**Purpose:** Main agent class that orchestrates all components (LLM, tools, memory, RAG).

**Methods:**

###### `__init__(self)`
**Purpose:** Initializes the agent with all required components.

**What it does:**
- Validates OpenAI API key presence
- Initializes ChatOpenAI LLM instance
- Creates VectorStoreManager and DocumentLoader for RAG
- Sets up all available tools via `_setup_tools()`
- Initializes ConversationSummaryBufferMemory
- Creates the agent executor via `_create_agent()`

**Error Handling:**
- Raises ValueError if API key is missing
- Falls back to simplified memory if advanced memory unavailable

###### `_setup_tools(self)`
**Purpose:** Initializes and registers all available tools.

**What it does:**
- Adds Calculator tool
- Adds WebSearch tool (via AdvancedWebSearch class)
- Adds CodeExecutor tool
- Reserves slot for DocumentQA tool (added after documents loaded)

**Error Handling:**
- Catches and logs tool initialization errors
- Continues with available tools if some fail

###### `load_documents(self, file_path: str, file_type: str = "pdf") -> str`
**Purpose:** Loads documents into the vector store and enables document Q&A capability.

**What it does:**
- Validates file existence
- Loads PDF or text documents using DocumentLoader
- Creates FAISS vector store from document chunks
- Saves vector store to disk for persistence
- Creates DocumentQATool instance
- Recreates agent with new DocumentQA tool included
- Returns success message with chunk count

**Parameters:**
- `file_path`: Path to document file
- `file_type`: "pdf" or "text" (default: "pdf")

**Returns:**
- Success message with number of chunks loaded, or error message

###### `_create_agent(self) -> AgentExecutor | SimpleAgentWrapper`
**Purpose:** Creates and configures the agent executor with tools and memory.

**What it does:**
- Checks if agent framework is available
- Creates prompt template with system instructions, chat history placeholder, and agent scratchpad
- Creates agent using available type (OpenAI tools or ReAct)
- Wraps agent in AgentExecutor with memory, error handling, and iteration limits
- Falls back to simple LLM chain if agent framework unavailable

**Returns:**
- AgentExecutor instance or SimpleAgentWrapper fallback

**Fallback Behavior:**
- If agent framework unavailable, creates simple LLMChain
- Wraps chain in SimpleAgentWrapper to match agent interface

###### `query(self, user_input: str) -> str`
**Purpose:** Processes user queries through the agent.

**What it does:**
- Invokes agent with user input
- Extracts output from agent response
- Handles errors gracefully

**Returns:**
- Agent response string or error message

###### `get_conversation_summary(self) -> str`
**Purpose:** Generates a summary of the conversation history.

**What it does:**
- Uses memory's summarization capability
- Generates condensed summary of conversation
- Handles cases where summarization unavailable

**Returns:**
- Conversation summary string or error message

---

#### **Module: `config.py`**
Centralized configuration management.

**Classes:**

##### `Config`
**Purpose:** Stores all configuration settings and environment variables.

**Class Attributes:**
- `OPENAI_API_KEY`: OpenAI API key from environment
- `LANGCHAIN_TRACING_V2`: LangSmith tracing enabled/disabled
- `LANGCHAIN_API_KEY`: LangSmith API key
- `LANGCHAIN_PROJECT`: LangSmith project name
- `VECTOR_STORE_DIR`: Directory path for vector store persistence
- `MODEL_NAME`: LLM model to use (default: "gpt-4")
- `TEMPERATURE`: LLM temperature setting (default: 0.7)
- `MAX_TOKENS`: Maximum tokens for responses (default: 2000)

**Purpose:** Provides single source of truth for all configuration values, making it easy to modify settings without changing code.

---

#### **Module: `rag/document_loader.py`**
Handles document loading and text splitting for RAG.

**Classes:**

##### `DocumentLoader`
**Purpose:** Loads documents from files and splits them into chunks suitable for embedding.

**Methods:**

###### `__init__(self, chunk_size=1000, chunk_overlap=200)`
**Purpose:** Initializes the document loader with text splitting configuration.

**What it does:**
- Creates RecursiveCharacterTextSplitter with specified chunk size and overlap
- Initializes OpenAIEmbeddings for creating embeddings

**Parameters:**
- `chunk_size`: Maximum characters per chunk (default: 1000)
- `chunk_overlap`: Characters to overlap between chunks (default: 200)

###### `load_pdf(self, file_path: str) -> List[Document]`
**Purpose:** Loads a PDF file and splits it into chunks.

**What it does:**
- Uses PyPDFLoader to extract text from PDF
- Splits document into chunks using configured text splitter
- Returns list of Document objects

**Returns:**
- List of Document chunks

###### `load_text(self, file_path: str) -> List[Document]`
**Purpose:** Loads a text file and splits it into chunks.

**What it does:**
- Uses TextLoader to load text file
- Splits document into chunks using configured text splitter
- Returns list of Document objects

**Returns:**
- List of Document chunks

###### `create_embeddings(self, documents) -> List[List[float]]`
**Purpose:** Creates embeddings for document content.

**What it does:**
- Extracts page content from documents
- Generates embeddings using OpenAI embeddings model
- Returns list of embedding vectors

**Returns:**
- List of embedding vectors (each is a list of floats)

---

#### **Module: `rag/vector_store.py`**
Manages vector storage and similarity search for RAG.

**Classes:**

##### `VectorStoreManager`
**Purpose:** Manages FAISS vector store creation, persistence, and similarity search operations.

**Methods:**

###### `__init__(self, persist_directory: str = "./vector_store")`
**Purpose:** Initializes the vector store manager.

**What it does:**
- Sets up OpenAI embeddings instance
- Configures persistence directory path
- Initializes vector_store to None (created when documents loaded)

**Parameters:**
- `persist_directory`: Directory to save/load vector store (default: "./vector_store")

###### `create_vector_store(self, documents: List[Document]) -> FAISS`
**Purpose:** Creates a FAISS vector store from document chunks.

**What it does:**
- Generates embeddings for all documents
- Creates FAISS index from documents and embeddings
- Stores reference to vector store instance

**Returns:**
- FAISS vector store instance

###### `load_vector_store(self) -> FAISS | None`
**Purpose:** Loads an existing vector store from disk.

**What it does:**
- Checks if persistence directory exists
- Loads FAISS index and embeddings from disk
- Returns vector store instance or None if not found

**Returns:**
- FAISS vector store instance or None

###### `save_vector_store(self) -> None`
**Purpose:** Saves the current vector store to disk for persistence.

**What it does:**
- Saves FAISS index and metadata to configured directory
- Enables vector store to be reused across sessions

###### `similarity_search(self, query: str, k: int = 4) -> List[Document]`
**Purpose:** Finds documents most similar to the query.

**What it does:**
- Creates embedding for query
- Searches vector store for k most similar documents
- Returns list of Document objects

**Parameters:**
- `query`: Search query string
- `k`: Number of results to return (default: 4)

**Returns:**
- List of most similar Document objects

###### `similarity_search_with_score(self, query: str, k: int = 4) -> List[Tuple[Document, float]]`
**Purpose:** Finds similar documents with relevance scores.

**What it does:**
- Performs similarity search
- Returns documents with their similarity scores
- Useful for filtering by relevance threshold

**Returns:**
- List of tuples: (Document, similarity_score)

---

#### **Module: `tools/calculator.py`**
Provides calculator tool for mathematical operations.

**Functions:**

##### `calculator(expression: str) -> str`
**Purpose:** Safely evaluates mathematical expressions.

**What it does:**
- Validates input contains only safe mathematical characters
- Evaluates expression using Python's eval()
- Returns formatted result or error message

**Safety:**
- Character whitelist prevents code injection
- Exception handling for invalid expressions

##### `get_calculator_tool() -> Tool`
**Purpose:** Creates a LangChain Tool wrapper for the calculator function.

**What it does:**
- Wraps calculator function in Tool object
- Provides name and description for agent to use
- Returns Tool instance ready for agent integration

**Returns:**
- LangChain Tool instance

---

#### **Module: `tools/code_executor.py`**
Provides safe Python code execution capability.

**Classes:**

##### `CodeExecutor`
**Purpose:** Executes Python code in a safe, controlled environment.

**Methods:**

###### `__init__(self)`
**Purpose:** Initializes the code executor.

**What it does:**
- Creates PythonREPLTool instance from LangChain experimental tools
- Sets up safe execution environment

###### `execute_python(self, code: str) -> str`
**Purpose:** Safely executes Python code with security checks.

**What it does:**
- Checks for dangerous keywords (os, sys, subprocess, eval, exec)
- Blocks potentially unsafe code
- Executes code in Python REPL tool
- Returns execution result or error message

**Security:**
- Keyword blacklist prevents dangerous operations
- Sandboxed execution environment

**Returns:**
- Execution result string or error message

###### `get_tool(self) -> Tool`
**Purpose:** Creates a LangChain Tool wrapper for code execution.

**What it does:**
- Wraps execute_python method in Tool object
- Provides description for agent decision-making
- Returns Tool instance

**Returns:**
- LangChain Tool instance

---

#### **Module: `tools/document_qa.py`**
Implements RAG-based document question answering.

**Classes:**

##### `DocumentQATool`
**Purpose:** Answers questions about loaded documents using RAG (Retrieval-Augmented Generation).

**Methods:**

###### `__init__(self, vector_store_manager: VectorStoreManager)`
**Purpose:** Initializes the document QA tool with vector store.

**What it does:**
- Stores reference to vector store manager
- Creates ChatOpenAI instance for answer generation
- Sets up RAG chain via `_setup_qa_chain()`

**Parameters:**
- `vector_store_manager`: VectorStoreManager instance with loaded documents

###### `_setup_qa_chain(self) -> None`
**Purpose:** Configures the RAG pipeline using LangChain Expression Language (LCEL).

**What it does:**
- Creates retriever from vector store (returns top 3 results)
- Defines prompt template for context-based Q&A
- Builds LCEL chain: retriever → format docs → prompt → LLM → parser
- Stores chain and retriever for use in queries

**Chain Flow:**
1. Retrieve relevant document chunks
2. Format chunks into context string
3. Create prompt with context and question
4. Generate answer using LLM
5. Parse output to string

###### `query_documents(self, question: str) -> str`
**Purpose:** Answers a question using RAG pipeline.

**What it does:**
- Validates that documents are loaded
- Invokes RAG chain with question
- Retrieves source documents for citation
- Formats answer with source citations
- Returns formatted response

**Returns:**
- Answer string with source citations, or error message

###### `get_tool(self) -> Tool`
**Purpose:** Creates a LangChain Tool wrapper for document Q&A.

**What it does:**
- Wraps query_documents method in Tool object
- Provides description for agent to decide when to use
- Returns Tool instance

**Returns:**
- LangChain Tool instance

---

#### **Module: `tools/web_search.py`**
Provides web search capability with async support.

**Classes:**

##### `AdvancedWebSearch`
**Purpose:** Searches the web for current information using DuckDuckGo.

**Methods:**

###### `__init__(self)`
**Purpose:** Initializes the web search tool.

**What it does:**
- Creates DuckDuckGoSearchRun instance from LangChain community tools

###### `search_web(self, query: str) -> str`
**Purpose:** Performs a web search and returns results.

**What it does:**
- Executes search using DuckDuckGo
- Formats results with query context
- Handles errors gracefully

**Parameters:**
- `query`: Search query string

**Returns:**
- Formatted search results or error message

###### `async_search(self, queries: List[str]) -> List[str]`
**Purpose:** Performs multiple web searches asynchronously.

**What it does:**
- Creates async tasks for each query
- Executes searches in parallel
- Returns list of results

**Parameters:**
- `queries`: List of search query strings

**Returns:**
- List of search result strings

**Use Case:** Efficiently search multiple topics in parallel

###### `get_tool(self) -> Tool`
**Purpose:** Creates a LangChain Tool wrapper for web search.

**What it does:**
- Wraps search_web method in Tool object
- Provides description for agent decision-making
- Returns Tool instance

**Returns:**
- LangChain Tool instance

---

## Summary: Module Organization

### Day 1 Medium Lab Structure
```
main.py          → Core agent logic, input processing, conversation loop
tools.py         → Tool definitions (Calculator, WebSearch)
```

### Day 1 Advanced Lab Structure
```
main.py                    → AdvancedAgent class, main entry point
config.py                  → Configuration management
rag/
  ├── document_loader.py   → DocumentLoader class
  └── vector_store.py      → VectorStoreManager class
tools/
  ├── calculator.py        → Calculator tool
  ├── code_executor.py     → CodeExecutor class
  ├── document_qa.py       → DocumentQATool class (RAG)
  └── web_search.py        → AdvancedWebSearch class
```

**Key Design Patterns:**
- **Separation of Concerns:** Each module has a single responsibility
- **Tool Wrapper Pattern:** All tools expose `get_tool()` method for consistent integration
- **Manager Pattern:** VectorStoreManager and DocumentLoader manage complex operations
- **Chain Pattern:** RAG uses LCEL chain composition for pipeline construction

---

## Day 1 Medium Lab: Core Components

### 1. **LLM (Large Language Model) - The Brain**
**Component:** `ChatOpenAI` from LangChain
**Location:** `main.py` (lines 15-19)

**What it does:**
- Provides the core intelligence and language understanding
- Processes user input and generates responses
- Acts as the decision-making engine

**Key Teaching Points:**
- **Model Selection:** Using GPT-4 for better reasoning capabilities
- **Temperature (0.7):** Controls creativity vs. determinism
  - Lower (0-0.3): More focused, deterministic
  - Higher (0.7-1.0): More creative, varied responses
- **API Key Management:** Secure handling via environment variables

**Code Pattern:**
```python
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY")
)
```

---

### 2. **Tools - The Agent's Capabilities**
**Component:** Custom Tool Functions
**Location:** `tools.py`

**What it does:**
- Extends the agent's capabilities beyond text generation
- Provides specific functions the agent can call
- Each tool has a name, function, and description

**Core Tools in Medium Lab:**

#### a) **Calculator Tool**
- **Purpose:** Performs mathematical calculations
- **Safety:** Input validation to prevent code injection
- **Pattern:** Function → Tool wrapper → Description

#### b) **Web Search Tool**
- **Purpose:** Searches the internet for current information
- **Integration:** Uses DuckDuckGoSearchRun from LangChain Community
- **Use Case:** When agent needs real-time or external information

**Key Teaching Points:**
- **Tool Description is Critical:** The LLM uses descriptions to decide when to use tools
- **Tool Structure:** `Tool(name, func, description)`
- **Error Handling:** Tools should gracefully handle failures

**Code Pattern:**
```python
Tool(
    name="Calculator",
    func=calculator,
    description="Useful for performing mathematical calculations..."
)
```

---

### 3. **Memory - Conversation Context**
**Component:** Conversation History Management
**Location:** `main.py` (lines 22, 76-108)

**What it does:**
- Maintains conversation context across multiple turns
- Allows the agent to remember previous interactions
- Enables coherent multi-turn conversations

**Implementation in Medium Lab:**
- **Simple List-Based Memory:** Stores conversation history in a list
- **Context Window Management:** Keeps last 10 exchanges (20 messages)
- **Context Injection:** Passes recent history to LLM in prompts

**Key Teaching Points:**
- **Why Memory Matters:** Without it, each turn is independent
- **Memory Limitations:** Token limits require truncation
- **Memory Types:** 
  - Buffer (stores all) - Simple but can overflow
  - Summary (compresses) - More efficient but may lose details

**Code Pattern:**
```python
conversation_history = []
# Add to history
conversation_history.append(f"User: {user_input}")
conversation_history.append(f"Assistant: {response}")
# Keep only recent history
if len(conversation_history) > 20:
    conversation_history = conversation_history[-20:]
```

---

### 4. **Input Processing & Tool Routing**
**Component:** Pattern Matching & Decision Logic
**Location:** `main.py` (lines 27-113)

**What it does:**
- Analyzes user input to determine intent
- Routes requests to appropriate tools
- Handles both tool-based and conversational queries

**Decision Flow:**
1. **Pattern Detection:** Uses regex to identify calculation or search requests
2. **Tool Execution:** Calls appropriate tool function
3. **Fallback:** Uses LLM for general conversation
4. **Context Building:** Incorporates conversation history

**Key Teaching Points:**
- **Rule-Based Routing:** Simple pattern matching for tool selection
- **Limitation:** This is a simplified approach (Advanced uses agent framework)
- **Trade-offs:** 
  - Simple: Fast, predictable
  - Agent-based: More flexible, can handle complex reasoning

**Code Pattern:**
```python
# Check for calculator
if any(op in user_input for op in ["+", "-", "*", "/"]):
    result = tools_dict["Calculator"].func(expression)
    return result

# Check for search
if "search" in user_input_lower:
    result = tools_dict["WebSearch"].func(query)
    return result

# Default: Use LLM
response = llm.invoke(prompt_text)
```

---

### 5. **Prompt Engineering**
**Component:** System Instructions & Context Formatting
**Location:** `main.py` (lines 79-95)

**What it does:**
- Defines the agent's personality and capabilities
- Structures the conversation context
- Guides the LLM's behavior

**Key Elements:**
- **System Instructions:** Define agent role and capabilities
- **Context Injection:** Includes conversation history
- **Few-Shot Examples:** (Can be added) Show desired behavior

**Key Teaching Points:**
- **Prompt Structure:** System message → Context → User input
- **Clarity Matters:** Clear instructions lead to better behavior
- **Context Management:** Balance between too little and too much context

---

## Day 1 Advanced Lab: Core Components

### 1. **RAG (Retrieval-Augmented Generation) System**

#### a) **Document Loader**
**Component:** `DocumentLoader` class
**Location:** `rag/document_loader.py`

**What it does:**
- Loads documents from various formats (PDF, text)
- Splits documents into manageable chunks
- Prepares documents for embedding

**Key Concepts:**
- **Chunking:** Breaking large documents into smaller pieces
  - `chunk_size=1000`: Size of each chunk in characters
  - `chunk_overlap=200`: Overlap between chunks (maintains context)
- **Text Splitting:** Uses RecursiveCharacterTextSplitter
  - Tries to split at natural boundaries (sentences, paragraphs)
  - Preserves semantic meaning

**Key Teaching Points:**
- **Why Chunking?** LLMs have token limits; chunks fit in context window
- **Overlap Importance:** Prevents losing context at chunk boundaries
- **Chunk Size Trade-off:**
  - Too small: Loses context
  - Too large: May exceed token limits

**Code Pattern:**
```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
documents = loader.load()
chunks = text_splitter.split_documents(documents)
```

---

#### b) **Vector Store Manager**
**Component:** `VectorStoreManager` class
**Location:** `rag/vector_store.py`

**What it does:**
- Creates embeddings for document chunks
- Stores vectors in FAISS (Facebook AI Similarity Search)
- Enables semantic search over documents

**Key Concepts:**
- **Embeddings:** Convert text to numerical vectors
  - Similar text → Similar vectors
  - Enables semantic similarity search
- **FAISS:** Efficient vector database
  - Fast similarity search
  - Can persist to disk
- **Similarity Search:** Finds relevant chunks for a query

**Key Teaching Points:**
- **Embeddings = Meaning:** Vectors capture semantic meaning
- **Similarity Search:** Finds relevant content, not just keyword matches
- **Persistence:** Vector stores can be saved and reloaded

**Code Pattern:**
```python
# Create embeddings and store
vector_store = FAISS.from_documents(
    documents=chunks,
    embedding=OpenAIEmbeddings()
)

# Search for similar content
results = vector_store.similarity_search(query, k=4)
```

---

#### c) **Document QA Tool**
**Component:** `DocumentQATool` class
**Location:** `tools/document_qa.py`

**What it does:**
- Combines retrieval (vector search) with generation (LLM)
- Answers questions based on loaded documents
- Provides source citations

**RAG Pipeline:**
1. **Query:** User asks a question
2. **Retrieval:** Find relevant document chunks (vector search)
3. **Augmentation:** Add chunks to LLM context
4. **Generation:** LLM generates answer using retrieved context

**Key Teaching Points:**
- **RAG = Retrieval + Generation:** Two-step process
- **Context Window:** Retrieved chunks fit in LLM context
- **Source Attribution:** Always cite sources for transparency
- **LCEL (LangChain Expression Language):** Modern way to build chains

**Code Pattern:**
```python
# Create RAG chain
qa_chain = (
    {
        "context": retriever | format_docs,  # Retrieve & format
        "question": RunnablePassthrough()     # Pass question
    }
    | prompt                                  # Create prompt
    | llm                                     # Generate answer
    | StrOutputParser()                       # Parse output
)

# Execute
answer = qa_chain.invoke(question)
```

---

### 2. **Advanced Tools**

#### a) **Code Executor Tool**
**Component:** `CodeExecutor` class
**Location:** `tools/code_executor.py`

**What it does:**
- Executes Python code in a safe environment
- Enables data analysis and computation
- Includes safety checks

**Key Features:**
- **PythonREPLTool:** LangChain's safe Python execution
- **Safety Checks:** Blocks dangerous operations
- **Use Cases:** Calculations, data analysis, algorithm execution

**Key Teaching Points:**
- **Security:** Always validate code before execution
- **Sandboxing:** Code runs in isolated environment
- **Error Handling:** Graceful failure for invalid code

---

#### b) **Advanced Web Search**
**Component:** `AdvancedWebSearch` class
**Location:** `tools/web_search.py`

**What it does:**
- Searches the web for current information
- Supports async operations for parallel searches
- Integrates with DuckDuckGo

**Key Features:**
- **Async Support:** Can perform multiple searches concurrently
- **Error Handling:** Graceful degradation on failures

---

### 3. **Agent Framework**
**Component:** LangChain Agent System
**Location:** `main.py` (lines 169-249)

**What it does:**
- Orchestrates tool selection and execution
- Uses LLM to reason about which tools to use
- Manages multi-step workflows

**Key Concepts:**
- **Agent Types:**
  - `CONVERSATIONAL_REACT_DESCRIPTION`: Conversational with tool use
  - `REACT`: ReAct (Reasoning + Acting) pattern
- **Agent Loop:**
  1. LLM receives user input + available tools
  2. LLM decides: Use tool or respond directly
  3. If tool: Execute tool, add result to context
  4. Repeat until final answer
- **Agent Executor:** Manages the agent loop

**Key Teaching Points:**
- **Automatic Tool Selection:** LLM chooses tools based on descriptions
- **Multi-Step Reasoning:** Agent can chain multiple tool calls
- **Error Handling:** `handle_parsing_errors=True` for robustness
- **Max Iterations:** Prevents infinite loops

**Code Pattern:**
```python
agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,
    max_iterations=5
)
response = agent_executor.invoke({"input": user_query})
```

---

### 4. **Advanced Memory Management**
**Component:** `ConversationSummaryBufferMemory`
**Location:** `main.py` (lines 101-113)

**What it does:**
- Combines buffer and summary approaches
- Keeps recent messages in full
- Summarizes older messages to save tokens

**Key Features:**
- **Token Limit:** `max_token_limit=2000` prevents overflow
- **Automatic Summarization:** Older messages compressed
- **Recent Context:** Latest messages preserved in detail

**Key Teaching Points:**
- **Hybrid Approach:** Best of both worlds
- **Token Efficiency:** More efficient than pure buffer
- **Context Preservation:** Better than pure summary

**Comparison:**
| Memory Type | Pros | Cons |
|------------|------|------|
| Buffer | Complete history | Token overflow risk |
| Summary | Token efficient | May lose details |
| SummaryBuffer | Balanced | More complex |

---

### 5. **Configuration Management**
**Component:** `Config` class
**Location:** `config.py`

**What it does:**
- Centralizes configuration
- Manages environment variables
- Provides default values

**Key Teaching Points:**
- **Separation of Concerns:** Config separate from logic
- **Environment Variables:** Secure credential management
- **Default Values:** Sensible defaults for development

---

## Lab Construction: How Components Work Together

### Day 1 Medium Lab Architecture

```
┌─────────────┐
│   User      │
│   Input     │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  Input Processor    │ ◄── Pattern Matching
│  (main.py)          │
└──────┬──────────────┘
       │
       ├──► Calculator Tool ──┐
       │                       │
       ├──► Web Search Tool ──┤
       │                       │
       └──► LLM (Direct) ──────┤
                                │
                                ▼
                        ┌───────────────┐
                        │   Response    │
                        │   Generator   │
                        └───────┬───────┘
                                │
                                ▼
                        ┌───────────────┐
                        │   Memory      │
                        │   (History)   │
                        └───────────────┘
```

**Flow:**
1. User provides input
2. Input processor analyzes intent (pattern matching)
3. Routes to appropriate tool OR LLM
4. Tool executes and returns result
5. Response generated and added to memory
6. Memory used for next turn's context

---

### Day 1 Advanced Lab Architecture

```
┌─────────────┐
│   User      │
│   Input     │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│   Agent Executor    │
│   (Orchestrator)    │
└──────┬──────────────┘
       │
       ├──► LLM (Decision Maker)
       │    │
       │    ├──► Tool Selection
       │    │
       │    └──► Response Generation
       │
       ├──► Tool 1: Calculator
       │
       ├──► Tool 2: Web Search
       │
       ├──► Tool 3: Code Executor
       │
       └──► Tool 4: Document QA
            │
            ├──► Vector Store (FAISS)
            │    │
            │    └──► Document Chunks
            │
            └──► RAG Chain
                 │
                 ├──► Retrieval (Similarity Search)
                 │
                 └──► Generation (LLM + Context)
                      │
                      ▼
            ┌─────────────────┐
            │  Memory Manager │
            │  (SummaryBuffer)│
            └─────────────────┘
```

**Flow:**
1. User provides input
2. Agent Executor receives input + memory context
3. LLM analyzes input and available tools
4. LLM decides: Use tool(s) or respond directly
5. If tool needed:
   - Execute tool
   - Add result to context
   - LLM processes result
   - Repeat if needed
6. Final response generated
7. Memory updated (with summarization if needed)

---

## Key Differences: Medium vs Advanced

| Aspect | Medium Lab | Advanced Lab |
|--------|-----------|--------------|
| **Tool Selection** | Rule-based (pattern matching) | LLM-based (agent framework) |
| **Memory** | Simple list buffer | SummaryBuffer with token limits |
| **Document Handling** | None | Full RAG system |
| **Tools** | 2 (Calculator, Web Search) | 4+ (Calculator, Web Search, Code Executor, Document QA) |
| **Architecture** | Linear processing | Agent loop with reasoning |
| **Complexity** | Low | High |
| **Flexibility** | Limited | High (can handle complex queries) |

---

## Teaching Progression

### Step 1: Understanding the Basics (Medium Lab)
1. **Start with LLM:** Show how LLM generates text
2. **Add Tools:** Extend capabilities with functions
3. **Add Memory:** Enable multi-turn conversations
4. **Pattern Matching:** Show simple routing logic

### Step 2: Building Complexity (Advanced Lab)
1. **RAG Introduction:** Why we need document retrieval
2. **Vector Stores:** How embeddings enable semantic search
3. **Agent Framework:** How LLM reasons about tool use
4. **Advanced Memory:** Managing long conversations

### Step 3: Integration & Optimization
1. **Component Interaction:** How pieces work together
2. **Error Handling:** Robustness in production
3. **Performance:** Token management, caching
4. **Observability:** Monitoring and debugging

---

## Common Student Questions & Answers

### Q1: Why do we need tools? Can't the LLM do everything?
**A:** LLMs are great at language but limited in:
- Real-time information (web search)
- Precise calculations (calculator)
- Code execution (code executor)
- Document-specific knowledge (RAG)

Tools extend capabilities beyond text generation.

### Q2: What's the difference between Medium and Advanced memory?
**A:** 
- **Medium:** Simple list, keeps all messages (can overflow)
- **Advanced:** SummaryBuffer, compresses old messages (efficient)

### Q3: How does the agent decide which tool to use?
**A:** 
- **Medium:** Pattern matching (if "search" in input → use search tool)
- **Advanced:** LLM reads tool descriptions and reasons about which tool fits the task

### Q4: What is RAG and why is it important?
**A:** RAG = Retrieval-Augmented Generation
- **Problem:** LLMs have training cutoff dates and limited context
- **Solution:** Retrieve relevant documents, add to context, then generate
- **Benefit:** Can answer questions about specific documents/domains

### Q5: Why chunk documents instead of using whole document?
**A:** 
- Token limits: LLMs have context window limits
- Precision: Smaller chunks = more relevant retrieval
- Efficiency: Faster search with smaller chunks

---

## Hands-On Exercises for Students

### Exercise 1: Add a New Tool (Medium Lab)
**Objective:** Understand tool structure
**Task:** Create a "TimeZone" tool that returns timezone info for a city
**Learning:** Tool definition, integration, description importance

### Exercise 2: Modify Chunk Size (Advanced Lab)
**Objective:** Understand RAG parameters
**Task:** Experiment with different chunk sizes (500, 1000, 2000)
**Learning:** Impact of chunk size on retrieval quality

### Exercise 3: Compare Memory Types
**Objective:** Understand memory trade-offs
**Task:** Implement both Buffer and SummaryBuffer, compare behavior
**Learning:** When to use which memory type

### Exercise 4: Tool Chaining
**Objective:** Understand agent reasoning
**Task:** Create a query that requires multiple tools
**Learning:** How agents chain tool calls

---

## Assessment Checklist

Students should be able to:
- [ ] Explain the role of each core component
- [ ] Identify when to use tools vs. direct LLM
- [ ] Understand the RAG pipeline (retrieve → augment → generate)
- [ ] Explain memory management strategies
- [ ] Create a custom tool
- [ ] Modify agent behavior through prompts
- [ ] Debug common issues (API keys, tool errors, memory overflow)

---

## Resources for Further Learning

1. **LangChain Documentation:**
   - Agents: https://python.langchain.com/docs/modules/agents/
   - Tools: https://python.langchain.com/docs/modules/tools/
   - Memory: https://python.langchain.com/docs/modules/memory/
   - RAG: https://python.langchain.com/docs/use_cases/question_answering/

2. **Key Concepts:**
   - ReAct Pattern: Reasoning + Acting
   - Vector Embeddings: Semantic similarity
   - FAISS: Efficient similarity search
   - LCEL: LangChain Expression Language

3. **Next Steps (Day 2):**
   - Multi-agent systems
   - Agent orchestration
   - State management
   - Complex workflows

---

## Conclusion

The Day 1 labs progressively build from simple rule-based systems to sophisticated agent frameworks with RAG capabilities. Understanding these core components provides the foundation for building production-ready AI agents.

**Key Takeaways:**
1. **LLM** = Intelligence engine
2. **Tools** = Extended capabilities
3. **Memory** = Context preservation
4. **RAG** = Document-aware generation
5. **Agent Framework** = Intelligent orchestration

Each component serves a specific purpose, and their integration creates powerful, capable AI systems.

