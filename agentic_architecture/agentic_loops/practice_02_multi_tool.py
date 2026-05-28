"""
+===========================================================================+
|                                                                           |
|  PRACTICE 2: MULTI-TOOL AGENTIC LOOP                                    |
|                                                                           |
|  Giving your AI agent MULTIPLE superpowers at once!                     |
|                                                                           |
|  This practice shows how Claude can use MULTIPLE tools in a SINGLE       |
|  response - more efficient than calling tools one-by-one.               |
|                                                                           |
|  + REAL-TIME SCENARIOS + MISTAKES DEVELOPERS MAKE + INTERVIEW Q&A      |
|                                                                           |
+===========================================================================+

INTERVIEW PREP: "How does Claude use multiple tools simultaneously?"
This question tests your understanding of parallel tool execution.
In production, this is CATASTROPHIC if mishandled.

REAL-TIME SCENARIO: User asks "Weather in Tokyo AND stock price of Apple."
If your code can't handle multiple tools, one fails silently!

===========================================================================
MULTI-TOOL CONCEPT: Parallel vs Sequential Execution
===========================================================================

    +-----------------------------------------------------------------------+
    | VISUAL: Single Tool vs Multi-Tool Response                          |
    +-----------------------------------------------------------------------+

    SINGLE TOOL:
    +-------------------+          +-------------------+
    | User asks ONE     | --------> | Claude calls ONE  |
    | question          |          | tool              |
    +-------------------+          +-------------------+
                                           |
                                           v
                                  +-------------------+
                                  | One result        |
                                  +-------------------+

    MULTI-TOOL:
    +-------------------+          +-------------------+
    | User asks about   | --------> | Claude calls ALL |
    | weather AND stock |          | 3 tools at once! |
    +-------------------+          +-------------------+
                                           |
                           +---------------+---------------+
                           |               |               |
                           v               v               v
                   +------------+  +------------+  +------------+
                   | get_weather|  | get_stock  |  | calculate  |
                   +------------+  +------------+  +------------+
                           |               |               |
                           v               v               v
                   +------------+  +------------+  +------------+
                   | 22C, Tokyo |  | AAPL: 180 |  | profit: 3k |
                   +------------+  +------------+  +------------+
                           |               |               |
                           +---------------+---------------+
                                           |
                                           v
                                  +-------------------+
                                  | Claude combines   |
                                  | all results into  |
                                  | complete answer  |
                                  +-------------------+

    +-----------------------------------------------------------------------+
    | KEY INSIGHT: All tools execute in parallel, then ALL results         |
    | are sent back together in next user message block                    |
    +-----------------------------------------------------------------------+

===========================================================================
KEY CONCEPTS YOU'LL LEARN
===========================================================================

    1. MULTI-TOOL PARALLELISM: Claude can call multiple tools at once
    2. LOOPING THROUGH BLOCKS: Handle text + tool_use + tool_result
    3. BATCH RESULT RETURN: All results sent back in one message
    4. TOOL SELECTION INTELLIGENCE: Claude chooses right tools per question

"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API credentials from environment
API_KEY = os.getenv("ANTHROPIC_API_KEY")
API_BASE = os.getenv("ANTHROPIC_API_BASE", "")

if not API_KEY:
    raise ValueError("ANTHROPIC_API_KEY not found in .env file")


from anthropic import Anthropic

# Create client with proper configuration
client_kwargs = {"api_key": API_KEY} if API_KEY else {}
if API_BASE:
    client_kwargs["base_url"] = API_BASE

client = Anthropic(**client_kwargs)


# ============================================================================
# MULTI-TOOL DEFINITION: Three tools for a trip planning assistant
# ============================================================================

tools = [
    {
        "name": "get_weather",
        "description": "Get the current weather for a city.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The name of the city to get weather for (e.g., 'Tokyo', 'Paris', 'New York')"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "Temperature unit - 'celsius' or 'fahrenheit'. Defaults to celsius if not specified."
                }
            },
            "required": ["city"]
        }
    },
    {
        "name": "search_wiki",
        "description": "Search Wikipedia for information about a topic.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query (e.g., 'Tokyo', 'Artificial Intelligence', 'Paris Eiffel Tower')"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "calculator",
        "description": "Perform basic arithmetic calculations.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The mathematical expression (e.g., '2 + 2', '100 * 24', '24 * 3')"
                }
            },
            "required": ["expression"]
        }
    }
]


def execute_tool(name: str, tool_input: dict) -> str:
    """
    Execute the appropriate tool based on its name.
    """
    if name == "get_weather":
        city = tool_input.get("city", "Unknown")
        unit = tool_input.get("unit", "celsius")
        return f"Weather in {city}: 22C, partly cloudy, humidity 65%"

    elif name == "search_wiki":
        query = tool_input.get("query", "")
        return f"Wikipedia summary for '{query}': Artificial Intelligence is the simulation of human intelligence by machines."

    elif name == "calculator":
        expression = tool_input.get("expression", "")
        try:
            result = eval(expression)
            return str(result)
        except Exception as e:
            return f"Error: {e}"

    return f"Unknown tool: {name}"


def run_agentic_loop(user_message: str, max_iterations: int = 10):
    """
    Run the agentic loop with multiple tools.

    The multi-tool pattern:
    1. Claude can return MULTIPLE tool_use blocks in ONE response
    2. Loop through ALL blocks, not just the first one
    3. Execute ALL tools, collect ALL results
    4. Add ALL tool results back to conversation
    """
    messages = [{"role": "user", "content": user_message}]

    for iteration in range(1, max_iterations + 1):
        print(f"\n{'='*50}")
        print(f"ITERATION {iteration}")
        print('='*50)

        print("Sending request to Claude with tools:")
        for tool in tools:
            print(f"   - {tool['name']}")

        response = client.messages.create(
            model="claude-haiku-4-5-20250601",
            max_tokens=4096,
            messages=messages,
            tools=tools,
        )

        print(f"\nStop reason: {response.stop_reason}")

        if response.stop_reason == "tool_use":
            print("\nClaude wants to use tool(s)!")

            assistant_message = {"role": "assistant", "content": []}
            tool_results = []

            # IMPORTANT: Loop through ALL content blocks!
            # Claude can return multiple tool_use blocks at once
            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input

                    print(f"\n   Tool called: {tool_name}")
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

            messages.append(assistant_message)

            # IMPORTANT: Add ALL tool results in order
            for tr in tool_results:
                messages.append({
                    "role": "user",
                    "content": [{"type": "tool_result", "tool_use_id": tr["tool_use_id"], "content": tr["content"]}]
                })

            print(f"\n   Executed {len(tool_results)} tool call(s)")
            continue

        elif response.stop_reason == "end_turn":
            print(f"\nDONE! Claude has the final answer:")
            print(f"\n{'-'*50}")
            final_text = ""
            for block in response.content:
                if block.type == "text" and block.text:
                    final_text = block.text
                    break
            print(final_text)
            print(f"{'-'*50}")
            return final_text

    return "Max iterations reached"


# ============================================================================
# REAL-TIME SCENARIOS: When multi-tool loops break in production
# ============================================================================

def show_real_time_scenarios():
    """
    Production scenarios where multi-tool execution breaks.
    """

    print("\n" + "=" * 70)
    print("REAL-TIME SCENARIOS: When Multi-Tool Execution Breaks")
    print("=" * 70)

    print("""
    +======================================================================+
    ||                                                                      ||
    ||  SCENARIO #1: The Silently Dropped Tool Call                        ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  PROBLEM:                                                            ||
    ||  - Claude returns 3 tool_use blocks                                  ||
    ||  - Your code only processes block[0], ignores [1] and [2]           ||
    ||  - Two tools never execute, user gets incomplete answer             ||
    ||                                                                      ||
    ||  CAUSE:                                                              ||
    ||  - Using block = response.content[0] instead of LOOP              ||
    ||  - Assuming only one tool call per response                          ||
    ||                                                                      ||
    ||  PRODUCTION IMPACT:                                                  ||
    ||  - User asks "Weather in Tokyo AND stock price AND my profit"      ||
    ||  - Only weather executes                                             ||
    ||  - User says "It didn't answer about my stocks!"                   ||
    ||  - Lost trust in the system                                          ||
    ||                                                                      ||
    ||  FIX: ALWAYS loop through response.content, not index [0]           ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  SCENARIO #2: The Request-Response Mismatch                        ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  PROBLEM:                                                            ||
    ||  - Claude calls get_weather and search_wiki                          ||
    ||  - Your execute_tool returns weather for search_wiki call           ||
    ||  - Results get attached to wrong tool calls!                        ||
    ||                                                                      ||
    ||  CAUSE:                                                              ||
    ||  - Adding tool results in wrong order to messages                   ||
    ||  - Not matching tool_use_id correctly                               ||
    ||                                                                      ||
    ||  PRODUCTION IMPACT:                                                  ||
    ||  - User sees "Weather in Tokyo: AAPL@180"                          ||
    ||  - Confused response, user errors                                   ||
    ||                                                                      ||
    ||  FIX: Always use block.id as tool_use_id, match exactly!            ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  SCENARIO #3: The Text Block Gotcha                                 ||
    │  ================================================================   ||
    ||                                                                      ||
    ||  PROBLEM:                                                            ||
    ||  - Claude returns text + multiple tool_use blocks                   ||
    ||  - Your code checks block.type but misses text block                ||
    ||  - Thinking text means "done" when more tools coming                ||
    ||                                                                      ||
    ||  CAUSE:                                                              ||
    ||  - Only checking for block.type == "tool_use"                       ||
    ||  - Not handling text blocks alongside tool_use blocks               ||
    ||                                                                      ||
    ||  PRODUCTION IMPACT:                                                  ||
    ||  - Claude says "Let me check all three..." AND calls 3 tools        ||
    ||  - Your code sees text, assumes final answer                        ||
    ||  - Tools never execute, wrong response                              ||
    ||                                                                      ||
    ||  FIX: Check stop_reason, not content, to decide flow!                ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  SCENARIO #4: The Parallel Execution Timeout                       ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  PROBLEM:                                                            ||
    ||  - Claude calls 10 tools, 2 are slow external API calls             ||
    ||  - User sees timeout after 30 seconds                                ||
    ||  - Partial results returned, confusing for user                     ||
    ||                                                                      ||
    ||  CAUSE:                                                              ||
    ||  - No timeout handling for individual tools                         ||
    ||  - Assuming all tool executions are fast                            ||
    ||                                                                      ||
    ||  PRODUCTION IMPACT:                                                  ||
    ||  - User gets partial answer, no indication of failure               ||
    ||  - "Where are my other results?"                                    ||
    ||                                                                      ||
    ||  FIX: Implement timeouts per tool, graceful degradation             ||
    ||                                                                      ||
    +======================================================================+
    """)


# ============================================================================
# MISTAKES DEVELOPERS MAKE: Expert warnings
# ============================================================================

def show_mistakes():
    """
    Common errors developers make with multi-tool execution.
    """

    print("\n" + "=" * 70)
    print("MISTAKES DEVELOPERS MAKE - EXPERT WARNINGS")
    print("=" * 70)

    print("""
    +======================================================================+
    ||                                                                      ||
    ||  MISTAKE #1: Only handling first content block                      ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WRONG CODE:                                                         ||
    ||  block = response.content[0]  # Only first block!                   ||
    ||  if block.type == "tool_use":                                        ||
    ||      execute_tool(block.name, block.input)                           ||
    ||                                                                      ||
    ||  WHAT HAPPENS:                                                       ||
    ||  - If Claude calls 3 tools, only first executes!                    ||
    ||  - Two tool calls silently drop                                       ||
    ||                                                                      ||
    ||  CORRECT CODE:                                                       ||
    ||  for block in response.content:  # Loop through ALL blocks!        ||
    ||      if block.type == "tool_use":                                    ||
    ||          execute_tool(block.name, block.input)                       ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  MISTAKE #2: Assuming tool calls are synchronous/ordered            ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WRONG CODE:                                                         ||
    ||  tool1_result = execute_tool("tool1", input1)                        ||
    ||  tool2_result = execute_tool("tool2", input2)                        ||
    ||  # Assuming tool1 always executes first                             ||
    ||                                                                      ||
    ||  WHAT HAPPENS:                                                       ||
    ||  - In multi-tool, order isn't guaranteed by dependencies             ||
    ||  - Could get mismatched results in conversation                     ||
    ||                                                                      ||
    ||  CORRECT CODE:                                                       ||
    ||  # Use block.id to match results, not execution order               ||
    ||  for block in response.content:                                       ||
    ||      if block.type == "tool_use":                                    ||
    ||          tool_results.append({                                       ||
    ||              "tool_use_id": block.id,  # Match by ID!              ||
    ||              "content": execute_tool(block.name, block.input)       ||
    ||          })                                                          ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  MISTAKE #3: Adding tool results to messages out of order           ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WRONG CODE:                                                         ||
    ||  messages.append({"role": "user", "content": [{                     ||
    ||      "type": "tool_example_result",                                 ||
    ||      "content": tool1_result                                        ||
    ||  }]})                                                                ||
    ||  messages.append({"role": "user", "content": [{                     ||
    ||      "type": "tool_example_result",                                 ||
    ||      "content": tool2_result                                        ||
    ||  }]})                                                                ||
    ||  # No tool_use_id! Claude can't match to correct tool               ||
    ||                                                                      ||
    ||  CORRECT CODE:                                                       ||
    ||  for tr in tool_results:  # In order of execution                   ||
    ||      messages.append({"role": "user", "content": [{                ||
    ||          "type": "tool_example_result",                             ||
    ||          "tool_use_id": tr["tool_use_id"],  # Required!            ||
    ||          "content": tr["content"]                                   ||
    ||      }]})                                                            ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  MISTAKE #4: Ignoring text blocks during tool execution             ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WRONG CODE:                                                         ||
    ||  for block in response.content:                                       ||
    ||      if block.type == "tool_use":                                    ||
    ||          # Only handling tool_use, ignoring text!                    ||
    ||                                                                      ||
    ||  WHAT HAPPENS:                                                       ||
    ||  - Claude's thinking text gets lost                                  ||
    ||  - Missing context for the tool calls                               ||
    ||                                                                      ||
    ||  CORRECT CODE:                                                       ||
    ||  assistant_message = {"role": "assistant", "content": []}           ||
    ||  for block in response.content:                                      ||
    ||      if block.type == "text":                                        ||
    ||          assistant_message["content"].append({                     ||
    ||              "type": "text",                                        ||
    ||              "text": block.text                                     ||
    ||          })                                                          ||
    ||      elif block.type == "tool_use":                                  ||
    ||          # Handle tool_use                                           ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  MISTAKE #5: Not handling unknown tools gracefully                   ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WRONG CODE:                                                         ||
    ||  def execute_tool(name, tool_input):                                 ||
    ||      if name == "calculator":                                        ||
    ||          return calc(tool_input)                                    ||
    ||      # No else/return for unknown tools!                            ||
    ||      # Returns None, breaks Claude's response                        ||
    ||                                                                      ||
    ||  CORRECT CODE:                                                       ||
    ||  def execute_tool(name, tool_input):                                ||
    ||      if name == "calculator":                                        ||
    ||          return calc(tool_input)                                    ||
    ||      elif name == "get_weather":                                     ||
    ||          return get_weather(tool_input)                             ||
    ||      else:                                                           ||
    ||          return f"Error: Unknown tool '{name}'"                      ||
    ||                                                                      ||
    +======================================================================+
    """)


# ============================================================================
# INTERVIEW Q&A: Expert answer frameworks
# ============================================================================

def show_interview_qa():
    """
    Common interview questions and expert answer frameworks.
    """

    print("\n" + "=" * 70)
    print("INTERVIEW QUESTIONS - EXPERT ANSWER FRAMEWORKS")
    print("=" * 70)

    print("""
    ======================================================================
    INTERVIEW Q1: "Can Claude call multiple tools in one response?"
    ======================================================================

    EXPECTED ANSWER:
    YES! Claude can call multiple tools simultaneously in a single response.
    Each tool call appears as a separate tool_use block in response.content.
    Your code must loop through ALL blocks, not just the first one. All
    results are then sent back to Claude in the next user message.

    EXAMPLE ANSWER:
    "Yes, Claude can call multiple tools at once. This is called parallel
    tool execution. Each tool appears as a separate block in response.content.
    Your code needs to loop through all blocks and collect all results before
    sending them back."

    RED FLAGS IN ANSWERS:
    - "No, it only calls one tool at a time" -> Outdated knowledge
    - "It depends on the model" -> Not understanding the API

    +-----------------------------------------------------------------------+
    | EXPERT TIP: Always mention "loop through all blocks" - that's the      |
    | key implementation detail interviewers look for.                      |
    +-----------------------------------------------------------------------+


    ======================================================================
    INTERVIEW Q2: "How do you handle multiple tool results?"
    ======================================================================

    EXPECTED ANSWER STRUCTURE:
    1. Loop through response.content - don't index [0]
    2. Execute each tool, collect results with tool_use_id
    3. Add assistant message with all tool_use blocks
    4. Add user message with ALL tool_result blocks (in matching order)

    EXAMPLE ANSWER:
    "I loop through response.content, execute each tool, and collect
    results in a list with their tool_use_id. Then I add one assistant
    message with all tool_use blocks, followed by user messages with
    tool_result blocks for each result."

    +-----------------------------------------------------------------------+
    | EXPERT TIP: Emphasize the tool_use_id matching - that's critical      |
    | for correct result attribution in multi-tool calls.                   |
    +-----------------------------------------------------------------------+


    ======================================================================
    INTERVIEW Q3: "What's the difference between parallel and sequential
                  tool calling?"
    ======================================================================

    EXPECTED ANSWER:
    "Parallel: Claude calls multiple tools at once in one response. All execute,
    results return together. Sequential: One tool's output becomes another's
    input in next iteration. For example, get_stock_price first, then
    calculate_profit with that result."

    USE CASES:
    - Parallel: Independent queries (weather AND stocks)
    - Sequential: Dependent queries (get price, then calculate profit)

    +-----------------------------------------------------------------------+
    | EXPERT TIP: Give concrete examples for each type.                      |
    +-----------------------------------------------------------------------+


    ======================================================================
    INTERVIEW Q4: "What happens if a tool fails in multi-tool execution?"
    ======================================================================

    EXPECTED ANSWER:
    "If one tool fails, I should:
    1. Catch the exception in execute_tool()
    2. Return an error string result (not crash)
    3. Include error in tool_result content
    4. Let Claude decide how to handle partial results
    5. Log which tool failed for debugging"

    CORRECT ERROR HANDLING:
    - Return: "Error: Database connection failed"
    - NOT: raise exception (crashes the loop)

    RED FLAGS IN ANSWERS:
    - "I crash the entire loop" -> Wrong approach
    - "I skip failed tools silently" -> Leads to confusion

    +-----------------------------------------------------------------------+
    | EXPERT TIP: Emphasize graceful degradation - let Claude handle errors.|
    +-----------------------------------------------------------------------+
    """)


# ============================================================================
# VISUAL REPRESENTATIONS: ASCII diagrams
# ============================================================================

def show_visual_representations():
    """
    ASCII diagrams showing multi-tool execution.
    """

    print("\n" + "=" * 70)
    print("VISUAL REPRESENTATIONS: Multi-Tool Execution Flow")
    print("=" * 70)

    print("""
    +======================================================================+
    ||  DIAGRAM 1: Multi-Tool Response Structure                           ||
    +======================================================================+

    USER MESSAGE: "What's weather in Tokyo AND stock price of AAPL?"

    RESPONSE (Claude returns multiple blocks):
    +---------------------------------------------------------------+
    | response.content = [                                           |
    |     {                                                         |
    |         "type": "text",                                        |
    |         "text": "Let me check both for you."                   |
    |     },                                                         |
    |     {                                                         | <- Block 0: Text
    |         "type": "tool_use",                                   |
    |         "id": "toolu_001",                                    |
    |         "name": "get_weather",                                | <- Block 1: Tool 1
    |         "input": {"city": "Tokyo"}                            |
    |     },                                                         |
    |     {                                                         | <- Block 2: Tool 2
    |         "type": "tool_use",                                   |
    |         "id": "toolu_002",                                    |
    |         "name": "get_stock_price",                            |
    |         "input": {"symbol": "AAPL"}                           |
    |     }                                                         |
    | ]                                                             |
    +---------------------------------------------------------------+

    WRONG: response.content[0] -> only gets text block!
    CORRECT: for block in response.content: -> gets ALL blocks!


    +======================================================================+
    ||  DIAGRAM 2: Multi-Tool Result Collection                            ||
    +======================================================================+

    +------------------+      +------------------+      +------------------+
    | Block 1:         |      | Block 2:         |      | Block 3:         |
    | get_weather      |      | get_stock_price |      | calculator       |
    | id: toolu_001   |      | id: toolu_002   |      | id: toolu_003   |
    +------------------+      +------------------+      +------------------+
           |                         |                         |
           v                         v                         v
    +------------------+      +------------------+      +------------------+
    | Result 1:        |      | Result 2:        |      | Result 3:        |
    | "22C, Tokyo"    |      | "AAPL: $180.50" |      | "profit: 2850"  |
    +------------------+      +------------------+      +------------------+
           |                         |                         |
           +-------------------------+-------------------------+
                                   |
                                   v
                    +------------------------------------------+
                    |  tool_results = [                        |
                    |      {"tool_use_id": "toolu_001",        |
                    |       "content": "22C, Tokyo"},        |
                    |      {"tool_use_id": "toolu_002",      |
                    |       "content": "AAPL: $180.50"},     |
                    |      {"tool_use_id": "toolu_003",     |
                    |       "content": "profit: 2850"}       |
                    |  ]                                      |
                    +------------------------------------------+


    +======================================================================+
    ||  DIAGRAM 3: Messages After Multi-Tool Execution                     ||
    +======================================================================+

    messages = [
        {
            "role": "user",
            "content": "What's weather in Tokyo AND stock price of AAPL?"
        },
        {
            "role": "assistant",
            "content": [
                {"type": "text", "text": "Let me check both..."},
                {"type": "tool_use", "id": "toolu_001", "name": "get_weather", ...},
                {"type": "tool_use", "id": "toolu_002", "name": "get_stock_price", ...}
                                             ^-- Multiple blocks in ONE message!
            ]
        },
        {
            "role": "user",                              ^-- Result for toolu_001
            "content": [{"type": "tool_example_result", "tool_use_id": "toolu_001", "content": "22C"}]
        },
        {
            "role": "user",                              ^-- Result for toolu_002
            "content": [{"type": "tool_example_result", "tool_use_id": "toolu_002", "content": "AAPL: $180"}]
        }
                                    ^-- Multiple separate messages!
    ]


    +======================================================================+
    ||  DIAGRAM 4: Common Mistake - Only First Block                      ||
    +======================================================================+

    WRONG CODE:
    block = response.content[0]  # Gets FIRST block only!
    if block.type == "tool_use":
        result = execute_tool(block.name, block.input)

    FLOW WHEN Claude returns [text, tool_use, tool_use]:
    +-------------------------+
    | response.content[0]     |  -> Returns TEXT block!
    | type: "text"            |  -> Your code thinks no tool was called
    +-------------------------+     because text != tool_use!

    FIX: ALWAYS loop through content:
    for block in response.content:
        if block.type == "tool_use":
            execute_tool(block.name, block.input)
    """)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    import sys

    # Fix stdout encoding for Windows
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("\n" + "=" * 70)
    print("PRACTICE 2: MULTI-TOOL AGENTIC LOOP")
    print("=" * 70)
    print("""
    This program shows how an AI can use MULTIPLE tools to answer a question.
    Watch as Claude calls 3 tools simultaneously in one response!

    Follow along as we:
    1. Run multi-tool agentic loop
    2. Show real-time scenarios where multi-tool breaks
    3. Highlight common mistakes developers make
    4. Provide interview Q&A with expert answers
    5. Show visual representations of the concepts
    """)

    print("\n" + "-" * 70)
    print("PART 1: Running the Multi-Tool Agentic Loop")
    print("-" * 70)

    user_input = """
    I'm planning a trip to Tokyo. Can you:
    1. Look up the weather there
    2. Calculate how many hours are in 3 days
    3. Search Wikipedia for information about Tokyo
    """

    print(f"USER REQUEST:\n{user_input}")
    print("\n" + "-" * 70 + "\n")

    result = run_agentic_loop(user_input)

    print("\n" + "-" * 70)
    print("PART 2: Real-Time Scenarios")
    print("-" * 70)
    show_real_time_scenarios()

    print("\n" + "-" * 70)
    print("PART 3: Common Mistakes")
    print("-" * 70)
    show_mistakes()

    print("\n" + "-" * 70)
    print("PART 4: Interview Q&A")
    print("-" * 70)
    show_interview_qa()

    print("\n" + "-" * 70)
    print("PART 5: Visual Representations")
    print("-" * 70)
    show_visual_representations()

    print("""
