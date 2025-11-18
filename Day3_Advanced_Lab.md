# Day 3 - Advanced Level Lab: Production-Ready Agentic API with Monitoring

## Lab Overview
**Duration:** 120 minutes  
**Objective:** Build a production-ready FastAPI service with Docker containerization, comprehensive monitoring, caching, rate limiting, authentication, and deployment configuration.

## Prerequisites
- Completed Day 3 Medium Lab
- Understanding of Docker
- Knowledge of monitoring and observability
- Familiarity with Redis (optional but recommended)

## Learning Outcomes
By the end of this lab, you will:
- Containerize the application with Docker
- Implement comprehensive monitoring and logging
- Add caching for improved performance
- Implement rate limiting and authentication
- Set up health checks and metrics
- Configure for production deployment
- Add distributed tracing

## Lab Setup

### Step 1: Environment Setup
```bash
pip install fastapi uvicorn[standard]
pip install langchain langchain-openai langgraph
pip install redis python-jose[cryptography] passlib[bcrypt]
pip install prometheus-client opentelemetry-api opentelemetry-sdk
pip install opentelemetry-instrumentation-fastapi
pip install structlog python-json-logger
pip install docker-compose
```

### Step 2: Project Structure
```
day3_advanced_lab/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── dependencies.py
│   ├── middleware.py
│   ├── models.py
│   ├── agent_service.py
│   ├── cache.py
│   ├── auth.py
│   ├── monitoring.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── auth.py
│   │   └── metrics.py
│   └── utils/
│       ├── __init__.py
│       └── logging.py
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   └── test_agent.py
├── .env.example
├── requirements.txt
├── .dockerignore
└── README.md
```

## Lab Implementation

### Part 1: Configuration Management (15 minutes)

**File: `app/config.py`**
```python
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    API_TITLE: str = "Agentic AI API"
    API_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = False
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    
    # OpenAI Settings
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_MAX_TOKENS: int = 2000
    
    # Redis Settings (for caching and rate limiting)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_ENABLED: bool = True
    
    # Authentication
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # Caching
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 3600  # seconds
    
    # Monitoring
    ENABLE_METRICS: bool = True
    ENABLE_TRACING: bool = True
    LOG_LEVEL: str = "INFO"
    
    # LangSmith
    LANGCHAIN_TRACING_V2: bool = True
    LANGCHAIN_API_KEY: Optional[str] = None
    LANGCHAIN_PROJECT: str = "agentic-ai-production"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### Part 2: Caching Layer (20 minutes)

**File: `app/cache.py`**
```python
from typing import Optional, Any
import redis
import json
import hashlib
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self):
        self.redis_client = None
        self.enabled = settings.CACHE_ENABLED and settings.REDIS_ENABLED
        
        if self.enabled:
            try:
                self.redis_client = redis.Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    db=settings.REDIS_DB,
                    password=settings.REDIS_PASSWORD,
                    decode_responses=True,
                    socket_connect_timeout=5
                )
                # Test connection
                self.redis_client.ping()
                logger.info("Redis cache connected successfully")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}. Caching disabled.")
                self.enabled = False
                self.redis_client = None
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_data = f"{prefix}:{json.dumps(args, sort_keys=True)}:{json.dumps(kwargs, sort_keys=True)}"
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"cache:{prefix}:{key_hash}"
    
    def get(self, prefix: str, *args, **kwargs) -> Optional[Any]:
        """Get value from cache"""
        if not self.enabled or not self.redis_client:
            return None
        
        try:
            key = self._generate_key(prefix, *args, **kwargs)
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
        
        return None
    
    def set(self, prefix: str, value: Any, ttl: Optional[int] = None, *args, **kwargs):
        """Set value in cache"""
        if not self.enabled or not self.redis_client:
            return
        
        try:
            key = self._generate_key(prefix, *args, **kwargs)
            ttl = ttl or settings.CACHE_TTL
            self.redis_client.setex(
                key,
                ttl,
                json.dumps(value)
            )
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    def delete(self, prefix: str, *args, **kwargs):
        """Delete value from cache"""
        if not self.enabled or not self.redis_client:
            return
        
        try:
            key = self._generate_key(prefix, *args, **kwargs)
            self.redis_client.delete(key)
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
    
    def clear_pattern(self, pattern: str):
        """Clear all keys matching pattern"""
        if not self.enabled or not self.redis_client:
            return
        
        try:
            keys = self.redis_client.keys(f"cache:{pattern}:*")
            if keys:
                self.redis_client.delete(*keys)
        except Exception as e:
            logger.error(f"Cache clear error: {e}")

