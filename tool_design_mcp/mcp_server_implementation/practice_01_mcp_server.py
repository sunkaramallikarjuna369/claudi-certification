"""
================================================================================
MCP SERVER IMPLEMENTATION - PRACTICE 01
================================================================================

WHAT IS MCP (Model Context Protocol)?
-------------------------------------
MCP is a standardized protocol for communication between AI models and external
tools/servers. It provides a structured way to:
- Register tools with an AI model
- Handle requests and responses
- Manage authentication and rate limiting
- Handle errors gracefully

This practice file covers:
1. Basic MCP server architecture
2. Tool registration and discovery
3. Authentication mechanisms
4. Rate limiting implementation
5. Error handling best practices
6. Structured error responses with isError flag
7. Multi-agent error propagation

================================================================================
"""

# ================================================================================
# SECTION 1: ENVIRONMENT SETUP AND IMPORTS
# ================================================================================

import os
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps

# python-dotenv for reading API keys from .env file
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging for debugging and monitoring
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ================================================================================
# SECTION 2: ERROR CATEGORIES AND STRUCTURED RESPONSES
# ================================================================================

# NOTE: MCP uses structured error responses. Every error MUST include:
# - isError: true (boolean flag)
# - errorCategory: one of the four categories below
# - isRetryable: boolean indicating if retry might help
# - description: human-readable explanation of what went wrong

class ErrorCategory(Enum):
    """
    Four distinct error categories in MCP protocol.
    Each category has different retry behavior and handling patterns.
    """
    TRANSIENT = "transient"           # Temporary issues - retry might help
    VALIDATION = "validation"         # Input problems - retry won't help
    BUSINESS = "business"             # Policy violations - never retry
    PERMISSION = "permission"         # Access issues - never retry


@dataclass
class MCPError:
    """
    Structured error object for MCP responses.

    ATTRIBUTES:
        isError: Boolean flag - ALWAYS true when error occurs
        errorCategory: Category from ErrorCategory enum
        isRetryable: Boolean - true only for transient/validation errors
        description: Human-readable explanation
        code: Optional error code for programmatic handling
        details: Optional additional context
        timestamp: When the error occurred
    """
    isError: bool = True
    errorCategory: str = "transient"
    isRetryable: bool = True
    description: str = ""
    code: Optional[str] = None
    details: Optional[Dict] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict:
        """
        Convert error to dictionary format for JSON response.
        All MCP errors must be serializable to JSON.
        """
        return {
            "isError": self.isError,
            "errorCategory": self.errorCategory,
            "isRetryable": self.isRetryable,
            "description": self.description,
            "code": self.code,
            "details": self.details,
            "timestamp": self.timestamp
        }


# ================================================================================
# SECTION 3: RATE LIMITING IMPLEMENTATION
# ================================================================================

@dataclass
class RateLimitConfig:
    """
    Configuration for rate limiting on MCP server endpoints.

    ATTRIBUTES:
        max_requests: Maximum requests allowed per window
        window_seconds: Time window for counting requests
        burst_allowance: Extra requests allowed in burst scenarios
    """
    max_requests: int = 100
    window_seconds: int = 60
    burst_allowance: int = 10


class RateLimiter:
    """
    Token bucket algorithm for rate limiting MCP server requests.

    COMMON MISTAKE: Many developers only check request count without
    considering time windows. This implementation properly tracks
    requests per time window.

    INTERVIEW Q: How does token bucket differ from leaky bucket?
    - Token bucket: Allows burst traffic up to bucket size
    - Leaky bucket: Smooths traffic to constant rate
    """
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.tokens = config.max_requests
        self.last_refill = time.time()
        self.request_times: List[float] = []

    def allow_request(self, client_id: str) -> bool:
        """
        Check if request is allowed under rate limit.

        ARGS:
            client_id: Identifier for the client making request

        RETURNS:
            True if request allowed, False if rate limited
        """
        current_time = time.time()
        self._refill_tokens(current_time)

        # Remove old requests outside the window
        cutoff_time = current_time - self.config.window_seconds
        self.request_times = [t for t in self.request_times if t > cutoff_time]

        # Check if under limit (plus burst allowance)
        max_allowed = self.config.max_requests + self.config.burst_allowance

        if len(self.request_times) < max_allowed:
            self.request_times.append(current_time)
            logger.info(f"Request allowed for client {client_id}. "
                       f"Count: {len(self.request_times)}/{max_allowed}")
            return True

        logger.warning(f"Request denied for client {client_id}. "
                      f"Rate limit exceeded: {len(self.request_times)}/{max_allowed}")
        return False

    def _refill_tokens(self, current_time: float):
        """Refill tokens based on elapsed time."""
        elapsed = current_time - self.last_refill
        refill_rate = self.config.max_requests / self.config.window_seconds
        self.tokens = min(self.config.max_requests, self.tokens + elapsed * refill_rate)
        self.last_refill = current_time


