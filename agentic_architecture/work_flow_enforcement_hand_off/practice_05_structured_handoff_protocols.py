"""
================================================================================
PRACTICE 5: STRUCTURED HANDOFF PROTOCOLS
================================================================================

When an agent cannot resolve an issue and must escalate to a human,
the handoff MUST follow a structured protocol.

CRITICAL: Human agents do NOT have access to conversation transcripts!
The handoff summary must include ALL essential information.
================================================================================

REAL-TIME SCENARIO - HANDOFF FAILURE:
------------------------------------
A customer called about a billing dispute. AI agent tried to help
but after 15 minutes couldn't resolve it. Handoff to human agent:

INCOMPLETE HANDOFF:
"Customer has billing question. Please help."

Human agent response:
- "Can you give me the customer ID?" (missing!)
- "What was the issue again?" (no summary!)
- "What have you tried?" (no history!)
- "What's the refund amount?" (not stated!)

Customer had to repeat everything. Escalated to manager.
Review found: 5 minutes wasted re-explaining what AI already knew.

COMPLETE HANDOFF (after fix):
"Customer ID: CUST-12345, Order: #67890
Issue: Double charge on shipping ($15.99)
Timeline: Verified order, attempted refund, system error PR-403
Refund amount: $15.99
Action: Manual refund approval needed"

Human agent resolved in 2 minutes. Customer satisfied.

MISTAKE: Assuming human agent can read the transcript!
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
# VISUAL: THE HANDOFF CONSTRAINT
# ================================================================================
#
#   WRONG ASSUMPTION:                         REALITY:
#   -----------------                         -------
#
#   +------------------+                      +------------------+
#   | AI Agent        |                      | AI Agent        |
#   | Cannot resolve  |                      | Cannot resolve  |
#   +--------+---------+                      +--------+---------+
#            |                                         |
#            v                                         v
#   +------------------+                      +------------------+
#   | "Human can read  |                      | "Human needs     |
#   |  the transcript" |                      |  summary"        |
#   +------------------+                      +------------------+
#            |                                         |
#            v                                         v
#   INCOMPLETE HANDOFF                         COMPLETE HANDOFF
#   (customer repeats)                        (immediate help)
#
#   HUMAN AGENTS DO NOT HAVE TRANSCRIPT ACCESS!
#   THE HANDOFF MUST CONTAIN EVERYTHING!
# ================================================================================


def demonstrate_critical_constraint():
    """
    Emphasize the critical constraint about transcript access.

    EXAM CRITICAL:
    Human agents do NOT have access to conversation transcripts.
    This is a fundamental architectural constraint.
    If you forget this, handoffs will always be incomplete.
    """
    print("\n" + "=" * 70)
    print("CRITICAL CONSTRAINT: No Transcript Access")
    print("=" * 70)

    print("""
+----------------------------------------------------------------------+
|  WRONG ASSUMPTION:                                                   |
|                                                                      |
|  "The human agent can just read the chat transcript                 |
|   to understand what happened."                                      |
|                                                                      |
|  REALITY:                                                            |
|                                                                      |
|  Human agents do NOT have access to conversation transcripts!       |
|                                                                      |
|  If the handoff summary is incomplete, the human agent               |
|  CANNOT look it up - they just don't know what happened!           |
|                                                                      |
|  Therefore:                                                          |
|  The handoff summary MUST include EVERYTHING the human               |
|  agent needs to help the customer.                                  |
+----------------------------------------------------------------------+

    ARCHITECTURAL CONSTRAINT:
    The AI agent and human agent are SEPARATE systems.
    They do NOT share conversation history.
    The handoff is the ONLY source of information.

    MEMORIZE THIS: Human agents have NO transcript access!
""")


def show_wrong_handoff():
    """
    Show what NOT to do in a handoff.

    PRODUCTION CASE:
    A retail company had 30% of escalations require "back-and-forth"
    where human asked for information the AI already had.

    Root cause: Incomplete handoffs assuming transcript access.
    Cost: 5-10 minutes per escalation, 1000 escalations/month.

    After fixing handoff protocol:
    - Back-and-forth reduced to 5%
    - 45 minutes/day saved per human agent
    - CSAT scores improved 20%
    """
    print("\n" + "=" * 70)
    print("WRONG: Incomplete Handoff")
    print("=" * 70)

    print("""
