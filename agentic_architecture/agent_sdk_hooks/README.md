"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║           AGENT SDK HOOKS: PreToolUse & PostToolUse                       ║
║                                                                              ║
║  Controlling Agent Behavior Before and After Tool Execution                ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

TWO HOOK TYPES
══════════════

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   PRETOOLUSE HOOK - BEFORE Tool Execution                               │
    │   ──────────────────────────────────────────                           │
    │                                                                         │
    │   Runs BEFORE the tool executes. Can:                                    │
    │   • BLOCK the action (prevent execution)                                │
    │   • MODIFY parameters                                                   │
    │   • REDIRECT to different tool                                          │
    │                                                                         │
    │   Use for: Policy enforcement, prerequisite checks, validation         │
    │                                                                         │
    │   ┌─────────────────────────────────────────────────────────────────┐  │
    │   │  if amount > 5000:                                             │  │
    │   │      block()  // Don't execute                                 │  │
    │   │      return "Requires manager approval"                         │  │
    │   │  }                                                             │  │
    │   └─────────────────────────────────────────────────────────────────┘  │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   POSTTOOLUSE HOOK - AFTER Tool Execution                              │
    │   ───────────────────────────────────────────                          │
    │                                                                         │
    │   Runs AFTER the tool executes, BEFORE the model sees the result.      │
    │   Can:                                                                   │
    │   • TRANSFORM data (normalize formats)                                  │
    │   • ADD metadata                                                         │
    │   • STRIP sensitive information                                         │
    │                                                                         │
    │   CANNOT block - the action has already happened!                       │
    │                                                                         │
    │   Use for: Data normalization, format conversion, metadata addition    │
    │                                                                         │
    │   ┌─────────────────────────────────────────────────────────────────┐  │
    │   │  // Convert timestamps to readable dates                       │  │
    │   │  if (result.timestamp) {                                       │  │
    │   │      result.date = normalizeTimestamp(result.timestamp);       │  │
    │   │  }                                                             │  │
    │   └─────────────────────────────────────────────────────────────────┘  │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘


THE CRITICAL DISTINCTION
═════════════════════════

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   PRETOOLUSE: "Should this action happen?"                            │
    │   ────────────────────────────────────────                            │
    │   → Decision made BEFORE execution                                     │
    │   → Can PREVENT the action from happening                              │
    │   → Use for: enforcement, blocking, prerequisites                     │
    │                                                                         │
    │   ─────────────────────────────────────────────────────────────────── │
    │                                                                         │
    │   POSTTOOLUSE: "How should I present this result?"                    │
    │   ───────────────────────────────────────────                         │
    │   → Action ALREADY happened                                           │
    │   → Cannot undo the action                                            │
    │   → Use for: transformation, normalization                           │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘

    ⚠️  EXAM WARNING:
    ─────────────
    Never use PostToolUse to block actions!
    The non-compliant behavior has ALREADY occurred!
    By the time PostToolUse runs, it's too late to prevent.


POSTTOOLUSE: DATA NORMALIZATION
════════════════════════════════

    Handles heterogeneous formats from different MCP tools:

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   BEFORE (raw tool outputs):                                           │
    │   ──────────────────────────                                           │
    │                                                                         │
    │   Tool A: {"timestamp": 1704067200}  → Unix timestamp                  │
    │   Tool B: {"date": "12/31/2024"}     → DD/MM/YYYY                     │
    │   Tool C: {"status_code": 200}       → Numeric code                    │
    │   Tool D: {"trend": 1}              → Magic number                     │
    │                                                                         │
    │   Model must figure out how to interpret each format!                   │
    │                                                                         │
    │   ─────────────────────────────────────────────────────────────────── │
    │                                                                         │
    │   AFTER (PostToolUse normalization):                                   │
    │   ────────────────────────────────────────────                        │
    │                                                                         │
    │   Tool A: {"timestamp": 1704067200} → {"date": "2024-01-01"}        │
    │   Tool B: {"date": "12/31/2024"}    → {"date": "2024-12-31"}         │
    │   Tool C: {"status_code": 200}      → {"status": "success"}          │
    │   Tool D: {"trend": 1}             → {"trend": "rising"}            │
    │                                                                         │
    │   Model sees CONSISTENT format regardless of source!                   │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘


PRETOOLUSE: POLICY ENFORCEMENT
══════════════════════════════

    Intercepts calls before execution for deterministic enforcement:

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   EXAMPLE 1: Block high refunds                                       │
    │   ────────────────────────────────────                                 │
    │                                                                         │
    │   PreToolUse hook on process_refund → {                                │
    │       if (amount > 500) {                                             │
    │           block() // refund never executes                             │
    │           redirect to human escalation                                │
    │       }                                                               │
    │   }                                                                   │
    │                                                                         │
    │   ─────────────────────────────────────────────────────────────────── │
    │                                                                         │
    │   EXAMPLE 2: AML compliance gate                                      │
    │   ───────────────────────────────────                                 │
    │                                                                         │
    │   PreToolUse hook on transfer_funds → {                                │
    │       if (!session.amlCheckPassed) {                                  │
    │           block() // transfer blocked until AML verified              │
    │           return "Complete AML check first"                           │
    │       }                                                               │
    │   }                                                                   │
    │                                                                         │
    │   ─────────────────────────────────────────────────────────────────── │
    │                                                                         │
    │   The hook ensures LEGAL COMPLIANCE deterministically!                  │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘


DECISION FRAMEWORK: HOOKS VS PROMPTS
══════════════════════════════════

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   USE HOOKS (100% guarantee) when:                                     │
    │   ────────────────────────────────────                                 │
    │                                                                         │
    │   ✓ Single failure = financial loss or legal risk                      │
    │   ✓ Compliance requirement (AML, KYC)                                  │
    │   ✓ Security operation (identity verification)                         │
    │   ✓ High-stakes financial operation (refunds, transfers)               │
    │                                                                         │
    │   ─────────────────────────────────────────────────────────────────── │
    │                                                                         │
    │   USE PROMPTS (~90-95% compliance) when:                               │
    │   ─────────────────────────────────────                               │
    │                                                                         │
    │   ✓ Minor failures are acceptable                                      │
    │   ✓ Formatting preference                                             │
    │   ✓ Response tone                                                      │
    │   ✓ Style guideline                                                   │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   THE KEY QUESTION:                                                    │
    │                                                                         │
    │   "What happens if this fails?"                                        │
    │                                                                         │
    │   If failure = financial loss / legal risk → HOOKS                     │
    │   If failure = minor inconvenience → PROMPTS                             │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘


EXAM TRAPS TO AVOID
═══════════════════

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   TRAP 1: "Use prompts for financial operations"                       │
    │   ──────────────────────────────────────────────────                   │
    │   WRONG! Financial ops have legal/financial risk.                       │
    │   Prompt ~95% success = 5% failure = unacceptable loss.               │
    │   Must use PRETOOLUSE for 100% guarantee.                               │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   TRAP 2: "Use PostToolUse to block actions"                           │
    │   ──────────────────────────────────────────────────                   │
    │   WRONG! PostToolUse runs AFTER execution.                              │
    │   By the time it runs, the action has already happened!                 │
    │   Cannot undo with PostToolUse. Use PreToolUse to block BEFORE.        │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   TRAP 3: "Use routing classifiers for workflow enforcement"          │
    │   ──────────────────────────────────────────────────────               │
    │   WRONG! Routing classifiers handle ROUTING (which agent?), not       │
    │   workflow enforcement (correct order of operations?).                  │
    │   For workflow enforcement, use PreToolUse hooks.                       │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   TRAP 4: "Add few-shot examples for security ops"                     │
    │   ──────────────────────────────────────────────────                   │
    │   WRONG! Examples work ~90%, not 100%.                                  │
    │   Security breach = catastrophic. Must use hooks.                      │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘


GUARANTEE COMPARISON
════════════════════

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   PROMPTS: ~90-95% success rate                                       │
    │   ───────────────────────────────                                      │
    │                                                                         │
    │   • Instructions in system prompt                                       │
    │   • Language model may not follow perfectly                             │
    │   • Adversarial prompts can bypass                                     │
    │   • Complex scenarios may confuse                                      │
    │                                                                         │
    │   For 1000 operations at 95%:                                          │
    │       50 failures → May be unacceptable for financial/security        │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   HOOKS: 100% success rate                                              │
    │   ──────────────────────────                                           │
    │                                                                         │
    │   • Code runs before/after execution                                   │
    │   • Cannot be bypassed by prompts                                      │
    │   • Deterministic execution                                             │
    │   • Works even with adversarial input                                   │
    │                                                                         │
    │   For 1000 operations at 100%:                                          │
    │       0 failures → Guaranteed compliance                               │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘


WHAT THIS FOLDER COVERS
════════════════════════

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   practice_01_two_hook_types.py                                       │
    │   ├─ PreToolUse vs PostToolUse comparison                              │
    │   └─ When to use each based on timing and purpose                      │
    │                                                                         │
    │   practice_02_posttooluse_normalization.py                              │
    │   ├─ Data normalization from heterogeneous sources                      │
    │   └─ Unix timestamps, numeric codes, mixed formats                      │
    │                                                                         │
    │   practice_03_pretooluse_policy.py                                      │
    │   ├─ Policy enforcement before execution                                │
    │   └─ Blocking unauthorized actions, AML compliance                      │
    │                                                                         │
    │   practice_04_decision_framework.py                                     │
    │   ├─ When to use hooks vs prompts                                       │
    │   └─ Decision matrix with scenarios                                     │
    │                                                                         │
    │   practice_05_complete_example.py                                       │
    │   ├─ Complete implementation with PreToolUse + PostToolUse together  │
    │   └─ Customer support agent with verification and normalization          │
    │                                                                         │
    │   TEMPLATE.py                                                         │
    │   └─ Starting template with hook implementations                        │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘

"""

# ═══════════════════════════════════════════════════════════════════════════
# KEY CONCEPTS SUMMARY
# ═══════════════════════════════════════════════════════════════════════════

"""
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   KEY DISTINCTIONS:                                                    │
│                                                                         │
│   PRETOOLUSE = BEFORE execution (can block)                           │
│   POSTTOOLUSE = AFTER execution (can transform, cannot block)          │
│                                                                         │
│   ─────────────────────────────────────────────────────────────────────  │
│                                                                         │
│   USE HOOKS when:                                                       │
│   • Single failure = financial loss / legal risk                       │
│   • 100% compliance required                                           │
│   • Security operation                                                  │
│                                                                         │
│   USE PROMPTS when:                                                     │
│   • Minor failures acceptable                                          │
│   • Formatting / style preference                                      │
│                                                                         │
│   ─────────────────────────────────────────────────────────────────────  │
│                                                                         │
│   EXAM TIPS:                                                            │
│   • "PostToolUse to block" = WRONG answer!                             │
│   • "Prompts for financial ops" = WRONG answer!                        │
│   • "Routing classifiers for enforcement" = WRONG answer!              │
│   • PreToolUse can block, PostToolUse cannot                           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
"""