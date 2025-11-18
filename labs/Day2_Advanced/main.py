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

