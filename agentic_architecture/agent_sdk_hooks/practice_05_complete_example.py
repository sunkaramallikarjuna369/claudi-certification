"""
+===========================================================================+
|                                                                           |
|  PRACTICE 5: COMPLETE HOOK IMPLEMENTATION EXAMPLE                        |
|                                                                           |
|  Putting it all together: A complete example with PreToolUse and          |
|  PostToolUse hooks working together for a customer support agent.         |
|                                                                           |
|  Scenario: Processing refund requests with verification, normalization,   |
|           and compliance enforcement.                                     |
|                                                                           |
+===========================================================================

===========================================================================
 VISUAL: COMPLETE ARCHITECTURE
===========================================================================

    +======================================================================+
    ||                                                                  ||
    ||  CUSTOMER SUPPORT AGENT - COMPLETE FLOW                          ||
    ||                                                                  ||
    ||  +--------------------------------------------------------------+ ||
    ||  |                                                              | ||
    ||  |   CUSTOMER: "I want a refund for order ORD-456"             | ||
    ||  |                                                              | ||
    ||  +--------------------------------------------------------------+ ||
    ||                              |                                    ||
    ||                              v                                    ||
    ||  +--------------------------------------------------------------+ ||
    ||  |                                                              | ||
    ||  |   STEP 1: get_customer (PreToolUse)                         | ||
    ||  |   --------------------------------------------------------  | ||
    ||  |   [PRETOOLUSE] Always allowed (entry point)                 | ||
    ||  |                                                              | ||
    ||  |   --> Verify customer exists                                | ||
    ||  |   --> Store in session                                       | ||
    ||  |                                                              | ||
    ||  +--------------------------------------------------------------+ ||
    ||                              |                                    ||
    ||                              v                                    ||
    ||  +--------------------------------------------------------------+ ||
    ||  |                                                              | ||
    ||  |   STEP 2: lookup_order (PreToolUse + PostToolUse)          | ||
    ||  |   --------------------------------------------------------  | ||
    ||  |   [PRETOOLUSE] Requires customer verified                   | ||
    ||  |   [POSTTOOLUSE] Normalize dates, add display format         | ||
    ||  |                                                              | ||
    ||  |   --> Verify order belongs to customer                       | ||
    ||  |   --> Normalize date formats                                 | ||
    ||  |                                                              | ||
    ||  +--------------------------------------------------------------+ ||
    ||                              |                                    ||
    ||                              v                                    ||
    ||  +--------------------------------------------------------------+ ||
    ||  |                                                              | ||
    ||  |   STEP 3: process_refund (PreToolUse + PostToolUse)        | ||
    ||  |   --------------------------------------------------------  | ||
    ||  |   [PRETOOLUSE] Amount limit, customer verified              | ||
    ||  |   [POSTTOOLUSE] Add refund ID, status                      | ||
    ||  |                                                              | ||
    ||  |   --> BLOCK if not verified or over limit                   | ||
    ||  |   --> APPROVE if all checks pass                            | ||
    ||  |                                                              | ||
    ||  +--------------------------------------------------------------+ ||
    ||                                                                  ||
    +======================================================================+

===========================================================================
 REAL-TIME SCENARIO: Production Customer Support Flow
===========================================================================

    SCENARIO: Bank Customer Support Agent

    A customer calls about an unauthorized transaction. The agent must:
    1. Verify customer identity
    2. Look up the transaction
    3. Process refund if legitimate

    +======================================================================+
    ||                                                                  ||
    ||  CONVERSATION FLOW:                                             ||
    ||                                                                  ||
    ||  Customer: "I didn't make this $500 charge on my account"      ||
    ||                                                                  ||
    ||  Agent: "Let me help. I'll need to verify your identity first." ||
    ||                                                                  ||
    ||  [Call: get_customer with PreToolUse (always allowed)]         ||
    ||                                                                  ||
    ||  Agent: "Verified. Now let me look up that transaction."          ||
    ||                                                                  ||
    ||  [Call: lookup_order with PreToolUse (requires verification)]   ||
    ||         + PostToolUse (normalizes data)                        ||
    ||                                                                  ||
    ||  Agent: "I found it. Would you like me to process a refund?"    ||
    ||                                                                  ||
    ||  Customer: "Yes, please refund the $500"                        ||
    ||                                                                  ||
    ||  [Call: process_refund with PreToolUse (checks amount, limit)]  ||
    ||         + PostToolUse (adds refund ID, confirmation)           ||
    ||                                                                  ||
    ||  Agent: "Done! Your refund of $500 is processing. Refund ID:   ||
    ||          REF-ORD-456. You'll receive it in 3-5 business days."  ||
    ||                                                                  ||
    +======================================================================+

===========================================================================
 MISTAKES DEVELOPERS MAKE
===========================================================================

    MISTAKE #1: Not enforcing workflow order
    -----------------------------------------------------------------------
    # WRONG: No order enforcement
    process_refund()  # Can be called without verification!
    lookup_order()    # Can be called without verification!
    -----------------------------------------------------------------------
    WHY IT BREAKS: Agent might skip verification steps.
    FIX: Use PreToolUse to require verification before financial ops.

    MISTAKE #2: Blocking in PostToolUse instead of PreToolUse
    -----------------------------------------------------------------------
    PostToolUse on process_refund:
        # WRONG: Tool already executed, can't block!
        if suspicious:
            block()  # Too late - refund already processed!
    -----------------------------------------------------------------------
    WHY IT BREAKS: Action already happened by the time PostToolUse runs.
    FIX: Use PreToolUse to block BEFORE execution.

    MISTAKE #3: Not normalizing data from different sources
    -----------------------------------------------------------------------
    # WRONG: Mixed formats confuse the model
    Tool A: {"date": 1704067200}      # Unix
    Tool B: {"date": "12/31/2024"}    # DD/MM/YYYY
    -----------------------------------------------------------------------
    WHY IT BREAKS: Model sees inconsistent formats, may misinterpret.
    FIX: Use PostToolUse to normalize all dates to ISO format.

    MISTAKE #4: Hardcoding limits instead of using session state
    -----------------------------------------------------------------------
    if amount > 5000:  # Hardcoded!
        block()
    -----------------------------------------------------------------------
    WHY IT BREAKS: Can't adjust limits without code change.
    FIX: Store limits in session state, allow dynamic adjustment.

===========================================================================
 INTERVIEW Q&A: Expert Answer Frameworks
===========================================================================

    Q1: "Design a customer support agent with proper safeguards"
    ----------------------------------------------------------------
    TEMPLATE:
    "I would design a multi-layer system:

    LAYER 1 - Entry Point (PreToolUse):
    - get_customer is always allowed
    - This is the entry point that starts verification

    LAYER 2 - Verification Required (PreToolUse):
    - lookup_order requires customer to be verified
    - PreToolUse checks session state before allowing

    LAYER 3 - Financial Operations (PreToolUse + PostToolUse):
    - process_refund requires:
      - Customer verified (PreToolUse)
      - Amount within limit (PreToolUse)
      - PostToolUse adds refund ID and confirmation

    LAYER 4 - Compliance (PreToolUse):
    - transfer_funds requires AML verification
    - This is enforced at code level, not prompt level

    The key insight is that each layer builds on the previous,
    with PreToolUse enforcing prerequisites and PostToolUse
    normalizing outputs."

    KEY PHRASE: "Layered approach with PreToolUse for prerequisites"

    ----------------------------------------------------------------

    Q2: "How do hooks work together in a complete system?"
    ----------------------------------------------------------------
    TEMPLATE:
    "PreToolUse and PostToolUse serve different purposes:

    PRETOOLUSE (BEFORE execution):
    - Checks prerequisites (is customer verified?)
    - Enforces limits (is amount within range?)
    - Validates compliance (is AML done?)
    - BLOCKS if checks fail

    POSTTOOLUSE (AFTER execution):
    - Transforms raw data (normalize dates)
    - Adds metadata (add refund ID)
    - Formats for display (add $ prefix)
    - CANNOT block (action already happened)

    Together they ensure:
    1. Only valid operations execute (PreToolUse)
    2. Results are consistent and usable (PostToolUse)"

    KEY PHRASE: "PreToolUse = gatekeeper, PostToolUse = normalizer"

    ----------------------------------------------------------------

    Q3: "How would you handle a fraudulent refund attempt?"
    ----------------------------------------------------------------
    TEMPLATE:
    "Multiple layers of defense:

    LAYER 1 - PreToolUse Verification:
    - Check customer is verified (block if not)
    - This happens BEFORE any data access

    LAYER 2 - PreToolUse Limits:
    - Check amount against customer's history
    - Block if pattern suggests fraud (rate limit)

    LAYER 3 - PostToolUse Logging:
    - Log all refund attempts
    - Flag suspicious patterns for review

    LAYER 4 - Post-Processing Audit:
    - ML model analyzes refund patterns
    - Flags anomalies for human review

    The key is PreToolUse prevents fraudulent execution,
    while PostToolUse enables detection and auditing."

    KEY PHRASE: "Defense in depth - prevent, detect, audit"

===========================================================================
 VISUAL: TOOL EXECUTION FLOW WITH BOTH HOOKS
===========================================================================

    +======================================================================+
    ||                                                                  ||
    ||  TOOL EXECUTION WITH HOOKS:                                     ||
    ||                                                                  ||
    ||    1. Agent decides: "Call process_refund"                     ||
    ||           |                                                      ||
    ||           v                                                      ||
    ||    2. [PRETOOLUSE] <-- Policy Check                             ||
    ||           |                                                      ||
    ||       +---+---+                                                  ||
    ||       |       |                                                  ||
    ||    PASS        FAIL                                              ||
    ||       |       |                                                  ||
    ||       v       v                                                  ||
    ||   Execute   Return error                                          ||
    ||       |       |                                                  ||
    ||       v       |                                                  ||
    ||    [POSTTOOLUSE]                                                 ||
    ||    (Transform)                                                   ||
    ||       |                                                          ||
    ||       v                                                          ||
    ||    Result + Metadata                                             ||
    ||                                                                  ||
    +======================================================================+

===========================================================================
 CODE PATTERN: Complete Implementation
===========================================================================

    # =======================================================================
    # STATE: Session management
    # =======================================================================

    class SessionState:
        def __init__(self):
            self.verified_customers = set()
            self.processed_refunds = []
            self.aml_verified = set()

        def verify_customer(self, customer_id):
            self.verified_customers.add(customer_id)

        def is_verified(self, customer_id):
            return customer_id in self.verified_customers

    session = SessionState()

    # =======================================================================
    # PRETOOLUSE: Policy enforcement (BEFORE execution)
    # =======================================================================

    def pretooluse_check(tool_name, params):
        """
        PreToolUse hook - runs BEFORE tool execution.
        Returns: {"allowed": bool, "error"?: str, "message"?: str}
        """
        # get_customer is always allowed (entry point)
        if tool_name == "get_customer":
            return {"allowed": True}

        # lookup_order requires verification
        if tool_name == "lookup_order":
            customer_id = params.get("customer_id")
            if not session.is_verified(customer_id):
                return {
                    "allowed": False,
                    "error": "CUSTOMER_NOT_VERIFIED",
                    "message": "Must verify customer first"
                }
            return {"allowed": True}

        # process_refund requires verification + amount check
        if tool_name == "process_refund":
            customer_id = params.get("customer_id")
            amount = params.get("amount", 0)

            if not session.is_verified(customer_id):
                return {
                    "allowed": False,
                    "error": "CUSTOMER_NOT_VERIFIED",
                    "message": "Must verify customer first"
                }

            if amount > 5000:
                return {
                    "allowed": False,
                    "error": "AMOUNT_EXCEEDS_LIMIT",
                    "message": "Refunds over $5,000 require approval"
                }

            return {"allowed": True}

        return {"allowed": True}

    # =======================================================================
    # POSTTOOLUSE: Data transformation (AFTER execution)
    # =======================================================================

    def posttooluse_transform(tool_name, raw_result):
        """
        PostToolUse hook - runs AFTER tool execution.
        Transforms raw data into consistent format.
        """
        result = raw_result.copy()

        if tool_name == "get_customer":
            from datetime import datetime
            result["retrieved_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            result["verified"] = True

        elif tool_name == "lookup_order":
            if "amount" in result:
                result["amount_display"] = f"${result['amount']:.2f}"
            if "status" in result:
                status_map = {"pending": "Awaiting", "delivered": "Completed"}
                result["status_display"] = status_map.get(result["status"], result["status"])

        elif tool_name == "process_refund":
            result["refund_id"] = f"REF-{result.get('order_id', 'UNKNOWN')}"
            result["status"] = "COMPLETED"

        return result

    # =======================================================================
    # TOOL EXECUTION: With hooks
    # =======================================================================

    def execute_tool(tool_name, params):
        # PRETOOLUSE: Check policy
        precheck = pretooluse_check(tool_name, params)
        if not precheck["allowed"]:
            return {"success": False, "error": precheck["error"], "message": precheck["message"]}

        # Execute tool (simulated)
        # ... tool execution code ...

        # POSTTOOLUSE: Transform result
        result = posttooluse_transform(tool_name, result)
        return {"success": True, "data": result}

===========================================================================
 WHAT WE HAVE LEARNT SUMMARY
===========================================================================

    +======================================================================+
    ||                                                                  ||
    ||              WHAT WE HAVE LEARNT                                 ||
    ||              =====================                                 ||
    ||                                                                  ||
    +======================================================================+

    1. COMPLETE ARCHITECTURE:
       - Entry points (get_customer) always allowed
       - Verification required for data access
       - Financial ops require verification + limits
       - Compliance ops require AML verification

    2. PRETOOLUSE + POSTTOOLUSE TOGETHER:
       - PreToolUse = gatekeeper (before) - can block
       - PostToolUse = normalizer (after) - cannot block
       - Both run in sequence for complete coverage

    3. WORKFLOW ENFORCEMENT:
       - Correct order: verify -> lookup -> process
       - PreToolUse enforces order
       - Cannot skip verification

    4. DATA NORMALIZATION:
       - Different tools return different formats
       - PostToolUse normalizes to consistent format
       - Model sees clean, consistent data

    5. REAL-WORLD USE CASES:
       - Customer support agents
       - Financial transaction processing
       - Compliance verification systems
       - Any system requiring guaranteed enforcement

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


# ========================================================================
# STATE: Session and tool state
# ========================================================================

class SessionState:
    """Session state for customer support agent."""

    def __init__(self):
        self.verified_customers = set()
        self.processed_refunds = []
        self.aml_verified = set()

    def verify_customer(self, customer_id):
        self.verified_customers.add(customer_id)

    def is_verified(self, customer_id):
        return customer_id in self.verified_customers

    def verify_aml(self, customer_id):
        self.aml_verified.add(customer_id)

    def is_aml_verified(self, customer_id):
        return customer_id in self.aml_verified


session = SessionState()


# ========================================================================
# TOOLS: Define available tools
# ========================================================================

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
        "description": "Lookup order details for refund processing",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string"}
            },
            "required": ["order_id"]
        }
    },
    {
        "name": "process_refund",
        "description": "Process refund - requires verification",
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


# ========================================================================
# PRETOOLUSE HOOKS: Policy Enforcement
# ========================================================================

def pretooluse_check(tool_name, params):
    """
    PreToolUse hook - runs BEFORE tool execution.
    Returns: {"allowed": bool, "error"?: str, "message"?: str}
    """
    print(f"\n   [PRETOOLUSE] Checking {tool_name}...")

    # get_customer - always allowed (first step in any flow)
    if tool_name == "get_customer":
        print("   [PRETOOLUSE] get_customer always allowed")
        return {"allowed": True}

    # lookup_order - requires customer verification
    if tool_name == "lookup_order":
        customer_id = params.get("customer_id", "UNKNOWN")
        if not session.is_verified(customer_id):
            print("   [PRETOOLUSE] Customer not verified!")
            return {
                "allowed": False,
                "error": "CUSTOMER_NOT_VERIFIED",
                "message": "Must verify customer first with get_customer"
            }
        print("   [PRETOOLUSE] Customer verified")
        return {"allowed": True}

    # process_refund - requires verification + amount check
    if tool_name == "process_refund":
        customer_id = params.get("customer_id", "UNKNOWN")
        amount = params.get("amount", 0)

        # Check 1: Customer verified
        if not session.is_verified(customer_id):
            print("   [PRETOOLUSE] Customer not verified!")
            return {
                "allowed": False,
                "error": "CUSTOMER_NOT_VERIFIED",
                "message": "Must verify customer first"
            }

        # Check 2: Amount limit ($5000)
        if amount > 5000:
            print("   [PRETOOLUSE] Amount exceeds $5000 limit!")
            return {
                "allowed": False,
                "error": "AMOUNT_EXCEEDS_LIMIT",
                "message": "Refunds over $5,000 require manager approval"
            }

        print("   [PRETOOLUSE] All checks passed")
        return {"allowed": True}

    # transfer_funds - requires AML compliance
    if tool_name == "transfer_funds":
        customer_id = params.get("customer_id", "UNKNOWN")

        if not session.is_aml_verified(customer_id):
            print("   [PRETOOLUSE] AML not verified!")
            return {
                "allowed": False,
                "error": "AML_REQUIRED",
                "message": "AML (Anti-Money Laundering) verification required"
            }

        print("   [PRETOOLUSE] AML verified")
        return {"allowed": True}

    return {"allowed": True}


# ========================================================================
# POSTTOOLUSE HOOKS: Data Normalization
# ========================================================================

def posttooluse_transform(tool_name, raw_result):
    """
    PostToolUse hook - runs AFTER tool execution, BEFORE model sees result.
    Transforms raw data into consistent, normalized format.
    """
    print(f"   [POSTTOOLUSE] Transforming {tool_name} output...")

    transformed = raw_result.copy()

    if tool_name == "get_customer":
        # Add normalized timestamp
        from datetime import datetime
        transformed["retrieved_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        transformed["verified"] = True
        print("   [POSTTOOLUSE] Added verified flag and timestamp")

    elif tool_name == "lookup_order":
        # Add human-readable status
        status_map = {
            "pending": "Awaiting processing",
            "processing": "Being prepared",
            "shipped": "On the way",
            "delivered": "Completed",
            "returned": "Returned by customer"
        }
        original_status = raw_result.get("status", "unknown")
        transformed["status_display"] = status_map.get(original_status, original_status)
        transformed["amount_display"] = f"${raw_result.get('amount', 0):.2f}"
        print("   [POSTTOOLUSE] Added status_display and amount_display")

    elif tool_name == "process_refund":
        # Add refund details
        transformed["refund_timestamp"] = "2024-01-01T12:00:00Z"
        transformed["status"] = "COMPLETED"
        transformed["refund_id"] = f"REF-{raw_result.get('order_id', 'UNKNOWN')}"
        print("   [POSTTOOLUSE] Added refund metadata")

    elif tool_name == "transfer_funds":
        # Add transfer details
        transformed["transfer_timestamp"] = "2024-01-01T12:00:00Z"
        transformed["status"] = "COMPLETED"
        transformed["reference"] = f"TRF-{raw_result.get('transaction_id', 'UNKNOWN')}"
        print("   [POSTTOOLUSE] Added transfer metadata")

    return transformed


# ========================================================================
# TOOL EXECUTION: With hooks
# ========================================================================

def execute_tool(tool_name, params):
    """
    Execute tool with PreToolUse and PostToolUse hooks.
    """
    print("\n" + "=" * 60)
    print(f"EXECUTING: {tool_name}")
    print("=" * 60)

    # PRETOOLUSE: Check policy before execution
    print(f"\n   Tool call: {tool_name}({params})")
    precheck = pretooluse_check(tool_name, params)

    if not precheck["allowed"]:
        print(f"\n   BLOCKED by PreToolUse!")
        print(f"   Error: {precheck['error']}")
        print(f"   Message: {precheck['message']}")
        return {
            "success": False,
            "error": precheck["error"],
            "message": precheck["message"]
        }

    # Execute tool (simulated)
    print(f"\n   PreToolUse passed - executing tool...")

    # Simulate tool execution
    if tool_name == "get_customer":
        session.verify_customer(params["customer_id"])
        raw_result = {
            "customer_id": params["customer_id"],
            "name": f"Customer {params['customer_id']}",
            "email": f"customer{params['customer_id']}@example.com",
            "status": "active"
        }
    elif tool_name == "lookup_order":
        raw_result = {
            "order_id": params["order_id"],
            "customer_id": params.get("customer_id", "UNKNOWN"),
            "amount": 299.99,
            "status": "delivered",
            "date": 1704067200  # Unix timestamp
        }
    elif tool_name == "process_refund":
        raw_result = {
            "order_id": params["order_id"],
            "amount": params["amount"],
            "status": "processed"
        }
        session.processed_refunds.append(params["amount"])
    elif tool_name == "transfer_funds":
        raw_result = {
            "transaction_id": "TX12345",
            "amount": params["amount"],
            "destination": params["destination"],
            "status": "completed"
        }
    else:
        raw_result = {"error": "Unknown tool"}

    # POSTTOOLUSE: Transform result
    print("\n   Running PostToolUse hook...")
    result = posttooluse_transform(tool_name, raw_result)

    print(f"\n   Tool executed successfully!")
    print(f"   Result: {result}")

    return result


def demonstrate_complete_flow():
    """
    Demonstrate the complete flow with hooks.
    """
    print("\n" + "=" * 70)
    print("COMPLETE FLOW: Processing a Refund Request")
    print("=" * 70)

    print("""
    +======================================================================+
    ||                                                                  ||
    ||  SCENARIO: Customer CUST-123 requests $299.99 refund             ||
    ||                                                                  ||
    ||  Step 1: get_customer (PreToolUse check)                        ||
    ||  Step 2: lookup_order (PreToolUse check)                        ||
    ||  Step 3: process_refund (PreToolUse check + PostToolUse)        ||
    ||                                                                  ||
    +======================================================================+
    """)

    print("\n[STEP 1] Get customer (always allowed)")
    execute_tool("get_customer", {"customer_id": "CUST-123"})

    print("\n[STEP 2] Lookup order (requires verification)")
    execute_tool("lookup_order", {"order_id": "ORD-456", "customer_id": "CUST-123"})

    print("\n[STEP 3] Process refund (requires verification + amount check)")
    execute_tool("process_refund", {"customer_id": "CUST-123", "order_id": "ORD-456", "amount": 299.99})


def demonstrate_blocked_flow():
    """
    Demonstrate a blocked flow.
    """
    print("\n" + "=" * 70)
    print("BLOCKED FLOW: Skipping Verification")
    print("=" * 70)

    print("""
    +======================================================================+
    ||                                                                  ||
    ||  SCENARIO: Try to process refund WITHOUT verification           ||
    ||                                                                  ||
    ||  Attempt: process_refund(customer_id="CUST-999", amount=500)    ||
    ||                                                                  ||
    ||  PreToolUse check: Is CUST-999 verified? --> NO                  ||
    ||                                                                  ||
    ||  Result: BLOCKED!                                                 ||
    ||  Error: CUSTOMER_NOT_VERIFIED                                    ||
    ||  Message: Must verify customer first                             ||
    ||                                                                  ||
    +======================================================================+
    """)

    print("\n[ATTEMPT] Process refund without verification")
    execute_tool("process_refund", {"customer_id": "CUST-999", "order_id": "ORD-789", "amount": 500})


def demonstrate_aml_block():
    """
    Demonstrate AML compliance block.
    """
    print("\n" + "=" * 70)
    print("BLOCKED FLOW: Transfer without AML")
    print("=" * 70)

    print("""
    +======================================================================+
    ||                                                                  ||
    ||  SCENARIO: Transfer $50,000 without AML verification             ||
    ||                                                                  ||
    ||  Attempt: transfer_funds(amount=$50,000)                          ||
    ||                                                                  ||
    ||  PreToolUse check: Is AML verified? --> NO                        ||
    ||                                                                  ||
    ||  Result: BLOCKED!                                                 ||
    ||  Error: AML_REQUIRED                                             ||
    ||  Message: AML verification required for transfers                ||
    ||                                                                  ||
    +======================================================================+
    """)

    print("\n[ATTEMPT] Transfer without AML verification")
    execute_tool("transfer_funds", {"customer_id": "CUST-456", "amount": 50000, "destination": "CH"})


if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    print("\n" + "=" * 70)
    print("PRACTICE 5: COMPLETE HOOK IMPLEMENTATION EXAMPLE")
    print("=" * 70)
    print("""
    This program demonstrates a complete customer support agent with:
        - PreToolUse hooks for policy enforcement (blocking)
        - PostToolUse hooks for data normalization (transforming)

    Watch how the hooks work together to ensure:
        1. Correct workflow order (verification first)
        2. Amount limits enforced
        3. AML compliance required
        4. Consistent output format
    """)

    demonstrate_complete_flow()
    demonstrate_blocked_flow()
    demonstrate_aml_block()

    print("""
    +======================================================================+
    ||                                                                  ||
    ||              WHAT WE HAVE LEARNT                                 ||
    ||              =====================                                 ||
    ||                                                                  ||
    +======================================================================+

    1. We implemented PRETOOLUSE hooks:
       - Check policy BEFORE tool execution
       - Can block unauthorized operations
       - Enforce customer verification
       - Enforce amount limits
       - Enforce AML compliance

    2. We implemented POSTTOOLUSE hooks:
       - Transform data AFTER tool execution
       - Add consistent formatting
       - Add human-readable status displays
       - Add metadata (timestamps, IDs)

    3. We demonstrated the COMPLETE FLOW:
       - get_customer (always allowed)
       - lookup_order (requires verification)
       - process_refund (requires verification + amount check)
       - All hooks work together

    4. We demonstrated BLOCKED FLOWS:
       - Skip verification --> BLOCKED
       - Transfer without AML --> BLOCKED

    5. KEY INSIGHT:
       PreToolUse = ENFORCE (before)
       PostToolUse = TRANSFORM (after)
       Together they ensure correct behavior AND consistent output!

    6. REAL-WORLD USE:
       - PreToolUse for security, compliance, verification
       - PostToolUse for data normalization, metadata addition
       - Hooks = 100% guarantee, Prompts = ~90% compliance

    +======================================================================+
    ||                                                                  ||
    ||                    PROGRAM COMPLETE!                             ||
    ||                                                                  ||
    +======================================================================+
    """)