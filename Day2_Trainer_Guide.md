# Day 2 Labs - Trainer's Guide: Multi-Agent Systems with LangGraph

## Overview
This guide provides trainers with a comprehensive breakdown of the Day 2 labs (Medium and Advanced), focusing on multi-agent systems, LangGraph workflows, state management, and agent orchestration.

---

## Day 2 Medium Lab: Core Components

### 1. **LangGraph - Graph-Based Workflow Engine**
**Component:** `StateGraph` from LangGraph
**Location:** `graph/research_graph.py`

**What it does:**
- Defines a state machine workflow for multi-agent collaboration
- Manages execution flow between agents
- Handles state transitions and data passing
- Compiles graph into executable workflow

**Key Concepts:**
- **Nodes:** Individual agent functions that process state
- **Edges:** Connections between nodes (can be fixed or conditional)
- **State:** Shared data structure passed between nodes
- **Entry Point:** Starting node of the workflow
- **END:** Terminal node that stops execution

**Key Teaching Points:**
- **Graph vs. Chain:** Graphs allow complex branching and loops
- **State Persistence:** State is passed and updated through nodes
- **Compilation:** Graph must be compiled before execution
- **Node Functions:** Each node receives state, processes it, returns updated state

**Code Pattern:**
```python
workflow = StateGraph(ResearchState)
workflow.add_node("researcher", self.research_node)
workflow.add_node("summarizer", self.summarize_node)
workflow.set_entry_point("researcher")
workflow.add_edge("researcher", "summarizer")
workflow.add_edge("summarizer", END)
return workflow.compile()
```

---

### 2. **State Management - Shared Data Structure**
**Component:** `ResearchState` TypedDict
**Location:** `state.py`

**What it does:**
- Defines the schema for shared state across agents
- Uses `Annotated` with `operator.add` for list accumulation
- Ensures type safety and structure

**Key Fields:**
- `messages`: Conversation history (accumulated)
- `research_results`: Research findings string
- `final_answer`: Final synthesized answer
- `query`: Original user query
- `iteration_count`: Number of iterations

**Key Teaching Points:**
- **TypedDict:** Provides type hints and structure
- **Annotated Lists:** `operator.add` allows nodes to append to lists
- **State Immutability:** Nodes return new state, don't mutate directly
- **State Access:** Nodes read from and write to state dictionary

**Code Pattern:**
```python
class ResearchState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    research_results: str
    final_answer: str
    query: str
    iteration_count: int
```

---

### 3. **Researcher Agent - Information Gathering**
**Component:** `ResearcherAgent` class
**Location:** `agents/researcher.py`

**What it does:**
- Conducts web research using search tools
- Uses LangChain agent framework with DuckDuckGo search
- Returns comprehensive research findings

**Key Features:**
- **Agent Framework:** Uses AgentExecutor for tool-based research
- **Web Search:** DuckDuckGoSearchRun for internet searches
- **Fallback:** Direct search if agent framework unavailable
- **Error Handling:** Graceful error messages

**Key Teaching Points:**
- **Agent vs. Direct LLM:** Agents can use tools, direct LLM cannot
- **Tool Integration:** Search tool extends agent capabilities
- **Research Prompt:** Structured prompt guides research quality
- **Output Format:** Returns string findings for downstream processing

---

### 4. **Summarizer Agent - Synthesis**
**Component:** `SummarizerAgent` class
**Location:** `agents/summarizer.py`

**What it does:**
- Synthesizes research findings into coherent answers
- Uses lower temperature (0.3) for focused, consistent summaries
- Structures information logically

**Key Features:**
- **Prompt Engineering:** Detailed system prompt for summarization guidelines
- **Context Integration:** Combines query and research results
- **LCEL Chain:** Uses LangChain Expression Language for clean composition
- **Temperature Control:** Lower temperature for more deterministic output

**Key Teaching Points:**
- **Temperature Selection:** Lower for summarization, higher for creativity
- **Prompt Structure:** System + Human message pattern
- **Chain Composition:** `prompt | llm` creates executable chain
- **Output Formatting:** Returns content string for state update

---

### 5. **Graph Nodes - Execution Functions**
**Component:** Node functions in `ResearchGraph`
**Location:** `graph/research_graph.py`

**What it does:**
- Each node function processes state and returns updated state
- Implements agent execution logic
- Manages state transitions

**Node Functions:**

#### `research_node(state: ResearchState) -> ResearchState`
- Extracts query from state or messages
- Calls ResearcherAgent to perform research
- Updates state with research results
- Appends messages to conversation history
- Increments iteration count

#### `summarize_node(state: ResearchState) -> ResearchState`
- Retrieves query and research results from state
- Calls SummarizerAgent to create summary
- Updates final_answer in state
- Appends summary to messages

**Key Teaching Points:**
- **Node Signature:** Must accept state, return state
- **State Extraction:** Read from state dictionary
- **State Update:** Modify state and return
- **Message Handling:** Extract query from HumanMessage if needed

