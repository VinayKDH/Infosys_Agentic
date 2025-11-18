from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os

class SummarizerAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.3,  # Lower temperature for more focused summaries
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert summarizer. Your task is to synthesize research findings 
            into a clear, concise, and well-structured answer.
            
            Guidelines:
            - Provide a comprehensive answer based on the research
            - Organize information logically
            - Include key points and important details
            - Write in a clear, professional tone
            - If information is incomplete, mention it"""),
            ("human", """Original Query: {query}
            
            Research Findings:
            {research_results}
            
            Please provide a comprehensive summary that answers the query.""")
        ])
    
    def summarize(self, query: str, research_results: str) -> str:
        """Summarize research results into a final answer"""
        chain = self.prompt | self.llm
        
        try:
            response = chain.invoke({
                "query": query,
                "research_results": research_results
            })
            return response.content
        except Exception as e:
            return f"Summarization error: {str(e)}"

