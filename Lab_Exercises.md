# Lab Exercises - Day 1 & Day 2

This document contains all exercises from Day 1 and Day 2 labs for easy reference.

---

## Day 1 Medium Lab Exercises

### Exercise 1: Add a New Tool (15 minutes)
**Objective:** Understand tool structure and integration

**Task:**
Create a custom tool that:
- Takes a city name as input
- Returns a formatted string with timezone information
- Integrate it into your agent

**Learning Outcomes:**
- Tool definition and structure
- Tool integration with agent
- Importance of tool descriptions

**Steps:**
1. Create a function that takes a city name
2. Return timezone information (can use a simple dictionary or API)
3. Wrap it in a `Tool` object with name and description
4. Add to the tools list
5. Test with the agent

---

### Exercise 2: Error Handling (10 minutes)
**Objective:** Implement robust error handling

**Task:**
Enhance error handling:
- Add try-catch blocks for tool failures
- Provide user-friendly error messages
- Implement retry logic for failed tool calls

**Learning Outcomes:**
- Error handling patterns
- User experience considerations
- Retry mechanisms

**Steps:**
1. Wrap tool calls in try-except blocks
2. Create meaningful error messages
3. Implement retry logic with exponential backoff
4. Test with invalid inputs

---

### Exercise 3: Conversation Analysis (15 minutes)
**Objective:** Add observability and tracking

**Task:**
Add functionality to:
- Count the number of tool calls made in a conversation
- Track which tools are used most frequently
- Display a summary at the end of the conversation

**Learning Outcomes:**
- State tracking
- Analytics and observability
- Conversation metadata

**Steps:**
1. Create a tracking dictionary for tool usage
2. Increment counters when tools are called
3. Display summary at conversation end
4. Track tool names and call counts

---

## Day 1 Advanced Lab Exercises

### Exercise 1: Multi-Document RAG (20 minutes)
**Objective:** Extend RAG to handle multiple documents

**Task:**
- Load multiple PDF documents
- Implement document source tracking
- Create a tool that can search across all documents
- Add document filtering by metadata

**Learning Outcomes:**
- Multi-document vector stores
- Source attribution
- Metadata filtering
- Document management

**Steps:**
1. Modify `DocumentLoader` to handle multiple files
2. Add metadata to document chunks (source, page number)
3. Update vector store to include metadata
4. Modify DocumentQA tool to filter by metadata
5. Test with multiple documents

---

### Exercise 2: Tool Chaining (15 minutes)
**Objective:** Understand tool composition

**Task:**
- Create a tool that chains multiple tools together
- Example: "Analyze data from web search using Python"
- Implement error handling for tool chains

**Learning Outcomes:**
- Tool composition patterns
- Sequential tool execution
- Error propagation in chains

**Steps:**
1. Create a new tool that uses web search
2. Pass search results to code executor
3. Handle errors at each step
4. Return combined results

---

### Exercise 3: Advanced Memory (15 minutes)
**Objective:** Implement sophisticated memory management

**Task:**
- Implement entity memory to track specific entities
- Add conversation summarization at intervals
- Create a memory export/import feature

**Learning Outcomes:**
- Entity extraction and tracking
- Memory summarization
- Memory persistence

**Steps:**
1. Use LangChain's EntityMemory
2. Extract entities from conversations
3. Summarize conversations periodically
4. Save/load memory to/from file

---

### Exercise 4: Observability (15 minutes)
**Objective:** Add monitoring and tracing

**Task:**
- Set up LangSmith tracing
- Add custom metrics tracking
- Create a dashboard for agent performance

**Learning Outcomes:**
- LangSmith integration
- Performance monitoring
- Metrics collection

**Steps:**
1. Set up LangSmith API key
2. Enable tracing in agent
3. Add custom metrics (response time, token usage)
4. View traces in LangSmith dashboard

---

## Day 2 Medium Lab Exercises

### Exercise 1: Add Quality Check Node (20 minutes)
**Objective:** Implement conditional routing and quality gates

**Task:**
Create a quality checker agent that:
- Reviews the research results
- Determines if more research is needed
- Routes back to researcher if quality is insufficient
- Uses conditional edges in LangGraph

**Hint:** Use `workflow.add_conditional_edges()` for routing logic.

**Learning Outcomes:**
- Conditional routing in LangGraph
- Quality assessment logic
- Feedback loops in graphs

**Steps:**
1. Create a `quality_check` node function
2. Implement quality assessment logic
3. Create routing function `should_continue_research`
4. Add conditional edge from researcher to quality_check
5. Route back to researcher or to summarizer

