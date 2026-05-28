"""
+===========================================================================+
|                                                                           |
|  PRACTICE 3: AGENT TOOL GATE - SPAWNING SUBAGENTS                         |
|                                                                           |
|  Critical requirement: Coordinator MUST have "Agent" in allowedTools!    |
|  + REAL-TIME SCENARIOS + MISTAKES + INTERVIEW GUIDE                      |
|                                                                           |
+===========================================================================+

INTERVIEW PREP: "What tool enables multi-agent spawning in Claude Code?"
This question tests your understanding of the Agent Tool Gate requirement.

REAL-TIME SCENARIO: You spent 3 days architecting a sophisticated multi-agent
system with specialized researchers, analysts, and writers. The system is
elegant. It would work perfectly. Except... you forgot to include the "Agent"
tool in the coordinator's allowedTools. The coordinator CANNOT spawn any
subagents. Everything fails silently or with a cryptic error.

===========================================================================
 THE AGENT TOOL GATE: A BINARY REQUIREMENT
===========================================================================

    +-----------------------------------------------------------------------+
    |  CRITICAL: This is NOT a preference, it's a REQUIREMENT!              |
    |                                                                       |
    |  Without "Agent" in allowedTools:                                     |
    |  - Coordinator CANNOT spawn subagents                                 |
    |  - Multi-agent work is IMPOSSIBLE                                     |
    |  - Your architecture is dead on arrival                               |
    |                                                                       |
    |  With "Agent" in allowedTools:                                        |
    |  - Coordinator CAN spawn subagents                                    |
    |  - Multi-agent coordination WORKS                                     |
    |  - Your architecture comes to life!                                  |
    +-----------------------------------------------------------------------+

    +=======================================================================+
    ||  VISUAL: THE TOOL GATE CONCEPT                                       ||
    ||                                                                      ||
    ||  WITHOUT "Agent" in allowedTools:                                    ||
    ||  +---------------------------+                                       ||
    ||  | Coordinator              |                                       ||
    ||  |                          |                                       ||
    ||  | allowedTools:            |                                       ||
    ||  | ["calculate", "search"]  |                                       ||
    ||  |                          |                                       ||
    ||  | Tries to spawn subagent  |                                       ||
    ||  |        X                 |                                       ||
    ||  | [FAILS!]                 |                                       ||
    ||  +---------------------------+                                       ||
    ||                                                                      ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WITH "Agent" in allowedTools:                                       ||
    ||  +---------------------------+                                       ||
    ||  | Coordinator              |                                       ||
    ||  |                          |                                       ||
    ||  | allowedTools:            |                                       ||
    ||  | ["Agent", "calculate",   |                                       ||
    ||  |  "search"]               |                                       ||
    ||  |                          |                                       ||
    ||  | Can spawn subagent  ---->+---------------------------+           ||
    ||  |                          | Subagent spawned!        |           ||
    ||  +---------------------------+                          |           ||
    ||                                                         |           ||
    ||                                      +------------------+           ||
    +=======================================================================+

"""

import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY", "")
api_base = os.getenv("ANTHROPIC_API_BASE", "")

from anthropic import Anthropic

client_kwargs = {"api_key": api_key} if api_key else {}
if api_base:
    client_kwargs["base_url"] = api_base
client = Anthropic(**client_kwargs)


# ============================================================================
# REAL-TIME SCENARIOS: When Agent Tool Gate Fails
# ============================================================================

