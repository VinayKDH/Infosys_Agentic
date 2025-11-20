# Day 3 Labs - Trainer's Guide: FastAPI Deployment & Production

## Overview
This guide provides trainers with a comprehensive breakdown of the Day 3 labs (Medium and Advanced), focusing on deploying AI agents as production-ready APIs using FastAPI, with progression from basic deployment to production-ready systems with monitoring, caching, authentication, and containerization.

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

---

## Day 3 Medium Lab: Core Components

### 1. **FastAPI Application (`app/main.py`)**
The main FastAPI application that serves as the entry point for the API service.

**Purpose:** Sets up the FastAPI application, configures middleware, registers routers, and provides basic endpoints.

**Key Components:**
- FastAPI app initialization with metadata
- CORS middleware for cross-origin requests
- Router registration for API endpoints
- Health check endpoint
- Root endpoint with API information

### 2. **Pydantic Models (`app/models.py`)**
Data validation and serialization models using Pydantic.

**Purpose:** Defines the structure and validation rules for request and response data.

**Models:**
- `QueryRequest`: Validates incoming query requests
- `QueryResponse`: Structures agent query responses
- `StreamChunk`: Models streaming response chunks
- `ErrorResponse`: Standardizes error responses

### 3. **Agent Service (`app/agent_service.py`)**
Service layer that integrates LangGraph with the API.

**Purpose:** Manages agent execution, session handling, and state management.

**Key Features:**
- LangGraph workflow integration
- Session management
- Async query processing
- Streaming response generation

### 4. **API Routes (`app/routes/agent.py`)**
REST API endpoints for interacting with the agent system.

**Purpose:** Exposes HTTP endpoints for agent queries, streaming, and session management.

**Endpoints:**
- `POST /api/v1/query`: Process agent queries
- `POST /api/v1/query/stream`: Stream agent responses
- `GET /api/v1/session/{session_id}`: Get session information
- `DELETE /api/v1/session/{session_id}`: Delete a session
- `GET /api/v1/sessions`: List all active sessions

---

## Day 3 Medium Lab: Module Reference

### **Module: `app/main.py`**
Main FastAPI application entry point.

**Global Variables:**
- `app` (FastAPI): The main FastAPI application instance

**Functions:**

##### `root() -> dict`
**Purpose:** Root endpoint that returns API information.

**What it does:**
- Returns API metadata (message, version, docs URL)
- Provides basic API information for clients

##### `health_check() -> dict`
**Purpose:** Health check endpoint for monitoring and load balancers.

**What it does:**
- Returns simple health status
- Used by monitoring systems to check service availability

**Key Features:**
- CORS middleware configuration
- Router registration with prefix
- Async endpoint support

---

### **Module: `app/models.py`**
Pydantic models for request/response validation.

**Classes:**

##### `QueryRequest(BaseModel)`
**Purpose:** Validates and structures incoming query requests.

**Fields:**
- `query` (str): User query to process (required, 1-2000 chars)
- `session_id` (Optional[str]): Session ID for conversation continuity
- `stream` (bool): Whether to stream the response (default: False)
- `max_iterations` (Optional[int]): Maximum agent iterations (default: 10)

**Validation:**
- Query length validation (min 1, max 2000 characters)
- Type checking for all fields

##### `QueryResponse(BaseModel)`
**Purpose:** Structures agent query responses.

**Fields:**
- `response` (str): Agent response text
- `session_id` (str): Session identifier
- `execution_time` (float): Execution time in seconds
- `tokens_used` (Optional[int]): Number of tokens consumed
- `metadata` (Optional[Dict]): Additional response metadata

##### `StreamChunk(BaseModel)`
**Purpose:** Models individual chunks in streaming responses.

**Fields:**
- `chunk` (str): Response chunk text
- `done` (bool): Whether this is the final chunk
- `metadata` (Optional[Dict]): Chunk metadata

##### `ErrorResponse(BaseModel)`
**Purpose:** Standardizes error responses.

**Fields:**
- `error` (str): Error message
- `detail` (Optional[str]): Detailed error information
- `code` (Optional[str]): Error code

---

### **Module: `app/agent_service.py`**
Service layer for agent execution and session management.

**Classes:**

##### `AgentState(TypedDict)`
**Purpose:** Defines the state schema for LangGraph workflow.

**Fields:**
- `messages` (Annotated[List[BaseMessage], operator.add]): Conversation messages (accumulated)
- `query` (str): Current user query
- `response` (str): Agent response

