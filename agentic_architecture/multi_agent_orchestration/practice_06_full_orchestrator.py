"""
PRACTICE 6: FULL MULTI-AGENT ORCHESTRATOR
=========================================
Putting it all together - the complete orchestrator!

+------------------------------------------------------------------+
|                  FULL ORCHESTRATION ARCHITECTURE                  |
+------------------------------------------------------------------+
|                                                                    |
|   User Request                                                      |
|        |                                                           |
|        v                                                           |
|   +------------------------------------------------------------+   |
|   |                    COORDINATOR                               |   |
|   |  +------------------+  +------------------+                  |   |
|   |  | Task Analyzer     |  | Agent Selector    |                  |   |
|   |  +------------------+  +------------------+                  |   |
|   |  | Context Builder   |  | Quality Controller |                  |   |
|   |  +------------------+  +------------------+                  |   |
|   +------------------------------------------------------------+   |
|        |                                                           |
|        v                                                           |
|   +------------------------------------------------------------+   |
|   |                    AGENT EXECUTION                           |   |
|   |                                                            |   |
|   |  +-----------+  +-----------+  +-----------+  +-----------+ |   |
|   |  |RESEARCHER|->| ANALYST   |->| WRITER    |->|FACT CHECK | |   |
|   |  +-----------+  +-----------+  +-----------+  +-----------+ |   |
|   |       |              |              |              |       |   |
|   |       v              v              v              v       |   |
|   |   [Research]     [Analysis]      [Draft]       [Verify]   |   |
|   +------------------------------------------------------------+   |
|        |                                                           |
|        v                                                           |
|   +------------------------------------------------------------+   |
|   |                    RESULT AGGREGATION                        |   |
|   +------------------------------------------------------------+   |
|        |                                                           |
|        v                                                           |
|      OUTPUT                                                        |
|                                                                    |
+------------------------------------------------------------------+

KEY CONCEPT: All five patterns work together in production:
1. Hub-and-Spoke: All communication through coordinator
2. Dynamic Selection: Appropriate agents selected per request
3. Scope Partitioning: Work divided by agent capabilities
4. Iterative Refinement: Quality checked and improved
5. Explicit Context: Complete info passed to each agent
"""

import os
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
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
# PATTERN 1: HUB-AND-SPOKE COORDINATOR
# ============================================================================
"""
Hub-and-Spoke means:
- Coordinator is the single point of control
- All agents communicate through coordinator
- No direct agent-to-agent communication
- Coordinator maintains orchestration state
"""

# ============================================================================
# PATTERN 2: DYNAMIC AGENT SELECTION
# ============================================================================
"""
Dynamic Selection means:
- Analyze request to determine needed agents
- Score each agent type based on request content
- Select agents above confidence threshold
- Multi-intent requests select multiple agents
"""


# ============================================================================
# REAL-TIME SCENARIO: Enterprise Report Generation
# ============================================================================
"""
PRODUCTION SCENARIO: Quarterly Business Report

A CEO needs a quarterly report. The orchestrator must:

Step 1: ANALYZE REQUEST
- "Generate Q3 2024 business report for board presentation"
- Detect: Research (financial data), Analyst (metrics), Writer (format)

Step 2: DYNAMIC SELECTION
- Select: Researcher, Analyst, Writer (based on request)
- Skip: Calculator (no math detected), Fact Checker (not explicit)

Step 3: SCOPE PARTITIONING
- Researcher scopes: Revenue, Expenses, Growth metrics
- Each scope is independent, no overlap

Step 4: ITERATIVE REFINEMENT
- Writer drafts -> Check quality -> Refine if needed
- Quality threshold: 85/100 for board-level content

Step 5: EXPLICIT CONTEXT
- Each agent gets: original request + previous outputs + constraints
- Writer knows: "For board presentation, executive summary first"

Output: Polished report ready for C-suite presentation
"""


# ============================================================================
# AGENT DEFINITIONS
# ============================================================================

