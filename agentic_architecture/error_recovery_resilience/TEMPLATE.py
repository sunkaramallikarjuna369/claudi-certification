"""
+===========================================================================+
|                                                                           |
|  TEMPLATE: SESSION STATE RESUMPTION PATTERNS                            |
|                                                                           |
|  Starting template for session state management with                     |
|  comprehensive examples + expert guidance                               |
|                                                                           |
+===========================================================================+

This template provides a starting point for implementing session state
resumption patterns in your Claude Code CLI workflow.

INTERVIEW PREP: "Design a session management system for Claude Code"
This tests your understanding of session state, stale context, and resumption.

===========================================================================
 THREE SESSION MANAGEMENT APPROACHES
===========================================================================

    +======================================================================+
    ||                                                                      ||
    ||  APPROACH 1: --resume <session-name>                                ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  When to use:                                                        ||
    ||  + Context remains VALID (files haven't changed)                    ||
    ||  + No files have changed since last session                        ||
    ||  + Need to continue exact work from where you left off            ||
    ||                                                                      ||
    ||  Command: $ claude --resume my-session                              ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  APPROACH 2: fork_session                                           ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  When to use:                                                        ||
    ||  + Exploring DIVERGENT approaches                                   ||
    ||  + A/B testing different strategies                                  ||
    ||  + Want to try approach A AND approach B simultaneously            ||
    ||                                                                      ||
    ||  Command (inside Claude Code): /fork_session new-branch-name        ||
    ||                                                                      ||
    ||  KEY: Creates INDEPENDENT branches, not shared context!            ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  APPROACH 3: Fresh Start + Summary Injection                       ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  When to use:                                                        ||
    ||  + Files have CHANGED since last session                          ||
    ||  + Long session with cluttered history                             ||
    ||  + Dependency updates since last session                           ||
    ||  + Need to move forward without stale data                         ||
    ||                                                                      ||
    ||  Command: $ claude --session new-session                          |
    ||                                                                      ||
    ||  KEY: Transfer KNOWLEDGE (insights), not tool results (snapshots)  ||
    ||                                                                      |
    +======================================================================+

===========================================================================
 KEY RULES TO REMEMBER
===========================================================================

    RULE #1: Files changed? -> DON'T use --resume!
    RULE #2: fork_session = branching, not resuming
    RULE #3: Transfer KNOWLEDGE, not tool results
    RULE #4: Re-read does NOT clear stale tool results!
    RULE #5: EVEN 1 file change = fresh start + summary

===========================================================================
 THE STALE CONTEXT PROBLEM
===========================================================================

    When you resume a session, the ENTIRE conversation history is restored,
    including every tool result from the previous session.

    If files have changed, these tool results become "stale" - they show
    the OLD state of the file, not the CURRENT state.

    The agent now has conflicting information:
    - OLD tool result: "auth.ts uses MD5"
    - NEW file read: "auth.ts uses bcrypt"
    = CONTRADICTORY ADVICE!

    THE FIX: Fresh start + summary injection
    - Start NEW session (no stale tool results)
    - Inject structured SUMMARY of findings
    - Agent re-analyzes modified files
    - Clear, accurate, current analysis!

===========================================================================
 KNOWLEDGE vs TOOL RESULTS
===========================================================================

    TOOL RESULTS (STALE - DON'T transfer these):
    "File auth.ts: content = '...uses MD5...'"

    KNOWLEDGE (STAYS RELEVANT - Transfer these):
    "Day 1 analysis: Found MD5 security vulnerability in auth.ts"
    "Developer fixed: auth.ts now uses bcrypt"

    KEY INSIGHT:
    Tool results are SNAPSHOTS that become stale when files change.
    Knowledge is INSIGHTS that remain relevant over time.

"""

import os
import anthropic
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List


# Load environment variables from .env file
load_dotenv()

# Get API key from environment
API_KEY = os.getenv("ANTHROPIC_API_KEY")

if not API_KEY:
    raise ValueError("ANTHROPIC_API_KEY not found in .env file")


