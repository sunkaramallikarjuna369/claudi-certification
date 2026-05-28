"""
================================================================================
PRACTICE 3: THE CORRECT FIX - TARGETED RE-ANALYSIS
================================================================================

The correct approach when files have changed:
    1. Start a FRESH session (no stale tool results)
    2. Inject a STRUCTURED SUMMARY of prior findings
    3. Specify WHICH files have changed
    4. Agent re-analyzes only the modified files

This avoids stale context while preserving valuable knowledge!
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


def show_the_correct_approach():
    """
    Show the correct approach to resuming after file changes.
    """
    print("\n" + "=" * 70)
    print("THE CORRECT APPROACH: Fresh Start + Summary Injection")
    print("=" * 70)

    print("""
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: Start a FRESH session                                 │
│  ────────────────────────────────────────────────────────────  │
│                                                                 │
│  $ claude --session new-session  # NEW session, not resumed! │
│                                                                 │
│  No conversation history. No stale tool results.                │
│  Clean slate to work from.                                      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: Inject STRUCTURED SUMMARY of prior findings          │
│  ────────────────────────────────────────────────────────────  │
│                                                                 │
│  "Prior analysis summary:                                     │
│   - auth.ts: Uses MD5 hashing (security issue)              │
│   - database.ts: Has SQL injection vulnerability            │
│   - api-routes.ts: Missing rate limiting                    │
│   - User implemented MD5 fix on Day 1"                       │
│                                                                 │
│  This transfers the KNOWLEDGE, not stale tool results!        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: Specify WHICH files have CHANGED                    │
│  ────────────────────────────────────────────────────────────  │
│                                                                 │
│  "Modified files: auth.ts (fixed MD5 → bcrypt)             │
│                   database.ts (no changes)                   │
│                   api-routes.ts (added rate limiting)       │
│                                                                 │
│  Please re-analyze: auth.ts, api-routes.ts"                │
│                                                                 │
│  Agent knows exactly what to focus on!                        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  STEP 4: Agent RE-ANALYZES only modified files               │
│  ────────────────────────────────────────────────────────────  │
│                                                                 │
│  Agent reads fresh auth.ts → confirms bcrypt fix ✓           │
│  Agent reads fresh api-routes.ts → confirms rate limiting ✓  │
│  Agent combines fresh analysis with prior findings            │
│                                                                 │
│  Result: Complete, current, accurate analysis!                │
└─────────────────────────────────────────────────────────────────┘
""")


def show_vs_naive_approach():
    """
    Compare correct approach vs naive approach.
    """
    print("\n" + "=" * 70)
    print("CORRECT vs NAIVE APPROACH")
    print("=" * 70)

    print("""
┌─────────────────────────────────────────────────────────────────┐
│  NAIVE APPROACH (WRONG):                                       │
│  ────────────────────────────────────────────────────────────  │
│                                                                 │
│  1. Resume session: --resume session-name                    │
│  2. Ask to re-read: "auth.ts changed, re-read it"           │
│                                                                 │
│  Problems:                                                    │
│  ❌ Stale tool results still in conversation history          │
│  ❌ Agent has conflicting old + new data                     │
│  ❌ May still give contradictory advice                      │
│  ❌ Confused about what is current state                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  CORRECT APPROACH (RIGHT):                                    │
│  ────────────────────────────────────────────────────────────  │
│                                                                 │
│  1. Fresh session: --session new-session                     │
│  2. Inject summary: Prior findings + changed files          │
│                                                                 │
│  Benefits:                                                    │
│  ✓ No stale tool results in history                           │
│  ✓ Clean context for fresh analysis                           │
│  ✓ Prior knowledge preserved via summary                       │
│  ✓ Targeted re-analysis of only changed files                │
│  ✓ Complete, current, accurate results                        │
└─────────────────────────────────────────────────────────────────┘
""")


def show_targeted_reanalysis_pattern():
    """
    Show the targeted re-analysis pattern.
    """
    print("\n" + "=" * 70)
    print("TARGETED RE-ANALYSIS PATTERN")
    print("=" * 70)

    print("""
