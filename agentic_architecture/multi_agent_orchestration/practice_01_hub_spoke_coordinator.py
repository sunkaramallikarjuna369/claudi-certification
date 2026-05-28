"""
PRACTICE 1: HUB-AND-SPOKE COORDINATOR
======================================
The foundation of multi-agent orchestration!
One coordinator managing multiple specialized agents.

+------------------------------------------------------------------+
|                    HUB-AND-SPOKE ARCHITECTURE                     |
+------------------------------------------------------------------+
|                                                                    |
|                        COORDINATOR                                 |
|                      (The Hub Node)                                |
|                          [O]                                       |
|                         / | \                                      |
|                        /  |  \                                     |
|                       /   |   \                                    |
|                      /    |    \                                   |
|                     /     |     \                                  |
|                    v      v      v                                 |
|              +-----+ +------+ +-----+                              |
|              | AG1 | | AG2  | | AG3  |                              |
|              |     | |      | |      |  <-- Spoke Agents            |
|              +-----+ +------+ +-----+                              |
|                                                                    |
|   FLOW: User -> Coordinator -> Agent1                              |
|                   -> Agent2 -> ...                                 |
|                   -> Agent3                                        |
|                   -> Return to User                                |
|                                                                    |
+------------------------------------------------------------------+

KEY CONCEPT: All communication flows through the coordinator.
Each agent is a "spoke" - only the hub (coordinator) knows the full picture.
"""

import os
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY", "")
api_base = os.getenv("ANTHROPIC_API_BASE", "")

from anthropic import Anthropic
client_kwargs = {"api_key": api_key} if api_key else {}
if api_base:
    client_kwargs["base_url"] = api_base
client = Anthropic(**client_kwargs)


# ============================================================================
# REAL-TIME SCENARIO: E-Commerce Product Launch
# ============================================================================
"""
PRODUCTION SCENARIO: Product Launch Orchestration

Imagine you're launching a new product. The coordinator must:
1. Call RESEARCHER: Gather market data, competitor info, pricing trends
2. Call ANALYST: Evaluate market fit, ROI projections, risk assessment
3. Call WRITER: Create marketing copy, product descriptions, press release
4. Call FACT_CHECKER: Verify all claims, statistics, compliance

Without hub-and-spoke, agents work in silos and produce inconsistent output.
With hub-and-spoke, the coordinator ensures seamless information flow.
"""

# ============================================================================
# MISTAKE #1: Skipping the Coordinator (Direct Agent Communication)
# ============================================================================
"""
COMMON ERROR: Letting agents communicate directly with each other

    Agent1 -----> Agent2 -----> Agent3

WHY THIS BREAKS:
- Agent2 might miss critical context from Agent1
- No single point of control for quality
- Debugging becomes impossible ("where did this data come from?")
- Race conditions when Agent3 depends on Agent2, but Agent2 still waiting for Agent1

CORRECT APPROACH:
    Coordinator
        |
        v
    Agent1 (wait for complete result)
        |
        v (pass full context)
    Agent2 (has everything from Agent1)
        |
        v (pass full context)
    Agent3 (has everything from Agent1 AND Agent2)
"""

# ============================================================================
# MISTAKE #2: Not Passing Context Between Agents
# ============================================================================
"""
COMMON ERROR: Assuming agents "just know" what previous agents did

INCORRECT:
    research_results = call_researcher(topic)
    writer_output = call_writer(topic)  # Writer has NO idea what researcher found!

CORRECT:
    research_results = call_researcher(topic)
    writer_output = call_writer(topic, research_data)  # Writer has full context
"""

# ============================================================================
# INTERVIEW Q&A: Hub-and-Spoke Pattern
# ============================================================================
"""
Q: When would you choose hub-and-spoke over other architectures?
A: Hub-and-spoke is ideal when:
   - You need centralized control and monitoring
   - Tasks are sequential (output of one becomes input of next)
   - Debugging and audit trails are critical
   - The coordinator needs to maintain global state

Q: What are the main drawbacks of hub-and-spoke?
A: - Single point of failure (if coordinator crashes, system fails)
   - Potential bottleneck if coordinator becomes overloaded
   - Not suitable for parallel independent tasks (use mesh instead)

Q: How do you handle coordinator failure?
A: Implement:
   - Health checks and heartbeats
   - Circuit breakers (stop calling agents if coordinator is unhealthy)
   - Checkpointing (save state periodically so work isn't lost)
   - Dead letter queues (retry failed tasks)
"""


# ============================================================================
# AGENT DEFINITIONS
# ============================================================================

