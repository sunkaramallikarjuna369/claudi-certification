"""
================================================================================
WORKFLOW ENFORCEMENT & HANDOFF - TEMPLATE
================================================================================

Your starting point for building agents with proper enforcement
and structured handoff protocols.
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
# STEP 1: Define Tools with Prerequisite Gates
# ================================================================================

# Prerequisite state tracker
class WorkflowState:
    """Track workflow state for prerequisite gates."""

    def __init__(self):
        self.verified_customers = set()
        self.completed_steps = {}

    def verify_customer(self, customer_id: str):
        self.verified_customers.add(customer_id)

    def is_customer_verified(self, customer_id: str) -> bool:
        return customer_id in self.verified_customers

    def mark_step_complete(self, step_id: str, result: dict):
        self.completed_steps[step_id] = result

    def is_step_complete(self, step_id: str) -> bool:
        return step_id in self.completed_steps


workflow_state = WorkflowState()


def execute_tool(name: str, tool_input: dict) -> dict:
    """
    Execute tool WITH prerequisite gate checking.

    This is the KEY pattern for programmatic enforcement.
    """
    # ===========================================================================
    # GATE: get_customer - no prerequisites
    # ===========================================================================
    if name == "get_customer":
        customer_id = tool_input.get("customer_id")
        print(f"\n   [TOOL] get_customer({customer_id})")
        print("   [GATE] No prerequisites - ALLOWED")

        # Simulate getting customer
        result = {
            "customer_id": customer_id,
            "name": f"Customer {customer_id}",
            "verified": True
        }

        # Mark as verified in state
        workflow_state.verify_customer(customer_id)

        return {"success": True, "data": result}

    # ===========================================================================
    # GATE: lookup_order - requires customer verification
    # ===========================================================================
    elif name == "lookup_order":
        customer_id = tool_input.get("customer_id")
        order_id = tool_input.get("order_id")

        print(f"\n   [TOOL] lookup_order({order_id})")
        print(f"   [GATE] Checking: Customer {customer_id} verified?")

        # PREREQUISITE GATE
        if not workflow_state.is_customer_verified(customer_id):
            print("   [GATE] ❌ BLOCKED - Customer not verified!")
            return {
                "success": False,
                "error": "PREREQUISITE_NOT_MET",
                "message": "Must call get_customer first to verify identity.",
                "required_action": "get_customer",
                "required_params": {"customer_id": customer_id}
            }

        print("   [GATE] ✓ Verified - ALLOWED")

        result = {
            "order_id": order_id,
            "amount": 99.99,
            "status": "delivered"
        }

        workflow_state.mark_step_complete(f"order_{order_id}", result)

        return {"success": True, "data": result}

    # ===========================================================================
    # GATE: process_refund - FINANCIAL operation, requires verification
    # ===========================================================================
    elif name == "process_refund":
        customer_id = tool_input.get("customer_id")
        order_id = tool_input.get("order_id")
        amount = tool_input.get("amount", 0)

        print(f"\n   [TOOL] process_refund(${amount})")
        print("   [GATE] Checking FINANCIAL prerequisites:")

        # PREREQUISITE GATE 1: Customer must be verified
        if not workflow_state.is_customer_verified(customer_id):
            print("   [GATE] ❌ BLOCKED - Customer not verified!")
            return {
                "success": False,
                "error": "PREREQUISITE_NOT_MET",
                "message": "Cannot process refund - customer not verified. Call get_customer first."
            }

        print("   [GATE] ✓ Customer verified")

        # PREREQUISITE GATE 2: Order must exist
        if not workflow_state.is_step_complete(f"order_{order_id}"):
            print("   [GATE] ❌ BLOCKED - Order not verified!")
            return {
                "success": False,
                "error": "PREREQUISITE_NOT_MET",
                "message": "Must lookup order before processing refund."
            }

        print("   [GATE] ✓ Order verified")
        print("   [GATE] ✓ All prerequisites met - PROCESSING REFUND")

        return {
            "success": True,
            "data": {
                "refund_id": f"REF-{order_id}",
                "amount": amount,
                "status": "processed"
            }
        }

    return {"success": False, "error": f"Unknown tool: {name}"}


# ================================================================================
# STEP 2: Define Tools List (for API)
# ================================================================================

tools = [
    {
        "name": "get_customer",
        "description": "Get customer information by ID. Always call this first.",
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
        "description": "Lookup order details. Requires customer verification.",
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "string"},
                "order_id": {"type": "string"}
            },
            "required": ["customer_id", "order_id"]
        }
    },
    {
        "name": "process_refund",
        "description": "Process a refund. FINANCIAL operation - requires verification!",
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "string"},
                "order_id": {"type": "string"},
                "amount": {"type": "number"}
            },
            "required": ["customer_id", "order_id", "amount"]
        }
    }
]


# ================================================================================
# STEP 3: Structured Handoff Function
# ================================================================================

def create_handoff_summary(
    customer_id: str,
    conversation_summary: str,
    root_cause: str,
    recommended_action: str,
    refund_amount: float = None
) -> dict:
    """
    Create a properly structured handoff for human agents.

    REQUIRED fields:
    - customer_id: So human can look up account
    - conversation_summary: Human has NO transcript access
    - root_cause: Human needs context
    - recommended_action: Human needs guidance
    - refund_amount: If financial issue
    """
    return {
        "handoff_type": "ESCALATION",
        "priority": "STANDARD",

        # REQUIRED: Customer identification
        "customer_id": customer_id,

        # REQUIRED: What happened
        "conversation_summary": conversation_summary,

        # REQUIRED: Why it's being escalated
        "root_cause_analysis": root_cause,

        # REQUIRED: What human should do
        "recommended_action": recommended_action,
    }


def demonstrate_enforcement_pattern():
    """
    Demonstrate the complete enforcement pattern.
    """
    print("\n" + "=" * 60)
    print("DEMO: Prerequisite Gate Enforcement")
    print("=" * 60)

    print("\nScenario: Try to skip verification steps")

    # Try to process refund WITHOUT prerequisites
    print("\n[1] Attempting refund without verification...")
    result = execute_tool("process_refund", {
        "customer_id": "123",
        "order_id": "456",
        "amount": 99.99
    })

    print(f"   Result: {result['success']}")
    if not result['success']:
        print(f"   Error: {result.get('message', result.get('error'))}")

    # Correct flow
    print("\n[2] Following correct order...")

    print("\n   Step 1: Get customer...")
    execute_tool("get_customer", {"customer_id": "123"})

    print("\n   Step 2: Lookup order...")
    execute_tool("lookup_order", {"customer_id": "123", "order_id": "456"})

    print("\n   Step 3: Process refund...")
    result = execute_tool("process_refund", {
        "customer_id": "123",
        "order_id": "456",
        "amount": 99.99
    })

    print(f"   Result: {result['success']}")
    if result['success']:
        print(f"   Refund ID: {result['data']['refund_id']}")


def demonstrate_handoff_pattern():
    """
    Demonstrate the structured handoff pattern.
    """
    print("\n" + "=" * 60)
    print("DEMO: Structured Handoff")
    print("=" * 60)

    handoff = create_handoff_summary(
        customer_id="CUST-12345",
        conversation_summary="""
