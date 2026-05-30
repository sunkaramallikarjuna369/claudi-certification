"""
+===========================================================================+
|                                                                           |
|  UNDERSTANDING "required" IN input_schema                                 |
|                                                                           |
|  A clear explanation with aligned examples!                             |
|                                                                           |
+===========================================================================
"""

import os
import sys
import json
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ANTHROPIC_API_KEY")

if not API_KEY:
    raise ValueError("Please add ANTHROPIC_API_KEY to your .env file")


# ============================================================================
# PART 1: What is "required"?
# ============================================================================

def explain_required():
    """Explain what 'required' means."""

    print("\n" + "=" * 70)
    print("  PART 1: WHAT IS 'required' ?")
    print("=" * 70)

    print("""
| =======================================================================
| THE SIMPLE ANSWER:
| =======================================================================
|
| "required" tells Claude which parameters it MUST provide.
|
| If a parameter is in "required" -> Claude MUST give it
| If a parameter is NOT in "required" -> It's optional (can skip it)
|
| =======================================================================
| VISUAL:
| =======================================================================
|
|     input_schema = {
|
|         "properties": {
|
|             "name": { "type": "string" }       <-- in required list
|             |                                     (MUST provide!)
|
|             "age": { "type": "integer" }        <-- NOT in required
|                                                 (CAN skip)
|         },
|
|         "required": ["name"]          <-- ONLY name is required!
|     }
|
| =======================================================================
|
| In this example:
| - "name" -> MUST be provided (required)
| - "age"  -> CAN skip (optional)
|
    """)

    input("\n>>> PRESS ENTER to continue...")


# ============================================================================
# PART 2: Aligned Examples - Step by Step
# ============================================================================

