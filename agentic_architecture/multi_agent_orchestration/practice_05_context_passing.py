"""
PRACTICE 5: EXPLICIT CONTEXT PASSING
====================================
THE MOST CRITICAL PATTERN - Pass ALL context to subagents explicitly!

+------------------------------------------------------------------+
|               CONTEXT PASSING ARCHITECTURE                        |
+------------------------------------------------------------------+
|                                                                    |
|   WITHOUT Context Passing (BROKEN):                                |
|   +-----------+        +-----------+        +-----------+         |
|   |COORDINATOR| -----> |  AGENT 1  | -----> |  AGENT 2  |         |
|   +-----------+        +-----------+        +-----------+         |
|                                                                    |
|   Agent 2 sees: "Topic: X"                                         |
|   Agent 2 does NOT see: original request, Agent 1's output,         |
|                         style requirements, constraints            |
|                                                                    |
+------------------------------------------------------------------+
|                                                                    |
|   WITH Context Passing (WORKS):                                    |
|   +-----------+                                                   |
|   |COORDINATOR|                                                   |
|   +-----------+                                                   |
|        |                                                          |
|        v                                                          |
|   +-----------+                                                   |
|   |  AGENT 1  | <-- Gets: [Topic + Original Request]               |
|   +-----------+                                                   |
|        |                                                          |
|        v (passes full context forward)                            |
|   +-----------+                                                   |
|   |  AGENT 2  | <-- Gets: [Topic + Original Request +              |
|   +-----------+        Agent 1's Output + Style + Constraints]    |
|                                                                    |
+------------------------------------------------------------------+

KEY CONCEPT: Subagents are STATELESS. Each call must include EVERYTHING
the agent needs. No inheritance, no shared state, no "just figure it out."
"""

import os
from dotenv import load_dotenv
from typing import Dict, Any, Optional, List

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY", "")
api_base = os.getenv("ANTHROPIC_API_BASE", "")

from anthropic import Anthropic
client_kwargs = {"api_key": api_key} if api_key else {}
if api_base:
    client_kwargs["base_url"] = api_base
client = Anthropic(**client_kwargs)


# ============================================================================
# REAL-TIME SCENARIO: Medical Report Generation
# ============================================================================
"""
PRODUCTION SCENARIO: Patient Medical Report

A medical report must include:
1. Patient history (from intake form)
2. Current symptoms (from examination)
3. Test results (from lab)
4. Diagnosis (from doctor)
5. Treatment plan (from specialist)
6. Follow-up instructions (from protocol)

Without context passing:
- Each agent generates content independently
- Diagnosis might conflict with test results
- Treatment might ignore patient history

With context passing:
- Each agent receives ALL previous information
- Specialist sees: history + symptoms + test results + doctor notes
- Output is coherent and integrated
- No contradictions or missed information

THE RULE: Every agent call is a complete, self-contained unit.
"""

# ============================================================================
# CONTEXT BUILDER FUNCTION
# ============================================================================

