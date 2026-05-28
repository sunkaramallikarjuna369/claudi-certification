"""
+===========================================================================+
|                                                                           |
|  PRACTICE 2: THE ATTENTION DILUTION PROBLEM                             |
|                                                                           |
|  When analyzing many items, attention gets spread thin.                  |
|  Early items get detailed focus, later items get shallow treatment.       |
|                                                                           |
|  + REAL-TIME SCENARIOS + MISTAKES + INTERVIEW Q&A + VISUALS             |
|                                                                           |
+===========================================================================+

This is an ARCHITECTURAL problem, not a model capability issue!

REAL-TIME SCENARIO: Your security team asks AI to review 50 files for
vulnerabilities. AI misses critical SQL injection in file 47. Why?

INTERVIEW PREP: "Why does attention dilution happen and how do you fix it?"
This tests understanding of architectural patterns vs model capabilities.

===========================================================================
 VISUAL: WHAT IS ATTENTION DILUTION?
===========================================================================

    +-----------------------------------------------------------------------+
    |  PROBLEM: Model allocates attention across ALL items                 |
    |                                                                       |
    |  When reviewing 14 files in one pass:                                |
    |                                                                       |
    |  +-------------------------------------------------------+           |
    |  | FILE 1   [███████████████████████████████] DETAILED    |           |
    |  | FILE 2   [███████████████████████████████] DETAILED    |           |
    |  | FILE 3   [███████████████████████████████] DETAILED    |           |
    |  | FILE 4   [███████████████████████████████] DETAILED    |           |
    |  | FILE 5   [███████████████████████████████] DETAILED    |           |
    |  | FILE 6   [████████████████████████████] MODERATE       |           |
    |  | FILE 7   [████████████████████████████] MODERATE       |           |
    |  | FILE 8   [████████████████████] SHAKING               |           |
    |  | FILE 9   [████████████████████] SHAKING               |           |
    |  | FILE 10  [███████████████] MINIMAL                    |           |
    |  | FILE 11  [███████████████] MINIMAL                    |           |
    |  | FILE 12  [███████████] SHALLOW                        |           |
    |  | FILE 13  [███████████] SHALLOW                        |           |
    |  | FILE 14  [███████] VERY SHALLOW                       |           |
    |  +-------------------------------------------------------+           |
    |                                                                       |
    |  Later files get progressively less attention!                       |
    |                                                                       |
    +-----------------------------------------------------------------------+

===========================================================================
 REAL-TIME SCENARIO 1: The Security Audit That Missed Critical Bugs
===========================================================================

    CONTEXT:
    - Company uses AI for security reviews before production deploy
    - Developer submits 14 files for security audit
    - Uses single-pass approach: "Review all these files"

    FILES 1-5: DETAILED REVIEW (consumed the attention budget)
    - Found null pointer risks in auth/permissions.py
    - Found SQL injection vulnerabilities in db/queries.py
    - Detailed suggestions for improvements

    FILES 10-14: SHALLOW REVIEW (attention was exhausted)
    - NULL POINTER BUG in utils/session.py -> MISSED!
    - SQL INJECTION in api/orders.py -> MISSED!
    - Only checked minor style issues

    THE BROKEN THING:
    - File 14 has NULL POINTER BUG that causes crash in production!
    - Attention was exhausted before reaching critical files
    - "File 14: Looks good" -> Deploys with critical bug

    ROOT CAUSE:
    - Single pass allocates attention across ALL 14 files
    - Early files consumed the attention budget
    - Later files got minimal coverage

===========================================================================
 REAL-TIME SCENARIO 2: The Documentation Quality Varies
===========================================================================

    CONTEXT:
    - AI reviews 20 API endpoint documents
    - Need consistent quality across all endpoints

    WHAT HAPPENS:
    - Endpoints 1-8: Detailed docs, examples, error cases covered
    - Endpoints 9-15: Basic coverage, some examples
    - Endpoints 16-20: "See similar endpoints" - no details!

    WHY THIS BREAKS THINGS:
    - Developers using endpoints 16-20 don't get full context
    - Important edge cases not documented
    - Users of the API get inconsistent experience

    THE PATTERN:
    - Attention dilutes as more items are processed
    - Later items systematically get worse quality
    - This is PREDICTABLE and REPEATABLE

===========================================================================
 REAL-TIME SCENARIO 3: The Code Review Inconsistency
===========================================================================

    CONTEXT:
    - Senior developer asks AI to review 30 files for bugs
    - AI flags issues in files 1-15 consistently
    - Files 16-30 have fewer issues reported

    DEVELOPER'S MISTAKE:
    - "Files 16-30 are probably cleaner code"
    - Only fixes issues in files 1-15
    - Deploys code with uncaught bugs

    WHY THIS IS WRONG:
    - Later files got LESS attention, not LESS bugs
    - Attention was diluted, not quality determined
    - Files 16-30 likely have EQUAL or MORE issues
    - But AI didn't have attention budget to find them

    THE INSIGHT:
    - Attention dilution is ARCHITECTURAL
    - More powerful model doesn't fix it
    - Better prompts doesn't fix it
    - Must use MULTI-PASS architecture

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


def demonstrate_attention_dilution():
    """
    Show how attention dilutes across many items.
    """
    print("\n" + "=" * 70)
    print("THE ATTENTION DILUTION PROBLEM")
    print("=" * 70)

    print("""
    +======================================================================+
    ||                                                                      ||
    ||  PROBLEM: Model allocates attention across ALL items                 ||
    ||                                                                      ||
    ||  When reviewing 14 files in one pass:                               ||
    ||                                                                      ||
    ||  +------------------------------------------------------+           ||
    ||  | FILE 1   [███████████████████████████████] DETAILED  |           ||
    ||  | FILE 2   [███████████████████████████████] DETAILED  |           ||
    ||  | FILE 3   [███████████████████████████████] DETAILED  |           ||
    ||  | FILE 4   [███████████████████████████████] DETAILED  |           ||
    ||  | FILE 5   [███████████████████████████████] DETAILED  |           ||
    ||  | FILE 6   [████████████████████████████] MODERATE    |           ||
    ||  | FILE 7   [████████████████████████████] MODERATE    |           ||
    ||  | FILE 8   [████████████████████] SHAKING            |           ||
    ||  | FILE 9   [████████████████████] SHAKING            |           ||
    ||  | FILE 10  [███████████████] MINIMAL                  |           ||
    ||  | FILE 11  [███████████████] MINIMAL                  |           ||
    ||  | FILE 12  [███████████] SHALLOW                      |           ||
    ||  | FILE 13  [███████████] SHALLOW                      |           ||
    ||  | FILE 14  [███████] VERY SHALLOW                     |           ||
    ||  +------------------------------------------------------+           ||
    ||                                                                      ||
    ||  Later files get progressively less attention!                      ||
    ||                                                                      ||
    +======================================================================+
    """)


def show_symptoms():
    """
    Show the symptoms of attention dilution.
    """
    print("\n" + "=" * 70)
    print("ATTENTION DILUTION SYMPTOMS")
    print("=" * 70)

    print("""
    +======================================================================+
    ||  SYMPTOM 1: Detailed feedback for first files, shallow for later   ||
    ||                                                                      ||
    ||  "Files 1-5 have thorough reviews with specific suggestions"         ||
    ||  "Files 10-14 have generic comments like 'looks good'"               ||
    +======================================================================+

    +======================================================================+
    ||  SYMPTOM 2: Inconsistent pattern detection                          ||
    ||                                                                      ||
    ||  "Same pattern flagged problematic in File 3"                        ||
    ||  "Same pattern approved in File 11"                                  ||
    ||  Model attention was already diluted when it reached File 11!       ||
    +======================================================================+

    +======================================================================+
    ||  SYMPTOM 3: Critical bugs missed, minor issues caught               ||
    ||                                                                      ||
    ||  "File 14 has NULL POINTER BUG that causes crash" <--- MISSED!       ||
    ||  "File 1 has minor style issue" <--- CAUGHT!                         ||
    ||                                                                      ||
    ||  Attention was exhausted before reaching the critical bug          ||
    +======================================================================+
    """)

    # Visual representation
    print("\nVISUAL: Review Quality Across 14 Files")
    print("-" * 50)
    print("File  | Quality of Review")
    print("-" * 50)
    for i in range(1, 15):
        quality = max(1, 10 - (i - 1) * 0.7)
        bar = "#" * int(quality)
        print(f"  {i:2}  | {bar} {quality:.1f}")


def show_the_real_example():
    """
    Show the real-world example from the certification guide.
    """
    print("\n" + "=" * 70)
    print("REAL EXAMPLE: 14-File Code Review")
    print("=" * 70)

    print("""
    +======================================================================+
    ||  SCENARIO: Code review 14 files in one pass                         ||
    ||                                                                      ||
    ||  EXPECTED: All files get same level of scrutiny                      ||
    ||  ACTUAL:                                                           ||
    ||                                                                      ||
    ||  Files 1-5: DETAILED REVIEW                                          ||
    ||    [CHECK] Found null pointer risks                                  ||
    ||    [CHECK] Found SQL injection vulnerabilities                       ||
    ||    [CHECK] Detailed suggestions for improvements                   ||
    ||                                                                      ||
    ||  Files 10-14: SHALLOW REVIEW                                         ||
    ||    [ X ] Missed null pointer bug (causes production crash!)         ||
    ||    [ X ] Missed SQL injection vulnerability                         ||
    ||    [ X ] Only checked minor style issues                             ||
    ||                                                                      ||
    ||  ROOT CAUSE: Attention was allocated across all 14 files            ||
    ||  Early files consumed the attention budget                          ||
    ||  Later files got minimal coverage                                   ||
    +======================================================================+
    """)


def show_wrong_fixes():
    """
    Show the wrong approaches to fixing attention dilution.
    """
    print("\n" + "=" * 70)
    print("WRONG FIXES (Exam Traps!)")
    print("=" * 70)

    print("""
    +======================================================================+
    ||                                                                      ||
    ||  WRONG FIX #1: Use a more powerful model                            ||
    ||  =================================================================   ||
    ||                                                                      ||
    ||  "Let's use Claude Opus instead of Sonnet for better results"        ||
    ||                                                                      ||
    ||  WHY IT'S WRONG:                                                     ||
    ||  Attention dilution is ARCHITECTURAL, not capability-related!         ||
    ||  More powerful model still has same attention allocation             ||
    ||  The problem is HOW we structure the task, not WHICH model           ||
    ||                                                                      ||
    ||  FIXED: Multi-pass architecture gives each item full attention       ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  WRONG FIX #2: Use larger context window                             ||
    ||  =================================================================   ||
    ||                                                                      ||
    ||  "Let's increase max_tokens to handle more files"                    ||
    ||                                                                      ||
    ||  WHY IT'S WRONG:                                                     ||
    ||  Larger context = more items to review                                ||
    ||  More items = more diluted attention                                 ||
    ||  Still doesn't solve the allocation problem                         ||
    ||                                                                      ||
    ||  Example:                                                            ||
    ||  - 14 files with 4096 tokens = moderate dilution                     ||
    ||  - 50 files with 8192 tokens = worse dilution!                       ||
    ||  - More capacity = more items = same problem                         ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  WRONG FIX #3: Write better prompts                                   ||
    ||  =================================================================   ||
    ||                                                                      ||
    ||  "Let's add more detailed instructions for thorough review"          ||
    ||                                                                      ||
    ||  WHY IT'S WRONG:                                                     ||
    ||  Better prompts improve AVERAGE quality                             ||
    ||  But they don't solve ATTENTION ALLOCATION                           ||
    ||  Model still divides attention across all items equally             ||
    ||  Later items still get less attention                                ||
    ||                                                                      ||
    ||  "Be thorough" instruction doesn't fix architectural problem         ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  WRONG FIX #4: Batch without integration pass                        ||
    ||  =================================================================   ||
    ||                                                                      ||
    ||  "Let's batch files 1-7 and 8-14 separately"                         ||
    ||                                                                      ||
    ||  WHY IT'S WRONG:                                                     ||
    ||  Still misses CROSS-CUTTING issues                                   ||
    ||  File 1 issue might relate to File 8 issue                           ||
    ||  Batching alone doesn't solve cross-item attention                   ||
    ||                                                                      ||
    ||  Example:                                                            ||
    ||  - Auth file (batch 1) uses MD5 for passwords                        ||
    ||  - Database file (batch 2) stores passwords in plaintext             ||
    ||  - Both batches missed the cross-file vulnerability!                 ||
    ||                                                                      ||
    +======================================================================+
    """)


def show_correct_fix():
    """
    Show the correct architectural fix: Multi-pass architecture.
    """
    print("\n" + "=" * 70)
    print("CORRECT FIX: MULTI-PASS ARCHITECTURE")
    print("=" * 70)

    print("""
    +======================================================================+
    ||  SOLUTION: Separate local analysis from cross-item integration      ||
    ||                                                                      ||
    ||  +------------------------------------------------------+           ||
    ||  |  PASS 1: Per-Item Local Analysis                     |           ||
    ||  |                                                      |           ||
    ||  |  Each file gets FULL attention budget:               |           ||
    ||  |                                                      |           ||
    ||  |  File 1  --> Full analysis, full attention           |           ||
    ||  |  File 2  --> Full analysis, full attention           |           ||
    ||  |  File 3  --> Full analysis, full attention           |           ||
    ||  |  ...                                                |           ||
    ||  |  File 14 --> Full analysis, full attention           |           ||
    ||  |                                                      |           ||
    ||  |  Each file gets the SAME quality of review!         |           ||
    ||  +------------------------------------------------------+           ||
    ||                           |                                          ||
    ||                           v                                          ||
    ||  +------------------------------------------------------+           ||
    ||  |  PASS 2: Cross-Item Integration                     |           ||
    ||  |                                                      |           ||
    ||  |  After all local passes complete:                   |           ||
    ||  |  [CHECK] Check for data flow consistency            |           ||
    ||  |  [CHECK] Check for pattern consistency across files |           ||
    ||  |  [CHECK] Check for dependency issues                |           ||
    ||  |  [CHECK] Check for cross-cutting security concerns  |           ||
    ||  |                                                      |           ||
    ||  |  Now ALL files have been analyzed thoroughly        |           ||
    ||  |  Integration can check relationships between them    |           ||
    ||  +------------------------------------------------------+           ||
    +======================================================================+
    """)

    print("\nWHY THIS WORKS:")
    print("-" * 50)
    print("""
    BEFORE (single pass):
        14 files / attention budget = diluted per file

    AFTER (multi-pass):
        14 passes * full attention = equally thorough per file
        + 1 integration pass for cross-file issues

    Result:
        [CHECK] All files get full attention
        [CHECK] Cross-cutting issues are caught
        [CHECK] No critical bugs missed in later files
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
    INTERVIEW Q1: "Why does attention dilution happen?"
    ======================================================================

    EXPECTED ANSWER:
    Attention dilution is architectural, not a model capability issue.
    When you give AI many items to process in one pass, it allocates
    attention across ALL items. Early items consume the attention budget,
    leaving less for later items. No model can maintain equal focus on
    50 items as it does on 5.

    RED FLAGS IN ANSWERS:
    - "The model is not powerful enough" -> Wrong framing
    - "We need better prompts" -> Doesn't fix allocation
    - "Context window is too small" -> More context = more items = worse

    +-----------------------------------------------------------------------+
    | EXPERT TIP: Emphasize "ARCHITECTURAL, not capability"                 |
    | This is the key insight interviewers want to hear                     |
    +-----------------------------------------------------------------------+
    """)

    message = client.messages.create(
        model="claude-haiku-4-5-20250601",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": "As an expert, explain in 2 sentences why attention "
                      "dilution happens and why more powerful models don't fix it."
        }]
    )

    print("Example Expert Answer:")
    print(f"    {message.content[0].text[:300]}...")

    # Q2
    print("""
    ======================================================================
    INTERVIEW Q2: "How do you fix attention dilution?"
    ======================================================================

    EXPECTED ANSWER:
    Multi-pass architecture separates local analysis from cross-item
    integration. Pass 1: Loop over each item, giving full attention to
    each one individually. Pass 2: After all local passes, check for
    cross-file/cross-item issues. This ensures every item gets equal
    attention AND cross-cutting concerns are caught.

    RED FLAGS IN ANSWERS:
    - "Use a more powerful model" -> Wrong (architectural issue)
    - "Batch files separately" -> Misses cross-file issues
    - "Write better prompts" -> Doesn't fix allocation problem

    +-----------------------------------------------------------------------+
    | EXPERT TIP: Mention BOTH passes: local + integration                  |
    | "Pass 1: each item gets full attention. Pass 2: check relationships"  |
    +-----------------------------------------------------------------------+
    """)

    # Q3
    print("""
    ======================================================================
    INTERVIEW Q3: "What's the difference between batching and multi-pass?"
    ======================================================================

    EXPECTED ANSWER:
    Batching splits items into groups but still uses single-pass per group.
    Multi-pass gives each item its OWN pass with full attention. Batching
    alone still has attention dilution within each batch. Multi-pass ensures
    every item gets equal focus AND still has integration pass for cross-item
    issues.

    +-----------------------------------------------------------------------+
    | EXPERT TIP: "Batching = same problem, smaller batches.                |
    | Multi-pass = different architecture, solves the problem."            |
    +-----------------------------------------------------------------------+
    """)


def show_decision_flowchart():
    """
    Shows visual flowchart for fixing attention dilution.
    """

    print("\n" + "=" * 70)
    print("VISUAL: FIXING ATTENTION DILUTION")
    print("=" * 70)

    print("""
                      +--------------------+
                      |  Need to review    |
                      |  multiple items?   |
                      +--------------------+
                               |
                               v
                    +---------------------+
                    | Is equal attention  |
                    | required for all?    |
                    +---------------------+
                          /        \\
                         /          \\
                        v            v
                      YES           NO
                       |              |
                       v              |
    +----------------------+           |
    | WRONG: Single pass   |          |
    | (attention dilutes) |           |
    +----------------------+           |
                       |              |
                       v              v
    +----------------------+    [Consider single pass]
    | CORRECT: Multi-pass  |
    | Architecture         |
    +----------------------+
           |
           v
    +----------------------+
    | PASS 1: Loop over   |
    | each item with full |
    | attention           |
    +----------------------+
           |
           v
    +----------------------+
    | PASS 2: Cross-item  |
    | integration for     |
    | relationships       |
    +----------------------+
    """)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("""