def create_researcher_response(topic: str, context: str = "") -> str:
    """
    The RESEARCHER agent - specializes in gathering information!

    ASCII ART: Researcher Agent Role
    +---------------------------+
    |     RESEARCHER AGENT      |
    +---------------------------+
    |  Input: Topic + Context    |
    |  Process: Web search,     |
    |          Data gathering   |
    |  Output: Structured facts |
    +---------------------------+
    """
    print(f"[RESEARCHER] Starting research on: {topic}")

    researcher_prompt = f"""You are a research specialist AI agent.
Your job is to gather comprehensive information about the given topic.

TOPIC: {topic}

{context if context else ""}

Provide a structured research summary with:
1. Key facts and statistics
2. Main concepts and definitions
3. Important considerations
4. Any relevant data points

Be thorough but concise - this will be used by another agent."""

    response = client.messages.create(
        model="claude-haiku-4-5-20250601",
        max_tokens=2048,
        messages=[{"role": "user", "content": researcher_prompt}],
        tools=[]
    )

    result = response.content[0].text
    print(f"[RESEARCHER] Research complete ({len(result)} chars)")
    return result


def create_writer_response(topic: str, research_data: str) -> str:
    """
    The WRITER agent - specializes in creating polished output!

    ASCII ART: Writer Agent Role
    +---------------------------+
    |       WRITER AGENT        |
    +---------------------------+
    |  Input: Topic + Research  |
    |  Process: Writing,        |
    |          Structuring      |
    |  Output: Final document   |
    +---------------------------+
    """
    print(f"[WRITER] Creating output on: {topic}")

    writer_prompt = f"""You are a professional writer AI agent.
Your job is to transform research data into a clear, engaging response.

ORIGINAL TOPIC: {topic}

RESEARCH DATA:
{research_data}

Create a well-structured response that:
1. Directly addresses the topic
2. Incorporates the research data naturally
3. Is clear and easy to understand
4. Has good flow and organization"""

    response = client.messages.create(
        model="claude-haiku-4-5-20250601",
        max_tokens=2048,
        messages=[{"role": "user", "content": writer_prompt}],
        tools=[]
    )

    result = response.content[0].text
    print(f"[WRITER] Writing complete ({len(result)} chars)")
    return result


def coordinator_orchestrate(user_request: str, show_flow: bool = True) -> str:
    """
    The COORDINATOR - orchestrates all the agents!

    ASCII ART: Coordinator Flow
    ==========================

    User Request
         |
         v
    +------------+
    | COORDINATOR |  <-- Analyzes request, plans execution
    +------------+
         |
         +---> Call RESEARCHER
         |           |
         |           v
         |     [Gather Data]
         |           |
         +---> Call WRITER
                     |
                     v
               [Create Output]
                     |
                     v
         +------------+
         | Return Result to User
         +------------+

    """
    if show_flow:
        print(f"\n{'='*60}")
        print(f"[COORDINATOR] Processing request: {user_request}")
        print('='*60)

        print("\n[COORDINATOR] Analyzing request...")
        print("[COORDINATOR] Planning execution:")
        print("   1. Call Researcher agent to gather information")
        print("   2. Pass research to Writer agent")
        print("   3. Return final output to user")

        print("\n" + "-"*60)
        print("[COORDINATOR] Calling RESEARCHER agent...")
        print("-"*60)
    else:
        print(f"[COORDINATOR] Research -> Writer pipeline")

    research_results = create_researcher_response(
        topic=user_request,
        context=f"The user asked: '{user_request}'. Please research this topic thoroughly."
    )

    if show_flow:
        print("\n" + "-"*60)
        print("[COORDINATOR] Calling WRITER agent...")
        print("-"*60)

    writer_output = create_writer_response(
        topic=user_request,
        research_data=research_results
    )

    if show_flow:
        print("\n" + "-"*60)
        print("[COORDINATOR] Orchestration complete!")
        print("-"*60)

    return writer_output


# ============================================================================
# DEMONSTRATION WITH EDGE CASES
# ============================================================================

def demonstrate_edge_cases():
    """
    Shows how hub-and-spoke handles edge cases correctly.
    """
    print("\n" + "="*60)
    print("EDGE CASE DEMONSTRATION")
    print("="*60)

    # Edge Case 1: Very short request
    print("\n[EDGE CASE 1] Minimal request: 'What is AI?'")
    result = coordinator_orchestrate("What is AI?", show_flow=True)
    print(f"Result length: {len(result)} chars")

    # Edge Case 2: Complex multi-part request
    print("\n[EDGE CASE 2] Complex request: 'Explain photosynthesis and include chemical equations'")
    result = coordinator_orchestrate("Explain photosynthesis and include chemical equations", show_flow=True)
    print(f"Result length: {len(result)} chars")

    # Edge Case 3: Request with specific format requirements
    print("\n[EDGE CASE 3] Formatted request: 'List 5 facts about black holes in bullet points'")
    result = coordinator_orchestrate("List 5 facts about black holes in bullet points", show_flow=True)
    print(f"Result length: {len(result)} chars")


