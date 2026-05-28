"""
PRACTICE 4: ITERATIVE REFINEMENT
================================
Coordinator checks results for gaps and refines until complete!

+------------------------------------------------------------------+
|                  ITERATIVE REFINEMENT FLOW                        |
+------------------------------------------------------------------+
|                                                                    |
|   +------------------+                                            |
|   | GENERATE v1      |  <-- Create initial content                |
|   +------------------+                                            |
|          |                                                        |
|          v                                                        |
|   +------------------+                                            |
|   | EVALUATE v1       |  <-- Check for gaps, issues               |
|   | Score: 65/100    |                                            |
|   +------------------+                                            |
|          |                                                        |
|          v (score < 90)                                          |
|   +------------------+                                            |
|   | REFINE -> v2     |  <-- Generate improved version             |
|   +------------------+                                            |
|          |                                                        |
|          v                                                        |
|   +------------------+                                            |
|   | EVALUATE v2      |  <-- Check again                           |
|   | Score: 78/100   |                                            |
|   +------------------+                                            |
|          |                                                        |
|          v (score < 90)                                          |
|   +------------------+                                            |
|   | REFINE -> v3     |  <-- One more iteration                    |
|   +------------------+                                            |
|          |                                                        |
|          v                                                        |
|   +------------------+                                            |
|   | EVALUATE v3      |  <-- Score: 92/100                         |
|   | Score: 92/100   |  <-- PASSED! Output ready                   |
|   +------------------+                                            |
|                                                                    |
|   MAX ITERATIONS REACHED? -> Stop and return best version         |
|                                                                    |
+------------------------------------------------------------------+

KEY CONCEPT: The coordinator doesn't assume the first output is good.
It EVALUATES the output and REFINES if needed.
Loop until quality threshold is met OR max iterations exhausted.
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
# QUALITY THRESHOLDS AND CONSTANTS
# ============================================================================

QUALITY_THRESHOLD = 90  # Score required to pass without refinement
MAX_ITERATIONS = 5      # Maximum refinement cycles


# ============================================================================
# REAL-TIME SCENARIO: Legal Document Drafting
# ============================================================================
"""
PRODUCTION SCENARIO: Contract Draft with Quality Gates

Legal department must produce a contract that meets compliance standards.

Iteration 1: Draft initial contract
  -> Evaluator: "Missing arbitration clause, liability cap too high"
  -> Score: 45/100 -> REJECT

Iteration 2: Refine with arbitration clause, reduced liability
  -> Evaluator: "Arbitration clause present, liability OK, but missing GDPR clause"
  -> Score: 65/100 -> REJECT

Iteration 3: Refine with GDPR compliance section
  -> Evaluator: "All clauses present, but definitions are unclear"
  -> Score: 80/100 -> REJECT

Iteration 4: Refine definitions for clarity
  -> Evaluator: "Contract meets all requirements"
  -> Score: 95/100 -> PASS

Output: Compliant contract ready for review

Without iterative refinement: missing clauses, compliance issues, rejections
With iterative refinement: each gap caught and fixed before delivery
"""


# ============================================================================
# MISTAKE #1: No Evaluation (Trust First Output)
# ============================================================================
"""
COMMON ERROR: Assuming the first generated output is good enough

    content = generate(topic)
    return content  # No checking!

WHY THIS BREAKS:
- First output may have factual errors
- May miss critical requirements
- Quality is inconsistent
- No way to catch degradation

CORRECT APPROACH:
    content = generate(topic)
    evaluation = evaluate(content)
    if evaluation['score'] < threshold:
        content = refine(content, evaluation)
    return content
"""


# ============================================================================
# MISTAKE #2: Infinite Loops (No Exit Condition)
# ============================================================================
"""
COMMON ERROR: Refining forever with no stopping point

    while True:
        content = refine(content)
        if some_criteria():
            break  # What if criteria never met?

WHY THIS BREAKS:
- Potential infinite loop
- Wastes API calls and money
- User gets no response
- System becomes unresponsive

