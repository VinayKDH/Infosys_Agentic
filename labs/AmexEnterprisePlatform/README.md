# Amex Enterprise Customer Intelligence Platform

A production-ready AI-powered customer support and intelligence system for American Express, combining Day 1, Day 2, and Day 3 concepts.

## Overview

This platform provides:
- **Intelligent Customer Support** - AI-powered support with RAG for document Q&A
- **Fraud Detection** - Real-time transaction analysis and risk scoring
- **Account Intelligence** - Personalized financial insights and recommendations
- **Compliance Monitoring** - Automated regulatory compliance validation
- **Multi-Agent Orchestration** - Collaborative agent system using LangGraph
- **Production API** - FastAPI with authentication, caching, and monitoring

## Architecture

### Day 1 Components
- **RAG System** - Document retrieval and Q&A for banking policies
- **Banking Tools** - Transaction analysis, risk scoring, compliance validation
- **Memory Management** - Conversation and entity memory

### Day 2 Components
- **Multi-Agent System** - 6 specialized agents (Planner, Support, Fraud, Account Intel, Compliance, Reviewer)
- **LangGraph Workflow** - Orchestrated agent collaboration
- **State Management** - Comprehensive state tracking

### Day 3 Components
- **FastAPI Application** - Production-ready REST API
- **Authentication** - JWT-based security
- **Caching** - Redis-based response caching
- **Monitoring** - Prometheus metrics and structured logging
- **Docker** - Containerized deployment

## Setup

### Prerequisites
- Python 3.11+
- Docker and Docker Compose (optional)
- Redis (optional, for caching)
- OpenAI API key

### Installation

1. **Clone and navigate to the project:**
```bash
cd labs/AmexEnterprisePlatform
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY and other settings
```

5. **Initialize RAG system (optional):**
```bash
# Place banking documents in documents/ directory
# Then run initialization script (to be created)
python scripts/init_rag.py
```

## Running the Application

### Local Development

```bash
# Start Redis (if using caching)
docker run -d -p 6379:6379 redis:7-alpine

# Run the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Deployment

```bash
cd docker
docker-compose up --build
```

## API Endpoints

### Authentication
- `POST /api/v1/login` - Authenticate and get JWT token
- `GET /api/v1/me` - Get current user info

### Customer Support
- `POST /api/v1/query` - Process customer query
- `POST /api/v1/query/stream` - Stream response
- `GET /api/v1/session/{session_id}` - Get session info
- `DELETE /api/v1/session/{session_id}` - Delete session

### Monitoring
- `GET /api/v1/metrics` - Prometheus metrics
- `GET /health` - Health check

### Documentation
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

## Usage Examples

### 1. Authenticate
```bash
curl -X POST "http://localhost:8000/api/v1/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "customer1", "password": "password123"}'
```

### 2. Query Customer Support
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "query": "I see a charge for $500 at Best Buy yesterday, but I didn't make that purchase.",
    "customer_id": "CUST001",
    "stream": false
  }'
```

### 3. Stream Response
```bash
curl -X POST "http://localhost:8000/api/v1/query/stream" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "query": "How can I maximize my rewards this month?",
    "customer_id": "CUST001"
  }'
```

## Project Structure

```
AmexEnterprisePlatform/
├── app/                    # FastAPI application
│   ├── main.py            # Main application
│   ├── config.py          # Configuration
│   ├── auth.py            # Authentication
│   ├── cache.py           # Caching layer
│   ├── monitoring.py      # Metrics
│   ├── agent_service.py   # Agent orchestration
│   ├── models.py          # Pydantic models
│   └── routes/            # API routes
├── agents/                # Multi-agent system
│   ├── planner.py
│   ├── support_agent.py
│   ├── fraud_agent.py
│   ├── account_intel_agent.py
│   ├── compliance_agent.py
│   └── reviewer_agent.py
├── tools/                 # Banking tools
│   ├── transaction_analyzer.py
│   ├── account_calculator.py
│   ├── risk_scorer.py
│   ├── compliance_validator.py
│   └── document_qa.py
├── rag/                   # RAG system
│   ├── document_loader.py
│   └── vector_store.py
├── graph/                 # LangGraph workflow
│   └── amex_workflow.py
├── state/                 # State management
│   └── amex_state.py
├── documents/             # Banking documents (add your PDFs here)
├── docker/                # Docker configuration
│   ├── Dockerfile
│   └── docker-compose.yml
└── requirements.txt
```

## Features

### Security
- JWT-based authentication
- Role-based access control
- Input validation
- Secure password hashing

### Performance
- Redis caching for responses
- Async API endpoints
- Efficient agent orchestration

### Observability
- Prometheus metrics
- Structured logging
- Health checks
- Request tracing

### Compliance
- Automated compliance validation
- Regulatory requirement checking
- Audit logging

## Testing

### Quick Test

```bash
# Run basic tests
python test_basic.py
```

### Manual Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test authentication
curl -X POST "http://localhost:8000/api/v1/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "customer1", "password": "password123"}'
```

### Full Test Suite

See `TESTING_GUIDE.md` for comprehensive testing instructions.

## Monitoring

- **Metrics**: http://localhost:8000/api/v1/metrics
- **Health**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs

## Development

### Adding New Tools
1. Create tool in `tools/` directory
2. Use `@tool` decorator from LangChain
3. Add to agent's tool list

### Adding New Agents
1. Create agent class in `agents/` directory
2. Implement `process(state: AmexState) -> AmexState` method
3. Add node to workflow in `graph/amex_workflow.py`

### Modifying Workflow
Edit `graph/amex_workflow.py` to:
- Add new nodes
- Modify routing logic
- Change execution flow

## Troubleshooting

### Redis Connection Issues
- Ensure Redis is running: `docker ps | grep redis`
- Check REDIS_HOST and REDIS_PORT in .env

### OpenAI API Errors
- Verify OPENAI_API_KEY in .env
- Check API quota and rate limits

### Import Errors
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`

## License

This is a training project for educational purposes.

## Contributing

This is a demonstration project. For production use, additional security, testing, and compliance measures would be required.

