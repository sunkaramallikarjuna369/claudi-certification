"""
PRACTICE 2: DYNAMIC SUBAGENT SELECTION
======================================
The coordinator DECIDES which agents are needed based on the task!

+------------------------------------------------------------------+
|                 DYNAMIC AGENT SELECTION FLOW                      |
+------------------------------------------------------------------+
|                                                                    |
|   User Request                                                     |
|        |                                                           |
|        v                                                           |
|   +----------------+                                              |
|   | REQUEST PARSER  |  <-- Analyze intent, extract requirements    |
|   +----------------+                                              |
|        |                                                           |
|        v                                                           |
|   +----------------+                                              |
|   | AGENT SELECTOR  |  <-- Match request to appropriate agents    |
|   +----------------+                                              |
|        |                                                           |
|        +----> [Calculator] if math detected                       |
|        +----> [Researcher] if info requested                       |
|        +----> [Analyst] if comparison/evaluation                  |
|        +----> [Writer] if output format needed                    |
|        |                                                           |
|        v                                                           |
|   +----------------+                                              |
|   | EXECUTE SELECTED|                                              |
|   +----------------+                                              |
|        |                                                           |
|        v                                                           |
|   +----------------+                                              |
|   | SYNTHESIZE     |  <-- Combine results, produce final output   |
|   +----------------+                                              |
|        |                                                           |
|        v                                                           |
|      OUTPUT                                                        |
|                                                                    |
+------------------------------------------------------------------+

KEY CONCEPT: The system dynamically selects agents based on the request,
not a hardcoded pipeline. Same coordinator, different agents per request.
"""

import os
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional, Callable
from enum import Enum

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY", "")
api_base = os.getenv("ANTHROPIC_API_BASE", "")

from anthropic import Anthropic
client_kwargs = {"api_key": api_key} if api_key else {}
if api_base:
    client_kwargs["base_url"] = api_base
client = Anthropic(**client_kwargs)


# ============================================================================
# REAL-TIME SCENARIO: Customer Support Ticket Processing
# ============================================================================
"""
PRODUCTION SCENARIO: Automated Customer Support

A customer submits a ticket: "I was charged $50 twice for my subscription.
Also, I want to upgrade to premium. Can you compare your plans?"

DYNAMIC SELECTION MUST:
1. ANALYST agent: Detect "charged twice" -> triggers refund investigation
2. RESEARCHER agent: Look up account, transaction history
3. WRITER agent: Draft refund confirmation + plan comparison

The system automatically selects agents based on intent detection, not hardcoded rules.

+---------------------------+
| Customer Ticket Input     |
+---------------------------+
         |
         +---> "charged twice" ---> ANALYST (refund logic)
         |
         +---> "compare plans" ---> RESEARCHER (plan data)
         |
         +---> "write report" ---> WRITER (compose response)
         |
         v
   [Final Response to Customer]
"""


# ============================================================================
# AGENT TYPE DEFINITIONS
# ============================================================================

class AgentType(Enum):
    """
    Types of agents available in our system.

    ASCII ART: Agent Registry
    =========================

    +----------------+----------------+----------------+----------------+
    | CALCULATOR     | RESEARCHER     | ANALYST        | WRITER         |
    | [Math Ops]     | [Info Gather]  | [Evaluation]   | [Formatting]   |
    +----------------+----------------+----------------+----------------+

    Each agent has a specialty. The coordinator picks the right ones.
    """
    CALCULATOR = "calculator"
    RESEARCHER = "researcher"
    ANALYST = "analyst"
    WRITER = "writer"


# ============================================================================
# MISTAKE #1: Hardcoded Agent Selection (No Dynamic Logic)
# ============================================================================
"""
COMMON ERROR: Using if/else chains that always select the same agents

    if request == "math":
        agents = [CALCULATOR]
    elif request == "info":
        agents = [RESEARCHER]

WHY THIS BREAKS:
- Only handles exact matches, misses variations
- Can't combine multiple intents ("Calculate AND explain")
- Fragile - breaks when user phrasing changes
- No graceful fallback for unknown request types

BETTER APPROACH: Keyword scoring with threshold
- Count matches for each agent type
- Select agents above score threshold
- Default to RESEARCHER if no strong match
"""


