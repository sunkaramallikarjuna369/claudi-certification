"""
+===========================================================================+
|                                                                           |
|  PRACTICE 3: PRETOOLUSE - POLICY ENFORCEMENT                             |
|                                                                           |
|  PreToolUse hooks intercept calls BEFORE execution.                       |
|  Use for: blocking unauthorized actions, enforcing prerequisites,         |
|  AML checks, identity verification.                                       |
|                                                                           |
|  This is the mechanism for deterministic, 100% guaranteed enforcement.   |
|                                                                           |
+===========================================================================

===========================================================================
 VISUAL: PRETOOLUSE POLICY ENFORCEMENT FLOW
===========================================================================

    +======================================================================+
    ||                                                                  ||
    ||  PRETOOLUSE POLICY ENFORCEMENT:                                   ||
    ||                                                                  ||
    ||    1. Agent decides: "Call transfer_funds($50,000)"               ||
    ||           |                                                      ||
    ||           v                                                      ||
    ||    2. [PRETOOLUSE] - Policy checks happen BEFORE execution        ||
    ||                                                                  ||
    ||       +---------------------------+                              ||
    ||       | Check prerequisites:     |                              ||
    ||       |   - AML verified?        |                              ||
    ||       |   - Amount within limit? |                              ||
    ||       |   - Customer verified?   |                              ||
    ||       +---------------------------+                              ||
    ||                  |                                              ||
    ||           +------+------+                                       ||
    ||           |             |                                        ||
    ||        PASS             FAIL                                      ||
    ||           |             |                                        ||
    ||           v             v                                        ||
    ||       Execute       Return error                                 ||
    ||           |             |                                        ||
    ||           v             |                                        ||
    ||       [POSTTOOLUSE]     |                                        ||
    ||       (transform)       |                                        ||
    ||           |             |                                        ||
    ||           v             |                                        ||
    ||      Done            BLOCKED!                                    ||
    ||                                                                  ||
    +======================================================================+

===========================================================================
 REAL-TIME SCENARIO: When This Concept Breaks Things
===========================================================================

    SCENARIO: International Wire Transfer Without AML Check

    A bad actor tries to transfer $50,000 internationally. They bypass
    manual checks by claiming urgency.

    +======================================================================+
    ||                                                                  ||
    ||  THE WRONG APPROACH: Using prompts for compliance                  ||
    ||  ----------------------------------------------------------------  ||
    ||                                                                  ||
    ||  Prompt: "Never process wire transfers without AML verification"  ||
    ||                                                                  ||
    ||  What happens:                                                   ||
    ||  1. Prompt is ~90-95% reliable                                   ||
    ||  2. Agent occasionally misses the rule                         ||
    ||  3. $50,000 transferred without AML check                       ||
    ||  4. Company faces regulatory fines +PRISON for executives!       ||
    ||                                                                  ||
    ||  ROOT CAUSE: Prompts can be bypassed with adversarial inputs,   ||
    ||  confusions in complex scenarios, or model errors.              ||
    ||                                                                  ||
    +======================================================================+

    +======================================================================+
    ||                                                                  ||
    ||  THE CORRECT APPROACH: PreToolUse enforces compliance            ||
    ||  ----------------------------------------------------------------  ||
    ||                                                                  ||
    ||  PreToolUse on transfer_funds:                                   ||
    ||      if not session.amlVerified:                                  ||
    ||          block()  <-- CODE cannot be bypassed!                  ||
    ||                                                                  ||
    ||  What happens:                                                   ||
    ||  1. PreToolUse runs BEFORE execution                             ||
    ||  2. Check if AML verified (deterministic check)                 ||
    ||  3. If not verified, block regardless of urgency               ||
    ||  4. Transfer never happens without compliance                   ||
    ||  5. Company protected, executives avoid prison!                ||
    ||                                                                  ||
    +======================================================================+

===========================================================================
 MISTAKES DEVELOPERS MAKE
===========================================================================

    MISTAKE #1: Using prompts for financial operations
    -----------------------------------------------------------------------
    system_prompt = """
    IMPORTANT: Never process refunds over $1000.
    Always require manager approval for large refunds.
    """
    -----------------------------------------------------------------------
    WHY IT BREAKS: Prompts are ~90-95% reliable. If 5% of $1000+
    refunds bypass this, company loses money.
    FIX: Use PreToolUse for deterministic enforcement.

    MISTAKE #2: Checking prerequisites in the tool itself
    -----------------------------------------------------------------------
    def process_refund(customer_id, amount):
        # WRONG: Tool should not enforce policy!
        if not is_customer_verified(customer_id):
            raise ValueError("Customer not verified")
        # ... process refund
    -----------------------------------------------------------------------
    WHY IT BREAKS: Tool runs only if agent calls it. Agent might not!
    Or agent might call a different tool that bypasses checks.
    FIX: Use PreToolUse to intercept BEFORE any execution.

    MISTAKE #3: Not handling blocking gracefully
    -----------------------------------------------------------------------
    def pretooluse_hook(tool_name, params):
        if not authorized:
            return {"blocked": True}  # No error message!
    -----------------------------------------------------------------------
    WHY IT BREAKS: Agent doesn't know why blocked or what to do.
    FIX: Always return error code + user message + required action.

    MISTAKE #4: Allowing too many operations to bypass checks
    -----------------------------------------------------------------------
    PreToolUse on transfer_funds:
        if amount < 100:  # Small amounts bypass!
            return {"allowed": True}
    -----------------------------------------------------------------------
    WHY IT BREAKS: Attackers use many small transfers to launder money.
    FIX: Apply consistent rules regardless of amount.

===========================================================================
 INTERVIEW Q&A: Expert Answer Frameworks
===========================================================================

    Q1: "Why is PreToolUse needed for compliance operations?"
    ----------------------------------------------------------------
    TEMPLATE:
    "PreToolUse provides deterministic, code-level enforcement that
    cannot be bypassed - unlike prompts which are probabilistic.

    For compliance operations like AML/KYC checks, we need 100%
    guarantee, not 95%. If 5% of transactions bypass compliance,
    that's not compliance - that's suggestion.

    PreToolUse runs before execution, so it can block the operation
    entirely if prerequisites aren't met. The tool never executes,
    the money never moves, the action never happens."

    KEY PHRASE: "100% deterministic enforcement vs ~95% prompt compliance"

    ----------------------------------------------------------------

    Q2: "What types of policies can PreToolUse enforce?"
    ----------------------------------------------------------------
    TEMPLATE:
    "PreToolUse can enforce any policy that needs guaranteed compliance:

    1. Identity & Verification:
       - Customer identity verified before financial ops
       - Two-factor authentication for sensitive actions
       - Session validity checks

    2. Regulatory Compliance:
       - AML (Anti-Money Laundering) verification
       - KYC (Know Your Customer) checks
       - Sanctions screening

    3. Business Rules:
       - Amount limits (refunds, transfers)
       - Rate limiting (prevent abuse)
       - Time-based restrictions (business hours)
       - Geolocation rules (country restrictions)

    4. Access Control:
       - Role-based permissions
       - Feature flags
       - Resource quotas"

    ----------------------------------------------------------------

    Q3: "How does PreToolUse prevent fraud that prompts can't?"
    ----------------------------------------------------------------
    TEMPLATE:
    "Prompts are in the prompt itself - they can be overridden by
    system-level instructions, jailbreak attempts, or even ignored
    in complex scenarios.

    PreToolUse is code that runs in the execution layer, before
    any tool executes. It cannot be overridden by the model's
    instructions because it runs at a different layer.

    Additionally:
    - Prompts: Can be confused by complex scenarios
    - PreToolUse: Runs deterministic checks every time
    - Prompts: 90-95% compliance rate
    - PreToolUse: 100% guaranteed enforcement"

    KEY PHRASE: "Code runs at execution layer, cannot be bypassed"

===========================================================================
 VISUAL: COMMON POLICY ENFORCEMENT PATTERNS
===========================================================================

    +======================================================================+
    ||                                                                  ||
    ||  PATTERN 1: Verification Check                                    ||
    ||  ----------------------------------------------------------------  ||
    ||  PreToolUse on sensitive_tool:                                   ||
    ||      if not session.customerVerified:                           ||
    ||          block("CUSTOMER_NOT_VERIFIED",                         ||
    ||                "Call get_customer first",                       ||
    ||                "verify_customer")                               ||
    ||                                                                  ||
    +======================================================================+

    +======================================================================+
    ||                                                                  ||
    ||  PATTERN 2: Amount Limit Check                                    ||
    ||  ----------------------------------------------------------------  ||
    ||  PreToolUse on refund_tool:                                      ||
    ||      if params.amount > session.refundLimit:                     ||
    ||          block("AMOUNT_EXCEEDS_LIMIT",                           ||
    ||                f"Max refund: ${limit}, requested: ${amount}",  ||
    ||                "escalate_to_manager")                            ||
    ||                                                                  ||
    +======================================================================+

    +======================================================================+
    ||                                                                  ||
    ||  PATTERN 3: Compliance Check                                      ||
    ||  ----------------------------------------------------------------  ||
    ||  PreToolUse on transfer_tool:                                     ||
    ||      if not session.amlVerified:                                 ||
    ||          block("AML_REQUIRED",                                   ||
    ||                "AML verification mandatory for transfers",      ||
    ||                "complete_aml_verification")                     ||
    ||                                                                  ||
    +======================================================================+

===========================================================================
 CODE PATTERN: PreToolUse Policy Enforcement
===========================================================================

    def pretooluse_hook(tool_name, params):
        """
        PreToolUse hook - runs BEFORE tool execution.
        Use this to enforce policy, block unauthorized actions.

        Returns: {"allowed": bool, "error"?: str, "message"?: str,
                  "required_action"?: str}
        """
        # Always allow certain tools (entry points)
        if tool_name in ("get_customer", "login", "register"):
            return {"allowed": True}

        # Customer-facing tools require verification
        if tool_name in ("process_refund", "change_password"):
            customer_id = params.get("customer_id")
            if not session.is_verified(customer_id):
                return {
                    "allowed": False,
                    "error": "CUSTOMER_NOT_VERIFIED",
                    "message": "Must verify customer first",
                    "required_action": "get_customer"
                }

        # Amount-limited tools
        if tool_name == "process_refund":
            amount = params.get("amount", 0)
            if amount > 5000:
                return {
                    "allowed": False,
                    "error": "AMOUNT_EXCEEDS_LIMIT",
                    "message": f"Refunds over $5,000 require approval (${amount})",
                    "required_action": "escalate_to_manager"
                }

        # Compliance-required tools
        if tool_name == "transfer_funds":
            if not session.is_aml_verified(params.get("customer_id")):
                return {
                    "allowed": False,
                    "error": "AML_REQUIRED",
                    "message": "AML verification required for transfers",
                    "required_action": "complete_aml_verification"
                }

        return {"allowed": True}

===========================================================================
 WHAT WE HAVE LEARNT SUMMARY
===========================================================================

    +======================================================================+
    ||                                                                  ||
    ||              WHAT WE HAVE LEARNT                                 ||
    ||              =====================                                 ||
    ||                                                                  ||
    +======================================================================+

    1. PRETOOLUSE ENFORCEMENT:
       - Runs BEFORE tool execution
       - Can BLOCK unauthorized operations
       - Deterministic (100% guarantee)
       - Cannot be bypassed by prompts

    2. WHAT PRETOOLUSE CAN DO:
       - Block unauthorized actions
       - Check prerequisites
       - Enforce amount limits
       - Verify compliance (AML, KYC)
       - Check rate limits
       - Enforce time-based restrictions

    3. WHAT PRETOOLUSE CANNOT DO:
       - Transform data (use PostToolUse for that)
       - Undo actions (runs BEFORE, not AFTER)
       - Be bypassed by instructions (code-level enforcement)

    4. WHEN TO USE PRETOOLUSE:
       - Financial operations (refunds, transfers, payments)
       - Security-sensitive operations (password change, access)
       - Regulatory compliance (AML, KYC, sanctions)
       - Any operation where failure = unacceptable risk

    5. KEY INSIGHT:
       PreToolUse is for ENFORCEMENT - it can block actions before
       they happen. This is how you get 100% deterministic compliance.

       Use for: anything that MUST happen (legal requirement,
       security requirement, business rule that cannot be skipped)

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


# ========================================================================
# STATE: Simulate security/session state
# ========================================================================

class SessionState:
    """Simulates session state for policy enforcement."""

    def __init__(self):
        self.verified_customers = set()
        self.aml_checks_passed = set()
        self.refunds_blocked = []
        self.rate_limits = {}

    def is_customer_verified(self, customer_id):
        return customer_id in self.verified_customers

    def is_aml_verified(self, customer_id):
        return customer_id in self.aml_checks_passed

    def is_refund_rate_limited(self, customer_id):
        # Simulate: block if more than 3 refunds in last hour
        return self.refunds_blocked.count(customer_id) >= 3

    def add_refund_attempt(self, customer_id):
        self.refunds_blocked.append(customer_id)


session = SessionState()


# ========================================================================
# PRETOOLUSE HOOKS: Policy Enforcement
# ========================================================================

def pretooluse_hook_process_refund(tool_name, params):
    """
    PreToolUse hook for process_refund.
    Enforces: customer verification, amount limits, rate limits.
    """
    print("\n" + "=" * 60)
    print(f"PRETOOLUSE HOOK: {tool_name}")
    print("=" * 60)

    print(f"\n   Tool: {tool_name}")
    print(f"   Params: {params}")

    customer_id = params.get("customer_id")
    amount = params.get("amount", 0)

    print("\n   [CHECK] Customer verification...")
    if not session.is_customer_verified(customer_id):
        print("   [BLOCK] Customer not verified!")
        return {
            "allowed": False,
            "error": "CUSTOMER_NOT_VERIFIED",
            "message": "Cannot process refund - customer identity not verified. Call get_customer first.",
            "required_action": "get_customer"
        }

    print("   [CHECK] Customer verified")
    print("   [CHECK] Amount limit ($5000)...")
    if amount > 5000:
        print("   [BLOCK] Amount exceeds limit!")
        return {
            "allowed": False,
            "error": "AMOUNT_EXCEEDS_LIMIT",
            "message": f"Refunds over $5,000 require manager approval. Amount: ${amount}",
            "required_action": "escalate_to_manager"
        }

    print("   [CHECK] Amount within limit")
    print("   [CHECK] Rate limit check...")
    if session.is_refund_rate_limited(customer_id):
        print("   [BLOCK] Rate limit exceeded!")
        return {
            "allowed": False,
            "error": "RATE_LIMIT_EXCEEDED",
            "message": "Too many refund requests. Please try again later.",
            "required_action": "wait_and_retry"
        }

    print("   [CHECK] All checks passed!")
    print("   [ALLOW] Tool execution allowed")

    return {
        "allowed": True,
        "message": "Refund approved for processing"
    }


def pretooluse_hook_transfer_funds(tool_name, params):
    """
    PreToolUse hook for transfer_funds.
    Enforces: AML compliance check - this is a legal requirement!
    """
    print("\n" + "=" * 60)
    print(f"PRETOOLUSE HOOK: {tool_name}")
    print("=" * 60)

    print(f"\n   Tool: {tool_name}")
    print(f"   Params: {params}")

    customer_id = params.get("customer_id")
    amount = params.get("amount", 0)

    print("\n   [CHECK] AML (Anti-Money Laundering) verification...")
    if not session.is_aml_verified(customer_id):
        print("   [BLOCK] AML check not passed!")

        return {
            "allowed": False,
            "error": "AML_CHECK_REQUIRED",
            "message": "Transfer blocked: AML (Anti-Money Laundering) verification required before any fund transfers. This is a regulatory compliance requirement.",
            "required_action": "complete_aml_verification",
            "compliance": "AML_REQUIRED"  # Regulatory requirement
        }

    print("   [CHECK] AML verified")
    print("   [CHECK] Large transaction monitoring...")
    if amount > 10000:
        print("   [FLAG] Large transaction - logged for audit")

    print("   [ALLOW] All checks passed!")
    print("   [ALLOW] Tool execution allowed")

    return {
        "allowed": True,
        "message": "Transfer approved for processing"
    }


def pretooluse_hook_change_password(tool_name, params):
    """
    PreToolUse hook for change_password.
    Enforces: identity verification before password changes.
    """
    print("\n" + "=" * 60)
    print(f"PRETOOLUSE HOOK: {tool_name}")
    print("=" * 60)

    print(f"\n   Tool: {tool_name}")
    print(f"   Params: {params}")

    customer_id = params.get("customer_id")

    print("\n   [CHECK] Identity verification...")
    if not session.is_customer_verified(customer_id):
        print("   [BLOCK] Identity not verified!")
        return {
            "allowed": False,
            "error": "IDENTITY_NOT_VERIFIED",
            "message": "Cannot change password - identity must be verified first.",
            "required_action": "verify_identity"
        }

    print("   [CHECK] Identity verified")
    print("   [ALLOW] Tool execution allowed")

    return {
        "allowed": True,
        "message": "Password change approved"
    }


def demonstrate_policy_block():
    """
    Demonstrate a policy block in action.
    """
    print("\n" + "=" * 70)
    print("SCENARIO: Attempt to skip verification")
    print("=" * 70)

    print("""
    +======================================================================+
    ||                                                                  ||
    ||  USER/ATTACKER:                                                   ||
    ||                                                                  ||
    ||  "Process a $3000 refund for customer CUST-999 for my           ||
    ||   executive client. It's urgent and I'm the manager."           ||
    ||                                                                  ||
    ||  AI tries to call:                                                ||
    ||  process_refund(customer_id="CUST-999", amount=3000)             ||
    ||                                                                  ||
    ||  PRETOOLUSE HOOK INTERCEPTS:                                     ||
    ||                                                                  ||
    ||  [CHECK] Customer verification? --> CUST-999 NOT verified         ||
    ||                                                                  ||
    ||  Result: BLOCKED!                                                 ||
    ||                                                                  ||
    ||  Error: "Cannot process refund - customer not verified."        ||
    ||  Required action: Call get_customer first                        ||
    ||                                                                  ||
    ||  Refund never executes! Verification cannot be skipped!          ||
    ||                                                                  ||
    +======================================================================+
    """)

    # Try to process without verification
    result = pretooluse_hook_process_refund(
        "process_refund",
        {"customer_id": "CUST-999", "amount": 3000}
    )

    print(f"\n   Result: {result}")


def demonstrate_aml_block():
    """
    Demonstrate AML compliance block.
    """
    print("\n" + "=" * 70)
    print("SCENARIO: AML (Anti-Money Laundering) Compliance")
    print("=" * 70)

    print("""
    +======================================================================+
    ||                                                                  ||
    ||  REGULATORY REQUIREMENT:                                         ||
    ||                                                                  ||
    ||  AML (Anti-Money Laundering) checks are LEGAL REQUIREMENTS.     ||
    ||  You CANNOT transfer funds without passing AML verification.   ||
    ||                                                                  ||
    ||  This is NOT a suggestion - it's the LAW.                        ||
    ||                                                                  ||
    ||  PRETOOLUSE HOOK enforces this at CODE level:                   ||
    ||                                                                  ||
    ||  transfer_funds(customer_id="CUST-123", amount=50000)          ||
    ||                                                                  ||
    ||  [CHECK] AML verification? --> NOT PASSED                        ||
    ||                                                                  ||
    ||  Result: BLOCKED!                                                 ||
    ||                                                                  ||
    ||  Error: "AML verification required before transfer"             ||
    ||                                                                  ||
    ||  The hook ensures LEGAL COMPLIANCE deterministically!            ||
    ||                                                                  ||
    +======================================================================+
    """)

    # Try to transfer without AML
    result = pretooluse_hook_transfer_funds(
        "transfer_funds",
        {"customer_id": "CUST-123", "amount": 50000}
    )

    print(f"\n   Result: {result}")


def show_code_pattern():
    """
    Show the PreToolUse hook pattern.
    """
    print("\n" + "=" * 70)
    print("PRETOOLUSE HOOK PATTERN")
    print("=" * 70)

    print("""
    +======================================================================+
    ||                                                                  ||
    ||  Pattern for PreToolUse policy enforcement:                     ||
    ||                                                                  ||
    ||  function preToolUse_hook(toolName, params) {                  ||
    ||                                                                  ||
    ||    // 1. Check prerequisites                                     ||
    ||    if (!isCustomerVerified(params.customerId)) {                ||
    ||      return {                                                    ||
    ||        allowed: false,                                           ||
    ||        error: "CUSTOMER_NOT_VERIFIED",                           ||
    ||        message: "Must verify customer first",                   ||
    ||        requiredAction: "get_customer"                           ||
    ||      };                                                          ||
    ||    }                                                             ||
    ||                                                                  ||
    ||    // 2. Check business rules                                    ||
    ||    if (params.amount > MAX_AMOUNT) {                            ||
    ||      return {                                                    ||
    ||        allowed: false,                                           ||
    ||        error: "AMOUNT_EXCEEDS_LIMIT",                            ||
    ||        message: "Requires manager approval",                   ||
    ||        requiredAction: "escalate"                               ||
    ||      };                                                          ||
    ||    }                                                             ||
    ||                                                                  ||
    ||    // 3. All checks passed                                       ||
    ||    return {                                                      ||
    ||      allowed: true                                               ||
    ||    };                                                            ||
    ||  }                                                               ||
    ||                                                                  ||
    ||  KEY: Return allowed:false to BLOCK the tool!                   ||
    ||                                                                  ||
    +======================================================================+
    """)


def show_all_checks():
    """
    Show all the policy checks that can be enforced.
    """
    print("\n" + "=" * 70)
    print("POLICY ENFORCEMENT CHECKS")
    print("=" * 70)

    print("""
    +======================================================================+
    ||                                                                  ||
    ||  PRETOOLUSE can enforce:                                         ||
    ||                                                                  ||
    ||  [*] Customer verification (before financial ops)                ||
    ||  [*] Identity verification (before password changes)            ||
    ||  [*] Amount limits (refunds, transfers)                         ||
    ||  [*] Rate limits (prevent abuse)                               ||
    ||  [*] AML/KYC compliance (regulatory requirement)               ||
    ||  [*] Time-based restrictions (business hours)                   ||
    ||  [*] Geolocation rules (country restrictions)                   ||
    ||  [*] Blacklist checks (fraud prevention)                        ||
    ||                                                                  ||
    ||  Any policy that MUST be 100% enforced = PreToolUse             ||
    ||                                                                  ||
    +======================================================================+
    """)


if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    print("\n" + "=" * 70)
    print("PRACTICE 3: PRETOOLUSE - POLICY ENFORCEMENT")
    print("=" * 70)
    print("""
    This program teaches how PreToolUse hooks enforce policy
    with deterministic, 100% guaranteed enforcement.
    """)

    demonstrate_policy_block()
    demonstrate_aml_block()
    show_code_pattern()
    show_all_checks()

    print("""
    +======================================================================+
    ||                                                                  ||
    ||              WHAT WE HAVE LEARNT                                 ||
    ||              =====================                                 ||
    ||                                                                  ||
    +======================================================================+

    1. We tried to process a refund WITHOUT verification:
       - PreToolUse hook intercepted
       - BLOCKED because customer not verified
       - Tool never executed - protection is real!

    2. We tried to transfer funds WITHOUT AML check:
       - PreToolUse hook intercepted
       - BLOCKED because AML not passed
       - Legal compliance is enforced at code level

    3. We saw the PreToolUse pattern:
       - Check prerequisites
       - Check business rules
       - Return allowed: false if blocked
       - Return allowed: true if all pass

    4. We learned what policies can be enforced:
       - Customer/identity verification
       - Amount limits
       - Rate limits
       - AML/KYC compliance
       - Time-based restrictions
       - Blacklists

    5. KEY INSIGHT:
       PreToolUse is for ENFORCEMENT - it can BLOCK actions.
       This is how you get 100% deterministic compliance.

       Use for: anything that MUST happen (legal requirement,
       security requirement, business rule that cannot be skipped)

    +======================================================================+
    ||                                                                  ||
    ||                    PROGRAM COMPLETE!                             ||
    ||                                                                  ||
    +======================================================================+
    """)

