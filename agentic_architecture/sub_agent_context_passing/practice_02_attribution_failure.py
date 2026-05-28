"""
+===========================================================================+
|                                                                           |
|  PRACTICE 2: ATTRIBUTION FAILURE - THE CITATION PROBLEM                  |
|                                                                           |
|  Real case study: Synthesis agent produces great reports with NO sources |
|  + REAL-TIME SCENARIOS + MISTAKES + INTERVIEW GUIDE                      |
|                                                                           |
+===========================================================================+

INTERVIEW PREP: "Why do multi-agent reports sometimes lack citations?"
This question tests your understanding of metadata stripping during context passing.

REAL-TIME SCENARIO: Your company's research team ships a 50-page market
analysis. Everything looks professional. Then a journalist asks: "Where did
you get that statistic about 40% market growth?" The synthesis agent can't
answer - it was never told where the data came from!

===========================================================================
 THE ATTRIBUTION PROBLEM: METADATA STRIPPING
===========================================================================

    +-----------------------------------------------------------------------+
    |  WHAT HAPPENS:                                                        |
    |                                                                       |
    |  Research Agent 1 --> Finds data --> Has source info                  |
    |                                    |                                  |
    |                                    v                                  |
    |  Coordinator passes to Synthesis --> STRIPS SOURCE INFO               |
    |                                    |                                  |
    |                                    v                                  |
    |  Synthesis Agent --> Writes report --> NO CITATIONS POSSIBLE          |
    |                                                                       |
    |  ROOT CAUSE: Coordinator only passes CONTENT, not METADATA!            |
    +-----------------------------------------------------------------------+

    +=======================================================================+
    ||  VISUAL: THE ATTRIBUTION FAILURE FLOW                                ||
    ||                                                                      ||
    ||  RESEARCHER SUBAGENT                                                ||
    ||  +---------------------------+                                       ||
    ||  | Content: "AAPL grew 8%"   |                                       ||
    ||  | Source: TechNews.com     | <-- Has metadata!                     ||
    ||  | Confidence: high         |                                       ||
    ||  +---------------------------+                                       ||
    ||                |                                                    ||
    │                v                                                    ||
    ||  +---------------------------+                                       ||
    ||  | Coordinator: Pass to     |                                       ||
    ||  | Synthesis Agent          |                                       ||
    ||  |                          |                                       ||
    ||  | [Strips metadata!]       | <-- THE BUG!                         ||
    ||  | "AAPL grew 8%"           |                                       ||
    ||  +---------------------------+                                       ||
    ||                |                                                    ||
    │                v                                                    ||
    ||  +---------------------------+                                       │
    ||  | SYNTHESIS AGENT          |                                       ||
    ||  |                          |                                       ||
    ||  | Receives: "AAPL grew 8%" |                                       ||
    ||  | NO SOURCE, NO CITATION!  |                                       ||
    ||  +---------------------------+                                       │
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
# REAL-TIME SCENARIOS: When Attribution Failure Causes Problems
# ============================================================================

def show_real_time_scenarios():
    """
    Production scenarios where attribution failure causes issues.
    """

    print("\n" + "=" * 70)
    print("REAL-TIME SCENARIOS: When Attribution Fails")
    print("=" * 70)

    print("""
    +======================================================================+
    ||  SCENARIO #1: The Market Report Disaster                           ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  CONTEXT: Investment bank's AI research team                       ||
    ||                                                                      ||
    ||  WHAT HAPPENED:                                                      ||
    ||  1. Research agents found 15 statistics from various sources      ||
    ||  2. Synthesis agent wrote comprehensive market report              ||
    ||  3. Report published, shared with clients                           ||
    ||  4. Journalist asks for sources on key claims                       ||
    ||  5. Synthesis agent: "I don't know where that came from"          ||
    ||  6. PR disaster, loss of credibility                                 ||
    ||                                                                      ||
    ||  ROOT CAUSE:                                                        ||
    ||  - Research agents produced structured data with sources            ||
    ||  - Coordinator passed ONLY content to synthesis agent               ||
    ||  - Metadata (URLs, confidence, timestamps) was stripped             ||
    ||                                                                      ||
    ||  REAL CONSEQUENCE:                                                   ||
    ||  - Bank had to issue correction and public apology                 ||
    ||  - 3 senior analysts spent 2 weeks re-attributing all claims        ||
    ||  - Lost 2 major client accounts                                     ||
    ||                                                                      ||
    ||  LESSON: Metadata is not optional - it's essential for credibility!||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  SCENARIO #2: The Medical Research Fiasco                          ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  CONTEXT: AI-assisted medical literature review                     ||
    ||                                                                      ||
    ||  WHAT HAPPENED:                                                      ||
    ||  1. Three research agents analyzed different paper sets             ||
    ||  2. Synthesis agent wrote: "Studies show 40% efficacy"             ||
    ||  3. Doctor asks: "Which studies? What journals? What methodology?"  ||
    ||  4. Synthesis agent had no citation information                     ||
    ||  5. Report rejected by medical board                                ||
    ||                                                                      ||
    ||  ROOT CAUSE:                                                        ||
    ||  - Each research agent knew its sources (papers, journals)          ||
    ||  - Coordinator passed content but NOT the source references        ||
    ||  - Synthesis agent couldn't cite because it was never told sources  ||
    ||                                                                      ||
    ||  REAL CONSEQUENCE:                                                   │
    ||  - Project delayed 6 months                                        ||
    ||  - Team had to manually re-review all sources                       ||
    ||  - AI system blamed (wrongly) for hallucinations                     ||
    ||                                                                      ||
    ||  LESSON: In regulated domains, attribution is NOT optional!        ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  SCENARIO #3: The Compliance Violation                              ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  CONTEXT: Financial compliance reporting system                      ||
    ||                                                                      ||
    ||  WHAT HAPPENED:                                                      ||
    ||  1. Audit agent found 3 potential violations                        ||
    ||  2. Report agent wrote summary without source tracking              ||
    ||  3. Regulators asked for evidence trail                             ||
    ||  4. Company couldn't prove findings came from actual documents      ||
    ||  5. Fined for "inability to substantiate audit conclusions"        ||
    ||                                                                      ||
    ||  ROOT CAUSE:                                                        ||
    ||  - Audit agent documented document names, page numbers, timestamps ||
    ||  - Coordinator stripped this metadata when passing to report agent  ||
    ||  - Final report had conclusions but no evidence trail               ||
    ||                                                                      ||
    ||  REAL CONSEQUENCE:                                                   ||
    ||  - $500K regulatory fine                                            ||
    ||  - Mandatory 3rd party audit of entire system                       ||
    ||  - CTO resignation                                                  │
    ||                                                                      ||
    ||  LESSON: Compliance requires FULL AUDIT TRAIL, not just conclusions||
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
    ||  MISTAKE #1: "The source is obvious from the content"              ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WHY IT'S WRONG:                                                     ||
    ||  If source info isn't passed, synthesis agent CANNOT cite it.       ||
    ||  The content "AAPL grew 8%" doesn't tell you WHERE that came from.  ||
    ||                                                                      ||
    ||  BAD CODE:                                                          ||
    ||  findings = []                                                      ||
    ||  for result in research_results:                                     ||
    ||      findings.append(result["content"])  // Stripped metadata!      ||
    ||                                                                      ||
    ||  pass_to_synthesis(findings)  // No sources!                        ||
    ||                                                                      ||
    ||  CORRECT CODE:                                                      ||
    ||  findings = []                                                       ||
    ||  for result in research_results:                                     ||
    ||      findings.append({                                              ||
    ||          "content": result["content"],                              ||
    ||          "source": result["source"],  // INCLUDE THIS!              ||
    ||          "confidence": result["confidence"],                        ||
    ||          "agent": result["agent"]                                    ||
    ||      })                                                              ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  MISTAKE #2: "I'll add sources in the final output only"           ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WHY IT'S WRONG:                                                     ||
    ||  If synthesis agent doesn't have source info, it CAN'T add it!     ||
    ||  You can't cite what you don't know about.                          ||
    ||                                                                      ||
    ||  BAD FLOW:                                                          ||
    ||  Research --> Strips metadata --> Synthesis --> Tries to cite       ||
    ||                              ^                                        ||
    ||                              |                                        ||
    ||                    Can't cite what isn't there!                     ||
    ||                                                                      ||
    ||  CORRECT FLOW:                                                       ||
    ||  Research --> Keeps metadata --> Synthesis --> Has sources!        ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  MISTAKE #3: "Metadata makes context too big"                       ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WHY IT'S WRONG:                                                     ||
    ||  - Metadata is SMALL compared to content (just a few fields)        ||
    ||  - The cost of NO attribution (legal, credibility) is HUGE          ||
    ||  - You can summarize/compress metadata, not drop it entirely        ||
    ||                                                                      ||
    ||  BAD DECISION:                                                      ||
    ||  // "Skip metadata to save tokens"                                 ||
    ||  // Results in: unverified claims, legal risk, reputation damage   ||
    ||                                                                      ||
    ||  GOOD DECISION:                                                      ||
    ||  // Include essential metadata: source URL, confidence, timestamp   ||
    ||  // Compress if needed: "source": "TechNews Q3 2024" instead of URL  ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  MISTAKE #4: Blaming the synthesis agent for missing citations     ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WHY IT'S WRONG:                                                     ||
    ||  Synthesis agent can only cite what it receives. If sources weren't  ||
    ||  passed, synthesis agent did nothing wrong. The bug is upstream.    ||
    ||                                                                      ||
    ||  INVESTIGATION FLOW:                                                ||
    ||                                                                      ||
    ||  Synthesis gives no citations?                                      ||
    ||           |                                                          ||
    ||           v                                                          │
    ||  Check: Did coordinator pass source info?                           ||
    ||           |                                                          |
    ||           v                                                          ||
    ||  If NO --> Coordinator is the bug (not synthesis!)                  ||
    ||  If YES --> Check: Did synthesis prompt instruct to cite?           ||
    ||                                                                      ||
    ||  KEY INSIGHT: Most attribution failures are COORDINATOR bugs!       ||
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
    INTERVIEW Q1: "Why do multi-agent reports sometimes lack citations?"
    ========================================================================

    EXPECTED ANSWER:
    Citations are missing when the coordinator strips metadata during context
    passing. Research agents typically produce structured data with source
    information, but if the coordinator only passes content to synthesis
    agents (dropping the metadata), there's no way to cite. The synthesis
    agent is not at fault - it can only cite what it receives.

    RED FLAGS IN ANSWERS:
    - "The synthesis agent is lazy" -> Wrong! Can't cite what you don't have
    - "AI doesn't do citations" -> With proper context, it can and does
    - "We should add citations at the end" -> Too late if source info gone

    +-----------------------------------------------------------------------+
    | EXPERT TIP: Say "metadata stripping during context passing"            |
    | This is the specific technical term interviewers expect!             |
    +-----------------------------------------------------------------------+
    """)

    # Demo with actual API call
    message = client.messages.create(
        model="claude-haiku-4-5-20250601",
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": "As an expert in multi-agent systems, explain in 2 sentences "
                      "why AI research reports might lack proper citations even when "
                      "the research was done correctly. Mention context passing."
        }]
    )

    print("\nExample Expert Answer:")
    print(f"    {message.content[0].text[:400]}...")

    print("""
    ========================================================================
    INTERVIEW Q2: "How do you ensure proper attribution in multi-agent pipelines?"
    ========================================================================

    EXPECTED ANSWER:
    1. Define structured output schema for all subagents (include metadata fields)
    2. Coordinator passes FULL structured data (not just content)
    3. Synthesis prompts explicitly instruct to cite using provided sources
    4. Validate that metadata survives the pass-through

    STRUCTURED METADATA SCHEMA:
    {
        "content": "...",           // The actual finding
        "source": "URL or name",    // Required!
        "confidence": "high/med/low",  // Required!
        "agent": "researcher",      // Who produced this
        "timestamp": "...",         // When retrieved
        "page_number": "..."        // For document citations
    }

    +-----------------------------------------------------------------------+
    | EXPERT TIP: Mention schema validation - don't let metadata be dropped |
    +-----------------------------------------------------------------------+
    """)

    print("""
    ========================================================================
    INTERVIEW Q3: "What's the difference between content and metadata?"
    ========================================================================

    EXPECTED ANSWER:
    Content is the actual information: "AAPL grew 8% revenue." Metadata is
    information ABOUT the information: "Source: TechNews.com, Confidence: high,
    Retrieved: 2024-01-15." Content tells you WHAT. Metadata tells you
    WHERE IT CAME FROM and HOW TRUSTWORTHY IT IS.

    EXAMPLE:
    - Content: "Study shows drug efficacy of 85%"
    - Metadata: "Source: NEJM vol. 390, p. 234, Double-blind RCT, n=2000"

    Without metadata, you can't:
    - Verify the claim
    - Assess reliability
    - Properly cite in your work

    +-----------------------------------------------------------------------+
    | EXPERT TIP: Use the "information about information" framework          |
    +-----------------------------------------------------------------------+
    """)

    print("""
    ========================================================================
    INTERVIEW Q4: "A synthesis agent keeps giving wrong citations. Who's at fault?"
    ========================================================================

    EXPECTED ANSWER:
    Check upstream before blaming synthesis:
    1. Did coordinator pass source metadata to synthesis? If no -> coordinator bug
    2. Did synthesis prompt explicitly instruct to cite? If no -> prompt bug
    3. If both yes, then check synthesis agent's logic

    MOST COMMON: Coordinator stripped metadata, not synthesis agent's fault!

    DEBUGGING FRAMEWORK:
    """
    +-------------+     +-------------+     +-------------+
    | Researcher  | --> | Coordinator | --> | Synthesis   |
    |             |     |             |     |             |
    | Has sources |     | Passes info  |     | Should cite |
    | [YES]       |     | [metadata?]  |     | [sources?]  |
    +-------------+     +-------------+     +-------------+
                            |
                            v
                    If metadata stripped here,
                    synthesis cannot cite!
                    THE BUG IS HERE!

    +-----------------------------------------------------------------------+
    | EXPERT TIP: "Check the coordinator first" - show systematic debugging |
    +-----------------------------------------------------------------------+
    """)


