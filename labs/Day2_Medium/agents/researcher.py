from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import os

class ResearcherAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.search_tool = DuckDuckGoSearchRun()
        
        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a research assistant. Use the search tool to find information."),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create agent
        agent = create_react_agent(self.llm, [self.search_tool], prompt)
        
        # Create agent executor
        self.agent = AgentExecutor(
            agent=agent,
            tools=[self.search_tool],
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

