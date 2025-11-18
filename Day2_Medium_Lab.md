# Day 2 - Medium Level Lab: Building a Multi-Agent Research System with LangGraph

## Lab Overview
**Duration:** 90 minutes  
**Objective:** Build a multi-agent research system using LangGraph with researcher and summarizer agents that collaborate to answer complex queries.

## Prerequisites
- Completed Day 1 labs
- Understanding of graph-based workflows
- Basic knowledge of state machines

## Learning Outcomes
By the end of this lab, you will:
- Understand LangGraph concepts (nodes, edges, state)
- Build a graph-based agent workflow
- Implement multi-agent collaboration
- Manage state across agent interactions
- Add conditional routing and flow control
- Integrate LangSmith for observability

## Lab Setup

### Step 1: Environment Setup
```bash
pip install langchain langchain-openai langchain-community langgraph
pip install langsmith python-dotenv
pip install duckduckgo-search beautifulsoup4
```

### Step 2: Project Structure
```
day2_medium_lab/
├── main.py
├── agents/
│   ├── __init__.py
│   ├── researcher.py
│   └── summarizer.py
├── graph/
│   ├── __init__.py
│   └── research_graph.py
├── state.py
├── .env
└── requirements.txt
```

## Lab Implementation

### Part 1: Define Graph State (15 minutes)

**File: `state.py`**
```python
from typing import TypedDict, List, Annotated
from langchain_core.messages import BaseMessage
import operator

class ResearchState(TypedDict):
    """State schema for the research graph"""
    messages: Annotated[List[BaseMessage], operator.add]
    research_results: str
    final_answer: str
    query: str
    iteration_count: int
```

### Part 2: Create Agent Nodes (30 minutes)

**File: `agents/researcher.py`**
```python
from langchain_openai import ChatOpenAI
from langchain.tools import DuckDuckGoSearchRun
from langchain.agents import initialize_agent, AgentType
from langchain.prompts import ChatPromptTemplate
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
```

**File: `agents/summarizer.py`**
```python
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
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
```

### Part 3: Build LangGraph (30 minutes)

**File: `graph/research_graph.py`**
```python
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
```

### Part 4: Main Application (15 minutes)

**File: `main.py`**
```python
from graph.research_graph import ResearchGraph
from dotenv import load_dotenv
import os

load_dotenv()

def main():
    print("=" * 60)
    print("Multi-Agent Research System")
    print("=" * 60)
    print("\nThis system uses two agents:")
    print("1. Researcher Agent - Searches the web for information")
    print("2. Summarizer Agent - Synthesizes findings into answers")
    print("\n" + "=" * 60)
    
    # Initialize graph
    research_graph = ResearchGraph()
    
    while True:
        query = input("\nEnter your research query (or 'exit' to quit): ").strip()
        
        if query.lower() in ['exit', 'quit', 'bye']:
            print("\nGoodbye!")
            break
        
        if not query:
            print("Please enter a valid query.")
            continue
        
        print(f"\nProcessing query: {query}")
        print("-" * 60)
        
        try:
            # Run the graph
            result = research_graph.run(query)
            
            # Display results
            print("\n" + "=" * 60)
            print("FINAL ANSWER")
            print("=" * 60)
            print(result["final_answer"])
            print("\n" + "=" * 60)
            print(f"Iterations: {result['iteration_count']}")
            print("=" * 60)
            
        except Exception as e:
            print(f"\nError: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
```

## Lab Exercises

### Exercise 1: Add Quality Check Node (20 minutes)
Create a quality checker agent that:
- Reviews the research results
- Determines if more research is needed
- Routes back to researcher if quality is insufficient
- Uses conditional edges in LangGraph

**Hint:** Use `workflow.add_conditional_edges()` for routing logic.

### Exercise 2: Add Error Handling (15 minutes)
Enhance the graph with:
- Try-catch blocks in each node
- Error state handling
- Retry logic for failed operations
- User-friendly error messages

### Exercise 3: Add LangSmith Tracing (15 minutes)
Integrate LangSmith:
1. Set up LangSmith API key in `.env`
2. Add tracing to graph execution
3. View traces in LangSmith dashboard
4. Analyze agent performance

## Testing Scenarios

### Test 1: Simple Query
**Input:** "What is machine learning?"
**Expected:** Research → Summarize → Clear answer

### Test 2: Complex Query
**Input:** "Compare the latest developments in GPT-4 and Claude 3"
**Expected:** Multiple searches → Comprehensive comparison

### Test 3: Multi-Step Query
**Input:** "What are the best practices for deploying AI models in production?"
**Expected:** Research → Quality check → Additional research if needed → Summary

## Advanced Features to Add

### Feature 1: Conditional Routing
```python
def should_continue_research(state: ResearchState) -> str:
    """Determine if more research is needed"""
    research_results = state.get("research_results", "")
    iteration = state.get("iteration_count", 0)
    
    # Check if research is sufficient
    if len(research_results) < 500:
        return "researcher"  # Need more research
    elif iteration >= 3:
        return "summarizer"  # Max iterations reached
    else:
        return "summarizer"  # Proceed to summary

# Add conditional edge
workflow.add_conditional_edges(
    "researcher",
    should_continue_research,
    {
        "researcher": "researcher",
        "summarizer": "summarizer"
    }
)
```

### Feature 2: Parallel Research
Research multiple aspects in parallel:
```python
def parallel_research_node(state: ResearchState) -> ResearchState:
    """Research multiple aspects in parallel"""
    query = state["query"]
    
    # Split query into sub-queries
    sub_queries = split_query(query)
    
    # Research each in parallel (using async)
    results = [researcher.research(q) for q in sub_queries]
    
    state["research_results"] = "\n\n".join(results)
    return state
```

## Deliverables

1. Complete implementation with:
   - Research graph
   - Two agent nodes
   - State management
   - Error handling

2. Test results for at least 5 different queries

3. Documentation:
   - Graph architecture diagram
   - State flow explanation
   - Agent responsibilities

4. LangSmith trace analysis:
   - Execution time per node
   - Token usage
   - Error rates

## Troubleshooting

**Issue:** Graph compilation errors
- Solution: Ensure all nodes return the state dictionary

**Issue:** State not persisting
- Solution: Use `Annotated` with `operator.add` for list fields

**Issue:** LangSmith not tracing
- Solution: Set `LANGCHAIN_TRACING_V2=true` and `LANGCHAIN_API_KEY` in `.env`

## Resources

- [LangGraph Documentation](https://python.langchain.com/docs/langgraph)
- [LangGraph Concepts](https://python.langchain.com/docs/langgraph/concepts)
- [State Management](https://python.langchain.com/docs/langgraph/concepts/low_level#state)
- [LangSmith Tracing](https://docs.smith.langchain.com/)

