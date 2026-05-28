"""
PRACTICE 3: SCOPE PARTITIONING
=============================
Divide work so agents DON'T overlap - each agent owns a distinct area!

+------------------------------------------------------------------+
|                   SCOPE PARTITIONING CONCEPT                      |
+------------------------------------------------------------------+
|                                                                    |
|   +------------------------------------------------------------+   |
|   |                      FULL TOPIC                              |   |
|   |                "Renewable Energy Sources"                    |   |
|   +------------------------------------------------------------+   |
|                              |                                    |
|            +-----------------+-----------------+                  |
|            |                   |                   |              |
|            v                   v                   v              |
|   +-------------+      +-------------+      +-------------+        |
|   |   SOLAR     |      |    WIND     |      |   HYDRO     |        |
|   |   AGENT     |      |    AGENT    |      |    AGENT    |        |
|   | (Scope: PV)|      |(Scope: Wind)|      |(Scope: H2O) |        |
|   +-------------+      +-------------+      +-------------+        |
|            |                   |                   |              |
|            +-----------------+-----------------+                  |
|                              |                                    |
|                              v                                    |
|   +------------------------------------------------------------+   |
|   |                    AGGREGATOR                               |   |
|   |           (Combines non-overlapping scopes)                 |   |
|   +------------------------------------------------------------+   |
|                                                                    |
+------------------------------------------------------------------+

KEY CONCEPT: Each agent has a TIGHT, NON-OVERLAPPING scope.
Scopes are defined upfront. Agents stay within their boundaries.
Aggregator combines results without duplicating or contradicting.
"""

import os
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY", "")
api_base = os.getenv("ANTHROPIC_API_BASE", "")

from anthropic import Anthropic
client_kwargs = {"api_key": api_key} if api_key else {}
if api_base:
    client_kwargs["base_url"] = api_base
client = Anthropic(**client_kwargs)


# ============================================================================
# SCOPE DEFINITIONS (Non-Overlapping Domains)
# ============================================================================

RENEWABLE_ENERGY_SCOPES = {
    "solar": {
        "name": "Solar Energy",
        "description": "Photovoltaic solar panels, solar thermal systems, concentrated solar power",
        "focus": "Technologies that capture sunlight to generate electricity or heat",
        "keywords": ["photovoltaic", "solar panel", "sunlight", "solar thermal",
                     "CSP", "concentrated", "solar farm", "rooftop"],
        "excludes": ["wind", "hydro", "geothermal", "biomass", "tidal"]
    },
    "wind": {
        "name": "Wind Energy",
        "description": "Onshore and offshore wind turbines, wind farm operations",
        "focus": "Technologies that convert wind motion into electrical power",
        "keywords": ["wind turbine", "onshore", "offshore", "wind farm",
                     "aerodynamic", "rotor", "wind power"],
        "excludes": ["solar", "hydro", "geothermal", "biomass", "tidal"]
    },
    "hydro": {
        "name": "Hydroelectric",
        "description": "Run-of-river, reservoir dams, pumped storage, micro-hydro",
        "focus": "Technologies that use flowing or falling water to generate power",
        "keywords": ["hydroelectric", "dam", "water flow", "turbine", "reservoir",
                     "pumped storage", "run-of-river"],
        "excludes": ["solar", "wind", "geothermal", "biomass", "tidal"]
    },
    "geothermal": {
        "name": "Geothermal Energy",
        "description": "Geothermal power plants, ground source heat pumps, enhanced geothermal",
        "focus": "Technologies that harness heat from beneath the Earth's surface",
        "keywords": ["geothermal", "heat pump", "earth heat", "thermal gradient",
                     "hot springs", "Enhanced Geothermal System"],
        "excludes": ["solar", "wind", "hydro", "biomass", "tidal"]
    },
    "biomass": {
        "name": "Biomass Energy",
        "description": "Biofuels, biogas, biomass combustion, anaerobic digestion",
        "focus": "Technologies that convert organic materials into energy",
        "keywords": ["biomass", "biofuel", "biogas", "anaerobic", "organic",
                     "combustion", "feedstock", "ethanol"],
        "excludes": ["solar", "wind", "hydro", "geothermal", "tidal"]
    },
    "tidal": {
        "name": "Tidal and Wave Energy",
        "description": "Tidal turbines, wave energy converters, ocean thermal",
        "focus": "Technologies that harness energy from ocean tides and waves",
        "keywords": ["tidal", "wave energy", "ocean", "current", "turbine",
                     "ocean thermal", "marine"],
        "excludes": ["solar", "wind", "hydro", "geothermal", "biomass"]
    }
}


