"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║           ERROR RECOVERY & RESILIENCE                                      ║
║                                                                              ║
║  Session Management, Stale Context, and Recovery Patterns                   ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

WHY ERROR RECOVERY MATTERS
════════════════════════════

    In real-world agentic systems, things go wrong:

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   SITUATIONS THAT REQUIRE RECOVERY:                                  │
    │                                                                         │
    │   • Session interrupted (crash, timeout, user left)                  │
    │   • Files modified during agent work                                  │
    │   • Dependencies updated                                              │
    │   • Long session with cluttered history                               │
    │   • Agent gave contradictory advice                                   │
    │                                                                         │
    │   Without proper recovery, agents work with STALE context             │
    │   and produce WRONG outputs!                                          │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘


THREE SESSION MANAGEMENT APPROACHES
══════════════════════════════════

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   APPROACH 1: --resume <session-name>                                │
    │   ───────────────────────────────────────────────                     │
    │                                                                         │
    │   What it does:                                                      │
    │   • Restores COMPLETE conversation history                             │
    │   • Includes ALL tool results from previous session                  │
    │   • Agent has context of everything that happened                   │
    │                                                                         │
    │   When to use:                                                       │
    │   ✓ Prior context remains VALID                                        │
    │   ✓ No files have changed since last session                        │
    │   ✓ Need to continue exact work from where you left off            │
    │                                                                         │
    │   When to avoid:                                                     │
    │   ✗ Files have been modified since last session                      │
    │   ✗ Long session with cluttered history                             │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   APPROACH 2: fork_session                                            │
    │   ────────────────────────────────────                               │
    │                                                                         │
    │   What it does:                                                      │
    │   • Creates INDEPENDENT branches from current state                     │
    │   • Each branch operates SEPARATELY                                    │
    │   • Changes in one branch do NOT affect the other                   │
    │                                                                         │
    │   When to use:                                                       │
    │   ✓ Exploring DIVERGENT approaches                                   │
    │   ✓ A/B testing different strategies                                  │
    │   ✓ Want to try approach A AND approach B simultaneously            │
    │                                                                         │
    │   When to avoid:                                                     │
    │   ✗ Just want to continue the same line of investigation            │
    │   ✗ Session has stale context (fork inherits it!)                    │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   APPROACH 3: Fresh Start + Summary Injection                        │
    │   ───────────────────────────────────────────────────                │
    │                                                                         │
    │   What it does:                                                      │
    │   • Starts a COMPLETELY NEW session                                 │
    │   • NO stale tool results in history                                   │
    │   • Curated knowledge transfers via structured summary              │
    │   • Clean slate with important context                              │
    │                                                                         │
    │   When to use:                                                       │
    │   ✓ Files have CHANGED since last session                          │
    │   ✓ Long session with cluttered history                             │
    │   ✓ Dependency updates since last session                           │
    │   ✓ Need to move forward without stale data                         │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘


THE STALE CONTEXT PROBLEM
═══════════════════════════

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   THE CENTRAL CONCEPT:                                                │
    │                                                                         │
    │   Stale context occurs when an agent resumes a session after         │
    │   code modifications and reasons from cached tool results that        │
    │   no longer reflect the current state of files.                       │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘

    HOW IT MANIFESTS:

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   DAY 1: Initial Analysis                                             │
    │   ─────────────────────────────────────────────────────              │
    │   • Agent reads auth.ts → finds: "Uses MD5 for hashing"            │
    │   • Tool result stored: "File auth.ts: uses MD5 hashing"           │
    │                                                                         │
    │   User implements the fix (changes auth.ts to use bcrypt)           │
    │                                                                         │
    │   DAY 2: Resume Session                                             │
    │   ─────────────────────────────────────────────────────              │
    │   • Tool result says: "auth.ts uses MD5" ← STALE!                  │
    │   • Fresh read says: "auth.ts uses bcrypt" ← CURRENT!              │
    │   • Agent gets CONFLICTED information                                │
    │   • Gives CONTRADICTORY advice                                       │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘

    WHY IT HAPPENS:

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   When resuming, the ENTIRE conversation history is restored,          │
    │   including every tool result.                                        │
    │                                                                         │
    │   If a file was read during the previous session and has since       │
    │   been modified, the OLD file contents remain as a tool result.       │
    │                                                                         │
    │   The model reasons from that stale data ALONGSIDE new data.        │
    │                                                                         │
    │   Result: Contradictions, confusion, wrong outputs!                 │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘


REAL EXAMPLE: THE CONTRADICTORY ADVICE BUG
══════════════════════════════════════════

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   SCENARIO: 50-file codebase analyzed over two days                   │
    │                                                                         │
    │   DAY 1:                                                                  │
    │   • Identified three authentication issues                            │
    │   • Found in auth.ts, session.ts, middleware.ts                     │
    │   • Tool results stored in conversation history                      │
    │                                                                         │
    │   OVERNIGHT: User fixes all three issues                              │
    │   • Modified auth.ts, session.ts, middleware.ts                      │
    │                                                                         │
    │   DAY 2: Resume Session                                               │
    │   ─────────────────────────────────────────────────────              │
    │                                                                         │
    │   USER: "Continue the analysis"                                        │
    │                                                                         │
    │   CLAUDE: "You have three authentication issues to fix:              │
    │   1. auth.ts uses MD5 hashing - UPGRADE TO BCRYPT"                  │
    │   2. session.ts has weak token validation - ADD RSA SIGNATURES"        │
    │   3. middleware.ts doesn't validate tokens - ADD VALIDATION"         │
    │                                                                         │
    │   PROBLEM: All three issues were already fixed!                       │
    │                                                                         │
    │   ROOT CAUSE: Old tool results still in conversation history!        │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘


THE NAIVE FIX (INSUFFICIENT)
═══════════════════════════════

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   WHAT MANY DEVELOPERS DO:                                             │
    │   ─────────────────────────────────────                               │
    │                                                                         │
    │   $ claude --resume session                                        │
    │   > "auth.ts has been modified, re-read it please"                  │
    │                                                                         │
    │   WHY IT'S INSUFFICIENT:                                             │
    │   ────────────────────────────                                       │
    │   • Stale tool results still in conversation history                 │
    │   • Model may still reference old information                        │
    │   • Contradictory advice may still occur                            │
    │   • The stale data is NOT cleared by re-reading files!              │
    │                                                                         │
    │   The model sees BOTH:                                              │
    │   • Old tool result: "auth.ts uses MD5"                             │
    │   • Fresh read: "auth.ts uses bcrypt"                               │
    │   • Still confused about which is current state                      │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘


THE CORRECT FIX: TARGETED RE-ANALYSIS
════════════════════════════════════════

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   THE CORRECT APPROACH:                                               │
    │   ────────────────────────                                            │
    │                                                                         │
    │   1. Start a FRESH session                                           │
    │   2. Inject structured SUMMARY of prior findings                     │
    │   3. Specify WHICH files have changed                                 │
    │   4. Agent re-analyzes only modified files                           │
    │                                                                         │
    │   ────────────────────────────────────────────────────────────────── │
    │                                                                         │
    │   NO stale tool results in the new session!                         │
    │   Prior knowledge preserved via the summary injection!              │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘

    STEP-BY-STEP:

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   STEP 1: Start fresh session                                         │
    │   ─────────────────────────────────────                             │
    │   $ claude --session day2-analysis  # NEW, not resumed!              │
    │                                                                         │
    │   ────────────────────────────────────────────────────────────────── │
    │                                                                         │
    │   STEP 2: Inject structured summary                                    │
    │   ──────────────────────────────────────────                         │
    │                                                                         │
    │   "Prior analysis (Day 1) identified three authentication issues:    │
    │    - auth.ts: Used MD5 hashing                                       │
    │    - session.ts: Weak token validation                               │
    │    - middleware.ts: Missing token validation                          │
    │                                                                         │
    │   FIXES IMPLEMENTED:                                                   │
    │    - auth.ts: Changed MD5 -> bcrypt                                 │
    │    - session.ts: Added RSA signatures                                │
    │    - middleware.ts: Added token validation                          │
    │                                                                         │
    │   ────────────────────────────────────────────────────────────────── │
    │                                                                         │
    │   STEP 3: Specify changed files                                       │
    │   ─────────────────────────────────────                             │
    │                                                                         │
    │   "Modified files: auth.ts, session.ts, middleware.ts               │
    │    Please re-analyze these three files to verify fixes."            │
    │                                                                         │
    │   ────────────────────────────────────────────────────────────────── │
    │                                                                         │
    │   STEP 4: Agent re-analyzes only modified files                     │
    │   ───────────────────────────────────────────────────                 │
    │   Agent reads fresh auth.ts → confirms bcrypt fix ✓                  │
    │   Agent reads fresh session.ts → confirms RSA signatures ✓           │
    │   Agent reads fresh middleware.ts → confirms validation ✓             │
    │                                                                         │
    │   Result: Complete, current, accurate analysis!                       │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘


TARGETED RE-ANALYSIS vs FULL RE-EXPLORATION
══════════════════════════════════════════

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   WRONG: Full re-exploration                                           │
    │   ────────────────────────────────────                                │
    │                                                                         │
    │   "Re-analyze the entire 50-file codebase"                            │
    │                                                                         │
    │   Problems:                                                            │
    │   ✗ Wasteful - only 3 files changed                                   │
    │   ✗ Takes too long                                                    │
    │   ✗ May miss important context from prior analysis                    │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   RIGHT: Targeted re-analysis                                          │
    │   ──────────────────────────────────                                   │
    │                                                                         │
    │   "Prior analysis identified issues in these 3 files.                  │
    │    These files have been modified. Re-analyze only them.              │
    │    Trust prior findings for the other 47 files."                      │
    │                                                                         │
    │   Benefits:                                                            │
    │   ✓ Fast - only re-analyze changed files                               │
    │   ✓ Reliable - no stale context                                        │
    │   ✓ Efficient - preserves knowledge without stale data                │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘


DECISION MATRIX
══════════════════

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   SCENARIO                              │  BEST APPROACH                  │
    │   ─────────────────────────────────────┼────────────────────────────────│
    │                                                                         │
    │   Continuing work from yesterday,       │  --resume                     │
    │   no files changed                      │  (Full history still valid)    │
    │                                                                         │
    ├────────────────────────────────────────┼────────────────────────────────│
    │                                                                         │
    │   Comparing two refactoring             │  fork_session                 │
    │   approaches (microservices vs          │  (Independent branches)        │
    │   monolith)                             │                               │
    │                                                                         │
    ├────────────────────────────────────────┼────────────────────────────────│
    │                                                                         │
    │   Resuming after modifying 3 of        │  Fresh start + summary        │
    │   50 files                              │  (Only modified files need     │
    │                                        │   re-analysis)                 │
    │                                                                         │
    ├────────────────────────────────────────┼────────────────────────────────│
    │                                                                         │
    │   Long session with cluttered          │  Fresh start + summary        │
    │   history                              │  (Start clean, inject         │
    │                                        │   knowledge)                   │
    │                                                                         │
    ├────────────────────────────────────────┼────────────────────────────────│
    │                                                                         │
    │   Testing strategy vs documentation    │  fork_session                 │
    │   strategy                             │  (Exploring alternatives)    │
    │                                                                         │
    ├────────────────────────────────────────┼────────────────────────────────│
    │                                                                         │
    │   Resuming after dependency            │  Fresh start + summary        │
    │   updates                               │  (Need fresh analysis of      │
    │                                        │   dependency impact)          │
    │                                                                         │
    └────────────────────────────────────────┴────────────────────────────────┘


