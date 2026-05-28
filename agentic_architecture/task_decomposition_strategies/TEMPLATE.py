"""
+===========================================================================+
|                                                                           |
|  TASK DECOMPOSITION STRATEGIES - TEMPLATE                               |
|                                                                           |
|  Your starting point for implementing task decomposition strategies.      |
|                                                                           |
|  Choose the right pattern based on your task:                            |
|      FIXED PIPELINE: Steps known in advance                               |
|      DYNAMIC DECOMPOSITION: Steps emerge from discoveries                |
|      MULTI-PASS: Many items needing equal attention                      |
|                                                                           |
|  + REAL-TIME SCENARIOS + MISTAKES + INTERVIEW Q&A + VISUALS             |
|                                                                           |
+===========================================================================+

This template provides three decomposition patterns:

INTERVIEW PREP: "How do you choose between fixed, dynamic, and multi-pass?"
Tests understanding of when to apply each pattern.

===========================================================================
 PATTERN SELECTION QUICK GUIDE
===========================================================================

    +-----------------------------------------------------------------------+
    |  QUESTION: Do you know the steps in advance?                         |
    |                                                                       |
    |  YES --> FIXED PIPELINE                                             |
    |  - Steps predetermined                                              |
    |  - Order is fixed                                                    |
    |  - Examples: document processing, code review, compliance              |
    |                                                                       |
    |  NO --> QUESTION: Is the scope open-ended?                          |
    |                                                                       |
    |       YES --> DYNAMIC DECOMPOSITION                                  |
    |       - Subtasks emerge from discoveries                             |
    |       - Plan evolves with evidence                                   |
    |       - Examples: investigation, security audit, debugging            |
    |                                                                       |
    |       NO --> QUESTION: Many items needing equal attention?          |
    |                                                                       |
    |            YES --> MULTI-PASS                                       |
    |            - Pass 1: Each item gets full attention                   |
    |            - Pass 2: Cross-item integration                          |
    |            - Examples: batch file review, multi-doc analysis         |
    |                                                                       |
    |            NO --> SINGLE PASS                                        |
    |            - One item, straightforward task                          |
    |                                                                       |
    +-----------------------------------------------------------------------+

===========================================================================
 REAL-TIME SCENARIO 1: Choosing the Wrong Pattern
===========================================================================

    CONTEXT:
    - Developer building document processing system
    - Uses DYNAMIC decomposition (wrong choice!)
    - "I want flexibility in case documents are different"

    WHAT HAPPENS:
    - Document A: Extract -> Transform -> Validate -> Store
    - Document B: Transform -> Extract -> Store (skip validation!)
    - Document C: Store (skip everything else!)
    - Inconsistent results, no audit trail, quality varies

    THE BROKEN THING:
    - Structured task with known steps
    - Using dynamic when fixed is correct
    - "Flexibility" is actually inconsistency

    THE FIX:
    - FIXED PIPELINE for document processing
    - Steps are known: extract -> transform -> validate -> store
    - Same order every time, consistent results

===========================================================================
 REAL-TIME SCENARIO 2: Ignoring Attention Dilution
===========================================================================

    CONTEXT:
    - Developer building code review system
    - Reviews 100 files for security issues
    - Uses FIXED PIPELINE in single pass (wrong approach!)

    WHAT HAPPENS:
    - Files 1-20: Detailed review (issues found)
    - Files 80-100: Shallow review (critical bugs missed!)
    - "We reviewed all 100 files"
    - But files 80-100 had critical vulnerabilities

    THE BROKEN THING:
    - Many items needing equal attention
    - Single pass causes attention dilution
    - Fixed pipeline is right, but architecture is wrong

    THE FIX:
    - MULTI-PASS ARCHITECTURE
    - Pass 1: Each file gets full attention (loop)
    - Pass 2: Cross-file integration
    - All files get equal coverage

===========================================================================
 REAL-TIME SCENARIO 3: Dynamic for Structured Task
===========================================================================

    CONTEXT:
    - Developer building invoice processing
    - Uses DYNAMIC decomposition (wrong!)
    - "Each invoice might need different processing"

    WHAT HAPPENS:
    - Invoice 1: Standard -> All 4 steps
    - Invoice 2: Has attachments -> New subtask A, B, C
    - Invoice 3: Missing fields -> New subtask D
    - No consistency, can't predict what happens

    THE FIX:
    - FIXED PIPELINE
    - All invoices: Extract -> Transform -> Validate -> Store
    - Validation catches anomalies
    - Consistent, testable, auditable

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
# PATTERN SELECTOR: Choose the right decomposition strategy
# ================================================================================

def select_decomposition_pattern(task_type: str) -> str:
    """
    Select the appropriate decomposition pattern based on task type.

    Returns: "fixed", "dynamic", or "multi_pass"
    """
    if task_type in ["review", "process", "extract", "validate", "transform"]:
        # Structured tasks with known steps
        return "fixed"

    elif task_type in ["explore", "investigate", "audit", "debug", "research"]:
        # Open-ended tasks with unknown scope
        return "dynamic"

    elif task_type in ["batch", "review_multiple", "analyze_files", "check_items"]:
        # Many items needing equal attention
        return "multi_pass"

    return "fixed"  # Default to fixed


# ================================================================================
# PATTERN 1: FIXED SEQUENTIAL PIPELINE
# ================================================================================

class FixedPipeline:
    """
    Fixed sequential pipeline for predictable, structured tasks.

    Steps are known in advance, execute in order.
    Each step takes previous output as input.
    """

    def __init__(self, steps: list):
        self.steps = steps

    def execute(self, initial_input: dict) -> dict:
        """Execute pipeline with error handling."""
        context = initial_input.copy()
        results = []

        for i, step in enumerate(self.steps):
            print(f"\n[STEP {i + 1}] {step['name']}")

            try:
                output = step['handler'](context)
                context.update(output)
                results.append({
                    "step": step['name'],
                    "status": "success",
                    "output": output
                })

                # Check for validation failures - FAIL FAST
                if output.get('validation') == 'failed':
                    return {
                        "status": "failed",
                        "failed_at": step['name'],
                        "results": results
                    }

            except Exception as e:
                return {
                    "status": "failed",
                    "failed_at": step['name'],
                    "error": str(e),
                    "results": results
                }

        return {
            "status": "success",
            "results": results,
            "final_output": context
        }


# ================================================================================
# PATTERN 2: DYNAMIC ADAPTIVE DECOMPOSITION
# ================================================================================

class DynamicDecomposer:
    """
    Dynamic adaptive decomposition for open-ended tasks.

    Subtasks are generated based on discoveries.
    Plan evolves as more is learned.
    """

    def __init__(self, max_subtasks: int = 20):
        self.max_subtasks = max_subtasks
        self.subtasks = []
        self.completed = []
        self.findings = []

    def add_subtask(self, task: str, reason: str):
        """Add a new subtask discovered during exploration."""
        if len(self.subtasks) >= self.max_subtasks:
            print(f"[LIMIT] Max subtasks reached ({self.max_subtasks})")
            return

        self.subtasks.append({
            "id": len(self.subtasks) + 1,
            "task": task,
            "reason": reason,
            "status": "pending"
        })

    def complete_subtask(self, task_id: int, result: dict):
        """Mark a subtask as completed."""
        for st in self.subtasks:
            if st["id"] == task_id:
                st["status"] = "completed"
                st["result"] = result
                self.completed.append(st)
                break

    def run(self, initial_task: str, initial_subtasks: list) -> dict:
        """Execute dynamic decomposition."""
        # Add initial subtasks
        for st in initial_subtasks:
            self.add_subtask(st['task'], st.get('reason', 'Initial subtask'))

        # Process loop
        while self.get_pending():
            pending = self.get_pending()

            for st in pending[:]:
                # Process subtask
                result = self.process_subtask(st)

                # Check for new subtasks from discoveries
                new_subtasks = self.discover_new_subtasks(result)
                for nt in new_subtasks:
                    self.add_subtask(nt['task'], nt['reason'])

                self.complete_subtask(st['id'], result)

                if len(self.subtasks) >= self.max_subtasks:
                    break

        return {
            "status": "complete",
            "total": len(self.subtasks),
            "completed": len(self.completed),
            "findings": self.findings
        }

    def get_pending(self) -> list:
        return [st for st in self.subtasks if st["status"] == "pending"]

    def process_subtask(self, subtask: dict) -> dict:
        """Process a single subtask. Override for custom logic."""
        return {"status": "completed", "summary": subtask['task']}

    def discover_new_subtasks(self, result: dict) -> list:
        """Override to discover new subtasks based on results."""
        return []


# ================================================================================
# PATTERN 3: MULTI-PASS ARCHITECTURE
# ================================================================================

class MultiPassReviewer:
    """
    Multi-pass architecture for analyzing many items with equal attention.

    PASS 1: Per-item local analysis (full attention per item)
    PASS 2: Cross-item integration (check relationships)
    """

    def __init__(self):
        self.local_results = []
        self.integration_results = []

    def pass_1_local_analysis(self, items: list) -> list:
        """
        PASS 1: Analyze each item with FULL attention.

        Each item gets its own pass - no attention sharing.
        """
        results = []

        for i, item in enumerate(items, 1):
            print(f"   [{i}/{len(items)}] Analyzing {item.get('name', item.get('id', 'item'))}...")

            # Full attention analysis for this item
            result = self.analyze_item(item)
            results.append(result)

        self.local_results = results
        return results

    def pass_2_integration(self) -> list:
        """
        PASS 2: Check for cross-item issues.
        """
        issues = []

        # Check for pattern consistency
        # Check for data flow issues
        # Check for cross-cutting concerns

        self.integration_results = issues
        return issues

    def analyze_item(self, item: dict) -> dict:
        """Override with actual analysis logic."""
        return {
            "item": item,
            "issues": [],
            "status": "complete"
        }

    def run(self, items: list) -> dict:
        """Execute multi-pass review."""
        # PASS 1: Local analysis
        local_results = self.pass_1_local_analysis(items)

        # PASS 2: Integration
        integration_issues = self.pass_2_integration()

        # Combine
        all_issues = []
        for result in local_results:
            for issue in result.get('issues', []):
                issue['source'] = result['item']
                all_issues.append(issue)

        for issue in integration_issues:
            all_issues.append(issue)

        return {
            "status": "complete",
            "items_processed": len(items),
            "local_results": local_results,
            "integration_issues": integration_issues,
            "total_issues": len(all_issues)
        }


# ================================================================================
# DEMO: Show how to use each pattern
# ================================================================================

def demo_fixed_pipeline():
    """Demo: Fixed pipeline for document processing."""
    print("\n" + "=" * 60)
    print("DEMO: Fixed Pipeline")
    print("=" * 60)

    def step_1_extract(data):
        return {"text": "Extracted from document"}

    def step_2_transform(data):
        return {"structured": {"key": "value"}}

    def step_3_load(data):
        return {"stored": True}

    pipeline = FixedPipeline([
        {"name": "Extract", "handler": step_1_extract},
        {"name": "Transform", "handler": step_2_transform},
        {"name": "Load", "handler": step_3_load}
    ])

    result = pipeline.execute({"document": "report.pdf"})
    print(f"\n   Result: {result['status']}")


def demo_dynamic_decomposition():
    """Demo: Dynamic decomposition for investigation."""
    print("\n" + "=" * 60)
    print("DEMO: Dynamic Decomposition")
    print("=" * 60)

    class InvestigationDecomposer(DynamicDecomposer):
        def process_subtask(self, subtask):
            # Simulate processing
            return {"status": "completed", "finding": f"Analyzed: {subtask['task']}"}

        def discover_new_subtasks(self, result):
            # Simulate discovery
            if len(self.completed) == 1:
                return [{"task": "Related task discovered", "reason": "Based on finding"}]
            return []

    decomposer = InvestigationDecomposer(max_subtasks=10)
    result = decomposer.run("Investigate security", [
        {"task": "Check authentication"},
        {"task": "Check database access"}
    ])

    print(f"\n   Result: {result['status']}")
    print(f"   Subtasks: {result['total']}")


def demo_multi_pass():
    """Demo: Multi-pass for batch review."""
    print("\n" + "=" * 60)
    print("DEMO: Multi-Pass")
    print("=" * 60)

    class FileReviewer(MultiPassReviewer):
        def analyze_item(self, item):
            return {
                "item": item['name'],
                "issues": [{"type": "style", "description": "Minor issue"}],
                "status": "complete"
            }

    reviewer = FileReviewer()
    files = [
        {"name": f"file_{i}.py"} for i in range(1, 6)
    ]

    result = reviewer.run(files)
    print(f"\n   Files reviewed: {result['items_processed']}")
    print(f"   Issues found: {result['total_issues']}")


def show_pattern_comparison():
    """
    Show comparison of three patterns.
    """
    print("\n" + "=" * 70)
    print("PATTERN COMPARISON")
    print("=" * 70)

    print("""
    +======================================================================+
    ||                      PATTERN COMPARISON                             ||
    ||                                                                      ||
    ||  +------------------+------------------+------------------+          ||
    ||  | Aspect           | Fixed           | Dynamic         |          ||
    ||  +------------------+------------------+------------------+          ||
    ||  | Steps known?     | Yes             | No              |          ||
    ||  | Order fixed?     | Yes             | No              |          ||
    ||  | Adapts?          | No              | Yes             |          ||
    ||  | Scope known?     | Yes             | No              |          ||
    ||  | Safety limits?   | Not needed      | Yes (max_subs)  |          ||
    ||  +------------------+------------------+------------------+          ||
    ||                                                                      ||
    ||  +------------------+------------------+                           ||
    ||  | Aspect           | Multi-Pass      |                             ||
    ||  +------------------+------------------+                           ||
    ||  | Many items?      | Yes             |                             ||
    ||  | Equal attention?  | Yes             |                             ||
    ||  | Passes?          | 2 (local+int)   |                             ||
    ||  +------------------+------------------+                           ||
    ||                                                                      ||
    +======================================================================+
    """)


def show_when_to_use():
    """
    Show when to use each pattern.
    """
    print("\n" + "=" * 70)
    print("WHEN TO USE EACH PATTERN")
    print("=" * 70)

    print("""
    +======================================================================+
    ||  USE FIXED PIPELINE WHEN:                                          ||
    ||                                                                      ||
    ||  - Steps are known in advance                                        ||
    ||  - Order is predetermined                                           ||
    ||  - Task is structured and predictable                                ||
    ||                                                                      ||
    ||  Examples:                                                           ||
    ||  - Document processing: Extract -> Transform -> Validate -> Store    ||
    ||  - Code review: Lint -> Test -> Scan -> Deploy                      ||
    ||  - Compliance: Check Rule 1 -> Rule 2 -> ... -> Report              ||
    +======================================================================+

    +======================================================================+
    ||  USE DYNAMIC DECOMPOSITION WHEN:                                    ||
    ||                                                                      ||
    ||  - Scope is unknown or open-ended                                    ||
    ||  - Discoveries may change direction                                  ||
    ||  - Following the evidence matters                                    ||
    ||                                                                      ||
    ||  Examples:                                                           ||
    ||  - Legacy system exploration (don't know what you'll find)          ||
    ||  - Security audits (vulnerabilities can be anywhere)                ||
    ||  - Debugging unfamiliar code (root cause unknown)                     ||
    ||  - Research investigation (open-ended, follow evidence)             ||
    ||                                                                      ||
    ||  IMPORTANT: Set max_subtasks limit to prevent infinite loops!        ||
    +======================================================================+

    +======================================================================+
    ||  USE MULTI-PASS WHEN:                                               ||
    ||                                                                      ||
    ||  - Many items needing equal attention                                ||
    ||  - Single pass would cause attention dilution                        ||
    ||  - Cross-item relationships matter                                   ||
    ||                                                                      ||
    ||  Examples:                                                           ||
    ||  - Batch file review (50+ files)                                     ||
    ||  - Multi-document analysis                                           ||
    ||  - Multiple endpoint documentation                                   ||
    ||  - Security review of entire codebase                               ||
    ||                                                                      ||
    ||  IMPORTANT: Pass 1 = full attention per item. Pass 2 = integration! ||
    +======================================================================+
    """)


# ================================================================================
# MAIN
# ================================================================================

if __name__ == "__main__":
    print("""
