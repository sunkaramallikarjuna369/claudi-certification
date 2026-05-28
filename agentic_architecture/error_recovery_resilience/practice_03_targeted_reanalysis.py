"""
+===========================================================================+
|                                                                           |
|  PRACTICE 3: THE CORRECT FIX - TARGETED RE-ANALYSIS                     |
|                                                                           |
|  Learn the fresh start + summary injection pattern                        |
|  + REAL-TIME IMPLEMENTATION + EXPERT GUIDANCE                            |
|                                                                           |
+===========================================================================+

THE CORRECT FIX: Fresh Start + Summary Injection
===========================================================================

    When files have changed since your last session, the correct approach is:

    1. Start a FRESH session (no conversation history)
    2. Inject a STRUCTURED SUMMARY of prior findings
    3. Specify WHICH files have changed
    4. Agent RE-ANALYZES only modified files

    This gives you fresh analysis WITHOUT stale tool results!

===========================================================================
 STEP-BY-STEP VISUALIZATION
===========================================================================

    STEP 1: Start FRESH session
    ---------------------------
    $ claude --session new-session

    +-----------------------------------------------------------------------+
    | OLD SESSION (day1-session):                                          |
    | +---------------------------+                                        |
    | | Tool Result 1 (STALE)      |  <- Delete this                       |
    | | Tool Result 2 (STALE)      |                                        |
    | | Tool Result 3 (STALE)      |                                        |
    | +---------------------------+                                        |
    +-----------------------------------------------------------------------+
                                    X (Discard!)

    NEW SESSION (new-session):
    +---------------------------+
    | [Empty - fresh start]     |  <- No stale tool results!
    +---------------------------+

    STEP 2: Inject STRUCTURED SUMMARY
    ---------------------------------
    What you type:
        === SUMMARY ===
        Prior analysis summary:
        - auth.ts: Had MD5 hashing (security issue #1)
        - database.ts: Had SQL injection vulnerability (issue #2)
        - api-routes.ts: Missing rate limiting (issue #3)
        - User implemented fixes for auth.ts (MD5 -> bcrypt)
        === END SUMMARY ===

    What the agent receives:
    +---------------------------+
    | KNOWLEDGE:                |
    | - Found MD5 in auth.ts    |
    | - Found SQL vuln in db.ts |
    | - User fixed auth.ts      |
    +---------------------------+

    NOT tool results! KNOWLEDGE!

    STEP 3: Specify CHANGED files
    ------------------------------
    What you type:
        === CHANGED FILES ===
        Modified files:
        - auth.ts (user implemented bcrypt fix)

        Please re-analyze: auth.ts to verify the fix
        === END ===

    STEP 4: Agent RE-ANALYZES
    --------------------------
    Agent reads fresh auth.ts
    Confirms bcrypt fix is correct
    Validates other findings (database.ts, api-routes.ts)
    Result: Complete, current, ACCURATE analysis!

"""

import os
import anthropic
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment
API_KEY = os.getenv("ANTHROPIC_API_KEY")

if not API_KEY:
    raise ValueError("ANTHROPIC_API_KEY not found in .env file")