EXAM TRAPS TO AVOID
═════════════════════

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   TRAP 1: Full re-exploration                                          │
    │   ────────────────────────────────────                                │
    │                                                                         │
    │   When only 3 files changed, using full re-exploration is wasteful.    │
    │   Inform the agent about specific changes instead.                     │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   TRAP 2: Resume after modifications                                   │
    │   ────────────────────────────────────────                             │
    │                                                                         │
    │   Resuming preserves stale tool results. The agent may reason from    │
    │   outdated file contents.                                              │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   TRAP 3: Confusing fork_session with --resume                       │
    │   ──────────────────────────────────────────────────────               │
    │                                                                         │
    │   Fork creates branches for exploring different approaches;           │
    │   resume continues the same conversation.                             │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   TRAP 4: Using fork_session for stale context                        │
    │   ────────────────────────────────────────────────                   │
    │                                                                         │
    │   Fork branches from the existing session, which still contains       │
    │   stale tool results. The fork INHERITS the stale context!           │
    │                                                                         │
    │   If context is stale, use fresh start + summary, NOT fork!            │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘


WHAT THIS FOLDER COVERS
════════════════════════

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   practice_01_session_management_approaches.py                         │
    │   ├─ Three approaches: --resume, fork_session, fresh start + summary    │
    │   └─ When to use each based on scenario                               │
    │                                                                         │
    │   practice_02_stale_context_problem.py                                │
    │   ├─ The stale context problem explained                              │
    │   ├─ Contradictory advice bug                                         │
    │   └─ Why naive fix fails                                             │
    │                                                                         │
    │   practice_03_targeted_reanalysis.py                                    │
    │   ├─ The correct fix: fresh start + summary injection                  │
    │   ├─ Step-by-step pattern                                            │
    │   └─ Targeted vs full re-exploration                                  │
    │                                                                         │
    │   practice_04_decision_matrix.py                                      │
    │   ├─ Decision matrix for all scenarios                                 │
    │   └─ Exam traps and how to avoid them                                 │
    │                                                                         │
    │   TEMPLATE.py                                                        │
    │   └─ Starting template with session management patterns               │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘

"""

# ═══════════════════════════════════════════════════════════════════════════
# KEY CONCEPTS SUMMARY
# ═══════════════════════════════════════════════════════════════════════════

"""
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   THREE SESSION MANAGEMENT APPROACHES:                                 │
│                                                                         │
│   --resume: Full history (use when context valid)                     │
│   fork_session: Independent branches (use for exploration)             │
│   Fresh start + summary: New session with curated knowledge             │
│                                                                         │
│   ─────────────────────────────────────────────────────────────────────  │
│                                                                         │
│   THE STALE CONTEXT PROBLEM:                                           │
│                                                                         │
│   • Resuming restores ALL tool results                                 │
│   • Files may have changed since tool results were generated          │
│   • Agent has conflicting information: stale vs fresh                  │
│   • Contradictory advice and confused agents!                          │
│                                                                         │
│   ─────────────────────────────────────────────────────────────────────  │
│                                                                         │
│   THE CORRECT FIX:                                                     │
│                                                                         │
│   • Start FRESH session (no stale tool results)                        │
│   • Inject structured SUMMARY of prior findings                        │
│   • Specify WHICH files have changed                                  │
│   • Agent re-analyzes only modified files                              │
│                                                                         │
│   ─────────────────────────────────────────────────────────────────────  │
│                                                                         │
│   EXAM TIPS:                                                           │
│                                                                         │
│   • Files changed? → Fresh start + summary (NOT --resume!)             │
│   • fork_session = divergent exploration, NOT continuation              │
│   • Fork INHERITS stale context - use fresh start instead!            │
│   • "Resume and re-read" = WRONG answer!                               │
│   • Targeted re-analysis > full re-exploration                         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
"""