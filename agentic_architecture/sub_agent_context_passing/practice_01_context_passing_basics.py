"""
+===========================================================================+
|                                                                           |
|  PRACTICE 1: CONTEXT PASSING BASICS                                       |
|                                                                           |
|  The Golden Rule: Subagents do NOT automatically inherit context!       |
|  + REAL-TIME SCENARIOS + MISTAKES + INTERVIEW GUIDE                      |
|                                                                           |
+===========================================================================+

INTERVIEW PREP: "How do subagents get context in multi-agent systems?"
This question tests your understanding of the fundamental isolation principle.

REAL-TIME SCENARIO: Your production multi-agent system starts giving
wrong recommendations. Users complain. Investigation reveals: subagent B
was supposed to use subagent A's output, but the coordinator forgot to
pass it. The output was generated but never delivered!

===========================================================================
 THE FUNDAMENTAL RULE: CONTEXT ISOLATION
===========================================================================

    +-----------------------------------------------------------------------+
    |  NEVER ASSUME subagents automatically share context!                  |
    |  NEVER assume subagent A knows what subagent B produced!               |
    +-----------------------------------------------------------------------+

    What beginners think happens:
    +---------------------------+     +---------------------------+
    | Coordinator knows         | --> | Subagent automatically    |
    | everything                |     | has all that context      |
    +---------------------------+     +---------------------------+

    What ACTUALLY happens:
    +---------------------------+     +---------------------------+
    | Coordinator knows         |     | Subagent ONLY has         |
    | everything                | --> | what was explicitly       |
    |                           |     | passed to it              |
    +---------------------------+     +---------------------------+
                                      | CANNOT see coordinator    |
                                      | history automatically!    |
                                      +---------------------------+

===========================================================================
 VISUAL: THE ISOLATION PRINCIPLE
===========================================================================

    +=======================================================================+
    ||                                                                      ||
    ||  COORDINATOR (The Brain)                                            ||
    ||  +--------------------------------------------------------------+   ||
    ||  | - Knows FULL conversation history                            |   ||
    ||  | - Knows ALL subagent outputs                                  |   ||
    ||  | - Knows user preferences, history, constraints                 |   ||
    ||  | - RESPONSIBLE for passing info to subagents                   |   ||
    ||  +--------------------------------------------------------------+   ||
    ||                              |                                     ||
    ||        +---------------------+---------------------+                ||
    ||        |                     |                     |                 ||
    ||        v                     v                     v                 ||
    ||  +===============+    +===============+    +===============+         ||
    ||  |  SUBAGENT A  |    |  SUBAGENT B  |    |  SUBAGENT C  |         ||
    ||  |              |    |              |    |              |         ||
    ||  | Context:     |    | Context:     |    | Context:     |         ||
    ||  | ONLY what    |    | ONLY what    |    | ONLY what    |         ||
    ||  | was passed  |    | was passed  |    | was passed  |         ||
    ||  | to it!       |    | to it!       |    | to it!       |         ||
    ||  |              |    |              |    |              |         ||
    ||  | CANNOT see   |    | CANNOT see   |    | CANNOT see   |         ||
    ||  | Subagent B/C |    | Subagent A/C |    | Subagent A/B |         ||
    ||  +===============+    +===============+    +===============+         ||
    ||                                                                      ||
    ||  KEY INSIGHT: Each subagent has ISOLATED context!                    ||
    ||  If coordinator doesn't pass it, subagent doesn't have it!         ||
    ||                                                                      ||
    +=======================================================================+

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


# ============================================================================
# REAL-TIME SCENARIOS: When Context Isolation Breaks Production
# ============================================================================

def show_real_time_scenarios():
    """
    Production scenarios where context isolation causes failures.
    """

    print("\n" + "=" * 70)
    print("REAL-TIME SCENARIOS: When Context Isolation Breaks Things")
    print("=" * 70)

    print("""
    +======================================================================+
    ||  SCENARIO #1: The Missing User Profile                              ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  CONTEXT: E-commerce recommendation system                           ||
    ||                                                                      ||
    ||  WHAT HAPPENED:                                                      ||
    ||  1. Coordinator receives: "Recommend products for user X"          ||
    ||  2. Spawns Product-Research subagent                                ||
    ||  3. Subagent returns: Generic recommendations                       ||
    ||  4. User gets SAME recommendations as everyone else!               ||
    ||                                                                      ||
    ||  ROOT CAUSE:                                                        ||
    ||  - Coordinator knew user X has 3 kids, VIP status, $500 budget    ||
    ||  - But DIDN'T pass user profile to subagent!                        ||
    ||  - Subagent had no idea who it was recommending for               ||
    ||                                                                      ||
    ||  REAL CONSEQUENCE:                                                   ||
    ||  - User sees baby products (has 3 kids!) but no recommendations    ||
    ||  - VIP user gets same treatment as new user                        ||
    ||  - Lost revenue, confused users, support tickets                    ||
    ||                                                                      ||
    ||  LESSON: Always pass USER CONTEXT explicitly!                       ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  SCENARIO #2: The Silent Data Loss                                  ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  CONTEXT: Research synthesis pipeline                               ||
    ||                                                                      ||
    ||  WHAT HAPPENED:                                                      ||
    ||  1. Subagent A researches: finds critical safety issue             ||
    ||  2. Subagent B writes report (uses Subagent A output)               ||
    ||  3. Final report: Safety issue MISSING!                             ||
    ||  4. Product shipped with known vulnerability                        ||
    ||                                                                      ||
    ||  ROOT CAUSE:                                                        ||
    ||  - Subagent A clearly documented the safety issue                  ||
    ||  - Coordinator passed Subagent A output to Subagent B              ||
    ||  - But Subagent B's prompt didn't INSTRUCT it to include A's output ||
    ||  - Subagent B thought it should generate fresh content             ||
    ||                                                                      ||
    ||  REAL CONSEQUENCE:                                                   ||
    ||  - Critical finding lost in the chain                               ||
    ||  - Had to recall product, massive PR damage                        ||
    ||  - Team blamed Subagent B, but coordinator was at fault            ||
    ||                                                                      ||
    ||  LESSON: Context passing REQUIRES explicit instruction!             ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  SCENARIO #3: The Dependency Chain Break                            ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  CONTEXT: Multi-step data processing pipeline                       ||
    ||                                                                      ||
    ||  Flow:                                                              ||
    ||  [Fetcher] --> [Cleaner] --> [Analyzer] --> [Reporter]              ||
    ||                                                                      ||
    ||  WHAT HAPPENED:                                                      ||
    ||  1. Fetcher correctly gets raw data (10,000 records)                ||
    ||  2. Cleaner runs but subagent forgets record count context          ||
    ||  3. Cleaner passes output to Analyzer but says "cleaned data ready"  ||
    ||  4. Analyzer doesn't know 8,000 of 10,000 were filtered            ||
    ||  5. Analyzer gives wrong percentages (thinks 100% processed)       ||
    ||                                                                      ||
    ||  ROOT CAUSE:                                                        ||
    ||  - Cleaner's output didn't include metadata: records_in, records_out ||
    ||  - Analyzer assumed full dataset                                     ||
    ||                                                                      ||
    ||  LESSON: Always include METADATA about the work done!               ||
    ||                                                                      ||
    +======================================================================+
    """)


# ============================================================================
# MISTAKES DEVELOPERS MAKE
# ============================================================================

def show_mistakes_developers_make():
    """
    Common mistakes with explanations.
    """

    print("\n" + "=" * 70)
    print("MISTAKES DEVELOPERS MAKE - Expert Warnings")
    print("=" * 70)

    print("""
    +======================================================================+
    ||  MISTAKE #1: "The coordinator knows the context already"            ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WHY IT'S WRONG:                                                     ||
    ||  The coordinator having context is IRRELEVANT.                       ||
    ||  Subagents are SEPARATE processes with their own context windows!   ||
    ||                                                                      ||
    ||  BAD CODE:                                                          ||
    ||  spawn_agent(description="Analyze the data")                        ||
    ||  // Context is implied from coordinator conversation               ||
    ||  // Subagent has NO IDEA what "the data" refers to!                ||
    ||                                                                      ||
    ||  CORRECT CODE:                                                      ||
    ||  spawn_agent(                                                       ||
    ||      description="Analyze Q3 sales data",                          ||
    ||      context={                                                      ||
    ||          "data": q3_sales_data,                                     ||
    ||          "previous_quarter": q2_sales_data,                        ||
    ||          "user_goal": "Compare quarterly trends"                   ||
    ||      }                                                               ||
    ||  )                                                                  ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  MISTAKE #2: "Subagent A will tell Subagent B what it found"       ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WHY IT'S WRONG:                                                     ||
    ||  Subagents CANNOT communicate directly! The coordinator must        ||
    ||  collect A's output and pass it to B explicitly.                    ||
    ||                                                                      ||
    ||  BAD FLOW:                                                          ||
    ||                                                                      ||
    ||  Subagent A -----> Works -----> Done! Output stored                  |
    ||                         |                                           |
    ||                         x (Never delivered to B!)                   |
    ||                         |                                           |
    ||  Subagent B -----> Works -----> No context from A!                  |
    ||                                                                      ||
    ||  CORRECT FLOW:                                                      ||
    ||                                                                      ||
    ||  Subagent A -----> Output -----> Coordinator collects                |
    ||                                   |                                  |
    ||                                   v                                  |
    ||                          Coordinator passes to B                    |
    ||                                   |                                  |
    ||                                   v                                  |
    ||  Subagent B -----> Has A's output -----> Can use it                  |
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  MISTAKE #3: "I passed a lot of context, that's enough"              ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WHY IT'S WRONG:                                                     ||
    ||  Context quantity != Context quality. You must include:             ||
    ||  - WHAT task to perform                                              ||
    ||  - WHY this task exists                                              ||
    ||  - WHAT output format is expected                                    ||
    ||  - WHAT constraints/requirements apply                               ||
    ||                                                                      ||
    ||  BAD CONTEXT:                                                       ||
    ||  "User wants product recommendations"                               ||
    ||  // Missing: Which user? What preferences? What budget?           ||
    ||                                                                      ||
    ||  GOOD CONTEXT:                                                      ||
    ||  context={                                                           ||
    ||      "user_id": "user_123",                                         ||
    ||      "preferences": {"category": "tech", "price_range": "mid"},     ||
    ||      "budget": 500,                                                 ||
    ||      "purpose": "Birthday gift for husband"                        ||
    ||  }                                                                  ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  MISTAKE #4: "The subagent will figure it out"                      ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WHY IT'S WRONG:                                                     ||
    ||  Subagents don't have intuition. They can only work with what       ||
    ||  they receive. If you don't specify, they guess (often wrong).      ||
    ||                                                                      ||
    ||  BAD:                                                                ||
    ||  "Analyze the sales data and suggest improvements"                 ||
    ||  // Subagent might: summarize, visualize, fix bugs, anything!       ||
    ||                                                                      ||
    ||  GOOD:                                                               ||
    ||  "Calculate: (1) Month-over-month growth % (2) Top 5 products      ||
    ||   by revenue (3) Any anomalies > 20% variance. Format as JSON."    ||
    ||                                                                      ||
    +======================================================================+
    """)


# ============================================================================
# INTERVIEW Q&A
# ============================================================================

def show_interview_qa():
    """
    Interview questions and expert answer frameworks.
    """

    print("\n" + "=" * 70)
    print("INTERVIEW QUESTIONS & EXPERT ANSWERS GUIDE")
    print("=" * 70)

    print("""
    ========================================================================
    INTERVIEW Q1: "How do subagents get context in multi-agent systems?"
    ========================================================================

    EXPECTED ANSWER:
    They don't automatically get anything! The coordinator must explicitly pass
    all needed context to each subagent. This includes task description,
    background information, constraints, and any outputs from previous
    subagents. Subagents have isolated context windows.

    RED FLAGS IN ANSWERS:
    - "They share the coordinator's context" -> Fundamental misunderstanding
    - "They can see other subagent outputs" -> No, never automatically
    - "I'll just pass what's relevant" -> Vague, shows lack of rigor

    +-----------------------------------------------------------------------+
    | EXPERT TIP: Emphasize "explicitly passed" - every time!                |
    | Show you understand it's NOT automatic.                               |
    +-----------------------------------------------------------------------+
    """)

    # Demo with actual API call
    message = client.messages.create(
        model="claude-haiku-4-5-20250601",
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": "As an expert in multi-agent systems, explain in 2 sentences "
                      "how subagents get context. Emphasize the isolation principle."
        }]
    )

    print("\nExample Expert Answer:")
    print(f"    {message.content[0].text[:400]}...")

    print("""
    ========================================================================
    INTERVIEW Q2: "What's wrong with this code?"
    ========================================================================

    CODE:
    coordinator.analyze_task(user_request)
    coordinator.spawn_agent("Generate a report")  # No context passed!

    EXPECTED ANSWER:
    This will fail because the subagent has no idea what to report on.
    The coordinator knows the user request but that's not passed to the
    subagent. You need to pass the user's request explicitly along with
    any relevant background, constraints, and expected format.

    WHAT TO SAY:
    "The subagent is spawned with only a description but no context.
    It doesn't know WHAT to report on, WHO it's for, or WHAT format.
    The coordinator must pass all this explicitly."

    +-----------------------------------------------------------------------+
    | EXPERT TIP: Point out the ISOLATION explicitly.                        |
    | "The coordinator knowing is irrelevant - subagent needs its own copy" |
    +-----------------------------------------------------------------------+
    """)

    print("""
    ========================================================================
    INTERVIEW Q3: "How would you debug a subagent giving wrong answers?"
    ========================================================================

    EXPECTED ANSWER:
    1. Check if subagent received correct context from coordinator
    2. Verify coordinator passed ALL needed information
    3. Check if outputs from previous subagents were passed forward
    4. Review if context was stripped/modified during passing
    5. Check if metadata (sources, confidence) was included

    COMMON MISTAKE:
    Interviewers look for whether you blame the subagent vs the coordinator.
    Most bugs are COORDINATOR failures, not subagent failures!

    ANSWER FRAMEWORK:
    "I first check the coordinator's context passing logic, not the subagent.
    Most issues are upstream - missing context, stripped metadata, or
    incorrect instruction composition."

    +-----------------------------------------------------------------------+
    | EXPERT TIP: Say "check the coordinator first" - shows deep knowledge  |
    +-----------------------------------------------------------------------+
    """)

    print("""
    ========================================================================
    INTERVIEW Q4: "When should you NOT use multi-agent systems?"
    ========================================================================

    EXPECTED ANSWER:
    - Simple, single-step tasks (overhead not worth it)
    - When context must be shared in real-time (latency issues)
    - When task breakdown costs more than doing it directly
    - When you can't reliably pass context (complex dependencies)

    FOLLOW-UP: "What makes context passing reliable?"
    ANSWER: Explicit structure (schemas), metadata inclusion, validation
    at coordinator level, and testing the context passed to each subagent.

    +-----------------------------------------------------------------------+
    | EXPERT TIP: Mention the coordination overhead is real cost!            |
    | Not every problem needs multi-agent architecture.                    |
    +-----------------------------------------------------------------------+
    """)


# ============================================================================
# DEMONSTRATION FUNCTIONS
# ============================================================================

def create_research_agent_message(task: str, context: str) -> list:
    """
    Create a message for a research subagent WITH explicit context.

    This is the CORRECT pattern - we pass all needed information explicitly.

    BAD pattern (what beginners do):
        messages = [{"role": "user", "content": "Research topic X"}]
        // Missing: What topic? What format? What sources?

    GOOD pattern (what we do here):
        We include EVERYTHING the subagent needs to complete the task.
    """
    messages = [
        {
            "role": "user",
            "content": f"""You are a research agent. Complete the following task:

