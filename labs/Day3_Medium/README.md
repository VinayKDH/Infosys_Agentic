# Day 3 - Medium Level Lab: Deploying AI Agent as FastAPI Service

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

3. Create a `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your_key_here
```

4. Run the server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or:
```bash
python -m app.main
```

## Usage

### Access the API
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Test with curl
```bash
# Query endpoint
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is machine learning?", "stream": false}'

# Stream endpoint
curl -X POST "http://localhost:8000/api/v1/query/stream" \
  -H "Content-Type: application/json" \
  -d '{"query": "Explain AI in simple terms"}'
```

## Project Structure
```
Day3_Medium/
├── app/
│   ├── main.py
│   ├── models.py
│   ├── agent_service.py
│   └── routes/
│       └── agent.py
└── requirements.txt
```

