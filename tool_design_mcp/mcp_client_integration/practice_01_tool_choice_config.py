"""
================================================================================
MCP CLIENT INTEGRATION - PRACTICE 01
================================================================================

WHAT IS TOOL CHOICE CONFIGURATION?
---------------------------------
Tool choice determines HOW the AI model selects which tool to use when
multiple tools are available. This is critical for:

1. Performance: Too many tools degrades selection accuracy
2. Cost: Unnecessary tool calls increase latency and expenses
3. Reliability: Proper configuration ensures correct tool selection

This practice file covers:
1. Tool choice modes: "auto", "any", and forced selection
2. Optimal tool count recommendations (4-5 per agent)
3. Scoped cross-role tools pattern
4. Least privilege tool design
5. Avoiding coordinator bottlenecks

================================================================================
"""

# ================================================================================
# SECTION 1: ENVIRONMENT SETUP
# ================================================================================

import os
import json
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Configure model and API settings
MODEL_NAME = "claude-haiku-4-5-20250601"
API_KEY = os.getenv("ANTHROPIC_API_KEY", "")


# ================================================================================
# SECTION 2: TOOL CHOICE MODES EXPLAINED
# ================================================================================

class ToolChoiceMode(Enum):
    """
    Three modes for controlling how AI selects tools.

    MODE COMPARISON:
    +-----------+------------+----------------+------------------+
    | Mode      | AI Decides | Must Call Tool | Use Case         |
    +-----------+------------+----------------+------------------+
    | "auto"    | Yes        | No (optional)  | Flexible tasks   |
    | "any"     | Yes        | Yes (any one)  | Multi-tool tasks |
    | forced    | No         | Yes (specific) | Constrained flow |
    +-----------+------------+----------------+------------------+
    """

    AUTO = "auto"           # Model decides if/which tool to use
    ANY = "any"            # Must call tool, model chooses which
    NONE = "none"          # No tools available (baseline)


@dataclass
class ToolChoiceConfig:
    """
    Configuration for tool selection behavior.

    ATTRIBUTES:
        mode: One of "auto", "any", or tool name for forced selection
        tool_count: Number of tools available (affects selection accuracy)
        expected_tools: List of tools the task might need

    IMPORTANT INSIGHT:
    When tool_count > 18, selection accuracy degrades significantly.
    Keep each agent's tool set to 4-5 tools maximum.
    """
    mode: str = "auto"
    tool_count: int = 1
    expected_tools: List[str] = None

    def __post_init__(self):
        if self.expected_tools is None:
            self.expected_tools = []


# ================================================================================
# SECTION 3: TOOL DEFINITION STRUCTURE
# ================================================================================

@dataclass
class MCPtool:
    """
    MCP Tool definition for client integration.

    ATTRIBUTES:
        name: Unique identifier for the tool
        description: Detailed description (3-5 sentences for best results)
                   This helps AI understand when to use the tool
        input_schema: JSON schema for parameters
        category: Tool category for grouping

    BEST PRACTICE: Write descriptions that explain:
    - What the tool does (action)
    - When to use it (trigger)
    - What output to expect (result)
    """
    name: str
    description: str
    input_schema: Dict[str, Any]
    category: str = "general"


# ================================================================================
# SECTION 4: TOOL CATEGORIES FOR DIFFERENT AGENTS
# ================================================================================

# SCENARIO: We have multiple specialized agents:
# - Web Search Agent: Finds and retrieves web content
# - Document Analysis Agent: Processes and extracts info from documents
# - Synthesis Agent: Combines information into reports
# - Coordinator Agent: Orchestrates other agents

# Each agent gets a SCOPED set of tools (not all tools)

