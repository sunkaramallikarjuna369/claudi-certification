"""
================================================================================
TOOL SELECTION AND ROUTING - PRACTICE 01
================================================================================

WHAT IS TOOL SELECTION?
-----------------------
Tool selection determines how AI chooses which tool to use when given
multiple options. Understanding built-in tools and proper tool routing
is essential for effective MCP integration.

This practice file covers:
1. Six Claude Code built-in tools
2. Grep vs Glob - core distinction
3. Enhanced MCP descriptions
4. Build vs Use decision framework
5. Incremental codebase discovery pattern
6. Edit tool strategies

================================================================================
"""

# ================================================================================
# SECTION 1: ENVIRONMENT SETUP
# ================================================================================

import os
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Configure API settings
MODEL_NAME = "claude-haiku-4-5-20250601"
API_KEY = os.getenv("ANTHROPIC_API_KEY", "")


# ================================================================================
# SECTION 2: THE SIX BUILT-IN TOOLS
# ================================================================================

@dataclass
class BuiltInTool:
    """
    Represents one of the six Claude Code built-in tools.

    THE SIX BUILT-IN TOOLS:
    +----------+------------------+----------------------------------------+
    | Tool     | Purpose          | When to Use                           |
    +----------+------------------+----------------------------------------+
    | Read     | Read file contents| Examine specific files                 |
    | Write    | Create/overwrite  | Create new files or replace content    |
    | Edit     | Modify existing   | Change specific parts of files         |
    | Bash     | Execute commands  | Run shell commands, scripts           |
    | Grep     | Search CONTENT    | Find patterns inside files             |
    | Glob     | Search by NAME    | Find files by path/name pattern        |
    +----------+------------------+----------------------------------------+

    IMPORTANT: These are ALWAYS available. MCP tools are additions.
    """

    name: str
    description: str
    category: str
    use_cases: List[str]


# Define all six built-in tools
BUILT_IN_TOOLS = [
    BuiltInTool(
        name="Read",
        description="Read the complete contents of a file from the filesystem. "
                   "Supports reading specific line ranges with offset/limit parameters. "
                   "Returns file contents as text. Can read any file type including "
                   "source code, configuration, text, and binary (displayed as text).",
        category="file_system",
        use_cases=[
            "Examine source code files",
            "Read configuration files",
            "View documentation",
            "Check file contents before editing"
        ]
    ),
    BuiltInTool(
        name="Write",
        description="Create a new file or completely overwrite an existing file. "
                   "Use when creating new files from scratch or replacing entire content. "
                   "Does NOT support appending - use Edit for modifications. "
                   "Will create parent directories if they don't exist.",
        category="file_system",
        use_cases=[
            "Create new source files",
            "Create new documentation",
            "Initialize empty files",
            "Replace file content entirely"
        ]
    ),
    BuiltInTool(
        name="Edit",
        description="Make targeted modifications to existing files. "
                   "Uses old_string/new_string replacement where old_string must exist in file. "
                   "Shortest unique anchor first. Widens search if non-unique. "
                   "Use Read+Write as last resort when Edit cannot find unique anchor.",
        category="file_system",
        use_cases=[
            "Modify specific lines in code",
            "Fix typos or errors",
            "Add new functionality to existing files",
            "Update configuration values"
        ]
    ),
    BuiltInTool(
        name="Bash",
        description="Execute shell commands in the terminal. "
                   "Commands run in the working directory by default. "
                   "Supports all standard shell commands including pipes, redirects, and scripts. "
                   "Returns command output (stdout/stderr) and exit code.",
        category="system",
        use_cases=[
            "Run tests and linters",
            "Execute build scripts",
            "Git operations",
            "Package management",
            "File operations via command line"
        ]
    ),
    BuiltInTool(
        name="Grep",
        description="Search for text patterns INSIDE files. "
                   "Returns matching lines with line numbers. "
                   "Essential for finding function calls, error messages, imports, "
                   "variable usages, and any text within file contents.",
        category="search",
        use_cases=[
            "Find function definitions across codebase",
            "Locate all usages of a variable",
            "Search for error messages in logs",
            "Find imports of specific modules"
        ]
    ),
    BuiltInTool(
        name="Glob",
        description="Find files by NAME or path pattern, not content. "
                   "Matches files based on glob patterns (*.py, **/*.ts, etc). "
                   "Does NOT search inside files - use Grep for content search. "
                   "Essential for discovering file structure and extensions.",
        category="search",
        use_cases=[
            "Find all files with specific extension",
            "List all files in a directory",
            "Discover project structure",
            "Find files matching naming patterns"
        ]
    )
]