class SessionStateManager:
    """
    Manages session state and resumption for Claude Code CLI workflows.

    This class helps track:
    - Session history and findings
    - Modified files that need re-analysis
    - Knowledge summaries for injection into fresh sessions

    EXPERT TIP: Use this to track your session state and generate
    summaries for fresh sessions!
    """

    def __init__(self, session_name: str):
        """
        Initialize the session state manager.

        Args:
            session_name: Name identifier for this session
        """
        self.session_name = session_name
        self.findings: List[Dict[str, Any]] = []
        self.modified_files: List[str] = []
        self.analysis_history: List[str] = []

    def add_finding(self, file: str, issue: str, status: str = "open"):
        """
        Record a finding from analysis.

        Args:
            file: File path that has the issue
            issue: Description of the issue found
            status: "open", "fixed", "acknowledged"

        EXAMPLE:
        manager.add_finding("auth.ts", "Uses MD5 hashing (security issue)", status="open")
        """
        self.findings.append({
            "file": file,
            "issue": issue,
            "status": status,
        })

    def mark_file_modified(self, file: str, change_description: str):
        """
        Mark a file as modified since last session.

        Args:
            file: File path that was modified
            change_description: Brief description of what changed

        EXAMPLE:
        manager.mark_file_modified("auth.ts", "Upgraded MD5 to bcrypt")
        """
        self.modified_files.append(file)
        self.add_finding(file, change_description, status="modified")

    def generate_summary(self) -> str:
        """
        Generate a structured summary for injection into fresh session.

        KNOWLEDGE (not tool results!) - this is what makes it work!

        Returns:
            Formatted summary string with all findings and context
        """
        summary_parts = ["Prior analysis summary:"]

        # Add findings by status
        open_issues = [f for f in self.findings if f["status"] == "open"]
        fixed_issues = [f for f in self.findings if f["status"] in ("fixed", "modified")]

        if open_issues:
            summary_parts.append("\nOpen issues:")
            for finding in open_issues:
                summary_parts.append(f"  - {finding['file']}: {finding['issue']}")

        if fixed_issues:
            summary_parts.append("\nFixed/modified:")
            for finding in fixed_issues:
                summary_parts.append(f"  - {finding['file']}: {finding['issue']}")

        if self.modified_files:
            summary_parts.append(f"\nModified files requiring re-analysis:")
            for f in self.modified_files:
                summary_parts.append(f"  - {f}")

        return "\n".join(summary_parts)

    def generate_injection_prompt(self) -> str:
        """
        Generate a complete prompt for injecting into fresh session.

        This is the KNOWLEDGE to transfer, not tool results!
        """
        summary = self.generate_summary()

        injection_parts = [
            summary,
            "\n\nPlease re-analyze the modified files to verify the changes.",
            "\nFor unmodified files, the findings above are still valid.",
        ]

        return "\n".join(injection_parts)

    def print_session_context(self):
        """
        Print current session context for debugging.
        """
        print(f"\nSession: {self.session_name}")
        print(f"Total findings: {len(self.findings)}")
        print(f"Modified files: {len(self.modified_files)}")
        print(f"\nFindings:")
        for f in self.findings:
            print(f"  [{f['status']}] {f['file']}: {f['issue']}")


def demonstrate_session_patterns():
    """
    Demonstrates the three session management approaches.
    """

    client = anthropic.Anthropic(api_key=API_KEY)

    print("\n" + "=" * 70)
    print("SESSION STATE MANAGEMENT - DEMONSTRATION")
    print("=" * 70)

    # Create session manager
    manager = SessionStateManager("code-review-session")

    # Simulate analysis findings (KNOWLEDGE, not tool results!)
    manager.add_finding("auth.ts", "Uses MD5 hashing (security issue)", status="open")
    manager.add_finding("database.ts", "Has SQL injection vulnerability", status="open")
    manager.add_finding("api-routes.ts", "Missing rate limiting", status="open")

    # User fixes auth.ts
    manager.mark_file_modified("auth.ts", "Upgraded MD5 to bcrypt")

    print("\n[Session Context - Knowledge Being Tracked]")
    manager.print_session_context()

    print("\n[Generated Summary for Fresh Session - KNOWLEDGE, not tool results!]")
    summary = manager.generate_injection_prompt()
    print(summary)

    # Demonstrate using the summary
    print("\n[Demonstrating Summary Injection]")
    message = client.messages.create(
        model="claude-haiku-4-5-20250601",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"""
            {summary}

            Based on this knowledge:
            1. What security improvements has the developer made?
            2. What remaining issues should be addressed?
            3. What would you recommend for verification?
            """
        }]
    )

    print("\n[Agent Response to Knowledge Injection]")
    print(f"    {message.content[0].text[:300]}...")


