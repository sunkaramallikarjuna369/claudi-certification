"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║           SUBAGENT CONTEXT PASSING & GUARDRAILS                             ║
║                                                                              ║
║  The Critical Rules for Multi-Agent Context Management                     ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

WHAT IS CONTEXT PASSING?
══════════════════════════

    The Golden Rule of Multi-Agent Systems:

    ════════════════════════════════════════════════════════════════════════
    │                                                                        │
    │   SUBAGENTS DO NOT AUTOMATICALLY INHERIT CONTEXT FROM THE COORDINATOR! │
    │                                                                        │
    │   Every piece of information a subagent needs must be EXPLICITLY       │
    │   passed to it. Always. No exceptions.                                │
    │                                                                        │
    ════════════════════════════════════════════════════════════════════════

    This is the MOST IMPORTANT concept in multi-agent systems.


WHY DOES THIS MATTER?
════════════════════════

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   WITHOUT EXPLICIT CONTEXT PASSING:                                    │
    │   ──────────────────────────────────                                   │
    │                                                                         │
    │   Coordinator has full conversation history                           │
    │   Subagent spawns with minimal context                                 │
    │   → Subagent doesn't know user's original question!                    │
    │   → Subagent doesn't know what other agents found!                    │
    │   → Subagent doesn't know user's preferences!                         │
    │   → Confused, incomplete, or wrong outputs!                           │
    │                                                                         │
    │   ─────────────────────────────────────────────────────────────────── │
    │                                                                         │
    │   WITH EXPLICIT CONTEXT PASSING:                                      │
    │   ────────────────────────────────────                                │
    │                                                                         │
    │   Coordinator passes ALL needed information to subagent               │
    │   "You are researching X. User wants Y. Background: Z..."              │
    │   → Subagent has everything it needs!                                │
    │   → Complete, accurate, reliable outputs!                            │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘


THE ATTRIBUTION FAILURE PROBLEM
══════════════════════════════

    A common and critical failure in multi-agent systems:

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   SITUATION:                                                            │
    │   ─────────                                                             │
    │   Research Agent 1: Finds "AAPL revenue grew 8% in Q3"                 │
    │   Research Agent 2: Finds "iPhone sales drove the growth"              │
    │   Synthesis Agent: Writes report with NO CITATIONS!                  │
    │                                                                         │
    │   ROOT CAUSE:                                                          │
    │   ────────────                                                         │
    │   The coordinator STRIPPED all metadata before passing content to      │
    │   the synthesis agent. The synthesis agent literally CANNOT cite        │
    │   sources it was never given!                                          │
    │                                                                         │
    │   ─────────────────────────────────────────────────────────────────── │
    │                                                                         │
    │   THE FIX:                                                             │
    │   ────────                                                             │
    │   Always pass structured metadata alongside content:                    │
    │   • Source URL and document name                                       │
    │   • Page numbers and confidence levels                                 │
    │   • Which agent retrieved the finding                                   │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘


CORRECT CONTEXT PASSING STRUCTURE
════════════════════════════════

    Always pass structured data with these fields:

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   {                                                                   │
    │       "content": "...",           // The actual finding/information     │
    │       "source": "URL or name",    // Where did this come from?          │
    │       "confidence": "high",      // How certain is the agent?          │
    │       "agent": "researcher",      // Which subagent produced this?     │
    │       "timestamp": "...",        // When was this retrieved?          │
    │       "page_number": "1-3",       // For document citations             │
    │       "raw_data": {...}           // Optional: structured data          │
    │   }                                                                   │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘


SUBAGENT ISOLATION - THE CRITICAL RULE
════════════════════════════════════

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   ⚠️  SUBAGENTS HAVE ISOLATED CONTEXT!                                  │
    │                                                                         │
    │   This means:                                                          │
    │   • Subagent A cannot see what Subagent B knows                        │
    │   • Subagent A cannot see the coordinator's conversation history       │
    │   • Subagent A cannot see Subagent B's outputs automatically           │
    │                                                                         │
    │   ─────────────────────────────────────────────────────────────────── │
    │                                                                         │
    │   WRONG ASSUMPTION (What beginners do):                                │
    │   ───────────────────────────────────                                 │
    │   "I already told the coordinator, so all subagents will              │
    │    automatically know it"                                              │
    │                                                                         │
    │   → FALSE! Subagents have ISOLATED context!                            │
    │                                                                         │
    │   ─────────────────────────────────────────────────────────────────── │
    │                                                                         │
    │   CORRECT PATTERN (What experts do):                                   │
    │   ────────────────────────────────────                                 │
    │   Coordinator EXPLICITLY passes all context to each subagent:         │
    │   "You are researching X. Here is everything you need to know:         │
    │    - User's original question: Y                                      │
    │    - What other agents found: Z                                       │
    │    - User's preferences: W                                           │
    │    - What we're looking for: V"                                       │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘


THE AGENT TOOL GATE - CRITICAL REQUIREMENT
═══════════════════════════════════════

    To spawn subagents, the coordinator MUST have "Agent" in allowedTools!

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   REQUIRED CONFIGURATION:                                              │
    │   ────────────────────────                                             │
    │                                                                         │
    │   allowedTools = ["Agent", "calculator", "search", ...]                │
    │                   └─────                                                │
    │                   MUST include "Agent" to spawn subagents!             │
    │                                                                         │
    │   This is a BINARY requirement, not a preference!                       │
    │   Without it, subagent spawning fails completely!                      │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘


