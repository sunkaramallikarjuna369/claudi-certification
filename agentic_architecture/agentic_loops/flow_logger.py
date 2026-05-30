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
|  TEACHING MODE: Sleep timers added for student comprehension            |
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

if not API_KEY:
    raise ValueError("ANTHROPIC_API_KEY not found in .env file")


from anthropic import Anthropic

client = Anthropic(api_key=API_KEY)


# ============================================================================
# CONFIGURATION - Teaching Mode Settings
# ============================================================================

TEACHING_MODE = True  # Set to False for faster execution

def pause(seconds: float = 1.5, message: str = ""):
    """Pause execution for student comprehension."""
    if TEACHING_MODE:
        print()
        if message:
            print(f"    [PAUSE] {message}")
        time.sleep(seconds)


def section_pause():
    """Longer pause between major sections."""
    if TEACHING_MODE:
        time.sleep(2.0)


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
        pause(1.0, f"Step {self.step} complete")

    def next_iteration(self):
        """Start the next iteration."""
        self.iteration += 1
        print(f"\n\n{'#'*70}")
        print(f"# ITERATION {self.iteration}")
        print(f"#{'#'*70}\n")
        pause(1.5, f"Starting iteration {self.iteration}")

    def separator(self, title: str = ""):
        """Print a separator with optional title."""
        print(f"\n{'~'*60}")
        if title:
            print(f"~ {title}")
            print(f"~{'~'*59}")
        pause(0.8, "Moving to next phase")


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

    IMPORTANT CONCEPT FOR STUDENTS:
    --------------------------------
    Claude is a REASONING engine, not an EXECUTION engine.
    Claude decides WHAT tool to use, but YOUR CODE actually RUNS it.

    Think of it like this:
    - Claude = The architect who designs the plan
    - Your code = The construction workers who execute the plan
    """
    logger.separator("TOOL EXECUTION ON YOUR LOCAL MACHINE")
    print(f"|")
    print(f"| ============================================================")
    print(f"| TEACHER NOTE: This is where YOUR code executes the tool!")
    print(f"| ============================================================")
    print(f"|")
    print(f"| REMEMBER: Tools execute on YOUR machine, NOT Claude's cloud!")
    print(f"|")
    pause(2.0, "Understanding tool execution location")
    print(f"|")
    print(f"| Tool that was requested: {tool_name}")
    print(f"| Parameters (input) passed: {tool_input}")
    print(f"|")
    pause(1.0, "Analyzing tool request")

    result = None
    if tool_name == "calculator":
        expression = tool_input.get("expression", "")
        print(f"|")
        print(f"| Evaluating mathematical expression: {expression}")
        print(f"|")
        pause(1.5, "Computing the result")

        try:
            result = eval(expression)
            print(f"|")
            print(f"| ===============================================")
            print(f"| COMPUTATION COMPLETE!")
            print(f"| Result: {result}")
            print(f"| Result type: {type(result).__name__}")
            print(f"| ===============================================")
            print(f"|")
        except Exception as e:
            result = f"Error: {e}"
            print(f"| ERROR occurred: {e}")

    pause(1.0, "Tool execution finished")
    print(f"|")
    print(f"| Tool executor complete! Returning result to agentic loop...")
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

    logger.separator("PHASE 0: INITIALIZATION")

    print("|")
    print("| STUDENT GUIDE: What happens in this phase?")
    print("| - We set up our Python environment")
    print("| - Create an empty messages list to store conversation")
    print("| - Define the tools we want Claude to be able to use")
    print("|")
    pause(2.0, "Understanding initialization")

    print("|")
    print("| Step 1: Creating empty messages list...")
    print("|")
    print("|     messages = []")
    print("|")
    messages = []
    pause(1.0, "Empty messages list created")

    print("|")
    print("| Step 2: Defining available tools...")
    print("|")
    print("|     This tells Claude what tools exist and when to use them")
    print("|")
    tools = get_tool_definition()
    print(f"| Tools defined: {[t['name'] for t in tools]}")
    print(f"|")
    pause(1.5, "Tool definitions ready")

    print("| Tool schema that will be sent to Claude:")
    print(f"|")
    print(f"| {tools}")
    print("|")
    print("| [INFO] Claude sees this tool definition and learns when to use it")
    print("|")
    pause(1.0, "Understanding tool schema")

    # =========================================================================
    # ADD USER MESSAGE
    # =========================================================================

    logger.separator("PHASE 1: ADDING USER MESSAGE")

    print("|")
    print("| STUDENT GUIDE: What happens in this phase?")
    print("| - User sends a message (like 'What is 1500 + 2500?')")
    print("| - We wrap it in a 'user' role message structure")
    print("| - Add it to our messages list")
    print("|")
    pause(2.0, "Understanding user message handling")

    print(f"| User message: \"{user_message}\"")
    print("|")
    print("| Step 1: Building the role='user' message structure...")
    print("|")
    print("|     messages.append({")
    print("|         'role': 'user',")
    print("|         'content': user_message")
    print("|     })")
    print("|")
    pause(1.0, "Building user message structure")

    messages.append({
        "role": "user",
        "content": user_message
    })

    print("|")
    print("| [SUCCESS] User message added to conversation history!")
    print("|")
    print(f"| Current messages list has {len(messages)} message(s)")
    print("|")
    print("|")
    print("| TEACHER NOTE: The messages list now contains:")
    print("|     messages = [")
    print("|         {'role': 'user', 'content': 'What is 1500 + 2500?...'}")
    print("|     ]")
    print("|")
    pause(1.5, "User message added to history")

    # =========================================================================
    # MAIN LOOP
    # =========================================================================

    section_pause()
    print("=" * 70)
    print("STARTING THE MAIN AGENTIC LOOP")
    print("=" * 70)
    print("""
