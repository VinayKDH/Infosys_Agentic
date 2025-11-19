from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from tools.document_qa import DocumentQATool
from tools.code_executor import CodeExecutor
from tools.web_search import AdvancedWebSearch
from tools.calculator import get_calculator_tool
from rag.vector_store import VectorStoreManager
from rag.document_loader import DocumentLoader
from config import Config
import os
from dotenv import load_dotenv

# Try to import agent components with fallbacks
try:
    from langchain.agents import AgentExecutor, create_openai_tools_agent
    AGENT_TYPE = "openai_tools"
except ImportError:
    try:
        from langchain.agents import AgentExecutor, create_react_agent
        AGENT_TYPE = "react"
    except ImportError:
        AGENT_TYPE = "simple"

# Try to import memory with fallbacks
try:
    from langchain.memory import ConversationSummaryBufferMemory
except ImportError:
    # Simple memory fallback
    class ConversationSummaryBufferMemory:
        def __init__(self, **kwargs):
            self.chat_memory = type('obj', (object,), {'messages': []})()
            self.llm = kwargs.get('llm')
        
        def save_context(self, inputs, outputs):
            pass
        
        def load_memory_variables(self, inputs):
            return {"chat_history": []}
        
        def predict_new_summary(self, messages, existing_summary):
            return "Conversation summary not available."

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
        try:
            self.memory = ConversationSummaryBufferMemory(
                llm=self.llm,
                memory_key="chat_history",
                return_messages=True,
                max_token_limit=2000
            )
        except:
            self.memory = ConversationSummaryBufferMemory(llm=self.llm)
        
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
        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful AI assistant with access to multiple tools.
            You can answer questions, search the web, execute code, query documents, and perform calculations.
            Use the appropriate tool for each task."""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create the agent based on available type
        if AGENT_TYPE == "openai_tools":
            agent = create_openai_tools_agent(self.llm, self.tools, prompt)
        elif AGENT_TYPE == "react":
            agent = create_react_agent(self.llm, self.tools, prompt)
        else:
            # Fallback: simple chain
            from langchain.chains import LLMChain
            return LLMChain(llm=self.llm, prompt=prompt, memory=self.memory, verbose=True)
        
        # Create agent executor with memory
        try:
            agent_executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                memory=self.memory,
                verbose=True,
                handle_parsing_errors=True,
                max_iterations=5
            )
        except:
            # Fallback without memory
            agent_executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                verbose=True,
                handle_parsing_errors=True,
                max_iterations=5
            )
        
        return agent_executor
    
    def query(self, user_input: str):
        """Process user query"""
        try:
            response = self.agent.invoke({"input": user_input})
            return response['output'] if isinstance(response, dict) else str(response)
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_conversation_summary(self):
        """Get summary of conversation"""
        try:
            return self.memory.predict_new_summary(
                self.memory.chat_memory.messages,
                ""
            )
        except:
            return "Conversation summary not available."

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
