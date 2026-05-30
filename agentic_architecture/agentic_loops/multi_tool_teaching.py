"""
+===========================================================================+
|                                                                           |
|  MULTI-TOOL AGENTIC LOOP: Complete Teaching Program                     |
|                                                                           |
|  Learn how Claude handles MULTIPLE tools in ONE response!               |
|                                                                           |
|  This program teaches:                                                  |
|  - Single-tool vs Multi-tool patterns                                    |
|  - Why you MUST loop through ALL content blocks                          |
|  - Common mistakes that break production systems                        |
|  - Visual diagrams for beginners to understand                          |
|                                                                           |
+===========================================================================
"""

import os
import sys
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("ANTHROPIC_API_KEY")
API_BASE = os.getenv("ANTHROPIC_API_BASE", "")

if not API_KEY:
    raise ValueError("""
+==========================================================================+
|                                                                          |
|  ERROR: ANTHROPIC_API_KEY not found!                                     |
|                                                                          |
|  Please create a .env file with your API key:                           |
|  1. Create a file named ".env" in the project root                      |
|  2. Add this line:                                                       |
|     ANTHROPIC_API_KEY=your-key-here                                     |
|                                                                          |
+==========================================================================+
    """)

from anthropic import Anthropic

client = Anthropic(api_key=API_KEY, base_url=API_BASE or None)


# ============================================================================
# CONFIGURATION
# ============================================================================

INTERACTIVE_MODE = True  # Set to False for auto-continue
AUTO_DELAY = 0.5

def wait_for_input(prompt: str = ""):
    """Wait for user to press ENTER."""
    if INTERACTIVE_MODE:
        input(f"\n>>> PRESS ENTER to continue {prompt}...")
    else:
        time.sleep(AUTO_DELAY)


def print_section(title: str):
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


# ============================================================================
# PART 1: The Problem - Why Multi-Tool Matters
# ============================================================================

def show_the_problem():
    """
    Show why single-tool is not enough.
    """

    print_section("PART 1: THE PROBLEM - Single Tool Isn't Enough")

    print("""
| Imagine you're building a TRIP PLANNING assistant!
|
| User asks: "What's the weather in Tokyo? And tell me about Japan."
|
| With a SINGLE tool, what happens?
| -----------------------------------
| Option A: Call weather tool -> Get weather -> DONE (no info about Japan)
| Option B: Call wiki tool -> Get info -> DONE (no weather)
| Option C: Call tool 1, wait, call tool 2, wait... SLOW!
|
| THE PROBLEM: User asked TWO things, but single-tool code can only do ONE!
|    """)

    wait_for_input("(Understanding the limitation)")

    print("""
| But Claude can call MULTIPLE tools at once!
|
| With MULTI-TOOL support:
| -------------------------
| User: "Weather in Tokyo AND tell me about Japan"
|        |
|        v
| Claude: Sees TWO needs -> Calls BOTH tools at once!
|        |
|        +---> get_weather(city="Tokyo")
|        |
|        +---> search_wiki(query="Japan")
|        |
|        v
| Results return together -> Claude combines into complete answer
|        |
|        v
| User gets BOTH answers at once! Fast and complete!
|    """)

    wait_for_input("(Seeing the solution)")


# ============================================================================
# PART 2: Visual Comparison - Single vs Multi Tool
# ============================================================================

