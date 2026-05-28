"""
================================================================================
PRACTICE 5: COMMON GUARDRAIL FAILURES
================================================================================

Four critical mistakes to avoid in multi-agent systems:
    1. Assuming subagents automatically access coordinator history
    2. Blaming downstream agents for context passing failures
    3. Proposing tool fixes when the real issue is message composition
    4. Sequential spawning for tasks that could run parallel

This file demonstrates each failure and the correct approach.
================================================================================
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


def failure_1_assume_auto_context():
    """
    FAILURE 1: Assuming subagents automatically access coordinator history.
    """
    print("\n" + "=" * 70)
    print("FAILURE 1: Assuming Automatic Context Access")
    print("=" * 70)

    print("""
┌─────────────────────────────────────────────────────────────────┐
│  WRONG ASSUMPTION:                                              │
│                                                                 │
│  "I already told the coordinator about the user's question,    │
│   so all subagents will automatically know it"                  │
│                                                                 │
│  Reality:                                                       │
│  - Subagents do NOT see coordinator history                     │
│  - Subagents do NOT see other subagent outputs automatically    │
│  - Subagent A cannot see Subagent B's work                     │
│  - Everything must be EXPLICITLY passed                          │
└─────────────────────────────────────────────────────────────────┘
""")

    print("\n[WRONG CODE]")
    print("-" * 50)
    print("""
# Coordinator spawns subagent
spawn_agent(
    description="Write email based on user's request",
    # User's original question is NOT automatically included!
    # Agent doesn't know who the user is or what they asked!
)
""")

    print("\n[CORRECT CODE]")
    print("-" * 50)
    print("""
# Coordinator spawns subagent WITH EXPLICIT context
spawn_agent(
    description="Write email based on user's request",
    context={
        "user_request": "User asked for a refund on order #12345",
        "user_name": "John Smith",
        "user_email": "john@example.com",
        "order_details": {...}
    }
)
""")


def failure_2_blame_wrong_agent():
    """
    FAILURE 2: Blaming downstream agents for context passing failures.
    """
    print("\n" + "=" * 70)
    print("FAILURE 2: Blaming Downstream Agents")
    print("=" * 70)

    print("""
┌─────────────────────────────────────────────────────────────────┐
│  SITUATION:                                                     │
│                                                                 │
│  Synthesis Agent produces wrong answer.                        │
│  Blame is assigned to Synthesis Agent.                          │
│                                                                 │
│  Root Cause Investigation:                                     │
│                                                                 │
│  Synthesis Agent received:                                      │
│    - "AAPL revenue grew 8%" ← No source!                       │
│    - "Market conditions were tough" ← No context!              │
│                                                                 │
│  Research Agent 1: Provided source TechNews.com ✓               │
│  Research Agent 2: Provided source MarketWatch ✓                 │
│                                                                 │
│  Coordinator: Stripped all metadata! ❌                         │
│                                                                 │
│  THE COORDINATOR IS THE PROBLEM, NOT THE SYNTHESIS AGENT!       │
└─────────────────────────────────────────────────────────────────┘
""")

    print("\nThe pattern:")
    print("    Problem appears in Agent C's output")
    print("    Agent C is blamed")
    print("    But root cause is Agent A or Coordinator")
    print("    Investigation finds: context passing was broken!")


def failure_3_wrong_fix():
    """
    FAILURE 3: Proposing tool fixes when message composition is the issue.
    """
    print("\n" + "=" * 70)
    print("FAILURE 3: Wrong Fix - Adding Tools")
    print("=" * 70)

    print("""
┌─────────────────────────────────────────────────────────────────┐
│  PROBLEM: Subagent doesn't have access to database             │
│                                                                 │
│  WRONG FIX: Add database tool to subagent's allowedTools        │
│                                                                 │
│  Why it's wrong:                                                │
│    - Subagent already has a database tool                        │
│    - Subagent is not USING it because...                         │
│    - The coordinator's PROMPT doesn't instruct it to query!     │
│                                                                 │
│  CORRECT FIX: Fix the message composition in the coordinator   │
│                                                                 │
│  Before: "Research competitor pricing"                          │
│  After:  "Research competitor pricing by querying the database.  │
│           The database contains tables: products, prices.        │
│           Query relevant tables and summarize findings."         │
└─────────────────────────────────────────────────────────────────┘
""")

    print("\nTool access ≠ Instruction to use")
    print("    You can have ALL the tools but still not use them")
    print("    The coordinator's prompt must INSTRUCT subagent to use tools")


def failure_4_sequential_for_parallel():
    """
    FAILURE 4: Sequential spawning when parallel would work.
    """
    print("\n" + "=" * 70)
    print("FAILURE 4: Sequential Spawning for Parallel Tasks")
    print("=" * 70)

    print("""
