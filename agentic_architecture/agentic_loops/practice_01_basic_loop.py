"""
+===========================================================================+
|                                                                           |
|  PRACTICE 1: BASIC AGENTIC LOOP                                           |
|                                                                           |
|  The "Hello World" of AI Agents - The simplest possible agent             |
|  that uses tools to accomplish tasks                                      |
|                                                                           |
|  This practice introduces the fundamental agentic loop pattern:          |
|  Send message -> Get response -> Execute tools -> Loop back              |
|                                                                           |
|  + REAL-TIME SCENARIOS + MISTAKES DEVELOPERS MAKE + INTERVIEW Q&A      |
|                                                                           |
+===========================================================================+

INTERVIEW PREP: "How does an AI agent use tools?"
This question tests your understanding of the fundamental agent loop.
Understanding this pattern is CRITICAL for building production AI systems.

REAL-TIME SCENARIO: You're building a customer service chatbot.
You need the AI to look up order status, calculate refunds, and
update database records. All done through tool calling!

===========================================================================
THE BASIC AGENTIC LOOP - STEP BY STEP
===========================================================================

    +-----------------------------------------------------------------------+
    | VISUAL: The Complete Agentic Loop Flow                                |
    +-----------------------------------------------------------------------+

    +-------------------+          +-------------------+
    |   USER MESSAGE    |          |   Claude receives |
    | "What is 2+2?"    | --------> |   the question    |
    +-------------------+          +-------------------+
                                           |
                                           v
    +-------------------+          +-------------------+
    |   FINAL ANSWER    | <-------- |   Claude thinks:  |
    | "The answer is 4" |          | "Use calculator!" |
    +-------------------+          +-------------------+
             ^                          |
             |                          | (No tool needed,
             |                          |  simple math)
             |                          v
             |                  +-------------------+
             |                  | stop_reason =     |
             |                  | "end_turn"        |
             |                  +-------------------+

    ---- vs when tools ARE needed ----

    +-------------------+          +-------------------+
    |   USER MESSAGE    |          |   Claude receives |
    | "What is 1500 +   | --------> |   the question    |
    |  2500?"          |          +-------------------+
    +-------------------+                   |
                                            v
                               +-------------------+
                               | Claude decides:   |
                               | "Need calculator" |
                               +-------------------+
                                            |
                                            | tool_use
                                            v
    +-------------------+          +-------------------+
    |   FINAL ANSWER    | <-------- |   Tool called:    |
    | "The answer is    |          | calculator(1500+  |
    |  4000"           |          | 2500)            |
    +-------------------+          +-------------------+
             ^                          |
             |                          v
             |                  +-------------------+
             |                  | Tool executes     |
             |                  | Returns: 4000    |
             |                  +-------------------+
             |                          |
             |                          v (result sent back)
             |                  +-------------------+
             |                  | Claude synthesizes|
             |                  | Final answer      |
             |                  +-------------------+
             |                          |
             +--------------------------+
                      (Loop back with result)

    +-----------------------------------------------------------------------+
    | KEY INSIGHT: The loop continues until stop_reason = "end_turn"       |
    | Each tool call adds to conversation history for next iteration       |
    +-----------------------------------------------------------------------+

===========================================================================
KEY CONCEPTS YOU'LL LEARN
===========================================================================

    1. TOOL DEFINITION: How to tell Claude what tools exist
    2. TOOL CALLING: How Claude decides to use a tool
    3. TOOL EXECUTION: How to run the tool and return results
    4. LOOP MECHANICS: How the agentic loop continues until done

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
# TOOL DEFINITION
# ============================================================================
# This is how we TELL Claude what tools it can use!
# Claude doesn't have built-in tools - we define them here.

tools = [
    {
        "name": "calculator",
        "description": "Perform basic arithmetic calculations",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Mathematical expression to evaluate (e.g., '2 + 2', '10 * 5', '1500 + 2500')"
                }
            },
            "required": ["expression"]
        }
    }
]


def execute_tool(name: str, tool_input: dict) -> str:
    """
    Execute a tool and return the result as a string.

    IMPORTANT: This is where YOUR code actually does the work!
    The AI decides WHAT to call, YOU decide HOW to execute it.
    """
    if name == "calculator":
        try:
            expression = tool_input["expression"]
            result = eval(expression)
            return str(result)
        except Exception as e:
            return f"Error: {e}"

    return f"Unknown tool: {name}"


def run_agentic_loop(user_message: str):
    """
    Run the agentic loop pattern.

    The core pattern:
    1. Send messages to Claude
    2. Check stop_reason - if "tool_use", execute tools
    3. If "end_turn", return the final answer
    """
    messages = [{"role": "user", "content": user_message}]
    iteration = 0

    while True:
        iteration += 1
        print(f"\n{'='*50}")
        print(f"ITERATION {iteration}")
        print('='*50)

        print("Sending request to Claude...")

        response = client.messages.create(
            model="claude-haiku-4-5-20250601",
            max_tokens=4096,
            messages=messages,
            tools=tools,
        )

        print(f"Stop reason: {response.stop_reason}")

        if response.stop_reason == "tool_use":
            print("\nClaude wants to use a tool!")

            # Build the assistant message with tool_use blocks
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

            print("\nLooping back to Claude with tool results...")
            continue

        elif response.stop_reason == "end_turn":
            print("\nClaude has the final answer!")

            final_response = ""
            for block in response.content:
                if block.type == "text" and block.text:
                    final_response = block.text
                    break

            print(f"\n   Final response:\n   {final_response}")

            return final_response


# ============================================================================
# REAL-TIME SCENARIOS: When basic loops break in production
# ============================================================================

def show_real_time_scenarios():
    """
    Production scenarios where the basic agentic loop concept breaks.
    """

    print("\n" + "=" * 70)
    print("REAL-TIME SCENARIOS: When Basic Loops Break in Production")
    print("=" * 70)

    print("""
    +======================================================================+
    ||                                                                      ||
    ||  SCENARIO #1: The Infinite Loop                                     ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  PROBLEM:                                                            ||
    ||  - Your agent keeps calling tools forever                            ||
    ||  - Never reaches stop_reason = "end_turn"                           ||
    ||  - In production: Server hangs, timeout after 60 seconds            ||
    ||                                                                      ||
    ||  CAUSE:                                                              ||
    ||  - Tool returns values that trigger more tool calls                  ||
    ||  - No max_iterations limit set                                       ||
    ||  - Model keeps "thinking" it needs more tools                       ||
    ||                                                                      ||
    ||  PRODUCTION IMPACT:                                                  ||
    ||  - Server hangs                                                      ||
    ||  - User sees "Request processing..." forever                        ||
    ||  - AWS Lambda timeout after 60 seconds                               ||
    ||  - Lost requests, angry users                                        ||
    ||                                                                      ||
    ||  FIX: Always set max_iterations = 10 or 20                          ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  SCENARIO #2: The Tool Not Defined Error                            ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  PROBLEM:                                                            ||
    ||  - Claude says "I need to use searchWikipedia tool"                  ||
    ||  - But you never defined searchWikipedia in your tools list!       ||
    ||  - Result: Claude ignores the tool, gives wrong answer              ||
    ||                                                                      ||
    ||  CAUSE:                                                              ||
    ||  - Tools list is empty or incomplete                                ||
    ||  - Forgot to pass tools= parameter to messages.create()           ||
    ||  - Copy-paste error from previous project                           ||
    ||                                                                      ||
    ||  PRODUCTION IMPACT:                                                  ||
    ||  - User asks "Check order status #12345"                            ||
    ||  - Claude says "I would search the database..." but can't            ||
    ||  - Gives incomplete answer, user frustrated                         ||
    ||                                                                      ||
    ||  FIX: Always double-check tools list before deployment              ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  SCENARIO #3: The Wrong Tool Result Format                          ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  PROBLEM:                                                            ||
    ||  - Your execute_tool returns a Python dict                          ||
    ||  - But Claude expects a STRING in tool_result content               ||
    ||  - Result: Claude fails to parse the response                       ||
    ||                                                                      ||
    ||  CAUSE:                                                              ||
    ||  - Returning {"result": "value"} instead of "value"                 ||
    ||  - Missing str() conversion                                         ||
    ||                                                                      ||
    ||  PRODUCTION IMPACT:                                                  ||
    ||  - Agent gets TypeError when trying to combine results             ||
    ||  - "TypeError: cannot concatenate 'dict' and 'str'"                 ||
    ||  - Incomplete responses to users                                    ||
    ||                                                                      ||
    ||  FIX: ALWAYS return a STRING from execute_tool()                    ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  SCENARIO #4: The Missing tool_use_id                               ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  PROBLEM:                                                            ||
    ||  - You forget to include block.id in tool_use message               ||
    ||  - Claude can't match tool result to correct call                   ||
    ||  - In multi-tool calls: results get mixed up                        ||
    ||                                                                      ||
    ||  CAUSE:                                                              ||
    ||  - Forgetting "id": block.id in assistant_message                  ||
    ||  - Typo in tool_use_id field                                        ||
    ||                                                                      ||
    ||  PRODUCTION IMPACT:                                                  ||
    ||  - User asks "What's weather AND stock price?"                     ||
    ||  - Weather result gets attached to stock tool call                  ||
    ||  - Contradictory response: "Stock price is partly cloudy"          ||
    ||                                                                      ||
    ||  FIX: Always copy block.id exactly as provided                      ||
    ||                                                                      ||
    +======================================================================+
    """)


# ============================================================================
# MISTAKES DEVELOPERS MAKE: Expert warnings
# ============================================================================

def show_mistakes():
    """
    Common errors developers make with basic agentic loops.
    """

    print("\n" + "=" * 70)
    print("MISTAKES DEVELOPERS MAKE - EXPERT WARNINGS")
    print("=" * 70)

    print("""
    +======================================================================+
    ||                                                                      ||
    ||  MISTAKE #1: Forgetting the tools parameter                         ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WRONG CODE:                                                         ||
    ||  response = client.messages.create(                                  ||
    ||      model="claude-haiku-4-5-20250601",                              ||
    ||      messages=messages,                                              ||
    ||      # tools=tools <- FORGOTTEN!                                     ||
    ||  )                                                                   ||
    ||                                                                      ||
    ||  WHAT HAPPENS:                                                       ||
    ||  - Claude never sees the tool definitions                           ||
    ||  - Claude says "I can't use tools" or ignores them                  ||
    ||                                                                      ||
    ||  CORRECT CODE:                                                       ||
    ||  response = client.messages.create(                                  ||
    ||      model="claude-haiku-4-5-20250601",                              ||
    ||      messages=messages,                                              ||
    ||      tools=tools,              # ALWAYS include this                ||
    ||  )                                                                   ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  MISTAKE #2: Not handling tool_use stop_reason                      ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WRONG CODE:                                                         ||
    ||  if response.stop_reason == "end_turn":                             ||
    ||      # Only handles end_turn, ignores tool_use!                     ||
    ||      return response                                                 ||
    ||                                                                      ||
    ||  WHAT HAPPENS:                                                       ||
    ||  - If Claude wants to use a tool, your code ignores it              ||
    ||  - Response gets dropped, no answer to user                         ||
    ||                                                                      ||
    ||  CORRECT CODE:                                                       ||
    ||  if response.stop_reason == "tool_use":                            ||
    ||      # Execute tools and loop back                                   ||
    ||      execute_tools_and_loop()                                        ||
    ||  elif response.stop_reason == "end_turn":                           ||
    ||      return response                                                 ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  MISTAKE #3: Using eval() in production (SECURITY RISK!)            ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WRONG CODE:                                                         ||
    ||  def execute_tool(name, tool_input):                                 ||
    ||      if name == "calculator":                                        ||
    ||          return eval(tool_input["expression"])  # DANGEROUS!       ||
    ||                                                                      ||
    ||  SECURITY RISK:                                                      ||
    ||  - User input: "__import__('os').system('rm -rf /')"                ||
    ||  - eval() executes shell commands = COMPROMISED SERVER               ||
    ||                                                                      ||
    ||  CORRECT CODE:                                                       ||
    ||  import ast                                                          ||
    ||  def safe_eval(expr):                                                ||
    ||      try:                                                            ||
    ||          # Only allow math operations                                ||
    ||          tree = ast.parse(expr, mode='eval')                         ||
    ||          # Validate nodes are only math ops                          ||
    ||          return eval(compile(tree, '', 'eval'),                      ||
    ||                        {"__builtins__": {}})                         ||
    ||      except:                                                         ||
    ||          return "Invalid expression"                                 ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  MISTAKE #4: Not passing tool_use_id in result message              ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WRONG CODE:                                                         ||
    ||  messages.append({                                                   ||
    ||      "role": "user",                                                  ||
    ||      "content": [{                                                   ||
    ||          "type": "tool_result",                                      ||
    ||          "content": result  # Missing tool_use_id!                  ||
    ||      }]                                                              ||
    ||  })                                                                   ||
    ||                                                                      ||
    ||  WHAT HAPPENS:                                                       ||
    ||  - Claude can't match result to correct tool call                    ||
    ||  - With multiple tools: results get confused                        ||
    ||                                                                      ||
    ||  CORRECT CODE:                                                       ||
    ||  messages.append({                                                   ||
    ||      "role": "user",                                                  ||
    ||      "content": [{                                                   ||
    ||          "type": "tool_example_result",                              ||
    ||          "tool_use_id": tool_result["tool_use_id"],  # Required!   ||
    ||          "content": tool_result_example["content"]                  ||
    ||      }]                                                              ||
    ||  })                                                                   ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  MISTAKE #5: Not converting results to string                       ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WRONG CODE:                                                         ||
    ||  def execute_tool(name, tool_input):                                 ||
    ||      if name == "calculator":                                        ||
    ||          return 1500 + 2500  # Returns int, not string!           ||
    ||                                                                      ||
    ||  WHAT HAPPENS:                                                       ||
    ||  - Claude receives int, not string                                  ||
    ||  - Claude's tool_result content expects string                       ||
    ||  - TypeError in subsequent processing                               ||
    ||                                                                      ||
    ||  CORRECT CODE:                                                       ||
    ||  def execute_tool(name, tool_input):                                ||
    ||      if name == "calculator":                                        ||
    ||          return str(1500 + 2500)  # Always return string!            ||
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
    INTERVIEW Q1: "How does an AI agent use tools?"
    ======================================================================

    EXPERT ANSWER STRUCTURE:
    1. Define tools in a schema with name, description, input schema
    2. Pass tools to the model via messages.create(tools=tools)
    3. Model decides whether to use a tool based on stop_reason
    4. If tool_use: execute tool, return result as string
    5. Add result back to conversation history
    6. Loop until stop_reason = "end_turn"

    EXAMPLE ANSWER:
    "You define tools as a list of schemas with name, description, and
    input_schema. Pass this to the model when creating messages. The model
    responds with stop_reason='tool_use' when it wants to call a tool. Your
    code executes the tool, returns the result as a string, and adds it back
    to the conversation. This loop continues until stop_reason='end_turn'."

    RED FLAGS IN ANSWERS:
    - "The AI just knows how to use tools" -> Shows no understanding
    - "Tools are built into the model" -> Wrong, models don't have tools!
    - "You call tools before sending to the model" -> Confuses the flow

    +-----------------------------------------------------------------------+
    | EXPERT TIP: Always mention that tools must be PASSED to the model.    |
    | Models don't have built-in tools - they're defined by developers.     |
    +-----------------------------------------------------------------------+


    ======================================================================
    INTERVIEW Q2: "What is stop_reason and why does it matter?"
    ======================================================================

    EXPERT ANSWER STRUCTURE:
    1. stop_reason tells you WHY the model stopped generating
    2. "tool_use" = model wants to call a tool, loop continues
    3. "end_turn" = model has final answer, loop ends
    4. Must check this to know whether to execute tools or return answer

    EXAMPLE ANSWER:
    "stop_reason tells you what the model decided to do. If it's 'tool_use',
    the model wants to call a tool - you execute it and loop back. If it's
    'end_turn', the model has the final answer and you can return it to
    the user. Ignoring stop_reason means you can't handle tool calls."

    KEY VALUES TO MEMORIZE:
    - "tool_use" = execute tools, keep looping
    - "end_turn" = return final answer
    - "max_tokens" = hit token limit (unexpected)

    +-----------------------------------------------------------------------+
    | EXPERT TIP: Mention all three stop_reason values and their handling.   |
    +-----------------------------------------------------------------------+


    ======================================================================
    INTERVIEW Q3: "What's the difference between function calling and
                  tool use in Claude's API?"
    ======================================================================

    EXPERT ANSWER:
    "In Anthropic's API, it's called 'tool use'. You pass tool definitions
    to messages.create() and the model returns tool_use blocks when it
    wants to call a tool. Other APIs like OpenAI call this 'function
    calling', but the concept is the same: model decides when to use
    a tool, returns the call request, you execute and return results."

    RED FLAGS IN ANSWERS:
    - "They're completely different" -> Shows confusion
    - "Function calling is better" -> Subjective, missing explanation

    +-----------------------------------------------------------------------+
    | EXPERT TIP: Know that Anthropic uses "tool use" as the terminology.   |
    +-----------------------------------------------------------------------+


    ======================================================================
    INTERVIEW Q4: "How do you prevent infinite tool loops?"
    ======================================================================

    EXPERT ANSWER STRUCTURE:
    1. Always set max_iterations limit (e.g., 10 or 20)
    2. Track iteration count, break if exceeded
    3. Log iterations for debugging
    4. Return partial answer if max iterations reached

    EXAMPLE ANSWER:
    "I always set a max_iterations limit and track the count. If it exceeds
    the limit, I return what we have so far with a note that the request
    was too complex. I also log iterations for debugging if users report
    issues. This prevents server hangs in production."

    RED FLAGS IN ANSWERS:
    - "I've never had that happen" -> Likely untested in production
    - "Just increase max_tokens" -> Doesn't fix loops

    +-----------------------------------------------------------------------+
    | EXPERT TIP: Production systems ALWAYS have max_iterations limits.     |
    +-----------------------------------------------------------------------+
    """)


# ============================================================================
# VISUAL REPRESENTATIONS: ASCII diagrams
# ============================================================================

def show_visual_representations():
    """
    ASCII diagrams showing the agentic loop concept.
    """

    print("\n" + "=" * 70)
    print("VISUAL REPRESENTATIONS: Understanding the Agentic Loop")
    print("=" * 70)

    print("""
    +======================================================================+
    ||  DIAGRAM 1: Complete Agentic Loop Flowchart                        ||
    +======================================================================+

                         [User Message]
                               |
                               v
                    +----------------------+
                    |  messages.create()    |
                    |  (with tools)         |
                    +----------------------+
                               |
                               v
                    +----------------------+
                    |  Claude Responds     |
                    +----------------------+
                               |
                               v
                    +----------------------+
                    |  Check stop_reason   |
                    +----------------------+
                        /              \\
                       /                \\
                      v                  v
           +------------------+  +------------------+
           | tool_use?        |  | end_turn?        |
           +------------------+  +------------------+
                 |                    |
                 |                    |
                 v                    v
        +------------------+  +------------------+
        | Execute tool()    |  | [FINAL ANSWER]   |
        | Return result    |  | Return to user   |
        +------------------+  +------------------+
                 |                    |
                 |                    |
                 v                    |
        +------------------+          |
        | Add result to    |          |
        | messages        |          |
        +------------------+          |
                 |                    |
                 +--------------------+
                      (Loop back)


    +======================================================================+
    ||  DIAGRAM 2: Message Structure in Multiple Iterations                ||
    +======================================================================+

    ITERATION 1:
    +-------------------------------+
    | role: "user"                  |  <- Initial question
    | content: "What is 1500+2500?" |
    +-------------------------------+
    | role: "assistant"            |  <- Claude's analysis
    | content: "I'll calculate"    |
    +-------------------------------+
    | role: "assistant"            |  <- Tool call
    | content: [tool_use: calc]    |
    +-------------------------------+

    ITERATION 2 (after tool execution):
    +-------------------------------+
    | role: "user"                  |  <- Initial question
    | content: "What is 1500+2500?" |
    +-------------------------------+
    | role: "assistant"            |
    | content: "I'll calculate"    |
    +-------------------------------+
    | role: "assistant"            |
    | content: [tool_use: calc]    |
    +-------------------------------+
    | role: "user"                 |  <- Tool RESULT added
    | content: [tool_result: 4000]|
    +-------------------------------+

    ITERATION 3:
    +-------------------------------+
    | role: "user"                  |
    | content: "What is 1500+2500?" |
    +-------------------------------+
    | ...all previous...           |
    +-------------------------------+
    | role: "assistant"            |  <- FINAL ANSWER
    | content: "The answer is 4000"|
    +-------------------------------+


    +======================================================================+
    ||  DIAGRAM 3: Tool Definition Schema Structure                       ||
    +======================================================================+

    tool_definition = {
        "name": "calculator",           <- Tool identifier
        "description": "...",          <- What it does (for model)
        "input_schema": {              <- Parameters the tool accepts
            "type": "object",           <- Always "object"
            "properties": {            <- Parameter definitions
                "expression": {
                    "type": "string",  <- Parameter type
                    "description": ""  <- What it means (for model)
                }
            },
            "required": ["expression"] <- Mandatory parameters
        }
    }


    +======================================================================+
    ||  DIAGRAM 4: Tool Use Response Structure                            ||
    +======================================================================+

    response.content = [
        {
            "type": "text",
            "text": "I'll calculate this for you."
        },
        {
            "type": "tool_use",                 <- Tool call block
            "id": "toolu_abc123",               <- Unique ID for result
            "name": "calculator",               <- Tool name
            "input": {                          <- Parameters passed
                "expression": "1500 + 2500"
            }
        }
    ]

    YOUR execute_tool receives:
        name = "calculator"
        tool_input = {"expression": "1500 + 2500"}

    YOU MUST RETURN:
        str = "4000"

    THEN add to messages:
        {
            "role": "user",
            "content": [{
                "type": "tool_result",
                "tool_use_id": "toolu_abc123",  <- Match the ID!
                "content": "4000"                <- STRING result
            }]
        }
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
    print("PRACTICE 1: BASIC AGENTIC LOOP")
    print("=" * 70)
    print("""
    This program demonstrates the simplest possible agentic loop.
    Watch how Claude uses the calculator tool!

    Follow along as we:
    1. Run the basic agentic loop
    2. Show real-time scenarios where loops break
    3. Highlight common mistakes developers make
    4. Provide interview Q&A with expert answers
    5. Show visual representations of the concepts
    """)

    print("\n" + "-" * 70)
    print("PART 1: Running the Basic Agentic Loop")
    print("-" * 70)

    user_input = "What is 1500 + 2500? Use the calculator tool to compute this."

    print(f"\nUser asking: \"{user_input}\"")
    print("\n" + "-" * 70 + "\n")

    run_agentic_loop(user_input)

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
||  1. THE BASIC AGENTIC LOOP PATTERN:                                  ||
||                                                                      ||
||  - User sends message                                                 ||
||  - Claude responds with stop_reason                                  ||
||  - If "tool_use": execute tools, loop back                          ||
||  - If "end_turn": return final answer                                ||
||                                                                      ||
||  TOOLS MUST BE PASSED to messages.create(tools=tools)               ||
||  Claude doesn't have built-in tools - you define them!              ||
||                                                                      ||
+======================================================================+