# WEB SEARCH AGENT TOOLS (4 tools - optimal count)
WEB_SEARCH_TOOLS = [
    MCPtool(
        name="search_web",
        description="Search the web for information on a topic. "
                   "Use when you need current events, facts, or data not in the codebase. "
                   "Returns list of relevant URLs and summaries. "
                   "Best for general queries and topic exploration.",
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "max_results": {"type": "number", "default": 10}
            },
            "required": ["query"]
        },
        category="web"
    ),
    MCPtool(
        name="fetch_page",
        description="Retrieve the full content of a web page from a URL. "
                   "Use after search_web when you need detailed information from a result. "
                   "Returns page content and metadata. "
                   "Best for extracting full articles or documentation.",
        input_schema={
            "type": "object",
            "properties": {
                "url": {"type": "string"},
                "max_length": {"type": "number", "default": 5000}
            },
            "required": ["url"]
        },
        category="web"
    ),
    MCPtool(
        name="extract_links",
        description="Extract all hyperlinks from a web page. "
                   "Use when you need to discover related pages or navigation structure. "
                   "Returns list of URLs and link text. "
                   "Best for sitemap discovery and link analysis.",
        input_schema={
            "type": "object",
            "properties": {
                "url": {"type": "string"},
                "filter_pattern": {"type": "string", "default": ""}
            },
            "required": ["url"]
        },
        category="web"
    ),
    MCPtool(
        name="save_snippet",
        description="Save a text snippet to persistent storage for later use. "
                   "Use when you find information worth referencing in final output. "
                   "Returns confirmation with snippet ID. "
                   "Best for collecting evidence and citations.",
        input_schema={
            "type": "object",
            "properties": {
                "content": {"type": "string"},
                "source_url": {"type": "string"},
                "tags": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["content"]
        },
        category="web"
    )
]

# DOCUMENT ANALYSIS AGENT TOOLS (4 tools - optimal count)
DOCUMENT_TOOLS = [
    MCPtool(
        name="extract_metadata",
        description="Extract metadata from a document (author, date, version, etc). "
                   "Use when you need document provenance or version info. "
                   "Returns dictionary of metadata fields. "
                   "Best for document verification and source attribution.",
        input_schema={
            "type": "object",
            "properties": {
                "file_path": {"type": "string"}
            },
            "required": ["file_path"]
        },
        category="document"
    ),
    MCPtool(
        name="extract_data_points",
        description="Extract structured data points from unstructured text. "
                   "Use when you need to convert prose to tabular data. "
                   "Returns list of extracted entities and values. "
                   "Best for converting articles to structured formats.",
        input_schema={
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "schema": {"type": "object"},
                "precision": {"type": "number", "default": 0.9}
            },
            "required": ["text"]
        },
        category="document"
    ),
    MCPtool(
        name="summarize_content",
        description="Generate a concise summary of document content. "
                   "Use when full content is too long for context. "
                   "Returns summary with key points. "
                   "Best for condensing lengthy documents.",
        input_schema={
            "type": "object",
            "properties": {
                "content": {"type": "string"},
                "max_length": {"type": "number", "default": 200},
                "focus": {"type": "string", "default": ""}
            },
            "required": ["content"]
        },
        category="document"
    ),
    MCPtool(
        name="verify_claim",
        description="Verify a factual claim against document corpus. "
                   "Use when you need to confirm if information is in documents. "
                   "Returns verification status and supporting excerpts. "
                   "Best for fact-checking and claim validation.",
        input_schema={
            "type": "object",
            "properties": {
                "claim": {"type": "string"},
                "corpus_id": {"type": "string", "default": "default"}
            },
            "required": ["claim"]
        },
        category="document"
    )
]

# SYNTHESIS AGENT TOOLS (4 tools - scoped)
# NOTE: This agent has a SCOPED version of verify_fact instead of routing
# through coordinator. This is a key optimization pattern.
SYNTHESIS_TOOLS = [
    MCPtool(
        name="compile_report",
        description="Compile multiple data sources into a structured report. "
                   "Use when you have gathered information and need formatted output. "
                   "Returns formatted report with sections and citations. "
                   "Best for final output generation.",
        input_schema={
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "sections": {"type": "array"},
                "format": {"type": "string", "default": "markdown"}
            },
            "required": ["title", "sections"]
        },
        category="synthesis"
    ),
    MCPtool(
        name="verify_fact",
        description="Verify a factual claim using scoped local verification. "
                   "Use when synthesis agent needs to confirm facts before including. "
                   "This is a SCOPED version - only checks local summaries, not full corpus. "
                   "Returns verification status with confidence score. "
                   "Best for quick fact validation during synthesis.",
        input_schema={
            "type": "object",
            "properties": {
                "fact": {"type": "string"},
                "expected_value": {"type": "string"}
            },
            "required": ["fact"]
        },
        category="synthesis"
    ),
    MCPtool(
        name="format_citation",
        description="Format a citation in various citation styles (APA, MLA, Chicago, etc). "
                   "Use when you need properly formatted references. "
                   "Returns formatted citation string. "
                   "Best for academic or professional documents.",
        input_schema={
            "type": "object",
            "properties": {
                "source": {"type": "string"},
                "style": {"type": "string", "default": "APA"},
                "include_url": {"type": "boolean", "default": True}
            },
            "required": ["source"]
        },
        category="synthesis"
    ),
    MCPtool(
        name="assess_coverage",
        description="Assess how well gathered information covers the topic. "
                   "Use when you need to know if more research is needed. "
                   "Returns coverage score and identified gaps. "
                   "Best for quality assurance before finalizing report.",
        input_schema={
            "type": "object",
            "properties": {
                "topic": {"type": "string"},
                "gathered_items": {"type": "array"}
            },
            "required": ["topic"]
        },
        category="synthesis"
    )
]

