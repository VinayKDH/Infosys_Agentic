import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false")
    LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY", "")
    LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "agentic-ai-lab")
    
    # Vector Store
    VECTOR_STORE_DIR = "./vector_store"
    
    # Model Configuration
    MODEL_NAME = "gpt-4"
    TEMPERATURE = 0.7
    MAX_TOKENS = 2000

