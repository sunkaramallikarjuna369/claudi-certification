"""
+===========================================================================+
|                                                                           |
|  COMPLETE GUIDE TO TOOLS: What, Why, and How                            |
|                                                                           |
|  Learn everything about tools from scratch!                              |
|                                                                           |
|  This program covers:                                                   |
|  - What is a tool?                                                       |
|  - Tool anatomy (name, description, input_schema)                         |
|  - Parameter types and validation                                         |
|  - Required vs optional fields                                            |
|  - Real examples of tools                                                 |
|  - How Claude uses tool definitions                                       |
|                                                                           |
+===========================================================================
"""

import os
import sys
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

INTERACTIVE_MODE = True

def wait_for_input(prompt: str = ""):
    if INTERACTIVE_MODE:
        input(f"\n>>> PRESS ENTER to continue {prompt}...")
    else:
        print(f"\n>>> Auto-continuing...")

def print_section(title: str):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


# ============================================================================
# PART 1: What is a Tool?
# ============================================================================

def part_what_is_tool():
    """Explain what a tool is in simple terms."""

    print_section("PART 1: WHAT IS A TOOL?")

    print("""
| =======================================================================
| THE SIMPLE ANSWER:
| =======================================================================
|
| A TOOL is a way to give Claude SPECIAL ABILITIES!
|
| Think of it like this:
|
|     WITHOUT TOOLS: Claude can only TALK (text in, text out)
|
|     WITH TOOLS:    Claude can also DO things like:
|                    - Search the web
|                    - Run code
|                    - Read files
|                    - Send emails
|                    - And MORE!
|
| =======================================================================
| REAL-WORLD EXAMPLE:
| =======================================================================
|
| Imagine you have a really smart assistant.
|
| You ask: "What's the weather today?"
|
| WITHOUT TOOL:
|     Assistant says: "I don't know, I can't check weather"
|
| WITH WEATHER TOOL:
|     Assistant uses tool -> Gets weather -> Tells you!
|
| =======================================================================
| TOOL = ABILITY = SUPERPOWER!
| =======================================================================
|     """)

    wait_for_input()


# ============================================================================
# PART 2: Tool Anatomy - The 3 Parts
# ============================================================================

def part_tool_anatomy():
    """Explain the 3 parts of a tool."""

    print_section("PART 2: TOOL ANATOMY - Every Tool Has 3 Parts")

    print("""
| Every tool definition has EXACTLY 3 parts:
|
+==========================================================================+
|                                                                          |
|   PART 1: "name"        - What is it called? (unique identifier)         |
|   PART 2: "description" - What does it do? When should Claude use it?  |
|   PART 3: "input_schema" - What information does it need?               |
|                                                                          |
+==========================================================================+
|
| Think of a tool like a RECIPE:
|
|     name:        The dish name (e.g., "Chocolate Cake")
|     description: The instructions (e.g., "Best for birthdays!")
|     input_schema: Ingredients needed (e.g., flour, sugar, chocolate)
|
| =======================================================================
| VISUAL REPRESENTATION:
| =======================================================================
|
|     +----------------------------------------------------------+
|     |  TOOL                                                     |
|     |                                                          |
|     |  +------------+                                          |
|     |  | name:      |  <-- What is it called?                   |
|     |  | "calculator"                                        |
|     |  +------------+                                          |
|     |                                                          |
|     |  +------------+                                          |
|     |  | description:|  <-- What does it do?                    |
|     |  | "Perform   |     When should Claude use it?            |
|     |  |  math..."  |                                          |
|     |  +------------+                                          |
|     |                                                          |
|     |  +------------+                                          |
|     |  |input_schema|  <-- What does it need as input?         |
|     |  |  {...}     |                                          |
|     |  +------------+                                          |
|     |                                                          |
|     +----------------------------------------------------------+
|
|     """)

    wait_for_input()


# ============================================================================
# PART 3: NAME - The First Part
# ============================================================================