# ============================================================================
# MISTAKE #2: Not Handling Multi-Intent Requests
# ============================================================================
"""
COMMON ERROR: Only selecting ONE agent, ignoring compound requests

INCORRECT:
    "What is AI? Write a report about it."
    -> Selects only WRITER (ignores that research is needed first)

CORRECT:
    "What is AI? Write a report about it."
    -> Detects: RESEARCHER (understand AI) + WRITER (create report)
    -> Executes: Researcher first, then Writer with research context

THE RULE: Always select ALL agents that match, not just one.
"""


# ============================================================================
# MISTAKE #3: No Confidence Scoring for Selection
# ============================================================================
"""
COMMON ERROR: Binary yes/no selection without confidence levels

INCORRECT:
    if "calculate" in request:
        use_calculator = True
    # Either 100% or 0% confidence

CORRECT:
    calculate_score = sum(1 for kw in math_keywords if kw in request)
    research_score = sum(1 for kw in info_keywords if kw in request)

    # Scores: calculate=3, research=1
    # Select Calculator (3 >= threshold 2)
    # Also select Researcher (1 >= threshold 1)
    # Confidence: Calculator=75%, Researcher=25%

This allows nuanced selection and graceful degradation.
"""


# ============================================================================
# INTERVIEW Q&A: Dynamic Agent Selection
# ============================================================================
"""
Q: How do you determine which agents to use for a given request?
A: We use a multi-stage approach:

   STAGE 1: Intent Classification
   - Parse the request to identify key intents
   - Use keyword matching and semantic analysis
   - Score each potential agent type

   STAGE 2: Agent Mapping
   - Map intents to available agents
   - Some intents map to multiple agents
   - Some agents can handle multiple intents

   STAGE 3: Pipeline Construction
   - Order agents based on dependencies
   - Agent B may need Agent A's output
   - Create execution plan

Q: What happens if the request doesn't match any known pattern?
A: Fallback strategy:
   - Start with RESEARCHER as default (gather info first)
   - Use ANALYST to understand context
   - If still unclear, ask clarifying questions
   - Log unknown patterns for future improvement

Q: How do you handle conflicting agent recommendations?
A: Priority-based resolution:
   - ANALYST > WRITER > RESEARCHER > CALCULATOR for conflicts
   - Or use voting if multiple agents agree
   - Or return multiple options to user
   - Always log conflicts for review
"""


# ============================================================================
# AGENT IMPLEMENTATIONS
# ============================================================================

def call_calculator_agent(problem: str) -> str:
    """
    CALCULATOR AGENT - Handles math problems!

    ASCII ART: Calculator Flow
    ==========================

    Input: "What is 15% of 200?"
           |
           v
    +--------------+
    |   PARSE      |  Extract: operand1=15, operator=%, operand2=200
    +--------------+
           |
           v
    +--------------+
    |   CALCULATE   |  15 / 100 * 200 = 30
    +--------------+
           |
           v
    Output: "15% of 200 = 30"
    """
    print(f"   [CALCULATOR] Processing: {problem}")

    prompt = f"""You are a calculator assistant. Solve this math problem.

Problem: {problem}

Provide only the final answer with a brief explanation."""

    response = client.messages.create(
        model="claude-haiku-4-5-20250601",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
        tools=[]
    )

    result = response.content[0].text
    print(f"   [CALCULATOR] Done!")
    return result


def call_researcher_agent(topic: str) -> str:
    """
    RESEARCHER AGENT - Gathers information!

    ASCII ART: Researcher Flow
    =========================

    Input: "Explain how blockchain works"
           |
           v
    +-----------------+
    |   DECOMPOSE     |  Break into: blockchain, consensus, mining
    +-----------------+
           |
           v
    +-----------------+
    |   GATHER FACTS  |  For each subtopic, find key information
    +-----------------+
           |
           v
    +-----------------+
    |   SYNTHESIZE    |  Combine into coherent research summary
    +-----------------+
           |
           v
    Output: Structured research findings
    """
    print(f"   [RESEARCHER] Researching: {topic}")

    prompt = f"""You are a research assistant. Provide key information about this topic.

Topic: {topic}

Provide:
1. Brief definition
2. Key facts (3-5 points)
3. Why it's important

Be concise but thorough."""

    response = client.messages.create(
        model="claude-haiku-4-5-20250601",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
        tools=[]
    )

    result = response.content[0].text
    print(f"   [RESEARCHER] Done!")
    return result


