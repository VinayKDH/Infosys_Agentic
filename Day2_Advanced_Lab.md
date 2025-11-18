# Day 2 - Advanced Level Lab: Complex Multi-Agent System with Advanced State Management

## Lab Overview
**Duration:** 120 minutes  
**Objective:** Build a sophisticated multi-agent system with a planner, researcher, coder, and reviewer agents using LangGraph with advanced state management, human-in-the-loop, and dynamic routing.

## Prerequisites
- Completed Day 2 Medium Lab
- Understanding of async programming
- Familiarity with complex state machines

## Learning Outcomes
By the end of this lab, you will:
- Design and implement a 4-agent collaborative system
- Use advanced LangGraph features (human-in-the-loop, interrupts)
- Implement dynamic state management with checkpoints
- Create conditional routing with multiple decision points
- Add agent-to-agent communication patterns
- Implement observability and monitoring

## Lab Setup

### Step 1: Environment Setup
```bash
pip install langchain langchain-openai langchain-community langgraph
pip install langsmith python-dotenv
pip install duckduckgo-search beautifulsoup4
pip install aiohttp asyncio
pip install pydantic
```

### Step 2: Project Structure
```
day2_advanced_lab/
├── main.py
├── agents/
│   ├── __init__.py
│   ├── planner.py
│   ├── researcher.py
│   ├── coder.py
│   └── reviewer.py
├── graph/
│   ├── __init__.py
│   └── multi_agent_graph.py
├── state.py
├── utils/
│   ├── __init__.py
│   ├── checkpoints.py
│   └── routing.py
├── .env
└── requirements.txt
```

## Lab Implementation

### Part 1: Advanced State Management (20 minutes)

**File: `state.py`**
```python
from typing import TypedDict, List, Annotated, Optional, Dict, Any
from langchain_core.messages import BaseMessage
import operator
from datetime import datetime
from enum import Enum

class AgentRole(str, Enum):
    PLANNER = "planner"
    RESEARCHER = "researcher"
    CODER = "coder"
    REVIEWER = "reviewer"

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_REVIEW = "needs_review"

class Task(TypedDict):
    id: str
    description: str
    assigned_to: AgentRole
    status: TaskStatus
    result: Optional[str]
    dependencies: List[str]
    created_at: str
    completed_at: Optional[str]

class MultiAgentState(TypedDict):
    """Advanced state schema for multi-agent system"""
    # Messages
    messages: Annotated[List[BaseMessage], operator.add]
    
    # User query
    original_query: str
    
    # Planning
    plan: Optional[Dict[str, Any]]
    tasks: Annotated[List[Task], operator.add]
    current_task_id: Optional[str]
    
    # Research
    research_findings: Annotated[List[Dict[str, str]], operator.add]
    
    # Code
    code_artifacts: Annotated[List[Dict[str, str]], operator.add]
    
    # Review
    review_feedback: Annotated[List[Dict[str, str]], operator.add]
    
    # Final output
    final_output: str
    
    # Metadata
    iteration_count: int
    agent_history: Annotated[List[Dict[str, Any]], operator.add]
    errors: Annotated[List[str], operator.add]
    requires_human_input: bool
    human_feedback: Optional[str]
```

### Part 2: Agent Implementations (40 minutes)