def show_aligned_examples():
    """Show examples with clear alignment."""

    print("\n" + "=" * 70)
    print("  PART 2: ALIGNED EXAMPLES")
    print("=" * 70)

    print("""
| =======================================================================
| EXAMPLE 1: Weather Tool
| =======================================================================
|
| We want a weather tool that:
| - MUST have: city name
| - CAN HAVE: temperature unit (defaults to celsius)
|
| LOOK AT THE STRUCTURE:
| ----------------------
    """)

    tool1 = {
        "name": "get_weather",
        "description": "Get weather for a city",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "Name of the city"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "Temperature unit"
                }
            },
            "required": ["city"]
        }
    }

    print("""
|     input_schema = {
|
|         "properties": {
|
|             "city": {
|                 "type": "string",
|                 "description": "Name of the city"
|             },
|             # =====> city is REQUIRED (it's in "required" list!)
|
|             "unit": {
|                 "type": "string",
|                 "enum": ["celsius", "fahrenheit"],
|                 "description": "Temperature unit"
|             }
|             # =====> unit is OPTIONAL (NOT in "required" list!)
|         },
|
|         # Look! Only "city" is in the required list!
|         "required": ["city"]
|     }
|
| =======================================================================
| WHAT HAPPENS WHEN USER SAYS:
| =======================================================================
|
| User: "What's weather in Tokyo?"
|
| Claude sends: {"city": "Tokyo"}
|              (unit is skipped - uses default!)
|
| User: "What's weather in Tokyo in fahrenheit?"
|
| Claude sends: {"city": "Tokyo", "unit": "fahrenheit"}
|
    """)

    input("\n>>> PRESS ENTER to continue...")

    print("""
| =======================================================================
| EXAMPLE 2: Calculator Tool
| =======================================================================
|
| We want a calculator that:
| - MUST have: expression to calculate
| - Nothing is optional (only one parameter)
|
| LOOK AT THE STRUCTURE:
| ----------------------
    """)

    tool2 = {
        "name": "calculator",
        "description": "Calculate math",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Math expression like 2+2"
                }
            },
            "required": ["expression"]  # expression is required
        }
    }

    print("""
|     input_schema = {
|
|         "properties": {
|
|             "expression": {
|                 "type": "string",
|                 "description": "Math expression like 2+2"
|             }         <-- Only ONE parameter, it's required!
|         },
|
|         "required": ["expression"]     <-- Look! Only expression!
|     }
|
| =======================================================================
| WHAT HAPPENS WHEN USER SAYS:
| =======================================================================
|
| User: "Calculate 1500 + 2500"
|
| Claude sends: {"expression": "1500 + 2500"}
|
| That's it! No optional parameters to worry about!
|
    """)

    input("\n>>> PRESS ENTER to continue...")

    print("""
| =======================================================================
| EXAMPLE 3: Email Tool (Multiple Required)
| =======================================================================
|
| We want an email tool that:
| - MUST have: recipient, subject, body
| - Nothing is optional
|
| LOOK AT THE STRUCTURE:
| ----------------------
    """)

    tool3 = {
        "name": "send_email",
        "description": "Send an email",
        "input_schema": {
            "type": "object",
            "properties": {
                "recipient": {
                    "type": "string",
                    "description": "Email address"
                },
                "subject": {
                    "type": "string",
                    "description": "Email subject"
                },
                "body": {
                    "type": "string",
                    "description": "Email body text"
                },
                "cc": {
                    "type": "string",
                    "description": "CC email address (optional)"
                }
            },
            # Note: All parameters are defined in "properties"
# but only "recipient", "subject", "body" are in "required" list
# "cc" is optional (not in required list)
"required": ["recipient", "subject", "body"]
        }
    }

    print("""
|     input_schema = {
|
|         "properties": {
|
|             "recipient": { "type": "string" },   <-- REQUIRED!
|             "subject":   { "type": "string" },   <-- REQUIRED!
|             "body":      { "type": "string" },   <-- REQUIRED!
|             "cc":        { "type": "string" }     <-- OPTIONAL!
|         },
|
|         "required": ["recipient", "subject", "body"]
|                     <-- Notice: "cc" is NOT in this list!
|                     <-- So cc is optional!
|     }
|
| =======================================================================
| WHAT HAPPENS WHEN USER SAYS:
| =======================================================================
|
| User: "Send email to john@email.com with subject 'Hi' and body 'Hello'"
|
| Claude sends: {
|     "recipient": "john@email.com",
|     "subject": "Hi",
|     "body": "Hello"
| }
| (cc is skipped)
|
| User: "Send email to john@email.com with subject 'Hi', body 'Hello', cc to jane@email.com"
|
| Claude sends: {
|     "recipient": "john@email.com",
|     "subject": "Hi",
|     "body": "Hello",
|     "cc": "jane@email.com"      <-- Optional parameter used!
| }
|
    """)

    input("\n>>> PRESS ENTER to continue...")


# ============================================================================
# PART 3: Empty vs No "required" field
# ============================================================================

def show_empty_vs_no_required():
    """Show the difference between empty list and no field."""

    print("\n" + "=" * 70)
    print("  PART 3: EMPTY LIST vs NO 'required' FIELD")
    print("=" * 70)

    print("""
| =======================================================================
| THESE TWO ARE DIFFERENT!
| =======================================================================
|
| OPTION A: Empty list
| --------------------
|     "required": []      <-- Empty list = ALL parameters optional!
|
| OPTION B: No "required" field at all
| ------------------------------------
|     (just don't include "required" at all)
|
| Both mean: "Nothing is required"
|
| But OPTION B is MORE COMMON and CLEANER.
|
| =======================================================================
| RECOMMENDED STYLE:
| =======================================================================
|
| DON'T WRITE:  "required": []
|
| DO THIS:      Just leave out the "required" field entirely!
|
| Example (CLEAN):
| ---------------
|     input_schema = {
|         "type": "object",
|         "properties": {
|             "city": {"type": "string"},
|             "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
|         }           <-- No "required" field = all optional!
|     }
|
    """)

    input("\n>>> PRESS ENTER to continue...")


# ============================================================================
# PART 4: Common Mistakes
# ============================================================================

