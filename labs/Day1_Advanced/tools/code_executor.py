from langchain_core.tools import Tool
from langchain_experimental.tools import PythonREPLTool

class CodeExecutor:
    def __init__(self):
        self.python_repl = PythonREPLTool()
    
    def execute_python(self, code: str) -> str:
        """Safely execute Python code"""
        try:
            # Basic safety check
            dangerous_keywords = ['import os', 'import sys', 'subprocess', 'eval', 'exec']
            if any(keyword in code.lower() for keyword in dangerous_keywords):
                return "Error: Potentially unsafe code detected. Use only safe Python operations."
            
            result = self.python_repl.run(code)
            return f"Execution result:\n{result}"
        except Exception as e:
            return f"Error executing code: {str(e)}"
    
    def get_tool(self) -> Tool:
        """Get LangChain tool"""
        return Tool(
            name="PythonExecutor",
            func=self.execute_python,
            description="""Useful for executing Python code and performing data analysis.
            Input should be valid Python code. Use this for calculations, data manipulation, or analysis.
            Do NOT use for file system operations or network requests."""
        )