---

## Day 2 Advanced Lab: Core Components

### 1. **Advanced State Management**
**Component:** `MultiAgentState` TypedDict
**Location:** `state.py`

**What it does:**
- Complex state schema supporting multiple agent types
- Task management with status tracking
- Separate storage for different work products
- Metadata for observability

**Key Features:**
- **Enums:** `AgentRole` and `TaskStatus` for type safety
- **Task Structure:** TypedDict for task definition
- **Annotated Lists:** Multiple accumulating lists for different data types
- **Metadata Fields:** Agent history, errors, human input flags

**Key Teaching Points:**
- **Structured State:** Complex state enables sophisticated workflows
- **Task Management:** Tasks track status, assignments, dependencies
- **Work Product Separation:** Research, code, reviews stored separately
- **Observability:** Agent history and errors enable debugging

---

### 2. **Planner Agent - Task Decomposition**
**Component:** `PlannerAgent` class
**Location:** `agents/planner.py`

**What it does:**
- Breaks down complex queries into actionable tasks
- Assigns tasks to appropriate agents
- Identifies task dependencies
- Uses structured output parsing

**Key Features:**
- **Pydantic Output Parser:** Ensures structured plan output
- **TaskPlan Model:** Defines plan structure with tasks and reasoning
- **Task Creation:** Converts plan into Task objects with UUIDs
- **Agent Assignment:** Maps tasks to appropriate agent roles

**Key Teaching Points:**
- **Structured Output:** Pydantic ensures consistent plan format
- **Task Decomposition:** Breaking complex problems into smaller tasks
- **Dependency Management:** Tasks can depend on other tasks
- **Agent Selection:** Planner decides which agent handles each task

---

### 3. **Researcher Agent (Advanced) - Context-Aware Research**
**Component:** `ResearcherAgent` class
**Location:** `agents/researcher.py`

**What it does:**
- Performs research for specific tasks
- Incorporates context from previous tasks
- Returns structured findings with sources
- Tracks task status and timestamps

**Key Features:**
- **Task-Based:** Works on Task objects, not just queries
- **Context Integration:** Uses previous research/code as context
- **Source Extraction:** Extracts URLs from research results
- **Status Tracking:** Returns status (COMPLETED/FAILED) with results

**Key Teaching Points:**
- **Context Passing:** Agents receive context from previous work
- **Task Tracking:** Each research operation linked to specific task
- **Source Attribution:** Extracting and storing source URLs
- **Error Handling:** Returns structured error information

---

### 4. **Coder Agent - Code Generation**
**Component:** `CoderAgent` class
**Location:** `agents/coder.py`

**What it does:**
- Generates code based on task descriptions
- Uses research findings as context
- Extracts code blocks from markdown
- Provides explanations with code

**Key Features:**
- **Low Temperature (0.2):** More deterministic code generation
- **Context Integration:** Uses research findings and previous code
- **Code Extraction:** Parses markdown code blocks
- **Explanation Separation:** Separates code from explanations

**Key Teaching Points:**
- **Temperature for Code:** Lower temperature for consistent code
- **Context Usage:** Research informs code generation
- **Code Parsing:** Extracting code from LLM markdown responses
- **Structured Output:** Returns code, explanation, status separately

---

### 5. **Reviewer Agent - Quality Assurance**
**Component:** `ReviewerAgent` class
**Location:** `agents/reviewer.py`

**What it does:**
- Reviews work products (research or code)
- Provides approval or revision feedback
- Checks quality, completeness, alignment
- Determines if work meets requirements

**Key Features:**
- **Work Product Analysis:** Reviews both research and code
- **Approval Logic:** Determines if work is approved
- **Feedback Generation:** Provides detailed improvement suggestions
- **Status Determination:** Sets task status based on review

**Key Teaching Points:**
- **Quality Gates:** Review ensures work meets standards
- **Feedback Loop:** Rejected work triggers revision
- **Multi-Format Review:** Handles different work product types
- **Approval Criteria:** LLM determines approval based on guidelines

---

### 6. **Conditional Routing - Dynamic Flow Control**
**Component:** `RoutingLogic` class
**Location:** `utils/routing.py`

**What it does:**
- Determines next node based on current state
- Implements decision logic for conditional edges
- Routes to appropriate agent based on task status
- Handles approval/rejection routing

**Routing Functions:**

#### `after_planning(state) -> str`
- Checks for research tasks → routes to researcher
- Checks for coding tasks → routes to coder
- Otherwise → routes to synthesizer

#### `after_research(state) -> str`
- Always routes to reviewer for quality check

#### `after_coding(state) -> str`
- Always routes to reviewer for code review

#### `after_review(state) -> str`
- If approved: checks for more tasks → routes accordingly
- If rejected: routes back to original agent for revision
- If no more tasks: routes to synthesizer

