"""
================================================================================
PRACTICE 4: MULTI-CONCERN REQUEST HANDLING
================================================================================

When customers submit requests with multiple issues, the correct approach:

    1. DECOMPOSE - Break into distinct items
    2. INVESTIGATE - Research each in parallel
    3. SYNTHESIZE - Combine into unified resolution

One request = One response addressing ALL concerns!
================================================================================

REAL-TIME SCENARIO - CUSTOMER FRUSTRATION:
------------------------------------------
A telecom company noticed 40% of escalations came from multi-concern
requests handled incorrectly.

Customer: "I need to change my plan, report a billing error, and ask
           about upgrading my phone."

WRONG APPROACH (3 interactions):
1. Agent: "Let me help with the plan change first." [5 min]
2. Agent: "Now for the billing error?" [5 min]
3. Agent: "And your phone upgrade?" [5 min]

Total time: 15 min, customer frustrated, multiple transfers

RIGHT APPROACH (1 interaction):
1. Agent: Decomposes -> Investigates all 3 -> Synthesizes response
Total time: 5 min, customer happy, one interaction

Result: 40% reduction in escalations after training agents on
multi-concern handling!

MISTAKE: Treating each concern as a separate conversation!
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
# VISUAL: WRONG vs RIGHT APPROACH
# ================================================================================
#
#   WRONG APPROACH:                          RIGHT APPROACH:
#   ----------------                         ----------------
#
#   Customer: "3 concerns"                   Customer: "3 concerns"
#          |                                     |
#          v                                     v
#   Agent: handles #1                        Agent: DECOMPOSES
#          |                                     |
#          v                                     v
#   Customer: "next?"                        Agent: INVESTIGATES
#          |                                   all 3 in PARALLEL
#          v                                     |
#   Agent: handles #2                          |
#          |                                     v
#          v                                   Agent: SYNTHESIZES
#   Customer: "next?"                              |
#          |                                        v
#          v                                   Customer: ONE response
#   Agent: handles #3                              |
#          |                                        v
#          v                                   Customer: SATISFIED!
#   Customer: FRUSTRATED
#
#   3 interactions, wasted time                1 interaction, efficient
# ================================================================================


def demonstrate_wrong_approach():
    """
    Show the wrong way to handle multi-concern requests.

    PRODUCTION CASE:
    A customer had 5 concerns in one message. Agent handled one at a time.
    By concern #3, customer had been on hold for 20 minutes and escalated.

    The agent didn't realize they were destroying customer experience.
    Each concern was small, but total time was unacceptable.
    """
    print("\n" + "=" * 70)
    print("WRONG APPROACH: Handle One Concern at a Time")
    print("=" * 70)

    print("""
+----------------------------------------------------------------------+
|  CUSTOMER REQUEST:                                                   |
|                                                                      |
|  "I need to return item #123, update my shipping address to         |
|   456 Oak St, and I'm also wondering about my loyalty points."        |
|                                                                      |
+----------------------------------------------------------------------+

    WRONG AGENT BEHAVIOR:

    +-----------------------+        +-----------------------+
    | Agent says:           |        | Customer response:    |
    | "Let me help with    | -----> | Okay, here's the      |
    |  the return first."  |        | return info...        |
    +-----------------------+        +-----------------------+
    +-----------------------+        +-----------------------+
    | Agent says:           |        | Customer response:    |
    | "Now, what's your    | -----> | Oh, right, the       |
    |  new address?"        |        | address change...     |
    +-----------------------+        +-----------------------+
    +-----------------------+        +-----------------------+
    | Agent says:           |        | Customer response:    |
    | "And your loyalty    | -----> | Sigh... loyalty       |
    |  points question?"    |        | points question...    |
    +-----------------------+        +-----------------------+

    Result: 3 separate interactions, frustrated customer!
    Customer wanted ONE response addressing ALL concerns!

+----------------------------------------------------------------------+

    WHY AGENTS DO THIS WRONG:
    1. System prompts focus on "handle the current query"
    2. Agents don't decompose multi-concern requests
    3. Agents treat each identified concern as a new turn
    4. No framework for parallel investigation

    FIX: DECOMPOSE -> INVESTIGATE -> SYNTHESIZE framework
