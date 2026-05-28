"""
MULTI-AGENT ORCHESTRATION TEMPLATE
==================================
Your starting point for building multi-agent systems!
Copy and customize for your needs.

+------------------------------------------------------------------+
|                    TEMPLATE ARCHITECTURE                         |
+------------------------------------------------------------------+
|                                                                    |
|   +------------------------+                                     |
|   | ORIGINAL REQUEST        |                                     |
|   +------------------------+                                     |
|              |                                                  |
|              v                                                  |
|   +------------------------+                                     |
|   | COORDINATOR             |  <-- Your orchestrator logic here   |
|   | - analyze_task()        |                                     |
|   | - build_context()       |                                     |
|   | - execute_agent()       |                                     |
|   | - orchestrate()         |                                     |
|   +------------------------+                                     |
|              |                                                  |
|              +---> Agent 1 (with context)                        |
|              +---> Agent 2 (with context)                        |
|              +---> Agent N (with context)                        |
|              |                                                  |
|              v                                                  |
|   +------------------------+                                     |
|   | AGGREGATE RESULTS        |                                     |
|   +------------------------+                                     |
|              |                                                  |
|              v                                                  |
|        FINAL OUTPUT                                              |
|                                                                    |
+------------------------------------------------------------------+

KEY CONCEPTS TO IMPLEMENT:
1. Hub-and-Spoke: All through coordinator
2. Dynamic Selection: Pick agents based on request
3. Scope Partitioning: Divide work clearly
4. Iterative Refinement: Check and improve quality
5. Explicit Context: Pass everything to each agent
"""

import os
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
from enum import Enum

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY", "")
api_base = os.getenv("ANTHROPIC_API_BASE", "")

from anthropic import Anthropic
client_kwargs = {"api_key": api_key} if api_key else {}
if api_base:
    client_kwargs["base_url"] = api_base
client = Anthropic(**client_kwargs)


# ============================================================================
# SECTION 1: AGENT DEFINITIONS
# ============================================================================
"""
DEFINE YOUR AGENT TYPES HERE

ASCII ART: Agent Definition Structure
======================================

+------------------------+
| AgentRole Enum         |
+------------------------+
| RESEARCHER = "researcher"
| ANALYST = "analyst"    |
| WRITER = "writer"      |
| ...                    |
+------------------------+

Each agent has:
- A role (from the enum)
- Keywords for dynamic selection
- A weight for scoring
- A specific task prompt
"""

class AgentRole(Enum):
    """
    Define your agent roles here.
    Customize these based on your use case.

    EXAMPLE ROLES:
    - RESEARCHER: Gathers information
    - ANALYST: Evaluates and compares
    - WRITER: Creates content
    - FACT_CHECKER: Verifies accuracy
    - EDITOR: Revises and polishes
    """
    RESEARCHER = "researcher"
    ANALYST = "analyst"
    WRITER = "writer"
    # Add more roles as needed based on your use case


# ============================================================================
# SECTION 2: CONTEXT BUILDER
# ============================================================================
"""
BUILD COMPLETE CONTEXT FOR EACH AGENT CALL

ASCII ART: Context Building
============================

+------------------------+
| ORIGINAL REQUEST       |  (always required)
+------------------------+
           |
+----------+-----------+
|                      |
v                      v
+--------+      +--------+
| STYLE  |      | RESULTS|  (previous agent outputs)
+--------+      +--------+
|                      |
+----------+-----------+
           |
           v
+------------------------+
| COMPLETE CONTEXT       |
| (pass to next agent)   |
+------------------------+
"""