def show_visual_comparison():
    """
    Show visual diagrams comparing single vs multi-tool.
    """

    print_section("PART 2: VISUAL COMPARISON - Single vs Multi Tool")

    print("""
+==========================================================================+
|                                                                          |
|  SINGLE TOOL FLOW: One at a time                                         |
|                                                                          |
+==========================================================================+

    USER QUESTION
         |
         v
    +------------+
    |   Claude   |
    +------------+
         |
         | "Use ONE tool"
         v
    +-----------------------------+
    | Tool 1 (e.g., get_weather)  |
    +-----------------------------+
         |
         v
    +------------+
    |   Result   |
    +------------+
         |
         v
    USER WAITS... (if more tools needed, loop again!)

    TIME: Slow - N tools = N loops = N waits


+==========================================================================+
|                                                                          |
|  MULTI-TOOL FLOW: Everything at once!                                   |
|                                                                          |
+==========================================================================+

    USER QUESTION (with multiple needs)
         |
         v
    +------------+
    |   Claude   |
    +------------+
         |
         | "Use MULTIPLE tools"
         v
    +-----------+ +-----------+ +-----------+
    | Tool 1    | | Tool 2    | | Tool 3    |
    |weather    | | search    | |calculate  |
    +-----------+ +-----------+ +-----------+
         |            |            |
         v            v            v
    ALL AT ONCE (parallel execution)
         |
         v
    +------------+
    | ALL Results|
    +------------+
         |
         v
    USER GETS COMPLETE ANSWER (one loop!)

    TIME: Fast - Multiple tools in ONE loop!
    """)

    wait_for_input("(Visualizing the difference)")


# ============================================================================
# PART 3: The Critical Mistake - Only Handling First Block
# ============================================================================

def show_critical_mistake():
    """
    Show the #1 mistake developers make.
    """

    print_section("PART 3: THE CRITICAL MISTAKE")

    print("""
| =======================================================================
| WARNING: This mistake breaks production systems!
| =======================================================================
|
| THE MISTAKE: Only handling the FIRST content block
|
| WRONG CODE:
| ---------------------------------------------------------------------------
| response = client.messages.create(...)
|
| block = response.content[0]  <-- ONLY FIRST BLOCK!
|
| if block.type == "tool_use":
|     result = execute_tool(block.name, block.input)
|     # What about the other 2 tools?! THEY'RE IGNORED!
| ---------------------------------------------------------------------------
|
| WHY THIS HAPPENS:
| - Developers ASSUME only one tool call per response
| - Claude CAN return multiple tool_use blocks
| - Code works in testing (single question), fails in production
|
| THE RESULT:
| - User asks for weather, wiki, AND calculator
| - Only weather executes
| - User complains "You didn't answer my calculator question!"
| - Support tickets flood in...
|     """)

    wait_for_input("(Understanding the mistake)")

    print("""
| =======================================================================
| THE CORRECT CODE: Loop through ALL blocks!
| =======================================================================
|
| CORRECT CODE:
| ---------------------------------------------------------------------------
| response = client.messages.create(...)
|
| for block in response.content:  <-- LOOP THROUGH ALL!
|
|     if block.type == "tool_use":
|         result = execute_tool(block.name, block.input)
|         # ALL tools get processed! Success!
|
| ---------------------------------------------------------------------------
|
| KEY INSIGHT:
| - ALWAYS loop through response.content with 'for' statement
| - NEVER assume response.content only has one block
| - Claude decides how many tools to use, not you!
|     """)

    wait_for_input("(Learning the fix)")


# ============================================================================
# PART 4: Content Block Anatomy
# ============================================================================

def show_block_anatomy():
    """
    Show what Claude's response can contain.
    """

    print_section("PART 4: CONTENT BLOCK ANATOMY")

    print("""
| response.content is a LIST of blocks. Each block can be:
|
| +========================================================================+
| | BLOCK TYPE      | WHAT IT IS                         | EXAMPLE        |
| +========================================================================+
| | "text"          | Claude's text response              | "The weather..."|
| | "tool_use"       | Claude requesting a tool call      | get_weather(...)|
| | "tool_result"    | Not from Claude - it's from YOU    | Result to send  |
| +========================================================================+
|
| A Claude response might look like:
|
| response.content = [
|     Block 1: { type: "text", text: "Let me check..." },
|     Block 2: { type: "tool_use", name: "get_weather", input: {...} },
|     Block 3: { type: "tool_use", name: "search_wiki", input: {...} },
|     Block 4: { type: "tool_use", name: "calculator", input: {...} }
| ]
|
| YOU MUST handle ALL of these blocks!
|     """)

    wait_for_input("(Understanding block types)")


