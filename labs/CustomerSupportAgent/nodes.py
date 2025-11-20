"""
Node implementations for Customer Support Email Agent
Based on LangGraph thinking patterns
"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.tools import DuckDuckGoSearchRun
from typing import Literal
from pydantic import BaseModel, Field
import os
import re
import json
from datetime import datetime
from state import EmailAgentState

# Initialize LLM (lazy initialization)
llm = None

def get_llm():
    """Get or create LLM instance"""
    global llm
    if llm is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.3,
            api_key=api_key
        )
    return llm

# Initialize tools (lazy initialization)
search_tool = None

def get_search_tool():
    """Get or create search tool instance"""
    global search_tool
    if search_tool is None:
        search_tool = DuckDuckGoSearchRun()
    return search_tool

# Pydantic model for classification output
class EmailClassification(BaseModel):
    intent: Literal["question", "bug", "billing", "feature", "complex"] = Field(description="Email intent")
    urgency: Literal["low", "medium", "high", "critical"] = Field(description="Urgency level")
    topic: str = Field(description="Main topic of the email")
    summary: str = Field(description="Brief summary of the email")

# Simple in-memory knowledge base (in production, use a real vector store)
knowledge_base = {
    "password reset": "To reset your password, go to Settings > Security > Reset Password. You'll receive an email with reset instructions.",
    "export feature": "The export feature supports PDF, CSV, and Excel formats. Click the Export button in the top menu.",
    "billing": "You can view your billing information in Settings > Billing. For billing issues, contact support@example.com.",
    "api": "Our API documentation is available at api.example.com/docs. API keys can be generated in Settings > API.",
}

def read_email(state: EmailAgentState) -> EmailAgentState:
    """Read and parse incoming email"""
    print("\n[Read Email] Processing email...")
    
    # In a real system, this would parse email from IMAP/API
    # For demo, we assume email_content is already set
    email_content = state.get("email_content", "")
    sender_email = state.get("sender_email", "")
    email_id = state.get("email_id", "")
    
    if not email_content:
        state["errors"].append("No email content provided")
        return state
    
    # Extract key information
    print(f"[Read Email] Email from: {sender_email}")
    print(f"[Read Email] Email ID: {email_id}")
    print(f"[Read Email] Content preview: {email_content[:100]}...")
    
    # Add to messages
    state["messages"].append(HumanMessage(content=f"Email from {sender_email}: {email_content}"))
    
    return state


def classify_intent(state: EmailAgentState) -> EmailAgentState:
    """Classify email intent and store classification in state"""
    print("\n[Classify Intent] Analyzing email...")
    
    email_content = state.get("email_content", "")
    sender_email = state.get("sender_email", "")
    
    # Create classification prompt
    parser = JsonOutputParser(pydantic_object=EmailClassification)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an email classification system for customer support.
        
        Classify emails into one of these intents:
        - "question": Simple product questions that can be answered with documentation
        - "bug": Reports of software bugs or errors
        - "billing": Billing, payment, or subscription issues
        - "feature": Feature requests or suggestions
        - "complex": Complex technical issues requiring human expertise
        
        Urgency levels:
        - "low": General inquiries, feature requests
        - "medium": Standard support questions
        - "high": Issues affecting user experience
        - "critical": Urgent issues like billing errors, security concerns
        
        {format_instructions}"""),
        ("human", """Classify this email:
        
        From: {sender_email}
        Content: {email_content}
        
        Provide classification with intent, urgency, topic, and summary.""")
    ]).partial(format_instructions=parser.get_format_instructions())
    
    try:
        chain = prompt | get_llm() | parser
        classification_result = chain.invoke({
            "sender_email": sender_email,
            "email_content": email_content
        })
        
        # Convert Pydantic model to dict for state storage
        if hasattr(classification_result, 'dict'):
            classification = classification_result.dict()
        elif hasattr(classification_result, 'model_dump'):
            classification = classification_result.model_dump()
        else:
            classification = classification_result
        
        state["classification"] = classification
        
        print(f"[Classify Intent] Intent: {classification['intent']}")
        print(f"[Classify Intent] Urgency: {classification['urgency']}")
        print(f"[Classify Intent] Topic: {classification['topic']}")
        
        # Add classification to messages
        intent = classification["intent"]
        urgency = classification["urgency"]
        state["messages"].append(AIMessage(
            content=f"Classification: {intent} ({urgency} urgency) - {classification['summary']}"
        ))
            
    except Exception as e:
        error_msg = f"Classification error: {str(e)}"
        print(f"[Classify Intent] Error: {error_msg}")
        state["errors"].append(error_msg)
        # Set default classification on error
        state["classification"] = {
            "intent": "complex",
            "urgency": "high",
            "topic": "error",
            "summary": error_msg
        }
    
    return state


