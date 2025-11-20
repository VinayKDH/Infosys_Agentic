# LangGraph Q&A - Quick Reference Guide

## Basic Concepts

### Q1: What is LangGraph?
**A:** LangGraph is a library for building stateful, multi-actor applications with LLMs. It extends LangChain by adding graph-based workflows that support cycles, conditional routing, and persistent state.

### Q2: How is LangGraph different from LangChain?
**A:** 
- **LangChain:** Primarily for building chains (linear sequences)
- **LangGraph:** For building graphs (complex workflows with branching, loops, and state management)
- **Key Difference:** LangGraph supports cycles, conditional routing, and state persistence, while LangChain chains are typically linear

### Q3: What is a StateGraph?
**A:** A StateGraph is the core component that defines a workflow. It consists of:
- **Nodes:** Functions that process state
- **Edges:** Connections between nodes (fixed or conditional)
- **State:** Shared data structure passed between nodes

---

## State Management

### Q4: What is state in LangGraph?
**A:** State is a TypedDict that stores all data shared between nodes. It's passed from node to node and can be modified by each node.

### Q5: What does `Annotated[List, operator.add]` mean?
**A:** This annotation tells LangGraph to append to lists instead of replacing them. When multiple nodes add items to the same list field, they accumulate rather than overwrite each other.

**Example:**
```python
messages: Annotated[List[BaseMessage], operator.add]
# Node 1 adds message A → [A]
# Node 2 adds message B → [A, B] (not just [B])
```

### Q6: How do nodes modify state?
**A:** Nodes receive state as input, modify it, and return the updated state. LangGraph merges the returned state with the existing state.

**Pattern:**
```python
def my_node(state: MyState) -> MyState:
    state["field"] = "new_value"  # Modify state
    return state  # Return updated state
```

---

## Nodes

### Q7: What is a node in LangGraph?
**A:** A node is a function that:
- Takes state as input
- Processes the state
- Returns updated state
- Does one specific thing (single responsibility)

### Q8: Can a node function be used for both processing and routing?
**A:** No, it's better to separate them:
- **Node function:** Updates state, returns state
- **Routing function:** Reads state, returns next node name (string)

This separation makes code clearer and easier to test.

### Q9: What should a node function return?
**A:** A node function should return the updated state dictionary. The function signature is:
```python
def my_node(state: MyState) -> MyState:
    # Process state
    return state
```

---

## Edges and Routing

### Q10: What is the difference between fixed edges and conditional edges?
**A:**
- **Fixed Edge:** Always goes to the same next node
  ```python
  workflow.add_edge("node_a", "node_b")
  ```
- **Conditional Edge:** Routes to different nodes based on state
  ```python
  workflow.add_conditional_edges("node_a", routing_function, {
      "option1": "node_b",
      "option2": "node_c"
  })
  ```

### Q11: How does conditional routing work?
**A:** 
1. After a node executes, LangGraph calls the routing function
2. Routing function receives the updated state
3. Routing function returns a string (next node name)
4. LangGraph follows the edge to that node

**Example:**
```python
def route(state: MyState) -> str:
    if state["value"] > 10:
        return "high_value_node"
    else:
        return "low_value_node"
```

### Q12: What does START and END mean?
**A:**
- **START:** Special node that marks the entry point of the graph
- **END:** Special node that marks the termination point
- All workflows must have a START and eventually reach END

---

## Graph Construction

### Q13: How do you build a LangGraph workflow?
**A:** 
1. Create StateGraph with state schema
2. Add nodes using `add_node()`
3. Add edges using `add_edge()` or `add_conditional_edges()`
4. Set entry point with `set_entry_point()`
5. Compile with `compile()`

**Example:**
```python
workflow = StateGraph(MyState)
workflow.add_node("node1", my_node_function)
workflow.set_entry_point("node1")
workflow.add_edge("node1", END)
graph = workflow.compile()
```

### Q14: What does `compile()` do?
**A:** `compile()` converts the graph definition into an executable workflow. You must compile before you can run the graph.

