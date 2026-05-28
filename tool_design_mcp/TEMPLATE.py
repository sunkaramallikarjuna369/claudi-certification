"""
================================================================================
MCP TOOL DESIGN - COMPREHENSIVE TEMPLATE
================================================================================

This template demonstrates all patterns covered in the MCP tool design course:
- MCP Server Implementation
- Tool Choice Configuration
- Structured Error Handling
- Tool Selection and Routing
- Built-in Tools Usage

MODEL: claude-haiku-4-5-20250601

================================================================================
"""

# ================================================================================
# SECTION 1: ENVIRONMENT SETUP AND IMPORTS
# ================================================================================

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Configure API settings
MODEL_NAME = "claude-haiku-4-5-20250601"
API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# ================================================================================
# SECTION 2: ERROR CATEGORIES AND STRUCTURED RESPONSES
# ================================================================================

class ErrorCategory(Enum):
    """
    Four distinct error categories in MCP protocol.

    +------------------+-------------+----------------------------------------+
    | Category         | isRetryable | Common Causes                          |
    +------------------+-------------+----------------------------------------+
    | TRANSIENT        | TRUE        | Timeouts, rate limits, unavailability  |
    | VALIDATION       | TRUE        | Invalid input, missing fields          |
    | BUSINESS         | FALSE       | Policy violations, limit exceedances   |
    | PERMISSION       | FALSE       | Access denied, invalid credentials     |
    +------------------+-------------+----------------------------------------+
    """

    TRANSIENT = "transient"
    VALIDATION = "validation"
    BUSINESS = "business"
    PERMISSION = "permission"