+-----------------------------------------------------------------------+
|  TEMPLATE: What to inject in new session                             |
|                                                                       |
|  [PRIOR ANALYSIS SUMMARY]                                              |
|  - Files analyzed: {list all files from prior session}               |
|  - Key findings: {summarize findings per file}                       |
|  - Changes implemented: {what was fixed since then}                  |
|                                                                        |
|  [MODIFIED FILES - need re-analysis]                                   |
|  - {list files that changed}                                         |
|                                                                        |
|  [UNCHANGED FILES - assumed current]                                   |
|  - {list files that didn't change - can trust prior findings}         |
|                                                                        |
|  [REQUEST]                                                            |
|  Please re-analyze the modified files and update the findings          |
|  based on their current state.                                        |
+-----------------------------------------------------------------------+
""")


def show_example():
    """
    Show a complete example.
    """
    print("\n" + "=" * 70)
    print("COMPLETE EXAMPLE")
    print("=" * 70)

    print("""
┌─────────────────────────────────────────────────────────────────┐
│  DAY 1 SESSION (Original Analysis)                             │
│  ────────────────────────────────────────────────────────────  │
│                                                                 │
│  Files analyzed: 50 files                                     │
│  Key issues found:                                            │
│    - auth.ts: Uses MD5 (security issue)                      │
│    - database.ts: SQL injection vulnerability                │
│    - api-routes.ts: Missing rate limiting                     │
│    - config.ts: Hardcoded credentials                          │
│                                                                 │
│  User implements fixes for MD5 and rate limiting               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  DAY 2 SESSION (Wrong approach - Naive)                       │
│  ────────────────────────────────────────────────────────────  │
│                                                                 │
│  $ claude --resume day1-session                              │
│  > "auth.ts and api-routes.ts were modified, re-analyze"    │
│                                                                 │
│  Result:                                                      │
│  - Agent confused by stale + fresh data                       │
│  - May still reference MD5 findings                          │
│  - May miss some changes                                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  DAY 2 SESSION (Correct approach - Fresh + Summary)           │
│  ────────────────────────────────────────────────────────────  │
│                                                                 │
│  $ claude --session day2-fresh                              │
│                                                                 │
│  First message injected:                                       │
│                                                                 │
│  "PRIOR ANALYSIS (Day 1):                                     │
│   Files analyzed: 50 files                                    │
│   Key issues:                                                 │
│     - auth.ts: Used MD5 hashing                              │
│     - database.ts: SQL injection                              │
│     - api-routes.ts: Missing rate limiting                   │
│     - config.ts: Hardcoded credentials                        │
│                                                                 │
│   FIXES IMPLEMENTED:                                          │
│     - auth.ts: Changed MD5 → bcrypt (Day 1)                 │
│     - api-routes.ts: Added rate limiting (Day 1)            │
│                                                                 │
│   FILES MODIFIED SINCE LAST SESSION:                         │
│     - auth.ts                                                 │
│     - api-routes.ts                                          │
│                                                                 │
│   FILES UNCHANGED (trust prior findings):                    │
│     - database.ts, config.ts, and 46 others                  │
│                                                                 │
│   REQUEST: Re-analyze auth.ts and api-routes.ts only.        │
│   Prior findings for other files are still valid."            │
└─────────────────────────────────────────────────────────────────┘
""")


def show_implementation():
    """
    Show how to implement this pattern.
    """
    print("\n" + "=" * 70)
    print("IMPLEMENTATION: Fresh Session with Summary")
    print("=" * 70)

    print("""
+-----------------------------------------------------------------------+
|  CODE PATTERN:                                                      |
|                                                                       |
|  # 1. Start fresh session                                          |
|  messages = []                                                       |
|                                                                       |
|  # 2. Inject structured summary as first message                   |
|  summary = \"\"\"                                                      |
|  PRIOR ANALYSIS SUMMARY:                                            |
|  - auth.ts: Found MD5 hashing issue                                |
|  - database.ts: Found SQL injection                                |
|  - api-routes.ts: Found missing rate limiting                     |
|                                                                       |
|  CHANGES MADE:                                                      |
|  - auth.ts: Fixed MD5 -> bcrypt                                    |
|  - api-routes.ts: Added rate limiting                             |
|                                                                       |
|  FILES TO RE-ANALYZE:                                              |
|  - auth.ts, api-routes.ts                                          |
|                                                                       |
|  REMAINING ISSUES TO ADDRESS:                                       |
|  - database.ts: SQL injection (still needs fix)                    |
|                                                                       |
|  Please re-analyze the modified files and confirm fixes.              |
|  \"\"\"                                                              |
|                                                                       |
|  messages.append({"role": "user", "content": summary})             |
|                                                                       |
|  # 3. Continue with new work                                        |
|  messages.append({"role": "user",                                  |
|                    "content": "Now let's fix database.ts"})         |
|                                                                       |
|  # 4. Fresh analysis, no stale tool results!                       |
+-----------------------------------------------------------------------+
""")


if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    print("\n" + "=" * 70)
    print("PRACTICE 3: THE CORRECT FIX - TARGETED RE-ANALYSIS")
    print("=" * 70)
    print("""
This program teaches the correct approach when resuming after file changes:
    1. Start FRESH session (no stale tool results)
    2. Inject STRUCTURED SUMMARY of prior findings
    3. Specify WHICH files have changed
    4. Agent re-analyzes only modified files
""")

    show_the_correct_approach()
    show_vs_naive_approach()
    show_targeted_reanalysis_pattern()
    show_example()
    show_implementation()

    print("""
================================================================================
WHAT JUST HAPPENED?
================================================================================

    1. We learned the CORRECT approach:
       - Start a FRESH session (not resume!)
       - Inject structured summary of prior findings
       - Specify which files have changed
       - Agent re-analyzes only the modified files

    2. We compared CORRECT vs NAIVE:
       - Naive: Resume + re-read = stale data still present
       - Correct: Fresh + summary = clean context, preserved knowledge

    3. We saw the PATTERN:
       - Template for injecting summary
       - Clear separation of modified vs unchanged files
       - Targeted re-analysis request

    4. We saw a COMPLETE EXAMPLE:
       - Day 1: Analyzed 50 files, found 4 issues
       - Day 2: Fixed 2 issues
       - Day 2 (correct): Fresh session, inject summary, re-analyze 2 files

    KEY INSIGHT:
    The fix is NOT about re-reading files in a resumed session.
    The fix is about starting fresh and injecting curated knowledge!

    Transfer KNOWLEDGE, not stale tool results!
================================================================================
""")
    print("\n" + "=" * 70)
    print("PROGRAM COMPLETE!")
    print("=" * 70)