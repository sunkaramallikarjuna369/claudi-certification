# Agentic Loop Architecture

A comprehensive guide to building agentic systems with Claude using tool use and iterative loops.

## Overview

The agentic loop is a fundamental pattern where an AI model can use tools, observe results, and continue processing until it reaches a conclusion. The key to this pattern is the `stop_reason` field in API responses.

## Folder Structure

```
agentic_architecture/
├── agentic_loops/
│   ├── agentic-loop.md          # Core documentation
│   ├── practice_01_basic_loop.py    # Basic agentic loop
│   ├── practice_02_multi_tool.py    # Multiple tools
│   ├── practice_03_sequential_tools.py  # Sequential execution
│   ├── practice_04_error_handling.py    # Error handling
│   ├── practice_05_react_pattern.py     # ReAct pattern
│   ├── practice_06_stateful_agent.py    # Stateful agent
│   └── TEMPLATE.md              # Quick reference template
```

## Key Concepts

### The Loop

```
┌─────────────┐
│ User Input  │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────┐
│  Send to Claude Messages API│
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│  Receive Response            │
│  Check stop_reason          │
└──────┬──────────────────────┘
       │
       ├── tool_use? ──► Execute tools → Append results → Loop
       │
       └── end_turn? ──► Present to user → Done
```

### Stop Reason

The `stop_reason` field is the **authoritative** signal for controlling the loop:

| Stop Reason | Action |
|-------------|--------|
| `tool_use` | Execute tools, append results, continue loop |
| `end_turn` | Present final response, exit loop |

## Practice Files

| File | Description |
|------|-------------|
| `practice_01_basic_loop.py` | Simplest possible agentic loop with one tool |
| `practice_02_multi_tool.py` | Multiple tools available to the model |
| `practice_03_sequential_tools.py` | Tools that depend on each other's output |
| `practice_04_error_handling.py` | Graceful handling of tool failures |
| `practice_05_react_pattern.py` | ReAct (Reason + Act) reasoning pattern |
| `practice_06_stateful_agent.py` | Agent that maintains state across sessions |

## Running the Examples

```bash
# Install dependencies
pip install anthropic python-dotenv

# Set your API key
export ANTHROPIC_API_KEY=your-key-here

# Run any practice file
python practice_01_basic_loop.py
```

## Quick Reference Code

```python
from anthropic import Anthropic

client = Anthropic()
tools = [...]  # Your tool definitions

messages = [{"role": "user", "content": "Your task"}]

while True:
    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=4096,
        messages=messages,
        tools=tools,
    )

    if response.stop_reason == "tool_use":
        for block in response.content:
            if block.type == "tool_use":
                result = execute_tool(block.name, block.input)
                messages.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    }]
                })
        continue

    elif response.stop_reason == "end_turn":
        print(response.content[0].text)
        break
```

## Anti-Patterns to Avoid

- ❌ Parsing natural language like "I'm done"
- ❌ Using iteration count as primary stopping mechanism
- ❌ Checking `content[0].type == "text"` for completion

See `agentic-loop.md` for detailed documentation.