# ================================================================================
# SECTION 3: GREP VS GLOB - THE CORE DISTINCTION
# ================================================================================

def explain_grep_vs_glob():
    """
    Explain the fundamental difference between Grep and Glob.

    THIS IS A CRITICAL DISTINCTION THAT MANY DEVELOPERS MISS!

    GREP = Search CONTENT (inside files)
    GLOB = Search NAME (file paths)

    Think of it as:
    - Grep: "Find all files containing the word 'error'"
    - Glob: "Find all files named 'error*.log'"
    """

    print("\n" + "=" * 70)
    print("GREP vs GLOB: THE CORE DISTINCTION")
    print("=" * 70)

    comparison = """
    +=========================================================================+
    |                           COMPARISON                                   |
    +=========================================================================+

    +---------------------------+-------------------+------------------------+
    | Aspect                    | GREP              | GLOB                   |
    +---------------------------+-------------------+------------------------+
    | Searches                  | CONTENT inside    | NAME/PATH of           |
    |                           | files             | files                  |
    +---------------------------+-------------------+------------------------+
    | What it finds            | Lines containing  | Files matching         |
    |                           | pattern           | path pattern           |
    +---------------------------+-------------------+------------------------+
    | Example query            | "def main"        | "*.py"                 |
    +---------------------------+-------------------+------------------------+
    | Finds                    | All functions     | All Python files       |
    |                           | named 'main'      | in the project         |
    +---------------------------+-------------------+------------------------+
    | Output                    | Lines with        | File paths/names       |
    |                           | context           | (no content)           |
    +---------------------------+-------------------+------------------------+

    +=========================================================================+
    |                         VISUAL EXAMPLES                                |
    +=========================================================================+

    GREP Example:
    +---------------------------------------------------------------------+
    | Pattern: "handle_error"                                             |
    |                                                                       |
    | Result:                                                              |
    |   src/utils.py:42    def handle_error(msg):                         |
    |   src/api.py:128     if result: handle_error(e)                    |
    |   tests/test.py:15   with pytest.raises(handle_error):             |
    |                                                                       |
    | -> Finds lines containing "handle_error" (3 different contexts)   |
    +---------------------------------------------------------------------+

    GLOB Example:
    +---------------------------------------------------------------------+
    | Pattern: "**/*.py"                                                   |
    |                                                                       |
    | Result:                                                              |
    |   src/utils.py                                                      |
    |   src/api.py                                                        |
    |   tests/test.py                                                      |
    |                                                                       |
    | -> Finds Python files by extension (knows nothing about content)   |
    +---------------------------------------------------------------------+

    +=========================================================================+
    |                       DECISION FLOWCHART                              |
    +=========================================================================+

    Do you want to find...
    +---------------------+
    |                     |
    +--> File NAME/PATH? --> YES --> Use GLOB
    |                     |
    | (e.g., "all .py files",
    |  "files in src/",   |
    |  "test_*.py")
    |
    +--> Text INSIDE files? --> YES --> Use GREP
    |                     |
    | (e.g., "function call",
    |  "error message",   |
    |  "import statement")
    |
    +--> BOTH? --> Use GLOB first to find files, then GREP to search inside

    """

    print(comparison)


