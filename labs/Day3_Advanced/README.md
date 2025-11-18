# Day 3 - Advanced Level Lab: Production-Ready Agentic API

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file:
```
OPENAI_API_KEY=your_key_here
SECRET_KEY=your-secret-key-here
REDIS_HOST=localhost
REDIS_ENABLED=true
```

4. Start Redis (if using Docker):
```bash
docker run -d -p 6379:6379 redis:7-alpine
```

5. Run the server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Docker Deployment

```bash
cd docker
docker-compose up --build
```

## Features

- ✅ Authentication (JWT)
- ✅ Caching (Redis)
- ✅ Rate Limiting
- ✅ Monitoring (Prometheus metrics)
- ✅ Health Checks
- ✅ Structured Logging

## Access

- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Metrics: http://localhost:8000/api/v1/metrics
- Health: http://localhost:8000/health

