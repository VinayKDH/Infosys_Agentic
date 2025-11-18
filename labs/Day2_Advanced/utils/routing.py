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