def call_analyst_agent(data: str) -> str:
    """
    ANALYST AGENT - Analyzes and interprets data!

    ASCII ART: Analyst Flow
    ======================

    Input: [Research Data]
           |
           v
    +---------------+
    |   EVALUATE    |  Assess quality, completeness, accuracy
    +---------------+
           |
           v
    +---------------+
    |   COMPARE     |  Benchmark against known standards
    +---------------+
           |
           v
    +---------------+
    |   RECOMMEND   |  Provide actionable insights
    +---------------+
           |
           v
    Output: Analysis with recommendations
    """
    print(f"   [ANALYST] Analyzing: {data[:50]}...")

    prompt = f"""You are an analyst assistant. Analyze the following data/information.

Data: {data}

Provide:
1. Key patterns or trends
2. Strengths and weaknesses
3. Simple conclusion or recommendation"""

    response = client.messages.create(
        model="claude-haiku-4-5-20250601",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
        tools=[]
    )

    result = response.content[0].text
    print(f"   [ANALYST] Done!")
    return result


def call_writer_agent(content: str, style: str = "clear") -> str:
    """
    WRITER AGENT - Creates polished output!

    ASCII ART: Writer Flow
    ====================

    Input: [Facts + Analysis + Requirements]
           |
           v
    +-------------+
    |   STRUCTURE  |  Organize: intro, body, conclusion
    +-------------+
           |
           v
    +-------------+
    |   DRAFT      |  Write initial version
    +-------------+
           |
           v
    +-------------+
    |   POLISH     |  Refine for clarity, flow, style
    +-------------+
           |
           v
    Output: Final formatted document
    """
    print(f"   [WRITER] Writing ({style} style)...")

    prompt = f"""You are a professional writer. Create polished content.

Content to work with:
{content}

Style: {style}

Create a well-structured, engaging response."""

    response = client.messages.create(
        model="claude-haiku-4-5-20250601",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
        tools=[]
    )

    result = response.content[0].text
    print(f"   [WRITER] Done!")
    return result


# ============================================================================
# DYNAMIC SELECTION LOGIC
# ============================================================================

def analyze_request(request: str) -> Dict[str, Any]:
    """
    Analyze the request and DECIDE which agents are needed!

    This implements scoring-based dynamic selection.
    Each keyword category contributes to an agent's score.
    Agents with score above threshold are selected.
    """

    print(f"\n[COORDINATOR] Analyzing request...")
    print(f"   Request: \"{request}\"")

    # Define keyword categories with weights
    math_keywords = {
        "keywords": ["calculate", "math", "number", "+", "-", "*", "/",
                     "percent", "%", "what is", "cost", "total", "sum", "price"],
        "weight": 1.0
    }

    research_keywords = {
        "keywords": ["what is", "what are", "how does", "explain",
                     "tell me about", "describe", "define", "information",
                     "tell me", "definition", "meaning"],
        "weight": 1.0
    }

    analysis_keywords = {
        "keywords": ["compare", "versus", "vs", "better", "worse",
                     "should", "recommend", "pros and cons", "analyze",
                     "evaluation", "assessment", "difference between"],
        "weight": 1.2  # Higher weight for explicit analysis requests
    }

    write_keywords = {
        "keywords": ["write", "report", "summary", "explain to",
                     "create", "document", "article", "draft", "compose"],
        "weight": 1.0
    }

    # Calculate scores
    scores = {
        AgentType.CALCULATOR: 0,
        AgentType.RESEARCHER: 0,
        AgentType.ANALYST: 0,
        AgentType.WRITER: 0
    }

    request_lower = request.lower()

    # Math score
    for kw in math_keywords["keywords"]:
        if kw in request_lower:
            scores[AgentType.CALCULATOR] += math_keywords["weight"]

    # Research score
    for kw in research_keywords["keywords"]:
        if kw in request_lower:
            scores[AgentType.RESEARCHER] += research_keywords["weight"]

    # Analysis score
    for kw in analysis_keywords["keywords"]:
        if kw in request_lower:
            scores[AgentType.ANALYST] += analysis_keywords["weight"]

    # Write score
    for kw in write_keywords["keywords"]:
        if kw in request_lower:
            scores[AgentType.WRITER] += write_keywords["weight"]

    # Select agents above threshold (0.5 minimum)
    threshold = 0.5
    selected_agents = []
    selection_reasons = {}

    for agent_type, score in scores.items():
        if score >= threshold:
            selected_agents.append(agent_type)
            selection_reasons[agent_type.value] = f"score={score:.1f}"
            print(f"   {agent_type.value.upper()}: score={score:.1f} -> SELECTED")
        else:
            print(f"   {agent_type.value.upper()}: score={score:.1f} -> not selected")

    # Default to RESEARCHER if nothing selected
    if not selected_agents:
        selected_agents.append(AgentType.RESEARCHER)
        selection_reasons["researcher"] = "default fallback"
        print("   No strong match -> Defaulting to Researcher")

    print(f"\n   Selected {len(selected_agents)} agent(s): {[a.value for a in selected_agents]}")

    return {
        "agents": selected_agents,
        "scores": scores,
        "reasons": selection_reasons,
        "threshold": threshold
    }