class AgentRole(Enum):
    """
    Roles available in the orchestration system.

    ASCII ART: Agent Registry
    =========================

    +----------------+----------------+----------------+----------------+
    | COORDINATOR    | RESEARCHER     | ANALYST        | WRITER         |
    | [Orchestrate]  | [Gather Info] | [Evaluate]     | [Create Output] |
    +----------------+----------------+----------------+----------------+
    |                |                |                |                |
    | FACT_CHECKER   |                |                |                |
    | [Verify Truth] |                |                |                |
    +----------------+----------------+----------------+----------------+

    Each agent has a specific role. Coordinator selects based on request.
    """
    COORDINATOR = "coordinator"
    RESEARCHER = "researcher"
    ANALYST = "analyst"
    WRITER = "writer"
    FACT_CHECKER = "fact_checker"


@dataclass
class Agent:
    """
    Represents an agent in the system.

    ASCII ART: Agent Structure
    ==========================

    +------------------------+
    | Agent: {name}          |
    +------------------------+
    | Role: {role.value}      |
    | Description: {desc}    |
    | Capabilities:          |
    |   - {cap1}             |
    |   - {cap2}             |
    +------------------------+
    """
    role: AgentRole
    name: str
    description: str
    capabilities: List[str]

    # Scoring weights for dynamic selection
    keywords: List[str] = field(default_factory=list)
    weight: float = 1.0


# Define available agents with scoring info
AVAILABLE_AGENTS = [
    Agent(
        role=AgentRole.RESEARCHER,
        name="Researcher",
        description="Gathers information and data from various sources",
        capabilities=["web_search", "data_analysis", "fact_finding"],
        keywords=["what is", "explain", "information", "research", "find",
                  "gather", "tell me about", "describe", "definition"],
        weight=1.0
    ),
    Agent(
        role=AgentRole.ANALYST,
        name="Analyst",
        description="Evaluates data, compares options, provides insights",
        capabilities=["comparison", "evaluation", "trend_analysis"],
        keywords=["compare", "versus", "vs", "analyze", "evaluate", "assess",
                  "recommend", "better", "worse", "difference", "pros", "cons"],
        weight=1.2
    ),
    Agent(
        role=AgentRole.WRITER,
        name="Writer",
        description="Creates clear, well-structured content",
        capabilities=["technical_writing", "creative_writing", "editing"],
        keywords=["write", "report", "create", "document", "article", "draft",
                  "compose", "summary", "explain to"],
        weight=1.0
    ),
    Agent(
        role=AgentRole.FACT_CHECKER,
        name="Fact Checker",
        description="Verifies accuracy of claims and data",
        capabilities=["verification", "cross_reference", "accuracy_check"],
        keywords=["verify", "fact check", "confirm", "validate", "accuracy",
                  "true", "false", "correct", "reliable"],
        weight=0.8
    )
]


# ============================================================================
# MISTAKE #1: Hardcoded Pipeline (Ignoring Dynamic Selection)
# ============================================================================
"""
COMMON ERROR: Always using the same agents regardless of request

    # WRONG - hardcoded
    def orchestrate(request):
        agents = [RESEARCHER, ANALYST, WRITER, FACT_CHECKER]
        # Always uses all 4, even for simple requests

WHY THIS BREAKS:
- Wasteful for simple requests
- Too slow for time-sensitive tasks
- Cost inefficient
- Over-engineered for basic needs

CORRECT APPROACH:
    def orchestrate(request):
        agents = select_agents(request)  # Dynamic based on content
        # Only uses what's needed
"""


# ============================================================================
# MISTAKE #2: No Quality Gates (Skip Iterative Refinement)
# ============================================================================
"""
COMMON ERROR: Trusting first output without evaluation

    content = writer_agent(request, context)
    return content  # No quality check!

WHY THIS BREAKS:
- Inconsistent output quality
- May contain errors or gaps
- No improvement mechanism
- User gets unpredictable results

CORRECT APPROACH:
    content = writer_agent(request, context)
    evaluation = evaluator_agent(content)
    if evaluation['score'] < threshold:
        content = refine(content, evaluation)
    return content
"""