# ============================================================================
# WHAT WE HAVE LEARNT
# ============================================================================
"""
=============================================================================
WHAT WE HAVE LEARNT: Hub-and-Spoke Coordinator Pattern
=============================================================================

1. ARCHITECTURE BASICS
   --------------------
   - Hub-and-spoke has ONE central coordinator (the hub)
   - All agents (spokes) communicate ONLY through the coordinator
   - No direct agent-to-agent communication
   - Coordinator maintains global state and orchestrates flow

2. WHEN TO USE HUB-AND-SPOKE
   --------------------------
   - Sequential tasks where output of one feeds into next
   - Need for centralized control and monitoring
   - Debugging and audit trails are critical
   - Global state management required
   - Quality control at a single point

3. COMMON MISTAKES TO AVOID
   -------------------------
   MISTAKE 1: Direct Agent Communication
   - Agents should NEVER talk directly to each other
   - All data must flow through the coordinator
   - Otherwise you lose control and visibility

   MISTAKE 2: Missing Context
   - Always pass complete context to each agent
   - Don't assume agents know what previous agents did
   - Explicit context passing prevents "where did this come from?" issues

   MISTAKE 3: Stateless Coordinator
   - The coordinator should maintain conversation history
   - For multi-turn interactions, keep track of what's happened
   - Otherwise the coordinator can't make informed decisions

4. PRODUCTION CONSIDERATIONS
   --------------------------
   - Implement health checks for the coordinator
   - Add circuit breakers to prevent cascading failures
   - Use checkpointing for long-running orchestrations
   - Consider dead letter queues for failed tasks
   - Add monitoring and alerting for coordinator health

5. INTERVIEW ANSWER FRAMEWORK
   --------------------------
   When explaining hub-and-spoke in an interview:

   Step 1: Describe the architecture
   "Hub-and-spoke is a centralized orchestration pattern where a single
    coordinator manages all agent interactions. Agents are 'spokes' that
    only communicate with the central 'hub'."

   Step 2: Explain why it matters
   "This gives us centralized control, making debugging and monitoring
    straightforward. It's ideal for sequential tasks where output of one
    agent becomes input of the next."

   Step 3: Give a real example
   "For instance, in a document generation pipeline: researcher gathers
    data, analyst evaluates it, writer creates the document - all
    orchestrated through a single coordinator."

   Step 4: Acknowledge tradeoffs
   "The tradeoff is that the coordinator can become a bottleneck, and
    there's a single point of failure. For independent parallel tasks,
    a mesh architecture might be better."

6. ASCII DIAGRAM SUMMARY
   ----------------------

   HUB-AND-SPOKE:

       [Coordinator]     <-- Single point of control
          /    \          All communication through hub
         /      \
        v        v
   [Agent1]  [Agent2]    Spokes are specialized
        \        /
         v      v
          \    /
       [Result]

   vs MESH (for comparison):

   [A1] -- [A2]          No central control
    |  \  /  |            Harder to debug
    |   \/   |            Better for parallel tasks
    |  /\   |
   [A3] -- [A4]

=============================================================================
"""


if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    print("\n" + "="*60)
    print("PRACTICE 1: HUB-AND-SPOKE COORDINATOR")
    print("="*60)

    print("""
+------------------------------------------------------------------+
|                    HUB-AND-SPOKE ARCHITECTURE                     |
+------------------------------------------------------------------+
|                                                                    |
|                        COORDINATOR                                 |
|                      (The Hub Node)                                |
|                          [O]                                       |
|                         / | \\                                      |
|                        /  |  \\                                     |
|                       /   |   \\                                    |
|                      /    |    \\                                   |
|                     /     |     \\                                  |
|                    v      v      v                                 |
|              +-----+ +------+ +-----+                              |
|              | AG1 | | AG2  | | AG3  |                              |
|              +-----+ +------+ +-----+                              |
|                                                                    |
+------------------------------------------------------------------+
""")

    user_request = "Explain how photosynthesis works in simple terms"

    print(f"\nUser Request: {user_request}")
    print("\n" + "-"*60 + "\n")

    result = coordinator_orchestrate(user_request, show_flow=True)

    print("\n" + "="*60)
    print("FINAL RESULT:")
    print("="*60)
    print(result)
    print("\n" + "="*60)

    # Show edge cases
    demonstrate_edge_cases()

    print("\n" + "="*60)
    print("PROGRAM COMPLETE!")
    print("="*60)
    print("\nSee WHAT WE HAVE LEARNT section for comprehensive summary.")