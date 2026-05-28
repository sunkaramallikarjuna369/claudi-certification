"""
================================================================================
SESSION STATE & RESUMPTION - TEMPLATE
================================================================================

Your starting point for implementing session state management strategies.

Choose the right approach based on your scenario:
    --resume: When context is still valid
    fork_session: When exploring divergent approaches
    Fresh start + summary: When files have changed or context is stale
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


# ================================================================================
# SESSION STATE MANAGER
# ================================================================================

class SessionStateManager:
    """
    Manages session state and determines the best resumption approach.
    """

    def __init__(self):
        self.session_history = []
        self.prior_findings = {}
        self.modified_files = set()

    def record_findings(self, findings: dict):
        """Record findings from a session."""
        self.prior_findings.update(findings)

    def add_modified_file(self, filepath: str):
        """Mark a file as modified since last session."""
        self.modified_files.add(filepath)

    def create_summary(self) -> str:
        """
        Create a structured summary for injection into fresh sessions.
        """
        # Build the summary
        summary_parts = []

        if self.prior_findings:
            summary_parts.append("PRIOR ANALYSIS FINDINGS:")
            summary_parts.append("─" * 50)
            for filepath, finding in self.prior_findings.items():
                summary_parts.append(f"\n{filepath}:")
                summary_parts.append(f"  - {finding}")

        if self.modified_files:
            summary_parts.append("\n\nFILES MODIFIED SINCE LAST SESSION:")
            summary_parts.append("─" * 50)
            for filepath in sorted(self.modified_files):
                summary_parts.append(f"  - {filepath}")
            summary_parts.append("\nThese files need re-analysis.")

        if self.prior_findings and not self.modified_files:
            summary_parts.append("\n\nAll prior files are UNCHANGED.")
            summary_parts.append("Prior findings remain valid.")

        return "\n".join(summary_parts)

    def determine_approach(self) -> str:
        """
        Determine the best session management approach.

        Returns:
            "resume": Use --resume (context still valid)
            "fork": Use fork_session (exploring alternatives)
            "fresh": Use fresh start + summary (files changed or stale context)
        """
        if self.modified_files:
            return "fresh"  # Files changed - need fresh start

        if self.session_history and len(self.session_history) > 50:
            return "fresh"  # Cluttered history - start fresh

        return "resume"  # Context still valid


# ================================================================================
# SESSION TYPES
# ================================================================================

def create_resume_session(session_name: str, context: dict) -> list:
    """
    Create messages for --resume approach.

    Use when: Prior context is still valid, no files changed.
    """
    print(f"\n   [APPROACH] --resume {session_name}")
    print("   [REASON] Prior context is still valid")

    # For resume, just continue with the existing conversation
    # The CLI handles restoring history
    messages = []

    if context.get("continuation_message"):
        messages.append({
            "role": "user",
            "content": context["continuation_message"]
        })

    return messages


def create_fork_session(base_session: str, branch_name: str, purpose: str) -> dict:
    """
    Create parameters for fork_session approach.

    Use when: Exploring divergent approaches.
    """
    print(f"\n   [APPROACH] fork_session")
    print(f"   [REASON] Exploring: {purpose}")
    print(f"   [BASE] {base_session} → {branch_name}")

    return {
        "type": "fork",
        "base_session": base_session,
        "new_branch": branch_name,
        "purpose": purpose
    }


def create_fresh_session_with_summary(state_manager: SessionStateManager, new_work: str) -> list:
    """
    Create messages for fresh start + summary approach.

    Use when: Files have changed, history is cluttered, or dependency updates.
    """
    print(f"\n   [APPROACH] Fresh session + summary injection")
    print(f"   [REASON] Files modified or stale context")

    messages = []

    # Create and inject the summary
    summary = state_manager.create_summary()

    if summary.strip():
        summary_message = f"""CONTEXT FROM PRIOR SESSION
{'='*50}
{summary}