# COORDINATOR AGENT TOOLS (3 tools - minimal)
# COORDINATOR SHOULD NOT route all traffic - give it direct capabilities
COORDINATOR_TOOLS = [
    MCPtool(
        name="delegate_task",
        description="Delegate a subtask to another specialized agent. "
                   "Use when the task requires capabilities of another agent type. "
                   "Returns agent response and status. "
                   "Best for breaking complex tasks into parallel subtasks.",
        input_schema={
            "type": "object",
            "properties": {
                "agent_type": {"type": "string"},
                "task_description": {"type": "string"},
                "context": {"type": "object"}
            },
            "required": ["agent_type", "task_description"]
        },
        category="coordination"
    ),
    MCPtool(
        name="review_output",
        description="Review output from another agent for quality and completeness. "
                   "Use when you need to validate agent work before proceeding. "
                   "Returns review score and improvement suggestions. "
                   "Best for quality gates between agent steps.",
        input_schema={
            "type": "object",
            "properties": {
                "output": {"type": "string"},
                "criteria": {"type": "array"}
            },
            "required": ["output"]
        },
        category="coordination"
    ),
    MCPtool(
        name="request_revision",
        description="Request an agent to revise its output based on feedback. "
                   "Use when review_output found issues to fix. "
                   "Returns revision status and updated output. "
                   "Best for iterative refinement of agent work.",
        input_schema={
            "type": "object",
            "properties": {
                "agent_id": {"type": "string"},
                "feedback": {"type": "string"},
                "priority": {"type": "string", "default": "normal"}
            },
            "required": ["agent_id", "feedback"]
        },
        category="coordination"
    )
]


# ================================================================================
# SECTION 5: TOOL SELECTION OPTIMIZATION TABLE
# ================================================================================

def print_tool_selection_guide():
    """
    Print comprehensive guide for tool selection optimization.
    This table shows recommended tool counts and scoping strategies.
    """

    guide = """
    +=========================================================================+
    |              TOOL SELECTION OPTIMIZATION GUIDE                         |
    +=========================================================================+

    RECOMMENDED TOOL COUNT PER AGENT: 4-5 tools (NOT 18+)

    | Agent Role          | Tool Count | Tools Included                          |
    |---------------------|------------|----------------------------------------|
    | Web Search          |     4      | search_web, fetch_page, extract_links,  |
    |                     |            | save_snippet                            |
    |---------------------|------------|----------------------------------------|
    | Document Analysis   |     4      | extract_metadata, extract_data_points,  |
    |                     |            | summarize_content, verify_claim         |
    |---------------------|------------|----------------------------------------|
    | Synthesis           |     4      | compile_report, verify_fact (scoped),   |
    |                     |            | format_citation, assess_coverage        |
    |---------------------|------------|----------------------------------------|
    | Coordinator         |     3      | delegate_task, review_output,           |
    |                     |            | request_revision                        |
    +---------------------+------------+----------------------------------------+

    WHY 4-5 TOOLS?

    Research shows that AI tool selection accuracy degrades when:
    - More than 18 tools are available to a single agent
    - Tools have similar purposes without clear distinction
    - Descriptions are too brief or generic

    BEST PRACTICES:

    1. SCOPED CROSS-ROLE TOOLS
       +------------------------------------------+
       | Bad: Coordinator routes everything       |
       |   Coordinator -> Web Search Agent       |
       |   Coordinator -> Doc Analysis Agent      |
       |   (Adds 2-3 round trips, 40% latency)    |
       +------------------------------------------+

       +------------------------------------------+
       | Good: Synthesis gets scoped tools        |
       |   Synthesis has verify_fact (scoped)    |
       |   No coordinator routing needed         |
       |   (Faster, less latency)                 |
       +------------------------------------------+

    2. LEAST PRIVILEGE TOOL DESIGN
       +------------------------------------------+
       | Bad: Generic tool with all permissions  |
       |   "database": Full read/write/delete     |
       |   (Too much power, hard to audit)        |
       +------------------------------------------+

       +------------------------------------------+
       | Good: Constrained scoped tools           |
       |   "read_user_profile": Read only         |
       |   "update_preferences": Write prefs     |
       |   (Auditable, minimal blast radius)     |
       +------------------------------------------+

    3. DESCRIPTIVE TOOL NAMES
       +------------------------------------------+
       | Bad: Generic names                       |
       |   "search", "get", "do", "process"      |
       |   (Confusing for AI selection)          |
       +------------------------------------------+

       +------------------------------------------+
       | Good: Action-object names                |
       |   "search_codebase", "fetch_page",       |
       |   "extract_metadata", "verify_claim"    |
       |   (Clear purpose, easy selection)       |
       +------------------------------------------+
    """

    print(guide)


