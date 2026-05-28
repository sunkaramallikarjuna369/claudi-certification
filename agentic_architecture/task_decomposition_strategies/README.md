"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║           TASK DECOMPOSITION STRATEGIES                                 ║
║                                                                              ║
║  How to Break Down Complex Tasks for Agentic Systems                      ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

TWO CORE PATTERNS
═══════════════════

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   PATTERN 1: FIXED SEQUENTIAL PIPELINE                               │
    │   ────────────────────────────────────────────────                   │
    │                                                                         │
    │   Work breaks into PREDETERMINED steps executed in ORDER            │
    │   Each step takes previous output as input                            │
    │                                                                         │
    │   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐      │
    │   │ Step 1  │───>│ Step 2  │───>│ Step 3  │───>│ Step 4  │      │
    │   │ Extract  │    │Transform│    │Validate │    │  Load   │      │
    │   │   PDF    │    │  Data   │    │ Schema  │    │   DB    │      │
    │   └─────────┘    └─────────┘    └─────────┘    └─────────┘      │
    │       │              │              │              │                │
    │       ▼              ▼              ▼              ▼                │
    │   PDF Text      Cleaned CSV    Schema OK     Success!            │
    │                                                                         │
    │   Best for: Predictable, structured tasks                           │
    │   Examples: Code review, document processing, compliance checks    │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   PATTERN 2: DYNAMIC ADAPTIVE DECOMPOSITION                         │
    │   ─────────────────────────────────────────────────                   │
    │                                                                         │
    │   Subtasks GENERATED based on discoveries                            │
    │   Plan EVOLVES as agent learns more about the problem               │
    │                                                                         │
    │                         ┌─────────┐                                │
    │                         │  START  │                                │
    │                         └────┬────┘                                │
    │                              │                                      │
    │                              ▼                                      │
    │                    ┌─────────────────┐                            │
    │                    │   Analyze       │                            │
    │                    │  Discovery #1    │                            │
    │                    └────────┬─────────┘                            │
    │                             │                                      │
    │              ┌─────────────┼─────────────┐                        │
    │              │             │             │                        │
    │              ▼             ▼             ▼                        │
    │         ┌────────┐   ┌────────┐   ┌────────┐                  │
    │         │Subtask │   │Subtask │   │Subtask │                  │
    │         │   A    │   │   B    │   │   C    │                  │
    │         └────┬───┘   └────┬───┘   └────┬───┘                  │
    │              │             │             │                        │
    │              └─────────────┼─────────────┘                        │
    │                            ▼                                      │
    │                    ┌─────────────────┐                            │
    │                    │   Analyze       │                            │
    │                    │  Discovery #2   │                            │
    │                    └────────┬─────────┘                            │
    │                             │                                      │
    │                             ▼                                      │
    │                    ┌─────────────────┐                            │
    │                    │ NEW SUBTASKS!   │ ← Surprises emerge!       │
    │                    └─────────────────┘                            │
    │                                                                         │
    │   Best for: Open-ended investigation, security audits              │
    │   Examples: Legacy system exploration, debugging unfamiliar code  │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘


SELECTION GUIDE
═════════════════

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   TASK CHARACTERISTICS              │         USE THIS PATTERN         │
    │   ─────────────────────────────────┼────────────────────────────────  │
    │                                                                         │
    │   Steps known in advance            │  FIXED PIPELINE                │
    │   Predictable workflow               │  Sequential steps               │
    │   Structured input/output           │  Easy to test each step        │
    │   Audit trail needed               │  Clear checkpoints             │
    │                                                                         │
    ├────────────────────────────────────┼────────────────────────────────┤
    │                                                                         │
    │   Open-ended, unknown scope         │  DYNAMIC DECOMPOSITION          │
    │   Discovery-driven                  │  Subtasks emerge                │
    │   Unexpected findings possible      │  Adapts to complexity         │
    │   Thoroughness over speed          │  Follow the evidence           │
    │                                                                         │
    └────────────────────────────────────┴────────────────────────────────┘


