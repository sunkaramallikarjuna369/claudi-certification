"""
================================================================================
CLAUDE CERTIFIED ARCHITECT - COMPLETE STUDY MATERIALS
================================================================================

Repository: https://github.com/sunkaramallikarjuna369/claudi-certification

This repository contains comprehensive practice materials for passing the
Claude Certified Architect certification exam.

EXAM DETAILS
===============================================================================
- Total Task Statements: 30
- Total Questions: 150+
- Passing Score: 720/1000 points
- Exam Duration: 3 hours

================================================================================
FIVE CERTIFICATION DOMAINS
================================================================================

+==============================================================================+
|                                                                              |
|  DOMAIN 1: AGENTIC ARCHITECTURE & ORCHESTRATION (27%)                       |
|  Domain 2: TOOL DESIGN & MCP INTEGRATION (18%)                              |
|  Domain 3: CLAUDE CODE CONFIGURATION & WORKFLOWS (20%)                     |
|  Domain 4: PROMPT ENGINEERING & STRUCTURED OUTPUT (20%)                    |
|  Domain 5: CONTEXT MANAGEMENT & RELIABILITY (15%)                          |
|                                                                              |
+==============================================================================+

================================================================================
DOMAIN 1: AGENTIC ARCHITECTURE & ORCHESTRATION (27%)
================================================================================

Folder: agentic_architecture/

This domain covers designing and implementing agentic systems using Claude's
API, including loop management, orchestration patterns, guardrails, and the
Claude Agent SDK.

SUBFOLDERS:
-------------------------------------------------------------------------------

    agentic_loops/
    ----------------------------------------------------------------------------
    - Basic agentic loop pattern (send -> respond -> tools -> loop)
    - Multi-tool parallel execution
    - Sequential tool execution
    - Error handling in loops
    - ReAct pattern (Reason + Act)
    - Stateful agents with memory

    Key Concepts:
    - stop_reason checking (tool_use vs end_turn)
    - Message handling (assistant before tool_result)
    - Loop termination conditions

    multi_agent_orchestration/
    ----------------------------------------------------------------------------
    - Hub-and-spoke coordinator pattern
    - Dynamic agent selection
    - Scope-based partitioning
    - Iterative refinement loops
    - Context passing between agents
    - Full orchestrator implementation

    Key Concepts:
    - Coordinator as central routing hub
    - Subagent tool limitation (4-5 tools per agent)
    - Scoped cross-role tools for efficiency
    - Least privilege tool design

    sub_agent_context_passing/
    ----------------------------------------------------------------------------
    - Explicit context passing (never inherited)
    - Attribution failure prevention
    - Agent-to-tool gating
    - fork_session vs --resume patterns
    - Common guardrail failures

    Key Concepts:
    - Context is NEVER inherited, ALWAYS passed
    - Subagent isolation in context
    - Metadata inclusion in context passing

    work_flow_enforcement_hand_off/
    ----------------------------------------------------------------------------
    - Enforcement spectrum (prompts ~90% vs hooks 100%)
    - Prerequisite gates (code-level enforcement)
    - Subagent lifecycle hooks
    - Multi-concern handling
    - Structured handoff protocols

    Key Concepts:
    - Financial/security operations require hooks
    - Human agents have NO transcript access
    - Handoff must include: Customer ID, summary, root cause, action

    agent_sdk_hooks/
    ----------------------------------------------------------------------------
    - PreToolUse hooks (before execution, can block)
    - PostToolUse hooks (after execution, can transform)
    - Policy enforcement patterns
    - Data normalization
    - Decision framework: hooks vs prompts

    Key Concepts:
    - PreToolUse: "Should this action happen?" (can block)
    - PostToolUse: "How should I present this result?" (cannot block)
    - Never use PostToolUse to block - too late!

    task_decomposition_strategies/
    ----------------------------------------------------------------------------
    - Fixed sequential pipeline
    - Dynamic adaptive decomposition
    - Attention dilution problem
    - Multi-pass architecture solution

    Key Concepts:
    - Fixed pipeline: Steps known in advance
    - Dynamic decomposition: Subtasks emerge
    - Multi-pass: Local analysis + cross-item integration
    - Attention dilution: Later items get less focus

    session_state_resumption/
    ----------------------------------------------------------------------------
    - Three approaches: --resume, fork_session, fresh start + summary
    - Stale context problem
    - Targeted re-analysis pattern
    - Decision matrix for session management

    Key Concepts:
    - Files changed? DON'T use --resume!
    - fork_session = branches, --resume = linear
    - Transfer KNOWLEDGE, not tool results

    error_recovery_resilience/
    ----------------------------------------------------------------------------
    - Session management approaches
    - Stale context problem
    - Targeted re-analysis
    - Decision matrix

    Key Concepts:
    - Fresh start when files modified
    - Summary injection for knowledge transfer

FILES IN EACH SUBFOLDER:
-------------------------------------------------------------------------------
- README.md: Detailed documentation with ASCII diagrams
- TEMPLATE.py: Starting template with patterns
- practice_XX_*.py: Practice files (5-6 per folder)

Each practice file includes:
+ Real-time scenarios showing practical applications
+ Common mistakes developers make (and how to avoid)
+ Interview Q&A preparation with expert answers
+ "WHAT WE HAVE LEARNT" summary section
+ ASCII-formatted comments for easy reading


================================================================================
DOMAIN 2: TOOL DESIGN & MCP INTEGRATION (18%)
================================================================================

Folder: tool_design_mcp/

This domain covers designing effective tool schemas, implementing MCP servers
and clients, and integrating external services into Claude-powered applications.

SUBFOLDERS:
-------------------------------------------------------------------------------

    tool_schema_design/
    ----------------------------------------------------------------------------
    - Production-grade tool descriptions (5 elements)
    - Tool splitting patterns
    - Input format specifications
    - Boundary definitions between tools

    Key Concepts:
    - Description is PRIMARY mechanism for tool selection
    - Five elements: purpose, inputs, examples, limits, boundaries
    - Split generic tools into purpose-specific tools

    mcp_server_implementation/
    ----------------------------------------------------------------------------
    - Model Context Protocol fundamentals
    - Server architecture patterns
    - Authentication and security
    - Rate limiting and quotas
    - Tool registration and discovery

    Key Concepts:
    - MCP provides standardized tool integration
    - Server-client bridge architecture
    - Handles registration, auth, rate limiting

    mcp_client_integration/
    ----------------------------------------------------------------------------
    - tool_choice configurations (auto, any, forced)
    - Optimal tool count (4-5 per agent)
    - Scoped cross-role tools
    - Least privilege design
    - Multi-agent tool tables

    Key Concepts:
    - "auto": Model decides whether to use tools
    - "any": Must call tool, model chooses which
    - "forced": Must call specific named tool
    - 18+ tools degrades selection reliability

    tool_error_handling/
    ----------------------------------------------------------------------------
    - Structured error responses with isError flag
    - Four error categories: transient, validation, business, permission
    - isRetryable flag for each error type
    - Access failure vs valid empty result distinction
    - Multi-agent error propagation

    Key Concepts:
    - Transient (timeouts): isRetryable: true
    - Validation (bad input): isRetryable: true
    - Business (policy): isRetryable: false
    - Permission (access denied): isRetryable: false

    tool_selection_routing/
    ----------------------------------------------------------------------------
    - Six built-in Claude Code tools (Read, Write, Edit, Bash, Grep, Glob)
    - Grep vs Glob core distinction
    - Enhanced MCP descriptions
    - Build vs use community servers
    - Incremental codebase discovery pattern

    Key Concepts:
    - Grep finds INSIDE files (content)
    - Glob finds by NAME (paths)
    - Use community servers for Jira, GitHub, Slack
    - Build custom only for team-specific workflows


================================================================================
DOMAIN 3: CLAUDE CODE CONFIGURATION & WORKFLOWS (20%)
================================================================================

Folder: claude_code_configuration/

This domain covers configuring Claude Code for development workflows, managing
settings and hooks, and integrating with CI/CD pipelines.

SUBFOLDERS:
-------------------------------------------------------------------------------

    claude_code_setup/
    ----------------------------------------------------------------------------
    - Installation and configuration
    - Settings management
    - Environment variables and .env integration
    - Project-level vs user-level settings
    - Model selection (haiku, sonnet, opus)
    - Context window and timeout configuration

    Key Concepts:
    - Use .env for API keys (never hardcode)
    - Project settings vs user settings
    - Model selection affects cost and capability

    permissions_hooks/
    ----------------------------------------------------------------------------
    - Hook system (before_tool, after_tool, on_error)
    - Pre-commit and post-commit hooks
    - Permission models for tool execution
    - Security considerations
    - Environment-specific hook configurations

    Key Concepts:
    - Hooks enable validation, logging, notifications
    - Security hooks for destructive operations
    - Environment-specific configurations

    workflow_automation/
    ----------------------------------------------------------------------------
    - Automating repetitive tasks
    - Script-based workflows
    - Multi-step task automation
    - Error recovery in workflows
    - Workflow state management
    - Custom command definitions

    Key Concepts:
    - Workflow state persistence
    - Error recovery patterns
    - Branch-specific workflows

    ci_cd_integration/
    ----------------------------------------------------------------------------
    - Non-interactive mode (--print flag)
    - GitHub Actions, GitLab CI, Jenkins examples
    - Exit codes and error handling
    - Security in CI environment
    - Automated testing and deployment

    Key Concepts:
    - Claude Code works in CI pipelines
    - Use --print for non-interactive mode
    - Handle exit codes properly

    best_practices/
    ----------------------------------------------------------------------------
    - Project structure organization
    - CLAUDE.md documentation standards
    - Code review workflows
    - Testing strategies
    - Security scanning
    - Collaboration guidelines

    Key Concepts:
    - CLAUDE.md documents project conventions
    - Standardized project structure
    - Team collaboration patterns

    advanced_configuration/
    ----------------------------------------------------------------------------
    - Custom tool development
    - MCP server configuration
    - Performance tuning
    - Cost optimization
    - Multi-project management
    - Security hardening

    Key Concepts:
    - Advanced customization options
    - Performance and cost balance
    - Team-wide configurations


================================================================================
DOMAIN 4: PROMPT ENGINEERING & STRUCTURED OUTPUT (20%)
================================================================================

Folder: prompt_engineering/

This domain covers crafting effective prompts, implementing structured output
patterns, and applying prompt engineering techniques for production applications.

SUBFOLDERS:
-------------------------------------------------------------------------------

    system_prompts/
    ----------------------------------------------------------------------------
    - Clear role definition
    - Explicit output format requirements
    - Criteria specification
    - Constraint definitions
    - Tone and style guidelines
    - System prompt structure patterns

    Key Concepts:
    - Role clarity improves responses
    - Explicit criteria prevent ambiguity
    - Constraints define boundaries

    structured_output/
    ----------------------------------------------------------------------------
    - JSON schema definition for outputs
    - Type specifications and validation
    - Required vs optional fields
    - Enum usage for controlled values
    - Tool output formatting
    - Nested object structures

    Key Concepts:
    - Structured output enables reliable parsing
    - JSON schema for type safety
    - Enum for controlled values

    prompt_chaining/
    ----------------------------------------------------------------------------
    - Multi-step prompt sequences
    - Output validation between steps
    - Retry logic for failures
    - State management across steps
    - Chain termination conditions
    - Loop detection

    Key Concepts:
    - Chaining enables complex workflows
    - Validation between steps
    - State persistence across steps

    few_shot_prompting/
    ----------------------------------------------------------------------------
    - Example selection criteria
    - Positive vs negative examples
    - Example formatting techniques
    - Number of examples (optimal range)
    - Diversity in example sets
    - Chain-of-thought examples

    Key Concepts:
    - 2-5 examples typically optimal
    - Diversity > quantity
    - Quality of examples matters

    batch_processing/
    ----------------------------------------------------------------------------
    - Batch request patterns
    - Parallel processing strategies
    - Token optimization techniques
    - Cost reduction methods
    - Rate limiting handling
    - Batch size optimization

    Key Concepts:
    - Batch processing reduces API calls
    - Token optimization reduces costs
    - Rate limit handling prevents failures

    multi_instance_review/
    ----------------------------------------------------------------------------
    - Parallel instance processing
    - Cross-instance validation
    - Consensus-based verification
    - Disagreement handling
    - Quality thresholds
    - Output reconciliation

    Key Concepts:
    - Multiple instances for reliability
    - Consensus for quality assurance
    - Disagreement handling protocols


================================================================================
DOMAIN 5: CONTEXT MANAGEMENT & RELIABILITY (15%)
================================================================================

Folder: context_management/

This domain covers managing context windows effectively, implementing caching
strategies, handling long conversations, and building reliable production systems.

SUBFOLDERS:
-------------------------------------------------------------------------------

    context_windows/
    ----------------------------------------------------------------------------
    - Context window limits and optimization
    - Token budgeting strategies
    - Message pruning techniques
    - Efficient context usage
    - Truncation strategies
    - Priority-based selection

    Key Concepts:
    - Window limits require careful management
    - Token budgeting prevents overflow
    - Priority-based context selection

    prompt_caching/
    ----------------------------------------------------------------------------
    - Cache hit optimization
    - Repeated content caching
    - Cache invalidation strategies
    - Cost reduction through caching
    - TTL configuration
    - Cache warming

    Key Concepts:
    - Caching reduces costs significantly
    - TTL for cache freshness
    - Invalidation for accuracy

    long_conversations/
    ----------------------------------------------------------------------------
    - Conversation state management
    - Message summarization techniques
    - Historical context extraction
    - Context refresh patterns
    - Memory bank patterns
    - Progressive pruning

    Key Concepts:
    - Summarize to compress context
    - Memory bank for persistent state
    - Rolling context management

    rate_limiting/
    ----------------------------------------------------------------------------
    - Rate limit handling patterns
    - Quota management
    - Backoff strategies
    - Retry with exponential backoff
    - Budget tracking
    - Cost control

    Key Concepts:
    - Exponential backoff prevents throttling
    - Quota tracking for cost control
    - Graceful degradation under limits

    monitoring_observability/
    ----------------------------------------------------------------------------
    - System health monitoring
    - Performance metrics
    - Error rate tracking
    - Latency monitoring
    - Cost monitoring
    - Alert configuration
    - Log aggregation

    Key Concepts:
    - Metrics enable optimization
    - Alert thresholds prevent issues
    - Log aggregation for debugging

    production_reliability/
    ----------------------------------------------------------------------------
    - Error handling patterns
    - Circuit breaker patterns
    - Fallback strategies
    - Timeout configuration
    - Graceful degradation
    - Health check endpoints
    - Recovery mechanisms

    Key Concepts:
    - Circuit breakers prevent cascading failures
    - Fallbacks ensure continued operation
    - Health checks enable monitoring


================================================================================
FILE STRUCTURE SUMMARY
================================================================================

    claudi-certification/
    |
    +-- README.md (this file - complete overview)
    |
    +-- agentic_architecture/
    |   +-- agentic_loops/
    |   +-- multi_agent_orchestration/
    |   +-- sub_agent_context_passing/
    |   +-- work_flow_enforcement_hand_off/
    |   +-- agent_sdk_hooks/
    |   +-- task_decomposition_strategies/
    |   +-- session_state_resumption/
    |   +-- error_recovery_resilience/
    |
    +-- tool_design_mcp/
    |   +-- tool_schema_design/
    |   +-- mcp_server_implementation/
    |   +-- mcp_client_integration/
    |   +-- tool_error_handling/
    |   +-- tool_selection_routing/
    |
    +-- claude_code_configuration/
    |   +-- claude_code_setup/
    |   +-- permissions_hooks/
    |   +-- workflow_automation/
    |   +-- ci_cd_integration/
    |   +-- best_practices/
    |   +-- advanced_configuration/
    |
    +-- prompt_engineering/
    |   +-- system_prompts/
    |   +-- structured_output/
    |   +-- prompt_chaining/
    |   +-- few_shot_prompting/
    |   +-- batch_processing/
    |   +-- multi_instance_review/
    |
    +-- context_management/
        +-- context_windows/
        +-- prompt_caching/
        +-- long_conversations/
        +-- rate_limiting/
        +-- monitoring_observability/
        +-- production_reliability/


================================================================================
HOW TO USE THESE MATERIALS
================================================================================

1. START WITH DOMAIN 1 (27% of exam)
   - agentic_loops/ is your foundation
   - Understand stop_reason and message handling
   - Practice basic loop patterns first

2. UNDERSTAND THE PATTERNS, NOT JUST THE CODE
   - Each practice file explains WHY, not just WHAT
   - Real-time scenarios show practical applications
   - Common mistakes teach what to avoid

3. REVIEW INTERVIEW Q&A SECTIONS
   - Each file includes expert-level Q&A
   - These prepare you for exam scenarios
   - Understand concepts, not just facts

4. RUN THE PRACTICE FILES
   - All files use Haiku model (cheapest)
   - API key from .env (never hardcoded)
   - Run with: python practice_XX_*.py

5. FOCUS ON EXAM TRAPS
   - Watch for common mistakes highlighted
   - Know when to use hooks vs prompts
   - Understand architectural solutions


================================================================================
EXAM PREPARATION TIPS
================================================================================

KEY KNOWLEDGE AREAS:

    +==============================================================================+
    |                                                                              |
    |  AGENTIC LOOPS:                                                              |
    |  - stop_reason: tool_use (continue) vs end_turn (stop)                      |
    |  - Messages: assistant before tool_result                                    |
    |  - Loop termination conditions                                              |
    |                                                                              |
    |  MULTI-AGENT:                                                                |
    |  - 4-5 tools per agent (18+ degrades selection)                             |
    |  - Coordinator for routing, not all through coordinator                      |
    |  - Context is NEVER inherited, ALWAYS passed                                 |
    |                                                                              |
    |  HOOKS:                                                                      |
    |  - PreToolUse: BEFORE execution (can block)                                 |
    |  - PostToolUse: AFTER execution (cannot block)                               |
    |  - Use hooks for financial/security, prompts for style                      |
    |                                                                              |
    |  TASK DECOMPOSITION:                                                         |
    |  - Fixed pipeline: Steps known in advance                                    |
    |  - Dynamic: Subtasks emerge                                                  |
    |  - Multi-pass fixes attention dilution                                      |
    |                                                                              |
    |  SESSION MANAGEMENT:                                                         |
    |  - Files changed? Fresh start + summary (NOT --resume!)                    |
    |  - fork_session = branches                                                   |
    |  - --resume = linear continuation                                           |
    |                                                                              |
    |  TOOL DESIGN:                                                               |
    |  - Descriptions are PRIMARY mechanism for selection                         |
    |  - Five elements: purpose, inputs, examples, limits, boundaries            |
    |  - Split generic tools into purpose-specific ones                           |
    |                                                                              |
    |  ERROR HANDLING:                                                            |
    |  - Four categories: transient, validation, business, permission             |
    |  - isRetryable flag for each                                                |
    |  - Access failure vs empty result distinction                               |
    |                                                                              |
    |  WORKFLOW:                                                                  |
    |  - Programmatic enforcement (100%) for financial/security                    |
    |  - Prompt-based (~90%) for formatting/style                                 |
    |  - Handoff must include: Customer ID, summary, root cause, action          |
    |                                                                              |
    +==============================================================================+


================================================================================
TECHNICAL REQUIREMENTS
================================================================================

    - Python 3.8+
    - anthropic package
    - python-dotenv package
    - API key in .env file

    Installation:
        pip install anthropic python-dotenv


================================================================================
CONTRIBUTING
================================================================================

This repository is for study and practice purposes.
Feel free to fork and customize for your learning needs.

Good luck with your certification exam!


================================================================================
"""

print("""
================================================================================
CLAUDE CERTIFIED ARCHITECT - COMPLETE STUDY MATERIALS
================================================================================

Repository: https://github.com/sunkaramallikarjuna369/claudi-certification

This comprehensive repository contains ALL practice materials needed to
pass the Claude Certified Architect certification exam.

FIVE DOMAINS COVERED:
---------------------

    Domain 1: Agentic Architecture & Orchestration (27%)
    Domain 2: Tool Design & MCP Integration (18%)
    Domain 3: Claude Code Configuration & Workflows (20%)
    Domain 4: Prompt Engineering & Structured Output (20%)
    Domain 5: Context Management & Reliability (15%)

See the full README.md file for complete details on all folders and content.
""")