**Key Teaching Points:**
- **Conditional Edges:** Enable dynamic workflow routing
- **State-Based Decisions:** Routing depends on state content
- **Feedback Loops:** Rejection routes back for revision
- **Task Completion:** Routing checks for pending tasks

---

### 7. **Multi-Agent Graph - Complex Orchestration**
**Component:** `MultiAgentGraph` class
**Location:** `graph/multi_agent_graph.py`

**What it does:**
- Orchestrates 4 agents (Planner, Researcher, Coder, Reviewer)
- Manages complex state transitions
- Implements checkpoints for state persistence
- Handles task execution and tracking

**Key Features:**
- **Checkpoints:** MemorySaver enables state persistence
- **Multiple Nodes:** 5 nodes (planner, researcher, coder, reviewer, synthesizer)
- **Conditional Routing:** Dynamic flow based on state
- **Context Building:** Aggregates context for agents

**Node Functions:**

#### `planning_node(state) -> state`
- Extracts query from messages
- Calls PlannerAgent to create plan
- Updates state with tasks and plan
- Logs to agent_history

#### `research_node(state) -> state`
- Finds next pending research task
- Builds context from previous work
- Calls ResearcherAgent
- Updates task status and research_findings

#### `coding_node(state) -> state`
- Finds next pending coding task
- Builds context from research
- Calls CoderAgent
- Updates task status and code_artifacts

#### `review_node(state) -> state`
- Finds current task being reviewed
- Retrieves work product (code or research)
- Calls ReviewerAgent
- Updates task status based on approval
- Sets requires_human_input if rejected

#### `synthesize_node(state) -> state`
- Aggregates all work products
- Creates final comprehensive answer
- Updates final_output in state

**Key Teaching Points:**
- **Graph Complexity:** Multiple agents require careful orchestration
- **State Management:** Complex state tracks multiple work streams
- **Checkpoints:** Enable resumable execution and debugging
- **Context Aggregation:** Each agent receives relevant context

---

## Module/Class/Function Reference

This section provides a quick reference guide to all classes, functions, and modules in both labs.

---

### Day 2 Medium Lab: Module Reference

#### **Module: `state.py`**
Defines the state schema for the research graph.

**Classes:**

##### `ResearchState` (TypedDict)
**Purpose:** Defines the structure of shared state between graph nodes.

**Fields:**
- `messages: Annotated[List[BaseMessage], operator.add]` - Conversation history (accumulated)
- `research_results: str` - Research findings from researcher agent
- `final_answer: str` - Final synthesized answer from summarizer
- `query: str` - Original user query
- `iteration_count: int` - Number of graph iterations

**Key Features:**
- Uses `Annotated` with `operator.add` for list accumulation
- TypedDict provides type safety
- Simple structure for linear workflow

---

#### **Module: `agents/researcher.py`**
Implements the researcher agent for web research.

**Classes:**

##### `ResearcherAgent`
**Purpose:** Conducts web research using search tools and agent framework.

**Methods:**

###### `__init__(self)`
**Purpose:** Initializes the researcher agent with LLM and search tool.

**What it does:**
- Creates ChatOpenAI instance (temperature 0.7)
- Initializes DuckDuckGoSearchRun tool
- Creates agent executor with search tool (if available)
- Falls back to direct search if agent framework unavailable

**Error Handling:**
- Gracefully handles missing agent framework
- Provides fallback search capability

###### `research(self, query: str) -> str`
**Purpose:** Performs research on a given query.

**What it does:**
- Creates research prompt with query
- Invokes agent executor to search web
- Returns comprehensive research findings
- Falls back to direct search if agent unavailable

**Parameters:**
- `query`: Research query string

**Returns:**
- Research findings string or error message

**Key Features:**
- Uses structured research prompt
- Agent framework enables tool use
- Error handling with fallback

---

#### **Module: `agents/summarizer.py`**
Implements the summarizer agent for synthesizing research.

**Classes:**

##### `SummarizerAgent`
**Purpose:** Synthesizes research findings into coherent answers.

**Methods:**

###### `__init__(self)`
**Purpose:** Initializes the summarizer agent with LLM and prompt.

**What it does:**
- Creates ChatOpenAI instance (temperature 0.3 for focused summaries)
- Defines prompt template with summarization guidelines
- Sets up system and human message structure

**Key Features:**
- Lower temperature for more deterministic output
- Detailed system prompt with guidelines
- Structured prompt template

###### `summarize(self, query: str, research_results: str) -> str`
**Purpose:** Creates a comprehensive summary from research findings.

**What it does:**
- Formats prompt with query and research results
- Invokes LLM chain to generate summary
- Returns synthesized answer

**Parameters:**
- `query`: Original user query
- `research_results`: Research findings string

**Returns:**
- Synthesized summary string or error message

**Key Features:**
- LCEL chain composition (`prompt | llm`)
- Context integration (query + research)
- Error handling