+===========================================================================+
|                                                                           |
|  TASK DECOMPOSITION STRATEGIES - TEMPLATE                               |
|  + REAL-TIME SCENARIOS + MISTAKES + INTERVIEW Q&A + VISUALS             |
|                                                                           |
|  This template provides three decomposition patterns:                    |
|                                                                           |
|  1. FIXED PIPELINE: For structured, predictable tasks                    |
|  2. DYNAMIC DECOMPOSITION: For open-ended investigation                  |
|  3. MULTI-PASS: For many items needing equal attention                  |
|                                                                           |
|  Choose based on your task characteristics!                             |
|                                                                           |
+===========================================================================+
    """)

    demo_fixed_pipeline()
    demo_dynamic_decomposition()
    demo_multi_pass()
    show_pattern_comparison()
    show_when_to_use()

    print("\n" + "=" * 70)
    print("WHAT WE HAVE LEARNT")
    print("=" * 70)
    print("""
    +======================================================================+
    ||  1. THREE DECOMPOSITION PATTERNS:                                   ||
    ||                                                                      ||
    ||  FIXED PIPELINE:                                                    ||
    ||  - Steps known in advance, execute in order                          ||
    ||  - Each step takes previous output as input                         ||
    ||  - Best for: code review, document processing, compliance             ||
    ||                                                                      ||
    ||  DYNAMIC DECOMPOSITION:                                             ||
    ||  - Subtasks emerge from discoveries                                 ||
    ||  - Plan evolves as you learn                                        ||
    ||  - Has safety limits (max_subtasks)                                ||
    ||  - Best for: investigation, security audits, debugging               ||
    ||                                                                      ||
    ||  MULTI-PASS:                                                        ||
    ||  - Pass 1: Each item gets full attention                            ||
    ||  - Pass 2: Check cross-item relationships                            ||
    ||  - Fixes attention dilution problem                                 ||
    ||  - Best for: batch file review, multi-doc analysis                  ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  2. PATTERN SELECTION:                                              ||
    ||                                                                      ||
    ||  Know the steps? --> FIXED PIPELINE                                 ||
    ||  Unknown scope? --> DYNAMIC DECOMPOSITION                            ||
    ||  Many items? --> MULTI-PASS                                         ||
    ||                                                                      ||
    ||  WRONG CHOICE = poor results or wasted effort                       ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  3. COMMON MISTAKES:                                               ||
    ||                                                                      ||
    ||  - Fixed for open-ended tasks (can't adapt)                         ||
    ||  - Dynamic for structured tasks (inconsistent results)             ||
    ||  - Single pass for many items (attention dilution)                   ||
    ||  - No safety limits in dynamic (infinite loops)                     ||
    ||  - Skipping integration pass (miss cross-file issues)                ||
    ||                                                                      ||
    +======================================================================+

    COPY THIS TEMPLATE and customize for your use case!

    CHOOSE THE RIGHT PATTERN:
    - Know the steps? --> Fixed pipeline
    - Unknown scope? --> Dynamic decomposition
    - Many items? --> Multi-pass
    """)


"""
+===========================================================================+
|                                                                           |
|  KEY CONCEPTS FROM THIS FILE:                                           |
|                                                                           |
|  THREE PATTERNS:                                                        |
|  - Fixed: steps known, execute in order                                  |
|  - Dynamic: subtasks emerge, plan evolves                                 |
|  - Multi-pass: each item full attention + integration                    |
|                                                                           |
|  PATTERN SELECTION:                                                     |
|  - Know steps? -> Fixed                                                  |
|  - Unknown scope? -> Dynamic                                             |
|  - Many items? -> Multi-pass                                             |
|                                                                           |
|  TEMPLATE USAGE:                                                         |
|  - Copy this file as starting point                                      |
|  - Implement FixedPipeline for structured tasks                          |
|  - Implement DynamicDecomposer for investigation                         |
|  - Implement MultiPassReviewer for batch analysis                        |
|                                                                           |
|  EXAM TIPS:                                                              |
|  - Always choose pattern based on task characteristics                   |
|  - Wrong pattern = poor results                                         |
|  - Multi-pass is architectural fix for attention dilution                 |
|                                                                           |
|  INTERVIEW PREP:                                                        |
|  - "How do you choose between fixed, dynamic, multi-pass?"              |
|  - "How does multi-pass fix attention dilution?"                         |
|  - "How do you prevent infinite loops in dynamic?"                       |
|                                                                           |
+===========================================================================+
"""