def build_context(
    original_request: str,
    style_requirements: Optional[Dict] = None,
    previous_results: Optional[Dict] = None,
    constraints: Optional[List[str]] = None
) -> str:
    """
    Build COMPLETE context for an agent.

    This function ensures every agent receives everything it needs:
    - Original request (so agent knows the goal)
    - Style requirements (format, tone, audience)
    - Previous results (so agent can build upon prior work)
    - Constraints (length limits, what to avoid)

    ARGUMENTS:
        original_request: The user's original request
        style_requirements: Dict with format, audience, tone, etc.
        previous_results: Dict of {agent_name: output}
        constraints: List of constraint strings

    RETURNS:
        Complete context string to pass to agent

    MISTAKE TO AVOID:
        Don't pass partial context! Every piece is important.
    """
    parts = []

    # Always include original request
    parts.append("=" * 60)
    parts.append("ORIGINAL REQUEST")
    parts.append("=" * 60)
    parts.append(original_request)

    # Style requirements
    if style_requirements:
        parts.append("\n" + "=" * 60)
        parts.append("STYLE REQUIREMENTS")
        parts.append("=" * 60)
        for key, value in style_requirements.items():
            parts.append(f"  * {key}: {value}")

    # Previous results from other agents
    if previous_results:
        parts.append("\n" + "=" * 60)
        parts.append("PREVIOUS WORK (build upon this)")
        parts.append("=" * 60)
        for agent_name, result in previous_results.items():
            parts.append(f"\n--- {agent_name.upper()} ---\n{result[:2000]}")

    # Constraints
    if constraints:
        parts.append("\n" + "=" * 60)
        parts.append("CONSTRAINTS")
        parts.append("=" * 60)
        for constraint in constraints:
            parts.append(f"  * {constraint}")

    return "\n".join(parts)


# ============================================================================
# SECTION 3: AGENT IMPLEMENTATIONS
# ============================================================================
"""
IMPLEMENT YOUR AGENTS HERE

ASCII ART: Agent Implementation
================================

+------------------------+
| call_agent()           |
+------------------------+
| Input: role, context   |
|       task, additional |
+------------------------+
|                        |
| Build complete prompt |
| Call LLM with context |
| Return response       |
+------------------------+
"""

def call_agent(
    role: AgentRole,
    context: str,
    task: str,
    additional_info: Optional[str] = None
) -> str:
    """
    Call a specialized agent with complete context!

    This is the core agent execution function. It:
    1. Builds a complete prompt with context
    2. Calls the LLM with the prompt
    3. Returns the agent's response

    ARGUMENTS:
        role: The agent role (determines base prompt)
        context: Complete context string
        task: Specific task for this agent
        additional_info: Any extra information

    RETURNS:
        Agent's response text
    """

    # Build the prompt with complete context
    prompt = f"""You are a {role.value} specialist.

{'='*60}
COMPLETE CONTEXT
{'='*60}
{context}
{'='*60}

TASK:
{task}
"""

    if additional_info:
        prompt += f"\n\nADDITIONAL INFORMATION:\n{additional_info}"

    response = client.messages.create(
        model="claude-haiku-4-5-20250601",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
        tools=[]
    )

    return response.content[0].text


# ============================================================================
# SECTION 4: COORDINATOR CLASS
# ============================================================================
"""
THE MAIN ORCHESTRATOR CLASS

ASCII ART: Coordinator Structure
================================

+------------------------+
| MultiAgentCoordinator  |
+------------------------+
| __init__()             |  Initialize agents, settings
| analyze_task()          |  Parse request, select agents
| build_context()         |  Assemble complete context
| execute_agent()         |  Run a single agent
| orchestrate()           |  Main orchestration loop
+------------------------+
"""

