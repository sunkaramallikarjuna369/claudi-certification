"""
================================================================================
PRACTICE 1: THREE SESSION MANAGEMENT APPROACHES
================================================================================

Three ways to handle session state and resumption:

    1. --resume: Full conversation history restored
    2. fork_session: Independent branching from shared baseline
    3. Fresh start + summary: New session with curated knowledge injected

Know when to use each approach!
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


def demonstrate_resume():
    """
    Approach 1: --resume <session-name>
    Restores full conversation history including all tool results.
    """
    print("\n" + "=" * 70)
    print("APPROACH 1: --resume <session-name>")
    print("=" * 70)

    print("""
┌─────────────────────────────────────────────────────────────────┐
│  --resume SESSION-NAME                                          │
│                                                                 │
│  What it does:                                                 │
│  • Restores COMPLETE conversation history                       │
│  • Includes ALL tool results from previous session             │
│  • Agent has context of everything that happened               │
│                                                                 │
│  When to use:                                                  │
│  ✓ Prior context remains VALID                                  │
│  ✓ No files have changed since last session                    │
│  ✓ Need to continue exact work from where you left off        │
│                                                                 │
│  Example:                                                      │
│  $ claude --session research-2024 --resume                    │
│  "Continue with the analysis we were doing yesterday"          │
└─────────────────────────────────────────────────────────────────┘
""")


def demonstrate_fork_session():
    """
    Approach 2: fork_session
    Creates independent branching from a shared baseline.
    """
    print("\n" + "=" * 70)
    print("APPROACH 2: fork_session")
    print("=" * 70)

    print("""
┌─────────────────────────────────────────────────────────────────┐
│  fork_session [--name NEW-BRANCH-NAME]                         │
│                                                                 │
│  What it does:                                                 │
│  • Creates INDEPENDENT branches from current state             │
│  • Each branch operates SEPARATELY                             │
│  • Changes in one branch do NOT affect the other               │
│                                                                 │
│  When to use:                                                  │
│  ✓ Exploring DIVERGENT approaches                               │
│  ✓ A/B testing different strategies                            │
│  ✓ Want to try approach A AND approach B simultaneously        │
│                                                                 │
│  Example:                                                      │
│                                                                 │
│  Main Session "refactor" ──────┬──► Branch A: "Use microservices"│
│                                │                                  │
│                                └──► Branch B: "Use monolith"     │
│                                                                 │
│  Both explore different architectures without affecting        │
│  each other!                                                   │
└─────────────────────────────────────────────────────────────────┘
""")


def demonstrate_fresh_start():
    """
    Approach 3: Fresh start with summary injection
    New session with structured summary of prior findings.
    """
    print("\n" + "=" * 70)
    print("APPROACH 3: FRESH START + SUMMARY INJECTION")
    print("=" * 70)

    print("""
┌─────────────────────────────────────────────────────────────────┐
│  Fresh session + Injected summary                              │
│                                                                 │
│  What it does:                                                 │
│  • Starts a COMPLETELY NEW session                             │
│  • NO stale tool results in history                             │
│  • Curated knowledge transfers via structured summary         │
│  • Clean slate with important context                          │
│                                                                 │
│  When to use:                                                  │
│  ✓ Files have CHANGED since last session                      │
│  ✓ Long session with cluttered history                         │
│  ✓ Dependency updates since last session                       │
│  ✓ Need to move forward without stale data                     │
│                                                                 │
│  Example:                                                      │
│                                                                 │
│  OLD SESSION found:                                           │
│  - auth.ts: uses MD5 hashing (security issue!)                 │
│  - database.ts: has SQL injection vulnerability               │
│                                                                 │
│  NEW SESSION starts with:                                      │
│  "Prior analysis found: auth.ts uses MD5, database.ts has     │
│   SQL injection. Modified files: auth.ts, database.ts.       │
│   Please re-analyze these files."                             │
└─────────────────────────────────────────────────────────────────┘
""")


def show_comparison():
    """
    Side-by-side comparison of the three approaches.
    """
    print("\n" + "=" * 70)
    print("COMPARISON: All Three Approaches")
    print("=" * 70)

    print("""