┌─────────────────────────────────────────────────────────────────┐
│  TASK: Research 5 different topics (completely independent)      │
│                                                                 │
│  WRONG: Sequential (Takes 5x as long)                          │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  1. Spawn Researcher Topic 1 ──► Wait ──► Get results          │
│  2. Spawn Researcher Topic 2 ──► Wait ──► Get results          │
│  3. Spawn Researcher Topic 3 ──► Wait ──► Get results          │
│  4. Spawn Researcher Topic 4 ──► Wait ──► Get results          │
│  5. Spawn Researcher Topic 5 ──► Wait ──► Get results          │
│                                                                 │
│  Total time: 5 × research_time                                 │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│  CORRECT: Parallel (Takes 1× as long)                          │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  1. Spawn ALL 5 Researchers at once!                           │
│  2. Wait for all results                                       │
│                                                                 │
│  Total time: 1 × max(research_time)                            │
└─────────────────────────────────────────────────────────────────┘
""")

    print("\nAsk before spawning sequentially:")
    print("    'Are these tasks independent? Can they run simultaneously?'")
    print("    If YES: Spawn in parallel!")


def show_correct_pattern():
    """
    Show the correct pattern that avoids all failures.
    """
    print("\n" + "=" * 70)
    print("CORRECT PATTERN - Avoiding All Failures")
    print("=" * 70)

    print("""
┌─────────────────────────────────────────────────────────────────┐
│  COORDINATOR (correct implementation)                           │
│                                                                 │
│  1. EXPLICIT context passing                                     │
│     - Pass ALL needed info to each subagent                    │
│     - Include: task, background, examples, constraints           │
│     - Subagents cannot guess what they need!                   │
│                                                                 │
│  2. Structured metadata                                         │
│     - Always include source attribution                         │
│     - Include confidence levels                                 │
│     - Include which agent produced the output                   │
│                                                                 │
│  3. Complete instructions in messages                          │
│     - Don't assume subagent knows what tools to use             │
│     - Tell subagent EXACTLY what to do with each tool          │
│     - Message composition > Tool access                         │
│                                                                 │
│  4. Parallel for independent                                   │
│     - Spawn independent tasks simultaneously                    │
│     - Only sequential when tasks depend on each other          │
│                                                                 │
│  5. Root cause analysis                                         │
│     - When something breaks, investigate the chain             │
│     - Check: coordinator → subagent outputs → next subagent   │
│     - Don't blindly blame the last agent in the chain          │
└─────────────────────────────────────────────────────────────────┘
""")


def summary_checklist():
    """
    Quick checklist for avoiding guardrail failures.
    """
    print("\n" + "=" * 70)
    print("QUICK CHECKLIST - Avoiding Guardrail Failures")
    print("=" * 70)

    print("""
Before shipping multi-agent code, verify:

□ Context Explicit?
    - Does each subagent have ALL the info it needs?
    - Did we pass user history, preferences, constraints?
    - Did we include examples or templates?

□ Metadata Included?
    - Are sources cited in subagent outputs?
    - Is confidence level provided?
    - Can we trace which agent produced each finding?

□ Instructions Complete?
    - Does the prompt tell subagent WHEN to use tools?
    - Are tool output formats specified?
    - Are edge cases handled in the prompt?

□ Parallelization Considered?
    - Are there independent tasks that could run simultaneously?
    - Are we spawning sequentially when we could parallel?

□ Root Cause Analysis Done?
    - If there's a bug, did we trace back through the chain?
    - Are we blaming the right agent?
    - Is the coordinator at fault, not the downstream agents?
""")


if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    print("\n" + "=" * 70)
    print("PRACTICE 5: COMMON GUARDRAIL FAILURES")
    print("=" * 70)
    print("""
This program teaches four critical mistakes in multi-agent systems:
    1. Assuming automatic context access
    2. Blaming downstream agents incorrectly
    3. Fixing with tools instead of messages
    4. Sequential spawning for parallel tasks

Learn these to avoid common bugs in production systems!
""")

    failure_1_assume_auto_context()
    failure_2_blame_wrong_agent()
    failure_3_wrong_fix()
    failure_4_sequential_for_parallel()
    show_correct_pattern()
    summary_checklist()

    print("""
================================================================================
WHAT JUST HAPPENED?
================================================================================

    1. We learned 4 common guardrail failures:
       - Failure 1: Subagents don't auto-inherit context
       - Failure 2: Downstream agents blamed for coordinator mistakes
       - Failure 3: Adding tools when message composition is the issue
       - Failure 4: Sequential spawning when parallel would work

    2. We saw the correct pattern that avoids all failures:
       - Explicit context passing
       - Structured metadata
       - Complete instructions
       - Parallel for independent tasks
       - Root cause analysis

    3. We got a checklist to verify our multi-agent code

    EXAM TIPS:
    - Subagents have ISOLATED context - never assume automatic access
    - When synthesis fails, check coordinator's context passing first
    - Tool access ≠ Instruction to use - messages must instruct!
    - Independent tasks should ALWAYS run in parallel
================================================================================
""")
    print("\n" + "=" * 70)
    print("PROGRAM COMPLETE!")
    print("=" * 70)