**Code Pattern:**
```python
def quality_check_node(state: ResearchState) -> ResearchState:
    # Assess research quality
    # Update state with quality score
    return state

def should_continue_research(state: ResearchState) -> str:
    quality = state.get("quality_score", 0)
    if quality < threshold:
        return "researcher"  # Need more research
    else:
        return "summarizer"  # Quality sufficient
```

---

### Exercise 2: Add Error Handling (15 minutes)
**Objective:** Implement comprehensive error handling

**Task:**
Enhance the graph with:
- Try-catch blocks in each node
- Error state handling
- Retry logic for failed operations
- User-friendly error messages

**Learning Outcomes:**
- Error handling in graph nodes
- State-based error tracking
- Retry mechanisms
- User experience

**Steps:**
1. Wrap each node function in try-except
2. Add errors to state["errors"] list
3. Implement retry logic with max attempts
4. Provide clear error messages to users

---

### Exercise 3: Add LangSmith Tracing (15 minutes)
**Objective:** Integrate observability

**Task:**
Integrate LangSmith:
1. Set up LangSmith API key in `.env`
2. Add tracing to graph execution
3. View traces in LangSmith dashboard
4. Analyze agent performance

**Learning Outcomes:**
- LangSmith setup
- Graph tracing
- Performance analysis

**Steps:**
1. Add `LANGCHAIN_TRACING_V2=true` to `.env`
2. Add `LANGCHAIN_API_KEY` to `.env`
3. Run graph and view traces
4. Analyze execution times and token usage

---

## Day 2 Advanced Lab Exercises

### Exercise 1: Human-in-the-Loop (25 minutes)
**Objective:** Implement real human review

**Task:**
Implement human feedback:
- Add interrupt points in the graph
- Allow human to approve/reject at review stage
- Resume execution after human input
- Store human feedback in state

**Learning Outcomes:**
- LangGraph interrupts
- Human interaction patterns
- State resumption
- Approval workflows

**Steps:**
1. Import `interrupt` from `langgraph.types`
2. Add interrupt in `human_review` node when review needed
3. Resume execution with human input
4. Store human feedback in state
5. Use feedback in subsequent nodes

**Code Pattern:**
```python
from langgraph.types import interrupt

def human_review(state: MultiAgentState) -> MultiAgentState:
    if requires_review:
        interrupt()  # Pauses execution
        # Human provides input
        # Resume with human_feedback in state
    return state
```

---

### Exercise 2: Parallel Task Execution (20 minutes)
**Objective:** Execute independent tasks concurrently

**Task:**
Execute independent tasks in parallel:
- Identify tasks with no dependencies
- Use async execution for parallel tasks
- Merge results back into state
- Handle race conditions

**Learning Outcomes:**
- Async programming in LangGraph
- Parallel execution patterns
- Task dependency management
- Result merging

**Steps:**
1. Identify tasks with no dependencies
2. Create async node functions
3. Use `asyncio.gather()` for parallel execution
4. Merge results into state
5. Handle synchronization

---

### Exercise 3: Advanced Error Recovery (15 minutes)
**Objective:** Implement sophisticated error handling

**Task:**
Implement sophisticated error handling:
- Retry failed tasks with exponential backoff
- Fallback strategies for each agent
- Error aggregation and reporting
- Graceful degradation

**Learning Outcomes:**
- Retry patterns
- Fallback strategies
- Error aggregation
- System resilience

**Steps:**
1. Implement retry decorator with exponential backoff
2. Create fallback functions for each agent
3. Aggregate errors in state
4. Implement graceful degradation logic

---

## Testing Scenarios

### Day 1 Medium Lab

**Test 1: Basic Conversation**
- Input: "What is the capital of France?"
- Expected: Direct LLM response without tool usage

**Test 2: Calculator Tool**
- Input: "What is 25 * 37?"
- Expected: Calculator tool executes, returns result

**Test 3: Web Search Tool**
- Input: "Search for latest AI news"
- Expected: Web search executes, returns results

**Test 4: Memory Test**
- Input: "My name is John. What's my name?"
- Expected: Agent remembers name from previous turn

---

### Day 1 Advanced Lab

**Scenario 1: Document Q&A**
1. Load a technical document (PDF)
2. Ask questions about the document content
3. Verify RAG retrieval is working
4. Check source citations

**Scenario 2: Multi-Tool Workflow**
1. Ask: "Search for Python best practices, then write a Python function to demonstrate one"
2. Verify web search executes
3. Verify code executor runs the generated code
4. Check memory retains context