class MultiAgentCoordinator:
    """
    Template for a multi-agent coordinator.
    Customize this for your specific use case!

    USAGE:
        coordinator = MultiAgentCoordinator()
        result = coordinator.orchestrate("Your request here")

    CUSTOMIZATION POINTS:
        - Add/modify agent roles
        - Customize selection logic
        - Adjust quality thresholds
        - Add monitoring/logging
    """

    def __init__(self):
        self.agents = {}
        self.quality_threshold = 85
        self.max_iterations = 3
        print("Multi-Agent Coordinator initialized")
        print(f"   Quality threshold: {self.quality_threshold}/100")
        print(f"   Max iterations: {self.max_iterations}")

    def analyze_and_select_agents(self, request: str) -> List[AgentRole]:
        """
        Decide which agents are needed for this request.

        IMPLEMENTATION GUIDE:
        1. Define keywords for each agent role
        2. Score request against each role
        3. Select roles above threshold
        4. Return list of selected roles

        CUSTOMIZE THIS for your use case!
        """
        needed = []

        # EXAMPLE: Keyword-based selection
        # Customize these based on your agent definitions

        if any(word in request.lower() for word in ["what is", "explain", "research",
                                                     "information", "find", "tell me"]):
            needed.append(AgentRole.RESEARCHER)

        if any(word in request.lower() for word in ["compare", "analyze", "evaluate",
                                                     "assess", "difference", "pros", "cons"]):
            needed.append(AgentRole.ANALYST)

        if any(word in request.lower() for word in ["write", "report", "create",
                                                     "document", "article", "draft"]):
            needed.append(AgentRole.WRITER)

        # Default if nothing matched
        if not needed:
            needed.append(AgentRole.RESEARCHER)
            print(f"   (defaulting to Researcher)")

        print(f"   Selected agents: {[a.value for a in needed]}")
        return needed

    def build_context(
        self,
        request: str,
        style_requirements: Optional[Dict] = None,
        previous_results: Optional[Dict] = None
    ) -> str:
        """
        Build complete context for an agent.
        Delegates to the build_context() function above.
        """
        return build_context(
            original_request=request,
            style_requirements=style_requirements,
            previous_results=previous_results
        )

    def execute_agent(
        self,
        role: AgentRole,
        context: str,
        task: str
    ) -> str:
        """
        Execute a single agent.
        """
        print(f"   [COORDINATOR] Calling {role.value} agent...")

        result = call_agent(role, context, task)

        print(f"   [{role.value.upper()}] Complete! ({len(result)} chars)")
        return result

    def get_task_for_role(self, role: AgentRole) -> str:
        """
        Return the task description for each role.
        Customize these for your use case!

        ASCII ART: Task Mapping
        ======================

        +------------------------+
        | Role          | Task  |
        +------------------------+
        | RESEARCHER    | "..." |
        | ANALYST      | "..." |
        | WRITER       | "..." |
        +------------------------+
        """
        tasks = {
            AgentRole.RESEARCHER: "Research the topic thoroughly. Provide key facts, data, and insights. Be accurate and comprehensive.",
            AgentRole.ANALYST: "Analyze the provided information. Make comparisons where relevant. Provide clear insights and recommendations.",
            AgentRole.WRITER: "Create a well-structured, engaging final output based on all the provided information."
        }
        return tasks.get(role, "Process the information as needed.")

    def orchestrate(
        self,
        request: str,
        style_requirements: Optional[Dict] = None,
        constraints: Optional[List[str]] = None
    ) -> str:
        """
        Main orchestration method!

        ASCII ART: Orchestration Flow
        ============================

        +------------------------+
        | START: Request          |
        +------------------------+
                   |
                   v
        +------------------------+
        | ANALYZE: Select agents  |
        +------------------------+
                   |
                   v
        +------------------------+
        | EXECUTE: Run each agent |
        | (with full context)    |
        +------------------------+
                   |
                   v
        +------------------------+
        | AGGREGATE: Combine     |
        +------------------------+
                   |
                   v
        +------------------------+
        | END: Final output      |
        +------------------------+

        ARGUMENTS:
            request: The user's original request
            style_requirements: Dict with format, audience, etc.
            constraints: List of constraint strings

        RETURNS:
            Final orchestrated output
        """
        print(f"\n{'='*60}")
        print(f"[COORDINATOR] Starting orchestration")
        print(f"   Request: {request[:50]}...")
        print('='*60)

        # Step 1: Analyze and select agents (Dynamic Selection)
        agents_needed = self.analyze_and_select_agents(request)

        # Step 2: Execute agents in sequence
        results = {}
        context = request

        for agent_role in agents_needed:
            # Build complete context for this agent
            full_context = self.build_context(
                request=request,
                style_requirements=style_requirements,
                previous_results=results if results else None
            )

            # Get task for this role
            task = self.get_task_for_role(agent_role)

            # Execute the agent
            result = self.execute_agent(agent_role, full_context, task)

            # Store result with capitalized name
            results[agent_role.value.title()] = result

        # Step 3: Return final result
        # Priority: Writer > Analyst > Researcher
        final = (
            results.get("Writer") or
            results.get("Analyst") or
            results.get("Researcher") or
            "No result generated"
        )

        print(f"\n[COORDINATOR] Orchestration complete!")
        print(f"   Agents used: {list(results.keys())}")

        return final