# ============================================================================
# REAL-TIME SCENARIO: Legal Document Review
# ============================================================================
"""
PRODUCTION SCENARIO: Contract Analysis with Scope Partitioning

A law firm needs to analyze a 100-page contract. Scopes could be:
- SCOPE A: Payment terms, schedules, penalties
- SCOPE B: Termination clauses, exit conditions
- SCOPE C: Liability limitations, indemnification
- SCOPE D: IP ownership, confidentiality

Each scope agent reviews ONLY their section. No overlap.
Aggregator combines into final legal opinion.

WHY SCOPE PARTITIONING:
- Two lawyers reviewing the same clause might give conflicting advice
- Partitioning prevents this by assigning exclusive ownership
- Clear accountability: "Who reviewed clause 4.2?" -> Scope A agent
- Parallel execution: all scopes can run simultaneously
"""


# ============================================================================
# MISTAKE #1: Overlapping Scopes (Boundary Ambiguity)
# ============================================================================
"""
COMMON ERROR: Defining scopes that overlap or have ambiguous boundaries

BAD SCOPE DEFINITION:
    Scope A: "Financial information"
    Scope B: "Business information"
    # What's "financial business"? Overlap!

WHY THIS BREAKS:
- Agent A might cover something that Agent B also covers
- Inconsistent or duplicate content
- Conflicting information in final output
- Hard to track who owns what

GOOD SCOPE DEFINITION:
    Scope A: "Revenue, costs, profit margins, financial projections"
    Scope B: "Products, services, market position, competitors"
    # Clear, non-overlapping, unambiguous
"""


# ============================================================================
# MISTAKE #2: Scopes Too Broad (Loss of Specialization)
# ============================================================================
"""
COMMON ERROR: Making scopes too large, defeating the purpose

BAD:
    Scope A: "Everything about topic X"
    Scope B: "Everything else about topic X"
    # No real division, no specialization

WHY THIS BREAKS:
- Agents become generalists again
- Lose benefits of focused expertise
- Might as well not have scopes

GOOD:
    Scope A: "Technical implementation details"
    Scope B: "Business impact and ROI"
    Scope C: "Risk factors and mitigations"
    # Each has clear focus and expertise
"""


# ============================================================================
# MISTAKE #3: Not Defining Scope Boundaries Explicitly
# ============================================================================
"""
COMMON ERROR: Leaving scope definition vague

INCORRECT:
    Scope: "Research solar energy"

CORRECT:
    Scope: "Solar Energy"
    Focus: "Photovoltaic and thermal technologies for electricity generation"
    Excludes: "Wind, hydro, storage (batteries), policy aspects"
    Keywords: "solar panel, photovoltaic, thermal, sunlight"

Without explicit boundaries, agents will venture into other scopes
and create overlap/conflicts in the final output.
"""


# ============================================================================
# INTERVIEW Q&A: Scope Partitioning
# ============================================================================
"""
Q: How do you define appropriate scopes?
A: The key is DISJOINT, EXHAUSTIVE partitioning:

   1. MUTUALLY EXCLUSIVE
   - No overlap between scopes
   - Each data point belongs to exactly one scope
   - Use "excludes" lists to clarify boundaries

   2. COLLECTIVELY EXHAUSTIVE
   - Together, scopes cover the entire topic
   - No gaps between scopes
   - Every aspect of the topic is covered

   3. ACTIONABLE GRANULARITY
   - Scopes should be small enough to be manageable
   - Large enough to be meaningful
   - Rule of thumb: one agent should complete in <10 minutes

Q: What happens if a request doesn't fit neatly into scopes?
A: Options:
   - Refine scope definitions to be more comprehensive
   - Add a "general" scope for cross-cutting concerns
   - Have one scope handle "other" items
   - Split into hierarchical scopes (primary + secondary)

Q: How do you handle dependencies between scopes?
A: Minimize dependencies! Scope partitioning works best when:
   - Each scope is self-contained
   - Dependencies are explicit and documented
   - Aggregator handles the combining logic

   If dependency is unavoidable:
   - Define order: Scope A must complete before Scope B
   - Pass outputs explicitly (context passing pattern)
"""


