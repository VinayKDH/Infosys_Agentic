from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
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
        from langchain_core.prompts import ChatPromptTemplate
        
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