# Global cache instance
cache_service = CacheService()
```

### Part 3: Authentication (20 minutes)

**File: `app/auth.py`**
```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# In production, use a proper user database
# This is a simplified example
USERS_DB = {
    "admin": {
        "username": "admin",
        "hashed_password": pwd_context.hash("admin123"),  # Change in production!
        "role": "admin"
    },
    "user": {
        "username": "user",
        "hashed_password": pwd_context.hash("user123"),  # Change in production!
        "role": "user"
    }
}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Authenticate a user"""
    user = USERS_DB.get(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = USERS_DB.get(username)
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """Get current active user"""
    # Add any additional checks here (e.g., user is active)
    return current_user
```

### Part 4: Rate Limiting (15 minutes)

**File: `app/middleware.py`**
```python
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import redis
import time
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.redis_client = None
        self.enabled = settings.RATE_LIMIT_ENABLED
        
        if self.enabled and settings.REDIS_ENABLED:
            try:
                self.redis_client = redis.Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    db=settings.REDIS_DB,
                    password=settings.REDIS_PASSWORD,
                    decode_responses=True
                )
                self.redis_client.ping()
            except Exception as e:
                logger.warning(f"Redis not available for rate limiting: {e}")
                self.enabled = False
    
    async def dispatch(self, request: Request, call_next):
        if not self.enabled or not self.redis_client:
            return await call_next(request)
        
        # Get client identifier (IP address or user ID)
        client_id = request.client.host
        if hasattr(request.state, "user") and request.state.user:
            client_id = request.state.user.get("username", client_id)
        
        # Rate limit key
        key = f"ratelimit:{client_id}"
        current_time = int(time.time())
        window_start = current_time - settings.RATE_LIMIT_WINDOW
        
        try:
            # Get current request count
            pipe = self.redis_client.pipeline()
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zcard(key)
            pipe.zadd(key, {str(current_time): current_time})
            pipe.expire(key, settings.RATE_LIMIT_WINDOW)
            results = pipe.execute()
            
            request_count = results[1] + 1  # +1 for current request
            
            if request_count > settings.RATE_LIMIT_REQUESTS:
                return Response(
                    content="Rate limit exceeded",
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    headers={
                        "X-RateLimit-Limit": str(settings.RATE_LIMIT_REQUESTS),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(current_time + settings.RATE_LIMIT_WINDOW)
                    }
                )
            
            # Add rate limit headers
            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(settings.RATE_LIMIT_REQUESTS)
            response.headers["X-RateLimit-Remaining"] = str(settings.RATE_LIMIT_REQUESTS - request_count)
            response.headers["X-RateLimit-Reset"] = str(current_time + settings.RATE_LIMIT_WINDOW)
            
            return response
        
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # On error, allow request through
            return await call_next(request)
```

### Part 5: Monitoring and Metrics (25 minutes)

**File: `app/monitoring.py`**
```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Response
import time
import logging
from functools import wraps

# Prometheus metrics
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

active_sessions = Gauge(
    'active_sessions_total',
    'Number of active sessions'
)

agent_executions = Counter(
    'agent_executions_total',
    'Total agent executions',
    ['status']
)

agent_duration = Histogram(
    'agent_execution_duration_seconds',
    'Agent execution duration'
)

cache_hits = Counter(
    'cache_hits_total',
    'Total cache hits',
    ['operation']
)

cache_misses = Counter(
    'cache_misses_total',
    'Total cache misses',
    ['operation']
)

def track_request_metrics(func):
    """Decorator to track request metrics"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            response = await func(*args, **kwargs)
            status_code = getattr(response, 'status_code', 200)
            request_count.labels(
                method=kwargs.get('method', 'GET'),
                endpoint=kwargs.get('endpoint', 'unknown'),
                status=status_code
            ).inc()
            return response
        except Exception as e:
            request_count.labels(
                method=kwargs.get('method', 'GET'),
                endpoint=kwargs.get('endpoint', 'unknown'),
                status=500
            ).inc()
            raise
        finally:
            duration = time.time() - start_time
            request_duration.labels(
                method=kwargs.get('method', 'GET'),
                endpoint=kwargs.get('endpoint', 'unknown')
            ).observe(duration)
    return wrapper