# ============================================================================
# SCOPE AGENT IMPLEMENTATION
# ============================================================================

def research_scope(scope_key: str, scope_info: Dict) -> str:
    """
    A specialized agent that researches ONLY its assigned scope!

    ASCII ART: Scope Agent Workflow
    ==============================

    +---------------------------+
    | SCOPE DEFINITION          |
    | Name: Solar Energy        |
    | Focus: PV + Thermal       |
    | Excludes: Wind, Hydro...   |
    +---------------------------+
              |
              v
    +---------------------------+
    | SCOPE BOUNDARY CHECK       |
    | Is this about Solar?      |
    | Yes: proceed              |
    | No: skip this content     |
    +---------------------------+
              |
              v
    +---------------------------+
    | RESEARCH WITHIN SCOPE      |
    | Only scope-relevant topics |
    +---------------------------+
              |
              v
    +---------------------------+
    | OUTPUT (scope-marked)      |
    | Clearly labeled as Solar   |
    +---------------------------+
    """
    print(f"\n   [SCOPE: {scope_key.upper()}] Researching...")

    # Build explicit scope instructions
    excludes_str = ", ".join(scope_info.get("excludes", []))

    prompt = f"""You are a specialized research agent with a TIGHT SCOPE.

YOUR SCOPE: {scope_info['name']}
DESCRIPTION: {scope_info['description']}
FOCUS: {scope_info['focus']}

SCOPE BOUNDARIES (MUST RESPECT):
- You MAY cover: {scope_info['focus']}
- You MUST NOT cover: {excludes_str}

KEYWORDS THAT IDENTIFY YOUR SCOPE:
{', '.join(scope_info.get('keywords', []))}

IMPORTANT RULES:
1. Stay strictly within your assigned scope
2. Do NOT venture into excluded topics
3. If something is unclear, default to NOT covering it
4. Mark any borderline content as "scope-adjacent" but don't deeply explore

Research thoroughly within YOUR SCOPE ONLY.
Include:
1. How it works (basic principle)
2. Current state of the technology
3. Key advantages
4. Main challenges
5. Notable projects or installations

Do NOT venture outside your scope. Stick to {scope_info['name']} only."""

    response = client.messages.create(
        model="claude-haiku-4-5-20250601",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
        tools=[]
    )

    result = response.content[0].text
    print(f"   [SCOPE: {scope_key.upper()}] Complete!")

    return f"\n{'='*40}\n{scope_info['name'].upper()}\n{'='*40}\n{result}"


# ============================================================================
# AGGREGATOR IMPLEMENTATION
# ============================================================================

def aggregate_results(results: List[str], original_topic: str) -> str:
    """
    Combine all scope results into a coherent report!

    ASCII ART: Aggregator Workflow
    ============================

    Results from Scopes:
    +-------------+ +-------------+ +-------------+
    | SOLAR       | | WIND        | | HYDRO       |
    | (non-overlap)| | (non-overlap)| | (non-overlap)|
    +-------------+ +-------------+ +-------------+

              |           |           |
              +-----+-----+           |
                    |                 |
                    v                 |
            +-----------------+      |
            |  AGGREGATOR      |      |
            |  (Combine, don't |      |
            |   duplicate)     |      |
            +-----------------+      |
                    |                 |
                    v                 v
            +--------------------------------+
            |     COHERENT FINAL REPORT      |
            |   Each section from one scope  |
            |   No duplication, no conflict  |
            +--------------------------------+
    """
    print(f"\n[COORDINATOR] Aggregating {len(results)} scope results...")

    aggregator_prompt = f"""You are an aggregation agent. Combine research from multiple scopes into one comprehensive report.

ORIGINAL TOPIC: {original_topic}

SCOPE RESULTS:
{chr(10).join(results)}

IMPORTANT AGGREGATION RULES:
1. MAINTAIN SCOPE BOUNDARIES - don't mix topics between sections
2. NO DUPLICATION - if two scopes cover similar ground, pick one
3. NO CONFLICT - if scopes seem to contradict, flag and resolve
4. CLEAR STRUCTURE - one section per scope, well-organized
5. COHERENT INTRO/SUMMARY - tie everything together

Create a well-organized report that:
1. Has a clear structure (one section per scope)
2. Maintains the scope boundaries - don't mix topics
3. Provides a brief introduction
4. Ends with a summary or conclusion

Keep each scope's findings clearly separated."""

    response = client.messages.create(
        model="claude-haiku-4-5-20250601",
        max_tokens=2048,
        messages=[{"role": "user", "content": aggregator_prompt}],
        tools=[]
    )

    result = response.content[0].text
    print("[COORDINATOR] Aggregation complete!")

    return result


