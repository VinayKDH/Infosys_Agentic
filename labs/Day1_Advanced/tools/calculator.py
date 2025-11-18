from langchain_core.tools import Tool

def calculator(expression: str) -> str:
    """Evaluates a mathematical expression safely."""
    try:
        allowed_chars = set('0123456789+-*/()., ')
        if not all(c in allowed_chars for c in expression):
            return "Error: Invalid characters in expression"
        
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"

def get_calculator_tool():
    return Tool(
        name="Calculator",
        func=calculator,
        description="Useful for performing mathematical calculations. Input should be a valid mathematical expression like '2+2' or '10*5'."
    )

