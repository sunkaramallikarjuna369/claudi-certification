"""
+===========================================================================+
|                                                                           |
|  PRACTICE 3: SEQUENTIAL TOOL EXECUTION                                   |
|                                                                           |
|  When one tool's output becomes another's input!                         |
|                                                                           |
|  This practice shows how to chain tools together where each tool's      |
|  output feeds into the next tool's input. Real agents do this!         |
|                                                                           |
|  + REAL-TIME SCENARIOS + MISTAKES DEVELOPERS MAKE + INTERVIEW Q&A    |
|                                                                           |
+===========================================================================+

INTERVIEW PREP: "How do you implement sequential tool execution?"
This question tests your understanding of data flow between tools.
In production, this is where MOST agent failures happen.

REAL-TIME SCENARIO: User asks "I bought AAPL at $150, now it's $178.50,
100 shares. What's my profit in EUR?"
Requires: calculate_profit -> convert_currency (chained!)

===========================================================================
SEQUENTIAL VS PARALLEL: Understanding the Difference
===========================================================================

    +-----------------------------------------------------------------------+
    | VISUAL: Parallel vs Sequential Tool Execution                        |
    +-----------------------------------------------------------------------+

    PARALLEL (all run together):
    +-------------+     +-------------+
    | get_weather |     | get_stock   |      <-- Independent
    +-------------+     +-------------+            no data dependency
          |                   |
          v                   v
    +-------------+     +-------------+
    |  "22C, Tokyo"|    | "AAPL: 180" |
    +-------------+     +-------------+
          |                   |
          +---------+---------+
                    |
                    v
              Complete answer

    SEQUENTIAL (chained):
    +-------------+          +-------------+          +-------------+
    | get_price  | ------> | calc_profit | ------> | convert_EUR|
    | AAPL: 180  |          | profit: 2850|          | 2622 EUR   |
    +-------------+          +-------------+          +-------------+
          ^                         ^                         ^
          |                         |                         |
          | output feeds            | output feeds            | final
          | into next input         | into next input        | answer

    +-----------------------------------------------------------------------+
    | KEY INSIGHT: Sequential means ONE iteration's output feeds into      |
    | the NEXT iteration's input, not multiple tools in one response       |
    +-----------------------------------------------------------------------+

===========================================================================
KEY CONCEPTS YOU'LL LEARN
===========================================================================

    1. TOOL CHAINING: How one tool's output becomes another's input
    2. CONTEXT PRESERVATION: Maintaining data across iterations
    3. DEPENDENCY GRAPH: Understanding tool execution order
    4. PASSING VALUE: How Claude interprets and uses tool results

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
# TOOL DEFINITIONS: Financial tools for sequential execution demo
# ============================================================================

tools = [
    {
        "name": "get_stock_price",
        "description": "Get the current stock price for a company.",
        "input_schema": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "The stock ticker symbol. Examples: 'AAPL' (Apple), 'GOOGL' (Google), 'MSFT' (Microsoft)"
                }
            },
            "required": ["symbol"]
        }
    },
    {
        "name": "calculate_profit",
        "description": "Calculate profit or loss from a stock trade.",
        "input_schema": {
            "type": "object",
            "properties": {
                "buy_price": {
                    "type": "number",
                    "description": "The price per share when you bought"
                },
                "sell_price": {
                    "type": "number",
                    "description": "The current or selling price per share"
                },
                "shares": {
                    "type": "number",
                    "description": "How many shares you own"
                }
            },
            "required": ["buy_price", "sell_price", "shares"]
        }
    },
    {
        "name": "convert_currency",
        "description": "Convert an amount from one currency to another.",
        "input_schema": {
            "type": "object",
            "properties": {
                "amount": {
                    "type": "number",
                    "description": "The amount to convert"
                },
                "from_currency": {
                    "type": "string",
                    "description": "Source currency (e.g., 'USD', 'EUR')"
                },
                "to_currency": {
                    "type": "string",
                    "description": "Target currency (e.g., 'EUR', 'USD')"
                }
            },
            "required": ["amount", "from_currency", "to_currency"]
        }
    }
]


def execute_tool(name: str, tool_input: dict) -> str:
    """
    Execute a tool and return the result.

    NOTE: For sequential execution, the RETURN FORMAT matters!
    Claude interprets this for the next tool call.
    """
    if name == "get_stock_price":
        symbol = tool_input.get("symbol", "").upper()

        prices = {
            "AAPL": 178.50,
            "GOOGL": 142.30,
            "MSFT": 378.90,
            "AMZN": 178.25,
            "TSLA": 248.50
        }

        price = prices.get(symbol, 100.00)
        return f"{symbol}: ${price:.2f} per share"

    elif name == "calculate_profit":
        buy_price = tool_input.get("buy_price")
        sell_price = tool_input.get("sell_price")
        shares = tool_input.get("shares")

        profit_per_share = sell_price - buy_price
        total_profit = profit_per_share * shares

        return f"Buy: ${buy_price}, Sell: ${sell_price}, Shares: {shares}, Profit/Loss: ${total_profit:.2f}"

    elif name == "convert_currency":
        amount = tool_input.get("amount")
        from_currency = tool_input.get("from_currency", "").upper()
        to_currency = tool_input.get("to_currency", "").upper()

        rates = {
            "USD_TO_EUR": 0.92,
            "EUR_TO_USD": 1.09,
            "USD_TO_GBP": 0.79,
            "GBP_TO_USD": 1.27
        }

        key = f"{from_currency}_TO_{to_currency}"
        rate = rates.get(key, 1.0)

        converted = amount * rate
        return f"{amount} {from_currency} = {converted:.2f} {to_currency}"

    return f"Unknown tool: {name}"


def run_agentic_loop(user_message: str):
    """
    Run the agentic loop with sequential tool execution.

    The sequential pattern:
    1. Claude calls first tool (e.g., calculate_profit)
    2. Execute tool, return structured result
    3. Loop back - Claude sees result and calls next tool
    4. Repeat until Claude has all answers
    5. Claude synthesizes final answer from all tool results

    KEY: Each iteration's result feeds into the next iteration's decision.
    """
    messages = [{"role": "user", "content": user_message}]
    iteration = 0

    while True:
        iteration += 1

        print(f"\n{'='*60}")
        print(f"ITERATION {iteration}")
        print('='*60)

        response = client.messages.create(
            model="claude-haiku-4-5-20250601",
            max_tokens=4096,
            messages=messages,
            tools=tools,
        )

        print(f"Stop reason: {response.stop_reason}")

        if response.stop_reason == "tool_use":
            print("\nAI wants to use a tool:")

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

                    print(f"\n   TOOL: {tool_name}")
                    print(f"   INPUT: {tool_input}")

                    result = execute_tool(tool_name, tool_input)

                    print(f"   RESULT: {result}")

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

            print(f"\n   Adding result to conversation history...")
            print(f"   Looping back to continue...")
            continue

        elif response.stop_reason == "end_turn":
            print(f"\n{'='*60}")
            print("FINAL ANSWER:")
            print('='*60)

            final_text = ""
            for block in response.content:
                if block.type == "text" and block.text:
                    final_text = block.text
                    break
            print(final_text)
            print('='*60)

            return final_text


# ============================================================================
# REAL-TIME SCENARIOS: When sequential execution breaks in production
# ============================================================================

def show_real_time_scenarios():
    """
    Production scenarios where sequential tool execution breaks.
    """

    print("\n" + "=" * 70)
    print("REAL-TIME SCENARIOS: When Sequential Execution Breaks")
    print("=" * 70)

    print("""
    +======================================================================+
    ||                                                                      ||
    ||  SCENARIO #1: The Parsing Failure                                   ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  PROBLEM:                                                            ||
    ||  - calculate_profit returns "$2,850.00 USD profit"                   ||
    ||  - convert_currency expects just "2850", not formatted string        ||
    ||  - Claude can't parse the number from the formatted string          ||
    ||                                                                      ||
    ||  CAUSE:                                                              ||
    ||  - Tool returning human-readable format instead of machine-parseable ||
    ||  - Not planning for sequential use                                  ||
    ||                                                                      ||
    ||  PRODUCTION IMPACT:                                                  ||
    ||  - User asks "profit in EUR"                                         ||
    ||  - Claude gets "$2,850" but can't extract 2850 for next tool         ||
    ||  - "I'm not sure how to convert that"                              ||
    ||  - Task fails at step 2                                             ||
    ||                                                                      ||
    ||  FIX: Return both formatted AND raw numeric in result              ||
    ||  e.g., "Profit: $2,850 USD | raw: 2850"                             ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  SCENARIO #2: The Lost Context After Iteration                      ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  PROBLEM:                                                            ||
    ||  - User asked about stocks, made it through 3 steps                 ||
    ||  - Now wants to ask about different stocks                         ||
    ||  - Agent asks for buy_price AGAIN (lost context from step 1)        ||
    ||                                                                      ||
    ||  CAUSE:                                                              ||
    ||  - Tool results passed back but Claude "forgets" original parameters ||
    ||  - Not including original question context in each iteration        ||
    ||                                                                      ||
    ||  PRODUCTION IMPACT:                                                  ||
    ||  - User: "What about my GOOGL shares?"                              ||
    ||  - Agent: "What was the buy price for GOOGL?"                       ||
    ||  - Frustrating back-and-forth                                       ||
    ||                                                                      ||
    ||  FIX: Maintain state in your application, not just in Claude        ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  SCENARIO #3: The Circular Dependency                               ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  PROBLEM:                                                            ||
    ||  - Tool A needs Tool B's output, but Tool B needs Tool A's            ||
    ||  - Infinite loop: A->B->A->B->...                                   ||
    ||  - Max iterations hit, partial result returned                      ||
    ||                                                                      ||
    ||  CAUSE:                                                              ||
    ||  - Poor tool design creating circular dependencies                  ||
    ||  - Not thinking through dependency graph                          ||
    ||                                                                      ||
    ||  PRODUCTION IMPACT:                                                  ||
    ||  - Agent never completes, wastes API calls                          ||
    ||  - User sees "max iterations reached" with no answer                ||
    ||                                                                      ||
    ||  FIX: Design tools with clear, linear dependencies                  ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  SCENARIO #4: The Type Mismatch                                     ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  PROBLEM:                                                            ||
    ||  - get_stock_price returns string "$178.50"                         ||
    ||  - calculate_profit expects number (not string) for sell_price      ||
    ||  - Claude passes "$178.50" instead of 178.50                        ||
    ||  - TypeError or wrong calculation                                   ||
    ||                                                                      ||
    ||  CAUSE:                                                              ||
    ||  - Inconsistent return types across tools                           ||
    ||  - Not defining explicit return types in tool schema               ||
    ||                                                                      ||
    ||  PRODUCTION IMPACT:                                                  ||
    ||  - "Cannot subtract 'str' and 'int'" error in logs                 ||
    ||  - Calculations fail silently, wrong answers returned              ||
    ||                                                                      ||
    ||  FIX: Normalize all numeric returns to Python numbers, not strings  ||
    ||                                                                      ||
    +======================================================================+
    """)


# ============================================================================
# MISTAKES DEVELOPERS MAKE: Expert warnings
# ============================================================================

def show_mistakes():
    """
    Common errors developers make with sequential tool execution.
    """

    print("\n" + "=" * 70)
    print("MISTAKES DEVELOPERS MAKE - EXPERT WARNINGS")
    print("=" * 70)

    print("""
    +======================================================================+
    ||                                                                      ||
    ||  MISTAKE #1: Returning Human-Readable Instead of Machine-Parseable  ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WRONG CODE:                                                         ||
    ||  def execute_tool(name, tool_input):                                 ||
    ||      if name == "calculate_profit":                                  ||
    ||          return f"Total profit: ${total_profit:.2f}"  # Just text! ||
    ||                                                                      ||
    ||  WHAT HAPPENS:                                                       ||
    ||  - Claude receives "Total profit: $2,850.00"                        ||
    ||  - Next tool expects just "2850", can't parse from formatted string ||
    ||  - Sequential execution fails                                       ||
    ||                                                                      ||
    ||  CORRECT CODE:                                                       ||
    ||  def execute_tool(name, tool_input):                                 ||
    ||      if name == "calculate_profit":                                  ||
    ||          return json.dumps({                                        ||
    ||              "formatted": f"${total_profit:.2f}",                    ||
    ||              "numeric": total_profit,                               ||
    ||              "currency": "USD"                                      ||
    ||          })                                                          ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  MISTAKE #2: Not Maintaining State Across Iterations                 ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WRONG CODE:                                                         ||
    ||  def run_agentic_loop(user_message):                                ||
    ||      messages = [{"role": "user", "content": user_message}]         ||
    ||      # Only passes current message, no context stored               ||
    ||      # Claude must deduce all context from tool results             ||
    ||                                                                      ||
    ||  WHAT HAPPENS:                                                       ||
    ||  - After 5 iterations, Claude loses track of original parameters    ||
    ||  - Asks user to re-enter data already provided                      ||
    ||                                                                      ||
    ||  CORRECT CODE:                                                       ||
    ||  def run_agentic_loop(user_message, session_state):                ||
    ||      messages = session_state["messages"]                           ||
    ||      messages.append({"role": "user", "content": user_message})    ||
    ||      # session_state preserves original parameters across iterations||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  MISTAKE #3: Ignoring Tool Return Type Mismatch                     ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WRONG CODE:                                                         ||
    ||  def execute_tool(name, tool_input):                                 ||
    ||      if name == "get_stock_price":                                   ||
    ||          return f"${price}"  # Returns STRING for numeric context    ||
    ||      elif name == "calculate_profit":                                ||
    ||          return price1 - price2  # Expects NUMBER                   ||
    ||                                                                      ||
    ||  WHAT HAPPENS:                                                       ||
    ||  - String "$178.50" passed where number 178.50 expected              ||
    ||  - Type conversion fails                                            ||
    ||                                                                      ||
    ||  CORRECT CODE:                                                       ||
    ||  def execute_tool(name, tool_input):                                 ||
    ||      if name == "get_stock_price":                                   ||
    ||          return f"${price:.2f} per share"  # Include raw number     ||
    ||      # Always include number in extractable format                  ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  MISTAKE #4: Assuming Claude Remembers Tool Results Forever         ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WRONG ASSUMPTION:                                                   ||
    ||  "Claude called calculate_profit, so it remembers for next calls"   ||
    ||                                                                      ||
    ||  WHAT HAPPENS:                                                       ||
    ||  - After many iterations, context window fills up                    ||
    ||  - Earlier tool results get pushed out                              ||
    ||  - Claude "forgets" previous calculations                            ||
    ||                                                                      ||
    ||  CORRECT APPROACH:                                                   ||
    ||  - Store critical values in YOUR application state                 ||
    ||  - When asking Claude to continue, include prior values in prompt   ||
    ||  e.g., "Continue calculation: buy=150, sell=178.50, shares=100"    ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  MISTAKE #5: Not Planning the Dependency Chain                       ||
    ||  ================================================================   ||
    ||                                                                      ||
    ||  WRONG CODE:                                                         ||
    ||  # Two tools with circular dependency                              ||
    ||  get_weather_temp -> convert_fahrenheit_celsius -> get_weather_temp ||
    ||                                                                      ||
    ||  WHAT HAPPENS:                                                       ||
    ||  - Infinite loop                                                    ||
    ||  - Max iterations reached, no answer                                ||
    ||                                                                      ||
    ||  CORRECT CODE:                                                       ||
    ||  # Design tools with clear input/output types                       ||
    ||  # Tool A: raw_temperature -> Tool B: formatted_output              ||
    ||  # No circular dependencies                                         ||
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
    INTERVIEW Q1: "How do you implement sequential tool execution?"
    ======================================================================

    EXPECTED ANSWER STRUCTURE:
    1. Define tools with clear input/output contracts
    2. Design return formats for machine parsing, not just humans
    3. Each iteration: Claude sees previous results, decides next tool
    4. Loop until Claude has complete answer

    EXAMPLE ANSWER:
    "In sequential execution, one tool's output becomes the next tool's
    input. I design tools so their return values include both formatted
    text (for human readability) and structured data (for parsing by Claude).
    Each iteration adds to the conversation history so Claude sees all
    previous results and can chain them appropriately."

    +-----------------------------------------------------------------------+
    | EXPERT TIP: Emphasize return format design - that's the key to        |
    | successful sequential execution.                                       |
    +-----------------------------------------------------------------------+


    ======================================================================
    INTERVIEW Q2: "What's the difference between parallel and sequential?"
    ======================================================================

    EXPECTED ANSWER:

    PARALLEL:
    - Multiple tools called in ONE response
    - All execute simultaneously
    - Results return together in next iteration
    - For independent operations (weather AND stocks)

    SEQUENTIAL:
    - Tool A executes, result feeds into Tool B
    - Chain across multiple iterations
    - For dependent operations (get price -> calculate profit -> convert)

    RED FLAGS IN ANSWERS:
    - "They're the same" -> Shows confusion
    - "Sequential is always better" -> Misses use case differences

    +-----------------------------------------------------------------------+
    | EXPERT TIP: Give concrete examples for each type.                      |
    +-----------------------------------------------------------------------+


    ======================================================================
    INTERVIEW Q3: "How do you handle data passing between tools?"
    ======================================================================

    EXPECTED ANSWER:
    "I design return formats for parseability. Instead of just human-readable
    text, tools return structured data that Claude can easily parse. For
    example, calculate_profit might return: 'Result: $2850.00 USD (2850.00)'
    where Claude can extract the raw number for the next tool."

    FOR PRODUCTION:
    - Use JSON for structured returns when complex
    - Include both formatted and raw values in returns
    - Document expected input types in tool descriptions
    - Provide example inputs/outputs in schema description

    +-----------------------------------------------------------------------+
    | EXPERT TIP: Mention return format design as critical for chaining.   |
    +-----------------------------------------------------------------------+


    ======================================================================
    INTERVIEW Q4: "What happens when sequential execution fails?"
    ======================================================================

    EXPECTED ANSWER:
    "When sequential execution fails, I:
    1. Check if it's a parsing error (wrong format in result)
    2. Check if it's a type mismatch (string vs number)
    3. Check if it's a context loss (Claude forgot parameters)
    4. Implement graceful degradation: return partial results
    5. Log each step for debugging"

    GRACEFUL DEGRADATION:
    - If step 2 fails, return what step 1 found
    - Let user decide whether to continue or restart
    - Never crash the entire agent

    +-----------------------------------------------------------------------+
    | EXPERT TIP: Mention specific failure modes and how to debug them.    |
    +-----------------------------------------------------------------------+
    """)


# ============================================================================
# VISUAL REPRESENTATIONS: ASCII diagrams
# ============================================================================

def show_visual_representations():
    """
    ASCII diagrams showing sequential tool execution.
    """

    print("\n" + "=" * 70)
    print("VISUAL REPRESENTATIONS: Sequential Tool Execution")
    print("=" * 70)

    print("""
    +======================================================================+
    ||  DIAGRAM 1: Sequential Execution Flow                               ||
    +======================================================================+

    USER: "I bought 100 AAPL at $150, now $178. What's my profit in EUR?"

    ITERATION 1:
    +-------------------+      +--------------------------+
    | Claude sees:      |      | Claude decides:           |
    | User wants profit |----> | "Need to calculate first" |
    +-------------------+      +--------------------------+
                                     | tool_use
                                     v
                            +-------------------+
                            | calculate_profit  |
                            | buy=150, sell=178|
                            | shares=100       |
                            +-------------------+
                                     |
                                     v
                            +-------------------+
                            | Result:           |
                            | "Profit: $2850"   |
                            +-------------------+

    ITERATION 2:
    +-------------------+      +--------------------------+
    | Claude sees:      |      | Claude decides:          |
    | "$2850 USD profit"|----> | "Now convert to EUR"     |
    +-------------------+      +--------------------------+
                                     | tool_use
                                     v
                            +-------------------+
                            | convert_currency |
                            | amount=2850      |
                            | from=USD, to=EUR |
                            +-------------------+
                                     |
                                     v
                            +-------------------+
                            | Result:           |
                            | "2850 USD = 2622" |
                            +-------------------+

    ITERATION 3 (end_turn):
    +-------------------+      +--------------------------+
    | Claude sees both  |      | Claude synthesizes:     |
    | results           |----> | "Your profit is..."    |
    +-------------------+      +--------------------------+


    +======================================================================+
    ||  DIAGRAM 2: Return Format for Sequential Execution                ||
    +======================================================================+

    WRONG FORMAT (hard to parse):
    +------------------------------------------+
    | calculate_profit returns:                |
    | "Total profit: $2,850.00 USD"           |
    +------------------------------------------+
              |
              | Claude tries to parse "$2,850.00 USD"
              | Extract number? How to handle commas?
              | Is the "$" part of the number?
              v
         PARSING ERROR!


    CORRECT FORMAT (easy to parse):
    +------------------------------------------+
    | calculate_profit returns:                |
    | "Profit: $2850.00 USD (2850.00)"         |
    |                    ^      ^              |
    |                    |      |              |
    | formatted with $  |      raw number    |
    +------------------------------------------+
              |
              | Claude parses: raw number is 2850.00
              | Ready for next tool call!
              v
         SEQUENTIAL SUCCESS!


    +======================================================================+
    ||  DIAGRAM 3: Dependency Graph for Financial Tools                  ||
    +======================================================================+

    +----------+      +------------------+      +----------------+
    | get_     | ---> | calculate_profit | ---> | convert_      |
    | stock_pri |      | INPUT:           |      | currency      |
    | ce       |      | - buy_price       |      | INPUT:        |
    +----------+      | - sell_price (from|      | - amount (from|
                      |   get_stock OR    |      |   calc_profit) |
                      |   provided value |      | - from_currency|
                      | - shares         |      | - to_currency |
                      +------------------+      +----------------+
                           |                           |
                           | output feeds             | output is
                           | into next input          | final answer
                           v                           v
                      +------------------+      +----------------+
                      | Returns:         |      | Returns:       |
                      | "$profit USD"   |      | "X EUR"        |
                      +------------------+      +----------------+


    +======================================================================+
    ||  DIAGRAM 4: Context Preservation Across Iterations                ||
    +======================================================================+

    WRONG: No context preservation
    +---------------------------+
    | Message 1: buy=150, sell=178|
    +---------------------------+
    | Message 2: calculate_profit |
    +---------------------------+
    | Message 3: convert USD->EUR|
    +---------------------------+
    | Message N: "What was buy?" | <- Forgot!
    +---------------------------+

    CORRECT: Maintain state in your app
    +---------------------------+
    | session_state = {         |
    |   "buy_price": 150,       |
    |   "sell_price": 178,     |
    |   "shares": 100          |  <- Preserved across iterations
    |   "profit": 2850        |
    | }                         |
    +---------------------------+

    When Claude calls new tool, pass context:
    context = f"Previous results: buy=150, sell=178, profit=2850 USD"
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

    print("\n" + "=" * 60)
    print("PRACTICE 3: SEQUENTIAL TOOL EXECUTION")
    print("=" * 60)
    print("""
    This practice shows how to chain tools together where each tool's
    output feeds into the next tool's input.

    Example: Calculate profit (USD) -> Convert to EUR

    Follow along as we:
    1. Run sequential tool execution demo
    2. Show real-time scenarios where sequential breaks
    3. Highlight common mistakes developers make
    4. Provide interview Q&A with expert answers
    5. Show visual representations of the concepts
    """)

    print("\n" + "-" * 60)
    print("PART 1: Running Sequential Tool Execution")
    print("-" * 60)

    user_input = """
    I bought 100 shares of AAPL at $150 per share last month.
    The current price is $178.50.
    What is my profit in USD and EUR?
    """

    print(f"USER REQUEST:\n{user_input}")
    print("\n" + "-" * 60 + "\n")

    result = run_agentic_loop(user_input)

    print("\n" + "-" * 60)
    print("PART 2: Real-Time Scenarios")
    print("-" * 60)
    show_real_time_scenarios()

    print("\n" + "-" * 60)
    print("PART 3: Common Mistakes")
    print("-" * 60)
    show_mistakes()

    print("\n" + "-" * 60)
    print("PART 4: Interview Q&A")
    print("-" * 60)
    show_interview_qa()

    print("\n" + "-" * 60)
    print("PART 5: Visual Representations")
    print("-" * 60)
    show_visual_representations()

    print("""
================================================================================
WHAT WE HAVE LEARNT
================================================================================

+======================================================================+
||  1. SEQUENTIAL TOOL EXECUTION:                                         ||
||                                                                      ||
||  - One tool's output becomes another's input                         ||
||  - Chain across MULTIPLE iterations (not parallel)                   ||
||  - Claude sees results, decides next tool to call                    ||
||  - Loop until final answer achieved                                  ||
||                                                                      ||
||  PARALLEL: Multiple tools in ONE response (independent)             ||
||  SEQUENTIAL: Tool A's output -> Tool B's input (dependent)           ||
||                                                                      ||
+======================================================================+

+======================================================================+
||  2. REAL-TIME SCENARIOS (Sequential Execution Breakage):            ||
||                                                                      ||
||  SCENARIO #1: Parsing Failure                                         ||
||  - Human-readable return can't be parsed for next tool              ||
||  - Fix: Include both formatted and raw numeric values               ||
||                                                                      ||
||  SCENARIO #2: Lost Context After Iteration                           ||
||  - Claude "forgets" original parameters after many iterations        ||
||  - Fix: Maintain state in your application, not just Claude         ||
||                                                                      ||
||  SCENARIO #3: Circular Dependency                                    ||
||  - Tool A needs B, Tool B needs A = infinite loop                    ||
||  - Fix: Design tools with clear, linear dependencies                 ||
||                                                                      ||
||  SCENARIO #4: Type Mismatch                                          ||
||  - String "$178.50" passed where number expected                     ||
||  - Fix: Normalize all numeric returns, include raw numbers            ||
||                                                                      ||
+======================================================================+

+======================================================================+
||  3. MISTAKES DEVELOPERS MAKE:                                        ||
||                                                                      ||
||  MISTAKE #1: Human-readable only returns                             ||
||  - Include both formatted text AND raw numeric in returns           ||
||                                                                      ||
||  MISTAKE #2: Not maintaining state across iterations                ||
||  - Store critical values in your app, not just Claude's context     ||
||                                                                      ||
||  MISTAKE #3: Type mismatches between tools                           ||
||  - Define consistent return types across all tools                   ||
||                                                                      ||
||  MISTAKE #4: Assuming Claude remembers forever                       ||
||  - Context window fills up, earlier results pushed out               ||
||                                                                      ||
||  MISTAKE #5: No dependency planning                                  ||
||  - Design dependency graph before implementing tools               ||
||                                                                      ||
+======================================================================+

+======================================================================+
||  4. INTERVIEW Q&A FRAMEWORKS:                                        ||
||                                                                      ||
||  Q: "How do you implement sequential execution?"                     ||
||  A: Design return formats for parsing, chain across iterations       ||
||                                                                      ||
||  Q: "Parallel vs sequential?"                                        ||
||  A: Parallel = independent tools at once, Sequential = dependent     ||
||                                                                      ||
||  Q: "How do you handle data passing?"                                ||
||  A: Return both formatted and raw values, document expected types    ||
||                                                                      ||
||  Q: "What when sequential fails?"                                  ||
||  A: Check parsing, type, context; implement graceful degradation      ||
||                                                                      ||
+======================================================================+

+======================================================================+
||  5. VISUAL REPRESENTATIONS (ASCII Diagrams):                         ||
||                                                                      ||
||  - Sequential execution flow across iterations                      ||
||  - Return format design for parseability                            ||
||  - Dependency graph for tool chaining                               ||
||  - Context preservation vs loss                                     ||
||                                                                      ||
+======================================================================+

+======================================================================+
||  6. KEY RULES TO MEMORIZE:                                           ||
||                                                                      ||
||  RULE #1: Return both formatted AND raw values for chaining         ||
||  RULE #2: Maintain state in your app, not just in Claude            ||
||  RULE #3: Design dependency graph before implementation             ||
||  RULE #4: Normalize numeric returns to numbers, not strings         ||
||  RULE #5: Plan for parsing - Claude needs to extract next inputs    ||
||  RULE #6: Avoid circular dependencies                              ||
||                                                                      |
+======================================================================+

Next: practice_04_error_handling.py shows how to handle
ERRORS gracefully in agentic loops without crashing!

================================================================================
""")


"""
+===========================================================================+
|                                                                           |
|  KEY CONCEPTS FROM THIS FILE:                                           |
|                                                                           |
|  SEQUENTIAL EXECUTION:                                                   |
|  - One tool's output feeds into next tool's input                       |
|  - Chain across multiple iterations                                     |
|  - Design return formats for parseability                               |
|  - Maintain state in your application                                   |
|                                                                           |
|  REAL-TIME FIXES:                                                        |
|  - Return both formatted and raw values                                 |
|  - Normalize numeric types                                              |
|  - Plan dependency graphs                                               |
|  - Log each step for debugging                                          |
|                                                                           |
|  INTERVIEW PREP:                                                        |
|  - "What's the difference between parallel and sequential?"             |
|  - "How do you handle data passing between tools?"                       |
|  - "What when sequential execution fails?"                               |
|                                                                           |
|  NEXT: practice_04_error_handling.py (error handling)                  |
|                                                                           |
+===========================================================================+
"""
