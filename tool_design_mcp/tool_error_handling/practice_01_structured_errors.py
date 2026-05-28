"""
================================================================================
TOOL ERROR HANDLING - PRACTICE 01
================================================================================

WHAT IS STRUCTURED ERROR HANDLING?
----------------------------------
Error handling in MCP (Model Context Protocol) follows a strict structured
format that enables:
- Clear communication of failure states
- Appropriate retry behavior determination
- Multi-agent error propagation
- Debugging and monitoring

This practice file covers:
1. The isError flag - mandatory error indicator
2. Four error categories and their retry behavior
3. Access failure vs valid empty result distinction
4. Required metadata for all errors
5. Multi-agent error propagation patterns
6. Anti-patterns to avoid

================================================================================
"""

# ================================================================================
# SECTION 1: ENVIRONMENT SETUP
# ================================================================================

import os
import time
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Configure API settings
MODEL_NAME = "claude-haiku-4-5-20250601"
API_KEY = os.getenv("ANTHROPIC_API_KEY", "")


# ================================================================================
# SECTION 2: ERROR CATEGORIES EXPLAINED
# ================================================================================

class ErrorCategory(Enum):
    """
    Four distinct error categories in MCP protocol.

    EACH CATEGORY HAS SPECIFIC RETRY BEHAVIOR:

    +------------------+-----------------+----------------------------------+
    | Category         | isRetryable     | When to Use                      |
    +------------------+-----------------+----------------------------------+
    | TRANSIENT        | TRUE            | Temporary failures, retry may    |
    |                  |                 | succeed (timeouts, rate limits)  |
    +------------------+-----------------+----------------------------------+
    | VALIDATION       | TRUE            | Input problems, fix and retry    |
    |                  |                 | may work (invalid params)       |
    +------------------+-----------------+----------------------------------+
    | BUSINESS         | FALSE           | Policy violations, never retry   |
    |                  |                 | without user intervention       |
    +------------------+-----------------+----------------------------------+
    | PERMISSION       | FALSE           | Access denied, never retry      |
    |                  |                 | (wrong credentials)             |
    +------------------+-----------------+----------------------------------+
    """

    TRANSIENT = "transient"      # Temporary issues - retry might help
    VALIDATION = "validation"   # Input problems - fix and retry
    BUSINESS = "business"       # Policy violations - never retry
    PERMISSION = "permission"    # Access issues - never retry


# ================================================================================
# SECTION 3: STRUCTURED ERROR CLASS
# ================================================================================