+----------------------------------------------------------------------+
|  HANDOFF MESSAGE:                                                    |
|                                                                      |
|  "Customer needs help with their order. Please assist."             |
|                                                                      |
+----------------------------------------------------------------------+

    What the human agent sees:

    +---------------------+---------------------------------------------+
    | Customer ID?        | *** NOT PROVIDED ***                       |
    +---------------------+---------------------------------------------+
    | What was problem?   | *** NOT EXPLAINED ***                      |
    +---------------------+---------------------------------------------+
    | What was tried?     | *** UNKNOWN ***                            |
    +---------------------+---------------------------------------------+
    | Refund amount?      | *** NOT STATED ***                         |
    +---------------------+---------------------------------------------+
    | Recommended action? | *** NOT SPECIFIED ***                      |
    +---------------------+---------------------------------------------+

    Result: Human agent must re-ask customer everything!
            Customer is frustrated. Experience is broken.

+----------------------------------------------------------------------+

    WHY INCOMPLETE HANDOFFS HAPPEN:
    1. Developer assumes "human can read transcript"
    2. AI agent didn't know what to include
    3. No structured handoff protocol defined
    4. Each handoff is different and incomplete

    FIX: Define minimum required fields for every handoff!
""")


def show_correct_handoff():
    """
    Show the correct structured handoff protocol.

    VISUAL: REQUIRED FIELDS STRUCTURE
    ---------------------------------

    +----------------------------------------------------------+
    |  REQUIRED FIELDS FOR EVERY HANDOFF:                       |
    |                                                          |
    |  1. Customer ID                                           |
    |     Purpose: Look up account                              |
    |                                                          |
    |  2. Conversation Summary                                  |
    |     Purpose: Understand what happened                    |
    |                                                          |
    |  3. Root Cause Analysis                                   |
    |     Purpose: Why it's being escalated                     |
    |                                                          |
    |  4. Refund Amount (if applicable)                         |
    |     Purpose: Exact financial figure                       |
    |                                                          |
    |  5. Recommended Action                                    |
    |     Purpose: What human should do                        |
    +----------------------------------------------------------+
    """
    print("\n" + "=" * 70)
    print("CORRECT: Structured Handoff Protocol")
    print("=" * 70)

    print("""
+----------------------------------------------------------------------+
|  REQUIRED FIELDS FOR EVERY HANDOFF:                                  |
|                                                                      |
|  1. Customer ID ------------------------------------------------------|
|     Purpose: So human can look up the account                        |
|                                                                      |
|  2. Conversation Summary --------------------------------------------|
|     Purpose: What was asked and what was attempted                   |
|                                                                      |
|  3. Root Cause Analysis ---------------------------------------------|
|     Purpose: Agent's assessment of the underlying issue              |
|                                                                      |
|  4. Refund Amount (if applicable) ------------------------------------|
|     Purpose: Exact financial figure involved                         |
|                                                                      |
|  5. Recommended Action ----------------------------------------------|
|     Purpose: What the human should do next                          |
+----------------------------------------------------------------------+

    INTERVIEW TIP:
    When asked "what makes a good handoff?", answer with these 5 fields.
    The more complete the handoff, the faster the human can help.
""")


def show_complete_handoff_example():
    """
    Show a complete, properly structured handoff.
    """
    print("\n" + "=" * 70)
    print("COMPLETE HANDOFF EXAMPLE")
    print("=" * 70)

    handoff = {
        "handoff_type": "ESCALATION",
        "priority": "HIGH",
        "customer_id": "CUST-12345",
        "customer_name": "Jane Doe",
        "customer_email": "jane.doe@example.com",

        "conversation_summary": """
Customer contacted regarding order #67890.
Issue: Laptop received is defective (screen flickering).
Customer requests replacement or full refund.

Timeline:
- Customer provided order number and photos of defective screen
- Agent verified order exists and is within return window (14 days)
- Agent attempted to process replacement but system shows item out of stock
- Agent attempted refund but it failed with error code PR-403
- Agent tried multiple browsers but issue persists
        """.strip(),

        "root_cause_analysis": """
