"""
+===========================================================================+
|                                                                           |
|  PRACTICE 4: DECISION FRAMEWORK - WHEN TO USE HOOKS VS PROMPTS          |
|                                                                           |
|  The key decision rule for the certification exam:                       |
|                                                                           |
|    If single failure = financial loss or legal risk --> USE HOOKS       |
|    If failure = minor inconvenience --> USE PROMPTS                       |
|                                                                           |
|  Examples and decision matrix for each scenario.                         |
|                                                                           |
+===========================================================================

===========================================================================
 VISUAL: THE DECISION MATRIX
===========================================================================

    +======================================================================+
    ||                                                                  ||
    ||  YOUR REQUIREMENT:                                               ||
    ||                                                                  ||
    ||  +-----------------------+                                       ||
    ||  | What happens if       |                                       ||
    ||  | this fails?           |                                       ||
    ||  +-----------------------+                                       ||
    ||            |                                                  ||
    ||            v                                                  ||
    ||    +------+------+---+                                          ||
    ||    |             |    |                                          ||
    ||    v             v    v                                          ||
    || FINANCIAL   LEGAL/SECURITY  MINOR                               ||
    || LOSS             RISK      INCONVENIENCE                        ||
    ||    |             |    |                                          ||
    ||    v             v    v                                          ||
    || +-------+   +---------+  +--------+                              ||
    || | HOOKS |   |  HOOKS  |  | PROMPTS|                              ||
    || |(100%) |   | (100%) |  | (~90%)  |                              ||
    || +-------+   +---------+  +--------+                              ||
    ||                                                                  ||
    +======================================================================+

===========================================================================
 REAL-TIME SCENARIO: When This Concept Breaks Things
===========================================================================

    SCENARIO: Payment Processing System

    A company implements an AI agent to handle payment processing.
    They use prompts to enforce policy.

    +======================================================================+
    ||                                                                  ||
    ||  THE WRONG APPROACH: Using prompts for payments                   ||
    ||  ----------------------------------------------------------------  ||
    ||                                                                  ||
    ||  Prompt: "Never process payments over $10,000 without             ||
    ||           manager approval."                                     ||
    ||                                                                  ||
    ||  System processes 10,000 payments in a month.                    ||
    ||  Prompt compliance rate: ~95%                                    ||
    ||                                                                  ||
    ||  Result:                                                           ||
    ||  - 500 payments processed without approval                       ||
    ||  - $5 million in unapproved transactions                         ||
    ||  - Regulatory violation (PCI-DSS)                                ||
    ||  - Company fined $2 million                                      ||
    ||  - CEO and CTO fired                                            ||
    ||                                                                  ||
    +======================================================================+

    +======================================================================+
    ||                                                                  ||
    ||  THE CORRECT APPROACH: Using hooks for payments                   ||
    ||  ----------------------------------------------------------------  ||
    ||                                                                  ||
    ||  PreToolUse on process_payment:                                   ||
    ||      if amount > 10000 and not managerApproved:                  ||
    ||          block()  <-- 100% enforcement, no bypass possible     ||
    ||                                                                  ||
    ||  System processes 10,000 payments in a month.                    ||
    ||  Hook enforcement rate: 100%                                     ||
    ||                                                                  ||
    ||  Result:                                                           ||
    ||  - 10,000 payments processed correctly                          ||
    ||  - All over-limit payments blocked and escalated                ||
    ||  - Zero regulatory violations                                    ||
    ||  - Company protected!                                            ||
    ||                                                                  ||
    +======================================================================+

===========================================================================
 VISUAL: GUARANTEE COMPARISON
===========================================================================

    +======================================================================+
    ||                                                                  ||
    ||  PROMPTS: ~90-95% success rate                                   ||
    ||  =============================                                   ||
    ||                                                                  ||
    ||  * Instructions in system prompt                                 ||
    ||  * Language model may not follow perfectly                      ||
    ||  * Adversarial prompts can bypass                               ||
    ||  * Complex scenarios may confuse                               ||
    ||                                                                  ||
    ||  For 1000 operations at 95%:                                     ||
    ||    50 failures --> May be unacceptable for financial/security    ||
    ||                                                                  ||
    +======================================================================+

    +======================================================================+
    ||                                                                  ||
    ||  HOOKS: 100% success rate                                         ||
    ||  =========================                                       ||
    ||                                                                  ||
    ||  * Code runs before/after execution                             ||
    ||  * Cannot be bypassed by prompts                                ||
    ||  * Deterministic execution                                      ||
    ||  * Works even with adversarial input                            ||
    ||                                                                  ||
    ||  For 1000 operations at 100%:                                    ||
    ||    0 failures --> Guaranteed compliance                          ||
    ||                                                                  ||
    +======================================================================+

===========================================================================
 MISTAKES DEVELOPERS MAKE
===========================================================================

    MISTAKE #1: Using prompts for financial operations
    -----------------------------------------------------------------------
    "We'll just use a prompt saying 'always verify identity first'"
    -----------------------------------------------------------------------
    WHY IT BREAKS: Prompts are ~95% reliable. 5% failure on identity
    verification = account takeover risk.
    FIX: Use PreToolUse for 100% identity verification.

    MISTAKE #2: Adding more examples to improve prompt reliability
    -----------------------------------------------------------------------
    Prompt: "Here are 100 examples of correct refund processing..."
    -----------------------------------------------------------------------
    WHY IT BREAKS: More examples don't fix the fundamental limitation.
    Prompts will still fail ~5% of the time. You need deterministic
    enforcement for critical operations.
    FIX: Use hooks for anything that MUST work 100%.

    MISTAKE #3: Using routing classifiers for workflow enforcement
    -----------------------------------------------------------------------
    "We'll use an LLM router to decide which agent handles the request"
    -----------------------------------------------------------------------
    WHY IT BREAKS: Routing classifiers handle ROUTING (which agent?).
    They do NOT handle workflow enforcement (correct order?).
    A router might send to the wrong agent, or skip verification.
    FIX: Use PreToolUse hooks for workflow enforcement.

    MISTAKE #4: Thinking "hooks are overkill for this simple task"
    -----------------------------------------------------------------------
    "It's just a password change, prompts are fine"
    -----------------------------------------------------------------------
    WHY IT BREAKS: Password change without proper verification =
    account takeover. Even "simple" operations can have serious
    consequences if they fail.
    FIX: Think about worst case, not typical case.

    MISTAKE #5: Confusing PostToolUse with PreToolUse for blocking
    -----------------------------------------------------------------------
    "We added a PostToolUse hook to block unauthorized transfers"
    -----------------------------------------------------------------------
    WHY IT BREAKS: PostToolUse runs AFTER execution. The transfer
    already happened! You can't block after the fact.
    FIX: Use PreToolUse to block BEFORE execution.

===========================================================================
 INTERVIEW Q&A: Expert Answer Frameworks
===========================================================================

    Q1: "When should I use hooks vs prompts?"
    ----------------------------------------------------------------
    TEMPLATE:
    "Use this decision framework:

    1. What happens if this fails?
       - Financial loss? Legal/regulatory risk? Security breach?
         --> Use HOOKS (deterministic, 100%)
       - Minor inconvenience? Stylistic preference?
         --> Use PROMPTS (~90-95% acceptable)

    2. Is single failure acceptable?
       - NO for financial/security/compliance
         --> Use HOOKS
       - YES for low-stakes preferences
         --> Use PROMPTS

    The rule of thumb: If you can't afford 5% failure rate,
    use hooks. If minor failures are acceptable, prompts are fine."

    KEY PHRASE: "What happens if this fails?" - the answer determines
    whether you need 100% guarantee (hooks) or ~90% is OK (prompts)

    ----------------------------------------------------------------

    Q2: "Can't I just use better prompts to get 100% compliance?"
    ----------------------------------------------------------------
    TEMPLATE:
    "No. Prompts have a fundamental limitation - they're instructions
    to a language model, which operates probabilistically.

    Even with:
    - Perfect instructions
    - Many examples
    - Careful tuning

    The model will still occasionally deviate from instructions,
    especially:
    - In complex scenarios
    - With adversarial inputs
    - When instructions conflict

    Hooks run at the code execution level - they execute deterministically
    every time. There's no probabilistic element.

    For financial/legal/security requirements, this difference is
    critical. You need 100%, not 95%."

    TRAP ANSWER TO AVOID: "Yes, use more examples and better instructions"
    - This does not provide 100% guarantee!

    ----------------------------------------------------------------

    Q3: "What's the difference between hooks and routing classifiers?"
    ----------------------------------------------------------------
    TEMPLATE:
    "Routing classifiers decide WHICH agent or workflow handles a request.
    Hooks enforce rules WITHIN a workflow.

    Example:
    - Routing: "Customer complaint --> complaints agent"
    - Hook: "Process refund --> check if customer verified"

    A routing classifier might route to the right agent but still
    allow violations within that agent's execution.

    Hooks work at the tool execution level:
    - PreToolUse: Before tool runs
    - PostToolUse: After tool runs

    Use routing for "which path?" and hooks for "is this allowed?"

    KEY PHRASE: "Routing classifiers = which path. Hooks = is allowed."

    ----------------------------------------------------------------

    Q4: "What if my system has both hooks and prompts?"
    ----------------------------------------------------------------
    TEMPLATE:
    "That's the correct architecture for most systems:

    HOOKS (100% guarantee) for:
    - Financial operations
    - Security checks
    - Compliance requirements
    - Workflow enforcement

    PROMPTS (~90% OK) for:
    - Response tone and style
    - Formatting preferences
    - Content structure
    - Non-critical guidelines

    Think of it as defense in depth:
    - Hooks provide hard blocks for critical operations
    - Prompts guide general behavior

    This gives you deterministic enforcement where required,
    while keeping flexibility where it's acceptable."

===========================================================================
 VISUAL: DECISION FRAMEWORK FLOWCHART
===========================================================================

    +======================================================================+
    ||                                                                  ||
    ||                        START                                      ||
    ||                          |                                        ||
    ||                          v                                        ||
    ||           +----------------------------------+                   ||
    ||           | Is this financial, legal, or     |                   ||
    ||           | security related?                |                   ||
    ||           +----------------------------------+                   ||
    ||                    /              \                                ||
    ||                   /                \                               ||
    ||                  v                  v                              ||
    ||                YES                 NO                             ||
    ||                 |                    |                             ||
    ||                 v                    v                             ||
    ||      +------------------+    Is failure a minor                   ||
    ||      |   USE HOOKS     |    inconvenience?                       ||
    ||      |   (100% must    |          |                              ||
    ||      |    work!)      |          v                              ||
    ||      +------------------+   +-----------+                        ||
    ||                          |   NO           YES                     ||
    ||                          |     |              |                   ||
    ||                          |     v              v                   ||
    ||                          | +-----------+  +----------+           ||
    ||                          | |   USE     |  |  USE     |           ||
    ||                          | |   HOOKS   |  |  PROMPTS |           ||
    ||                          | | (Medium   |  | (~90% ok)|           ||
    ||                          | |  risk)    |  +----------+           ||
    ||                          | +-----------+                            ||
    ||                          +----------------------------------------+||
    +======================================================================+

===========================================================================
 DECISION TABLE: COMMON SCENARIOS
===========================================================================

    +======================+===================+===========================+
    | SCENARIO             | RISK LEVEL       | MECHANISM                |
    +======================+===================+===========================+
    | Refunds over $1000   | HIGH - Financial | PRETOOLUSE               |
    +----------------------+-------------------+---------------------------+
    | Wire transfers       | HIGH - AML reg   | PRETOOLUSE               |
    +----------------------+-------------------+---------------------------+
    | Password changes     | HIGH - Security  | PRETOOLUSE               |
    +----------------------+-------------------+---------------------------+
    | Identity verification | HIGH - Security  | PRETOOLUSE               |
    +----------------------+-------------------+---------------------------+
    | KYC/AML checks       | HIGH - Legal     | PRETOOLUSE               |
    +----------------------+-------------------+---------------------------+
    | Data normalization   | LOW - Formatting | POSTTOOLUSE              |
    +----------------------+-------------------+---------------------------+
    | Adding metadata      | LOW - Convenient | POSTTOOLUSE              |
    +----------------------+-------------------+---------------------------+
    | Response tone        | LOW - UX         | PROMPTS                  |
    +----------------------+-------------------+---------------------------+
    | Formatting style     | LOW - Display    | PROMPTS                  |
    +----------------------+-------------------+---------------------------+
    | Greeting conventions | LOW - UX         | PROMPTS                  |
    +----------------------+-------------------+---------------------------+

===========================================================================
 WHAT WE HAVE LEARNT SUMMARY
===========================================================================

    +======================================================================+
    ||                                                                  ||
    ||              WHAT WE HAVE LEARNT                                 ||
    ||              =====================                                 ||
    ||                                                                  ||
    +======================================================================+

    1. THE DECISION FRAMEWORK:
       - Financial, Security, Compliance --> HOOKS (100%)
       - Formatting, Style, Tone --> PROMPTS (~90%)

    2. WHY HOOKS FOR CRITICAL OPS:
       - Prompts are ~90-95% reliable
       - 5% failure rate = unacceptable for financial/legal/security
       - Hooks provide 100% deterministic enforcement

    3. WHY PROMPTS FOR NON-CRITICAL:
       - Minor failures are acceptable
       - Prompts are flexible and easier to update
       - Don't need 100% guarantee for style preferences

    4. EXAM TRAPS TO AVOID:
       - "Prompts for financial ops" = WRONG
       - "Few-shot for security" = WRONG
       - "PostToolUse to block" = WRONG
       - "Routing classifiers for enforcement" = WRONG

    5. THE QUESTION TEMPLATE:
       - What happens if it fails?
       - Is failure financial/legal/security?
       - Is single failure acceptable?

    6. THE GUARANTEE COMPARISON:
       - Hooks = 100% (deterministic)
       - Prompts = ~90-95% (probabilistic)

    ============================================================================
    EXAM TIPS:
    ============================================================================

    * Financial operations --> PreToolUse (not prompts!)
    * PostToolUse transforms, doesn't block
    * Routing classifiers = which path, not is allowed
    * Hooks for when failure = unacceptable
    * "What happens if this fails?" - answer determines choice

    +======================================================================+
    ||                                                                  ||
    ||                    PROGRAM COMPLETE!                             ||
    ||                                                                  ||
    +======================================================================+
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


def show_decision_matrix():
    """
    Show the complete decision matrix.
    """
    print("\n" + "=" * 70)
    print("DECISION MATRIX: HOOKS VS PROMPTS")
    print("=" * 70)

    print("""
    +=====================+=============================================+
    |                     |                                             |
    |    REQUIREMENT      |         USE THIS                           |
    |                     |                                             |
    +=====================+=============================================+
    |                     |                                             |
    |  Refunds            |  PRETOOLUSE - 100% guarantee                |
    |  Transfers          |  Required: financial loss risk              |
    |  Payments           |  Prompt cannot prevent fraud               |
    |                     |                                             |
    +---------------------+----------------------------------------------+
    |                     |                                             |
    |  Identity verification| PRETOOLUSE - 100% guarantee               |
    |  Access control     |  Required: security breach risk             |
    |  Password changes   |  Prompt cannot prevent impersonation        |
    |                     |                                             |
    +---------------------+----------------------------------------------+
    |                     |                                             |
    |  AML checks         |  PRETOOLUSE - 100% guarantee               |
    |  KYC verification   |  Required: legal/regulatory risk            |
    |  Sanctions screening|  Prompt cannot ensure compliance           |
    |                     |                                             |
    +---------------------+----------------------------------------------+
    |                     |                                             |
    |  Data normalization |  POSTTOOLUSE - always transform              |
    |  Format conversion  |  Always: inconsistent sources                |
    |  Adding metadata    |  Required: model needs consistent format    |
    |                     |                                             |
    +---------------------+----------------------------------------------+
    |                     |                                             |
    |  Response tone      |  PROMPTS - acceptable failure              |
    |  Formatting style   |  OK: minor inconsistency                     |
    |  Content structure |  OK: easy to fix later                      |
    |                     |                                             |
    +---------------------+----------------------------------------------+
    |                     |                                             |
    |  Greeting style     |  PROMPTS - acceptable failure              |
    |  Closing conventions| OK: minor UX issue                         |
    |  Language preferences| OK: easy to adjust                         |
    |                     |                                             |
    +---------------------+----------------------------------------------+

    REMEMBER:
        Hooks = Deterministic (100% guarantee)
        Prompts = Probabilistic (~90-95% compliance)
    """)


def show_scenario_analysis():
    """
    Analyze specific scenarios and decide which mechanism to use.
    """
    print("\n" + "=" * 70)
    print("SCENARIO ANALYSIS")
    print("=" * 70)

    scenarios = [
        {
            "scenario": "Customer requests $10,000 refund",
            "risk": "HIGH - $10,000 financial loss",
            "mechanism": "PRETOOLUSE",
            "reason": "Single failure = $10,000 loss. Cannot risk prompt failure."
        },
        {
            "scenario": "User wants to change account password",
            "risk": "HIGH - Account takeover risk",
            "mechanism": "PRETOOLUSE",
            "reason": "Single failure = security breach. Must verify identity."
        },
        {
            "scenario": "Transfer to foreign bank account",
            "risk": "HIGH - AML regulatory requirement",
            "mechanism": "PRETOOLUSE",
            "reason": "Legal requirement. Cannot transfer without AML check."
        },
        {
            "scenario": "Format price as $X.XX",
            "risk": "LOW - Minor display issue",
            "mechanism": "PROMPT",
            "reason": "If wrong, minor formatting issue. Easy to fix."
        },
        {
            "scenario": "Use professional tone in response",
            "risk": "LOW - Minor UX issue",
            "mechanism": "PROMPT",
            "reason": "If too casual, minor issue. Not a security or financial risk."
        },
        {
            "scenario": "Response should be in user's language",
            "risk": "LOW - Minor communication issue",
            "mechanism": "PROMPT",
            "reason": "If wrong language, easy to fix. Not critical."
        }
    ]

    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'=' * 60}")
        print(f"SCENARIO {i}: {scenario['scenario']}")
        print(f"{'=' * 60}")
        print(f"   Risk: {scenario['risk']}")
        print(f"   Mechanism: {scenario['mechanism']}")
        print(f"   Reason: {scenario['reason']}")


def show_exam_traps():
    """
    Show common exam traps and why they're wrong.
    """
    print("\n" + "=" * 70)
    print("EXAM TRAPS TO AVOID")
    print("=" * 70)

    print("""
    +======================================================================+
    ||                                                                  ||
    ||  TRAP 1: "Use prompts for financial operations"                 ||
    ||                                                                  ||
    ||  WRONG! Financial ops have legal/financial risk.                 ||
    ||  Prompt ~95% success = 5% failure = unacceptable loss.          ||
    ||  Must use PRETOOLUSE for 100% guarantee.                         ||
    +======================================================================+

    +======================================================================+
    ||                                                                  ||
    ||  TRAP 2: "Add few-shot examples for security ops"                ||
    ||                                                                  ||
    ||  WRONG! Examples work ~90%, not 100%.                           ||
    ||  Security breach = catastrophic. Must use hooks.                ||
    ||  Prompts are NOT sufficient for security operations.             ||
    +======================================================================+

    +======================================================================+
    ||                                                                  ||
    ||  TRAP 3: "Use PostToolUse to block actions"                      ||
    ||                                                                  ||
    ||  WRONG! PostToolUse runs AFTER execution.                        ||
    ||  By the time it runs, the action has already happened!          ||
    ||  Cannot block with PostToolUse - action already occurred.        ||
    ||  Use PreToolUse to block BEFORE execution.                       ||
    +======================================================================+

    +======================================================================+
    ||                                                                  ||
    ||  TRAP 4: "Use routing classifiers for workflow enforcement"      ||
    ||                                                                  ||
    ||  WRONG! Routing classifiers handle ROUTING (which agent?).      ||
    ||  They do NOT handle workflow enforcement (correct order?).      ||
    ||  For workflow enforcement, use PreToolUse hooks.                 ||
    +======================================================================+
    """)


def show_question_template():
    """
    Show the question template for making decisions.
    """
    print("\n" + "=" * 70)
    print("DECISION QUESTION TEMPLATE")
    print("=" * 70)

    print("""
    When deciding between hooks and prompts, ask:

    +======================================================================+
    ||                                                                  ||
    ||  1. What happens if this fails?                                 ||
    ||                                                                  ||
    ||  2. Is the failure cost:                                       ||
    ||     * Financial loss?      --> HOOKS (100% guarantee)            ||
    ||     * Legal/regulatory?     --> HOOKS (100% guarantee)          ||
    ||     * Security breach?      --> HOOKS (100% guarantee)          ||
    ||     * Minor inconvenience? --> PROMPTS (90-95% OK)              ||
    ||                                                                  ||
    ||  3. Is single failure acceptable?                               ||
    ||     * NO (high stakes)     --> HOOKS                             ||
    ||     * YES (low stakes)    --> PROMPTS                            ||
    ||                                                                  ||
    +======================================================================+

    Example question: "Should refunds use hooks or prompts?"

        1. What happens if it fails? --> $500 goes to wrong person
        2. Financial loss? --> YES
        3. Single failure acceptable? --> NO
        4. Answer: PRETOOLUSE (required for financial operations)
    """)


def show_guarantee_comparison():
    """
    Compare the guarantee levels.
    """
    print("\n" + "=" * 70)
    print("GUARANTEE COMPARISON")
    print("=" * 70)

    print("""
    +======================================================================+
    ||                                                                  ||
    ||  PROMPTS: ~90-95% success rate                                   ||
    ||                                                                  ||
    ||  * Instructions in system prompt                                 ||
    ||  * Language model may not follow perfectly                      ||
    ||  * Adversarial prompts can bypass                              ||
    ||  * Complex scenarios may confuse                               ||
    ||                                                                  ||
    ||  For 1000 operations at 95%:                                   ||
    ||    50 failures --> May be unacceptable for financial/security    ||
    +======================================================================+

    +======================================================================+
    ||                                                                  ||
    ||  HOOKS: 100% success rate                                        ||
    ||                                                                  ||
    ||  * Code runs before/after execution                             ||
    ||  * Cannot be bypassed by prompts                                ||
    ||  * Deterministic execution                                      ||
    ||  * Works even with adversarial input                            ||
    ||                                                                  ||
    ||  For 1000 operations at 100%:                                   ||
    ||    0 failures --> Guaranteed compliance                          ||
    +======================================================================+

    When failure is NOT acceptable:
        --> Use HOOKS (deterministic, 100%)

    When minor failures are acceptable:
        --> Use PROMPTS (probabilistic, ~90-95%)
    """)


if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    print("\n" + "=" * 70)
    print("PRACTICE 4: DECISION FRAMEWORK - HOOKS VS PROMPTS")
    print("=" * 70)
    print("""
    This program teaches when to use hooks vs prompts for the exam.
    Key decision: If failure = financial loss or legal risk --> use HOOKS.
    """)

    show_decision_matrix()
    show_scenario_analysis()
    show_exam_traps()
    show_question_template()
    show_guarantee_comparison()

    print("""
    +======================================================================+
    ||                                                                  ||
    ||              WHAT WE HAVE LEARNT                                 ||
    ||              =====================                                 ||
    ||                                                                  ||
    +======================================================================+

    1. We learned the DECISION MATRIX:
       - Financial, Security, Compliance --> HOOKS (100%)
       - Formatting, Style, Tone --> PROMPTS (~90%)

    2. We analyzed SCENARIOS:
       - High risk (refunds, identity) --> PreToolUse
       - Low risk (formatting, tone) --> Prompts

    3. We learned EXAM TRAPS:
       - "Prompts for financial ops" = WRONG
       - "Few-shot for security" = WRONG
       - "PostToolUse to block" = WRONG
       - "Routing classifiers for enforcement" = WRONG

    4. We learned the QUESTION TEMPLATE:
       - What happens if it fails?
       - Is failure financial/legal/security?
       - Is single failure acceptable?

    5. We compared GUARANTEES:
       - Hooks = 100% (deterministic)
       - Prompts = ~90-95% (probabilistic)

    ============================================================================
    EXAM TIPS:
    ============================================================================

    * Financial operations --> PreToolUse (not prompts!)
    * PostToolUse transforms, doesn't block
    * Routing classifiers = which path, not is allowed
    * Hooks for when failure = unacceptable

    +======================================================================+
    ||                                                                  ||
    ||                    PROGRAM COMPLETE!                             ||
    ||                                                                  ||
    +======================================================================+
    """)