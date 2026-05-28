"""
================================================================================
PRACTICE 3: SUBAGENT LIFECYCLE HOOKS
================================================================================

Agent SDK provides lifecycle events for subagent management:

    SubagentStart - fires when a subagent spawns
    SubagentStop  - fires when a subagent finishes

These hooks enable enforcement, logging, and validation.
================================================================================

REAL-TIME SCENARIO - OBSERVABILITY FAILURE:
------------------------------------------
A multi-agent system had 12 subagents processing customer requests.
No lifecycle hooks were implemented - no one knew:
- Which subagents were running
- How long each took
- What outputs were produced

Outage: One subagent entered infinite loop, consumed all resources.
Problem: No SubagentStart/SubagentStop hooks to detect anomalies.
Fix: Implemented hooks that logged duration and killed slow agents.

MISTAKE: Not implementing lifecycle hooks for observability!
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
# HOOK IMPLEMENTATIONS
# ================================================================================

class HookLogger:
    """Simple logger to track hook invocations."""

    def __init__(self):
        self.events = []

    def log(self, hook_name: str, data: dict):
        self.events.append({
            "hook": hook_name,
            "data": data
        })
        print(f"\n   [HOOK] {hook_name}")
        print(f"   [HOOK] Data: {data}")


logger = HookLogger()


def subagent_start_hook(subagent_id: str, agent_type: str, context: dict):
    """
    SubagentStart Hook - fires when a subagent spawns.

    Use cases:
    - Enforce rate limits
    - Log subagent invocations
    - Validate coordinator context passing

    PRODUCTION SCENARIO:
    A billing subagent was spawning without coordinator passing context.
    Hook detected: context is empty, returned False, blocked spawn!
    Caught a bug where coordinator forgot context passing.
    """
    print("\n" + "=" * 60)
    print(f"SUBAGENT START HOOK INVOKED")
    print("=" * 60)

    logger.log("SubagentStart", {
        "subagent_id": subagent_id,
        "agent_type": agent_type,
        "has_context": context is not None,
        "context_keys": list(context.keys()) if context else []
    })

    print("\n   [HOOK] Enforcing rate limits...")
    print("   [HOOK] Validating context passed by coordinator...")
    print("   [HOOK] Logging subagent invocation...")

    # Validation check
    if not context or len(context) == 0:
        print("   [HOOK] *** WARNING: No context passed to subagent! ***")
        print("   [HOOK] Coordinator may have forgotten context passing!")
        return False

    print("   [HOOK] + Validation passed - subagent ready")

    return True


def subagent_stop_hook(subagent_id: str, result: dict):
    """
    SubagentStop Hook - fires when a subagent finishes.

    Use cases:
    - Validate output schemas
    - Strip sensitive data
    - Performance monitoring

    REAL PRODUCTION USE:
    Financial reports were exposing internal cost data to customers.
    SubagentStop hook detected output contains "margin", "cost", "profit"
    fields, stripped them before returning to customer.
    Saved $200K in potential data leaks before compliance caught it.
    """
    print("\n" + "=" * 60)
    print(f"SUBAGENT STOP HOOK INVOKED")
    print("=" * 60)

    logger.log("SubagentStop", {
        "subagent_id": subagent_id,
        "success": result.get("success", False),
        "has_output": "output" in result,
        "duration_ms": result.get("duration_ms", "unknown")
    })

    print("\n   [HOOK] Validating output schema...")
    print("   [HOOK] Checking for sensitive data to strip...")
    print("   [HOOK] Recording performance metrics...")

    # Output validation
    if "output" in result:
        print(f"   [HOOK] + Output received ({len(str(result['output']))} chars)")
    else:
        print("   [HOOK] *** WARNING: No output from subagent! ***")

    return True


# ================================================================================
# VISUAL: LIFECYCLE HOOK TIMELINE
# ================================================================================
#
#   Coordinator                    Hook System                    Subagent
#   ----------                     ----------                    --------
#       |                             |                             |
#       | spawn(subagent_id)          |                             |
#       |---------------------------->|                             |
#       |                             |                             |
#       |                    +-----------------+                    |
#       |                    | SubagentStart   |                    |
#       |                    | - Rate limit    |                    |
#       |                    | - Validate ctx  |                    |
#       |                    | - Log           |                    |
#       |                    +-----------------+                    |
#       |                             |                             |
#       |                             |-------- start() ----------->|
#       |                             |                             |
#       |                             |                    +----------------+
#       |                             |                    | Subagent runs  |
#       |                             |                    | task           |
#       |                             |                    +----------------+
#       |                             |                             |
#       |                             |<------- result -----------|
#       |                             |                             |
#       |                    +-----------------+                    |
#       |                    | SubagentStop    |                    |
#       |                    | - Validate out  |                    |
#       |                    | - Strip data   |                    |
#       |                    | - Monitor perf |                    |
#       |                    +-----------------+                    |
#       |                             |                             |
#       |<-------- result ------------|                             |
#       |                             |                             |
#
#   HOOKS intercept lifecycle events for cross-cutting concerns!
# ================================================================================


def demonstrate_lifecycle_flow():
    """
    Demonstrate the lifecycle hooks in action.
    """
    print("\n" + "=" * 70)
    print("SUBAGENT LIFECYCLE FLOW")
    print("=" * 70)

    print("""
