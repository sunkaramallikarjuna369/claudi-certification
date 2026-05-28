"""
+===========================================================================+
|                                                                           |
|  PRACTICE 1: TWO HOOK TYPES - PreToolUse vs PostToolUse                  |
|                                                                           |
|  Two types of hooks for controlling agent behavior:                      |
|                                                                           |
|    PRETOOLUSE: Runs BEFORE tool execution - can BLOCK, MODIFY, REDIRECT  |
|    POSTTOOLUSE: Runs AFTER tool execution - can TRANSFORM data           |
|                                                                           |
|  CERTIFICATION EXAM: Know when to use each hook type!                   |
|                                                                           |
+===========================================================================

===========================================================================
 VISUAL: HOOK TIMELINE COMPARISON
===========================================================================

    +======================================================================+
    ||                                                                  ||
    ||  PRETOOLUSE (BEFORE execution):                                  ||
    ||  ==============================================================  ||
    ||                                                                  ||
    ||     Model decides tool ─────> [PRETOOLUSE] ──> Execute ──> Done  ||
    ||                               Runs HERE                          ||
    ||                               Can BLOCK                          ||
    ||                               Can MODIFY                         ||
    ||                               Can REDIRECT                       ||
    ||                                                                  ||
    +======================================================================+

    +======================================================================+
    ||                                                                  ||
    ||  POSTTOOLUSE (AFTER execution):                                  ||
    ||  ==============================================================  ||
    ||                                                                  ||
    ||     Execute ──> [POSTTOOLUSE] ──> Model sees result              ||
    ||                  Runs HERE                                      ||
    ||                  Can TRANSFORM                                  ||
    ||                  Can ADD metadata                               ||
    ||                  CANNOT BLOCK (too late!)                       ||
    ||                                                                  ||
    +======================================================================+

===========================================================================
 REAL-TIME SCENARIO: When This Concept Breaks Things
===========================================================================

    SCENARIO: E-commerce Order Processing System

    A customer requests a $5000 refund. The AI agent tries to process it.

    +======================================================================+
    ||                                                                  ||
    ||  THE WRONG APPROACH: Using PostToolUse to block                   ||
    ||  ----------------------------------------------------------------  ||
    ||                                                                  ||
    ||  PostToolUse on process_refund:                                  ||
    ||      if amount > 1000:                                          ||
    ||          block()  <-- WRONG! Cannot block here!                ||
    ||                                                                  ||
    ||  What happens:                                                   ||
    ||  1. Tool executes (refund goes through)                         ||
    ||  2. PostToolUse runs AFTER execution                           ||
    ||  3. Block called - but money already refunded!                  ||
    ||  4. Company loses $5000!                                         ||
    ||                                                                  ||
    ||  ROOT CAUSE: PostToolUse runs AFTER execution.                  ||
    ||  By the time it runs, the action is DONE.                      ||
    ||                                                                  ||
    +======================================================================+

    +======================================================================+
    ||                                                                  ||
    ||  THE CORRECT APPROACH: Using PreToolUse to block                ||
    ||  ----------------------------------------------------------------  ||
    ||                                                                  ||
    ||  PreToolUse on process_refund:                                   ||
    ||      if amount > 1000:                                          ||
    ||          block()  <-- CORRECT! Prevents execution               ||
    ||                                                                  ||
    ||  What happens:                                                   ||
    ||  1. PreToolUse runs BEFORE execution                           ||
    ||  2. Block called - refund never executes                        ||
    ||  3. Customer notified of approval requirement                   ||
    ||  4. Company protected!                                           ||
    ||                                                                  ||
    +======================================================================+

===========================================================================
 MISTAKES DEVELOPERS MAKE
===========================================================================

    MISTAKE #1: Using PostToolUse to block unauthorized actions
    -----------------------------------------------------------------------
    if tool_name == "transfer_funds":
        # WRONG: This runs AFTER execution!
        if not user.has_permission:
            block()  # Too late - money already transferred!
    -----------------------------------------------------------------------
    WHY IT BREAKS: PostToolUse cannot undo an action that already happened.
    FIX: Use PreToolUse to check permissions BEFORE execution.

    MISTAKE #2: Using PreToolUse to normalize data
    -----------------------------------------------------------------------
    PreToolUse on get_weather:
        # WRONG: This runs BEFORE execution!
        data['temp'] = fahrenheit_to_celsius(data['temp'])  # No data yet!
    -----------------------------------------------------------------------
    WHY IT BREAKS: PreToolUse has no tool result to transform.
    FIX: Use PostToolUse to transform the result after execution.

    MISTAKE #3: Thinking hooks are optional for critical operations
    -----------------------------------------------------------------------
    "We'll just use a prompt saying 'never process refunds over $1000'"
    -----------------------------------------------------------------------
    WHY IT BREAKS: Prompts are ~90-95% reliable. 5% failure on financial
    ops = unacceptable risk. Hooks provide 100% deterministic enforcement.

===========================================================================
 INTERVIEW Q&A: Expert Answer Frameworks
===========================================================================

    Q1: "What's the difference between PreToolUse and PostToolUse?"
    ----------------------------------------------------------------
    TEMPLATE:
    "PreToolUse runs BEFORE tool execution and can block, modify, or
    redirect the tool call. PostToolUse runs AFTER execution and can
    only transform the result - it cannot block since the action already
    happened.

    Think of it like airport security:
    - PreToolUse = security checkpoint (can stop you)
    - PostToolUse = baggage claim (already on plane, just collecting)"

    KEY PHRASE: "PostToolUse cannot block because the action already occurred"

    ----------------------------------------------------------------

    Q2: "When would you use PreToolUse vs PostToolUse?"
    ----------------------------------------------------------------
    TEMPLATE:
    "Use PreToolUse for anything that MUST be enforced with 100%
    guarantee: security checks, compliance requirements, prerequisite
    verification, blocking unauthorized operations.

    Use PostToolUse for data transformation: normalizing formats from
    different sources, adding metadata, converting codes to readable
    strings.

    The decision rule: if single failure = financial loss or legal
    risk, use PreToolUse. If it's just transforming output, use
    PostToolUse."

    KEY PHRASE: "Financial/legal risk = PreToolUse, Data transformation = PostToolUse"

    ----------------------------------------------------------------

    Q3: "Can PostToolUse be used to prevent unauthorized actions?"
    ----------------------------------------------------------------
    TEMPLATE:
    "No. PostToolUse runs AFTER tool execution. By the time it runs,
    the action has already completed. If someone transfers $10,000
    without permission, PostToolUse cannot undo that transfer.

    This is why PreToolUse exists - it runs before execution and can
    actually block the operation."

    TRAP ANSWER TO AVOID: "Yes, PostToolUse can block" - THIS IS WRONG!

===========================================================================
 VISUAL: THE EXECUTION FLOW WITH BOTH HOOKS
===========================================================================

    +======================================================================+
    ||                                                                  ||
    ||  COMPLETE FLOW:                                                   ||
    ||                                                                  ||
    ||    1. Model decides: "Call transfer_funds"                       ||
    ||           |                                                      ||
    ||           v                                                      ||
    ||    2. [PRETOOLUSE] <-- Policy check happens HERE                ||
    ||           |                                                      ||
    ||       +---+---+                                                  ||
    ||       |       |                                                  ||
    ||    ALLOWED  BLOCKED                                             ||
    ||       |       |                                                  ||
    ||       v       v                                                  ||
    ||   Execute  Return error                                          ||
    ||       |       |                                                  ||
    ||       v       |                                                  ||
    ||   [POSTTOOLUSE]                                                  ||
    ||   (Transform)                                                   ||
    ||       |                                                          ||
    ||       v                                                          ||
    ||    Model sees result                                             ||
    ||                                                                  ||
    +======================================================================+

===========================================================================
 CODE PATTERN: PreToolUse vs PostToolUse
===========================================================================

    # PRETOOLUSE - BEFORE execution (can block)
    def pretooluse_hook(tool_name, params):
        if tool_name == "process_refund":
            if params["amount"] > 5000:
                return {
                    "allowed": False,
                    "error": "AMOUNT_EXCEEDS_LIMIT",
                    "message": "Refunds over $5000 need manager approval"
                }
        return {"allowed": True}

    # POSTTOOLUSE - AFTER execution (cannot block)
    def posttooluse_hook(tool_name, result):
        if tool_name == "get_customer":
            # Add metadata to existing result
            result["retrieved_at"] = get_timestamp()
            result["data_source"] = "verified_database"
        return result

===========================================================================
 QUICK REFERENCE TABLE
===========================================================================

    +--------------------+-----------------------------------------------+
    | PRETOOLUSE         | POSTTOOLUSE                                  |
    +--------------------+-----------------------------------------------+
    | Runs BEFORE        | Runs AFTER                                   |
    | Can BLOCK          | CANNOT BLOCK                                 |
    | Can MODIFY params  | Can TRANSFORM result                         |
    | Can REDIRECT       | Can ADD metadata                             |
    | Use for: Security  | Use for: Normalization                       |
    | Use for: Compliance| Use for: Format conversion                   |
    | Use for: Validation| Use for: Adding context                      |
    +--------------------+-----------------------------------------------+

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


def demonstrate_pretooluse():
    """
    PreToolUse - runs BEFORE tool execution.
    """
    print("\n" + "=" * 70)
    print("PRETOOLUSE HOOK - BEFORE Tool Execution")
    print("=" * 70)

    print("""
    +======================================================================+
    ||                                                                  ||
    ||  PRETOOLUSE TIMELINE:                                             ||
    ||                                                                  ||
    ||  Model decides to call tool                                      ||
    ||       |                                                          ||
    ||       v                                                          ||
    ||  +------------------------+                                      ||
    ||  |     PRETOOLUSE         | <-- HOOK RUNS HERE                   ||
    ||  |       HOOK             |                                      ||
    ||  |                        |                                      ||
    ||  |  * Check policy        |                                      ||
    ||  |  * Validate input      |                                      ||
    ||  |  * BLOCK if bad        |                                      ||
    ||  |  * MODIFY params       |                                      ||
    ||  |  * REDIRECT call       |                                      ||
    ||  +-----------+------------+                                      ||
    ||              |                                                   ||
    ||       +------+------+                                              ||
    ||       |             |                                             ||
    ||       v             v                                              ||
    ||  +----------+ +-----------+ +-------------+                      ||
    ||  | ALLOWED  | |  BLOCKED  | | REDIRECTED  |                      ||
    ||  | Execute  | | Don't run | | To another  |                      ||
    ||  | tool     | | tool      | | tool        |                      ||
    ||  +----------+ +-----------+ +-------------+                      ||
    ||                                                                  ||
    +======================================================================+

    USE CASES FOR PRETOOLUSE:
        - Policy enforcement (refunds, transfers, payments)
        - Prerequisite checking (identity verification, AML checks)
        - Input validation (amount limits, format checks)
        - Blocking unauthorized actions (security compliance)

    """)


def demonstrate_posttooluse():
    """
    PostToolUse - runs AFTER tool execution.
    """
    print("\n" + "=" * 70)
    print("POSTTOOLUSE HOOK - AFTER Tool Execution")
    print("=" * 70)

    print("""
    +======================================================================+
    ||                                                                  ||
    ||  POSTTOOLUSE TIMELINE:                                            ||
    ||                                                                  ||
    ||  Tool executes                                                     ||
    ||       |                                                          ||
    ||       v                                                          ||
    ||  +------------------------+                                      ||
    ||  |    POSTTOOLUSE         | <-- HOOK RUNS HERE                   ||
    ||  |       HOOK             |                                      ||
    ||  |                        |                                      ||
    ||  |  * Transform data      |                                      ||
    ||  |  * Normalize format    |                                      ||
    ||  |  * Add metadata        |                                      ||
    ||  |  * Strip sensitive     |                                      ||
    ||  +-----------+------------+                                      ||
    ||              |                                                   ||
    ||              v                                                   ||
    ||  Model processes result (gets transformed data)                  ||
    ||                                                                  ||
    +======================================================================+

    USE CASES FOR POSTTOOLUSE:
        - Data normalization (timestamps to dates, codes to strings)
        - Format conversion (DD/MM/YYYY to ISO)
        - Adding context (metadata, timestamps, source info)
        - Result transformation (consistent output structure)

    WARNING: Cannot block actions! Tool already executed!

    """)


def show_key_distinction():
    """
    The critical distinction between hooks.
    """
    print("\n" + "=" * 70)
    print("CRITICAL DISTINCTION")
    print("=" * 70)

    print("""
    +======================================================================+
    ||                                                                  ||
    ||  PRETOOLUSE: "Should this action happen?"                        ||
    ||                                                                  ||
    ||  --> Decision made BEFORE execution                              ||
    ||  --> Can PREVENT the action from happening                       ||
    ||  --> Use for: enforcement, blocking, prerequisites               ||
    ||                                                                  ||
    ||  ----------------------------------------------------------------  ||
    ||                                                                  ||
    ||  POSTTOOLUSE: "How should I present this result?"                ||
    ||                                                                  ||
    ||  --> Action ALREADY happened                                     ||
    ||  --> Cannot undo the action                                      ||
    ||  --> Use for: transformation, normalization                     ||
    ||                                                                  ||
    +======================================================================+

    +======================================================================+
    ||                                                                  ||
    ||  *** EXAM WARNING ***                                             ||
    ||                                                                  ||
    ||  Never use PostToolUse to block actions!                          ||
    ||  The non-compliant behavior has ALREADY occurred!                ||
    ||  By the time PostToolUse runs, it is too late to prevent.         ||
    ||                                                                  ||
    +======================================================================+
    """)


def show_decision_framework():
    """
    When to use hooks vs prompts.
    """
    print("\n" + "=" * 70)
    print("HOOK VS PROMPT DECISION FRAMEWORK")
    print("=" * 70)

    print("""
    +=====================+=============================================+
    |      USE HOOKS      |         USE PROMPTS                         |
    +=====================+=============================================+
    |                     |                                             |
    |  100% guarantee     |  ~90-95% compliance acceptable             |
    |  required           |                                             |
    |                     |                                             |
    |  Single failure     |  Minor consequences for failure            |
    |  = financial loss    |                                             |
    |  or legal risk       |                                             |
    |                     |                                             |
    |  Examples:          |  Examples:                                  |
    |  * Refunds          |  * Formatting preferences                   |
    |  * Transfers        |  * Response tone                            |
    |  * Identity verif   |  * Content structure                       |
    |  * AML checks       |  * Style guidelines                        |
    |                     |                                             |
    +=====================+=============================================+

    DECISION RULE:
        Ask yourself: "What happens if this fails?"

        If failure = financial loss or legal risk --> HOOKS
        If failure = minor inconvenience --> PROMPTS

    """)


def show_concrete_examples():
    """
    Concrete examples of when to use each hook.
    """
    print("\n" + "=" * 70)
    print("CONCRETE EXAMPLES")
    print("=" * 70)

    print("""
    EXAMPLE 1: Refund Processing
    ---------------------------------------------------------------------

    PRETOOLUSE on process_refund:
        if amount > 1000:
            block()  # Don't execute
            return "Refunds over $1000 require manager approval"

    POSTTOOLUSE on process_refund:
        # TOO LATE! Refund already processed!
        # Cannot undo a refund that already happened!
        # Use PostToolUse for LOGGING, not blocking


    EXAMPLE 2: Data from Multiple Tools
    ---------------------------------------------------------------------

    Tool A returns: {"date": 1704067200}        # Unix timestamp
    Tool B returns: {"date": "12/31/2024"}     # DD/MM/YYYY
    Tool C returns: {"date": "2024-12-31"}     # ISO format

    POSTTOOLUSE normalizes all to ISO:
        Tool A: 1704067200 --> "2024-01-01"
        Tool B: "12/31/2024" --> "2024-12-31"
        Tool C: Already correct, no change

    Model sees consistent date format regardless of source!


    EXAMPLE 3: AML Compliance Check
    ---------------------------------------------------------------------

    PRETOOLUSE on transfer_funds:
        if not session.amlCheckPassed:
            block()  # Don't execute
            return "AML verification required before transfer"

    # AML check must happen BEFORE transfer
    # PostToolUse would be useless - money already moved!

    """)


if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    print("\n" + "=" * 70)
    print("PRACTICE 1: TWO HOOK TYPES - PreToolUse vs PostToolUse")
    print("=" * 70)
    print("""
    This program teaches the two types of SDK hooks:
        PreToolUse: Runs BEFORE tool execution (can block)
        PostToolUse: Runs AFTER tool execution (can transform)
    """)

    demonstrate_pretooluse()
    demonstrate_posttooluse()
    show_key_distinction()
    show_decision_framework()
    show_concrete_examples()

    print("""
    +======================================================================+
    ||                                                                  ||
    ||              WHAT WE HAVE LEARNT                                 ||
    ||              =====================                                 ||
    ||                                                                  ||
    +======================================================================+

    1. PRETOOLUSE HOOKS:
       - Run BEFORE tool execution
       - Can BLOCK, MODIFY, or REDIRECT tool calls
       - Use for: policy enforcement, prerequisites, validation
       - Cannot transform data (no result yet)

    2. POSTTOOLUSE HOOKS:
       - Run AFTER tool execution
       - Can TRANSFORM or NORMALIZE data
       - Use for: data formatting, adding metadata
       - CANNOT block (action already happened!)

    3. THE CRITICAL DISTINCTION:
       - PreToolUse = prevent action (BEFORE)
       - PostToolUse = transform result (AFTER)
       - NEVER use PostToolUse to block - it is too late!

    4. THE DECISION FRAMEWORK:
       - Financial/legal risk --> Use hooks (100% guarantee)
       - Minor preferences --> Use prompts (acceptable failure)

    5. COMMON MISTAKES:
       - Using PostToolUse to block (WRONG - action already happened!)
       - Using PreToolUse to transform data (WRONG - no data yet!)
       - Thinking prompts are enough for financial ops (WRONG - use hooks!)

    ============================================================================
    EXAM TIPS:
    ============================================================================

    * PreToolUse can block actions, PostToolUse cannot
    * PostToolUse transforms data AFTER execution
    * If failure = financial loss --> hooks required
    * "PostToolUse to block" = WRONG ANSWER on exam!
    * Think of PreToolUse as airport security (can stop you)
    * Think of PostToolUse as baggage claim (already on plane)

    +======================================================================+
    ||                                                                  ||
    ||                    PROGRAM COMPLETE!                             ||
    ||                                                                  ||
    +======================================================================+
    """)