# ============================================================================
# PART 5: Complete Visual Flow with Multi-Tool
# ============================================================================

def show_complete_flow():
    """
    Show the complete multi-tool flow diagram.
    """

    print_section("PART 5: COMPLETE MULTI-TOOL FLOW DIAGRAM")

    print("""
+==========================================================================+
|                                                                          |
|  COMPLETE MULTI-TOOL AGENTIC LOOP                                         |
|                                                                          |
+==========================================================================+

    STEP 1: INITIALIZATION
    =========================
         |
         v
    +-------------------+
    | messages = []     |
    | tools = [3 tools] |
    +-------------------+
         |
         v

    STEP 2: USER MESSAGE
    =========================
         |
         | messages.append({
         |   role: "user",
         |   content: "Weather in Tokyo AND info about Japan"
         | })
         v

    STEP 3: API REQUEST
    =========================
         |
         v
    +===========================================+
    | CLIENT -----> MESSAGES.CREATE()          |
    |              messages + 3 tools          |
    +===========================================+
         |
         v

    STEP 4: API RESPONSE
    =========================
         |
         | Claude responds with MULTIPLE blocks:
         |
         +--> Block 1: Text: "Let me check all that..."
         +--> Block 2: tool_use: get_weather(city="Tokyo")
         +--> Block 3: tool_use: search_wiki(query="Japan")
         |
         +---> stop_reason: "tool_use" (not end_turn!)
         |
         v

    STEP 5: CHECK STOP_REASON
    =========================
         |
         | if stop_reason == "tool_use":
         |       |
         |       v
         | LOOP THROUGH ALL BLOCKS!
         |
         +--> Block 0: Text -> Save for assistant message
         +--> Block 1: tool_use -> Execute get_weather
         +--> Block 2: tool_use -> Execute search_wiki
         |
         v

    STEP 6: EXECUTE ALL TOOLS (PARALLEL!)
    =========================
         |
         +===========+============+============+
         |           |            |            |
         v           v            v            v
    +---------+ +---------+ +---------+
    | get_    | | search_ | | (no 3rd |
    | weather | | wiki    | | tool in |
    +---------+ +---------+ | this    |
         |           |      | example)|
         v           v      +---------+
    +---------+ +---------+
    | "22C    | | "Japan: |
    | cloudy" | | info..."|
    +---------+ +---------+
         |           |
         v           v
    +===========+============+
    | ALL RESULTS COLLECTED |
    +=======================+
         |
         v

    STEP 7: UPDATE MESSAGES (IN ORDER!)
    =========================
         |
         +---> 1. Add assistant message (Claude's request)
         |       messages.append({
         |         role: "assistant",
         |         content: [text block + tool_use blocks]
         |       })
         |
         +---> 2. Add USER message with ALL tool results
         |       messages.append({
         |         role: "user",
         |         content: [{
         |           type: "tool_result",
         |           tool_use_id: id1,
         |           content: "22C cloudy"
         |         }, {
         |           type: "tool_result",
         |           tool_use_id: id2,
         |           content: "Japan info..."
         |         }]
         |       })
         |
         v

    STEP 8: LOOP BACK (OR EXIT)
    =========================
         |
         | Loop back to Step 3 with updated messages
         | Claude sees all results, forms final answer
         |
         +---> New response: stop_reason = "end_turn"
         |
         v

    STEP 9: FINAL ANSWER
    =========================
         |
         | Claude combines all info into complete answer:
         | "The weather in Tokyo is 22C and partly cloudy.
         |  Regarding Japan: [wiki info]..."
         |
         v
    +-------------------+
    | RETURN TO USER!   |
    +-------------------+


+==========================================================================+
|                                                                          |
|  KEY DIFFERENCE FROM SINGLE-TOOL:                                        |
|                                                                          |
|  - Loop through ALL blocks, not just index [0]                          |
|  - Collect ALL tool results, not just one                                |
|  - Add ALL results in one user message (or multiple user messages)       |
|  - Claude gets COMPLETE picture of all results                          |
|                                                                          |
+==========================================================================+
    """)

    wait_for_input("(Understanding the complete flow)")


