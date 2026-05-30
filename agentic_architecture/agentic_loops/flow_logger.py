"""
+===========================================================================+
|                                                                           |
|  FLOW_LOGGER: Complete Agentic Loop Execution Tracker                   |
|                                                                           |
|  This program shows the COMPLETE flow of an agentic loop with           |
|  detailed prints/logs at every step so you can see exactly how it works|
|                                                                           |
|  Perfect for understanding the mechanics step-by-step!                  |
|                                                                           |
+===========================================================================
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("ANTHROPIC_API_KEY")

if not API_KEY:
    raise ValueError("ANTHROPIC_API_KEY not found in .env file")


from anthropic import Anthropic

client = Anthropic(api_key=API_KEY)


# ============================================================================
# FLOW LOGGER - Tracks every step of execution
# ============================================================================

class FlowLogger:
    """Tracks and prints every step of the agentic loop execution."""

    def __init__(self):
        self.step = 0
        self.iteration = 0
        self.logs = []

    def next_step(self, category: str, message: str):
        """Log the next step in the execution flow."""
        self.step += 1
        self.logs.append(f"[{category}] {message}")
        print(f"\n{'='*60}")
        print(f"STEP {self.step}: [{category}]")
        print(f"{'='*60}")
        print(message)
        print()

    def next_iteration(self):
        """Start the next iteration."""
        self.iteration += 1
        print(f"\n\n{'#'*70}")
        print(f"# ITERATION {self.iteration}")
        print(f"#{'#'*70}\n")

    def separator(self, title: str = ""):
        """Print a separator with optional title."""
        print(f"\n{'~'*60}")
        if title:
            print(f"~ {title}")
            print(f"~{'~'*59}")


# ============================================================================
# TOOL DEFINITION
# ============================================================================

def get_tool_definition():
    """Returns the tool schema as Claude will see it."""
    return [
        {
            "name": "calculator",
            "description": "Perform basic arithmetic calculations. Use this when the user asks you to calculate math expressions like addition, subtraction, multiplication, or division.",
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


# ============================================================================
# TOOL EXECUTOR (ON YOUR MACHINE!)
# ============================================================================

def execute_tool_locally(tool_name: str, tool_input: dict, logger: FlowLogger) -> str:
    """
    EXECUTES THE TOOL ON YOUR LOCAL MACHINE!

    This is the key part: Claude tells us WHAT to do, but WE do it HERE.
    """
    logger.separator("TOOL EXECUTION ON YOUR LOCAL MACHINE")
    print(f"|")
    print(f"| TOOL EXECUTOR TRIGGERED!")
    print(f"|")
    print(f"| This code runs on YOUR computer, NOT in Claude's cloud!")
    print(f"|")
    print(f"| Tool Name: {tool_name}")
    print(f"| Tool Input: {tool_input}")
    print(f"|")

    result = None
    if tool_name == "calculator":
        expression = tool_input.get("expression", "")
        print(f"|")
        print(f"| Evaluating expression: {expression}")
        print(f"|")

        try:
            result = eval(expression)
            print(f"| RESULT: {result} (type: {type(result).__name__})")
        except Exception as e:
            result = f"Error: {e}"
            print(f"| ERROR: {e}")

    print(f"|")
    print(f"| Tool executor complete!")
    print(f"|")

    return str(result)


# ============================================================================
# COMPLETE AGENTIC LOOP WITH DETAILED LOGGING
# ============================================================================

def run_logged_agentic_loop(user_message: str):
    """
    Run the agentic loop with COMPLETE step-by-step logging.
    This shows exactly what happens at each stage!
    """

    logger = FlowLogger()

    # =========================================================================
    # INITIALIZATION
    # =========================================================================

    logger.separator("INITIALIZATION")

    print("| Setting up the agentic loop...")
    print("|")
    print("| Creating empty messages list...")
    messages = []

    print("|")
    print("| Defining available tools...")
    tools = get_tool_definition()
    print(f"|")
    print(f"| Tools defined: {[t['name'] for t in tools]}")
    print(f"|")
    print("| Tool schema that will be sent to Claude:")
    print(f"| {tools}")
    print("|")
    print("| [INFO] Claude sees this tool definition and learns when to use it")
    print("|")

    # =========================================================================
    # ADD USER MESSAGE
    # =========================================================================

    logger.separator("ADDING USER MESSAGE TO THE CONVERSATION")

    print(f"| User message: \"{user_message}\"")
    print("|")
    print("| Building the role='user' message structure...")
    print("|")
    print("| messages = [{")
    print("|     'role': 'user',")
    print("|     'content': user_message")
    print("| }]")
    print("|")

    messages.append({
        "role": "user",
        "content": user_message
    })

    print("| [SUCCESS] User message added to conversation history!")
    print("|")
    print(f"| Current messages list has {len(messages)} message(s)")
    print("|")

    # =========================================================================
    # MAIN LOOP
    # =========================================================================

    max_iterations = 10  # Safety limit!
    iteration = 0

    while iteration < max_iterations:
        iteration += 1
        logger.next_iteration()

        # =====================================================================
        # STEP 1: SEND REQUEST TO CLAUDE
        # =====================================================================

        logger.separator("STEP 1: SENDING REQUEST TO CLAUDE API")

        print("| Preparing to call client.messages.create()...")
        print("|")
        print("| Parameters being sent:")
        print("|   - model: 'claude-haiku-4-5-20250601'")
        print(f"│   - max_tokens: 4096")
        print(f"|   - messages: [{len(messages)} message(s) in history]")
        print("|   - tools: [calculator tool]")
        print("|")
        print("| [INFO] This API call goes to Claude's servers")
        print("|        Claude receives: your message + tool definitions")
        print("|        Claude responds with: What it wants to do next")
        print("|")

        print("| Calling API now...")
        print("| v" * 10)

        response = client.messages.create(
            model="claude-haiku-4-5-20250601",
            max_tokens=4096,
            messages=messages,
            tools=tools,
        )

        print("|")
        print("| ^" * 10)
        print("|")
        print("| [SUCCESS] Response received from Claude!")
        print("|")

        # =====================================================================
        # STEP 2: EXAMINE RESPONSE
        # =====================================================================

        logger.separator("STEP 2: EXAMINING CLAUDE'S RESPONSE")

        print("| Claude's response contains:")
        print(f"|   - stop_reason: '{response.stop_reason}'")
        print(f"|   - content blocks: {len(response.content)}")
        print("|")
        print("| Content block types:")
        for i, block in enumerate(response.content):
            print(f"|   Block {i+1}: type='{block.type}'")
        print("|")

        # =====================================================================
        # STEP 3: CHECK STOP REASON
        # =====================================================================

        logger.separator("STEP 3: CHECKING STOP_REASON")

        print("|")
        print("| The stop_reason tells us what Claude decided to do!")
        print("|")
        print("| Possible values:")
        print("|   'tool_use' -> Claude wants to call a tool")
        print("|   'end_turn' -> Claude has the final answer")
        print("|   'max_tokens' -> Hit token limit (unexpected)")
        print("|")
        print(f"| Current stop_reason: '{response.stop_reason}'")
        print("|")

        # =====================================================================
        # ROUTE BASED ON STOP REASON
        # =====================================================================

        if response.stop_reason == "tool_use":
            print("| [DECISION] It's 'tool_use'!")
            print("|            We need to execute tools!")
            print("|")
            print("|            -> Continue to tool execution phase")
            print("|")

            # =================================================================
            # PHASE: TOOL EXECUTION
            # =================================================================

            logger.separator("PHASE: EXECUTING TOOLS")

            print("| Building assistant message with tool calls...")
            print("|")

            # Build assistant message (MUST come before tool_result!)
            assistant_message = {
                "role": "assistant",
                "content": []
            }

            tool_results_to_add = []

            for block in response.content:
                if block.type == "text":
                    print(f"| Found text block: {block.text[:50]}...")
                    assistant_message["content"].append({
                        "type": "text",
                        "text": block.text
                    })

                elif block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    tool_id = block.id

                    print(f"|")
                    print(f"| FOUND TOOL_USE BLOCK!")
                    print(f"|")
                    print(f"| Tool Name: {tool_name}")
                    print(f"| Tool ID: {tool_id}")
                    print(f"| Tool Input: {tool_input}")
                    print(f"|")

                    # This is where YOUR code executes the tool!
                    print("|")
                    print("| CALLING execute_tool_locally()...")
                    print("| This runs the tool on YOUR computer!")
                    print("|")
                    result = execute_tool_locally(tool_name, tool_input, logger)

                    print(f"| Tool returned result: '{result}'")
                    print("|")

                    # Add tool_use block to assistant message
                    assistant_message["content"].append({
                        "type": "tool_use",
                        "id": tool_id,
                        "name": tool_name,
                        "input": tool_input
                    })

                    tool_results_to_add.append({
                        "tool_use_id": tool_id,
                        "content": result
                    })

            # =================================================================
            # ADD MESSAGES TO HISTORY
            # =================================================================

            logger.separator("ADDING TOOL RESULTS TO HISTORY")

            print("|")
            print("| Step 1: Append assistant message ( Claude's tool request )")
            print("|")
            messages.append(assistant_message)
            print("| [SUCCESS] Assistant message added!")
            print(f"| Messages now: {len(messages)} total")
            print("|")

            print("| Step 2: Append tool_result messages")
            print("|")
            for tool_result in tool_results_to_add:
                messages.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": tool_result["tool_use_id"],
                        "content": tool_result["content"]
                    }]
                })
                print(f"| Added: tool_result for {tool_result['tool_use_id']}")
            print("|")
            print("| [SUCCESS] Tool results added!")
            print(f"| Messages now: ")
            for i, msg in enumerate(messages):
                role = msg["role"]
                content_preview = str(msg["content"])[:40]
                print(f"|   [{i}] {role}: {content_preview}...")
            print("|")

            print("|")
            print("| [INFO] Now looping back to Claude with updated conversation")
            print("|")
            print("| V" * 20)
            print("|")
            print("| LOOPING BACK TO STEP 1...")
            print("|")
            continue

        # =====================================================================
        # END TURN - WE HAVE THE ANSWER!
        # =====================================================================

        elif response.stop_reason == "end_turn":
            print("| [DECISION] It's 'end_turn'!")
            print("|            Claude has the final answer!")
            print("|")
            print("|            -> Done looping, return the answer")
            print("|")

            logger.separator("FINAL ANSWER")

            final_response = ""
            for block in response.content:
                if block.type == "text":
                    final_response = block.text
                    break

            print("|")
            print("| Claude's final response:")
            print("|")
            print(f"| {final_response}")
            print("|")
            print("=" * 60)
            print("| AGENTIC LOOP COMPLETE!")
            print("=" * 60)
            print("|")
            print("| Final message count in history:")
            print(f"|   {len(messages)} messages stored")
            print("|")
            print("| These messages are saved and can be used to")
            print("| continue the conversation or resume later!")
            print("|")

            return final_response

        # =====================================================================
        # MAX TOKENS - ERROR CASE
        # =====================================================================

        elif response.stop_reason == "max_tokens":
            print("| [ERROR] Hit max_tokens limit!")
            print("|          Something went wrong or the response is too long")
            print("|")
            return "Error: Hit token limit"


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Fix stdout encoding for Windows
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("\n" + "=" * 70)
    print("FLOW LOGGER: COMPLETE AGENTIC LOOP EXECUTION TRACKER")
    print("=" * 70)
    print("""
