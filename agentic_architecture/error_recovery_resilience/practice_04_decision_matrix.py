"""
+===========================================================================+
|                                                                           |
|  PRACTICE 4: DECISION MATRIX FOR SESSION MANAGEMENT                      |
|                                                                           |
|  Learn when to use each approach based on your specific scenario         |
|  + REAL-TIME SCENARIOS + EXPERT DECISION TREES + INTERVIEW GUIDE        |
|                                                                           |
+===========================================================================+

DECISION MATRIX
===========================================================================

    Use this decision matrix to choose the right approach for your scenario:

    +--------------------------------+-------------------------------------+
    | SCENARIO                       | BEST APPROACH                      |
    +--------------------------------+-------------------------------------+
    | Continue work, no files       | --resume                           |
    | changed, context still valid    | (Full history restored)           |
    +--------------------------------+-------------------------------------+
    | Exploring alternatives/         | fork_session                       |
    | comparing approaches          | (Independent branches)             |
    +--------------------------------+-------------------------------------+
    | Files changed since last       | Fresh start + summary              |
    | session                      | (Clean slate + knowledge)          |
    +--------------------------------+-------------------------------------+
    | Long session with cluttered   | Fresh start + summary              |
    | history                      | (Start clean)                      |
    +--------------------------------+-------------------------------------+
    | Dependency updates occurred   | Fresh start + summary              |
    |                              | (Fresh dependency analysis)        |
    +--------------------------------+-------------------------------------+

INTERVIEW PREP: "How do you decide which session approach to use?"
This tests your understanding of when each approach is appropriate.

===========================================================================
 VISUAL DECISION FLOWCHART
===========================================================================

                            +------------------+
                            |  START          |
                            | Need to manage  |
                            | session?        |
                            +------------------+
                                     |
                                     v
                    +--------------------------------+
                    | Have files changed since      |
                    | last session?                 |
                    +--------------------------------+
                             /              \\
                            /                \\
                           v                  v
                         YES                  NO
                          |                    |
                          v                    v
          +-------------------+    +-------------------------+
          | Fresh Start +      |    | Is this for:          |
          | Summary Injection |    | (a) Continue work,    |
          | (Always when      |    |     or                |
          |  files changed!)  |    | (b) Explore options? |
          +-------------------+    +-------------------------+
                                        /              \\
                                       /                \\
                                      v                  v
                                    (a)                (b)
                                     |                  |
                                     v                  v
                           +---------------+    +-------------+
                           | --resume      |    | fork_session|
                           | (Linear       |    | (Branching) |
                           |  continue)    |    +-------------+
                           +---------------+

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


def show_complete_decision_matrix():
    """
    Shows the complete decision matrix with detailed scenarios.
    """

    print("\n" + "=" * 70)
    print("COMPLETE DECISION MATRIX - SCENARIO ANALYSIS")
    print("=" * 70)

    # Scenario 1
    print("""
    +======================================================================+
    ||                                                                      ||
    ||  SCENARIO 1: Continue Previous Work (No Changes)                   ||
    ||  ================================================================  ||
    ||                                                                      ||
    ||  CONTEXT: Yesterday you were analyzing a codebase.                  ||
    ||            No files have been modified since then.                  ||
    ||            You want to continue exactly where you left off.         ||
    ||                                                                      ||
    ||  APPROACH: --resume <session-name>                                 ||
    ||                                                                      ||
    ||  WHY:                                                              ||
    ||  - Context is still valid                                           ||
    ||  - All tool results are accurate                                   ||
    ||  - Full history restoration is beneficial                           ||
    ||                                                                      ||
    ||  EXAMPLE:                                                          ||
    ||  $ claude --resume security-audit-day1                              ||
    ||                                                                      ||
    ||  VISUAL:                                                            ||
    ||  Day 1: [Full analysis session]                                    ||
    ||                |                                                   ||
    ||                v                                                   ||
    ||  Day 2: --resume (continue with ALL history)                       ||
    ||                                                                      ||
    ||  +--------------------------------------------------------------------+|
    ||  | KEY POINT: Only use when you can say with confidence:             ||
    ||  | "No files have been modified since my last session"              ||
    ||  +--------------------------------------------------------------------+|
    ||                                                                      ||
    +======================================================================+
    """)

    # Scenario 2
    print("""
    +======================================================================+
    ||                                                                      ||
    ||  SCENARIO 2: Exploring Alternatives (Branching)                     ||
    ||  ================================================================  ||
    ||                                                                      ||
    ||  CONTEXT: You're working on a design decision.                       ||
    ||            You want to explore microservices approach AND              ||
    ||            monolithic approach to compare them.                      ||
    ||            Or: Try different refactoring strategies.                 ||
    ||                                                                      ||
    ||  APPROACH: fork_session                                             ||
    ||                                                                      ||
    ||  WHY:                                                              ||
    ||  - Independent branches let you explore without commitment           ||
    ||  - Changes in one branch don't affect the other                     ||
    ||  - Compare approaches side-by-side                                 ||
    ||                                                                      ||
    ||  EXAMPLE:                                                          ||
    ||  /fork_session microservices-exploration                             ||
    ||                                                                      ||
    ||  VISUAL:                                                            ||
    ||                  MASTER                                              ||
    ||                    |                                                  ||
    ||          +---------+---------+                                        ||
    ||          |                   |                                        ||
    ||          v                   v                                        ||
    ||     [microservices]     [monolith]                                   ||
    ||     (Branch A)          (Branch B)                                  ||
    ||                                                                      ||
    ||  +--------------------------------------------------------------------+|
    ||  | KEY POINT: Use for EXPLORATION, not for continuing work!          ||
    ||  | fork_session creates INDEPENDENT branches, not shared context      ||
    ||  +--------------------------------------------------------------------+|
    ||                                                                      ||
    +======================================================================+
    """)

    # Scenario 3
    print("""
    +======================================================================+
    ||                                                                      ||
    ||  SCENARIO 3: Resuming After File Changes                            ||
    ||  ================================================================  ||
    ||                                                                      ||
    ||  CONTEXT: Yesterday you analyzed 50 files.                          ||
    ||            User modified 3 files overnight based on your feedback.   ||
    ||            You want to continue the analysis.                       ||
    ||                                                                      ||
    ||  APPROACH: Fresh start + summary injection                          ||
    ||                                                                      ||
    ||  WHY:                                                              ||
    ||  - Tool results for the 3 modified files are stale                  ||
    ||  - Need fresh analysis for those specific files                     ||
    ||  - Other 47 files are fine (reference via summary)                 ||
    ||                                                                      ||
    ||  EXAMPLE:                                                          ||
    ||  $ claude --session security-audit-round2                            ||
    ||                                                                      ||
    ||  [Inject summary of prior findings]                                 ||
    ||  [Specify modified files: auth.ts, database.ts, api-routes.ts]     ||
    ||  [Ask to re-analyze modified files]                                 ||
    ||                                                                      ||
    ||  VISUAL:                                                            ||
    ||  OLD SESSION: Tool results (3 stale) + Tool results (47 valid)     ||
    ||                 x                                                      ||
    ||  NEW SESSION: [Summary: "47 findings OK, 3 need re-check"]         ||
    ||  +--------------------------------------------------------------------+|
    ||  | KEY POINT: Files changed = ALWAYS fresh start + summary!         ||
    ||  | Even ONE file changed means you need this approach               ||
    ||  +--------------------------------------------------------------------+|
    ||                                                                      ||
    +======================================================================+
    """)

    # Scenario 4
    print("""
    +======================================================================+
    ||                                                                      ||
    ||  SCENARIO 4: Cluttered History (Too Many Turns)                     ||
    ||  ================================================================  ||
    ||                                                                      ||
    ||  CONTEXT: 3-hour session with 200+ conversation turns.             ||
    ||            History is getting unwieldy.                             ||
    ||            You need to wrap up and document findings.               ||
    ||                                                                      ||
    ||  APPROACH: Fresh start + summary injection                          ||
    ||                                                                      ||
    ||  WHY:                                                              ||
    ||  - Start clean                                                     ||
    ||  - Inject curated summary of all findings                           ||
    ||  - Agent can work with clean slate while retaining knowledge        ||
    ||                                                                      ||
    ||  EXAMPLE:                                                          |
    ||  $ claude --session architecture-review-clean                       |
    ||                                                                      ||
    ||  [Inject comprehensive summary of 3-hour session]                   ||
    ||  [Continue work from a clean state]                                 ||
    ||                                                                      ||
    ||  +--------------------------------------------------------------------+|
    ||  | KEY POINT: Long sessions can benefit from periodic "clean starts" |
    ||  | to maintain clarity and avoid context dilution                   ||
    ||  +--------------------------------------------------------------------+|
    ||                                                                      ||
    +======================================================================+
    """)

    # Scenario 5
    print("""
    +======================================================================+
    ||                                                                      ||
    ||  SCENARIO 5: Dependency Updates                                      ||
    ||  ================================================================  ||
    ||                                                                      ||
    ||  CONTEXT: You analyzed code using React 17.                          ||
    ||            User upgraded to React 18 overnight.                       ||
    ||            You need to re-analyze for compatibility issues.         ||
    ||                                                                      ||
    ||  APPROACH: Fresh start + summary injection                          ||
    ||                                                                      ||
    ||  WHY:                                                              ||
    ||  - Dependency changes can affect the entire codebase                 ||
    ||  - Need fresh analysis with new dependency context                 ||
    ||  - Old tool results may reference deprecated APIs                   ||
    ||                                                                      ||
    ||  EXAMPLE:                                                          |
    ||  $ claude --session react18-migration                                |
    ||                                                                      ||
    ||  [Inject prior findings: "5 files had deprecated APIs"]            ||
    ||  [Specify: "Updated React 17 -> React 18"]                           ||
    ||  [Ask: "Re-analyze for React 18 compatibility"]                    ||
    ||                                                                      ||
    ||  +--------------------------------------------------------------------+|
    ||  | KEY POINT: Any environment change (dependencies, config, etc.)     ||
    ||  | means you need fresh analysis with updated context                |
    ||  +--------------------------------------------------------------------+|
    ||                                                                      |
    +======================================================================+
    """)


def show_real_time_mistakes():
    """
    Shows real mistakes developers make with session decisions.
    """

    print("\n" + "=" * 70)
    print("REAL-TIME MISTAKES DEVELOPERS MAKE")
    print("=" * 70)

    print("""
    +======================================================================+
    ||                                                                      ||
    ||  MISTAKE #1: Using --resume when files changed                      ||
    ||  ================================================================  ||
    ||                                                                      ||
    ||  SCENARIO:                                                          ||
    ||  "I analyzed my auth code yesterday. Today I made some changes.      |
    ||   Can I just resume?"                                                |
    ||                                                                      ||
    ||  WRONG ANSWER:                                                      |
    ||  "Yes, use --resume and re-read the modified files"                 ||
    ||                                                                      ||
    ||  REAL CONSEQUENCE:                                                  ||
    ||  - Stale tool results cause contradictory advice                    ||
    ||  - Agent flags fixes that are already done                          ||
    ||  - Confused analysis of current state                              ||
    ||                                                                      ||
    ||  CORRECT ANSWER:                                                    |
    ||  "No - use fresh start + summary injection instead"                 |
    ||                                                                      ||
    ||  WHY: --resume restores ALL tool results, including stale ones.       |
    ||       Re-reading doesn't clear them.                                |
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  MISTAKE #2: Using fork_session for continuation                    ||
    ||  ================================================================  ||
    ||                                                                      ||
    ||  SCENARIO:                                                          ||
    ||  "I need to continue the work from yesterday. Should I fork?"       ||
    ||                                                                      ||
    ||  WRONG ANSWER:                                                      |
    ||  "Yes, use fork_session to create a new session"                    ||
    ||                                                                      ||
    ||  REAL CONSEQUENCE:                                                  |
    ||  - fork_session creates INDEPENDENT branch                          |
    ||  - No shared context with original session                          ||
    ||  - All work from yesterday is gone                                 ||
    ||                                                                      ||
    ||  CORRECT ANSWER:                                                    ||
    ||  "Use --resume to continue from yesterday"                          ||
    ||                                                                      ||
    ||  WHY: fork_session is for EXPLORATION, not continuation.            ||
    ||       --resume continues a specific session linearly.               ||
    ||                                                                      |
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  MISTAKE #3: Always starting fresh sessions                          ||
    ||  ================================================================  ||
    ||                                                                      ||
    ||  SCENARIO:                                                          |
    ||  "I always start fresh sessions to avoid any confusion"             ||
    ||                                                                      ||
    ||  WRONG APPROACH:                                                    ||
    ||  - Start fresh session every time                                   |
    ||  - Don't leverage --resume when context is valid                    ||
    ||  - Lose valuable conversation history                               ||
    ||                                                                      ||
    ||  WHEN --resume IS CORRECT:                                          ||
    ||  - Files haven't changed                                            ||
    ||  - Context is still relevant                                         ||
    ||  - Want to continue exact work                                       ||
    ||                                                                      ||
    ||  WHY THIS MATTERS:                                                  ||
    ||  - --resume gives FULL context without stale issues                 ||
    ||  - More efficient than re-explaining everything                     ||
    ||  - Maintains continuity of work                                     ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  MISTAKE #4: Not specifying changed files                           ||
    ||  ================================================================  ||
    ||                                                                      ||
    ||  SCENARIO:                                                          |
    ||  "I used fresh start + summary, but agent missed the fixes"        ||
    ||                                                                      ||
    ||  WRONG SUMMARY:                                                     ||
    ||  ===                                                                  ||
    ||  I analyzed 50 files yesterday. Made some changes. Continue.       ||
    ||  ===                                                                  |
    ||                                                                      ||
    ||  CORRECT SUMMARY:                                                   ||
    ||  ===                                                                  |
    ||  Prior findings: auth.ts had MD5, database.ts had SQL vuln         ||
    ||  Modified files: auth.ts (fixed to bcrypt)                          ||
    ||  Please re-analyze: auth.ts to verify the fix                       ||
    ||  ===                                                                  |
    ||                                                                      ||
    ||  WHY THIS MATTERS:                                                  ||
    ||  - Without specifics, agent doesn't know what to focus on          ||
    ||  - May re-analyze unchanged files instead of modified ones          ||
    ||  - Clear instructions = better results                             ||
    ||                                                                      |
    +======================================================================+
    """)


def show_interview_qa():
    """
    Shows interview questions and expert answers.
    """

    client = anthropic.Anthropic(api_key=API_KEY)

    print("\n" + "=" * 70)
    print("INTERVIEW Q&A PREPARATION")
    print("=" * 70)

    # Q1
    print("""
    ======================================================================
    Q1: "How do you decide which session approach to use?"
    ======================================================================

    STRUCTURE YOUR ANSWER:

    STEP 1: Ask the key question
    ----------------------------
    "First, I ask: 'Have any files changed since the last session?'"

    STEP 2: Branch based on answer
    -------------------------------
    "If YES - always use fresh start + summary injection.
     If NO - then ask: 'Is this for exploring alternatives or continuing work?'

    STEP 3: Choose based on purpose
    --------------------------------
    For exploration/branching: use fork_session
    For linear continuation: use --resume

    FULL DECISION TREE:
    Files changed?
        |
        +-- YES --> Fresh start + summary
        |
        +-- NO --> Exploring alternatives?
                   |
                   +-- YES --> fork_session
                   |
                   +-- NO --> --resume
    """)

    print("""
    ======================================================================
    Q2: "What if only ONE file changed - do I still need fresh start?"
    ======================================================================

    EXPERT ANSWER:
    "Yes, absolutely! Even ONE file change means --resume is inappropriate.
    The stale tool result for that file will cause confusion. Always use
    fresh start + summary injection when ANY files have changed.

    The key insight is that even a single stale tool result can cause
    contradictory behavior. The agent will have:
    - Old tool result saying the old state
    - Fresh file read showing the new state
    - Conflicting information = confused agent"

    ======================================================================
    Q3: "When would you NOT use --resume even if files haven't changed?"
    ======================================================================

    EXPERT ANSWER:
    "Two scenarios:

    1. EXPLORATION MODE:
    Even with unchanged files, if you want to explore alternative approaches,
    you use fork_session. For example, trying microservices vs monolith
    design - these are different branches, not linear continuation.

    2. FRESH PERSPECTIVE:
    Sometimes a long session gets cluttered. Even without file changes,
    starting fresh with a summary can provide clearer context. Though
    --resume is technically correct in this case, fresh start + summary
    can be more efficient for very long sessions."

    ======================================================================
    Q4: "What's the most common mistake with session management?"
    ======================================================================

    EXPERT ANSWER:
    "The most common mistake is using --resume when files have changed,
    then trying to fix it with 'just re-read the files.' This doesn't work
    because re-reading doesn't clear the stale tool results from history.

    The correct approach is always fresh start + summary when files change.
    This is counterintuitive for many developers who think 're-reading = fresh.'"

    """)

    message = client.messages.create(
        model="claude-haiku-4-5-20250601",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": ("As an expert, give a one-minute explanation of how to "
                       "choose between --resume, fork_session, and fresh start "
                       "+ summary for managing Claude Code sessions.")
        }]
    )

    print("Expert explanation:")
    print(f"    {message.content[0].text[:400]}...")


def show_exam_traps():
    """
    Highlights common exam traps to avoid.
    """

    print("\n" + "=" * 70)
    print("EXAM TRAPS - HOW TO AVOID THEM")
    print("=" * 70)

    print("""
    +======================================================================+
    ||                                                                      ||
    ||  TRAP #1: "Just resume and re-read changed files"                  ||
    ||  ================================================================  ||
    ||                                                                      ||
    ||  WHY IT'S WRONG:                                                    ||
    ||  - Re-reading gives fresh content                                   ||
    ||  - But stale tool results are STILL in conversation history!        ||
    ||  - Agent has conflicting information = confused                    ||
    ||                                                                      ||
    ||  THE EXAM TESTS:                                                    ||
    ||  - Do you understand that re-reading doesn't clear history?        ||
    ||  - Do you know the root cause of stale context?                     ||
    ||                                                                      ||
    ||  CORRECT ANSWER: Fresh start + summary injection                    ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  TRAP #2: Confusing fork_session with --resume                      ||
    ||  ================================================================  ||
    ||                                                                      ||
    ||  SCENARIO: "User wants to continue work from yesterday"             ||
    ||                                                                      ||
    ||  WRONG ANSWER: fork_session                                         ||
    ||                                                                      ||
    ||  WHY IT'S WRONG:                                                    ||
    ||  - fork_session creates INDEPENDENT branch                          ||
    ||  - No shared context with original session                          ||
    ||  - Should use --resume for continuation                             ||
    ||                                                                      ||
    ||  KEY DISTINCTION:                                                   ||
    ||  - fork_session = branching (exploration)                          ||
    ||  - --resume = linear continuation (same conversation)              ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  TRAP #3: Using --resume when "a few files" changed                  ||
    ||  ================================================================  ||
    ||                                                                      ||
    ||  SCENARIO: "Only 3 of 50 files changed - can I still use resume?" ||
    ||                                                                      ||
    ||  WRONG ANSWER: Yes, resume is fine with 're-read the changed files'" ||
    ||                                                                      ||
    ||  WHY IT'S WRONG:                                                    |
    ||  - Even ONE stale tool result causes problems                       ||
    ||  - Agent has conflicting info for those 3 files                     ||
    ||  - Contradictory behavior will emerge                               ||
    ||                                                                      ||
    ||  CORRECT ANSWER: Fresh start + summary injection                    ||
    ||                                                                      ||
    ||  EVEN 1 FILE CHANGE = FRESH START + SUMMARY                         ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  TRAP #4: Forgetting that fork_session is INDEPENDENT               ||
    ||  ================================================================  ||
    ||                                                                      ||
    ||  SCENARIO: "I used fork_session, why don't I see my previous work?"  ||
    ||                                                                      ||
    ||  WHY THIS HAPPENS:                                                  ||
    ||  - fork_session creates a NEW, INDEPENDENT branch                    ||
    ||  - No context is shared from the original session                   |
    ||  - Each branch operates completely separately                       ||
    ||                                                                      ||
    ||  CORRECT EXPECTATION:                                                |
    ||  - fork_session = start fresh with no prior context                 ||
    ||  - If you want context, you need to inject via summary              ||
    ||                                                                      ||
    +======================================================================+
    """)


def interactive_decision_helper():
    """
    Provides an interactive helper for making session management decisions.
    """

    print("\n" + "=" * 70)
    print("INTERACTIVE DECISION HELPER")
    print("=" * 70)

    print("""
    +======================================================================+
    ||                                                                      ||
    ||  ANSWER THESE QUESTIONS TO FIND YOUR APPROACH:                       ||
    ||                                                                      ||
    +======================================================================+

    QUESTION 1: Have any files changed since the last session?
    ----------------------------------------------------------------------
    [Files modified? Updated dependencies? Configuration changes?]

        YES -> ANSWER: Fresh start + summary injection
               Go to Question A

        NO  -> Go to Question 2

    QUESTION 2: Is this for exploring alternatives?
    ----------------------------------------------------------------------
    [Trying different approaches? A/B testing? Comparing strategies?]

        YES -> ANSWER: fork_session
               (Creates independent branch for exploration)

        NO  -> ANSWER: --resume
               (Continue linear work with full context)

    QUESTION A (after confirming fresh start needed):
    ----------------------------------------------------------------------
    What do you want to inject?

        "Prior findings summary: [list what you found]"
        "Modified files: [list what changed]"
        "What to focus on: [your goals for this session]"

    +======================================================================+
    ||                                                                      ||
    ||  QUICK REFERENCE:                                                   ||
    ||                                                                      ||
    ||  Files changed? YES + Any scenario -> Fresh start + summary        ||
    ||  Files changed? NO  + Exploring?  -> fork_session                 ||
    ||  Files changed? NO  + Continuing?  -> --resume                      ||
    ||                                                                      ||
    +======================================================================+
    """)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("""
