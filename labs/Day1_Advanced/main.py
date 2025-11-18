from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationSummaryBufferMemory
from tools.document_qa import DocumentQATool
from tools.code_executor import CodeExecutor
from tools.web_search import AdvancedWebSearch
from tools.calculator import get_calculator_tool
from rag.vector_store import VectorStoreManager
from rag.document_loader import DocumentLoader
from config import Config
import os
from dotenv import load_dotenv

load_dotenv()

class AdvancedAgent:
    def __init__(self):
        # Initialize LLM
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize RAG components
        self.vector_store_manager = VectorStoreManager()
        self.document_loader = DocumentLoader()
        
        # Initialize tools
        self.tools = []
        self._setup_tools()
        
        # Initialize memory
        self.memory = ConversationSummaryBufferMemory(
            llm=self.llm,
            memory_key="chat_history",
            return_messages=True,
            max_token_limit=2000
        )
        
        # Initialize agent
        self.agent = self._create_agent()
    
    def _setup_tools(self):
        """Setup all available tools"""
        # Calculator
        self.tools.append(get_calculator_tool())
        
        # Web Search
        web_search = AdvancedWebSearch()
        self.tools.append(web_search.get_tool())
        
        # Code Executor
        code_executor = CodeExecutor()
        self.tools.append(code_executor.get_tool())
        
        # Document QA (will be added after documents are loaded)
        self.document_qa_tool = None
    
    def load_documents(self, file_path: str, file_type: str = "pdf"):
        """Load documents into vector store"""
        try:
            if file_type == "pdf":
                documents = self.document_loader.load_pdf(file_path)
            else:
                documents = self.document_loader.load_text(file_path)
            
            self.vector_store_manager.create_vector_store(documents)
            self.vector_store_manager.save_vector_store()
            
            # Add Document QA tool
            doc_qa = DocumentQATool(self.vector_store_manager)
            self.document_qa_tool = doc_qa.get_tool()
            
            # Recreate agent with new tool
            if self.document_qa_tool:
                self.tools.append(self.document_qa_tool)
                self.agent = self._create_agent()
            
            return f"Successfully loaded {len(documents)} document chunks."
        except Exception as e:
            return f"Error loading documents: {str(e)}"
    
    def _create_agent(self):
        """Create agent with tools and memory"""
        agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5,
            early_stopping_method="generate"
        )
        
        return agent
    
    def query(self, user_input: str):
        """Process user query"""
        try:
            response = self.agent.invoke({"input": user_input})
            return response['output']
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_conversation_summary(self):
        """Get summary of conversation"""
        return self.memory.predict_new_summary(
            self.memory.chat_memory.messages,
            ""
        )

# Main execution
if __name__ == "__main__":
    agent = AdvancedAgent()
    
    print("=" * 60)
    print("Advanced AgentAI with RAG Capabilities")
    print("=" * 60)
    print("\nAvailable capabilities:")
    print("- Document Q&A (load documents first)")
    print("- Web Search")
    print("- Python Code Execution")
    print("- Mathematical Calculations")
    print("- Conversational Memory")
    print("\nCommands:")
    print("- 'load <file_path>' - Load a document")
    print("- 'summary' - Get conversation summary")
    print("- 'exit' - Exit the agent")
    print("=" * 60)
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("\nAgentAI: Goodbye! Here's a summary of our conversation:")
            print(agent.get_conversation_summary())
            break
        
        if user_input.lower().startswith('load '):
            file_path = user_input[5:].strip()
            result = agent.load_documents(file_path)
            print(f"AgentAI: {result}")
            continue
        
        if user_input.lower() == 'summary':
            summary = agent.get_conversation_summary()
            print(f"\nConversation Summary:\n{summary}")
            continue
        
        response = agent.query(user_input)
        print(f"\nAgentAI: {response}")