**Key Design:**
- Uses `Annotated` with `operator.add` for message accumulation
- Proper TypedDict for LangGraph compatibility

##### `AgentService`
**Purpose:** Main service class that manages agent execution and sessions.

**Instance Variables:**
- `llm` (ChatOpenAI): Language model instance
- `memory` (MemorySaver): LangGraph checkpoint memory
- `graph` (CompiledGraph): Compiled LangGraph workflow
- `sessions` (Dict[str, Dict]): In-memory session storage

**Methods:**

###### `__init__(self)`
**Purpose:** Initializes the agent service with LLM and graph.

**What it does:**
- Validates OpenAI API key presence
- Initializes ChatOpenAI LLM
- Creates MemorySaver for checkpoints
- Builds and compiles LangGraph workflow
- Initializes session storage dictionary

**Error Handling:**
- Raises ValueError if API key is missing

###### `_build_graph(self) -> CompiledGraph`
**Purpose:** Constructs the LangGraph workflow.

**What it does:**
- Creates StateGraph with AgentState schema
- Adds agent processing node
- Sets entry point to "agent" node
- Connects agent node to END
- Compiles graph with checkpoint memory

**Returns:** Compiled LangGraph workflow

###### `_agent_node(self, state: AgentState) -> AgentState`
**Purpose:** Processes user queries through the LLM.

**What it does:**
- Extracts last user message from state
- Falls back to query field if no message found
- Invokes LLM with user query
- Creates AIMessage with response
- Returns updated state with response

**State Updates:**
- Adds AIMessage to messages list (accumulated)
- Sets response field with LLM output
- Preserves query field

###### `async def process_query(self, query: str, session_id: str = None, max_iterations: int = 10) -> Dict[str, Any]`
**Purpose:** Processes a user query asynchronously.

**What it does:**
- Generates session ID if not provided
- Creates or retrieves session metadata
- Prepares LangGraph configuration with thread_id
- Creates initial state with user message
- Executes graph with checkpoint config
- Tracks execution time
- Updates session metadata
- Returns structured response

**Returns:**
- Dictionary with response, session_id, execution_time, metadata

**Error Handling:**
- Wraps exceptions with descriptive error messages

###### `async def stream_query(self, query: str, session_id: str = None) -> AsyncIterator[str]`
**Purpose:** Streams agent response in real-time.

**What it does:**
- Creates session ID if not provided
- Prepares initial state
- Executes graph to get full response
- Splits response into words
- Yields words one by one with delays
- Simulates streaming behavior

**Returns:** AsyncIterator yielding response chunks

**Note:** Simplified implementation - in production, would stream from agent directly

###### `def get_session_info(self, session_id: str) -> Dict[str, Any]`
**Purpose:** Retrieves information about a session.

**What it does:**
- Checks if session exists
- Returns session metadata or error

**Returns:** Session dictionary or error dictionary

###### `def clear_session(self, session_id: str) -> bool`
**Purpose:** Deletes a session from storage.

**What it does:**
- Removes session from sessions dictionary
- Returns success status

**Returns:** True if deleted, False if not found

**Global Functions:**

##### `get_agent_service() -> AgentService`
**Purpose:** Lazy initialization of global agent service instance.

**What it does:**
- Checks if agent_service exists
- Creates new instance if needed
- Returns singleton instance

**Design Pattern:** Singleton with lazy initialization

---

### **Module: `app/routes/agent.py`**
API route handlers for agent endpoints.

**Global Variables:**
- `router` (APIRouter): FastAPI router instance

**Functions:**

##### `@router.post("/query", response_model=QueryResponse)`
**Purpose:** Endpoint for processing agent queries.

**What it does:**
- Validates request using QueryRequest model
- Gets agent service instance
- Rejects streaming requests (redirects to stream endpoint)
- Calls agent_service.process_query()
- Returns QueryResponse with results

**Error Handling:**
- ValueError → 400 Bad Request
- Other exceptions → 500 Internal Server Error

**Request Body:**
- QueryRequest with query, optional session_id, stream flag, max_iterations

**Response:**
- QueryResponse with response, session_id, execution_time, metadata

##### `@router.post("/query/stream")`
**Purpose:** Endpoint for streaming agent responses.

**What it does:**
- Gets agent service instance
- Creates async generator function
- Iterates over stream_query chunks
- Formats chunks as Server-Sent Events (SSE)
- Yields SSE-formatted data
- Sends final chunk with done flag