# ============================================================================
# SECTION 5: CUSTOMIZATION HELPERS
# ============================================================================
"""
HELPER FUNCTIONS FOR COMMON CUSTOMIZATIONS

These are optional utilities you can use or modify.
"""

def create_style_requirements(
    audience: str = "general",
    format_type: str = "plain text",
    length: str = "medium",
    tone: str = "neutral"
) -> Dict[str, str]:
    """
    Create a standard style requirements dictionary.

    USAGE:
        style = create_style_requirements(
            audience="technical",
            format_type="report",
            length="800-1000 words",
            tone="professional"
        )
    """
    return {
        "Audience": audience,
        "Format": format_type,
        "Length": length,
        "Tone": tone
    }


def create_constraints(
    must_include: Optional[List[str]] = None,
    must_avoid: Optional[List[str]] = None,
    max_length: Optional[int] = None
) -> List[str]:
    """
    Create a standard constraints list.

    USAGE:
        constraints = create_constraints(
            must_include=["examples", "data"],
            must_avoid=["jargon", "complex math"],
            max_length=1000
        )
    """
    constraints = []

    if must_include:
        constraints.append(f"Include: {', '.join(must_include)}")

    if must_avoid:
        constraints.append(f"Avoid: {', '.join(must_avoid)}")

    if max_length:
        constraints.append(f"Maximum length: {max_length} words")

    return constraints


