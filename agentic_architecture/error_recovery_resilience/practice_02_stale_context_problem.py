"""
+===========================================================================+
|                                                                           |
|  PRACTICE 2: THE STALE CONTEXT PROBLEM                                  |
|                                                                           |
|  Learn WHY resuming after file changes causes contradictory behavior     |
|  + REAL-TIME SCENARIOS + INTERVIEW GUIDE FOR EXPERTS                     |
|                                                                           |
+===========================================================================

THE STALE CONTEXT PROBLEM
===========================================================================

    When you resume a session, the ENTIRE conversation history is restored,
    including every tool result from the previous session.

    This causes agents to reason from OUTDATED file contents alongside CURRENT
    data, producing CONTRADICTORY advice!

INTERVIEW PREP: "Why does Claude Code sometimes give contradictory advice?"
This question tests your understanding of session state management.

===========================================================================
 DAY 1: Initial Analysis (What Happens)
===========================================================================

    User: "Analyze auth.ts for security issues"
    Agent reads auth.ts -> finds: "Uses MD5 for hashing"
    Agent: "You should upgrade from MD5 to bcrypt"
    Tool result stored: "File auth.ts: uses MD5 hashing"

    User implements the fix (changes auth.ts)

    +-----------------------------------------------------------------------+
    | VISUALIZATION: Day 1 Tool Result                                     |
    +-----------------------------------------------------------------------+
    |                                                                       |
    |  Tool Result:                                                         |
    |  +---------------------------------------------------------------------+|
    |  | File: auth.ts                                                      ||
    |  | Found: "Uses MD5 hashing"                                          ||
    |  | Timestamp: Day 1, 10:30 AM                                        ||
    |  +---------------------------------------------------------------------+|
    |                                                                       |
    |  This tool result is STORED in conversation history!                |
    |                                                                       |
    +-----------------------------------------------------------------------+

===========================================================================
 DAY 2: Resume Session (The Problem Emerges!)
===========================================================================

    User: "claude --resume day1-session"
    Conversation history restored with tool results!
    Tool result still says: "auth.ts uses MD5" <- STALE!

    +-----------------------------------------------------------------------+
    | VISUALIZATION: Day 2 - Dual Information Conflict                      |
    +-----------------------------------------------------------------------+
    |                                                                       |
    |  RESUMED SESSION:                                                     |
    |  +---------------------------------------------------------------------+|
    |  | Tool Result from Day 1:                                           ||
    |  |   "auth.ts uses MD5 hashing" <- STALE (outdated info)              ||
    |  +---------------------------------------------------------------------+|
    |                              ^                                       |
    |                              |                                        |
    |                     CONFLICTING INFO!                                |
    |                              |                                        |
    |                              v                                        |
    |  +---------------------------------------------------------------------+|
    |  | Fresh File Read (Day 2):                                          ||
    |  |   "auth.ts uses bcrypt" <- CURRENT (now correct)                   ||
    |  +---------------------------------------------------------------------+|
    |                                                                       |
    |  Agent has BOTH in context -> CONFUSION!                             |
    |                                                                       |
    +-----------------------------------------------------------------------+

=======================================================================
 POSSIBLE CONTRADICTORY RESPONSES FROM THE AGENT
=======================================================================

    WRONG RESPONSE #1:
    "Your auth.ts uses MD5 which is insecure..."
    Based on stale tool result, giving advice about FIXED issue!
    -> Developer: "I already fixed that!"

    WRONG RESPONSE #2:
    "auth.ts uses bcrypt, which is good..."
    Fresh read correct, but may conflict with other stale findings
    -> Inconsistent with earlier session conclusions

    WRONG RESPONSE #3:
    "It seems auth.ts was changed from MD5 to bcrypt..."
    Acknowledging conflict, but still CONFUSED
    -> Shows the agent doesn't trust its own context

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


def explain_stale_context_problem():
    """
    Explains the stale context problem with visual diagrams and examples.
    """

    client = anthropic.Anthropic(api_key=API_KEY)

    print("\n" + "=" * 70)
    print("THE STALE CONTEXT PROBLEM - COMPLETE EXPLANATION")
    print("=" * 70)

    print("""
    +======================================================================+
    ||                                                                      ||
    ||  WHAT IS STALE CONTEXT?                                             ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  When you use --resume, ALL conversation history is restored,        ||
    ||  including tool results from previous sessions.                     ||
    ||                                                                      ||
    ||  These tool results are "stale" when:                                ||
    ||  - Files have been modified since they were generated               ||
    ||  - Dependencies have been updated                                   ||
    ||  - Configuration has changed                                        ||
    ||                                                                      ||
    ||  The stale data conflicts with FRESH information,                   ||
    ||  causing the agent to give CONTRADICTORY advice!                    ||
    ||                                                                      ||
    +======================================================================+
    """)

    print("""
    +======================================================================+
    ||                                                                      ||
    ||  VISUAL: How Stale Context Happens                                   ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||    DAY 1: Analysis Session                                           ||
    ||    ------------                                                     ||
    ||    +----------------------+                                         ||
    ||    | Tool reads auth.ts   | --> Finds: "MD5 hashing"                ||
    |    | Tool Result STORED   | --> Tool result: "auth.ts uses MD5"     ||
    |    +----------------------+                                         ||
    ||          |                                                           ||
    ||          v                                                           |
    ||    User implements fix (changes auth.ts)                            ||
    ||          |                                                           |
    ||          v                                                           ||
    ||    DAY 2: Resume Session                                             |
    ||    ------------                                                     ||
    ||    +----------------------+                                         ||
    ||    | --resume DAY1        | --> ALL history restored!             ||
    ||    | Tool Result STILL   | --> Still says: "auth.ts uses MD5"    ||
    |    | + Fresh read auth.ts | --> Now shows: "uses bcrypt"           ||
    |    +----------------------+                                         ||
    |          |                                                           |
    |          v                                                           ||
    |    CONFLICT! Agent has:                                              |
    |    - OLD tool result: "uses MD5"                                     ||
    |    - NEW file read: "uses bcrypt"                                   ||
    |    = CONFUSION = CONTRADICTORY advice                                ||
    |                                                                      ||
    +======================================================================+
    """)

    message = client.messages.create(
        model="claude-haiku-4-5-20250601",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": "You analyze code on Day 1 and find an SQL injection "
                      "vulnerability. On Day 2, you resume the session. The "
                      "developer says they fixed it. You read the file and see "
                      "the fix. But your old tool result says the vulnerability "
                      "still exists. How do you resolve this conflict?"
        }]
    )

    print("AI Response to explaining the dilemma:")
    print(f"    {message.content[0].text[:350]}...")


def show_real_time_scenarios():
    """
    Shows REAL-TIME scenarios where stale context causes problems.
    """

    print("\n" + "=" * 70)
    print("REAL-TIME PRODUCTION SCENARIOS")
    print("=" * 70)

    print("""
    +======================================================================+
    ||                                                                      ||
    ||  SCENARIO #1: Security Audit Gone Wrong                            ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  CONTEXT: You're conducting a security audit on a 100-file app.    ||
    ||  Day 1: You analyze files 1-50, find 10 issues including MD5       ||
    ||         hashing in auth.ts. Developer fixes all 10 issues.          ||
    ||  Day 2: You resume session. Developer asks to continue audit.     ||
    ||                                                                      ||
    ||  WHAT HAPPENS:                                                      ||
    ||  - Resume restores ALL tool results from Day 1                     ||
    ||  - Tool result still says "auth.ts uses MD5"                        ||
    ||  - Agent reads current auth.ts = "uses bcrypt" (fixed!)             ||
    ||  - Agent gives advice: "Upgrade from MD5 to bcrypt" <- ALREADY FIXED||
    ||                                                                      ||
    ||  REAL CONSEQUENCE:                                                  ||
    ||  - Developer frustrated: "I already fixed that!"                    ||
    ||  - Lost trust in Claude Code                                        ||
    ||  - Wasted time re-explaining context                                ||
    ||                                                                      ||
    ||  CORRECT FIX: Fresh start + summary injection                        ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  SCENARIO #2: Refactoring With Stale References                      ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  CONTEXT: You're refactoring a monolithic auth service to modules. ||
    ||  Day 1: You identify components: auth.ts, token.ts, session.ts     ||
    ||  Developer reorganizes the folder structure.                        ||
    ||  Day 2: You resume session.                                        ||
    ||                                                                      ||
    ||  WHAT HAPPENS:                                                      ||
    ||  - Resume restores tool results with old file paths                 ||
    ||  - agent says: "refactor auth.ts" <- FILE MOVED!                    ||
    ||  - agent says: "token.ts has these methods" <- FILE DELETED!        ||
    ||  - agent tries to reference files that don't exist                  |
    ||                                                                      ||
    ||  REAL CONSEQUENCE:                                                  ||
    ||  - Agent makes recommendations about non-existent files             ||
    |  - Confusing guidance that doesn't match reality                    ||
    ||  - Refactoring guidance becomes unreliable                         ||
    ||                                                                      ||
    ||  CORRECT FIX: Fresh start + summary injection                        ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  SCENARIO #3: API Migration With Mixed Versions                    ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  CONTEXT: Analyzing code for React 17 to React 18 migration.      ||
    ||  Day 1: You find deprecated API usage: componentWillMount         ||
    ||  Developer updates React, fixes deprecated APIs.                  ||
    ||  Day 2: You resume session.                                        ||
    ||                                                                      ||
    ||  WHAT HAPPENS:                                                      ||
    ||  - Resume restores old tool results referencing React 17 APIs       ||
    |  - agent sees new code = context says old (stale)                   ||
    ||  - Agent says: "This API is deprecated" <- ALREADY FIXED            ||
    ||  - Agent flags issues that were already resolved                    |
    ||                                                                      ||
    ||  REAL CONSEQUENCE:                                                  ||
    ||  - Developer gets incorrect migration warnings                     ||
    ||  - Wastes time investigating "issues" that are actually fine       ||
    ||  - Confusion about actual migration requirements                     |
    ||                                                                      ||
    ||  CORRECT FIX: Fresh start + summary injection                        ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  SCENARIO #4: Database Schema Changes                               ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  CONTEXT: Reviewing code for a database migration.                  ||
    ||  Day 1: You analyze models/user.ts - has "email" field             ||
    ||  Developer adds "email_verified" and "phone" fields                ||
    ||  Day 2: You resume session to continue analysis.                    ||
    ||                                                                      ||
    ||  WHAT HAPPENS:                                                      |
    ||  - Resume restores tool results about old schema                    ||
    ||  - Agent has conflicting info about User model                     ||
    ||  - Agent gives advice about fields that don't exist in old schema   ||
    |  - Or recommends things that are already done                        ||
    |                                                                      ||
    ||  REAL CONSEQUENCE:                                                  ||
    ||  - Agent produces inconsistent code suggestions                    ||
    ||  - Confusion about what the current schema actually is             ||
    ||  - Potentially breaking database changes                            ||
    ||                                                                      ||
    ||  CORRECT FIX: Fresh start + summary injection                        ||
    ||                                                                      ||
    +======================================================================+
    """)


def show_naive_fix_fails():
    """
    Shows why naive fixes (re-reading) don't solve the problem.
    """

    client = anthropic.Anthropic(api_key=API_KEY)

    print("\n" + "=" * 70)
    print("WHY NAIVE FIXES DON'T WORK")
    print("=" * 70)

    print("""
    +======================================================================+
    ||                                                                      ||
    ||  NAIVE FIX #1: "Just resume and re-read changed files"              ||
    ||  ================================================================   ||
    ||                                                                      |
    ||  WHAT DEVELOPERS THINK:                                              ||
    ||  "If I just re-read the files, the agent should know the new state" ||
    ||                                                                      ||
    ||  WHY IT FAILS:                                                       ||
    ||  - Re-reading gives FRESH file content                               ||
    ||  - But OLD tool results are STILL in conversation history!         ||
    ||  - Agent has BOTH stale AND fresh in context                       ||
    ||  - Agent doesn't know which to trust!                               ||
    ||                                                                      ||
    ||  THE AGENT'S DILEMMA:                                                ||
    ||  - Tool result from yesterday: "auth.ts uses MD5"                   ||
    |  - Fresh read today: "auth.ts uses bcrypt"                           ||
    ||  - Which is the CURRENT truth?                                      ||
    ||  - Agent gets confused and may give conflicting advice!           ||
    ||                                                                      |
    ||  +--------------------------------------------------------------------+|
    ||  | KEY INSIGHT: Re-reading files does NOT clear old tool results! | ||
    ||  +--------------------------------------------------------------------+|
    ||                                                                      |
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  NAIVE FIX #2: "I'll be more specific in internal details"                ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WHAT DEVELOPERS THINK:                                              ||
    ||  "If I say 'remember, auth.ts was updated', it'll be clear"        ||
    ||                                                                      ||
    ||  WHY IT FAILS:                                                       ||
    ||  - Prompt improvement can help ~90% of the time                      ||
    ||  - But stale tool results are STILL in context                      ||
    ||  - Agent still has to reconcile conflicting information            ||
    ||  - Prompts cannot "delete" tool results from conversation!        ||
    ||                                                                      ||
    ||  THE REAL FIX:                                                       ||
    ||  - Start a FRESH session (no history)                              ||
    ||  - Inject structured SUMMARY of what you learned                     ||
    ||  - NO stale tool results = NO conflict!                            ||
    ||                                                                      |
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  NAIVE FIX #3: "I'll delete the old session and start fresh"       ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WHAT DEVELOPERS THINK:                                              ||
    ||  "If I start a completely new session, context is clean"           ||
    ||                                                                      ||
    ||  PARTIAL TRUTH - BUT INCOMPLETE:                                     ||
    ||  - Yes, new session = no stale tool results                         ||
    ||  - BUT - No context about prior work                               ||
    ||  - Agent doesn't know what you found earlier                        ||
    ||  - Must re-explain everything                                      ||
    ||                                                                      ||
    ||  THE COMPLETE FIX:                                                   ||
    ||  - Fresh session + SUMMARY INJECTION                                 ||
    ||  - Start fresh (no stale tool results)                              ||
    ||  - Inject knowledge: "Day 1 found X, User fixed Y"                 ||
    ||  - Agent has context WITHOUT stale data!                            ||
    ||                                                                      |
    +======================================================================+
    """)

    message = client.messages.create(
        model="claude-haiku-4-5-20250601",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": "A developer says: 'I'll just resume the session and ask "
                      "Claude to re-read the modified files. That should fix any "
                      "stale context issues.' What's wrong with this approach?"
        }]
    )

    print("Why this reasoning is flawed:")
    print(f"    {message.content[0].text[:350]}...")


def show_interview_qa():
    """
    Shows interview questions and expert answers.
    """

    print("\n" + "=" * 70)
    print("INTERVIEW Q&A PREPARATION")
    print("=" * 70)

    print("""
    ======================================================================
    Q1: "Why does Claude Code sometimes give contradictory advice?"
    ======================================================================

    FRAME YOUR ANSWER LIKE THIS:

    STAGE 1: Explain the root cause
    --------------------------------
    "Claude Code's contradictory behavior usually stems from stale context.
    When you use --resume, the entire conversation history is restored,
    including tool results from previous sessions."

    STAGE 2: Explain what happens
    ------------------------------
    "If files have been modified since those tool results were generated,
    the agent now has conflicting information: old tool results showing
    the previous state, AND fresh file reads showing the current state."

    STAGE 3: Explain the symptom
    -----------------------------
    "This causes the agent to give contradictory advice - sometimes
    recommending fixes for issues that were already resolved, or
    approving patterns it previously flagged as problematic."

    STAGE 4: Give the solution
    ----------------------------
    "The fix is to use fresh start + summary injection: start a new
    session with no stale tool results, and inject a curated summary
    of the knowledge gained from the previous session."

    ======================================================================
    Q2: "Why doesn't re-reading files fix the stale context problem?"
    ======================================================================

    EXPERT ANSWER:
    "Re-reading files gives fresh content, but it does NOT clear the
    old tool results from conversation history. The agent still has
    both in its context, leading to confusion about which is correct.
    The stale data is not in the files - it's in the conversation
    history that gets restored with --resume."

    ======================================================================
    Q3: "What's the difference between tool results and knowledge?"
    ======================================================================

    EXPERT ANSWER:
    "Tool results are snapshots - 'File X contains Y' - that become
    stale when files change. Knowledge is insights - 'Day 1 found SQL
    injection in database.ts' - that remain relevant even when files
    are modified. Knowledge transfer works because it captures
    discoveries and insights, not file contents."

    ======================================================================
    Q4: "How do you prevent stale context in production workflows?"
    ======================================================================

    EXPERT ANSWER:
    "In production, I follow these rules:
    1. Use --resume only when context is still valid (no file changes)
    2. Use fork_session for branching/exploration tasks
    3. After file changes, always use fresh start + summary injection
    4. Transfer KNOWLEDGE, not tool results (describe insights, not snapshots)
    5. Specify exactly which files have changed for targeted re-analysis"

    """)


def show_symptoms_in_action():
    """
    Shows real symptoms of stale context in action.
    """

    print("\n" + "=" * 70)
    print("REAL SYMPTOMS OF STALE CONTEXT IN ACTION")
    print("=" * 70)

    print("""
    +======================================================================+
    ||                                                                      ||
    ||  SYMPTOM #1: Inconsistent Security Findings                          ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  Dialogue showing inconsistency:                                     ||
    ||  ----------------------------------------------------------------   ||
    ||  User: "File 3 has an SQL injection, fix it"                         ||
    ||  Agent: "Fixed! Added parameterized query."                          ||
    ||                                                                      ||
    ||  [Hours later, in resumed session]                                  ||
    ||                                                                      ||
    ||  User: "Check File 11 for security issues"                          ||
    ||  Agent: "No issues found."                                           ||
    ||                                                                      ||
    ||  REALITY: File 11 has the SAME SQL injection pattern as File 3!    ||
    ||  CAUSE: Stale context from earlier work consumed attention budget   ||
    ||         Agent didn't apply the same scrutiny to File 11            ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  SYMPTOM #2: Confusion About Current Code State                     ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  Dialogue showing confusion:                                         ||
    |  ----------------------------------------------------------------   ||
    ||  User: "Did we fix the MD5 issue in auth.ts?"                        ||
    ||  Agent: "I don't see MD5 in the current file..."                    ||
    ||  Agent: "But my context from yesterday said it uses MD5..."         ||
    ||  Agent: "So was it fixed before or did I miss it?"                  ||
    ||  User: "So is it fixed or not?"                                     ||
    ||  Agent: "I'm not sure..."                                           ||
    ||                                                                      |
    ||  CAUSE: Stale tool result saying MD5 exists + fresh file saying it   ||
    ||         doesn't = agent uncertain about what happened                ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      |
    ||  SYMPTOM #3: Contradictory Recommendations                          ||
    ||  ================================================================   ||
    ||                                                                      ||
    |  Day 1: "auth.ts uses MD5 - upgrade to bcrypt" (flagged issue)       ||
    |                                                                      |
    |  Day 2: Resume session, same agent says:                            ||
    ||  "auth.ts uses bcrypt - looking good!" (approved now?)             ||
    ||                                                                      ||
    ||  Day 3: Resume session again:                                       ||
    |  "Your auth.ts still uses MD5, upgrade to bcrypt" <- BACK TO DAY 1 ||
    |                                                                      ||
    |  CAUSE: Agent oscillates between trusting stale tool result and       |
    |         fresh file reads, resulting in contradictory guidance        |
    |                                                                      |
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  SYMPTOM #4: Wasted Time Re-explaining Context                       ||
    ||  ================================================================   ||
    |                                                                      |
    |  Developer: "I already fixed that issue you mentioned yesterday"    ||
    |  Agent: "Which issue? I'm not seeing that in my current context"   ||
    |  Developer: "The MD5 hashing in auth.ts"                           ||
    |  Agent: "Oh yes, I see MD5 in my context - upgrade it to bcrypt"    ||
    |  Developer: "But I already upgraded it!"                            ||
    |  Agent: "I see the current file uses bcrypt..."                    ||
    |  Agent: "But my history says MD5 was there, so I assumed..."       ||
    |                                                                      ||
    |  CONVERSATION BECOMES BACK-AND-FORTH FRUSTRATION                     |
    |                                                                      |
    +======================================================================+
    """)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("""
