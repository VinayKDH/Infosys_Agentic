# Agentic AI Training - Labs Index

## Overview
This document provides an index of all lab exercises for the 3-day Agentic AI Training program. Each day has two lab levels: **Medium** and **Advanced**.

## Lab Structure

### Day 1: Foundations of Agentic AI & LangChain Core

#### Day 1 - Medium Level Lab
**File:** `Day1_Medium_Lab.md`  
**Duration:** 90 minutes  
**Focus:** Building a Conversational Agent with LangChain

**Key Topics:**
- LangChain environment setup
- Prompt templates and few-shot learning
- Conversation memory (ConversationBufferMemory)
- Custom tools integration (calculator, web search)
- Basic agent chain implementation

**Learning Outcomes:**
- Set up LangChain environment
- Create prompt templates
- Implement conversation memory
- Integrate custom tools
- Build functional conversational agent

**Prerequisites:**
- Python 3.11+
- OpenAI API key
- Basic Python knowledge

---

#### Day 1 - Advanced Level Lab
**File:** `Day1_Advanced_Lab.md`  
**Duration:** 120 minutes  
**Focus:** Multi-Tool Agent with RAG Integration

**Key Topics:**
- RAG implementation with FAISS vector store
- Multiple specialized agent tools
- ConversationSummaryBufferMemory
- Async agent execution
- Document-aware agent system
- LangSmith observability

**Learning Outcomes:**
- Implement RAG using FAISS
- Create multiple specialized tools
- Use advanced memory management
- Implement async execution
- Build document-aware agents
- Add observability

**Prerequisites:**
- Completed Day 1 Medium Lab
- Understanding of vector databases
- Familiarity with async/await

---

### Day 2: Building and Orchestrating Agents with LangGraph

#### Day 2 - Medium Level Lab
**File:** `Day2_Medium_Lab.md`  
**Duration:** 90 minutes  
**Focus:** Multi-Agent Research System with LangGraph

**Key Topics:**
- LangGraph concepts (nodes, edges, state)
- Graph-based agent workflows
- Multi-agent collaboration
- State management across agents
- Conditional routing and flow control
- LangSmith integration

**Learning Outcomes:**
- Understand LangGraph architecture
- Build graph-based workflows
- Implement multi-agent systems
- Manage state across interactions
- Add conditional routing
- Integrate observability

**Prerequisites:**
- Completed Day 1 labs
- Understanding of graph workflows
- Basic state machine knowledge

---

#### Day 2 - Advanced Level Lab
**File:** `Day2_Advanced_Lab.md`  
**Duration:** 120 minutes  
**Focus:** Complex Multi-Agent System with Advanced State Management

**Key Topics:**
- 4-agent collaborative system (Planner, Researcher, Coder, Reviewer)
- Advanced LangGraph features (human-in-the-loop, interrupts)
- Dynamic state management with checkpoints
- Conditional routing with multiple decision points
- Agent-to-agent communication patterns
- Comprehensive observability

**Learning Outcomes:**
- Design 4-agent systems
- Use advanced LangGraph features
- Implement dynamic state management
- Create complex routing logic
- Add human-in-the-loop capabilities
- Implement comprehensive monitoring

**Prerequisites:**
- Completed Day 2 Medium Lab
- Understanding of async programming
- Familiarity with complex state machines

---

### Day 3: Deploying Agentic Systems with FastAPI

#### Day 3 - Medium Level Lab
**File:** `Day3_Medium_Lab.md`  
**Duration:** 90 minutes  
**Focus:** Deploying AI Agent as FastAPI Service

**Key Topics:**
- FastAPI integration with LangGraph/LangChain
- Async API endpoints
- Streaming responses (Server-Sent Events)
- Concurrent session handling
- Basic error handling and validation
- Local deployment

**Learning Outcomes:**
- Integrate agents with FastAPI
- Create async endpoints
- Implement streaming responses
- Handle concurrent sessions
- Add error handling
- Deploy locally