================================================================================
WHAT WE HAVE LEARNT
================================================================================

+======================================================================+
||  1. MULTI-TOOL PARALLEL EXECUTION:                                    ||
||                                                                      ||
||  - Claude can call MULTIPLE tools in a SINGLE response              ||
||  - Each tool appears as a separate block in response.content        ||
||  - Must loop through ALL blocks, not just block[0]                  ||
||  - ALL results sent back together in next iteration                 ||
||                                                                      ||
||  TOOLS execute in parallel, results return together                 ||
||                                                                      ||
+======================================================================+

+======================================================================+
||  2. REAL-TIME SCENARIOS (Multi-Tool Breakage):                       ||
||                                                                      ||
||  SCENARIO #1: Silently Dropped Tool Call                            ||
||  - Using block[0] instead of loop drops 2 of 3 tools               ||
||  - Fix: for block in response.content:                              ||
||                                                                      ||
||  SCENARIO #2: Request-Response Mismatch                             ||
||  - Results misattached due to wrong tool_use_id                    ||
||  - Fix: Always use block.id as tool_use_id                          ||
||                                                                      ||
||  SCENARIO #3: Text Block Gotcha                                      ||
||  - Seeing text block means final answer, but MORE tools coming!     ||
||  - Fix: Check stop_reason, not content type                         ||
||                                                                      ||
||  SCENARIO #4: Parallel Execution Timeout                            ||
||  - Slow tools cause timeout before all complete                     ||
||  - Fix: Implement timeouts per tool, graceful degradation          ||
||                                                                      ||
+======================================================================+