def part_name():
    """Explain the name field."""

    print_section("PART 3: NAME - The First Part")

    print("""
| =======================================================================
| WHAT IS THE "name"?
| =======================================================================
|
| The "name" is a UNIQUE identifier for your tool.
|
| Rules for names:
| ----------------
| 1. Must be a string
| 2. Must be UNIQUE (no two tools with same name)
| 3. Should be lowercase with underscores (no spaces!)
| 4. Should describe what the tool does
| 5. No special characters (just letters, numbers, underscores)
|
| Good examples:
| --------------
|     "calculator"
|     "get_weather"
|     "search_wikipedia"
|     "send_email"
|
| Bad examples:
| -------------
|     "Calculator"     (capital letters - bad!)
|     "get weather"     (spaces - bad!)
|     "calculator!!"    (special chars - bad!)
|     "calc"            (too vague - what's calc?)
|
| =======================================================================
| IMPORTANT:
| =======================================================================
|
| The name is what Claude uses to CALL the tool!
|
| When Claude decides to use a tool, it says:
|     "I'll use the 'get_weather' tool"
|
| So make your names CLEAR and DESCRIPTIVE!
|
|     """)

    wait_for_input()


# ============================================================================
# PART 4: Description - The Second Part
# ============================================================================

def part_description():
    """Explain the description field."""

    print_section("PART 4: DESCRIPTION - The Second Part")

    print("""
| =======================================================================
| WHAT IS THE "description"?
| =======================================================================
|
| The "description" is your chance to TEACH Claude about the tool!
|
| It should explain:
| ------------------
| 1. What the tool does (the purpose)
| 2. When Claude should use it (the trigger)
| 3. Any important details the user needs to know
|
| This is ONE OF THE MOST IMPORTANT parts of a tool definition!
| A good description = Claude uses the tool correctly!
| A bad description = Claude might misuse or ignore the tool!
|
| =======================================================================
| WHAT TO INCLUDE:
| =======================================================================
|
| 1. What the tool does:
|    "Calculates mathematical expressions"
|
| 2. When to use it:
|    "Use this when user asks for math calculations"
|
| 3. Examples of inputs:
|    "e.g., '2 + 2', '10 * 5', '1500 + 2500'"
|
| =======================================================================
| EXAMPLE DESCRIPTIONS:
| =======================================================================
|
| TOOL 1: Calculator
| ------------------
| "Perform basic arithmetic calculations. Use this when the user asks
|  you to calculate math expressions like addition, subtraction,
|  multiplication, or division. The expression should contain only
|  numbers and operators (+, -, *, /)."
|
| TOOL 2: Get Weather
| ------------------
| "Get the current weather for a city. Use this when the user asks
|  about weather conditions. Returns temperature, conditions,
|  and humidity. Supports both celsius and fahrenheit."
|
| TOOL 3: Search Wikipedia
| ----------------------
| "Search Wikipedia for information about any topic. Use this when
|  the user wants to learn about people, places, history, science,
|  or any factual information. Returns a summary of the topic."
|
|     """)

    wait_for_input()


# ============================================================================
# PART 5: Input Schema - The Third Part
# ============================================================================

def part_input_schema():
    """Explain the input_schema field."""

    print_section("PART 5: INPUT_SCHEMA - The Third Part")

    print("""
| =======================================================================
| WHAT IS THE "input_schema"?
| =======================================================================
|
| The "input_schema" defines WHAT INPUT the tool needs to work.
|
| Think of it like the PARAMETERS of a function:
|
|     function calculate(expression: str):
|         ...
|
|     input_schema tells Claude what to pass!
|
| =======================================================================
| INPUT_SCHEMA STRUCTURE:
| =======================================================================
|
| input_schema = {
|     "type": "object",                    <-- Always "object"
|     "properties": {                      <-- List of parameters
|         "param_name": {                  <-- Parameter name
|             "type": "string",           <-- Data type
|             "description": "..."        <-- What this param does
|         }
|     },
|     "required": ["param_name"]           <-- Which params are mandatory
| }
|
|     """)

    wait_for_input()