# ============================================================================
# DEMONSTRATION FUNCTIONS
# ============================================================================

def simulate_research_agent(source_name: str, query: str) -> dict:
    """
    Simulate a research agent that finds information from a specific source.
    Returns structured data with METADATA (this is the fix!).
    """
    print(f"\n   [SUBAGENT] Researching: '{query}'")
    print(f"   [SUBAGENT] Source: {source_name}")

    messages = [
        {
            "role": "user",
            "content": f"Find information about: {query}. Be specific and include source details."
        }
    ]

    response = client.messages.create(
        model="claude-haiku-4-5-20250601",
        max_tokens=1024,
        messages=messages,
    )

    result = ""
    for block in response.content:
        if block.type == "text" and block.text:
            result = block.text
            break

    # THE FIX: Return structured data with metadata!
    return {
        "content": result,
        "source": source_name,
        "query": query,
        "confidence": "high",
        "agent": "researcher"
    }


def coordinator_bad_passes_context(research_results: list) -> str:
    """
    BAD COORDINATOR: Strips metadata, only passes content.

    This causes ATTRIBUTION FAILURE - the synthesis agent
    cannot cite sources it was never given!
    """
    print("\n" + "=" * 60)
    print("[BAD COORDINATOR] Passing content WITHOUT metadata...")
    print("=" * 60)

    # BAD: Only passing the text content, losing all metadata
    bad_context = "Research findings:\n\n"
    for i, result in enumerate(research_results, 1):
        bad_context += f"Finding {i}: {result['content']}\n\n"

    print("   What the synthesis agent receives:")
    print(f"   '{bad_context[:150]}...'")
    print("\n   Problem: No source information! No citations possible!")

    messages = [
        {
            "role": "user",
            "content": f"""You are a synthesis agent. Write a report based on these findings.
Include proper citations for each claim.

FINDINGS:
{bad_context}

Write a well-structured report with citations."""
        }
    ]

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

    print(f"\n   [RESULT] Synthesis without metadata:")
    print(f"   '{result[:200]}...'")

    return result