# ============================================================================
# PART 6: Code Comparison - Wrong vs Right
# ============================================================================

def show_code_comparison():
    """
    Show the right and wrong code side by side.
    """

    print_section("PART 6: CODE COMPARISON - Wrong vs Right")

    print("""
| =======================================================================
| WRONG CODE: Assumes only one tool call
| =======================================================================
|
| # BAD: Only handles FIRST block
| response = client.messages.create(...)
|
| block = response.content[0]  # WRONG!
|
| if block.type == "tool_use":
|     result = execute_tool(block.name, block.input)
|     # Other tools: IGNORED!
|
| # WHY THIS FAILS:
| # - Claude might return 3 tool_use blocks
| # - You only process the first one
| # - User gets incomplete answers
|
+===========================================================================
    """)

    wait_for_input("(Seeing the wrong code)")

    print("""
| =======================================================================
| CORRECT CODE: Loop through ALL blocks
| =======================================================================
|
| # CORRECT: Handle ALL content blocks
| response = client.messages.create(...)
|
| assistant_message = {"role": "assistant", "content": []}
| tool_results = []
|
| for block in response.content:  # Loop through ALL!
|
|     if block.type == "text":
|         # Save text for assistant message
|         assistant_message["content"].append({
|             "type": "text",
|             "text": block.text
|         })
|
|     elif block.type == "tool_use":
|         # CLUECAL TOOL CALL!
|         tool_name = block.name
|         tool_input = block.input
|         tool_id = block.id
|
|         # Execute on YOUR machine
|         result = execute_tool(tool_name, tool_input)
|
|         # Save for later
|         assistant_message["content"].append({
|             "type": "tool_use",
|             "id": tool_id,
|             "name": tool_name,
|             "input": tool_input
|         })
|
|         tool_results.append({
|             "tool_use_id": tool_id,
|             "content": result
|         })
|
| # Add messages in order
| messages.append(assistant_message)
| messages.append({  # All results in one user message
|     "role": "user",
|     "content": [{
|         "type": "tool_result",
|         "tool_use_id": tr["tool_use_id"],
|         "content": tr["content"]
|     } for tr in tool_results]
| })
|
| docmd THIS is correct:
| # - ALL blocks processed
| # - ALL tools executed
| # - ALL results returned to Claude
|
+===========================================================================
    """)

    wait_for_input("(Seeing the correct code)")


# ============================================================================
# PART 7: Live Demo with Claude
# ============================================================================

