"""
Day 1 Medium Lab - Conversational Agent with LangChain
This version is compatible with Python 3.11, 3.12, and 3.14
"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from tools import tools
from dotenv import load_dotenv
import os
import re

load_dotenv()

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY")
)

# Simple conversation history (in-memory)
conversation_history = []

# Create tools dictionary
tools_dict = {tool.name: tool for tool in tools}

def process_input(user_input: str):
    """Process user input and handle tool calls"""
    global conversation_history
    
    user_input_lower = user_input.lower()
    
    # Check for calculator requests
    if any(op in user_input for op in ["+", "-", "*", "/", "="]) or "calculate" in user_input_lower:
        # Extract mathematical expression
        # Try to find expressions like "25 * 37" or "what is 2+2"
        calc_patterns = [
            r'(\d+(?:\.\d+)?)\s*([+\-*/])\s*(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*([+\-*/])\s*(\d+(?:\.\d+)?)',
        ]
        
        for pattern in calc_patterns:
            calc_match = re.search(pattern, user_input)
            if calc_match:
                expr = calc_match.group(0).strip()
                try:
                    result = tools_dict["Calculator"].func(expr)
                    conversation_history.append(f"User: {user_input}")
                    conversation_history.append(f"Assistant: {result}")
                    return result
                except Exception as e:
                    pass
    
    # Check for search requests
    if "search" in user_input_lower or "find" in user_input_lower or "look up" in user_input_lower:
        # Extract search query
        search_patterns = [
            r'(?:search|find|look up)[\s:]+(.+)',
            r'search for (.+)',
            r'find (.+)',
        ]
        
        for pattern in search_patterns:
            search_match = re.search(pattern, user_input_lower)
            if search_match:
                query = search_match.group(1).strip()
                try:
                    result = tools_dict["WebSearch"].func(query)
                    conversation_history.append(f"User: {user_input}")
                    conversation_history.append(f"Assistant: {result[:200]}...")
                    return result
                except Exception as e:
                    return f"Search error: {str(e)}"
    
    # Build context from conversation history
    context = "\n".join(conversation_history[-6:]) if conversation_history else ""
    
    # Create prompt with conversation history
    if context:
        prompt_text = f"""You are a helpful AI assistant. You have access to tools for calculations and web searches.
        
Previous conversation:
{context}

Current user input: {user_input}

Provide a helpful response. If the user asks for calculations or searches, mention that you can help with that."""
    else:
        prompt_text = f"""You are a helpful AI assistant. You can help with:
- Answering questions
- Performing calculations (just ask me to calculate something)
- Searching the web (just ask me to search for something)

User: {user_input}
Assistant:"""
    
    # Use LLM for normal conversation
    try:
        response = llm.invoke(prompt_text)
        answer = response.content if hasattr(response, 'content') else str(response)
        
        # Update conversation history
        conversation_history.append(f"User: {user_input}")
        conversation_history.append(f"Assistant: {answer}")
        
        # Keep only last 10 exchanges
        if len(conversation_history) > 20:
            conversation_history = conversation_history[-20:]
        
        return answer
    except Exception as e:
        return f"Error: {str(e)}"

# Test the agent
if __name__ == "__main__":
    print("=" * 60)
    print("AgentAI: Hello! I can help you with:")
    print("  - Calculations (e.g., 'What is 25 * 37?')")
    print("  - Web searches (e.g., 'Search for latest AI news')")
    print("  - General conversations")
    print("=" * 60)
    print()
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("\nAgentAI: Goodbye!")
            break
        
        if not user_input.strip():
            continue
        
        try:
            response = process_input(user_input)
            print(f"\nAgentAI: {response}")
        except Exception as e:
            print(f"\nAgentAI: Sorry, I encountered an error: {str(e)}")
            import traceback
            traceback.print_exc()