def demonstrate_grep_vs_glob_use_cases():
    """
    Show practical examples of when to use Grep vs Glob.
    """

    print("\n" + "-" * 70)
    print("PRACTICAL USE CASES")
    print("-" * 70)

    scenarios = [
        {
            "task": "Find all Python files in the project",
            "answer": "GLOB",
            "reason": "Looking for files by extension (NAME), not content"
        },
        {
            "task": "Find all places where 'calculate_total' is called",
            "answer": "GREP",
            "reason": "Looking for function calls inside files (CONTENT)"
        },
        {
            "task": "Find all test files",
            "answer": "GLOB",
            "reason": "Looking for files matching naming pattern (NAME)"
        },
        {
            "task": "Find all 'TODO' comments in code",
            "answer": "GREP",
            "reason": "Looking for text patterns inside files (CONTENT)"
        },
        {
            "task": "Find all files in 'src/' directory",
            "answer": "GLOB",
            "reason": "Looking for files by path location (NAME)"
        },
        {
            "task": "Find all 'except' blocks handling errors",
            "answer": "GREP",
            "reason": "Looking for code patterns inside files (CONTENT)"
        },
        {
            "task": "Find all configuration files (yaml, json, toml)",
            "answer": "GLOB",
            "reason": "Looking for files by extension (NAME)"
        },
        {
            "task": "Find all usages of 'api_key' variable",
            "answer": "GREP",
            "reason": "Looking for variable references inside files (CONTENT)"
        }
    ]

    print("\n+----------+------------------------+--------------------------------+")
    print("| Task     | Tool      | Reason                                |")
    print("+----------+------------------------+--------------------------------+")

    for s in scenarios:
        print(f"| {s['task'][:24]:<24} | {s['answer']:<8} | {s['reason'][:32]:<32} |")

    print("+----------+------------------------+--------------------------------+")


# ================================================================================
# SECTION 4: ENHANCED MCP DESCRIPTIONS
# ================================================================================

def explain_enhanced_descriptions():
    """
    Explain why MCP tool descriptions should be 3-5 sentences.

    A well-written description helps AI understand:
    1. What the tool does (action)
    2. When to use it (trigger conditions)
    3. What output to expect (result format)

    This prevents "built-in tool bias" where AI defaults to using
    built-in tools even when a better MCP tool exists.
    """

    print("\n" + "=" * 70)
    print("ENHANCED MCP TOOL DESCRIPTIONS")
    print("=" * 70)

    explanation = """
    +=========================================================================+
    |                    WHY DETAILED DESCRIPTIONS?                         |
    +=========================================================================+

    PROBLEM: Built-in Tool Bias
    +---------------------------------------------------------------------+
    | AI models are trained heavily on built-in tools (Grep, Read, etc).  |
    | Without detailed MCP descriptions, AI may default to using built-ins |
    | even when a specialized MCP tool would be better.                   |
    +---------------------------------------------------------------------+

    SOLUTION: Enhanced Descriptions (3-5 sentences)

    BAD (too brief):
    +---------------------------------------------------------------------+
    | "search_codebase: Search for code patterns"                         |
    |                                                                       |
    | Problem: Too vague. AI doesn't know when to use this vs Grep.      |
    +---------------------------------------------------------------------+

    GOOD (enhanced):
    +---------------------------------------------------------------------+
    | "search_codebase: Performs semantic code search using AST-aware     |
    | analysis. Use when you need to find function definitions, class     |
    | references, or code patterns that span multiple files. Returns      |
    | structured results with file paths, line numbers, and context.      |
    | Best for understanding code architecture and finding implementations." |
    +---------------------------------------------------------------------+

    This tells AI:
    - WHAT: AST-aware semantic search
    - WHEN: Function definitions, class references, cross-file patterns
    - OUTPUT: Structured results with paths, lines, context
    - BEST FOR: Code architecture understanding

    +=========================================================================+
    |                      DESCRIPTION TEMPLATE                             |
    +=========================================================================+

    Tool description should always include:

    1. ACTION: What the tool does
       "Performs X using Y"

    2. TRIGGER: When to use it
       "Use when you need to..."

    3. OUTPUT: What it returns
       "Returns [description of output]"

    4. BEST FOR: Ideal use cases
       "Best for [specific scenarios]"

    Example:
    +---------------------------------------------------------------------+
    | "extract_dependencies: Analyzes import statements and package         |
    | requirements across your codebase. Use when you need to understand   |
    | project dependencies or find unused imports. Returns list of        |
    | packages with version constraints and file locations where used.    |
    | Best for dependency auditing and cleanup before upgrades."          |
    +---------------------------------------------------------------------+

    """

    print(explanation)