""")


def demonstrate_correct_approach():
    """
    Show the correct way to handle multi-concern requests.

    VISUAL FLOW:
    ------------

    DECOMPOSE:                INVESTIGATE:              SYNTHESIZE:
    ----------                -----------               ----------

    Customer has              Spawn research           Combine results
    3 concerns:               agents in                into ONE
    1. Return                 PARALLEL:                response:
    2. Address               [return policy]            |
    3. Loyalty               [address process]          v
        |                     [loyalty balance]    ONE RESPONSE
        v                                           with ALL 3
    Break into                                          concerns
    distinct items                                        addressed
    """
    print("\n" + "=" * 70)
    print("CORRECT APPROACH: Decompose -> Investigate -> Synthesize")
    print("=" * 70)

    print("""
+----------------------------------------------------------------------+
|  STEP 1: DECOMPOSE                                                  |
|  ----------------------------------------------------------------   |
|                                                                      |
|  Customer has 3 distinct concerns:                                   |
|                                                                      |
|  1. Return item #123                                                |
|  2. Update shipping address to 456 Oak St                           |
|  3. Loyalty points inquiry                                           |
|                                                                      |
+----------------------------------------------------------------------+

+----------------------------------------------------------------------+
|  STEP 2: INVESTIGATE (in parallel)                                    |
|  ----------------------------------------------------------------   |
|                                                                      |
|  +--------------+  +--------------+  +--------------+               |
|  | Research:    |  | Research:    |  | Research:    |               |
|  | Return       |  | Address      |  | Loyalty      |               |
|  | policy       |  | update       |  | points       |               |
|  |              |  | process      |  | balance      |               |
|  +------+-------+  +------+-------+  +------+-------+               |
|         |                 |                 |                         |
|         +-----------------+-----------------+                         |
|                           v                                          |
|  STEP 3: SYNTHESIZE                                                   |
|  ----------------------------------------------------------------   |
|                                                                      |
|  Unified response addressing ALL concerns:                           |
|                                                                      |
|  "I can help with all three requests!                               |
|                                                                      |
|  1. RETURN: Your return for item #123 is confirmed.                  |
|     You'll receive a prepaid label within 24 hours.                   |
|                                                                      |
|  2. ADDRESS: Your shipping address has been updated to              |
|     456 Oak St for your next order.                                |
|                                                                      |
|  3. LOYALTY: You currently have 2,500 points worth $25.             |
|     Your recent purchase added 500 points."                          |
+----------------------------------------------------------------------+

    KEY PRINCIPLE: ONE REQUEST = ONE RESPONSE addressing ALL concerns!
""")


def show_decomposition_example():
    """
    Show how to properly decompose a complex request.

    REAL CUSTOMER REQUEST:
    "I bought a laptop last week but it's running slow.
     Also, my account shows I was charged twice for shipping,
     and I want to know if I'm eligible for the new
     extended warranty you advertise."

    DECOMPOSITION:
    1. Technical issue - laptop performance
    2. Billing error - double shipping charge
    3. Warranty inquiry - extended coverage eligibility

    All 3 can be handled in ONE response!
    """
    print("\n" + "=" * 70)
    print("DECOMPOSITION EXAMPLE")
    print("=" * 70)

    complex_request = """
    "I bought a laptop last week but it's running slow.
     Also, my account shows I was charged twice for shipping,
     and I want to know if I'm eligible for the new
     extended warranty you advertise."
    """

    print(f"Complex Request:\n{complex_request}")

    print("\nDecomposed into distinct concerns:")
    print("-" * 50)

    concerns = [
        {
            "id": 1,
            "type": "TECHNICAL_SUPPORT",
            "issue": "Laptop running slow",
            "action": "Troubleshoot performance issues"
        },
        {
            "id": 2,
            "type": "BILLING_REFUND",
            "issue": "Double shipping charge",
            "action": "Verify charges, process refund if confirmed"
        },
        {
            "id": 3,
            "type": "WARRANTY_INQUIRY",
            "issue": "Extended warranty eligibility",
            "action": "Check purchase date, explain warranty options"
        }
    ]

    for concern in concerns:
        print(f"\n   Concern {concern['id']}: {concern['type']}")
        print(f"   Issue: {concern['issue']}")
        print(f"   Action: {concern['action']}")

    print("\n" + "-" * 50)
    print("All 3 can be researched/addressed in parallel!")
    print("Single unified response covers everything.")


def show_parallel_investigation():
    """
    Demonstrate parallel investigation of concerns.

    PERFORMANCE IMPACT:
    If done sequentially (1 then 2 then 3): 15 minutes
    If done in parallel (all at once): 5 minutes
    Time savings: 67%!

    VISUAL:
    -------

    SEQUENTIAL (wrong):             PARALLEL (right):

    [Research 1] 5 min              [Research 1] \
                                   [Research 2]  --- 5 min total
    [Research 2] 5 min              [Research 3] /
    [Research 3] 5 min
    ──────────────                  ─────────────
    Total: 15 min                   Total: 5 min
    """
    print("\n" + "=" * 70)
    print("PARALLEL INVESTIGATION")
    print("=" * 70)

    print("""