def show_real_time_scenarios():
    """
    Production scenarios where Agent Tool Gate issues cause failures.
    """

    print("\n" + "=" * 70)
    print("REAL-TIME SCENARIOS: When Agent Tool Gate Fails")
    print("=" * 70)

    print("""
    +======================================================================+
    ||  SCENARIO #1: The Silent Failure                                    ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  CONTEXT: Enterprise research automation system                      ||
    ||                                                                      ||
    ||  WHAT HAPPENED:                                                      ||
    ||  1. Team built 5-tier multi-agent architecture                       ||
    ||  2. Deployed to production                                           ||
    ||  3. All requests returned generic "task complete" responses        ||
    ||  4. Subagents were NEVER spawned!                                    ||
    ||                                                                      ||
    ||  ROOT CAUSE:                                                        ||
    ||  - Coordinator defined: calculate, search, analyze tools            ||
    ||  - MISSING: "Agent" tool                                             ||
    ||  - Coordinator couldn't spawn subagents but didn't error clearly    ||
    ||  - System looked like it worked, but did nothing                      ||
    ||                                                                      ||
    ||  REAL CONSEQUENCE:                                                   ||
    ||  - 3 weeks of production running with fake automation              ||
    ||  - Manual work continued while "automation" ran                     ||
    ||  - Customer reported: "Results don't match actual analysis"         ||
    ||  - Emergency fix deployed on weekend                                 │
    ||                                                                      ||
    ||  LESSON: "Agent" tool is ALL OR NOTHING for multi-agent!           ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  SCENARIO #2: The Partial Permission Problem                        ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  CONTEXT: Customer support multi-agent system                        ||
    ||                                                                      ||
    ||  WHAT HAPPENED:                                                      ||
    │  1. Tier-1 support agent spawns Tier-2 for complex issues           ||
    │  2. Some requests worked, some silently failed                       │
    │  3. Customers with complex issues got wrong responses               │
    │                                                                      ||
    │  ROOT CAUSE:                                                        ||
    │  - Some users had sessions where "Agent" was in allowedTools        │
    │  - Others had sessions without "Agent" in allowedTools              │
    │  - Inconsistent behavior based on session configuration             │
    │                                                                      ||
    │  REAL CONSEQUENCE:                                                   ||
    │  - Escalations handled by wrong tier (Tier-1 handling Tier-2 work)  │
    │  - Customer frustration: "I already explained this twice"            │
    │  - Support team blamed for poor answers (was infrastructure!)      │
    │                                                                      │
    │  LESSON: ALL coordinators need "Agent" tool, not just some!         │
    │                                                                      │
    +======================================================================+

    +======================================================================+
    ||  SCENARIO #3: The API Version Mismatch                               ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  CONTEXT: Company migrating Claude API versions                       ||
    ||                                                                      ||
    ||  WHAT HAPPENED:                                                      ||
    │  1. Migrated from Claude 3 to Claude 4                               │
    │  2. Tool definitions changed format                                 │
    │  3. Agent tool definition became invalid                             │
    │  4. Subagent spawning broke across entire system                      │
    │                                                                      ||
    │  ROOT CAUSE:                                                        ||
    │  - Tool schema changed in new API version                            │
    │  - Valid tool definition in v3 became invalid in v4                  │
    │  - No error thrown, just silently failed                              │
    │                                                                      ||
    │  REAL CONSEQUENCE:                                                   │
    │  - Production down for 6 hours before root cause found             │
    │  - Hotfix deployed to all coordinators                               │
    │  - Post-mortem revealed: no monitoring for subagent spawn rate       │
    │                                                                      ||
    │  LESSON: Test Agent tool functionality after API migrations!        │
    │                                                                      ||
    +======================================================================+
    """)


# ============================================================================
# MISTAKES DEVELOPERS MAKE
# ============================================================================

def show_mistakes_developers_make():
    """
    Common mistakes with explanations.
    """

    print("\n" + "=" * 70)
    print("MISTAKES DEVELOPERS MAKE - Expert Warnings")
    print("=" * 70)

    print("""
    +======================================================================+
    ||  MISTAKE #1: "I'll add the Agent tool later"                        ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WHY IT'S WRONG:                                                     ||
    ||  If you don't include "Agent" from the start, you can't spawn        ||
    ||  subagents AT ALL during initial development and testing.            ||
    ||  You can't iterate on multi-agent logic without the capability!     ||
    ||                                                                      ||
    ||  BAD PLANNING:                                                      ||
    ||  Phase 1: Build coordinator with task tools                          ||
    ||  Phase 2: (Oops) Can't spawn subagents, add Agent tool              ||
    ||  Phase 3: Need to re-architect everything for multi-agent          ||
    ||                                                                      ||
    ||  CORRECT PLANNING:                                                   ||
    ||  Always include "Agent" tool from day 1!                             ||
    ||  Even if you're not spawning yet, include it for future capability   ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  MISTAKE #2: "Only certain coordinators need Agent tool"            ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WHY IT'S WRONG:                                                     ||
    ||  ANY coordinator that might spawn subagents needs "Agent" tool.     ||
    ||  If a coordinator CAN spawn but doesn't have tool, it silently      ||
    ||  fails. You won't know until runtime that spawning doesn't work.    ||
    ||                                                                      ||
    ||  BAD:                                                               ||
    ||  Tier-1 coordinator: ["Agent", "search"]  <- Has Agent              ||
    ||  Tier-2 coordinator: ["search", "calculate"] <- Missing Agent!     ||
    ||                                                                      ||
    ||  CORRECT:                                                            ||
    ||  ALL coordinators that spawn: ["Agent", ...other tools...]           ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  MISTAKE #3: Confusing allowedTools with system prompt              ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WHY IT'S WRONG:                                                     ||
    ||  allowedTools = what coordinator CAN DO (permissions)                ||
    ||  system_prompt = what coordinator SHOULD DO (instructions)           ||
    ||  These are DIFFERENT!                                                ||
    ||                                                                      ||
    ||  BAD:                                                               ||
    ||  system_prompt: "You can spawn subagents..."  <- Told to do it      ||
    ||  allowedTools: ["calculate", "search"]  <- But CAN'T do it!         ||
    ||                                                                      ||
    ||  CORRECT:                                                            ||
    ||  allowedTools: ["Agent", "calculate", "search"]  <- CAN spawn      ||
    ||  system_prompt: "Spawn subagents when..."  <- Told WHEN to do it   ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  MISTAKE #4: "The Agent tool is optional for simple systems"        ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WHY IT'S WRONG:                                                     ||
    ||  Even simple systems benefit from multi-agent patterns. But more     ||
    ||  importantly: If you think you "don't need it" and later discover    ||
    ||  you do, you've built the wrong architecture. Include it always.    ||
    ||                                                                      ||
    ||  RULE:                                                               ||
    ||  If you're building a coordinator that might EVER spawn subagents,   ||
    ||  include "Agent" tool from the start. It's a single line addition.  ||
    ||                                                                      ||
    +======================================================================+
    """)


