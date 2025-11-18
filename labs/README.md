# Agentic AI Training - Lab Projects

This directory contains fully functional lab projects for the 3-day Agentic AI Training program.

## Lab Structure

### Day 1 Labs
- **Day1_Medium**: Basic conversational agent with LangChain
- **Day1_Advanced**: Multi-tool agent with RAG integration

### Day 2 Labs
- **Day2_Medium**: Multi-agent research system with LangGraph
- **Day2_Advanced**: Complex multi-agent system with state management

### Day 3 Labs
- **Day3_Medium**: FastAPI deployment of AI agent
- **Day3_Advanced**: Production-ready API with monitoring

## Quick Start

Each lab directory contains:
- Complete source code
- `requirements.txt` for dependencies
- `README.md` with setup instructions
- Example `.env.example` file

### General Setup Steps

1. Navigate to the lab directory:
```bash
cd labs/Day1_Medium  # or any other lab
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
# Copy example and edit
cp .env.example .env
# Add your OPENAI_API_KEY
```

5. Run the application:
```bash
python main.py  # or follow lab-specific instructions
```

## Prerequisites

- Python 3.11+ (tested with Python 3.14)
- OpenAI API key
- (Optional) Redis for Day 3 Advanced lab
- (Optional) Docker for Day 3 Advanced lab

**Note**: All labs have been updated for Python 3.14 compatibility. See `PYTHON_3_14_COMPATIBILITY.md` for details.

## Notes

- Each lab is self-contained and can be run independently
- Make sure to set up your `.env` file with API keys before running
- Some labs require additional services (Redis, Docker) - see individual READMEs

## Support

Refer to the main lab documentation files in the parent directory for detailed explanations and exercises.

## Python 3.14 Compatibility

All labs have been updated to work with Python 3.14. Key changes:
- Updated all package versions to latest compatible releases
- Migrated to LangChain Core imports (`langchain_core`)
- Updated RAG implementation to use LCEL (LangChain Expression Language)
- All Pydantic models use v2 syntax

See `PYTHON_3_14_COMPATIBILITY.md` for detailed information about compatibility updates.

