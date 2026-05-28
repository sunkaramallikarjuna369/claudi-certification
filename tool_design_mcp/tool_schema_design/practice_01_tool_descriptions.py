"""
+===========================================================================+
|                                                                           |
|  PRACTICE 1: TOOL SCHEMA DESIGN & DESCRIPTIONS                           |
|                                                                           |
|  Learn how to write production-grade tool descriptions that Claude      |
|  can understand and use correctly!                                       |
|                                                                           |
|  + REAL-TIME SCENARIOS + MISTAKES DEVELOPERS MAKE + INTERVIEW Q&A      |
|                                                                           |
+===========================================================================

INTERVIEW PREP: "How do you design effective tool schemas for AI agents?"
This tests your understanding of tool selection and schema design.

REAL-TIME SCENARIO: Your customer service AI keeps misrouting requests.
Customers asking about orders get connected to identity verification.
The root cause? Poor tool descriptions!

===========================================================================
WHY TOOL DESCRIPTIONS MATTER
===========================================================================

    +-----------------------------------------------------------------------+
    | VISUAL: How Claude Selects Tools                                       |
    +-----------------------------------------------------------------------+

    User: "Check my order status"     User: "Verify my identity"
           |                                |
           v                                v
    +-------------------+            +-------------------+
    | Tool A: "Get     |            | Tool B: "Look up |
    |  customer info"   |            |  customer by     |
    |  [VAGUE]          |            |  email/phone"     |
    +-------------------+            +-------------------+
           |                                |
           v                                v
    CLAUDE DECIDES:                  CLAUDE DECIDES:
    "Check order" -> ???            "Verify identity" -> ???
           |                                |
           v                                v
    CONFUSION! NO CLEAR             CORRECT MATCH!
    MATCH!

    +-----------------------------------------------------------------------+
    | KEY INSIGHT: Tool descriptions are the PRIMARY mechanism             |
    | for tool selection - not metadata or routing classifiers!            |
    +-----------------------------------------------------------------------+

===========================================================================
FIVE ELEMENTS OF PRODUCTION-GRADE DESCRIPTIONS
===========================================================================

    +======================================================================+
    ||                                                                      ||
    ||  ELEMENT #1: What the tool does (primary purpose)                    ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  - Clear, unambiguous statement of purpose                          ||
    ||  - What problem does it solve?                                       ||
    ||  - What result does it return?                                       ||
    ||                                                                      ||
    ||  EXAMPLE:                                                           ||
    ||  "Looks up customer account information by email, phone, or ID"    ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  ELEMENT #2: What inputs it expects                                  ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  - Data types (string, number, array)                               ||
    ||  - Formats (email, phone, date format)                              ||
    ||  - Constraints (required vs optional, ranges)                       ||
    ||                                                                      ||
    ||  EXAMPLE:                                                           ||
    ||  "order_id: string, format #NNNNN (e.g., #12345)"                   ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  ELEMENT #3: Example queries it handles well                        ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  - Concrete use cases                                                ||
    ||  - Real user queries that trigger this tool                         ||
    ||                                                                      ||
    ||  EXAMPLE:                                                           ||
    ||  "Use for: 'Where's my order?', 'Track package #12345',            ||
    ||   'When will my order arrive?'"                                      ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  ELEMENT #4: Edge cases and limitations                             ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  - What it does NOT handle                                           ||
    ||  - Boundary conditions                                              │
    ||  - Known limitations                                                ||
    ||                                                                      ||
    ||  EXAMPLE:                                                           ||
    ||  "Does NOT handle: bulk orders, international shipping,            ||
    ||   orders older than 90 days"                                        ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  ELEMENT #5: Explicit boundaries (when to use THIS vs OTHER tool)   ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  - Clear differentiation from similar tools                         ||
    ||  - Decision criteria for routing                                     ||
    ||                                                                      ||
    ||  EXAMPLE:                                                           ||
    ||  "Use get_customer for identity verification.                        ||
    ||   Use lookup_order for order-specific queries."                    ||
    ||                                                                      ||
    +======================================================================+

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


def demonstrate_bad_vs_good_descriptions():
    """
    Shows the difference between bad and production-grade tool descriptions.
    """

    client = anthropic.Anthropic(api_key=API_KEY)

    print("\n" + "=" * 70)
    print("BAD vs PRODUCTION-GRADE TOOL DESCRIPTIONS")
    print("=" * 70)

    # BAD EXAMPLE
    print("""
    +======================================================================+
    ||                                                                      ||
    ||  BAD EXAMPLE (Causes misrouting):                                    ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  Tool 1: "Retrieves customer information"                           ||
    ||  Tool 2: "Retrieves order details"                                   ||
    ||                                                                      ||
    ||  WHAT'S WRONG:                                                      ||
    ||  - Too vague - Claude can't distinguish when to use which          ||
    ||  - No input format specification                                    ||
    ||  - No boundaries between similar tools                             ||
    ||  - No example queries                                               ||
    ||                                                                      ||
    ||  RESULT: Claude misroutes requests!                                 ||
    ||                                                                      ||
    +======================================================================+
    """)

    # GOOD EXAMPLE
    print("""
    +======================================================================+
    ||                                                                      ||
    ||  PRODUCTION-GRADE EXAMPLE (Correct routing):                         ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  get_customer: "Looks up a customer account by email address,       ||
    ||    phone number, or customer ID. Returns customer profile           ||
    ||    (name, contact details, account status, loyalty tier).          ||
    ||    Use this when verifying customer identity.                        ||
    ||    Do NOT use for order-specific queries - use lookup_order."       ||
    ||                                                                      ||
    ||  lookup_order: "Retrieves order details by order number            ||
    ||    (format: #NNNNN, e.g., #12345) or tracking ID.                   ||
    ||    Returns order status, items, shipping, refund eligibility.       ||
    ||    Use when customer asks about a specific order.                    │
    ||    Do NOT use for identity verification - use get_customer."         ||
    ||                                                                      ||
    ||  WHY IT WORKS:                                                      ||
    ||  - Clear purpose statement                                          ||
    ||  - Input format specified                                           ||
    ||  - Example queries included                                         ||
    ||  - Explicit boundaries (Do NOT use for X)                          ||
    ||                                                                      ||
    +======================================================================+
    """)

    message = client.messages.create(
        model="claude-haiku-4-5-20250601",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": "As an expert, explain why tool descriptions are the "
                      "primary mechanism for AI agent tool selection. "
                      "What happens when descriptions are vague?"
        }]
    )

    print("\nAI Response:")
    print(f"    {message.content[0].text[:300]}...")


def show_tool_splitting_pattern():
    """
    Shows the tool splitting pattern for better granularity.
    """

    print("\n" + "=" * 70)
    print("TOOL SPLITTING PATTERN")
    print("=" * 70)

    print("""
    +======================================================================+
    ||                                                                      ||
    ||  BEFORE (Generic tool):                                              ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  analyze_document: "Analyzes documents for various purposes"        ||
    ||                                                                      ||
    ||  PROBLEM: Too generic, Claude doesn't know which approach to use    ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  AFTER (Split into purpose-specific tools):                          ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  extract_data_points: "Extracts structured data fields from          ||
    ||    documents (dates, amounts, names, addresses). Returns JSON        ||
    ||    with field-value pairs. Use for forms, invoices, receipts."      ||
    ||                                                                      ||
    ||  summarize_content: "Produces concise summary of key arguments      ||
    ||    and conclusions from documents. Returns 2-3 paragraph summary.   │
    ||    Use for articles, reports, contracts."                            ||
    ||                                                                      ||
    ||  verify_claim_against_source: "Checks if a specific claim or        ||
    ||    statement is supported by the source document. Returns true/false||
    ||    with excerpt. Use for fact-checking and verification tasks."      ||
    ||                                                                      ||
    ||  WHY SPLITTING WORKS:                                               ||
    ||  - Each tool has clear, specific purpose                            ||
    ||  - Claude can select appropriate tool based on query                │
    ||  - Reduces confusion and misrouting                                 │
    ||                                                                      ||
    +======================================================================+
    """)


def show_real_time_scenarios():
    """
    Shows real production scenarios where tool schema matters.
    """

    print("\n" + "=" * 70)
    print("REAL-TIME PRODUCTION SCENARIOS")
    print("=" * 70)

    print("""
    +======================================================================+
    ||                                                                      ||
    ||  SCENARIO #1: E-Commerce Customer Service Chatbot                   ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  PROBLEM: Customer asks "Where's my order?"                         ||
    ||           AI routes to wrong tool, gives incorrect info              ||
    ||                                                                      ||
    ||  ROOT CAUSE: Tool description too vague                             ||
    ||  "retrieve_order: Gets order information"                          │
    ||                                                                      ||
    ||  FIX: Production-grade description:                                 ||
    ||  "Retrieves order status by order number (#NNNNN) or tracking ID.  ||
    ||   Returns: current status, estimated delivery, tracking updates.   ||
    ||   Use for: 'Where's my order?', 'Track package', 'Delivery date'.  ||
    ||   Do NOT use for: returns, refunds, account changes."              ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  SCENARIO #2: Healthcare Appointment Scheduler                       ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  PROBLEM: AI books appointment in wrong time slot                   ||
    ||           Patient shows up at wrong time                            ||
    ||                                                                      ||
    ||  ROOT CAUSE: No timezone handling in tool description                ||
    ||                                                                      ||
    ||  FIX: Add timezone specification:                                   ||
    ||  "Schedules appointments in patient's local timezone.              ||
    ||   Required input: date, time slot, provider ID.                     │
    ||   Time format: 24-hour (14:00, not 2pm).                            │
    ||   Automatically converts UTC times to local timezone."              ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  SCENARIO #3: Financial Trading Bot                                  ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  PROBLEM: AI executes wrong type of trade                           ||
    ||           Market order vs limit order confusion                      ||
    ||                                                                      ||
    ||  ROOT CAUSE: No distinction between trade types in schema           ||
    ||                                                                      ||
    ||  FIX: Split into specific tools:                                    ||
    ||  - execute_market_order: "Market order - immediate execution"      ||
    ||  - execute_limit_order: "Limit order - execute at price or better" ||
    ||  - execute_stop_order: "Stop order - trigger at threshold"          ||
    ||                                                                      ||
    +======================================================================+
    """)


def show_mistakes():
    """
    Shows common mistakes developers make with tool schema design.
    """

    print("\n" + "=" * 70)
    print("COMMON MISTAKES DEVELOPERS MAKE")
    print("=" * 70)

    print("""
    +======================================================================+
    ||                                                                      ||
    ||  MISTAKE #1: Generic, vague tool names                              ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WRONG: "get_data" "process_info" "handle_request"                 ||
    ||                                                                      ||
    ||  WHY WRONG: Claude can't determine when to use these tools         ||
    ||                                                                      ||
    ||  CORRECT: "get_customer_by_email" "calculate_refund"               ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  MISTAKE #2: Missing input format specifications                    ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WRONG: "order_id: string" <- Just type, no format                  ||
    ||                                                                      ||
    ||  CORRECT: "order_id: string, format #NNNNN (e.g., #12345)"         ||
    ||                                                                      ||
    ||  WHY: Without format, Claude may send wrong format                   ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  MISTAKE #3: No boundaries between similar tools                    ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WRONG: Two tools with overlapping purposes, no distinction          ||
    ||                                                                      ||
    ||  CORRECT: "Use get_customer for identity. Use lookup_order          ||
    ||            for orders. Do NOT confuse these."                        ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  MISTAKE #4: Adding routing classifiers before improving desc       ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WRONG: "The customer said 'order' so use order tool"               ||
    ||                                                                      ||
    ||  CORRECT: First improve descriptions, THEN add classifiers           ||
    ||          if still needed after description improvements             ||
    ||                                                                      ||
    ||  WHY: Good descriptions solve most routing issues!                  ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  MISTAKE #5: No example queries in description                       ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WRONG: "Retrieves order details" <- No examples                    ||
    ||                                                                      ||
    ||  CORRECT: "Use for: 'Where's my order', 'Track #12345',            ||
    ||           'When will it arrive?'"                                   ||
    ||                                                                      ||
    +======================================================================+
    """)


def show_interview_qa():
    """
    Shows interview questions and expert answers.
    """

    print("\n" + "=" * 70)
    print("INTERVIEW Q&A PREPARATION")
    print("=" * 70)

    print("""
    ======================================================================
    Q1: "What are the five elements of production-grade tool descriptions?"
    ======================================================================

    EXPERT ANSWER:
    "1. What the tool does (primary purpose)
     2. What inputs it expects (data types, formats, constraints)
     3. Example queries it handles well (concrete use cases)
     4. Edge cases and limitations (what it does NOT do)
     5. Explicit boundaries (when to use THIS vs similar tools)"

    ======================================================================
    Q2: "How do you handle similar tools with overlapping functionality?"
    ======================================================================

    EXPERT ANSWER:
    "Use explicit boundaries in descriptions. For example:
    'Use get_customer for identity verification.
     Use lookup_order for order-specific queries.
     Do NOT confuse these two tools.'
     This tells Claude exactly when to use each tool."

    ======================================================================
    Q3: "When should you split a generic tool into multiple specific ones?"
    ======================================================================

    EXPERT ANSWER:
    "When the tool has multiple distinct purposes that Claude can't
     reliably distinguish. For example, split 'analyze_document' into:
     - extract_data_points (structured data extraction)
     - summarize_content (summary generation)
     - verify_claim_against_source (fact verification)
     Each has a clear, single purpose."

    ======================================================================
    Q4: "What's the first thing to fix before adding routing classifiers?"
    ======================================================================

    EXPERT ANSWER:
    "Improve the tool descriptions first! Routing classifiers are
     complementary, not a replacement for good descriptions. The exam
     tests whether you know to optimize descriptions before adding
     external routing logic."

    """)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("""
+===========================================================================+
|                                                                           |
|  TOOL SCHEMA DESIGN & DESCRIPTIONS - PRACTICE                            |
|                                                                           |
|  Learn to write production-grade tool descriptions!                        |
|                                                                           |
+===========================================================================+
    """)

    demonstrate_bad_vs_good_descriptions()
    show_tool_splitting_pattern()
    show_real_time_scenarios()
    show_mistakes()
    show_interview_qa()

    print("\n" + "=" * 70)
    print("WHAT WE HAVE LEARNT")
    print("=" * 70)
    print("""
    +======================================================================+
    ||  1. FIVE ELEMENTS OF PRODUCTION-GRADE DESCRIPTIONS:                ||
    ||                                                                      ||
    ||  ELEMENT 1: What the tool does (primary purpose)                    ||
    ||  ELEMENT 2: What inputs it expects (types, formats, constraints)     ||
    ||  ELEMENT 3: Example queries it handles well (concrete use cases)     ||
    ||  ELEMENT 4: Edge cases and limitations (what it does NOT do)       ||
    ||  ELEMENT 5: Explicit boundaries (when to use THIS vs other tools)    ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  2. TOOL SPLITTING PATTERN:                                         ||
    ||                                                                      ||
    ||  BEFORE: "analyze_document" (generic, confusing)                    ||
    ||                                                                      ||
    ||  AFTER:                                                              ||
    ||  - extract_data_points (structured data)                            ||
    ||  - summarize_content (key arguments)                               ||
    ||  - verify_claim_against_source (fact-check)                          ||
    ||                                                                      ||
    ||  Split when tool has multiple distinct purposes!                     ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  3. REAL-TIME SCENARIOS:                                           ||
    ||                                                                      ||
    ||  SCENARIO #1: E-commerce chatbot - wrong tool routing              ||
    ||  SCENARIO #2: Healthcare scheduler - timezone issues                ||
    ||  SCENARIO #3: Trading bot - wrong trade type                        ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  4. COMMON MISTAKES:                                               ||
    ||                                                                      ||
    ||  MISTAKE #1: Generic, vague tool names                              ||
    ||  MISTAKE #2: Missing input format specifications                    ||
    ||  MISTAKE #3: No boundaries between similar tools                   ||
    ||  MISTAKE #4: Adding classifiers before improving descriptions         ||
    ||  MISTAKE #5: No example queries in description                       ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  5. INTERVIEW TIPS:                                                 ||
    ||                                                                      ||
    ||  - Know all five elements of tool descriptions                       ||
    ||  - Explain tool splitting with concrete examples                    ||
    ||  - Know when descriptions need improvement vs classifiers           ||
    ||  - Always include explicit boundaries in descriptions               ||
    ||                                                                      ||
    +======================================================================+

    Next: practice_02_structured_error_responses.py shows how to handle
    errors gracefully in tool implementations!
    """)


"""
+===========================================================================+
|                                                                           |
|  KEY CONCEPTS FROM THIS FILE:                                            |
|                                                                           |
|  TOOL DESCRIPTIONS:                                                      |
|  - Primary mechanism for Claude tool selection                            |
|  - Five elements: purpose, inputs, examples, limits, boundaries          |
|  - Always improve descriptions before adding classifiers                  |
|                                                                           |
|  TOOL SPLITTING:                                                         |
|  - Split generic tools into purpose-specific tools                       |
|  - Each tool has clear, single purpose                                   |
|  - Reduces confusion and improves accuracy                               |
|                                                                           |
|  ERROR HANDLING PATTERNS:                                                |
|  - Include error code, message, action, retry flag                       |
|  - Structured responses over unstructured messages                       |
|                                                                           |
|  EXAM TIPS:                                                              |
|  - Describe all five elements with examples                             |
|  - Know tool splitting criteria                                         |
|  - Tool descriptions > routing classifiers                               |
|                                                                           |
+===========================================================================+
"""