# ================================================================================
# SECTION 5: BUILD VS USE DECISION FRAMEWORK
# ================================================================================

class BuildVsUseFramework:
    """
    Framework for deciding when to build custom MCP tools vs use existing.

    PRINCIPLE: Build custom only for:
    - Team-specific workflows
    - Custom business logic
    - Proprietary systems

    Use community servers for:
    - Standard integrations (Jira, GitHub, Slack)
    - Well-documented APIs
    - Common use cases
    """

    @staticmethod
    def should_build(tool_requirement: str) -> Tuple[bool, str]:
        """
        Decide if a custom tool should be built.

        RETURNS:
            Tuple of (should_build: bool, reason: str)
        """

        # Check for standard integration patterns
        standard_integrations = [
            "jira", "github", "gitlab", "slack", "discord",
            "notion", "asana", "linear", "google", "aws",
            "azure", "Salesforce", "HubSpot"
        ]

        for integration in standard_integrations:
            if integration.lower() in tool_requirement.lower():
                return (False, f"Use existing {integration} community server")

        # Check for team-specific requirements
        team_specific_patterns = [
            "internal workflow",
            "custom business logic",
            "proprietary system",
            "internal API",
            "team-specific process"
        ]

        for pattern in team_specific_patterns:
            if pattern in tool_requirement.lower():
                return (True, "Team-specific requirement - build custom")

        # Default to using existing tools
        return (False, "Consider using built-in tools or community servers")


def demonstrate_build_vs_use():
    """
    Demonstrate the build vs use decision framework.
    """

    print("\n" + "=" * 70)
    print("BUILD VS USE DECISION FRAMEWORK")
    print("=" * 70)

    scenarios = [
        "Create GitHub issues from conversation",
        "Query internal database for customer data",
        "Send messages to Slack channel",
        "Process team-specific approval workflow",
        "Fetch Jira tickets for sprint",
        "Query proprietary ML model API",
        "Search codebase for function definitions",
        "Connect to internal HR system"
    ]

    framework = BuildVsUseFramework()

    print("\n+--------------------------------+----------+----------------------------+")
    print("| Requirement                    | Decision | Reason                     |")
    print("+--------------------------------+----------+----------------------------+")

    for scenario in scenarios:
        should_build, reason = framework.should_build(scenario)
        decision = "BUILD" if should_build else "USE"
        print(f"| {scenario:<30} | {decision:<7} | {reason:<27} |")

    print("+--------------------------------+----------+----------------------------+")


# ================================================================================
# SECTION 6: INCREMENTAL CODEBASE DISCOVERY
# ================================================================================