+===========================================================================+
|                                                                           |
|  PRACTICE 2: THE ATTENTION DILUTION PROBLEM                             |
|  + REAL-TIME SCENARIOS + MISTAKES + INTERVIEW Q&A + VISUALS             |
|                                                                           |
|  This program teaches:                                                   |
|  1. What attention dilution is and why it happens                       |
|  2. Real production scenarios where it causes failures                  |
|  3. Common mistakes developers make (exam traps!)                      |
|  4. The correct architectural fix (multi-pass)                         |
|                                                                           |
+===========================================================================+
    """)

    demonstrate_attention_dilution()
    show_symptoms()
    show_the_real_example()
    show_wrong_fixes()
    show_correct_fix()
    show_interview_qa()
    show_decision_flowchart()

    print("\n" + "=" * 70)
    print("WHAT WE HAVE LEARNT")
    print("=" * 70)
    print("""
    +======================================================================+
    ||  1. WHAT IS ATTENTION DILUTION:                                    ||
    ||                                                                      ||
    ||  - Model allocates attention across ALL items                      ||
    ||  - Early items get detailed focus                                   ||
    ||  - Later items get shallow treatment                                ||
    ||  - This is ARCHITECTURAL, not capability!                           ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  2. REAL-TIME SCENARIOS:                                            ||
    ||                                                                      ||
    ||  SCENARIO 1: Security Audit Missed Bugs                             ||
    ||  - 14 files reviewed in one pass                                    ||
    ||  - Files 1-5: detailed. Files 10-14: shallow                        ||
    ||  - NULL POINTER BUG in file 14 caused production crash!            ||
    ||                                                                      ||
    ||  SCENARIO 2: Documentation Quality Varies                             ||
    ||  - 20 API docs reviewed in one pass                                 ||
    ||  - Endpoints 1-8: detailed. Endpoints 16-20: minimal                ||
    ||  - Developers missing important context                             ||
    ||                                                                      ||
    ||  SCENARIO 3: Code Review Inconsistency                              ||
    ||  - 30 files reviewed in one pass                                    ||
    ||  - Later files have fewer issues reported                           ||
    ||  - But they likely have EQUAL or MORE issues                       ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  3. WRONG FIXES (EXAM TRAPS!):                                      ||
    ||                                                                      ||
    ||  [ X ] Use more powerful model                                       ||
    ||      - Still has same attention allocation                           ||
    ||      - Architectural problem, not capability!                        ||
    ||                                                                      ||
    ||  [ X ] Use larger context window                                     ||
    ||      - More items = more diluted attention                          ||
    ||                                                                      ||
    ||  [ X ] Write better prompts                                          ||
    ||      - Improves average, not allocation                             ||
    ||                                                                      ||
    ||  [ X ] Batch without integration                                     ||
    ||      - Still misses cross-file issues                                ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  4. CORRECT FIX: MULTI-PASS ARCHITECTURE                            ||
    ||                                                                      ||
    ||  PASS 1: Per-item local analysis                                    ||
    ||  - Loop over each item individually                                  ||
    ||  - Each item gets FULL attention                                     ||
    ||                                                                      ||
    ||  PASS 2: Cross-item integration                                      ||
    ||  - Check for relationships between items                             ||
    ||  - Find cross-cutting issues                                         ||
    ||                                                                      ||
    ||  Result: All items get equal attention + cross-file issues caught!   ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  5. INTERVIEW TIPS:                                                 ||
    ||                                                                      ||
    ||  - Mention "ARCHITECTURAL, not capability"                          ||
    ||  - Multi-pass = Pass 1 (local) + Pass 2 (integration)               ||
    ||  - Batching != Multi-pass (batching still has dilution)             ||
    ||                                                                      ||
    ||  EXPECTED ANSWER STRUCTURE:                                          ||
    ||  1. What attention dilution is (architectural)                     ||
    ||  2. Why wrong fixes don't work (explains each)                      ||
    ||  3. How multi-pass solves it (local + integration)                 ||
    ||                                                                      ||
    +======================================================================+

    Next: practice_03_fixed_pipeline.py shows how to implement
    a fixed sequential pipeline with proper error handling!
    """)


"""
+===========================================================================+
|                                                                           |
|  KEY CONCEPTS FROM THIS FILE:                                           |
|                                                                           |
|  ATTENTION DILUTION:                                                     |
|  - Model divides attention across all items                              |
|  - Later items get less focus                                            |
|  - Architectural problem, not model capability!                          |
|                                                                           |
|  WRONG FIXES (EXAM TRAPS):                                               |
|  - More powerful model                                                   |
|  - Larger context window                                                 |
|  - Better prompts                                                        |
|  - Batching without integration                                          |
|                                                                           |
|  CORRECT FIX:                                                            |
|  - Multi-pass architecture                                               |
|  - Pass 1: Per-item local analysis (full attention)                      |
|  - Pass 2: Cross-item integration (relationships)                        |
|                                                                           |
|  EXAM TIPS:                                                              |
|  - "Architectural, not capability" is the key phrase                   |
|  - Multi-pass = local + integration                                      |
|  - Mention both passes in answer                                         |
|                                                                           |
|  INTERVIEW PREP:                                                        |
|  - "Why does attention dilution happen?"                                |
|  - "How do you fix it?"                                                  |
|  - "What's the difference between batching and multi-pass?"             |
|                                                                           |
+===========================================================================+
"""