+===========================================================================+
|                                                                           |
|  THE STALE CONTEXT PROBLEM - COMPLETE EDITION                            |
|  + REAL-TIME SCENARIOS + INTERVIEW GUIDE                                 |
|                                                                           |
|  This program shows:                                                      |
|  1. WHY stale context causes contradictory behavior                      |
|  2. REAL-TIME production scenarios where it breaks things                |
|  3. Why naive fixes (re-reading) don't work                             |
|  4. Interview Q&A preparation                                           |
|                                                                           |
+===========================================================================+
    """)

    explain_stale_context_problem()
    show_real_time_scenarios()
    show_naive_fix_fails()
    show_interview_qa()
    show_symptoms_in_action()

    print("\n" + "=" * 70)
    print("WHAT WE HAVE LEARNT")
    print("=" * 70)
    print("""
    +======================================================================+
    ||  1. THE STALE CONTEXT PROBLEM:                                       ||
    ||                                                                      ||
    ||  DEFINITION:                                                         ||
    ||  - Resuming restores ALL tool results from previous sessions          ||
    ||  - These become "stale" when files have changed                     ||
    ||  - Agent has conflicting info: stale vs fresh                       ||
    ||  - Contradictory advice emerges!                                     ||
    ||                                                                      ||
    ||  WHY IT HAPPENS:                                                    ||
    ||  - --resume restores the ENTIRE conversation history                 ||
    |  - Tool results = snapshots of files at that moment                  ||
    ||  - If files changed, snapshots show old state                        ||
    ||  - Agent must reconcile stale AND current information                ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  2. REAL-TIME SCENARIOS:                                             ||
    ||                                                                      ||
    ||  SCENARIO #1: Security Audit Gone Wrong                             ||
    ||  - Find MD5 issue, developer fixes, resume, agent re-flags issue     ||
    ||                                                                      ||
    ||  SCENARIO #2: Refactoring With Stale References                     ||
    ||  - Agent gives advice about moved/deleted files                      ||
    ||                                                                      ||
    ||  SCENARIO #3: API Migration With Mixed Versions                     ||
    ||  - Agent flags deprecated APIs that were already migrated           ||
    ||                                                                      ||
    ||  SCENARIO #4: Database Schema Changes                               ||
    ||  - Agent gives advice about old schema, confusing new state         ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  3. WHY NAIVE FIX #1 (re-read files) DOESN'T WORK:                  ||
    ||                                                                      |
    ||  DEVELOPER THINKING: "Re-reading = fresh context"                    ||
    ||                                                                      ||
    ||  WHY IT FAILS:                                                       ||
    ||  - Re-reading gives FRESH file content                               ||
    ||  - BUT: OLD tool results are STILL in conversation!                 ||
    ||  - Agent has BOTH stale and fresh = CONFUSION                       ||
    ||  - Re-reading doesn't delete tool results from history!              ||
    ||                                                                      ||
    ||  THE REAL FIX: Start FRESH session + inject structured summary       ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  4. INTERVIEW Q&A FRAMEWORK:                                         ||
    ||                                                                      ||
    ||  Q: "Why contradictory advice?"                                      ||
    ||  A: Stale context from --resume. Files changed, but old tool         ||
    ||     results still in conversation history. Conflicting info.         ||
    ||                                                                      ||
    ||  Q: "Why doesn't re-reading help?"                                  ||
    ||  A: Re-reading gives fresh content but doesn't clear stale tool       ||
    ||     results. Both are in context. Agent confused.                    ||
    ||                                                                      ||
    ||  Q: "What's the fix?"                                                ||
    ||  A: Fresh start + summary injection. Start session with no history, ||
    ||     inject knowledge of what was learned. Clear + accurate.         ||
    ||                                                                      |
    +======================================================================+

    +======================================================================+
    ||  5. KEY SYMPTOMS TO RECOGNIZE:                                       ||
    ||                                                                      ||
    ||  SYMPTOM #1: Inconsistent findings across similar files              ||
    ||  SYMPTOM #2: Agent confused about whether code was fixed            ||
    ||  SYMPTOM #3: Contradictory recommendations over time               ||
    ||  SYMPTOM #4: Wasted time re-explaining what was done                 ||
    ||                                                                      ||
    ||  IF YOU SEE THESE -> Think STALE CONTEXT!                            ||
    ||                                                                      ||
    +======================================================================+

    Next: practice_03_targeted_reanalysis.py shows THE CORRECT FIX
    with fresh start + summary injection!
    """)


"""
+===========================================================================+
|                                                                           |
|  KEY CONCEPTS FROM THIS FILE:                                             |
|                                                                           |
|  PROBLEM:                                                                 |
|  - Stale context = tool results from before file changes                  |
|  - --resume restores ALL history including stale tool results           |
|  - Agent has conflicting info = contradictory advice                    |
|                                                                           |
|  REAL SCENARIOS:                                                         |
|  - Security audit: fixes re-flagged                                      |
|  - Refactoring: advice on moved/deleted files                            |
|  - API migration: deprecated APIs re-flagged                             |
|  - Schema changes: advice on old schema state                           |
|                                                                           |
|  NAIVE FIX FAILS:                                                        |
|  - "Just re-read files" = Doesn't clear tool results from history!      |
|  - Both stay in context = confusing                                     |
|                                                                           |
|  INTERVIEW TIPS:                                                         |
|  - Mention "stale context" and "contradictory behavior"                 |
|  - Explain WHY naive fixes don't work                                    |
|  - Show you understand the root cause, not just symptoms                |
|                                                                           |
|  EXAM TIPS:                                                              |
|  - "Resume and re-read" = WRONG answer!                                  |
|  - Must explain WHY this is wrong                                        |
|  - Root cause is conversational history restoration                     |
|                                                                           |
+===========================================================================+
"""