class IncrementalDiscovery:
    """
    Pattern for efficiently exploring large codebases.

    PRINCIPLE: Don't read everything upfront. Use alternating
    search and read operations to incrementally discover structure.

    PATTERN: Grep -> Read -> Grep -> Read (not upfront reading)

    This is more efficient because:
    1. You discover relevant files first
    2. You avoid reading irrelevant content
    3. You follow code paths naturally
    """

    @staticmethod
    def discover_project_structure() -> List[str]:
        """
        Demonstrate incremental discovery pattern.

        RETURNS:
            List of steps in the discovery process
        """

        steps = """
        +=========================================================================+
        |              INCREMENTAL CODEBASE DISCOVERY                            |
        +=========================================================================+

        WRONG APPROACH (reading everything):
        +---------------------------------------------------------------------+
        | 1. Read all files in project (1000+ files)                          |
        | 2. Try to understand everything                                      |
        | 3. Get lost in irrelevant details                                     |
        | Result: OVERWHELMED, inefficient, slow                               |
        +---------------------------------------------------------------------+

        RIGHT APPROACH (incremental):
        +---------------------------------------------------------------------+
        | Step 1: GREP - Find relevant files                                    |
        |         "Find files containing 'main' function"                     |
        |         Result: main.py, app.py, run.py                              |
        +---------------------------------------------------------------------+

        | Step 2: READ - Examine the relevant files                            |
        |         Read main.py to understand entry point                       |
        |         Result: Understanding of application flow                    |
        +---------------------------------------------------------------------+

        | Step 3: GREP - Find related files based on discovery                  |
        |         "Find files importing from 'main' module"                     |
        |         Result: config.py, routes.py, middleware.py                  |
        +---------------------------------------------------------------------+

        | Step 4: READ - Continue exploration                                   |
        |         Read files discovered in step 3                              |
        |         Result: Expanded understanding                              |
        +---------------------------------------------------------------------+

        | Step 5: GREP - Find specific patterns                                 |
        |         "Find all API endpoint definitions"                         |
        |         Result: routes.py, handlers.py, views.py                   |
        +---------------------------------------------------------------------+

        | Continue alternating until understanding complete...                |

        +---------------------------------------------------------------------+

        BENEFITS:
        - Only read relevant files
        - Follow natural code paths
        - Build understanding incrementally
        - Stop when satisfied (don't over-explore)

        """

        return [steps]

    @staticmethod
    def example_session():
        """
        Show example discovery session with pseudo-commands.
        """

        print("\n" + "-" * 70)
        print("EXAMPLE DISCOVERY SESSION")
        print("-" * 70)

        session = """
        > Grep: "def handle_request"
        Found: server.py:45, handler.py:23

        > Read: handler.py (focus on line 23)
        Shows: handle_request calls authenticate, then routes to specific handlers

        > Grep: "authentication" (in handler.py context)
        Found: auth.py:1 (authentication module), middleware.py:15 (auth middleware)

        > Read: auth.py
        Shows: Authentication class with validate_token method

        > Grep: "validate_token"
        Found: auth.py:42 (definition), tests/test_auth.py:55 (test usage)

        > Read: tests/test_auth.py
        Shows: Test cases for authentication - helps understand expected behavior

        ... (continue until understanding complete)
        """

        print(session)


# ================================================================================
# SECTION 7: EDIT TOOL STRATEGIES
# ================================================================================

class EditToolStrategies:
    """
    Strategies for using the Edit tool effectively.

    IMPORTANT RULES:
    1. Shortest unique anchor first
    2. Widen old_string if non-unique
    3. Use Read+Write as last resort
    """

    @staticmethod
    def demonstrate_edit_patterns():
        """
        Show different Edit tool strategies.
        """

        print("\n" + "=" * 70)
        print("EDIT TOOL STRATEGIES")
        print("=" * 70)

        strategies = """
        +=========================================================================+
        |                         STRATEGY 1: UNIQUE ANCHOR                     |
        +=========================================================================+

        When you can find a unique string to match:

        +---------------------------------------------------------------------+
        | old_string = "def calculate_total(items):"                          |
        | new_string = "def calculate_total(items, tax_rate=0.1):"           |
        +---------------------------------------------------------------------+

        Use this when the context is unique and won't match elsewhere.

        +=========================================================================+
        |                         STRATEGY 2: WIDER CONTEXT                     |
        +=========================================================================+

        When the short string appears multiple times:

        +---------------------------------------------------------------------+
        | First attempt (FAILS - "return" appears 50 times):                 |
        |   old_string = "return"                                             |
        |   new_string = "return None"                                        |
        |   Error: "Non-unique match in file"                                |
        +---------------------------------------------------------------------+

        +---------------------------------------------------------------------+
        | Fix: Add surrounding context to make unique                         |
        |   old_string = "def get_value()\\n    return"                       |
        |   new_string = "def get_value()\\n    return None"                   |
        +---------------------------------------------------------------------+

        +=========================================================================+
        |                         STRATEGY 3: READ + WRITE                      |
        +=========================================================================+

        When edits are too complex for targeted replacement:

        +---------------------------------------------------------------------+
        | 1. Read the entire file                                              |
        | 2. Modify the content in memory                                     |
        | 3. Write the entire file back                                       |
        +---------------------------------------------------------------------+

        Use when:
        - Multiple scattered changes needed
        - No unique anchors available
        - Complex restructuring required

        +=========================================================================+
        |                         COMMON MISTAKES                               |
        +=========================================================================+

        MISTAKE 1: Trying to edit too much at once
        +---------------------------------------------------------------------+
        | Bad:                                                                     |
        |   old_string = "entire 100-line function with multiple changes"       |
        |                                                                       |
        | Good:                                                                    |
        |   old_string = "single line or unique block"                          |
        +---------------------------------------------------------------------+

        MISTAKE 2: Not checking uniqueness before editing
        +---------------------------------------------------------------------+
        | Bad:                                                                     |
        |   old_string = "return data"  # May appear 20 times!                 |
        |                                                                       |
        | Good:                                                                    |
        |   old_string = "def get_data():\\n    return data"  # Unique context |
        +---------------------------------------------------------------------+

        MISTAKE 3: Using line numbers (don't work reliably)
        +---------------------------------------------------------------------+
        | Bad:                                                                     |
        |   old_string = "line 42: return data"                                 |
        |                                                                       |
        | Good:                                                                    |
        |   old_string = "surrounding unique context"                           |
        +---------------------------------------------------------------------+

        """

        print(strategies)