# ============================================================================
# INTERVIEW Q&A
# ============================================================================

def show_interview_qa():
    """
    Interview questions and expert answer frameworks.
    """

    print("\n" + "=" * 70)
    print("INTERVIEW QUESTIONS & EXPERT ANSWERS GUIDE")
    print("=" * 70)

    print("""
    ========================================================================
    INTERVIEW Q1: "What tool enables multi-agent spawning in Claude Code?"
    ========================================================================

    EXPECTED ANSWER:
    The "Agent" tool (sometimes called "Subagent" or "Spawn"). This tool
    must be explicitly included in the coordinator's allowedTools list.
    Without it, no subagent spawning is possible, regardless of the
    system prompt or architecture.

    RED FLAGS IN ANSWERS:
    - "Any tool can spawn agents" -> Wrong, it's specifically the Agent tool
    - "It's automatic" -> Wrong, must be explicitly allowed
    - "I don't know" -> Shows lack of fundamental knowledge

    +-----------------------------------------------------------------------+
    | EXPERT TIP: Say "Agent tool in allowedTools" - exact terminology!     |
    +-----------------------------------------------------------------------+
    """)

    # Demo with actual API call
    message = client.messages.create(
        model="claude-haiku-4-5-20250601",
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": "As an expert in Claude Code multi-agent systems, explain "
                      "in 2 sentences what tool enables a coordinator to spawn "
                      "subagents and why it must be explicitly included."
        }]
    )

    print("\nExample Expert Answer:")
    print(f"    {message.content[0].text[:400]}...")

    print("""
    ========================================================================
    INTERVIEW Q2: "A coordinator can't spawn subagents. What's wrong?"
    ========================================================================

    EXPECTED ANSWER:
    Check if "Agent" is in allowedTools. That's the most common issue.
    Also check: Is the tool definition valid? Is the API version correct?
    Are there permission restrictions?

    DEBUGGING STEPS:
    1. Print coordinator's allowedTools list
    2. Verify "Agent" (or "Subagent") is included
    3. Check tool definition schema matches API version
    4. Check for runtime permission errors

    +-----------------------------------------------------------------------+
    | EXPERT TIP: This is a binary check - either Agent is there or it     |
    | isn't. No middle ground!                                              |
    +-----------------------------------------------------------------------+
    """)

    print("""
    ========================================================================
    INTERVIEW Q3: "What's the difference between allowedTools and system prompt?"
    ========================================================================

    EXPECTED ANSWER:
    allowedTools is a PERMISSION - what the coordinator is ALLOWED to do.
    system_prompt is an INSTRUCTION - what the coordinator SHOULD do.
    You need BOTH: the permission (allowedTools) AND the instruction
    (system_prompt telling it when to use the Agent tool).

    ANALOGY:
    - allowedTools = Having a key to a door
    - system_prompt = Knowing when to open the door

    You can have the key (allowedTools) but not know when to use it.
    Or you can know when (system_prompt) but not have the key (allowedTools).
    You need BOTH!

    +-----------------------------------------------------------------------+
    | EXPERT TIP: Use the permission vs instruction distinction             |
    +-----------------------------------------------------------------------+
    """)

    print("""
    ========================================================================
    INTERVIEW Q4: "When should you NOT use the Agent tool?"
    ========================================================================

    EXPECTED ANSWER:
    - Simple single-task requests (overkill to spawn subagents)
    - When you need real-time shared state (spawning adds latency)
    - When the task can be done directly without specialization
    - When token budget is very constrained (spawning has overhead)

    TRADE-OFF:
    Multi-agent = More capability but more complexity and overhead.
    Use it when the task genuinely benefits from parallel specialization.

    +-----------------------------------------------------------------------+
    | EXPERT TIP: Mention the coordination overhead is a real cost!         |
    +-----------------------------------------------------------------------+
    """)


