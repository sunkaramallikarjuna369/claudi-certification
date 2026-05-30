"""
+===========================================================================+
|                                                                           |
|  UNDERSTANDING "required" IN input_schema                                 |
|                                                                           |
|  A clear explanation with aligned examples!                             |
|                                                                           |
+===========================================================================+

WHAT THIS FILE TEACHES:
-----------------------
"required" is a list in input_schema that tells Claude:
  "Which parameters MUST be included when calling my tool"

When Claude calls a tool, it sends PARAMETER VALUES to the tool function.
These values are sent via the tool's "input" parameter.

This file explains:
  1. What "required" means
  2. How it affects what Claude SENDS to the tool
  3. Common mistakes
  4. Visual comparisons

NO API CALLS - This file only explains the concept!
"""

import sys


# ============================================================================
# PART 1: What is "required"?
# ============================================================================

def explain_required():
    """Explain what 'required' means."""

    print("\n" + "=" * 70)
    print("  PART 1: WHAT IS 'required' ?")
    print("=" * 70)

    print("""
+----------------------------------------------------------------------+
|                                                                      |
|  THE SIMPLE ANSWER:                                                  |
|  -------------------                                                 |
|                                                                      |
|  "required" is a LIST that tells Claude which parameters it          |
|  MUST include when calling your tool.                                |
|                                                                      |
|  WHEN CLAUDE CALLS A TOOL, IT SENDS VALUES TO THE TOOL FUNCTION:    |
|  ----------------------------------------------------------------   |
|                                                                      |
|      YOUR TOOL (Python function):                                    |
|      --------------------------                                      |
|      def my_tool(tool_input):                                        |
|          # tool_input is a DICTIONARY with parameter values          |
|          # Example: {"name": "John", "age": 30}                      |
|                                                                      |
|                                                                      |
|      WHAT CLAUDE SENDS TO YOUR TOOL:                                 |
|      --------------------------------                                |
|      Claude builds a dictionary and passes it to your function       |
|                                                                      |
|  THE "required" LIST CONTROLS WHAT GOES IN THAT DICTIONARY:           |
|  ---------------------------------------------------------           |
|                                                                      |
|      If a parameter IS in "required" list -> MUST be in the dict    |
|      If a parameter is NOT in "required" -> Can be SKIPPED          |
|                                                                      |
+----------------------------------------------------------------------+
    """)

    print("""
+----------------------------------------------------------------------+
|                                                                      |
|  VISUAL EXAMPLE:                                                     |
|  ---------------                                                     |
|                                                                      |
|  input_schema = {                                                    |
|                                                                      |
|      "properties": {                                                 |
|                                                                      |
|          "name": { "type": "string" },   # <-- MUST be in dict      |
|          "age":  { "type": "integer" }   # <-- CAN be skipped       |
|      },                                                              |
|                                                                      |
|      "required": ["name"]           # ONLY "name" is required!      |
|  }                                                                   |
|                                                                      |
|  WHAT CLAUDE SENDS TO THE TOOL (two possible outcomes):              |
|  ----------------------------------------------------               |
|                                                                      |
|      Case A: User gives only name                                   |
|      --------------------------------                               |
|      Claude sends: {"name": "John"}                                 |
|                     ^^^^^^^^^^^                                      |
|                     age is SKIPPED (it's optional)                   |
|                                                                      |
|                                                                      |
|      Case B: User gives both name and age                           |
|      ----------------------------------------                       |
|      Claude sends: {"name": "John", "age": 30}                      |
|                                     ^^^^^^^^                        |
|                                     age IS included (optional,      |
|                                     but user mentioned it)           |
|                                                                      |
+----------------------------------------------------------------------+
    """)

    input("\n>>> PRESS ENTER to continue...")


# ============================================================================
# PART 2: Where Does Claude Send The Data?
# ============================================================================