# ============================================================================
# WHAT WE HAVE LEARNT
# ============================================================================
"""
=============================================================================
WHAT WE HAVE LEARNT: Multi-Agent Orchestration Template
=============================================================================

1. TEMPLATE STRUCTURE
   ------------------

   +------------------------+     +------------------------+
   | SECTION 1             | --> | Agent Definitions      |
   | AgentRole Enum        |     | Define your agents     |
   +------------------------+     +------------------------+
   | SECTION 2             | --> | Context Builder        |
   | build_context()       |     | Assemble full context  |
   +------------------------+     +------------------------+
   | SECTION 3             | --> | Agent Implementation   |
   | call_agent()          |     | Execute with context   |
   +------------------------+     +------------------------+
   | SECTION 4             | --> | Coordinator Class     |
   | MultiAgentCoordinator |     | Main orchestrator      |
   +------------------------+     +------------------------+
   | SECTION 5             | --> | Customization Helpers  |
   | Helper functions      |     | Reusable utilities     |
   +------------------------+     +------------------------+

2. KEY CUSTOMIZATION POINTS
   -------------------------

   | Point              | What to Customize               |
   |--------------------|----------------------------------|
   | AgentRole Enum     | Add roles for your use case      |
   | Selection Logic    | Keywords and scoring for agents   |
   | Task Prompts       | What each agent is asked to do   |
   | Quality Threshold  | Pass/fail score for outputs       |
   | Max Iterations     | How many refinement cycles       |

3. COMMON CUSTOMIZATIONS
   ---------------------

   ADD A NEW AGENT:
   1. Add to AgentRole enum: ANALYST = "analyst"
   2. Add task in get_task_for_role()
   3. Add keywords in analyze_and_select_agents()

   CHANGE SELECTION LOGIC:
   - Modify keywords in analyze_and_select_agents()
   - Adjust scoring threshold
   - Add new selection criteria

   CHANGE OUTPUT FORMAT:
   - Modify build_context() structure
   - Update task prompts
   - Add format-specific instructions

4. BEST PRACTICES
   ---------------

   ALWAYS:
   - Build complete context (don't skip parts)
   - Log agent selection decisions
   - Track execution time and costs
   - Handle failures gracefully

   NEVER:
   - Hardcode agent sequences (use dynamic selection)
   - Pass partial context to agents
   - Skip quality evaluation (use iterative refinement)
   - Ignore errors and continue silently

5. INTERVIEW ANSWER FRAMEWORK
   --------------------------

   "How do you use this template in production?"

   Step 1: Explain the structure
   "The template has 5 main sections: agent definitions, context
    builder, agent implementations, coordinator class, and helpers."

   Step 2: Describe customization
   "You customize the AgentRole enum for your use case, modify
    the selection logic, and adjust task prompts."

   Step 3: Show how it combines patterns
   "The coordinator uses dynamic selection to pick agents, builds
    explicit context for each, and can use iterative refinement
    for quality control."

   Step 4: Address flexibility
   "It's a starting point - you can add monitoring, caching,
    error handling, and other production features as needed."

6. EXTENDING THE TEMPLATE
   -----------------------

   For production use, consider adding:

   +------------------------+--------------------------------+
   | Feature                | Implementation                 |
   +------------------------+--------------------------------+
   | Logging                | Add to execute_agent()          |
   | Caching                | Store results, check before call |
   | Retry Logic           | Wrap call_agent() in retry loop |
   | Metrics                | Track tokens, latency, errors   |
   | Fallback Agents        | Define alternatives for each     |
   | Async Execution       | Use asyncio for parallelism    |
   | Timeout Handling      | Add timeout to API calls        |
   +------------------------+--------------------------------+

=============================================================================
"""


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    print("\n" + "="*60)
    print("MULTI-AGENT ORCHESTRATION TEMPLATE")
    print("="*60)
    print("""
+------------------------------------------------------------------+
|                    TEMPLATE ARCHITECTURE                         |
+------------------------------------------------------------------+
|                                                                    |
|   +------------------------+                                     |
|   | ORIGINAL REQUEST        |                                     |
|   +------------------------+                                     |
|              |                                                  |
|              v                                                  |
|   +------------------------+                                     |
|   | COORDINATOR             |  <-- Your orchestrator logic here   |
|   +------------------------+                                     |
|              |                                                  |
|              +---> Agent 1 (with context)                        |
|              +---> Agent 2 (with context)                        |
|              +---> Agent N (with context)                        |
|              |                                                  |
|              v                                                  |
|   +------------------------+                                     |
|   | AGGREGATE RESULTS        |                                     |
|   +------------------------+                                     |
|              |                                                  |
|              v                                                  |
|        FINAL OUTPUT                                              |
|                                                                    |
+------------------------------------------------------------------+

HOW TO USE THIS TEMPLATE:
========================

1. Customize AgentRole enum with your roles
2. Modify selection logic in analyze_and_select_agents()
3. Adjust task prompts in get_task_for_role()
4. Add any additional helper functions
5. Instantiate MultiAgentCoordinator and call orchestrate()

    """)

    # Create coordinator
    coordinator = MultiAgentCoordinator()

    # Process a request
    request = "What is machine learning? Write a brief explanation."

    print(f"\n{'='*60}")
    print(f"EXAMPLE REQUEST: {request}")
    print(f"{'='*60}\n")

    result = coordinator.orchestrate(
        request=request,
        style_requirements=create_style_requirements(
            audience="beginners",
            format_type="educational article",
            length="500-700 words",
            tone="friendly and informative"
        ),
        constraints=create_constraints(
            must_include=["real-world examples", "simple explanation"],
            must_avoid=["technical jargon", "complex equations"]
        )
    )

    print("\n" + "-"*60)
    print("RESULT:")
    print("-"*60)
    print(result[:500] + ("..." if len(result) > 500 else ""))

    print("\n" + "="*60)
    print("TEMPLATE COMPLETE")
    print("="*60)
    print("""
NEXT STEPS:
===========

1. Customize the AgentRole enum for your use case
2. Modify agent selection logic
3. Adjust task prompts and context building
4. Add production features (logging, caching, etc.)

See WHAT WE HAVE LEARNT section for detailed customization guide.
""")