def execute_agents(agent_list: List[AgentType], request: str) -> Dict[AgentType, str]:
    """
    Execute the selected agents in order!

    ASCII ART: Execution Pipeline
    ============================

    Agent List: [Researcher, Analyst, Writer]

    +---+    +----------+    +---------+    +-------+
    | R | -> | ANALYST  | -> | WRITER  | -> | OUTPUT|
    +---+    +----------+    +---------+    +-------+

    Each agent receives context from all previous agents.
    """
    results = {}
    context = request

    for agent in agent_list:
        print(f"\n{'='*50}")
        print(f"[COORDINATOR] Calling {agent.value.upper()} agent...")

        if agent == AgentType.CALCULATOR:
            result = call_calculator_agent(request)
            results[agent] = result
            context = f"User asked: {request}\n\nCalculation result: {result}"

        elif agent == AgentType.RESEARCHER:
            result = call_researcher_agent(context)
            results[agent] = result
            context = result  # Next agent gets research results

        elif agent == AgentType.ANALYST:
            result = call_analyst_agent(context)
            results[agent] = result
            context = result  # Next agent gets analysis

        elif agent == AgentType.WRITER:
            result = call_writer_agent(context)
            results[agent] = result
            # Writer is usually last, no context update needed

    return results


def coordinate_request(request: str) -> str:
    """
    Main coordinator function - orchestrates everything!

    ASCII ART: Full Orchestration
    ============================

    User Request
         |
         v
    +-----------------+
    | ANALYZE         |  <-- Analyze request
    | (select agents) |
    +-----------------+
         |
         v
    +-----------------+
    | EXECUTE         |  <-- Run selected agents
    | (in sequence)   |
    +-----------------+
         |
         v
    +-----------------+
    | SYNTHESIZE      |  <-- Combine outputs
    +-----------------+
         |
         v
      Final Output
    """
    print(f"\n{'='*60}")
    print(f"[COORDINATOR] Processing: {request}")
    print('='*60)

    # Step 1: Analyze and select agents
    analysis = analyze_request(request)
    selected_agents = analysis["agents"]

    # Step 2: Execute agents
    agent_results = execute_agents(selected_agents, request)

    # Step 3: Synthesize final output
    print(f"\n{'='*50}")
    print("[COORDINATOR] Synthesizing final output...")

    # Priority order: Writer > Analyst > Researcher > Calculator
    if AgentType.WRITER in agent_results:
        final_output = agent_results[AgentType.WRITER]
    elif AgentType.ANALYST in agent_results:
        final_output = agent_results[AgentType.ANALYST]
    elif AgentType.RESEARCHER in agent_results:
        final_output = agent_results[AgentType.RESEARCHER]
    elif AgentType.CALCULATOR in agent_results:
        final_output = agent_results[AgentType.CALCULATOR]
    else:
        final_output = "No results generated"

    print("[COORDINATOR] Orchestration complete!")

    return final_output


# ============================================================================
# DEMONSTRATION
# ============================================================================

def demonstrate_selection_scenarios():
    """
    Show how dynamic selection handles different request types.
    """
    test_cases = [
        ("What is 15% of 200?", "Simple math - should use Calculator only"),
        ("What is artificial intelligence?", "Information request - should use Researcher"),
        ("Compare solar vs wind energy. Write a brief report.",
         "Complex task - should use Researcher + Analyst + Writer"),
        ("Calculate the ROI if I invest $10,000 at 7% for 5 years.",
         "Math + Analysis - Calculator + Analyst"),
    ]

    for i, (request, description) in enumerate(test_cases, 1):
        print(f"\n{'#'*60}")
        print(f"TEST CASE {i}: {description}")
        print(f"{'#'*60}")
        print(f"Request: \"{request}\"\n")

        result = coordinate_request(request)

        print(f"\n{'='*50}")
        print("RESULT:")
        print(f"{'='*50}")
        print(result[:500] + ("..." if len(result) > 500 else ""))