**Response Type:** StreamingResponse with text/event-stream media type

**SSE Format:**
- `data: {json_chunk}\n\n`
- Final chunk has `done: true`

##### `@router.get("/session/{session_id}")`
**Purpose:** Retrieves session information.

**What it does:**
- Gets agent service instance
- Calls get_session_info()
- Returns session data or 404 error

**Path Parameters:**
- `session_id` (str): Session identifier

**Response:**
- Session metadata dictionary or 404 error

##### `@router.delete("/session/{session_id}")`
**Purpose:** Deletes a session.

**What it does:**
- Gets agent service instance
- Calls clear_session()
- Returns success message or 404 error

**Path Parameters:**
- `session_id` (str): Session identifier

**Response:**
- Success message or 404 error

##### `@router.get("/sessions")`
**Purpose:** Lists all active sessions.

**What it does:**
- Gets agent service instance
- Returns list of session IDs and count

**Response:**
- Dictionary with sessions list and count

---

## Day 3 Advanced Lab: Production-Ready Agentic API

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

---

## Day 3 Advanced Lab: Core Components

### 1. **Configuration Management (`app/config.py`)**
Centralized configuration using Pydantic Settings.

**Purpose:** Manages all application settings from environment variables with validation and defaults.

**Key Features:**
- Environment variable loading
- Type validation
- Sensible defaults
- Production-ready settings

### 2. **Caching Layer (`app/cache.py`)**
Redis-based caching service.

**Purpose:** Improves performance by caching responses and reducing redundant computations.

**Key Features:**
- Redis connection management
- Automatic fallback if Redis unavailable
- TTL-based expiration
- Key generation with hashing

### 3. **Authentication (`app/routes/auth.py`)**
JWT-based authentication system.

**Purpose:** Secures API endpoints with token-based authentication.

**Key Features:**
- JWT token generation
- Password hashing with bcrypt
- User authentication
- Token validation

### 4. **Monitoring (`app/monitoring.py`)**
Prometheus metrics collection.

**Purpose:** Provides observability and performance monitoring.

**Key Features:**
- Request metrics (count, duration)
- Agent execution metrics
- Session tracking
- Prometheus format export

### 5. **Enhanced Main Application (`app/main.py`)**
Production-ready FastAPI application.

**Purpose:** Orchestrates all components with middleware, logging, and error handling.

**Key Features:**
- Structured logging
- Request logging middleware
- Global exception handlers
- Health checks with dependencies

---

## Day 3 Advanced Lab: Module Reference

### **Module: `app/config.py`**
Configuration management using Pydantic Settings.

**Classes:**

##### `Settings(BaseSettings)`
**Purpose:** Centralized application configuration with environment variable support.

**Configuration Categories:**

**API Settings:**
- `API_TITLE` (str): API title
- `API_VERSION` (str): API version
- `API_PREFIX` (str): URL prefix for API routes
- `DEBUG` (bool): Debug mode flag

**Server Settings:**
- `HOST` (str): Server host address
- `PORT` (int): Server port
- `WORKERS` (int): Number of worker processes

**OpenAI Settings:**
- `OPENAI_API_KEY` (str): OpenAI API key (required)
- `OPENAI_MODEL` (str): Model name
- `OPENAI_TEMPERATURE` (float): Model temperature
- `OPENAI_MAX_TOKENS` (int): Maximum tokens

**Redis Settings:**
- `REDIS_HOST` (str): Redis host
- `REDIS_PORT` (int): Redis port
- `REDIS_DB` (int): Redis database number
- `REDIS_PASSWORD` (Optional[str]): Redis password
- `REDIS_ENABLED` (bool): Enable Redis

**Authentication:**
- `SECRET_KEY` (str): JWT secret key
- `ALGORITHM` (str): JWT algorithm
- `ACCESS_TOKEN_EXPIRE_MINUTES` (int): Token expiration

**Rate Limiting:**
- `RATE_LIMIT_ENABLED` (bool): Enable rate limiting
- `RATE_LIMIT_REQUESTS` (int): Requests per window
- `RATE_LIMIT_WINDOW` (int): Time window in seconds

**Caching:**
- `CACHE_ENABLED` (bool): Enable caching
- `CACHE_TTL` (int): Cache TTL in seconds

**Monitoring:**
- `ENABLE_METRICS` (bool): Enable metrics
- `ENABLE_TRACING` (bool): Enable tracing
- `LOG_LEVEL` (str): Logging level