**File: `agents/planner.py`**
```python
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List
from state import Task, AgentRole, TaskStatus
import os
import json
import uuid
from datetime import datetime

class TaskPlan(BaseModel):
    tasks: List[dict] = Field(description="List of tasks to complete")
    reasoning: str = Field(description="Reasoning behind the plan")

class PlannerAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.3,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.parser = PydanticOutputParser(pydantic_object=TaskPlan)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert planning agent. Your role is to break down complex 
            queries into actionable tasks.
            
            Analyze the user's request and create a detailed plan with:
            1. Research tasks (if information gathering is needed)
            2. Coding tasks (if code generation is required)
            3. Review tasks (for quality assurance)
            
            Consider dependencies between tasks. Tasks should be specific and actionable.
            
            {format_instructions}"""),
            ("human", "User Query: {query}\n\nCreate a detailed plan to address this query.")
        ]).partial(format_instructions=self.parser.get_format_instructions())
    
    def create_plan(self, query: str) -> dict:
        """Create a plan from user query"""
        chain = self.prompt | self.llm | self.parser
        
        try:
            result = chain.invoke({"query": query})
            
            # Convert to tasks
            tasks = []
            for i, task_desc in enumerate(result.tasks):
                task = Task(
                    id=str(uuid.uuid4()),
                    description=task_desc.get("description", ""),
                    assigned_to=AgentRole(task_desc.get("agent", "researcher")),
                    status=TaskStatus.PENDING,
                    result=None,
                    dependencies=task_desc.get("dependencies", []),
                    created_at=datetime.now().isoformat(),
                    completed_at=None
                )
                tasks.append(task)
            
            return {
                "tasks": tasks,
                "reasoning": result.reasoning,
                "plan_structure": json.dumps([t["description"] for t in result.tasks], indent=2)
            }
        except Exception as e:
            return {
                "tasks": [],
                "reasoning": f"Error creating plan: {str(e)}",
                "plan_structure": ""
            }
```

**File: `agents/researcher.py`**
```python
from langchain_openai import ChatOpenAI
from langchain.tools import DuckDuckGoSearchRun
from langchain.agents import initialize_agent, AgentType
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
        
        self.agent = initialize_agent(
            tools=[self.search_tool],
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
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
        # Simple extraction - can be enhanced
        import re
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        return urls[:5]  # Limit to 5 sources
```

**File: `agents/coder.py`**
```python
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from state import Task, TaskStatus
import os
from datetime import datetime
import re

class CoderAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.2,  # Lower temperature for code generation
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert software developer. Generate clean, well-documented code.
            
            Guidelines:
            - Write production-ready code
            - Include proper error handling
            - Add comments and docstrings
            - Follow best practices
            - Consider edge cases"""),
            ("human", """Task: {task_description}
            
            Context/Requirements:
            {context}
            
            Generate the code to complete this task. Include:
            1. Complete code implementation
            2. Brief explanation
            3. Usage examples if applicable""")
        ])
    
    def generate_code(self, task: Task, context: dict = None) -> dict:
        """Generate code for a task"""
        context_str = ""
        if context:
            context_str = f"Research findings: {context.get('research', '')}\n"
            context_str += f"Previous code: {context.get('code', '')}"
        
        chain = self.prompt | self.llm
        
        try:
            response = chain.invoke({
                "task_description": task["description"],
                "context": context_str
            })
            
            code_content = response.content
            code_blocks = self._extract_code_blocks(code_content)
            
            return {
                "task_id": task["id"],
                "code": code_blocks[0] if code_blocks else code_content,
                "explanation": self._extract_explanation(code_content),
                "status": TaskStatus.COMPLETED,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "task_id": task["id"],
                "code": "",
                "explanation": f"Code generation error: {str(e)}",
                "status": TaskStatus.FAILED,
                "timestamp": datetime.now().isoformat()
            }
    
    def _extract_code_blocks(self, text: str) -> list:
        """Extract code blocks from markdown"""
        pattern = r'```(?:python|javascript|typescript|java|go|rust)?\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)
        return matches
    
    def _extract_explanation(self, text: str) -> str:
        """Extract explanation text (non-code)"""
        # Remove code blocks
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        return text.strip()
```

**File: `agents/reviewer.py`**
```python
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from state import Task, TaskStatus
import os
from datetime import datetime

class ReviewerAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.3,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a quality assurance reviewer. Review work products for:
            1. Accuracy and correctness
            2. Completeness
            3. Quality and best practices
            4. Alignment with requirements
            
            Provide constructive feedback and approve or request revisions."""),
            ("human", """Original Task: {task_description}
            
            Work Product:
            {work_product}
            
            Context:
            {context}
            
            Review this work product and provide:
            1. Quality assessment (approve/needs_revision)
            2. Detailed feedback
            3. Specific improvement suggestions""")
        ])
    
    def review(self, task: Task, work_product: dict, context: dict = None) -> dict:
        """Review a work product"""
        context_str = str(context) if context else "No additional context"
        
        work_product_str = ""
        if "code" in work_product:
            work_product_str = f"Code:\n{work_product['code']}\n\nExplanation:\n{work_product.get('explanation', '')}"
        elif "findings" in work_product:
            work_product_str = f"Research Findings:\n{work_product['findings']}"
        
        chain = self.prompt | self.llm
        
        try:
            response = chain.invoke({
                "task_description": task["description"],
                "work_product": work_product_str,
                "context": context_str
            })
            
            review_text = response.content
            approved = "approve" in review_text.lower() or "approved" in review_text.lower()
            
            return {
                "task_id": task["id"],
                "approved": approved,
                "feedback": review_text,
                "status": TaskStatus.COMPLETED if approved else TaskStatus.NEEDS_REVIEW,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "task_id": task["id"],
                "approved": False,
                "feedback": f"Review error: {str(e)}",
                "status": TaskStatus.FAILED,
                "timestamp": datetime.now().isoformat()
            }
```

### Part 3: Advanced LangGraph with Checkpoints (40 minutes)

**File: `graph/multi_agent_graph.py`**
```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, AIMessage
from state import MultiAgentState, AgentRole, TaskStatus
from agents.planner import PlannerAgent
from agents.researcher import ResearcherAgent
from agents.coder import CoderAgent
from agents.reviewer import ReviewerAgent
from utils.routing import RoutingLogic
import json

class MultiAgentGraph:
    def __init__(self, enable_checkpoints: bool = True):
        # Initialize agents
        self.planner = PlannerAgent()
        self.researcher = ResearcherAgent()
        self.coder = CoderAgent()
        self.reviewer = ReviewerAgent()
        self.routing = RoutingLogic()
        
        # Build graph
        self.graph = self._build_graph(enable_checkpoints)
    
    def _build_graph(self, enable_checkpoints: bool):
        """Build the multi-agent graph"""
        workflow = StateGraph(MultiAgentState)
        
        # Add nodes
        workflow.add_node("planner", self.planning_node)
        workflow.add_node("researcher", self.research_node)
        workflow.add_node("coder", self.coding_node)
        workflow.add_node("reviewer", self.review_node)
        workflow.add_node("synthesizer", self.synthesize_node)
        
        # Set entry point
        workflow.set_entry_point("planner")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "planner",
            self.routing.after_planning,
            {
                "researcher": "researcher",
                "coder": "coder",
                "synthesizer": "synthesizer"
            }
        )
        
        workflow.add_conditional_edges(
            "researcher",
            self.routing.after_research,
            {
                "reviewer": "reviewer",
                "coder": "coder",
                "synthesizer": "synthesizer"
            }
        )
        
        workflow.add_conditional_edges(
            "coder",
            self.routing.after_coding,
            {
                "reviewer": "reviewer",
                "synthesizer": "synthesizer"
            }
        )
        
        workflow.add_conditional_edges(
            "reviewer",
            self.routing.after_review,
            {
                "researcher": "researcher",
                "coder": "coder",
                "synthesizer": "synthesizer",
                "end": END
            }
        )
        
        workflow.add_edge("synthesizer", END)
        
        # Compile with checkpoints
        if enable_checkpoints:
            memory = MemorySaver()
            return workflow.compile(checkpointer=memory)
        else:
            return workflow.compile()
    
    def planning_node(self, state: MultiAgentState) -> MultiAgentState:
        """Planning node"""
        print("\n[Planner] Creating execution plan...")
        
        query = state.get("original_query", "")
        if not query and state.get("messages"):
            for msg in reversed(state["messages"]):
                if isinstance(msg, HumanMessage):
                    query = msg.content
                    break
        
        state["original_query"] = query
        
        # Create plan
        plan_result = self.planner.create_plan(query)
        state["plan"] = plan_result
        state["tasks"] = plan_result["tasks"]
        
        state["messages"].append(AIMessage(
            content=f"Plan created with {len(plan_result['tasks'])} tasks:\n{plan_result['reasoning']}"
        ))
        
        state["agent_history"].append({
            "agent": "planner",
            "action": "created_plan",
            "timestamp": __import__("datetime").datetime.now().isoformat()
        })
        
        return state
    
    def research_node(self, state: MultiAgentState) -> MultiAgentState:
        """Research node"""
        print("\n[Researcher] Conducting research...")
        
        # Get next research task
        research_tasks = [t for t in state.get("tasks", []) 
                         if t["assigned_to"] == AgentRole.RESEARCHER 
                         and t["status"] == TaskStatus.PENDING]
        
        if not research_tasks:
            return state
        
        task = research_tasks[0]
        state["current_task_id"] = task["id"]
        
        # Get context from previous tasks
        context = self._build_context(state)
        
        # Perform research
        result = self.researcher.research(task, context)
        
        # Update state
        state["research_findings"].append(result)
        task["status"] = result["status"]
        task["result"] = result["findings"]
        task["completed_at"] = result["timestamp"]
        
        state["messages"].append(AIMessage(
            content=f"Research completed for: {task['description']}"
        ))
        
        return state
    
    def coding_node(self, state: MultiAgentState) -> MultiAgentState:
        """Coding node"""
        print("\n[Coder] Generating code...")
        
        # Get next coding task
        coding_tasks = [t for t in state.get("tasks", []) 
                       if t["assigned_to"] == AgentRole.CODER 
                       and t["status"] == TaskStatus.PENDING]
        
        if not coding_tasks:
            return state
        
        task = coding_tasks[0]
        state["current_task_id"] = task["id"]
        
        # Build context
        context = self._build_context(state)
        
        # Generate code
        result = self.coder.generate_code(task, context)
        
        # Update state
        state["code_artifacts"].append(result)
        task["status"] = result["status"]
        task["result"] = result["code"]
        task["completed_at"] = result["timestamp"]
        
        state["messages"].append(AIMessage(
            content=f"Code generated for: {task['description']}"
        ))
        
        return state
    
    def review_node(self, state: MultiAgentState) -> MultiAgentState:
        """Review node"""
        print("\n[Reviewer] Reviewing work...")
        
        current_task_id = state.get("current_task_id")
        if not current_task_id:
            return state
        
        # Find the task
        task = next((t for t in state["tasks"] if t["id"] == current_task_id), None)
        if not task:
            return state
        
        # Get work product
        work_product = {}
        if task["assigned_to"] == AgentRole.CODER:
            work_product = next((c for c in state["code_artifacts"] 
                               if c["task_id"] == current_task_id), {})
        elif task["assigned_to"] == AgentRole.RESEARCHER:
            work_product = next((r for r in state["research_findings"] 
                               if r["task_id"] == current_task_id), {})
        
        # Review
        context = self._build_context(state)
        review_result = self.reviewer.review(task, work_product, context)
        
        # Update state
        state["review_feedback"].append(review_result)
        
        if review_result["approved"]:
            task["status"] = TaskStatus.COMPLETED
        else:
            task["status"] = TaskStatus.NEEDS_REVIEW
            state["requires_human_input"] = True
        
        state["messages"].append(AIMessage(
            content=f"Review: {'Approved' if review_result['approved'] else 'Needs Revision'}\n{review_result['feedback']}"
        ))
        
        return state
    
    def synthesize_node(self, state: MultiAgentState) -> MultiAgentState:
        """Synthesize final output"""
        print("\n[Synthesizer] Creating final output...")
        
        from langchain_openai import ChatOpenAI
        from langchain.prompts import ChatPromptTemplate
        
        llm = ChatOpenAI(model="gpt-4", temperature=0.3)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Synthesize all work products into a comprehensive final answer."),
            ("human", """Original Query: {query}
            
            Research Findings: {research}
            Code Artifacts: {code}
            Review Feedback: {reviews}
            
            Create a comprehensive final answer that addresses the original query.""")
        ])
        
        research_str = "\n".join([r.get("findings", "") for r in state["research_findings"]])
        code_str = "\n".join([c.get("code", "") for c in state["code_artifacts"]])
        reviews_str = "\n".join([r.get("feedback", "") for r in state["review_feedback"]])
        
        chain = prompt | llm
        response = chain.invoke({
            "query": state["original_query"],
            "research": research_str,
            "code": code_str,
            "reviews": reviews_str
        })
        
        state["final_output"] = response.content
        state["messages"].append(AIMessage(content=state["final_output"]))
        
        return state
    
    def _build_context(self, state: MultiAgentState) -> dict:
        """Build context from state for agents"""
        return {
            "research": "\n".join([r.get("findings", "") for r in state.get("research_findings", [])]),
            "code": "\n".join([c.get("code", "") for c in state.get("code_artifacts", [])]),
            "tasks": [t["description"] for t in state.get("tasks", []) if t["status"] == TaskStatus.COMPLETED]
        }
    
    def run(self, query: str, config: dict = None) -> dict:
        """Execute the graph"""
        initial_state = {
            "messages": [HumanMessage(content=query)],
            "original_query": query,
            "plan": None,
            "tasks": [],
            "current_task_id": None,
            "research_findings": [],
            "code_artifacts": [],
            "review_feedback": [],
            "final_output": "",
            "iteration_count": 0,
            "agent_history": [],
            "errors": [],
            "requires_human_input": False,
            "human_feedback": None
        }
        
        if config is None:
            config = {"configurable": {"thread_id": "1"}}
        
        result = self.graph.invoke(initial_state, config)
        return result
```

**File: `utils/routing.py`**
```python
from state import MultiAgentState, AgentRole, TaskStatus

class RoutingLogic:
    """Routing logic for conditional edges"""
    
    def after_planning(self, state: MultiAgentState) -> str:
        """Route after planning"""
        tasks = state.get("tasks", [])
        
        # Check if there are research tasks
        research_tasks = [t for t in tasks if t["assigned_to"] == AgentRole.RESEARCHER]
        if research_tasks:
            return "researcher"
        
        # Check if there are coding tasks
        coding_tasks = [t for t in tasks if t["assigned_to"] == AgentRole.CODER]
        if coding_tasks:
            return "coder"
        
        # Otherwise synthesize
        return "synthesizer"
    
    def after_research(self, state: MultiAgentState) -> str:
        """Route after research"""
        # Always review research
        return "reviewer"
    
    def after_coding(self, state: MultiAgentState) -> str:
        """Route after coding"""
        # Always review code
        return "reviewer"
    
    def after_review(self, state: MultiAgentState) -> str:
        """Route after review"""
        current_task_id = state.get("current_task_id")
        if not current_task_id:
            return "synthesizer"
        
        # Find the task
        task = next((t for t in state["tasks"] if t["id"] == current_task_id), None)
        if not task:
            return "synthesizer"
        
        # Check if approved
        reviews = state.get("review_feedback", [])
        latest_review = next((r for r in reversed(reviews) if r["task_id"] == current_task_id), None)
        
        if latest_review and latest_review.get("approved"):
            # Check for more tasks
            pending_tasks = [t for t in state["tasks"] if t["status"] == TaskStatus.PENDING]
            
            if any(t["assigned_to"] == AgentRole.CODER for t in pending_tasks):
                return "coder"
            elif any(t["assigned_to"] == AgentRole.RESEARCHER for t in pending_tasks):
                return "researcher"
            else:
                return "synthesizer"
        else:
            # Needs revision - check which agent
            if task["assigned_to"] == AgentRole.CODER:
                return "coder"
            elif task["assigned_to"] == AgentRole.RESEARCHER:
                return "researcher"
            else:
                return "synthesizer"
```

### Part 4: Main Application with Human-in-the-Loop (20 minutes)

**File: `main.py`**
```python
from graph.multi_agent_graph import MultiAgentGraph
from dotenv import load_dotenv
import os

load_dotenv()

def main():
    print("=" * 70)
    print("Advanced Multi-Agent System")
    print("=" * 70)
    print("\nAgents:")
    print("1. Planner - Breaks down queries into tasks")
    print("2. Researcher - Gathers information")
    print("3. Coder - Generates code")
    print("4. Reviewer - Quality assurance")
    print("\n" + "=" * 70)
    
    graph = MultiAgentGraph(enable_checkpoints=True)
    
    while True:
        query = input("\nEnter your query (or 'exit' to quit): ").strip()
        
        if query.lower() in ['exit', 'quit']:
            break
        
        if not query:
            continue
        
        print(f"\nProcessing: {query}")
        print("-" * 70)
        
        try:
            config = {"configurable": {"thread_id": "main_thread"}}
            result = graph.run(query, config)
            
            print("\n" + "=" * 70)
            print("FINAL OUTPUT")
            print("=" * 70)
            print(result["final_output"])
            print("\n" + "=" * 70)
            
            # Show statistics
            print(f"\nStatistics:")
            print(f"- Tasks completed: {len([t for t in result['tasks'] if t['status'].value == 'completed'])}")
            print(f"- Research findings: {len(result['research_findings'])}")
            print(f"- Code artifacts: {len(result['code_artifacts'])}")
            print(f"- Reviews: {len(result['review_feedback'])}")
            print("=" * 70)
            
        except Exception as e:
            print(f"\nError: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
```

## Lab Exercises

### Exercise 1: Human-in-the-Loop (25 minutes)
Implement human feedback:
- Add interrupt points in the graph
- Allow human to approve/reject at review stage
- Resume execution after human input
- Store human feedback in state

### Exercise 2: Parallel Task Execution (20 minutes)
Execute independent tasks in parallel:
- Identify tasks with no dependencies
- Use async execution for parallel tasks
- Merge results back into state
- Handle race conditions

### Exercise 3: Advanced Error Recovery (15 minutes)
Implement sophisticated error handling:
- Retry failed tasks with exponential backoff
- Fallback strategies for each agent
- Error aggregation and reporting
- Graceful degradation

## Testing Scenarios

### Scenario 1: Research + Code Generation
**Query:** "Research FastAPI best practices and create a sample REST API"
**Expected Flow:** Plan → Research → Review → Code → Review → Synthesize

### Scenario 2: Complex Multi-Step Task
**Query:** "Create a data analysis pipeline: research pandas best practices, write code to load and analyze a CSV, and create visualizations"
**Expected:** Multiple research tasks → Multiple code tasks → Reviews → Synthesis

### Scenario 3: Quality Assurance Loop
**Query:** "Write a Python function to calculate Fibonacci numbers"
**Expected:** Code → Review (may request revision) → Revised Code → Review → Approve

## Deliverables

1. Complete implementation with all 4 agents
2. Graph with checkpoints and state management
3. Test suite covering all routing scenarios
4. Performance analysis:
   - Execution time per agent
   - Token usage breakdown
   - Success rates
5. Architecture documentation:
   - State flow diagram
   - Agent interaction patterns
   - Routing decision tree

## Advanced Challenges

### Challenge 1: Dynamic Agent Creation
- Create agents on-demand based on task requirements
- Implement agent specialization
- Add agent learning from past tasks

### Challenge 2: Distributed Execution
- Run agents on different processes/machines
- Implement message passing between distributed agents
- Handle network failures

### Challenge 3: Agent Optimization
- Implement agent performance tracking
- Auto-tune agent parameters
- Optimize routing decisions based on historical data

## Resources

- [LangGraph Advanced Patterns](https://python.langchain.com/docs/langgraph)
- [State Management](https://python.langchain.com/docs/langgraph/concepts/low_level#state)
- [Checkpoints](https://python.langchain.com/docs/langgraph/how_to/persistence)
- [Human-in-the-Loop](https://python.langchain.com/docs/langgraph/how_to/interrupt)