+======================================================================+
||  2. REAL-TIME SCENARIOS (Production Breakage):                      ||
||                                                                      ||
||  SCENARIO #1: Infinite Loop                                          ||
||  - No max_iterations limit causes server hangs                       ||
||  - Fix: Always set iteration limits                                  ||
||                                                                      ||
||  SCENARIO #2: Tool Not Defined                                       ||
||  - Forgetting tools= parameter                ||
||  - Fix: Double-check tools list before deploy                        ||
||                                                                      ||
||  SCENARIO #3: Wrong Result Format                                   ||
||  - Returning dict instead of string                                  ||
||  - Fix: Always return str() from execute_tool()                      ||
||                                                                      ||
||  SCENARIO #4: Missing tool_use_id                                    ||
||  - Forgetting block.id causes result mix-ups                        ||
||  - Fix: Always include tool_use_id in result message                ||
||                                                                      ||
+======================================================================+

+======================================================================+
||  3. MISTAKES DEVELOPERS MAKE:                                        ||
||                                                                      ||
||  MISTAKE #1: Forgetting tools parameter                             ||
||  - Always pass tools= to messages.create()                           ||
||                                                                      ||
||  MISTAKE #2: Not handling tool_use stop_reason                      ||
||  - Must check both "tool_use" and "end_turn"                        ||
||                                                                      ||
||  MISTAKE #3: Using eval() in production                             ||
||  - SECURITY RISK! Use safe_eval with ast.parse()                    ||
||                                                                      ||
||  MISTAKE #4: Missing tool_use_id in result                          ||
||  - Include block.id for each tool call result                        ||
||                                                                      ||
||  MISTAKE #5: Not converting results to string                       ||
||  - execute_tool() must return str(), not int/dict/etc.               ||
||                                                                      ||
+======================================================================+

