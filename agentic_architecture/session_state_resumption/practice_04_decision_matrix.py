"""
================================================================================
PRACTICE 4: DECISION MATRIX - WHICH APPROACH TO USE?
================================================================================

When should you use --resume, fork_session, or fresh start + summary?

This decision matrix will help you choose the right approach.
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


def show_decision_matrix():
    """
    Show the decision matrix for session approaches.
    """
    print("\n" + "=" * 70)
    print("DECISION MATRIX: Which Approach to Use?")
    print("=" * 70)

    print("""
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DECISION MATRIX                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  SCENARIO                              │  BEST APPROACH                    │
│  ─────────────────────────────────────┼────────────────────────────────── │
│                                                                             │
│  Work from yesterday, no files        │  --resume                        │
│  changed, continue exact work         │  (Full history still valid)       │
│                                      │                                   │
│  ─────────────────────────────────────┼────────────────────────────────── │
│                                                                             │
│  Comparing two refactoring             │  fork_session                    │
│  approaches (microservices vs         │  (Independent branches)           │
│  monolith)                             │                                   │
│                                      │                                   │
│  ─────────────────────────────────────┼────────────────────────────────── │
│                                                                             │
│  Resuming after modifying 3 of        │  Fresh start + summary           │
│  50 files                              │  (Only modified files need        │
│                                      │   re-analysis)                   │
│  ─────────────────────────────────────┼────────────────────────────────── │
│                                                                             │
│  Long session with cluttered           │  Fresh start + summary           │
│  history                               │  (Start clean, inject knowledge)   │
│                                      │                                   │
│  ─────────────────────────────────────┼────────────────────────────────── │
│                                                                             │
│  Resuming after dependency            │  Fresh start + summary           │
│  updates (package.json changed)       │  (Need fresh analysis of          │
│                                      │   dependency impact)              │
│  ─────────────────────────────────────┼────────────────────────────────── │
│                                                                             │
│  Want to explore two different        │  fork_session                    │
│  approaches from same starting        │  (Branching for exploration)     │
│  point                                │                                   │
│                                      │                                   │
│  ─────────────────────────────────────┼────────────────────────────────── │
│                                                                             │
│  Files definitely haven't changed      │  --resume                        │
│  (sure about context validity)        │  (Full history is trustworthy)   │
│                                      │                                   │
└─────────────────────────────────────────────────────────────────────────────┘
""")


def show_detailed_scenarios():
    """
    Show detailed scenarios with reasoning.
    """
    print("\n" + "=" * 70)
    print("DETAILED SCENARIOS")
    print("=" * 70)

    scenarios = [
        {
            "title": "SCENARIO 1: No changes, continue work",
            "situation": "You were analyzing a codebase yesterday. No files have changed since then. You want to continue from where you left off.",
            "best_approach": "--resume",
            "reasoning": "Full conversation history is still valid. No files changed, so tool results are accurate. Just resume and continue.",
            "command": "$ claude --session analysis-yesterday --resume"
        },
        {
            "title": "SCENARIO 2: Some files changed",
            "situation": "You analyzed 50 files. You modified 3 of them (fixed security issues). Now you want to continue.",
            "best_approach": "Fresh start + summary",
            "reasoning": "Cannot use --resume because 3 files changed (stale tool results). Start fresh, inject summary of findings, re-analyze only the 3 modified files.",
            "command": "$ claude --session analysis-day2\n# Inject summary with changed files listed"
        },
        {
            "title": "SCENARIO 3: Exploring alternatives",
            "situation": "You need to compare two different refactoring approaches: microservices vs monolithic architecture. Want to explore both options.",
            "best_approach": "fork_session",
            "reasoning": "Need to explore divergent paths. fork_session creates independent branches. Can work on both approaches without affecting each other.",
            "command": "$ claude --session refactor\n/fork microservices\n/fork monolith"
        },
        {
            "title": "SCENARIO 4: Cluttered history",
            "situation": "You had a long debugging session. 100+ messages, many tool calls, got off track multiple times. History is messy.",
            "best_approach": "Fresh start + summary",
            "reasoning": "Resume would restore all the mess. Fresh start gives you a clean slate. Inject a summary of key findings to preserve important knowledge.",
            "command": "$ claude --session clean-session\n# Inject distilled knowledge from messy session"
        },
        {
            "title": "SCENARIO 5: Dependency updates",
            "situation": "You were analyzing code. Then ran 'npm update' or 'pip install --upgrade'. Dependencies changed.",
            "best_approach": "Fresh start + summary",
            "reasoning": "Dependencies changed → may affect code behavior, compatibility, security. Need fresh analysis of how new dependencies impact the codebase.",
            "command": "$ claude --session after-updates\n# Inject prior findings, note dependency updates"
        },
        {
            "title": "SCENARIO 6: A/B testing approaches",
            "situation": "You want to test if Option A or Option B is better for solving a problem. Need to try both.",
            "best_approach": "fork_session",
            "reasoning": "fork_session creates independent branches. Work on Option A in one branch, Option B in another. Compare results without interference.",
            "command": "$ claude --session test-ab\n/fork option-a\n/fork option-b"
        }
    ]

    for scenario in scenarios:
        print(f"\n{'─' * 70}")
        print(f"{scenario['title']}")
        print(f"{'─' * 70}")
        print(f"\n   Situation: {scenario['situation']}")
        print(f"\n   Best approach: {scenario['best_approach']}")
        print(f"   Why: {scenario['reasoning']}")
        print(f"\n   Command:\n   {scenario['command']}")


def show_quick_reference():
    """
    Show quick reference for decision making.
    """
    print("\n" + "=" * 70)
    print("QUICK REFERENCE")
    print("=" * 70)

    print("""
