from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from state import Task, TaskStatus
import os
from datetime import datetime

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
            handle_parsing_errors=True,
            max_iterations=3
        )
    
    def research(self, task: Task, context: dict = None) -> dict:
        """Perform research for a task"""
        query = task["description"]
        
        if context:
            query = f"{query}\n\nContext from previous tasks: {context}"
        
        research_prompt = f"""Research the following topic comprehensively:
        {query}
        
        Provide detailed findings with sources. Focus on accuracy and relevance."""
        
        try:
            result = self.agent.invoke({"input": research_prompt})
            
            return {
                "task_id": task["id"],
                "findings": result["output"],
                "sources": self._extract_sources(result["output"]),
                "status": TaskStatus.COMPLETED,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "task_id": task["id"],
                "findings": f"Research error: {str(e)}",
                "sources": [],
                "status": TaskStatus.FAILED,
                "timestamp": datetime.now().isoformat()
            }
    
    def _extract_sources(self, text: str) -> list:
        """Extract source URLs from research text"""
        import re
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        return urls[:5]