# ================================================================================
# SECTION 4: AUTHENTICATION HANDLER
# ================================================================================

class AuthHandler:
    """
    Handles authentication for MCP server requests.

    REAL-TIME SCENARIO: In production, you might integrate with:
    - OAuth 2.0 providers (Google, GitHub, Microsoft)
    - JWT tokens for stateless auth
    - API key validation for simple integrations

    BEST PRACTICE: Never store raw API keys. Hash them and compare hashes.
    """

    def __init__(self):
        # In production, load this from secure configuration
        self.valid_api_keys = set()
        self.api_key_hash_map: Dict[str, str] = {}
        self._load_api_keys()

    def _load_api_keys(self):
        """
        Load and validate API keys from environment.

        NOTE: In production, API keys should be hashed before storage.
        This example stores them for demonstration but NEVER do this
        in production code!
        """
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            self.valid_api_keys.add(api_key)
            logger.info("API key loaded from environment")

    def validate_request(self, headers: Dict[str, str]) -> bool:
        """
        Validate authentication for incoming request.

        ARGS:
            headers: Request headers containing auth credentials

        RETURNS:
            True if authentication successful, False otherwise
        """
        auth_header = headers.get("Authorization", "")

        if not auth_header:
            logger.warning("Missing Authorization header")
            return False

        # Extract the actual token from "Bearer <token>"
        parts = auth_header.split(" ")
        if len(parts) != 2 or parts[0].lower() != "bearer":
            logger.warning("Invalid Authorization header format")
            return False

        token = parts[1]

        # Validate against stored keys
        if token in self.valid_api_keys:
            logger.info("Authentication successful")
            return True

        logger.warning("Invalid API key provided")
        return False

    def get_auth_error(self) -> MCPError:
        """
        Generate structured authentication error response.

        NOTE: Permission errors are NEVER retryable because the
        problem won't fix itself without user intervention.
        """
        return MCPError(
            isError=True,
            errorCategory=ErrorCategory.PERMISSION.value,
            isRetryable=False,
            description="Authentication failed. Please provide valid credentials.",
            code="AUTH_FAILED",
            details={"hint": "Include valid Authorization header"}
        )


# ================================================================================
# SECTION 5: TOOL REGISTRY AND DISCOVERY
# ================================================================================

@dataclass
class ToolDefinition:
    """
    Definition of a tool available in the MCP server.

    ATTRIBUTES:
        name: Unique identifier for the tool
        description: What the tool does (be detailed for AI to understand)
        input_schema: JSON schema for tool parameters
        handler: Function to execute when tool is called
        requires_auth: Whether this tool needs authentication
        rate_limit: Optional rate limit override for this tool
    """
    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: Callable
    requires_auth: bool = True
    rate_limit: Optional[RateLimitConfig] = None