Agent assessment: The order contains a limited-edition laptop.
System is unable to process replacement (out of stock) OR refund
(possible inventory system sync issue). The specific error PR-403
indicates a backend inventory-refund synchronization failure.

This requires manual intervention from billing or inventory team.
        """.strip(),

        "refund_amount": "$1,299.00",

        "recommended_action": """
Please:
1. Verify refund eligibility with inventory team
2. If approved, manually process refund of $1,299.00 to original payment method
3. Alternatively, offer customer priority replacement when stock returns
4. Customer has expressed preference for refund over replacement
        """.strip(),

        "previous_interactions": 1,
        "customer_sentiment": "frustrated but patient"
    }

    print("\n[HANDOFF SUMMARY - ESCALATION TO HUMAN AGENT]")
    print("=" * 60)

    print(f"\n[Customer Information:]")
    print(f"   ID: {handoff['customer_id']}")
    print(f"   Name: {handoff['customer_name']}")
    print(f"   Email: {handoff['customer_email']}")

    print(f"\n[Conversation Summary:]")
    for line in handoff['conversation_summary'].split('\n'):
        print(f"   {line}")

    print(f"\n[Root Cause Analysis:]")
    for line in handoff['root_cause_analysis'].split('\n'):
        print(f"   {line}")

    if handoff['refund_amount']:
        print(f"\n[Refund Amount: {handoff['refund_amount']}]")

    print(f"\n[Recommended Action:]")
    for line in handoff['recommended_action'].split('\n'):
        print(f"   {line}")

    print(f"\n[Additional Context:]")
    print(f"   Previous interactions: {handoff['previous_interactions']}")
    print(f"   Customer sentiment: {handoff['customer_sentiment']}")

    return handoff


def show_minimum_required_fields():
    """
    Emphasize the minimum required fields.

    EXAM CRITICAL - THESE ARE REQUIRED FOR EVERY HANDOFF:
    -----------------------------------------------------
    1. Customer ID - Cannot help without this!
    2. Conversation summary - Human has no transcript!
    3. Root cause analysis - Human needs context!
    4. Recommended action - Human needs guidance!
    5. Refund amount - If financial issue, show exact amount!

    Any handoff missing these is INCOMPLETE and WRONG!
    """
    print("\n" + "=" * 70)
    print("MINIMUM REQUIRED FIELDS (EXAM CRITICAL!)")
    print("=" * 70)

    print("""
+----------------------------------------------------------------------+
|  EXAM TIP: Missing ANY of these = WRONG ANSWER!                     |
|                                                                      |
|  + Customer ID ------------------------------------------------------+  |
|  | Purpose: Cannot help without this!                                 |  |
|  +--------------------------------------------------------------------+  |
|                                                                      |
|  + Conversation summary ----------------------------------------------+  |
|  | Purpose: Human has NO transcript access!                          |  |
|  +--------------------------------------------------------------------+  |
|                                                                      |
|  + Root cause analysis ----------------------------------------------+  |
|  | Purpose: Human needs context to understand issue                   |  |
|  +--------------------------------------------------------------------+  |
|                                                                      |
|  + Recommended action ----------------------------------------------+  |
|  | Purpose: Human needs guidance on what to do next                  |  |
|  +--------------------------------------------------------------------+  |
|                                                                      |
|  + Refund amount -----------------------------------------------------+  |
|  | Purpose: If financial issue, exact amount needed                  |  |
|  +--------------------------------------------------------------------+  |
|                                                                      |
|  These are NOT optional. They are REQUIRED.                          |
|  A handoff missing any of these is INCOMPLETE and WRONG.             |
+----------------------------------------------------------------------+

    CERTIFICATION MEMORIZATION:
    Every handoff needs: ID, Summary, Root Cause, Action, Amount
    If it's missing any of these five, it's wrong!