+===========================================================================+
|                                                                           |
|  DECISION MATRIX FOR SESSION MANAGEMENT                                 |
|  + REAL-TIME SCENARIOS + EXPERT DECISION TREES                           |
|                                                                           |
|  This program covers:                                                    |
|  1. Complete decision matrix with 5 scenarios                            |
|  2. Real-time mistakes developers make                                   |
|  3. Interview Q&A preparation                                           |
|  4. Exam traps and how to avoid them                                   |
|  5. Interactive decision helper                                          |
|                                                                           |
+===========================================================================+
    """)

    show_complete_decision_matrix()
    show_real_time_mistakes()
    show_interview_qa()
    show_exam_traps()
    interactive_decision_helper()

    print("\n" + "=" * 70)
    print("WHAT WE HAVE LEARNT")
    print("=" * 70)
    print("""
    +======================================================================+
    ||  1. DECISION MATRIX - WHEN TO USE EACH APPROACH:                   ||
    ||                                                                      ||
    ||  +----------------------------------+--------------------------------+ ||
    ||  | SCENARIO                        | APPROACH                      | ||
    ||  +----------------------------------+--------------------------------+ ||
    ||  | Continue work, files unchanged  | --resume                      | ||
    ||  | Exploring alternatives          | fork_session                  | ||
    ||  | Files changed (any amount!)     | Fresh start + summary         | ||
    ||  | Cluttered history              | Fresh start + summary         | ||
    ||  | Dependency updates               | Fresh start + summary         | ||
    ||  +----------------------------------+--------------------------------+ ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  2. REAL-TIME MISTAKES:                                            ||
    ||                                                                      ||
    ||  MISTAKE #1: --resume when files changed                           ||
    ||  - Causes stale context, contradictory advice                       ||
    ||                                                                      ||
    ||  MISTAKE #2: fork_session for continuation                         ||
    ||  - Creates independent branch, loses all context                   ||
    ||                                                                      ||
    ||  MISTAKE #3: Always starting fresh                                 ||
    ||  - Loses valuable conversation history unnecessarily                ||
    ||                                                                      ||
    ||  MISTAKE #4: Not specifying changed files                         ||
    ||  - Agent doesn't know what to focus on                             ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  3. EXAM TRAPS TO AVOID:                                            ||
    ||                                                                      ||
    ||  TRAP #1: "Resume and re-read" = WRONG!                            ||
    ||  - Re-reading doesn't clear stale tool results                     ||
    ||                                                                      ||
    ||  TRAP #2: fork_session vs --resume confusion                        ||
    ||  - fork_session = branching                                         ||
    ||  - --resume = linear continuation                                  ||
    ||                                                                      ||
    ||  TRAP #3: "Only 3 files changed" -> Still WRONG for --resume       ||
    ||  - EVEN 1 file change = fresh start + summary                       ||
    ||                                                                      ||
    ||  TRAP #4: fork_session doesn't share context                        ||
    ||  - Each branch is completely independent                           ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  4. INTERVIEW FRAMEWORK:                                           ||
    ||                                                                      ||
    ||  KEY QUESTION: "Have files changed since last session?"            ||
    ||                                                                      ||
    ||  YES -> Fresh start + summary (always, no exceptions!)            ||
    ||  NO  -> Exploring? -> fork_session                                 ||
    ||  NO  -> Continuing? -> --resume                                     ||
    ||                                                                      ||
    ||  EXPECTED ANSWER STRUCTURE:                                         ||
    ||  1. State the key decision question                                ||
    ||  2. Branch based on file changes                                    |
    ||  3. For exploration vs continuation                                ||
    ||  4. Give concrete example for each                                 ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  5. MEMORY TRICK FOR DECISIONS:                                    ||
    ||                                                                      ||
    ||  Think: "FRESH" for when files change                               ||
    ||  F - Files changed? -> YES                                          ||
    ||  R - Resume? -> NO, need Fresh start                               ||
    ||  E - Every file change counts (even 1!)                           ||
    ||  S - Summary injection needed                                       ||
    ||  H - Help agent know what to focus on                              ||
    ||                                                                      ||
    +======================================================================+

    This completes the error_recovery_resilience folder practices!
    You now have all the tools to manage sessions effectively.
    """)


"""
+===========================================================================+
|                                                                           |
|  KEY CONCEPTS FROM THIS FILE:                                           |
|                                                                           |
|  DECISION MATRIX:                                                        |
|  - Files changed -> Fresh start + summary (always)                     |
|  - No changes + exploring -> fork_session                               |
|  - No changes + continuing -> --resume                                   |
|                                                                           |
|  REAL MISTAKES:                                                         |
|  - Using --resume when files changed                                    |
|  - Using fork_session for continuation                                 |
|  - Not specifying changed files                                         |
|                                                                           |
|  EXAM TRAPS:                                                            |
|  - "Resume and re-read" = WRONG!                                       |
|  - fork_session = branching, --resume = continuation                   |
|  - Even 1 file change = fresh start + summary                           |
|                                                                           |
|  INTERVIEW TIPS:                                                        |
|  - Have decision tree memorized                                         |
|  - Explain with concrete examples                                       |
|  - Know why each approach is correct                                    |
|                                                                           |
+===========================================================================+
"""
