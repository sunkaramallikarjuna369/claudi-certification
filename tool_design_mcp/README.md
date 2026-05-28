"""
+===========================================================================+
|                                                                           |
|  DOMAIN 2: TOOL DESIGN & MCP INTEGRATION (18%)                           |
|                                                                           |
|  This folder covers how to design effective tool schemas, implement     |
|  MCP servers and clients, and integrate external services into          |
|  Claude-powered applications.                                            |
|                                                                           |
|  EXAM WEIGHT: 18% of certification                                        |
|                                                                           |
+===========================================================================+

FIVE CORE SUBTOPICS
===========================================================================

    +======================================================================+
    ||  2.1 Tool Interface Design                                          ||
    ||  - Design effective tool schemas                                    ||
    ||  - JSON schema definitions for tools                                ||
    ||  - Best practices for tool naming and descriptions                 ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  2.2 Structured Error Responses                                     ||
    ||  - Error handling patterns for tools                                ||
    ||  - Graceful degradation strategies                                  ||
    ||  - User-friendly error messages                                     ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  2.3 Tool Distribution & Tool Choice                                ||
    ||  - How Claude selects which tools to use                            ||
    ||  - Tool selection optimization                                       ||
    ||  - Batch tool patterns                                               ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  2.4 MCP Server Integration                                         ||
    ||  - Model Context Protocol fundamentals                              ||
    ||  - Server implementation patterns                                    ||
    ||  - Client integration strategies                                     ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  2.5 Built-in Tools                                                 ||
    ||  - Claude Code built-in tool capabilities                           ||
    ||  - Tool selection and routing                                        ||
    ||  - Custom vs built-in tool usage                                     ||
    ||                                                                      ||
    +======================================================================+

KEY CONCEPTS TO MASTER
===========================================================================

    1. TOOL SCHEMA DESIGN
       - JSON Schema format for tool definitions
       - Required vs optional parameters
       - Description clarity for Claude understanding
       - Example syntax and validation

    2. MCP (Model Context Protocol)
       - Server-client architecture
       - Tool registration and discovery
       - Streaming and async patterns
       - Security and authentication

    3. TOOL SELECTION MECHANICS
       - How Claude decides which tools to use
       - Parallel tool calls
       - Tool choice optimization
       - Fallback strategies

    4. ERROR HANDLING PATTERNS
       - Graceful degradation
       - Retry logic
       - User-friendly error messages
       - Error codes and categories

    5. INTEGRATION STRATEGIES
       - External API integration
       - Database operations via tools
       - File system operations
       - Service mesh patterns

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


# ============================================================================
# TOOL SCHEMA DESIGN - Practice Files
# ============================================================================

def demonstrate_tool_schema():
    """
    Demonstrates proper tool schema design with JSON format.
    """

    client = anthropic.Anthropic(api_key=API_KEY)

    print("\n" + "=" * 70)
    print("TOOL SCHEMA DESIGN - JSON Format Demonstration")
    print("=" * 70)

    # Example tool schema
    tool_schema = {
        "name": "calculate_refund",
        "description": "Calculate and process refund for customer order",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The unique order identifier"
                },
                "amount": {
                    "type": "number",
                    "description": "Refund amount in dollars"
                },
                "reason": {
                    "type": "string",
                    "description": "Reason for refund",
                    "enum": ["defective", "wrong_item", "late_delivery", "customer_request"]
                }
            },
            "required": ["order_id", "amount"]
        }
    }

    print("""
    +======================================================================+
    ||                                                                      ||
    ||  WELL-DESIGNED TOOL SCHEMA:                                          ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  Key Elements:                                                       ||
    ||  1. Clear, descriptive name (calculate_refund)                       ||
    ||  2. Detailed description explaining purpose and usage               ||
    ||  3. Structured input_schema with type, description                   ||
    ||  4. Required fields marked explicitly                                ||
    ||  5. Enum for controlled values (reason field)                        ||
    ||                                                                      ||
    ||  WHY THIS MATTERS:                                                  ||
    ||  - Claude understands when and how to use the tool                  ||
    ||  - Parameter validation prevents errors                              ||
    ||  - Clear descriptions improve tool selection accuracy               ||
    ||                                                                      ||
    +======================================================================+
    """)

    print(f"Tool Schema:\n{tool_schema}")

    # Demonstrate with actual API call
    message = client.messages.create(
        model="claude-haiku-4-5-20250601",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": "Explain why tool schema design is important for AI agent "
                      "systems. What makes a good tool schema vs a bad one?"
        }]
    )

    print("\nAI Response:")
    print(f"    {message.content[0].text[:300]}...")


def show_mcp_concepts():
    """
    Shows Model Context Protocol fundamentals.
    """

    print("\n" + "=" * 70)
    print("MODEL CONTEXT PROTOCOL (MCP) - FUNDAMENTALS")
    print("=" * 70)

    print("""
    +======================================================================+
    ||                                                                      ||
    ||  WHAT IS MCP?                                                        ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  Model Context Protocol is a standardized way to connect AI models   ||
    ||  to external tools, data sources, and services.                      ||
    ||                                                                      ||
    ||  ARCHITECTURE:                                                       ||
    ||                                                                      ||
    ||  +----------------+      +------------------+      +----------------+||
    ||  | Claude Model  | <--> | MCP Server      | <--> | External API  ||
    ||  |               |      | (Bridge)         |      | / DB / Files   ||
    ||  +----------------+      +------------------+      +----------------+||
    ||                                                                      ||
    ||  MCP Server responsibilities:                                         ||
    ||  - Tool registration and discovery                                    ||
    ||  - Request/response transformation                                   ||
    ||  - Authentication and security                                       ||
    ||  - Rate limiting and quotas                                          ||
    ||                                                                      ||
    +======================================================================+
    """)


def show_error_handling():
    """
    Shows structured error response patterns.
    """

    print("\n" + "=" * 70)
    print("STRUCTURED ERROR RESPONSES")
    print("=" * 70)

    print("""
    +======================================================================+
    ||                                                                      ||
    ||  BAD ERROR (Unstructured):                                           ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  "Error occurred"                                                    ||
    ||                                                                      ||
    ||  WHY IT'S BAD:                                                       ||
    ||  - No error code                                                    ||
    ||  - No actionable information                                         │
    ||  - User doesn't know what happened or what to do                    ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  GOOD ERROR (Structured):                                             ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  {                                                                    ||
    ||    "error": {                                                         ||
    ||      "code": "INVALID_ORDER_ID",                                    ||
    ||      "message": "Order ID 'ABC123' not found",                       ||
    ||      "action": "Verify order ID or contact support",                ||
    ||      "retry_possible": false                                        ||
    ||    }                                                                  ||
    ||  }                                                                    ||
    ||                                                                      ||
    ||  WHY IT'S GOOD:                                                      ||
    ||  - Machine-readable error code                                      ||
    ||  - Human-readable message                                           ||
    ||  - Suggested action                                                 ||
    ||  - Retry guidance                                                   ||
    ||                                                                      ||
    +======================================================================+
    """)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("""