+----------------------------------------------------------------------+
|  TIMELINE: Subagent Invocation                                       |
|                                                                      |
|  Coordinator                                                          |
|  spawns subagent        [ SubagentStart Hook fires ]                 |
|  ---------------------> +--------------------------------+            |
|                          | - Rate limit check            |            |
|                          | - Context validation          |            |
|                          | - Logging                    |            |
|                          +-------------------+------------+            |
|                                          |                           |
|                                          v                           |
|                          +--------------------------------+            |
|                          | Subagent executes task        |            |
|                          +-------------------+------------+            |
|                                          |                           |
|                                          v                           |
|                          [ SubagentStop Hook fires ]                   |
|                          +--------------------------------+            |
|                          | - Output validation           |            |
|                          | - Sensitive data stripping    |            |
|                          | - Performance monitoring      |            |
|                          +-------------------+------------+            |
|                                          |                           |
|  Coordinator <------------------------------------------              |
|  receives result                                                     |
+----------------------------------------------------------------------+

KEY POINT:
Hooks are CROSS-CUTTING CONCERNS:
- They apply to ALL subagents automatically
- You don't modify each subagent's code
- Hooks intercept lifecycle events globally
""")


def demonstrate_subagent_scoped_hooks():
    """
    Show how subagent-scoped hooks work.

    CRITICAL CONCEPT:
    Each subagent defines its OWN hooks in AgentDefinition.
    These hooks ONLY intercept tool calls made by THAT subagent.

    VISUAL:
    -------

    BILLING SUBAGENT (has refund limit hook)
    |
    |-> process_refund called
    |   |-> Hook intercepts, checks amount
    |   |-> If amount > 1000: BLOCK
    |   |-> If amount <= 1000: ALLOW
    |
    +-> TECHNICAL SUPPORT SUBAGENT (no refund limit hook)
        |
        |-> process_refund called
            |-> No hook defined
            |-> Refund goes through

    HOOKS ARE SCOPED - one agent's hooks don't affect other agents!
    """
    print("\n" + "=" * 70)
    print("SUBAGENT-SCOPED HOOKS")
    print("=" * 70)

    print("""
+----------------------------------------------------------------------+
|  IMPORTANT: Subagent hooks are SCOPED to that agent!                 |
|                                                                      |
|  Each subagent can have its OWN hooks defined in                    |
|  AgentDefinition frontmatter. These hooks ONLY                       |
|  intercept tool calls made by THAT SPECIFIC subagent.               |
|                                                                      |
|  Example:                                                            |
|                                                                      |
|  +--------------------------------------------------------------+   |
|  | BILLING SUBAGENT                                             |   |
|  |                                                              |   |
|  | PreToolUse hook:                                            |   |
|  |   if amount > 1000: block_refund()                         |   |
|  |   else: allow()                                             |   |
|  |                                                              |   |
|  | Tools called by this subagent --> Hook intercepts them     |   |
|  | Tools called by other agents --> Hook ignores them          |   |
|  +--------------------------------------------------------------+   |
|                                                                      |
|  +--------------------------------------------------------------+   |
|  | TECHNICAL SUPPORT SUBAGENT                                   |   |
|  |                                                              |   |
|  | No refund amount hook defined                               |   |
|  |                                                              |   |
|  | Can process any refund amount (different policy)            |   |
|  +--------------------------------------------------------------+   |
|                                                                      |
|  HOOKS ARE AGENT-SPECIFIC - one agent's hooks don't                  |
|  affect other agents' tool calls!                                    |
+----------------------------------------------------------------------+

