"""
+===========================================================================+
|                                                                           |
|  PRACTICE 4: FORK_SESSION vs --resume                                      |
|                                                                           |
|  Two different session management concepts - DON'T confuse them!         |
|  + REAL-TIME SCENARIOS + MISTAKES + INTERVIEW GUIDE                      |
|                                                                           |
+===========================================================================+

INTERVIEW PREP: "What's the difference between fork_session and --resume?"
This question tests your understanding of session branching vs continuation.

REAL-TIME SCENARIO: You've been working on a complex microservices
refactoring for 3 hours. Now you need to explore a completely different
approach. If you use --resume, you continue in the same session. If you
use fork_session, you create a NEW BRANCH. Using the wrong one wastes
hours of work or loses context.

===========================================================================
 FORK_SESSION vs --resume: TWO DISTINCT CONCEPTS
===========================================================================

    +-----------------------------------------------------------------------+
    |  FORK_SESSION = Creates INDEPENDENT branches (divergent exploration)    |
    |  --resume = Continues EXISTING session (linear continuation)          |
    |                                                                       |
    |  Don't confuse them on exams! They serve different purposes!         |
    +-----------------------------------------------------------------------+

    +=======================================================================+
    ||  VISUAL: FORK_SESSION creates branches                               ||
    ||                                                                      ||
    ||           MAIN BRANCH (main-session)                                  ||
    ||                  |                                                  ||
    ||         +---------+---------+                                        ||
    ||         |                   |                                       ||
    ||         v                   v                                        ||
    ||  +------------+      +------------+                                 ||
    ||  | Branch A   |      | Branch B   |                                 ||
    ||  | Explore    |      | Explore    |                                 ||
    ||  | approach X |      | approach Y |                                 ||
    ||  +------------+      +------------+                                 ||
    ||         |                   |                                        ||
    ||         v                   v                                        ||
    ||  Independent         Independent                                    ||
    ||  changes             changes                                         ||
    ||                                                                      ||
    ||  Changes in Branch A DO NOT affect Branch B!                          ||
    ||                                                                      ||
    +=======================================================================+

    +=======================================================================+
    ||  VISUAL: --resume continues a session                               ||
    ||                                                                      ||
    ||  SESSION: my-session                                                  ||
    ||  +---------------------------+                                       ||
    ||  | Message 1                 | <- History from before               ||
    ||  | Tool Result 1             |                                       ||
    ||  | Message 2                 |                                       ||
    ||  | Tool Result 2             |                                       ||
    ||  +---------------------------+                                       ||
    ||           |                                                          ||
    ||           v                                                          ||
    ||  --resume my-session                                                 ||
    ||           |                                                          ||
    │           v                                                          ||
    ||  +---------------------------+                                       ||
    ||  | [ALL OF THE ABOVE]        | <- Exact copy restored               ||
    ||  | Message 3 (new)           | <- Continue from here                ||
    ||  +---------------------------+                                       ||
    ||           |                                                          ||
    │           v                                                          ||
    ||  Agent has FULL history! Can continue work seamlessly!             ||
    ||                                                                      ||
    +=======================================================================+

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


# ============================================================================
# REAL-TIME SCENARIOS: When Fork vs Resume Confusion Causes Problems
# ============================================================================

def show_real_time_scenarios():
    """
    Production scenarios where fork_session vs --resume confusion causes issues.
    """

    print("\n" + "=" * 70)
    print("REAL-TIME SCENARIOS: When Fork vs Resume Confusion Fails")
    print("=" * 70)

    print("""
    +======================================================================+
    ||  SCENARIO #1: The "Lost 3 Hours" Disaster                          ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  CONTEXT: Complex database migration project                          ||
    ||                                                                      ||
    ||  WHAT HAPPENED:                                                      ||
    ||  1. Dev spent 3 hours analyzing migration approach                   ||
    ||  2. Manager asked: "Also check an alternative approach"             ||
    ||  3. Dev used --resume to create new branch (WRONG!)                   ||
    ||  4. 3 hours of work wiped out - continuation instead of branch       ||
    ||  5. Had to start analysis over                                      ||
    ||                                                                      ||
    ||  ROOT CAUSE:                                                        ||
    ||  - Dev wanted to explore alternative while keeping original           ||
    ||  - --resume CONTINUES current session (same context)                │
    ||  - Should have used fork_session to create independent branch      ||
    ||                                                                      ||
    ||  REAL CONSEQUENCE:                                                   ||
    ||  - 3 hours of work lost (had to reproduce analysis)                   ||
    ||  - Deadline missed                                                   ||
    ||  - Team frustrated with "unreliable" tool                           ||
    ||                                                                      ||
    ||  LESSON: Want to explore? Use fork_session! Want to continue? Use --resume ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  SCENARIO #2: The "Where Did My Context Go?" Problem                ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  CONTEXT: Long research session on AI trends                          ||
    ||                                                                      ||
    ||  WHAT HAPPENED:                                                      ||
    ||  1. Research session "ai-trends" has 40+ messages of findings      ||
    ||  2. Need to explore "AI in healthcare" as separate topic            ||
    ||  3. Used fork_session to create "ai-healthcare"                      ||
    ||  4. New branch has NO context from "ai-trends" session!             ||
    ||  5. Dev confused: "I forked it, why don't I have the context?"      ||
    ||                                                                      ||
    ||  ROOT CAUSE:                                                        ||
    ||  - fork_session creates INDEPENDENT branches                         ||
    ||  - Each branch has its OWN context (starts fresh)                   ||
    ||  - fork_session = divergence, NOT context sharing!                  ||
    ||                                                                      ||
    ||  REAL CONSEQUENCE:                                                   ||
    ||  - Had to re-explain entire research context                         ||
    ||  - fork_session used incorrectly as "continuation"                  ||
    ||                                                                      ||
    ||  LESSON: fork_session branches are INDEPENDENT - no shared context! ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  SCENARIO #3: The "Stale Context" Production Bug                     ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  CONTEXT: Multi-agent code review system                              ||
    ||                                                                      ||
    ||  WHAT HAPPENED:                                                      ||
    ||  1. Agent analyzed codebase for security issues                      ||
    ||  2. Team fixed critical issues overnight                             ||
    ||  3. Dev resumed session next day with --resume                       ||
    ||  4. Agent had stale tool results from before fixes                   ||
    ||  5. Agent gave advice based on OLD vulnerable code                   ||
    ||                                                                      ||
    ||  ROOT CAUSE:                                                        ||
    ||  - --resume restores ALL conversation history                         ||
    ||  - But tool results from before file changes are stale!            ||
    ||  - Should have used fresh start + summary injection                  ||
    ||                                                                      ||
    ||  REAL CONSEQUENCE:                                                   ||
    ||  - Agent recommended fixes for already-fixed vulnerabilities        ||
    ||  - Team confused: "We already fixed that!"                          ||
    ||  - Trust in AI system damaged                                        ||
    ||                                                                      ||
    ||  LESSON: --resume only if context still VALID!                        ||
    ||                                                                      ||
    +======================================================================+
    """)


# ============================================================================
# MISTAKES DEVELOPERS MAKE
# ============================================================================

def show_mistakes_developers_make():
    """
    Common mistakes with explanations.
    """

    print("\n" + "=" * 70)
    print("MISTAKES DEVELOPERS MAKE - Expert Warnings")
    print("=" * 70)

    print("""
    +======================================================================+
    ||  MISTAKE #1: Using fork_session when you want to continue           ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WHY IT'S WRONG:                                                     ||
    ||  fork_session creates a NEW INDEPENDENT branch.                      ||
    ||  Your current context is NOT copied to the new branch.              ||
    ||                                                                      ||
    ||  BAD:                                                               ||
    ||  Working on task for hours...                                        │
    ||  Want to take a break and resume later                               ||
    ||  Use fork_session (WRONG!)                                           ||
    ||  New branch has NO context!                                          ||
    ||                                                                      ||
    ||  CORRECT:                                                            ||
    ||  Working on task for hours...                                        ||
    ||  Need to continue later with same context                            ||
    ||  Use --resume (continues same session with all history)             ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  MISTAKE #2: Using --resume when you want to explore alternatives  ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WHY IT'S WRONG:                                                     ||
    ||  --resume CONTINUES your current session.                           ||
    ||  All changes go to the same context. You can't "go back."           ||
    ||                                                                      ||
    ||  BAD:                                                               ||
    ||  Have approach A working in current session...                       ||
    ||  Want to try approach B without losing A                            ||
    ||  Use --resume (WRONG!)                                               ||
    ||  Both approaches in same session, can't compare cleanly            ||
    ||                                                                      ||
    ||  CORRECT:                                                            ||
    ||  Have approach A working...                                          │
    ||  Want to try approach B while keeping A                             ||
    ||  Use fork_session to create branch for B                            ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  MISTAKE #3: Assuming fork_session shares context                  ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WHY IT'S WRONG:                                                     ||
    ||  fork_session creates INDEPENDENT branches.                         ||
    ||  Each branch has its OWN context window.                             ||
    ||  Changes in one branch do NOT affect the other.                     ||
    ||                                                                      ||
    ||  BAD ASSUMPTION:                                                    ||
    ||  Branch B (forked from A) --> Can see all of A's context             ||
    ||  WRONG! Branch B starts FRESH with no history.                      ||
    ||                                                                      ||
    ||  CORRECT UNDERSTANDING:                                              ||
    ||  Branch A: Context A                                                ||
    ||  Branch B: Context B (completely separate)                          ||
    ||  They are INDEPENDENT.                                              ||
    ||                                                                      │
    +======================================================================+

    +======================================================================+
    ||  MISTAKE #4: Using --resume after file changes                       ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WHY IT'S WRONG:                                                     ||
    ||  --resume restores ALL tool results, including stale ones!           ||
    ||  If files changed, you have conflicting old + new context.         ||
    ||                                                                      ||
    ||  BAD:                                                               ||
    ||  Analyzed code yesterday, files changed overnight                   ||
    ||  --resume session (WRONG!)                                           ||
    ||  Agent has stale tool results!                                      ||
    ||                                                                      ||
    ||  CORRECT:                                                            ||
    ||  Analyzed code, files changed overnight                              ||
    ||  Start new session + inject summary of prior findings               ||
    ||  OR: Start new session + ask to re-analyze changed files           ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  MISTAKE #5: Thinking fork_session = backup                         ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WHY IT'S WRONG:                                                     ||
    ||  fork_session doesn't "save" your work - it creates a new branch.  ||
    ||  The new branch starts fresh. You still have your original.          ||
    ||                                                                      ||
    ||  BETTER:                                                             ||
    ||  For backup: Use natural session persistence                        ||
    ||  For exploration: Use fork_session (creates branching context)      ||
    ||                                                                      ||
    +======================================================================+
    """)


# ============================================================================
# INTERVIEW Q&A
# ============================================================================

def show_interview_qa():
    """
    Interview questions and expert answer frameworks.
    """

    print("\n" + "=" * 70)
    print("INTERVIEW QUESTIONS & EXPERT ANSWERS GUIDE")
    print("=" * 70)

    print("""
    ========================================================================
    INTERVIEW Q1: "What's the difference between fork_session and --resume?"
    ========================================================================

    EXPECTED ANSWER:
    fork_session creates INDEPENDENT branches from current state - each branch
    operates separately with no shared context. Use for exploring alternatives.
    --resume CONTINUES an existing session from where it left off - all
    previous context is restored. Use for picking up interrupted work.

    KEY DIFFERENTIATOR:
    fork_session = divergent (branches out)
    --resume = linear (continues straight)

    RED FLAGS IN ANSWERS:
    - "They're basically the same" -> Wrong! Very different!
    - "fork_session continues work" -> Wrong! Creates new branch!
    - "I use them interchangeably" -> Shows confusion

    +-----------------------------------------------------------------------+
    | EXPERT TIP: Say "branching vs linear continuation" - shows you       |
    | understand the fundamental difference!                               |
    +-----------------------------------------------------------------------+
    """)

    # Demo with actual API call
    message = client.messages.create(
        model="claude-haiku-4-5-20250601",
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": "As an expert in Claude Code session management, explain in 2 sentences "
                      "the key difference between fork_session and --resume commands. "
                      "Focus on the branching vs linear distinction."
        }]
    )

    print("\nExample Expert Answer:")
    print(f"    {message.content[0].text[:400]}...")

    print("""
    ========================================================================
    INTERVIEW Q2: "When would you use fork_session?"
    ========================================================================

    EXPECTED ANSWER:
    Use fork_session when you want to explore DIVERGENT approaches:
    - Try multiple solutions to the same problem
    - A/B test different strategies
    - "What if we used microservices vs monolith?"
    - Compare two refactoring approaches before committing
    - When you want to branch WITHOUT losing the original path

    DON'T USE for:
    - Continuing interrupted work (use --resume)
    - Picking up where you left off (use --resume)
    - When context from before matters (use --resume or fresh start)

    +-----------------------------------------------------------------------+
    | EXPERT TIP: Give concrete examples - "Explore microservices AND        |
    | monolith in parallel branches before deciding"                       |
    +-----------------------------------------------------------------------+
    """)

    print("""
    ========================================================================
    INTERVIEW Q3: "When would you use --resume?"
    ========================================================================

    EXPECTED ANSWER:
    Use --resume when you want to CONTINUE a session with full context:
    - Picking up after an interruption (meeting, crash, end of day)
    - Continuing the same work without branching
    - When all prior context is still relevant
    - After taking a break in the middle of a task

    DON'T USE if:
    - Files have changed (use fresh start + summary)
    - You want to try alternatives (use fork_session)
    - Context is cluttered from long session (use fresh start)

    WARNING: Only use --resume if context is still VALID!

    +-----------------------------------------------------------------------+
    | EXPERT TIP: Mention the caveat: "only if context still valid"         |
    +-----------------------------------------------------------------------+
    """)

    print("""
    ========================================================================
    INTERVIEW Q4: "A developer says fork_session shares context. Correct?"
    ========================================================================

    EXPECTED ANSWER:
    NO! fork_session creates INDEPENDENT branches. Each branch has its own
    separate context. Changes in one branch do NOT affect the other. This is
    the key misunderstanding that causes bugs.

    VISUAL:
    Main Branch (context A) ---fork_session---> New Branch (context B)
                                           ---starts FRESH---
                                           ---NO shared context---

    If you want to continue work with context, use --resume, not fork_session.

    +-----------------------------------------------------------------------+
    | EXPERT TIP: Be very clear: "independent branches, no shared context"   |
    +-----------------------------------------------------------------------+
    """)


# ============================================================================
# DEMONSTRATION FUNCTIONS
# ============================================================================

def demonstrate_fork_session():
    """
    Demonstrate fork_session - creates independent branches.
    """
    print("\n" + "=" * 70)
    print("FORK_SESSION - Creating Independent Branches")
    print("=" * 70)

    print("""
    +=======================================================================+
    ||  MAIN SESSION: "research-ai-trends"                                  ||
    ||                                                                      ||
    ||  - Current state: Analyzed AI trends in healthcare                   ||
    ||  - User asks: "What about finance sector?"                          ||
    ||                                                                      ||
    ||  FORK SESSION -> Creates "research-ai-trends-finance"                ||
    ||                                                                      ||
    ||  Now you have TWO independent sessions:                             ||
    ||                                                                      ||
    ||  +----------------------------+    +-----------------------------+  ||
    ||  | research-ai-trends        |    | research-ai-trends-        |  ||
    ||  | (original)                |    | finance (forked)           |  ||
    ||  |                          |    |                             |  ||
    ||  | Healthcare focus         |    | Finance focus              |  ||
    ||  | 50 messages              |    | Starts fresh!              |  ||
    ||  | Keep exploring           |    | Explore parallel           |  ||
    ||  +----------------------------+    +-----------------------------+  ||
    ||                                                                      ||
    ||  Changes in one branch DO NOT affect the other!                      ||
    ||                                                                      ||
    +=======================================================================+
    """)

    print("\nWhen to use fork_session:")
    print("    - Explore multiple directions simultaneously")
    print("    - Test different approaches without committing")
    print("    - A/B testing of agent strategies")
    print("    - When you want to 'go back in time' and try another path")


def demonstrate_resume():
    """
    Demonstrate --resume - continues a specific session.
    """
    print("\n" + "=" * 70)
    print("--resume - Continuing a Session")
    print("=" * 70)

    print("""
    +=======================================================================+
    ||  SCENARIO: You were working on "project-alpha" session               ||
    ||                                                                      ||
    ||  You asked: "Research microservices architecture"                     ||
    ||  Agent provided extensive findings...                               ||
    ||                                                                      ||
    ||  [Session interrupted - had to leave, computer crashed, etc.]        ||
    ||                                                                      ||
    ||  Now you come back and want to continue that work.                   ||
    ||                                                                      ||
    ||  --resume project-alpha                                              ||
    ||                                                                      ||
    ||  +---------------------------------------------------------------+  ||
    ||  |  project-alpha (RESUMED)                                       |  ||
    ||  |                                                                |  ||
    ||  |  All previous context is preserved!                           |  ||
    ||  |  - Microservices research findings                             |  │
    ||  |  - All conversation history                                    |  │
    ||  |  - Ready to continue or expand on the work                     |  │
    ||  |                                                                |  │
    ||  |  You can ask: "Now compare to monolith architecture"           |  │
    ||  |  And the agent will know about the microservices research!    |  │
    ||  +---------------------------------------------------------------+  ||
    ||                                                                      ||
    +=======================================================================+
    """)

    print("\nWhen to use --resume:")
    print("    - Pick up where you left off")
    print("    - Continue a long-running investigation")
    print("    - When context from earlier matters")
    print("    - After interruptions (crashes, meetings, etc.)")


def compare_fork_vs_resume():
    """
    Side-by-side comparison of fork_session vs --resume.
    """
    print("\n" + "=" * 70)
    print("COMPARISON: fork_session vs --resume")
    print("=" * 70)

    print("""
    +=======================================================================+
    ||                    |                    |                          ||
    ||     FORK_SESSION   |      --resume       |                          ||
    +=====================+=====================+==========================+
    ||                    |                    |                          ||
    ||  Creates a NEW     |  CONTINUES an      |                          ||
    ||  independent       |  existing session  |                          ||
    ||  branch            |  from where it     |                          ||
    ||                    |  left off           |                          ||
    ||  ----------------  |  ----------------  |                          ||
    ||                    |                    |                          ||
    ||  "Let's try this   |  "Continue where   |                          ||
    ||   approach AND     |   I left off"       |                          ||
    ||   this one"        |                    |                          ||
    ||                    |                    |                          ||
    ||  Branch A ---+---Branch B              |                          ||
    ||             /                                                  ||
    ||            /    Branch C               |                          ||
    ||           /                                                   ||
    ||                    |                    |                          ||
    ||  Each branch is    |  Same session,      |                          ||
    ||  INDEPENDENT       |  continued          |                          ||
    ||                    |                    |                          ||
    ||  ----------------  |  ----------------  |                          ||
    ||                    |                    |                          ||
    ||  Use when:         |  Use when:          |                          ||
    ||  - Exploring       |  - Continuing work  |                          ||
    ||    alternatives    |  - Context matters   |                          ||
    ||  - Parallel        |  - Picking up after   |                          ||
    ||    research        |    interruption       |                          ||
    ||  - Want to branch  |                       |                          ||
    ||    without losing  |                       |                          ||
    ||    original        |                       |                          ||
    +=======================================================================+
    """)

    print("\nEXAM TIP: Don't confuse these two!")
    print("    fork_session = creates branches (divergent)")
    print("    --resume = continues session (linear)")


def show_practical_example():
    """
    Show a practical workflow using both concepts.
    """
    print("\n" + "=" * 70)
    print("PRACTICAL WORKFLOW EXAMPLE")
    print("=" * 70)

    print("""
    Scenario: Researching AI adoption in different industries

    Step 1: Start main research session
        > claude --session research-industry-ai
        > "Research AI adoption in healthcare"

    Step 2: Get some findings, want to explore finance in parallel
        > /fork research-industry-ai --name research-industry-ai-finance
        > "Research AI adoption in finance"

        Now running TWO research branches in parallel!

    Step 3: Must leave unexpectedly (main session)
        (Session preserved automatically)

    Step 4: Come back later, resume the work
        > claude --session research-industry-ai --resume
        > "Continue with healthcare findings, now add manufacturing sector"

    Step 5: Later, merge insights from all branches
        > /fork research-industry-ai --name synthesis
        > "You have research from healthcare, finance, and manufacturing.
             Write a comprehensive report comparing AI adoption across
             these three industries."
    """)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    print("\n" + "=" * 70)
    print("PRACTICE 4: FORK_SESSION vs --resume")
    print("=" * 70)
    print("""
