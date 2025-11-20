"""Customer support agent"""
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from state.amex_state import AmexState
from app.config import settings
from tools.transaction_analyzer import analyze_transaction, get_transaction_history
from tools.account_calculator import calculate_rewards, calculate_interest, calculate_minimum_payment
from tools.document_qa import query_banking_documents


class SupportAgent:
    """Handles customer support inquiries"""
    
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set in environment variables")
        
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.7,
            api_key=settings.OPENAI_API_KEY
        )
        
        # Define tools
        self.tools = [
            analyze_transaction,
            get_transaction_history,
            calculate_rewards,
            calculate_interest,
            calculate_minimum_payment,
            query_banking_documents
        ]
        
        # Create agent
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a helpful customer support agent for American Express.
                You help customers with:
                - Account inquiries
                - Transaction questions
                - Rewards and benefits
                - Billing questions
                - General account information
                
                Always be professional, empathetic, and accurate. Use tools to get real information.
                If you don't know something, say so and offer to connect them with a specialist."""),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad")
            ])
            
            agent = create_openai_tools_agent(self.llm, self.tools, prompt)
            self.agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True)
        except Exception as e:
            # Fallback if agent creation fails
            print(f"Warning: Could not create agent executor: {e}")
            self.agent_executor = None
    
    def process(self, state: AmexState) -> AmexState:
        """Process support request"""
        query = state.get("original_query", "")
        customer_id = state.get("customer_id", "")
        
        try:
            if self.agent_executor is None:
                # Fallback response if agent not initialized
                response = self.llm.invoke(f"Customer asked: {query}. Provide a helpful response as a customer support agent.")
                response_text = response.content if hasattr(response, 'content') else str(response)
            else:
                # Get chat history
                messages = state.get("messages", [])
                chat_history = [msg for msg in messages if isinstance(msg, (HumanMessage, AIMessage))]
                
                # Execute agent
                result = self.agent_executor.invoke({
                    "input": query,
                    "chat_history": chat_history
                })
                
                response_text = result.get("output", "I apologize, but I couldn't process your request.")
            
            state["support_result"] = response_text
            state["messages"] = state.get("messages", []) + [
                AIMessage(content=f"Support Agent: {response_text}")
            ]
        
        except Exception as e:
            error_msg = f"Support agent error: {str(e)}"
            state["errors"] = state.get("errors", []) + [error_msg]
            state["support_result"] = "I encountered an error. Please try again or contact support."
        
        return state