**Prerequisites:**
- Completed Day 1 and Day 2 labs
- Understanding of REST APIs
- Basic FastAPI knowledge

---

#### Day 3 - Advanced Level Lab
**File:** `Day3_Advanced_Lab.md`  
**Duration:** 120 minutes  
**Focus:** Production-Ready Agentic API with Monitoring

**Key Topics:**
- Docker containerization
- Comprehensive monitoring and logging
- Redis caching layer
- Rate limiting and authentication
- Health checks and Prometheus metrics
- Production deployment configuration
- Distributed tracing

**Learning Outcomes:**
- Containerize applications
- Implement monitoring and logging
- Add caching for performance
- Implement rate limiting and auth
- Set up metrics and health checks
- Configure for production
- Add distributed tracing

**Prerequisites:**
- Completed Day 3 Medium Lab
- Understanding of Docker
- Knowledge of monitoring/observability
- Familiarity with Redis (optional)

---

## Lab Progression Path

### Recommended Learning Path

1. **Day 1 Medium** → Build foundational skills
2. **Day 1 Advanced** → Enhance with RAG and advanced features
3. **Day 2 Medium** → Learn LangGraph basics
4. **Day 2 Advanced** → Master complex multi-agent systems
5. **Day 3 Medium** → Deploy basic API
6. **Day 3 Advanced** → Production-ready deployment

### Alternative Paths

**Fast Track (Experienced Developers):**
- Day 1 Advanced (skip Medium)
- Day 2 Advanced (skip Medium)
- Day 3 Advanced (skip Medium)

**Gradual Build (Beginners):**
- Complete all Medium labs first
- Then attempt Advanced labs
- Review Medium concepts as needed

## Common Prerequisites Across All Labs

### Required Tools
- Python 3.11+
- VS Code (with extensions)
- Git
- OpenAI API key
- (Optional) Anthropic API key

### Required Python Packages (Base)
```bash
pip install langchain langchain-openai langchain-community
pip install langgraph langsmith
pip install fastapi uvicorn[standard]
pip install python-dotenv pydantic
```

### Environment Setup
Each lab includes specific setup instructions. General setup:
1. Create virtual environment
2. Install dependencies
3. Configure `.env` file with API keys
4. Verify installation

## Lab Deliverables

Each lab requires:
1. **Working Code** - Complete implementation
2. **Test Results** - Demonstration of functionality
3. **Documentation** - Code comments and brief report
4. **Exercises** - Additional challenges completed

## Assessment Criteria

### Medium Level Labs
- ✅ Code compiles and runs
- ✅ Basic functionality works
- ✅ Exercises completed
- ✅ Documentation present

### Advanced Level Labs
- ✅ All medium criteria met
- ✅ Advanced features implemented
- ✅ Performance considerations addressed
- ✅ Production-ready code quality
- ✅ Comprehensive testing

## Support Resources

### Documentation
- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://python.langchain.com/docs/langgraph)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

### Community
- LangChain Discord
- Stack Overflow (tag: langchain)
- GitHub Discussions

## Troubleshooting

Common issues and solutions are provided in each lab document. General tips:
- Check Python version (3.11+)
- Verify API keys in `.env`
- Ensure all dependencies installed
- Check virtual environment activation
- Review error messages carefully

## Next Steps After Training

1. **Build Your Own Agent** - Apply concepts to real projects
2. **Explore Advanced Topics** - Vector stores, fine-tuning, etc.
3. **Join Community** - Contribute to open source
4. **Stay Updated** - Follow LangChain/LangGraph updates
5. **Practice** - Build increasingly complex systems

---

## Quick Reference

| Day | Medium Lab | Advanced Lab | Key Focus |
|-----|-----------|--------------|-----------|
| 1 | Conversational Agent | RAG Agent | LangChain Fundamentals |
| 2 | Research System | Multi-Agent System | LangGraph Orchestration |
| 3 | FastAPI Service | Production API | Deployment & Monitoring |

---

**Last Updated:** 2024  
**Version:** 1.0