ATTENTION DILUTION PROBLEM
═══════════════════════════

    When analyzing many items, attention gets spread thin.
    Early items get detailed focus, later items get shallow treatment.

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   PROBLEM: Model allocates attention across ALL items                    │
    │                                                                         │
    │   When reviewing 14 files in one pass:                                 │
    │                                                                         │
    │   FILE 1   ████████████████████████████████ DETAILED                  │
    │   FILE 2   ████████████████████████████████ DETAILED                  │
    │   FILE 3   ████████████████████████████████ DETAILED                  │
    │   FILE 4   ████████████████████████████████ DETAILED                  │
    │   FILE 5   ████████████████████████████████ DETAILED                  │
    │   FILE 6   ██████████████████████████ MODERATE                       │
    │   FILE 7   ██████████████████████████ MODERATE                       │
    │   FILE 8   ████████████████████ SHAKING                            │
    │   FILE 9   ████████████████████ SHAKING                            │
    │   FILE 10  ████████████████ MINIMAL                                 │
    │   FILE 11  ████████████████ MINIMAL                                 │
    │   FILE 12  ████████████ SHALLOW                                     │
    │   FILE 13  ████████████ SHALLOW                                     │
    │   FILE 14  ████████ VERY SHALLOW                                    │
    │                                                                         │
    │   Later files get progressively less attention!                       │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘


ATTENTION DILUTION SYMPTOMS
════════════════════════════

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   SYMPTOM 1: Detailed feedback for first files, shallow for later     │
    │   ───────────────────────────────────────────────────────────          │
    │   "Files 1-5 have thorough reviews with specific suggestions"           │
    │   "Files 10-14 have generic comments like 'looks good'"                │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   SYMPTOM 2: Inconsistent pattern detection                           │
    │   ──────────────────────────────────────────────────                   │
    │   "Same pattern flagged problematic in File 3"                         │
    │   "Same pattern approved in File 11"                                   │
    │   Model attention was diluted when it reached File 11!                │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   SYMPTOM 3: Critical bugs missed, minor issues caught                │
    │   ──────────────────────────────────────────────────────              │
    │   "File 14 has NULL POINTER BUG that causes crash" ← MISSED!         │
    │   "File 1 has minor style issue" ← CAUGHT!                          │
    │   Attention exhausted before reaching critical bug!                   │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘


REAL EXAMPLE: 14-FILE CODE REVIEW
══════════════════════════════════

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   SCENARIO: Code review 14 files in one pass                          │
    │                                                                         │
    │   EXPECTED: All files get same level of scrutiny                       │
    │   ACTUAL:                                                                │
    │                                                                         │
    │   Files 1-5: DETAILED REVIEW                                          │
    │     ✓ Found null pointer risks                                         │
    │     ✓ Found SQL injection vulnerabilities                             │
    │     ✓ Detailed suggestions for improvements                            │
    │                                                                         │
    │   Files 10-14: SHALLOW REVIEW                                        │
    │     ✗ Missed null pointer bug (causes production crash!)              │
    │     ✗ Missed SQL injection vulnerability                               │
    │     ✗ Only checked minor style issues                                  │
    │                                                                         │
    │   ROOT CAUSE: Attention was allocated across all 14 files              │
    │   Early files consumed the attention budget                           │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘


WRONG FIXES (EXAM TRAPS!)
══════════════════════════

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   WRONG FIX #1: Use a more powerful model                             │
    │   ────────────────────────────────────────────                         │
    │   "Let's use Claude Opus instead of Sonnet for better results"         │
    │                                                                         │
    │   WHY IT'S WRONG:                                                      │
    │   Attention dilution is ARCHITECTURAL, not capability-related!        │
    │   More powerful model still has same attention allocation              │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   WRONG FIX #2: Use larger context window                              │
    │   ────────────────────────────────────────────                         │
    │   "Let's increase max_tokens to handle more files"                    │
    │                                                                         │
    │   WHY IT'S WRONG:                                                      │
    │   Larger context = more items to review                                │
    │   More items = more diluted attention                                  │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   WRONG FIX #3: Write better prompts                                  │
    │   ────────────────────────────────────────────                         │
    │   "Let's add more detailed instructions for thorough review"           │
    │                                                                         │
    │   WHY IT'S WRONG:                                                      │
    │   Better prompts improve AVERAGE quality                              │
    │   But they don't solve ATTENTION ALLOCATION                            │
    │   Later items still get less attention!                                │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   WRONG FIX #4: Batch without integration pass                        │
    │   ────────────────────────────────────────────────                     │
    │   "Let's batch files 1-7 and 8-14 separately"                          │
    │                                                                         │
    │   WHY IT'S WRONG:                                                      │
    │   Still misses CROSS-CUTTING issues                                    │
    │   Batching alone doesn't solve cross-file attention                    │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘


CORRECT FIX: MULTI-PASS ARCHITECTURE
═════════════════════════════════════

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   SOLUTION: Separate local analysis from cross-item integration        │
    │                                                                         │
    │   ┌─────────────────────────────────────────────────────────────┐    │
    │   │  PASS 1: Per-Item Local Analysis                            │    │
    │   │                                                             │    │
    │   │  Each file gets FULL attention budget:                      │    │
    │   │                                                             │    │
    │   │  File 1  ──> Full analysis, full attention                │    │
    │   │  File 2  ──> Full analysis, full attention                │    │
    │   │  File 3  ──> Full analysis, full attention                │    │
    │   │  ...                                                    │    │
    │   │  File 14 ──> Full analysis, full attention                │    │
    │   │                                                             │    │
    │   │  Each file gets the SAME quality of review!               │    │
    │   └─────────────────────────────────────────────────────────────┘    │
    │                              │                                       │
    │                              ▼                                       │
    │   ┌─────────────────────────────────────────────────────────────┐    │
    │   │  PASS 2: Cross-Item Integration                            │    │
    │   │                                                             │    │
    │   │  After all local passes complete:                          │    │
    │   │  • Check for data flow consistency                         │    │
    │   │  • Check for pattern consistency across files               │    │
    │   │  • Check for dependency issues                            │    │
    │   │  • Check for cross-cutting security concerns                │    │
    │   │                                                             │    │
    │   │  Now ALL files have been analyzed thoroughly               │    │
    │   │  Integration can check relationships between them          │    │
    │   └─────────────────────────────────────────────────────────────┘    │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘

    WHY THIS WORKS:
    ───────────────
    BEFORE (single pass):
        14 files ÷ attention budget = diluted per file

    AFTER (multi-pass):
        14 passes × full attention = equally thorough per file
        + 1 integration pass for cross-file issues

    Result:
        ✓ All files get full attention
        ✓ Cross-cutting issues are caught
        ✓ No critical bugs missed in later files


WHAT THIS FOLDER COVERS
════════════════════════

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   practice_01_two_core_patterns.py                                     │
    │   ├─ Fixed Sequential Pipeline vs Dynamic Adaptive Decomposition        │
    │   └─ When to use each based on task characteristics                   │
    │                                                                         │
    │   practice_02_attention_dilution.py                                     │
    │   ├─ The attention dilution problem                                     │
    │   ├─ Symptoms and real-world example                                  │
    │   └─ Why architectural fix is needed (not better model)               │
    │                                                                         │
    │   practice_03_fixed_pipeline.py                                         │
    │   ├─ Implementation of fixed sequential pipeline                      │
    │   └─ Benefits: predictable, debuggable, monitorable                   │
    │                                                                         │
    │   practice_04_dynamic_decomposition.py                                  │
    │   ├─ Dynamic adaptive decomposition with emerging subtasks              │
    │   └─ How to handle open-ended investigation                            │
    │                                                                         │
    │   practice_05_multi_pass_architecture.py                                 │
    │   ├─ Multi-pass architecture: local + integration passes               │
    │   └─ The correct fix for attention dilution                            │
    │                                                                         │
    │   TEMPLATE.py                                                         │
    │   └─ Starting template with all three patterns                         │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘

"""

# ═══════════════════════════════════════════════════════════════════════════
# KEY CONCEPTS SUMMARY
# ═══════════════════════════════════════════════════════════════════════════

"""
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   TWO CORE PATTERNS:                                                    │
│                                                                         │
│   FIXED PIPELINE: Steps known in advance → Execute in order            │
│   DYNAMIC: Subtasks emerge from discoveries → Adapts                  │
│                                                                         │
│   ─────────────────────────────────────────────────────────────────────  │
│                                                                         │
│   ATTENTION DILUTION:                                                  │
│   • Model allocates attention across ALL items                         │
│   • Early items get detailed focus, later items get shallow           │
│   • Critical bugs missed in later files!                              │
│                                                                         │
│   ─────────────────────────────────────────────────────────────────────  │
│                                                                         │
│   CORRECT FIX FOR ATTENTION DILUTION:                                  │
│   • Multi-pass architecture                                            │
│   • Pass 1: Per-item local analysis (full attention per item)         │
│   • Pass 2: Cross-item integration (check relationships)               │
│                                                                         │
│   ─────────────────────────────────────────────────────────────────────  │
│                                                                         │
│   EXAM TRAPS:                                                          │
│   • "More powerful model" = WRONG (architectural, not capability)    │
│   • "Better prompts" = WRONG (improves average, not allocation)       │
│   • "Batching without integration" = WRONG (misses cross-file)        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
"""