PARALLEL vs SEQUENTIAL SPAWNING
══════════════════════════════

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   WRONG: Sequential (wastes time)                                      │
    │   ────────────────────────────────────                                 │
    │                                                                         │
    │   1. Spawn Subagent A ───────> Wait... ───────> Get result A            │
    │   2. Spawn Subagent B ───────> Wait... ───────> Get result B            │
    │   3. Spawn Subagent C ───────> Wait... ───────> Get result C           │
    │                                                                         │
    │   Total time: Time(A) + Time(B) + Time(C)                             │
    │                                                                         │
    │   ─────────────────────────────────────────────────────────────────── │
    │                                                                         │
    │   RIGHT: Parallel (efficient)                                          │
    │   ────────────────────────────────                                    │
    │                                                                         │
    │   1. Spawn Subagent A ───────────────────> Get result A                │
    │   2. Spawn Subagent B ───────────────────> Get result B                │
    │   3. Spawn Subagent C ───────────────────> Get result C                │
    │                                                                         │
    │   Total time: max(Time(A), Time(B), Time(C)) ← Much faster!           │
    │                                                                         │
    │   When tasks are INDEPENDENT, spawn them in PARALLEL!                 │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘


FORK_SESSION vs --resume
════════════════════════

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   fork_session: Creates INDEPENDENT branches                          │
    │   ─────────────────────────────────────────                           │
    │   • Use for: Exploring alternatives, A/B testing                     │
    │   • Changes in one branch don't affect others                        │
    │   • "Let's try approach A AND approach B"                            │
    │                                                                         │
    │   --resume: Continues a specific session LINEARLY                     │
    │   ─────────────────────────────────────────────────                   │
    │   • Use for: Picking up where you left off                            │
    │   • All previous context is preserved                                 │
    │   • "Continue where I left off"                                       │
    │                                                                         │
    │   These are DIFFERENT tools for DIFFERENT purposes!                    │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘


COMMON GUARDRAIL FAILURES
════════════════════════

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   FAILURE 1: Assuming subagents auto-inherit context                  │
    │   ─────────────────────────────────────────────────                    │
    │   WRONG: "Subagent should know what to do"                            │
    │   RIGHT: Always pass explicit context                                 │
    │                                                                         │
    │   ─────────────────────────────────────────────────────────────────── │
    │                                                                         │
    │   FAILURE 2: Blaming downstream agents for coordinator failures       │
    │   ───────────────────────────────────────────────────────               │
    │   If synthesis agent produces wrong output, check if coordinator      │
    │   stripped metadata before passing content!                           │
    │                                                                         │
    │   ─────────────────────────────────────────────────────────────────── │
    │                                                                         │
    │   FAILURE 3: Proposing tool fixes when message composition is issue   │
    │   ─────────────────────────────────────────────────────────────         │
    │   The coordinator's PROMPT must instruct subagent to use tools,       │
    │   not just give it access to tools!                                   │
    │                                                                         │
    │   ─────────────────────────────────────────────────────────────────── │
    │                                                                         │
    │   FAILURE 4: Sequential spawning for tasks that could run parallel    │
    │   ───────────────────────────────────────────────────────────           │
    │   Independent tasks should ALWAYS run in parallel!                    │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘


WHAT THIS FOLDER COVERS
════════════════════════

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   practice_01_context_passing_basics.py                                │
    │   ├─ The golden rule: subagents don't auto-inherit context            │
    │                                                                         │
    │   practice_02_attribution_failure.py                                   │
    │   ├─ Real case: synthesis agent loses citations                       │
    │   └─ Solution: Pass structured metadata with content                 │
    │                                                                         │
    │   practice_03_agent_tool_gate.py                                      │
    │   ├─ Must include "Agent" in allowedTools to spawn subagents          │
    │   └─ Parallel vs sequential spawning                                │
    │                                                                         │
    │   practice_04_fork_vs_resume.py                                        │
    │   ├─ fork_session = branching (exploration)                          │
    │   └─ --resume = linear continuation (pickup)                          │
    │                                                                         │
    │   practice_05_common_guardrail_failures.py                            │
    │   ├─ 4 critical mistakes to avoid                                    │
    │   └─ Correct patterns to follow                                       │
    │                                                                         │
    │   TEMPLATE.py                                                         │
    │   └─ Starting template with context passing patterns                  │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘

"""

# ═══════════════════════════════════════════════════════════════════════════
# KEY CONCEPTS SUMMARY
# ═══════════════════════════════════════════════════════════════════════════

"""
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   KEY RULES:                                                            │
│                                                                         │
│   1. SUBAGENTS HAVE ISOLATED CONTEXT                                    │
│      - Never assume automatic context inheritance                      │
│      - Always pass explicit context to every subagent                   │
│                                                                         │
│   2. PASS STRUCTURED METADATA                                          │
│      - Source, confidence, agent name, timestamp                      │
│      - Enables attribution and traceability                            │
│                                                                         │
│   3. MUST INCLUDE "Agent" IN allowedTools                               │
│      - Required to spawn subagents                                      │
│      - Binary requirement, not optional                                │
│                                                                         │
│   4. USE PARALLEL SPAWNING FOR INDEPENDENT TASKS                        │
│      - Much more efficient than sequential                             │
│                                                                         │
│   5. fork_session = BRANCHING, --resume = CONTINUING                    │
│      - Different tools for different purposes                          │
│                                                                         │
│   6. CHECK ROOT CAUSE BEFORE BLAMING DOWNSTREAM AGENTS                  │
│      - Coordinator context passing failures ≠ subagent failures         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
"""