def explain_where_data_goes():
    """Explain that Claude sends data TO the tool function."""

    print("\n" + "=" * 70)
    print("  PART 2: WHERE DOES CLAUDE SEND THE DATA?")
    print("=" * 70)

    print("""
+----------------------------------------------------------------------+
|                                                                      |
|  ANSWER: CLAUDE SENDS DATA TO YOUR TOOL FUNCTION                    |
|  --------------------------------------------------------            |
|                                                                      |
|  When you define a tool like this:                                   |
|                                                                      |
|      tools = [{                                                      |
|          "name": "greet",                                           |
|          "description": "Greet someone",                            |
|          "input_schema": { ... }                                    |
|      }]                                                              |
|                                                                      |
|  And Claude decides to use it, Claude CALLS your tool.              |
|                                                                      |
|  Think of it like this:                                             |
|                                                                      |
|      YOUR CODE:                          WHAT CLAUDE DOES:           |
|      ----------                          --------------               |
|                                                                      |
|      def greet(tool_input):        <--  Claude calls this           |
|          name = tool_input["name"]      function with values         |
|          print(f"Hello, {name}!")         in tool_input              |
|                                                                      |
|                                                                      |
|  WHAT IS "tool_input"?                                               |
|  --------------------                                                |
|                                                                      |
|      tool_input is a DICTIONARY with the parameter values            |
|      Claude decides which keys to include based on "required"       |
|                                                                      |
+----------------------------------------------------------------------+
    """)

    print("""
+----------------------------------------------------------------------+
|                                                                      |
|  EXAMPLE: Weather Tool                                              |
|  -----------------------                                            |
|                                                                      |
|  Tool Definition:                                                   |
|  ----------------                                                   |
|      tools = [{                                                      |
|          "name": "get_weather",                                      |
|          "input_schema": {                                            |
|              "properties": {                                         |
|                  "city": {"type": "string"},                         |
|                  "unit": {"type": "string"}                          |
|              },                                                      |
|              "required": ["city"]        # <-- Only city required   |
|          }                                                           |
|      }]                                                              |
|                                                                      |
|                                                                      |
|  Your Python Code (receives what Claude sends):                      |
|  ------------------------------------------------                   |
|                                                                      |
|      def get_weather(tool_input):        # tool_input is a dict     |
|          city = tool_input["city"]       # ALWAYS present (required)|
|          unit = tool_input.get("unit")   # Might be None (optional) |
|                                                                      |
|          # Claude sends EITHER:                                     |
|          #   {"city": "Tokyo"}           (user didn't mention unit) |
|          #   {"city": "Tokyo", "unit": "fahrenheit"} (user mentioned)|
|                                                                      |
+----------------------------------------------------------------------+
    """)

    input("\n>>> PRESS ENTER to continue...")


# ============================================================================
# PART 3: Aligned Examples
# ============================================================================

