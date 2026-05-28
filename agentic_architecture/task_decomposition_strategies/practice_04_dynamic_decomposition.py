"""
+===========================================================================+
|                                                                           |
|  PRACTICE 4: DYNAMIC ADAPTIVE DECOMPOSITION                             |
|                                                                           |
|  When task scope is unknown or discoveries may change direction,        |
|  use dynamic adaptive decomposition.                                    |
|                                                                           |
|  Best for: open-ended investigation, legacy system exploration,         |
|  security audits.                                                       |
|                                                                           |
|  + REAL-TIME SCENARIOS + MISTAKES + INTERVIEW Q&A + VISUALS             |
|                                                                           |
+===========================================================================+

This file shows how to implement and use dynamic decomposition.

REAL-TIME SCENARIO: You're handed a legacy system with no documentation.
Task: "Find all security vulnerabilities." How do you structure this?

INTERVIEW PREP: "How does dynamic decomposition handle discoveries
that change the investigation scope?" Tests understanding of adaptive systems.

===========================================================================
 VISUAL: DYNAMIC DECOMPOSITION FLOW
===========================================================================

    +-----------------------------------------------------------------------+
    |  DYNAMIC ADAPTIVE DECOMPOSITION                                       |
    |                                                                       |
    |                      START TASK                                       |
    |                         |                                             |
    |                         v                                             |
    |                 +----------------+                                    |
    |                 | Analyze Task  |                                    |
    |                 | Generate Init |                                    |
    |                 | Subtasks      |                                    |
    |                 +-------+--------+                                    |
    |                         |                                             |
    |                         v                                             |
    |                 [Process Subtask A]                                   |
    |                         |                                             |
    |                    FINDING!                                           |
    |                         |                                             |
    |                         v                                             |
    |                 +----------------+                                    |
    |                 | New Subtask X  | <--- DISCOVERED!                   |
    |                 | New Subtask Y  | <--- DISCOVERED!                   |
    |                 +-------+--------+                                    |
    |                         |                                             |
    |                         v                                             |
    |                 [Process Subtask X]                                   |
    |                 [Process Subtask Y]                                   |
    |                         |                                             |
    |                    MORE FINDINGS                                      |
    |                         |                                             |
    |                         v                                             |
    |                 [Continue until no pending]                           |
    |                         |                                             |
    |                         v                                             |
    |                 +----------------+                                    |
    |                 | Compile Final  |                                    |
    |                 | Results        |                                    |
    |                 +----------------+                                    |
    |                                                                       |
    |  KEY: Subtasks GENERATED based on discoveries!                       |
    |  Plan EVOLVES as agent learns more about problem                     |
    |                                                                       |
    +-----------------------------------------------------------------------+

===========================================================================
 REAL-TIME SCENARIO 1: The Legacy Security Audit
===========================================================================

    CONTEXT:
    - Developer inherits legacy system, no documentation
    - Task: "Find all security vulnerabilities"
    - Uses FIXED pipeline approach (WRONG!)

    WHAT HAPPENS WITH FIXED:
    - Creates 4 predetermined steps:
      Step 1: Check authentication files
      Step 2: Check database access patterns
      Step 3: Check API endpoints
      Step 4: Generate report

    THE DISCOVERY LOOP:
    - Discovers auth system uses MD5 hashing (Step 1)
    - But this leads to needing to check password reset flow
    - Password reset leads to email verification
    - Email verification leads to... (pipeline has no step for this!)

    THE BROKEN THING:
    - FIXED pipeline CANNOT add new steps when discoveries emerge
    - Agent must either:
      a) Ignore the new findings (miss critical issues)
      b) Branch outside the pipeline (breaks the flow)
    - Security audit is incomplete

    WHY DYNAMIC DECOMPOSITION IS CORRECT:
    - Start with authentication check
    - FINDING: MD5 vulnerability
    - NEW SUBTASK: Check password reset flow
    - FINDING: No rate limiting on password reset
    - NEW SUBTASK: Check email verification
    - FINDING: Email verification uses insecure channel
    - NEW SUBTASK: Check data transmission security
    - Plan evolves with each discovery, follows the evidence

===========================================================================
 REAL-TIME SCENARIO 2: The Debugging Investigation
===========================================================================

    CONTEXT:
    - Production system has mysterious crashes
    - Root cause is unknown
    - Developer uses FIXED pipeline (WRONG!)

    FIXED APPROACH:
    Step 1: Check database logs
    Step 2: Check application logs
    Step 3: Check system metrics
    Step 4: Generate report

    THE PROBLEM:
    - Database logs show connection timeout
    - But WHY is there a timeout?
    - FIXED pipeline has no step for "investigate timeout cause"
    - Must force finding into wrong step or ignore it

    DYNAMIC APPROACH:
    - Start with database logs
    - FINDING: Connection timeout
    - NEW SUBTASK: Investigate connection pool
    - FINDING: Pool exhaustion
    - NEW SUBTASK: Check what exhausted the pool
    - FINDING: Memory leak in cache service
    - NEW SUBTASK: Check cache configuration
    - Follow the evidence, let root cause emerge

===========================================================================
 REAL-TIME SCENARIO 3: The Codebase Exploration
===========================================================================

    CONTEXT:
    - New developer joins team, needs to understand codebase
    - Task: "Map all services and their dependencies"
    - But you don't know what services exist!

    WHY FIXED FAILS:
    - Fixed pipeline requires knowing steps in advance
    - "Check service A, then B, then C" - but you don't know A, B, C
    - Must discover services first

    DYNAMIC WORKS:
    - Start with entry point (main.py)
    - FINDING: Imports auth_service, payment_service
    - NEW SUBTASK: Map auth_service dependencies
    - NEW SUBTASK: Map payment_service dependencies
    - Follow imports, discover the architecture
    - Subtasks emerge as you explore

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


# ================================================================================
# TASK STATE: Track discovery and subtasks
# ================================================================================

class ExplorationState:
    """
    State tracker for dynamic decomposition.
    Manages subtasks, findings, and discovery loop.
    """

    def __init__(self):
        self.subtasks = []
        self.completed = []
        self.findings = []
        self.discovered_new_leads = []

    def add_subtask(self, task: str, reason: str):
        """
        Add a new subtask discovered during exploration.
        This is the KEY feature of dynamic decomposition!
        """
        task_id = len(self.subtasks) + 1
        self.subtasks.append({
            "id": task_id,
            "task": task,
            "reason": reason,
            "status": "pending"
        })
        print(f"\n   [DISCOVERED] New subtask: {task}")
        print(f"   [REASON] {reason}")

    def complete_subtask(self, task_id: int, result: dict):
        """Mark a subtask as completed."""
        for task in self.subtasks:
            if task["id"] == task_id:
                task["status"] = "completed"
                task["result"] = result
                self.completed.append(task)
                break

    def get_pending_subtasks(self) -> list:
        """Get all pending subtasks."""
        return [t for t in self.subtasks if t["status"] == "pending"]

    def add_finding(self, finding: str):
        """Record a significant finding."""
        self.findings.append(finding)
        print(f"\n   [FINDING] {finding}")


# ================================================================================
# DYNAMIC DECOMPOSER: Adapts based on discoveries
# ================================================================================

def analyze_and_decompose(task: str, context: dict, state: ExplorationState):
    """
    Analyze a task and dynamically generate subtasks.

    Unlike fixed pipeline, this can discover NEW subtasks based on findings.
    """
    print(f"\n   [ANALYZING] {task}")

    # Initial decomposition based on task type
    subtasks = []

    if "explore" in task.lower() or "investigate" in task.lower():
        # Open-ended exploration - start broad
        subtasks = [
            {"task": "Identify key components and their relationships", "priority": 1},
            {"task": "Map data flows and dependencies", "priority": 2},
            {"task": "Identify potential issues or anomalies", "priority": 3}
        ]

    elif "security" in task.lower() or "audit" in task.lower():
        # Security audit - check common vulnerability areas
        subtasks = [
            {"task": "Check authentication mechanisms", "priority": 1},
            {"task": "Analyze input validation", "priority": 1},
            {"task": "Review data access patterns", "priority": 2},
            {"task": "Check for injection vulnerabilities", "priority": 1}
        ]

    return subtasks


def process_subtask(subtask: dict, state: ExplorationState) -> dict:
    """
    Process a single subtask and potentially discover new ones.

    This is where the ADAPTIVE part happens - subtasks can spawn new subtasks!
    """
    task = subtask["task"]

    print(f"\n   [PROCESSING] {task}")

    # Simulate processing
    result = {
        "status": "completed",
        "summary": f"Processed: {task}"
    }

    # Simulate discoveries that lead to new subtasks
    # In real implementation, this would be AI-driven
    if "authentication" in task.lower():
        state.add_finding("Authentication uses outdated hashing algorithm")
        state.add_subtask(
            "Check password storage implementation",
            "Related to authentication finding"
        )
        state.add_subtask(
            "Review session management",
            "Related to authentication finding"
        )

    elif "database" in task.lower() or "data" in task.lower():
        state.add_finding("Found direct SQL query construction")
        state.add_subtask(
            "Check for SQL injection vulnerability",
            "Direct SQL queries found - potential injection risk"
        )

    elif "api" in task.lower() or "endpoint" in task.lower():
        state.add_finding("API endpoints lack rate limiting")
        state.add_subtask(
            "Review API security controls",
            "Rate limiting missing - potential DoS vector"
        )

    return result


def run_dynamic_decomposition(initial_task: str) -> dict:
    """
    Execute dynamic adaptive decomposition.

    Unlike fixed pipeline, this continues until no more pending subtasks
    OR a stopping condition is met.
    """
    print("\n" + "=" * 70)
    print("DYNAMIC ADAPTIVE DECOMPOSITION")
    print("=" * 70)

    state = ExplorationState()

    print(f"\nInitial Task: {initial_task}")

    # Step 1: Initial decomposition
    print("\n[PHASE 1] Initial Decomposition")
    initial_subtasks = analyze_and_decompose(initial_task, {}, state)

    print(f"\n   Generated {len(initial_subtasks)} initial subtasks")
    for i, st in enumerate(initial_subtasks, 1):
        state.add_subtask(st["task"], f"Initial subtask {i}")

    # Step 2: Process subtasks (may discover new ones)
    print("\n[PHASE 2] Process Subtasks (Adaptive)")
    max_iterations = 20  # Safety limit to prevent infinite loops
    iteration = 0

    while state.get_pending_subtasks() and iteration < max_iterations:
        iteration += 1
        pending = state.get_pending_subtasks()

        print(f"\n   Iteration {iteration}: {len(pending)} pending subtasks")

        # Process each pending subtask
        for subtask in pending[:]:  # Copy list to avoid modification during iteration
            result = process_subtask(subtask, state)
            state.complete_subtask(subtask["id"], result)

            # Safety: stop if we discover too many new subtasks
            if len(state.subtasks) > 15:
                print(f"\n   [LIMIT] Too many subtasks discovered ({len(state.subtasks)}). Stopping to prevent infinite loop.")
                break

    # Step 3: Compile results
    print("\n[PHASE 3] Compile Results")

    return {
        "status": "complete",
        "total_subtasks": len(state.subtasks),
        "completed": len(state.completed),
        "findings": state.findings,
        "all_subtasks": state.subtasks
    }


def demonstrate_dynamic_vs_fixed():
    """
    Compare dynamic decomposition to fixed pipeline.
    """
    print("\n" + "=" * 70)
    print("DYNAMIC vs FIXED: When to Use Each")
    print("=" * 70)

    print("""
    +======================================================================+
    ||  FIXED PIPELINE                                                     ||
    ||                                                                      ||
    ||  Task: "Review authentication code"                                ||
    ||  Plan: Step 1 --> Step 2 --> Step 3 --> Done                        ||
    ||                                                                      ||
    ||  Problem: What if you discover the auth system is broken           ||
    ||           in a way that requires checking OTHER systems?            ||
    ||                                                                      ||
    ||  FIXED pipeline CANNOT adapt!                                       ||
    +======================================================================+

    +======================================================================+
    ||  DYNAMIC DECOMPOSITION                                              ||
    ||                                                                      ||
    ||  Task: "Review authentication code"                                ||
    ||  Plan: Start with auth, FOLLOW THE EVIDENCE                         ||
    ||                                                                      ||
    ||  Step 1: Review auth --> Find: SQL query vulnerability             ||
    ||  Step 2: Investigate SQL --> Find: No parameterized queries         ||
    ||  Step 3: Check database layer --> Find: Raw queries everywhere      ||
    ||  Step 4: Expand scope --> Need to check ALL database calls        ||
    ||                                                                      ||
    ||  DYNAMIC adapts to discoveries!                                     ||
    +======================================================================+
    """)


def demonstrate_investigation():
    """
    Demonstrate a real investigation scenario.
    """
    print("\n" + "=" * 70)
    print("DEMO: Legacy System Investigation")
    print("=" * 70)

    initial_task = "Investigate the legacy order processing system for security issues"

    print(f"\nInitial Task: {initial_task}")
    print("\n" + "-" * 50)

    result = run_dynamic_decomposition(initial_task)

    print("\n" + "=" * 70)
    print("INVESTIGATION COMPLETE")
    print("=" * 70)

    print(f"\n   Subtasks generated: {result['total_subtasks']}")
    print(f"   Subtasks completed: {result['completed']}")
    print(f"\n   Key Findings:")
    for i, finding in enumerate(result['findings'], 1):
        print(f"   {i}. {finding}")


def show_real_time_mistakes():
    """
    Shows REAL mistakes developers make with dynamic decomposition.
    """
    print("\n" + "=" * 70)
    print("REAL MISTAKES DEVELOPERS MAKE - EXPERT WARNINGS")
    print("=" * 70)

    print("""
    +======================================================================+
    ||                                                                      ||
    ||  MISTAKE #1: Not having safety limits (infinite loops!)            ||
    ||  =================================================================   ||
    ||                                                                      ||
    ||  WHAT HAPPENS IN PRODUCTION:                                        ||
    ||  - Agent keeps discovering new subtasks                             ||
    ||  - No limit on number of subtasks                                    ||
    ||  - Process never ends, runs forever                                 ||
    ||                                                                      ||
    ||  REAL CONSEQUENCE:                                                   ||
    ||  - "The investigation has been running for 3 days"                   ||
    ||  - Must kill the process                                            ||
    ||  - No results to show                                               ||
    ||                                                                      ||
    ||  CORRECT APPROACH:                                                   ||
    ||  - Set MAX_SUBTASKS limit (e.g., 20 or 50)                          ||
    ||  - Stop when limit reached                                           ||
    ||  - Return partial results with "limit reached" status              ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  MISTAKE #2: Using dynamic for everything (over-engineering)        ||
    ||  =================================================================   ||
    ||                                                                      ||
    ||  WHAT HAPPENS:                                                       ||
    ||  - Developer uses dynamic for simple document processing            ||
    ||  - Each document triggers different subtask sequence                ||
    ||  - No consistency between runs                                      ||
    ||  - Hard to test, audit, predict                                     ||
    ||                                                                      ||
    ||  REAL CONSEQUENCE:                                                   ||
    ||  - Document A: Extract -> Transform -> Validate -> Store            ||
    ||  - Document B: Transform -> Extract -> Store (skip validation!)    ||
    ||  - Document C: Validate -> Store (skip extract!)                     ||
    ||  - No predictability, hard to debug                                  ||
    ||                                                                      ||
    ||  CORRECT APPROACH:                                                   ||
    ||  - FIXED pipeline for structured tasks                              ||
    ||  - Dynamic only for open-ended investigation                        ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  MISTAKE #3: Not tracking findings properly                         ||
    ||  =================================================================   ||
    ||                                                                      ||
    ||  WHAT HAPPENS:                                                       ||
    ||  - Agent finds important issue                                       ||
    ||  - But doesn't record it properly                                    ||
    ||  - Findings lost when subtask completes                              ||
    ||  - Final report missing critical discoveries                        ||
    ||                                                                      ||
    ||  CORRECT APPROACH:                                                   ||
    ||  - ExplorationState tracks all findings                              ||
    ||  - Add finding at each discovery                                    ||
    ||  - Include findings in final report                                  ||
    ||                                                                      ||
    +======================================================================+
    """)


def show_interview_qa():
    """
    Shows common interview questions and expert answers.
    """
    print("\n" + "=" * 70)
    print("INTERVIEW QUESTIONS & EXPERT ANSWERS GUIDE")
    print("=" * 70)

    # Q1
    print("""
    ======================================================================
    INTERVIEW Q1: "When would you choose dynamic over fixed?"
    ======================================================================

    EXPECTED ANSWER:
    Dynamic when task scope is unknown or discoveries may change direction.
    Examples: legacy system exploration (don't know what you'll find),
    security audits (vulnerabilities can be anywhere), debugging unfamiliar
    code (root cause unknown), research investigation (open-ended, follow
    the evidence).

    RED FLAGS IN ANSWERS:
    - "Always use dynamic, it's more flexible" -> Over-engineering
    - "I don't know the difference" -> Not clear on patterns

    +-----------------------------------------------------------------------+
    | EXPERT TIP: Give concrete scenario where dynamic was necessary        |
    | "We found that auth vulnerability led to database exposure, which    |
    | led to another vulnerability. Fixed pipeline would have missed this."  |
    +-----------------------------------------------------------------------+
    """)

    # Q2
    print("""
    ======================================================================
    INTERVIEW Q2: "How do you prevent infinite loops in dynamic?"
    ======================================================================

    EXPECTED ANSWER:
    Set a MAX_SUBTASKS limit and check it at each iteration. When limit
    is reached, stop and return partial results with status indicating
    "limit reached". This ensures the process terminates even if discoveries
    continue. Also track completed subtasks to avoid re-processing.

    +-----------------------------------------------------------------------+
    | EXPERT TIP: Mention specific implementation details                   |
    | "I use max_subtasks=20 and check after each subtask completes"      |
    +-----------------------------------------------------------------------+
    """)

    # Q3
    print("""
    ======================================================================
    INTERVIEW Q3: "How does dynamic handle discoveries that change scope?"
    ======================================================================

    EXPECTED ANSWER:
    When a subtask produces a finding that requires new investigation,
    a new subtask is generated and added to the pending list. The loop
    continues processing pending subtasks (including newly discovered ones)
    until no pending remain OR the limit is reached. This allows the plan
    to evolve based on evidence, not stick to a predetermined sequence.

    +-----------------------------------------------------------------------+
    | EXPERT TIP: Explain the loop mechanism                                 |
    | "while pending_subtasks: process subtask -> check for new findings   |
    | -> generate new subtasks -> add to pending -> continue"              |
    +-----------------------------------------------------------------------+
    """)


def show_pros_and_cons():
    """
    Show pros and cons of dynamic decomposition.
    """
    print("\n" + "=" * 70)
    print("PROS AND CONS")
    print("=" * 70)

    print("""
    +======================================================================+
    ||  PROS:                                                              ||
    ||                                                                      ||
    ||  [CHECK] Adapts to unexpected complexity                             ||
    ||  [CHECK] Can follow any lead or discovery                           ||
    ||  [CHECK] Produces thorough, comprehensive results                   ||
    ||  [CHECK] Better for research and investigation                      ||
    ||  [CHECK] Handles ambiguity well                                     ||
    ||                                                                      ||
    +======================================================================+
    ||                                                                      ||
    ||  CONS:                                                               ||
    ||                                                                      ||
    ||  [ X ] Less predictable                                             ||
    ||  [ X ] Harder to estimate completion time                            ||
    ||  [ X ] More complex to implement and debug                         ||
    ||  [ X ] May go down rabbit holes                                     ||
    ||  [ X ] Difficult to monitor progress                                ||
    ||  [ X ] Need safety limits to prevent infinite loops                ||
    ||                                                                      ||
    +======================================================================+
    """)


def show_visual_state_tracking():
    """
    Show visual of how state tracking works.
    """
    print("\n" + "=" * 70)
    print("VISUAL: STATE TRACKING IN DYNAMIC DECOMPOSITION")
    print("=" * 70)

    print("""
    +======================================================================+
    ||  EXPLORATION STATE                                                  ||
    ||                                                                      ||
    ||  +------------------+                                               ||
    ||  | subtasks: []     |  <-- All subtasks (pending + completed)       ||
    ||  +------------------+                                               ||
    ||  | completed: []    |  <-- Finished subtasks                        ||
    ||  +------------------+                                               ||
    ||  | findings: []     |  <-- Key discoveries                          ||
    ||  +------------------+                                               ||
    ||                                                                      ||
    ||  FLOW:                                                               ||
    ||  1. Initial subtasks added to subtasks[] with status="pending"      ||
    ||  2. Process subtask: look at subtask, do work, potentially find    ||
    ||  3. If finding leads to new subtask: add_subtask() -> subtasks[]    ||
    ||  4. Complete subtask: mark status="completed", add to completed[]  ||
    ||  5. Continue until no pending OR limit reached                      ||
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
|  PRACTICE 4: DYNAMIC ADAPTIVE DECOMPOSITION                             |
|  + REAL-TIME SCENARIOS + MISTAKES + INTERVIEW Q&A + VISUALS             |
|                                                                           |
|  This program teaches:                                                   |
|  1. How to implement dynamic decomposition                               |
|  2. Real production scenarios where it fits                              |
|  3. Common mistakes and how to avoid them                                |
|  4. Interview Q&A with expert answer frameworks                         |
|                                                                           |
+===========================================================================+
    """)

    demonstrate_dynamic_vs_fixed()
    demonstrate_investigation()
    show_real_time_mistakes()
    show_interview_qa()
    show_pros_and_cons()
    show_visual_state_tracking()

    print("\n" + "=" * 70)
    print("WHAT WE HAVE LEARNT")
    print("=" * 70)
    print("""
    +======================================================================+
    ||  1. HOW TO IMPLEMENT DYNAMIC DECOMPOSITION:                        ||
    ||                                                                      ||
    ||  - ExplorationState tracks subtasks, findings, completed            ||
    ||  - Initial decomposition generates starting subtasks                 ||
    ||  - Process loop: each subtask can discover NEW subtasks              ||
    ||  - Loop continues until no pending OR limit reached                 ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  2. REAL-TIME SCENARIOS:                                            ||
    ||                                                                      ||
    ||  SCENARIO 1: Legacy Security Audit                                   ||
    ||  - Start with auth check -> find MD5 vulnerability                  ||
    ||  - Leads to password reset -> leads to email verification          ||
    ||  - Fixed pipeline would miss these connections                      ||
    ||                                                                      ||
    ||  SCENARIO 2: Debugging Investigation                                ||
    ||  - Start with logs -> find connection timeout                       ||
    ||  - Leads to pool exhaustion -> leads to memory leak                 ||
    ||  - Follow evidence, let root cause emerge                           ||
    ||                                                                      ||
    ||  SCENARIO 3: Codebase Exploration                                   ||
    ||  - Start with entry point -> discover services                      ||
    ||  - Follow imports -> map dependencies                               ||
    ||  - Subtasks emerge as you explore                                   ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  3. COMMON MISTAKES (EXPERT WARNINGS):                             ||
    ||                                                                      ||
    ||  MISTAKE #1: No safety limits (infinite loops)                       ||
    ||  - Agent keeps discovering, never stops                            ||
    ||  - FIX: Set MAX_SUBTASKS limit, check after each iteration           ||
    ||                                                                      ||
    ||  MISTAKE #2: Dynamic for everything (over-engineering)              ||
    ||  - Inconsistent results, hard to audit                             ||
    ||  - FIX: Use fixed for structured tasks                              ||
    ||                                                                      ||
    ||  MISTAKE #3: Not tracking findings properly                         ||
    ||  - Discoveries lost, final report incomplete                        ||
    ||  - FIX: ExplorationState tracks all findings                         ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  4. INTERVIEW TIPS:                                                 ||
    ||                                                                      ||
    ||  - Know when to use dynamic (unknown scope, discoveries matter)      ||
    ||  - Explain safety limits (max_subtasks)                             ||
    ||  - Describe the discovery loop mechanism                             ||
    ||                                                                      ||
    ||  EXPECTED ANSWER STRUCTURE:                                          ||
    ||  1. When dynamic is appropriate (scenarios)                         ||
    ||  2. How it adapts (subtask generates subtask)                       ||
    ||  3. How to prevent infinite loops (safety limits)                   ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  5. KEY RULES TO MEMORIZE:                                          ||
    ||                                                                      ||
    ||  RULE #1: Unknown scope? -> Use dynamic decomposition                 ||
    ||  RULE #2: Always set MAX_SUBTASKS limit to prevent infinite loops   ||
    ||  RULE #3: Track findings in ExplorationState                        ||
    ||  RULE #4: Don't use dynamic for structured tasks (use fixed)        ||
    ||                                                                      ||
    +======================================================================+

    Next: practice_05_multi_pass_architecture.py shows the complete
    solution for attention dilution with multi-pass!
    """)


"""
+===========================================================================+
|                                                                           |
|  KEY CONCEPTS FROM THIS FILE:                                           |
|                                                                           |
|  DYNAMIC DECOMPOSITION:                                                  |
|  - Subtasks generated based on discoveries                              |
|  - Plan evolves as more is learned                                       |
|  - ExplorationState tracks subtasks, findings, completed                 |
|                                                                           |
|  SAFETY MECHANISMS:                                                     |
|  - MAX_SUBTASKS limit to prevent infinite loops                          |
|  - Track completed subtasks to avoid re-processing                       |
|  - Include findings in final report                                      |
|                                                                           |
|  USE CASES:                                                              |
|  - Legacy system exploration (don't know what you'll find)              |
|  - Security audits (vulnerabilities can be anywhere)                      |
|  - Debugging unfamiliar code (root cause unknown)                         |
|  - Research investigation (open-ended, follow evidence)                  |
|                                                                           |
|  EXAM TIPS:                                                              |
|  - Always set safety limits (max_subtasks)                               |
|  - Track findings in ExplorationState                                     |
|  - Use fixed for structured, dynamic for open-ended                      |
|                                                                           |
|  INTERVIEW PREP:                                                        |
|  - "When would you choose dynamic over fixed?"                           |
|  - "How do you prevent infinite loops?"                                  |
|  - "How does dynamic handle discoveries?"                                |
|                                                                           |
+===========================================================================+
"""