"""
Day 1 Advanced Lab - Multi-Tool Agent with RAG Integration
Optimized for Python 3.11
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Check for required packages and provide helpful error messages
try:
    from langchain_openai import ChatOpenAI
except ImportError:
    print("ERROR: langchain-openai not installed!")
    print("Please run: pip install -r requirements.txt")
    sys.exit(1)

try:
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
except ImportError:
    print("ERROR: langchain-core not installed!")
    print("Please run: pip install -r requirements.txt")
    sys.exit(1)

# Import local modules
from tools.document_qa import DocumentQATool
from tools.code_executor import CodeExecutor
from tools.web_search import AdvancedWebSearch
from tools.calculator import get_calculator_tool
from rag.vector_store import VectorStoreManager
from rag.document_loader import DocumentLoader
from config import Config

# Try to import agent components with fallbacks
try:
    from langchain.agents import AgentExecutor, create_openai_tools_agent
    AGENT_TYPE = "openai_tools"
    AGENT_AVAILABLE = True
except ImportError:
    try:
        from langchain.agents import AgentExecutor, create_react_agent
        AGENT_TYPE = "react"
        AGENT_AVAILABLE = True
    except ImportError:
        AGENT_TYPE = "simple"
        AGENT_AVAILABLE = False
        print("Warning: AgentExecutor not available. Using simplified mode.")

# Try to import memory with fallbacks
try:
    from langchain.memory import ConversationSummaryBufferMemory
    MEMORY_AVAILABLE = True
except ImportError:
    MEMORY_AVAILABLE = False
    # Simple memory fallback
    class ConversationSummaryBufferMemory:
        def __init__(self, **kwargs):
            self.chat_memory = type('obj', (object,), {'messages': []})()
            self.llm = kwargs.get('llm')
            self.messages = []
        
        def save_context(self, inputs, outputs):
            if isinstance(inputs, dict) and 'input' in inputs:
                self.messages.append(('user', inputs['input']))
            if isinstance(outputs, dict) and 'output' in outputs:
                self.messages.append(('assistant', outputs['output']))
        
        def load_memory_variables(self, inputs):
            return {"chat_history": self.messages}
        
        def predict_new_summary(self, messages, existing_summary):
            return "Conversation summary not available in simplified mode."

load_dotenv()

class AdvancedAgent:
    def __init__(self):
        # Check for API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in .env file. Please add it.")
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            api_key=api_key
        )
        
        # Initialize RAG components
        self.vector_store_manager = VectorStoreManager()
        self.document_loader = DocumentLoader()
        
        # Initialize tools
        self.tools = []
        self._setup_tools()
        
        # Initialize memory
        try:
            if MEMORY_AVAILABLE:
                self.memory = ConversationSummaryBufferMemory(
                    llm=self.llm,
                    memory_key="chat_history",
                    return_messages=True,
                    max_token_limit=2000
                )
            else:
                self.memory = ConversationSummaryBufferMemory(llm=self.llm)
        except Exception as e:
            print(f"Warning: Memory initialization failed: {e}")
            self.memory = ConversationSummaryBufferMemory(llm=self.llm)
        
        # Initialize agent
        self.agent = self._create_agent()
    
    def _setup_tools(self):
        """Setup all available tools"""
        try:
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
        except Exception as e:
            print(f"Warning: Some tools failed to initialize: {e}")
    
    def load_documents(self, file_path: str, file_type: str = "pdf"):
        """Load documents into vector store"""
        try:
            if not os.path.exists(file_path):
                return f"Error: File not found: {file_path}"
            
            if file_type == "pdf":
                documents = self.document_loader.load_pdf(file_path)
            else:
                documents = self.document_loader.load_text(file_path)
            
            if not documents:
                return "Error: No documents loaded from file."
            
            self.vector_store_manager.create_vector_store(documents)
            self.vector_store_manager.save_vector_store()
            
            # Add Document QA tool
            doc_qa = DocumentQATool(self.vector_store_manager)
            self.document_qa_tool = doc_qa.get_tool()
            
            # Recreate agent with new tool
            if self.document_qa_tool:
                # Remove old DocumentQA tool if exists
                self.tools = [t for t in self.tools if t.name != "DocumentQA"]
                self.tools.append(self.document_qa_tool)
                self.agent = self._create_agent()
            
            return f"Successfully loaded {len(documents)} document chunks."
        except Exception as e:
            return f"Error loading documents: {str(e)}"
    
    def _create_agent(self):
        """Create agent with tools and memory"""
        if not AGENT_AVAILABLE or not self.tools:
            # Fallback: simple LLM chain
            from langchain.chains import LLMChain
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a helpful AI assistant. You can help with questions, 
                but note that advanced tool features are not available in this mode."""),
                ("human", "{input}"),
            ])
            chain = LLMChain(llm=self.llm, prompt=prompt, verbose=True)
            
            class SimpleAgentWrapper:
                def __init__(self, chain):
                    self.chain = chain
                
                def invoke(self, input_dict):
                    result = self.chain.invoke(input_dict)
                    return {"output": result.get("text", str(result))}
            
            return SimpleAgentWrapper(chain)
        
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
        try:
            if AGENT_TYPE == "openai_tools":
                agent = create_openai_tools_agent(self.llm, self.tools, prompt)
            elif AGENT_TYPE == "react":
                agent = create_react_agent(self.llm, self.tools, prompt)
            else:
                raise ImportError("No agent type available")
            
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
            except Exception:
                # Fallback without memory
                agent_executor = AgentExecutor(
                    agent=agent,
                    tools=self.tools,
                    verbose=True,
                    handle_parsing_errors=True,
                    max_iterations=5
                )
            
            return agent_executor
        except Exception as e:
            print(f"Warning: Agent creation failed: {e}. Using simplified mode.")
            # Fallback to simple chain
            from langchain.chains import LLMChain
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a helpful AI assistant."),
                ("human", "{input}"),
            ])
            chain = LLMChain(llm=self.llm, prompt=prompt, verbose=True)
            
            class SimpleAgentWrapper:
                def __init__(self, chain):
                    self.chain = chain
                
                def invoke(self, input_dict):
                    result = self.chain.invoke(input_dict)
                    return {"output": result.get("text", str(result))}
            
            return SimpleAgentWrapper(chain)
    
    def query(self, user_input: str):
        """Process user query"""
        try:
            response = self.agent.invoke({"input": user_input})
            if isinstance(response, dict):
                return response.get('output', str(response))
            return str(response)
        except Exception as e:
            return f"Error processing query: {str(e)}"
    
    def get_conversation_summary(self):
        """Get summary of conversation"""
        try:
            if hasattr(self.memory, 'predict_new_summary'):
                return self.memory.predict_new_summary(
                    self.memory.chat_memory.messages if hasattr(self.memory.chat_memory, 'messages') else [],
                    ""
                )
            return "Conversation summary not available."
        except Exception as e:
            return f"Summary error: {str(e)}"

# Main execution
if __name__ == "__main__":
    try:
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
            
            if not user_input:
                continue
            
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
    
    except ValueError as e:
        print(f"\nERROR: {e}")
        print("\nPlease create a .env file with your OPENAI_API_KEY")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
