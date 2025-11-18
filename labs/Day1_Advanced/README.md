# Day 1 - Advanced Level Lab: Multi-Tool Agent with RAG Integration

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

3. Create a `.env` file:
```bash
cp .env.example .env
```

4. Edit `.env` and add your OpenAI API key

5. Run the agent:
```bash
python main.py
```

## Usage

### Loading Documents
```
You: load documents/sample.pdf
```

### Querying Documents
```
You: What is the main topic of the document?
```

### Using Tools
- Calculator: "What is 25 * 37?"
- Web Search: "Search for latest AI news"
- Code Execution: "Write a Python function to calculate factorial"

### Getting Conversation Summary
```
You: summary
```

## Project Structure
```
Day1_Advanced/
├── main.py
├── config.py
├── tools/
│   ├── calculator.py
│   ├── web_search.py
│   ├── code_executor.py
│   └── document_qa.py
├── rag/
│   ├── document_loader.py
│   └── vector_store.py
├── documents/  # Place your PDF/text files here
└── vector_store/  # Auto-generated for storing embeddings
```

