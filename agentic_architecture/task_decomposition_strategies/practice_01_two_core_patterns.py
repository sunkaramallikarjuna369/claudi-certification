"""
+===========================================================================+
|                                                                           |
|  PRACTICE 1: TWO CORE PATTERNS - FIXED vs DYNAMIC                       |
|                                                                           |
|  Learn the fundamental approaches to task decomposition                 |
|  + REAL-TIME SCENARIOS + MISTAKES + INTERVIEW Q&A + VISUALS              |
|                                                                           |
+===========================================================================+

This practice teaches the two fundamental approaches to task decomposition:

    FIXED SEQUENTIAL PIPELINE: Steps are known in advance
    DYNAMIC ADAPTIVE DECOMPOSITION: Steps emerge based on discoveries

REAL-TIME SCENARIO: You're building a code review pipeline. A developer
says "just review all 50 files" in one pass. What could go wrong?

INTERVIEW PREP: "When would you choose fixed pipeline over dynamic
decomposition?" Tests understanding of task characteristics.

===========================================================================
 VISUAL: TWO CORE PATTERNS COMPARISON
===========================================================================

    +-----------------------------------------------------------------------+
    |  PATTERN 1: FIXED SEQUENTIAL PIPELINE                                 |
    |  +---------------------------------------------------------------------+|
    |                                                                       |
    |    INPUT      STEP 1      STEP 2      STEP 3      STEP 4      OUTPUT  |
    |    ------+----------+----------+----------+----------+-------         |
    |         |          |          |          |          |                |
    |         v          v          v          v          v                |
    |     [EXTRACT] -> [TRANSFORM] -> [VALIDATE] -> [STORE]                |
    |         |          |            |            |                        |
    |         v          v            v            v                        |
    |     Raw Text   Cleaned Data  Schema OK   Success!                   |
    |                                                                       |
    |    Steps are PREDETERMINED and EXECUTE in ORDER                      |
    |    Each step takes previous output as input                          |
    |                                                                       |
    +-----------------------------------------------------------------------+

    +-----------------------------------------------------------------------+
    |  PATTERN 2: DYNAMIC ADAPTIVE DECOMPOSITION                             |
    |  +---------------------------------------------------------------------+|
    |                                                                       |
    |                         START TASK                                     |
    |                            |                                          |
    |                            v                                          |
    |                    [Analyze: A, B, C]                                 |
    |                            |                                          |
    |              +-------------+-------------+                           |
    |              |             |             |                             |
    |              v             v             v                             |
    |         [Subtask]    [Subtask]    [Subtask]                          |
    |            A            B            C                                |
    |              |             |             |                            |
    |              +-------------+-------------+                           |
    |                            |                                          |
    |                            v                                          |
    |                    [Analyze: New X, Y] <- DISCOVERED!                  |
    |                            |                                          |
    |              +-------------+-------------+                           |
    |              |             |             |                             |
    |              v             v             v                             |
    |         [Subtask]    [Subtask]    [Subtask]                          |
    |            X            Y           (more...)                        |
    |                                                                       |
    |    Subtasks GENERATED based on discoveries!                          |
    |    Plan EVOLVES as agent learns more about problem                    |
    |                                                                       |
    +-----------------------------------------------------------------------+

===========================================================================
 REAL-TIME SCENARIO 1: The Failed Code Review Pipeline
===========================================================================

    CONTEXT:
    - Company builds a security review pipeline for all new code
    - Developer creates one pipeline for "review all files"
    - 50 files submitted in one pass to the AI

    WHAT HAPPENS IN PRODUCTION:
    - Files 1-10 get detailed analysis (MD5 found, SQL injection found)
    - Files 30-40 get moderate attention (some issues found)
    - Files 45-50 get minimal attention (mostly skipped)

    THE BROKEN THING:
    - Critical SQL injection in file 47 was MISSED!
    - Agent was "tired" - attention was exhausted
    - Later files systematically get less attention

    WHY FIXED PIPELINE FAILS HERE:
    - Single pass cannot give equal attention to 50 items
    - Later items get progressively less focus
    - Critical bugs hide in files 40+

    THE FIX:
    - Use MULTI-PASS architecture (covered in Practice 5)
    - Pass 1: Each file gets full attention (loop over files)
    - Pass 2: Cross-file integration (find relationships)

===========================================================================
 REAL-TIME SCENARIO 2: The Legacy System Investigation
===========================================================================

    CONTEXT:
    - Developer inherits legacy system, no documentation
    - Task: "Find all security vulnerabilities"
    - Uses FIXED pipeline approach

    WHAT HAPPENS:
    - Creates 4 predetermined steps:
      Step 1: Check authentication files
      Step 2: Check database access patterns
      Step 3: Check API endpoints
      Step 4: Generate report

    THE PROBLEM:
    - Discovers auth system uses MD5 hashing (Step 1)
    - But this leads to needing to check password reset flow
    - Password reset flow leads to email verification
    - Email verification leads to...

    - FIXED PIPELINE CANNOT ADAPT!
    - Agent must either:
      a) Ignore the new findings (miss critical issues)
      b) Branch outside the pipeline (breaks the flow)

    WHY DYNAMIC DECOMPOSITION IS CORRECT HERE:
    - Start with authentication check
    - FINDING: MD5 vulnerability
    - NEW SUBTASK: Check password reset
    - FINDING: No rate limiting on password reset
    - NEW SUBTASK: Check email verification
    - Plan evolves with each discovery

    THE BROKEN THING:
    - Using the WRONG pattern for the task type
    - Fixed pipeline = known steps, known scope
    - Legacy investigation = unknown scope, discoveries matter

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


def demonstrate_fixed_pipeline():
    """
    Pattern 1: Fixed Sequential Pipeline (Prompt Chaining)
    """
    print("\n" + "=" * 70)
    print("PATTERN 1: FIXED SEQUENTIAL PIPELINE")
    print("=" * 70)

    print("""
    +======================================================================+
    ||  FIXED PIPELINE (Prompt Chaining)                                    ||
    ||                                                                      ||
    ||  Work breaks into PREDETERMINED steps in ORDER                      ||
    ||  Each step takes previous output as input                            ||
    ||                                                                      ||
    ||  +---------+    +---------+    +---------+    +---------+          ||
    ||  | Step 1  |--->| Step 2  |--->| Step 3  |--->| Step 4  |          ||
    ||  |         |    |         |    |         |    |         |          ||
    ||  | Extract |    |Transform|    |Validate |    | Load to |          ||
    ||  | PDF     |    | Data    |    | Schema  |    | DB      |          ||
    ||  +---------+    +---------+    +---------+    +---------+          ||
    ||       |              |              |              |                 ||
    ||       v              v              v              v                 ||
    ||   PDF Text      Cleaned CSV    Schema Valid   Success!             ||
    ||                                                                      ||
    ||  Characteristics:                                                   ||
    ||  [CHECK] Predictable - steps are known in advance                  ||
    ||  [CHECK] Consistent - same output for same input                   ||
    ||  [CHECK] Debuggable - easy to identify which step failed           ||
    ||  [CHECK] Monitorable - can track progress at each stage            ||
    ||                                                                      ||
    +======================================================================+
    """)

    print("\nWHEN TO USE FIXED PIPELINE:")
    print("-" * 50)
    scenarios = [
        ("Code review", "Review each file systematically"),
        ("Document processing", "Extract -> Transform -> Validate -> Load"),
        ("Compliance checks", "Check rule 1 -> Check rule 2 -> Generate report"),
        ("Data pipeline", "Fetch -> Clean -> Transform -> Store"),
    ]
    for task, desc in scenarios:
        print(f"    [CHECK] {task}: {desc}")


def demonstrate_dynamic_decomposition():
    """
    Pattern 2: Dynamic Adaptive Decomposition
    """
    print("\n" + "=" * 70)
    print("PATTERN 2: DYNAMIC ADAPTIVE DECOMPOSITION")
    print("=" * 70)

    print("""
    +======================================================================+
    ||  DYNAMIC ADAPTIVE DECOMPOSITION                                     ||
    ||                                                                      ||
    ||  Subtasks GENERATED based on discoveries                            ||
    ||  Plan EVOLVES as agent learns more about the problem                 ||
    ||                                                                      ||
    ||                          +---------+                                 ||
    ||                          | START   |                                 ||
    ||                          | Task    |                                 ||
    ||                          +----+----+                                 ||
    ||                               |                                      ||
    ||                               v                                      ||
    ||                    +------------------+                              ||
    ||                    |  Analyze        |                              ||
    ||                    |  Discovery #1   |                              ||
    ||                    +-------+----------+                              ||
    ||                            |                                       ||
    ||              +-------------+-------------+                          ||
    ||              |             |             |                          ||
    ||              v             v             v                          ||
    ||         +--------+   +--------+   +--------+                        ||
    ||         | Subtask|   | Subtask|   | Subtask|                        ||
    ||         |  A     |   |  B     |   |  C     |                        ||
    ||         +----+---+   +----+---+   +----+---+                        ||
    ||              |             |             |                         ||
    ||              +-------------+-------------+                          ||
    ||                            v                                       ||
    ||                    +------------------+                              ||
    ||                    |  Analyze        |                              ||
    ||                    |  Discovery #2   |                              ||
    ||                    +-------+----------+                              ||
    ||                            v                                       ||
    ||                    +------------------+                              ||
    ||                    | NEW SUBTASKS!   | <--- Surprises emerge!       ||
    ||                    | D-E-F discovered|                              ||
    ||                    +------------------+                              ||
    ||                                                                      ||
    ||  Characteristics:                                                   ||
    ||  [CHECK] Adapts to unexpected complexity                            ||
    ||  [CHECK] Produces thorough results                                   ||
    ||  [ X ] Less predictable                                             ||
    ||  [ X ] Harder to estimate completion time                            ||
    ||                                                                      ||
    +======================================================================+
    """)

    print("\nWHEN TO USE DYNAMIC DECOMPOSITION:")
    print("-" * 50)
    scenarios = [
        ("Legacy system exploration", "Don't know what you'll find"),
        ("Security audits", "Vulnerabilities can be anywhere"),
        ("Debugging unfamiliar code", "Root cause unknown"),
        ("Research investigation", "Open-ended, follow the evidence"),
    ]
    for task, desc in scenarios:
        print(f"    [CHECK] {task}: {desc}")


def show_selection_guide():
    """
    Guide for choosing the right pattern.
    """
    print("\n" + "=" * 70)
    print("SELECTION GUIDE: Which Pattern to Use?")
    print("=" * 70)

    print("""
    +======================================================================+
    ||                         DECISION MATRIX                             ||
    ||======================================================================|
    ||                                                                      ||
    ||  TASK CHARACTERISTICS          |         USE THIS PATTERN           ||
    ||  ----------------------------------------------------------------   ||
    ||                                                                      ||
    ||  Steps known in advance          |  FIXED PIPELINE                  ||
    ||  ------------------------------  |  -----------------------          ||
    ||  Predictable workflow            |  Sequential steps                 ||
    ||  Structured input/output         |  Easy to test each step           ||
    ||  Audit trail needed              |  Clear checkpoints                ||
    ||                                                                      ||
    ||======================================================================|
    ||                                                                      ||
    ||  Task Characteristics           |         USE THIS PATTERN           ||
    ||  ----------------------------------------------------------------   ||
    ||                                                                      ||
    ||  Open-ended, unknown scope       |  DYNAMIC DECOMPOSITION           ||
    ||  ------------------------------  |  -----------------------          ||
    ||  Discovery-driven                |  Subtasks emerge                  ||
    ||  Unexpected findings possible     |  Adapts to complexity            ||
    ||  Thoroughness over speed         |  Follow the evidence              ||
    ||                                                                      ||
    +======================================================================+
    """)

    print("\nPRACTICAL EXAMPLES:")
    print("-" * 50)

    examples = [
        ("Multi-file code review", "FIXED", "Review each file in order, systematic"),
        ("Legacy codebase exploration", "DYNAMIC", "Explore, discover, follow leads"),
        ("Document extraction", "FIXED", "Extract -> Validate -> Transform -> Store"),
        ("Security audit", "DYNAMIC", "Scan for vulnerabilities, follow any findings"),
        ("Compliance check", "FIXED", "Check each rule systematically"),
        ("Debug unfamiliar system", "DYNAMIC", "Hypothesize -> Investigate -> Discover root cause"),
    ]

    print(f"{'Task':<35} {'Pattern':<10} {'Why':<30}")
    print("-" * 75)
    for task, pattern, why in examples:
        print(f"{task:<35} {pattern:<10} {why:<30}")


def show_real_time_mistakes():
    """
    Shows REAL mistakes developers make with pattern selection.
    """

    print("\n" + "=" * 70)
    print("REAL MISTAKES DEVELOPERS MAKE - EXPERT WARNINGS")
    print("=" * 70)

    print("""
    +======================================================================+
    ||                                                                      ||
    ||  MISTAKE #1: Using FIXED pipeline for open-ended investigation      ||
    ||  =================================================================   ||
    ||                                                                      ||
    ||  WHAT HAPPENS IN PRODUCTION:                                        ||
    ||  - Developer building security audit pipeline                        ||
    ||  - Uses fixed 4-step approach: Auth -> DB -> API -> Report          ||
    ||  - Discovers MD5 vulnerability in auth (Step 1)                     ||
    ||  - But MD5 leads to password reset issues                           ||
    ||  - Password reset leads to email verification                       ||
    ||  - FIXED pipeline CANNOT add new steps!                            ||
    ||                                                                      ||
    ||  REAL CONSEQUENCE:                                                   ||
    ||  - Either skip the new findings (miss critical issues)               ||
    ||  - Or force findings into wrong steps (lose context)                ||
    ||  - Audit is incomplete, critical vulnerabilities missed              ||
    ||                                                                      ||
    ||  CORRECT APPROACH:                                                   ||
    ||  - Use DYNAMIC DECOMPOSITION                                        ||
    ||  - Let subtasks emerge from discoveries                              ||
    ||  - Follow the evidence wherever it leads                            ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  MISTAKE #2: Using DYNAMIC for structured, predictable tasks        ||
    ||  =================================================================   ||
    ||                                                                      ||
    ||  WHAT HAPPENS:                                                       ||
    ||  - Developer building document processing pipeline                  ||
    ||  - Uses dynamic decomposition "to be flexible"                      ||
    ||  - Each document triggers different subtask sequence                 ||
    ||  - No consistency between documents                                 ||
    ||  - Hard to audit, predict, or test                                 ||
    ||                                                                      ||
    ||  REAL CONSEQUENCE:                                                   ||
    ||  - Document A: Extract -> Transform -> Validate -> Store             ||
    ||  - Document B: Transform -> Extract -> Store (skip validation!)     ||
    ||  - Inconsistent results, quality varies                             ||
    ||  - Cannot give stakeholders predictable pipeline                    ||
    ||                                                                      ||
    ||  CORRECT APPROACH:                                                   ||
    ||  - FIXED pipeline for structured tasks                              ||
    ||  - Steps are known, order is clear, can test each step              ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  MISTAKE #3: Not considering ATTENTION DILUTION for batch review    ||
    ||  =================================================================   ||
    ||                                                                      ||
    ||  WHAT HAPPENS:                                                       ||
    ||  - Developer needs to review 50 files                               ||
    ||  - Uses fixed OR dynamic, single pass over all files                ||
    ||  - Files 1-20 get good attention, files 30-50 get shallow           ||
    ||  - Critical bugs in file 47 are MISSED                              ||
    ||                                                                      ||
    ||  REAL CONSEQUENCE:                                                   ||
    ||  - "Your review missed the SQL injection in file 47!"                ||
    ||  - "File 47 causes production crash"                                ||
    ||  - Both fixed and dynamic suffer from same problem                  ||
    ||                                                                      ||
    ||  CORRECT APPROACH:                                                   ||
    ||  - MULTI-PASS architecture (covered in Practice 5)                   ||
    ||  - Pass 1: Each file gets FULL attention (loop)                     ||
    ||  - Pass 2: Cross-file integration                                   ||
    ||                                                                      ||
    +======================================================================+
    """)


def show_interview_qa():
    """
    Shows common interview questions and expert answers.
    """

    client = anthropic.Anthropic(api_key=API_KEY)

    print("\n" + "=" * 70)
    print("INTERVIEW QUESTIONS & EXPERT ANSWERS GUIDE")
    print("=" * 70)

    # Q1
    print("""
    ======================================================================
    INTERVIEW Q1: "When would you choose fixed pipeline over dynamic?"
    ======================================================================

    EXPECTED ANSWER:
    Fixed pipeline when steps are known in advance and task is structured.
    Examples: code review (each file), document processing (extract ->
    transform -> validate -> store), compliance checks. Fixed pipeline
    gives predictable execution, clear checkpoints, and easy debugging.

    RED FLAGS IN ANSWERS:
    - "Always use fixed pipeline" -> Shows misunderstanding
    - "Dynamic is always better because it's flexible" -> Wrong for structured tasks
    - Can't give concrete examples -> Not clear on use cases

    +-----------------------------------------------------------------------+
    | EXPERT TIP: Give specific examples from your experience.              |
    | "I use fixed for our CI/CD pipeline because steps never change"       |
    +-----------------------------------------------------------------------+
    """)

    message = client.messages.create(
        model="claude-haiku-4-5-20250601",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": "As an expert, explain in 2 sentences when to choose "
                      "fixed pipeline over dynamic decomposition."
        }]
    )

    print("Example Expert Answer:")
    print(f"    {message.content[0].text[:300]}...")

    # Q2
    print("""
    ======================================================================
    INTERVIEW Q2: "What's the main weakness of fixed sequential pipeline?"
    ======================================================================

    EXPECTED ANSWER:
    Cannot adapt to unexpected findings. If you discover something in step 2
    that requires investigating a new area, fixed pipeline has no mechanism
    to add new steps or change direction. You're stuck with the predetermined
    plan even when evidence suggests a different approach.

    Also: attention dilution when processing many items in single pass.

    RED FLAGS IN ANSWERS:
    - "No weakness, it's simple" -> Oversimplifies
    - "Performance issues" -> Not the main weakness

    +-----------------------------------------------------------------------+
    | EXPERT TIP: Mention attention dilution as second weakness.           |
    | "Fixed pipeline also suffers from attention dilution in batch review" |
    +-----------------------------------------------------------------------+
    """)

    # Q3
    print("""
    ======================================================================
    INTERVIEW Q3: "How do you decide between the two patterns?"
    ======================================================================

    EXPECTED ANSWER:
    Ask: "Do I know the steps in advance?" If yes -> fixed pipeline.
    Ask: "Is the scope open-ended?" If yes -> dynamic decomposition.
    Ask: "Are there many items needing equal attention?" If yes -> multi-pass.

    +-----------------------------------------------------------------------+
    | EXPERT TIP: Mention the decision criteria clearly:                    |
    | - Known steps -> Fixed                                                |
    | - Unknown scope -> Dynamic                                            |
    | - Many items -> Multi-pass                                            |
    +-----------------------------------------------------------------------+
    """)


def demonstrate_three_patterns():
    """
    Demonstrate all three patterns with AI responses.
    """

    client = anthropic.Anthropic(api_key=API_KEY)

    print("\n" + "=" * 70)
    print("THREE PATTERNS DEMONSTRATION")
    print("=" * 70)

    print("""
    =======================================================================
    PATTERN SELECTION QUIZ: Which pattern fits each scenario?
    =======================================================================
    """)

    scenarios = [
        "Review 100 code files for security vulnerabilities",
        "Process incoming invoices: extract data, validate, store in database",
        "Debug an unfamiliar system where root cause is unknown",
        "Extract text from PDFs, transform to structured format, validate schema"
    ]

    for i, scenario in enumerate(scenarios, 1):
        print(f"\nScenario {i}: {scenario}")

        message = client.messages.create(
            model="claude-haiku-4-5-20250601",
            max_tokens=512,
            messages=[{
                "role": "user",
                "content": f"For this scenario: '{scenario}'. Should you use "
                          "fixed pipeline, dynamic decomposition, or multi-pass? "
                          "Answer in 2 sentences."
            }]
        )

        print(f"    {message.content[0].text[:200]}...")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("""
