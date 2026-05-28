# Multi-Agent Orchestration Patterns

A comprehensive guide to orchestrating multiple AI agents working together.

## Overview

Multi-agent orchestration is about coordinating multiple specialized agents to work together on complex tasks. Instead of one agent doing everything, we have a COORDINATOR that assigns work to specialized agents.

## Folder Structure

```
multi_agent_orchestration/
├── README.md                    # This file
├── orchestration-patterns.md    # Core documentation
├── practice_01_hub_spoke_coordinator.py    # Basic coordination
├── practice_02_dynamic_selection.py        # Smart agent selection
├── practice_03_scope_partitioning.py       # Dividing work
├── practice_04_iterative_refinement.py    # Quality improvement
├── practice_05_context_passing.py          # Passing context properly
├── practice_06_full_orchestrator.py        # Complete system
└── TEMPLATE.py                     # Quick reference template
```

## Core Patterns

### 1. Hub-and-Spoke (Coordinator Pattern)
All communication flows through a central coordinator. Subagents never communicate directly.

```
                    COORDINATOR (Hub)
                    ┌─────────────────┐
                    │                 │
        ┌───────────┼────────┬────────┘
        │           │        │
        ▼           ▼        ▼
    Agent A    Agent B   Agent C
        │           │        │
        └───────────┼────────┘
                    │
            BACK TO COORDINATOR
```

### 2. Dynamic Subagent Selection
The coordinator decides which agents are needed based on the task complexity.

| Task Type | Agents Used |
|-----------|-------------|
| Simple question | 1 agent |
| Research + analysis | 2 agents |
| Complex report | 3+ agents |

### 3. Scope Partitioning
Divide work so agents don't overlap:
- Agent A: "Solar energy only"
- Agent B: "Wind energy only"
- Agent C: "Hydro only"

### 4. Iterative Refinement
Generate → Check for gaps → Refine → Check again → Done

### 5. Explicit Context Passing
**CRITICAL**: Subagents don't inherit context. Everything must be explicitly passed!

```python
# WRONG (assumes context)
subagent_prompt = "Write about {topic}"

# CORRECT (explicit context)
subagent_prompt = f"""
ORIGINAL REQUEST: {user_request}
STYLE REQUIREMENTS: {style}
PREVIOUS WORK: {research_data}
TASK: Write about {topic}
"""
```

## Practice Files

| File | Pattern | Description |
|------|---------|-------------|
| `practice_01_hub_spoke_coordinator.py` | Hub-and-Spoke | Basic coordinator with specialized agents |
| `practice_02_dynamic_selection.py` | Dynamic Selection | Coordinator chooses agents based on task |
| `practice_03_scope_partitioning.py` | Scope Partitioning | Divide work into non-overlapping scopes |
| `practice_04_iterative_refinement.py` | Iterative Refinement | Check and improve results |
| `practice_05_context_passing.py` | Explicit Context | Pass complete context to subagents |
| `practice_06_full_orchestrator.py` | All patterns | Complete multi-agent system |

## Common Failure Pattern

**Narrow Decomposition**: If output misses categories, the coordinator's task decomposition was too narrow. Adding agents doesn't help if they receive the same narrow assignment.

## Key Principles

1. **All communication through coordinator** - Subagents never talk directly
2. **Dynamic selection** - Use only needed agents, not all always
3. **Clear scope boundaries** - No overlap between agents
4. **Iterate for quality** - Check results and refine
5. **Explicit context** - Pass everything to subagents, don't assume

## Running the Examples

```bash
cd multi_agent_orchestration
pip install anthropic python-dotenv
python practice_01_hub_spoke_coordinator.py
```

## Anti-Patterns to Avoid

- ❌ Subagents sharing memory or history
- ❌ Narrow task decomposition
- ❌ Assuming agents know context
- ❌ Agents talking to each other directly
- ❌ One-shot generation without quality checks