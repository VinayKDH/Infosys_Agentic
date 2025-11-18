# Day 2 - Advanced Level Lab: Complex Multi-Agent System

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

4. Run the application:
```bash
python main.py
```

## Usage

The system uses 4 agents:
- **Planner**: Breaks down queries into tasks
- **Researcher**: Gathers information
- **Coder**: Generates code
- **Reviewer**: Quality assurance

Example queries:
- "Research FastAPI best practices and create a sample REST API"
- "Create a data analysis pipeline: research pandas best practices, write code to load and analyze a CSV"

## Project Structure
```
Day2_Advanced/
├── main.py
├── state.py
├── agents/
│   ├── planner.py
│   ├── researcher.py
│   ├── coder.py
│   └── reviewer.py
├── graph/
│   └── multi_agent_graph.py
└── utils/
    └── routing.py
```