+----------------------------------------------------------------------+
|  COORDINATOR spawns 3 research agents IN PARALLEL:                   |
|                                                                      |
|  +--------------------------------------------------------------+   |
|  | Agent 1: Technical Support                                  |   |
|  | - Check laptop specs and known issues                        |   |
|  | - Research troubleshooting steps                              |   |
|  +--------------------------------------------------------------+   |
|                                                                      |
|  +--------------------------------------------------------------+   |
|  | Agent 2: Billing                                            |   |
|  | - Check order #12345 for duplicate charges                  |   |
|  | - Verify if double-charge is real                            |   |
|  +--------------------------------------------------------------+   |
|                                                                      |
|  +--------------------------------------------------------------+   |
|  | Agent 3: Warranty                                           |   |
|  | - Check purchase date                                        |   |
|  | - Review warranty terms and eligibility                      |   |
|  +--------------------------------------------------------------+   |
|                                                                      |
|  All run SIMULTANEOUSLY - saves time!                               |
|  Results collected --> Synthesized into unified response             |
+----------------------------------------------------------------------+

    PERFORMANCE COMPARISON:

    Sequential:  [Research 1] -> [Research 2] -> [Research 3]
                        5 min          5 min          5 min
                    Total: 15 minutes

    Parallel:    [Research 1] \
                 [Research 2]  --- All at once
                 [Research 3] /
                    Total: 5 minutes

    Time saved: 67% with parallel investigation!
""")


def show_synthesis_template():
    """
    Show the template for synthesizing multi-concern responses.
    """
    print("\n" + "=" * 70)
    print("SYNTHESIS TEMPLATE")
    print("=" * 70)

    print("""
+----------------------------------------------------------------------+
|  UNIFIED RESPONSE FORMAT:                                           |
|                                                                      |
|  "I can help with all [NUMBER] requests!                           |
|                                                                      |
|  ----------------------------------------------------------------    |
|                                                                      |
|  1. [CONCERN 1 - brief description]                                 |
|     Resolution: [What was done/found]                                |
|     Next steps: [If any]                                             |
|                                                                      |
|  ----------------------------------------------------------------    |
|                                                                      |
|  2. [CONCERN 2 - brief description]                                 |
|     Resolution: [What was done/found]                                |
|     Next steps: [If any]                                             |
|                                                                      |
|  ----------------------------------------------------------------    |
|                                                                      |
|  3. [CONCERN 3 - brief description]                                 |
|     Resolution: [What was done/found]                                |
|     Next steps: [If any]                                             |
|                                                                      |
|  ----------------------------------------------------------------    |
|                                                                      |
|  Is there anything else I can help you with?"                       |
+----------------------------------------------------------------------+

    KEY: Each concern addressed in ONE response, not multiple exchanges!

    INTERVIEW TIP:
    When asked "how do you handle multiple concerns in one request?",
    use the DECOMPOSE -> INVESTIGATE -> SYNTHESIZE framework.
""")


def demonstrate_key_principle():
    """
    Emphasize the key principle.
    """
    print("\n" + "=" * 70)
    print("KEY PRINCIPLE: ONE REQUEST = ONE RESPONSE")
    print("=" * 70)

    print("""
+----------------------------------------------------------------------+
|  CUSTOMER MINDSET:                                                   |
|                                                                      |
|  "I sent ONE message with ALL my issues.                            |
|   I expect ONE response that addresses them ALL."                   |
|                                                                      |
|  NOT:                                                               |
|  "I sent ONE message but the agent wants to handle                  |
|   each issue separately in multiple exchanges."                      |
|                                                                      |
|  The agent should:                                                  |
|  + Acknowledge all concerns upfront                                  |
|  + Address each one clearly                                          |
|  + Provide complete resolution (or clear next steps)                 |
|  + End with one combined response                                   |
+----------------------------------------------------------------------+

    COMMON MISTAKE:
    Agent thinks "I should handle one thing at a time for clarity."
    Customer thinks "I gave you everything at once - just answer!"

    FIX: Always decompose, investigate, synthesize.
""")


def show_common_mistakes():
    """
    Common errors developers make with multi-concern requests.
    """
    print("\n" + "=" * 70)
    print("MISTAKES DEVELOPERS MAKE")
    print("=" * 70)

    print("""