# ================================================================================
# SECTION 8: TOOL SELECTION MATRIX
# ================================================================================

def print_tool_selection_matrix():
    """
    Print comprehensive matrix of built-in tools and their use cases.
    """

    matrix = """
    +=========================================================================+
    |                    TOOL SELECTION MATRIX                                |
    +=========================================================================+

    +============+============================================================+
    | TOOL: Read |                                                             |
    +============+============================================================+
    | Purpose:   | Read file contents                                         |
    +------------+------------------------------------------------------------+
    | When to use| - Examine specific files                                   |
    |            | - Read source code before editing                          |
    |            | - View configuration                                      |
    |            | - Check documentation                                     |
    +------------+------------------------------------------------------------+
    | Example:   | Read file_path="/path/to/file.py", limit=100, offset=0      |
    +============+============================================================+

    +============+============================================================+
    | TOOL: Write |                                                            |
    +============+============================================================+
    | Purpose:   | Create new files or overwrite entirely                     |
    +------------+------------------------------------------------------------+
    | When to use| - Create new source files                                  |
    |            | - Create new documentation                                 |
    |            | - Replace entire file content                             |
    +------------+------------------------------------------------------------+
    | Example:   | Write file_path="/path/to/new.py", content="..."            |
    +------------+------------------------------------------------------------+
    | Note:      | Does NOT append - use Edit for modifications                |
    +============+============================================================+

    +============+============================================================+
    | TOOL: Edit |                                                             |
    +============+============================================================+
    | Purpose:   | Modify existing files (targeted changes)                    |
    +------------+------------------------------------------------------------+
    | When to use| - Change specific lines                                    |
    |            | - Fix typos/errors                                         |
    |            | - Add functionality                                        |
    +------------+------------------------------------------------------------+
    | Strategy:  | 1. Find shortest unique anchor                             |
    |            | 2. Widen old_string if non-unique                          |
    |            | 3. Use Read+Write as last resort                            |
    +------------+------------------------------------------------------------+
    | Example:   | Edit file_path="/path/to/file.py",                         |
    |            |           old_string="def foo():",                         |
    |            |           new_string="def foo(): pass"                     |
    +============+============================================================+

    +============+============================================================+
    | TOOL: Bash |                                                             |
    +============+============================================================+
    | Purpose:   | Execute shell commands                                      |
    +------------+------------------------------------------------------------+
    | When to use| - Run tests and linters                                    |
    |            | - Git operations                                           |
    |            | - Build scripts                                            |
    |            | - Package management                                       |
    +------------+------------------------------------------------------------+
    | Example:   | Bash command="python -m pytest tests/"                     |
    +============+============================================================+

    +============+============================================================+
    | TOOL: Grep |                                                             |
    +============+============================================================+
    | Purpose:   | Search CONTENT inside files                                  |
    +------------+------------------------------------------------------------+
    | When to use| - Find function definitions                                 |
    |            | - Find usages of variables                                  |
    |            | - Search for error messages                                |
    |            | - Find imports                                             |
    +------------+------------------------------------------------------------+
    | Key point: | Searches INSIDE files, returns matching lines               |
    +------------+------------------------------------------------------------+
    | Example:   | Grep path="/src", pattern="def main", output_mode="content" |
    +============+============================================================+

    +============+============================================================+
    | TOOL: Glob |                                                             |
    +============+============================================================+
    | Purpose:   | Search FILES by NAME/PATH pattern                           |
    +------------+------------------------------------------------------------+
    | When to use| - Find all files with extension                             |
    |            | - List files in directory                                  |
    |            | - Discover project structure                              |
    +------------+------------------------------------------------------------+
    | Key point: | Searches by NAME, not content                               |
    +------------+------------------------------------------------------------+
    | Example:   | Glob path="/src", pattern="*.py"                           |
    +============+============================================================+

    +=========================================================================+
    |                    MCP TOOL INTEGRATION                                 |
    +=========================================================================+

    MCP tools are ADDITIONS to built-in tools. They extend capabilities.

    +---------------------------+-------------------------------------------+
    | Built-in Tools            | MCP Tools (additions)                     |
    +---------------------------+-------------------------------------------+
    | Always available          | Must be registered with server             |
    | Generic purpose           | Often domain-specific                      |
    | Low-level operations       | Higher-level workflows                     |
    +---------------------------+-------------------------------------------+

    Example: Built-in Grep vs MCP search_codebase

    Built-in Grep:
    - Searches for text pattern in files
    - Returns matching lines

    MCP search_codebase (if available):
    - Semantic search using AST
    - Understands code structure
    - Returns function definitions, references, context

    """

    print(matrix)