""")


def demonstrate_bad_vs_good():
    """
    Side-by-side comparison of bad vs good handoffs.

    IMPACT MEASUREMENT:
    After implementing structured handoffs:

    BEFORE:
    - Avg escalation resolution: 12 minutes
    - Back-and-forth rate: 30%
    - Customer satisfaction: 65%

    AFTER:
    - Avg escalation resolution: 4 minutes
    - Back-and-forth rate: 5%
    - Customer satisfaction: 88%

    67% faster resolution, 83% less back-and-forth!
    """
    print("\n" + "=" * 70)
    print("BAD vs GOOD HANDOFF COMPARISON")
    print("=" * 70)

    print("""
+-----------------------+-----------------------------------------------+
|  BAD HANDOFF          |  GOOD HANDOFF                                |
+-----------------------+-----------------------------------------------+
|                       |                                               |
|  "Customer needs      |  Customer ID: CUST-12345                      |
|   help"               |  Order: #67890                               |
|                       |                                               |
|  Human must:          |  Summary: Defective laptop, refund requested   |
|  + Ask for ID         |  Root cause: System error PR-403             |
|  + Ask what problem   |  Refund: $1,299.00                           |
|  + Ask what's been    |  Action: Manual refund approval needed        |
|    tried              |                                               |
|  + Ask for amounts    |  Human can IMMEDIATELY help!                 |
|                       |                                               |
|  Time wasted:         |  Time saved: 5-10 minutes per handoff        |
|  Customer angry        |  Customer satisfied                          |
+-----------------------+-----------------------------------------------+

    IMPACT SUMMARY:

    Before structured handoffs:
    - 30% of escalations need "back-and-forth"
    - Average resolution: 12 minutes
    - Customer frustration high

    After structured handoffs:
    - 5% of escalations need clarification
    - Average resolution: 4 minutes
    - Customer satisfaction improved 35%
""")


def show_handoff_checklist():
    """
    Provide a checklist for before sending a handoff.
    """
    print("\n" + "=" * 70)
    print("HANDOFF CHECKLIST")
    print("=" * 70)

    print("""
Before sending ANY handoff to human agent, verify:

+---------------------------------------------------+------------------------+
| Item                                              | Check                  |
+---------------------------------------------------+------------------------+
| Customer ID included?                             | [ ]                    |
|    --> Human needs this to look up the account    |                        |
+---------------------------------------------------+------------------------+
| Conversation summary included?                   | [ ]                    |
|    --> Human has NO transcript access             |                        |
+---------------------------------------------------+------------------------+
| Root cause analysis included?                     | [ ]                    |
|    --> Human needs to understand what happened    |                        |
+---------------------------------------------------+------------------------+
| Refund amount (if applicable) included?          | [ ]                    |
|    --> Exact financial figure, not vague desc.    |                        |
+---------------------------------------------------+------------------------+
| Recommended action included?                   | [ ]                    |
|    --> Human needs clear guidance on next steps  |                        |
+---------------------------------------------------+------------------------+
| Previous interactions documented?                | [ ]                    |
|    --> Human knows if customer is repeat caller   |                        |
+---------------------------------------------------+------------------------+
| Customer sentiment noted?                        | [ ]                    |
|    --> Human can adjust approach accordingly      |                        |
+---------------------------------------------------+------------------------+
""")


def show_common_mistakes():
    """
    Common errors developers make with handoffs.
    """
    print("\n" + "=" * 70)
    print("MISTAKES DEVELOPERS MAKE")
    print("=" * 70)

    print("""
MISTAKE 1: Assuming human can read transcript
---------------------------------------------
WRONG:
    "Please help this customer." (no context)

RIGHT:
    "Customer ID: CUST-12345, Issue: billing error,
    Timeline: [summary], Recommended action: [action]"


MISTAKE 2: Vague summaries
---------------------------
WRONG:
    "Customer had a problem with their order."

RIGHT:
    "Order #67890: Customer charged $15.99 twice for shipping.
    Verified order exists, attempted refund, system error occurred."


MISTAKE 3: Missing financial amounts
------------------------------------
WRONG:
    "Customer wants a refund for overcharge."

RIGHT:
    "Customer wants refund for $15.99 duplicate shipping charge."


MISTAKE 4: No recommended action
---------------------------------
WRONG:
    "Escalating this customer."

RIGHT:
    "Please manually process refund of $15.99 to original payment
    method. Customer confirmed original payment method still valid."