┌──────────────┬────────────────────────────────────────────────────────────┐
│  APPROACH    │  CHARACTERISTICS                                          │
├──────────────┼────────────────────────────────────────────────────────────┤
│              │                                                            │
│  --resume    │  • Full conversation history restored                     │
│              │  • ALL tool results included                               │
│              │  • Stale if files changed!                                 │
│              │  • Use when: context still valid                           │
│              │                                                            │
├──────────────┼────────────────────────────────────────────────────────────┤
│              │                                                            │
│  fork_session│  • Creates INDEPENDENT branches                            │
│              │  • Changes don't affect each other                         │
│              │  • For exploration/testing different paths               │
│              │  • Use when: divergent approaches needed                   │
│              │                                                            │
├──────────────┼────────────────────────────────────────────────────────────┤
│              │                                                            │
│  Fresh start │  • New session, no stale tool results                     │
│  + summary   │  • Curated knowledge transferred                           │
│              │  • Specify changed files for targeted re-analysis         │
│              │  • Use when: files changed, history cluttered             │
│              │                                                            │
└──────────────┴────────────────────────────────────────────────────────────┘
""")


def show_key_difference():
    """
    Highlight the key difference between approaches.
    """
    print("\n" + "=" * 70)
    print("KEY DIFFERENCE: Tool Results")
    print("=" * 70)

    print("""
┌─────────────────────────────────────────────────────────────────┐
│  --resume:                                                     │
│  ────────────────────────────────────────────────────────────  │
│  Conversation includes:                                         │
│  • "I analyzed auth.ts" → tool result with OLD content         │
│  • "I found vulnerability" → based on OLD file version        │
│  • Now file is changed, but tool result says OLD findings      │
│                                                                 │
│  PROBLEM: Agent has stale data mixed with new data!            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  Fresh start + summary:                                        │
│  ────────────────────────────────────────────────────────────  │
│  Conversation includes:                                         │
│  • "Prior analysis found: auth.ts uses MD5" (knowledge)        │
│  • "Modified files: auth.ts" (instruction)                     │
│  • Agent re-analyzes auth.ts → gets FRESH results              │
│                                                                 │
│  SOLUTION: No stale tool results, just curated knowledge!      │
└─────────────────────────────────────────────────────────────────┘
""")


if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    print("\n" + "=" * 70)
    print("PRACTICE 1: THREE SESSION MANAGEMENT APPROACHES")
    print("=" * 70)
    print("""
This program teaches the three ways to handle session state:
    1. --resume: Full history restored (watch for stale data!)
    2. fork_session: Independent branches (for exploration)
    3. Fresh start + summary: New session with curated knowledge
""")

    demonstrate_resume()
    demonstrate_fork_session()
    demonstrate_fresh_start()
    show_comparison()
    show_key_difference()

    print("""
================================================================================
WHAT JUST HAPPENED?
================================================================================

    1. We learned about --resume:
       - Restores COMPLETE conversation history
       - Includes ALL tool results
       - Problem: stale if files have changed!

    2. We learned about fork_session:
       - Creates INDEPENDENT branches
       - Changes don't affect each other
       - Use for: exploring different approaches

    3. We learned about Fresh start + summary:
       - New session with curated knowledge
       - No stale tool results
       - Specify changed files for targeted re-analysis

    4. We saw the KEY DIFFERENCE:
       - --resume has stale tool results mixed with new data
       - Fresh start has curated knowledge, no stale results

    EXAM TIPS:
    - Files changed? → Fresh start + summary (NOT --resume!)
    - Exploring approaches? → fork_session
    - No changes? → --resume is fine
================================================================================
""")
    print("\n" + "=" * 70)
    print("PROGRAM COMPLETE!")
    print("=" * 70)