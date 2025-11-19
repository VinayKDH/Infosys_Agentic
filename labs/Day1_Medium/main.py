from langchain_openai import ChatOpenAI
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

# Try to import and create agent with fallbacks
try:
    # Try newer LangChain API
    from langchain.agents import create_openai_tools_agent, AgentExecutor
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful AI assistant. You have access to tools to help answer questions.
        Use the tools when needed, especially for calculations and web searches.
        Always be polite and helpful."""),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    agent = create_openai_tools_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5
    )
except ImportError:
    try:
        # Try alternative import path
        from langchain_core.agents import AgentExecutor
        from langchain.agents import create_react_agent
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful AI assistant. You have access to tools to help answer questions.
            Use the tools when needed, especially for calculations and web searches.
            Always be polite and helpful."""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        agent = create_react_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            memory=memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5
        )
    except ImportError:
        # Fallback: Use simple chain with tool calling
        from langchain.chains import LLMChain
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful AI assistant. You have access to tools.
            When you need to use a tool, describe what you need and I'll help you."""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ])
        chain = LLMChain(llm=llm, prompt=prompt, memory=memory, verbose=True)
        
        # Create a wrapper to handle tool calls
        class SimpleAgentExecutor:
            def __init__(self, chain, tools):
                self.chain = chain
                self.tools = {tool.name: tool for tool in tools}
            
            def invoke(self, input_dict):
                user_input = input_dict.get("input", "")
                # Check if user wants to use a tool
                if "calculate" in user_input.lower() or any(op in user_input for op in ["+", "-", "*", "/"]):
                    # Try calculator
                    for tool in self.tools.values():
                        if tool.name == "Calculator":
                            try:
                                # Extract expression
                                import re
                                expr = re.findall(r'[\d+\-*/()., ]+', user_input)
                                if expr:
                                    result = tool.func(expr[0].strip())
                                    return {"output": result}
                            except:
                                pass
                
                # Use LLM chain
                result = self.chain.invoke(input_dict)
                return {"output": result.get("text", str(result))}
        
        agent_executor = SimpleAgentExecutor(chain, tools)

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