# ================================================================================
# SECTION 9: INTERVIEW Q&A
# ================================================================================

def print_interview_questions():
    """
    Print common interview questions about tool selection.
    """

    qa = """
    +=========================================================================+
    |                      INTERVIEW Q&A                                     |
    +=========================================================================+

    Q: What is the difference between Grep and Glob?
    +-------------------------------------------------------------------------+
    | A: Grep searches CONTENT inside files (text patterns).                   |
    |    Glob searches by NAME/path (file names and extensions).              |
    |    Use Grep for finding function calls, imports, error messages.        |
    |    Use Glob for finding files by extension or path pattern.              |
    +-------------------------------------------------------------------------+

    Q: When should I use Read vs Grep?
    +-------------------------------------------------------------------------+
    | A: Use Read when you know the specific file path and want to examine    |
    |    its contents. Use Grep when you need to find which files contain     |
    |    specific text. Read first to understand, then Grep to discover.    |
    +-------------------------------------------------------------------------+

    Q: Why are detailed MCP tool descriptions important?
    +-------------------------------------------------------------------------+
    | A: AI has bias toward built-in tools (Grep, Read, etc). Detailed        |
    |    descriptions (3-5 sentences) explain what tool does, when to use,  |
    |    and expected output. This helps AI choose MCP tools over built-ins.  |
    +-------------------------------------------------------------------------+

    Q: When should I build custom MCP tools vs use existing?
    +-------------------------------------------------------------------------+
    | A: Build custom for: team-specific workflows, custom business logic,   |
    |    proprietary systems. Use community servers for: Jira, GitHub, Slack, |
    |    and other standard integrations.                                    |
    +-------------------------------------------------------------------------+

    Q: What is the incremental codebase discovery pattern?
    +-------------------------------------------------------------------------+
    | A: Grep -> Read -> Grep -> Read (alternating). Don't read everything   |
    |    upfront. Start with broad search, then narrow down by reading       |
    |    relevant files, then search again based on discoveries.             |
    +-------------------------------------------------------------------------+

    Q: What are the Edit tool strategies?
    +-------------------------------------------------------------------------+
    | A: (1) Find shortest unique anchor first. (2) Widen old_string if       |
    |    non-unique match. (3) Use Read+Write as last resort when no unique   |
    |    anchor exists.                                                       |
    +-------------------------------------------------------------------------+

    Q: What are the six built-in tools in Claude Code?
    +-------------------------------------------------------------------------+
    | A: Read, Write, Edit, Bash, Grep, Glob. These are always available.    |
    |    MCP tools are additional tools registered with MCP servers.         |
    +-------------------------------------------------------------------------+

    """

    print(qa)