This program demonstrates the COMPLETE flow of an agentic loop
with detailed step-by-step logging at every stage.

You'll see:
- How messages are built and sent to Claude
- What Claude responds with
- How stop_reason determines the next action
- When and how tools are executed (ON YOUR MACHINE!)
- How results flow back to Claude for final answer
    """)

    print("\n" + "=" * 70)
    print("STARTING THE LOGGED AGENTIC LOOP")
    print("=" * 70)

    # Simple math question that requires the calculator tool
    user_input = "What is 1500 + 2500? Please use the calculator tool."

    print(f"\n>>> User asking: \"{user_input}\"")
    print("\n>>> Watch the flow below!\n")

    result = run_logged_agentic_loop(user_input)

    print("\n" + "=" * 70)
    print("EXECUTION COMPLETE!")
    print("=" * 70)
    print(f"""
RESULT: {result}

WHAT HAPPENED STEP BY STEP:
1. User message sent to Claude with tool definition
2. Claude analyzed the request and said "tool_use"
3. Your code executed the calculator on YOUR machine
4. Result sent back to Claude
5. Claude synthesized the final answer
6. Claude said "end_turn" - loop complete!

KEY TAKEAWAY:
- Claude decides WHAT tool to use
- YOUR CODE executes the tool on YOUR machine
- Results are sent back to Claude for reasoning
    """)

    print("\n" + "=" * 70)
    print("WHAT WE HAVE LEARNT FROM THIS FLOW LOGGER:")
    print("=" * 70)
    print("""
