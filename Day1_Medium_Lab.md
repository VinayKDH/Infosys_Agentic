# Day 1 - Medium Level Lab: Building a Conversational Agent with LangChain

## Lab Overview
**Duration:** 90 minutes  
**Objective:** Build a functional conversational agent using LangChain with memory, tools, and prompt templates.

## Prerequisites
- Python 3.11+ installed
- OpenAI API key
- Basic understanding of Python and APIs

## Learning Outcomes
By the end of this lab, you will:
- Set up LangChain environment and dependencies
- Create prompt templates with few-shot examples
- Implement conversation memory using ConversationBufferMemory
- Integrate custom tools (calculator, web search)
- Build a complete conversational agent chain

## Lab Setup

### Step 1: Environment Setup
```bash
# Create virtual environment
python -m venv agentic_ai_env
source agentic_ai_env/bin/activate  # On Windows: agentic_ai_env\Scripts\activate

# Install dependencies
pip install langchain langchain-openai langchain-community python-dotenv requests
```

### Step 2: Project Structure
```
day1_medium_lab/
├── main.py
├── tools.py
├── .env
└── requirements.txt
```

### Step 3: Configuration
Create `.env` file:
```
OPENAI_API_KEY=your_api_key_here
```

Create `requirements.txt`:
```
langchain==0.1.0
langchain-openai==0.0.5
langchain-community==0.0.20
python-dotenv==1.0.0
requests==2.31.0
```

## Lab Implementation

### Part 1: Basic LLM Chain with Prompt Template (20 minutes)

**File: `main.py`**
```python
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY")
)

# Create prompt template with few-shot examples
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful AI assistant named AgentAI. 
    You can help users with:
    - Answering questions
    - Performing calculations
    - Searching the web
    - Having conversations
    
    Always be polite and concise. If you need to use a tool, mention it clearly."""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])

# Initialize memory
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

# Create chain
chain = LLMChain(
    llm=llm,
    prompt=prompt,
    memory=memory,
    verbose=True
)

# Test the chain
if __name__ == "__main__":
    print("AgentAI: Hello! How can I help you today?")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("AgentAI: Goodbye!")
            break
        
        response = chain.invoke({"input": user_input})
        print(f"AgentAI: {response['text']}")
```

**Task 1.1:** Run the basic chain and test with:
- "What is the capital of France?"
- "Tell me a joke"
- "What did I just ask you?" (to test memory)

### Part 2: Adding Custom Tools (30 minutes)

**File: `tools.py`**
```python
from langchain.tools import Tool
from langchain.utilities import DuckDuckGoSearchRun
import math

# Calculator tool
def calculator(expression: str) -> str:
    """Evaluates a mathematical expression safely."""
    try:
        # Only allow safe mathematical operations
        allowed_chars = set('0123456789+-*/()., ')
        if not all(c in allowed_chars for c in expression):
            return "Error: Invalid characters in expression"
        
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"

# Web search tool
search = DuckDuckGoSearchRun()

# Create tool list
tools = [
    Tool(
        name="Calculator",
        func=calculator,
        description="Useful for performing mathematical calculations. Input should be a valid mathematical expression like '2+2' or '10*5'."
    ),
    Tool(
        name="WebSearch",
        func=search.run,
        description="Useful for searching the internet for current information, news, or facts. Input should be a search query."
    )
]
```

**File: `main.py` (Updated)**
```python
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from tools import tools
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY")
)

# Initialize memory
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

# Create agent with tools
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    memory=memory,
    verbose=True,
    handle_parsing_errors=True
)

# Test the agent
if __name__ == "__main__":
    print("AgentAI: Hello! I can help you with calculations, web searches, and conversations.")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("AgentAI: Goodbye!")
            break
        
        try:
            response = agent.invoke({"input": user_input})
            print(f"AgentAI: {response['output']}")
        except Exception as e:
            print(f"AgentAI: Sorry, I encountered an error: {str(e)}")
```