def demonstrate_four_step_pattern():
    """
    Shows the four-step pattern for fresh start + summary injection.
    """

    client = anthropic.Anthropic(api_key=API_KEY)

    print("\n" + "=" * 70)
    print("THE FOUR-STEP PATTERN - COMPLETE DEMONSTRATION")
    print("=" * 70)

    # ============================================================
    # STEP 1: Fresh Session
    # ============================================================

    print("""
    +======================================================================+
    ||                                                                      ||
    ||  STEP 1: Start a FRESH session                                     ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  COMMAND: $ claude --session new-session                            ||
    ||                                                                      ||
    ||  WHAT HAPPENS:                                                      ||
    ||  - NEW session starts with NO conversation history                 ||
    ||  - NO stale tool results anywhere                                  ||
    ||  - Agent has a clean slate                                         ||
    ||                                                                      ||
    ||  WHY THIS MATTERS:                                                  ||
    ||  - In --resume, old tool results STAY in conversation               ||
    ||  - In fresh session, there's nothing stale to begin with!          ||
    ||                                                                      ||
    ||  +--------------------------------------------------------------------+|
    ||  | PRO TIP: Always use a descriptive session name like:              ||
    ||  | $ claude --session security-audit-round2                          ||
    ||  | This helps track which round you're in                           ||
    ||  +--------------------------------------------------------------------+|
    ||                                                                      ||
    +======================================================================+
    """)

    # ============================================================
    # STEP 2: Structured Summary
    # ============================================================

    print("""
    +======================================================================+
    ||                                                                      ||
    ||  STEP 2: Inject STRUCTURED SUMMARY of prior findings                ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WHAT TO INJECT:                                                     ||
    ||                                                                      ||
    ||  Prior analysis summary:                                             ||
    ||  - auth.ts: Had MD5 hashing (security issue #1)                    ||
    ||  - database.ts: Had SQL injection vulnerability (issue #2)          ||
    ||  - api-routes.ts: Missing rate limiting (issue #3)                  ||
    ||  - User implemented fixes for auth.ts (MD5 -> bcrypt)               ||
    ||                                                                      ||
    ||  WHAT NOT TO INJECT (TOOL RESULTS):                                  ||
    ||  X "File auth.ts: uses MD5 hashing" <- This is a STALE snapshot!   ||
    ||                                                                      ||
    ||  WHY KNOWLEDGE WORKS:                                               ||
    ||  - Knowledge: "Found MD5 issue in auth.ts" <- Stays relevant!       ||
    ||  - Tool result: "auth.ts uses MD5" <- Becomes stale!               ||
    ||                                                                      ||
    +======================================================================+
    """)

    # Demonstrate with actual API call
    prior_summary = """
    Prior analysis summary:
    - auth.ts: Had MD5 hashing (security issue #1)
    - database.ts: Had SQL injection vulnerability (issue #2)
    - api-routes.ts: Missing rate limiting (issue #3)
    - User implemented fixes for auth.ts (MD5 -> bcrypt)
    """

    message = client.messages.create(
        model="claude-haiku-4-5-20250601",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"I have a code analysis summary from yesterday:\n{prior_summary}\n\n"
                      f"What knowledge do you now have about this codebase?"
        }]
    )

    print("Agent response showing it absorbed the knowledge:")
    print(f"    {message.content[0].text[:250]}...")

    # ============================================================
    # STEP 3: Changed Files
    # ============================================================

    print("""
    +======================================================================+
    ||                                                                      ||
    ||  STEP 3: Specify WHICH files have CHANGED                          ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WHAT TO SAY:                                                        ||
    ||                                                                      ||
    ||  Modified files:                                                     ||
    ||  - auth.ts (user implemented bcrypt fix)                            ||
    ||                                                                      ||
    ||  Please re-analyze: auth.ts to verify the fix                        ||
    ||                                                                      ||
    ||  WHY THIS MATTERS:                                                  ||
    ||  - Tells agent exactly what needs fresh analysis                    ||
    ||  - Agent doesn't waste time re-checking unchanged files              ||
    ||  - Clear focus = more thorough analysis                              ||
    ||                                                                      ||
    +======================================================================+
    """)

    # ============================================================
    # STEP 4: Re-Analysis
    # ============================================================

    print("""
    +======================================================================+
    ||                                                                      ||
    ||  STEP 4: Agent RE-ANALYZES only modified files                     ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WHAT THE AGENT DOES:                                                ||
    ||  1. Reads fresh auth.ts                                             ||
    ||  2. Confirms bcrypt fix is implemented correctly                     ||
    ||  3. Notes any issues with the fix implementation                    ||
    ||  4. Validates other findings are still accurate                     ||
    ||                                                                      ||
    ||  RESULT:                                                             ||
    ||  - Complete analysis with NO stale context                          ||
    ||  - Accurate picture of current code state                           ||
    ||  - No contradictory advice!                                         |
    ||                                                                      ||
    +======================================================================+
    """)