# ============================================================================
# PART 6: Parameter Types
# ============================================================================

def part_parameter_types():
    """Explain different parameter types."""

    print_section("PART 6: PARAMETER TYPES")

    print("""
| =======================================================================
| DATA TYPES YOU CAN USE:
| =======================================================================
|
| +============+===============+=====================================+
| | TYPE       | EXAMPLE      | WHEN TO USE                        |
| +============+===============+=====================================+
| | "string"   | "Tokyo"      | Text, names, queries, messages     |
| | "number"   | 42           | Any numeric value (integer or float)|
| | "integer"  | 10           | Whole numbers only                  |
| | "boolean"  | true/false   | Yes/No, on/off, enable/disable      |
| | "array"    | [1, 2, 3]    | List of items                      |
| | "object"   | {key: value} | Nested data structure              |
| +============+===============+=====================================+
|
| =======================================================================
| EXAMPLE OF EACH TYPE:
| =======================================================================
|
| STRING:
| -------
|     "city": {
|         "type": "string",
|         "description": "Name of the city"
|     }
|     Usage: {"city": "Tokyo"}
|
| NUMBER:
| -------
|     "temperature": {
|         "type": "number",
|         "description": "Temperature value"
|     }
|     Usage: {"temperature": 25.5}
|
| INTEGER:
| -------
|     "count": {
|         "type": "integer",
|         "description": "Number of items"
|     }
|     Usage: {"count": 5}
|
| BOOLEAN:
| -------
|     "include_celsius": {
|         "type": "boolean",
|         "description": "Show temperature in celsius"
|     }
|     Usage: {"include_celsius": true}
|
| ARRAY:
| -------
|     "cities": {
|         "type": "array",
|         "description": "List of city names",
|         "items": {"type": "string"}
|     }
|     Usage: {"cities": ["Tokyo", "Paris", "New York"]}
|
| ENUM (Pre-defined choices):
| -------
|     "unit": {
|         "type": "string",
|         "enum": ["celsius", "fahrenheit"],
|         "description": "Temperature unit"
|     }
|     Usage: {"unit": "celsius"}
|
|     """)

    wait_for_input()


# ============================================================================
# PART 7: Required vs Optional Parameters
# ============================================================================

def part_required_optional():
    """Explain required vs optional parameters."""

    print_section("PART 7: REQUIRED vs OPTIONAL PARAMETERS")

    print("""
| =======================================================================
| THE "required" FIELD:
| =======================================================================
|
| The "required" list tells Claude which parameters are MANDATORY.
|
| If a parameter is NOT in the "required" list, it's OPTIONAL.
|
| =======================================================================
| EXAMPLE:
| =======================================================================
|
| input_schema = {
|     "type": "object",
|     "properties": {
|         "city": {
|             "type": "string",
|             "description": "Name of the city (REQUIRED)"
|         },
|         "unit": {
|             "type": "string",
|             "enum": ["celsius", "fahrenheit"],
|             "description": "Temperature unit (OPTIONAL)"
|         }
|     },
|     "required": ["city"]        <-- Only "city" is required!
| }
|
| In this example:
| ----------------
| - "city" is REQUIRED - Claude MUST provide it
| - "unit" is OPTIONAL - Claude can skip it (will use default)
|
| =======================================================================
| WHEN TO MAKE PARAMETERS REQUIRED:
| =======================================================================
|
| Required when:
| - The tool CANNOT work without it
| - It's critical for the operation
|
| Optional when:
| - There's a sensible default value
| - The user might not want to specify it
|
| =======================================================================
| TIP:
| =======================================================================
|
| Keep "required" as small as possible!
| Only mark truly essential parameters as required.
| This makes tools more flexible and easier to use.
|
|     """)

    wait_for_input()


# ============================================================================
# PART 8: Complete Tool Example
# ============================================================================

