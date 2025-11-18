from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import initialize_agent, AgentType
from langchain_core.prompts import ChatPromptTemplate
import os

class ResearcherAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.search_tool = DuckDuckGoSearchRun()
        
        # Create agent with search tool
        self.agent = initialize_agent(
            tools=[self.search_tool],
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True
        )
    
    def research(self, query: str) -> str:
        """Research a query using web search"""
        research_prompt = f"""You are a research assistant. Your task is to gather comprehensive 
        information about the following query: {query}
        
        Search the web and collect relevant information. Provide detailed findings with sources.
        Focus on accuracy and completeness."""
        
        try:
            result = self.agent.invoke({"input": research_prompt})
            return result["output"]
        except Exception as e:
            return f"Research error: {str(e)}"