@dataclass
class MCPError:
    """
    Structured error object for MCP protocol responses.

    IMPORTANT: Every field is REQUIRED for proper error communication.

    ATTRIBUTES:
        isError: Boolean - ALWAYS True when an error occurs
        errorCategory: Category from ErrorCategory enum (string value)
        isRetryable: Boolean - True only for transient/validation errors
        description: Human-readable explanation (not for debugging)
        code: Optional error code for programmatic handling
        details: Optional additional context for debugging

    COMMON MISTAKE: Don't put debugging info in description.
    Description is for end users, details is for developers.
    """

    # Required fields (with defaults to allow partial construction)
    isError: bool = True                    # ALWAYS True for errors
    errorCategory: str = "transient"        # Category as string
    isRetryable: bool = True                # Retry recommendation
    description: str = ""                   # User-friendly message

    # Optional fields
    code: Optional[str] = None              # Programmatic error code
    details: Optional[Dict[str, Any]] = None  # Debug information
    timestamp: str = field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert error to dictionary for JSON serialization.

        RETURNS:
            Dictionary with all error fields
        """
        result = {
            "isError": self.isError,
            "errorCategory": self.errorCategory,
            "isRetryable": self.isRetryable,
            "description": self.description
        }

        # Only include optional fields if they have values
        if self.code:
            result["code"] = self.code
        if self.details:
            result["details"] = self.details
        result["timestamp"] = self.timestamp

        return result


# ================================================================================
# SECTION 4: ERROR FACTORY FUNCTIONS
# ================================================================================

class ErrorFactory:
    """
    Factory class for creating standardized MCP errors.

    USE FACTORY FUNCTIONS INSTEAD OF DIRECT INSTANTIATION
    to ensure consistent error structure across the codebase.
    """

    # =======================
    # TRANSIENT ERRORS
    # =======================

    @staticmethod
    def timeout(
        message: str = "Request timed out",
        details: Optional[Dict] = None
    ) -> MCPError:
        """
        Create a timeout error.

        TRANSIENT - can retry with backoff
        """
        return MCPError(
            isError=True,
            errorCategory=ErrorCategory.TRANSIENT.value,
            isRetryable=True,
            description=message,
            code="TIMEOUT",
            details=details
        )

    @staticmethod
    def service_unavailable(
        service: str,
        details: Optional[Dict] = None
    ) -> MCPError:
        """
        Create a service unavailable error.

        TRANSIENT - service may come back online
        """
        return MCPError(
            isError=True,
            errorCategory=ErrorCategory.TRANSIENT.value,
            isRetryable=True,
            description=f"Service '{service}' is temporarily unavailable",
            code="SERVICE_UNAVAILABLE",
            details=details
        )

    @staticmethod
    def rate_limit_exceeded(
        retry_after: Optional[int] = None,
        details: Optional[Dict] = None
    ) -> MCPError:
        """
        Create a rate limit exceeded error.

        TRANSIENT - wait and retry may succeed
        """
        msg = "Rate limit exceeded"
        if retry_after:
            msg += f". Retry after {retry_after} seconds"

        return MCPError(
            isError=True,
            errorCategory=ErrorCategory.TRANSIENT.value,
            isRetryable=True,
            description=msg,
            code="RATE_LIMITED",
            details={"retry_after": retry_after, **(details or {})}
        )

    # =======================
    # VALIDATION ERRORS
    # =======================

    @staticmethod
    def invalid_input(
        field_name: str,
        reason: str,
        details: Optional[Dict] = None
    ) -> MCPError:
        """
        Create an invalid input error.

        VALIDATION - fix input and retry may work
        """
        return MCPError(
            isError=True,
            errorCategory=ErrorCategory.VALIDATION.value,
            isRetryable=True,
            description=f"Invalid input for '{field_name}': {reason}",
            code="INVALID_INPUT",
            details={"field": field_name, **(details or {})}
        )

    @staticmethod
    def missing_field(
        field_name: str,
        details: Optional[Dict] = None
    ) -> MCPError:
        """
        Create a missing required field error.

        VALIDATION - provide field and retry
        """
        return MCPError(
            isError=True,
            errorCategory=ErrorCategory.VALIDATION.value,
            isRetryable=True,
            description=f"Missing required field: '{field_name}'",
            code="MISSING_FIELD",
            details={"field": field_name, **(details or {})}
        )

    @staticmethod
    def out_of_range(
        field_name: str,
        value: Any,
        min_val: Optional[Any] = None,
        max_val: Optional[Any] = None,
        details: Optional[Dict] = None
    ) -> MCPError:
        """
        Create an out of range error.

        VALIDATION - adjust value and retry
        """
        msg = f"Value '{value}' for '{field_name}' is out of range"
        if min_val is not None and max_val is not None:
            msg += f" (expected {min_val} to {max_val})"
        elif min_val is not None:
            msg += f" (must be >= {min_val})"
        elif max_val is not None:
            msg += f" (must be <= {max_val})"

        return MCPError(
            isError=True,
            errorCategory=ErrorCategory.VALIDATION.value,
            isRetryable=True,
            description=msg,
            code="OUT_OF_RANGE",
            details={"value": value, "min": min_val, "max": max_val, **(details or {})}
        )

    # =======================
    # BUSINESS ERRORS
    # =======================

    @staticmethod
    def policy_violation(
        policy_name: str,
        reason: str,
        details: Optional[Dict] = None
    ) -> MCPError:
        """
        Create a policy violation error.

        BUSINESS - never retry without user intervention
        """
        return MCPError(
            isError=True,
            errorCategory=ErrorCategory.BUSINESS.value,
            isRetryable=False,
            description=f"Policy violation: {policy_name}. {reason}",
            code="POLICY_VIOLATION",
            details={"policy": policy_name, **(details or {})}
        )

    @staticmethod
    def limit_exceeded(
        limit_type: str,
        current: int,
        maximum: int,
        details: Optional[Dict] = None
    ) -> MCPError:
        """
        Create a limit exceeded error.

        BUSINESS - user must upgrade or clean up
        """
        return MCPError(
            isError=True,
            errorCategory=ErrorCategory.BUSINESS.value,
            isRetryable=False,
            description=f"Limit exceeded: {limit_type} ({current}/{maximum})",
            code="LIMIT_EXCEEDED",
            details={"current": current, "maximum": maximum, **(details or {})}
        )

    # =======================
    # PERMISSION ERRORS
    # =======================

    @staticmethod
    def access_denied(
        resource: str,
        reason: str = "Insufficient permissions",
        details: Optional[Dict] = None
    ) -> MCPError:
        """
        Create an access denied error.

        PERMISSION - never retry with same credentials
        """
        return MCPError(
            isError=True,
            errorCategory=ErrorCategory.PERMISSION.value,
            isRetryable=False,
            description=f"Access denied to '{resource}': {reason}",
            code="ACCESS_DENIED",
            details=details
        )

    @staticmethod
    def invalid_credentials(
        details: Optional[Dict] = None
    ) -> MCPError:
        """
        Create an invalid credentials error.

        PERMISSION - credentials must be updated
        """
        return MCPError(
            isError=True,
            errorCategory=ErrorCategory.PERMISSION.value,
            isRetryable=False,
            description="Authentication failed: Invalid credentials",
            code="INVALID_CREDENTIALS",
            details=details
        )

    @staticmethod
    def expired_token(
        details: Optional[Dict] = None
    ) -> MCPError:
        """
        Create an expired token error.

        PERMISSION - user must re-authenticate
        """
        return MCPError(
            isError=True,
            errorCategory=ErrorCategory.PERMISSION.value,
            isRetryable=False,
            description="Authentication failed: Token has expired",
            code="TOKEN_EXPIRED",
            details=details
        )


# ================================================================================
# SECTION 5: ACCESS FAILURE vs EMPTY RESULT
# ================================================================================

def demonstrate_access_vs_empty():
    """
    Critical distinction: Access failure vs Valid empty result.

    This is a common source of bugs - developers treat empty results
    as errors and retry them unnecessarily.
    """

    print("\n" + "=" * 70)
    print("CRITICAL: Access Failure vs Valid Empty Result")
    print("=" * 70)

    print("""
    +=========================================================================+
    | SCENARIO: Searching for users in a database                            |
    +=========================================================================+

    CASE 1: Access Failure (ERROR - retry might help)
    +---------------------------------------------------------------------+
    | You try to connect to database but get connection timeout.         |
    |                                                                     |
    | Response:                                                           |
    |   isError: true                                                     |
    |   errorCategory: "transient"                                        |
    |   isRetryable: true                                                 |
    |   description: "Database connection timed out"                       |
    |                                                                     |
    | ACTION: Retry with backoff - connection may succeed next time       |
    +---------------------------------------------------------------------+

    CASE 2: Valid Empty Result (NOT ERROR - don't retry)
    +---------------------------------------------------------------------+
    | You successfully connect to database and run query.                 |
    | Query returns 0 rows because no users match.                        |
    |                                                                     |
    | Response:                                                           |
    |   isError: false                                                    |
    |   resultCount: 0                                                   |
    |   results: []                                                       |
    |                                                                     |
    | ACTION: Don't retry - there's nothing to find.                      |
    |         Empty result is a valid outcome, not an error.             |
    +---------------------------------------------------------------------+

    COMMON MISTAKE:

    if response.get("results") is None:
        # WRONG: Treats empty array same as access failure
        # This causes infinite retry loops for valid empty results!

    CORRECT APPROACH:

    if response.get("isError"):
        # Handle error - check isRetryable
        if response["error"]["isRetryable"]:
            retry_with_backoff()
    elif response.get("resultCount", 0) == 0:
        # Valid empty result - no retry needed
        # Handle empty state gracefully
    """)

    # Example code demonstrating the correct approach

    class MockToolResponse:
        """Simulates different tool response scenarios."""

        @staticmethod
        def access_failure():
            """Simulates database connection timeout."""
            return {
                "isError": True,
                "error": {
                    "errorCategory": "transient",
                    "isRetryable": True,
                    "description": "Database connection timed out",
                    "code": "TIMEOUT"
                }
            }

        @staticmethod
        def valid_empty_result():
            """Simulates successful query returning empty results."""
            return {
                "isError": False,
                "resultCount": 0,
                "results": []
            }

    print("\nExample Code:")

    # Test access failure
    print("\n--- Access Failure (should retry) ---")
    response = MockToolResponse.access_failure()
    print(f"isError: {response.get('isError')}")
    if response.get("isError"):
        error = response.get("error", {})
        print(f"Category: {error.get('errorCategory')}")
        print(f"isRetryable: {error.get('isRetryable')}")
        print("Action: RETRY with backoff")

    # Test empty result
    print("\n--- Valid Empty Result (don't retry) ---")
    response = MockToolResponse.valid_empty_result()
    print(f"isError: {response.get('isError')}")
    print(f"resultCount: {response.get('resultCount')}")
    print("Action: HANDLE empty state gracefully, do NOT retry")


# ================================================================================
# SECTION 6: MULTI-AGENT ERROR PROPAGATION
# ================================================================================

class AgentErrorHandler:
    """
    Handles error propagation in multi-agent systems.

    PRINCIPLE: Subagents handle errors locally. Only propagate
    unresolved errors upward. This prevents error storms and
    provides context at each level.
    """

    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.local_handlers: Dict[str, Callable] = {}

    def register_local_handler(self, error_code: str, handler: Callable):
        """
        Register a local error handler for specific error codes.

        ARGS:
            error_code: Error code this handler manages
            handler: Function to handle the error locally
        """
        self.local_handlers[error_code] = handler
        print(f"[{self.agent_name}] Registered local handler for: {error_code}")

    def handle_error(self, error: MCPError) -> Optional[MCPError]:
        """
        Attempt to handle error locally. If cannot resolve,
        return error for propagation.

        RETURNS:
            None if error handled locally
            MCPError if error should propagate upward

        EXAMPLE:
            synthesis_agent.handle_error(database_error)
            # If local handler exists for TIMEOUT, tries recovery
            # If no handler or recovery failed, returns error for coordinator
        """
        error_code = error.code

        if error_code in self.local_handlers:
            print(f"[{self.agent_name}] Attempting local handling for: {error_code}")

            # Try local recovery
            try:
                recovered = self.local_handlers[error_code](error)
                if recovered:
                    print(f"[{self.agent_name}] Local recovery successful")
                    return None  # Error handled, don't propagate
                else:
                    print(f"[{self.agent_name}] Local recovery failed, propagating")
                    return error  # Propagate upward
            except Exception as e:
                print(f"[{self.agent_name}] Local handler exception: {e}")
                return error  # Propagate with context

        # No local handler - propagate
        print(f"[{self.agent_name}] No local handler for '{error_code}', propagating")
        return error

    def create_propagation_context(
        self,
        original_error: MCPError,
        context: Dict[str, Any]
    ) -> MCPError:
        """
        Add context to error before propagating to parent agent.

        RETURNS:
            MCPError with added context about where it originated
        """
        return MCPError(
            isError=True,
            errorCategory=original_error.errorCategory,
            isRetryable=original_error.isRetryable,
            description=original_error.description,
            code=original_error.code,
            details={
                "origin_agent": self.agent_name,
                "original_details": original_error.details,
                "propagation_context": context
            }
        )


def demonstrate_error_propagation():
    """
    Demonstrate multi-agent error handling flow.
    """

    print("\n" + "=" * 70)
    print("MULTI-AGENT ERROR PROPAGATION EXAMPLE")
    print("=" * 70)

    # Create agents with local handlers
    web_search_agent = AgentErrorHandler("WebSearchAgent")
    synthesis_agent = AgentErrorHandler("SynthesisAgent")
    coordinator_agent = AgentErrorHandler("CoordinatorAgent")

    # Register local handlers
    def retry_with_cache(error: MCPError) -> bool:
        """Local handler: retry using cached data."""
        print(f"  -> Trying cache fallback...")
        return True  # Simulated successful recovery

    web_search_agent.register_local_handler("TIMEOUT", retry_with_cache)

    def use_defaults(error: MCPError) -> bool:
        """Local handler: use default values."""
        print(f"  -> Using default values...")
        return True

    synthesis_agent.register_local_handler("MISSING_FIELD", use_defaults)

    # Simulate error flow
    print("\n--- Error Flow Simulation ---")

    # Step 1: Web search encounters timeout
    print("\n1. WebSearchAgent encounters TIMEOUT")
    timeout_error = ErrorFactory.timeout("Connection to search API timed out")
    print(f"   Original error: {timeout_error.description}")

    # Step 2: Attempt local handling
    result = web_search_agent.handle_error(timeout_error)
    if result is None:
        print("   -> Local recovery successful, no propagation needed")
    else:
        print("   -> Local handling failed, propagating to Coordinator")

        # Step 3: Propagate with context
        propagated = coordinator_agent.create_propagation_context(
            result,
            {"attempted_recovery": True, "used_cache": True}
        )
        print(f"   -> Coordinator received: {propagated.description}")
        print(f"   -> Context: origin={propagated.details.get('origin_agent')}")

    # Step 4: Synthesis gets a validation error (can handle locally)
    print("\n2. SynthesisAgent encounters MISSING_FIELD")
    missing_error = ErrorFactory.missing_field("expected_value")
    print(f"   Original error: {missing_error.description}")

    result = synthesis_agent.handle_error(missing_error)
    if result is None:
        print("   -> Local recovery successful (used defaults)")
    else:
        print("   -> Could not handle locally, would propagate")


# ================================================================================
# SECTION 7: TOOL EXECUTION WITH ERROR HANDLING
# ================================================================================

class ToolExecutor:
    """
    Executes tools with proper error handling.

    PATTERN: Every tool execution should:
    1. Wrap execution in try-catch
    2. Convert exceptions to structured MCPError
    3. Include partial results when possible
    4. Return consistent response structure
    """

    def __init__(self):
        self.execution_history: List[Dict] = []

    def execute(
        self,
        tool_name: str,
        handler: Callable,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a tool with structured error handling.

        ARGS:
            tool_name: Name of the tool
            handler: Function to execute
            parameters: Parameters to pass

        RETURNS:
            Either success response or structured error
        """

        try:
            # Validate parameters
            self._validate_parameters(parameters, tool_name)

            # Execute tool
            result = handler(parameters)

            # Log success
            self._log_execution(tool_name, "success")

            return {
                "isError": False,
                "result": result,
                "tool": tool_name
            }

        except ValueError as e:
            # Validation error - retry might help after fix
            error = ErrorFactory.invalid_input(
                field_name=str(e),
                reason=str(e)
            )
            self._log_execution(tool_name, "validation_error")
            return self._format_error_response(error, tool_name)

        except TimeoutError as e:
            # Timeout - retry with backoff
            error = ErrorFactory.timeout(str(e))
            self._log_execution(tool_name, "timeout")
            return self._format_error_response(error, tool_name)

        except PermissionError as e:
            # Permission error - never retry
            error = ErrorFactory.access_denied(
                resource=tool_name,
                reason=str(e)
            )
            self._log_execution(tool_name, "permission_error")
            return self._format_error_response(error, tool_name)

        except Exception as e:
            # Unexpected error - include partial results
            error = MCPError(
                isError=True,
                errorCategory=ErrorCategory.BUSINESS.value,
                isRetryable=False,
                description="Tool execution failed unexpectedly",
                code="TOOL_ERROR",
                details={
                    "exception_type": type(e).__name__,
                    "exception_message": str(e)
                }
            )
            self._log_execution(tool_name, "error")
            return self._format_error_response(error, tool_name)

    def _validate_parameters(
        self,
        parameters: Dict[str, Any],
        tool_name: str
    ):
        """Validate required parameters."""
        required_fields = ["query"]  # Example requirement

        for field in required_fields:
            if field not in parameters:
                raise ValueError(field)

    def _format_error_response(
        self,
        error: MCPError,
        tool_name: str
    ) -> Dict[str, Any]:
        """Format error into standard response structure."""
        return {
            "isError": True,
            "error": error.to_dict(),
            "tool": tool_name
        }

    def _log_execution(self, tool_name: str, status: str):
        """Log execution for monitoring."""
        self.execution_history.append({
            "tool": tool_name,
            "status": status,
            "timestamp": datetime.utcnow().isoformat()
        })


# ================================================================================
# SECTION 8: ANTI-PATTERNS AND BEST PRACTICES
# ================================================================================

def print_error_handling_guide():
    """
    Print comprehensive error handling best practices and anti-patterns.
    """

    guide = """
    +=========================================================================+
    |              ERROR HANDLING BEST PRACTICES                             |
    +=========================================================================+

    ANTI-PATTERN 1: Generic Errors
    +---------------------------------------------------------------------+
    | BAD:                                                                   |
    |   return {"error": "Something went wrong"}                            |
    |                                                                       |
    | GOOD:                                                                  |
    |   return {                                                            |
    |     "isError": true,                                                  |
    |     "errorCategory": "transient",                                     |
    |     "isRetryable": true,                                             |
    |     "description": "Database connection timed out after 30s"         |
    |   }                                                                   |
    +---------------------------------------------------------------------+

    ANTI-PATTERN 2: Empty Results as Errors
    +---------------------------------------------------------------------+
    | BAD:                                                                   |
    |   if results is empty:                                               |
    |     return {"error": "No results found"}  # WRONG!                  |
    |                                                                       |
    | GOOD:                                                                  |
    |   if results is empty:                                                |
    |     return {"isError": false, "resultCount": 0, "results": []}      |
    +---------------------------------------------------------------------+

    ANTI-PATTERN 3: Business Errors as Retryable
    +---------------------------------------------------------------------+
    | BAD:                                                                   |
    |   # User exceeded rate limit, but you mark as retryable              |
    |   return {"isRetryable": true, ...}  # User retries forever!        |
    |                                                                       |
    | GOOD:                                                                  |
    |   # Business errors are never retryable                              |
    |   return {"isRetryable": false, "errorCategory": "business", ...}   |
    +---------------------------------------------------------------------+

    ANTI-PATTERN 4: Missing Error Context
    +---------------------------------------------------------------------+
    | BAD:                                                                   |
    |   return {"isError": true, "description": "Failed"}                 |
    |                                                                       |
    | GOOD:                                                                  |
    |   return {                                                            |
    |     "isError": true,                                                 |
    |     "errorCategory": "validation",                                   |
    |     "description": "Invalid query parameter",                        |
    |     "code": "INVALID_QUERY",                                         |
    |     "details": {"parameter": "query", "reason": "too long"}         |
    |   }                                                                   |
    +---------------------------------------------------------------------+

    ANTI-PATTERN 5: Swallowing Exceptions
    +---------------------------------------------------------------------+
    | BAD:                                                                   |
    |   try:                                                                |
    |     do_something()                                                    |
    |   except:                                                             |
    |     pass  # Silent failure!                                          |
    |                                                                       |
    | GOOD:                                                                  |
    |   try:                                                                |
    |     do_something()                                                    |
    |   except Exception as e:                                              |
    |     return ErrorFactory.service_unavailable(str(e))                  |
    +---------------------------------------------------------------------+

    +=========================================================================+
    |              ERROR CATEGORY QUICK REFERENCE                           |
    +=========================================================================+

    +------------------+-------------+----------------------------------------+
    | Category         | isRetryable | Common Causes                          |
    +------------------+-------------+----------------------------------------+
    | TRANSIENT        | TRUE        | Timeouts, network errors, rate limits,  |
    |                  |             | service restarts, temporary unavailability|
    +------------------+-------------+----------------------------------------+
    | VALIDATION       | TRUE        | Invalid input, missing fields,          |
    |                  |             | out-of-range values, type mismatches   |
    +------------------+-------------+----------------------------------------+
    | BUSINESS         | FALSE       | Policy violations, limit exceedances,   |
    |                  |             | quota exceeded, contract violations     |
    +------------------+-------------+----------------------------------------+
    | PERMISSION       | FALSE       | Access denied, invalid credentials,     |
    |                  |             | expired tokens, insufficient permissions|
    +------------------+-------------+----------------------------------------+

    """

    print(guide)


# ================================================================================
# SECTION 9: DEMONSTRATION
# ================================================================================

def run_error_handling_demo():
    """
    Demonstrate error handling in action.
    """

    print("\n" + "=" * 70)
    print("ERROR HANDLING DEMONSTRATION")
    print("=" * 70)

    executor = ToolExecutor()

    # Simulate different error scenarios
    scenarios = [
        {
            "name": "Timeout Error",
            "error": ErrorFactory.timeout(
                "Search API timed out after 30 seconds",
                {"api_endpoint": "/search", "timeout_ms": 30000}
            )
        },
        {
            "name": "Validation Error",
            "error": ErrorFactory.invalid_input(
                field_name="query",
                reason="Query exceeds maximum length of 1000 characters",
                details={"query_length": 1500, "max_length": 1000}
            )
        },
        {
            "name": "Policy Violation",
            "error": ErrorFactory.policy_violation(
                policy_name="rate-limit-policy",
                reason="Exceeded 1000 requests per hour",
                details={"current_requests": 1050, "limit": 1000}
            )
        },
        {
            "name": "Access Denied",
            "error": ErrorFactory.access_denied(
                resource="private-repository",
                reason="Token does not have read permission"
            )
        }
    ]

    for i, scenario in enumerate(scenarios, 1):
        print(f"\n--- Scenario {i}: {scenario['name']} ---")
        error = scenario["error"]

        print(f"isError: {error.isError}")
        print(f"errorCategory: {error.errorCategory}")
        print(f"isRetryable: {error.isRetryable}")
        print(f"description: {error.description}")
        print(f"code: {error.code}")
        if error.details:
            print(f"details: {error.details}")

        # Demonstrate retry logic
        if error.isRetryable:
            print("-> ACTION: Retry with backoff")
        else:
            print("-> ACTION: Do not retry, address root cause")


# ================================================================================
# SECTION 10: INTERVIEW Q&A
# ================================================================================

def print_interview_questions():
    """
    Print common interview questions about error handling.
    """

    qa = """
    +=========================================================================+
    |                      INTERVIEW Q&A                                     |
    +=========================================================================+

    Q: What is the isError flag and why is it needed?
    +-------------------------------------------------------------------------+
    | A: The isError flag is a boolean that MUST be true when an error       |
    |    occurs. It provides clear, unambiguous signaling of failure state.  |
    |    This allows consumers to immediately check isError before looking   |
    |    at other response fields.                                            |
    +-------------------------------------------------------------------------+

    Q: What are the four error categories and their retry behavior?
    +-------------------------------------------------------------------------+
    | A: (1) TRANSIENT - retry might help (timeouts, rate limits)           |
    |    (2) VALIDATION - retry after fixing input (invalid params)         |
    |    (3) BUSINESS - never retry (policy violations)                      |
    |    (4) PERMISSION - never retry (access denied)                       |
    +-------------------------------------------------------------------------+

    Q: What is the difference between access failure and empty result?
    +-------------------------------------------------------------------------+
    | A: Access failure = isError:true, isRetryable:true (connection issue) |
    |    Empty result = isError:false, resultCount:0 (valid outcome)         |
    |    Empty results should NOT trigger retries - there's nothing to find. |
    +-------------------------------------------------------------------------+

    Q: How does multi-agent error propagation work?
    +-------------------------------------------------------------------------+
    | A: Subagents handle errors locally first. Only unresolved errors      |
    |    propagate upward. This prevents error storms and provides context   |
    |    at each level. Each level can attempt recovery before escalating.  |
    +-------------------------------------------------------------------------+

    Q: What metadata is required for every error?
    +-------------------------------------------------------------------------+
    | A: (1) isError: true (required)                                        |
    |    (2) errorCategory: one of four categories                          |
    |    (3) isRetryable: boolean flag                                       |
    |    (4) description: human-readable message                             |
    +-------------------------------------------------------------------------+

    Q: What is an anti-pattern in error handling?
    +-------------------------------------------------------------------------+
    | A: Common anti-patterns include:                                       |
    |    - Generic errors without category/retry info                        |
    |    - Treating empty results as errors (causes infinite retries)       |
    |    - Marking business errors as retryable                              |
    |    - Swallowing exceptions without proper error response               |
    +-------------------------------------------------------------------------+

    """

    print(qa)


# ================================================================================
# MAIN EXECUTION
# ================================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("TOOL ERROR HANDLING - PRACTICE 01: STRUCTURED ERROR RESPONSES")
    print("=" * 70)

    # Print best practices guide
    print_error_handling_guide()

    # Demonstrate access vs empty distinction
    demonstrate_access_vs_empty()

    # Demonstrate error propagation
    demonstrate_error_propagation()

    # Run error handling demo
    run_error_handling_demo()

    # Print interview Q&A
    print_interview_questions()


# ================================================================================
# WHAT WE HAVE LEARNT
# =============================================================================

"""
SUMMARY OF KEY CONCEPTS:

1. THE isError FLAG
   - Boolean flag, ALWAYS true when error occurs
   - First check for any response handling
   - Clear signal of failure state

2. FOUR ERROR CATEGORIES
   - TRANSIENT: Timeouts, rate limits - retry might help (isRetryable: true)
   - VALIDATION: Invalid input - fix and retry (isRetryable: true)
   - BUSINESS: Policy violations - never retry (isRetryable: false)
   - PERMISSION: Access denied - never retry (isRetryable: false)

3. ACCESS FAILURE vs EMPTY RESULT
   - Access failure: isError=true, isRetryable=true (retry may work)
   - Valid empty: isError=false, resultCount=0 (don't retry)
   - Common mistake: treating empty as error causes infinite retries

4. REQUIRED METADATA
   - isError: true
   - errorCategory: string from four options
   - isRetryable: boolean
   - description: user-friendly message

5. MULTI-AGENT ERROR PROPAGATION
   - Subagents handle locally first
   - Only propagate unresolved errors upward
   - Add context at each level
   - Prevents error storms

6. ERROR FACTORY PATTERN
   - Standardized error creation
   - Consistent structure across codebase
   - Self-documenting error codes

7. ANTI-PATTERNS TO AVOID
   - Generic errors without category/retry info
   - Empty results treated as errors
   - Business errors marked as retryable
   - Swallowing exceptions silently
   - Missing error context/details

8. INTERVIEW QUESTIONS

   Q: What is the isError flag?
   A: Boolean flag that MUST be true when error occurs, used for clear
      failure state signaling.

   Q: How do you decide if an error is retryable?
   A: Check error category: TRANSIENT and VALIDATION are retryable,
      BUSINESS and PERMISSION are not.

   Q: What's the difference between access failure and empty result?
   A: Access failure is an error (isError:true) that might succeed on retry.
      Empty result is valid (isError:false) - nothing to find, don't retry.

   Q: How does error propagation work in multi-agent systems?
   A: Subagents try to handle locally first. Only unresolved errors
      propagate upward with context added at each level.
"""

print()
print("=" * 70)
print("END OF PRACTICE 01: STRUCTURED ERROR RESPONSES")
print("=" * 70)