# ============================================================================
# COORDINATOR ORCHESTRATION
# ============================================================================

def partition_and_research(topic: str, scopes: Dict[str, Dict]) -> str:
    """
    The coordinator orchestrates scope-partitioned research!

    ASCII ART: Full Scope Partitioning Flow
    =======================================

    Topic: "Renewable Energy Sources"
              |
              v
    +-------------------+
    | DECOMPOSE          |  Split into 6 scopes
    | (define boundaries)|
    +-------------------+
              |
    +---------+---------+---------+
    |         |         |         |
    v         v         v         v
    [SOLAR] [WIND] [HYDRO] [GEO] [BIOMASS] [TIDAL]
    (each agent works within its scope)
    |         |         |         |         |         |
    +---------+---------+---------+---------+
              |
              v
    +-------------------+
    | AGGREGATE          |  Combine into final report
    | (maintain borders) |
    +-------------------+
              |
              v
         Final Report
    """
    print(f"\n{'='*60}")
    print(f"[COORDINATOR] Topic: {topic}")
    print(f"Scope count: {len(scopes)}")
    print('='*60)

    print("\n[COORDINATOR] Scope Partitioning:")
    print("="*50)
    for key, info in scopes.items():
        print(f"   [{key.upper()}] {info['name']}")
        print(f"           Focus: {info['focus']}")
        print(f"           Excludes: {', '.join(info.get('excludes', []))}")
        print()

    print("\n" + "-"*60)
    print("[COORDINATOR] Executing scope agents (parallel-ready)...")
    print("-"*60)

    results = []
    for scope_key, scope_info in scopes.items():
        result = research_scope(scope_key, scope_info)
        results.append(result)

    print("\n" + "-"*60)
    print("[COORDINATOR] Aggregating scope results...")
    print("-"*60)

    final_report = aggregate_results(results, topic)

    print("\n[COORDINATOR] Scope partitioning complete!")

    return final_report


# ============================================================================
# DEMONSTRATION: Scope Boundary Enforcement
# ============================================================================

def demonstrate_scope_boundaries():
    """
    Show how scope boundaries are enforced.
    """
    print("\n" + "="*60)
    print("SCOPE BOUNDARY DEMONSTRATION")
    print("="*60)

    # Test with a request that spans multiple scopes
    print("""
    Request: "Compare renewable energy sources"

    Scope Breakdown:
    +----------+----------+----------+
    | SOLAR    | WIND     | HYDRO    |  (3 parallel scopes)
    | Focus:   | Focus:   | Focus:   |
    | Sunlight| Wind     | Water    |
    | to power | to power | to power |
    +----------+----------+----------+

    Each agent works ONLY within its scope.
    Solar agent does NOT discuss wind pros/cons.
    Wind agent does NOT discuss solar efficiency.
    Aggregator combines without duplication.
    """)


