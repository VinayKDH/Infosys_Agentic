# Customer Support Email Agent

A LangGraph-based customer support email agent that automatically handles incoming customer emails by classifying them, searching documentation, creating bug tickets, and drafting responses.

## Overview

This agent implements the patterns described in the [LangGraph Thinking Guide](https://docs.langchain.com/oss/python/langgraph/thinking-in-langgraph). It demonstrates:

- **Discrete node design**: Each step is a separate node function
- **State management**: Shared state passed between nodes
- **Conditional routing**: Dynamic flow based on email classification
- **Error handling**: Graceful error handling at each step
- **Human-in-the-loop**: Support for human review when needed

## Features

The agent handles:

1. **Simple product questions**: "How do I reset my password?"
2. **Bug reports**: "The export feature crashes when I select PDF format"
3. **Urgent billing issues**: "I was charged twice for my subscription!"
4. **Feature requests**: "Can you add dark mode to the mobile app?"
5. **Complex technical issues**: "Our API integration fails intermittently with 504 errors"

## Architecture

### Nodes

1. **read_email**: Parses and extracts email content
2. **classify_intent**: Classifies email by intent and urgency using LLM
3. **doc_search**: Searches knowledge base/documentation
4. **bug_tracking**: Creates bug tickets in tracking system
5. **draft_response**: Generates appropriate email response
6. **human_review**: Determines if human review is needed
7. **send_reply**: Sends final email response

### State

The `EmailAgentState` includes:
- Raw email data (content, sender, ID)
- Classification results
- Search results and customer history
- Draft and final responses
- Human review flags
- Error tracking

### Routing Logic

- **Bug reports** → bug_tracking → draft_response
- **Questions** → doc_search → draft_response
- **Critical/Complex** → human_review → send_reply
- **Others** → draft_response → human_review → send_reply

## Setup

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Set up environment variables**:
Create a `.env` file:
```
OPENAI_API_KEY=your_api_key_here
```

3. **Run the agent**:
```bash
python main.py
```

## Usage

The agent provides an interactive interface where you can:

1. **Process example emails**: Test with pre-defined scenarios
2. **Enter custom emails**: Process your own email content
3. **View results**: See classification, search results, and generated responses

## Example Workflow

```
Email: "How do I reset my password?"

1. read_email → Extracts email content
2. classify_intent → Classifies as "question" (low urgency)
3. doc_search → Finds password reset documentation
4. draft_response → Generates helpful response with instructions
5. human_review → Auto-approves (low urgency)
6. send_reply → Sends response to customer
```

## Key Design Patterns

### 1. Discrete Steps
Each node does one specific thing, making the workflow:
- Easy to debug (inspect state between steps)
- Resumable (checkpoints at node boundaries)
- Observable (see progress at each step)

### 2. State as Shared Memory
State stores raw data, not formatted text:
- Different nodes can format data differently
- Easy to change prompts without modifying state
- Clear debugging (see exactly what each node received)

### 3. Conditional Routing
Nodes make routing decisions using `Command` objects:
- Explicit flow control
- Traceable decisions
- Easy to understand what happens next

### 4. Error Handling
Different error types handled appropriately:
- Transient failures: Retry with exponential backoff
- LLM errors: Fallback to human review
- Unexpected errors: Log and escalate

## Extending the Agent

### Add Real Email Integration
Replace `read_email` to connect to:
- IMAP/SMTP servers
- Email APIs (SendGrid, Mailgun)
- Webhook endpoints

### Add Vector Search
Replace simple keyword search with:
- FAISS vector store
- Pinecone/Weaviate
- Embedding-based similarity search

### Add Real Bug Tracking
Connect `bug_tracking` to:
- Jira
- GitHub Issues
- Linear
- Custom ticketing system

### Add Human-in-the-Loop
Use `interrupt()` for real human review:
```python
from langgraph.types import interrupt

def human_review(state):
    if requires_review:
        interrupt()  # Pauses execution
        # Resume with human input
```

## References

- [LangGraph Thinking Guide](https://docs.langchain.com/oss/python/langgraph/thinking-in-langgraph)
- [LangGraph Documentation](https://python.langchain.com/docs/langgraph)
- [LangGraph State Management](https://python.langchain.com/docs/langgraph/concepts/low_level#state)

## License

This is an educational example based on LangGraph patterns.