def part_complete_example():
    """Show a complete tool definition."""

    print_section("PART 8: COMPLETE TOOL EXAMPLE")

    print("""
| =======================================================================
| EXAMPLE: WEATHER TOOL
| =======================================================================
|
| Let's build a complete weather tool step by step:
|
| STEP 1: Name
| -----------
| What should we call it? -> "get_weather"
|
| STEP 2: Description
| ------------------
| What does it do?
| "Get the current weather for a city. Use this when the user asks
|  about weather conditions like temperature, rain, or humidity.
|  Returns the current conditions and temperature."
|
| STEP 3: Input Schema
| ------------------
| What does it need?
| - city (required): Which city?
| - unit (optional): celsius or fahrenheit?
|
| =======================================================================
| THE COMPLETE TOOL:
| =======================================================================
|
    """)

    tool_example = {
        "name": "get_weather",
        "description": "Get the current weather for a city. Use this when the user asks about weather conditions like temperature, rain, or humidity. Returns the current conditions and temperature in the requested unit.",
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
                    "description": "The temperature unit to use. Defaults to celsius if not specified."
                }
            },
            "required": ["city"]
        }
    }

    import json
    print(json.dumps(tool_example, indent=4))

    print("""
|
| =======================================================================
| HOW CLAUDE SEES THIS TOOL:
| =======================================================================
|
| Claude reads this and understands:
|
| - Name: "get_weather"
| - When to use: When user asks about weather
| - Required input: "city" (must provide!)
| - Optional input: "unit" (defaults to celsius)
|
| When Claude decides to use this tool, it creates:
|
|     {
|         "name": "get_weather",
|         "input": {"city": "Tokyo", "unit": "celsius"}
|     }
|
| Your code then receives: tool_name="get_weather", input={...}
|
|     """)

    wait_for_input()


# ============================================================================
# PART 9: Multiple Tools Example
# ============================================================================

def part_multiple_tools():
    """Show how to define multiple tools."""

    print_section("PART 9: MULTIPLE TOOLS")

    print("""
| =======================================================================
| YOU CAN HAVE MULTIPLE TOOLS!
| =======================================================================
|
| When you create the tools list, just add more tool objects:
|
| tools = [
|
|     TOOL 1: Calculator
|     {
|         "name": "calculator",
|         "description": "...",
|         "input_schema": {...}
|     },
|
|     TOOL 2: Get Weather
|     {
|         "name": "get_weather",
|         "description": "...",
|         "input_schema": {...}
|     },
|
|     TOOL 3: Search Wikipedia
|     {
|         "name": "search_wiki",
|         "description": "...",
|         "input_schema": {...}
|     }
|
| ]
|
| Claude can use ANY of these tools as needed!
|
| =======================================================================
| COMPLETE MULTI-TOOL EXAMPLE:
| =======================================================================
|
|     """)

    tools = [
        {
            "name": "calculator",
            "description": "Perform basic arithmetic calculations. Use this when the user asks you to calculate math expressions. Supports addition (+), subtraction (-), multiplication (*), and division (/).",
            "input_schema": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The mathematical expression to evaluate (e.g., '2 + 2', '10 * 5', '1500 + 2500')"
                    }
                },
                "required": ["expression"]
            }
        },
        {
            "name": "get_weather",
            "description": "Get the current weather for a city. Use this when the user asks about weather conditions. Returns temperature, conditions, and humidity.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The name of the city to get weather for"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Temperature unit. Defaults to celsius."
                    }
                },
                "required": ["city"]
            }
        },
        {
            "name": "search_wiki",
            "description": "Search Wikipedia for information about any topic. Use this when the user wants to learn about people, places, history, or factual information.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to look up on Wikipedia"
                    }
                },
                "required": ["query"]
            }
        }
    ]

    print(f"Defined {len(tools)} tools:")
    for i, tool in enumerate(tools, 1):
        print(f"\n  Tool {i}: {tool['name']}")
        print(f"           {tool['description'][:60]}...")

    print("""
|
| When you pass this to Claude:
|
|     response = client.messages.create(
|         ...
|         tools=tools
|     )
|
| Claude can use ANY of these tools as needed!
|
|     """)

    wait_for_input()