def show_decision_flowchart():
    """
    Shows the decision flowchart for choosing session approach.
    """

    print("\n" + "=" * 70)
    print("DECISION FLOWCHART - EXPERT REFERENCE")
    print("=" * 70)

    print("""
    +======================================================================+
    ||                                                                      ||
    ||                        START                                         ||
    ||                          |                                           ||
    ||                          v                                           ||
    ||         +----------------------------------+                        ||
    ||         | Files changed since last session? |                        ||
    ||         +----------------------------------+                        ||
    ||                    /              \\                                  ||
    ||                   /                \\                                 ||
    ||                  v                  v                                ||
    ||                YES                 NO                               ||
    ||                 |                    |                               ||
    ||                 v                    v                               ||
    ||  +---------------------------+   Is this for:                       ||
    ||  | Fresh Start + Summary     |   (a) Continue work?                ||
    ||  | (Always when files        |   (b) Explore alternatives?          ||
    ||  |  changed - NO EXCEPTIONS!)|   +---------------------------+     ||
    ||  +---------------------------+              /              \\       ||
    ||                                     /              \\              ||
    ||                                    v              v               ||
    ||                                  (a)            (b)              ||
    ||                                   |              |                ||
    |                                   v              v                 ||
    ||                          +--------------+  +-------------+          ||
    ||                          | --resume     |  | fork_session|         ||
    ||                          | (Linear      |  | (Branching) |         ||
    ||                          |  continue)   |  +-------------+          ||
    ||                          +--------------+                            ||
    ||                                                                      ||
    +======================================================================+
    """)

    print("""
    +======================================================================+
    ||                                                                      ||
    ||  MEMORY TRICK - "FRESH":                                            ||
    ||                                                                      ||
    ||  F - Files changed? -> YES                                          ||
    ||  R - Resume? -> NO, need Fresh start                               ||
    ||  E - Every file change counts (even 1!)                             ||
    ||  S - Summary injection needed                                       ||
    ||  H - Help agent focus on what changed                               ||
    ||                                                                      ||
    +======================================================================+
    """)