+======================================================================+
|                                                                      |
|  1. FLOW IS CONSISTENT:                                              |
|     User message -> Claude analyzes -> stop_reason determines path  |
|                                                                      |
|  2. TOOL EXECUTION IS LOCAL:                                        |
|     execute_tool_locally() runs on YOUR machine, not Claude's cloud |
|     Claude only RECEIVES the result of what YOU executed            |
|                                                                      |
|  3. MESSAGE HANDLING MATTERS:                                       |
|     - Add assistant message BEFORE tool_result                       |
|     - Include tool_use_id to match results to calls                 |
|     - Return STRING from tool, not other types                       |
|                                                                      |
|  4. LOOP CONTINUES UNTIL end_turn:                                  |
|     - tool_use = execute tools, loop back                           |
|     - end_turn = return final answer                                 |
|                                                                      |
+======================================================================+
""")


"""
+===========================================================================+
|                                                                           |
|  EXECUTION FLOW SUMMARY:                                                 |
|                                                                           |
|  Your Computer                          Claude Cloud                      |
|  =============                          ===========    |
|                                                                           |
|  [1] Build messages list                                                  |
|      |                                    |                                |
|      | messages.create()                  |                                |
|      v                                    v                                |
|  [2] Send to Claude API  ----------------->  Claude receives              |
|                                             - user message |
|                                             - tool definitions |
|                                             (Claude learns when to use tools) |
|                                                                           |
|  [3] Claude analyzes request                                              |
|      - Checks if tools needed     |
|      - Decides: tool_use or end_turn |
|                                                                           |
|      |                                                               |
|      v                                                               |
|  [4] Claude responds with stop_reason                                    |
|      <----------------- Response with stop_reason + content |
|                                                                           |
|  [5a] If tool_use:                                                        |
|       - Find tool in response.content |
|       - YOUR CODE executes it HERE |  |
|       - Return result as string  |
|       - Add to messages  |
|       - Loop back to step [2]        |
|                                                                           |
|  [5b] If end_turn:                                                       |
|       - Handled content to user     |
|       - Done!                     (No loop back)           |
|                                                                           |
|  KEY INSIGHT: Claude is the REASONING engine. YOU are the EXECUTION engine.|
|                                                                           |
+===========================================================================+
"""