def show_real_time_implementation():
    """
    Shows how to implement this in real-world workflows.
    """

    print("\n" + "=" * 70)
    print("REAL-TIME IMPLEMENTATION GUIDE")
    print("=" * 70)

    print("""
    +======================================================================+
    ||                                                                      ||
    ||  USE CASE #1: Security Audit After Fixes                            ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  SCENARIO: You audited 100 files, found 15 issues.                   |
    ||            Developers fixed 10 issues. You need to verify fixes.      ||
    ||                                                                      ||
    ||  IMPLEMENTATION:                                                     ||
    ||                                                                      ||
    ||  Step 1: $ claude --session security-audit-v2                       |
    ||                                                                      ||
    ||  Step 2: Inject summary:                                             ||
    ||  === START ===                                                            |
    ||  Prior findings (15 issues identified):                             ||
    ||  1. auth.ts: MD5 hashing (#1) <- FIXED                               ||
    ||  2. database.ts: SQL injection (#2) <- FIXED                        ||
    ||  3. api-routes.ts: Missing auth (#3) <- FIXED                       ||
    ||  ...                                                                ||
    ||  10-15: [Other issues, various statuses]                            ||
    ||  === END ===                                                            |
    ||                                                                      ||
    ||  Step 3: Specify changed files:                                     ||
    ||  === START ===                                                            |
    ||  Modified files: auth.ts, database.ts, api-routes.ts                ||
    ||  Please verify: Each fix was implemented correctly                   |
    ||  === END ===                                                            |
    ||                                                                      ||
    ||  Step 4: Agent re-analyzes only modified files                       ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  USE CASE #2: Code Review After Refactoring                         ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  SCENARIO: You reviewed a monolith. Team split into microservices.   ||
    ||            You need to review the new microservice structure.         ||
    ||                                                                      ||
    ||  IMPLEMENTATION:                                                     ||
    ||                                                                      |
    ||  Step 1: $ claude --session microservices-review                    ||
    ||                                                                      ||
    ||  Step 2: Inject context:                                            ||
    ||  === START ===                                                            |
    ||  Original analysis (monolith):                                       ||
    ||  - Single auth service with all authentication logic                 ||
    ||  - Database: single User table                                      ||
    ||  - API: single /api routes                                          ||
    ||                                                                      ||
    ||  Migration to microservices:                                         ||
    ||  - auth-service: split from main app                                ||
    ||  - user-service: handles user data                                  ||
    ||  - api-gateway: routes to microservices                             ||
    ||  === END ===                                                            |
    ||                                                                      |
    ||  Step 3: Specify new structure:                                     ||
    ||  === START ===                                                            |
    ||  New services: auth-service/, user-service/, api-gateway/            ||
    ||  Please review: New architecture, inter-service communication       ||
    ||  === END ===                                                            |
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  USE CASE #3: Dependency Update Analysis                             ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  SCENARIO: You analyzed code using React 17. React 18 released.     ||
    ||            You need to analyze for migration issues.                 |
    ||                                                                      ||
    ||  IMPLEMENTATION:                                                     ||
    ||                                                                      |
    ||  Step 1: $ claude --session react18-migration                       ||
    ||                                                                      ||
    ||  Step 2: Inject prior context:                                       ||
    ||  === START ===                                                            |
    ||  React 17 analysis findings:                                         ||
    ||  - 5 files use componentWillMount (deprecated)                      ||
    |  - 3 files use componentWillReceiveProps (deprecated)                ||
    ||  - 2 files use React.createClass (deprecated)                       ||
    ||                                                                      ||
    ||  Dependencies: React 17.2.4                                        ||
    ||  === END ===                                                            |
    ||                                                                      ||
    ||  Step 3: Specify update:                                            ||
    ||  === START ===                                                            |
    ||  Updated to: React 18.2.0                                           ||
    ||  Please re-analyze: Migration compatibility, new deprecations        ||
    ||  === END ===                                                            |
    ||                                                                      ||
    +======================================================================+
    """)