**Scenario 3: Complex Reasoning**
1. Load financial data document
2. Ask: "Based on the document, calculate the ROI if we invest $10,000"
3. Verify agent uses DocumentQA tool first
4. Verify calculator tool for computation

---

### Day 2 Medium Lab

**Test 1: Simple Query**
- Input: "What is machine learning?"
- Expected: Research → Summarize → Clear answer

**Test 2: Complex Query**
- Input: "Compare the latest developments in GPT-4 and Claude 3"
- Expected: Multiple searches → Comprehensive comparison

**Test 3: Multi-Step Query**
- Input: "What are the best practices for deploying AI models in production?"
- Expected: Research → Quality check → Additional research if needed → Summary

---

### Day 2 Advanced Lab

**Scenario 1: Research + Code Generation**
- Query: "Research FastAPI best practices and create a sample REST API"
- Expected Flow: Plan → Research → Review → Code → Review → Synthesize

**Scenario 2: Complex Multi-Step Task**
- Query: "Create a data analysis pipeline: research pandas best practices, write code to load and analyze a CSV, and create visualizations"
- Expected: Multiple research tasks → Multiple code tasks → Reviews → Synthesis

**Scenario 3: Quality Assurance Loop**
- Query: "Write a Python function to calculate Fibonacci numbers"
- Expected: Code → Review (may request revision) → Revised Code → Review → Approve

---

## Advanced Challenges

### Day 1 Advanced Challenges

**Challenge 1: Custom Embeddings**
- Implement custom embedding model
- Compare performance with OpenAI embeddings
- Optimize for specific domain

**Challenge 2: Tool Learning**
- Implement a tool that learns from past interactions
- Store tool usage patterns
- Suggest tool improvements

**Challenge 3: Multi-Modal RAG**
- Add image processing capabilities
- Integrate vision models
- Create image + text RAG system

---

### Day 2 Advanced Challenges

**Challenge 1: Dynamic Agent Creation**
- Create agents on-demand based on task requirements
- Implement agent specialization
- Add agent learning from past tasks

**Challenge 2: Distributed Execution**
- Run agents on different processes/machines
- Implement message passing between distributed agents
- Handle network failures

**Challenge 3: Agent Optimization**
- Implement agent performance tracking
- Auto-tune agent parameters
- Optimize routing decisions based on historical data

---

## Exercise Difficulty Levels

### Beginner (Day 1 Medium)
- Exercise 1: Add New Tool ⭐⭐
- Exercise 2: Error Handling ⭐
- Exercise 3: Conversation Analysis ⭐⭐

### Intermediate (Day 1 Advanced)
- Exercise 1: Multi-Document RAG ⭐⭐⭐
- Exercise 2: Tool Chaining ⭐⭐
- Exercise 3: Advanced Memory ⭐⭐⭐
- Exercise 4: Observability ⭐⭐

### Intermediate (Day 2 Medium)
- Exercise 1: Quality Check Node ⭐⭐⭐
- Exercise 2: Error Handling ⭐⭐
- Exercise 3: LangSmith Tracing ⭐⭐

### Advanced (Day 2 Advanced)
- Exercise 1: Human-in-the-Loop ⭐⭐⭐⭐
- Exercise 2: Parallel Execution ⭐⭐⭐⭐
- Exercise 3: Error Recovery ⭐⭐⭐

---

## Tips for Completing Exercises

1. **Start Simple:** Begin with basic implementation, then add complexity
2. **Test Incrementally:** Test each feature as you add it
3. **Read Documentation:** Refer to LangChain/LangGraph docs for API details
4. **Use Examples:** Look at existing code for patterns
5. **Debug Systematically:** Use print statements and checkpoints to debug
6. **Handle Errors:** Always add error handling from the start
7. **Document Your Code:** Add comments explaining your approach

---

## Assessment Criteria

For each exercise, students should demonstrate:
- [ ] Correct implementation of required functionality
- [ ] Proper error handling
- [ ] Code comments and documentation
- [ ] Testing with multiple scenarios
- [ ] Understanding of concepts (explain in comments or report)

---

## Resources

- [LangChain Documentation](https://python.langchain.com/docs/)
- [LangGraph Documentation](https://python.langchain.com/docs/langgraph)
- [LangChain Tools](https://python.langchain.com/docs/modules/tools/)
- [LangGraph State Management](https://python.langchain.com/docs/langgraph/concepts/low_level#state)
- [LangSmith Tracing](https://docs.smith.langchain.com/)