# ============================================================================
# TOOL DEFINITIONS
# ============================================================================

# Define tools for the coordinator
tools = [
    {
        "name": "Agent",
        "description": "Spawn a subagent to perform a specific task. The coordinator MUST include this tool to spawn subagents.",
        "input_schema": {
            "type": "object",
            "properties": {
                "description": {
                    "type": "string",
                    "description": "What this subagent should do"
                },
                "agent_name": {
                    "type": "string",
                    "description": "Name identifier for the subagent"
                },
                "system_prompt": {
                    "type": "string",
                    "description": "Instructions for the subagent"
                }
            },
            "required": ["description", "agent_name", "system_prompt"]
        }
    },
    {
        "name": "calculate",
        "description": "Perform mathematical calculations",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Math expression to evaluate"
                }
            },
            "required": ["expression"]
        }
    }
]


def execute_tool(name: str, tool_input: dict) -> str:
    """
    Execute tool and return result.
    For simulation purposes.
    """
    if name == "Agent":
        return f"Subagent spawned: {tool_input['agent_name']} - {tool_input['description']}"

    elif name == "calculate":
        try:
            return str(eval(tool_input["expression"]))
        except Exception as e:
            return f"Error: {e}"

    return f"Unknown tool: {name}"


# ============================================================================
# DEMONSTRATION FUNCTIONS
# ============================================================================

def demonstrate_tool_gate_failure():
    """
    Demonstrate what happens when Agent tool is NOT in allowedTools.
    """
    print("\n" + "=" * 70)
    print("DEMONSTRATION: Coordinator WITHOUT Agent tool")
    print("=" * 70)

    print("""
    +=======================================================================+
    ||  COORDINATOR (WITHOUT Agent tool)                                   ||
    ||                                                                      ||
    ||  allowedTools = ["calculate"]  <- MISSING "Agent"!                   ||
    ||                                                                      ||
    ||  User: "Research AI trends and write a report"                       ||
    ||                                                                      ||
    ||  Coordinator tries to spawn research agent...                       ||
    ||                                                                      ||
    ||  +---------------------------+                                       ||
    ||  | X FAILS: Cannot spawn!   |                                       ||
    ||  | "Agent" not in allowedTools|                                     ||
    ||  +---------------------------+                                       ||
    ||                                                                      ||
    ||  The coordinator cannot do multi-agent work!                         ||
    ||                                                                      ||
    +=======================================================================+
    """)

    print("\nThis is a BINARY requirement, not a preference.")
    print("Without 'Agent' in allowedTools, you cannot spawn subagents.")


def demonstrate_tool_gate_success():
    """
    Demonstrate correct setup with Agent tool in allowedTools.
    """
    print("\n" + "=" * 70)
    print("DEMONSTRATION: Coordinator WITH Agent tool")
    print("=" * 70)

    print("""
    +=======================================================================+
    ||  COORDINATOR (WITH Agent tool)                                      ||
    ||                                                                      ||
    ||  allowedTools = ["Agent", "calculate"]  <- Agent included!         ||
    ||                                                                      ||
    ||  User: "Research AI trends and write a report"                       ||
    ||                                                                      ||
    ||  Coordinator can now:                                                ||
    ||                                                                      ||
    ||  [SUCCESS] Spawn Research Agent -> Collects AI trends               ||
    ||  [SUCCESS] Spawn Writer Agent -> Writes the report                  ||
    ||  [SUCCESS] Combine results -> Final response to user                 ||
    ||                                                                      ||
    +=======================================================================+
    """)