def build_complete_context(
    user_request: str,
    style_requirements: Optional[Dict] = None,
    previous_results: Optional[Dict] = None,
    constraints: Optional[Dict] = None,
    additional_info: Optional[Dict] = None
) -> str:
    """
    Build a COMPLETE context string for subagents!

    ASCII ART: Context Building
    ==========================

    +------------------------+
    | ORIGINAL REQUEST       |  (always required)
    +------------------------+
           |
    +------+------+----------+
    |             |          |
    v             v          v
+--------+  +---------+  +----------+
| STYLE  |  | PREVIOUS|  |CONSTRAINTS|
|REQ'S   |  | RESULTS |  |           |
+--------+  +---------+  +----------+
           |             |
           +------+------+
                  |
                  v
    +------------------------+
    | COMPLETE CONTEXT STRING |
    | (everything in one)    |
    +------------------------+

    """
    context_parts = []

    # 1. ORIGINAL REQUEST (always included!)
    context_parts.append("=" * 60)
    context_parts.append("ORIGINAL USER REQUEST")
    context_parts.append("=" * 60)
    context_parts.append(user_request)

    # 2. STYLE REQUIREMENTS (if provided)
    if style_requirements:
        context_parts.append("\n" + "=" * 60)
        context_parts.append("STYLE & FORMAT REQUIREMENTS")
        context_parts.append("=" * 60)

        for key, value in style_requirements.items():
            context_parts.append(f"* {key}: {value}")

    # 3. PREVIOUS RESULTS (if any - THIS IS KEY!)
    if previous_results:
        context_parts.append("\n" + "=" * 60)
        context_parts.append("PREVIOUS WORK (Build upon this!)")
        context_parts.append("=" * 60)

        for agent_name, result in previous_results.items():
            context_parts.append(f"\n--- {agent_name.upper()} RESULTS ---")
            # Truncate long results to prevent token overflow
            truncated = result[:2000] + "..." if len(result) > 2000 else result
            context_parts.append(truncated)

    # 4. CONSTRAINTS (if any)
    if constraints:
        context_parts.append("\n" + "=" * 60)
        context_parts.append("CONSTRAINTS & RULES")
        context_parts.append("=" * 60)

        for key, value in constraints.items():
            context_parts.append(f"* {key}: {value}")

    # 5. ADDITIONAL INFO (if any)
    if additional_info:
        context_parts.append("\n" + "=" * 60)
        context_parts.append("ADDITIONAL INFORMATION")
        context_parts.append("=" * 60)

        for key, value in additional_info.items():
            context_parts.append(f"* {key}: {value}")

    return "\n".join(context_parts)


# ============================================================================
# MISTAKE #1: Assuming Subagents Know Previous Work
# ============================================================================
"""
COMMON ERROR: Thinking agents "inherit" context from previous calls

INCORRECT CODE:
    research = call_researcher(topic)      # Got 500 chars of research
    write = call_writer(topic)              # Writer sees ONLY topic!
                                           # Lost all the research!

WHY THIS BREAKS:
- Each API call is INDEPENDENT
- No memory between calls
- Writer produces generic output with no research
- Entire chain breaks

CORRECT CODE:
    research = call_researcher(topic)      # Got 500 chars of research
    write = call_writer(topic, research)    # Writer gets topic + research

THE FIX: Always pass previous results as context to next agent.
"""


# ============================================================================
# MISTAKE #2: Partial Context (Missing Requirements)
# ============================================================================
"""
COMMON ERROR: Passing some context but missing critical parts

INCORRECT CODE:
    context = f"Topic: {topic}\nResearch: {research}"
    # Missing: style requirements, constraints, original request

WHY THIS BREAKS:
- Agent doesn't know audience level ("Write for kids")
- Agent doesn't know format requirements ("Include bullet points")
- Agent doesn't know constraints ("Under 500 words")
- Output doesn't match requirements

CORRECT CODE:
    context = build_complete_context(
        user_request=original_request,    # Must include!
        style_requirements={"Audience": "High school students"},
        previous_results={"research": research},
        constraints={"Max length": "500 words"}
    )
"""


# ============================================================================
# MISTAKE #3: No Original Request in Later Context
# ============================================================================
"""
COMMON ERROR: Context for Agent 2 doesn't include original request

INCORRECT CODE:
    # Agent 2 context
    context = f"Previous output:\n{agent1_output}"
    # Where did this original request go? Lost!

WHY THIS BREAKS:
- Agent 2 loses sight of what we're actually trying to do
- Might contradict the original intent
- "Write a report" becomes "answer a question"
- Direction drift

CORRECT CODE:
    # Agent 2 context
    context = build_complete_context(
        user_request=original_request,     # ALWAYS include this!
        previous_results={"agent1": agent1_output}
    )
"""