# ============================================================================
# MISTAKE #3: Poor Context Assembly (Broken Explicit Context)
# ============================================================================
"""
COMMON ERROR: Not building proper context for agents

    # WRONG - incomplete context
    prompt = f"Write about {topic}"
    # Missing: original request, style, constraints, previous work

WHY THIS BREAKS:
- Agent doesn't know full picture
- Output may contradict requirements
- Inconsistent format/style
- May miss critical information

CORRECT APPROACH:
    context = build_complete_context(
        user_request=original_request,
        style_requirements=style,
        previous_results=prior_outputs,
        constraints=limits
    )
"""


# ============================================================================
# INTERVIEW Q&A: Full Orchestration
# ============================================================================
"""
Q: How do all five patterns work together in production?
A: Each pattern addresses a specific aspect:

   1. HUB-AND-SPOKE: Provides the architecture
      "All agents communicate through a single coordinator.
       No direct agent-to-agent communication."

   2. DYNAMIC SELECTION: Handles request analysis
      "Based on the request content, we score each agent type
       and select only those that are relevant."

   3. SCOPE PARTITIONING: Divides the work
      "Each agent has a specific, non-overlapping scope.
       This prevents duplication and conflicts."

   4. ITERATIVE REFINEMENT: Ensures quality
      "Each output is evaluated. If quality is below threshold,
       we refine until it meets standards."

   5. EXPLICIT CONTEXT: Transfers information
      "Every agent call includes complete context:
       original request, previous outputs, requirements."

Q: How do you handle failures in the orchestration pipeline?
A: Several strategies:

   1. FAULT ISOLATION
   - If one agent fails, don't fail entire pipeline
   - Log failure, continue with remaining agents
   - Return partial result with error explanation

   2. RETRY LOGIC
   - Each agent call has max_retries
   - Exponential backoff between retries
   - Circuit breaker for repeated failures

   3. FALLBACK AGENTS
   - If preferred agent unavailable, use fallback
   - Researcher unavailable? Use cached data + flag

   4. DEAD LETTER QUEUE
   - Failed tasks go to DLQ for manual review
   - Alert on DLQ size spikes
   - Regular triage of failed requests

Q: How do you optimize for cost in multi-agent systems?
A: Cost optimization strategies:

   1. MINIMIZE AGENT COUNT
   - Only use agents that are actually needed
   - Simple request = 1 agent, complex = multiple

   2. LIMIT ITERATIONS
   - Set MAX_ITERATIONS based on request value
   - High-value output = more iterations
   - Low-value = fewer iterations or skip refinement

   3. CACHE COMMON CONTEXT
   - Store frequently used context pieces
   - Reuse without regenerating each time

   4. USE CHEAPER MODELS FOR SIMPLE TASKS
   - Haiku for straightforward generation
   - Opus/Sonnet only for complex reasoning
   - Route based on task complexity
"""


# ============================================================================
# COORDINATOR CLASS
# ============================================================================

