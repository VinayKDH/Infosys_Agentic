# Day 3 Labs Review

## Overview

Day 3 focuses on **deploying AI agents as production-ready APIs** using FastAPI. The labs progress from basic API deployment to production-ready systems with monitoring, caching, authentication, and containerization.

---

## Day 3 Medium Lab: Deploying AI Agent as FastAPI Service

### **Duration:** 90 minutes
### **Objective:** 
Deploy your multi-agent system as a production-ready FastAPI service with async endpoints, streaming responses, and basic error handling.

### **Learning Outcomes:**
- ✅ Integrate LangGraph/LangChain with FastAPI
- ✅ Create async API endpoints for agent execution
- ✅ Implement streaming responses for real-time updates
- ✅ Handle concurrent user sessions
- ✅ Add basic error handling and validation
- ✅ Deploy the service locally

### **Project Structure:**
```
day3_medium_lab/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application setup
│   ├── models.py            # Pydantic request/response models
│   ├── agent_service.py     # Agent service integration
│   └── routes/
│       ├── __init__.py
│       └── agent.py         # API routes/endpoints
├── .env
├── requirements.txt
└── README.md
```

### **Core Components:**

#### 1. **FastAPI Application (`app/main.py`)**
- FastAPI app initialization
- CORS middleware configuration
- Router registration
- Health check endpoint
- Root endpoint

#### 2. **Pydantic Models (`app/models.py`)**
- `QueryRequest`: Request model with query, session_id, stream flag, max_iterations
- `QueryResponse`: Response model with response, session_id, execution_time, tokens_used, metadata
- `StreamChunk`: Model for streaming response chunks
- `ErrorResponse`: Error response model

#### 3. **Agent Service (`app/agent_service.py`)**
- `AgentService` class:
  - LLM initialization (ChatOpenAI)
  - LangGraph workflow building
  - Session management
  - `process_query()`: Process queries asynchronously
  - `stream_query()`: Stream responses in real-time
  - `get_session_info()`: Retrieve session information
  - `clear_session()`: Delete sessions

#### 4. **API Routes (`app/routes/agent.py`)**
- `POST /api/v1/query`: Process agent queries
- `POST /api/v1/query/stream`: Stream agent responses (SSE)
- `GET /api/v1/session/{session_id}`: Get session information
- `DELETE /api/v1/session/{session_id}`: Delete a session
- `GET /api/v1/sessions`: List all active sessions

### **Key Features:**
1. **Async Processing**: All endpoints are async for better concurrency
2. **Streaming Responses**: Server-Sent Events (SSE) for real-time updates
3. **Session Management**: Track conversations across multiple requests
4. **Error Handling**: Try-catch blocks with proper HTTP status codes
5. **API Documentation**: Auto-generated OpenAPI/Swagger docs at `/docs`

### **Endpoints Summary:**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Root endpoint with API info |
| `/health` | GET | Health check |
| `/api/v1/query` | POST | Process agent query |
| `/api/v1/query/stream` | POST | Stream agent response |
| `/api/v1/session/{session_id}` | GET | Get session info |
| `/api/v1/session/{session_id}` | DELETE | Delete session |
| `/api/v1/sessions` | GET | List all sessions |
| `/docs` | GET | Interactive API documentation |

### **Exercises:**
1. **Add Request Validation** (15 min) - Input sanitization, rate limiting, timeout handling
2. **Error Handling Enhancement** (15 min) - Custom exception handlers, logging
3. **Background Tasks** (15 min) - Long-running queries, task status endpoints
4. **API Documentation** (10 min) - Enhanced docstrings, examples

### **Testing:**
- Health check endpoint
- Query endpoint processing
- Streaming endpoint chunks
- Session management
- Error handling
- Concurrent requests
- API documentation accessibility

---

## Day 3 Advanced Lab: Production-Ready Agentic API with Monitoring

### **Duration:** 120 minutes
### **Objective:** 
Build a production-ready FastAPI service with Docker containerization, comprehensive monitoring, caching, rate limiting, authentication, and deployment configuration.

### **Learning Outcomes:**
- ✅ Containerize the application with Docker
- ✅ Implement comprehensive monitoring and logging
- ✅ Add caching for improved performance
- ✅ Implement rate limiting and authentication
- ✅ Set up health checks and metrics
- ✅ Configure for production deployment
- ✅ Add distributed tracing