def coordinator_good_passes_context(research_results: list) -> str:
    """
    GOOD COORDINATOR: Passes structured metadata alongside content.

    This enables ATTRIBUTION - the synthesis agent knows exactly
    where each piece of information came from!
    """
    print("\n" + "=" * 60)
    print("[GOOD COORDINATOR] Passing content WITH metadata...")
    print("=" * 60)

    # GOOD: Structured data with metadata
    good_context = "Research findings with sources:\n\n"
    for i, result in enumerate(research_results, 1):
        good_context += f"""---
Finding {i}:
  Content: {result['content']}
  Source: {result['source']}
  Query: {result['query']}
  Confidence: {result['confidence']}
  Retrieved by: {result['agent']}
---

"""

    print("   What the synthesis agent receives:")
    print(f"   '{good_context[:200]}...'")
    print("\n   Perfect: Source, confidence, and agent all included!")

    messages = [
        {
            "role": "user",
            "content": f"""You are a synthesis agent. Write a report based on these findings.
Include proper citations for each claim using the source information provided.

FINDINGS WITH METADATA:
{good_context}

Write a well-structured report with citations like [Source: name]."""
        }
    ]

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

    print(f"\n   [RESULT] Synthesis with metadata:")
    print(f"   '{result[:200]}...'")

    return result


