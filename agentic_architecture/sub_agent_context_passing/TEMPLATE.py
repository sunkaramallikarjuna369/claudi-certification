"""
================================================================================
SUBAGENT CONTEXT PASSING - TEMPLATE
================================================================================

Your starting point for building multi-agent systems with proper context passing.
================================================================================
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


# ================================================================================
# STEP 1: Define your tools (including Agent tool for spawning!)
# ================================================================================

tools = [
    {
        "name": "Agent",
        "description": "Spawn a subagent to perform a specific task",
        "input_schema": {
            "type": "object",
            "properties": {
                "description": {
                    "type": "string",
                    "description": "What this subagent should do"
                },
                "agent_name": {
                    "type": "string",
                    "description": "Name identifier for the subagent"
                },
                "system_prompt": {
                    "type": "string",
                    "description": "Instructions for the subagent"
                }
            },
            "required": ["description", "agent_name", "system_prompt"]
        }
    },
    {
        "name": "search",
        "description": "Search for information",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query"
                }
            },
            "required": ["query"]
        }
    }
]


# ================================================================================
# STEP 2: Define your subagent types
# ================================================================================

SUBAGENT_DEFINITIONS = {
    "researcher": {
        "description": "Research agent - finds and summarizes information",
        "system_prompt": """You are a research agent. Your job is to find information.

RULES:
1. Always cite your sources with [Source: name]
2. Include confidence levels: high/medium/low
3. Return findings in structured format with metadata
4. If you can't find info, say so clearly

OUTPUT FORMAT:
{
    "content": "your findings",
    "source": "where you found it",
    "confidence": "high/medium/low"
}""",
        "tools": ["search"]
    },
    "writer": {
        "description": "Writer agent - synthesizes information into text",
        "system_prompt": """You are a writing agent. Your job is to create clear, well-structured output.

RULES:
1. Always cite sources using [Source: name] format
2. Maintain factual accuracy
3. Structure with headers and bullet points
4. Flag any uncertain information
""",
        "tools": []
    },
    "analyst": {
        "description": "Analysis agent - performs calculations and analysis",
        "system_prompt": """You are an analysis agent. Your job is to analyze data and provide insights.

RULES:
1. Show your work/calculations
2. Include confidence levels
3. Note any assumptions
4. Flag outliers or anomalies
""",
        "tools": ["calculate"]
    }
}


# ================================================================================
# STEP 3: Context passing functions
# ================================================================================

def create_subagent_message(
    agent_type: str,
    task: str,
    context: dict = None,
    metadata: dict = None
) -> list:
    """
    Create a properly formatted message for a subagent.

    Args:
        agent_type: Type of subagent (from SUBAGENT_DEFINITIONS)
        task: What the subagent should do
        context: Background information the subagent needs
        metadata: Structured metadata for attribution

    Returns:
        List of message dicts ready for API call
    """
    agent_def = SUBAGENT_DEFINITIONS.get(agent_type, {})

    # Build the context section
    context_section = ""
    if context:
        context_section = "\n\nBACKGROUND CONTEXT:\n"
        for key, value in context.items():
            context_section += f"- {key}: {value}\n"

    # Build metadata section
    metadata_section = ""
    if metadata:
        metadata_section = "\n\nMETADATA (for attribution):\n"
        for key, value in metadata.items():
            metadata_section += f"- {key}: {value}\n"

    content = f"""You are a {agent_def.get('description', 'general agent')}.

TASK:{task}
{context_section}
{metadata_section}