# ============================================================================
# INTERVIEW Q&A: Context Passing
# ============================================================================
"""
Q: Why is explicit context passing so critical?
A: Because LLM API calls are STATELESS. Each call:

   1. Only receives what's in that specific call
   2. Has no memory of previous calls
   3. Can't "see" what other agents did

   Without explicit passing, information is LOST between agents.
   The coordinator must ensure EVERY call contains everything needed.

Q: How do you handle long context that exceeds token limits?
A: Several strategies:

   1. TRUNCATION
   - Keep first N chars + last M chars
   - "The beginning of...the end of"
   - Simple but loses middle content

   2. SUMMARIZATION
   - Summarize previous results before passing
   - "Research found X, Y, Z (3 key points)"
   - Keeps important info, removes noise

   3. HIERARCHICAL PASSING
   - Only pass relevant subset to each agent
   - Agent 2 doesn't need everything from Agent 1
   - Selectively include what's needed

   4. STORE AND REFERENCE
   - Store full results in database
   - Pass only IDs/references
   - Agent can fetch if needed
   - More complex but handles large data

Q: What about context contamination between agents?
A: Good concern! Recommendations:

   1. CLEAR BOUNDARIES
   - Mark each section clearly ("=== AGENT 1 OUTPUT ===")

   2. SEPARATE CONCERNS
   - Research output doesn't include styling instructions
   - Each piece serves a specific purpose

   3. NO CROSS-REFERENCES
   - Agent 2 shouldn't reference Agent 3's work
   - Pass Agent 3's work explicitly to Agent 4
"""


# ============================================================================
# SUBAGENTS WITH COMPLETE CONTEXT
# ============================================================================

def call_researcher_with_context(context: str) -> str:
    """
    Researcher agent with COMPLETE context passed!

    ASCII ART: Researcher with Full Context
    =======================================

    +---------------------+
    | CONTEXT (complete)  |
    +---------------------+
    | Original request    |
    | Style requirements   |
    | (empty for research)|
    | Constraints          |
    +---------------------+
              |
              v
    +---------------------+
    | RESEARCHER AGENT    |
    | - Knows the goal    |
    | - Knows the audience|
    | - Knows constraints |
    | - Can ask clarifying|
    +---------------------+
              |
              v
    +---------------------+
    | RESEARCH OUTPUT     |
    | (structured facts)  |
    +---------------------+
    """
    print(f"   [RESEARCHER] Starting with complete context...")

    prompt = f"""You are a research specialist. Use the complete context provided below.

{context}

TASK:
Conduct thorough research based on the original request and requirements.
Focus on finding accurate, relevant information.
Provide structured findings that can be used by a writer agent.

Format your research as:
1. Key findings (3-5 main points)
2. Supporting details
3. Any data or statistics
4. Important caveats or limitations

Be thorough and accurate."""

    response = client.messages.create(
        model="claude-haiku-4-5-20250601",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
        tools=[]
    )

    result = response.content[0].text
    print(f"   [RESEARCHER] Complete! ({len(result)} chars)")
    return result


def call_writer_with_context(context: str, research_data: str) -> str:
    """
    Writer agent with COMPLETE context + research data!

    ASCII ART: Writer with Full Context + Research
    ===============================================

    +---------------------------+
    | CONTEXT (complete)        |
    +---------------------------+
    | Original request          |
    | Style requirements        |
    | Constraints               |
    +---------------------------+
              |
              v
    +---------------------------+
    | RESEARCH DATA             |
    +---------------------------+
    | (from researcher agent)   |
    +---------------------------+
              |
              v
    +---------------------------+
    | WRITER AGENT              |
    | - Has original goal       |
    | - Knows style needed      |
    | - Has all research        |
    | - Can produce final       |
    +---------------------------+
              |
              v
    +---------------------------+
    | FINAL POLISHED OUTPUT     |
    +---------------------------+
    """
    print(f"   [WRITER] Starting with complete context + research...")

    prompt = f"""You are a professional writer. Use the complete context and research data below.

{context}

RESEARCH DATA TO INCORPORATE:
{research_data}

TASK:
Write the final output based on:
1. The original user request
2. The style requirements
3. The research data provided
4. Any constraints specified

IMPORTANT:
- Follow the style requirements exactly
- Incorporate all relevant research
- Don't add information not in the research
- Stay within any length constraints

Produce the complete, polished final output."""

    response = client.messages.create(
        model="claude-haiku-4-5-20250601",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
        tools=[]
    )

    result = response.content[0].text
    print(f"   [WRITER] Complete! ({len(result)} chars)")
    return result