TASK: {task}

CONTEXT (everything you need to know):
{context}

INSTRUCTIONS:
1. Perform the research based on the context provided
2. Return your findings in a structured format
3. Include citations for where each piece of information came from
"""
        }
    ]
    return messages


def run_subagent(task: str, context: str = "") -> str:
    """
    Simulate running a subagent with explicit context passing.

    Args:
        task: What the subagent should do
        context: All background information the subagent needs
    """
    print(f"\n   [SUBAGENT] Task: {task[:50]}...")
    print(f"   [SUBAGENT] Context provided: {len(context)} characters")

    messages = create_research_agent_message(task, context)

    # In real implementation, this would spawn an actual subagent
    # For demo, we show the pattern

    response = client.messages.create(
        model="claude-haiku-4-5-20250601",
        max_tokens=2048,
        messages=messages,
    )

    result = ""
    for block in response.content:
        if block.type == "text" and block.text:
            result = block.text
            break

    return result


def demonstrate_context_passing():
    """
    Demonstrate the CORRECT way to pass context to subagents.
    """
    print("\n" + "=" * 70)
    print("DEMONSTRATION: Research Agent with Explicit Context")
    print("=" * 70)

    # THE WRONG WAY - forgetting context
    print("\n[BAD EXAMPLE] What most beginners do:")
    print("-" * 50)
    print("""
    task = "Analyze AAPL stock performance"
    // Forgetting to pass: current price, user's purchase price,
    // their portfolio size, risk tolerance, time horizon...
    run_subagent(task)
    """)
    print("   Result: Subagent has NO idea what to analyze!")

    # THE RIGHT WAY - explicit context
    print("\n[GOOD EXAMPLE] What professionals do:")
    print("-" * 50)

    user_context = """