**Task 2.1:** Test the agent with:
- "What is 25 * 37?"
- "Search for the latest news about AI"
- "Calculate 100 / 4 and then search for information about that number"

### Part 3: Enhanced Prompt Engineering (20 minutes)

**Task 3.1:** Modify the agent to use a custom system prompt:
```python
from langchain.agents import AgentExecutor
from langchain.agents.conversational_chat.base import ConversationalChatAgent
from langchain.prompts import MessagesPlaceholder

# Custom system message
system_message = """You are AgentAI, an intelligent assistant with access to tools.
Guidelines:
1. Always think step-by-step before using tools
2. Explain what tool you're using and why
3. Provide clear, concise answers
4. Remember previous conversation context
5. If a calculation is simple, you can do it yourself; otherwise use the calculator tool
"""

# Create agent with custom prompt
agent_prompt = ConversationalChatAgent.create_prompt(
    tools=tools,
    system_message=system_message,
    human_message="{input}",
    placeholder=MessagesPlaceholder(variable_name="chat_history")
)

agent = ConversationalChatAgent(
    llm=llm,
    tools=tools,
    prompt=agent_prompt
)

agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=True,
    handle_parsing_errors=True
)
```

**Task 3.2:** Test with complex queries:
- "What's the weather like today? If it's sunny, calculate 2^10, otherwise search for indoor activities"
- "Remember that my favorite number is 42. What is 42 * 3?"

### Part 4: Memory Management (20 minutes)

**Task 4.1:** Implement conversation summary memory for long conversations:
```python
from langchain.memory import ConversationSummaryMemory

# Replace ConversationBufferMemory with ConversationSummaryMemory
memory = ConversationSummaryMemory(
    llm=llm,
    memory_key="chat_history",
    return_messages=True
)
```

**Task 4.2:** Test memory persistence:
1. Have a 5-6 turn conversation
2. Ask the agent to recall information from earlier
3. Compare behavior with BufferMemory vs SummaryMemory

## Lab Exercises

### Exercise 1: Add a New Tool (15 minutes)
Create a custom tool that:
- Takes a city name as input
- Returns a formatted string with timezone information
- Integrate it into your agent

### Exercise 2: Error Handling (10 minutes)
Enhance error handling:
- Add try-catch blocks for tool failures
- Provide user-friendly error messages
- Implement retry logic for failed tool calls

### Exercise 3: Conversation Analysis (15 minutes)
Add functionality to:
- Count the number of tool calls made in a conversation
- Track which tools are used most frequently
- Display a summary at the end of the conversation

## Testing Checklist

- [ ] Basic conversation works without tools
- [ ] Calculator tool executes correctly
- [ ] Web search tool returns results
- [ ] Memory persists across multiple turns
- [ ] Agent chooses appropriate tools
- [ ] Error handling works for invalid inputs
- [ ] System prompt influences agent behavior

## Deliverables

1. Complete `main.py` with all features
2. `tools.py` with at least 2 custom tools
3. A test script demonstrating:
   - Basic conversation
   - Tool usage
   - Memory functionality
4. A brief report (1 page) explaining:
   - Design decisions
   - Challenges faced
   - Improvements made

## Troubleshooting

**Issue:** "OpenAI API key not found"
- Solution: Ensure `.env` file exists and contains `OPENAI_API_KEY=your_key`

**Issue:** "Tool not found" error
- Solution: Verify tools are properly imported and passed to the agent

**Issue:** Memory not working
- Solution: Check that `memory_key` matches the prompt variable name

## Next Steps

After completing this lab:
- Review the agent's decision-making process
- Experiment with different temperature values
- Try different LLM models (gpt-3.5-turbo vs gpt-4)
- Prepare for Day 2: LangGraph multi-agent systems

## Resources

- [LangChain Agents Documentation](https://python.langchain.com/docs/modules/agents/)
- [LangChain Tools Documentation](https://python.langchain.com/docs/modules/tools/)
- [LangChain Memory Documentation](https://python.langchain.com/docs/modules/memory/)