def show_mistakes():
    """Show common mistakes with required."""

    print("\n" + "=" * 70)
    print("  PART 4: COMMON MISTAKES")
    print("=" * 70)

    print("""
| =======================================================================
| MISTAKE 1: Forgetting to put required parameter in list
| =======================================================================
|
| WRONG:
| -------
|     "properties": {
|         "city": {"type": "string"}    <-- We NEED this!
|     },
|     "required": []                    <-- WRONG! Empty list!
|
| RESULT: Claude might NOT send "city" because it's not required!
|
| CORRECT:
| --------
|     "properties": {
|         "city": {"type": "string"}
|     },
|     "required": ["city"]              <-- Right! Put it in the list!
|
| =======================================================================
| MISTAKE 2: Making everything required
| =======================================================================
|
| WRONG:
| -------
|     "properties": {
|         "name": {"type": "string"},
|         "age": {"type": "integer"},
|         "city": {"type": "string"},
|         "country": {"type": "string"}
|     },
|     "required": ["name", "age", "city", "country"]
|
| RESULT: Users must provide ALL 4, even when they only want to use one!
|         Tool becomes inflexible and hard to use.
|
| CORRECT:
| --------
|     "required": ["name"]              <-- Only truly required ones!
|
| =======================================================================
| MISTAKE 3: Not understanding what "required" means
| =======================================================================
|
| WRONG ASSUMPTION:
| -----------------
| "If I put parameter in 'required', it will have a default value"
|
| TRUTH:
| ------
| "required" only means "Claude MUST provide this parameter"
| It does NOT give a default value!
| If you need a default, handle it in your CODE!
|
| Example:
| --------
|     "properties": {
|         "unit": {
|             "type": "string",
|             "enum": ["celsius", "fahrenheit"]
|         }           <-- No default here!
|     },
|     "required": []      <-- unit is optional
|
| In your code:
|     unit = tool_input.get("unit", "celsius")   <-- Default in code!
|                             ^^^^^^^^^^^^^^
|                             Default value HERE!
|
    """)

    input("\n>>> PRESS ENTER to continue...")


# ============================================================================
# PART 5: Visual Comparison
# ============================================================================

def show_visual_comparison():
    """Show visual comparison of different scenarios."""

    print("\n" + "=" * 70)
    print("  PART 5: VISUAL COMPARISON")
    print("=" * 70)

    print("""
| =======================================================================
| SCENARIO A: No required parameters at all
| =======================================================================
|
| input_schema = {
|     "type": "object",
|     "properties": {
|         "name": {"type": "string"},
|         "age":  {"type": "integer"}
|     }
|     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
|     NO "required" field = All optional!
| }
|
| Claude can send: {}
|                  {}
|                  {"name": "John"}
|                  {"age": 25}
|                  {"name": "John", "age": 25}
|
| =======================================================================
| SCENARIO B: One required parameter
| =======================================================================
|
| input_schema = {
|     "type": "object",
|     "properties": {
|         "name": {"type": "string"},
|         "age":  {"type": "integer"}
|     },
|     "required": ["name"]
| }
|
| Claude MUST send: {"name": ...}           (at minimum!)
| Claude CAN add:    {"name": ..., "age": 25}
| Claude CANNOT send: {} or {"age": 25}
|
| =======================================================================
| SCENARIO C: Two required parameters
| =======================================================================
|
| input_schema = {
|     "type": "object",
|     "properties": {
|         "name": {"type": "string"},
|         "age":  {"type": "integer"},
|         "city": {"type": "string"}
|     },
|     "required": ["name", "age"]
| }
|
| Claude MUST send: {"name": ..., "age": ...}
| Claude CAN add:    {"name": ..., "age": ..., "city": "..."}
| Claude CANNOT send: {"name": "John"} only
|
| =======================================================================
| SUMMARY TABLE:
| =======================================================================
|
| required list           | What Claude MUST send
|--------------------------|---------------------------
| [] (empty)               | Nothing (all optional!)
| ["name"]                 | At least name
| ["name", "age"]          | At least name AND age
| (no field)               | Nothing (all optional!)
|
    """)

    input("\n>>> PRESS ENTER to continue...")


# ============================================================================
# PART 6: Live Demo
# ============================================================================