EXAM TIP:
When asked "do hooks apply globally or per-agent?", remember:
- LIFECYCLE hooks (SubagentStart/Stop) can be global
- PRE/POST TOOL hooks are SCOPED to the agent that defines them
""")


def demonstrate_auto_conversion():
    """
    Show how stop hooks auto-convert to SubagentStop events.

    INTERVIEW Q&A:
    -------------
    Q: "What's the relationship between post_tool_stop hooks and
        SubagentStop events?"
    A: "In AgentDefinition frontmatter, you define post_tool_stop hooks.
        At runtime, these hooks are AUTOMATICALLY CONVERTED to
        SubagentStop events. Both approaches achieve the same result -
        you can define hooks in frontmatter OR handle them via
        SubagentStop at runtime."
    """
    print("\n" + "=" * 70)
    print("AUTO-CONVERSION: Stop Hooks -> SubagentStop")
    print("=" * 70)

    print("""
+----------------------------------------------------------------------+
|  AgentDefinition frontmatter:                                       |
|                                                                      |
|  ```yaml                                                            |
|  name: billing-agent                                                |
|  description: Handles billing operations                            |
|  tools: [process_refund, get_customer]                             |
|                                                                      |
|  pre_tool_use:                                                      |
|    - hook: validate_billing_prerequisites                          |
|                                                                      |
|  post_tool_stop:     <-- Defined in subagent frontmatter           |
|    - hook: validate_output_schema                                  |
|  ```                                                                |
|                                                                      |
+----------------------------------------------------------------------+

    At RUNTIME:

    post_tool_stop hooks in subagent frontmatter
                    |
                    v
    +-----------------------------------+
    | AUTOMATICALLY CONVERTED to        |
    | SubagentStop events               |
    +-----------------------------------+

    This means:
    - You can define hooks in frontmatter OR
    - You can handle them via SubagentStop at runtime
    Both approaches achieve the same result!
""")


def show_hook_use_cases():
    """
    Summary of when to use each hook.
    """
    print("\n" + "=" * 70)
    print("HOOK USE CASES SUMMARY")
    print("=" * 70)

    print("""
+--------------------+--------------------------------------------------+
|     HOOK           |  USE CASES                                      |
+--------------------+--------------------------------------------------+
|                    |                                                  |
|  SubagentStart     |  * Enforce rate limits                         |
|                    |  * Log subagent invocations                     |
|                    |  * Validate coordinator context passing         |
|                    |  * Pre-flight checks                           |
|                    |  * Block unauthorized spawns                   |
|                    |                                                  |
+--------------------+--------------------------------------------------+
|                    |                                                  |
|  SubagentStop      |  * Validate output schemas                     |
|                    |  * Strip sensitive data                        |
|                    |  * Performance monitoring                      |
|                    |  * Result transformation                        |
|                    |  * Anomaly detection                           |
|                    |                                                  |
+--------------------+--------------------------------------------------+
|                    |                                                  |
|  PreToolUse        |  * Workflow enforcement                        |
|  (subagent-scoped) |  * Prerequisite gate checks                    |
|                    |  * Amount/type restrictions                     |
|                    |  * Security validations                         |
|                    |                                                  |
+--------------------+--------------------------------------------------+
|                    |                                                  |
|  PostToolStop      |  * Output validation                           |
|  (subagent-scoped) |  * Sensitive data stripping                     |
|                    |  * Result transformation                       |
|                    |                                                  |
+--------------------+--------------------------------------------------+
""")


def show_common_mistakes():
    """
    Common errors developers make with lifecycle hooks.
    """
    print("\n" + "=" * 70)
    print("MISTAKES DEVELOPERS MAKE")
    print("=" * 70)

    print("""
MISTAKE 1: Confusing routing with workflow enforcement
------------------------------------------------------
WRONG:
    "I have a routing classifier, so my workflow is enforced."

RIGHT:
    Routing classifier decides WHICH AGENT handles request.
    It does NOT enforce correct sequence of operations.

    You still need PreToolUse hooks for workflow enforcement.


MISTAKE 2: Global hooks when scoped hooks needed
-------------------------------------------------
WRONG:
    Global PreToolUse hook tries to block refunds for billing agent.
    But technical_support agent also gets blocked (wrong!).

RIGHT:
    Define PreToolUse hook ONLY in billing agent's AgentDefinition.
    technical_support agent has no refund hook, can process normally.


MISTAKE 3: Not handling hook failures
-------------------------------------
WRONG:
    def subagent_start_hook(...):
        print("Warning: no context")
        return True  # Always returns True, even on failure!

RIGHT:
    def subagent_start_hook(...):
        if not context:
            return False  # Block the spawn!
        return True