+===========================================================================+
|                                                                           |
|  PRACTICE 1: TWO CORE PATTERNS - FIXED vs DYNAMIC                       |
|  + REAL-TIME SCENARIOS + MISTAKES + INTERVIEW Q&A + VISUALS              |
|                                                                           |
|  This program teaches:                                                    |
|  1. Two fundamental approaches to task decomposition                    |
|  2. Real production scenarios where each pattern fits                   |
|  3. Common mistakes developers make                                      |
|  4. Interview Q&A with expert answer frameworks                         |
|                                                                           |
+===========================================================================+
    """)

    demonstrate_fixed_pipeline()
    demonstrate_dynamic_decomposition()
    show_selection_guide()
    show_real_time_mistakes()
    show_interview_qa()
    demonstrate_three_patterns()

    print("\n" + "=" * 70)
    print("WHAT WE HAVE LEARNT")
    print("=" * 70)
    print("""
    +======================================================================+
    ||  1. TWO CORE PATTERNS:                                              ||
    ||                                                                      ||
    ||  FIXED SEQUENTIAL PIPELINE:                                         ||
    ||  - Steps known in advance, execute in order                          ||
    ||  - Each step takes previous output as input                         ||
    ||  - Best for: code review, document processing, compliance            ||
    ||                                                                      ||
    ||  DYNAMIC ADAPTIVE DECOMPOSITION:                                     ||
    ||  - Subtasks generated based on discoveries                          ||
    ||  - Plan evolves as more is learned                                   ||
    ||  - Best for: investigation, security audits, debugging              ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  2. REAL-TIME SCENARIOS:                                            ||
    ||                                                                      ||
    ||  SCENARIO 1: Code Review Pipeline                                   ||
    ||  - Single pass over 50 files -> attention dilutes                   ||
    ||  - Critical bugs in files 45-50 are MISSED                         ||
    ||  - Fix: Use multi-pass architecture                                 ||
    ||                                                                      ||
    ||  SCENARIO 2: Legacy System Investigation                             ||
    ||  - Using fixed pipeline for open-ended investigation                ||
    ||  - Cannot add new subtasks when discoveries emerge                  ||
    ||  - Fix: Use dynamic decomposition                                    ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  3. COMMON MISTAKES (EXPERT WARNINGS):                               ||
    ||                                                                      ||
    ||  MISTAKE #1: Fixed for open-ended tasks                             ||
    ||  - Cannot adapt when discoveries require new direction              ||
    ||                                                                      ||
    ||  MISTAKE #2: Dynamic for structured tasks                           ||
    ||  - Inconsistent results, hard to audit                               ||
    ||                                                                      ||
    ||  MISTAKE #3: Ignoring attention dilution                            ||
    ||  - Both patterns fail for batch review without multi-pass           ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  4. INTERVIEW TIPS:                                                 ||
    ||                                                                      ||
    ||  - Know concrete examples for each pattern                          ||
    ||  - Fixed: document processing, compliance checks                     ||
    ||  - Dynamic: legacy exploration, security audits                      ||
    ||  - Mention attention dilution as key weakness                       ||
    ||                                                                      ||
    ||  EXPECTED ANSWER STRUCTURE:                                          ||
    ||  1. State the scenario                                              ||
    ||  2. State the correct pattern                                       ||
    ||  3. Explain WHY this pattern fits                                    ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  5. KEY RULES TO MEMORIZE:                                          ||
    ||                                                                      ||
    ||  RULE #1: Known steps? -> Fixed pipeline                             ||
    ||  RULE #2: Unknown scope? -> Dynamic decomposition                    ||
    ||  RULE #3: Many items equal attention? -> Multi-pass                 ||
    ||  RULE #4: Wrong pattern = poor results or wasted effort             ||
    ||                                                                      ||
    +======================================================================+

    Next: practice_02_attention_dilution.py explains WHY single-pass
    review fails and how attention dilution affects quality!
    """)


"""
+===========================================================================+
|                                                                           |
|  KEY CONCEPTS FROM THIS FILE:                                           |
|                                                                           |
|  PATTERNS:                                                               |
|  - Fixed sequential pipeline: steps known, execute in order             |
|  - Dynamic adaptive decomposition: subtasks emerge from discoveries     |
|                                                                           |
|  REAL-TIME SCENARIOS:                                                    |
|  - Code review pipeline misses bugs in later files                       |
|  - Legacy investigation cannot adapt with fixed pipeline                 |
|                                                                           |
|  MISTAKES TO AVOID:                                                     |
|  - Fixed for open-ended tasks                                            |
|  - Dynamic for structured tasks                                          |
|  - Ignoring attention dilution for batch review                          |
|                                                                           |
|  EXAM TIPS:                                                              |
|  - Know when to use each pattern                                         |
|  - Give concrete examples in interview                                   |
|  - Mention attention dilution as key weakness                            |
|                                                                           |
|  INTERVIEW PREP:                                                        |
|  - "When would you choose fixed over dynamic?"                           |
|  - "What's the main weakness of fixed pipeline?"                         |
|  - "How do you decide which pattern to use?"                             |
|                                                                           |
+===========================================================================+
"""