+======================================================================+
||  3. MISTAKES DEVELOPERS MAKE:                                        ||
||                                                                      ||
||  APRIORI #1: Only handling first content block                       ||
||  - Use for block in response.content: not block[0]                  ||
||                                                                      ||
||  MISTAKE #2: Assuming tool calls are ordered                        ||
||  - Use block.id to match results, not execution order                ||
||                                                                      ||
||  MISTAKE #3: Adding results out of order                            ||
||  - Always include tool_use_id in each tool_result                   ||
||                                                                      ||
||  MISTAKE #4: Ignoring text blocks                                   ||
||  - Must handle text blocks alongside tool_use blocks                ||
||                                                                      ||
||  MISTAKE #5: Not handling unknown tools gracefully                  ||
||  - Return error string, don't raise exception                       ||
||                                                                      ||
+======================================================================+

+======================================================================+
||  4. INTERVIEW Q&A FRAMEWORKS:                                        ||
||                                                                      ||
||  Q: "Can Claude call multiple tools in one response?"               ||
||  A: YES - loop through ALL blocks, collect ALL results              ||
||                                                                      ||
||  Q: "How do you handle multiple tool results?"                       ||
||  A: Loop through content, use block.id for matching                 ||
||                                                                      ||
||  Q: "What's parallel vs sequential tool calling?"                   ||
||  A: Parallel = independent (weather AND stocks)                      ||
||     Sequential = dependent (get price, then calculate)             ||
||                                                                      ||
||  Q: "What if a tool fails in multi-tool execution?"                ||
||  A: Return error string, let Claude handle gracefully               ||
||                                                                      ||
+======================================================================+

