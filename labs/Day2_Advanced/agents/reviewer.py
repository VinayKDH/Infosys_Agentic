from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
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