| This is where the magic happens!
| The loop will continue until Claude says it's done (end_turn)
|""")
    pause(2.0, "Starting main loop")

    max_iterations = 10  # Safety limit!
    iteration = 0

    while iteration < max_iterations:
        iteration += 1
        logger.next_iteration()

        # =====================================================================
        # STEP 1: SEND REQUEST TO CLAUDE
        # =====================================================================

        logger.separator("STEP 1: SENDING REQUEST TO CLAUDE API")

        print("|")
        print("| STUDENT GUIDE:")
        print("| - This is where we send our messages to Claude")
        print("| - We include the tool definitions so Claude knows what it can use")
        print("| - Claude will analyze and respond with what it wants to do")
        print("|")
        pause(2.5, "Understanding API request")

        print("| Preparing to call client.messages.create()...")
        print("|")
        print("| Parameters being sent:")
        print("|   - model: 'claude-haiku-4-5-20250601'")
        print(f"|   - max_tokens: 4096")
        print(f"|   - messages: [{len(messages)} message(s) in history]")
        print("|   - tools: [calculator tool]")
        print("|")
        pause(1.0, "Reviewing API parameters")

        print("|")
        print("| VISUAL: What's happening now?")
        print("|")
        print("|    Your Computer                          Claude Cloud")
        print("|    =============                          ===========")
        print("|")
        print("|    messages.create() --------->  Claude receives request")
        print("|                                     - user message")
        print("|                                     - tool definitions")
        print("|                                     (Claude learns about tools)")
        print("|")
        print("|")
        pause(2.0, "Visualizing the API call")

        print("|")
        print("| [API CALL] Sending request to Claude...")
        print("|")
        print("|     v" * 15)
        print("|")
        pause(1.0, "Making API call")

        response = client.messages.create(
            model="claude-haiku-4-5-20250601",
            max_tokens=4096,
            messages=messages,
            tools=tools,
        )

        print("|")
        print("|     ^" * 15)
        print("|")
        print("| [SUCCESS] Response received from Claude!")
        print("|")
        pause(1.5, "API response received")

        # =====================================================================
        # STEP 2: EXAMINE RESPONSE
        # =====================================================================

        logger.separator("STEP 2: EXAMINING CLAUDE'S RESPONSE")

        print("|")
        print("| STUDENT GUIDE:")
        print("| - Claude's response contains important information")
        print("| - 'stop_reason' tells us what Claude decided to do")
        print("| - 'content' contains Claude's message and any tool calls")
        print("|")
        pause(2.0, "Understanding response structure")

        print("| Claude's response contains:")
        print(f"|   - stop_reason: '{response.stop_reason}'")
        print(f"|   - content blocks: {len(response.content)}")
        print("|")
        print("| Content block types:")
        for i, block in enumerate(response.content):
            print(f"|   Block {i+1}: type='{block.type}'")
            if hasattr(block, 'text'):
                print(f"|           text: {block.text[:50]}...")
            if hasattr(block, 'name'):
                print(f"|           tool_name: {block.name}")
        print("|")
        pause(1.5, "Response analysis complete")

        # =====================================================================
        # STEP 3: CHECK STOP REASON
        # =====================================================================

        logger.separator("STEP 3: CHECKING STOP_REASON")

        print("|")
        print("| ===============================================")
        print("| CRITICAL CONCEPT - STOP_REASON!")
        print("| ===============================================")
        print("|")
        print("| The stop_reason tells us what Claude decided to do!")
        print("|")
        pause(2.0, "Understanding stop_reason importance")
        print("| Possible values:")
        print("|")
        print("|   'tool_use' -> Claude wants to call a tool")
        print("|               -> We execute the tool, then loop back")
        print("|")
        pause(1.0, "Learning about tool_use")
        print("|   'end_turn' -> Claude has the final answer!")
        print("|               -> We're done! Return answer to user")
        print("|")
        pause(1.0, "Learning about end_turn")
        print("|   'max_tokens' -> Hit token limit (unexpected)")
        print("|")
        pause(1.0, "Learning about max_tokens")
        print(f"|")
        print("| ===============================================")
        print(f"| Current stop_reason: '{response.stop_reason}'")
        print("| ===============================================")
        print("|")
        pause(2.0, f"Current stop_reason is: {response.stop_reason}")

        # =====================================================================
        # ROUTE BASED ON STOP REASON
        # =====================================================================

        if response.stop_reason == "tool_use":
            print("|")
            print("| ===============================================")
            print("| DECISION: stop_reason = 'tool_use'")
            print("| ===============================================")
            print("|")
            print("| Claude wants to use a tool!")
            print("|")
            print("| Next steps:")
            print("|   1. Find which tool(s) Claude wants to call")
            print("|   2. Execute those tools on YOUR machine")
            print("|   3. Send results back to Claude")
            print("|   4. Loop back for Claude's next decision")
            print("|")
            pause(2.5, "Understanding tool_use decision")

            # =================================================================
            # PHASE: TOOL EXECUTION
            # =================================================================

            logger.separator("PHASE: TOOL EXECUTION")

            print("|")
            print("| STUDENT GUIDE:")
            print("| - We extract tool calls from Claude's response")
            print("| - Build an 'assistant' message with those tool calls")
            print("| - Execute the tools (THIS HAPPENS ON YOUR MACHINE!)")
            print("| - Add tool results to messages")
            print("| - Loop back to send results to Claude")
            print("|")
            pause(2.5, "Understanding tool execution flow")

            print("| Building assistant message with tool calls...")
            print("|")
            pause(1.0, "Building assistant message")

            # Build assistant message (MUST come before tool_result!)
            assistant_message = {
                "role": "assistant",
                "content": []
            }

            tool_results_to_add = []

            for block in response.content:
                if block.type == "text":
                    print(f"| Found text block from Claude: {block.text[:50]}...")
                    assistant_message["content"].append({
                        "type": "text",
                        "text": block.text
                    })
                    pause(0.5, "Adding text to assistant message")

                elif block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    tool_id = block.id

                    print(f"|")
                    print(f"| ===============================================")
                    print(f"| FOUND TOOL_USE BLOCK!")
                    print(f"| ===============================================")
                    print(f"|")
                    print(f"| Tool Name: {tool_name}")
                    print(f"| Tool ID: {tool_id}")
                    print(f"| Tool Input: {tool_input}")
                    print(f"|")
                    pause(1.5, "Found tool call details")

                    # THIS IS THE KEY PART - Tool execution happens HERE!
                    print("|")
                    print("| [CALLING TOOL EXECUTOR]...")
                    print("|")
                    print("| Remember: execute_tool_locally() runs on YOUR computer!")
                    print("| Claude doesn't execute tools - YOUR CODE does!")
                    print("|")
                    pause(2.0, "Important: tools execute locally!")

                    result = execute_tool_locally(tool_name, tool_input, logger)

                    print(f"|")
                    print(f"| Tool returned result: '{result}'")
                    print("|")
                    pause(1.0, "Tool execution complete")

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

            logger.separator("ADDING RESULTS TO MESSAGES")

            print("|")
            print("| STUDENT GUIDE:")
            print("| - We must add messages in the CORRECT order:")
            print("|   1. Assistant message (Claude's tool request)")
            print("|   2. User message with tool_result (the execution result)")
            print("|")
            pause(2.0, "Understanding message order")

            print("|")
            print("| Step 1: Append assistant message")
            print("|         This represents what Claude said/request")
            print("|")
            messages.append(assistant_message)
            print("| [SUCCESS] Assistant message added!")
            print(f"| Messages now: {len(messages)} total")
            print("|")
            pause(1.0, "Assistant message added")

            print("| Step 2: Append tool_result message")
            print("|         This contains the result of our tool execution")
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
            print(f"|")
            pause(1.0, "Tool results added")

            print("|")
            print("| Current messages list:")
            for i, msg in enumerate(messages):
                role = msg["role"]
                content = msg["content"]
                if isinstance(content, list):
                    types = [c.get('type', 'unknown') for c in content]
                    content_str = str(types)
                else:
                    content_str = str(content)[:40]
                print(f"|   [{i}] {role}: {content_str}")
            print("|")
            pause(1.5, "Reviewing updated messages")

            print("|")
            print("| ===============================================")
            print("| LOOPING BACK TO CLAUDE")
            print("| ===============================================")
            print("|")
            print("| VISUAL: The loop continues!")
            print("|")
            print("|    Tool executed locally")
            print("|          |")
            print("|          v")
            print("|    Results added to messages")
            print("|          |")
            print("|          v")
            print("|    messages.create() called again")
            print("|          |")
            print("|          v")
            print("|    Back to STEP 1 (Claude analyzes again)")
            print("|")
            pause(2.5, "Understanding loop continuation")

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
            print("|")
            print("| ===============================================")
            print("| DECISION: stop_reason = 'end_turn'")
            print("| ===============================================")
            print("|")
            print("| Claude has the final answer!")
            print("|")
            print("| The agentic loop is COMPLETE!")
            print("|")
            pause(2.5, "Understanding end_turn")

            logger.separator("PHASE: FINAL ANSWER")

            print("|")
            print("| STUDENT GUIDE:")
            print("| - stop_reason = 'end_turn' means Claude is done thinking")
            print("| - No more tool calls needed")
            print("| - We can extract the final text response and return it")
            print("|")
            pause(2.0, "Understanding final answer extraction")

            final_response = ""
            for block in response.content:
                if block.type == "text":
                    final_response = block.text
                    break

            print("|")
            print("| ===============================================")
            print("| CLAUDE'S FINAL ANSWER:")
            print("| ===============================================")
            print("|")
            print(f"| {final_response}")
            print("|")
            print("| ===============================================")
            print("|")
            pause(2.0, "Viewing final answer")

            print("|")
            print("| AGENTIC LOOP COMPLETE!")
            print("|")
            print(f"| Final message count in history: {len(messages)}")
            print("|")
            print("| These messages are saved and can be used to")
            print("| continue the conversation or resume later!")
            print("|")
            pause(1.5, "Loop complete")

            return final_response

        # =====================================================================
        # MAX TOKENS - ERROR CASE
        # =====================================================================

        elif response.stop_reason == "max_tokens":
            print("|")
            print("| [ERROR] Hit max_tokens limit!")
            print("|          This means the response was too long")
            print("|          or something unexpected happened")
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
| TEACHING MODE: This program demonstrates the complete flow of an
| agentic loop with step-by-step logging and pauses for comprehension.
|
| You'll see:
| - How messages are built and sent to Claude
| - What Claude responds with at each step
| - How stop_reason determines the next action
| - When and how tools are executed (ON YOUR MACHINE!)
| - How results flow back to Claude for final answer
|
| WATCH CAREFULLY - Each section will pause for you to read and understand!
    """)

    pause(3.0, "Starting soon...")

    print("\n" + "=" * 70)
    print("STARTING THE LOGGED AGENTIC LOOP")
    print("=" * 70)

    # Simple math question that requires the calculator tool
    user_input = "What is 1500 + 2500? Please use the calculator tool."

    print(f"\n>>> STUDENT: User asking: \"{user_input}\"")
    print("\n>>> Watch the flow below and read each explanation carefully!\n")

    pause(2.0, "Starting the demonstration")

    result = run_logged_agentic_loop(user_input)

    section_pause()

    print("\n" + "=" * 70)
    print("EXECUTION COMPLETE - SUMMARY")
    print("=" * 70)

    print(f"""
| FINAL RESULT: {result}

| WHAT HAPPENED STEP BY STEP:
| ==========================================================================
| STEP 0: INITIALIZATION
|   - Created empty messages list
|   - Defined tools (calculator)
|
| STEP 1: ADDED USER MESSAGE
|   - Wrapped user input in 'user' role message
|   - Added to messages list
|
| STEP 2: SENT REQUEST TO CLAUDE API
|   - Called messages.create() with messages + tools
|   - Claude received and analyzed the request
|
| STEP 3: RECEIVED RESPONSE
|   - Claude said: 'tool_use' (wants to use calculator)
|   - Extracted tool call from response
|
| STEP 4: EXECUTED TOOL LOCALLY
|   - Your code evaluated: 1500 + 2500
|   - Result: 4000
|
| STEP 5: SENT RESULTS BACK TO CLAUDE
|   - Added assistant message + tool_result to messages
|   - Called messages.create() again
|
| STEP 6: RECEIVED FINAL ANSWER
|   - Claude said: 'end_turn' (done thinking)
|   - Extracted final text response
|   - AGENTIC LOOP COMPLETE!
| ==========================================================================

| KEY TAKEAWAYS:
| ==========================================================================
| 1. Claude is the REASONING engine - it decides WHAT to do
| 2. YOUR CODE is the EXECUTION engine - it actually DOES things
| 3. The loop continues until stop_reason = 'end_turn'
| 4. Messages must be added in correct order: assistant BEFORE tool_result
| ==========================================================================
    """)

    pause(3.0, "Review complete summary")

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

    print("""
| TEACHING MODE COMPLETE!
| ==========================================================================
| To disable pauses, set TEACHING_MODE = False at the top of the file.
| ==========================================================================
    """)


"""
+===========================================================================+
|                                                                           |
|  EXECUTION FLOW SUMMARY - VISUAL CHEAT SHEET:                          |
|                                                                           |
+===========================================================================+

    Your Computer                          Claude Cloud
    =============                          ===========

    [1] Build messages list
        |
        v
    [2] messages.create() ----------------->  Claude receives
        |                                     - user message
        |                                     - tool definitions
        v                                     (Claude learns tools)
    [3] Claude analyzes
        |    |
        |    +-- tool_use? --> [4] Execute tool locally
        |    |                    |
        |    |                    v
        |    |                Add result to messages
        |    |                    |
        |    +---- Loop back to [2] ----+
        |
        +-- end_turn? --> [5] Return answer to user

    KEY INSIGHT: Claude is the REASONING engine. YOU are the EXECUTION engine.

+===========================================================================+
"""