# ================================================================================
# SECTION 6: CLIENT IMPLEMENTATION EXAMPLE
# ================================================================================

class MCPClient:
    """
    MCP Client for integrating with MCP servers.

    RESPONSIBILITIES:
    - Configure tool choice behavior per request
    - Handle tool execution and response parsing
    - Manage authentication headers
    - Handle errors with proper retry logic
    """

    def __init__(self, api_key: str, model: str = MODEL_NAME):
        self.api_key = api_key
        self.model = model
        self.default_tools: List[MCPtool] = []

        print(f"MCP Client initialized with model: {self.model}")

    def configure_tools(
        self,
        tools: List[MCPtool],
        tool_choice: str = "auto"
    ) -> Dict[str, Any]:
        """
        Configure tools and tool choice for a request.

        ARGS:
            tools: List of MCPtool definitions
            tool_choice: "auto", "any", or specific tool name

        RETURNS:
            Tool configuration dictionary for API call

        IMPORTANT: tool_choice affects how AI selects tools:
        - "auto": AI decides if/how to use tools (default, most flexible)
        - "any": AI must call a tool and chooses which (good for routing)
        - "<tool_name>": AI must call that specific tool (forced selection)
        """
        self.default_tools = tools

        config = {
            "tools": [
                {
                    "name": t.name,
                    "description": t.description,
                    "input_schema": t.input_schema
                }
                for t in tools
            ],
            "tool_choice": {
                "type": tool_choice
            }
        }

        print(f"Configured {len(tools)} tools with tool_choice='{tool_choice}'")
        return config

    def execute_request(
        self,
        prompt: str,
        tools: Optional[List[MCPtool]] = None,
        tool_choice: str = "auto"
    ) -> Dict[str, Any]:
        """
        Execute a request with tool configuration.

        ARGS:
            prompt: User prompt/query
            tools: Optional tool list (uses default if not provided)
            tool_choice: Tool selection mode

        RETURNS:
            Response dictionary with tool calls and results

        NOTE: In production, this would call the actual MCP API.
        This example shows the configuration structure.
        """

        # Use provided tools or fall back to defaults
        active_tools = tools if tools is not None else self.default_tools

        # Build request configuration
        request_config = self.configure_tools(active_tools, tool_choice)

        # Simulated response structure
        response = {
            "model": self.model,
            "tool_config": request_config,
            "tool_choice_mode": tool_choice,
            "tool_count": len(active_tools),
            "status": "configured"
        }

        print(f"Request configured: {len(active_tools)} tools, mode={tool_choice}")

        return response


# ================================================================================
# SECTION 7: TOOL CHOICE SCENARIOS
# ================================================================================