MISTAKE 1: Treating each concern as a separate interaction
-----------------------------------------------------------------
WRONG:
    Customer: "3 concerns"
    Agent: "Let me handle concern #1 first"
    [5 min later]
    Agent: "Now for concern #2..."
    [Customer frustrated, escalates]

RIGHT:
    Customer: "3 concerns"
    Agent: Decomposes, investigates all 3 in parallel,
           synthesizes ONE response addressing all concerns.


MISTAKE 2: Not decomposing - missing hidden concerns
-------------------------------------------------------
WRONG:
    Customer: "My laptop is slow AND I was charged twice"
    Agent: "Let me help with the laptop first"
    [Misses billing concern entirely!]

RIGHT:
    Customer: "My laptop is slow AND I was charged twice"
    Agent: Decomposes into:
    1. Performance issue
    2. Billing error
    Both addressed in response.


MISTAKE 3: Sequential investigation when parallel is possible
----------------------------------------------------------------
WRONG:
    Agent: "Let me research concern 1..."
    [5 min later]
    Agent: "Let me research concern 2..."
    [5 min later]
    Agent: "Let me research concern 3..."
    Total: 15 minutes!

RIGHT:
    Agent: Spawns 3 research agents in parallel
    All 3 complete at ~same time
    Total: 5 minutes!


MISTAKE 4: Synthesis that's too brief for some concerns
----------------------------------------------------------
WRONG:
    "I've addressed your 3 concerns. Anything else?"

    Customer thinks: "You barely mentioned my billing issue!"

RIGHT:
    "I've addressed your 3 concerns:

    1. LAPTOP: [detailed troubleshooting steps]
    2. BILLING: [refund confirmed, $15.99 credited]
    3. WARRANTY: [eligible, costs $X]

    Each concern gets proper attention in synthesis!
""")


def show_interview_qa():
    """
    Interview questions and expert answer frameworks.
    """
    print("\n" + "=" * 70)
    print("INTERVIEW Q&A - MULTI-CONCERN HANDLING")
    print("=" * 70)

    print("""
Q1: "A customer sends one message with 5 different concerns.
    How do you handle it?"

A:  "I use the DECOMPOSE -> INVESTIGATE -> SYNTHESIZE framework:

    1. DECOMPOSE: Break the message into distinct concerns
       (e.g., refund request, address change, warranty inquiry)

    2. INVESTIGATE: Research each concern in parallel using
       specialized subagents if needed

    3. SYNTHESIZE: Combine results into ONE response that
       addresses all concerns clearly

    Key principle: ONE REQUEST = ONE RESPONSE addressing ALL concerns.
    I never make customers re-explain issues in multiple exchanges.


Q2: "Why is parallel investigation important?"

A:  "Performance. If I handle concerns sequentially (1 then 2 then 3),
    each taking 5 minutes, total time is 15 minutes.

    If I investigate all 3 in parallel, total time is ~5 minutes.
    That's 67% time savings, which directly impacts customer
    satisfaction and operational costs.

    In production systems, this also reduces latency and improves
    the customer experience significantly.


Q3: "What if some concerns require different agents?"

A:  "That's where the coordinator pattern shines:

    1. Coordinator decomposes the request
    2. Coordinator spawns multiple specialized subagents IN PARALLEL
       (billing agent, technical agent, warranty agent)
    3. Each subagent handles their specialty
    4. Coordinator collects results and synthesizes ONE response

    The key is the coordinator handles the complexity so the
    customer gets a simple, unified experience.


Q4: "How do you ensure synthesis is comprehensive?"

A:  "I use a structured template:

    'I can help with [NUMBER] requests:

    1. [CONCERN]: [Resolution] [Next steps if any]
    2. [CONCERN]: [Resolution] [Next steps if any]
    ...

    Is there anything else I can help with?'

    Each concern gets:
    - Clear identification
    - Resolution or status
    - Next steps if action needed
    This ensures nothing is overlooked in synthesis."
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
|  LESSON 1: THE PROBLEM                                             |
+----------------------------------------------------------------------+

    Customers send ONE message with MULTIPLE concerns.
    They expect ONE response addressing ALL concerns.

    Wrong approach: Handle one concern at a time
    - Multiple interactions
    - Customer frustration
    - Escalations

    Right approach: Decompose -> Investigate -> Synthesize
    - One response covers all
    - Customer satisfaction
    - Efficient resolution


+----------------------------------------------------------------------+
|  LESSON 2: THE DECOMPOSE STEP                                       |
+----------------------------------------------------------------------+

    Break the customer message into DISTINCT concerns:

    "Laptop slow, double charge, warranty question"
           |
           v
    +-----------------------+
    | 1. Performance issue |
    | 2. Billing error     |
    | 3. Warranty inquiry  |
    +-----------------------+

    Each concern:
    - Is independently actionable
    - May need different research
    - Needs its own resolution


