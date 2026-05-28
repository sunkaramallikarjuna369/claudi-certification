"""
================================================================================
PRACTICE 2: THE STALE CONTEXT PROBLEM
================================================================================

When you resume a session, the entire conversation history is restored,
including every tool result from the previous session.

This causes agents to reason from outdated file contents alongside current
data, producing contradictory advice!
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


def demonstrate_stale_context():
    """
    Show how stale context causes problems.
    """
    print("\n" + "=" * 70)
    print("THE STALE CONTEXT PROBLEM")
    print("=" * 70)

    print("""
┌─────────────────────────────────────────────────────────────────┐
│  SCENARIO: Resuming after file changes                          │
│                                                                 │
│  DAY 1: Initial Analysis                                        │
│  ────────────────────────────────────────────────────────────  │
│  • User: "Analyze auth.ts for security issues"                │
│  • Agent reads auth.ts → finds: "Uses MD5 for hashing"       │
│  • Agent: "You should upgrade from MD5 to bcrypt"             │
│  • Tool result stored in conversation:                         │
│    "File auth.ts: uses MD5 hashing"                           │
│                                                                 │
│  User implements the fix (changes auth.ts)                      │
│                                                                 │
│  DAY 2: Resume Session                                         │
│  ────────────────────────────────────────────────────────────  │
│  • User: "claude --resume day1-session"                       │
│  • Conversation history restored with tool results!             │
│  • Tool result still says: "auth.ts uses MD5" ← STALE!      │
│                                                                 │
│  • User: "Continue analyzing auth.ts"                         │
│  • Agent reads NEW auth.ts → finds: "Uses bcrypt" ← NEW!    │
│  • BUT Agent also has OLD tool result: "uses MD5"            │
│  • Agent gets confused!                                        │
└─────────────────────────────────────────────────────────────────┘
""")


def show_contradictory_behavior():
    """
    Show how stale context leads to contradictory behavior.
    """
    print("\n" + "=" * 70)
    print("CONTRADICTORY BEHAVIOR FROM STALE CONTEXT")
    print("=" * 70)

    print("""
┌─────────────────────────────────────────────────────────────────┐
│  RESUMED SESSION with stale tool results:                      │
│                                                                 │
│  User: "What's the current state of auth.ts?"                  │
│                                                                 │
│  Agent considers:                                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Tool result from Day 1: "auth.ts uses MD5 hashing"   │   │
│  │ Fresh read of auth.ts: "auth.ts uses bcrypt"          │   │
│  │                                                         │   │
│  │ Which one is true?!                                    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  POSSIBLE CONTRADICTORY RESPONSES:                             │
│                                                                 │
│  ❌ "Your auth.ts uses MD5 which is insecure..."              │
│     (Based on stale tool result, WRONG!)                       │
│                                                                 │
│  ❌ "auth.ts uses bcrypt, which is good..."                   │
│     (Fresh read correct, but may conflict with other stale)   │
│                                                                 │
│  ❌ "It seems auth.ts was changed from MD5 to bcrypt..."     │
│     (Acknowledging conflict, but still confusing)              │
│                                                                 │
│  The agent is confused because it has CONFLICTING information!
└─────────────────────────────────────────────────────────────────┘
""")


def show_concrete_example():
    """
    Show a concrete example of the problem.
    """
    print("\n" + "=" * 70)
    print("CONCRETE EXAMPLE: File Deletion")
    print("=" * 70)

    print("""