CORRECT APPROACH:
    max_iterations = 5
    for i in range(max_iterations):
        content = generate(...)
        evaluation = evaluate(...)
        if evaluation['passes']:
            break
    return content  # Or best effort from all iterations
"""


# ============================================================================
# MISTAKE #3: Ignoring Evaluation Feedback
# ============================================================================
"""
COMMON ERROR: Passing evaluation results but not using them

    content = generate(topic)
    evaluation = evaluate(content)
    # Evaluation says "missing examples"
    # But we just call generate() again without addressing the gap!

WHY THIS BREAKS:
- Refinement doesn't fix actual problems
- Score doesn't improve (or gets worse)
- Wasted iterations

CORRECT APPROACH:
    content = generate(topic)
    evaluation = evaluate(content)
    gaps = evaluation['gaps']  # Get specific gaps

    # Feed gaps back to generator
    content = refine_with_feedback(topic, previous_work, gaps)
"""


# ============================================================================
# INTERVIEW Q&A: Iterative Refinement
# ============================================================================
"""
Q: How do you decide when to stop refining?
A: Multi-criteria stopping conditions:

   1. QUALITY THRESHOLD
   - If score >= threshold (e.g., 90/100), stop
   - This is the primary stopping condition

   2. MAX ITERATIONS
   - If we've tried N times, stop regardless of score
   - Prevents infinite loops
   - Return best effort from all iterations

   3. DIMINISHING RETURNS
   - If improvement between iterations is minimal (<2 points), stop
   - Suggests we're near the ceiling

   4. TIME BUDGET
   - If we've spent too much time, stop
   - Important for real-time applications

Q: How do you handle cases where refinement doesn't help?
A: Several strategies:

   1. RECORD ALL ITERATIONS
   - Save output from each iteration
   - If final score is worse, use earlier version

   2. CHANGE APPROACH
   - If purely generative refinement isn't helping,
   - Try different agent types (e.g., fact-checker instead of writer)

   3. ESCALATE
   - Flag as "requires human review"
   - Pass to human agent with all iteration attempts

Q: What's the cost trade-off for iterative refinement?
A: Each iteration costs API calls. Considerations:

   - Quality vs Cost: 1 iteration = baseline quality, 3 = higher, 5 = near ceiling
   - Set MAX based on value of output (high-value docs warrant more iterations)
   - Consider caching/refining for similar future requests
   - Budget for failed iterations too (not all will succeed)
"""


# ============================================================================
# AGENT IMPLEMENTATIONS
# ============================================================================

def generate_content(
    topic: str,
    previous_work: Optional[str] = None,
    feedback: Optional[str] = None
) -> str:
    """
    GENERATOR AGENT - Creates the content!

    ASCII ART: Generator with Feedback
    ==================================

    +------------------+
    | Base Topic       |
    +------------------+
          |
          v
    +------------------+
    | Previous Work    |  (if refinement)
    +------------------+
          |
          v (if feedback exists)
    +------------------+
    | Evaluation Gaps   |  "You're missing examples"
    +------------------+
          |
          v
    +------------------+
    | GENERATE          |  "Write with examples"
    +------------------+
          |
          v
    +------------------+
    | Improved Version  |
    +------------------+
    """
    print(f"   [GENERATOR] Creating content...")

    if previous_work:
        prompt = f"""Continue improving this content about: {topic}

PREVIOUS VERSION:
{previous_work}

"""
        if feedback:
            prompt += f"""
EVALUATION FEEDBACK (address these gaps):
{feedback}

"""
        prompt += """Add more detail, fix any issues, and improve the overall quality.
Make it more complete and thorough. Address the feedback directly."""
    else:
        prompt = f"""Write comprehensive content about: {topic}