class MultiAgentCoordinator:
    """
    The complete orchestrator combining all patterns!

    ASCII ART: Coordinator Components
    =================================

    +------------------------------------------+
    |           MULTI-AGENT COORDINATOR        |
    +------------------------------------------+
    |                                          |
    |  +------------------------------------+  |
    |  | Task Analyzer                       |  |
    |  | - Parse request                    |  |
    |  | - Extract requirements             |  |
    |  +------------------------------------+  |
    |                |                        |
    |  +------------------------------------+  |
    |  | Agent Selector (Dynamic)           |  |
    |  | - Score each agent type           |  |
    |  | - Select based on confidence      |  |
    |  +------------------------------------+  |
    |                |                        |
    |  +------------------------------------+  |
    |  | Context Builder (Explicit)         |  |
    |  | - Assemble complete context       |  |
    |  | - Include all prior work         |  |
    |  +------------------------------------+  |
    |                |                        |
    |  +------------------------------------+  |
    |  | Quality Controller (Iterative)    |  |
    |  | - Evaluate each output            |  |
    |  | - Trigger refinement if needed    |  |
    |  +------------------------------------+  |
    |                |                        |
    |  +------------------------------------+  |
    |  | Execution Engine                   |  |
    |  | - Run selected agents in order    |  |
    |  | - Manage dependencies             |  |
    |  +------------------------------------+  |
    |                                          |
    +------------------------------------------+
    """

    def __init__(self):
        self.agents = AVAILABLE_AGENTS
        self.conversation_history = []
        self.quality_threshold = 85
        self.max_iterations = 3
        print("Multi-Agent Coordinator initialized")
        print(f"   Available agents: {[a.name for a in self.agents]}")
        print(f"   Quality threshold: {self.quality_threshold}/100")
        print(f"   Max iterations: {self.max_iterations}\n")

    # ========================================================================
    # PATTERN 2: DYNAMIC AGENT SELECTION
    # ========================================================================

    def analyze_task(self, request: str) -> Dict[str, Any]:
        """
        Analyze the request and decide how to handle it!

        ASCII ART: Task Analysis
        =======================

        +------------------+
        | User Request     |
        +------------------+
              |
              v
        +------------------+
        | Keyword Matching |  <-- Score each agent type
        +------------------+
              |
              +----> Researcher: 2 matches (score: 2.0)
              +----> Analyst: 1 match (score: 1.2)
              +----> Writer: 1 match (score: 1.0)
              +----> Fact Checker: 0 matches (score: 0.0)
              |
              v
        +------------------+
        | Select Above     |  <-- Threshold-based selection
        | Threshold        |
        +------------------+
              |
              v
        +------------------+
        | [Researcher,     |
        |  Analyst, Writer] |
        +------------------+

        """
        print(f"\n{'='*60}")
        print(f"[COORDINATOR] Analyzing task...")
        print(f"   Request: {request[:80]}...")
        print('='*60)

        # Score each agent based on request content
        scores = {}
        selected_agents = []

        request_lower = request.lower()

        for agent in self.agents:
            score = 0
            for keyword in agent.keywords:
                if keyword in request_lower:
                    score += agent.weight

            scores[agent.role] = score
            print(f"   {agent.name}: score={score:.1f}, keywords matched")

            # Select if score >= 0.5 (at least one keyword hit)
            if score >= 0.5:
                selected_agents.append(agent.role)

        # Always include Writer if content requested
        if any(kw in request_lower for kw in ["write", "report", "create", "article"]):
            if AgentRole.WRITER not in selected_agents:
                selected_agents.append(AgentRole.WRITER)
                print(f"   Writer: added (content requested)")

        # Default to Researcher if nothing selected
        if not selected_agents:
            selected_agents.append(AgentRole.RESEARCHER)
            print(f"   (defaulted to Researcher)")

        print(f"\n   Selected agents: {[a.value for a in selected_agents]}")

        return {
            "agents": selected_agents,
            "scores": scores,
            "original_request": request
        }

    # ========================================================================
    # PATTERN 5: EXPLICIT CONTEXT PASSING
    # ========================================================================

    def build_context(
        self,
        request: str,
        agent_role: AgentRole,
        previous_results: Optional[Dict] = None,
        style_requirements: Optional[Dict] = None,
        constraints: Optional[Dict] = None
    ) -> str:
        """
        Build COMPLETE context for a subagent!

        ASCII ART: Context Assembly
        ==========================

        +------------------------+
        | ORIGINAL REQUEST       |  (always included)
        +------------------------+
                   |
        +----------+----------+
        |                    |
        v                    v
    +--------+          +--------+
    | PREV   |          | STYLE  |
    | RESULTS|          | REQ'S  |
    +--------+          +--------+
        |                    |
        +-------+------------+
                |
                v
        +------------------------+
        | COMPLETE CONTEXT STRING |
        +------------------------+

        """
        context_parts = []

        # Original request (always included!)
        context_parts.append("=" * 60)
        context_parts.append("ORIGINAL REQUEST")
        context_parts.append("=" * 60)
        context_parts.append(request)

        # Agent role and scope
        context_parts.append("\n" + "=" * 60)
        context_parts.append(f"YOUR ROLE: {agent_role.value.upper()}")
        context_parts.append("=" * 60)

        # Find agent info
        for agent in self.agents:
            if agent.role == agent_role:
                context_parts.append(f"Agent: {agent.name}")
                context_parts.append(f"Description: {agent.description}")
                break

        # Style requirements
        if style_requirements:
            context_parts.append("\n" + "=" * 60)
            context_parts.append("STYLE REQUIREMENTS")
            context_parts.append("=" * 60)
            for key, value in style_requirements.items():
                context_parts.append(f"* {key}: {value}")

        # Previous results (if any)
        if previous_results:
            context_parts.append("\n" + "=" * 60)
            context_parts.append("PREVIOUS AGENTS' WORK")
            context_parts.append("=" * 60)
            for agent_name, result in previous_results.items():
                context_parts.append(f"\n--- {agent_name.upper()} ---\n{result[:1500]}")

        # Constraints
        if constraints:
            context_parts.append("\n" + "=" * 60)
            context_parts.append("CONSTRAINTS")
            context_parts.append("=" * 60)
            for key, value in constraints.items():
                context_parts.append(f"* {key}: {value}")

        return "\n".join(context_parts)

    # ========================================================================
    # AGENT EXECUTION
    # ========================================================================

    def execute_agent(
        self,
        agent_role: AgentRole,
        context: str,
        task_specifics: Optional[str] = None
    ) -> str:
        """
        Execute a specific agent with complete context!
        """

        agent_name = agent_role.value.replace("_", " ").title()

        print(f"\n{'='*50}")
        print(f"[COORDINATOR] Calling {agent_name} agent...")
        print(f"{'='*50}")

        # Build the prompt based on role
        prompts = {
            AgentRole.RESEARCHER: f"""You are a research specialist.

{context}

TASK:
Research thoroughly based on the original request.
Provide structured findings with key facts, data, and insights.
Be accurate and comprehensive.

Format as:
1. Main findings (3-5 points)
2. Supporting details
3. Important data or statistics
4. Any limitations or caveats""",

            AgentRole.ANALYST: f"""You are an analysis specialist.

{context}

TASK:
Analyze the provided information.
Make comparisons where relevant.
Provide clear insights and recommendations.

Format as:
1. Key observations
2. Comparisons (if applicable)
3. Insights
4. Recommendations (if applicable)""",

            AgentRole.WRITER: f"""You are a professional writer.

{context}

TASK:
Create a well-structured, engaging output based on all the provided information.
Follow any style requirements specified.
Make sure to incorporate all relevant details from previous work.

Produce the final polished output.""",

            AgentRole.FACT_CHECKER: f"""You are a fact-checking specialist.

{context}

TASK:
Verify the accuracy of claims made.
Identify any potential errors or misleading information.
Cross-reference with known facts.

Return a verification report with:
1. Verified claims (with evidence)
2. Questionable claims (flagged for review)
3. Overall accuracy rating"""
        }

        prompt = prompts.get(agent_role, "Process this information:\n\n" + context)

        if task_specifics:
            prompt += f"\n\nSPECIFIC TASK:\n{task_specifics}"

        response = client.messages.create(
            model="claude-haiku-4-5-20250601",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
            tools=[]
        )

        result = response.content[0].text
        print(f"   [{agent_name.upper()}] Complete! ({len(result)} chars)")
        return result

    # ========================================================================
    # PATTERN 4: ITERATIVE REFINEMENT (Quality Gate)
    # ========================================================================

    def evaluate_output(self, content: str, request: str) -> Dict[str, Any]:
        """
        Evaluate output quality (Iterative Refinement step)

        ASCII ART: Quality Evaluation
        ============================

        +------------------+
        | Content to       |
        | Evaluate          |
        +------------------+
              |
              v
        +------------------+
        | Heuristic Checks  |
        | - Length?         |
        | - Structure?      |
        | - Keywords?       |
        +------------------+
              |
              v
        +------------------+
        | Quality Score    |  0-100
        +------------------+
              |
              v
        +------------------+
        | Pass/Fail        |
        +------------------+

        """
        print(f"   [QUALITY] Evaluating output...")

        # Heuristic scoring (simplified for demo)
        score = 50  # Base score

        # Length contributes
        if len(content) > 500:
            score += 10
        if len(content) > 1000:
            score += 10
        if len(content) > 2000:
            score += 5

        # Structure indicators
        if "\n" in content:  # Has line breaks
            score += 5
        if any(marker in content for marker in ["1.", "2.", "- ", "* "]):
            score += 5  # Has list formatting

        # Completeness indicators
        if len(request.split()) > 5:  # Complex request
            if len(content) > 500:
                score += 5

        # Cap at 95
        score = min(score, 95)

        print(f"   [QUALITY] Score: {score}/100")

        return {
            "score": score,
            "pass": score >= self.quality_threshold,
            "gaps": "Content needs more detail" if score < 70 else None
        }

    # ========================================================================
    # MAIN ORCHESTRATION
    # ========================================================================

    def orchestrate(
        self,
        request: str,
        style_requirements: Optional[Dict] = None,
        constraints: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        The main orchestration method - combines all patterns!

        ASCII ART: Full Orchestration Flow
        ==================================

        Input: User Request
              |
              v
        +-----------------+
        | ANALYZE         |  <-- Dynamic Selection
        | (select agents) |
        +-----------------+
              |
              v
        +-----------------+
        | EXECUTE AGENTS  |  <-- Hub-and-Spoke
        | (in sequence)   |  <-- Explicit Context passed
        +-----------------+
              |
              v
        +-----------------+
        | EVALUATE        |  <-- Iterative Refinement
        | (check quality) |
        +-----------------+
              |
              v (if fail)
        +-----------------+
        | REFINE          |  <-- Loop back
        +-----------------+
              |
              v (if pass)
        +-----------------+
        | AGGREGATE       |  <-- Scope Partitioning
        | (combine output)|
        +-----------------+
              |
              v
        Output: Final Result

        """
        print("\n" + "="*60)
        print("FULL ORCHESTRATION STARTING")
        print("="*60)
        print(f"Request: {request[:60]}...")

        # Step 1: Analyze and select agents (Dynamic Selection)
        analysis = self.analyze_task(request)
        needed_agents = analysis["agents"]

        # Step 2: Execute agents in sequence (Hub-and-Spoke + Explicit Context)
        all_results = {}
        iteration = 0

        for agent_role in needed_agents:
            # Build complete context for this agent
            context = self.build_context(
                request=request,
                agent_role=agent_role,
                previous_results=all_results if all_results else None,
                style_requirements=style_requirements,
                constraints=constraints
            )

            # Execute the agent
            result = self.execute_agent(agent_role, context)
            agent_name = agent_role.value.replace("_", " ").title()
            all_results[agent_name] = result

            # Step 3: Quality check (Iterative Refinement)
            if agent_role == AgentRole.WRITER:  # Check final output quality
                evaluation = self.evaluate_output(result, request)
                if not evaluation['pass'] and iteration < self.max_iterations - 1:
                    print(f"\n   [QUALITY] Below threshold, would refine...")
                    iteration += 1

        # Step 4: Aggregate results (if multiple agents)
        final_result = self.aggregate_results(all_results)

        print("\n" + "="*60)
        print("ORCHESTRATION COMPLETE")
        print("="*60)
        print(f"   Agents used: {list(all_results.keys())}")
        print(f"   Total results: {len(all_results)}")
        print(f"   Final output length: {len(final_result)} chars")

        return {
            "final_output": final_result,
            "all_results": all_results,
            "agents_used": [a.value for a in needed_agents]
        }

    def aggregate_results(self, results: Dict[str, str]) -> str:
        """
        Combine results from multiple agents into final output.
        If only one result, return it directly.
        """
        if len(results) == 1:
            return list(results.values())[0]

        # Multiple agents - return the writer's output if available
        if "Writer" in results:
            return results["Writer"]
        elif "Analyst" in results:
            return results["Analyst"]
        elif "Researcher" in results:
            return results["Researcher"]
        else:
            # Fallback to first result
            return list(results.values())[0]


# ============================================================================
# DEMONSTRATION
# ============================================================================

def demonstrate_orchestration():
    """
    Show the full orchestrator in action.
    """
    print("\n" + "="*60)
    print("ORCHESTRATION DEMONSTRATION")
    print("="*60)

    # Create coordinator
    coordinator = MultiAgentCoordinator()

    # Test request
    request = "Explain how blockchain technology works and write a report for technical readers."

    print(f"\n{'#'*60}")
    print(f"REQUEST: {request}")
    print(f"{'#'*60}")

    result = coordinator.orchestrate(
        request=request,
        style_requirements={
            "Format": "Technical report",
            "Audience": "Software developers",
            "Length": "800-1200 words",
            "Tone": "Professional but accessible"
        },
        constraints={
            "Include": "Real-world examples",
            "Avoid": " Oversimplification"
        }
    )

    print("\n" + "-"*60)
    print("FINAL OUTPUT PREVIEW:")
    print("-"*60)
    print(result["final_output"][:800] + ("..." if len(result["final_output"]) > 800 else ""))

    return result


# ============================================================================
# WHAT WE HAVE LEARNT
# ============================================================================
"""
=============================================================================
WHAT WE HAVE LEARNT: Full Multi-Agent Orchestration
=============================================================================

1. ALL FIVE PATTERNS WORK TOGETHER
   --------------------------------

   +------------------+     +------------------+
   | Hub-and-Spoke    | --> | Architecture     |
   |                  |     | Central coordinator|
   +------------------+     +------------------+
                 |
                 v
   +------------------+     +------------------+
   | Dynamic Selection | --> | Agent Selection  |
   |                  |     | Score-based      |
   +------------------+     +------------------+
                 |
                 v
   +------------------+     +------------------+
   | Scope Partitioning| --> | Work Division    |
   |                  |     | Non-overlapping  |
   +------------------+     +------------------+
                 |
                 v
   +------------------+     +------------------+
   | Iterative Refine | --> | Quality Control   |
   |                  |     | Evaluate + Refine |
   +------------------+     +------------------+
                 |
                 v
   +------------------+     +------------------+
   | Explicit Context | --> | Information Flow  |
   |                  |     | Complete context |
   +------------------+     +------------------+

2. PATTERN INTERACTIONS
   --------------------

   HUB-AND-SPOKE + EXPLICIT CONTEXT:
   - Coordinator passes context through the hub
   - Each agent receives full context from coordinator

   DYNAMIC SELECTION + SCOPE PARTITIONING:
   - Selected agents are assigned non-overlapping scopes
   - Researcher covers data, Analyst covers evaluation, etc.

   ITERATIVE REFINEMENT + EXPLICIT CONTEXT:
   - Quality feedback becomes part of next iteration's context
   - Each refinement has full history of what came before

3. COMMON MISTAKES TO AVOID
   ------------------------

   MISTAKE 1: Hardcoded Pipeline
   - Always using same agents regardless of request
   - Use dynamic selection to pick only needed agents

   MISTAKE 2: Skipping Quality Gates
   - Trusting first output without evaluation
   - Use iterative refinement to ensure quality

   MISTAKE 3: Incomplete Context
   - Not passing all required information to agents
   - Always build complete context with build_complete_context()

   MISTAKE 4: No Fallback for Failures
   - System breaks if one agent fails
   - Implement fault isolation and retry logic

4. PRODUCTION CONSIDERATIONS
   -------------------------

   FAULT TOLERANCE:
   - Each agent call should be retryable
   - Track failed tasks for manual review
   - Continue with remaining agents if one fails

   COST OPTIMIZATION:
   - Only use agents that are actually needed
   - Limit iterations based on request value
   - Consider caching common context pieces

   MONITORING:
   - Log each agent's input and output
   - Track quality scores across iterations
   - Monitor token usage per orchestration

   SCALABILITY:
   - Coordinator can become bottleneck
   - Consider async execution for independent agents
   - Add load balancing for high volume

5. INTERVIEW ANSWER FRAMEWORK
   --------------------------

   "How do all these patterns work together in production?"

   Step 1: Start with the coordinator role
   "The coordinator is the central hub. It analyzes each request,
    selects appropriate agents, builds their context, executes them,
    and evaluates the outputs."

   Step 2: Explain the pattern combination
   "Dynamic selection picks which agents are needed. Scope partitioning
    defines what each agent does. Explicit context passes all needed
    information. Iterative refinement ensures quality."

   Step 3: Give a concrete example
   "For a research report: Coordinator analyzes request -> selects
    Researcher and Writer -> Researcher gathers data in scope X ->
    Writer receives data + context -> Evaluator checks quality ->
    Refines if needed -> Final report produced."

   Step 4: Address tradeoffs
   "The tradeoff is complexity. For simple tasks, this is overkill.
    For complex tasks requiring quality, this architecture ensures
    consistent, high-quality outputs."

6. VISUAL SUMMARY
   ---------------

   COMPLETE ORCHESTRATION:

   Request: "Write a technical report on AI"
              |
              v
   +------------------------+
   | ANALYZE: Select agents  |
   | -> Researcher, Writer  |
   +------------------------+
              |
              v
   +------------------------+
   | EXECUTE: Researcher    |
   | Context: [Request +    |
   |          Style +       |
   |          Constraints]  |
   +------------------------+
              |
              v
   +------------------------+
   | EXECUTE: Writer        |
   | Context: [Request +    |
   |          Research +    |
   |          Style +       |
   |          Constraints]  |
   +------------------------+
              |
              v
   +------------------------+
   | EVALUATE: Check quality |
   | If < threshold: refine  |
   +------------------------+
              |
              v
   +------------------------+
   | OUTPUT: Final report   |
   +------------------------+

   ALL PATTERNS COMBINED:
   ======================

   * Hub-and-Spoke: All through coordinator
   * Dynamic Selection: Right agents for the job
   * Scope Partitioning: Clear work divisions
   * Iterative Refinement: Quality assurance
   * Explicit Context: Complete information flow

   This is how REAL multi-agent systems work in production!

=============================================================================
"""


if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    print("\n" + "="*60)
    print("PRACTICE 6: FULL MULTI-AGENT ORCHESTRATOR")
    print("="*60)
    print("""
This brings together ALL the patterns:

+------------------------------------------------------------+
|                     PATTERN INTEGRATION                     |
+------------------------------------------------------------+

| Pattern            | Role in Orchestrator                  |
|--------------------|----------------------------------------|
| Hub-and-Spoke      | Central coordinator controls all      |
| Dynamic Selection  | Analyze request -> select agents      |
| Scope Partitioning | Work divided by agent capabilities    |
| Iterative Refine   | Quality checked -> refine if needed   |
| Explicit Context   | Complete info passed to each agent    |

The coordinator orchestrates everything!
    """)

    result = demonstrate_orchestration()

    print("\n" + "="*60)
    print("PROGRAM COMPLETE!")
    print("="*60)
    print(f"""
ALL PATTERNS COMBINED:
=====================

    * Hub-and-Spoke: All communication through coordinator
    * Dynamic Selection: Appropriate agents selected
    * Scope Partitioning: Work divided by role
    * Iterative Refinement: Quality checked
    * Explicit Context: Complete info passed to each agent

The coordinator is the brain that makes multi-agent systems work!

See WHAT WE HAVE LEARNT section for comprehensive summary.
""")