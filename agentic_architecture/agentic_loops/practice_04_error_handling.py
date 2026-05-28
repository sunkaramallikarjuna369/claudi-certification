"""
PRACTICE 4: ERROR HANDLING IN AGENTIC LOOPS
Because things go wrong, and that's OK!
"""

import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY", "")
api_base = os.getenv("ANTHROPIC_API_BASE", "")

from anthropic import Anthropic
client_kwargs = {"api_key": api_key} if api_key else {}
if api_base:
    client_kwargs["base_url"] = api_base
client = Anthropic(**client_kwargs)

tools = [
    {
        "name": "divide_numbers",
        "description": "Divide one number by another. Will return an error if you try to divide by zero!",
        "input_schema": {
            "type": "object",
            "properties": {
                "dividend": {
                    "type": "number",
                    "description": "The number to be divided (the top number in division)"
                },
                "divisor": {
                    "type": "number",
                    "description": "The number to divide by (the bottom number). CANNOT be zero!"
                }
            },
            "required": ["dividend", "divisor"]
        }
    },
    {
        "name": "get_user_data",
        "description": "Get user information from the database. Available users: ID '1' (Alice), ID '2' (Bob).",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "The user's ID number (e.g., '1', '2', '999'). Note: only IDs 1 and 2 exist!"
                }
            },
            "required": ["user_id"]
        }
    },
    {
        "name": "send_email",
        "description": "Send an email to a recipient.",
        "input_schema": {
            "type": "object",
            "properties": {
                "to": {
                    "type": "string",
                    "description": "The recipient's email address"
                },
                "subject": {
                    "type": "string",
                    "description": "The email subject line"
                },
                "body": {
                    "type": "string",
                    "description": "The email message body"
                }
            },
            "required": ["to", "subject", "body"]
        }
    }
]


class ToolExecutionError(Exception):
    """Custom exception for tool-specific errors."""
    pass


def execute_tool(name: str, tool_input: dict) -> dict:
    """
    Execute a tool with comprehensive error handling.
    """
    try:
        if name == "divide_numbers":
            dividend = tool_input["dividend"]
            divisor = tool_input["divisor"]

            if divisor == 0:
                raise ToolExecutionError("Cannot divide by zero!")

            result = dividend / divisor

            return {
                "success": True,
                "result": f"{dividend} / {divisor} = {result:.4f}",
                "raw_value": result
            }

        elif name == "get_user_data":
            user_id = tool_input["user_id"]

            users = {
                "1": {"name": "Alice", "email": "alice@example.com"},
                "2": {"name": "Bob", "email": "bob@example.com"}
            }

            if user_id == "999":
                raise ToolExecutionError(f"User with ID {user_id} not found in database")

            user = users.get(user_id)

            if user:
                return {
                    "success": True,
                    "result": f"User found: {user['name']} ({user['email']})"
                }
            else:
                raise ToolExecutionError(f"No user found with ID {user_id}")

        elif name == "send_email":
            return {
                "success": True,
                "result": f"Email sent to {tool_input['to']} with subject: {tool_input['subject']}"
            }

        else:
            return {
                "success": False,
                "error": f"Unknown tool: {name}"
            }

    except ToolExecutionError as e:
        return {
            "success": False,
            "error": str(e)
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {type(e).__name__}: {e}"
        }


def run_agentic_loop(user_message: str):
    """
    Run the agentic loop with proper error handling.
    """
    messages = [{"role": "user", "content": user_message}]
    iteration = 0

    while True:
        iteration += 1

        print(f"\n{'='*60}")
        print(f"ITERATION {iteration}")
        print('='*60)

        response = client.messages.create(
            model="claude-haiku-4-5-20250601",
            max_tokens=4096,
            messages=messages,
            tools=tools,
        )

        print(f"Stop reason: {response.stop_reason}")

        if response.stop_reason == "tool_use":
            print("\nTool execution:")

            assistant_message = {"role": "assistant", "content": []}
            tool_results_to_add = []

            for block in response.content:
                if block.type == "text" and block.text:
                    assistant_message["content"].append({
                        "type": "text",
                        "text": block.text
                    })
                elif block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input

                    print(f"\n   Calling: {tool_name}")
                    print(f"   Input: {tool_input}")

                    result = execute_tool(tool_name, tool_input)

                    if result["success"]:
                        print(f"   SUCCESS: {result['result']}")
                        content = result['result']
                    else:
                        print(f"   ERROR: {result['error']}")
                        content = f"Error: {result['error']}"

                    assistant_message["content"].append({
                        "type": "tool_use",
                        "id": block.id,
                        "name": block.name,
                        "input": block.input
                    })

                    tool_results_to_add.append({
                        "tool_use_id": block.id,
                        "content": content
                    })

            messages.append(assistant_message)

            for tool_result in tool_results_to_add:
                messages.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": tool_result["tool_use_id"],
                        "content": tool_result["content"]
                    }]
                })

            continue

        elif response.stop_reason == "end_turn":
            print(f"\n{'='*60}")
            print("FINAL ANSWER:")
            print('='*60)
            final_text = ""
            for block in response.content:
                if block.type == "text" and block.text:
                    final_text = block.text
                    break
            print(final_text)
            print('='*60)

            return final_text


if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    print("\n" + "="*60)
    print("PRACTICE 4: ERROR HANDLING IN AGENTIC LOOPS")
    print("="*60)

    examples = [
        ("Example 1: Divide by zero (ERROR)", "What is 100 divided by 0?"),
        ("Example 2: User not found (ERROR)", "Get user data for user ID 999"),
        ("Example 3: Valid user (SUCCESS)", "Get user data for user ID 1"),
    ]

    for title, query in examples:
        print(f"\n{'#'*60}")
        print(f"{title}")
        print(f"{'#'*60}")
        print(f"Query: {query}\n")
        run_agentic_loop(query)

    print("""
================================================================================
WHAT JUST HAPPENED?
================================================================================

    1. We tested 3 scenarios with different error conditions:
       - Divide by zero (math error)
       - User ID 999 (not found error)
       - User ID 1 (success)
    2. Each tool execution was wrapped in TRY/EXCEPT blocks
    3. When an error occurred, we returned a structured error response
    4. The error was passed back to Claude so it could handle it gracefully
    5. Claude adapted its response based on the error it received

    KEY INSIGHT: Robust agents handle errors gracefully!
    Instead of crashing, the agent learns from errors and tries alternatives.
================================================================================
""")
    print("\n" + "="*60)
    print("PROGRAM COMPLETE!")
    print("="*60)