**LangSmith:**
- `LANGCHAIN_TRACING_V2` (bool): Enable LangSmith tracing
- `LANGCHAIN_API_KEY` (Optional[str]): LangSmith API key
- `LANGCHAIN_PROJECT` (str): LangSmith project name

**Configuration:**
- Loads from `.env` file
- Case-sensitive field names
- Type validation

**Global Variable:**
- `settings` (Settings): Singleton settings instance

---

### **Module: `app/cache.py`**
Redis-based caching service.

**Classes:**

##### `CacheService`
**Purpose:** Manages Redis caching with graceful fallback.

**Instance Variables:**
- `redis_client` (Optional[Redis]): Redis client instance
- `enabled` (bool): Whether caching is enabled

**Methods:**

###### `__init__(self)`
**Purpose:** Initializes cache service with Redis connection.

**What it does:**
- Checks if caching is enabled in settings
- Attempts Redis connection
- Tests connection with ping()
- Disables caching if connection fails
- Logs connection status

**Error Handling:**
- Gracefully disables caching on connection failure
- Logs warnings for debugging

###### `_generate_key(self, prefix: str, *args, **kwargs) -> str`
**Purpose:** Generates cache key from arguments.

**What it does:**
- Serializes arguments to JSON
- Creates MD5 hash of serialized data
- Returns formatted cache key

**Key Format:** `cache:{prefix}:{hash}`

###### `get(self, prefix: str, *args, **kwargs) -> Optional[Any]`
**Purpose:** Retrieves value from cache.

**What it does:**
- Generates cache key
- Retrieves value from Redis
- Deserializes JSON value
- Returns value or None

**Error Handling:**
- Returns None on errors
- Logs errors for debugging

###### `set(self, prefix: str, value: Any, ttl: Optional[int] = None, *args, **kwargs)`
**Purpose:** Stores value in cache.

**What it does:**
- Generates cache key
- Serializes value to JSON
- Stores in Redis with TTL
- Uses default TTL if not specified

**Error Handling:**
- Silently fails on errors
- Logs errors for debugging

**Global Variable:**
- `cache_service` (CacheService): Singleton cache service instance

---

### **Module: `app/monitoring.py`**
Prometheus metrics collection.

**Global Variables:**

##### `request_count` (Counter)
**Purpose:** Tracks total HTTP requests.

**Labels:**
- `method`: HTTP method
- `endpoint`: Request endpoint
- `status`: Response status code

##### `request_duration` (Histogram)
**Purpose:** Tracks HTTP request duration.

**Labels:**
- `method`: HTTP method
- `endpoint`: Request endpoint

##### `active_sessions` (Gauge)
**Purpose:** Tracks number of active sessions.

##### `agent_executions` (Counter)
**Purpose:** Tracks total agent executions.

**Labels:**
- `status`: Execution status (success/failure)

##### `agent_duration` (Histogram)
**Purpose:** Tracks agent execution duration.

**Functions:**

##### `get_metrics() -> bytes`
**Purpose:** Exports Prometheus metrics in text format.

**What it does:**
- Generates Prometheus-formatted metrics
- Returns bytes for HTTP response

**Usage:** Called by metrics endpoint to expose metrics

---

### **Module: `app/routes/auth.py`**
JWT-based authentication endpoints.

**Global Variables:**
- `router` (APIRouter): FastAPI router instance
- `security` (HTTPBearer): Bearer token security scheme
- `pwd_context` (CryptContext): Password hashing context
- `USERS_DB` (Dict): In-memory user database (demo)

**Functions:**

##### `create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str`
**Purpose:** Creates a JWT access token.

**What it does:**
- Copies token data
- Calculates expiration time
- Adds expiration to token data
- Encodes JWT with secret key
- Returns encoded token string

**Parameters:**
- `data`: Token payload (typically contains user info)
- `expires_delta`: Optional custom expiration time

**Returns:** Encoded JWT token string

##### `@router.post("/login")`
**Purpose:** Authenticates user and returns JWT token.

**What it does:**
- Retrieves user from database
- Verifies password with bcrypt
- Creates JWT access token
- Returns token and type

**Request Parameters:**
- `username` (str): User username
- `password` (str): User password

**Response:**
- Dictionary with `access_token` and `token_type`

**Error Handling:**
- Raises 401 Unauthorized for invalid credentials

---

### **Module: `app/main.py` (Advanced)**
Enhanced FastAPI application with production features.

