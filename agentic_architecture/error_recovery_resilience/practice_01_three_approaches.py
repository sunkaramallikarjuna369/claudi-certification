"""
+===========================================================================+
|                                                                           |
|  PRACTICE 1: THREE SESSION MANAGEMENT APPROACHES                        |
|                                                                           |
|  Learn the three ways to manage sessions in Claude Code CLI               |
|  + REAL-TIME MISTAKES DEVELOPERS MAKE + INTERVIEW GUIDE                  |
|                                                                           |
+===========================================================================+

This practice covers the THREE fundamental approaches to session management.
Each approach has specific use cases and trade-offs.

INTERVIEW PREP: "How do you manage context in long-running Claude Code sessions?"
This question tests your understanding of session state and resumption patterns.

REAL-TIME SCENARIO: You've been analyzing a 50-file codebase for 2 hours.
You need to take a break and resume tomorrow. What do you do?

===========================================================================
 APPROACH 1: --resume <session-name>  (Full History Restoration)
===========================================================================

    What it does:
    - Restores COMPLETE conversation history
    - Includes ALL tool results from previous session
    - Agent has context of everything that happened

    When to use:
    + Prior context remains VALID (files unchanged)
    + No files have changed since last session
    + Need to continue exact work from where you left off

    Command:
    $ claude --resume my-session

    +-----------------------------------------------------------------------+
    | VISUALIZATION: What --resume does under the hood                      |
    +-----------------------------------------------------------------------+
    |                                                                       |
    |  SESSION: day1-session                                                |
    |  +---------------------------+                                        |
    |  | Tool Result 1              |  <- ALL restored                      |
    |  | Tool Result 2              |  <- Including stale ones            |
    |  | Tool Result 3              |                                        |
    |  | User Message 1              |                                        |
    |  | Assistant Response 1       |                                        |
    |  | ...                        |                                        |
    |  +---------------------------+                                        |
    |           |                                                           |
    |           v                                                           |
    |  RESUME with --resume                                                 |
    |           |                                                           |
    |           v                                                           |
    |  +---------------------------+                                        |
    |  | [ALL OF THE ABOVE]        |  <- Exact copy restored              |
    |  |                           |                                        |
    |  +---------------------------+                                        |
    |           |                                                           |
    |           v                                                           |
    |  Agent has FULL history including TOOL RESULTS                        |
    |                                                                       |
    +-----------------------------------------------------------------------+

===========================================================================
 APPROACH 2: fork_session  (Branching for Exploration)
===========================================================================

    What it does:
    - Creates INDEPENDENT branches from current state
    - Each branch operates SEPARATELY
    - Changes in one branch do NOT affect the other

    When to use:
    + Exploring DIVERGENT approaches
    + A/B testing different strategies
    + Want to try approach A AND approach B simultaneously
    + Need to compare two solutions without committing

    Command (inside Claude Code):
    /fork_session new-branch-name

    +-----------------------------------------------------------------------+
    | VISUALIZATION: fork_session creates INDEPENDENT branches              |
    +-----------------------------------------------------------------------+
    |                                                                       |
    |          MASTER BRANCH (main-session)                                  |
    |                 |                                                      |
    |        +--------+--------+                                            |
    |        |                 |                                           |
    |        v                 v                                           |
    |  +------------+    +------------+                                     |
    |  | Branch A   |    | Branch B    |                                    |
    |  | microservices|  | monolith    |                                    |
    |  +------------+    +------------+                                     |
    |        |                 |                                           |
    |        v                 v                                           |
    |  Changes here       Changes here                                     |
    |  DON'T affect       DON'T affect                                     |
    |  Branch B           Branch A                                          |
    |                                                                       |
    |  KEY INSIGHT: Independent state, not shared context!                |
    |                                                                       |
    +-----------------------------------------------------------------------+

===========================================================================
 APPROACH 3: Fresh Start + Summary Injection  (Clean Slate)
===========================================================================

    What it does:
    - Starts a COMPLETELY NEW session
    - NO stale tool results in history
    - Curated knowledge transfers via structured summary
    - Clean slate with important context

    When to use:
    + Files have CHANGED since last session
    + Long session with cluttered history
    + Dependency updates since last session
    + Need to move forward without stale data

    Command:
    $ claude --session new-session

    +-----------------------------------------------------------------------+
    | VISUALIZATION: Fresh start = NO tool results                          |
    +-----------------------------------------------------------------------+
    |                                                                       |
    |  OLD SESSION (has stale tool results):                               |
    |  +---------------------------+                                        |
    |  | Tool Result 1 (STALE)      |  <- Outdated info                    |
    |  | Tool Result 2 (STALE)      |                                        |
    |  | Tool Result 3 (STALE)      |                                        |
    |  +---------------------------+                                        |
    |           x (Discard this!)                                          |
    |                                                                       |
    |  NEW SESSION (clean slate):                                          |
    |  +---------------------------+                                        |
    |  | [SUMMARY INJECTED]         |  <- "Day 1 found X, Y, Z"           |
    |  | (Knowledge, not results)   |                                        |
    |  +---------------------------+                                        |
    |           |                                                           |
    |           v                                                           |
    |  Agent has KNOWLEDGE but NO stale tool results!                      |
    |  Agent read fresh files = accurate picture                           |
    |                                                                       |
    +-----------------------------------------------------------------------+

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


def demonstrate_three_approaches():
    """
    Demonstrates all three session management approaches with examples.
    """

    client = anthropic.Anthropic(api_key=API_KEY)

    print("\n" + "=" * 70)
    print("THREE SESSION MANAGEMENT APPROACHES - FULL DEMONSTRATION")
    print("=" * 70)

    # ============================================================
    # APPROACH 1: --resume (Full History Restoration)
    # ============================================================

    print("""
    +======================================================================+
    ||                                                                      ||
    ||  APPROACH 1: --resume <session-name>                               ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  COMMAND: $ claude --resume my-coding-session                       ||
    ||                                                                      ||
    ||  WHAT HAPPENS:                                                       ||
    ||  - ALL conversation history restored                                 ||
    ||  - ALL tool results included (even stale ones!)                    ||
    ||  - Agent has full context of everything from before                 ||
    ||                                                                      ||
    ||  WHEN TO USE:                                                        ||
    ||  + Context is still VALID (files haven't changed)                   ||
    ||  + Need to continue exact work                                      ||
    ||  + Prior conversation is still relevant                            ||
    ||                                                                      ||
    ||  WHEN NOT TO USE:                                                    ||
    ||  - Files have been MODIFIED since last session                      ||
    ||  - Dependencies have been UPDATED                                   ||
    ||  - You need a clean slate for new exploration                       ||
    ||                                                                      ||
    +======================================================================+
    """)

    message = client.messages.create(
        model="claude-haiku-4-5-20250601",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": "Explain when --resume is the RIGHT choice for "
                      "managing Claude Code sessions. Give a specific "
                      "scenario where it works best."
        }]
    )

    print("AI Response:")
    print(f"    {message.content[0].text[:300]}...")

    # ============================================================
    # APPROACH 2: fork_session (Branching)
    # ============================================================

    print("""
    +======================================================================+
    ||                                                                      ||
    ||  APPROACH 2: fork_session                                           ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  COMMAND: /fork_session new-branch-name                             ||
    ||                                                                      ||
    ||  WHAT HAPPENS:                                                       ||
    ||  - Creates INDEPENDENT branch from current state                    ||
    ||  - Branch operates SEPARATELY (no shared context)                   ||
    ||  - Changes in one branch do NOT affect the other                    ||
    ||                                                                      ||
    ||  WHEN TO USE:                                                        ||
    ||  + Exploring two different approaches                               ||
    ||  + A/B testing strategies                                           ||
    ||  + Want to compare WITHOUT committing                              ||
    ||  + Prototyping before choosing direction                            ||
    ||                                                                      ||
    ||  KEY INSIGHT:                                                       ||
    ||  fork_session is for BRANCHING, NOT for continuing work!           ||
    ||  --resume = linear continuation                                     ||
    ||  fork_session = divergence into new directions                      ||
    ||                                                                      ||
    +======================================================================+
    """)

    message = client.messages.create(
        model="claude-haiku-4-5-20250601",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": "You have a design decision to make for your app. "
                      "You want to explore microservices AND monolith approaches "
                      "before deciding. How would fork_session help here?"
        }]
    )

    print("AI Response:")
    print(f"    {message.content[0].text[:300]}...")

    # ============================================================
    # APPROACH 3: Fresh Start + Summary
    # ============================================================

    print("""
    +======================================================================+
    ||                                                                      ||
    ||  APPROACH 3: Fresh Start + Summary Injection                        ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  COMMAND: $ claude --session new-session                            ||
    ||                                                                      ||
    ||  WHAT HAPPENS:                                                       ||
    ||  - NEW session with NO conversation history                          ||
    ||  - NO stale tool results in context                                  ||
    ||  - Curated KNOWLEDGE injected via summary                           ||
    ||  - Clean slate + important context                                  ||
    ||                                                                      ||
    ||  WHEN TO USE:                                                        ||
    ||  + Files have CHANGED since last session                            ||
    ||  + Long session with cluttered history                              ||
    ||  + Dependency updates have occurred                                ||
    ||  + Need fresh analysis with current state                          ||
    ||                                                                      ||
    ||  WHAT TO INJECT:                                                     ||
    ||  - "Prior findings: auth.ts had MD5 issue, database.ts had SQL vuln" ||
    ||  - "User implemented MD5 fix: auth.ts now uses bcrypt"               ||
    ||  - "Please re-analyze: auth.ts"                                     ||
    ||                                                                      ||
    ||  KEY INSIGHT:                                                       ||
    ||  Transfer KNOWLEDGE (insights), not tool results (snapshots)!       ||
    ||                                                                      ||
    +======================================================================+
    """)

    message = client.messages.create(
        model="claude-haiku-4-5-20250601",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": "You analyzed 50 files yesterday for security issues. "
                      "User fixed the top 5 issues overnight. You need to continue. "
                      "Why is fresh start + summary injection better than --resume?"
        }]
    )

    print("AI Response:")
    print(f"    {message.content[0].text[:300]}...")


def show_real_time_mistakes():
    """
    Shows REAL mistakes developers make with session management.
    """

    print("\n" + "=" * 70)
    print("REAL MISTAKES DEVELOPERS MAKE - EXPERT WARNINGS")
    print("=" * 70)

    print("""
    +======================================================================+
    ||                                                                      ||
    ||  MISTAKE #1: Using --resume when files have changed                 ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WHAT HAPPENS IN PRODUCTION:                                         ||
    ||  - Developer resumes session after modifying files                  ||
    ||  - Agent has stale tool results from before modification            ||
    ||  - Agent gives advice based on OLD code                             ||
    ||  - Contradictory behavior and confusion                             ||
    ||                                                                      ||
    ||  REAL CONSEQUENCE:                                                   ||
    ||  - "Your code uses MD5" -> Developer says "I already fixed that!"  ||
    ||  - Agent insists on fixes that are already done                      ||
    ||  - Lost confidence in the tool                                       ||
    ||  - Wasted development time                                           ||
    ||                                                                      ||
    ||  CORRECT APPROACH:                                                   ||
    ||  $ claude --session new-session                                      ||
    ||  [Inject summary: "auth.ts was fixed, use bcrypt"]                  |
    ||  [Ask agent to re-analyze modified files]                           ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  MISTAKE #2: Confusing fork_session with --resume                   ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WHAT HAPPENS:                                                       ||
    ||  - Developer wants to "continue work from yesterday"                ||
    ||  - Uses fork_session instead of --resume                            ||
    ||  - Gets a NEW BRANCH, not continuation                               ||
    ||  - All context from yesterday is GONE                              ||
    ||                                                                      ||
    ||  REAL CONSEQUENCE:                                                   ||
    ||  - Developer asks "continue the password reset refactor"            ||
    ||  - fork_session created but agent has NO context                    ||
    ||  - Must re-explain everything from scratch                          ||
    ||  - Wasted time and context                                           ||
    ||                                                                      ||
    ||  CORRECT APPROACH:                                                   ||
    ||  - Continue work (context still valid) -> Use --resume              ||
    ||  - Explore alternatives -> Use fork_session                         ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  MISTAKE #3: Re-reading files to "fix" stale context                ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WHAT HAPPENS:                                                       ||
    ||  - Developer resumes with --resume                                  ||
    ||  - Agent still has stale tool results                               ||
    ||  - Developer says "please re-read the files"                       ||
    ||  - Agent reads files but STILL has stale tool results               ||
    ||  - Still confused about current state                               ||
    ||                                                                      ||
    ||  REAL CONSEQUENCE:                                                   ||
    ||  - Developer thinks re-reading = fixing context                     ||
    ||  - But stale tool results are STILL in conversation!              ||
    ||  - Agent still confused about current state                        ||
    ||  - Inconsistent advice continues                                    ||
    ||                                                                      ||
    ||  CORRECT APPROACH:                                                   ||
    ||  - Fresh start = starting session with NO PRIOR HISTORY            ||
    ||  - Re-reading does NOT clear stale tool results!                   ||
    ||  - Must inject knowledge to transfer insights                       ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  MISTAKE #4: Transferring tool results instead of knowledge        ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WHAT HAPPENS:                                                       ||
    ||  - Developer starts fresh session                                   ||
    ||  - Pastes OLD tool results: "File auth.ts: uses MD5 hashing"       ||
    ||  - But auth.ts now uses bcrypt!                                     ||
    ||  - Agent has stale snapshot in fresh session too!                  ||
    ||                                                                      ||
    ||  REAL CONSEQUENCE:                                                   ||
    ||  - Copy-pasting tool results = still stale data!                   ||
    ||  - Must summarize INSIGHTS: "Found MD5 issue, user fixed to bcrypt" ||
    ||  - Not snapshots of previous file contents                          ||
    ||                                                                      ||
    ||  CORRECT APPROACH:                                                   ||
    ||  - Knowledge: "Day 1 found MD5 security issue in auth.ts"          ||
    ||  - Tool result: "File auth.ts: content = '...uses MD5...'"         ||
    ||  - Knowledge stays relevant. This is knowledge.                    ||
    ||                                                                      ||
    +======================================================================+
    """)


def show_interview_qa():
    """
    Shows common interview questions and expert answers.
    """

    client = anthropic.Anthropic(api_key=API_KEY)

    print("\n" + "=" * 70)
    print("INTERVIEW QUESTIONS& EXPERT ANSWERS GUIDE")
    print("=" * 70)

    # Q1
    print("""
    ======================================================================
    INTERVIEW Q1: "How do you manage context in long-running sessions?"
    ======================================================================

    EXPECTED ANSWER:
    It depends on whether files have changed. If files are unchanged and I need
    to continue the same work, I use --resume. If files have changed, I start
    a fresh session and inject a summary of prior findings. I never transfer
    tool results directly - I summarize the knowledge gained.

    RED FLAGS IN ANSWERS:
    - "I always use --resume" -> Shows misunderstanding
    - "I copy-paste all tool results to new session" -> Wrong approach
    - "fork_session is for continuing work" -> Confuses concepts

    +-----------------------------------------------------------------------+
    | EXPERT TIP: Mention the importance of KNOWLEDGE transfer vs tool      |
    | results. That shows deep understanding of the stale context problem.  |
    +-----------------------------------------------------------------------+
    """)

    message = client.messages.create(
        model="claude-haiku-4-5-20250601",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": "As an expertClaude Code user, explain in 3 sentences "
                      "how you manage context in long-running sessions."
        }]
    )

    print("Example Expert Answer:")
    print(f"    {message.content[0].text[:400]}...")

    # Q2
    print("""
    ======================================================================
    INTERVIEW Q2: "What's wrong with using --resume after file changes?"
    ======================================================================

    EXPECTED ANSWER:
    --resume restores ALL tool results from the previous session, including
    stale ones. If files changed, the agent now has conflicting information:
    old tool results showing the previous state AND fresh file reads showing
    the current state. This causes contradictory behavior. The correct fix
    is a fresh start with summary injection.

    RED FLAGS IN ANSWERS:
    - "Nothing's wrong, just re-read the files" -> Doesn't fix stale results
    - "It's fine if history is helpful" -> Misses the stale context problem

    +-----------------------------------------------------------------------+
    | EXPERT TIP: Mention "stale context" and "contradictory behavior"        |
    | These are the key technical terms interviewers expect.                |
    +-----------------------------------------------------------------------+
    """)

    # Q3
    print("""
    ======================================================================
    INTERVIEW Q3: "When would you use fork_session?"
    ======================================================================

    EXPECTED ANSWER:
    fork_session is for EXPLORATION, not continuation. You use it when you want
    to try multiple approaches simultaneously - like exploring microservices
    AND monolith for a new system, or A/B testing different refactoring
    strategies. It's branching, not continuing. For continuing work you use
    --resume (if context valid).

    RED FLAGS IN ANSWERS:
    - "I use it to continue from where I left off" -> Wrong command!
    - "Fork session shares context" -> No, each branch is independent

    +-----------------------------------------------------------------------+
    | EXPERT TIP: Emphasize "independent branches" vs "shared context".      |
    | This is the key differentiator from --resume.                         |
    +-----------------------------------------------------------------------+
    """)

    # Q4
    print("""
    ======================================================================
    INTERVIEW Q4: "What's the difference between tool results and knowledge?"
    ======================================================================

    EXPECTED ANSWER:
    Tool results are snapshots - "File X contains Y" - that become stale when
    files change. Knowledge is insights - "Day 1 found SQL injection in
    database.ts" - that remain relevant even when files are modified.
    Knowledge transfer is reliable because it captures discoveries, not
    file snapshots.

    +-----------------------------------------------------------------------+
    | EXPERT TIP: Give concrete examples:                                    |
    | - Tool result: "auth.ts uses MD5 hashing" (becomes stale)            |
    | - Knowledge: "Found MD5 vulnerability, fixed to bcrypt" (stays valid) |
    +-----------------------------------------------------------------------+
    """)


def show_decision_flowchart():
    """
    Shows visual flowchart for decision making.
    """

    print("\n" + "=" * 70)
    print("VISUAL DECISION FLOWCHART")
    print("=" * 70)

    print("""
                      +--------------------+
                      |  START: Need to   |
                      |  resume session?   |
                      +--------------------+
                               |
                               v
                    +---------------------+
                    | Files changed since |
                    | last session?       |
                    +---------------------+
                          /        \\
                         /          \\
                        v            v
                      YES           NO
                       |              |
                       v              v
    +----------------------+  +---------------------+
    | Use Fresh Start      |  | Context still      |
    | + Summary Injection |  | valid?              |
    +----------------------+  +---------------------+
           |                       /        \\
           |                      /          \\
           |                     v            v
           |                   YES           NO
           |                    |              |
           |                    v              v
           |   +--------------+   +-----------+
           |   | --resume     |   | fork_session|
           |   | (Linear     |   | (Branching  |
           |   |  continue) |   |  explore)   |
           |   +--------------+   +-----------+
           |                         ^
           |                         |
           +-------------------------+
                          |
                          v
                 [Fresh session,
                  inject summary
                  of prior findings]
    """)


def show_quick_reference():
    """
    Shows quick reference table.
    """

    print("\n" + "=" * 70)
    print("QUICK REFERENCE TABLE")
    print("=" * 70)

    print("""
    +--------------------------------+-------------------------------------+
    | SCENARIO                       | BEST APPROACH                      |
    +--------------------------------+-------------------------------------+
    | Continue work, no files       | --resume                           |
    | changed, context still valid   | (Full history restored)           |
    +--------------------------------+-------------------------------------+
    | Exploring alternatives/       | fork_session                       |
    | comparing approaches          | (Independent branches)             |
    +--------------------------------+-------------------------------------+
    | Files changed since last      | Fresh start + summary              |
    | session                      | (Clean slate + knowledge)          |
    +--------------------------------+-------------------------------------+
    | Long session with cluttered   | Fresh start + summary              |
    | history                      | (Start clean)                      |
    +--------------------------------+-------------------------------------+
    | Dependency updates occurred   | Fresh start + summary              |
    |                              | (Fresh dependency analysis)        |
    +--------------------------------+-------------------------------------+
    """)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("""
+===========================================================================+
|                                                                           |
|  THREE SESSION MANAGEMENT APPROACHES                                     |
|  + REAL-TIME MISTAKES + INTERVIEW GUIDE                                  |
|                                                                           |
|  This program covers:                                                    |
|  1. Three session management approaches                                  |
|  2. Real mistakes developers make                                        |
|  3. Interview Q&A guide                                                 |
|  4. Visual flowcharts and decision trees                                 |
|                                                                           |
+===========================================================================+
    """)

    demonstrate_three_approaches()
    show_real_time_mistakes()
    show_interview_qa()
    show_decision_flowchart()
    show_quick_reference()

    print("\n" + "=" * 70)
    print("WHAT WE HAVE LEARNT")
    print("=" * 70)
    print("""
    +======================================================================+
    ||  1. THREE SESSION MANAGEMENT APPROACHES:                            ||
    ||                                                                      ||
    ||  --resume:                                                          ||
    ||  - Restores COMPLETE conversation history                             ||
    ||  - Use when context is STILL VALID (no files changed)               ||
    ||  - Includes ALL tool results (even stale ones!)                    ||
    ||                                                                      ||
    ||  fork_session:                                                       ||
    ||  - Creates INDEPENDENT branches                                      ||
    ||  - Use for EXPLORING alternatives                                    ||
    ||  - NOT for continuing work linearly                                  ||
    ||                                                                      ||
    ||  Fresh start + summary:                                              ||
    ||  - Starts NEW session with NO stale tool results                    ||
    ||  - Transfer KNOWLEDGE (not tool results)                             ||
    ||  - Use when files have CHANGED!                                      ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  2. REAL MISTAKES DEVELOPERS MAKE (EXPERT WARNINGS):                ||
    ||                                                                      ||
    ||  MISTAKE #1: --resume when files changed                            ||
    ||  - Stale tool results cause contradictory behavior                 ||
    ||                                                                      ||
    ||  MISTAKE #2: fork_session instead of --resume                       ||
    ||  - Gets new branch, not continuation                                ||
    ||                                                                      ||
    ||  MISTAKE #3: "Just re-read files"                                   ||
    ||  - Re-reading does NOT clear stale tool results!                    ||
    ||                                                                      ||
    ||  MISTAKE #4: Transferring tool results instead of knowledge          ||
    ||  - Must summarize INSIGHTS, not paste snapshots!                    ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  3. INTERVIEW TIPS:                                                  ||
    ||                                                                      ||
    ||  - Mention "stale context" and "contradictory behavior"            ||
    ||  - Explain --resume vs fork_session vs fresh start                ||
    ||  - Key differentiator: Transfer KNOWLEDGE, not tool results         ||
    ||  - fork_session = branching, --resume = linear continuation        ||
    ||                                                                      ||
    ||  EXPECTED ANSWER STRUCTURE:                                          ||
    ||  1. State the scenario                                              ||
    ||  2. State the correct approach                                       ||
    ||  3. Explain WHY this approach is correct                            ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  4. KEY RULES TO MEMORIZE:                                           ||
    ||                                                                      ||
    ||  RULE #1: Files changed? -> DON'T use --resume!                     ||
    ||  RULE #2: fork_session = branching, NOT resuming                   ||
    ||  RULE #3: Transfer KNOWLEDGE, not tool results                      ||
    ||  RULE #4: Re-read does NOT clear stale tool results!               ||
    ||                                                                      ||
    +======================================================================+

    Next: practice_02_stale_context_problem.py shows WHY resuming
    after file changes causes contradictory behavior!
    """)


"""
+===========================================================================+
|                                                                           |
|  KEY CONCEPTS FROM THIS FILE:                                           |
|                                                                           |
|  APPROACHES:                                                              |
|  - --resume: Full history restored (only if context valid)             |
|  - fork_session: Independent branches (for exploration)                |
|  - Fresh start + summary: New session with knowledge transfer          |
|                                                                           |
|  REAL-TIME MISTAKES:                                                     |
|  - Using --resume when files changed                                     |
|  - Confusing fork_session with --resume                                  |
|  - Re-reading files doesn't fix stale context                           |
|  - Transferring tool results (snapshots) instead of knowledge           |
|                                                                           |
|  EXAM TIPS:                                                              |
|  - Mention "stale context" when answering                               |
|  - Always explain WHY an approach is correct                            |
|  - fork_session = branching, --resume = linear continuation            |
|                                                                           |
|  INTERVIEW PREP:                                                        |
|  - "How do you manage context in long sessions?"                         |
|  - Have scenario-based examples ready                                   |
|  - Know the difference between tool results and knowledge               |
|                                                                           |
+===========================================================================+
"""