MISTAKE 4: Hooks that modify subagent behavior
-----------------------------------------------
WRONG:
    def subagent_stop_hook(...):
        result["output"] = modify_output(result["output"])
        return result  # Hooks should not modify!

RIGHT:
    Hooks are for CROSS-CUTTING concerns (logging, validation).
    For modifying behavior, use agent logic, not hooks.


MISTAKE 5: Forgetting auto-conversion
-------------------------------------
WRONG:
    "post_tool_stop hooks and SubagentStop are different things."

RIGHT:
    post_tool_stop hooks in frontmatter AUTO-CONVERT to
    SubagentStop events at runtime. They are equivalent!
""")


def show_interview_qa():
    """
    Interview questions and expert answer frameworks.
    """
    print("\n" + "=" * 70)
    print("INTERVIEW Q&A - SUBAGENT LIFECYCLE HOOKS")
    print("=" * 70)

    print("""
Q1: "What's the difference between SubagentStart and PreToolUse hooks?"

A:  "SubagentStart fires when a subagent is SPAWNED, regardless of
    what tool it calls. It's good for:
    - Rate limiting
    - Logging spawn events
    - Validating coordinator context

    PreToolUse fires when a SPECIFIC TOOL is about to execute within
    a subagent. It's scoped to that agent and good for:
    - Prerequisite gate checks
    - Amount restrictions
    - Security validations

    Think of SubagentStart as 'subagent-level' and PreToolUse as
    'tool-level' hooks.


Q2: "Are lifecycle hooks global or per-agent?"

A:  "It depends on the hook type:

    GLOBAL hooks:
    - SubagentStart (can be registered globally)
    - SubagentStop (can be registered globally)

    SCOPED hooks:
    - PreToolUse (defined in AgentDefinition, only applies to
      tools called BY THAT AGENT)
    - PostToolStop (same scope)

    EXAM TIP: PreToolUse/PostToolStop are scoped to the agent
    that defines them. One agent's hooks don't affect other agents.


Q3: "How do post_tool_stop hooks relate to SubagentStop events?"

A:  "They're the same thing! In AgentDefinition frontmatter, you define
    post_tool_stop hooks. At runtime, these are AUTOMATICALLY CONVERTED
    to SubagentStop events.

    You can define hooks either way:
    1. In frontmatter: post_tool_stop: validate_schema
    2. At runtime: handle SubagentStop event

    Both achieve identical behavior.


Q4: "What are cross-cutting concerns and why do hooks matter?"

A:  "Cross-cutting concerns are behaviors that apply across multiple
    parts of the system:

    - Logging: Every subagent should log its actions
    - Validation: Every financial operation should validate
    - Monitoring: Every subagent should report performance

    Without hooks, you'd have to add logging/validation to EACH
    subagent's code. With hooks, you add it ONCE at the lifecycle level.

    Hooks = centralized enforcement for cross-cutting concerns
    = less code duplication = fewer bugs
""")


# ================================================================================
# WHAT WE HAVE LEARNT
# ================================================================================

def show_what_we_learnt():
    """
    Comprehensive summary of all concepts learned.
    """
    print("\n" + "=" * 70)
    print("WHAT WE HAVE LEARNT")
    print("=" * 70)

    print("""
+----------------------------------------------------------------------+
|  LESSON 1: LIFECYCLE HOOKS OVERVIEW                                 |
+----------------------------------------------------------------------+

    SubagentStart:
    - Fires when a subagent spawns
    - Good for: rate limits, logging, context validation
    - Can block unauthorized spawns by returning False

    SubagentStop:
    - Fires when a subagent finishes
    - Good for: output validation, data stripping, monitoring
    - Can detect anomalies in subagent results


+----------------------------------------------------------------------+
|  LESSON 2: HOOK vs SCOPED TOOL HOOKS                               |
+----------------------------------------------------------------------+

    LIFECYCLE HOOKS (can be global):
    - SubagentStart
    - SubagentStop
    - Apply to all subagent events

    TOOL HOOKS (scoped to agent):
    - PreToolUse
    - PostToolStop
    - Only apply to tools called BY THAT SPECIFIC AGENT


+----------------------------------------------------------------------+
|  LESSON 3: AUTO-CONVERSION                                          |
+----------------------------------------------------------------------+

    post_tool_stop hooks in frontmatter
                    |
                    v
    +-----------------------------------+
    | AUTOMATICALLY CONVERTED to        |
    | SubagentStop events at runtime     |
    +-----------------------------------+

    You can use either approach - they're equivalent!


