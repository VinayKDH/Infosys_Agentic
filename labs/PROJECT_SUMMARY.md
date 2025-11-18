# Lab Projects Summary

## Overview

This directory contains **6 fully functional lab projects** for the 3-day Agentic AI Training program. Each lab is self-contained with complete source code, dependencies, and documentation.

## Project Structure

```
labs/
├── Day1_Medium/          # Basic conversational agent
├── Day1_Advanced/        # Multi-tool agent with RAG
├── Day2_Medium/          # Multi-agent research system
├── Day2_Advanced/        # Complex multi-agent system
├── Day3_Medium/          # FastAPI deployment
├── Day3_Advanced/        # Production-ready API
├── README.md             # Main lab guide
└── ENV_SETUP.md          # Environment setup guide
```

## Day 1 Labs

### Day1_Medium - Conversational Agent
**Files:**
- `main.py` - Main application entry point
- `tools.py` - Calculator and web search tools
- `requirements.txt` - Python dependencies
- `README.md` - Setup and usage instructions

**Features:**
- LangChain agent with memory
- Custom tools (calculator, web search)
- Conversation continuity

### Day1_Advanced - Multi-Tool Agent with RAG
**Files:**
- `main.py` - Advanced agent application
- `config.py` - Configuration management
- `tools/` - Multiple specialized tools
  - `calculator.py`
  - `web_search.py`
  - `code_executor.py`
  - `document_qa.py`
- `rag/` - RAG implementation
  - `document_loader.py`
  - `vector_store.py`
- `requirements.txt`
- `README.md`

**Features:**
- RAG with FAISS vector store
- Multiple specialized tools
- Document Q&A capabilities
- Code execution
- Advanced memory management

## Day 2 Labs

### Day2_Medium - Multi-Agent Research System
**Files:**
- `main.py` - Application entry point
- `state.py` - Graph state definition
- `agents/` - Agent implementations
  - `researcher.py`
  - `summarizer.py`
- `graph/` - LangGraph implementation
  - `research_graph.py`
- `requirements.txt`
- `README.md`

**Features:**
- LangGraph workflow
- Two-agent collaboration
- State management
- Research and summarization pipeline

### Day2_Advanced - Complex Multi-Agent System
**Files:**
- `main.py` - Main application
- `state.py` - Advanced state schema
- `agents/` - Four specialized agents
  - `planner.py`
  - `researcher.py`
  - `coder.py`
  - `reviewer.py`
- `graph/` - Multi-agent graph
  - `multi_agent_graph.py`
- `utils/` - Utility functions
  - `routing.py`
- `requirements.txt`
- `README.md`

**Features:**
- 4-agent collaborative system
- Dynamic task planning
- Code generation
- Quality review process
- Checkpoint-based state management

## Day 3 Labs

### Day3_Medium - FastAPI Deployment
**Files:**
- `app/` - FastAPI application
  - `main.py` - FastAPI app setup
  - `models.py` - Pydantic models
  - `agent_service.py` - Agent service layer
  - `routes/` - API routes
    - `agent.py` - Agent endpoints
- `requirements.txt`
- `README.md`

**Features:**
- FastAPI REST API
- Async endpoints
- Streaming responses
- Session management
- Interactive API docs

### Day3_Advanced - Production-Ready API
**Files:**
- `app/` - Production FastAPI app
  - `main.py` - Main application
  - `config.py` - Configuration
  - `models.py` - Data models
  - `agent_service.py` - Agent service
  - `cache.py` - Redis caching
  - `monitoring.py` - Prometheus metrics
  - `routes/` - API routes
    - `agent.py`
    - `auth.py`
    - `metrics.py`
- `docker/` - Docker configuration
  - `Dockerfile`
  - `docker-compose.yml`
- `requirements.txt`
- `README.md`

**Features:**
- Docker containerization
- Redis caching
- Authentication (JWT)
- Rate limiting
- Prometheus metrics
- Health checks
- Structured logging

## Quick Start

1. **Choose a lab** from the directory
2. **Navigate to the lab folder**:
   ```bash
   cd labs/Day1_Medium
   ```
3. **Set up environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
4. **Create `.env` file** (see ENV_SETUP.md)
5. **Run the application**:
   ```bash
   python main.py
   ```

## Dependencies Summary

### Common Dependencies
- `langchain` - LangChain framework
- `langchain-openai` - OpenAI integration
- `langchain-community` - Community tools
- `python-dotenv` - Environment variables

### Day 1 Advanced
- `faiss-cpu` - Vector store
- `langchain-experimental` - Experimental features
- `pypdf` - PDF processing

### Day 2 Labs
- `langgraph` - Graph-based workflows

### Day 3 Labs
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation

### Day 3 Advanced
- `redis` - Caching
- `prometheus-client` - Metrics
- `python-jose` - JWT tokens
- `passlib` - Password hashing

## Testing

Each lab can be tested independently:

1. **Day 1 Labs**: Interactive command-line interface
2. **Day 2 Labs**: Query-based research system
3. **Day 3 Labs**: REST API endpoints (test with curl or Postman)

## Next Steps

After completing the labs:
1. Review the code structure
2. Experiment with modifications
3. Try the exercises in the lab documentation
4. Build your own agentic AI applications

## Support

- Refer to individual lab README files for detailed instructions
- Check ENV_SETUP.md for environment configuration
- Review the main lab documentation files for concepts and exercises

