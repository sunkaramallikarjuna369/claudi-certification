"""
+===========================================================================+
|                                                                           |
|  FLOW_LOGGER: Complete Agentic Loop Execution Tracker                   |
|                                                                           |
|  TEACHING MODE with INTERACTIVE CONTROLS                                 |
|                                                                           |
|  Press ENTER after each phase to continue (or auto-continue mode)        |
|  Perfect for explaining the complete flow to students step-by-step!      |
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
|                                                                          |
|  1. Create a file named ".env" in the project root                       |
|  2. Add this line:                                                       |
|     ANTHROPIC_API_KEY=sk-ant-your-key-here                              |
|                                                                          |
|  To get your API key:                                                   |
|  - Go to https://console.anthropic.com/                                 |
|  - Sign up/log in                                                        |
|  - Go to API Keys section                                                |
|  - Create a new key                                                      |
|                                                                          |
+==========================================================================+
    """)

# Import after env check
from anthropic import Anthropic

# Create client with proper configuration
client_kwargs = {"api_key": API_KEY}
if API_BASE:
    client_kwargs["base_url"] = API_BASE

client = Anthropic(**client_kwargs)


# ============================================================================
# CONFIGURATION - Teaching Mode with Controls
# ============================================================================

INTERACTIVE_MODE = True  # True = wait for keypress, False = auto continue
AUTO_DELAY = 0.5  # Delay in auto mode (seconds)

def wait_for_input(prompt: str = ""):
    """
    Wait for user to press ENTER to continue.
    In auto mode (INTERACTIVE_MODE=False), auto-continues after delay.
    """
    if INTERACTIVE_MODE:
        input(f"\n>>> PRESS ENTER to continue {prompt}...")
    else:
        print(f"\n>>> Auto-continuing in {AUTO_DELAY}s... (INTERACTIVE_MODE=False)")
        time.sleep(AUTO_DELAY)


def print_progress_bar(current: int, total: int, label: str = ""):
    """Print a progress bar showing current phase."""
    bar_length = 30
    filled = int(bar_length * current / total)
    bar = "=" * filled + "-" * (bar_length - filled)
    percent = int(100 * current / total)
    print(f"\n[{bar}] {percent}% {label}")


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

def execute_tool_locally(tool_name: str, tool_input: dict) -> str:
    """
    EXECUTES THE TOOL ON YOUR LOCAL MACHINE!

    CRITICAL CONCEPT FOR STUDENTS:
    - Claude is a REASONING engine (thinks about what to do)
    - Your code is an EXECUTION engine (actually does things)
    - The two work TOGETHER in the agentic loop
    """

    print()
    print("| " + "=" * 60)
    print("| IMPORTANT CONCEPT FOR STUDENTS!")
    print("| " + "=" * 60)
    print("|")
    print("| REMEMBER:")
    print("|   Claude decides WHAT tool to use")
    print("|   YOUR CODE actually RUNS the tool")
    print("|")
    print("| This is security by design!")
    print("| Claude can't execute arbitrary code directly.")
    print("| Only your code can execute things on your machine.")
    print("|")

    wait_for_input("(Understanding tool execution)")

    print("|")
    print(f"| Tool requested: {tool_name}")
    print(f"| Parameters: {tool_input}")
    print("|")

    result = None
    if tool_name == "calculator":
        expression = tool_input.get("expression", "")
        print(f"|")
        print(f"| Evaluating: {expression}")
        print("|")

        wait_for_input("(Computing result)")

        try:
            result = eval(expression)
            print("| " + "-" * 50)
            print(f"| RESULT: {result}")
            print("| " + "-" * 50)
            print("|")
        except Exception as e:
            result = f"Error: {e}"
            print(f"| ERROR: {e}")

    wait_for_input("(Execution complete)")

    return str(result)


# ============================================================================
# COMPLETE AGENTIC LOOP with Interactive Teaching
# ============================================================================

# Phase counter for display
phase_counter = {"current": 0, "total": 9}
phase_names = [
    "INITIALIZATION",
    "USER_MESSAGE",
    "API_REQUEST",
    "API_RESPONSE",
    "STOP_REASON",
    "TOOL_EXECUTION",
    "MESSAGE_UPDATE",
    "LOOP_BACK",
    "FINAL_ANSWER"
]