def demonstrate_tool_choice_scenarios():
    """
    Demonstrate different tool choice configurations for various scenarios.
    """

    print("\n" + "=" * 70)
    print("TOOL CHOICE CONFIGURATION SCENARIOS")
    print("=" * 70)

    # Create client
    client = MCPClient(api_key=API_KEY, model=MODEL_NAME)

    # Scenario 1: Flexible search (auto mode)
    print("\n" + "-" * 70)
    print("Scenario 1: User asks a general question")
    print("Prompt: 'What are the latest developments in AI?'")
    print("-" * 70)

    response = client.execute_request(
        prompt="What are the latest developments in AI?",
        tools=WEB_SEARCH_TOOLS,
        tool_choice="auto"  # AI decides if tool needed
    )

    print(f"Tool Choice Mode: {response['tool_choice_mode']}")
    print(f"Tool Count: {response['tool_count']}")
    print(f"Result: AI may or may not call a tool based on its knowledge")

    # Scenario 2: Must search (any mode)
    print("\n" + "-" * 70)
    print("Scenario 2: Task requires external data")
    print("Prompt: 'Find and summarize today's top 5 tech news'")
    print("-" * 70)

    response = client.execute_request(
        prompt="Find and summarize today's top 5 tech news",
        tools=WEB_SEARCH_TOOLS,
        tool_choice="any"  # AI must call a tool
    )

    print(f"Tool Choice Mode: {response['tool_choice_mode']}")
    print(f"Tool Count: {response['tool_count']}")
    print(f"Result: AI will call appropriate tool (search_web likely)")

    # Scenario 3: Forced tool selection
    print("\n" + "-" * 70)
    print("Scenario 3: Specific tool required")
    print("Prompt: 'Extract all links from https://example.com'")
    print("-" * 70)

    response = client.execute_request(
        prompt="Extract all links from https://example.com",
        tools=WEB_SEARCH_TOOLS,
        tool_choice="extract_links"  # Force specific tool
    )

    print(f"Tool Choice Mode: {response['tool_choice_mode']}")
    print(f"Forced Tool: extract_links")
    print(f"Result: AI must use extract_links tool")

    # Scenario 4: Multi-agent coordination
    print("\n" + "-" * 70)
    print("Scenario 4: Multi-agent task with scoped tools")
    print("Prompt: 'Research topic X and create a report with verified facts'")
    print("-" * 70)

    # Web search agent
    print("\n[Web Search Agent]")
    response1 = client.execute_request(
        prompt="Research topic X",
        tools=WEB_SEARCH_TOOLS,
        tool_choice="auto"
    )
    print(f"  Tools: {[t.name for t in WEB_SEARCH_TOOLS]}")

    # Synthesis agent (with scoped verify_fact)
    print("\n[Synthesis Agent]")
    response2 = client.execute_request(
        prompt="Create report with verified facts",
        tools=SYNTHESIS_TOOLS,
        tool_choice="auto"
    )
    print(f"  Tools: {[t.name for t in SYNTHESIS_TOOLS]}")
    print(f"  Note: Synthesis has local verify_fact (scoped), no coordinator needed!")

    # Coordinator
    print("\n[Coordinator Agent]")
    response3 = client.execute_request(
        prompt="Review and coordinate agent outputs",
        tools=COORDINATOR_TOOLS,
        tool_choice="any"
    )
    print(f"  Tools: {[t.name for t in COORDINATOR_TOOLS]}")


# ================================================================================
# SECTION 8: ANTI-PATTERNS TO AVOID
# ================================================================================