### **Project Structure:**
```
day3_advanced_lab/
├── app/
│   ├── __init__.py
│   ├── main.py              # Enhanced FastAPI app with middleware
│   ├── config.py            # Configuration management (Pydantic Settings)
│   ├── models.py            # Request/response models
│   ├── agent_service.py     # Agent service
│   ├── cache.py             # Redis caching layer
│   ├── auth.py              # JWT authentication
│   ├── monitoring.py        # Prometheus metrics
│   ├── middleware.py        # Rate limiting middleware
│   └── routes/
│       ├── __init__.py
│       ├── agent.py         # Agent endpoints
│       ├── auth.py          # Authentication endpoints
│       └── metrics.py       # Metrics endpoint
├── docker/
│   ├── Dockerfile           # Docker image definition
│   └── docker-compose.yml   # Multi-container setup
├── tests/
│   ├── test_api.py
│   └── test_agent.py
├── .env.example
├── requirements.txt
└── README.md
```

### **Core Components:**

#### 1. **Configuration Management (`app/config.py`)**
- `Settings` class using Pydantic Settings:
  - API settings (title, version, prefix, debug)
  - Server settings (host, port, workers)
  - OpenAI settings (API key, model, temperature, max_tokens)
  - Redis settings (host, port, db, password, enabled)
  - Authentication (secret key, algorithm, token expiry)
  - Rate limiting (enabled, requests, window)
  - Caching (enabled, TTL)
  - Monitoring (metrics, tracing, log level)
  - LangSmith (tracing, API key, project)

#### 2. **Caching Layer (`app/cache.py`)**
- `CacheService` class:
  - Redis connection management
  - `get()`: Retrieve cached values
  - `set()`: Store values with TTL
  - `delete()`: Remove cached values
  - `clear_pattern()`: Clear keys by pattern
  - Graceful fallback if Redis unavailable

#### 3. **Authentication (`app/auth.py`)**
- JWT token-based authentication
- Password hashing with bcrypt
- `authenticate_user()`: Verify credentials
- `create_access_token()`: Generate JWT tokens
- `get_current_user()`: Validate and extract user from token
- `get_current_active_user()`: Get active user dependency
- User database (simplified in-memory for demo)

#### 4. **Rate Limiting (`app/middleware.py`)**
- `RateLimitMiddleware` class:
  - Redis-based rate limiting
  - Sliding window algorithm
  - Per-client (IP or user) limits
  - Rate limit headers in responses
  - Graceful degradation if Redis unavailable

#### 5. **Monitoring (`app/monitoring.py`)**
- Prometheus metrics:
  - `request_count`: Total HTTP requests (by method, endpoint, status)
  - `request_duration`: Request duration histogram
  - `active_sessions`: Current active sessions gauge
  - `agent_executions`: Agent execution counter
  - `agent_duration`: Agent execution duration histogram
  - `cache_hits`/`cache_misses`: Cache performance metrics
- `track_request_metrics()`: Decorator for automatic tracking
- `get_metrics()`: Export Prometheus format

#### 6. **Enhanced Main Application (`app/main.py`)**
- Structured logging with `structlog`
- Request logging middleware
- Global exception handler
- Rate limiting middleware integration
- Health check with dependency status
- Router registration (auth, agent, metrics)

#### 7. **Docker Configuration**
- **Dockerfile:**
  - Python 3.11-slim base image
  - System dependencies installation
  - Application code copying
  - Health check configuration
  - Multi-worker uvicorn command

- **docker-compose.yml:**
  - API service with build configuration
  - Redis service for caching/rate limiting
  - Environment variable configuration
  - Volume mounts for development
  - Restart policies

### **Key Features:**

#### **Production Features:**
1. **Docker Containerization**: Multi-stage builds, optimized images
2. **Redis Caching**: Response caching for improved performance
3. **JWT Authentication**: Secure API access with token-based auth
4. **Rate Limiting**: Prevent abuse with configurable limits
5. **Prometheus Metrics**: Comprehensive monitoring and observability
6. **Structured Logging**: JSON-formatted logs for easy parsing
7. **Health Checks**: Dependency health monitoring
8. **Error Handling**: Global exception handlers with proper logging

#### **Security Features:**
- JWT token authentication
- Password hashing (bcrypt)
- Rate limiting per client
- CORS configuration
- Environment-based secrets

#### **Observability Features:**
- Request/response logging
- Performance metrics (duration, count)
- Cache hit/miss tracking
- Agent execution metrics
- Health check endpoints