@dataclass
class MCPError:
    """
    Structured error object for MCP protocol.

    REQUIRED FIELDS:
    - isError: Boolean (always True for errors)
    - errorCategory: String from ErrorCategory enum
    - isRetryable: Boolean (True only for transient/validation)
    - description: Human-readable explanation

    OPTIONAL FIELDS:
    - code: Programmatic error code
    - details: Additional context for debugging
    - timestamp: When error occurred
    """

    isError: bool = True
    errorCategory: str = "transient"
    isRetryable: bool = True
    description: str = ""
    code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for JSON serialization."""
        result = {
            "isError": self.isError,
            "errorCategory": self.errorCategory,
            "isRetryable": self.isRetryable,
            "description": self.description
        }
        if self.code:
            result["code"] = self.code
        if self.details:
            result["details"] = self.details
        result["timestamp"] = self.timestamp
        return result


class ErrorFactory:
    """
    Factory class for creating standardized MCP errors.

    USE THESE FACTORY METHODS INSTEAD OF DIRECT INSTANTIATION
    for consistent error structure across the codebase.
    """

    # TRANSIENT ERRORS (can retry)
    @staticmethod
    def timeout(message: str = "Request timed out", details: Optional[Dict] = None) -> MCPError:
        return MCPError(
            isError=True,
            errorCategory=ErrorCategory.TRANSIENT.value,
            isRetryable=True,
            description=message,
            code="TIMEOUT",
            details=details
        )

    @staticmethod
    def rate_limit_exceeded(retry_after: Optional[int] = None) -> MCPError:
        msg = "Rate limit exceeded"
        if retry_after:
            msg += f". Retry after {retry_after} seconds"
        return MCPError(
            isError=True,
            errorCategory=ErrorCategory.TRANSIENT.value,
            isRetryable=True,
            description=msg,
            code="RATE_LIMITED",
            details={"retry_after": retry_after}
        )

    @staticmethod
    def service_unavailable(service: str) -> MCPError:
        return MCPError(
            isError=True,
            errorCategory=ErrorCategory.TRANSIENT.value,
            isRetryable=True,
            description=f"Service '{service}' is temporarily unavailable",
            code="SERVICE_UNAVAILABLE"
        )

    # VALIDATION ERRORS (fix and retry)
    @staticmethod
    def invalid_input(field_name: str, reason: str) -> MCPError:
        return MCPError(
            isError=True,
            errorCategory=ErrorCategory.VALIDATION.value,
            isRetryable=True,
            description=f"Invalid input for '{field_name}': {reason}",
            code="INVALID_INPUT",
            details={"field": field_name}
        )

    @staticmethod
    def missing_field(field_name: str) -> MCPError:
        return MCPError(
            isError=True,
            errorCategory=ErrorCategory.VALIDATION.value,
            isRetryable=True,
            description=f"Missing required field: '{field_name}'",
            code="MISSING_FIELD",
            details={"field": field_name}
        )

    # BUSINESS ERRORS (never retry)
    @staticmethod
    def policy_violation(policy_name: str, reason: str) -> MCPError:
        return MCPError(
            isError=True,
            errorCategory=ErrorCategory.BUSINESS.value,
            isRetryable=False,
            description=f"Policy violation: {policy_name}. {reason}",
            code="POLICY_VIOLATION",
            details={"policy": policy_name}
        )

    @staticmethod
    def limit_exceeded(limit_type: str, current: int, maximum: int) -> MCPError:
        return MCPError(
            isError=True,
            errorCategory=ErrorCategory.BUSINESS.value,
            isRetryable=False,
            description=f"Limit exceeded: {limit_type} ({current}/{maximum})",
            code="LIMIT_EXCEEDED",
            details={"current": current, "maximum": maximum}
        )

    # PERMISSION ERRORS (never retry)
    @staticmethod
    def access_denied(resource: str, reason: str = "Insufficient permissions") -> MCPError:
        return MCPError(
            isError=True,
            errorCategory=ErrorCategory.PERMISSION.value,
            isRetryable=False,
            description=f"Access denied to '{resource}': {reason}",
            code="ACCESS_DENIED"
        )

    @staticmethod
    def invalid_credentials() -> MCPError:
        return MCPError(
            isError=True,
            errorCategory=ErrorCategory.PERMISSION.value,
            isRetryable=False,
            description="Authentication failed: Invalid credentials",
            code="INVALID_CREDENTIALS"
        )


# ================================================================================
# SECTION 3: TOOL DEFINITIONS AND SCHEMAS
# ================================================================================

@dataclass
class MCPtool:
    """
    MCP Tool definition.

    ATTRIBUTES:
    - name: Unique identifier
    - description: 3-5 sentences explaining what/when/output
    - input_schema: JSON schema for parameters
    - category: Tool category for grouping

    BEST PRACTICE: Write descriptions that prevent built-in tool bias.
    """

    name: str
    description: str
    input_schema: Dict[str, Any]
    category: str = "general"


class ToolRegistry:
    """
    Central registry for MCP tools.

    PURPOSE: Allows AI to discover available tools and their capabilities.
    """

    def __init__(self):
        self.tools: Dict[str, MCPtool] = {}
        self.categories: Dict[str, List[str]] = {}

    def register(self, tool: MCPtool):
        """Register a tool with the registry."""
        self.tools[tool.name] = tool
        category = tool.category
        if category not in self.categories:
            self.categories[category] = []
        self.categories[category].append(tool.name)

    def get(self, name: str) -> Optional[MCPtool]:
        """Get tool by name."""
        return self.tools.get(name)

    def list_by_category(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """List tools, optionally filtered by category."""
        if category:
            names = self.categories.get(category, [])
            tools = [self.tools[n] for n in names if n in self.tools]
        else:
            tools = list(self.tools.values())

        return [
            {
                "name": t.name,
                "description": t.description,
                "input_schema": t.input_schema
            }
            for t in tools
        ]


# ================================================================================
# SECTION 4: TOOL CHOICE CONFIGURATION
# ================================================================================

class ToolChoiceMode(Enum):
    """
    Three modes for controlling AI tool selection.

    +-----------+------------+----------------+------------------+
    | Mode      | AI Decides | Must Call Tool | Use Case         |
    +-----------+------------+----------------+------------------+
    | "auto"    | Yes        | No (optional)  | Flexible tasks   |
    | "any"     | Yes        | Yes (any one)  | Multi-tool tasks |
    | forced    | No         | Yes (specific) | Constrained flow |
    +-----------+------------+----------------+------------------+
    """

    AUTO = "auto"
    ANY = "any"
    NONE = "none"


@dataclass
class ToolChoiceConfig:
    """
    Configuration for tool selection behavior.

    RECOMMENDATIONS:
    - 4-5 tools per agent (NOT 18+)
    - Scoped cross-role tools (avoid coordinator routing)
    - Least privilege tool design
    """

    mode: str = "auto"
    tool_count: int = 1
    expected_tools: List[str] = field(default_factory=list)


# ================================================================================
# SECTION 5: EXAMPLE TOOL SETS FOR MULTI-AGENT ARCHITECTURE
# ================================================================================

# Web Search Agent Tools (4 tools - optimal count)
WEB_SEARCH_TOOLS = [
    MCPtool(
        name="search_web",
        description="Search the web for information on a topic. Use when you need "
                   "current events, facts, or data not in the codebase. Returns list "
                   "of relevant URLs and summaries. Best for general queries.",
        input_schema={
            "type": "object",
            "properties": {"query": {"type": "string"}, "max_results": {"type": "number"}},
            "required": ["query"]
        },
        category="web"
    ),
    MCPtool(
        name="fetch_page",
        description="Retrieve the full content of a web page from a URL. Use after "
                   "search_web when you need detailed information. Returns page "
                   "content and metadata. Best for extracting articles or docs.",
        input_schema={
            "type": "object",
            "properties": {"url": {"type": "string"}, "max_length": {"type": "number"}},
            "required": ["url"]
        },
        category="web"
    ),
    MCPtool(
        name="extract_links",
        description="Extract all hyperlinks from a web page. Use when you need to "
                   "discover related pages. Returns list of URLs and link text.",
        input_schema={
            "type": "object",
            "properties": {"url": {"type": "string"}, "filter_pattern": {"type": "string"}},
            "required": ["url"]
        },
        category="web"
    ),
    MCPtool(
        name="save_snippet",
        description="Save a text snippet to persistent storage for later use. Use when "
                   "you find information worth referencing. Returns snippet ID.",
        input_schema={
            "type": "object",
            "properties": {"content": {"type": "string"}, "source_url": {"type": "string"}},
            "required": ["content"]
        },
        category="web"
    )
]

# Document Analysis Tools (4 tools)
DOCUMENT_TOOLS = [
    MCPtool(
        name="extract_metadata",
        description="Extract metadata from a document (author, date, version). Use when "
                   "you need document provenance. Returns metadata dictionary.",
        input_schema={
            "type": "object",
            "properties": {"file_path": {"type": "string"}},
            "required": ["file_path"]
        },
        category="document"
    ),
    MCPtool(
        name="extract_data_points",
        description="Extract structured data points from unstructured text. Use when "
                   "you need to convert prose to tabular data. Returns extracted entities.",
        input_schema={
            "type": "object",
            "properties": {"text": {"type": "string"}, "schema": {"type": "object"}},
            "required": ["text"]
        },
        category="document"
    ),
    MCPtool(
        name="summarize_content",
        description="Generate a concise summary of document content. Use when full "
                   "content is too long. Returns summary with key points.",
        input_schema={
            "type": "object",
            "properties": {"content": {"type": "string"}, "max_length": {"type": "number"}},
            "required": ["content"]
        },
        category="document"
    ),
    MCPtool(
        name="verify_claim",
        description="Verify a factual claim against document corpus. Use when you "
                   "need to confirm information. Returns verification status.",
        input_schema={
            "type": "object",
            "properties": {"claim": {"type": "string"}, "corpus_id": {"type": "string"}},
            "required": ["claim"]
        },
        category="document"
    )
]

# Synthesis Tools (4 tools - scoped, no coordinator needed)
SYNTHESIS_TOOLS = [
    MCPtool(
        name="compile_report",
        description="Compile multiple data sources into a structured report. Use when "
                   "you have gathered information and need formatted output.",
        input_schema={
            "type": "object",
            "properties": {"title": {"type": "string"}, "sections": {"type": "array"}},
            "required": ["title", "sections"]
        },
        category="synthesis"
    ),
    MCPtool(
        name="verify_fact",
        description="Verify a factual claim using scoped local verification. Use when "
                   "synthesis agent needs to confirm facts before including. This is "
                   "a SCOPED version - only checks local summaries, not full corpus.",
        input_schema={
            "type": "object",
            "properties": {"fact": {"type": "string"}, "expected_value": {"type": "string"}},
            "required": ["fact"]
        },
        category="synthesis"
    ),
    MCPtool(
        name="format_citation",
        description="Format a citation in various citation styles (APA, MLA, Chicago). "
                   "Use when you need properly formatted references.",
        input_schema={
            "type": "object",
            "properties": {"source": {"type": "string"}, "style": {"type": "string"}},
            "required": ["source"]
        },
        category="synthesis"
    ),
    MCPtool(
        name="assess_coverage",
        description="Assess how well gathered information covers the topic. Use when "
                   "you need to know if more research is needed. Returns coverage score.",
        input_schema={
            "type": "object",
            "properties": {"topic": {"type": "string"}, "gathered_items": {"type": "array"}},
            "required": ["topic"]
        },
        category="synthesis"
    )
]


# ================================================================================
# SECTION 6: RATE LIMITING IMPLEMENTATION
# ================================================================================

@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    max_requests: int = 100
    window_seconds: int = 60
    burst_allowance: int = 10


class RateLimiter:
    """
    Token bucket algorithm for rate limiting.

    BEST PRACTICE: Track requests per time window per client.
    """

    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.tokens = config.max_requests
        self.last_refill = time.time()
        self.request_times: List[float] = []

    def allow_request(self, client_id: str) -> bool:
        """Check if request is allowed under rate limit."""
        current_time = time.time()
        self._refill_tokens(current_time)

        # Remove old requests
        cutoff = current_time - self.config.window_seconds
        self.request_times = [t for t in self.request_times if t > cutoff]

        max_allowed = self.config.max_requests + self.config.burst_allowance

        if len(self.request_times) < max_allowed:
            self.request_times.append(current_time)
            return True
        return False

    def _refill_tokens(self, current_time: float):
        """Refill tokens based on elapsed time."""
        elapsed = current_time - self.last_refill
        refill_rate = self.config.max_requests / self.config.window_seconds
        self.tokens = min(self.config.max_requests, self.tokens + elapsed * refill_rate)
        self.last_refill = current_time


# ================================================================================
# SECTION 7: AUTHENTICATION HANDLER
# ================================================================================

class AuthHandler:
    """
    Handles authentication for MCP server requests.

    BEST PRACTICE: Store API keys securely, never in plain text.
    """

    def __init__(self):
        self.valid_api_keys = set()
        self._load_api_keys()

    def _load_api_keys(self):
        """Load API keys from environment."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            self.valid_api_keys.add(api_key)

    def validate_request(self, headers: Dict[str, str]) -> bool:
        """Validate authentication for incoming request."""
        auth_header = headers.get("Authorization", "")

        if not auth_header:
            return False

        parts = auth_header.split(" ")
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return False

        token = parts[1]
        return token in self.valid_api_keys

    def get_auth_error(self) -> MCPError:
        """Generate structured authentication error."""
        return MCPError(
            isError=True,
            errorCategory=ErrorCategory.PERMISSION.value,
            isRetryable=False,
            description="Authentication failed. Please provide valid credentials.",
            code="AUTH_FAILED"
        )