def show_live_demo():
    """
    Demo with Claude using multiple tools.
    """

    print_section("PART 7: LIVE DEMONSTRATION WITH CLAUDE")

    print("""
| Now let's see it in action!
|
| We'll ask Claude to use multiple tools:
| - get_weather: Weather info
| - search_wiki: Information search
| - calculator: Simple math
|
| Watch how Claude calls ALL of them at once!
|     """)

    wait_for_input("(Starting live demo)")

    # Define the 3 tools
    tools = [
        {
            "name": "get_weather",
            "description": "Get the current weather for a city.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name"}
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
                    "query": {"type": "string", "description": "Search query"}
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
                    "expression": {"type": "string", "description": "Math expression"}
                },
                "required": ["expression"]
            }
        }
    ]

    messages = [{
        "role": "user",
        "content": "I need three things: (1) Weather in Tokyo, (2) Information about Mount Fuji, (3) Calculate 1500 + 2500"
    }]

    print("\n| User question: 'I need three things: (1) Weather in Tokyo, (2) Info about Mount Fuji, (3) Calculate 1500 + 2500'")
    print("|")
    print("| Sending to Claude with 3 tools available...")
    print("|")

    wait_for_input("(Sending to Claude)")

    response = client.messages.create(
        model="claude-haiku-4-5-20250601",
        max_tokens=1024,
        messages=messages,
        tools=tools,
    )

    print(f"|")
    print(f"| Claude responded!")
    print(f"| stop_reason: {response.stop_reason}")
    print(f"|")
    print(f"| Content blocks: {len(response.content)}")
    print("|")

    # Show all blocks
    for i, block in enumerate(response.content):
        print(f"| Block {i+1}: type='{block.type}'")
        if hasattr(block, 'text') and block.text:
            print(f"|         text: '{block.text[:60]}...'")
        if hasattr(block, 'name'):
            print(f"|         tool: {block.name}")
            print(f"|         input: {block.input}")
        print("|")

    wait_for_input("(Seeing Claude's response)")

    if response.stop_reason == "tool_use":
        print("\n| Claude wants to use tools! Let's execute ALL of them!")
        print("|")
        print("| " + "-" * 50)

        assistant_message = {"role": "assistant", "content": []}
        tool_results = []

        for block in response.content:
            if block.type == "tool_use":
                tool_name = block.name
                tool_input = block.input
                tool_id = block.id

                print(f"|")
                print(f"| Executing: {tool_name}")
                print(f"| Input: {tool_input}")

                # Simulate tool execution
                if tool_name == "get_weather":
                    result = f"Weather in {tool_input.get('city')}: 22C, partly cloudy"
                elif tool_name == "search_wiki":
                    result = f"Wikipedia: {tool_input.get('query')} is a famous mountain in Japan"
                elif tool_name == "calculator":
                    try:
                        result = str(eval(tool_input.get("expression", "0")))
                    except:
                        result = "Error"
                else:
                    result = "Unknown tool"

                print(f"| Result: {result}")

                assistant_message["content"].append({
                    "type": "tool_use",
                    "id": tool_id,
                    "name": tool_name,
                    "input": tool_input
                })

                tool_results.append({
                    "tool_use_id": tool_id,
                    "content": result
                })

        print("| " + "-" * 50)
        print(f"|")
        print(f"| Executed {len(tool_results)} tools in ONE loop!")
        print("|")

        wait_for_input("(Tools executed!)")

        # Update messages
        messages.append(assistant_message)
        messages.append({
            "role": "user",
            "content": [{
                "type": "tool_result",
                "tool_use_id": tr["tool_use_id"],
                "content": tr["content"]
            } for tr in tool_results]
        })

        # Get final response
        print("|")
        print("| Sending all results back to Claude...")
        print("|")

        final_response = client.messages.create(
            model="claude-haiku-4-5-20250601",
            max_tokens=1024,
            messages=messages,
            tools=tools,
        )

        if final_response.stop_reason == "end_turn":
            print("|")
            print("| CLAUDE'S FINAL ANSWER:")
            print("|" + "-" * 50)
            for block in final_response.content:
                if block.type == "text":
                    print(f"| {block.text}")
            print("|" + "-" * 50)

    wait_for_input("(Demo complete)")


# ============================================================================
# PART 8: Common Mistakes Summary
# ============================================================================