---

#### **Module: `graph/research_graph.py`**
Implements the LangGraph workflow for research and summarization.

**Classes:**

##### `ResearchGraph`
**Purpose:** Orchestrates the research and summarization workflow using LangGraph.

**Methods:**

###### `__init__(self)`
**Purpose:** Initializes the graph with agents and builds workflow.

**What it does:**
- Creates ResearcherAgent and SummarizerAgent instances
- Builds graph structure via `_build_graph()`
- Compiles graph for execution

###### `_build_graph(self) -> CompiledGraph`
**Purpose:** Constructs the LangGraph workflow.

**What it does:**
- Creates StateGraph with ResearchState schema
- Adds nodes: "researcher" and "summarizer"
- Sets entry point to "researcher"
- Adds edges: researcher → summarizer → END
- Compiles and returns graph

**Returns:**
- Compiled LangGraph workflow

**Key Features:**
- Simple linear workflow
- Fixed edges (no conditional routing)
- Two-node pipeline

###### `research_node(self, state: ResearchState) -> ResearchState`
**Purpose:** Node function that executes research.

**What it does:**
- Extracts query from state or messages
- Calls ResearcherAgent.research()
- Updates state with research results
- Appends research message to conversation
- Increments iteration count
- Returns updated state

**Key Features:**
- State extraction and update
- Message handling
- Error propagation

###### `summarize_node(self, state: ResearchState) -> ResearchState`
**Purpose:** Node function that creates final summary.

**What it does:**
- Retrieves query and research_results from state
- Calls SummarizerAgent.summarize()
- Updates final_answer in state
- Appends summary to messages
- Returns updated state

**Key Features:**
- State reading and writing
- Agent invocation
- Message logging

###### `run(self, query: str) -> dict`
**Purpose:** Executes the graph with a user query.

**What it does:**
- Creates initial state with query
- Invokes compiled graph
- Returns final state

**Parameters:**
- `query`: User research query

**Returns:**
- Final state dictionary with results

**Key Features:**
- State initialization
- Graph execution
- Result extraction

---

#### **Module: `main.py`**
Main entry point for the Medium lab application.

**Functions:**

##### `main()`
**Purpose:** Main application loop for user interaction.

**What it does:**
- Initializes ResearchGraph
- Displays welcome message
- Runs interactive loop:
  - Gets user query
  - Executes graph
  - Displays results
  - Shows iteration count
- Handles exit commands

**Key Features:**
- User interface
- Error handling
- Result display

---

### Day 2 Advanced Lab: Module Reference

#### **Module: `state.py`**
Defines advanced state schema with task management.

**Classes:**

##### `AgentRole` (Enum)
**Purpose:** Defines available agent roles.

**Values:**
- `PLANNER` - Planning agent
- `RESEARCHER` - Research agent
- `CODER` - Code generation agent
- `REVIEWER` - Quality review agent

##### `TaskStatus` (Enum)
**Purpose:** Defines task status values.

**Values:**
- `PENDING` - Task not started
- `IN_PROGRESS` - Task currently executing
- `COMPLETED` - Task finished successfully
- `FAILED` - Task failed
- `NEEDS_REVIEW` - Task needs revision

##### `Task` (TypedDict)
**Purpose:** Defines structure for individual tasks.

**Fields:**
- `id: str` - Unique task identifier (UUID)
- `description: str` - Task description
- `assigned_to: AgentRole` - Agent responsible for task
- `status: TaskStatus` - Current task status
- `result: Optional[str]` - Task result/output
- `dependencies: List[str]` - List of task IDs this depends on
- `created_at: str` - ISO timestamp of creation
- `completed_at: Optional[str]` - ISO timestamp of completion

##### `MultiAgentState` (TypedDict)
**Purpose:** Complex state schema for multi-agent system.

**Fields:**
- `messages: Annotated[List[BaseMessage], operator.add]` - Conversation history
- `original_query: str` - Original user query
- `plan: Optional[Dict[str, Any]]` - Execution plan
- `tasks: Annotated[List[Task], operator.add]` - List of tasks
- `current_task_id: Optional[str]` - ID of currently executing task
- `research_findings: Annotated[List[Dict[str, str]], operator.add]` - Research results
- `code_artifacts: Annotated[List[Dict[str, str]], operator.add]` - Generated code
- `review_feedback: Annotated[List[Dict[str, str]], operator.add]` - Review results
- `final_output: str` - Final synthesized output
- `iteration_count: int` - Number of iterations
- `agent_history: Annotated[List[Dict[str, Any]], operator.add]` - Agent action log
- `errors: Annotated[List[str], operator.add]` - Error log
- `requires_human_input: bool` - Flag for human intervention
- `human_feedback: Optional[str]` - Human-provided feedback

---

#### **Module: `agents/planner.py`**
Implements the planning agent for task decomposition.

**Classes:**

