"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║           SESSION STATE & RESUMPTION PATTERNS                             ║
║                                                                              ║
║  How to Handle Session State, Recovery, and Stale Context               ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

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

    When you resume a session, the entire conversation history is restored,
    including every tool result from the previous session.

    This causes agents to reason from outdated file contents alongside current
    data, producing contradictory advice!

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   DAY 1: Initial Analysis                                             │
    │   ─────────────────────────────────────────────────────              │
    │   • User: "Analyze auth.ts for security issues"                     │
    │   • Agent reads auth.ts → finds: "Uses MD5 for hashing"            │
    │   • Agent: "You should upgrade from MD5 to bcrypt"                │
    │   • Tool result stored: "File auth.ts: uses MD5 hashing"         │
    │                                                                         │
    │   User implements the fix (changes auth.ts)                          │
    │                                                                         │
    │   DAY 2: Resume Session                                             │
    │   ─────────────────────────────────────────────────────              │
    │   • User: "claude --resume day1-session"                           │
    │   • Conversation history restored with tool results!               │
    │   • Tool result still says: "auth.ts uses MD5" ← STALE!          │
    │                                                                         │
    │   User: "Continue analyzing auth.ts"                                │
    │   • Agent reads NEW auth.ts → finds: "Uses bcrypt" ← NEW!        │
    │   • BUT Agent also has OLD tool result: "uses MD5"               │
    │   • Agent gets confused!                                           │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘


CONTRADICTORY BEHAVIOR FROM STALE CONTEXT
══════════════════════════════════════════

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   RESUMED SESSION with stale tool results:                            │
    │                                                                         │
    │   User: "What's the current state of auth.ts?"                        │
    │                                                                         │
    │   Agent considers:                                                   │
    │   ┌───────────────────────────────────────────────────────────────┐   │
    │   │ Tool result from Day 1: "auth.ts uses MD5 hashing"        │   │
    │   │ Fresh read of auth.ts: "auth.ts uses bcrypt"               │   │
    │   │                                                             │   │
    │   │ Which one is true?!                                          │   │
    │   └───────────────────────────────────────────────────────────────┘   │
    │                                                                         │
    │   POSSIBLE CONTRADICTORY RESPONSES:                                  │
    │                                                                         │
    │   ❌ "Your auth.ts uses MD5 which is insecure..."                  │
    │      (Based on stale tool result, WRONG!)                           │
    │                                                                         │
    │   ❌ "auth.ts uses bcrypt, which is good..."                    │
    │      (Fresh read correct, but may conflict with other stale)       │
    │                                                                         │
    │   ❌ "It seems auth.ts was changed from MD5 to bcrypt..."        │
    │      (Acknowledging conflict, but still confusing)                │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘


WHY NAIVE FIX FAILS
═══════════════════════

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   NAIVE FIX (Not Good Enough):                                      │
    │   ───────────────────────────────────────────────────────             │
    │                                                                         │
    │   User: "claude --resume session"                                    │
    │   User: "auth.ts has been modified, re-read it please"             │
    │                                                                         │
    │   What happens:                                                      │
    │   1. Conversation history still has STALE tool results               │
    │   2. Agent re-reads auth.ts → has fresh content                    │
    │   3. Agent still has BOTH stale and fresh in context               │
    │   4. Agent may still get confused about which is correct             │
    │   5. Contradictory advice may still occur                          │
    │                                                                         │
    │   The stale tool results are STILL IN THE CONVERSATION!              │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘


THE CORRECT FIX: TARGETED RE-ANALYSIS
════════════════════════════════════════

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   STEP 1: Start a FRESH session                                      │
    │   ───────────────────────────────────────────────────                 │
    │   $ claude --session new-session  # NEW session, not resumed!         │
    │   No conversation history. No stale tool results.                      │
    │                                                                         │
    │   ────────────────────────────────────────────────────────────────── │
    │                                                                         │
    │   STEP 2: Inject STRUCTURED SUMMARY of prior findings              │
    │   ─────────────────────────────────────────────────────              │
    │                                                                         │
    │   "Prior analysis summary:                                         │
    │    - auth.ts: Uses MD5 hashing (security issue)                  │
    │    - database.ts: Has SQL injection vulnerability                │
    │    - api-routes.ts: Missing rate limiting                       │
    │    - User implemented MD5 fix on Day 1"                          │
    │                                                                         │
    │   This transfers the KNOWLEDGE, not stale tool results!            │
    │                                                                         │
    │   ────────────────────────────────────────────────────────────────── │
    │                                                                         │
    │   STEP 3: Specify WHICH files have CHANGED                         │
    │   ─────────────────────────────────────────────────────              │
    │                                                                         │
    │   "Modified files: auth.ts (fixed MD5 -> bcrypt)               │
    │    Please re-analyze: auth.ts"                                    │
    │                                                                         │
    │   Agent knows exactly what to focus on!                            │
    │                                                                         │
    │   ────────────────────────────────────────────────────────────────── │
    │                                                                         │
    │   STEP 4: Agent RE-ANALYZES only modified files                    │
    │   ─────────────────────────────────────────────────                 │
    │   Agent reads fresh auth.ts → confirms bcrypt fix ✓                │
    │   Agent combines fresh analysis with prior findings                  │
    │   Result: Complete, current, accurate analysis!                    │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘


DECISION MATRIX
══════════════════

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   SCENARIO                              │  BEST APPROACH                │
    │   ─────────────────────────────────────┼────────────────────────────── │
    │                                                                         │
    │   Work from yesterday, no files        │  --resume                    │
    │   changed, continue exact work         │  (Full history still valid)  │
    │                                                                         │
    ├────────────────────────────────────────┼──────────────────────────────┤
    │                                                                         │
    │   Comparing two refactoring             │  fork_session                 │
    │   approaches (microservices vs         │  (Independent branches)        │
    │   monolith)                           │                               │
    │                                                                         │
    ├────────────────────────────────────────┼──────────────────────────────┤
    │                                                                         │
    │   Resuming after modifying 3 of        │  Fresh start + summary       │
    │   50 files                             │  (Only modified files need     │
    │                                        │   re-analysis)               │
    │                                                                         │
    ├────────────────────────────────────────┼──────────────────────────────┤
    │                                                                         │
    │   Long session with cluttered          │  Fresh start + summary       │
    │   history                              │  (Start clean, inject       │
    │                                        │   knowledge)                 │
    │                                                                         │
    ├────────────────────────────────────────┼──────────────────────────────┤
    │                                                                         │
    │   Resuming after dependency            │  Fresh start + summary       │
    │   updates (package.json changed)        │  (Need fresh analysis of     │
    │                                        │   dependency impact)         │
    │                                                                         │
    └────────────────────────────────────────┴──────────────────────────────┘


KEY RULES TO REMEMBER
═══════════════════════

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   RULE 1: Files changed? → DON'T use --resume!                       │
    │                                                                         │
    │   --resume restores ALL tool results, including stale ones.            │
    │   This causes contradictory advice and confused agents.               │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   RULE 2: fork_session = branching, not resuming                    │
    │                                                                         │
    │   fork_session creates INDEPENDENT branches.                          │
    │   --resume continues a specific session linearly.                       │
    │   These are different tools for different purposes!                    │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   RULE 3: Transfer KNOWLEDGE, not tool results                        │
    │                                                                         │
    │   Fresh start + summary:                                              │
    │   • Inject what you LEARNED (knowledge)                               │
    │   • NOT what tools returned (stale results)                           │
    │   • Agent rebuilds understanding from fresh context                    │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   RULE 4: Specify changed files for targeted re-analysis              │
    │                                                                         │
    │   "Modified files: auth.ts, database.ts"                            │
    │   This tells agent exactly what needs fresh analysis.                  │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘


EXAM TRAPS TO AVOID
═════════════════════

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   EXAM TRAP 1: "Just resume and re-read changed files"             │
    │                                                                         │
    │   WRONG! This still has stale tool results in history.               │
    │   Stale data is NOT cleared by re-reading files!                     │
    │                                                                         │
    │   CORRECT: Fresh start + summary injection                           │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   EXAM TRAP 2: Confusing fork_session with --resume                │
    │                                                                         │
    │   --resume: Continues a specific session linearly                      │
    │   fork_session: Creates independent branches                         │
    │                                                                         │
    │   For exploring alternatives: fork_session                            │
    │   For continuing work: --resume (if context valid)                   │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   EXAM TRAP 3: Using --resume when files changed                    │
    │                                                                         │
    │   If scenario says "files were modified", --resume is WRONG.         │
    │   Must use fresh start + summary to avoid stale context!              │
    │                                                                         │
    │   The exam tests whether you recognize this!                         │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘


WHAT THIS FOLDER COVERS
════════════════════════

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                                                                         │
    │   practice_01_three_approaches.py                                     │
    │   ├─ Three session management approaches                                │
    │   └─ --resume, fork_session, fresh start + summary                   │
    │                                                                         │
    │   practice_02_stale_context_problem.py                                │
    │   ├─ The stale context problem                                         │
    │   └─ Why resuming after file changes causes issues                     │
    │                                                                         │
    │   practice_03_targeted_reanalysis.py                                   │
    │   ├─ The correct fix: fresh start + summary injection                │
    │   └─ Step-by-step pattern for resuming after file changes             │
    │                                                                         │
    │   practice_04_decision_matrix.py                                      │
    │   ├─ Decision matrix for choosing the right approach                  │
    │   └─ Detailed scenarios with reasoning                                  │
    │                                                                         │
    │   TEMPLATE.py                                                        │
    │   └─ Starting template with SessionStateManager                       │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘

"""

# ═══════════════════════════════════════════════════════════════════════════
# KEY CONCEPTS SUMMARY
# ═══════════════════════════════════════════════════════════════════════════

"""
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   THREE APPROACHES:                                                    │
│                                                                         │
│   --resume: Full history restored (use when context valid)          │
│   fork_session: Independent branches (use for exploration)           │
│   Fresh start + summary: New session with curated knowledge            │
│                                                                         │
│   ─────────────────────────────────────────────────────────────────────  │
│                                                                         │
│   THE STALE CONTEXT PROBLEM:                                          │
│   • Resuming restores ALL tool results                                │
│   • Files may have changed since tool results were generated          │
│   • Agent has conflicting information: stale vs fresh                 │
│   • Contradictory advice and confused agents!                         │
│                                                                         │
│   ─────────────────────────────────────────────────────────────────────  │
│                                                                         │
│   THE CORRECT FIX:                                                    │
│   • Start FRESH session (no stale tool results)                        │
│   • Inject structured SUMMARY of prior findings                        │
│   • Specify WHICH files have changed                                   │
│   • Agent re-analyzes only modified files                              │
│                                                                         │
│   ─────────────────────────────────────────────────────────────────────  │
│                                                                         │
│   EXAM TIPS:                                                          │
│   • Files changed? → Fresh start + summary (NOT --resume!)            │
│   • fork_session = divergent exploration                               │
│   • --resume = linear continuation (only if context valid)             │
│   • "Resume and re-read" = WRONG answer!                              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
"""