**Global Variables:**
- `app` (FastAPI): Main FastAPI application
- `logger` (Logger): Application logger

**Functions:**

##### `log_requests(request: Request, call_next) -> Response`
**Purpose:** Middleware for request/response logging.

**What it does:**
- Records request start time
- Logs request details (method, path, client)
- Processes request
- Calculates processing time
- Logs response details (status, duration)
- Adds X-Process-Time header
- Handles exceptions

**Middleware Type:** HTTP middleware

##### `health_check() -> dict`
**Purpose:** Enhanced health check with dependency status.

**What it does:**
- Checks cache service status
- Returns health status with dependencies

**Response:**
- Dictionary with status and dependency health

**Key Features:**
- Structured logging configuration
- Request logging middleware
- Router registration (auth, agent, metrics)
- Global exception handling
- Multi-worker support

---

## Key Concepts for Trainers

### **FastAPI Fundamentals:**
1. **Async/Await:** All endpoints are async for better concurrency
2. **Dependency Injection:** FastAPI's dependency system for reusable components
3. **Pydantic Models:** Request/response validation and serialization
4. **Middleware:** Request/response processing pipeline
5. **Routers:** Modular endpoint organization

### **Production Practices:**
1. **Configuration Management:** Environment-based settings
2. **Caching:** Redis for performance optimization
3. **Authentication:** JWT tokens for secure access
4. **Monitoring:** Prometheus metrics for observability
5. **Logging:** Structured logging for debugging
6. **Error Handling:** Global exception handlers
7. **Health Checks:** Dependency monitoring

### **LangGraph Integration:**
1. **State Management:** TypedDict with Annotated fields
2. **Checkpoints:** Session persistence with MemorySaver
3. **Async Execution:** Async query processing
4. **Streaming:** Real-time response streaming

### **Architecture Patterns:**
1. **Service Layer:** Separation of business logic
2. **Repository Pattern:** Data access abstraction
3. **Singleton Pattern:** Global service instances
4. **Lazy Initialization:** Deferred service creation

---

## Teaching Tips

### **Day 3 Medium:**
1. Start with FastAPI basics (async, models, routers)
2. Demonstrate LangGraph integration step by step
3. Show streaming responses with curl/Postman
4. Explain session management and state persistence
5. Practice error handling and validation

### **Day 3 Advanced:**
1. Explain production requirements (monitoring, caching, auth)
2. Demonstrate configuration management with .env
3. Show Redis caching in action
4. Walk through JWT authentication flow
5. Explain Prometheus metrics and monitoring
6. Demonstrate Docker deployment

### **Common Pitfalls:**
1. **State Schema:** Must use TypedDict with proper annotations
2. **Async/Await:** Remember to use async in FastAPI endpoints
3. **Error Handling:** Always handle exceptions gracefully
4. **Configuration:** Validate all required settings
5. **Caching:** Handle Redis unavailability gracefully

---

## Exercises for Students

### **Day 3 Medium:**
1. Add request validation and sanitization
2. Implement rate limiting per session
3. Add request timeout handling
4. Create custom exception handlers
5. Add API documentation examples

### **Day 3 Advanced:**
1. Add distributed tracing (OpenTelemetry)
2. Integrate PostgreSQL for sessions
3. Implement rate limiting middleware
4. Add load testing with Locust
5. Create Docker Compose with multiple services

---

## Assessment Criteria

### **Day 3 Medium:**
- ✅ FastAPI application runs successfully
- ✅ All endpoints respond correctly
- ✅ Streaming works properly
- ✅ Session management functions
- ✅ Error handling is comprehensive
- ✅ API documentation is complete

### **Day 3 Advanced:**
- ✅ Configuration management works
- ✅ Caching improves performance
- ✅ Authentication secures endpoints
- ✅ Metrics are collected correctly
- ✅ Docker deployment succeeds
- ✅ Health checks monitor dependencies
- ✅ Logging is structured and useful

---

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [FastAPI Async](https://fastapi.tiangolo.com/async/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Prometheus Metrics](https://prometheus.io/docs/concepts/metric_types/)
- [JWT Authentication](https://jwt.io/)
- [Redis Documentation](https://redis.io/docs/)
- [Docker Documentation](https://docs.docker.com/)

---

This trainer guide provides comprehensive coverage of both Day 3 labs, enabling trainers to effectively teach FastAPI deployment and production practices for AI agent systems.