def show_mistakes_summary():
    """
    Show all the common mistakes in summary.
    """

    print_section("PART 8: COMMON MISTAKES - QUICK REFERENCE")

    print("""
| =======================================================================
| MISTAKE #1: Only handling first block
| =======================================================================
|
| WRONG:   block = response.content[0]
| RIGHT:   for block in response.content:
|
+===========================================================================

| =======================================================================
| MISTAKE #2: Adding tool results in wrong order
| =======================================================================
|
| WRONG:   messages.append({tool_result})
|          messages.append({tool_result})  # Order might be wrong!
|
| RIGHT:   Collect ALL results first
|          Then add in loop with correct tool_use_id matching
|
+===========================================================================

| =======================================================================
| MISTAKE #3: Ignoring text blocks
| =======================================================================
|
| WRONG:   Only check: if block.type == "tool_use"
| RIGHT:   Handle BOTH text and tool_use in the loop
|
+===========================================================================

| =======================================================================
| MISTAKE #4: Using block index instead of ID matching
| =======================================================================
|
| WRONG:   Assuming results[0] matches tool_calls[0] positionally
| RIGHT:   Match by tool_use_id (block.id)
|
+===========================================================================

| =======================================================================
| MISTAKE #5: Breaking out of loop early
| =======================================================================
|
| WRONG:   for block in content:
|              if block.type == "tool_use":
|                  break  # STOPPING after first tool!
|
| RIGHT:   for block in content:
|              if block.type == "tool_use":
|                  process_it()
|              # DO NOT break! Continue through ALL blocks!
|
+===========================================================================
    """)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Fix stdout encoding for Windows
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("\n" + "=" * 70)
    print("  MULTI-TOOL AGENTIC LOOP - COMPLETE TEACHING PROGRAM")
    print("=" * 70)
    print("""
|
| This program teaches:
|
| 1. Why single-tool isn't enough
| 2. Visual comparison of single vs multi-tool
| 3. The critical mistake to avoid
| 4. Content block anatomy
| 5. Complete flow diagram
| 6. Code comparison (wrong vs right)
| 7. Live demo with Claude
| 8. Common mistakes summary
|
| Press ENTER to begin!
|
    """)

    wait_for_input()

    # Part 1: The problem
    show_the_problem()

    # Part 2: Visual comparison
    show_visual_comparison()

    # Part 3: Critical mistake
    show_critical_mistake()

    # Part 4: Block anatomy
    show_block_anatomy()

    # Part 5: Complete flow
    show_complete_flow()

    # Part 6: Code comparison
    show_code_comparison()

    # Part 7: Live demo
    show_live_demo()

    # Part 8: Mistakes summary
    show_mistakes_summary()

    print("\n" + "=" * 70)
    print("  MULTI-TOOL TEACHING PROGRAM COMPLETE!")
    print("=" * 70)
    print("""
|
| KEY TAKEAWAYS:
|
| 1. ALWAYS loop through ALL content blocks (for block in content)
|
| 2. NEVER assume only one tool call per response
|
| 3. Handle BOTH text and tool_use blocks in the same loop
|
| 4. Match results using tool_use_id (block.id)
|
| 5. Collect ALL results before sending back to Claude
|
| STAY SAFE IN PRODUCTION!
|
+==========================================================================+
    """)


"""
+===========================================================================+
|                                                                           |
|  EXTRA: Interview Questions & Answers                                    |
|                                                                           |
+===========================================================================+

| Q1: "How does Claude call multiple tools?"
|
| A: Claude can return multiple tool_use blocks in one response.
|    Each block contains: name, input, and unique id.
|    The response stop_reason is still "tool_use" (not end_turn).
|
+-----------------------------------------------------------------------------+

| Q2: "Why is looping through all blocks important?"
|
| A: Because Claude decides how many tools to use, not the developer.
|    If you only process the first block, you miss the other tools.
|    This causes incomplete answers and confused users.
|
+-----------------------------------------------------------------------------+

| Q3: "What happens if I don't execute all tools?"
|
| A: The tool results are never sent back to Claude.
|    Claude waits for results, but they never come.
|    The loop hangs or returns incomplete information.
|
+-----------------------------------------------------------------------------+

| Q4: "Can tool results be sent in multiple user messages?"
|
| A: Yes! You can add each tool result as a separate user message,
|    or all results in one user message. Both work.
|    The important part is matching tool_use_id correctly.
|
+-----------------------------------------------------------------------------+

| Q5: "What's the performance impact of multi-tool?"
|
| A: Multi-tool is FASTER because:
|    - All tools can execute in parallel (on your side)
|    - One fewer API round trip (vs sequential single-tool)
|    - Better user experience (gets complete answer faster)
|
+===========================================================================+
"""