Customer contacted about defective laptop from order #67890.
Agent verified customer identity and order details.
Attempted refund but system error PR-403 occurred.
Issue requires manual intervention.
        """.strip(),
        root_cause="""
Backend inventory-refund sync failure (error PR-403).
Order contains limited-edition item currently out of stock.
        """.strip(),
        recommended_action="""
1. Verify refund eligibility with billing team
2. If approved, manually process $1,299.00 refund
3. Alternatively, offer priority replacement when stock returns
        """.strip(),
        refund_amount=1299.00
    )

    print("\n[HANDOFF SUMMARY]")
    print(f"   Customer ID: {handoff['customer_id']}")
    print(f"   Type: {handoff['handoff_type']}")
    print("\n   Summary: Human can now help immediately!")


# ================================================================================
# MAIN
# ================================================================================

if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    print("\n" + "=" * 70)
    print("WORKFLOW ENFORCEMENT & HANDOFF - TEMPLATE")
    print("=" * 70)
    print("""
This template provides patterns for:
1. Prerequisite gates (programmatic enforcement)
2. Structured handoff protocols (for human escalation)

Key concepts:
- FINANCIAL operations require PROGRAMMATIC enforcement
- Human agents have NO transcript access - handoffs must be complete
- Gates are CODE, not prompts - they work 100% of the time
""")

    demonstrate_enforcement_pattern()
    demonstrate_handoff_pattern()

    print("""
================================================================================
WHAT JUST HAPPENED?
================================================================================

    1. We saw PREREQUISITE GATE implementation:
       - execute_tool() checks prerequisites BEFORE execution
       - Returns clear error if prerequisites not met
       - Describes what action is required
       - Works 100% (not probabilistic like prompts)

    2. We saw STRUCTURED HANDOFF implementation:
       - create_handoff_summary() with required fields
       - customer_id, summary, root cause, recommended action
       - refund_amount for financial issues
       - Human can immediately help without re-asking

    COPY THIS TEMPLATE and customize for your use case!

    REMEMBER:
    - High-stakes ops (financial, security, compliance) → Programmatic gates
    - Handoffs MUST include all required fields
    - Human agents have NO transcript access
    - Gates are CODE, not prompts
================================================================================
""")
    print("\n" + "=" * 70)
    print("TEMPLATE COMPLETE!")
    print("=" * 70)