def show_phase_header(phase_num, phase_name, explanation=""):
    """Show phase header with progress bar."""
    phase_counter["current"] = phase_num
    print(f"\n\n{'#'*70}")
    print(f"# PHASE {phase_num}/{phase_counter['total']}: {phase_name}")
    print(f"#{'#'*70}")
    if explanation:
        print(f"\n  {explanation}")
    print_progress_bar(phase_num, phase_counter["total"], phase_name)
    wait_for_input(f"(Phase {phase_num}: {phase_name})")


def run_interactive_agentic_loop(user_message: str):
    """
    Run the agentic loop with INTERACTIVE PHASE CONTROLS.
    Perfect for teaching - press ENTER after each phase to continue.
    """

    # =========================================================================
    # PHASE 1: INITIALIZATION
    # =========================================================================

    show_phase_header(1, "INITIALIZATION",
        "Setting up the Python environment, creating messages list, defining tools"
    )

    print("| Step 1: Creating empty messages list...")
    print("|")
    print("|     messages = []")
    print("|")

    messages = []
    print("| [SUCCESS] Empty list created")
    print("|")

    wait_for_input("(Messages list ready)")

    print("|")
    print("| Step 2: Defining available tools...")
    print("|")
    tools = get_tool_definition()
    print(f"| Tool defined: {[t['name'] for t in tools]}")
    print("|")

    print("| Tool schema (what Claude will see):")
    print(f"| {tools}")
    print("|")

    print("| " + "-" * 50)
    print("| TEACHER NOTE:")
    print("| - Tool schema tells Claude WHAT tools exist")
    print("| - Also tells Claude WHEN to use each tool")
    print("| - Claude learns from this schema automatically")
    print("| " + "-" * 50)
    print("|")

    # =========================================================================
    # PHASE 2: ADD USER MESSAGE
    # =========================================================================

    show_phase_header(2, "USER_MESSAGE",
        "Wrapping user input in message structure and adding to history"
    )

    print(f"| User message: \"{user_message}\"")
    print("|")

    print("| Building user message...")
    print("|")
    print("|     messages.append({")
    print("|         'role': 'user',")
    print("|         'content': user_message")
    print("|     })")
    print("|")

    messages.append({
        "role": "user",
        "content": user_message
    })

    print("| [SUCCESS] Message added!")
    print(f"| Messages list now has {len(messages)} message(s)")
    print("|")

    print("| " + "-" * 50)
    print("| TEACHER NOTE:")
    print("| - All messages must have a 'role' (user/assistant)")
    print("| - Content can be text or include tool calls/results")
    print("| - This creates the conversation history")
    print("| " + "-" * 50)
    print("|")

    # =========================================================================
    # MAIN LOOP - Starts here
    # =========================================================================

    iteration_count = 0
    max_iterations = 10
    assistant_message = None
    tool_results_to_add = None

    while iteration_count < max_iterations:
        iteration_count += 1

        print(f"\n\n{'='*70}")
        print(f"= ITERATION {iteration_count} - API COMMUNICATION")
        print(f"{'='*70}")
        wait_for_input(f"(Starting iteration {iteration_count})")

        # =====================================================================
        # PHASE 3: API REQUEST
        # =====================================================================

        show_phase_header(3, "API_REQUEST",
            "Sending request to Claude with messages and tool definitions"
        )

        print("| Preparing API call to Claude...")
        print("|")

        print("| Parameters being sent to Claude API:")
        print("|   " + "-" * 40)
        print("|   - model: 'claude-haiku-4-5-20250601'")
        print("|   - max_tokens: 4096")
        print(f"|   - messages: {len(messages)} message(s)")
        print("|   - tools: calculator")
        print("|   " + "-" * 40)
        print("|")

        print("| VISUAL - What's happening:")
        print("|")
        print("|    Your Computer          --->    Claude Cloud")
        print("|    [Python Script]                [Claude AI]")
        print("|    |")
        print("|    | messages.create()")
        print("|    | (with messages + tools)")
        print("|    v")
        print("| ==============================================>")
        print("|")
        print("| Claude receives:")
        print("|   1. User's question")
        print("|   2. Tool definitions (what tools exist)")
        print("|")

        wait_for_input("(Visualizing the API flow)")

        print("|")
        print("| [API CALL] Calling messages.create()...")
        print("|")
        print("|     |")
        print("|     v")
        print("|     Sending to Claude...")
        print("|")

        response = client.messages.create(
            model="claude-haiku-4-5-20250601",
            max_tokens=4096,
            messages=messages,
            tools=tools,
        )

        print("|")
        print("|     ^")
        print("|     |")
        print("| [SUCCESS] Response received!")
        print("|")

        # =====================================================================
        # PHASE 4: API RESPONSE
        # =====================================================================

        show_phase_header(4, "API_RESPONSE",
            "Analyzing Claude's response structure"
        )

        print("| Claude's response contains:")
        print("|")
        print("|   " + "-" * 40)
        print(f"|   stop_reason: '{response.stop_reason}'")
        print(f"|   content: {len(response.content)} block(s)")
        print("|   " + "-" * 40)
        print("|")

        print("| Content blocks in response:")
        for i, block in enumerate(response.content):
            print(f"|   Block {i+1}: type='{block.type}'")
            if hasattr(block, 'text') and block.text:
                text_preview = block.text[:50] + "..." if len(block.text) > 50 else block.text
                print(f"|             text: '{text_preview}'")
            if hasattr(block, 'name'):
                print(f"|             tool: {block.name}")
        print("|")

        print("| " + "-" * 50)
        print("| TEACHER NOTE:")
        print("| - response.content is a LIST of blocks")
        print("| - Each block can be 'text' or 'tool_use'")
        print("| - Multiple tool calls can happen in one response!")
        print("| " + "-" * 50)
        print("|")

        # =====================================================================
        # PHASE 5: STOP REASON
        # =====================================================================

        show_phase_header(5, "STOP_REASON",
            "Checking what Claude decided to do (tool_use or end_turn)"
        )

        print("| " + "=" * 50)
        print("| CRITICAL CONCEPT: stop_reason!")
        print("| " + "=" * 50)
        print("|")
        print("| stop_reason tells us WHAT CLAUDE DECIDED TO DO!")
        print("|")
        print("| Possible values:")
        print("|")
        print("|   'tool_use'  -> Claude wants to call a tool")
        print("|                 -> We must execute tools and loop back")
        print("|")
        print("|   'end_turn'  -> Claude has final answer")
        print("|                 -> We're done! Return the answer")
        print("|")
        print("|   'max_tokens' -> Hit token limit (unexpected)")
        print("|")

        wait_for_input("(Understanding stop_reason)")

        print("|")
        print("| " + "-" * 50)
        print(f"| Current value: stop_reason = '{response.stop_reason}'")
        print("| " + "-" * 50)
        print("|")

        if response.stop_reason == "tool_use":
            print("| [DECISION] Claude wants to use a tool!")
            print("|")
            print("| Next steps: Execute tool -> Add result -> Loop back")
            print("|")

        elif response.stop_reason == "end_turn":
            print("| [DECISION] Claude has the final answer!")
            print("|")
            print("| Agentic loop complete!")
            print("|")

        # Store for later use
        current_stop_reason = response.stop_reason

        # =====================================================================
        # PHASE 6: TOOL EXECUTION (if tool_use)
        # =====================================================================

        if current_stop_reason == "tool_use":

            show_phase_header(6, "TOOL_EXECUTION",
                "Executing tool on LOCAL machine (NOT Claude's cloud!)"
            )

            print("|")
            print("| Searching for tool_use blocks in response...")
            print("|")

            assistant_message = {
                "role": "assistant",
                "content": []
            }

            tool_results_to_add = []

            for block in response.content:
                if block.type == "text":
                    print(f"| Found text: {block.text[:50]}...")
                    assistant_message["content"].append({
                        "type": "text",
                        "text": block.text
                    })

                elif block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    tool_id = block.id

                    print(f"|")
                    print("| " + "=" * 50)
                    print("| FOUND TOOL CALL!")
                    print("| " + "=" * 50)
                    print(f"|")
                    print(f"|   Tool Name: {tool_name}")
                    print(f"|   Tool ID: {tool_id}")
                    print(f"|   Input: {tool_input}")
                    print("|")

                    wait_for_input("(Tool call details)")

                    # Execute the tool
                    result = execute_tool_locally(tool_name, tool_input)

                    print("|")
                    print(f"| Result returned: '{result}'")
                    print("|")

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

            # =====================================================================
            # PHASE 7: MESSAGE UPDATE
            # =====================================================================

            show_phase_header(7, "MESSAGE_UPDATE",
                "Adding assistant message and tool result to conversation history"
            )

            print("|")
            print("| Adding messages in CORRECT ORDER:")
            print("|")

            print("| Step 1: Append ASSISTANT message (Claude's tool request)")
            print("|")
            messages.append(assistant_message)
            print("| [SUCCESS] Added!")
            print(f"| Total messages now: {len(messages)}")
            print("|")

            wait_for_input("(Assistant message added)")

            print("|")
            print("| Step 2: Append USER message with tool_result")
            print("|         (This is the RESULT of our tool execution)")
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
            print("| [SUCCESS] Tool result added!")
            print(f"| Total messages now: {len(messages)}")
            print("|")

            print("| " + "-" * 50)
            print("| TEACHER NOTE - MESSAGE ORDER MATTERS!")
            print("| " + "-" * 50)
            print("|")
            print("| The messages we just added:")
            for i, msg in enumerate(messages[-2:], start=len(messages)-1):
                role = msg["role"]
                content_preview = str(msg["content"])[:50]
                print(f"|   [{i}] {role}: {content_preview}...")
            print("|")
            print("| 1. ASSISTANT message says 'I'm calling the calculator'")
            print("| 2. USER message says 'The result was 4000'")
            print("|")
            print("| This is how Claude knows the tool was executed!")
            print("|")

            # =====================================================================
            # PHASE 8: LOOP BACK
            # =====================================================================

            show_phase_header(8, "LOOP_BACK",
                "Sending updated messages back to Claude for continuation"
            )

            print("|")
            print("| THE LOOP CONTINUES!")
            print("|")
            print("| " + "-" * 50)
            print("| What happens next:")
            print("| " + "-" * 50)
            print("|")
            print("|   1. We call messages.create() AGAIN")
            print("|   2. Now with the UPDATED messages list")
            print("|      (includes original question + tool call + result)")
            print("|   3. Claude will analyze the UPDATED context")
            print("|   4. Claude decides: more tools needed? or done?")
            print("|")
            print("| VISUAL - The Loop:")
            print("|")
            print("|   [State before loop]")
            print("|        |")
            print("|        v")
            print("|   messages.create() -----> Claude")
            print("|        |")
            print("|        <----- Response (with updated history)")
            print("|        |")
            print("|   [Claude knows tool executed]")
            print("|        |")
            print("|        v")
            print("|   stop_reason checked again...")
            print("|")

            wait_for_input("(Loop pattern explained)")

            print("|")
            print("| V" * 20)
            print("|")
            print(f"| Looping back to ITERATION {iteration_count + 1}...")
            print("|")

            # Continue the loop - go back to while
            continue

        # =====================================================================
        # PHASE 9: FINAL ANSWER (if end_turn)
        # =====================================================================

        elif current_stop_reason == "end_turn":

            show_phase_header(9, "FINAL_ANSWER",
                "Extracting and presenting Claude's final response"
            )

            print("| Claude said 'end_turn'!")
            print("|")
            print("| This means:")
            print("|   - Claude has finished thinking")
            print("|   - No more tool calls needed")
            print("|   - Claude has the FINAL ANSWER")
            print("|")

            wait_for_input("(Understanding end_turn)")

            final_response = ""
            for block in response.content:
                if block.type == "text":
                    final_response = block.text
                    break

            print("|")
            print("| " + "=" * 50)
            print("| CLAUDE'S FINAL ANSWER:")
            print("| " + "=" * 50)
            print("|")
            print(f"| {final_response}")
            print("|")
            print("| " + "=" * 50)
            print("|")
            print("| AGENTIC LOOP COMPLETE!")
            print("| " + "=" * 50)
            print(f"|")
            print(f"| Total messages exchanged: {len(messages)}")
            print(f"| Total iterations: {iteration_count}")
            print("|")
            print("| These messages can now be:")
            print("|   - Saved for a later session")
            print("|   - Used to continue the conversation")
            print("|   - Used with /resume to continue later")
            print("|")

            return final_response

        # =====================================================================
        # ERROR CASE: max_tokens
        # =====================================================================

        elif current_stop_reason == "max_tokens":
            print("|")
            print("| ERROR: Hit max_tokens limit")
            print("|")
            return "Error: Hit token limit"

    # Max iterations reached
    return "Error: Max iterations reached"


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Fix stdout encoding for Windows
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("\n" + "=" * 70)
    print("FLOW LOGGER - INTERACTIVE TEACHING MODE")
    print("=" * 70)
    print("""
| This program demonstrates the COMPLETE agentic loop flow.
|
| TEACHING MODE - With PHASE CONTROLS:
| -----------------------------------
| - Phases are numbered 1-9 for easy tracking
| - Press ENTER after each phase to continue
| - Progress bar shows where you are
| - Teacher explanations between phases
|
| TO DISABLE INTERACTIVE MODE:
| Change INTERACTIVE_MODE = False at the top of this file
| Then it will auto-continue after {AUTO_DELAY} seconds per phase.
|
| Let's begin!
    """.format(AUTO_DELAY=AUTO_DELAY))

    input("\n>>> Press ENTER to start the demonstration...")

    print("\n" + "=" * 70)
    print("STARTING THE AGENTIC LOOP DEMONSTRATION")
    print("=" * 70)

    user_input = "What is 1500 + 2500? Please use the calculator tool."

    print(f"\n>>> User asking: \"{user_input}\"")
    print("\n>>> Watch each phase carefully!\n")

    result = run_interactive_agentic_loop(user_input)

    print("\n" + "=" * 70)
    print("DEMONSTRATION COMPLETE!")
    print("=" * 70)
    print(f"""
RESULT: {result}

PHASE SUMMARY:
==============
Phase 1: INITIALIZATION - Created messages list, defined tools
Phase 2: USER_MESSAGE - Added user's question to messages
Phase 3: API_REQUEST - Sent to Claude API
Phase 4: API_RESPONSE - Examined Claude's response
Phase 5: STOP_REASON - Checked Claude's decision (tool_use)
Phase 6: TOOL_EXECUTION - Ran calculator on YOUR machine
Phase 7: MESSAGE_UPDATE - Added results to messages
Phase 8: LOOP_BACK - Sent updated messages back
         (Back to Phase 3...)
Phase 9: FINAL_ANSWER - Claude returned the answer

KEY CONCEPTS COVERED:
====================
1. Claude is the REASONING engine - decides WHAT to do
2. Your code is the EXECUTION engine - does things
3. Tools execute on YOUR machine, not Claude's cloud
4. Messages must be added in correct order
5. Loop continues until stop_reason = 'end_turn'
    """)


"""
+===========================================================================+
|                                                                           |
|  QUICK REFERENCE - stop_reason VALUES:                                   |
|                                                                           |
|  'tool_use'  -> Execute tools and loop back                              |
|  'end_turn'  -> Return final answer (loop complete)                      |
|  'max_tokens' -> Error - hit token limit                                 |
|                                                                           |
|  MESSAGE ORDER (CRITICAL!):                                              |
|  1. Add assistant message (Claude's request)                            |
|  2. Add user message with tool_result (the result)                       |
|                                                                           |
|  TOOL EXECUTION:                                                         |
|  - Happens on YOUR machine                                               |
|  - Claude only RECEIVES the result                                       |
|  - Return string, not other types                                       |
|                                                                           |
+===========================================================================+
"""