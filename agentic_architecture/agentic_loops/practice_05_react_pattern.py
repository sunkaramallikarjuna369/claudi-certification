"""
PRACTICE 5: THE ReAct PATTERN (Reason + Act)
Teaching the AI to THINK step-by-step before acting!
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
        "name": "search",
        "description": "Search the web for information.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "read_file",
        "description": "Read the contents of a file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The file path to read"
                }
            },
            "required": ["path"]
        }
    },
    {
        "name": "calculate",
        "description": "Perform mathematical calculations.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The math expression to evaluate (e.g., '2 + 2', '100 * 0.07')"
                }
            },
            "required": ["expression"]
        }
    }
]


def execute_tool(name: str, tool_input: dict) -> str:
    """
    Execute a tool for the ReAct pattern.
    """
    if name == "search":
        query = tool_input.get("query", "")
        return f"Search results for '{query}': Found relevant information about the topic."

    elif name == "read_file":
        path = tool_input.get("path", "")
        return f"Contents of {path}: [File contents would be here]"

    elif name == "calculate":
        expression = tool_input.get("expression", "")
        try:
            result = eval(expression)
            return str(result)
        except Exception as e:
            return f"Error in calculation: {e}"

    return f"Unknown tool: {name}"


def run_react_loop(user_question: str):
    """
    Run the ReAct pattern - think step by step!
    """
    system_prompt = """You are a helpful assistant that uses the ReAct pattern.
Think step by step and show your work:

1. REASON about what the question is asking
2. PLAN the steps needed to answer
3. ACT by using tools as needed
4. OBSERVE the results from your actions
5. Provide the FINAL ANSWER

IMPORTANT: Use this format in your response:
- Thought: [your reasoning about the problem]
- Action: [tool name and why you're using it] (only when taking action)
- Observation: [what you learned from the action] (only after taking action)
- Answer: [your final conclusion]

Always show your reasoning so the user can follow your thought process."""

    messages = [
        {"role": "user", "content": user_question}
    ]

    iteration = 0

    while True:
        iteration += 1

        print(f"\n{'='*60}")
        print(f"ReAct ITERATION {iteration}")
        print('='*60)

        response = client.messages.create(
            model="claude-haiku-4-5-20250601",
            max_tokens=4096,
            system=system_prompt,
            messages=messages,
            tools=tools,
        )

        print(f"Stop reason: {response.stop_reason}")

        if response.stop_reason == "tool_use":

            assistant_message = {"role": "assistant", "content": []}
            tool_results_to_add = []

            for block in response.content:
                if block.type == "text" and block.text:
                    print(f"\nAI'S THINKING:")
                    print(f"{'-'*60}")
                    print(block.text)
                    print(f"{'-'*60}")
                    assistant_message["content"].append({
                        "type": "text",
                        "text": block.text
                    })
                elif block.type == "tool_use":
                    print(f"\nACTION:")
                    print(f"   Tool: {block.name}")
                    print(f"   Input: {block.input}")

                    result = execute_tool(block.name, block.input)

                    print(f"OBSERVATION: {result}")

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

            print(f"   Adding to history, continuing to think...")
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

        if iteration > 10:
            print("Max iterations reached")
            return None


if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    print("\n" + "="*60)
    print("PRACTICE 5: THE ReAct PATTERN (Reason + Act)")
    print("="*60)

    question = """
    If I have $10,000 invested at 7% annual interest,
    compounded monthly, how much will I have after 5 years?
    Calculate this step by step and show your work.
    """

    print(f"USER QUESTION:\n{question}")
    print("\n" + "-"*60 + "\n")

    result = run_react_loop(question)

    print("""
================================================================================
WHAT JUST HAPPENED?
================================================================================

    1. We asked Claude to calculate compound interest: $10,000 at 7% for 5 years
    2. We gave Claude a special PROMPT instructing it to use the ReAct pattern
    3. ReAct = Reason + Act - Think step-by-step before and after acting
    4. Claude showed its THINKING with "Thought:" labels
    5. Claude took ACTIONS by calling the calculate tool
    6. Claude made OBSERVATIONS based on the results
    7. Finally, Claude provided the ANSWER with complete calculations

    KEY INSIGHT: ReAct makes AI decision-making TRANSPARENT!
    You can see WHY the AI chose each step, not just the final answer.
    This is crucial for debugging and understanding AI behavior.
================================================================================
""")
    print("\n" + "="*60)
    print("PROGRAM COMPLETE!")
    print("="*60)