# ================================================================================
# SECTION 8: MCP SERVER IMPLEMENTATION
# ================================================================================

class MCPServer:
    """
    Main MCP server class handling tool execution and request routing.

    RESPONSIBILITIES:
    - Route incoming requests to appropriate tools
    - Handle authentication and rate limiting
    - Format responses in MCP protocol format
    - Manage error states gracefully
    """

    def __init__(self, model: str = MODEL_NAME):
        self.model = model
        self.registry = ToolRegistry()
        self.auth_handler = AuthHandler()
        self.rate_limiter = RateLimiter(RateLimitConfig())

    def register_tools(self, tools: List[MCPtool]):
        """Register multiple tools at once."""
        for tool in tools:
            self.registry.register(tool)

    def handle_request(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Handle incoming tool request.

        RETURNS:
            Dictionary with either result or structured error
        """
        headers = headers or {}
        request_id = f"req_{int(time.time() * 1000)}"

        # Step 1: Authenticate
        if not self.auth_handler.validate_request(headers):
            return self._format_error(self.auth_handler.get_auth_error(), request_id)

        # Step 2: Rate limit
        client_id = headers.get("X-Client-ID", "anonymous")
        if not self.rate_limiter.allow_request(client_id):
            error = ErrorFactory.rate_limit_exceeded()
            return self._format_error(error, request_id)

        # Step 3: Lookup tool
        tool = self.registry.get(tool_name)
        if not tool:
            error = MCPError(
                isError=True,
                errorCategory=ErrorCategory.VALIDATION.value,
                isRetryable=False,
                description=f"Tool '{tool_name}' not found",
                code="TOOL_NOT_FOUND"
            )
            return self._format_error(error, request_id)

        # Step 4: Validate parameters
        required = tool.input_schema.get("required", [])
        for field_name in required:
            if field_name not in parameters:
                error = ErrorFactory.missing_field(field_name)
                return self._format_error(error, request_id)

        # Step 5: Execute (simulated - in real implementation, call actual handler)
        return {
            "isError": False,
            "result": {"tool": tool_name, "status": "executed"},
            "request_id": request_id
        }

    def _format_error(self, error: MCPError, request_id: str) -> Dict[str, Any]:
        """Format error into MCP-compliant response."""
        return {
            "isError": True,
            "error": error.to_dict(),
            "request_id": request_id
        }


# ================================================================================
# SECTION 9: MULTI-AGENT ERROR HANDLING
# ================================================================================

class AgentErrorHandler:
    """
    Handles error propagation in multi-agent systems.

    PRINCIPLE: Subagents handle errors locally. Only propagate
    unresolved errors upward. This prevents error storms.
    """

    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.local_handlers: Dict[str, Callable] = {}

    def register_handler(self, error_code: str, handler: Callable):
        """Register a local error handler for specific error codes."""
        self.local_handlers[error_code] = handler

    def handle_error(self, error: MCPError) -> Optional[MCPError]:
        """
        Attempt to handle error locally. If cannot resolve, return for propagation.

        RETURNS:
            None if error handled locally
            MCPError if error should propagate upward
        """
        error_code = error.code

        if error_code in self.local_handlers:
            try:
                if self.local_handlers[error_code](error):
                    return None  # Handled successfully
            except Exception:
                pass

        return error  # Propagate upward


# ================================================================================
# SECTION 10: BUILT-IN TOOLS REFERENCE
# ================================================================================

"""
THE SIX CLAUDE CODE BUILT-IN TOOLS:

+----------+------------------+----------------------------------------+
| Tool     | Purpose          | When to Use                           |
+----------+------------------+----------------------------------------+
| Read     | Read file contents| Examine specific files                 |
| Write    | Create/overwrite  | Create new files or replace content    |
| Edit     | Modify existing   | Change specific parts of files         |
| Bash     | Execute commands  | Run shell commands, scripts            |
| Grep     | Search CONTENT    | Find patterns inside files             |
| Glob     | Search by NAME    | Find files by path/name pattern        |
+----------+------------------+----------------------------------------+

GREP vs GLOB - THE CORE DISTINCTION:
- Grep: Search CONTENT inside files (text patterns)
- Glob: Search FILES by NAME (paths/extensions)

Think: Grep = "find IN files", Glob = "find FILES"

EDIT TOOL STRATEGIES:
1. Find shortest unique anchor first
2. Widen old_string if non-unique
3. Use Read+Write as last resort

INCREMENTAL CODEBASE DISCOVERY:
Pattern: Grep -> Read -> Grep -> Read
Don't read everything upfront. Follow code paths naturally.
"""


# ================================================================================
# SECTION 11: MCP CLIENT IMPLEMENTATION
# ================================================================================

class MCPClient:
    """
    MCP Client for integrating with MCP servers.

    RESPONSIBILITIES:
    - Configure tool choice behavior per request
    - Handle tool execution and response parsing
    - Manage authentication headers
    """

    def __init__(self, api_key: str, model: str = MODEL_NAME):
        self.api_key = api_key
        self.model = model
        self.default_tools: List[MCPtool] = []

    def configure_tools(
        self,
        tools: List[MCPtool],
        tool_choice: str = "auto"
    ) -> Dict[str, Any]:
        """
        Configure tools and tool choice for a request.

        TOOL CHOICE MODES:
        - "auto": AI decides if/how to use tools (default)
        - "any": AI must call a tool and chooses which
        - "<tool_name>": AI must call that specific tool
        """
        self.default_tools = tools

        return {
            "tools": [
                {"name": t.name, "description": t.description, "input_schema": t.input_schema}
                for t in tools
            ],
            "tool_choice": {"type": tool_choice}
        }

    def execute_request(
        self,
        prompt: str,
        tools: Optional[List[MCPtool]] = None,
        tool_choice: str = "auto"
    ) -> Dict[str, Any]:
        """Execute a request with tool configuration."""
        active_tools = tools if tools is not None else self.default_tools

        return {
            "model": self.model,
            "tool_config": self.configure_tools(active_tools, tool_choice),
            "tool_count": len(active_tools),
            "tool_choice_mode": tool_choice
        }


# ================================================================================
# SECTION 12: DEMONSTRATION
# ================================================================================

def demonstrate_all_patterns():
    """Demonstrate all patterns in this template."""

    print("=" * 70)
    print("MCP TOOL DESIGN - COMPREHENSIVE TEMPLATE DEMONSTRATION")
    print("=" * 70)

    # 1. Error handling patterns
    print("\n--- ERROR HANDLING ---")
    errors = [
        ErrorFactory.timeout("API request timed out"),
        ErrorFactory.invalid_input("query", "exceeds maximum length"),
        ErrorFactory.policy_violation("rate-limit", "exceeded 1000 req/hour"),
        ErrorFactory.access_denied("database", "insufficient permissions")
    ]

    for error in errors:
        print(f"\nCategory: {error.errorCategory}")
        print(f"isRetryable: {error.isRetryable}")
        print(f"Description: {error.description}")

    # 2. Tool registry
    print("\n--- TOOL REGISTRY ---")
    registry = ToolRegistry()
    registry.register_tools(WEB_SEARCH_TOOLS)
    registry.register_tools(DOCUMENT_TOOLS)

    print(f"Registered tools: {list(registry.tools.keys())}")
    print(f"Categories: {list(registry.categories.keys())}")

    # 3. Tool choice configuration
    print("\n--- TOOL CHOICE CONFIGURATION ---")
    client = MCPClient(api_key=API_KEY, model=MODEL_NAME)

    configs = [
        ("auto", WEB_SEARCH_TOOLS),
        ("any", DOCUMENT_TOOLS),
        ("search_web", WEB_SEARCH_TOOLS)
    ]

    for mode, tools in configs:
        response = client.execute_request("test prompt", tools=tools, tool_choice=mode)
        print(f"Mode '{mode}': {response['tool_count']} tools configured")

    # 4. Rate limiting
    print("\n--- RATE LIMITING ---")
    limiter = RateLimiter(RateLimitConfig(max_requests=10, window_seconds=60))

    allowed = 0
    for i in range(15):
        if limiter.allow_request("test-client"):
            allowed += 1

    print(f"Requests allowed: {allowed}/15 (rate limited after {allowed})")

    # 5. Multi-agent error handling
    print("\n--- MULTI-AGENT ERROR HANDLING ---")
    agent = AgentErrorHandler("SynthesisAgent")

    def use_default_handler(error: MCPError) -> bool:
        print(f"  -> Using default values for {error.code}")
        return True

    agent.register_handler("MISSING_FIELD", use_default_handler)

    error = ErrorFactory.missing_field("expected_value")
    result = agent.handle_error(error)
    if result is None:
        print("Error handled locally - no propagation needed")
    else:
        print("Error propagated to parent agent")


# ================================================================================
# MAIN
# ================================================================================

if __name__ == "__main__":
    demonstrate_all_patterns()


# ================================================================================
# WHAT WE HAVE LEARNT
# =============================================================================

"""
SUMMARY OF ALL PATTERNS IN THIS TEMPLATE:

1. ERROR CATEGORIES AND HANDLING
   - TRANSIENT: can retry (timeouts, rate limits)
   - VALIDATION: fix and retry (invalid input)
   - BUSINESS: never retry (policy violations)
   - PERMISSION: never retry (access denied)

2. STRUCTURED ERROR RESPONSES
   - isError: true (always for errors)
   - errorCategory: from ErrorCategory enum
   - isRetryable: boolean flag
   - description: human-readable message

3. TOOL CHOICE CONFIGURATION
   - "auto": AI decides if/how to use tools
   - "any": AI must call tool, chooses which
   - "<name>": AI must call specific tool

4. OPTIMAL TOOL COUNT
   - 4-5 tools per agent (NOT 18+)
   - Scoped cross-role tools
   - Avoid coordinator routing (40% latency reduction)

5. TOOL REGISTRY
   - Centralized tool discovery
   - Category-based organization
   - Metadata for AI understanding

6. RATE LIMITING
   - Token bucket algorithm
   - Per-client tracking
   - Burst allowance for spikes

7. AUTHENTICATION
   - Bearer token validation
   - Header-based credentials
   - Never store raw API keys

8. MULTI-AGENT ERROR PROPAGATION
   - Subagents handle locally first
   - Only propagate unresolved errors
   - Add context at each level

9. BUILT-IN TOOLS
   - Read, Write, Edit, Bash, Grep, Glob
   - Grep searches content, Glob matches names
   - Enhanced descriptions prevent bias

10. INCREMENTAL DISCOVERY
    - Grep -> Read -> Grep -> Read
    - Don't read everything upfront
    - Follow code paths naturally
"""

print()
print("=" * 70)
print("END OF COMPREHENSIVE TEMPLATE")
print("=" * 70)