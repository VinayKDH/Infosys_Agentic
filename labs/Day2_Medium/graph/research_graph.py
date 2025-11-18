from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from agents.researcher import ResearcherAgent
from agents.summarizer import SummarizerAgent
from state import ResearchState

class ResearchGraph:
    def __init__(self):
        self.researcher = ResearcherAgent()
        self.summarizer = SummarizerAgent()
        self.graph = self._build_graph()
    
    def _build_graph(self):
        """Build the research graph"""
        # Create graph
        workflow = StateGraph(ResearchState)
        
        # Add nodes
        workflow.add_node("researcher", self.research_node)
        workflow.add_node("summarizer", self.summarize_node)
        
        # Define edges
        workflow.set_entry_point("researcher")
        workflow.add_edge("researcher", "summarizer")
        workflow.add_edge("summarizer", END)
        
        # Compile graph
        return workflow.compile()
    
    def research_node(self, state: ResearchState) -> ResearchState:
        """Node for research agent"""
        print("\n[Researcher Agent] Starting research...")
        
        # Get the latest query from messages
        query = state.get("query", "")
        if not query and state.get("messages"):
            # Extract query from last human message
            for msg in reversed(state["messages"]):
                if isinstance(msg, HumanMessage):
                    query = msg.content
                    break
        
        # Perform research
        research_results = self.researcher.research(query)
        
        # Update state
        state["research_results"] = research_results
        state["messages"].append(AIMessage(content=f"Research completed: {research_results[:200]}..."))
        state["iteration_count"] = state.get("iteration_count", 0) + 1
        
        print(f"[Researcher Agent] Research complete. Found {len(research_results)} characters of information.")
        
        return state
    
    def summarize_node(self, state: ResearchState) -> ResearchState:
        """Node for summarizer agent"""
        print("\n[Summarizer Agent] Creating summary...")
        
        query = state.get("query", "")
        research_results = state.get("research_results", "")
        
        # Generate summary
        final_answer = self.summarizer.summarize(query, research_results)
        
        # Update state
        state["final_answer"] = final_answer
        state["messages"].append(AIMessage(content=final_answer))
        
        print(f"[Summarizer Agent] Summary complete.")
        
        return state
    
    def run(self, query: str) -> dict:
        """Execute the research graph"""
        initial_state = {
            "messages": [HumanMessage(content=query)],
            "query": query,
            "research_results": "",
            "final_answer": "",
            "iteration_count": 0
        }
        
        result = self.graph.invoke(initial_state)
        return result