def run_coordinator_system(user_task: str) -> str:
    """
    Simulate a coordinator that spawns subagents.
    Shows the correct pattern with Agent tool.
    """
    print("\n" + "-" * 50)
    print("COORDINATOR DECISION PROCESS")
    print("-" * 50)

    messages = [
        {
            "role": "system",
            "content": """You are a coordinator agent.
You can spawn subagents using the 'Agent' tool when needed.
When spawning agents, provide clear descriptions and instructions.

For each user request:
1. Decide: Does this need a subagent? What kind?
2. Spawn the subagent with explicit context
3. Collect the results
4. Synthesize and respond
"""
        },
        {
            "role": "user",
            "content": user_task
        }
    ]

    print(f"User task: {user_task}")
    print("\nCoordinator analyzing task...")
    print("   -> Task requires research and synthesis")
    print("   -> Spawning subagents...")

    # Simulate the flow
    print("\n   [SUBAGENT 1] Research Agent spawned")
    print("   [SUBAGENT 1] Finding information about AI trends...")
    print("   [SUBAGENT 1] Returns findings to coordinator")

    print("\n   [SUBAGENT 2] Writer Agent spawned")
    print("   [SUBAGENT 2] Synthesizing research into report...")
    print("   [SUBAGENT 2] Returns completed report to coordinator")

    print("\n   [COORDINATOR] Combining subagent results...")
    print("   [COORDINATOR] Final response ready!")

    return "Task completed via multi-agent coordination"


def demonstrate_parallel_spawning():
    """
    Demonstrate that independent subagents should be spawned in parallel.
    """
    print("\n" + "=" * 70)
    print("PARALLEL vs SEQUENTIAL SPAWNING")
    print("=" * 70)

    print("""
    +=======================================================================+
    ||  WRONG: Sequential (wastes time)                                    ||
    ||  ===============================================================    ||
    ||                                                                      ||
    ||  1. Spawn Subagent A --------> Wait... --------> Get result A         ||
    ||                                                                      ||
    ||  2. Spawn Subagent B --------> Wait... --------> Get result B         ||
    ||                                                                      ||
    ||  Total time: Time(A) + Time(B)                                       ||
    ||                                                                      ||
    +=======================================================================+

    +=======================================================================+
    ||  CORRECT: Parallel (efficient)                                      ||
    ||  ===============================================================    ||
    ||                                                                      ||
    ||  1. Spawn Subagent A --------------------------------> Get result A   ||
    ||  2. Spawn Subagent B --------------------------------> Get result B   ||
    ||                                                                      ||
    ||  Both at the same time!                                              ||
    ||                                                                      ||
    ||  Total time: max(Time(A), Time(B))  <- Much faster!                  ||
    ||                                                                      ||
    +=======================================================================+
    """)

    print("\nWhen tasks are INDEPENDENT, spawn them in PARALLEL!")
    print("This is a key optimization for multi-agent systems.")