# ============================================================================
# PART 10: Visual Summary
# ============================================================================

def part_visual_summary():
    """Show a visual summary of tool structure."""

    print_section("PART 10: VISUAL SUMMARY")

    print("""
+==========================================================================+
|                                                                          |
|   TOOL STRUCTURE - ONE PICTURE TO REMEMBER IT ALL                        |
|                                                                          |
+==========================================================================+

    tools = [
        {
            "name": "tool_name_here",
            |       |
            |       +--> Must be unique, lowercase, descriptive
            |
            "description": "What this tool does and when to use it",
            |              |
            |              +--> Teach Claude when to use this tool
            |
            "input_schema": {
                |   "type": "object",              <-- Always "object"
                |
                "properties": {                   <-- List of parameters
                |   |
                |   +--> "param_name": {
                |           "type": "string",   <-- Data type
                |           "description": "..." <-- What it means
                |           "enum": [...]       <-- Optional: allowed values
                |       }
                |
                "required": ["param1"]           <-- Mandatory params only
            }
        }
    ]


+==========================================================================+
|                                                                          |
|   QUICK REFERENCE: COMMON PATTERNS                                       |
|                                                                          |
+==========================================================================+

| Pattern                          | Example                             |
+----------------------------------+-------------------------------------+
| String parameter                 | "type": "string"                    |
| Number parameter                 | "type": "number"                    |
| Choices (enum)                   | "enum": ["a", "b", "c"]            |
| Optional with default            | Not in "required" list              |
| Required parameter               | "required": ["city", "query"]      |
| Array of strings                 | "type": "array", "items": {"type": "string"} |


+==========================================================================+
|                                                                          |
|   TEST YOURSELF!                                                          |
|                                                                          |
+==========================================================================+

| What are the 3 parts of a tool?
| > name, description, input_schema
|
| What does "required" do?
| > Lists which parameters MUST be provided
|
| What type should you use for a yes/no option?
| > "boolean"
|
| What's the difference between "number" and "integer"?
| > "number" allows decimals, "integer" is whole numbers only
|
|     """)

    wait_for_input()


# ============================================================================
# PART 11: Live Demo - Create and Use a Tool
# ============================================================================