def show_knowledge_transfer_example():
    """
    Shows concrete example of knowledge vs tool results.
    """

    print("\n" + "=" * 70)
    print("KNOWLEDGE vs TOOL RESULTS - SIDE BY SIDE")
    print("=" * 70)

    print("""
    +======================================================================+
    ||                                                                      ||
    ||  TOOL RESULT (What --resume restores - WRONG to transfer):            ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  "Tool Result from Day 1:                                           ||
    ||   File: auth.ts                                                     ||
    ||   Content: '...crypto.createHash(\"md5\").update(password)...'       ||
    ||   "                                                                  ||
    ||                                                                      ||
    ||  PROBLEM: This is a snapshot. When file changes, this is stale!     ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  KNOWLEDGE (What summary injection transfers - CORRECT):              ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  "Day 1 findings:                                                    ||
    ||   - auth.ts: Found MD5 hashing vulnerability                        ||
    ||   - Severity: High (rainbow table attack possible)                  ||
    ||   - Recommendation: Upgrade to bcrypt                               ||
    ||   - Status: FIXED (developer upgraded MD5 to bcrypt)                 ||
    ||  "                                                                  ||
    ||                                                                      ||
    ||  WHY: This is an INSIGHT, not a file snapshot. Stays relevant!       ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  KEY TAKEAWAY:                                                     ||
    ||                                                                      ||
    ||  TOOL RESULTS = What the tool SAW (becomes stale)                  ||
    ||  KNOWLEDGE = What we LEARNED (stays relevant)                       ||
    ||                                                                      ||
    ||  Always transfer KNOWLEDGE when injecting into fresh sessions!      ||
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
|  SESSION STATE RESUMPTION - TEMPLATE WITH EXPERT GUIDANCE                |
|                                                                           |
|  Use this template as a starting point for session management!            |
|                                                                           |
+===========================================================================+
    """)

    demonstrate_session_patterns()
    show_decision_flowchart()
    show_knowledge_transfer_example()

    print("\n" + "=" * 70)
    print("HOW TO USE THIS TEMPLATE")
    print("=" * 70)
    print("""
    +======================================================================+
    ||                                                                      ||
    ||  1. CREATE SessionStateManager:                                     ||
    ||  ---------------------------------------------------------------     ||
    ||  manager = SessionStateManager("code-review-session")                ||
    ||                                                                      ||
    ||  2. ADD FINDINGS as you analyze:                                    ||
    ||  ---------------------------------------------------------------     ||
    ||  manager.add_finding("auth.ts", "MD5 hashing issue", status="open") ||
    ||                                                                      ||
    ||  3. MARK FILES AS MODIFIED:                                        ||
    ||  ---------------------------------------------------------------     ||
    ||  manager.mark_file_modified("auth.ts", "Upgraded to bcrypt")         ||
    ||                                                                      ||
    ||  4. GENERATE SUMMARY for fresh sessions:                            ||
    ||  ---------------------------------------------------------------     ||
    ||  summary = manager.generate_injection_prompt()                      ||
    ||                                                                      ||
    ||  5. INJECT INTO NEW SESSION:                                        ||
    ||  ---------------------------------------------------------------     ||
    ||  $ claude --session new-session                                      ||
    ||  > [Paste summary]                                                   ||
    ||  > Re-analyze the modified files                                     ||
    ||                                                                      ||
    +======================================================================+
    """)

    print("\n" + "=" * 70)
    print("KEY RULES")
    print("=" * 70)
    print("""
    RULE #1: Files changed? -> DON'T use --resume!
    RULE #2: fork_session = branching, not resuming
    RULE #3: Transfer KNOWLEDGE, not tool results
    RULE #4: Re-read does NOT clear stale tool results!
    RULE #5: EVEN 1 file change = fresh start + summary
    """)


"""
+===========================================================================+
|                                                                           |
|  SUMMARY OF SESSION STATE RESUMPTION PATTERNS                           |
|                                                                           |
|  THREE APPROACHES:                                                        |
|  - --resume: Full history restored (only if context valid)               |
|  - fork_session: Independent branches (for exploration)                   |
|  - Fresh start + summary: New session with curated knowledge transfer    |
|                                                                           |
|  THE STALE CONTEXT PROBLEM:                                              |
|  - Resuming restores ALL tool results                                    |
|  - Files may have changed since tool results were generated               |
|  - Agent has conflicting info: stale vs fresh                            |
|  - Contradictory advice!                                                 |
|                                                                           |
|  THE CORRECT FIX:                                                        |
|  - Start FRESH session (no stale tool results)                            |
|  - Inject structured SUMMARY of prior findings (KNOWLEDGE)                |
|  - Specify WHICH files have changed                                      |
|  - Agent re-analyzes only modified files                                 |
|                                                                           |
|  EXAM TIPS:                                                              |
|  - Files changed? -> Fresh start + summary (NOT --resume!)                |
|  - fork_session = divergent exploration                                   |
|  - --resume = linear continuation (only if context valid)                 |
|  - "Resume and re-read" = WRONG answer!                                  |
|  - Transfer KNOWLEDGE, not tool results                                   |
|                                                                           |
|  INTERVIEW TIPS:                                                         |
|  - Have decision tree memorized                                          |
|  - Explain KNOWLEDGE vs TOOL RESULTS with examples                       |
|  - Show you understand WHY each approach is correct                      |
|  - Know common mistakes and how to avoid them                            |
|                                                                           |
+===========================================================================+
"""