def show_live_demo():
    """Show live demo with Claude."""

    print("\n" + "=" * 70)
    print("  PART 6: LIVE DEMONSTRATION")
    print("=" * 70)

    print("""
| Let's test "required" in action!
|
| Tool: Greeting tool
| - "name" is REQUIRED
| - "language" is OPTIONAL (not in required list)
|
    """)

    input("\n>>> PRESS ENTER to test...")

    from anthropic import Anthropic

    client = Anthropic(api_key=API_KEY)

    # Tool with required field
    tools = [{
        "name": "greet",
        "description": "Greet someone",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Person's name"
                    # NOTE: "name" is in required list below!
                },
                "language": {
                    "type": "string",
                    "enum": ["english", "spanish"],
                    "description": "Language (optional)"
                    # NOTE: "language" is NOT in required list!
                }
            },
            "required": ["name"]  # <-- Only "name" is required!
        }
    }]

    print("\n| Tool structure:")
    print(json.dumps(tools[0], indent=4))
    print("\n| Notice: required = [\"name\"] only!")
    print("| This means 'name' is mandatory, 'language' is optional.")
    print("|")

    # Test 1: User provides only required parameter
    print("\n" + "-" * 50)
    print("TEST 1: User says 'Say hello to John'")
    print("-" * 50)

    messages = [{"role": "user", "content": "Say hello to John"}]

    response = client.messages.create(
        model="claude-haiku-4-5-20250601",
        max_tokens=512,
        messages=messages,
        tools=tools
    )

    print(f"| Claude called: {response.stop_reason}")

    for block in response.content:
        if block.type == "tool_use":
            print(f"| Tool: {block.name}")
            print(f"| Claude sent: {block.input}")
            print(f"| Notice: Only 'name' was sent (language is optional, skipped!)")

    # Test 2: User provides both parameters
    print("\n" + "-" * 50)
    print("TEST 2: User says 'Say hello to John in Spanish'")
    print("-" * 50)

    messages = [{"role": "user", "content": "Say hello to John in Spanish"}]

    response = client.messages.create(
        model="claude-haiku-4-5-20250601",
        max_tokens=512,
        messages=messages,
        tools=tools
    )

    print(f"| Claude called: {response.stop_reason}")

    for block in response.content:
        if block.type == "tool_use":
            print(f"| Tool: {block.name}")
            print(f"| Claude sent: {block.input}")
            print(f"| Notice: Both 'name' AND 'language' were sent!")

    print("\n| SUMMARY:")
    print("| - name is REQUIRED -> Claude always sends it")
    print("| - language is OPTIONAL -> Claude sends it only if user mentions it")


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
|
| This program explains:
|
| 1. What is 'required'?
| 2. Aligned examples (step by step)
| 3. Empty list vs No required field
| 4. Common mistakes
| 5. Visual comparison
| 6. Live demo with Claude
|
    """)

    input("\n>>> PRESS ENTER to begin...")

    explain_required()
    show_aligned_examples()
    show_empty_vs_no_required()
    show_mistakes()
    show_visual_comparison()
    show_live_demo()

    print("\n" + "=" * 70)
    print("  SUMMARY: 'required' MEANS...")
    print("=" * 70)
    print("""
|
| - Parameters in "required" -> MUST be provided by Claude
| - Parameters NOT in "required" -> Optional, can be skipped
| - Empty "required": [] -> All parameters are optional
| - No "required" field -> All parameters are optional
|
| TIP: Only put truly essential parameters in "required"
|      Keep it small for flexibility!
|
+==========================================================================+
    """)


"""
+===========================================================================+
|                                                                           |
|  QUICK REFERENCE CARD                                                    |
|                                                                           |
+===========================================================================+

| input_schema = {
|
|     "properties": {
|         "param1": {...},   <-- defined here
|         "param2": {...}    <-- defined here
|     },
|
|     "required": ["param1"]
|                  ^^^^^^^^^
|                  Only param1 is required!
|                  param2 is optional (not in list!)
| }
|
| RESULT:
| - Claude MUST send param1
| - Claude MAY send param2 (optional)
|
+===========================================================================+
"""