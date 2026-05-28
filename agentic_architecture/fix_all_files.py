# Script to fix message handling in all practice files
# Adds assistant message BEFORE tool_result (required by API)

import os
import re


def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'messages.append({' not in content:
        return False

    new_code = '''if response.stop_reason == "tool_use":
    # CASE 1: Claude wants to use a tool

    print("\\nClaude wants to use a tool!")

    # Build the assistant message with tool_use blocks
    assistant_message = {"role": "assistant", "content": []}
    tool_results = []

    for block in response.content:
        if block.type == "text" and block.text:
            assistant_message["content"].append({
                "type": "text",
                "text": block.text
            })
        elif block.type == "tool_use":
            tool_name = block.name
            tool_input = block.input

            print(f"\\n   Tool called: {tool_name}")
            print(f"   Input: {tool_input}")

            result = execute_tool(tool_name, tool_input)
            print(f"   Result: {result}")

            assistant_message["content"].append({
                "type": "tool_use",
                "id": block.id,
                "name": block.name,
                "input": block.input
            })

            tool_results.append({"tool_use_id": block.id, "content": result})

    # Add assistant message FIRST, then tool results
    messages.append(assistant_message)
    for tr in tool_results:
        messages.append({
            "role": "user",
            "content": [{"type": "tool_result", "tool_use_id": tr["tool_use_id"], "content": tr["content"]}]
        })

    print("\\nLooping back to Claude with tool results...")
    continue'''

    if 'assistant_message = {"role": "assistant"' in content:
        print(f"Already fixed: {filepath}")
        return False

    match = re.search(r'if response\.stop_reason == "tool_use":.*?# Loop back to send results to Claude\.\.\.\s*continue', content, re.DOTALL)
    if match:
        content = content[:match.start()] + new_code + content[match.end():]
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed: {filepath}")
        return True

    print(f"Could not find pattern in: {filepath}")
    return False


# Find all Python files
for root, dirs, files in os.walk('agentic_architecture'):
    for file in files:
        if file.endswith('.py'):
            fix_file(os.path.join(root, file))

print("\nDone!")
print("\nNote: practice_01 was already manually fixed. Check others manually if needed.")