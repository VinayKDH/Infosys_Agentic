"""
Simplified version that works with all LangChain versions
If main.py doesn't work, use this file instead
"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import LLMChain
from tools import tools
from dotenv import load_dotenv
import os
import re

load_dotenv()

# Try to import memory with fallbacks
try:
    from langchain.memory import ConversationBufferMemory
except ImportError:
    try:
        from langchain_core.memory import ConversationBufferMemory
    except ImportError:
        # Create a simple memory class if not available
        class ConversationBufferMemory:
            def __init__(self, **kwargs):
                self.chat_memory = type('obj', (object,), {'messages': []})()
            
            def save_context(self, inputs, outputs):
                pass
            
            def load_memory_variables(self, inputs):
                return {"chat_history": []}

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY")
)

# Initialize memory
try:
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
except:
    # Fallback: simple memory without return_messages
    memory = ConversationBufferMemory(
        memory_key="chat_history"
    )

# Create prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful AI assistant. You can:
    1. Answer questions
    2. Perform calculations (use Calculator tool)
    3. Search the web (use WebSearch tool)
    
    When you need to calculate, say "CALCULATE: <expression>"
    When you need to search, say "SEARCH: <query>"
    Otherwise, just answer normally."""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
])

# Create chain (try with memory, fallback without if needed)
try:
    chain = LLMChain(llm=llm, prompt=prompt, memory=memory, verbose=True)
except:
    # Fallback without memory
    chain = LLMChain(llm=llm, prompt=prompt, verbose=True)
    memory = None

# Create tools dictionary
tools_dict = {tool.name: tool for tool in tools}

def process_input(user_input: str):
    """Process user input and handle tool calls"""
    user_input_lower = user_input.lower()
    
    # Check for calculator requests
    if "calculate" in user_input_lower or any(op in user_input for op in ["+", "-", "*", "/", "="]):
        # Extract mathematical expression
        calc_match = re.search(r'(\d+(?:\.\d+)?\s*[+\-*/]\s*\d+(?:\.\d+)?)', user_input)
        if calc_match:
            expr = calc_match.group(1)
            try:
                result = tools_dict["Calculator"].func(expr)
                return result
            except:
                pass
    
    # Check for search requests
    if "search" in user_input_lower or "find" in user_input_lower or "look up" in user_input_lower:
        # Extract search query
        search_match = re.search(r'(?:search|find|look up)[\s:]+(.+)', user_input_lower)
        if search_match:
            query = search_match.group(1).strip()
            try:
                result = tools_dict["WebSearch"].func(query)
                return result
            except:
                pass
    
    # Use LLM chain for normal conversation
    result = chain.invoke({"input": user_input})
    return result.get("text", str(result))

# Test the agent
if __name__ == "__main__":
    print("AgentAI: Hello! I can help you with calculations, web searches, and conversations.")
    print("Examples:")
    print("  - 'What is 25 * 37?'")
    print("  - 'Search for latest AI news'")
    print("  - 'Tell me a joke'")
    print()
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("AgentAI: Goodbye!")
            break
        
        try:
            response = process_input(user_input)
            print(f"AgentAI: {response}")
        except Exception as e:
            print(f"AgentAI: Sorry, I encountered an error: {str(e)}")