### Q15: Can you have multiple entry points?
**A:** No, a graph has one entry point set with `set_entry_point()`. However, you can have multiple paths that converge later.

---

## Execution

### Q16: How do you run a LangGraph workflow?
**A:** Use `invoke()` with initial state:
```python
initial_state = {"field": "value", ...}
result = graph.invoke(initial_state)
```

### Q17: What happens if a node raises an exception?
**A:** The exception propagates and stops execution. You should handle errors within nodes to allow graceful degradation.

### Q18: Can you resume execution from a checkpoint?
**A:** Yes, with checkpoints enabled, you can:
- Save state at each node
- Resume from any checkpoint
- Inspect state at any point

---

## Checkpoints

### Q19: What are checkpoints?
**A:** Checkpoints save the state at each node, allowing you to:
- Resume execution after interruption
- Debug by inspecting state at any point
- Implement human-in-the-loop workflows

### Q20: How do you enable checkpoints?
**A:** Use a checkpointer when compiling:
```python
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)
```

### Q21: What is MemorySaver?
**A:** MemorySaver is an in-memory checkpointer. For production, use persistent checkpoints (database, file system, etc.).

---

## Advanced Features

### Q22: What is human-in-the-loop?
**A:** A pattern where execution pauses for human input. Use `interrupt()` to pause:
```python
from langgraph.types import interrupt

def my_node(state):
    if needs_human_input:
        interrupt()  # Pauses here
    # Resume after human input
```

### Q23: Can nodes run in parallel?
**A:** LangGraph executes nodes sequentially by default. For parallel execution, you need to design your graph with multiple entry paths or use async patterns.

### Q24: How do you handle loops in LangGraph?
**A:** Use conditional edges that route back to previous nodes:
```python
workflow.add_conditional_edges("node_a", check_condition, {
    "continue": "node_b",
    "retry": "node_a"  # Loops back
})
```

### Q25: What is the difference between a graph and a chain?
**A:**
- **Chain:** Linear sequence (A → B → C)
- **Graph:** Can have branching, loops, conditional routing (A → B or C → D → back to B)

---

## Best Practices

### Q26: What makes a good node function?
**A:**
- Does one specific thing
- Pure function (same input → same output)
- Handles errors gracefully
- Updates state clearly
- Logs important actions

### Q27: Should nodes modify state directly or return new state?
**A:** In Python, you typically modify state in place and return it. LangGraph handles merging automatically.

### Q28: How do you debug a LangGraph workflow?
**A:**
- Use checkpoints to inspect state at each node
- Add print statements in nodes
- Use `verbose=True` when available
- Check error logs in state["errors"]
- Use LangSmith for tracing

### Q29: When should you use conditional edges vs fixed edges?
**A:**
- **Fixed edges:** When flow is always the same
- **Conditional edges:** When flow depends on state content or processing results

### Q30: How do you test LangGraph workflows?
**A:**
- Test individual nodes with mock state
- Test routing functions with different state values
- Test full workflow with sample inputs
- Use checkpoints to verify state at each step

---

## Common Patterns

### Q31: What is the "discrete steps" pattern?
**A:** Breaking complex workflows into small, focused nodes. Each node does one thing, making the workflow easier to understand, debug, and modify.

### Q32: What is the "state as shared memory" pattern?
**A:** Storing raw data in state, not formatted text. This allows different nodes to format the same data differently without changing the state structure.

### Q33: How do you handle errors in a graph?
**A:**
- Catch errors in nodes
- Store errors in state["errors"]
- Use default values or fallback logic
- Route to error handling nodes if needed

### Q34: Can you have nested graphs?
**A:** Yes, you can create subgraphs and include them as nodes in a larger graph. This enables modular design.

### Q35: How do you pass data between nodes?
**A:** Through the shared state. Each node reads from state, processes, and writes back to state. The state is automatically passed to the next node.

---

## Performance and Optimization