{'='*50}
Please re-analyze the modified files if any, and continue with the new work below.
"""
        messages.append({
            "role": "user",
            "content": summary_message
        })

    # Add the new work
    if new_work:
        messages.append({
            "role": "user",
            "content": new_work
        })

    return messages


# ================================================================================
# DECISION HELPERS
# ================================================================================

def select_session_approach(
    modified_files: list = None,
    purpose: str = None,
    context_valid: bool = True,
    history_length: int = 0
) -> str:
    """
    Select the best session approach based on criteria.

    Args:
        modified_files: List of files that have changed
        purpose: Purpose for fork_session (e.g., "compare approaches")
        context_valid: Whether prior context is still valid
        history_length: Number of messages in session history

    Returns:
        "resume", "fork", or "fresh"
    """
    # Check if exploring alternatives
    if purpose and ("compare" in purpose.lower() or
                   "alternative" in purpose.lower() or
                   "explore" in purpose.lower()):
        return "fork"

    # Check if files modified
    if modified_files and len(modified_files) > 0:
        return "fresh"

    # Check if history is cluttered
    if history_length > 50:
        return "fresh"

    # Check if context is still valid
    if not context_valid:
        return "fresh"

    # Default to resume
    return "resume"


# ================================================================================
# DEMO: Show all approaches
# ================================================================================

def demo_all_approaches():
    """Demonstrate all three session management approaches."""

    print("\n" + "=" * 70)
    print("SESSION MANAGEMENT APPROACHES DEMO")
    print("=" * 70)

    # Demo 1: --resume
    print("\n[1] --resume approach")
    print("-" * 50)
    context = {
        "continuation_message": "Continue analyzing the database schema"
    }
    messages = create_resume_session("analysis-session", context)
    print(f"   Messages created: {len(messages)}")
    if messages:
        print(f"   First message: {messages[0]['content'][:50]}...")

    # Demo 2: fork_session
    print("\n[2] fork_session approach")
    print("-" * 50)
    fork_params = create_fork_session(
        base_session="refactor-base",
        branch_name="microservices",
        purpose="Compare microservices vs monolith"
    )
    print(f"   Fork created: {fork_params['base_session']} → {fork_params['new_branch']}")

    # Demo 3: Fresh start + summary
    print("\n[3] Fresh start + summary approach")
    print("-" * 50)
    state = SessionStateManager()
    state.record_findings({
        "auth.ts": "Uses MD5 hashing - should upgrade to bcrypt",
        "database.ts": "SQL injection vulnerability in query builder",
        "api-routes.ts": "Missing rate limiting"
    })
    state.add_modified_file("auth.ts")
    state.add_modified_file("api-routes.ts")

    messages = create_fresh_session_with_summary(
        state,
        "Now let's fix the SQL injection vulnerability"
    )
    print(f"   Messages created: {len(messages)}")
    for i, msg in enumerate(messages):
        print(f"   Message {i+1} (first 50 chars): {msg['content'][:50]}...")


# ================================================================================
# MAIN
# ================================================================================

if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    print("\n" + "=" * 70)
    print("SESSION STATE & RESUMPTION - TEMPLATE")
    print("=" * 70)
    print("""
This template provides session management patterns:

1. --resume: For continuing work when context is still valid
2. fork_session: For exploring divergent approaches
3. Fresh start + summary: For when files have changed or context is stale

Choose based on your scenario!
""")

    demo_all_approaches()

    print("""
================================================================================
WHAT JUST HAPPENED?
================================================================================

    1. We implemented a SessionStateManager:
       - Records findings from prior sessions
       - Tracks modified files
       - Creates structured summaries for injection

    2. We created three session approaches:
       - --resume: Continue with existing conversation
       - fork_session: Create independent branches
       - Fresh start + summary: New session with injected knowledge

    3. We implemented decision helpers:
       - select_session_approach() based on criteria
       - Modified files → fresh
       - Exploring alternatives → fork
       - Context valid → resume

    COPY THIS TEMPLATE and customize for your use case!

    REMEMBER:
    - Files changed? → Fresh start + summary
    - Exploring alternatives? → fork_session
    - Context valid? → --resume

    TRANSFER KNOWLEDGE, not stale tool results!
================================================================================
""")
    print("\n" + "=" * 70)
    print("TEMPLATE COMPLETE!")
    print("=" * 70)