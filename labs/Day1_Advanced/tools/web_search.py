from langchain_core.tools import Tool
from langchain_community.tools import DuckDuckGoSearchRun
from typing import List
import asyncio

class AdvancedWebSearch:
    def __init__(self):
        self.search = DuckDuckGoSearchRun()
    
    def search_web(self, query: str) -> str:
        """Search the web and return results"""
        try:
            results = self.search.run(query)
            return f"Search results for '{query}':\n{results}"
        except Exception as e:
            return f"Error searching: {str(e)}"
    
    async def async_search(self, queries: List[str]) -> List[str]:
        """Perform multiple searches asynchronously"""
        tasks = [asyncio.to_thread(self.search_web, query) for query in queries]
        return await asyncio.gather(*tasks)
    
    def get_tool(self) -> Tool:
        """Get LangChain tool"""
        return Tool(
            name="WebSearch",
            func=self.search_web,
            description="""Useful for searching the internet for current information, 
            news, facts, or any information not in the loaded documents.
            Input should be a clear search query."""
        )

