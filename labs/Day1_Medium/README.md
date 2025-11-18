# Day 1 - Medium Level Lab: Building a Conversational Agent with LangChain

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file from the example:
```bash
cp .env.example .env
```

4. Edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

5. Run the agent:
```bash
python main.py
```

## Usage

The agent supports:
- Basic conversations
- Mathematical calculations (use Calculator tool)
- Web searches (use WebSearch tool)

Example queries:
- "What is 25 * 37?"
- "Search for the latest news about AI"
- "Calculate 100 / 4 and then search for information about that number"

Type 'exit', 'quit', or 'bye' to exit.

