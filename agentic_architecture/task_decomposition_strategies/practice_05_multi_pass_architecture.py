"""
+===========================================================================+
|                                                                           |
|  PRACTICE 5: MULTI-PASS ARCHITECTURE                                     |
|                                                                           |
|  The architectural fix for attention dilution:                           |
|  1. Per-item local analysis passes: Full attention per item              |
|  2. Cross-item integration pass: Check relationships between items      |
|                                                                           |
|  This solves the problem of later items getting less attention.          |
|                                                                           |
|  + REAL-TIME SCENARIOS + MISTAKES + INTERVIEW Q&A + VISUALS             |
|                                                                           |
+===========================================================================+

This file shows the complete multi-pass architecture implementation.

REAL-TIME SCENARIO: Your security team needs to review 100 code files
for vulnerabilities. Using single pass, you miss critical bugs in files
80-100. How do you ensure equal coverage?

INTERVIEW PREP: "How does multi-pass architecture fix attention dilution?"
Tests understanding of architectural patterns and when to apply them.

===========================================================================
 VISUAL: MULTI-PASS vs SINGLE PASS
===========================================================================

    +-----------------------------------------------------------------------+
    |  BEFORE: Single Pass (Attention Dilution)                            |
    |                                                                       |
    |  Files 1-5:   [███████████████████████████████] DETAILED            |
    |  Files 10-14: [███████] VERY SHALLOW                                 |
    |                                                                       |
    |  Result: Critical bugs MISSED in files 10-14!                        |
    +-----------------------------------------------------------------------+

    +-----------------------------------------------------------------------+
    |  AFTER: Multi-Pass (Architectural Fix)                                |
    |                                                                       |
    |  PASS 1: Each file gets FULL attention                               |
    |  ----------------------------------------------------------------    |
    |  File 1:  [███████████████████████████████] 100% attention           |
    |  File 2:  [███████████████████████████████] 100% attention           |
    |  File 14: [███████████████████████████████] 100% attention <- FIXED!|
    |                                                                       |
    |  PASS 2: Cross-file integration                                     |
    |  ----------------------------------------------------------------    |
    |  - Auth file uses MD5 --> Database stores plaintext?                 |
    |  - API has no rate limiting --> Can exploit auth vulnerabilities     |
    |                                                                       |
    |  Result: ALL files get EQUAL attention! Critical bugs caught!        |
    +-----------------------------------------------------------------------+

===========================================================================
 REAL-TIME SCENARIO 1: The Security Audit That Caught Everything
===========================================================================

    CONTEXT:
    - Company needs to audit 50 files for security issues
    - Previous audit missed bugs in files 35-50 (attention diluted)
    - Using multi-pass architecture this time

    PASS 1: LOCAL ANALYSIS
    - Loop over each file individually
    - File 1: Full analysis (MD5 found, SQL injection found)
    - File 2: Full analysis (No issues)
    - File 50: Full analysis (Buffer overflow found!) <- NOW CAUGHT!

    THE FIX:
    - Each file gets 100% attention
    - No attention sharing between files
    - File 50 gets same quality review as File 1

    PASS 2: INTEGRATION
    - Auth file uses MD5 for password hashing
    - Database file stores passwords in plaintext
    - Integration finds: "MD5 hash + plaintext storage = exploit path"
    - This cross-file issue would be MISSED in single-pass!

    RESULT:
    - All 50 files reviewed with equal attention
    - 15 critical issues found in files 30-50 (would have been missed!)
    - 5 cross-file vulnerabilities found in integration pass

===========================================================================
 REAL-TIME SCENARIO 2: The Documentation Consistency Fix
===========================================================================

    CONTEXT:
    - AI generates documentation for 30 API endpoints
    - Previous single-pass: endpoints 20-30 had minimal docs
    - Using multi-pass this time

    PASS 1: LOCAL ANALYSIS
    - Each endpoint gets full documentation pass
    - Endpoint 1: Detailed, examples, error cases, best practices
    - Endpoint 30: Same level of detail! <- NOW CONSISTENT!

    PASS 2: INTEGRATION
    - Check for cross-endpoint consistency
    - Find: "Endpoint 5 and Endpoint 15 use different auth patterns"
    - Integration pass flags this inconsistency

    RESULT:
    - All 30 endpoints have consistent documentation
    - Cross-endpoint inconsistencies caught
    - No "see similar endpoint" shortcuts

===========================================================================
 REAL-TIME SCENARIO 3: The Bug Hunt That Found the Root Cause
===========================================================================

    CONTEXT:
    - Production system crashes intermittently
    - 20 files involved in the crash path
    - Need thorough review

    SINGLE-PASS PROBLEM:
    - Files 1-7: detailed analysis
    - Files 15-20: shallow analysis
    - Root cause in file 18 is MISSED

    MULTI-PASS SOLUTION:
    PASS 1: Each file gets full attention
    - File 18: Gets 100% analysis
    - Finds: "Race condition in concurrent access"
    - Finds: "No mutex protection in shared state"

    PASS 2: Integration
    - File 18 race condition + File 12 async handler = crash path
    - Integration maps the complete crash path across files

    RESULT:
    - Root cause found in file 18 (would have been missed!)
    - Complete crash path mapped across 5 files
    - Fix identified: add mutex protection

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


# ================================================================================
# MULTI-PASS REVIEWER: Implementation
# ================================================================================

class MultiPassCodeReviewer:
    """
    Multi-pass architecture for code review.
    Solves attention dilution by giving each file full attention.
    """

    def __init__(self):
        self.local_results = []
        self.integration_issues = []

    def pass_1_local_analysis(self, files: list) -> list:
        """
        PASS 1: Per-Item Local Analysis

        Each file gets FULL attention budget.
        No attention is shared with other files.
        """
        print("\n" + "=" * 70)
        print("PASS 1: LOCAL ANALYSIS (Per-File)")
        print("=" * 70)

        print(f"\n   Reviewing {len(files)} files with FULL attention each...")

        local_results = []

        for i, file in enumerate(files, 1):
            print(f"\n   [{i}/{len(files)}] Analyzing {file['name']}...")
            print(f"       Full attention budget allocated!")

            # Simulate full attention analysis
            result = self._analyze_file_with_full_attention(file)

            local_results.append(result)
            print(f"       Found {len(result['issues'])} issues")

        print("\n   [PASS 1 COMPLETE] All files analyzed with equal attention!")
        return local_results

    def _analyze_file_with_full_attention(self, file: dict) -> dict:
        """
        Analyze a single file with full attention.
        """
        # Simulate thorough analysis
        issues = []

        # In real implementation, this would use the AI with full context on ONE file
        file_name = file['name']

        # Check for various issues (simulated findings)
        if 'auth' in file_name.lower():
            issues.append({
                "severity": "high",
                "type": "security",
                "description": "Authentication uses MD5 for password hashing"
            })
            issues.append({
                "severity": "medium",
                "type": "best_practice",
                "description": "Session timeout not implemented"
            })

        if 'database' in file_name.lower() or 'db' in file_name.lower():
            issues.append({
                "severity": "high",
                "type": "security",
                "description": "SQL queries use string concatenation - SQL injection risk"
            })
            issues.append({
                "severity": "low",
                "type": "style",
                "description": "Missing database connection timeout"
            })

        if 'api' in file_name.lower():
            issues.append({
                "severity": "medium",
                "type": "security",
                "description": "API lacks rate limiting"
            })

        return {
            "file": file['name'],
            "issues": issues,
            "lines_reviewed": file.get('lines', 100),
            "attention_used": "100%"  # Full attention!
        }

    def pass_2_integration(self, local_results: list) -> list:
        """
        PASS 2: Cross-Item Integration

        After all local passes complete, check for:
        - Data flow consistency
        - Pattern consistency across files
        - Dependency issues
        - Cross-cutting security concerns
        """
        print("\n" + "=" * 70)
        print("PASS 2: CROSS-ITEM INTEGRATION")
        print("=" * 70)

        print("\n   Checking for cross-cutting issues...")

        integration_issues = []

        # Check 1: Consistent security patterns
        auth_files = [r for r in local_results if 'auth' in r['file'].lower()]
        if len(auth_files) > 1:
            # Check if they use consistent hashing
            hashing_issues = [f for f in auth_files if any(
                'MD5' in i['description'] for i in f['issues']
            )]
            if hashing_issues:
                integration_issues.append({
                    "type": "inconsistency",
                    "severity": "high",
                    "description": "Inconsistent password hashing: Some files use MD5, others may use stronger algorithms",
                    "affected_files": [f['file'] for f in hashing_issues],
                    "recommendation": "Standardize on bcrypt or argon2 for password hashing"
                })

        # Check 2: Data flow across files
        db_files = [r for r in local_results if 'database' in r['file'].lower() or 'db' in r['file'].lower()]
        api_files = [r for r in local_results if 'api' in r['file'].lower()]

        if db_files and api_files:
            # Check if API properly validates before database calls
            if any('SQL injection' in i['description'] for f in db_files for i in f['issues']):
                integration_issues.append({
                    "type": "data_flow_security",
                    "severity": "critical",
                    "description": "SQL injection in database layer could be exploited via API endpoints",
                    "recommendation": "API should validate all inputs before database operations"
                })

        # Check 3: Dependency issues
        integration_issues.append({
            "type": "dependency",
            "severity": "low",
            "description": "auth_service imports deprecated utility module",
            "recommendation": "Update to new utility package"
        })

        print(f"\n   Found {len(integration_issues)} cross-cutting issues")
        for issue in integration_issues:
            print(f"   * {issue['description']}")

        return integration_issues

    def run_review(self, files: list) -> dict:
        """
        Run complete multi-pass review.
        """
        print("\n" + "=" * 70)
        print("MULTI-PASS CODE REVIEW")
        print("=" * 70)

        # PASS 1: Local analysis
        local_results = self.pass_1_local_analysis(files)

        # PASS 2: Integration
        integration_issues = self.pass_2_integration(local_results)

        # Combine results
        all_issues = []
        for result in local_results:
            for issue in result['issues']:
                issue['file'] = result['file']
                all_issues.append(issue)

        # Deduplicate and add integration issues
        for int_issue in integration_issues:
            all_issues.append({
                **int_issue,
                'file': int_issue.get('affected_files', ['multiple'])
            })

        return {
            "status": "complete",
            "files_reviewed": len(files),
            "local_results": local_results,
            "integration_issues": integration_issues,
            "total_issues": len(all_issues),
            "all_issues": all_issues,
            "critical_issues": [i for i in all_issues if i.get('severity') == 'critical'],
            "high_issues": [i for i in all_issues if i.get('severity') == 'high'],
            "medium_issues": [i for i in all_issues if i.get('severity') == 'medium'],
            "low_issues": [i for i in all_issues if i.get('severity') == 'low']
        }


def demonstrate_multi_pass():
    """
    Demonstrate the multi-pass architecture.
    """
    print("\n" + "=" * 70)
    print("MULTI-PASS ARCHITECTURE DEMONSTRATION")
    print("=" * 70)

    # Sample files to review
    files = [
        {"name": "auth/login.py", "lines": 150},
        {"name": "auth/session.py", "lines": 200},
        {"name": "database/queries.py", "lines": 300},
        {"name": "database/models.py", "lines": 250},
        {"name": "api/endpoints.py", "lines": 400},
        {"name": "utils/helpers.py", "lines": 100},
    ]

    reviewer = MultiPassCodeReviewer()
    result = reviewer.run_review(files)

    print("\n" + "=" * 70)
    print("REVIEW RESULTS SUMMARY")
    print("=" * 70)

    print(f"\n   Files reviewed: {result['files_reviewed']}")
    print(f"   Total issues found: {result['total_issues']}")
    print(f"\n   Critical: {len(result['critical_issues'])}")
    print(f"   High: {len(result['high_issues'])}")
    print(f"   Medium: {len(result['medium_issues'])}")
    print(f"   Low: {len(result['low_issues'])}")

    print("\n   CRITICAL ISSUES (would have been missed without multi-pass):")
    for issue in result['critical_issues']:
        print(f"   * {issue['description']}")


def show_before_after():
    """
    Show the before/after comparison.
    """
    print("\n" + "=" * 70)
    print("BEFORE vs AFTER MULTI-PASS")
    print("=" * 70)

    print("""
    +======================================================================+
    ||  BEFORE: Single Pass (Attention Dilution)                            ||
    ||                                                                      ||
    ||  Files 1-5:   DETAILED REVIEW (consumed attention)                  ||
    ||  Files 10-14: SHALLOW REVIEW (attention exhausted)                  ||
    ||                                                                      ||
    ||  Result: Critical bugs MISSED in files 10-14!                       ||
    +======================================================================+

    +======================================================================+
    ||  AFTER: Multi-Pass (Architectural Fix)                              ||
    ||                                                                      ||
    ||  PASS 1: Each file gets FULL attention                             ||
    ||  -------------------------------------------------------------      ||
    ||  File 1:  100% attention --> Thorough review                       ||
    ||  File 2:  100% attention --> Thorough review                       ||
    ||  File 14: 100% attention --> Thorough review <-- Now covered!       ||
    ||                                                                      ||
    ||  PASS 2: Cross-file integration                                    ||
    ||  -------------------------------------------------------------      ||
    ||  - Check relationships between all files                            ||
    ||  - Find issues that span multiple files                             ||
    ||                                                                      ||
    ||  Result: All files get EQUAL attention! Critical bugs caught!        ||
    +======================================================================+
    """)


def show_implementation():
    """
    Show the implementation pattern.
    """
    print("\n" + "=" * 70)
    print("IMPLEMENTATION PATTERN")
    print("=" * 70)

    print("""
    +======================================================================+
    ||  CODE PATTERN:                                                      ||
    ||                                                                      ||
    ||  def multi_pass_review(files):                                      ||
    ||                                                                      ||
    ||      # PASS 1: Local Analysis                                       ||
    ||      # Each file gets FULL attention                                 ||
    ||      local_results = []                                             ||
    ||      for file in files:                                             ||
    ||          result = analyze_file(file, full_context=file)             ||
    ||          local_results.append(result)                                ||
    ||                                                                      ||
    ||      # PASS 2: Integration                                          ||
    ||      # Check cross-file issues                                      ||
    ||      integration_issues = check_relationships(local_results)         ||
    ||                                                                      ||
    ||      return combine_results(local_results, integration_issues)       ||
    ||                                                                      ||
    ||  KEY: For loop with full context per item,                          ||
    ||       not one call with all items!                                  ||
    +======================================================================+
    """)


def show_real_time_mistakes():
    """
    Shows REAL mistakes developers make with multi-pass.
    """
    print("\n" + "=" * 70)
    print("REAL MISTAKES DEVELOPERS MAKE - EXPERT WARNINGS")
    print("=" * 70)

    print("""
    +======================================================================+
    ||                                                                      ||
    ||  MISTAKE #1: Using single pass and calling it "multi-pass"          ||
    ||  =================================================================   ||
    ||                                                                      ||
    ||  WHAT HAPPENS:                                                       ||
    ||  - Developer says "I loop over files" but doesn't give full context ||
    ||  - Each file still gets diluted attention                           ||
    ||  - "I used a loop so it's multi-pass!"                              ||
    ||                                                                      ||
    ||  REAL CONSEQUENCE:                                                   ||
    ||  - Still has attention dilution                                      ||
    ||  - But developer thinks they're protected                            ||
    ||  - Critical bugs still missed                                        ||
    ||                                                                      ||
    ||  CORRECT APPROACH:                                                   ||
    ||  - Each iteration: FULL context for ONE file                        ||
    ||  - Not: partial context for all files                               ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  MISTAKE #2: Skipping the integration pass                          ||
    ||  =================================================================   ||
    ||                                                                      ||
    ||  WHAT HAPPENS:                                                       ||
    ||  - Developer implements Pass 1 (local analysis)                     ||
    ||  - Skips Pass 2 (integration) to save time                         ||
    ||  - Cross-file issues are MISSED                                     ||
    ||                                                                      ||
    ||  REAL CONSEQUENCE:                                                   ||
    ||  - Auth uses MD5 (file 1, caught in Pass 1)                        ||
    ||  - DB stores plaintext (file 2, caught in Pass 1)                   ||
    ||  - But exploit path across files is NOT found (Pass 2 missing!)      ||
    ||                                                                      ||
    ||  CORRECT APPROACH:                                                   ||
    ||  - ALWAYS run integration pass                                      ||
    ||  - Integration finds cross-file patterns                            ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  MISTAKE #3: Using multi-pass for single-item tasks                 ||
    ||  =================================================================   ||
    ||                                                                      ||
    ||  WHAT HAPPENS:                                                       ||
    ||  - Developer uses multi-pass for 1 file review                       ||
    ||  - Pass 2 (integration) has nothing to integrate                    ||
    ||  - Over-engineering, unnecessary complexity                          ||
    ||                                                                      ||
    ||  CORRECT APPROACH:                                                   ||
    ||  - Multi-pass for MULTIPLE items (many files, many docs)             ||
    ||  - Single pass for ONE item (1 file, 1 doc)                        ||
    ||                                                                      ||
    +======================================================================+
    """)


def show_interview_qa():
    """
    Shows common interview questions and expert answers.
    """
    print("\n" + "=" * 70)
    print("INTERVIEW QUESTIONS & EXPERT ANSWERS GUIDE")
    print("=" * 70)

    # Q1
    print("""
    ======================================================================
    INTERVIEW Q1: "How does multi-pass fix attention dilution?"
    ======================================================================

    EXPECTED ANSWER:
    Pass 1: Loop over each item individually, giving FULL attention to each
    one. Unlike single-pass that divides attention across all items, multi-pass
    ensures File 50 gets the same attention as File 1. Pass 2: After all local
    passes complete, run an integration pass to find cross-item relationships
    and patterns that span multiple files.

    RED FLAGS IN ANSWERS:
    - "It doesn't, use a better model" -> Wrong (architectural)
    - "Loop over items" -> Doesn't explain full context per item
    - "Single pass with larger context" -> Still dilutes attention

    +-----------------------------------------------------------------------+
    | EXPERT TIP: Emphasize BOTH passes                                     |
    | "Pass 1: each item gets full attention. Pass 2: cross-item check"    |
    +-----------------------------------------------------------------------+
    """)

    # Q2
    print("""
    ======================================================================
    INTERVIEW Q2: "What's the difference between batching and multi-pass?"
    ======================================================================

    EXPECTED ANSWER:
    Batching splits items into groups but still uses single-pass per group.
    Multi-pass gives each item its OWN pass with full attention. Batch of 10
    items still has attention dilution within the batch. Multi-pass ensures
    every single item gets equal focus. Also, batching often skips the
    integration pass, missing cross-file issues.

    +-----------------------------------------------------------------------+
    | EXPERT TIP: "Batching = same problem, smaller batches.                |
    | Multi-pass = different architecture, solves the problem."             |
    +-----------------------------------------------------------------------+
    """)

    # Q3
    print("""
    ======================================================================
    INTERVIEW Q3: "When should you NOT use multi-pass?"
    ======================================================================

    EXPECTED ANSWER:
    Multi-pass is overkill for single-item tasks. If you're reviewing one
    file, one document, or one endpoint, just do a single thorough pass.
    Multi-pass is for when you have MANY items needing equal attention.
    For single items, the overhead of multiple passes isn't justified.

    +-----------------------------------------------------------------------+
    | EXPERT TIP: "Multi-pass solves attention dilution with multiple      |
    | items. For single items, single pass is sufficient."                 |
    +-----------------------------------------------------------------------+
    """)


def show_decision_flowchart():
    """
    Show decision flowchart for when to use multi-pass.
    """
    print("\n" + "=" * 70)
    print("VISUAL: WHEN TO USE MULTI-PASS")
    print("=" * 70)

    print("""
                      +--------------------+
                      |  Reviewing multiple|
                      |  items (files,     |
                      |  docs, endpoints)?  |
                      +--------------------+
                               |
                               v
                    +---------------------+
                    | Need EQUAL attention  |
                    | for all items?        |
                    +---------------------+
                          /        \\
                         /          \\
                        v            v
                      YES           NO
                       |              |
                       v              |
    +----------------------+           |
    | WRONG: Single pass  |           |
    | (attention dilutes) |           |
    +----------------------+           |
                       |              |
                       v              |
    +----------------------+           |
    | CORRECT: Multi-pass  |          |
    +----------------------+           |
           |                          |
           v                          v
    +----------------------+    [Single pass OK]
    | PASS 1: Loop items   |
    | (full attention ea)  |
    +----------------------+
           |
           v
    +----------------------+
    | PASS 2: Integration  |
    | (cross-item check)   |
    +----------------------+
    """)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("""
