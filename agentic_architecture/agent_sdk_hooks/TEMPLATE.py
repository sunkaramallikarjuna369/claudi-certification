"""
+===========================================================================+
|                                                                           |
|  AGENT SDK HOOKS - TEMPLATE                                              |
|                                                                           |
|  Starting template for building agents with PreToolUse and               |
|  PostToolUse hooks. Includes comprehensive examples and expert guidance. |
|                                                                           |
|  INTERVIEW PREP: "Design a policy enforcement system using hooks"        |
|  This tests your understanding of PreToolUse, PostToolUse, and when     |
|  to use each type of hook.                                               |
|                                                                           |
+===========================================================================

===========================================================================
 VISUAL: HOOK ARCHITECTURE OVERVIEW
===========================================================================

    +======================================================================+
    ||                                                                  ||
    ||  AGENT WITH HOOKS ARCHITECTURE:                                  ||
    ||                                                                  ||
    ||    +--------------------------------------------------------------+ ||
    ||    |                                                              | ||
    ||    |   Agent decides: "Call tool_X"                              | ||
    ||    |                                                              | ||
    ||    +--------------------------------------------------------------+ ||
    ||                              |                                    ||
    ||                              v                                    ||
    ||    +--------------------------------------------------------------+ ||
    ||    |                                                              | ||
    ||    |   PRETOOLUSE HOOK (BEFORE execution)                       | ||
    ||    |   ==========================================                | ||
    ||    |                                                              | ||
    ||    |   * Check permissions/prerequisites                       | ||
    ||    |   * Validate input parameters                              | ||
    ||    |   * Enforce policy/business rules                          | ||
    ||    |   * Can BLOCK, MODIFY, or REDIRECT                         | ||
    ||    |                                                              | ||
    ||    +--------------------------------------------------------------+ ||
    ||                    /              \                                ||
    ||                   /                \                               ||
    ||                  v                  v                              ||
    ||               ALLOWED           BLOCKED                           ||
    ||                  |                  |                              ||
    ||                  v                  |                              ||
    ||    +-------------------------------+ |                             ||
    ||    |                               | |                             ||
    ||    |   TOOL EXECUTES               | |                             ||
    ||    |                               | |                             ||
    ||    +-------------------------------+ |                             ||
    ||                    \              / |                              ||
    ||                     \            /  |                              ||
    ||                      v          v    |                              ||
    ||    +--------------------------------------------------------------+ ||
    ||    |                                                              | ||
    ||    |   POSTTOOLUSE HOOK (AFTER execution)                        | ||
    ||    |   =========================================                  | ||
    ||    |                                                              | ||
    ||    |   * Transform raw output                                   | ||
    ||    |   * Normalize data formats                                  | ||
    ||    |   * Add metadata                                           | ||
    ||    |   * Filter sensitive fields                                 | ||
    ||    |                                                              | ||
    ||    +--------------------------------------------------------------+ ||
    ||                              |                                    ||
    ||                              v                                    ||
    ||    +--------------------------------------------------------------+ ||
    ||    |                                                              | ||
    ||    |   Agent sees: Normalized, consistent data                   | ||
    ||    |                                                              | ||
    ||    +--------------------------------------------------------------+ ||
    ||                                                                  ||
    +======================================================================+

===========================================================================
 THREE CLASSIC HOOK PATTERNS
===========================================================================

    +======================================================================+
    ||                                                                  ||
    ||  PATTERN 1: Verification Gate                                     ||
    ||  ==============================================================  ||
    ||                                                                  ||
    ||  PreToolUse: Check if user is verified before allowing access.  ||
    ||                                                                  ||
    ||  Use for: financial ops, sensitive data, password changes       ||
    ||                                                                  ||
    +======================================================================+

    +======================================================================+
    ||                                                                  ||
    ||  PATTERN 2: Amount Limit Enforcement                             ||
    ||  ==============================================================  ||
    ||                                                                  ||
    ||  PreToolUse: Check amount against limit before allowing op.      ||
    ||                                                                  ||
    ||  Use for: refunds, transfers, any monetary operation             ||
    ||                                                                  ||
    +======================================================================+

    +======================================================================+
    ||                                                                  ||
    ||  PATTERN 3: Data Normalization                                   ||
    ||  ==============================================================  ||
    ||                                                                  ||
    ||  PostToolUse: Transform raw output to consistent format          ||
    ||                                                                  ||
    ||  Use for: date formats, status codes, adding display fields     ||
    ||                                                                  ||
    +======================================================================+

===========================================================================
 REAL-TIME SCENARIO: E-commerce Checkout Agent
===========================================================================

    A customer is checking out with a shopping cart. The agent must:
    1. Verify customer identity
    2. Calculate totals with proper formatting
    3. Process payment (enforce fraud checks)
    4. Send confirmation (normalize output)

    +======================================================================+
    ||                                                                  ||
    ||  CHECKOUT FLOW WITH HOOKS:                                       ||
    ||                                                                  ||
    ||  Customer: "I'd like to checkout with my cart"                   ||
    ||                                                                  ||
    ||  [1] get_customer (PreToolUse: always allowed)                   ||
    ||      --> Verify identity                                         ||
    ||      --> Store in session                                        ||
    ||                                                                  ||
    ||  [2] calculate_totals (PostToolUse: normalize output)           ||
    ||      [POSTTOOLUSE] Format prices, add tax breakdown              ||
    ||      --> $124.99 -> "$124.99 USD"                               ||
    ||      --> 1234567890 -> "2024-01-01"                             ||
    ||                                                                  ||
    ||  [3] process_payment (PreToolUse: fraud check)                    ||
    ||      [PRETOOLUSE] Amount > $1000? --> Block + require auth       ||
    ||      [PRETOOLUSE] New customer, high value? --> Flag for review ||
    ||      --> Execute payment if all checks pass                     ||
    ||                                                                  ||
    ||  [4] send_confirmation (PostToolUse: add metadata)              ||
    ||      [POSTTOOLUSE] Add confirmation ID, timestamp                ||
    ||      --> Email confirmation with order details                   ||
    ||                                                                  ||
    +======================================================================+

===========================================================================
 MISTAKES DEVELOPERS MAKE
===========================================================================

    MISTAKE #1: No PreToolUse on entry points
    -----------------------------------------------------------------------
    # WRONG: Entry point might not be in hook list!
    # But what if agent bypasses get_customer?
    -----------------------------------------------------------------------
    WHY IT BREAKS: Entry points should always be allowed.
    FIX: Explicitly return {"allowed": True} for entry in PreToolUse.

    MISTAKE #2: Modifying original data in PostToolUse
    -----------------------------------------------------------------------
    def posttooluse_hook(tool_name, result):
        # WRONG: Mutating original!
        result["normalized"] = True
        return result
    -----------------------------------------------------------------------
    WHY IT BREAKS: Side effects, breaks audit trail.
    FIX: Always copy: result = result.copy() before modifying.

    MISTAKE #3: Forgetting to handle unknown tools
    -----------------------------------------------------------------------
    def pretooluse_hook(tool_name, params):
        if tool_name == "expected_tool":
            return {"allowed": True}
        # Unknown tool falls through - might be blocked or allowed!
    -----------------------------------------------------------------------
    WHY IT BREAKS: Unpredictable behavior for new tools.
    FIX: Handle explicitly: return {"allowed": True} for unknown.

    MISTAKE #4: Not returning required_action for blocked ops
    -----------------------------------------------------------------------
    def pretooluse_hook(tool_name, params):
        if something_wrong:
            return {"allowed": False, "error": "BLOCKED"}
        # No message about what to do next!
    -----------------------------------------------------------------------
    WHY IT BREAKS: Agent doesn't know how to recover.
    FIX: Always include "required_action" so agent knows next step.

===========================================================================
 INTERVIEW Q&A: Expert Answer Frameworks
===========================================================================

    Q1: "How do PreToolUse and PostToolUse work together?"
    ----------------------------------------------------------------
    TEMPLATE:
    "They serve complementary purposes:

    PRETOOLUSE (BEFORE):
    - Gatekeeper function
    - Runs before tool execution
    - Can block, modify, or redirect
    - Enforces policy and prerequisites

    POSTTOOLUSE (AFTER):
    - Normalizer function
    - Runs after tool execution
    - Cannot block (action already happened)
    - Transforms output for consistency

    Example workflow:
    1. Agent calls transfer_funds
    2. PreToolUse checks AML, account balance
       - BLOCK if checks fail
       - MODIFY params if needed
       - ALLOW if all pass
    3. Tool executes (if allowed)
    4. PostToolUse transforms output
       - Normalize currency formatting
       - Add transaction metadata
       - Format for display

    Together: PreToolUse = guard, PostToolUse = translator"

    ----------------------------------------------------------------

    Q2: "Design a hook system for a financial trading agent"
    ----------------------------------------------------------------
    TEMPLATE:
    "I would implement multiple layers:

    LAYER 1 - Identity (PreToolUse):
    - verify_trader() always allowed
    - All other ops check session.verified

    LAYER 2 - Account Status (PreToolUse):
    - Check account status (active, suspended, margin call)
    - Block if account restricted

    LAYER 3 - Position Limits (PreToolUse):
    - Check proposed position against limits
    - Block if would exceed daily/single limits

    LAYER 4 - Risk Checks (PreToolUse):
    - Check sector concentration
    - Check correlation with existing positions
    - Flag high-risk trades for review

    LAYER 5 - Execution (PostToolUse):
    - Normalize price data
    - Add execution metadata
    - Log for compliance

    KEY: Multiple PreToolUse checks, one PostToolUse normalizer"

    ----------------------------------------------------------------

    Q3: "Can you use both PreToolUse and PostToolUse for the same tool?"
    ----------------------------------------------------------------
    TEMPLATE:
    "Yes - and you often should for complete coverage:

    Same tool, both hooks:
    1. PreToolUse: Enforce prerequisites (BEFORE)
    2. Tool executes (if allowed)
    3. PostToolUse: Transform output (AFTER)

    Example for get_order:
    - PreToolUse: Require customer verified
    - Tool: Return order data
    - PostToolUse: Normalize dates, add display fields

    Each operates at different times:
    - PreToolUse: Can prevent execution
    - PostToolUse: Cannot prevent, can only transform output"

===========================================================================
 CODE PATTERN: Complete Template
===========================================================================

    # =======================================================================
    # STEP 1: Define Your Session State
    # =======================================================================

    class SessionState:
        """Session state for tracking verification, compliance, etc."""

        def __init__(self):
            self.verified_customers = set()
            self.aml_verified = set()
            self.completed_steps = set()

        def verify_customer(self, customer_id):
            self.verified_customers.add(customer_id)

        def is_verified(self, customer_id):
            return customer_id in self.verified_customers

        def verify_aml(self, customer_id):
            self.aml_verified.add(customer_id)

        def is_aml_verified(self, customer_id):
            return customer_id in self.aml_verified

    session = SessionState()

    # =======================================================================
    # STEP 2: Define Your Tools
    # =======================================================================

    tools = [
        {
            "name": "get_customer",
            "description": "Get customer information and verify identity",
            "input_schema": {
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string"}
                },
                "required": ["customer_id"]
            }
        },
        {
            "name": "process_refund",
            "description": "Process a refund - financial operation",
            "input_schema": {...}
        },
        {
            "name": "transfer_funds",
            "description": "Transfer funds - requires AML compliance",
            "input_schema": {...}
        }
    ]

    # =======================================================================
    # STEP 3: Implement PRETOOLUSE Hook (BEFORE execution)
    # =======================================================================

    def pretooluse_hook(tool_name, params):
        """
        PreToolUse hook - runs BEFORE tool execution.
        Returns: {"allowed": bool, "error"?: str, "message"?: str,
                  "required_action"?: str}
        """
        # Entry point - always allowed
        if tool_name == "get_customer":
            return {"allowed": True}

        # Requires verification
        if tool_name in ("lookup_order", "process_refund"):
            customer_id = params.get("customer_id")
            if not session.is_verified(customer_id):
                return {
                    "allowed": False,
                    "error": "CUSTOMER_NOT_VERIFIED",
                    "message": "Must verify customer first",
                    "required_action": "get_customer"
                }

        # Financial operation - check amount limit
        if tool_name == "process_refund":
            amount = params.get("amount", 0)
            if amount > 5000:
                return {
                    "allowed": False,
                    "error": "AMOUNT_EXCEEDS_LIMIT",
                    "message": "Refunds over $5,000 require approval",
                    "required_action": "escalate_to_manager"
                }

        # Compliance - requires AML
        if tool_name == "transfer_funds":
            if not session.is_aml_verified(params.get("customer_id")):
                return {
                    "allowed": False,
                    "error": "AML_REQUIRED",
                    "message": "AML verification required",
                    "required_action": "complete_aml_verification"
                }

        return {"allowed": True}

    # =======================================================================
    # STEP 4: Implement POSTTOOLUSE Hook (AFTER execution)
    # =======================================================================

    def posttooluse_hook(tool_name, raw_result):
        """
        PostToolUse hook - runs AFTER tool execution.
        Can only transform - CANNOT block!
        """
        result = raw_result.copy()  # Always copy!

        if tool_name == "get_customer":
            from datetime import datetime
            result["retrieved_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            result["verified"] = True

        elif tool_name == "lookup_order":
            if "amount" in result:
                result["amount_display"] = f"${result['amount']:.2f}"

        elif tool_name == "process_refund":
            result["refund_id"] = f"REF-{result.get('order_id', 'UNKNOWN')}"
            result["status"] = "COMPLETED"

        return result

    # =======================================================================
    # STEP 5: Execute Tool with Hooks
    # =======================================================================

    def execute_tool(tool_name, params):
        # 1. Run PreToolUse
        precheck = pretooluse_hook(tool_name, params)
        if not precheck["allowed"]:
            return {"success": False, "error": precheck["error"]}

        # 2. Execute tool
        result = tool_implementation(tool_name, params)

        # 3. Run PostToolUse
        transformed = posttooluse_hook(tool_name, result)

        return {"success": True, "data": transformed}

===========================================================================
 WHAT WE HAVE LEARNT SUMMARY
===========================================================================

    +======================================================================+
    ||                                                                  ||
    ||              WHAT WE HAVE LEARNT                                 ||
    ||              =====================                                 ||
    ||                                                                  ||
    +======================================================================+

    1. HOOK ARCHITECTURE:
       - PreLogToolUse: Before execution, can block
       - PostToolUse: After execution, cannot block
       - Work together for complete coverage

    2. PRETOOLUSE PATTERNS:
       - Verification gate (require customer verified)
       - Amount limits (check before executing)
       - Compliance checks (AML, KYC)
       - Entry points (always allowed)

    3. POSTTOOLUSE PATTERNS:
       - Data normalization (format dates, prices)
       - Metadata addition (timestamps, IDs)
       - Status translation (codes to readable strings)
       - Always copy before modifying

    4. KEY DECISIONS:
       - Financial/legal/security --> Use PreToolUse
       - Data formatting/styling --> Use PostToolUse or Prompts
       - Need 100% guarantee? --> Hooks
       - ~90% acceptable? --> Prompts

    5. COMMON PATTERNS:
       - Entry points always allowed
       - Financial ops require verification
       - All tools normalized to consistent format

    COPY THIS TEMPLATE AND CUSTOMIZE!

    +======================================================================+
    ||                                                                  ||
    ||                    TEMPLATE COMPLETE!                             ||
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


# =======================================================================
# STEP 1: Define Your Session State
# =======================================================================

class SessionState:
    """Session state for tracking verification, compliance, etc."""

    def __init__(self):
        self.verified_customers = set()
        self.aml_verified = set()
        self.completed_steps = set()

    def verify_customer(self, customer_id):
        self.verified_customers.add(customer_id)

    def is_verified(self, customer_id):
        return customer_id in self.verified_customers

    def verify_aml(self, customer_id):
        self.aml_verified.add(customer_id)

    def is_aml_verified(self, customer_id):
        return customer_id in self.aml_verified

    def mark_step_complete(self, step):
        self.completed_steps.add(step)

    def is_step_complete(self, step):
        return step in self.completed_steps


session = SessionState()


# =======================================================================
# STEP 2: Define Your Tools
# =======================================================================

tools = [
    {
        "name": "get_customer",
        "description": "Get customer information and verify identity",
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "string", "description": "Customer ID"}
            },
            "required": ["customer_id"]
        }
    },
    {
        "name": "lookup_order",
        "description": "Lookup order details",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "Order ID"},
                "customer_id": {"type": "string", "description": "Customer ID"}
            },
            "required": ["order_id", "customer_id"]
        }
    },
    {
        "name": "process_refund",
        "description": "Process a refund - financial operation",
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "string"},
                "order_id": {"type": "string"},
                "amount": {"type": "number"}
            },
            "required": ["customer_id", "order_id", "amount"]
        }
    },
    {
        "name": "transfer_funds",
        "description": "Transfer funds - requires AML compliance",
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "string"},
                "amount": {"type": "number"},
                "destination": {"type": "string"}
            },
            "required": ["customer_id", "amount", "destination"]
        }
    }
]


# =======================================================================
# STEP 3: Implement PRETOOLUSE Hooks (BEFORE execution)
# =======================================================================

def pretooluse_hook(tool_name, params):
    """
    PreToolUse hook - runs BEFORE tool execution.
    Use this to enforce policy, block unauthorized actions, check prerequisites.

    Returns: {"allowed": bool, "error"?: str, "message"?: str}
    """
    # =======================================================================
    # Add your policy checks here
    # =======================================================================

    # Example: get_customer is always allowed (first step)
    if tool_name == "get_customer":
        return {"allowed": True}

    # Example: lookup_order requires customer verification
    if tool_name == "lookup_order":
        customer_id = params.get("customer_id")
        if not session.is_verified(customer_id):
            return {
                "allowed": False,
                "error": "CUSTOMER_NOT_VERIFIED",
                "message": "Must verify customer with get_customer first"
            }
        return {"allowed": True}

    # Example: process_refund requires verification + amount limit
    if tool_name == "process_refund":
        customer_id = params.get("customer_id")
        amount = params.get("amount", 0)

        # Check customer verification
        if not session.is_verified(customer_id):
            return {
                "allowed": False,
                "error": "CUSTOMER_NOT_VERIFIED",
                "message": "Must verify customer first"
            }

        # Check amount limit
        if amount > 5000:
            return {
                "allowed": False,
                "error": "AMOUNT_EXCEEDS_LIMIT",
                "message": "Refunds over $5,000 require manager approval"
            }

        return {"allowed": True}

    # Example: transfer_funds requires AML compliance
    if tool_name == "transfer_funds":
        customer_id = params.get("customer_id")

        if not session.is_aml_verified(customer_id):
            return {
                "allowed": False,
                "error": "AML_REQUIRED",
                "message": "AML verification required before transfers"
            }

        return {"allowed": True}

    # Default: allow unknown tools (but you should add checks!)
    return {"allowed": True}


# =======================================================================
# STEP 4: Implement POSTTOOLUSE Hooks (AFTER execution)
# =======================================================================

def posttooluse_hook(tool_name, raw_result):
    """
    PostToolUse hook - runs AFTER tool execution, BEFORE model sees result.
    Use this to normalize data, add metadata, transform output.

    The tool already executed - this is for transformation, not blocking!
    """
    result = raw_result.copy()

    # =======================================================================
    # Add your transformations here
    # =======================================================================

    # Example: Add timestamp to customer data
    if tool_name == "get_customer":
        from datetime import datetime
        result["retrieved_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result["verified"] = True

    # Example: Normalize order data
    elif tool_name == "lookup_order":
        if "amount" in result:
            result["amount_display"] = f"${result['amount']:.2f}"
        if "status" in result:
            status_map = {
                "pending": "Awaiting processing",
                "delivered": "Completed",
                "returned": "Returned"
            }
            result["status_display"] = status_map.get(result["status"], result["status"])

    # Example: Add refund metadata
    elif tool_name == "process_refund":
        result["refund_id"] = f"REF-{result.get('order_id', 'UNKNOWN')}"
        result["status"] = "COMPLETED"

    # Example: Add transfer metadata
    elif tool_name == "transfer_funds":
        result["reference"] = f"TRF-{result.get('transaction_id', 'UNKNOWN')}"
        result["status"] = "COMPLETED"

    return result


# =======================================================================
# STEP 5: Execute Tool with Hooks
# =======================================================================

def execute_tool(tool_name, params):
    """
    Execute a tool with PreToolUse and PostToolUse hooks.

    Pattern:
    1. Run PreToolUse hook (check policy)
    2. If blocked, return error
    3. If allowed, execute tool
    4. Run PostToolUse hook (transform result)
    5. Return transformed result
    """
    print(f"\n   [HOOKS] Executing {tool_name}...")

    # PRETOOLUSE: Check policy
    precheck = pretooluse_hook(tool_name, params)

    if not precheck["allowed"]:
        print(f"   [PRETOOLUSE] BLOCKED: {precheck['error']}")
        return {
            "success": False,
            "error": precheck["error"],
            "message": precheck["message"]
        }

    print(f"   [PRETOOLUSE] Allowed")

    # Execute tool (your implementation here)
    # For demo, we simulate execution
    if tool_name == "get_customer":
        session.verify_customer(params["customer_id"])
        result = {
            "customer_id": params["customer_id"],
            "name": f"Customer {params['customer_id']}",
            "status": "active"
        }
    elif tool_name == "lookup_order":
        result = {
            "order_id": params["order_id"],
            "amount": 299.99,
            "status": "delivered"
        }
    elif tool_name == "process_refund":
        result = {
            "order_id": params["order_id"],
            "amount": params["amount"],
            "status": "processed"
        }
    elif tool_name == "transfer_funds":
        result = {
            "transaction_id": "TX12345",
            "amount": params["amount"],
            "status": "completed"
        }
    else:
        result = {"error": "Unknown tool"}

    # POSTTOOLUSE: Transform result
    transformed = posttooluse_hook(tool_name, result)
    print(f"   [POSTTOOLUSE] Transformed")

    return {
        "success": True,
        "data": transformed
    }


# =======================================================================
# MAIN: Demo
# =======================================================================

if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    print("\n" + "=" * 70)
    print("AGENT SDK HOOKS - TEMPLATE")
    print("=" * 70)
    print("""
    This template provides a starting point for implementing
    PreToolUse and PostToolUse hooks in your agents.

    Key patterns:
    1. PreToolUse: Enforce policy BEFORE execution (can block)
    2. PostToolUse: Transform data AFTER execution (cannot block)

    Copy and customize for your use case!
    """)

    # Demo: Correct flow
    print("\n" + "-" * 60)
    print("DEMO: Correct Flow with Hooks")
    print("-" * 60)

    print("\n[1] Get customer (always allowed)")
    result = execute_tool("get_customer", {"customer_id": "CUST-123"})
    print(f"   Result: {result['success']}")

    print("\n[2] Lookup order (requires verification)")
    result = execute_tool("lookup_order", {"order_id": "ORD-456", "customer_id": "CUST-123"})
    print(f"   Result: {result['success']}")

    print("\n[3] Process refund (requires verification + amount check)")
    result = execute_tool("process_refund", {"customer_id": "CUST-123", "order_id": "ORD-456", "amount": 299.99})
    print(f"   Result: {result['success']}")

    # Demo: Blocked flow
    print("\n" + "-" * 60)
    print("DEMO: Blocked Flow")
    print("-" * 60)

    print("\n[ATTEMPT] Process refund without verification")
    result = execute_tool("process_refund", {"customer_id": "CUST-999", "order_id": "ORD-789", "amount": 500})
    if not result["success"]:
        print(f"   Blocked: {result['error']} - {result['message']}")

    # Demo: AML block
    print("\n" + "-" * 60)
    print("DEMO: AML Compliance Block")
    print("-" * 60)

    print("\n[ATTEMPT] Transfer without AML verification")
    result = execute_tool("transfer_funds", {"customer_id": "CUST-456", "amount": 50000, "destination": "CH"})
    if not result["success"]:
        print(f"   Blocked: {result['error']} - {result['message']}")

    print("""
    +======================================================================+
    ||                                                                  ||
    ||              WHAT WE HAVE LEARNT                                 ||
    ||              =====================                                 ||
    ||                                                                  ||
    +======================================================================+

    1. We implemented PRETOOLUSE hooks:
       - Runs BEFORE tool execution
       - Can block unauthorized operations
       - Returns error with required_action
       - Enforces: verification, amount limits, AML compliance

    2. We implemented POSTTOOLUSE hooks:
       - Runs AFTER tool execution
       - Cannot block (action already happened!)
       - Transform data for consistent format
       - Add metadata, normalize formats

    3. We demonstrated the execution flow:
       - PreToolUse check --> Execute --> PostToolUse transform --> Result

    COPY THIS TEMPLATE and customize!

    REMEMBER:
    - PreToolUse = ENFORCE (before) - can block
    - PostToolUse = TRANSFORM (after) - cannot block
    - Use PreToolUse for: security, compliance, verification
    - Use PostToolUse for: data normalization, metadata
    - Hooks = 100% guarantee, Prompts = ~90% compliance

    +======================================================================+
    ||                                                                  ||
    ||                    TEMPLATE COMPLETE!                             ||
    ||                                                                  ||
    +======================================================================+
    """)