def call_editor_with_context(
    context: str,
    draft_content: str,
    revision_notes: Optional[List[str]] = None
) -> str:
    """
    Editor agent with COMPLETE context + draft + notes!

    ASCII ART: Editor with All Information
    ======================================

    +---------------------------+
    | CONTEXT                   |
    +---------------------------+
    | Original request          |
    | Style requirements        |
    +---------------------------+
              |
              v
    +---------------------------+
    | DRAFT CONTENT             |
    +---------------------------+
    | (from writer agent)        |
    +---------------------------+
              |
              v
    +---------------------------+
    | REVISION NOTES            |
    +---------------------------+
    | - "Fix grammar"           |
    | - "Shorten section 2"     |
    +---------------------------+
              |
              v
    +---------------------------+
    | EDITOR AGENT              |
    | - Has all information     |
    | - Knows what to fix      |
    +---------------------------+
              |
              v
    +---------------------------+
    | REVISED OUTPUT            |
    +---------------------------+
    """
    print(f"   [EDITOR] Starting with complete context + draft...")

    revision_section = ""
    if revision_notes:
        revision_section = "\nREVISION NOTES TO ADDRESS:\n"
        for note in revision_notes:
            revision_section += f"- {note}\n"

    prompt = f"""You are an editor specialist. Use the complete context and draft below.

{context}

{revision_section}

DRAFT CONTENT TO REVISE:
{draft_content}

TASK:
Revise the draft based on:
1. The original request (don't change the meaning)
2. The style requirements (ensure compliance)
3. The revision notes (address each point)

Produce a polished, final version.
"""

    response = client.messages.create(
        model="claude-haiku-4-5-20250601",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
        tools=[]
    )

    result = response.content[0].text
    print(f"   [EDITOR] Complete! ({len(result)} chars)")
    return result


# ============================================================================
# DEMONSTRATION
# ============================================================================

def demonstrate_context_passing():
    """
    Shows how to properly pass complete context to subagents!
    """
    print(f"\n{'='*60}")
    print("DEMONSTRATION: Proper Context Passing")
    print('='*60)

    # The original user request
    user_request = "Write a report on how solar energy works for a science magazine aimed at high school students."

    # Style requirements
    style_requirements = {
        "Format": "Scientific article",
        "Audience": "High school students (14-18 years old)",
        "Length": "800-1000 words",
        "Tone": "Engaging but informative",
        "Include": "Visual descriptions for concepts that could be illustrated"
    }

    # Constraints (special rules)
    constraints = {
        "Avoid": "Jargon without explanation",
        "Include": "At least one real-world example",
        "Structure": "Has clear headings for each major concept"
    }

    print("\nORIGINAL REQUEST:")
    print(f"   {user_request}")

    print("\nSTYLE REQUIREMENTS:")
    for k, v in style_requirements.items():
        print(f"   - {k}: {v}")

    print("\nCONSTRAINTS:")
    for k, v in constraints.items():
        print(f"   - {k}: {v}")

    # Build the context
    print("\n" + "-"*60)
    print("BUILDING COMPLETE CONTEXT...")
    print("-"*60)

    context = build_complete_context(
        user_request=user_request,
        style_requirements=style_requirements,
        constraints=constraints
    )

    print("\nCONTEXT THAT WILL BE PASSED TO SUBAGENTS:")
    print("="*60)
    print(context)
    print("="*60)

    # Call researcher with complete context
    print("\n" + "-"*60)
    print("Calling RESEARCHER with complete context...")
    print("-"*60)

    research_data = call_researcher_with_context(context)

    print("\nRESEARCH RESULTS (first 300 chars):")
    print(f"   {research_data[:300]}...")

    # Build updated context for writer (with research)
    print("\n" + "-"*60)
    print("BUILDING WRITER CONTEXT (with research)...")
    print("-"*60)

    writer_context = build_complete_context(
        user_request=user_request,
        style_requirements=style_requirements,
        previous_results={"research": research_data},
        constraints=constraints
    )

    # Call writer with complete context + research
    print("\n" + "-"*60)
    print("Calling WRITER with complete context + research...")
    print("-"*60)

    final_output = call_writer_with_context(writer_context, research_data)

    print("\n" + "-"*60)
    print("CONTEXT PASSING DEMONSTRATION COMPLETE!")
    print("-"*60)
    print(f"   Final output: {len(final_output)} characters")

    return final_output


