from langchain_core.tools import Tool
from langchain_community.tools import DuckDuckGoSearchRun
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