class ToolRegistry:
    """
    Central registry for all MCP tools.

    PURPOSE: Allows AI model to discover available tools and their
    capabilities through structured metadata.

    REAL-TIME SCENARIO: When AI needs to search code, it first
    queries the registry to find available search tools.
    """
    def __init__(self):
        self.tools: Dict[str, ToolDefinition] = {}
        self.categories: Dict[str, List[str]] = {}

    def register_tool(self, tool: ToolDefinition):
        """
        Register a new tool with the server.

        ARGS:
            tool: ToolDefinition instance with tool metadata
        """
        self.tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")

        # Update category index
        category = tool.input_schema.get("category", "general")
        if category not in self.categories:
            self.categories[category] = []
        self.categories[category].append(tool.name)

    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        """
        Retrieve tool definition by name.

        RETURNS:
            ToolDefinition if found, None otherwise
        """
        return self.tools.get(name)

    def list_tools(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all tools, optionally filtered by category.

        ARGS:
            category: Optional category filter

        RETURNS:
            List of tool metadata dictionaries for AI consumption
        """
        if category:
            tool_names = self.categories.get(category, [])
            tools = [self.tools[name] for name in tool_names if name in self.tools]
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
# SECTION 6: MCP SERVER IMPLEMENTATION
# ================================================================================

class MCPServer:
    """
    Main MCP server class handling tool execution and request routing.

    RESPONSIBILITIES:
    - Route incoming requests to appropriate tools
    - Handle authentication and rate limiting
    - Format responses in MCP protocol format
    - Manage error states gracefully

    COMMON MISTAKE: Developers often forget to handle partial results.
    If a tool partially succeeds, return the results along with warnings.
    """

    def __init__(self, model: str = "claude-haiku-4-5-20250601"):
        self.model = model
        self.registry = ToolRegistry()
        self.auth_handler = AuthHandler()
        self.rate_limiter = RateLimiter(RateLimitConfig())
        self.request_history: List[Dict] = []

        # Initialize default rate limit config
        self.default_rate_limit = RateLimitConfig(
            max_requests=100,
            window_seconds=60
        )

        logger.info(f"MCP Server initialized with model: {self.model}")

    def register_tools(self, tools: List[ToolDefinition]):
        """
        Register multiple tools at once.

        ARGS:
            tools: List of ToolDefinition instances
        """
        for tool in tools:
            self.registry.register_tool(tool)

    def handle_request(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Handle incoming tool request.

        ARGS:
            tool_name: Name of the tool to execute
            parameters: Parameters to pass to the tool
            headers: Optional request headers for auth

        RETURNS:
            Dictionary with either result or error information

        IMPORTANT: This method ALWAYS returns valid JSON structure.
        Never return raw exceptions or unhandled errors.
        """
        headers = headers or {}
        request_id = f"req_{int(time.time() * 1000)}"

        # Step 1: Authenticate
        if not self.auth_handler.validate_request(headers):
            error = self.auth_handler.get_auth_error()
            return self._format_error_response(error, request_id)

        # Step 2: Rate limiting
        client_id = headers.get("X-Client-ID", "anonymous")
        if not self.rate_limiter.allow_request(client_id):
            error = MCPError(
                isError=True,
                errorCategory=ErrorCategory.TRANSIENT.value,
                isRetryable=True,
                description="Rate limit exceeded. Please wait before retrying.",
                code="RATE_LIMITED"
            )
            return self._format_error_response(error, request_id)

        # Step 3: Tool lookup
        tool = self.registry.get_tool(tool_name)
        if not tool:
            error = MCPError(
                isError=True,
                errorCategory=ErrorCategory.VALIDATION.value,
                isRetryable=False,
                description=f"Tool '{tool_name}' not found. Available tools: {list(self.registry.tools.keys())}",
                code="TOOL_NOT_FOUND"
            )
            return self._format_error_response(error, request_id)

        # Step 4: Execute tool
        try:
            # Validate parameters against schema
            self._validate_parameters(parameters, tool.input_schema)

            # Execute the tool handler
            result = tool.handler(parameters)

            # Log successful execution
            self._log_request(request_id, tool_name, parameters, "success")

            return {
                "isError": False,
                "result": result,
                "tool": tool_name,
                "request_id": request_id,
                "model": self.model
            }

        except ValueError as e:
            # Validation errors - never retry
            error = MCPError(
                isError=True,
                errorCategory=ErrorCategory.VALIDATION.value,
                isRetryable=False,
                description=str(e),
                code="VALIDATION_ERROR",
                details={"parameters": parameters}
            )
            self._log_request(request_id, tool_name, parameters, "validation_error")
            return self._format_error_response(error, request_id)

        except TimeoutError as e:
            # Transient errors - retry might help
            error = MCPError(
                isError=True,
                errorCategory=ErrorCategory.TRANSIENT.value,
                isRetryable=True,
                description="Request timed out. Please retry.",
                code="TIMEOUT"
            )
            self._log_request(request_id, tool_name, parameters, "timeout")
            return self._format_error_response(error, request_id)

        except Exception as e:
            # Unexpected errors - include partial info
            error = MCPError(
                isError=True,
                errorCategory=ErrorCategory.BUSINESS.value,
                isRetryable=False,
                description="An unexpected error occurred. Please contact support.",
                code="INTERNAL_ERROR",
                details={"partial_info": str(e)}
            )
            self._log_request(request_id, tool_name, parameters, "error")
            return self._format_error_response(error, request_id)

    def _validate_parameters(
        self,
        parameters: Dict[str, Any],
        schema: Dict[str, Any]
    ):
        """
        Validate parameters against JSON schema.

        NOTE: In production, use jsonschema library for full validation.
        This is a simplified version for learning purposes.
        """
        required = schema.get("required", [])
        properties = schema.get("properties", {})

        # Check required fields
        for field_name in required:
            if field_name not in parameters:
                raise ValueError(f"Missing required parameter: {field_name}")

        # Check types
        for key, value in parameters.items():
            if key in properties:
                expected_type = properties[key].get("type")
                if expected_type == "string" and not isinstance(value, str):
                    raise ValueError(f"Parameter '{key}' must be string")
                elif expected_type == "number" and not isinstance(value, (int, float)):
                    raise ValueError(f"Parameter '{key}' must be number")
                elif expected_type == "array" and not isinstance(value, list):
                    raise ValueError(f"Parameter '{key}' must be array")

    def _format_error_response(self, error: MCPError, request_id: str) -> Dict[str, Any]:
        """
        Format error into MCP-compliant response structure.
        """
        return {
            "isError": True,
            "error": error.to_dict(),
            "request_id": request_id,
            "model": self.model
        }

    def _log_request(
        self,
        request_id: str,
        tool_name: str,
        parameters: Dict[str, Any],
        status: str
    ):
        """Log request for monitoring and debugging."""
        self.request_history.append({
            "request_id": request_id,
            "tool": tool_name,
            "status": status,
            "timestamp": datetime.utcnow().isoformat()
        })


# ================================================================================
# SECTION 7: EXAMPLE TOOL HANDLERS
# ================================================================================

def search_code_handler(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Example tool handler: Search code in repository.

    SCENARIO: AI needs to find all occurrences of a function across codebase.
    This handler would search and return matching locations.
    """
    query = params.get("query", "")
    file_filter = params.get("file_filter", "*")
    max_results = params.get("max_results", 50)

    # Simulated search results (in real implementation, use Grep)
    results = [
        {"file": "src/utils.py", "line": 42, "context": f"def {query}():"},
        {"file": "src/api.py", "line": 128, "context": f"    {query}(args)"},
        {"file": "tests/test_utils.py", "line": 15, "context": f"assert {query}()"}
    ]

    return {
        "tool": "search_code",
        "query": query,
        "file_filter": file_filter,
        "result_count": len(results),
        "results": results[:max_results]
    }


def read_file_handler(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Example tool handler: Read file contents.

    SCENARIO: AI needs to examine specific file for context.
    """
    file_path = params.get("path", "")
    max_lines = params.get("max_lines", 1000)

    # Simulated file read (in real implementation, use Read tool)
    if not file_path:
        raise ValueError("Path parameter is required")

    return {
        "tool": "read_file",
        "path": file_path,
        "content": f"# Simulated content of {file_path}\n# ... {max_lines} lines",
        "lines_read": max_lines
    }


# ================================================================================
# SECTION 8: SERVER INITIALIZATION AND USAGE EXAMPLE
# ================================================================================

def create_mcp_server() -> MCPServer:
    """
    Factory function to create and configure MCP server.

    RETURNS:
        Configured MCPServer instance with registered tools
    """
    server = MCPServer(model="claude-haiku-4-5-20250601")

    # Define available tools
    tools = [
        ToolDefinition(
            name="search_code",
            description="Search for code patterns across the repository. "
                       "Accepts query string and optional file filter. "
                       "Returns list of matches with file paths and line numbers.",
            input_schema={
                "type": "object",
                "category": "search",
                "required": ["query"],
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "file_filter": {"type": "string", "description": "File pattern filter"},
                    "max_results": {"type": "number", "description": "Maximum results"}
                }
            },
            handler=search_code_handler
        ),
        ToolDefinition(
            name="read_file",
            description="Read contents of a file from the filesystem. "
                       "Returns file content up to specified line limit.",
            input_schema={
                "type": "object",
                "category": "file",
                "required": ["path"],
                "properties": {
                    "path": {"type": "string", "description": "File path to read"},
                    "max_lines": {"type": "number", "description": "Maximum lines to read"}
                }
            },
            handler=read_file_handler
        )
    ]

    server.register_tools(tools)
    logger.info("MCP Server created with tools: search_code, read_file")

    return server


# ================================================================================
# SECTION 9: DEMONSTRATION
# ================================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("MCP SERVER IMPLEMENTATION - PRACTICE 01")
    print("=" * 70)
    print()

    # Create server
    server = create_mcp_server()

    # Example 1: Successful request
    print("-" * 70)
    print("Example 1: Successful Tool Request")
    print("-" * 70)

    response = server.handle_request(
        tool_name="search_code",
        parameters={"query": "calculate_total", "max_results": 10},
        headers={"Authorization": "Bearer test-key", "X-Client-ID": "demo-client"}
    )

    print(f"Success: {not response.get('isError', False)}")
    print(f"Result count: {response.get('result', {}).get('result_count', 0)}")
    print()

    # Example 2: Authentication error
    print("-" * 70)
    print("Example 2: Authentication Failure")
    print("-" * 70)

    response = server.handle_request(
        tool_name="search_code",
        parameters={"query": "test"},
        headers={"Authorization": "Bearer invalid-key"}
    )

    print(f"Is Error: {response.get('isError', False)}")
    print(f"Error Category: {response.get('error', {}).get('errorCategory', 'N/A')}")
    print(f"Is Retryable: {response.get('error', {}).get('isRetryable', 'N/A')}")
    print(f"Description: {response.get('error', {}).get('description', 'N/A')}")
    print()

    # Example 3: Rate limiting
    print("-" * 70)
    print("Example 3: Rate Limit Exceeded")
    print("-" * 70)

    # Make many requests to trigger rate limit
    for i in range(105):
        response = server.handle_request(
            tool_name="read_file",
            parameters={"path": f"/fake/path{i}.txt"},
            headers={"Authorization": "Bearer test-key", "X-Client-ID": "rate-test"}
        )
        if response.get("isError"):
            if response.get("error", {}).get("code") == "RATE_LIMITED":
                print(f"Rate limit triggered after {i} requests")
                print(f"Error: {response.get('error', {}).get('description')}")
                break

    print()

    # Example 4: Tool not found
    print("-" * 70)
    print("Example 4: Non-existent Tool")
    print("-" * 70)

    response = server.handle_request(
        tool_name="nonexistent_tool",
        parameters={},
        headers={"Authorization": "Bearer test-key"}
    )

    print(f"Is Error: {response.get('isError', False)}")
    print(f"Error Category: {response.get('error', {}).get('errorCategory', 'N/A')}")
    print(f"Code: {response.get('error', {}).get('code', 'N/A')}")
    print()

    # List available tools
    print("-" * 70)
    print("Available Tools in Registry")
    print("-" * 70)

    tools = server.registry.list_tools()
    for tool in tools:
        print(f"  - {tool['name']}: {tool['description'][:60]}...")


# ================================================================================
# WHAT WE HAVE LEARNT
# ================================================================================

"""
SUMMARY OF KEY CONCEPTS:

1. MCP (Model Context Protocol) Architecture
   - Standardized communication between AI and tools
   - Structured request/response format
   - Support for multiple tools and agents

2. Four Error Categories
   - TRANSIENT: Timeouts, service issues - can retry
   - VALIDATION: Invalid input - fix input, don't retry
   - BUSINESS: Policy violations - never retry
   - PERMISSION: Access denied - never retry

3. Structured Error Responses
   - isError: Boolean flag (always true when error)
   - errorCategory: From the four categories
   - isRetryable: True only for transient/validation
   - description: Human-readable explanation

4. Rate Limiting
   - Token bucket algorithm for smooth limiting
   - Per-client tracking with time windows
   - Burst allowance for occasional spikes

5. Authentication
   - Bearer token validation
   - Header-based credential passing
   - Never store raw API keys in production

6. Tool Registry Pattern
   - Centralized tool discovery
   - Category-based organization
   - Metadata for AI understanding

7. Common Mistakes to Avoid
   - Returning raw exceptions instead of structured errors
   - Not handling partial results
   - Forgetting rate limiting on all endpoints
   - Missing required field validation

8. Interview Questions & Answers

   Q: What is MCP and why use it?
   A: MCP (Model Context Protocol) is a standardized protocol for AI-tool
      communication. It provides structured request/response, authentication,
      rate limiting, and error handling in a consistent format.

   Q: How do you handle errors in MCP?
   A: Using structured error responses with isError flag, errorCategory,
      isRetryable flag, and description. Each category has different
      retry behavior.

   Q: What is the difference between validation and business errors?
   A: Validation errors come from malformed input (fix input and retry may work).
      Business errors come from policy violations (never retry without changes).

   Q: How does rate limiting work in MCP servers?
   A: Token bucket algorithm tracks requests per time window per client.
      Allows burst up to bucket size, then enforces limit.

   Q: What is multi-agent error propagation?
   A: Subagents handle errors locally. Only propagate unresolved errors upward.
      This prevents error storms and provides context.
"""

print()
print("=" * 70)
print("END OF PRACTICE 01: MCP SERVER IMPLEMENTATION")
print("=" * 70)