Cover the key aspects and provide useful information."""

    response = client.messages.create(
        model="claude-haiku-4-5-20250601",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
        tools=[]
    )

    result = response.content[0].text
    print(f"   [GENERATOR] Content created ({len(result)} chars)")
    return result


def evaluate_coverage(content: str, topic: str) -> Dict[str, Any]:
    """
    EVALUATOR AGENT - Checks content for gaps and quality!

    ASCII ART: Evaluation Process
    ============================

    +------------------+
    | Content to       |
    | Evaluate          |
    +------------------+
          |
          v
    +------------------+
    | CHECK 1: Length   |  Is it long enough?
    +------------------+
          |
          v
    +------------------+
    | CHECK 2: Facts    |  Are claims accurate?
    +------------------+
          |
          v
    +------------------+
    | CHECK 3: Depth    |  Is it thorough?
    +------------------+
          |
          v
    +------------------+
    | CHECK 4: Clarity  |  Is it understandable?
    +------------------+
          |
          v
    +------------------+
    | FINAL SCORE       |  0-100
    +------------------+
          |
          v
    +------------------+
    | GAPS FOUND        |  What needs fixing
    +------------------+
    """
    print(f"   [EVALUATOR] Checking coverage...")

    prompt = f"""You are an evaluation agent. Check the following content for completeness.

TOPIC: {topic}

CONTENT TO EVALUATE:
{content}

Analyze and respond with:
1. COVERAGE SCORE (0-100): How complete is this content?
2. GAPS FOUND: What's missing or not covered well?
3. SPECIFIC IMPROVEMENTS NEEDED: What should be added or expanded?

Be critical but fair. Focus on what's truly missing."""

    response = client.messages.create(
        model="claude-haiku-4-5-20250601",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
        tools=[]
    )

    evaluation = response.content[0].text
    print(f"   [EVALUATOR] Evaluation complete")

    # Heuristic scoring (in production, use ML or more sophisticated methods)
    score = 50  # Base score

    # Length contributes to score
    if len(content) > 1000:
        score += 10
    if len(content) > 2000:
        score += 10
    if len(content) > 4000:
        score += 10

    # Structure and depth
    if "example" in content.lower() or "for instance" in content.lower():
        score += 5
    if "data" in content.lower() or "statistics" in content.lower():
        score += 5
    if "step" in content.lower() or "process" in content.lower():
        score += 5
    if "definition" in content.lower() or "means" in content.lower():
        score += 5

    # Penalize for obvious gaps (simple heuristic)
    if len(content.split()) < 100:
        score -= 10  # Too short

    # Cap at 95 (leave room for human review)
    return {
        "score": min(score, 95),
        "evaluation": evaluation,
        "has_gaps": score < QUALITY_THRESHOLD,
        "gaps": evaluation
    }


# ============================================================================
# ITERATIVE REFINEMENT LOOP
# ============================================================================

def iterative_refine(
    topic: str,
    max_iterations: int = MAX_ITERATIONS,
    quality_threshold: int = QUALITY_THRESHOLD
) -> Dict[str, Any]:
    """
    The coordinator with ITERATIVE REFINEMENT!

    ASCII ART: Full Refinement Loop
    ==============================

    Topic
      |
      v
    +-----------+
    | Iteration |--------------------+
    |     1     |                    |
    +-----------+                    |
      |                                |
      v                                |
    +-----------+                     |
    | GENERATE  |                     |
    +-----------+                     |
      |                                |
      v                                |
    +-----------+     Yes             |
    | EVALUATE   |---- score >= T ?---+
    +-----------+     |
      |     |         |
      |     | No      |
      |     v         |
      |  +-----------+|
      |  | gaps found ||
      |  +-----------+|
      |     |          |
      +-----+          |
                      (stop)
      |
      v
    Return Best Content

    """
    print(f"\n{'='*60}")
    print(f"[COORDINATOR] Iterative refinement for: {topic}")
    print(f"   Quality threshold: {quality_threshold}/100")
    print(f"   Max iterations: {max_iterations}")
    print('='*60)

    current_content = None
    best_content = None
    best_score = 0
    all_iterations = []

    for iteration in range(1, max_iterations + 1):
        print(f"\n{'='*50}")
        print(f"ITERATION {iteration}/{max_iterations}")
        print(f"{'='*50}")

        # Generate content
        if iteration == 1:
            print(f"   [COORDINATOR] Initial generation...")
            current_content = generate_content(topic)
        else:
            print(f"   [COORDINATOR] Refining based on previous gaps...")
            current_content = generate_content(
                topic,
                previous_work=current_content,
                feedback=all_iterations[-1]['gaps'] if all_iterations else None
            )

        # Evaluate content
        evaluation = evaluate_coverage(current_content, topic)

        print(f"\n   Coverage Score: {evaluation['score']}/100")
        print(f"   Has gaps: {evaluation['has_gaps']}")

        # Track all iterations
        all_iterations.append({
            'iteration': iteration,
            'score': evaluation['score'],
            'gaps': evaluation['gaps'],
            'content': current_content
        })

        # Track best content
        if evaluation['score'] > best_score:
            best_score = evaluation['score']
            best_content = current_content
            print(f"   NEW BEST: {best_score}/100")

        # Check stopping conditions
        if not evaluation['has_gaps']:
            print(f"\n   QUALITY THRESHOLD MET! Score: {evaluation['score']}/100")
            break

        if iteration == max_iterations:
            print(f"\n   MAX ITERATIONS REACHED ({max_iterations})")
            print(f"   Best score achieved: {best_score}/100")

        print(f"\n   Gaps identified:")
        gap_preview = evaluation['gaps'][:300] if evaluation['gaps'] else "None"
        print(f"   {gap_preview}...")

    print(f"\n{'='*50}")
    print("[COORDINATOR] Iterative refinement complete!")
    print(f"{'='*50}")
    print(f"   Total iterations: {len(all_iterations)}")
    print(f"   Best score: {best_score}/100")

    return {
        'content': best_content,
        'score': best_score,
        'iterations': len(all_iterations),
        'all_versions': all_iterations
    }