# ================================================================================
# MAIN EXECUTION
# ================================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("TOOL SELECTION AND ROUTING - PRACTICE 01: BUILT-IN TOOLS")
    print("=" * 70)

    # List built-in tools
    print("\n" + "-" * 70)
    print("THE SIX BUILT-IN TOOLS")
    print("-" * 70)

    for i, tool in enumerate(BUILT_IN_TOOLS, 1):
        print(f"\n{i}. {tool.name} ({tool.category})")
        print(f"   {tool.description[:80]}...")

    # Explain Grep vs Glob
    explain_grep_vs_glob()
    demonstrate_grep_vs_glob_use_cases()

    # Enhanced descriptions
    explain_enhanced_descriptions()

    # Build vs Use
    demonstrate_build_vs_use()

    # Incremental discovery
    print("\n".join(IncrementalDiscovery.discover_project_structure()))
    IncrementalDiscovery.example_session()

    # Edit strategies
    EditToolStrategies.demonstrate_edit_patterns()

    # Tool selection matrix
    print_tool_selection_matrix()

    # Interview Q&A
    print_interview_questions()


# ================================================================================
# WHAT WE HAVE LEARNT
# =============================================================================

"""
SUMMARY OF KEY CONCEPTS:

1. THE SIX BUILT-IN TOOLS
   - Read: Read file contents
   - Write: Create/overwrite files
   - Edit: Modify existing files
   - Bash: Execute shell commands
   - Grep: Search CONTENT inside files
   - Glob: Search FILES by NAME/path

2. GREP vs GLOB CORE DISTINCTION
   - Grep: Search INSIDE files (content)
   - Glob: Search BY NAME (paths)
   - Grep finds lines with matching text
   - Glob finds files matching pattern

3. ENHANCED MCP DESCRIPTIONS (3-5 sentences)
   - Explain: what (action), when (trigger), output (result)
   - Prevents built-in tool bias
   - Helps AI choose MCP tools over built-ins

4. BUILD vs USE DECISION
   - Build: Team-specific workflows, custom logic, proprietary systems
   - Use: Standard integrations (Jira, GitHub, Slack, etc)

5. INCREMENTAL CODEBASE DISCOVERY
   - Pattern: Grep -> Read -> Grep -> Read
   - Don't read everything upfront
   - Follow code paths naturally
   - Stop when understanding is complete

6. EDIT TOOL STRATEGIES
   - Shortest unique anchor first
   - Widen old_string if non-unique
   - Read+Write as last resort

7. TOOL SELECTION GUIDANCE
   - Read: For examining specific known files
   - Write: For creating new files
   - Edit: For targeted modifications
   - Bash: For running commands/scripts
   - Grep: For finding content in files
   - Glob: For finding files by name

8. INTERVIEW QUESTIONS

   Q: What's the core difference between Grep and Glob?
   A: Grep searches content inside files, Glob searches by file name/path.

   Q: How do you prevent built-in tool bias?
   A: Write detailed MCP descriptions (3-5 sentences) explaining what,
      when, and output format.

   Q: When should you build vs use existing MCP tools?
   A: Build for team-specific/proprietary, use community servers
      for standard integrations.

   Q: What is the incremental discovery pattern?
   A: Alternating Grep and Read operations: Grep -> Read -> Grep -> Read
      to progressively explore codebase.

   Q: What are the Edit tool strategies?
   A: (1) Find unique anchor, (2) Widen if non-unique, (3) Read+Write last resort.
"""

print()
print("=" * 70)
print("END OF PRACTICE 01: BUILT-IN TOOLS AND TOOL SELECTION")
print("=" * 70)