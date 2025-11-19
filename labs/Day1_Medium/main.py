from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
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

# Create prompt template for the agent
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful AI assistant. You have access to tools to help answer questions.
    Use the tools when needed, especially for calculations and web searches.
    Always be polite and helpful."""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# Create the agent
agent = create_react_agent(llm, tools, prompt)

# Create agent executor with memory
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=5
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
            response = agent_executor.invoke({"input": user_input})
            print(f"AgentAI: {response['output']}")
        except Exception as e:
            print(f"AgentAI: Sorry, I encountered an error: {str(e)}")