+===========================================================================+
|                                                                           |
|  TOOL DESIGN & MCP INTEGRATION - TEMPLATE                               |
|                                                                           |
|  This folder contains practice files for Domain 2 of the certification.  |
|                                                                           |
|  Subfolders:                                                             |
|  - tool_schema_design/      (2.1)                                        |
|  - mcp_server_implementation/ (2.2)                                     |
|  - mcp_client_integration/ (2.3)                                        |
|  - tool_error_handling/    (2.4)                                        |
|  - tool_selection_routing/ (2.5)                                        |
|                                                                           |
+===========================================================================+
    """)

    demonstrate_tool_schema()
    show_mcp_concepts()
    show_error_handling()

    print("\n" + "=" * 70)
    print("WHAT WE HAVE LEARNT")
    print("=" * 70)
    print("""
    +======================================================================+
    ||  1. TOOL SCHEMA DESIGN:                                             ||
    ||                                                                      ||
    ||  - Clear, descriptive names for tools                                ||
    ||  - Structured JSON schema with types and descriptions               ||
    ||  - Required vs optional parameters                                  ||
    ||  - Enum for controlled value sets                                   ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  2. MCP (Model Context Protocol):                                   ||
    ||                                                                      ||
    ||  - Standardized way to connect AI to external tools                 ||
    ||  - Server-client architecture with bridge pattern                   ||
    ||  - Handles registration, auth, rate limiting                      ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  3. ERROR HANDLING:                                                 ||
    ||                                                                      ||
    ||  - Always use structured error responses                             ||
    ||  - Include: error code, message, action, retry flag                ||
    ||  - Never give unstructured "Error occurred" messages              ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  4. TOOL SELECTION:                                                 ||
    ||                                                                      ||
    ||  - Claude intelligently chooses which tools to use                  ||
    ||  - Can call multiple tools in parallel                               ||
    ||  - Tool descriptions help Claude decide                            ||
    ||                                                                      ||
    +======================================================================+

    Next: Explore each submodule folder for detailed practice files!
    """)


"""
+===========================================================================+
|                                                                           |
|  KEY CONCEPTS FROM THIS FILE:                                            |
|                                                                           |
|  TOOL SCHEMA:                                                            |
|  - JSON format with name, description, input_schema                   |
|  - Type annotations for all parameters                                  |
|  - Required fields marked explicitly                                     |
|  - Enum for controlled values                                             |
|                                                                           |
|  MCP (Model Context Protocol):                                          |
|  - Standardized tool integration protocol                                |
|  - Server-client architecture                                            |
|  - Handles registration, auth, security, rate limiting                |
|                                                                           |
|  ERROR HANDLING:                                                         |
|  - Structured responses with code, message, action                      |
|  - No unstructured error messages                                        |
|  - Include retry_possible flag                                           |
|                                                                           |
|  TOOL SELECTION:                                                         |
|  - Claude chooses tools based on descriptions                           |
|  - Parallel tool calls possible                                           |
|  - Optimization through clear schema design                             |
|                                                                           |
|  EXAM TIPS:                                                              |
|  - Know MCP architecture components                                     |
|  - Tool schema best practices                                           |
|  - Error handling patterns                                               |
|                                                                           |
+===========================================================================+
"""