USER PROFILE:
- Portfolio size: $50,000
- Risk tolerance: Medium
- Time horizon: 5 years
- Current AAPL holdings: 100 shares at $150 average cost

CURRENT DATA:
- AAPL current price: $178.50
- Market trend: Bullish
- Recent news: Strong iPhone sales, Services revenue growing
"""

    task = "Analyze if the user should hold, buy more, or sell their AAPL position"

    print(f"Context passed to subagent:\n{user_context[:200]}...")
    result = run_subagent(task, user_context)

    print(f"\n   Subagent Response (first 200 chars):\n   {result[:200]}...")

    return result


def demonstrate_isolated_context():
    """
    Demonstrate that subagents have ISOLATED context.
    """
    print("\n" + "=" * 70)
    print("CRITICAL CONCEPT: Subagent Context is ISOLATED")
    print("=" * 70)

    print("""
    +=======================================================================+
    ||  COORDINATOR (The Hub)                                              ||
    ||  +--------------------------------------------------------------+   ||
    ||  | - Knows full conversation history                            |   ||
    ||  | - Knows all subagent outputs                                  |   ||
    ||  | - Knows user preferences, history, constraints                 |   ||
    ||  +--------------------------------------------------------------+   ||
    ||                              |                                     ||
    ||        +---------------------+---------------------+                ||
    ||        |                     |                     |                 ||
    ||        v                     v                     v                 ||
    ||  +===============+    +===============+    +===============+       ||
    ||  |  SUBAGENT A  |    |  SUBAGENT B  |    |  SUBAGENT C  |       ||
    ||  |              |    |              |    |              |       ||
    ||  | Context: ONLY|    | Context: ONLY|    | Context: ONLY|       ||
    ||  | what was     |    | what was     |    | what was     |       ||
    ||  | passed to it |    | passed to it |    | passed to it |       ||
    ||  | explicitly!  |    | explicitly!   |    | explicitly!  |       ||
    ||  |              |    |              |    |              |       ||
    ||  | CANNOT see   |    | CANNOT see   |    | CANNOT see   |       ||
    ||  | Subagent B/C |    | Subagent A/C |    | Subagent A/B |       ||
    ||  +===============+    +===============+    +===============+       ||
    ||                                                                      ||
    +=======================================================================+
    """)

    print("\nExample: If Subagent A researches weather in Tokyo,")
    print("         Subagent B cannot automatically see that information!")
    print("         You MUST pass it explicitly if B needs it.")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    print("\n" + "=" * 70)
    print("PRACTICE 1: CONTEXT PASSING BASICS")
    print("=" * 70)
    print("""