def demonstrate_multi_agent_context_chain():
    """
    Shows context passing in a multi-agent chain.
    """
    print("\n" + "="*60)
    print("MULTI-AGENT CONTEXT CHAIN EXAMPLE")
    print("="*60)
    print("""
    Chain: Researcher -> Analyst -> Writer -> Editor

    Step 1: RESEARCHER
    Context: [Original Request]

    Step 2: ANALYST
    Context: [Original Request + Researcher Output]

    Step 3: WRITER
    Context: [Original Request + Researcher Output + Analyst Output]

    Step 4: EDITOR
    Context: [Original Request + Researcher Output + Analyst Output + Writer Draft]

    Each agent sees EVERYTHING prior agents produced,
    plus the original request and any constraints.
    """)


# ============================================================================
# WHAT WE HAVE LEARNT
# ============================================================================
"""
=============================================================================
WHAT WE HAVE LEARNT: Explicit Context Passing
=============================================================================

1. CORE CONCEPT
   ------------
   - LLM API calls are STATELESS (no memory between calls)
   - Each agent call must include EVERYTHING it needs
   - No inheritance, no shared state, no "just figure it out"
   - Coordinator is responsible for passing context forward

2. WHAT TO INCLUDE IN CONTEXT
   ---------------------------

   ALWAYS:
   +---------------------------+
   | ORIGINAL REQUEST          |  <-- The core task
   +---------------------------+

   USUALLY:
   +---------------------------+
   | PREVIOUS AGENTS' OUTPUTS  |  <-- Build upon prior work
   +---------------------------+
   | STYLE REQUIREMENTS        |  <-- Format, tone, audience
   +---------------------------+
   | CONSTRAINTS               |  <-- Length, what to avoid
   +---------------------------+

   SOMETIMES:
   +---------------------------+
   | ADDITIONAL INFORMATION    |  <-- Domain knowledge, etc.
   +---------------------------+

3. COMMON MISTAKES TO AVOID
   ------------------------

   MISTAKE 1: Assuming Agents Remember
   - "Agent 1 already knows the request" - WRONG!
   - Each call must include the original request

   MISTAKE 2: Partial Context
   - Passing only some info, missing critical parts
   - Always pass COMPLETE context

   MISTAKE 3: Forgetting to Pass Research
   - Researcher produces output, Writer never gets it
   - Always pass previous outputs to next agent

   MISTAKE 4: No Original Request in Later Calls
   - Context for Agent 3 only has Agent 1 and 2 output
   - Agent 3 loses sight of what we're trying to do

4. CONTEXT BUILDING STRATEGY
   -------------------------

   +------------------+    +------------------+
   | build_complete_  | -> | Returns complete |
   | context()        |    | context string   |
   +------------------+    +------------------+
              |
              v
   +------------------+    +------------------+
   | Pass context to  | -> | Agent receives   |
   | each agent call  |    | everything       |
   +------------------+    +------------------+

   FUNCTION SIGNATURE:
   def build_complete_context(
       user_request: str,           # ALWAYS required
       style_requirements: Dict,     # Often required
       previous_results: Dict,      # When chaining agents
       constraints: Dict,           # When present
       additional_info: Dict         # When needed
   ) -> str

5. HANDLING LARGE CONTEXT
   -----------------------
   Token limits are real. Strategies:

   TRUNCATION:
   - First 1000 + "..." + Last 500 chars
   - Simple but loses middle content

   SUMMARIZATION:
   - Summarize results before passing
   - "Research found: 3 key points, 2 statistics"
   - Keeps important info, removes noise

   SELECTIVE PASSING:
   - Agent 3 doesn't need ALL of Agent 1's output
   - Pass only what's relevant to Agent 3's task

   STORE AND REFERENCE:
   - Store in database, pass IDs
   - Agent can fetch if needed
   - For very large datasets

6. PRODUCTION CONSIDERATIONS
   -------------------------
   - Log context passed to each agent (debugging)
   - Monitor token usage per agent call
   - Set context length budgets per agent type
   - Track which context fields are actually used
   - Consider caching commonly used context pieces

7. INTERVIEW ANSWER FRAMEWORK
   --------------------------
   "Why is context passing the most critical pattern?"

   Step 1: Explain the stateless nature
   "LLM API calls have no memory. Each call is independent.
    If you don't pass context, information is lost."

   Step 2: Give the concrete problem
   "Imagine: Researcher gathers data, then Writer creates output.
    If you don't pass the research to the writer, the writer
    produces generic content with no data."

   Step 3: Describe the solution
   "We use explicit context passing. Every agent call includes
    the original request, previous outputs, style requirements,
    and constraints. Everything the agent needs."

   Step 4: Explain the coordinator's role
   "The coordinator is responsible for building complete context
    for each agent call. This is the main job of orchestration."

8. VISUAL SUMMARY
   ---------------

   WITHOUT CONTEXT PASSING (BROKEN):

   Request -> Agent1 -> Agent2 -> Agent3
                        |
                        v
                  "What was the
                   original task?"

   WITH CONTEXT PASSING (WORKS):

   Request -> Agent1 -> Agent2 -> Agent3
              |         |         |
              v         v         v
           [all]     [all]     [all]
           data      data      data

   Each agent sees the full picture.

=============================================================================
"""