def show_aligned_examples():
    """Show examples with clear alignment."""

    print("\n" + "=" * 70)
    print("  PART 3: ALIGNED EXAMPLES")
    print("=" * 70)

    print("""
+----------------------------------------------------------------------+
|                                                                      |
|  EXAMPLE 1: Weather Tool                                            |
|  -----------------------                                            |
|                                                                      |
|  Tool Requirements:                                                  |
|  ------------------                                                  |
|    - "city" -> REQUIRED (must be in dict)                           |
|    - "unit" -> OPTIONAL (can be skipped)                            |
|                                                                      |
+----------------------------------------------------------------------+

    tool = {
        "name": "get_weather",
        "input_schema": {
            "properties": {
                "city": {"type": "string"},
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
            },
            "required": ["city"]       # <-- ONLY city is required!
        }
    }

+----------------------------------------------------------------------+
|                                                                      |
|  WHAT CLAUDE SENDS TO THE TOOL:                                      |
|  --------------------------------                                    |
|                                                                      |
|    Scenario A: User says "What's weather in Tokyo?"                  |
|    ----------------------------------------------------              |
|    Claude sends to get_weather():                                    |
|        {"city": "Tokyo"}                                             |
|        ^^^^^^^^^^^^^^^                                               |
|        unit is SKIPPED (it's optional, user didn't ask for it)       |
|                                                                      |
|                                                                      |
|    Scenario B: User says "What's weather in Tokyo in fahrenheit?"    |
|    ---------------------------------------------------------------   |
|    Claude sends to get_weather():                                    |
|        {"city": "Tokyo", "unit": "fahrenheit"}                       |
|                          ^^^^^^^^^^^^^^^^^^^                        |
|                          unit IS included (optional, but user        |
|                          specifically asked for it)                 |
|                                                                      |
+----------------------------------------------------------------------+
    """)

    input("\n>>> PRESS ENTER for next example...")

    print("""
+----------------------------------------------------------------------+
|                                                                      |
|  EXAMPLE 2: Email Tool (Multiple Required Parameters)                |
|  ---------------------------------------------------------           |
|                                                                      |
|  Tool Requirements:                                                 |
|  ------------------                                                  |
|    - "recipient" -> REQUIRED                                        |
|    - "subject"   -> REQUIRED                                        |
|    - "body"      -> REQUIRED                                        |
|    - "cc"        -> OPTIONAL                                       |
|                                                                      |
+----------------------------------------------------------------------+

    tool = {
        "name": "send_email",
        "input_schema": {
            "properties": {
                "recipient": {"type": "string"},
                "subject":   {"type": "string"},
                "body":      {"type": "string"},
                "cc":        {"type": "string"}
            },
            "required": ["recipient", "subject", "body"]
                        # ^^^^^^^^^  ^^^^^^^^  ^^^^
                        # ALL THREE are in the required list!
                        # cc is NOT in the list -> optional
        }
    }

+----------------------------------------------------------------------+
|                                                                      |
|  WHAT CLAUDE SENDS TO THE TOOL:                                      |
|  --------------------------------                                    |
|                                                                      |
|    User: "Send email to john@email.com, subject 'Hi', body 'Hello'"  |
|    -----------------------------------------------------------------|
|    Claude sends to send_email():                                    |
|        {"recipient": "john@email.com", "subject": "Hi", "body": "Hello"}|
|        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^|
|        cc is SKIPPED (optional, not mentioned by user)              |
|                                                                      |
|                                                                      |
|    User: "Same email, also CC jane@email.com"                       |
|    --------------------------------------------                     |
|    Claude sends to send_email():                                    |
|        {"recipient": "john@email.com", "subject": "Hi", "body": "Hello",|
|         "cc": "jane@email.com"}                                     |
|                                    ^^^^^^^^^^^^^^^^^^                |
|                                    cc IS included (optional, but     |
|                                    user specifically asked for it)  |
|                                                                      |
+----------------------------------------------------------------------+
    """)

    input("\n>>> PRESS ENTER for next example...")

    print("""
+----------------------------------------------------------------------+
|                                                                      |
|  EXAMPLE 3: Calculator Tool (Single Required Parameter)             |
|  ------------------------------------------------------------        |
|                                                                      |
|  Tool Requirements:                                                  |
|  ------------------                                                  |
|    - "expression" -> REQUIRED (only parameter!)                     |
|                                                                      |
+----------------------------------------------------------------------+

    tool = {
        "name": "calculator",
        "input_schema": {
            "properties": {
                "expression": {"type": "string"}
            },
            "required": ["expression"]     # <-- Only one parameter!
        }
    }

+----------------------------------------------------------------------+
|                                                                      |
|  WHAT CLAUDE SENDS TO THE TOOL:                                      |
|  --------------------------------                                    |
|                                                                      |
|    User: "Calculate 1500 + 2500"                                     |
|    --------------------------------                                  |
|    Claude sends to calculator():                                    |
|        {"expression": "1500 + 2500"}                                 |
|                                                                      |
|    Simple! Only one parameter, and it's required, so Claude          |
|    always includes it.                                              |
|                                                                      |
+----------------------------------------------------------------------+
    """)

    input("\n>>> PRESS ENTER to continue...")


# ============================================================================
# PART 4: Empty vs No "required" field
# ============================================================================

