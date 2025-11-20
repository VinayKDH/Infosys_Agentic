"""
Main application for Customer Support Email Agent
Based on LangGraph thinking patterns
"""
from graph import create_email_agent_graph
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os
import json

load_dotenv()

def main():
    print("=" * 70)
    print("Customer Support Email Agent")
    print("=" * 70)
    print("\nThis agent handles customer support emails by:")
    print("1. Reading and parsing emails")
    print("2. Classifying intent and urgency")
    print("3. Searching documentation for answers")
    print("4. Creating bug tickets when needed")
    print("5. Drafting appropriate responses")
    print("6. Escalating to human review when necessary")
    print("7. Sending final responses")
    print("\n" + "=" * 70)
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\nERROR: OPENAI_API_KEY not found in environment variables!")
        print("Please set your OpenAI API key in a .env file or environment variable.")
        return
    
    # Create the graph
    print("\nInitializing email agent graph...")
    graph = create_email_agent_graph(enable_checkpoints=True)
    print("Graph initialized successfully!")
    
    # Example emails to test
    example_emails = [
        {
            "email_id": "email_001",
            "sender_email": "customer@example.com",
            "email_content": "How do I reset my password? I can't remember it."
        },
        {
            "email_id": "email_002",
            "sender_email": "user@example.com",
            "email_content": "The export feature crashes when I select PDF format. This is very frustrating!"
        },
        {
            "email_id": "email_003",
            "sender_email": "billing@company.com",
            "email_content": "I was charged twice for my subscription! This is urgent! Please fix this immediately."
        },
        {
            "email_id": "email_004",
            "sender_email": "developer@startup.com",
            "email_content": "Can you add dark mode to the mobile app? It would be really helpful."
        },
        {
            "email_id": "email_005",
            "sender_email": "tech@enterprise.com",
            "email_content": "Our API integration fails intermittently with 504 errors. We've tried everything but can't figure out the root cause. This is affecting our production system."
        }
    ]
    
    while True:
        print("\n" + "=" * 70)
        print("Options:")
        print("1. Process example emails")
        print("2. Enter custom email")
        print("3. Exit")
        print("=" * 70)
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            print("\nExample emails:")
            for i, email in enumerate(example_emails, 1):
                print(f"{i}. {email['email_content'][:60]}...")
            
            email_choice = input("\nSelect email number (1-5): ").strip()
            try:
                email_idx = int(email_choice) - 1
                if 0 <= email_idx < len(example_emails):
                    email = example_emails[email_idx]
                    process_email(graph, email)
                else:
                    print("Invalid email number!")
            except ValueError:
                print("Invalid input!")
        
        elif choice == "2":
            print("\nEnter email details:")
            email_id = input("Email ID: ").strip() or "custom_email_001"
            sender_email = input("Sender email: ").strip() or "customer@example.com"
            print("Email content (press Enter twice when done):")
            lines = []
            while True:
                line = input()
                if line == "" and lines and lines[-1] == "":
                    break
                lines.append(line)
            email_content = "\n".join(lines).strip()
            
            if email_content:
                email = {
                    "email_id": email_id,
                    "sender_email": sender_email,
                    "email_content": email_content
                }
                process_email(graph, email)
            else:
                print("No email content provided!")
        
        elif choice == "3":
            print("\nGoodbye!")
            break
        
        else:
            print("Invalid choice!")


def process_email(graph, email_data):
    """Process a single email through the agent"""
    print("\n" + "=" * 70)
    print("PROCESSING EMAIL")
    print("=" * 70)
    print(f"Email ID: {email_data['email_id']}")
    print(f"From: {email_data['sender_email']}")
    print(f"Content: {email_data['email_content'][:100]}...")
    print("=" * 70)
    
    # Create initial state
    initial_state = {
        "email_content": email_data["email_content"],
        "sender_email": email_data["sender_email"],
        "email_id": email_data["email_id"],
        "classification": None,
        "search_results": None,
        "customer_history": None,
        "bug_ticket_id": None,
        "draft_response": None,
        "final_response": None,
        "messages": [],
        "requires_human_review": False,
        "human_approved": None,
        "human_edited_response": None,
        "errors": []
    }
    
    # Run the graph
    try:
        config = {"configurable": {"thread_id": email_data["email_id"]}}
        result = graph.invoke(initial_state, config)
        
        # Display results
        print("\n" + "=" * 70)
        print("RESULTS")
        print("=" * 70)
        
        if result.get("classification"):
            classification = result["classification"]
            print(f"\nClassification:")
            print(f"  Intent: {classification['intent']}")
            print(f"  Urgency: {classification['urgency']}")
            print(f"  Topic: {classification['topic']}")
            print(f"  Summary: {classification['summary']}")
        
        if result.get("bug_ticket_id"):
            print(f"\nBug Ticket: {result['bug_ticket_id']}")
        
        if result.get("search_results"):
            print(f"\nDocumentation Results: {len(result['search_results'])} found")
            for i, result_text in enumerate(result['search_results'][:2], 1):
                print(f"  {i}. {result_text[:100]}...")
        
        if result.get("final_response"):
            print(f"\nFinal Response:")
            print("-" * 70)
            print(result["final_response"])
            print("-" * 70)
        
        if result.get("errors"):
            print(f"\nErrors: {len(result['errors'])}")
            for error in result["errors"]:
                print(f"  - {error}")
        
        print("\n" + "=" * 70)
        
    except Exception as e:
        print(f"\nError processing email: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