+===========================================================================+
|                                                                           |
|  PRACTICE 5: MULTI-PASS ARCHITECTURE                                     |
|  + REAL-TIME SCENARIOS + MISTAKES + INTERVIEW Q&A + VISUALS             |
|                                                                           |
|  This program teaches:                                                   |
|  1. How multi-pass fixes attention dilution                              |
|  2. Real production scenarios                                           |
|  3. Common mistakes and how to avoid them                                |
|  4. Interview Q&A with expert answer frameworks                         |
|                                                                           |
+===========================================================================+
    """)

    demonstrate_multi_pass()
    show_before_after()
    show_implementation()
    show_real_time_mistakes()
    show_interview_qa()
    show_decision_flowchart()

    print("\n" + "=" * 70)
    print("WHAT WE HAVE LEARNT")
    print("=" * 70)
    print("""
    +======================================================================+
    ||  1. HOW MULTI-PASS FIXES ATTENTION DILUTION:                       ||
    ||                                                                      ||
    ||  PASS 1: Per-item local analysis                                    ||
    ||  - Loop over each item individually                                 ||
    ||  - Each item gets FULL attention (100%)                             ||
    ||  - File 50 gets same review quality as File 1                       ||
    ||                                                                      ||
    ||  PASS 2: Cross-item integration                                     ||
    ||  - After all local passes complete                                  ||
    ||  - Check relationships between items                                ||
    ||  - Find cross-file patterns and vulnerabilities                     ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  2. REAL-TIME SCENARIOS:                                           ||
    ||                                                                      ||
    ||  SCENARIO 1: Security Audit                                         ||
    ||  - 50 files reviewed                                                ||
    ||  - Pass 1: File 50 gets full attention (NOT SHALLOW!)              ||
    ||  - Pass 2: Auth MD5 + DB plaintext = exploit path found             ||
    ||                                                                      ||
    ||  SCENARIO 2: Documentation Consistency                              ||
    ||  - 30 API endpoints documented                                      ||
    ||  - Pass 1: Each endpoint gets equal documentation                   │
    ||  - Pass 2: Cross-endpoint patterns checked                          ||
    ||                                                                      ||
    ||  SCENARIO 3: Bug Hunt                                               ||
    ||  - 20 files in crash path                                           ||
    ||  - Pass 1: Root cause in file 18 found (would be missed!)           │
    ||  - Pass 2: Complete crash path mapped                               ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  3. COMMON MISTAKES (EXPERT WARNINGS):                             ||
    ||                                                                      ||
    ||  MISTAKE #1: "Loop over items" without full context per item         ||
    ||  - Still has attention dilution                                     ||
    ||  - FIX: Full context for ONE item per iteration                      ||
    ||                                                                      ||
    ||  MISTAKE #2: Skipping integration pass                               ||
    ||  - Cross-file issues are missed                                      ||
    ||  - FIX: ALWAYS run integration pass                                 ||
    ||                                                                      ||
    ||  MISTAKE #3: Multi-pass for single-item tasks                       ||
    ||  - Over-engineering                                                 ||
    ||  - FIX: Multi-pass for multiple items, single for one               ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  4. INTERVIEW TIPS:                                                ||
    ||                                                                      ||
    ||  - Multi-pass = Pass 1 (local) + Pass 2 (integration)               ||
    ||  - Batching != Multi-pass (still has dilution)                      ||
    ||  - NOT for single items (overkill)                                   ||
    ||                                                                      ||
    ||  EXPECTED ANSWER STRUCTURE:                                          ||
    ||  1. What attention dilution is (architectural problem)              ||
    ||  2. How Pass 1 fixes it (full attention per item)                   ||
    ||  3. Why Pass 2 is needed (cross-item relationships)                ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  5. KEY RULES TO MEMORIZE:                                         ||
    ||                                                                      ||
    ||  RULE #1: Many items needing equal attention? -> Multi-pass          ||
    ||  RULE #2: Pass 1 = loop with full context per item                  ||
    ||  RULE #3: Pass 2 = integration for cross-item issues               ||
    ||  RULE #4: Batching is NOT multi-pass (still dilutes attention)     ||
    ||                                                                      ||
    +======================================================================+

    Next: TEMPLATE.py provides a reusable template for implementing
    these patterns in your own code!
    """)


"""
+===========================================================================+
|                                                                           |
|  KEY CONCEPTS FROM THIS FILE:                                           |
|                                                                           |
|  MULTI-PASS ARCHITECTURE:                                                |
|  - Pass 1: Each item gets FULL attention (loop with full context)         |
|  - Pass 2: Cross-item integration (relationships, patterns)              |
|                                                                           |
|  FIXES ATTENTION DILUTION:                                              |
|  - Single pass: File 50 gets diluted attention                          |
|  - Multi-pass: File 50 gets 100% attention                              |
|                                                                           |
|  MISTAKES TO AVOID:                                                     |
|  - Loop without full context (still dilutes)                              |
|  - Skipping integration pass (miss cross-file issues)                    |
|  - Multi-pass for single items (overkill)                                |
|                                                                           |
|  EXAM TIPS:                                                              |
|  - Multi-pass = local + integration                                      |
|  - Batching != Multi-pass                                                |
|  - NOT for single items                                                  |
|                                                                           |
|  INTERVIEW PREP:                                                        |
|  - "How does multi-pass fix attention dilution?"                        |
|  - "What's the difference between batching and multi-pass?"             |
|  - "When should you NOT use multi-pass?"                                 |
|                                                                           |
+===========================================================================+
"""