def get_metrics():
    """Get Prometheus metrics"""
    return generate_latest()
```

**File: `app/routes/metrics.py`**
```python
from fastapi import APIRouter
from fastapi.responses import Response
from app.monitoring import get_metrics

router = APIRouter()

@router.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(
        content=get_metrics(),
        media_type="text/plain"
    )
```

### Part 6: Enhanced Main Application (15 minutes)

**File: `app/main.py`**
```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.middleware import RateLimitMiddleware
from app.routes import agent, auth, metrics
from app.monitoring import request_count, request_duration
import logging
import time
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=False,
)

logger = structlog.get_logger()

app = FastAPI(
    title=settings.API_TITLE,
    description="Production-ready Agentic AI API",
    version=settings.API_VERSION,
    debug=settings.DEBUG
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
if settings.RATE_LIMIT_ENABLED:
    app.add_middleware(RateLimitMiddleware)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request
    logger.info(
        "request_started",
        method=request.method,
        path=request.url.path,
        client=request.client.host
    )
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            process_time=process_time
        )
        
        response.headers["X-Process-Time"] = str(process_time)
        return response
    
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            "request_failed",
            method=request.method,
            path=request.url.path,
            error=str(e),
            process_time=process_time
        )
        raise

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        "unhandled_exception",
        error=str(exc),
        path=request.url.path
    )
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc) if settings.DEBUG else None}
    )

# Include routers
app.include_router(auth.router, prefix=settings.API_PREFIX, tags=["authentication"])
app.include_router(agent.router, prefix=settings.API_PREFIX, tags=["agent"])
app.include_router(metrics.router, prefix=settings.API_PREFIX, tags=["metrics"])

@app.get("/")
async def root():
    return {
        "message": settings.API_TITLE,
        "version": settings.API_VERSION,
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    # Add health checks for dependencies (Redis, etc.)
    health_status = {
        "status": "healthy",
        "cache": "connected" if cache_service.enabled else "disabled"
    }
    return health_status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        workers=settings.WORKERS if not settings.DEBUG else 1
    )
```

### Part 7: Docker Configuration (10 minutes)

**File: `docker/Dockerfile`**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

**File: `docker/docker-compose.yml`**
```yaml
version: '3.8'

services:
  api:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
      - REDIS_HOST=redis
      - REDIS_ENABLED=true
    depends_on:
      - redis
    volumes:
      - ../app:/app/app
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

## Lab Exercises

### Exercise 1: Distributed Tracing (20 minutes)
- Integrate OpenTelemetry
- Add tracing to agent execution
- Export traces to Jaeger or Zipkin
- Analyze trace data

### Exercise 2: Database Integration (20 minutes)
- Add PostgreSQL for session storage
- Implement user management database
- Add query history storage
- Create database migrations

### Exercise 3: Load Testing (15 minutes)
- Use Locust or k6 for load testing
- Test rate limiting under load
- Measure performance metrics
- Identify bottlenecks

## Testing and Deployment

### Running with Docker:
```bash
cd docker
docker-compose up --build
```

### Access:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Metrics: http://localhost:8000/api/v1/metrics

## Deliverables

1. Complete production-ready application
2. Docker configuration
3. Monitoring dashboard setup
4. Load testing results
5. Deployment documentation
6. Security checklist

## Resources

- [FastAPI Production](https://fastapi.tiangolo.com/deployment/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Prometheus Metrics](https://prometheus.io/docs/concepts/metric_types/)
- [OpenTelemetry](https://opentelemetry.io/docs/)