+======================================================================+
||  5. VISUAL REPRESENTATIONS (ASCII Diagrams):                         ||
||                                                                      ||
||  - Multi-tool response structure with multiple blocks              ||
||  - Result collection and tool_use_id matching                       ||
||  - Message structure after multi-tool execution                     ||
||  - Common mistake: Only first block handled                         ||
||                                                                      ||
+======================================================================+

+======================================================================+
||  6. KEY RULES TO MEMORIZE:                                           ||
||                                                                      ||
||  RULE #1: Loop through ALL response.content blocks                 ||
||  RULE #2: Use block.id as tool_use_id for matching                 ||
||  RULE #3: Handle text and tool_use blocks together                  ||
||  RULE #4: Return strings, not exceptions, for errors               ||
||  RULE #5: Don't index [0] to check for tool_use - use type check   ||
||  RULE #6: All tool results added as separate user messages         ||
||                                                                      |
+======================================================================+

Next: practice_03_sequential_tools.py shows how to handle
SEQUENTIAL tool execution where one tool's output becomes another's input!

================================================================================
""")


"""
+===========================================================================+
|                                                                           |
|  KEY CONCEPTS FROM THIS FILE:                                           |
|                                                                           |
|  MULTI-TOOL:                                                             |
|  - Claude can call multiple tools at once                                |
|  - Loop through ALL response.content blocks                             |
|  - Use block.id for result matching                                     |
|  - Handle text + tool_use blocks together                               |
|                                                                           |
|  REAL-TIME FIXES:                                                        |
|  - Always loop, never index [0]                                         |
|  - Include tool_use_id in every result                                  |
|  - Log which tools called/executed                                      |
|                                                                           |
|  INTERVIEW PREP:                                                        |
|  - "Can Claude call multiple tools at once?"                            |
|  - "How do you handle multiple results?"                                |
|  - "What's parallel vs sequential tool calling?"                        |
|                                                                           |
|  NEXT: practice_03_sequential_tools.py (sequential execution)         |
|                                                                           |
+===========================================================================+
"""