+======================================================================+
||  4. INTERVIEW Q&A FRAMEWORKS:                                        ||
||                                                                      ||
||  Q: "How does an AI agent use tools?"                                ||
||  A: Define tools schema, pass to model, check stop_reason,          ||
||     execute tools, loop until end_turn                               ||
||                                                                      ||
||  Q: "What is stop_reason?"                                          ||
||  A: "tool_use" = execute and loop, "end_turn" = return answer,      ||
||     "max_tokens" = hit limit (unexpected)                            ||
||                                                                      ||
||  Q: "How to prevent infinite loops?"                                ||
||  A: Set max_iterations limit, track count, log iterations           ||
||                                                                      ||
||  KEY PHRASE: "Models don't have built-in tools - you define them!"  ||
||                                                                      ||
+======================================================================+

+======================================================================+
||  5. VISUAL REPRESENTATIONS (ASCII Diagrams):                         ||
||                                                                      ||
||  - Complete loop flowchart: User -> Model -> Tool -> Loop -> Answer ||
||  - Message structure across iterations                               ||
||  - Tool definition schema breakdown                                  ||
||  - Tool use response structure with tool_use_id                      ||
||                                                                      ||
+======================================================================+

+======================================================================+
||  6. KEY RULES TO MEMORIZE:                                           ||
||                                                                      ||
||  RULE #1: Tools must be PASSED to messages.create(tools=tools)      ||
||  RULE #2: Check stop_reason for "tool_use" vs "end_turn"          ||
||  RULE #3: Always return STRING from execute_tool()                    ||
||  RULE #4: Include tool_use_id (block.id) in each result message     ||
||  RULE #5: Set max_iterations limit to prevent infinite loops        ||
||  RULE #6: NEVER use eval() with user input in production           ||
||                                                                      |
+======================================================================+

Next: practice_02_multi_tool.py shows how to work with
MULTIPLE tools simultaneously in one response!

================================================================================
""")


"""
+===========================================================================+
|                                                                           |
|  KEY CONCEPTS FROM THIS FILE:                                           |
|                                                                           |
|  PATTERN:                                                                |
|  - messages.create(tools=tools) -> response.stop_reason                  |
|  - "tool_use" -> execute tools, add results, loop                        |
|  - "end_turn" -> return final answer                                      |
|                                                                           |
|  REAL-TIME FIXES:                                                        |
|  - Set max_iterations to prevent infinite loops                          |
|  - Double-check tools parameter is passed                                |
|  - Always return string from execute_tool()                               |
|  - Include tool_use_id in result messages                                |
|                                                                           |
|  INTERVIEW PREP:                                                        |
|  - "How does an AI agent use tools?"                                     |
|  - "What's the difference between tool_use and function calling?"        |
|  - "How do you prevent infinite loops?"                                 |
|                                                                           |
|  NEXT: practice_02_multi_tool.py (multiple tools)                       |
|                                                                           |
+===========================================================================+
"""