##### `TaskPlan` (Pydantic BaseModel)
**Purpose:** Structured output model for plan generation.

**Fields:**
- `tasks: List[dict]` - List of task descriptions
- `reasoning: str` - Reasoning behind the plan

##### `PlannerAgent`
**Purpose:** Breaks down queries into actionable tasks.

**Methods:**

###### `__init__(self)`
**Purpose:** Initializes planner with LLM and output parser.

**What it does:**
- Creates ChatOpenAI (temperature 0.3 for structured planning)
- Creates PydanticOutputParser for TaskPlan
- Defines prompt template with format instructions
- Sets up structured output generation

**Key Features:**
- Structured output parsing
- Lower temperature for consistent planning
- Format instructions in prompt

###### `create_plan(self, query: str) -> dict`
**Purpose:** Creates execution plan from user query.

**What it does:**
- Invokes LLM with query to generate plan
- Parses structured output using Pydantic
- Converts plan tasks into Task objects
- Assigns UUIDs and timestamps
- Maps agent roles to tasks
- Returns plan dictionary with tasks and reasoning

**Parameters:**
- `query`: User query string

**Returns:**
- Dictionary with:
  - `tasks`: List of Task objects
  - `reasoning`: Plan reasoning string
  - `plan_structure`: JSON string of task descriptions

**Key Features:**
- Structured output ensures consistent format
- Task creation with metadata
- Agent assignment logic
- Error handling with fallback

---

#### **Module: `agents/researcher.py`**
Advanced researcher agent with task-based research.

**Classes:**

##### `ResearcherAgent`
**Purpose:** Performs research for specific tasks with context.

**Methods:**

###### `__init__(self)`
**Purpose:** Initializes researcher with LLM and search tool.

**What it does:**
- Creates ChatOpenAI instance
- Initializes DuckDuckGoSearchRun
- Creates agent executor with search tool
- Handles fallback if agent framework unavailable

###### `research(self, task: Task, context: dict = None) -> dict`
**Purpose:** Performs research for a specific task.

**What it does:**
- Extracts query from task description
- Incorporates context from previous tasks
- Creates research prompt
- Invokes agent to search web
- Extracts source URLs from results
- Returns structured findings dictionary

**Parameters:**
- `task`: Task object to research
- `context`: Optional context from previous work

**Returns:**
- Dictionary with:
  - `task_id`: Task identifier
  - `findings`: Research findings string
  - `sources`: List of source URLs
  - `status`: TaskStatus (COMPLETED/FAILED)
  - `timestamp`: ISO timestamp

**Key Features:**
- Task-based research
- Context integration
- Source extraction
- Status tracking

###### `_extract_sources(self, text: str) -> list`
**Purpose:** Extracts URLs from research text.

**What it does:**
- Uses regex to find HTTP/HTTPS URLs
- Limits to 5 sources
- Returns list of URLs

**Returns:**
- List of source URL strings

---

#### **Module: `agents/coder.py`**
Implements code generation agent.

**Classes:**

##### `CoderAgent`
**Purpose:** Generates code based on task descriptions and context.

**Methods:**

###### `__init__(self)`
**Purpose:** Initializes coder with LLM and prompt.

**What it does:**
- Creates ChatOpenAI (temperature 0.2 for deterministic code)
- Defines prompt template with coding guidelines
- Sets up code generation chain

**Key Features:**
- Very low temperature for consistent code
- Detailed coding guidelines in prompt
- Context-aware generation

###### `generate_code(self, task: Task, context: dict = None) -> dict`
**Purpose:** Generates code for a task.

**What it does:**
- Builds context string from research and previous code
- Invokes LLM with task description and context
- Extracts code blocks from markdown response
- Separates code from explanation
- Returns structured code artifact

**Parameters:**
- `task`: Task object to code
- `context`: Optional context (research, previous code)

**Returns:**
- Dictionary with:
  - `task_id`: Task identifier
  - `code`: Extracted code string
  - `explanation`: Explanation text
  - `status`: TaskStatus
  - `timestamp`: ISO timestamp

**Key Features:**
- Code extraction from markdown
- Context integration
- Explanation separation
- Error handling

###### `_extract_code_blocks(self, text: str) -> list`
**Purpose:** Extracts code blocks from markdown.

**What it does:**
- Uses regex to find fenced code blocks
- Supports multiple languages
- Returns list of code strings

**Returns:**
- List of code block strings

###### `_extract_explanation(self, text: str) -> str`
**Purpose:** Extracts non-code explanation text.

**What it does:**
- Removes code blocks from text
- Returns remaining explanation text

**Returns:**
- Explanation string

---

#### **Module: `agents/reviewer.py`**
Implements quality review agent.

**Classes:**

##### `ReviewerAgent`
**Purpose:** Reviews work products for quality and approval.

**Methods:**

###### `__init__(self)`
**Purpose:** Initializes reviewer with LLM and prompt.