┌─────────────────────────────────────────────────────────────────┐
│  ASK YOURSELF:                                                 │
│                                                                 │
│  1. Have files changed since last session?                     │
│     YES → Fresh start + summary                                 │
│     NO  → Continue to question 2                                │
│                                                                 │
│  2. Do you need to explore divergent approaches?               │
│     YES → fork_session                                         │
│     NO  → Continue to question 3                                │
│                                                                 │
│  3. Is your conversation history cluttered/too long?            │
│     YES → Fresh start + summary                                 │
│     NO  → --resume                                              │
│                                                                 │
│  QUICK DECISION:                                              │
│                                                                 │
│  Files changed?          → Fresh start + summary               │
│  Exploring alternatives?  → fork_session                        │
│  Everything still valid?  → --resume                            │
└─────────────────────────────────────────────────────────────────┘
""")


def show_key_rules():
    """
    Show key rules to remember.
    """
    print("\n" + "=" * 70)
    print("KEY RULES TO REMEMBER")
    print("=" * 70)

    print("""
┌─────────────────────────────────────────────────────────────────┐
│  RULE 1: Files changed? → DON'T use --resume!                  │
│                                                                 │
│  --resume restores ALL tool results, including stale ones.       │
│  This causes contradictory advice and confused agents.          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  RULE 2: fork_session = branching, not resuming                 │
│                                                                 │
│  fork_session creates INDEPENDENT branches.                      │
│  --resume continues a specific session linearly.                │
│  These are different tools for different purposes!             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  RULE 3: Transfer KNOWLEDGE, not tool results                   │
│                                                                 │
│  Fresh start + summary:                                        │
│  - Inject what you LEARNED (knowledge)                         │
│  - NOT what tools returned (stale results)                     │
│  - Agent rebuilds understanding from fresh context               │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  RULE 4: Specify changed files for targeted re-analysis         │
│                                                                 │
│  "Modified files: auth.ts, database.ts"                        │
│  This tells agent exactly what needs fresh analysis.            │
│  Saves time, ensures accuracy.                                 │
└─────────────────────────────────────────────────────────────────┘
""")


def show_exam_tips():
    """
    Show exam-specific tips.
    """
    print("\n" + "=" * 70)
    print("EXAM TIPS")
    print("=" * 70)

    print("""
┌─────────────────────────────────────────────────────────────────┐
│  EXAM TRAP 1: "Just resume and re-read changed files"        │
│                                                                 │
│  WRONG! This still has stale tool results in history.         │
│  Stale data is NOT cleared by re-reading files!               │
│                                                                 │
│  CORRECT: Fresh start + summary injection                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  EXAM TRAP 2: Confusing fork_session with --resume            │
│                                                                 │
│  --resume: Continues a specific session linearly               │
│  fork_session: Creates independent branches                      │
│                                                                 │
│  For exploring alternatives: fork_session                      │
│  For continuing work: --resume (if context valid)              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  EXAM TRAP 3: Using --resume when files changed               │
│                                                                 │
│  If scenario says "files were modified", --resume is WRONG.  │
│  Must use fresh start + summary to avoid stale context!       │
│                                                                 │
│  The exam tests whether you recognize this!                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  EXAM TRAP 4: Forgetting to specify changed files             │
│                                                                 │
│  Fresh start + summary is correct, but...                       │
│  You must specify WHICH files changed!                         │
│  Without this, agent doesn't know what to re-analyze          │
└─────────────────────────────────────────────────────────────────┘
""")


if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    print("\n" + "=" * 70)
    print("PRACTICE 4: DECISION MATRIX - WHICH APPROACH TO USE?")
    print("=" * 70)
    print("""
This program provides a decision matrix for choosing the right
session management approach based on your scenario.
""")

    show_decision_matrix()
    show_detailed_scenarios()
    show_quick_reference()
    show_key_rules()
    show_exam_tips()

    print("""
================================================================================
WHAT JUST HAPPENED?
================================================================================

    1. We learned the DECISION MATRIX:
       - No changes, continue work → --resume
       - Files changed → Fresh start + summary
       - Exploring alternatives → fork_session
       - Cluttered history → Fresh start + summary

    2. We saw DETAILED SCENARIOS:
       - 6 different scenarios with reasoning
       - Best approach for each situation
       - Commands to use

    3. We got a QUICK REFERENCE:
       - 3 questions to ask yourself
       - Quick decision tree

    4. We learned KEY RULES:
       - Files changed → DON'T use --resume
       - fork_session = branching, not resuming
       - Transfer knowledge, not tool results
       - Specify changed files

    5. We learned EXAM TIPS:
       - Don't say "resume and re-read"
       - Don't confuse fork_session with --resume
       - Don't use --resume when files changed
       - Always specify changed files in summary

    EXAM TIPS SUMMARY:
    - Files changed? → Fresh start + summary (NOT --resume!)
    - fork_session = divergent exploration
    - --resume = linear continuation (only if context valid)
================================================================================
""")
    print("\n" + "=" * 70)
    print("PROGRAM COMPLETE!")
    print("=" * 70)