### Q36: How do you optimize LangGraph performance?
**A:**
- Minimize state size (only store necessary data)
- Use checkpoints efficiently
- Cache expensive operations
- Optimize LLM calls (batch when possible)
- Use appropriate chunk sizes for RAG

### Q37: Can you cache node results?
**A:** Yes, you can implement caching within nodes or use LangGraph's built-in caching mechanisms for LLM calls.

### Q38: How do you handle rate limits in LangGraph?
**A:**
- Add retry logic with exponential backoff in nodes
- Use rate limiting libraries
- Implement queuing for high-volume scenarios
- Use checkpoints to resume after rate limit errors

---

## Integration

### Q39: How do you integrate LangGraph with external systems?
**A:** Create nodes that interact with external APIs:
- Database queries
- Email sending (SMTP/API)
- Ticketing systems (Jira, GitHub)
- CRM systems
- Vector databases

### Q40: Can you use LangGraph with async/await?
**A:** Yes, LangGraph supports async node functions. Use `async def` for nodes that need async operations.

---

## Troubleshooting

### Q41: My graph doesn't compile. What's wrong?
**A:** Common issues:
- Missing entry point
- Node function doesn't return state
- Routing function doesn't return valid node name
- State schema mismatch
- Circular dependencies without exit condition

### Q42: State is not updating between nodes. Why?
**A:** 
- Make sure you're returning the updated state
- Check that you're modifying state fields correctly
- Verify state schema matches your modifications
- Ensure you're not creating a new dict instead of modifying existing one

### Q43: Conditional routing always goes to the same node. Why?
**A:**
- Check that routing function reads correct state fields
- Verify routing logic conditions
- Ensure state contains expected values
- Add debug prints to routing function

### Q44: How do I see what's happening in my graph?
**A:**
- Use `verbose=True` in graph compilation
- Add print statements in nodes
- Use LangSmith for detailed tracing
- Inspect checkpoints to see state at each step
- Check state["messages"] for execution log

---

## Quick Reference

### Graph Construction Pattern
```python
from langgraph.graph import StateGraph, START, END

workflow = StateGraph(MyState)
workflow.add_node("node1", node_function)
workflow.set_entry_point("node1")
workflow.add_edge("node1", END)
graph = workflow.compile()
```

### Conditional Routing Pattern
```python
def route(state: MyState) -> str:
    if condition:
        return "node_a"
    else:
        return "node_b"

workflow.add_conditional_edges("node", route, {
    "node_a": "node_a",
    "node_b": "node_b"
})
```

### Node Function Pattern
```python
def my_node(state: MyState) -> MyState:
    # Read from state
    value = state.get("field")
    
    # Process
    result = process(value)
    
    # Update state
    state["result"] = result
    state["messages"].append(AIMessage(content="Done"))
    
    # Return updated state
    return state
```

### State Definition Pattern
```python
from typing import TypedDict, List, Annotated
from langchain_core.messages import BaseMessage
import operator

class MyState(TypedDict):
    input: str
    result: str
    messages: Annotated[List[BaseMessage], operator.add]
    errors: Annotated[List[str], operator.add]
```

---

## Key Takeaways

1. **Graphs enable complex workflows** that chains cannot handle
2. **State is shared memory** between all nodes
3. **Nodes are discrete functions** that do one thing
4. **Routing enables dynamic flow** based on state
5. **Checkpoints enable resumability** and debugging
6. **Error handling** should be in each node
7. **Separation of concerns** makes graphs maintainable

---

## Resources

- [LangGraph Documentation](https://python.langchain.com/docs/langgraph)
- [LangGraph Concepts](https://python.langchain.com/docs/langgraph/concepts)
- [State Management](https://python.langchain.com/docs/langgraph/concepts/low_level#state)
- [Conditional Edges](https://python.langchain.com/docs/langgraph/concepts/low_level#conditional-edges)
- [Checkpoints](https://python.langchain.com/docs/langgraph/how_to/persistence)
- [Human-in-the-Loop](https://python.langchain.com/docs/langgraph/how_to/interrupt)