def print_anti_patterns():
    """
    Print common mistakes in tool configuration.
    """

    anti_patterns = """
    +=========================================================================+
    |                    COMMON ANTI-PATTERNS                                |
    +=========================================================================+

    ANTI-PATTERN 1: Too Many Tools per Agent
    +---------------------------------------------------------------------+
    | Problem: Giving one agent 18+ tools degrades selection accuracy.   |
    |          AI has difficulty distinguishing similar tools.           |
    |                                                                    |
    | Bad:                                                                    |
    |   Agent has: search, search_specific, search_generic, web_search,   |
    |             file_search, code_search, semantic_search...            |
    |                                                                    |
    | Good:                                                                    |
    |   Agent has: search_codebase, fetch_page, extract_links,           |
    |             save_snippet (4-5 clear tools)                          |
    +---------------------------------------------------------------------+

    ANTI-PATTERN 2: Routing Through Coordinator
    +---------------------------------------------------------------------+
    | Problem: Every tool call goes through coordinator, adding latency. |
    |          2-3 extra round trips, 40% more latency.                  |
    |                                                                    |
    | Bad:                                                                    |
    |   User -> Coordinator -> Web Search (round trip 1)                 |
    |        -> Coordinator -> Doc Analysis (round trip 2)              |
    |        -> Coordinator -> Synthesis (round trip 3)                  |
    |                                                                    |
    | Good:                                                                    |
    |   User -> Web Search -> Doc Analysis -> Synthesis                  |
    |        (direct calls, no coordinator bottleneck)                   |
    +---------------------------------------------------------------------+

    ANTI-PATTERN 3: Generic Tool Names
    +---------------------------------------------------------------------+
    | Problem: AI cannot distinguish tools with similar names.          |
    |          "do_something" tells nothing about purpose.               |
    |                                                                    |
    | Bad:                                                                    |
    |   "search", "get", "process", "handle", "do"                        |
    |                                                                    |
    | Good:                                                                    |
    |   "search_codebase", "get_user_profile", "process_payment",        |
    |   "handle_webhook", "do_health_check"                              |
    +---------------------------------------------------------------------+

    ANTI-PATTERN 4: Generic Permissions
    +---------------------------------------------------------------------+
    | Problem: Tools with too many permissions are hard to audit.        |
    |          Security risk: one compromised tool = full access.       |
    |                                                                    |
    | Bad:                                                                    |
    |   "database": ALL operations (read, write, delete, admin)           |
    |                                                                    |
    | Good:                                                                    |
    |   "read_user_profile": Read-only user data                         |
    |   "update_user_preferences": Write-only preferences                |
    |   "list_user_sessions": Read-only session listing                  |
    +---------------------------------------------------------------------+

    ANTI-PATTERN 5: Brief Tool Descriptions
    +---------------------------------------------------------------------+
    | Problem: AI cannot decide when to use tool without clear desc.    |
    |          Descriptions should be 3-5 sentences, not 5 words.        |
    |                                                                    |
    | Bad:                                                                    |
    |   "Search for files matching pattern" (too brief)                 |
    |                                                                    |
    | Good:                                                                    |
    |   "Search for files matching a pattern in the repository.          |
    |    Use when you need to find files containing specific text,      |
    |    function names, or error messages. Returns list of files       |
    |    with line numbers and matching context. Best for locating       |
    |    code references across multiple files." (detailed)              |
    +---------------------------------------------------------------------+

    """

    print(anti_patterns)


# ================================================================================
# SECTION 9: INTERVIEW Q&A
# ================================================================================

def print_interview_questions():
    """
    Print common interview questions and answers about tool choice config.
    """

    qa = """
    +=========================================================================+
    |                      INTERVIEW Q&A                                     |
    +=========================================================================+

    Q: What is the difference between tool_choice "auto" and "any"?
    +-------------------------------------------------------------------------+
    | A: "auto" means AI decides WHETHER to call a tool (may answer from     |
    |    knowledge). "any" means AI MUST call a tool and chooses which one.   |
    |    Use "auto" for flexible tasks, "any" when tool is necessary.        |
    +-------------------------------------------------------------------------+

    Q: Why is 4-5 tools the recommended count per agent?
    +-------------------------------------------------------------------------+
    | A: Research shows AI tool selection accuracy degrades with 18+ tools.   |
    |    With too many similar tools, AI cannot reliably choose the correct   |
    |    one. Fewer specialized tools improves selection accuracy.            |
    +-------------------------------------------------------------------------+

    Q: What is scoped cross-role tool design?
    +-------------------------------------------------------------------------+
    | A: Instead of routing all calls through a coordinator agent, give each  |
    |    agent the specific tools it needs directly. For example, synthesis  |
    |    agent gets a scoped verify_fact instead of calling coordinator.     |
    |    This reduces latency by 40% (no coordinator round trips).            |
    +-------------------------------------------------------------------------+

    Q: What is least privilege tool design?
    +-------------------------------------------------------------------------+
    | A: Tools should have minimal permissions - only what's needed for      |
    |    their function. Instead of one "database" tool with all permissions, |
    |    create separate "read_user", "update_preferences" tools.            |
    +-------------------------------------------------------------------------+

    Q: How do you handle tools with overlapping functionality?
    +-------------------------------------------------------------------------+
    | A: Either: (1) Merge into one tool with parameters, or (2) Make them   |
    |    distinctly different with clear use cases in descriptions.          |
    |    Overlap causes confusion in tool selection.                          |
    +-------------------------------------------------------------------------+

    Q: When would you use forced tool selection?
    +-------------------------------------------------------------------------+
    | A: Use when a specific tool MUST be called for workflow requirements.   |
    |    Example: "Extract links" must be used before "Fetch page" in a      |
    |    scraping workflow. Forces AI to follow the correct sequence.        |
    +-------------------------------------------------------------------------+

    """

    print(qa)


