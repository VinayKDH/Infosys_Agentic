from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
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