def show_knowledge_vs_tool_results():
    """
    Explains the critical difference between knowledge and tool results.
    """

    client = anthropic.Anthropic(api_key=API_KEY)

    print("\n" + "=" * 70)
    print("KNOWLEDGE vs TOOL RESULTS - THE CRITICAL DISTINCTION")
    print("=" * 70)

    print("""
    +======================================================================+
    ||                                                                      ||
    ||  TOOL RESULTS (What --resume restores - STALE):                      ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  Example:                                                            ||
    ||  "File auth.ts:                                                      ||
    ||   content = '...                                                     ||
    ||       async function hashPassword(password) {                         ||
    ||           return crypto.createHash(\"md5\").update(password)...      ||
    ||       }                                                             ||
    ||   '"                                                                ||
    ||                                                                      ||
    ||  PROBLEM:                                                           ||
    ||  - This is a SNAPSHOT of the file at that moment                   ||
    ||  - When file changes, this becomes STALE                            ||
    ||  - Shows OLD code, not current code                                  ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  KNOWLEDGE (What summary injection transfers - STAYS RELEVANT):        ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  Example:                                                            ||
    ||  "Day 1 analysis found:                                              ||
    ||   - auth.ts used MD5 hashing (security issue)                        ||
    ||   - This was flagged as vulnerable to rainbow table attacks         ||
    ||   - Developer intended to upgrade to bcrypt                          |
    ||  "                                                                  ||
    ||                                                                      ||
    ||  WHY IT WORKS:                                                      ||
    ||  - Describes INSIGHT, not file contents                              ||
    ||  - What we LEARNED, not what we SAW                                  |
    ||  - Stays relevant even when file changes                            ||
    ||  - Can be verified against current state                            ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  SIDE-BY-SIDE COMPARISON:                                           ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  TOOL RESULT:                                                        ||
    ||  "auth.ts uses MD5 hashing"                                          |
    ||  <- Snapshot, becomes stale when file changes                        |
    ||                                                                      ||
    ||  KNOWLEDGE:                                                          ||
    ||  "Found: MD5 security vulnerability in auth.ts"                       ||
    ||  "Developer plans to fix by upgrading to bcrypt"                      ||
    ||  "Fixed: bcrypt now in use"                                         ||
    ||  <- Insights, stay relevant even after file changes                 ||
    ||                                                                      ||
    +======================================================================+
    """)

    message = client.messages.create(
        model="claude-haiku-4-5-20250601",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": "Explain the difference between transferring "
                      "'tool results' vs transferring 'knowledge' to a new session. "
                      "Why is knowledge transfer more reliable?"
        }]
    )

    print("Agent's explanation:")
    print(f"    {message.content[0].text[:350]}...")