# ============================================================================
# DEMONSTRATION
# ============================================================================

def demonstrate_quality_progression():
    """
    Show how quality improves across iterations.
    """
    print("\n" + "="*60)
    print("QUALITY PROGRESSION EXAMPLE")
    print("="*60)
    print("""
    Iteration 1: "How does the stock market work?"
      -> Score: 45/100
      -> Gaps: Too basic, no examples, missing key concepts

    Iteration 2: "Refine with feedback: add examples, explain key concepts"
      -> Score: 68/100
      -> Gaps: Good depth, but missing risk information

    Iteration 3: "Add risk factors and mitigation strategies"
      -> Score: 85/100
      -> Gaps: Almost there, needs recent data references

    Iteration 4: "Include 2024 market trends and data"
      -> Score: 92/100
      -> Gaps: None - PASS!

    Output: Comprehensive, accurate, well-structured explanation
    """)


# ============================================================================
# WHAT WE HAVE LEARNT
# ============================================================================
"""
=============================================================================
WHAT WE HAVE LEARNT: Iterative Refinement
=============================================================================

1. CORE CONCEPT
   ------------
   - Don't trust first output - always evaluate
   - If gaps found, refine and re-evaluate
   - Loop until quality threshold met OR max iterations reached
   - Return best effort from all iterations

2. THE EVALUATE-GENERATE CYCLE
   ---------------------------

   +------------+      +-------------+
   | GENERATE   | ---> | EVALUATE    |
   | Create v1  |      | Check score |
   +------------+      +-------------+
          ^                 |
          |                 |
          |        +--------+
          |        |
          |        v (if gaps)
          |   +-------------+
          +-- | GENERATE    |
              | Create v2  |
              +-------------+
                     |
                     v (if still gaps)
                 REPEAT...

3. COMMON MISTAKES TO AVOID
   ------------------------
   MISTAKE 1: No Evaluation
   - "Just return the first output" - leads to inconsistent quality
   - ALWAYS check output before delivering

   MISTAKE 2: No Exit Condition
   - Infinite loop if criteria never met
   - ALWAYS set MAX_ITERATIONS as safety

   MISTAKE 3: Ignoring Feedback
   - "Evaluation says X" but refinement ignores X
   - Pass specific gaps to the generator

   MISTAKE 4: No Best Tracking
   - Content might get WORSE in later iterations
   - Track best score and return that version

4. QUALITY SCORING STRATEGIES
   --------------------------
   HEURISTIC SCORING (used in this example):
   - Length contribution (longer = more thorough)
   - Keyword presence (examples, data, definitions)
   - Structure indicators (steps, processes)

   LLM-BASED EVALUATION:
   - Use another LLM as evaluator
   - Prompt: "Rate this content 0-100 and explain gaps"
   - More accurate but more expensive

   HYBRID APPROACH:
   - Quick heuristic check first
   - Only call LLM evaluator if heuristic is borderline
   - Balances cost and accuracy

5. STOPPING CONDITIONS
   ------------------
   | Condition          | Action                          |
   |--------------------|--------------------------------|
   | Score >= threshold | Stop - output is good enough   |
   | Iterations == max  | Stop - return best effort      |
   | Improvement < 2%   | Stop - diminishing returns      |
   | Time exceeded      | Stop - real-time constraint    |

6. PRODUCTION CONSIDERATIONS
   -------------------------
   - Set thresholds based on use case (legal = high, chat = low)
   - Log all iterations for debugging and improvement
   - Consider caching successful patterns
   - Monitor cost per successful output
   - Track which gaps commonly appear (improve base generation)

7. INTERVIEW ANSWER FRAMEWORK
   --------------------------
   "How do you ensure quality in multi-agent outputs?"

   Step 1: Explain the problem
   "First outputs are often incomplete or contain errors.
    You can't just trust the initial result."

   Step 2: Describe the loop
   "We use iterative refinement: generate, evaluate, refine.
    If evaluation finds gaps, we pass feedback to generator
    and create an improved version."

   Step 3: Explain stopping
   "We stop when score meets threshold (e.g., 90/100) or
    we've hit max iterations (e.g., 5). We always return
    the best version from all attempts."

   Step 4: Address tradeoffs
   "More iterations = better quality but higher cost.
    We tune thresholds based on the value of the output.
    Legal documents get more iterations than chat responses."

8. VISUAL SUMMARY
   --------------

   ITERATIVE REFINEMENT TIMELINE:

   Iteration 1: Generate -> Evaluate -> Score: 45/100 -> GAPS FOUND
   Iteration 2: Generate -> Evaluate -> Score: 68/100 -> GAPS FOUND
   Iteration 3: Generate -> Evaluate -> Score: 85/100 -> GAPS FOUND
   Iteration 4: Generate -> Evaluate -> Score: 92/100 -> PASS!

   Quality: 45 -> 68 -> 85 -> 92 (improving)
   Cost: 1 -> 2 -> 3 -> 4 iterations

   TRADE-OFF: More iterations = higher cost but better quality

=============================================================================
"""


