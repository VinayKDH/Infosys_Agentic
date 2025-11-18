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

