# Day 1 - Medium Level Lab: Building a Conversational Agent with LangChain

## Python Version Recommendation

**Recommended:** Python 3.11 or 3.12 (most stable with LangChain)

**Python 3.14:** Works but may have compatibility warnings. The code includes fallbacks.

## Setup Instructions

1. **Create a virtual environment:**
```bash
# For Python 3.11/3.12 (recommended)
python3.11 -m venv venv
# or
python3.12 -m venv venv

# For Python 3.14
python3.14 -m venv venv
```

2. **Activate virtual environment:**
```bash
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. **Create a `.env` file:**
```bash
# Copy example and edit
# Create .env file with:
OPENAI_API_KEY=your_openai_api_key_here
```

5. **Run the agent:**
```bash
python main.py
```

## Usage

The agent supports:
- **Basic conversations** - Just chat normally
- **Mathematical calculations** - Ask "What is 25 * 37?" or "Calculate 100 / 4"
- **Web searches** - Ask "Search for latest AI news" or "Find information about Python"

Example queries:
- "What is 25 * 37?"
- "Search for the latest news about AI"
- "Calculate 100 / 4 and then search for information about that number"
- "Tell me a joke"

Type 'exit', 'quit', or 'bye' to exit.

## Troubleshooting

### If you get import errors:

1. **Update all packages:**
```bash
pip install --upgrade langchain langchain-openai langchain-community langchain-core
```

2. **Install with all extras:**
```bash
pip install langchain[all]
```

3. **Check Python version:**
```bash
python --version
```
Should be 3.11, 3.12, or 3.14

### If memory import fails:

The code now works without the memory module. It uses a simple in-memory conversation history.

### If you get Pydantic warnings:

These are warnings, not errors. The code will still work. To suppress:
```bash
pip install pydantic>=2.0
```

## Project Structure
```
Day1_Medium/
├── main.py              # Main application (simplified, works everywhere)
├── main_simple.py       # Alternative version with more fallbacks
├── tools.py             # Calculator and web search tools
├── requirements.txt     # Dependencies
└── README.md           # This file
```

## Features

✅ Works with Python 3.11, 3.12, and 3.14  
✅ No complex memory dependencies  
✅ Simple tool integration  
✅ Conversation history  
✅ Error handling with fallbacks  