def route_after_classify(state: EmailAgentState) -> str:
    """Route after classification based on intent and urgency"""
    classification = state.get("classification")
    if not classification:
        return "human_review"  # Default to human review if no classification
    
    intent = classification.get("intent", "")
    urgency = classification.get("urgency", "medium")
    
    # Routing logic
    if intent == "bug":
        return "bug_tracking"
    elif urgency == "critical" or intent == "complex":
        return "human_review"
    elif intent == "question":
        return "doc_search"
    else:
        # For billing, feature requests, etc., go to draft response
        return "draft_response"


def doc_search(state: EmailAgentState) -> EmailAgentState:
    """Search documentation/knowledge base for answers"""
    print("\n[Doc Search] Searching knowledge base...")
    
    classification = state.get("classification")
    if not classification:
        state["errors"].append("No classification available for search")
        return state
    
    topic = classification.get("topic", "")
    email_content = state.get("email_content", "")
    
    # Simple keyword-based search (in production, use vector search)
    search_query = f"{topic} {email_content}".lower()
    
    results = []
    for key, value in knowledge_base.items():
        if key.lower() in search_query:
            results.append(value)
    
    # If no results, try web search as fallback
    if not results:
        print("[Doc Search] No KB results, trying web search...")
        try:
            web_result = get_search_tool().run(f"{topic} {classification.get('summary', '')}")
            results.append(web_result[:500])  # Limit length
        except Exception as e:
            print(f"[Doc Search] Web search error: {str(e)}")
    
    state["search_results"] = results
    
    if results:
        print(f"[Doc Search] Found {len(results)} relevant results")
        state["messages"].append(AIMessage(content=f"Found {len(results)} relevant documentation results"))
    else:
        print("[Doc Search] No results found")
        state["messages"].append(AIMessage(content="No relevant documentation found"))
    
    return state


def bug_tracking(state: EmailAgentState) -> EmailAgentState:
    """Create or update bug ticket in tracking system"""
    print("\n[Bug Tracking] Creating bug ticket...")
    
    classification = state.get("classification")
    email_content = state.get("email_content", "")
    sender_email = state.get("sender_email", "")
    
    if not classification:
        state["errors"].append("No classification available for bug tracking")
        return state
    
    # In a real system, this would create a ticket in Jira, GitHub, etc.
    # For demo, we generate a ticket ID
    ticket_id = f"BUG-{datetime.now().strftime('%Y%m%d')}-{hash(email_content) % 10000:04d}"
    
    bug_info = {
        "ticket_id": ticket_id,
        "reporter": sender_email,
        "description": email_content,
        "topic": classification.get("topic", ""),
        "urgency": classification.get("urgency", "medium"),
        "created_at": datetime.now().isoformat()
    }
    
    state["bug_ticket_id"] = ticket_id
    
    print(f"[Bug Tracking] Created ticket: {ticket_id}")
    state["messages"].append(AIMessage(content=f"Bug ticket created: {ticket_id}"))
    
    # Save bug info (in production, this would be saved to a database)
    print(f"[Bug Tracking] Bug details: {json.dumps(bug_info, indent=2)}")
    
    return state