def show_empty_vs_no_required():
    """Show the difference between empty list and no field."""

    print("\n" + "=" * 70)
    print("  PART 4: EMPTY LIST vs NO 'required' FIELD")
    print("=" * 70)

    print("""
+----------------------------------------------------------------------+
|                                                                      |
|  THESE TWO APPROACHES PRODUCE THE SAME RESULT:                       |
|  --------------------------------------------------------            |
|                                                                      |
|    Option A: Empty list                                              |
|    ---------------                                                   |
|        "required": []      # All parameters are optional!            |
|                                                                      |
|    Option B: No "required" field at all                             |
|    ------------------------------------                              |
|        (just don't include "required" at all)                        |
|                                                                      |
|    Both mean: "Nothing is required - all parameters are optional"    |
|                                                                      |
|                                                                      |
|  WHICH SHOULD YOU USE?                                               |
|  ----------------------                                               |
|                                                                      |
|    RECOMMENDED: Option B - Just omit the "required" field           |
|   理由: Cleaner, simpler, more common in examples                   |
|                                                                      |
|    AVOID: Option A - "required": [] is rarely needed                |
|    理由: Extra code that doesn't add any value                      |
|                                                                      |
+----------------------------------------------------------------------+
    """)

    print("""
+----------------------------------------------------------------------+
|                                                                      |
|  EXAMPLE:                                                            |
|  --------                                                            |
|                                                                      |
|    DON'T WRITE:                                                      |
|    -------------                                                     |
|        input_schema = {                                              |
|            "properties": {                                          |
|                "name": {"type": "string"},                           |
|                "age":  {"type": "integer"}                          |
|            },                                                        |
|            "required": []      # Empty list - unnecessary           |
|        }                                                             |
|                                                                      |
|                                                                      |
|    DO THIS INSTEAD:                                                  |
|    -----------------                                                 |
|        input_schema = {                                              |
|            "properties": {                                          |
|                "name": {"type": "string"},                           |
|                "age":  {"type": "integer"}                          |
|            }                                                         |
|            # No "required" field = all optional!                    |
|        }                                                             |
|                                                                      |
+----------------------------------------------------------------------+
    """)

    input("\n>>> PRESS ENTER to continue...")


# ============================================================================
# PART 5: Common Mistakes
# ============================================================================

def show_mistakes():
    """Show common mistakes with required."""

    print("\n" + "=" * 70)
    print("  PART 5: COMMON MISTAKES")
    print("=" * 70)

    print("""
+----------------------------------------------------------------------+
|                                                                      |
|  MISTAKE 1: Empty required list when you need required params      |
|  ------------------------------------------------------------------  |
|                                                                      |
|    WRONG:                                                            |
|    ------                                                            |
|        "properties": {                                              |
|            "city": {"type": "string"}   # YOU NEED this!           |
|        },                                                            |
|        "required": []               # EMPTY! City won't be sent!  |
|                                                                      |
|    PROBLEM: Claude might NOT send "city" because it's not required! |
|              Your tool will crash trying to access tool_input["city"]|
|                                                                      |
|                                                                      |
|    CORRECT:                                                          |
|    --------                                                          |
|        "properties": {                                              |
|            "city": {"type": "string"}                               |
|        },                                                            |
|        "required": ["city"]         # Put it in the list!           |
|                                                                      |
+----------------------------------------------------------------------+
    """)

    print("""
+----------------------------------------------------------------------+
|                                                                      |
|  MISTAKE 2: Making everything required                              |
|  ------------------------------------------------                   |
|                                                                      |
|    WRONG:                                                            |
|    ------                                                            |
|        "properties": {                                              |
|            "name":    {"type": "string"},                            |
|            "age":     {"type": "integer"},                          |
|            "city":    {"type": "string"},                           |
|            "country": {"type": "string"}                           |
|        },                                                            |
|        "required": ["name", "age", "city", "country"]  # All 4!    |
|                                                                      |
|    PROBLEM: Users must provide ALL 4, even when they only want       |
|              to use one! Tool becomes inflexible.                   |
|                                                                      |
|                                                                      |
|    CORRECT:                                                          |
|    --------                                                          |
|        "required": ["name"]          # Only truly required ones!    |
|                                                                      |
|    TIP: Only put ESSENTIAL parameters in "required".                  |
|         If user can skip it, don't make it required!                 |
|                                                                      |
+----------------------------------------------------------------------+
    """)

    print("""
+----------------------------------------------------------------------+
|                                                                      |
|  MISTAKE 3: Confusing "required" with "has default value"           |
|  ------------------------------------------------------------------  |
|                                                                      |
|    WRONG ASSUMPTION:                                                 |
|    ------------------                                                |
|        "required" means "this will have a default value"             |
|                                                                      |
|    TRUTH:                                                            |
|    ------                                                            |
|        "required" ONLY means "Claude MUST send this parameter"       |
|        It does NOT give a default value!                             |
|                                                                      |
|                                                                      |
|    IF YOU NEED A DEFAULT VALUE:                                       |
|    --------------------------------                                  |
|        Handle it in your CODE!                                       |
|                                                                      |
|        Tool definition:                                              |
|        ----------------                                              |
|            "properties": {                                          |
|                "unit": {                                             |
|                    "type": "string",                                 |
|                    "enum": ["celsius", "fahrenheit"]                 |
|                }                                                     |
|            },                                                        |
|            "required": []         # Unit is optional                 |
|                                                                      |
|        Your Python code:                                             |
|        ------------------                                            |
|            def get_weather(tool_input):                              |
|                unit = tool_input.get("unit", "celsius")             |
|                                        ^^^^^^^^^^^^^^                |
|                                        Default value IN CODE!        |
|                                                                      |
+----------------------------------------------------------------------+
    """)

    input("\n>>> PRESS ENTER to continue...")