def show_common_mistakes():
    """
    Shows mistakes developers make with summary injection.
    """

    print("\n" + "=" * 70)
    print("COMMON MISTAKES WITH SUMMARY INJECTION")
    print("=" * 70)

    print("""
    +======================================================================+
    ||                                                                      ||
    ||  MISTAKE #1: Copying tool results verbatim                          ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WRONG:                                                              ||
    ||  === START ===                                                            |
    ||  From yesterday's session:                                           ||
    ||  Tool Result: File auth.ts - content = '...uses MD5...'             ||
    ||  === END ===                                                            |
    ||                                                                      ||
    ||  WHY IT'S WRONG:                                                     ||
    ||  - You're copying STALE snapshots into fresh session!                 ||
    ||  - The problem persists in new session                               ||
    ||                                                                      ||
    ||  CORRECT:                                                            ||
    ||  === START ===                                                            |
    ||  Prior findings: auth.ts had MD5 hashing (security issue)            |
    ||  === END ===                                                            |
    ||                                                                      |
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  MISTAKE #2: Not specifying changed files                           ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WRONG:                                                              ||
    ||  === START ===                                                            |
    ||  I analyzed 50 files yesterday. Fixed 10 issues. Continue.            ||
    ||  === END ===                                                            |
    ||                                                                      ||
    ||  WHY IT'S WRONG:                                                     ||
    ||  - Agent doesn't know which files to focus on                       ||
    ||  - May miss re-analyzing modified files                             ||
    ||  - No clear priority                                                |
    ||                                                                      ||
    ||  CORRECT:                                                            ||
    ||  === START ===                                                            |
    ||  Modified files: auth.ts, database.ts, api-routes.ts                 ||
    ||  Please re-analyze these to verify fixes                            ||
    ||  === END ===                                                            |
    ||                                                                      |
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  MISTAKE #3: Too verbose summaries                                  ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WRONG:                                                              ||
    ||  === START ===                                                            |
    ||  The file auth.ts was read at 10:30am and contained the function    |
    ||  hashPassword which used the MD5 algorithm as confirmed by the      ||
    ||  tool result which showed... [continues for 200 more words]         ||
    ||  === END ===                                                            |
    ||                                                                      ||
    ||  WHY IT'S WRONG:                                                     ||
    ||  - Too much detail obscures key information                         ||
    ||  - Agent has to parse through noise                                ||
    ||  - Hard to maintain                                                 |
    ||                                                                      ||
    ||  CORRECT:                                                            |
    ||  === START ===                                                            |
    ||  auth.ts: Had MD5 hashing vulnerability. Fixed to bcrypt.           ||
    ||  === END ===                                                            |
    ||                                                                      |
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  MISTAKE #4: Forgetting to mention fixes                           ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WRONG:                                                              |
    ||  === START ===                                                            |
    ||  auth.ts: Uses MD5 hashing                                          |
    ||  === END ===                                                            |
    ||                                                                      ||
    ||  WHY IT'S WRONG:                                                     ||
    ||  - Agent will flag MD5 as issue                                     ||
    ||  - Developer says "I already fixed that!"                          ||
    ||  - Wasted time and confusion                                        |
    ||                                                                      ||
    ||  CORRECT:                                                            ||
    ||  === START ===                                                            |
    ||  auth.ts: Had MD5 hashing <- FIXED to bcrypt                        |
    ||  === END ===                                                            |
    ||                                                                      |
    +======================================================================+
    """)