┌─────────────────────────────────────────────────────────────────┐
│  DAY 1: Codebase Analysis                                      │
│  ────────────────────────────────────────────────────────────  │
│  Tool result: "Found legacy_auth.py - deprecated module"      │
│  Tool result: "Found old_database.py - will be removed"       │
│                                                                 │
│  User deletes these files as planned                           │
│                                                                 │
│  DAY 2: Resume Session                                         │
│  ────────────────────────────────────────────────────────────  │
│  User: "Continue with the refactoring"                         │
│                                                                 │
│  Agent considers:                                              │
│  Tool result: "legacy_auth.py exists" ← STALE!               │
│  File system: "legacy_auth.py does NOT exist" ← TRUE!        │
│                                                                 │
│  Agent: "Let's update legacy_auth.py..."                      │
│  Error: "File not found"                                       │
│                                                                 │
│  OR WORSE:                                                    │
│  Agent: "Good, legacy_auth.py is deprecated. I recommend..."  │
│  (Recommending work on a file that doesn't exist!)             │
└─────────────────────────────────────────────────────────────────┘
""")


def show_more_problems():
    """
    Show additional problems caused by stale context.
    """
    print("\n" + "=" * 70)
    print("MORE PROBLEMS FROM STALE CONTEXT")
    print("=" * 70)

    print("""
┌─────────────────────────────────────────────────────────────────┐
│  PROBLEM 1: Recommending Already-Completed Changes             │
│                                                                 │
│  Stale: "auth.ts needs input validation"                     │
│  Fresh: User already added input validation                     │
│  Agent: "You should add input validation..."                  │
│  User: "I already did that!"                                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  PROBLEM 2: Conflicting File Contents                         │
│                                                                 │
│  Stale tool result says: "database.ts has connection pooling"│
│  Fresh read shows: "database.ts uses direct connections"     │
│  Agent is confused about actual implementation                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  PROBLEM 3: Reasoning from Outdated Structure                 │
│                                                                 │
│  Stale: "project has 20 files in src/ directory"             │
│  Fresh: After refactoring, project has 15 files              │
│  Agent references non-existent files in explanations           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  PROBLEM 4: Dependency Confusion                              │
│                                                                 │
│  Stale: "uses_dependencies: lodash v3, express v4"          │
│  Fresh: User upgraded to lodash v5, express v5               │
│  Agent recommends changes for OLD dependency versions         │
└─────────────────────────────────────────────────────────────────┘
""")


def show_why_naive_fix_fails():
    """
    Show why just asking agent to re-read files is not enough.
    """
    print("\n" + "=" * 70)
    print("WHY NAIVE FIX FAILS")
    print("=" * 70)

    print("""
┌─────────────────────────────────────────────────────────────────┐
│  NAIVE FIX (Not Good Enough):                                  │
│                                                                 │
│  User: "claude --resume session"                               │
│  User: "auth.ts has been modified, re-read it please"         │
│                                                                 │
│  What happens:                                                 │
│  1. Conversation history still has STALE tool results          │
│  2. Agent re-reads auth.ts → has fresh content                │
│  3. Agent still has BOTH stale and fresh in context           │
│  4. Agent may still get confused about which is correct         │
│  5. Contradictory advice may still occur                      │
│                                                                 │
│  The stale tool results are STILL IN THE CONVERSATION!        │
│  Agent still reasons from outdated information!                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  THE PROBLEM WITH JUST RE-READING:                            │
│                                                                 │
│  • Old tool result: "auth.ts uses MD5" ← Still in history!   │
│  • New read: "auth.ts uses bcrypt" ← Fresh                   │
│  • Agent sees BOTH and gets confused                           │
│  • Can't tell which is current state                           │
│                                                                 │
│  Simply asking to re-read DOESN'T CLEAR the stale data!      │
└─────────────────────────────────────────────────────────────────┘
""")


if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    print("\n" + "=" * 70)
    print("PRACTICE 2: THE STALE CONTEXT PROBLEM")
    print("=" * 70)
    print("""
This program teaches about the stale context problem:
When you resume, ALL tool results are restored, even if files changed.
This causes contradictory advice and confused agents!
""")

    demonstrate_stale_context()
    show_contradictory_behavior()
    show_concrete_example()
    show_more_problems()
    show_why_naive_fix_fails()

    print("""
================================================================================
WHAT JUST HAPPENED?
================================================================================

    1. We learned about the STALE CONTEXT PROBLEM:
       - Resuming restores ALL tool results
       - Files may have changed since tool results were generated
       - Agent has conflicting information: stale vs fresh

    2. We saw CONTRADICTORY BEHAVIOR:
       - Agent gets confused by having both old and new data
       - May recommend changes already completed
       - May reference files that no longer exist

    3. We saw CONCRETE EXAMPLES:
       - File deletion confusion
       - Recommending completed changes
       - Conflicting file contents
       - Outdated structure references
       - Old dependency versions

    4. We learned why NAIVE FIX FAILS:
       - Just asking to re-read doesn't clear stale data
       - Old tool results still in conversation history
       - Agent still reasons from both stale and fresh

    KEY INSIGHT:
    Simply resuming and asking to re-read changed files is
    NOT ENOUGH. The stale tool results remain in the history!

    THE FIX: Fresh start with structured summary injection
    (covered in the next practice)
================================================================================
""")
    print("\n" + "=" * 70)
    print("PROGRAM COMPLETE!")
    print("=" * 70)