def show_agent_definition_structure():
    """
    Show the structure for defining a subagent.
    """
    print("\n" + "=" * 70)
    print("SUBAGENT DEFINITION STRUCTURE")
    print("=" * 70)

    print("""
    When spawning a subagent, define it with:

    {
        "description": "What this agent does",
        "system_prompt": "Instructions for the agent",
        "tools": ["list", "of", "allowed", "tools"],  // Optional restrictions
        "model": "claude-sonnet-4-7"  // Optional model override
    }

    Example:
    {
        "description": "Research agent for tech news",
        "system_prompt": "You find and summarize tech news articles.
            Always cite sources and include confidence levels.
            Return findings in structured format.",
        "tools": ["web_search", "read_article"],
        "model": "claude-haiku-4-5-20250601"
    }
    """)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    print("\n" + "=" * 70)
    print("PRACTICE 3: AGENT TOOL GATE - SPAWNING SUBAGENTS")
    print("=" * 70)
    print("""
This program teaches the CRITICAL requirement for spawning subagents:
    The coordinator MUST have "Agent" in its allowedTools!

Without this tool, multi-agent coordination is impossible.
    """)

    # Show all enhanced sections
    show_real_time_scenarios()
    show_mistakes_developers_make()
    show_interview_qa()
    demonstrate_tool_gate_failure()
    demonstrate_tool_gate_success()
    demonstrate_parallel_spawning()
    show_agent_definition_structure()

    # Show the coordinator in action
    print("\n" + "-" * 50)
    print("COORDINATOR SIMULATION")
    print("-" * 50)

    result = run_coordinator_system("Research AI trends and write a report")
    print(f"\nResult: {result}")

    print("\n" + "=" * 70)
    print("WHAT WE HAVE LEARNT")
    print("=" * 70)
    print("""
    +======================================================================+
    ||  1. THE AGENT TOOL GATE:                                             ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WITHOUT "Agent" in allowedTools:                                    ||
    ||  - Coordinator CANNOT spawn subagents                                ||
    ||  - Multi-agent work is IMPOSSIBLE                                    ||
    ||  - System silently fails or errors                                   ||
    ||                                                                      ||
    ||  WITH "Agent" in allowedTools:                                       ||
    ||  - Coordinator CAN spawn subagents                                    ||
    ||  - Multi-agent coordination WORKS                                     ||
    ||                                                                      ||
    ||  KEY INSIGHT: This is a BINARY requirement, not a preference!       ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  2. REAL-TIME SCENARIOS WHERE THIS BREAKS:                           ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  - Silent failure (looks like it works, does nothing)                ||
    ||  - Partial permissions (some sessions work, others don't)            ||
    ||  - API version mismatch (Agent definition becomes invalid)          ||
    ||                                                                      ||
    ||  KEY INSIGHT: The system FAILS SILENTLY without clear error!         ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  3. COMMON MISTAKES:                                                 ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  MISTAKE #1: "I'll add Agent tool later"                            ||
    ||              -> Can't develop/test multi-agent without it!         ||
    ||                                                                      ||
    ||  MISTAKE #2: "Only certain coordinators need it"                     ||
    ||              -> ALL coordinators that spawn need it!                  ||
    ||                                                                      ||
    ||  MISTAKE #3: Confusing allowedTools with system prompt              ||
    ||              -> Permissions vs Instructions - different!             ||
    ||                                                                      ||
    ||  MISTAKE #4: "Optional for simple systems"                           ||
    ||              -> Include it ALWAYS for future flexibility            ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  4. INTERVIEW TIPS:                                                  ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  - Say "Agent tool in allowedTools" - exact terminology!             ||
    ||  - Explain: allowedTools = permissions, system_prompt = instructions ||
    ||  - Debug by checking allowedTools FIRST                             ||
    ||  - This is BINARY - either it's there or spawning fails             ||
    ||                                                                      ||
    ||  EXPECTED ANSWER STRUCTURE:                                          ||
    ||  1. State: "Agent tool must be in allowedTools"                     ||
    ||  2. Explain: Why this is binary (permission vs instruction)         ||
    ||  3. Give debugging approach                                         ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  5. KEY RULES TO MEMORIZE:                                           ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  RULE #1: ALWAYS include "Agent" in coordinator's allowedTools       ||
    ||  RULE #2: allowedTools = CAN DO, system_prompt = SHOULD DO          ||
    ||  RULE #3: ALL coordinators that spawn need Agent tool                ||
    ||  RULE #4: Include from day 1, not "later"                            ||
    ||  RULE #5: Test spawning after any API changes                        ||
    ||                                                                      ||
    +======================================================================+

    Next: practice_04_fork_vs_resume.py explains session management concepts!
    """)

    print("\n" + "=" * 70)
    print("PROGRAM COMPLETE!")
    print("=" * 70)


"""
+===========================================================================+
|                                                                           |
|  KEY CONCEPTS FROM THIS FILE:                                             |
|                                                                           |
|  CRITICAL REQUIREMENT: "Agent" tool must be in allowedTools!               |
|                                                                           |
|  REAL-TIME SCENARIOS:                                                     |
|  - Silent failure (looks like it works, does nothing)                    |
|  - Partial permissions (some sessions work, others don't)               |
|  - API version mismatch breaks tool definition                            |
|                                                                           |
|  MISTAKES TO AVOID:                                                       |
|  - "Add later" -> Can't develop without it!                               |
|  - "Only some need it" -> ALL coordinators that spawn need it!           |
|  - Confusing permissions with instructions                                |
|                                                                           |
|  INTERVIEW PREP:                                                          |
|  - "What tool enables spawning?" -> "Agent" in allowedTools               |
|  - Debug approach -> Check allowedTools first                             |
|  - Permission vs instruction distinction                                   |
|                                                                           |
+===========================================================================+
"""