def demonstrate_attribution_failure():
    """
    Demonstrate the attribution failure problem and solution.
    """
    print("\n" + "=" * 70)
    print("DEMONSTRATION: Research team produces report - with/without citations")
    print("=" * 70)

    print("""
    THE PROBLEM:
    1. Researcher A finds: "AAPL revenue grew 8% in Q3"
    2. Researcher B finds: "iPhone sales drove the growth"
    3. Coordinator passes only the CONTENT to Synthesis Agent
    4. Synthesis Agent writes: "AAPL had strong revenue growth..."
    5. NO CITATIONS! User has no idea where the info came from!

    ROOT CAUSE:
    The coordinator stripped the metadata (source, confidence, agent)
    before passing content to the synthesis agent.
    """)

    # Run research agents (simulated)
    print("\n" + "-" * 50)
    print("STEP 1: Running Research Subagents")
    print("-" * 50)

    research_results = []

    result1 = simulate_research_agent("TechNews.com", "AI chip market trends")
    research_results.append(result1)

    result2 = simulate_research_agent("MarketWatch", "semiconductor industry outlook")
    research_results.append(result2)

    print("\n" + "-" * 50)
    print("STEP 2: Compare Bad vs Good Context Passing")
    print("-" * 50)

    # Bad coordinator
    bad_report = coordinator_bad_passes_context(research_results)

    # Good coordinator
    good_report = coordinator_good_passes_context(research_results)

    print("\n" + "=" * 70)
    print("COMPARISON: Reports")
    print("=" * 70)

    print("\n[BAD REPORT] - No citations possible:")
    print(f"   {bad_report[:200]}...")

    print("\n[GOOD REPORT] - Citations included:")
    print(f"   {good_report[:200]}...")