# ================================================================================
# SECTION 10: DEMONSTRATION AND MAIN
# ================================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("MCP CLIENT INTEGRATION - PRACTICE 01: TOOL CHOICE CONFIGURATION")
    print("=" * 70)

    # Print tool selection guide
    print_tool_selection_guide()

    # Print anti-patterns
    print_anti_patterns()

    # Print interview Q&A
    print_interview_questions()

    # Run scenario demonstrations
    demonstrate_tool_choice_scenarios()

    # Print summary of all tool sets
    print("\n" + "=" * 70)
    print("TOOL SET SUMMARY")
    print("=" * 70)

    print("\nWeb Search Agent (4 tools):")
    for tool in WEB_SEARCH_TOOLS:
        print(f"  - {tool.name}")

    print("\nDocument Analysis Agent (4 tools):")
    for tool in DOCUMENT_TOOLS:
        print(f"  - {tool.name}")

    print("\nSynthesis Agent (4 tools - scoped):")
    for tool in SYNTHESIS_TOOLS:
        print(f"  - {tool.name}")

    print("\nCoordinator Agent (3 tools):")
    for tool in COORDINATOR_TOOLS:
        print(f"  - {tool.name}")

    print("\nTotal tools across all agents: ", end="")
    total = len(WEB_SEARCH_TOOLS) + len(DOCUMENT_TOOLS) + len(SYNTHESIS_TOOLS) + len(COORDINATOR_TOOLS)
    print(f"{total} (each agent has only 3-4, never 18+)")


# ================================================================================
# WHAT WE HAVE LEARNT
# =============================================================================

"""
SUMMARY OF KEY CONCEPTS:

1. TOOL CHOICE MODES
   - "auto": AI decides if/how to use tools (default, most flexible)
   - "any": AI must call a tool and chooses which (good for multi-tool tasks)
   - "<name>": AI must call specific tool (forced selection)

2. OPTIMAL TOOL COUNT
   - Recommended: 4-5 tools per agent
   - Problem: 18+ tools degrades selection accuracy
   - Solution: Scoped tools per agent role

3. SCOPED CROSS-ROLE TOOLS
   - Give agents tools they need directly
   - Avoid routing through coordinator
   - Reduces latency by 40% (no extra round trips)

4. LEAST PRIVILEGE TOOL DESIGN
   - Replace generic tools with constrained versions
   - Auditable permissions per tool
   - Minimal blast radius on compromise

5. TOOL DESCRIPTION BEST PRACTICES
   - 3-5 sentences (not 5 words)
   - Explain: what, when, output format
   - Prevent built-in tool bias with enhanced descriptions

6. ANTI-PATTERNS TO AVOID
   - Too many tools per agent
   - Routing through coordinator
   - Generic tool names
   - Generic permissions
   - Brief descriptions

7. TOOL SELECTION TABLE
   +------------------+------------------------------------+
   | Agent            | Scoped Tools                       |
   +------------------+------------------------------------+
   | Web Search       | search_web, fetch_page,            |
   |                  | extract_links, save_snippet        |
   +------------------+------------------------------------+
   | Document         | extract_metadata,                  |
   |                  | extract_data_points,               |
   |                  | summarize_content, verify_claim   |
   +------------------+------------------------------------+
   | Synthesis        | compile_report, verify_fact,      |
   |                  | format_citation, assess_coverage  |
   +------------------+------------------------------------+
   | Coordinator      | delegate_task, review_output,     |
   |                  | request_revision                  |
   +------------------+------------------------------------+

8. COMMON INTERVIEW QUESTIONS

   Q: How does "auto" differ from "any" tool_choice?
   A: "auto" lets AI decide to NOT call tools if it knows answer.
      "any" forces tool usage (AI must call something).

   Q: Why limit to 4-5 tools per agent?
   A: Tool selection accuracy degrades with 18+ tools.

   Q: What is the coordinator bottleneck problem?
   A: Routing all calls through coordinator adds 2-3 round trips
      and 40% latency. Solution: direct scoped tools.

   Q: What is least privilege in tool design?
   A: Tools should have minimal permissions needed for function.
      Not one "admin" tool, but several scoped tools.
"""

print()
print("=" * 70)
print("END OF PRACTICE 01: TOOL CHOICE CONFIGURATION")
print("=" * 70)