### **Endpoints Summary:**

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/` | GET | No | Root endpoint |
| `/health` | GET | No | Health check with dependencies |
| `/api/v1/metrics` | GET | No | Prometheus metrics |
| `/api/v1/auth/login` | POST | No | Authenticate and get token |
| `/api/v1/query` | POST | Yes | Process agent query (cached) |
| `/api/v1/query/stream` | POST | Yes | Stream agent response |
| `/api/v1/session/{id}` | GET | Yes | Get session info |
| `/api/v1/session/{id}` | DELETE | Yes | Delete session |
| `/docs` | GET | No | Interactive API documentation |

### **Exercises:**
1. **Distributed Tracing** (20 min) - OpenTelemetry integration, Jaeger/Zipkin export
2. **Database Integration** (20 min) - PostgreSQL for sessions/users, migrations
3. **Load Testing** (15 min) - Locust/k6 testing, performance analysis

### **Docker Deployment:**
```bash
cd docker
docker-compose up --build
```

**Services:**
- `api`: FastAPI application (port 8000)
- `redis`: Redis cache/rate limiting (port 6379)

### **Monitoring & Metrics:**
- **Prometheus Metrics**: Available at `/api/v1/metrics`
- **Health Checks**: `/health` endpoint with dependency status
- **Structured Logs**: JSON format for log aggregation
- **Request Tracking**: Duration, count, status codes

---

## Comparison: Medium vs Advanced

| Feature | Medium Lab | Advanced Lab |
|---------|-----------|--------------|
| **FastAPI Setup** | ✅ Basic | ✅ Enhanced with middleware |
| **Async Endpoints** | ✅ | ✅ |
| **Streaming** | ✅ SSE | ✅ SSE |
| **Session Management** | ✅ In-memory | ✅ With checkpoints |
| **Error Handling** | ✅ Basic | ✅ Comprehensive |
| **Configuration** | ❌ Hardcoded | ✅ Pydantic Settings |
| **Caching** | ❌ | ✅ Redis |
| **Authentication** | ❌ | ✅ JWT |
| **Rate Limiting** | ❌ | ✅ Redis-based |
| **Monitoring** | ❌ | ✅ Prometheus |
| **Logging** | ❌ Basic | ✅ Structured |
| **Docker** | ❌ | ✅ Dockerfile + Compose |
| **Health Checks** | ✅ Basic | ✅ With dependencies |
| **Metrics** | ❌ | ✅ Comprehensive |

---

## Technology Stack

### **Day 3 Medium:**
- FastAPI
- Uvicorn
- LangChain/LangGraph
- Pydantic
- Python-dotenv

### **Day 3 Advanced:**
- FastAPI
- Uvicorn
- LangChain/LangGraph
- Pydantic Settings
- Redis (caching, rate limiting)
- JWT (python-jose, passlib)
- Prometheus Client
- Docker & Docker Compose
- Structured Logging (structlog)

---

## Learning Progression

### **Day 3 Medium → Advanced:**
1. **Basic API** → **Production API**
2. **No Auth** → **JWT Authentication**
3. **No Caching** → **Redis Caching**
4. **No Rate Limiting** → **Rate Limiting**
5. **Basic Logging** → **Structured Logging**
6. **No Monitoring** → **Prometheus Metrics**
7. **Local Deployment** → **Docker Deployment**
8. **Simple Config** → **Environment-based Config**

---

## Key Concepts Covered

### **FastAPI:**
- Async/await patterns
- Dependency injection
- Request/response models
- Middleware
- Streaming responses (SSE)
- Background tasks
- Error handling

### **Production Practices:**
- Configuration management
- Environment variables
- Health checks
- Monitoring and metrics
- Structured logging
- Rate limiting
- Caching strategies
- Authentication/authorization
- Containerization
- Multi-service orchestration

### **Integration:**
- LangGraph with FastAPI
- Redis for caching/rate limiting
- Prometheus for metrics
- Docker for deployment
- JWT for authentication

---

## Testing Scenarios

### **Day 3 Medium:**
- ✅ Health check works
- ✅ Query endpoint processes requests
- ✅ Streaming returns chunks
- ✅ Session management works
- ✅ Error handling returns proper codes
- ✅ API docs accessible
- ✅ Concurrent requests handled

### **Day 3 Advanced:**
- ✅ Authentication flow
- ✅ Caching improves performance
- ✅ Rate limiting prevents abuse
- ✅ Metrics are collected
- ✅ Health checks monitor dependencies
- ✅ Docker deployment works
- ✅ Logs are structured
- ✅ Load testing passes

---

## Deliverables

### **Day 3 Medium:**
1. Complete FastAPI application
2. Test script (unit/integration tests)
3. API documentation
4. Deployment guide

### **Day 3 Advanced:**
1. Production-ready application
2. Docker configuration
3. Monitoring dashboard setup
4. Load testing results
5. Deployment documentation
6. Security checklist

---

## Next Steps After Day 3

- Add database persistence (PostgreSQL)
- Implement distributed tracing (OpenTelemetry)
- Set up CI/CD pipelines
- Deploy to cloud (AWS, GCP, Azure)
- Add API versioning
- Implement WebSocket support
- Add GraphQL endpoint
- Set up alerting (Prometheus AlertManager)

---

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [FastAPI Production](https://fastapi.tiangolo.com/deployment/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Prometheus Metrics](https://prometheus.io/docs/concepts/metric_types/)
- [OpenTelemetry](https://opentelemetry.io/docs/)
- [JWT Authentication](https://jwt.io/)
- [Redis Documentation](https://redis.io/docs/)

