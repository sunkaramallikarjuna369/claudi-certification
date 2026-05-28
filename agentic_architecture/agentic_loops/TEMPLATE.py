"""
AGENTIC LOOP TEMPLATE
Your starting point for building AI agents!
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
        "name": "tool_name",
        "description": "What this tool does.",
        "input_schema": {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "Description of param1"
                }
            },
            "required": ["param1"]
        }
    }
]


def execute_tool(name: str, tool_input: dict) -> str:
    """Execute a tool and return the result as a string."""
    if name == "tool_name":
        param1 = tool_input.get("param1")
        return f"Result: {param1}"

    return f"Unknown tool: {name}"


def run_agentic_loop(
    user_message: str,
    model: str = "claude-haiku-4-5-20250601",
    max_iterations: int = 20,
    tools: list = None
) -> str:
    """Run the agentic loop pattern."""
    if tools is None:
        tools = []

    messages = [{"role": "user", "content": user_message}]

    for iteration in range(1, max_iterations + 1):
        print(f"\n{'='*50}")
        print(f"Iteration {iteration}")
        print('='*50)

        response = client.messages.create(
            model=model,
            max_tokens=4096,
            messages=messages,
            tools=tools,
        )

        print(f"Stop reason: {response.stop_reason}")

        if response.stop_reason == "tool_use":
            print("\nClaude wants to use a tool!")

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

                    print(f"\n   Tool: {tool_name}")
                    print(f"   Input: {tool_input}")

                    result = execute_tool(tool_name, tool_input)
                    print(f"   Result: {result}")

                    assistant_message["content"].append({
                        "type": "tool_use",
                        "id": block.id,
                        "name": block.name,
                        "input": block.input
                    })

                    tool_results_to_add.append({
                        "tool_use_id": block.id,
                        "content": result
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
            print("\nClaude has the final answer!")

            final_text = ""
            for block in response.content:
                if block.type == "text" and block.text:
                    final_text = block.text
                    break

            return final_text

    return "Max iterations reached"


class AgenticConversation:
    """Manage conversation state for an agentic system."""

    def __init__(self, tools: list = None, model: str = "claude-haiku-4-5-20250601"):
        self.messages = []
        self.tools = tools or []
        self.model = model
        self.iteration_count = 0

    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})

    def add_system_message(self, content: str):
        self.messages.insert(0, {"role": "system", "content": content})

    def run(self, user_input: str, max_iterations: int = 20) -> str:
        self.add_message("user", user_input)

        for self.iteration_count in range(1, max_iterations + 1):
            print(f"\n[Iteration {self.iteration_count}]")

            response = client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=self.messages,
                tools=self.tools,
            )

            if response.stop_reason == "tool_use":
                assistant_message = {"role": "assistant", "content": []}
                tool_results_to_add = []

                for block in response.content:
                    if block.type == "text" and block.text:
                        assistant_message["content"].append({
                            "type": "text",
                            "text": block.text
                        })
                        self.add_message("assistant", block.text)
                    elif block.type == "tool_use":
                        result = execute_tool(block.name, block.input)

                        assistant_message["content"].append({
                            "type": "tool_use",
                            "id": block.id,
                            "name": block.name,
                            "input": block.input
                        })

                        tool_results_to_add.append({
                            "tool_use_id": block.id,
                            "content": result
                        })

                self.messages.append(assistant_message)

                for tool_result in tool_results_to_add:
                    self.messages.append({
                        "role": "user",
                        "content": [{
                            "type": "tool_result",
                            "tool_use_id": tool_result["tool_use_id"],
                            "content": tool_result["content"]
                        }]
                    })

                continue

            elif response.stop_reason == "end_turn":
                final = ""
                for block in response.content:
                    if block.type == "text" and block.text:
                        final = block.text
                        break
                self.add_message("assistant", final)
                return final

        return "Max iterations reached"

    def reset(self):
        system_msgs = [m for m in self.messages if m["role"] == "system"]
        self.messages = system_msgs
        self.iteration_count = 0


if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    print("\n" + "="*60)
    print("AGENTIC LOOP TEMPLATE")
    print("="*60)

    print("\n" + "-"*60)
    print("Simple run_agentic_loop() function")
    print("-"*60 + "\n")

    result = run_agentic_loop(
        user_message="Your task here!",
        tools=tools
    )

    print(f"\nFINAL RESULT:\n{result}")

    print("""
================================================================================
WHAT JUST HAPPENED?
================================================================================

    1. This is a TEMPLATE - use it as a starting point for your agents!
    2. The run_agentic_loop() function is the core pattern:
       - Send message → Get response → Check stop_reason
       - If tool_use: execute tools and loop back
       - If end_turn: return the final answer
    3. The AgenticConversation class adds STATE MANAGEMENT
    4. Customize tools, prompts, and error handling for your use case

    COPY THIS TEMPLATE to build your own agents!
    Key things to customize:
    - Define your tools in the tools list
    - Implement execute_tool() for each tool
    - Add system prompts for specialized behavior
    - Handle errors gracefully
================================================================================
""")
    print("\n" + "="*60)
    print("TEMPLATE COMPLETE!")
    print("="*60)