**What it does:**
- Creates ChatOpenAI (temperature 0.3)
- Defines prompt with review guidelines
- Sets up review chain

**Key Features:**
- Moderate temperature for balanced review
- Comprehensive review criteria
- Approval/rejection logic

###### `review(self, task: Task, work_product: dict, context: dict = None) -> dict`
**Purpose:** Reviews a work product (code or research).

**What it does:**
- Formats work product based on type (code or research)
- Builds context string
- Invokes LLM to review work
- Determines approval status from review text
- Returns structured review feedback

**Parameters:**
- `task`: Task being reviewed
- `work_product`: Dictionary with code or findings
- `context`: Optional additional context

**Returns:**
- Dictionary with:
  - `task_id`: Task identifier
  - `approved`: Boolean approval status
  - `feedback`: Review feedback string
  - `status`: TaskStatus (COMPLETED/NEEDS_REVIEW/FAILED)
  - `timestamp`: ISO timestamp

**Key Features:**
- Multi-format review (code and research)
- Approval determination
- Detailed feedback generation
- Status assignment

---

#### **Module: `utils/routing.py`**
Implements conditional routing logic.

**Classes:**

##### `RoutingLogic`
**Purpose:** Determines next node based on current state.

**Methods:**

###### `after_planning(self, state: MultiAgentState) -> str`
**Purpose:** Routes after planning node.

**What it does:**
- Checks for research tasks → returns "researcher"
- Checks for coding tasks → returns "coder"
- Otherwise → returns "synthesizer"

**Returns:**
- Next node name string

###### `after_research(self, state: MultiAgentState) -> str`
**Purpose:** Routes after research node.

**What it does:**
- Always routes to reviewer for quality check
- Returns "reviewer"

**Returns:**
- "reviewer" string

###### `after_coding(self, state: MultiAgentState) -> str`
**Purpose:** Routes after coding node.

**What it does:**
- Always routes to reviewer for code review
- Returns "reviewer"

**Returns:**
- "reviewer" string

###### `after_review(self, state: MultiAgentState) -> str`
**Purpose:** Routes after review node.

**What it does:**
- Finds current task being reviewed
- Checks if approved
- If approved:
  - Checks for more pending tasks
  - Routes to appropriate agent or synthesizer
- If rejected:
  - Routes back to original agent for revision
- Returns next node name

**Returns:**
- Next node name string

**Key Features:**
- State-based decision making
- Task status checking
- Approval/rejection handling
- Dynamic routing

---

#### **Module: `graph/multi_agent_graph.py`**
Implements complex multi-agent graph orchestration.

**Classes:**

##### `MultiAgentGraph`
**Purpose:** Orchestrates 4-agent system with complex routing.

**Methods:**

###### `__init__(self, enable_checkpoints: bool = True)`
**Purpose:** Initializes graph with all agents and builds workflow.

**What it does:**
- Creates all agent instances (Planner, Researcher, Coder, Reviewer)
- Creates RoutingLogic instance
- Builds graph via `_build_graph()`

**Parameters:**
- `enable_checkpoints`: Whether to enable state persistence

###### `_build_graph(self, enable_checkpoints: bool) -> CompiledGraph`
**Purpose:** Constructs the multi-agent graph workflow.

**What it does:**
- Creates StateGraph with MultiAgentState
- Adds 5 nodes: planner, researcher, coder, reviewer, synthesizer
- Sets entry point to "planner"
- Adds conditional edges with routing logic:
  - planner → (researcher/coder/synthesizer)
  - researcher → reviewer
  - coder → reviewer
  - reviewer → (researcher/coder/synthesizer/end)
- Adds fixed edge: synthesizer → END
- Compiles with checkpoints if enabled
- Returns compiled graph

**Key Features:**
- Multiple conditional edges
- Checkpoint support
- Complex routing logic

###### `planning_node(self, state: MultiAgentState) -> MultiAgentState`
**Purpose:** Executes planning node.

**What it does:**
- Extracts query from messages or state
- Calls PlannerAgent.create_plan()
- Updates state with plan and tasks
- Appends plan message to conversation
- Logs to agent_history
- Returns updated state

###### `research_node(self, state: MultiAgentState) -> MultiAgentState`
**Purpose:** Executes research node.

**What it does:**
- Finds next pending research task
- Sets current_task_id
- Builds context from previous work
- Calls ResearcherAgent.research()
- Updates research_findings
- Updates task status and result
- Appends message
- Returns updated state

###### `coding_node(self, state: MultiAgentState) -> MultiAgentState`
**Purpose:** Executes coding node.

**What it does:**
- Finds next pending coding task
- Sets current_task_id
- Builds context from research
- Calls CoderAgent.generate_code()
- Updates code_artifacts
- Updates task status and result
- Appends message
- Returns updated state

###### `review_node(self, state: MultiAgentState) -> MultiAgentState`
**Purpose:** Executes review node.