+----------------------------------------------------------------------+
|  LESSON 3: THE INVESTIGATE STEP                                     |
+----------------------------------------------------------------------+

    Research each concern IN PARALLEL for efficiency:

    Sequential:  [1] -> [2] -> [3] = 15 min total
    Parallel:    [1] \
                 [2]  = 5 min total
                 [3] /

    67% time savings with parallel investigation!


+----------------------------------------------------------------------+
|  LESSON 4: THE SYNTHESIZE STEP                                      |
+----------------------------------------------------------------------+

    Combine results into ONE unified response:

    "I can help with all 3 requests!

    1. LAPTOP: [detailed help]
    2. BILLING: [refund info]
    3. WARRANTY: [eligibility]

    Is there anything else?"

    Each concern gets clear resolution and next steps.


+----------------------------------------------------------------------+
|  LESSON 5: KEY PRINCIPLE                                           |
+----------------------------------------------------------------------+

    ONE REQUEST = ONE RESPONSE addressing ALL concerns

    Customer expectation:
    - Sent one message with all issues
    - Expects comprehensive answer
    - Doesn't want multiple exchanges

    Agent responsibility:
    - Decompose automatically
    - Investigate efficiently
    - Synthesize comprehensively


+----------------------------------------------------------------------+
|  LESSON 6: COMMON MISTAKES                                          |
+----------------------------------------------------------------------+

    1. Treating each concern as separate interaction
    2. Not decomposing - missing hidden concerns
    3. Sequential investigation when parallel is possible
    4. Synthesis that's too brief for some concerns


+----------------------------------------------------------------------+
|  LESSON 7: PRODUCTION IMPACT                                        |
+----------------------------------------------------------------------+

    Real data from telecom company:
    - 40% of escalations from multi-concern mishandling
    - After training on DECOMPOSE->INVESTIGATE->SYNTHESIZE
    - 40% reduction in escalations
    - Customer satisfaction scores improved

    The pattern works in production!


+----------------------------------------------------------------------+
|  KEY FORMULA FOR CERTIFICATION EXAM                                |
+----------------------------------------------------------------------+

    MULTI-CONCERN REQUEST HANDLING:

    1. DECOMPOSE - Break into distinct items
    2. INVESTIGATE - Research each in parallel
    3. SYNTHESIZE - Combine into ONE response

    ONE REQUEST = ONE RESPONSE addressing ALL concerns
+----------------------------------------------------------------------+
""")


if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    print("\n" + "=" * 70)
    print("PRACTICE 4: MULTI-CONCERN REQUEST HANDLING")
    print("=" * 70)
    print("""
This program teaches how to handle requests with multiple concerns:
    1. DECOMPOSE - Break into distinct items
    2. INVESTIGATE - Research each in parallel
    3. SYNTHESIZE - Combine into unified resolution
""")

    demonstrate_wrong_approach()
    demonstrate_correct_approach()
    show_decomposition_example()
    show_parallel_investigation()
    show_synthesis_template()
    demonstrate_key_principle()
    show_common_mistakes()
    show_interview_qa()
    show_what_we_learnt()

    print("""
================================================================================
WHAT JUST HAPPENED?
================================================================================

    1. We saw the WRONG approach:
       - Handle one concern at a time
       - Multiple exchanges
       - Frustrated customers

    2. We saw the CORRECT approach:
       - DECOMPOSE: Identify all distinct concerns
       - INVESTIGATE: Research each in parallel
       - SYNTHESIZE: Combine into unified response

    3. We learned the key principle:
       - ONE request = ONE response addressing ALL concerns
       - Customer expects comprehensive answer, not multiple exchanges

    4. We saw a synthesis template:
       - Number each concern
       - Provide resolution for each
       - List next steps if needed
       - End with offer to help further

    5. We practiced INTERVIEW Q&A:
       - Framework for explaining multi-concern handling
       - Why parallel investigation matters
       - How synthesis ensures comprehensiveness

    6. We learned COMMON MISTAKES:
       - Treating each concern as separate interaction
       - Not decomposing - missing hidden concerns
       - Sequential when parallel possible

    KEY INSIGHT:
    Multi-concern requests are an opportunity to exceed expectations.
    Handle all concerns well in one response = happy customer!

    DECOMPOSE -> INVESTIGATE -> SYNTHESIZE
================================================================================
""")
    print("\n" + "=" * 70)
    print("PROGRAM COMPLETE!")
    print("=" * 70)