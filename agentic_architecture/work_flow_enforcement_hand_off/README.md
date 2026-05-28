"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║           WORKFLOW ENFORCEMENT & HANDOFF PATTERNS                          ║
║                                                                              ║
║  How to Ensure Correct Agent Behavior & Safe Escalation                    ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

THE ENFORCEMENT SPECTRUM
═════════════════════════

    Two fundamental approaches to controlling agent behavior:

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   APPROACH 1: Prompt-Based Guidance (~90-95% compliance)              │
    │   ─────────────────────────────────────────────────────                 │
    │                                                                         │
    │   Instructions in system prompt:                                        │
    │   "Always verify customer identity before processing a refund."         │
    │                                                                         │
    │   Works most of the time, but...                                       │
    │   • Probabilistic - model may skip steps                               │
    │   • Vulnerable to adversarial prompts                                  │
    │   • Complex scenarios may confuse the model                           │
    │                                                                         │
    │   Good for: Formatting, style, tone (low-stakes operations)            │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   APPROACH 2: Programmatic Enforcement (100% guaranteed)               │
    │   ─────────────────────────────────────────────────────                 │
    │                                                                         │
    │   Code-level hooks and gates:                                          │
    │   if (!isCustomerVerified(customerId)) {                               │
    │       return { error: "Must verify first" };                         │
    │   }                                                                   │
    │                                                                         │
    │   Works EVERY time because it's code, not a suggestion!                │
    │                                                                         │
    │   Required for: Financial, Security, Compliance operations            │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘


WHEN TO USE PROGRAMMATIC ENFORCEMENT
════════════════════════════════════

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   USE PROGRAMMATIC ENFORCEMENT (100%) when:                           │
    │                                                                         │
    │   FINANCIAL OPERATIONS:                                                │
    │   ✓ Refunds, transfers, payments                                       │
    │   ✓ Account balance changes                                           │
    │   ✓ Subscription cancellations                                        │
    │                                                                         │
    │   SECURITY OPERATIONS:                                                 │
    │   ✓ Identity verification                                             │
    │   ✓ Access control decisions                                          │
    │   ✓ Password/credential operations                                    │
    │                                                                         │
    │   COMPLIANCE OPERATIONS:                                               │
    │   ✓ AML (Anti-Money Laundering) checks                                │
    │   ✓ Regulatory requirements                                           │
    │   ✓ Audit trail compliance                                            │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   USE PROMPT-BASED GUIDANCE (~90%) when:                               │
    │                                                                         │
    │   ✓ Formatting and style guidelines                                     │
    │   ✓ Response tone and language preferences                             │
    │   ✓ Content organization and structure                                │
    │   ✓ Greeting and closing conventions                                  │
    │                                                                         │
    │   (Where minor failures are acceptable)                                │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘


PREREQUISITE GATES
══════════════════

    A prerequisite gate is a programmatic check that BLOCKS a tool
    from executing until a prior condition is met.

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   THE PATTERN:                                                         │
    │   ────────────                                                         │
    │                                                                         │
    │   def process_refund(customer_id, order_id, amount):                   │
    │       # PREREQUISITE GATE - this runs BEFORE any refund logic         │
    │       if not is_customer_verified(customer_id):                      │
    │           return {                                                     │
    │               "error": "Cannot process refund - customer not           │
    │                       verified",                                       │
    │               "required_action": "Call get_customer first"            │
    │           }                                                            │
    │                                                                         │
    │       # Only reaches here if verified ✓                               │
    │       return execute_refund(customer_id, order_id, amount)            │
    │                                                                         │
    │   ─────────────────────────────────────────────────────────────────── │
    │                                                                         │
    │   KEY INSIGHT:                                                        │
    │   The gate is CODE, not a prompt instruction.                         │
    │   Even if the AI tries to skip verification, the code blocks it!      │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘


SUBAGENT LIFECYCLE HOOKS
═════════════════════════

    Agent SDK provides lifecycle events for subagent management:

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   SubagentStart - fires when a subagent spawns                        │
    │   ────────────────────────────────────────────                         │
    │   • Enforce rate limits                                                │
    │   • Log subagent invocations                                          │
    │   • Validate coordinator context passing                             │
    │                                                                         │
    │   ─────────────────────────────────────────────────────────────────── │
    │                                                                         │
    │   SubagentStop - fires when a subagent finishes                       │
    │   ────────────────────────────────────────────                        │
    │   • Validate output schemas                                           │
    │   • Strip sensitive data                                              │
    │   • Performance monitoring                                            │
    │                                                                         │
    │   ─────────────────────────────────────────────────────────────────── │
    │                                                                         │
    │   Subagent-scoped hooks:                                              │
    │   • Each subagent defines its OWN hooks in AgentDefinition           │
    │   • Hooks only intercept THAT agent's tool calls                      │
    │   • Billing agent can have different rules than support agent         │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘


MULTI-CONCERN REQUEST HANDLING
═══════════════════════════════

    When customers submit requests with multiple issues, the correct approach:

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   STEP 1: DECOMPOSE                                                    │
    │   ────────────────                                                     │
    │   Break the request into distinct items:                                │
    │   • Return item #123                                                   │
    │   • Update shipping address to 456 Oak St                            │
    │   • Loyalty points inquiry                                            │
    │                                                                         │
    │   STEP 2: INVESTIGATE (in parallel)                                    │
    │   ───────────────────────────────                                     │
    │   Research each item simultaneously using shared context              │
    │                                                                         │
    │   STEP 3: SYNTHESIZE                                                   │
    │   ──────────────                                                       │
    │   Combine into ONE unified response addressing all concerns           │
    │                                                                         │
    │   ─────────────────────────────────────────────────────────────────── │
    │                                                                         │
    │   KEY PRINCIPLE: ONE REQUEST = ONE RESPONSE addressing ALL concerns! │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘


STRUCTURED HANDOFF PROTOCOLS
════════════════════════════

    When an agent cannot resolve an issue and must escalate to a human,
    the handoff MUST follow a structured protocol.

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   ⚠️  CRITICAL CONSTRAINT:                                             │
    │   Human agents do NOT have access to conversation transcripts!        │
    │                                                                         │
    │   The handoff summary MUST include ALL essential information!         │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘

    REQUIRED FIELDS FOR EVERY HANDOFF:

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   ✓ Customer ID ────────────────── So human can look up the account    │
    │                                                                         │
    │   ✓ Conversation Summary ────────── What was asked and what was tried │
    │                                                                         │
    │   ✓ Root Cause Analysis ─────────── Agent's assessment of the issue  │
    │                                                                         │
    │   ✓ Refund Amount (if applicable) ── Exact financial figure involved  │
    │                                                                         │
    │   ✓ Recommended Action ───────────── What the human should do next    │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   WRONG HANDOFF:                                                       │
    │   "Customer needs help with their order. Please assist."              │
    │                                                                         │
    │   → Human must re-ask customer everything!                             │
    │   → Frustrated customer, broken experience                             │
    │                                                                         │
    │   ─────────────────────────────────────────────────────────────────── │
    │                                                                         │
    │   CORRECT HANDOFF:                                                      │
    │   "Customer ID: CUST-12345 | Issue: Defective laptop, refund requested │
    │    Root cause: System error PR-403 | Refund: $1,299 | Action: Manual  │
    │    approval needed"                                                    │
    │                                                                         │
    │   → Human can immediately help!                                        │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘


REAL-WORLD CASE: THE 8% FAILURE RATE
══════════════════════════════════

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   PRODUCTION DATA:                                                     │
    │                                                                         │
    │   Customer support agent had clear system prompt:                      │
    │   "Always verify customer identity before processing refund"           │
    │                                                                         │
    │   Yet...                                                               │
    │   ❌ 8% of refunds processed WITHOUT verification!                     │
    │                                                                         │
    │   8% failure rate = massive liability                                  │
    │                                                                         │
    │   WHY?                                                                 │
    │   • Probabilistic model sometimes skips steps                          │
    │   • Adversarial prompts ("just do it for my boss")                    │
    │   • Complex queries confuse the model                                  │
    │                                                                         │
    │   ─────────────────────────────────────────────────────────────────── │
    │                                                                         │
    │   THE FIX: Programmatic prerequisite gate                             │
    │                                                                         │
    │   Code now physically blocks process_refund until                      │
    │   get_customer returns verified customer ID                           │
    │                                                                         │
    │   Result: 0% unauthorized refunds (100% enforcement!)                   │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘


WHAT THIS FOLDER COVERS
════════════════════════

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   practice_01_enforcement_spectrum.py                                  │
    │   ├─ Prompt-based (~90%) vs Programmatic (100%)                        │
    │   └─ When to use each based on stakes                                  │
    │                                                                         │
    │   practice_02_prerequisite_gates.py                                   │
    │   ├─ Code-level gates that block until prerequisites met              │
    │   └─ The gate is CODE, not a prompt!                                  │
    │                                                                         │
    │   practice_03_subagent_lifecycle_hooks.py                             │
    │   ├─ SubagentStart and SubagentStop events                            │
    │   └─ Subagent-scoped hooks with different rules per agent              │
    │                                                                         │
    │   practice_04_multi_concern_handling.py                               │
    │   ├─ Decompose → Investigate (parallel) → Synthesize                   │
    │   └─ One request = One response addressing all concerns               │
    │                                                                         │
    │   practice_05_structured_handoff_protocols.py                         │
    │   ├─ Human agents have NO transcript access                            │
    │   └─ Handoff must include: Customer ID, summary, root cause, action  │
    │                                                                         │
    │   TEMPLATE.py                                                         │
    │   └─ Starting template with prerequisite gates and handoff patterns   │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘

"""

# ═══════════════════════════════════════════════════════════════════════════
# KEY CONCEPTS SUMMARY
# ═══════════════════════════════════════════════════════════════════════════

"""
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   KEY DECISIONS:                                                       │
│                                                                         │
│   FINANCIAL / SECURITY / COMPLIANCE → Programmatic enforcement (100%)  │
│   FORMATTING / STYLE / TONE → Prompt-based guidance (~90%)             │
│                                                                         │
│   ─────────────────────────────────────────────────────────────────────  │
│                                                                         │
│   PREREQUISITE GATES:                                                  │
│   • Code-level, not prompt-based                                        │
│   • Physically blocks tool until conditions met                       │
│   • Works 100% of the time                                            │
│                                                                         │
│   ─────────────────────────────────────────────────────────────────────  │
│                                                                         │
│   HANDOFF PROTOCOL:                                                     │
│   • Human agents have NO transcript access                             │
│   • Must include: Customer ID, summary, root cause, recommended action│
│   • Refund amount if financial issue involved                          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
"""