# Day 2 - Medium Level Lab: Multi-Agent Research System with LangGraph

## Setup Instructions

**Recommended: Python 3.11**

1. Create a virtual environment:
```bash
python3.11 -m venv venv
# Or if python3.11 is your default:
python -m venv venv

source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file:
```bash
cp .env.example .env
```

4. Add your OpenAI API key to `.env`

5. Run the application:
```bash
python main.py
```

## Usage

Enter research queries and the system will:
1. Use the Researcher Agent to search the web
2. Use the Summarizer Agent to synthesize findings

Example queries:
- "What is machine learning?"
- "Compare the latest developments in GPT-4 and Claude 3"
- "What are the best practices for deploying AI models?"

## Project Structure
```
Day2_Medium/
├── main.py
├── state.py
├── agents/
│   ├── researcher.py
│   └── summarizer.py
└── graph/
    └── research_graph.py
```