if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    print("\n" + "="*60)
    print("PRACTICE 4: ITERATIVE REFINEMENT")
    print("="*60)

    print("""
+------------------------------------------------------------------+
|                  ITERATIVE REFINEMENT FLOW                        |
+------------------------------------------------------------------+
|                                                                    |
|   +------------------+                                            |
|   | GENERATE v1      |                                            |
|   +------------------+                                            |
|          |                                                        |
|          v                                                        |
|   +------------------+                                            |
|   | EVALUATE v1       | ---- score >= 90? ---> STOP               |
|   +------------------+                                            |
|          |                                                        |
|          v (score < 90)                                          |
|   +------------------+                                            |
|   | REFINE -> v2     |                                            |
|   +------------------+                                            |
|          |                                                        |
|          v (repeat until pass or max iterations)                  |
|                                                                    |
+------------------------------------------------------------------+
""")

    topic = "How does the stock market work?"

    result = iterative_refine(topic, max_iterations=3)

    print("\n" + "="*60)
    print("FINAL RESULT:")
    print("="*60)
    print(f"Score: {result['score']}/100")
    print(f"Iterations: {result['iterations']}")
    print(f"\nContent preview:")
    print(result['content'][:1000] + ("..." if len(result['content']) > 1000 else ""))
    print("\n" + "="*60)

    demonstrate_quality_progression()

    print("\n" + "="*60)
    print("PROGRAM COMPLETE!")
    print("="*60)
    print("\nSee WHAT WE HAVE LEARNT section for comprehensive summary.")