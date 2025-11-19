from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import os

# Try to import agent components
try:
    from langchain.agents import AgentExecutor, create_openai_tools_agent
    AGENT_AVAILABLE = True
    AGENT_TYPE = "openai_tools"
except ImportError:
    try:
        from langchain.agents import AgentExecutor, create_react_agent
        AGENT_AVAILABLE = True
        AGENT_TYPE = "react"
    except ImportError:
        AGENT_AVAILABLE = False

class ResearcherAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.search_tool = DuckDuckGoSearchRun()
        
        if AGENT_AVAILABLE:
            # Create prompt template
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a research assistant. Use the search tool to find information."),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])
            
            # Create agent
            if AGENT_TYPE == "openai_tools":
                agent = create_openai_tools_agent(self.llm, [self.search_tool], prompt)
            else:
                agent = create_react_agent(self.llm, [self.search_tool], prompt)
            
            # Create agent executor
            self.agent = AgentExecutor(
                agent=agent,
                tools=[self.search_tool],
                verbose=True,
                handle_parsing_errors=True
            )
        else:
            self.agent = None
    
    def research(self, query: str) -> str:
        """Research a query using web search"""
        research_prompt = f"""You are a research assistant. Your task is to gather comprehensive 
        information about the following query: {query}
        
        Search the web and collect relevant information. Provide detailed findings with sources.
        Focus on accuracy and completeness."""
        
        try:
            if self.agent:
                result = self.agent.invoke({"input": research_prompt})
                return result["output"] if isinstance(result, dict) else str(result)
            else:
                # Fallback: direct search
                search_result = self.search_tool.run(query)
                return f"Research findings for '{query}':\n{search_result}"
        except Exception as e:
            return f"Research error: {str(e)}"