def draft_response(state: EmailAgentState) -> EmailAgentState:
    """Draft an appropriate email response"""
    print("\n[Draft Response] Generating response...")
    
    email_content = state.get("email_content", "")
    classification = state.get("classification")
    search_results = state.get("search_results", [])
    bug_ticket_id = state.get("bug_ticket_id")
    customer_history = state.get("customer_history", {})
    
    if not classification:
        state["errors"].append("No classification available for drafting response")
        return state
    
    # Build context for response generation
    context_parts = []
    
    if search_results:
        context_parts.append(f"Documentation:\n{chr(10).join(search_results)}")
    
    if bug_ticket_id:
        context_parts.append(f"Bug ticket created: {bug_ticket_id}. Please reference this ticket for updates.")
    
    if customer_history:
        context_parts.append(f"Customer history: {json.dumps(customer_history, indent=2)}")
    
    context = "\n\n".join(context_parts) if context_parts else "No additional context available."
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a professional customer support agent. Draft a helpful, empathetic email response.
        
        Guidelines:
        - Be professional and friendly
        - Address the customer's concern directly
        - Use information from documentation when available
        - Include bug ticket numbers if applicable
        - Keep responses concise but complete
        - If you don't have enough information, acknowledge it and offer next steps
        - Match the urgency level in your tone"""),
        ("human", """Original Email:
{email_content}

Classification:
- Intent: {intent}
- Urgency: {urgency}
- Topic: {topic}
- Summary: {summary}

Context:
{context}

Draft a professional email response to the customer.""")
    ])
    
    try:
        chain = prompt | get_llm()
        response = chain.invoke({
            "email_content": email_content,
            "intent": classification["intent"],
            "urgency": classification["urgency"],
            "topic": classification["topic"],
            "summary": classification["summary"],
            "context": context
        })
        
        draft = response.content if hasattr(response, 'content') else str(response)
        state["draft_response"] = draft
        
        print(f"[Draft Response] Draft generated ({len(draft)} characters)")
        state["messages"].append(AIMessage(content=f"Draft response generated"))
        
    except Exception as e:
        error_msg = f"Response drafting error: {str(e)}"
        print(f"[Draft Response] Error: {error_msg}")
        state["errors"].append(error_msg)
        state["draft_response"] = "We apologize, but we encountered an error generating your response. Our team will review your email shortly."
    
    return state


def human_review(state: EmailAgentState) -> EmailAgentState:
    """Human review node - can interrupt for human input"""
    print("\n[Human Review] Checking if human review is needed...")
    
    classification = state.get("classification")
    draft_response = state.get("draft_response")
    
    if not classification:
        state["errors"].append("No classification available for human review")
        return state
    
    urgency = classification.get("urgency", "medium")
    intent = classification.get("intent", "")
    
    # Determine if human review is required
    requires_review = (
        urgency == "critical" or
        intent == "complex" or
        intent == "billing" or
        not draft_response  # No draft means we need human help
    )
    
    state["requires_human_review"] = requires_review
    
    if requires_review:
        print("[Human Review] Human review required - pausing for input")
        # In a real system, this would use interrupt() to pause
        # For demo, we'll simulate approval
        print("[Human Review] (Simulated) Human approved the response")
        state["human_approved"] = True
        state["human_edited_response"] = draft_response  # Use draft as-is for demo
    else:
        print("[Human Review] No human review needed - auto-approved")
        state["human_approved"] = True
    
    return state


def send_reply(state: EmailAgentState) -> EmailAgentState:
    """Send the final email response"""
    print("\n[Send Reply] Sending email response...")
    
    # Determine which response to send
    if state.get("human_edited_response"):
        final_response = state["human_edited_response"]
    elif state.get("draft_response"):
        final_response = state["draft_response"]
    else:
        final_response = "Thank you for contacting us. We have received your email and will respond shortly."
    
    state["final_response"] = final_response
    
    # In a real system, this would send via SMTP/API
    sender_email = state.get("sender_email", "")
    email_id = state.get("email_id", "")
    
    print(f"[Send Reply] Sending to: {sender_email}")
    print(f"[Send Reply] Response preview: {final_response[:100]}...")
    print(f"[Send Reply] Email sent successfully!")
    
    state["messages"].append(AIMessage(content=f"Response sent to {sender_email}"))
    
    return state

