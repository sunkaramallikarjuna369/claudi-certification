# Agentic Loop Architecture

## Sequence Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        AGENTIC LOOP LIFECYCLE                       │
└─────────────────────────────────────────────────────────────────────┘

USER ───────────────────────────────> ENVIRONMENT ─────────────────> MODEL
│                                       │                              │
│  1. Send Request                      │                              │
│     (conversation history)            │                              │
│───────────────────────────────────────>                              │
│                                       │                              │
│                                       │  2. Analyze Context          │
│                                       │──────────────────────────────>│
│                                       │                              │
│                                       │  3. Model-Driven Decision    │
│                                       │<──────────────────────────────│
│                                       │                              │
│                                       │  4. Generate Response         │
│                                       │     + check stop_reason       │
│                                       │                              │
│                     ┌───────────────────────────────────┐           │
│                     │         STOP_REASON CHECK          │           │
│                     └───────────────────────────────────┘           │
│                                       │                              │
│                                       ├──+ stop_reason = "tool_use"? │
│                                       │  │                           │
│                                       ├─ YES ────────────────────────┤
│                                       │  │                           │
│                                       │  5. Execute Tool(s)          │
│                                       │──────────────────────────────>│
│                                       │                              │
│                                       │  6. Append Results to        │
│                                       │     Conversation History      │
│                                       │                              │
│                                       │  7. Loop Back (with results) │
│                                       │══════════════════════════════│
│                                       │                              │
│                                       ├─ NO (end_turn) ──────────────┤
│                                       │                              │
│  8. Present Final Response            │                              │
│<──────────────────────────────────────│                              │
│     to User                           │                              │
```

## Interaction Flow

```
┌──────────┐     Request      ┌─────────────┐    Analyze    ┌─────────┐
│   USER   │─────────────────>│ ENVIRONMENT │──────────────>│  MODEL  │
│          │                  │             │               │         │
│          │  Final Response  │             │  Tool Calls   │         │
│<─────────│<─────────────────│             │<───────────────│         │
└──────────┘                  └─────────────┘               └─────────┘
                                    ▲     ▲
                                    │     │
                              Append│     │Execute
                              Results    │Results
                                    │     │
                                    └─────┘
```

## The Agentic Loop

```
                    ┌─────────────────────────────┐
                    │       USER REQUEST          │
                    │  (with conversation history)│
                    └─────────────┬───────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────────┐
                    │    CLAUDE MESSAGES API      │
                    │   Send request to model      │
                    └─────────────┬───────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────────┐
                    │    RECEIVE RESPONSE         │
                    │    Inspect stop_reason      │
                    └─────────────┬───────────────┘
                                  │
                         ┌────────┴────────┐
                         │                 │
                    ┌────▼────┐      ┌─────▼─────┐
                    │tool_use │      │ end_turn  │
                    └────┬────┘      └─────┬─────┘
                         │                 │
                         ▼                 ▼
              ┌─────────────────┐   ┌─────────────────┐
              │ Execute Tools   │   │ Present Final   │
              │ Append results  │   │ Response to     │
              │ to history      │   │ User ✓          │
              └────────┬─────────┘   └─────────────────┘
                       │
                       └──────> LOOP BACK TO API
```

## Anti-Patterns (What NOT To Do)

```
┌─────────────────────────────────────────────────────────────────────┐
│                          ANTI-PATTERNS                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ✗ Parsing natural language phrases ("I'm done", "All done")       │
│    → Unreliable, model may vary wording                             │
│                                                                      │
│  ✗ Using iteration caps as primary stopping mechanism               │
│    → May cut off work or run unnecessary iterations                  │
│                                                                      │
│  ✗ Checking content[0].type == "text" for completion                │
│    → Claude can return text alongside tool_use blocks                │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Correct Implementation Pattern

```python
from anthropic import Anthropic

client = Anthropic()

messages = [{"role": "user", "content": "Your task here"}]

while True:
    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=4096,
        messages=messages,
        tools=[...],  # Your tool definitions
    )

    # Check stop_reason - the authoritative signal
    if response.stop_reason == "tool_use":
        for block in response.content:
            if block.type == "tool_use":
                tool_name = block.name
                tool_input = block.input

                # Execute the tool
                result = execute_tool(tool_name, tool_input)

                # Append tool result to conversation history
                messages.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    }]
                })
        # Loop continues - send back to model
        continue

    elif response.stop_reason == "end_turn":
        # Present response to user and exit loop
        final_response = response.content[0].text
        print(final_response)
        break
```

## Key Principles

| Principle | Description |
|-----------|-------------|
| **stop_reason is Authoritative** | Use `stop_reason` field, not natural language parsing |
| **Model-Driven Decisions** | Claude decides which tools to call based on context |
| **Deterministic Loop Control** | Loop continues on `tool_use`, exits on `end_turn` |
| **Append Results to History** | Tool results must be added to conversation for next iteration |

## Loop States

```
                    ┌──────────────────┐
                    │    IDLE          │
                    │  (Awaiting Input)│
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
              ┌─────│   PROCESSING     │─────┐
              │     │  (API Request)   │     │
              │     └──────────────────┘     │
              │                │            │
         ┌────▼────┐      ┌────▼────┐      │
         │tool_use │      │end_turn │      │
         └────┬────┘      └────┬─────┘      │
              │                │            │
              ▼                ▼            │
     ┌──────────────┐  ┌──────────────┐     │
     │   EXECUTING  │  │    DONE     │     │
     │    TOOLS     │  │  (Present   │     │
     └──────┬───────┘  │   Output)   │     │
            │          └──────────────┘     │
            │                ▲              │
            │                │              │
            └────────────────┴────────────┘
                 (Loop Back to API)
```