def show_interview_qa():
    """
    Shows interview questions and expert answers.
    """

    print("\n" + "=" * 70)
    print("INTERVIEW Q&A PREPARATION")
    print("=" * 70)

    print("""
    ======================================================================
    Q1: "How do you resume after file changes without stale context?"
    ======================================================================

    EXPERT ANSWER:
    "I use a fresh start with summary injection pattern. First, I start
    a completely new session with --session flag. Then I inject a
    structured summary of what I learned from the previous session,
    focusing on insights and findings, not tool results. I specify
    exactly which files have been modified so the agent knows what to
    re-analyze. This gives me fresh analysis without any stale context."

    KEY POINTS TO MENTION:
    - Fresh session (--session, not --resume)
    - Structured summary (KNOWLEDGE, not tool results)
    - Specify changed files
    - Targeted re-analysis

    ======================================================================
    Q2: "What's the difference between tool results and knowledge?"
    ======================================================================

    EXPERT ANSWER:
    "Tool results are snapshots - for example, 'File auth.ts contains
    uses MD5 hashing'. These become stale when files change. Knowledge
    is insight - 'Day 1 found MD5 security vulnerability in auth.ts,
    developer fixed it to bcrypt'. This stays relevant because it
    captures discoveries and insights, not file contents. Knowledge
    transfer is reliable because it describes what we learned, which
    remains valid even when the underlying files change."

    ======================================================================
    Q3: "Why is summary injection better than just re-reading files?"
    ======================================================================

    EXPERT ANSWER:
    "Re-reading files gives fresh content but doesn't address the core
    problem: stale tool results are still in conversation history. Both
    old tool results and fresh file reads exist in context, causing the
    agent to have conflicting information. Summary injection solves this
    by starting completely fresh - no stale tool results exist at all.
    The agent only has current file content and injected knowledge,
    eliminating the confusion."

    ======================================================================
    Q4: "How do you structure an effective summary for injection?"
    ======================================================================

    EXPERT ANSWER:
    "An effective summary has three parts: First, list prior findings
    with their status (open, fixed, acknowledged). Second, note any
    modifications made since the last session. Third, specify what you
    want the agent to focus on in this session. Keep it concise -
    bullet points, not verbose prose. Focus on insights and decisions,
    not raw file contents."

    EXAMPLE STRUCTURE:
        === EXAMPLE ===
        Prior findings:
        - auth.ts: MD5 hashing (issue #1) <- FIXED
        - database.ts: SQL injection (issue #2) <- OPEN
        - api-routes.ts: Missing rate limit (issue #3) <- OPEN

        Modified files: auth.ts (fixed to bcrypt)
        Please verify: auth.ts fix + continue analysis on other files
        === END EXAMPLE ===

    ======================================================================
    Q5: "What are common mistakes with this pattern?"
    ======================================================================

    EXPERT ANSWER:
    "Three common mistakes: First, copying tool results verbatim instead
    of summarizing knowledge - this just moves stale data to fresh session.
    Second, not specifying which files changed - agent doesn't know what
    to focus on. Third, making summaries too verbose - obscures key info.
    The fix is to describe insights, not file snapshots, and be specific
    about what needs re-analysis."

    """)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("""
+===========================================================================+
|                                                                           |
|  THE CORRECT FIX: Fresh Start + Summary Injection                        |
|  + REAL-TIME IMPLEMENTATION + EXPERT GUIDANCE                             |
|                                                                           |
|  This program shows:                                                      |
|  1. The four-step pattern for fresh start + summary injection            |
|  2. Real-time implementation for common use cases                       |
|  3. Knowledge vs tool results distinction                                |
|  4. Common mistakes and how to avoid them                               |
|  5. Interview Q&A preparation                                           |
|                                                                           |
+===========================================================================+
    """)

    demonstrate_four_step_pattern()
    show_real_time_implementation()
    show_knowledge_vs_tool_results()
    show_common_mistakes()
    show_interview_qa()

    print("\n" + "=" * 70)
    print("WHAT WE HAVE LEARNT")
    print("=" * 70)
    print("""
    +======================================================================+
    ||  1. THE FOUR-STEP PATTERN:                                          ||
    ||                                                                      ||
    ||  STEP 1: Start FRESH session                                        ||
    ||  $ claude --session new-session                                     ||
    ||  -> No conversation history, no stale tool results!                ||
    ||                                                                      ||
    ||  STEP 2: Inject STRUCTURED SUMMARY                                    ||
    ||  "Prior findings: auth.ts had MD5, database.ts had SQL vuln"         ||
    ||  -> Transfer KNOWLEDGE, not tool results!                          ||
    ||                                                                      ||
    ||  STEP 3: Specify CHANGED files                                       ||
    ||  "Modified files: auth.ts <- please re-analyze"                     ||
    ||  -> Tells agent what needs fresh attention!                        ||
    ||                                                                      ||
    ||  STEP 4: Agent RE-ANALYZES                                           ||
    |  -> Reads fresh files, confirms fixes, validates other findings       ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  2. KNOWLEDGE vs TOOL RESULTS:                                       ||
    ||                                                                      ||
    ||  TOOL RESULT (Snapshot - STALE):                                   ||
    ||  "File auth.ts: uses MD5 hashing"                                   ||
    ||  <- Becomes outdated when file changes                             ||
    ||                                                                      ||
    ||  KNOWLEDGE (Insight - STAYS RELEVANT):                             ||
    ||  "Found MD5 vulnerability in auth.ts, developer fixed to bcrypt"    ||
    ||  <- Describes discovery, not file contents                          ||
    ||                                                                      ||
    ||  KEY: Transfer INSIGHTS, not snapshots!                             ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  3. REAL-TIME USE CASES:                                             ||
    ||                                                                      ||
    ||  USE CASE #1: Security Audit After Fixes                           ||
    ||  - 15 issues found, 10 fixed -> verify fixes in fresh session       ||
    ||                                                                      ||
    ||  USE CASE #2: Code Review After Refactoring                         ||
    ||  - Monolith to microservices -> review new architecture             ||
    ||                                                                      ||
    ||  USE CASE #3: Dependency Update Analysis                           ||
    ||  - React 17 to 18 -> re-analyze for migration issues               ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  4. COMMON MISTAKES:                                                ||
    ||                                                                      ||
    ||  MISTAKE #1: Copying tool results verbatim                         ||
    ||  FIX: Summarize as knowledge, not file contents                     ||
    ||                                                                      ||
    ||  MISTAKE #2: Not specifying changed files                          ||
    ||  FIX: Always mention which files were modified                      ||
    ||                                                                      ||
    ||  MISTAKE #3: Too verbose summaries                                 ||
    ||  FIX: Keep it concise, bullet points, key insights                  ||
    ||                                                                      ||
    ||  MISTAKE #4: Forgetting to mention fixes                           ||
    ||  FIX: Always note what was fixed and what status                   ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  5. INTERVIEW TIPS:                                                 ||
    ||                                                                      ||
    ||  - Have the four steps memorized                                    ||
    ||  - Explain KNOWLEDGE vs TOOL RESULTS with examples                  ||
    ||  - Show you understand WHY this works (no stale context)            ||
    ||  - Know common mistakes and how to avoid them                       ||
    ||  - Have real-world use case examples ready                          ||
    ||                                                                      ||
    ||  EXPECTED ANSWER STRUCTURE:                                         ||
    ||  1. State the problem (stale context)                             ||
    ||  2. Explain the solution (fresh start + summary)                    ||
    ||  3. Give concrete examples                                         ||
    ||  4. Show practical implementation                                   ||
    ||                                                                      ||
    +======================================================================+

    Next: practice_04_decision_matrix.py helps you choose the right
    approach for different scenarios!
    """)