MISTAKE 5: Different handoff formats
------------------------------------
WRONG:
    Each handoff is different, some include key info, some don't.

RIGHT:
    All handoffs follow same structured format with required fields.
    Missing fields are immediately obvious.


MISTAKE 6: Forgetting this is architectural constraint
--------------------------------------------------------
WRONG:
    "Human agent probably has access to transcript anyway."

RIGHT:
    Human agents do NOT have transcript access.
    Handoff MUST contain everything - no exceptions!
""")


def show_interview_qa():
    """
    Interview questions and expert answer frameworks.
    """
    print("\n" + "=" * 70)
    print("INTERVIEW Q&A - STRUCTURED HANDOFFS")
    print("=" * 70)

    print("""
Q1: "Why do human agents need so much information in handoffs?
    Can't they just read the conversation?"

A:  "Human agents do NOT have access to conversation transcripts.
    This is an architectural constraint - the AI and human agent
    are separate systems that don't share conversation history.

    Therefore, the handoff must contain EVERYTHING the human needs:
    - Customer ID (to look up account)
    - What happened (conversation summary)
    - Why it's escalated (root cause)
    - What to do (recommended action)
    - Financial amounts if applicable

    Without these, human must re-ask customer everything,
    which is frustrating and wastes time.


Q2: "What's the minimum required information in a handoff?"

A:  "Five fields required for every handoff:

    1. Customer ID - Cannot help without this
    2. Conversation summary - Human has no transcript
    3. Root cause analysis - Human needs context
    4. Recommended action - Human needs guidance
    5. Refund amount (if applicable) - Exact figure needed

    Any handoff missing these is incomplete and wrong.


Q3: "What happens if handoffs are incomplete?"

A:  "Multiple problems:

    1. Human must re-ask customer for basic information
       - Wastes 5-10 minutes per escalation
       - Customer frustrated, repeat explanations

    2. Resolution time increases dramatically
       - From 4 minutes (complete) to 12 minutes (incomplete)
       - 67% slower

    3. Customer satisfaction drops
       - Customer already frustrated AI couldn't help
       - Now frustrated human can't help either

    4. Escalations to supervisors increase
       - "Let me get my manager"

    Bottom line: Incomplete handoffs destroy customer experience.


Q4: "How do you structure handoff information?"

A:  "I use a standardized format with required fields:

    Handoff Type: [ESCALATION]
    Priority: [HIGH/MEDIUM/LOW]
    Customer ID: [ID]
    Customer Name: [Name]
    Customer Email: [Email]

    Conversation Summary:
    [What customer asked, what agent tried, what failed]

    Root Cause Analysis:
    [Why this requires human intervention]

    Refund Amount: [$XXX.XX] (if financial)

    Recommended Action:
    [Step-by-step what human should do]

    Previous Interactions: [N]
    Customer Sentiment: [frustrated/angry/patient]

    This ensures nothing is forgotten and human can help immediately.
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
|  LESSON 1: THE CRITICAL CONSTRAINT                                  |
+----------------------------------------------------------------------+

    Human agents do NOT have access to conversation transcripts!

    This is an architectural constraint, not a preference.
    The AI and human are separate systems.
    Handoff is the ONLY source of information.

    If handoff is incomplete, human cannot help effectively.


+----------------------------------------------------------------------+
|  LESSON 2: FIVE REQUIRED FIELDS                                    |
+----------------------------------------------------------------------+

    Every handoff must include:

    1. Customer ID
       - Cannot look up account without this

    2. Conversation Summary
       - Human has no transcript access

    3. Root Cause Analysis
       - Human needs to understand what happened

    4. Recommended Action
       - Human needs guidance on what to do

    5. Refund Amount (if applicable)
       - Exact financial figure for refunds


+----------------------------------------------------------------------+
|  LESSON 3: BAD vs GOOD HANDOFFS                                     |
+----------------------------------------------------------------------+

    BAD HANDOFF:
    "Customer needs help."

    Human must ask:
    - Customer ID?
    - What was problem?
    - What was tried?
    - Amount involved?
    - What should I do?

    Time wasted: 5-10 minutes
    Customer: frustrated


    GOOD HANDOFF:
    "Customer ID: CUST-12345
    Issue: billing error, $15.99 duplicate charge
    Tried: verified order, attempted refund, error PR-403
    Action: manual refund approval needed"

    Human: immediately helps
    Time: 2-4 minutes
    Customer: satisfied