# ============================================================================
# PART 6: Visual Comparison
# ============================================================================

def show_visual_comparison():
    """Show visual comparison of different scenarios."""

    print("\n" + "=" * 70)
    print("  PART 6: VISUAL COMPARISON")
    print("=" * 70)

    print("""
+----------------------------------------------------------------------+
|                                                                      |
|  SCENARIO A: No required parameters at all                          |
|  ------------------------------------------------                   |
|                                                                      |
|    input_schema = {                                                  |
|        "properties": {                                               |
|            "name": {"type": "string"},                               |
|            "age":  {"type": "integer"}                               |
|        }                                                             |
|        # NO "required" field = All optional!                         |
|    }                                                                 |
|                                                                      |
|    What Claude SENDS to tool:                                         |
|    --------------------------------                                  |
|        {}                    <- Nothing required                     |
|        {"name": "John"}    <- Just name                             |
|        {"age": 25}         <- Just age                              |
|        {"name": "John", "age": 25}  <- Both (user provided both)   |
|                                                                      |
+----------------------------------------------------------------------+
    """)

    print("""
+----------------------------------------------------------------------+
|                                                                      |
|  SCENARIO B: One required parameter                                  |
|  ----------------------------------------                            |
|                                                                      |
|    input_schema = {                                                  |
|        "properties": {                                               |
|            "name": {"type": "string"},                               |
|            "age":  {"type": "integer"}                               |
|        },                                                            |
|        "required": ["name"]        # Only name is required          |
|    }                                                                 |
|                                                                      |
|    What Claude SENDS to tool:                                         |
|    --------------------------------                                  |
|        {"name": "John"}                    <- MINIMUM (name required)|
|        {"name": "John", "age": 25}          <- Optional included    |
|                                                                      |
|    INVALID (Claude won't send):                                      |
|    -----------------------------                                     |
|        {}              <- MISSING required "name"!                   |
|        {"age": 25}     <- MISSING required "name"!                 |
|                                                                      |
+----------------------------------------------------------------------+
    """)

    print("""
+----------------------------------------------------------------------+
|                                                                      |
|  SCENARIO C: Two required parameters                                |
|  ---------------------------------------                             |
|                                                                      |
|    input_schema = {                                                  |
|        "properties": {                                               |
|            "name":  {"type": "string"},                              |
|            "age":   {"type": "integer"},                             |
|            "city":  {"type": "string"}                               |
|        },                                                            |
|        "required": ["name", "age"]    # Both required               |
|    }                                                                 |
|                                                                      |
|    What Claude SENDS to tool:                                         |
|    --------------------------------                                  |
|        {"name": "John", "age": 25}                    <- MINIMUM    |
|        {"name": "John", "age": 25, "city": "NYC"}     <- Optional   |
|                                                                      |
|    INVALID (Claude won't send):                                      |
|    -----------------------------                                     |
|        {"name": "John"}              <- MISSING required "age"!     |
|        {"age": 25}                   <- MISSING required "name"!    |
|        {}                            <- MISSING both!              |
|                                                                      |
+----------------------------------------------------------------------+
    """)

    print("""
+----------------------------------------------------------------------+
|                                                                      |
|  SUMMARY TABLE:                                                      |
|  --------------                                                      |
|                                                                      |
|    required list           | What Claude MUST send                   |
|    ------------------------|--------------------------------         |
|    (no field)              | Nothing - all optional                  |
|    [] (empty)               | Nothing - all optional                  |
|    ["name"]                 | At least name                           |
|    ["name", "age"]          | At least name AND age                   |
|    ["name", "age", "city"]  | At least all three                      |
|                                                                      |
+----------------------------------------------------------------------+
    """)

    input("\n>>> PRESS ENTER to continue...")