def show_metadata_structure():
    """
    Show the recommended structure for passing context with metadata.
    """
    print("\n" + "=" * 70)
    print("RECOMMENDED METADATA STRUCTURE")
    print("=" * 70)

    print("""
    +=======================================================================+
    ||  Always pass structured data with these fields:                     ||
    ||                                                                      ||
    ||  {                                                                   ||
    ||      "content": "...",           // The actual finding/information  ||
    ||      "source": "URL or name",    // Where did this come from?        ||
    ||      "confidence": "high/med/low", // How certain is the agent?     ||
    ||      "agent": "researcher",      // Which subagent produced this?   ||
    ||      "timestamp": "...",         // When was this retrieved?        ||
    ||      "page_number": "1-3",       // For document citations           ||
    ||      "raw_data": {...}           // Optional: structured data       ||
    ||  }                                                                   ||
    ||                                                                      ||
    ||  This way, downstream agents can:                                   ||
    ||  - Cite sources properly                                             ||
    ||  - Assess confidence levels                                          ||
    ||  - Know which agent to ask follow-up questions                       ||
    ||                                                                      ||
    +=======================================================================+
    """)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    print("\n" + "=" * 70)
    print("PRACTICE 2: ATTRIBUTION FAILURE - THE CITATION PROBLEM")
    print("=" * 70)
    print("""
This program teaches a critical lesson in multi-agent systems:
    Losing metadata = Losing citations!

Real case: A synthesis agent produces great reports with NO sources.
Both research agents worked perfectly. The coordinator was the problem!
    """)

    # Show all enhanced sections
    show_real_time_scenarios()
    show_mistakes_developers_make()
    show_interview_qa()
    demonstrate_attribution_failure()
    show_metadata_structure()

    print("\n" + "=" * 70)
    print("WHAT WE HAVE LEARNT")
    print("=" * 70)
    print("""
    +======================================================================+
    ||  1. THE ATTRIBUTION PROBLEM:                                        ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  Research agents produce findings WITH source information.           ||
    ||  Coordinator passes content BUT strips metadata.                    ||
    ||  Synthesis agent CANNOT cite what it never received!                ||
    ||                                                                      ||
    ||  This is called "metadata stripping" - a common coordinator bug.     ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  2. REAL-TIME SCENARIOS WHERE THIS BREAKS:                           ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  - Market report disaster (journalist can't verify sources)         ||
    ||  - Medical research fiasco (can't cite specific studies)            ||
    ||  - Compliance violation (no audit trail for regulators)              ||
    ||                                                                      ||
    ||  KEY INSIGHT: Attribution failure causes CREDIBILITY DAMAGE         ||
    ||               and potentially LEGAL LIABILITY                        ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  3. COMMON MISTAKES:                                                 ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  MISTAKE #1: "The source is obvious from the content"                ||
    ||              -> It's NOT! You can't cite what you don't receive     ||
    ||                                                                      ||
    ||  MISTAKE #2: "I'll add citations at the end"                         ||
    ||              -> Too late if source info already stripped!           ||
    ||                                                                      ||
    ||  MISTAKE #3: "Metadata makes context too big"                       ||
    ||              -> Metadata is TINY vs legal/reputation cost of NO cites ||
    ||                                                                      ||
    ||  MISTAKE #4: Blaming synthesis agent for missing citations           ||
    ||              -> Synthesis can only cite what it receives!          ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  4. INTERVIEW TIPS:                                                  ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  - Say "metadata stripping during context passing"                   ||
    ||  - Explain: content vs metadata difference                          ||
    ||  - Debug by checking coordinator FIRST, not synthesis agent       ||
    ||  - Mention structured schema with required metadata fields          ||
    ||                                                                      ||
    ||  EXPECTED ANSWER STRUCTURE:                                          ||
    ||  1. Identify the problem: coordinator strips metadata               ||
    ||  2. Explain the consequence: synthesis can't cite                   ||
    ||  3. Give the solution: pass structured data with metadata           ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  5. KEY RULES TO MEMORIZE:                                           ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  RULE #1: ALWAYS include metadata when passing subagent outputs      ||
    ||  RULE #2: Metadata includes: source, confidence, agent, timestamp   ||
    ||  RULE #3: Synthesis agent can only cite what it receives            ||
    ||  RULE #4: Most attribution failures are COORDINATOR bugs!           ||
    ||  RULE #5: In regulated domains, attribution is NOT optional        ||
    ||                                                                      ||
    +======================================================================+

    Next: practice_03_agent_tool_gate.py shows the critical requirement
    for the Agent tool in coordinator's allowedTools!
    """)

    print("\n" + "=" * 70)
    print("PROGRAM COMPLETE!")
    print("=" * 70)


"""
+===========================================================================+
|                                                                           |
|  KEY CONCEPTS FROM THIS FILE:                                             |
|                                                                           |
|  THE PROBLEM: Metadata stripped during context passing = no citations     |
|                                                                           |
|  REAL-TIME SCENARIOS:                                                     |
|  - Market report: journalist can't verify sources                        |
|  - Medical research: can't cite specific studies                         |
|  - Compliance: no audit trail for regulators                             |
|                                                                           |
|  MISTAKES TO AVOID:                                                       |
|  - "Source is obvious" -> It's NOT!                                       |
|  - "Add citations at end" -> Too late if info already gone!                |
|  - Blaming synthesis agent -> Check coordinator first!                   |
|                                                                           |
|  INTERVIEW PREP:                                                          |
|  - "Why no citations?" -> Metadata stripping during context passing       |
|  - "Content vs metadata" -> Information vs info about info               |
|  - Debug approach -> Check coordinator before synthesis agent            |
|                                                                           |
+===========================================================================+
"""