This program teaches the FUNDAMENTAL rule of multi-agent systems:
    Subagents do NOT automatically inherit context!

Every piece of information a subagent needs must be EXPLICITLY passed.
    """)

    # Show all enhanced sections
    show_real_time_scenarios()
    show_mistakes_developers_make()
    show_interview_qa()
    demonstrate_context_passing()
    demonstrate_isolated_context()

    print("\n" + "=" * 70)
    print("WHAT WE HAVE LEARNT")
    print("=" * 70)
    print("""
    +======================================================================+
    ||  1. THE GOLDEN RULE:                                                ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  Subagents do NOT automatically inherit context from coordinator!   ||
    ||  Every piece of information a subagent needs must be EXPLICITLY     ||
    ||  passed to it. This includes:                                       ||
    ||                                                                      ||
    ||  - WHAT task to perform                                             ||
    ||  - WHY this task exists                                             ||
    ||  - WHO the user is and their preferences                            ||
    ||  - ANY outputs from previous subagents                              ||
    ||  - METADATA about the work (sources, confidence, timestamps)         ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  2. REAL-TIME SCENARIOS WHERE THIS BREAKS:                         ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  - Missing user profile (generic recommendations)                   ||
    ||  - Silent data loss (subagent B ignores A's output)                 ||
    ||  - Dependency chain breaks (missing metadata about work done)       ||
    ||                                                                      ||
    ||  KEY INSIGHT: The output was GENERATED but never DELIVERED!          ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  3. COMMON MISTAKES:                                                 ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  MISTAKE #1: Assuming coordinator knowing = subagent knowing        ||
    ||  MISTAKE #2: Assuming subagents can communicate directly            ||
    ||  MISTAKE #3: Passing quantity over quality of context              ||
    ||  MISTAKE #4: Expecting subagent to "figure it out"                 ||
    ||                                                                      ||
    ||  ALL of these lead to production failures!                          ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  4. INTERVIEW TIPS:                                                  ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  - Say "explicitly passed" - every time!                             ||
    ||  - Explain the COORDINATOR is responsible for passing               ||
    ||  - Most bugs are COORDINATOR failures, not subagent failures       ||
    ||  - Debug by checking coordinator's context passing first            ||
    ||                                                                      ||
    ||  EXPECTED ANSWER STRUCTURE:                                          ||
    ||  1. State: "Subagents have isolated context"                        ||
    ||  2. Explain: "Coordinator must explicitly pass everything"          ||
    ||  3. Give example: Show what good context passing looks like         ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  5. KEY RULES TO MEMORIZE:                                           ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  RULE #1: Context is NEVER inherited, ALWAYS passed explicitly      ||
    ||  RULE #2: Subagent A cannot see subagent B's output automatically  ||
    ||  RULE #3: Coordinator is responsible for context routing           ||
    ||  RULE #4: Include metadata (sources, confidence) when passing       ||
    ||  RULE #5: Be SPECIFIC in context, not just "relevant info"           ||
    ||                                                                      ||
    +======================================================================+

    Next: practice_02_attribution_failure.py shows what happens when
    metadata is stripped during context passing!
    """)

    print("\n" + "=" * 70)
    print("PROGRAM COMPLETE!")
    print("=" * 70)


"""
+===========================================================================+
|                                                                           |
|  KEY CONCEPTS FROM THIS FILE:                                             |
|                                                                           |
|  FUNDAMENTAL: Context is isolated, never inherited!                       |
|                                                                           |
|  REAL-TIME SCENARIOS:                                                     |
|  - Missing user profile causes generic recommendations                    |
|  - Silent data loss when outputs aren't passed forward                   |
|  - Dependency breaks when metadata is missing                             |
|                                                                           |
|  MISTAKES TO AVOID:                                                       |
|  - Assuming coordinator context = subagent context                        |
|  - Assuming subagents can communicate directly                            |
|  - Vague context passing                                                  |
|  - Expecting subagents to "figure it out"                                 |
|                                                                           |
|  INTERVIEW PREP:                                                          |
|  - "How do subagents get context?" -> They DON'T get it automatically   |
|  - "Debug approach" -> Check coordinator first!                           |
|  - "When not to use multi-agent" -> Simple tasks, real-time needs        |
|                                                                           |
+===========================================================================+
"""