**What it does:**
- Gets current_task_id from state
- Finds corresponding task
- Retrieves work product (code or research)
- Builds context
- Calls ReviewerAgent.review()
- Updates review_feedback
- Updates task status based on approval
- Sets requires_human_input if rejected
- Appends review message
- Returns updated state

###### `synthesize_node(self, state: MultiAgentState) -> MultiAgentState`
**Purpose:** Creates final synthesized output.

**What it does:**
- Aggregates all research findings
- Aggregates all code artifacts
- Aggregates all review feedback
- Creates synthesis prompt
- Invokes LLM to generate final answer
- Updates final_output in state
- Appends final message
- Returns updated state

**Key Features:**
- Context aggregation
- Final synthesis
- Comprehensive output

###### `_build_context(self, state: MultiAgentState) -> dict`
**Purpose:** Builds context dictionary for agents.

**What it does:**
- Aggregates research findings into string
- Aggregates code artifacts into string
- Lists completed task descriptions
- Returns context dictionary

**Returns:**
- Dictionary with research, code, and tasks

###### `run(self, query: str, config: dict = None) -> dict`
**Purpose:** Executes the graph with a query.

**What it does:**
- Creates initial state with query
- Sets up checkpoint config if needed
- Invokes graph with initial state
- Returns final state

**Parameters:**
- `query`: User query string
- `config`: Optional checkpoint configuration

**Returns:**
- Final state dictionary

---

#### **Module: `main.py`**
Main entry point for Advanced lab application.

**Functions:**

##### `main()`
**Purpose:** Main application loop.

**What it does:**
- Initializes MultiAgentGraph with checkpoints
- Displays welcome message with agent descriptions
- Runs interactive loop:
  - Gets user query
  - Executes graph with checkpoint config
  - Displays final output
  - Shows statistics (tasks, findings, artifacts, reviews)
- Handles errors and exit commands

**Key Features:**
- Checkpoint configuration
- Statistics display
- Error handling

---

## Lab Construction: How Components Work Together

### Day 2 Medium Lab Architecture

```
┌─────────────┐
│   User      │
│   Query     │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│   ResearchGraph     │
│   (LangGraph)       │
└──────┬──────────────┘
       │
       ├──► Entry Point: "researcher"
       │
       ▼
┌─────────────────────┐
│  research_node()    │
│  ┌───────────────┐  │
│  │ ResearcherAgent│  │
│  │ - Web Search  │  │
│  │ - Agent Exec  │  │
│  └───────────────┘  │
└──────┬──────────────┘
       │
       │ Updates: research_results
       │
       ▼
┌─────────────────────┐
│  summarize_node()   │
│  ┌───────────────┐  │
│  │SummarizerAgent│  │
│  │ - Synthesis   │  │
│  │ - LLM Chain   │  │
│  └───────────────┘  │
└──────┬──────────────┘
       │
       │ Updates: final_answer
       │
       ▼
       END
```

**Flow:**
1. User provides query
2. Graph initialized with query in state
3. Researcher node executes → updates research_results
4. Summarizer node executes → updates final_answer
5. Graph completes → returns final state

---

### Day 2 Advanced Lab Architecture

```
┌─────────────┐
│   User      │
│   Query     │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  MultiAgentGraph    │
│  (LangGraph)        │
└──────┬──────────────┘
       │
       ├──► Entry Point: "planner"
       │
       ▼
┌─────────────────────┐
│  planning_node()    │
│  ┌───────────────┐  │
│  │ PlannerAgent  │  │
│  │ - Task Break  │  │
│  │ - Assignment  │  │
│  └───────────────┘  │
└──────┬──────────────┘
       │
       │ Conditional Routing
       │
       ├──► Researcher ──┐
       │                 │
       ├──► Coder ───────┤
       │                 │
       └──► Synthesizer  │
                         │
       ┌─────────────────┘
       │
       ▼
┌─────────────────────┐
│  research_node()    │
│  ┌───────────────┐  │
│  │ResearcherAgent│  │
│  │ - Task-based  │  │
│  │ - Context     │  │
│  └───────────────┘  │
└──────┬──────────────┘
       │
       │ Always routes to:
       │
       ▼
┌─────────────────────┐
│  review_node()      │
│  ┌───────────────┐  │
│  │ ReviewerAgent │  │
│  │ - Approval    │  │
│  │ - Feedback    │  │
│  └───────────────┘  │
└──────┬──────────────┘
       │
       │ Conditional Routing
       │
       ├──► If Approved:
       │    ├──► More tasks? → Researcher/Coder
       │    └──► No tasks? → Synthesizer
       │
       └──► If Rejected:
            └──► Back to Researcher/Coder
                 (Revision Loop)
       │
       ▼
┌─────────────────────┐
│  synthesize_node()  │
│  ┌───────────────┐  │
│  │ Final LLM     │  │
│  │ - Aggregate   │  │
│  │ - Synthesize  │  │
│  └───────────────┘  │
└──────┬──────────────┘
       │
       ▼
       END
```