# ============================================================================
# WHAT WE HAVE LEARNT
# ============================================================================
"""
=============================================================================
WHAT WE HAVE LEARNT: Dynamic Subagent Selection
=============================================================================

1. CORE CONCEPT
   ------------
   - The coordinator ANALYZES each request to determine needed agents
   - Agent selection is DYNAMIC, not hardcoded
   - Same coordinator handles different requests with different agents
   - Multi-intent detection allows selecting multiple agents

2. SCORING-BASED SELECTION
   -----------------------
   - Each agent type has keyword categories
   - Request is scored against each category
   - Agents above threshold are selected
   - Enables nuanced selection (not binary)

3. COMMON MISTAKES TO AVOID
   ------------------------
   MISTAKE 1: Hardcoded Selection
   - Don't use if/else chains that always pick same agents
   - Instead: score each request and select accordingly

   MISTAKE 2: Single Agent Selection
   - Many requests have multiple intents
   - "Explain X and write a report" needs Researcher + Writer
   - Select ALL matching agents, not just one

   MISTAKE 3: No Fallback
   - Requests may not match any known pattern
   - Always have a default fallback (e.g., RESEARCHER)
   - Log unknown patterns for future improvement

4. PRODUCTION CONSIDERATIONS
   -------------------------
   - Implement confidence scoring for selections
   - Add logging to track which agents are selected and why
   - Monitor for bias (are some agents never selected?)
   - A/B test different selection algorithms
   - Consider semantic understanding, not just keyword matching

5. INTERVIEW ANSWER FRAMEWORK
   --------------------------
   "How do you decide which agents to use?"

   Step 1: Explain the analysis phase
   "We analyze each request to identify intents and entities. This could
    be keyword matching, semantic analysis, or ML-based classification."

   Step 2: Describe scoring mechanism
   "Each agent type has a scoring function. The request is evaluated
    against all agents, and those above a threshold are selected."

   Step 3: Handle multi-intent
   "Real requests often have multiple intents. 'What is X and write a
    report' triggers both Researcher and Writer."

   Step 4: Address edge cases
   "For unknown patterns, we have fallbacks like defaulting to Researcher.
    We also log these cases to improve the system."

6. VISUAL SUMMARY
   --------------

   DYNAMIC SELECTION FLOW:

   Request: "Compare A vs B and create a report"

   Analysis:
   +----------------+----------------+
   | Research keywords | 2 matches  | -> RESEARCHER (score: 2.0)
   | Analysis keywords | 1 match    | -> ANALYST (score: 1.2)
   | Writing keywords  | 1 match    | -> WRITER (score: 1.0)
   +----------------+----------------+

   Selection: [RESEARCHER, ANALYST, WRITER]

   Execution Order:
   +--------+    +--------+    +--------+
   |RESEARCH| -> |ANALYST | -> | WRITER | -> Output
   +--------+    +--------+    +--------+

=============================================================================
"""


if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    print("\n" + "="*60)
    print("PRACTICE 2: DYNAMIC SUBAGENT SELECTION")
    print("="*60)

    print("""
+------------------------------------------------------------------+
|                 DYNAMIC AGENT SELECTION FLOW                      |
+------------------------------------------------------------------+
|                                                                    |
|   User Request                                                     |
|        |                                                           |
|        v                                                           |
|   +----------------+                                              |
|   | REQUEST PARSER  |  <-- Analyze intent, extract requirements    |
|   +----------------+                                              |
|        |                                                           |
|        v                                                           |
|   +----------------+                                              |
|   | AGENT SELECTOR  |  <-- Match request to appropriate agents      |
|   +----------------+                                              |
|        |                                                           |
|        +----> [Calculator] if math detected                       |
|        +----> [Researcher] if info requested                       |
|        +----> [Analyst] if comparison/evaluation                  |
|        +----> [Writer] if output format needed                    |
|                                                                    |
+------------------------------------------------------------------+
""")

    demonstrate_selection_scenarios()

    print("\n" + "="*60)
    print("PROGRAM COMPLETE!")
    print("="*60)
    print("\nSee WHAT WE HAVE LEARNT section for comprehensive summary.")