+----------------------------------------------------------------------+
|  LESSON 4: PRODUCTION IMPACT                                        |
+----------------------------------------------------------------------+

    After implementing structured handoffs:

    +-------------------------+------------------+--------------------+
    | Metric                  | Before           | After              |
    +-------------------------+------------------+--------------------+
    | Avg resolution time     | 12 minutes       | 4 minutes          |
    | Back-and-forth rate     | 30%              | 5%                 |
    | Customer satisfaction   | 65%              | 88%                |
    +-------------------------+------------------+--------------------+

    67% faster resolution, 83% less frustration!


+----------------------------------------------------------------------+
|  LESSON 5: COMMON MISTAKES                                          |
+----------------------------------------------------------------------+

    1. Assuming human can read transcript
    2. Vague summaries ("had a problem")
    3. Missing financial amounts
    4. No recommended action
    5. Different formats for each handoff
    6. Forgetting this is architectural constraint


+----------------------------------------------------------------------+
|  LESSON 6: EXAM CRITICAL POINTS                                     |
+----------------------------------------------------------------------+

    MEMORIZE FOR EXAM:

    1. Human agents have NO transcript access
       - This is architectural, not optional

    2. Every handoff needs:
       - Customer ID
       - Conversation summary
       - Root cause analysis
       - Recommended action
       - Refund amount (if financial)

    3. Incomplete handoffs are always wrong
       - Missing any required field = wrong

    4. The more complete the handoff, the faster resolution
       - Structured protocol = better CX


+----------------------------------------------------------------------+
|  KEY FORMULA FOR CERTIFICATION EXAM                                |
+----------------------------------------------------------------------+

    HANDOFF = Customer ID + Summary + Root Cause + Action + Amount

    Human has no transcript. Handoff must contain everything!

    If asked "what makes a good handoff?":
    Answer with the five required fields and explain why each matters.
+----------------------------------------------------------------------+
""")


if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    print("\n" + "=" * 70)
    print("PRACTICE 5: STRUCTURED HANDOFF PROTOCOLS")
    print("=" * 70)
    print("""
This program teaches how to properly escalate from AI agent to human agent.

CRITICAL: Human agents do NOT have transcript access!
The handoff summary MUST include all essential information.
""")

    demonstrate_critical_constraint()
    show_wrong_handoff()
    show_correct_handoff()
    show_complete_handoff_example()
    show_minimum_required_fields()
    demonstrate_bad_vs_good()
    show_handoff_checklist()
    show_common_mistakes()
    show_interview_qa()
    show_what_we_learnt()

    print("""
================================================================================
WHAT JUST HAPPENED?
================================================================================

    1. We learned the CRITICAL CONSTRAINT:
       - Human agents do NOT have transcript access
       - Handoff summary MUST be complete
       - This is architectural, not optional

    2. We saw WRONG handoffs:
       - Missing essential information
       - Human must re-ask customer everything
       - Frustrating for everyone

    3. We saw CORRECT handoffs with five required fields:
       - Customer ID
       - Conversation summary
       - Root cause analysis
       - Recommended action
       - Refund amount (if applicable)

    4. We learned the MINIMUM REQUIRED FIELDS:
       - These are NOT optional
       - Missing any = incomplete handoff = wrong

    5. We practiced INTERVIEW Q&A:
       - Why so much information needed
       - What happens with incomplete handoffs
       - How to structure handoff format

    6. We learned COMMON MISTAKES:
       - Assuming transcript access
       - Vague summaries
       - Missing amounts
       - No recommended action

    EXAM TIPS:
    - Human agents have NO transcript access - remember this!
    - Every handoff needs: Customer ID, summary, root cause, action
    - Add refund amount if financial issue involved
    - Incomplete handoffs are always wrong
    - Structured handoffs = 67% faster resolution
================================================================================
""")
    print("\n" + "=" * 70)
    print("PROGRAM COMPLETE!")
    print("=" * 70)