# ============================================================================
# PART 7: Code Examples - What Your Tool Receives
# ============================================================================

def show_code_examples():
    """Show what your Python code receives from Claude."""

    print("\n" + "=" * 70)
    print("  PART 7: CODE EXAMPLES - WHAT YOUR TOOL RECEIVES")
    print("=" * 70)

    print("""
+----------------------------------------------------------------------+
|                                                                      |
|  EXAMPLE: Weather Tool Code                                         |
|  ---------------------------------                                   |
|                                                                      |
|  Tool Definition:                                                    |
|  ----------------                                                    |
|      tools = [{                                                      |
|          "name": "get_weather",                                      |
|          "input_schema": {                                           |
|              "properties": {                                        |
|                  "city": {"type": "string"},                        |
|                  "unit": {"type": "string"}                         |
|              },                                                     |
|              "required": ["city"]        # Only city required      |
|          }                                                           |
|      }]                                                              |
|                                                                      |
|                                                                      |
|  Your Python Code (tool callback):                                   |
|  ------------------------------------                                 |
|                                                                      |
|      def get_weather(tool_input):                                    |
|          # tool_input is what CLAUDE SENDS to your function          |
|                                                                      |
|          city = tool_input["city"]    # ALWAYS present (required)   |
|                                       # Claude GUARANTEES this      |
|                                       # because it's in "required"  |
|                                                                      |
|          unit = tool_input.get("unit")  # Might be None (optional)  |
|                                        # If skipped, returns None   |
|                                                                      |
|          if unit is None:                    # Handle optional      |
|              unit = "celsius"               # Default value        |
|                                                                      |
|          return f"Weather in {city}: 25 {unit}"                     |
|                                                                      |
|                                                                      |
|  WHAT CLAUDE SENDS IN DIFFERENT SCENARIOS:                           |
|  --------------------------------------------                       |
|                                                                      |
|    User: "Weather in Tokyo?"                                         |
|    Result: get_weather receives {"city": "Tokyo"}                   |
|             city = "Tokyo", unit = None                             |
|                                                                      |
|    User: "Weather in Tokyo in fahrenheit"                           |
|    Result: get_weather receives {"city": "Tokyo", "unit": "fahrenheit"}|
|             city = "Tokyo", unit = "fahrenheit"                     |
|                                                                      |
+----------------------------------------------------------------------+
    """)

    print("""
+----------------------------------------------------------------------+
|                                                                      |
|  EXAMPLE: Email Tool Code                                            |
|  --------------------------------                                    |
|                                                                      |
|  Tool Definition:                                                    |
|  ----------------                                                    |
|      tools = [{                                                      |
|          "name": "send_email",                                       |
|          "input_schema": {                                           |
|              "properties": {                                        |
|                  "recipient": {"type": "string"},                   |
|                  "subject":   {"type": "string"},                   |
|                  "body":      {"type": "string"},                   |
|                  "cc":        {"type": "string"}                    |
|              },                                                      |
|              "required": ["recipient", "subject", "body"]           |
|                          # cc is NOT required (not in list)         |
|          }                                                           |
|      }]                                                              |
|                                                                      |
|                                                                      |
|  Your Python Code (tool callback):                                   |
|  ------------------------------------                                 |
|                                                                      |
|      def send_email(tool_input):                                     |
|          # ALL of these are GUARANTEED to exist (required):         |
|          recipient = tool_input["recipient"]  # Always present!    |
|          subject   = tool_input["subject"]    # Always present!    |
|          body      = tool_input["body"]        # Always present!    |
|                                                                      |
|          # This MIGHT exist (optional):                              |
|          cc = tool_input.get("cc")           # Could be None        |
|                                                                      |
|          # Send the email...                                         |
|                                                                      |
|                                                                      |
|  WHAT CLAUDE SENDS:                                                  |
|  ------------------                                                  |
|                                                                      |
|    User: "Email to john@example.com, subject 'Hi', body 'Hello'"    |
|    Result: send_email receives {                                    |
|        "recipient": "john@example.com",                             |
|        "subject": "Hi",                                             |
|        "body": "Hello"                                              |
|    }                                                                 |
|    # cc is NOT in the dict (user didn't mention it)                 |
|                                                                      |
|    User: "Same email, CC jane@example.com"                           |
|    Result: send_email receives {                                    |
|        "recipient": "john@example.com",                             |
|        "subject": "Hi",                                             |
|        "body": "Hello",                                             |
|        "cc": "jane@example.com"                                      |
|    }                                                                 |
|    # cc IS in the dict (user mentioned it)                         |
|                                                                      |
+----------------------------------------------------------------------+
    """)

    input("\n>>> PRESS ENTER to continue...")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("\n" + "=" * 70)
    print("  UNDERSTANDING 'required' IN input_schema")
    print("=" * 70)

    print("""
+----------------------------------------------------------------------+
|                                                                      |
|  This program explains:                                               |
|                                                                      |
|  1. What is 'required'?                                              |
|  2. Where does Claude send the data?                                |
|  3. Aligned examples (step by step)                                 |
|  4. Empty list vs No required field                                 |
|  5. Common mistakes                                                 |
|  6. Visual comparison of scenarios                                  |
|  7. Code examples - what your tool receives                        |
|                                                                      |
|  KEY TAKEAWAY:                                                       |
|  "required" controls what goes in the dictionary that Claude        |
|  SENDS TO YOUR TOOL FUNCTION. Parameters in "required" MUST        |
|  be included. Parameters NOT in "required" CAN be skipped.           |
|                                                                      |
+----------------------------------------------------------------------+
    """)

    input("\n>>> PRESS ENTER to begin...")

    explain_required()
    explain_where_data_goes()
    show_aligned_examples()
    show_empty_vs_no_required()
    show_mistakes()
    show_visual_comparison()
    show_code_examples()

    print("""
+======================================================================+
|                                                                      |
|  WHAT JUST HAPPENED?                                                 |
|  ---------------------                                               |
|                                                                      |
|  You learned about "required" in Claude's input_schema:              |
|                                                                      |
|  1. "required" is a LIST that controls what parameters Claude       |
|     SENDS to your tool function.                                    |
|                                                                      |
|  2. Parameters in "required" list -> MUST be in the dict           |
|     Parameters NOT in "required" list -> CAN be skipped            |
|                                                                      |
|  3. When Claude calls your tool, it builds a dictionary and        |
|     passes it to your callback function via tool_input.             |
|                                                                      |
|  4. Only put truly essential parameters in "required"              |
|     to keep your tool flexible.                                      |
|                                                                      |
|  5. Handle optional parameters in your code with .get()            |
|     and provide default values there.                               |
|                                                                      |
+======================================================================+
    """)