Remember to include proper citations and metadata in your response."""

    return [{"role": "user", "content": content}]


def execute_tool(name: str, tool_input: dict) -> str:
    """Execute a tool."""
    if name == "Agent":
        return f"Spawned subagent: {tool_input.get('agent_name')}"
    elif name == "search":
        return f"Search results for '{tool_input.get('query')}': [mock results]"
    return f"Unknown tool: {name}"


# ================================================================================
# STEP 4: Coordinator pattern
# ================================================================================

def run_coordinator(user_task: str) -> str:
    """
    Example coordinator that uses proper context passing.

    This demonstrates the CORRECT pattern for multi-agent systems:
    1. Analyze task
    2. Spawn subagents with EXPLICIT context
    3. Collect results
    4. Synthesize and respond
    """
    print("\n" + "=" * 60)
    print("COORDINATOR EXECUTION")
    print("=" * 60)

    print(f"\nUser task: {user_task}")
    print("\nStep 1: Analyzing task...")

    # Example: Task requires research and synthesis
    requires_research = True
    requires_synthesis = True

    # Step 2: Create context (all info subagents need)
    user_context = {
        "original_question": user_task,
        "user_preferences": "Detailed answers with citations",
        "format": "Structured report"
    }

    # Step 3: Spawn research subagent WITH EXPLICIT CONTEXT
    if requires_research:
        print("Step 2: Spawning research subagent...")

        research_messages = create_subagent_message(
            agent_type="researcher",
            task="Research AI trends in 2024",
            context=user_context,
            metadata={
                "coordinator": "main-coordinator",
                "session_id": "example-123"
            }
        )

        print(f"   Context passed to researcher: {len(str(user_context))} chars")

    # Step 4: Spawn synthesis subagent WITH SUBAGENT OUTPUTS
    if requires_synthesis:
        print("Step 3: Spawning synthesis subagent...")

        # IMPORTANT: Pass researcher's output to synthesizer!
        synthesis_context = {
            **user_context,
            "research_findings": "[Would be actual findings from researcher]"
        }

        synthesis_messages = create_subagent_message(
            agent_type="writer",
            task="Write a report based on the research findings",
            context=synthesis_context,
            metadata={
                "source_agent": "researcher",
                "coordinator": "main-coordinator"
            }
        )

        print(f"   Context passed to writer: {len(str(synthesis_context))} chars")

    # Step 5: Coordinate response
    print("Step 4: Coordinating final response...")

    return """
    Multi-agent coordination complete!

    Key patterns demonstrated:
    1. Explicit context passing to each subagent
    2. Structured metadata for attribution
    3. Subagent outputs passed to downstream agents
    """


def run_parallel_subagents(tasks: list) -> list:
    """
    Example of spawning independent tasks in parallel.

    Use this when tasks are INDEPENDENT and can run simultaneously.
    """
    print("\n" + "=" * 60)
    print("PARALLEL SUBAGENT SPAWNING")
    print("=" * 60)

    results = []

    # Spawn ALL at once (parallel!)
    for i, task in enumerate(tasks, 1):
        print(f"\nSpawning subagent {i}/{len(tasks)}: {task[:30]}...")
        # In real implementation, these would all run simultaneously
        results.append({"task": task, "status": "completed"})

    print(f"\nAll {len(tasks)} tasks spawned in parallel!")
    print("Total time: max(individual_times) vs sum(individual_times)")

    return results


# ================================================================================
# MAIN
# ================================================================================

if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    print("\n" + "=" * 70)
    print("SUBAGENT CONTEXT PASSING - TEMPLATE")
    print("=" * 70)
    print("""
This template provides a starting point for multi-agent systems with proper context passing.

Key components:
1. Agent tool definition (REQUIRED for spawning subagents)
2. Subagent definitions with their system prompts
3. Context passing functions with metadata support
4. Coordinator pattern examples
5. Parallel spawning for independent tasks

Copy this template and customize for your use case!
""")

    # Demo: Coordinator
    print("\n" + "-" * 60)
    print("DEMO: Coordinator Pattern")
    print("-" * 60)

    result = run_coordinator("Research AI trends and write a report")
    print(result)

    # Demo: Parallel spawning
    print("\n" + "-" * 60)
    print("DEMO: Parallel Spawning")
    print("-" * 60)

    tasks = [
        "Research competitor A",
        "Research competitor B",
        "Research market size"
    ]
    results = run_parallel_subagents(tasks)
    print(f"Results: {results}")

    print("""
================================================================================
WHAT JUST HAPPENED?
================================================================================

    1. We saw the complete template structure:
       - Tools including "Agent" for spawning
       - Subagent definitions with system prompts
       - Context passing with metadata
       - Coordinator pattern
       - Parallel spawning

    2. We demonstrated proper context passing:
       - Every subagent gets explicit context
       - Metadata enables attribution
       - Outputs flow between agents

    3. We demonstrated parallel spawning:
       - Independent tasks run simultaneously
       - Much more efficient than sequential

    COPY THIS TEMPLATE and customize for your multi-agent system!

    Key reminders:
    - MUST include "Agent" tool for spawning subagents
    - ALWAYS pass explicit context to subagents
    - ALWAYS include metadata for attribution
    - Use parallel spawning for independent tasks
================================================================================
""")
    print("\n" + "=" * 70)
    print("TEMPLATE COMPLETE!")
    print("=" * 70)