def part_live_demo():
    """Live demo showing tool creation and usage."""

    print_section("PART 11: LIVE DEMONSTRATION")

    print("""
| Now let's see it in ACTION!
|
| We'll:
| 1. Define a simple tool
| 2. Ask Claude to use it
| 3. See what Claude sends back
|
|     """)

    wait_for_input("(Starting demo)")

    # Define a simple greeting tool
    tools = [
        {
            "name": "greet_user",
            "description": "Greet a user with a personalized message. Use this when you want to say hello to the user. Returns a greeting with their name.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The user's name to greet"
                    },
                    "language": {
                        "type": "string",
                        "enum": ["english", "spanish", "french", "japanese"],
                        "description": "Language for greeting. Defaults to english."
                    }
                },
                "required": ["name"]
            }
        }
    ]

    print("\n| Tool we created:")
    print(f"| Name: greet_user")
    print(f"| Description: {tools[0]['description']}")
    print(f"| Required: name")
    print(f"| Optional: language")
    print("|")

    wait_for_input("(Understanding our tool)")

    # Ask Claude to use the tool
    print("\n| User: 'Please greet John in Spanish'")
    print("|")

    messages = [{
        "role": "user",
        "content": "Please greet John in Spanish. Use the greet_user tool."
    }]

    print("| Sending to Claude with our tool available...")
    print("|")

    response = client.messages.create(
        model="claude-haiku-4-5-20250601",
        max_tokens=1024,
        messages=messages,
        tools=tools,
    )

    print(f"| Claude responded!")
    print(f"| stop_reason: {response.stop_reason}")
    print(f"|")

    if response.stop_reason == "tool_use":
        print("| Claude wants to use our tool!")
        print("|")
        for block in response.content:
            if block.type == "tool_use":
                print(f"| Tool name: {block.name}")
                print(f"| Tool input: {block.input}")
                print("|")
                print("| This is what Claude sent to our tool executor!")
                print("| Our code receives: tool_name, tool_input")

                # Execute the tool
                name = block.input.get("name", "")
                language = block.input.get("language", "english")

                greetings = {
                    "english": f"Hello, {name}! Nice to meet you!",
                    "spanish": f"Holla, {name}! Mucho gusto!",
                    "french": f"Bonjour, {name}! Enchante!",
                    "japanese": f"Konnichiwa, {name}! Hajimemashite!"
                }

                result = greetings.get(language, greetings["english"])

                print("|")
                print(f"| Tool result: {result}")
                print("|")
                print("| This result goes back to Claude!")

    elif response.stop_reason == "end_turn":
        print("| Claude didn't use the tool.")
        for block in response.content:
            if block.type == "text":
                print(f"| Claude said: {block.text}")

    print("|")
    wait_for_input("(Demo complete)")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Fix stdout encoding for Windows
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("\n" + "=" * 70)
    print("  COMPLETE GUIDE TO TOOLS - BEGINNER EDITION")
    print("=" * 70)
    print("""
|
| This program teaches you EVERYTHING about tools:
|
| 1. What is a tool?
| 2. Tool anatomy (3 parts)
| 3. The "name" field
| 4. The "description" field
| 5. The "input_schema" field
| 6. Parameter types
| 7. Required vs optional
| 8. Complete tool example
| 9. Multiple tools
| 10. Visual summary
| 11. Live demo with Claude
|
| Press ENTER to begin!
|
    """)

    wait_for_input()

    part_what_is_tool()
    part_tool_anatomy()
    part_name()
    part_description()
    part_input_schema()
    part_parameter_types()
    part_required_optional()
    part_complete_example()
    part_multiple_tools()
    part_visual_summary()
    part_live_demo()

    print("\n" + "=" * 70)
    print("  TOOL GUIDE COMPLETE!")
    print("=" * 70)
    print("""
|
| KEY TAKEAWAYS:
|
| 1. EVERY tool has 3 parts: name, description, input_schema
|
| 2. NAME: Unique identifier (lowercase, no spaces)
|
| 3. DESCRIPTION: Teach Claude when and how to use it
|
| 4. INPUT_SCHEMA: Define parameters (type, description, required)
|
| 5. TYPES: string, number, integer, boolean, array, enum
|
| 6. REQUIRED: Only mark essential parameters as required
|
| 7. Multiple tools = Multiple superpowers for Claude!
|
| NOW YOU KNOW EVERYTHING ABOUT TOOLS!
|
+==========================================================================+
    """)


"""
+===========================================================================+
|                                                                           |
|  EXTRA: Quick Reference Sheet                                            |
|                                                                           |
+===========================================================================+

| TOOL TEMPLATE:
| --------------
| {
|     "name": "your_tool_name",
|     "description": "What it does and when to use it",
|     "input_schema": {
|         "type": "object",
|         "properties": {
|             "param1": {
|                 "type": "string",
|                 "description": "What this parameter does"
|             },
|             "param2": {
|                 "type": "string",
|                 "enum": ["option1", "option2"],
|                 "description": "Pre-defined choices"
|             }
|         },
|         "required": ["param1"]
|     }
| }

| COMMON ERRORS TO AVOID:
| -----------------------
| - Forgetting the "type": "object" in input_schema
| - Not including required parameters in "required" list
| - Using spaces or capitals in tool names
| - Writing vague descriptions that don't help Claude
| - Making too many parameters required

| BEST PRACTICES:
| ---------------
| - Keep tool names clear and descriptive
| - Write detailed descriptions (help Claude understand)
| - Only mark truly required parameters
| - Use enum for limited choices
| - Test your tools with Claude!

+===========================================================================+
"""