# ============================================================================
# WHAT WE HAVE LEARNT
# ============================================================================
"""
=============================================================================
WHAT WE HAVE LEARNT: Scope Partitioning
=============================================================================

1. CORE CONCEPT
   ------------
   - Divide work into non-overlapping, clearly defined scopes
   - Each agent owns ONE scope exclusively
   - Scopes are defined UPFRONT before execution
   - Aggregator combines results without duplication

2. SCOPE DEFINITION PRINCIPLES
   ---------------------------
   MUTUALLY EXCLUSIVE:
   - No two scopes should cover the same content
   - Use "excludes" lists to clarify boundaries
   - If ambiguous, it's a bad scope definition

   COLLECTIVELY EXHAUSTIVE:
   - All scopes together must cover the full topic
   - No gaps between scopes
   - Add a "general/misc" scope if needed

   ACTIONABLE GRANULARITY:
   - Scopes should be completable in <10 minutes
   - One person/agent should be able to own it fully
   - Too small = overhead, too large = no specialization

3. COMMON MISTAKES TO AVOID
   ------------------------
   MISTAKE 1: Overlapping Scopes
   - Bad: "Financial" and "Business" (overlap in "financial business")
   - Good: "Revenue/costs" and "Products/market" (disjoint)

   MISTAKE 2: Scopes Too Broad
   - Bad: "Everything about X" (no real division)
   - Good: "Technical", "Business", "Risk" (clear focus areas)

   MISTAKE 3: No Explicit Boundaries
   - Bad: "Research solar energy"
   - Good: "Solar PV + thermal, excludes storage, policy"

4. SCOPE PARTITIONING VS OTHER PATTERNS
   -------------------------------------
   Scope Partitioning focuses on DATA DIVISION:
   - "Who owns what data?"

   vs Dynamic Selection focuses on AGENT SELECTION:
   - "Which agents are needed?"

   vs Iterative Refinement focuses on QUALITY:
   - "How do we ensure good output?"

   These patterns can COMBINE in production systems!

5. PRODUCTION CONSIDERATIONS
   -------------------------
   - Scope definitions should be versioned and documented
   - Overlap detection should be automated if possible
   - Aggregator needs clear rules for conflict resolution
   - Consider hierarchical scopes for complex topics
   - Track scope ownership for accountability

6. INTERVIEW ANSWER FRAMEWORK
   --------------------------
   "When would you use scope partitioning?"

   Step 1: Define the problem it solves
   "Scope partitioning is used when you need to divide a large topic
    into independent, non-overlapping work units."

   Step 2: Give concrete examples
   "For a legal document, you'd partition by clause type:
    - Payment terms (Scope A)
    - Termination clauses (Scope B)
    - Liability (Scope C)

    Each lawyer owns one scope. No overlap, clear accountability."

   Step 3: Explain benefits
   "Benefits: parallel execution, clear ownership, no duplication,
    easier quality control, scalable to more scopes."

   Step 4: Acknowledge limitations
   "Limitation: scopes must be well-defined upfront. For fuzzy or
    highly interdependent topics, this pattern may not apply."

7. VISUAL SUMMARY
   --------------

   SCOPE PARTITIONING:

   +-----------+ +-----------+ +-----------+ +-----------+
   |   SCOPE A | |   SCOPE B | |   SCOPE C | |   SCOPE D |
   |  (owned)  | |  (owned)  | |  (owned)  | |  (owned)  |
   +-----------+ +-----------+ +-----------+ +-----------+
        |             |             |             |
        +-------------+-------------+-------------+
                          |
                          v
                 +----------------+
                 |   AGGREGATOR   |
                 | (combine only) |
                 +----------------+
                          |
                          v
                    Final Report

   vs NO PARTITIONING:

   +-----------------------------------------------+
   |              SHARED WORKSPACE                  |
   |                                               |
   |   Agent A -------+                             |
   |                  | (might duplicate)           |
   |   Agent B -------+                             |
   |                  | (might conflict)            |
   |   Agent C -------+                             |
   |                                               |
   +-----------------------------------------------+

=============================================================================
"""


if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    print("\n" + "="*60)
    print("PRACTICE 3: SCOPE PARTITIONING")
    print("="*60)

    print("""
+------------------------------------------------------------------+
|                   SCOPE PARTITIONING CONCEPT                      |
+------------------------------------------------------------------+
|                                                                    |
|   +------------------------------------------------------------+   |
|   |                      FULL TOPIC                              |   |
|   +------------------------------------------------------------+   |
|                              |                                    |
|            +-----------------+-----------------+                  |
|            |                   |                   |              |
|            v                   v                   v              |
|   +-------------+      +-------------+      +-------------+        |
|   |   SCOPE A   |      |   SCOPE B   |      |   SCOPE C   |        |
|   | (Solar)     |      | (Wind)      |      | (Hydro)     |        |
|   +-------------+      +-------------+      +-------------+        |
|                              |                                    |
|                              v                                    |
|   +------------------------------------------------------------+   |
|   |                    AGGREGATOR                               |   |
|   +------------------------------------------------------------+   |
|                                                                    |
+------------------------------------------------------------------+
""")

    topic = "Renewable Energy Sources"
    scopes = RENEWABLE_ENERGY_SCOPES

    result = partition_and_research(topic, scopes)

    print("\n" + "="*60)
    print("FINAL REPORT:")
    print("="*60)
    print(result)
    print("\n" + "="*60)

    demonstrate_scope_boundaries()

    print("\n" + "="*60)
    print("PROGRAM COMPLETE!")
    print("="*60)
    print("\nSee WHAT WE HAVE LEARNT section for comprehensive summary.")