**Flow:**
1. User provides query
2. Planner creates task plan
3. Router determines next agent (researcher/coder)
4. Agent executes task → updates state
5. Reviewer checks quality
6. Router decides: approve → next task, reject → revision
7. Synthesizer creates final output
8. Graph completes

---

## Key Differences: Medium vs Advanced

| Aspect | Medium Lab | Advanced Lab |
|--------|-----------|--------------|
| **Agents** | 2 (Researcher, Summarizer) | 4 (Planner, Researcher, Coder, Reviewer) |
| **Graph Complexity** | Linear (2 nodes) | Complex (5 nodes, conditional routing) |
| **State** | Simple (5 fields) | Complex (15+ fields, tasks, metadata) |
| **Routing** | Fixed edges | Conditional edges with logic |
| **Task Management** | None | Full task lifecycle tracking |
| **Work Products** | Single (research) | Multiple (research, code, reviews) |
| **Quality Control** | None | Reviewer agent with approval |
| **Checkpoints** | None | Optional state persistence |
| **Context Passing** | Basic | Advanced (aggregated context) |
| **Error Handling** | Basic | Structured (error tracking) |
| **Observability** | Minimal | Agent history, error logs |

---

## Teaching Progression

### Step 1: Understanding LangGraph Basics (Medium Lab)
1. **State Definition:** Show how TypedDict defines shared state
2. **Node Functions:** Explain node signature and state handling
3. **Graph Construction:** Build simple linear graph
4. **Execution:** Run graph and observe state flow

### Step 2: Building Multi-Agent Systems (Advanced Lab)
1. **Task Decomposition:** How planner breaks down queries
2. **Agent Specialization:** Different agents for different tasks
3. **Conditional Routing:** Dynamic flow based on state
4. **Quality Control:** Review and feedback loops

### Step 3: Advanced Features
1. **Checkpoints:** State persistence and resumability
2. **Context Management:** Aggregating context for agents
3. **Error Handling:** Structured error tracking
4. **Observability:** Agent history and monitoring

---

## Common Student Questions & Answers

### Q1: What's the difference between LangChain chains and LangGraph?
**A:** 
- **Chains:** Linear, sequential execution
- **Graphs:** Support branching, loops, conditional routing, complex workflows

### Q2: Why use `Annotated` with `operator.add`?
**A:** 
- Allows nodes to append to lists without overwriting
- LangGraph uses this to accumulate messages/work products
- Without it, each node would replace the entire list

### Q3: How does conditional routing work?
**A:** 
- Routing function receives state
- Returns next node name as string
- Graph uses this to determine which edge to follow
- Enables dynamic workflows based on state

### Q4: What are checkpoints used for?
**A:** 
- State persistence across executions
- Resumable workflows
- Debugging (inspect state at any point)
- Human-in-the-loop (pause and resume)

### Q5: How do agents share context?
**A:** 
- State is shared across all nodes
- Each agent reads relevant state fields
- Agents write results to state
- Context builder aggregates relevant information

---

## Summary: Module Organization

### Day 2 Medium Lab Structure
```
main.py                    → Main entry point, user interface
state.py                   → ResearchState TypedDict
agents/
  ├── researcher.py        → ResearcherAgent class
  └── summarizer.py        → SummarizerAgent class
graph/
  └── research_graph.py    → ResearchGraph class, LangGraph workflow
```

### Day 2 Advanced Lab Structure
```
main.py                    → Main entry point, user interface
state.py                   → MultiAgentState, Task, Enums
agents/
  ├── planner.py           → PlannerAgent class
  ├── researcher.py        → ResearcherAgent class
  ├── coder.py             → CoderAgent class
  └── reviewer.py          → ReviewerAgent class
graph/
  └── multi_agent_graph.py → MultiAgentGraph class, complex workflow
utils/
  └── routing.py           → RoutingLogic class, conditional routing
```

**Key Design Patterns:**
- **State Machine Pattern:** LangGraph implements state machine
- **Agent Pattern:** Specialized agents for different tasks
- **Routing Pattern:** Conditional edges enable dynamic flow
- **Checkpoint Pattern:** State persistence for resumability
- **Context Builder Pattern:** Aggregating relevant information

---

## Conclusion

The Day 2 labs progressively build from simple linear workflows to complex multi-agent systems with dynamic routing and quality control. Understanding these components provides the foundation for building production-ready multi-agent AI systems.

**Key Takeaways:**
1. **LangGraph** = Workflow orchestration engine
2. **State** = Shared data structure between agents
3. **Nodes** = Agent execution functions
4. **Routing** = Dynamic flow control
5. **Tasks** = Structured work units
6. **Checkpoints** = State persistence

Each component serves a specific purpose, and their integration creates powerful, collaborative AI agent systems.