"""
+===========================================================================+
|                                                                           |
|  KEY CONCEPTS FROM THIS FILE:                                            |
|                                                                           |
|  FOUR-STEP PATTERN:                                                      |
|  1. Fresh session (--session, not --resume)                             |
|  2. Inject structured SUMMARY of findings                               |
|  3. Specify changed files                                               |
|  4. Agent re-analyzes modified files                                    |
|                                                                           |
|  KNOWLEDGE vs TOOL RESULTS:                                             |
|  - Tool results: snapshots -> become stale                              |
|  - Knowledge: insights -> stay relevant                                 |
|  - Transfer KNOWLEDGE, not tool results!                               |
|                                                                           |
|  COMMON MISTAKES:                                                        |
|  - Copying tool results verbatim (still stale!)                        |
|  - Not specifying changed files                                         |
|  - Too verbose summaries                                               |
|  - Forgetting to mention fixes                                          |
|                                                                           |
|  EXAM TIPS:                                                              |
|  - Fresh start + summary = CORRECT when files changed                  |
|  - "Resume and re-read" = WRONG answer!                               |
|  - Always transfer KNOWLEDGE, not tool results                         |
|                                                                           |
|  INTERVIEW PREP:                                                         |
|  - Have four steps memorized                                           |
|  - Explain difference with concrete examples                            |
|  - Know why it works (no stale context)                                |
|                                                                           |
+===========================================================================+
"""