+----------------------------------------------------------------------+
|  LESSON 4: CROSS-CUTTING CONCERNS                                  |
+----------------------------------------------------------------------+

    Cross-cutting concerns:
    - Behaviors that apply across multiple parts of system
    - Examples: logging, validation, monitoring

    Without hooks:
    - Add logging to EACH subagent's code
    - Lots of duplication, lots of bugs

    With hooks:
    - Add logging ONCE at lifecycle level
    - Applies to all subagents automatically
    - Single source of truth


+----------------------------------------------------------------------+
|  LESSON 5: COMMON MISTAKES                                          |
+----------------------------------------------------------------------+

    1. Confusing routing with workflow enforcement
    2. Global hooks when scoped hooks needed
    3. Not handling hook failures (always return True)
    4. Hooks that modify subagent behavior
    5. Forgetting auto-conversion


+----------------------------------------------------------------------+
|  LESSON 6: PRODUCTION USE CASES                                     |
+----------------------------------------------------------------------+

    Real-world hook applications:

    OBSERVABILITY:
    - Log subagent spawn/finish times
    - Detect infinite loops (long-running subagents)
    - Monitor performance metrics

    SECURITY:
    - Validate context passed by coordinator
    - Block unauthorized subagent spawns
    - Strip sensitive data from outputs

    ENFORCEMENT:
    - PreToolUse for prerequisite gates
    - Amount restrictions per agent type
    - Rate limiting on spawns


+----------------------------------------------------------------------+
|  KEY FORMULA FOR CERTIFICATION EXAM                                |
+----------------------------------------------------------------------+

    SUBAGENT LIFECYCLE:
    SubagentStart -> Subagent executes -> SubagentStop

    HOOKS are lifecycle intercept points for cross-cutting concerns.

    SCOPING:
    - Global hooks: apply to all subagents
    - Scoped hooks: apply only to tools called by THAT agent

    AUTO-CONVERSION:
    post_tool_stop in frontmatter = SubagentStop at runtime
+----------------------------------------------------------------------+
""")


if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    print("\n" + "=" * 70)
    print("PRACTICE 3: SUBAGENT LIFECYCLE HOOKS")
    print("=" * 70)
    print("""
This program teaches the Agent SDK lifecycle hooks for subagent management:
    SubagentStart - fires when a subagent spawns
    SubagentStop  - fires when a subagent finishes
""")

    demonstrate_lifecycle_flow()
    demonstrate_subagent_scoped_hooks()
    demonstrate_auto_conversion()
    show_hook_use_cases()
    show_common_mistakes()
    show_interview_qa()
    show_what_we_learnt()

    # Simulate hook invocations
    print("\n" + "-" * 60)
    print("SIMULATED HOOK INVOCATIONS")
    print("-" * 60)

    subagent_start_hook(
        subagent_id="billing-agent-001",
        agent_type="billing",
        context={"customer_id": "123", "task": "process_refund"}
    )

    subagent_stop_hook(
        subagent_id="billing-agent-001",
        result={
            "success": True,
            "output": "Refund processed: $150.00",
            "duration_ms": 245
        }
    )

    print("\n" + "-" * 60)
    print(f"Total hook events logged: {len(logger.events)}")
    print("-" * 60)

    print("""
================================================================================
WHAT JUST HAPPENED?
================================================================================

    1. We learned about SubagentStart hook:
       - Fires when a subagent spawns
       - Use for: rate limits, logging, context validation
       - Can block unauthorized spawns by returning False

    2. We learned about SubagentStop hook:
       - Fires when a subagent finishes
       - Use for: output validation, data stripping, monitoring
       - Can detect anomalies in results

    3. We learned about SUBAGENT-SCOPED hooks:
       - Each subagent defines its OWN hooks
       - Hooks only intercept THAT agent's tool calls
       - Billing agent can have different rules than support agent

    4. We learned about AUTO-CONVERSION:
       - Stop hooks in frontmatter convert to SubagentStop events
       - Both approaches work identically at runtime

    5. We practiced INTERVIEW Q&A:
       - SubagentStart vs PreToolUse differences
       - Global vs scoped hooks
       - Cross-cutting concerns

    KEY INSIGHT:
    Lifecycle hooks enable cross-cutting concerns like logging,
    validation, and enforcement across all subagents without
    modifying each subagent's core logic.
================================================================================
""")
    print("\n" + "=" * 70)
    print("PROGRAM COMPLETE!")
    print("=" * 70)