This program teaches two important session management concepts:
    fork_session: Creates independent branches
    --resume: Continues an existing session

These are NOT the same thing! Know the difference.
    """)

    # Show all enhanced sections
    show_real_time_scenarios()
    show_mistakes_developers_make()
    show_interview_qa()
    demonstrate_fork_session()
    demonstrate_resume()
    compare_fork_vs_resume()
    show_practical_example()

    print("\n" + "=" * 70)
    print("WHAT WE HAVE LEARNT")
    print("=" * 70)
    print("""
    +======================================================================+
    ||  1. FORK_SESSION vs --resume - TWO DISTINCT CONCEPTS:               ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  FORK_SESSION:                                                      ||
    ||  - Creates INDEPENDENT branches from current state                   ||
    ||  - Each branch operates SEPARATELY                                  ||
    ||  - Changes in one branch do NOT affect others                       ||
    ||  - Use for: Exploring alternatives, A/B testing, parallel paths   ||
    ||                                                                      ||
    ||  --resume:                                                          ||
    ||  - Continues EXISTING session from where it left off                ||
    ||  - ALL previous context is restored                                 ||
    ||  - Use for: Picking up after interruption, continuing work        ||
    ||                                                                      ||
    ||  KEY DIFFERENTIATOR:                                                 ||
    ||  fork_session = divergent (branches out)                            ||
    ||  --resume = linear (continues straight)                            ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  2. REAL-TIME SCENARIOS WHERE CONFUSION FAILS:                       ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  - "Lost 3 hours": Used --resume when wanted branch (lost work)     ||
    ||  - "Where did context go": fork_session doesn't share context!     ||
    ||  - "Stale context bug": --resume after file changes (bad advice)    ||
    ||                                                                      ||
    ||  KEY INSIGHT: Wrong choice = lost work OR stale context!            ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  3. COMMON MISTAKES:                                                 ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  MISTAKE #1: fork_session when want to continue                       ||
    ||              -> New branch has NO context from before!               ||
    ||                                                                      ||
    ||  MISTAKE #2: --resume when want to explore alternatives              ||
    ||              -> Both in same session, can't compare cleanly          ||
    ||                                                                      ||
    ||  MISTAKE #3: Assuming fork_session shares context                    ||
    ||              -> Independent branches, NO shared context!            ||
    ||                                                                      ||
    ||  MISTAKE #4: --resume after file changes                             ||
    ||              -> Stale tool results cause contradictory advice      ||
    ||                                                                      ||
    ||  MISTAKE #5: Thinking fork_session = backup                          ||
    ||              -> Creates new branch, doesn't "save" existing work    ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  4. INTERVIEW TIPS:                                                  ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  - Say "branching vs linear continuation"                           ||
    ||  - fork_session = independent branches, no shared context          ||
    ||  - --resume = continues same session with all history               ||
    ||  - --resume caveat: "only if context still valid"                    ||
    ||                                                                      ||
    ||  EXPECTED ANSWER STRUCTURE:                                          ||
    ||  1. State: fork_session for alternatives, --resume for continuation ||
    ||  2. Explain: Independent branches vs shared context                 ||
    ||  3. Give concrete examples                                           ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  5. KEY RULES TO MEMORIZE:                                           ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  RULE #1: fork_session = branching, NOT continuation                ||
    ||  RULE #2: --resume = linear continuation, NOT branching             ||
    ||  RULE #3: fork_session branches are INDEPENDENT (no shared context) ||
    ||  RULE #4: --resume only if context is STILL VALID                   ||
    ||  RULE #5: Use fork_session to explore, --resume to continue         ||
    ||                                                                      ||
    +======================================================================+

    Next: practice_05_common_guardrail_failures.py shows common pitfalls
    in multi-agent context passing!
    """)

    print("\n" + "=" * 70)
    print("PROGRAM COMPLETE!")
    print("=" * 70)


"""
+===========================================================================+
|                                                                           |
|  KEY CONCEPTS FROM THIS FILE:                                             |
|                                                                           |
|  fork_session = creates INDEPENDENT branches (divergent exploration)      |
|  --resume = continues EXISTING session (linear continuation)             |
|                                                                           |
|  REAL-TIME SCENARIOS:                                                     |
|  - "Lost 3 hours" using wrong command                                     |
|  - fork_session doesn't share context (independent branches)              |
|  - --resume with stale context after file changes                         |
|                                                                           |
|  MISTAKES TO AVOID:                                                       |
|  - fork_session when want to continue                                     |
|  - --resume when want to explore alternatives                             |
|  - Assuming shared context in forked branches                              |
|  - --resume after file changes                                            |
|                                                                           |
|  INTERVIEW PREP:                                                          |
|  - "Difference?" -> branching vs linear continuation                     |
|  - "When fork?" -> exploring alternatives                                 |
|  - "When resume?" -> picking up interrupted work (context valid)         |
|                                                                           |
+===========================================================================+
"""