if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    print("\n" + "="*60)
    print("PRACTICE 5: EXPLICIT CONTEXT PASSING")
    print("="*60)
    print("""
THIS IS THE MOST CRITICAL PATTERN!

The key lesson:
- DON'T assume subagents know anything beyond what you explicitly give them
- DO pass complete context to every subagent

Watch how we build comprehensive context and pass it to agents!
    """)

    result = demonstrate_context_passing()

    print("\n" + "="*60)
    print("FINAL OUTPUT:")
    print("="*60)
    print(result)
    print("\n" + "="*60)

    demonstrate_multi_agent_context_chain()

    print("\n" + "="*60)
    print("PROGRAM COMPLETE!")
    print("="*60)
    print("""
KEY TAKEAWAYS:
==============

    1. SUBAGENTS DON'T INHERIT CONTEXT
       Every piece of information must be EXPLICITLY passed!

    2. BUILD COMPLETE CONTEXT
       Include: original request, style, previous results, constraints

    3. EACH AGENT GETS EVERYTHING IT NEEDS
       No guessing, no assumptions, no "figure it out"

    4. ISOLATION IS GOOD
       Each agent call is independent and complete

This is what separates WORKING multi-agent systems from broken ones!

See WHAT WE HAVE LEARNT section for comprehensive summary.
""")