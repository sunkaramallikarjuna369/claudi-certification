"""
+===========================================================================+
|                                                                           |
|  PRACTICE 2: POSTTOOLUSE - DATA NORMALIZATION                           |
|                                                                           |
|  PostToolUse hooks handle heterogeneous formats from different tools.      |
|  The model receives consistent data regardless of source tool.            |
|                                                                           |
|  Example: Unix timestamps --> ISO dates, numeric codes --> readable      |
|           strings, mixed formats --> consistent structure                 |
|                                                                           |
+===========================================================================

===========================================================================
 VISUAL: THE HETEROGENEOUS DATA PROBLEM
===========================================================================

    +======================================================================+
    ||                                                                  ||
    ||  PROBLEM: Different tools return data in different formats:      ||
    ||                                                                  ||
    ||  +----------------------+----------------------------------------+|
    ||  | TOOL                 | RAW OUTPUT                            ||
    ||  +----------------------+----------------------------------------+|
    ||  | weather_api          | {"temp": 72, "date": 1704067200}     ||
    ||  | (Returns Unix time)  |                                        ||
    ||  +----------------------+----------------------------------------+|
    ||  | stock_api            | {"price": 150.25, "trend": 1}         ||
    ||  | (Returns codes)      |                                        ||
    ||  +----------------------+----------------------------------------+|
    ||  | calendar_api         | {"event": "Party", "date": "25/12/24"}||
    ||  | (Returns DD/MM/YY)   |                                        ||
    ||  +----------------------+----------------------------------------+|
    ||  | database             | {"id": 12345, "created": 1704067200}  ||
    ||  | (Returns mixed)      |                                        ||
    ||  +----------------------+----------------------------------------+|
    ||                                                                  ||
    ||  Model must figure out how to interpret each format!             ||
    ||                                                                  ||
    +======================================================================+

===========================================================================
 VISUAL: THE NORMALIZATION SOLUTION
===========================================================================

    +======================================================================+
    ||                                                                  ||
    ||  SOLUTION: PostToolUse normalizes ALL data to consistent format: ||
    ||                                                                  ||
    ||  +----------------------+----------------------------------------+|
    ||  | TOOL                 | NORMALIZED OUTPUT                      ||
    ||  +----------------------+----------------------------------------+|
    ||  | weather_api          | {"temp": "72F", "date": "2024-01-01"} ||
    ||  +----------------------+----------------------------------------+|
    ||  | stock_api            | {"price": "$150.25", "trend": "rising"}|
    ||  +----------------------+----------------------------------------+|
    ||  | calendar_api         | {"event": "Party", "date": "2024-12-25"}|
    ||  +----------------------+----------------------------------------+|
    ||  | database             | {"id": "USR-12345", "created": "2024-01-01"}|
    ||  +----------------------+----------------------------------------+|
    ||                                                                  ||
    ||  Model sees CONSISTENT format regardless of source!               ||
    ||                                                                  ||
    +======================================================================+

===========================================================================
 REAL-TIME SCENARIO: When This Concept Breaks Things
===========================================================================

    SCENARIO: Multi-Source Financial Dashboard

    An AI agent is building a financial dashboard. It queries three
    different APIs:

    +======================================================================+
    ||                                                                  ||
    ||  API 1 (Stock): {"symbol": "AAPL", "price": 182.52, "change": -2.5}|
    ||  API 2 (Crypto): {"asset": "BTC", "value": 43500, "delta": -150}  ||
    ||  API 3 (Forex): {"pair": "EUR/USD", "rate": 1.087, "direction": 1}||
    ||                                                                  ||
    ||  WITHOUT PostToolUse normalization:                              ||
    ||  ----------------------------------------------------------------  ||
    ||  Model sees:                                                      ||
    ||  - "change": -2.5 (what unit? dollars? percent?)                 ||
    ||  - "delta": -150 (same question!)                                ||
    ||  - "direction": 1 (what does 1 mean?)                           ||
    ||                                                                  ||
    ||  Agent tries to compare: "-2.5 vs -150 vs 1"                    ||
    ||  Gets confused, makes wrong recommendation!                      ||
    ||                                                                  ||
    +======================================================================+

    +======================================================================+
    ||                                                                  ||
    ||  WITH PostToolUse normalization:                                  ||
    ||  ----------------------------------------------------------------  ||
    ||  PostToolUse normalizes to:                                       ||
    ||  - Stock: {"price": "$182.52", "change": "-2.5%", "direction": "down"}|
    ||  - Crypto: {"price": "$43,500", "change": "-$150 (-0.34%)", "direction": "down"}|
    ||  - Forex: {"rate": "1.087", "change": "+0.12%", "direction": "up"}||
    ||                                                                  ||
    ||  Model sees consistent format:                                    ||
    ||  - All have "direction": "up/down"                               ||
    ||  - All have human-readable prices                                ||
    ||  - All have consistent change format                             ||
    ||                                                                  ||
    ||  Agent makes correct comparison and recommendation!               ||
    ||                                                                  ||
    +======================================================================+

===========================================================================
 MISTAKES DEVELOPERS MAKE
===========================================================================

    MISTAKE #1: Trying to normalize in PreToolUse
    -----------------------------------------------------------------------
    PreToolUse on get_data:
        # WRONG: No data exists yet!
        result['date'] = convert_timestamp(result['timestamp'])  # None!
    -----------------------------------------------------------------------
    WHY IT BREAKS: PreToolUse runs BEFORE execution. No result to transform!
    FIX: Use PostToolUse - it runs AFTER execution when data exists.

    MISTAKE #2: Normalizing in the tool itself instead of hook
    -----------------------------------------------------------------------
    def get_weather(location):
        raw_data = fetch_weather(location)
        # WRONG: Tool should return raw data, hook should transform
        return {
            "temp": fahrenheit_to_celsius(raw_data['temp']),
            "date": unix_to_iso(raw_data['timestamp'])
        }
    -----------------------------------------------------------------------
    WHY IT BREAKS: Tool loses original data. Can't audit raw values.
    If you need both raw and normalized, normalize in PostToolUse.

    MISTAKE #3: Not handling unknown codes gracefully
    -----------------------------------------------------------------------
    def normalize_status(code):
        # WRONG: No fallback for unknown codes!
        return status_map[code]  # KeyError if code not in map!
    -----------------------------------------------------------------------
    WHY IT BREAKS: One unknown code crashes everything.
    FIX: Always use .get() with a fallback value.

    MISTAKE #4: Mutating the original result instead of copying
    -----------------------------------------------------------------------
    def posttooluse_hook(tool_name, result):
        # WRONG: Modifying original!
        result['normalized'] = True
        return result
    -----------------------------------------------------------------------
    WHY IT BREAKS: Side effects, hard to debug, breaks auditing.
    FIX: Always copy the result first: result = result.copy()

===========================================================================
 INTERVIEW Q&A: Expert Answer Frameworks
===========================================================================

    Q1: "Why is data normalization important in multi-tool systems?"
    ----------------------------------------------------------------
    TEMPLATE:
    "In production systems, different tools return data in different
    formats - Unix timestamps vs ISO dates, numeric codes vs strings,
    different conventions for null values or missing fields.

    Without normalization, the model must figure out each format. This
    leads to:
    - Inconsistent interpretation (did -2.5 mean dollars or percent?)
    - Parsing errors (what if the format changes?)
    - Confusing model responses (model doesn't know what to compare)

    PostToolUse normalizes all data to consistent format before the
    model sees it, so the model always works with predictable data."

    KEY PHRASE: "Consistent format regardless of source tool"

    ----------------------------------------------------------------

    Q2: "What kinds of transformations can PostToolUse perform?"
    ----------------------------------------------------------------
    TEMPLATE:
    "PostToolUse can perform any data transformation:

    1. Format conversion:
       - Unix timestamps to ISO dates
       - DD/MM/YYYY to YYYY-MM-DD
       - Numbers to formatted strings ($1,234.56)

    2. Code translation:
       - Numeric status codes to readable strings (200 --> 'success')
       - Magic numbers to semantic values (1 --> 'rising')
       - Internal codes to external representations

    3. Structure normalization:
       - Flatten nested structures
       - Rename fields for consistency
       - Add computed fields

    4. Metadata enrichment:
       - Add timestamps
       - Add source information
       - Add confidence scores"

    KEY PHRASE: "Anything that makes data more usable by the model"

    ----------------------------------------------------------------

    Q3: "Can PostToolUse be used to filter sensitive data?"
    ----------------------------------------------------------------
    TEMPLATE:
    "Yes. PostToolUse can strip sensitive data from results before
    the model sees them. Examples:
    - Remove internal IDs or system fields
    - Redact PII (social security numbers, etc.)
    - Strip debug information
    - Remove fields the model doesn't need

    This is different from blocking - the tool has already executed,
    but PostToolUse can ensure the model only sees appropriate data."

    KEY PHRASE: "Filter, not block - the action already happened"

===========================================================================
 VISUAL: POSTTOOLUSE EXECUTION FLOW
===========================================================================

    +======================================================================+
    ||                                                                  ||
    ||  POSTTOOLUSE NORMALIZATION FLOW:                                ||
    ||                                                                  ||
    ||    1. Tool executes                                              ||
    ||           |                                                      ||
    ||           v                                                      ||
    ||    2. Raw result returned                                        ||
    ||       {"timestamp": 1704067200, "price": 150}                   ||
    ||           |                                                      ||
    ||           v                                                      ||
    ||    3. [POSTTOOLUSE] runs - transforms data                       ||
    ||       {"date": "2024-01-01", "price_display": "$150.00"}        ||
    ||           |                                                      ||
    ||           v                                                      ||
    ||    4. Model sees only normalized result                          ||
    ||                                                                  ||
    +======================================================================+

===========================================================================
 CODE PATTERN: PostToolUse Normalization
===========================================================================

    def normalize_timestamp_to_iso(timestamp):
        """Convert Unix timestamp to ISO date string."""
        from datetime import datetime
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d")

    def normalize_status_code(code):
        """Convert numeric status codes to human-readable strings."""
        status_map = {
            0: "inactive",
            1: "pending",
            2: "active",
            200: "success",
            400: "bad_request",
            500: "server_error"
        }
        return status_map.get(code, f"unknown_code_{code}")

    def posttooluse_hook(tool_name, raw_result):
        """
        PostToolUse hook - transforms raw data into consistent format.
        IMPORTANT: Tool already executed, cannot block here!
        """
        print(f"\n   [POSTTOOLUSE] Transforming {tool_name} output...")

        result = raw_result.copy()  # Always copy!

        if tool_name == "weather_api":
            # Convert timestamps
            if "timestamp" in result:
                result["date"] = normalize_timestamp_to_iso(result["timestamp"])
                del result["timestamp"]
            # Format numbers
            if "temperature" in result:
                result["temperature"] = f"{result['temperature']}F"

        elif tool_name == "stock_api":
            # Convert codes to readable strings
            if "status_code" in result:
                result["status"] = normalize_status_code(result["status_code"])
                del result["status_code"]

        return result

===========================================================================
 WHAT WE HAVE LEARNT SUMMARY
===========================================================================

    +======================================================================+
    ||                                                                  ||
    ||              WHAT WE HAVE LEARNT                                 ||
    ||              =====================                                 ||
    ||                                                                  ||
    +======================================================================+

    1. THE PROBLEM:
       - Different tools return data in different formats
       - Unix timestamps, DD/MM/YYYY, numeric codes, etc.
       - Model must parse each format differently
       - Leads to confusion and errors

    2. THE SOLUTION:
       - PostToolUse hook runs AFTER tool execution
       - Transforms raw data into consistent format
       - Model sees normalized data regardless of source

    3. WHAT POSTTOOLUSE CAN DO:
       - Convert timestamps to readable dates
       - Translate numeric codes to strings
       - Standardize date formats across tools
       - Add contextual metadata
       - Filter sensitive fields

    4. WHAT POSTTOOLUSE CANNOT DO:
       - Block tool execution (too late!)
       - Access data before it exists (use PreToolUse for that)

    5. KEY INSIGHT:
       PostToolUse is for TRANSFORMATION, not BLOCKING.
       The tool already executed - the hook just normalizes the output.

    6. COMMON TRANSFORMATIONS:
       - Unix timestamp --> ISO date (YYYY-MM-DD)
       - Numeric code --> readable string
       - Mixed formats --> consistent structure
       - Raw values --> formatted display values

"""

import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY", "")
api_base = os.getenv("ANTHROPIC_API_BASE", "")

from anthropic import Anthropic

client_kwargs = {"api_key": api_key} if api_key else {}
if api_base:
    client_kwargs["base_url"] = api_base
client = Anthropic(**client_kwargs)


# ========================================================================
# STATE: Simulate tool outputs with different formats
# ========================================================================

class ToolOutputSimulator:
    """Simulates different tool outputs with varying data formats."""

    def __init__(self):
        # These simulate different MCP tools returning data in different formats
        self.tools = {
            "weather_api": self.weather_api_output,
            "stock_api": self.stock_api_output,
            "calendar_api": self.calendar_api_output,
            "database": self.database_output
        }

    def weather_api_output(self):
        """Weather API returns Unix timestamps."""
        return {
            "source": "weather_api",
            "data": {
                "timestamp": 1704067200,
                "temperature": 72,
                "condition": "sunny"
            }
        }

    def stock_api_output(self):
        """Stock API returns numeric codes."""
        return {
            "source": "stock_api",
            "data": {
                "status_code": 200,
                "price_change": -2.5,
                "trend": 1,
                "volume": 1500000
            }
        }

    def calendar_api_output(self):
        """Calendar API returns dates in DD/MM/YYYY."""
        return {
            "source": "calendar_api",
            "data": {
                "event_date": "25/12/2024",
                "reminder": "15/12/2024",
                "created": "01/12/2024"
            }
        }

    def database_output(self):
        """Database returns mixed formats."""
        return {
            "source": "database",
            "data": {
                "id": "USR-12345",
                "created_unix": 1704067200,
                "status": "active",
                "flags": [0, 0, 1, 0]
            }
        }


simulator = ToolOutputSimulator()


# ========================================================================
# POSTTOOLUSE HOOKS: Data Normalization
# ========================================================================

def normalize_timestamp_to_iso(timestamp):
    """Convert Unix timestamp to ISO date string."""
    from datetime import datetime
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d")


def normalize_date_to_iso(date_str):
    """Convert DD/MM/YYYY to ISO date string."""
    from datetime import datetime
    dt = datetime.strptime(date_str, "%d/%m/%Y")
    return dt.strftime("%Y-%m-%d")


def normalize_status_code(code):
    """Convert numeric status codes to human-readable strings."""
    status_map = {
        0: "inactive",
        1: "pending",
        2: "active",
        3: "suspended",
        200: "success",
        400: "bad_request",
        401: "unauthorized",
        403: "forbidden",
        500: "server_error"
    }
    return status_map.get(code, f"unknown_code_{code}")


def normalize_trend_code(code):
    """Convert trend code to human-readable."""
    trend_map = {
        -1: "declining",
        0: "stable",
        1: "rising"
    }
    return trend_map.get(code, "unknown")


def normalize_flag_array(flags):
    """Convert numeric flags to boolean."""
    return [bool(f) for f in flags]


def post_tooluse_hook(tool_output):
    """
    PostToolUse hook - normalizes data from various tools.
    This runs AFTER tool execution but BEFORE model sees results.
    """
    print("\n" + "=" * 60)
    print("POSTTOOLUSE HOOK: Data Normalization")
    print("=" * 60)

    print(f"\n   Tool: {tool_output['source']}")
    print(f"   Raw data: {tool_output['data']}")

    source = tool_output['source']
    data = tool_output['data'].copy()

    # Normalize based on source tool
    if source == "weather_api":
        print("\n   [NORMALIZING] Converting timestamps to ISO dates...")
        data['event_date'] = normalize_timestamp_to_iso(data['timestamp'])
        data['temperature'] = f"{data['temperature']}F"
        del data['timestamp']

    elif source == "stock_api":
        print("\n   [NORMALIZING] Converting status codes to readable strings...")
        data['status'] = normalize_status_code(data['status_code'])
        data['trend_description'] = normalize_trend_code(data['trend'])
        del data['status_code']
        del data['trend']

    elif source == "calendar_api":
        print("\n   [NORMALIZING] Converting DD/MM/YYYY to ISO dates...")
        data['event_date'] = normalize_date_to_iso(data['event_date'])
        data['reminder_date'] = normalize_date_to_iso(data['reminder'])
        data['created_date'] = normalize_date_to_iso(data['created'])
        del data['event_date']  # Will be replaced
        del data['reminder']
        del data['created']

    elif source == "database":
        print("\n   [NORMALIZING] Converting mixed formats...")
        data['created_date'] = normalize_timestamp_to_iso(data['created_unix'])
        data['status'] = data['status']
        data['flags_array'] = normalize_flag_array(data['flags'])
        del data['created_unix']
        del data['id']
        del data['flags']

    print(f"\n   Normalized data: {data}")

    return {
        "success": True,
        "normalized": data
    }


def demonstrate_normalization_problem():
    """
    Show the problem that PostToolUse solves.
    """
    print("\n" + "=" * 70)
    print("THE PROBLEM: Heterogeneous Data Formats")
    print("=" * 70)

    print("""
    +======================================================================+
    ||                                                                  ||
    ||  WITHOUT PostToolUse normalization:                             ||
    ||                                                                  ||
    ||  Model receives raw data in various formats:                    ||
    ||                                                                  ||
    ||  Tool A: {"timestamp": 1704067200}  <-- Unix timestamp           ||
    ||  Tool B: {"date": "25/12/2024"}     <-- DD/MM/YYYY               ||
    ||  Tool C: {"status_code": 200}       <-- Numeric code              ||
    ||  Tool D: {"trend": 1}              <-- Magic number              ||
    ||                                                                  ||
    ||  Model must figure out how to interpret each format!            ||
    ||  Inconsistent behavior based on source tool.                    ||
    ||  Potential parsing errors and confusion.                        ||
    ||                                                                  ||
    +======================================================================+
    """)

    print("\nWITHOUT PostToolUse:")
    print("-" * 50)
    for source in ["weather_api", "stock_api", "calendar_api", "database"]:
        raw = simulator.tools[source]()
        print(f"   {source}: {raw['data']}")

    print("\n" + "-" * 50)
    print("Model sees: mixed formats, must parse each differently")


def demonstrate_normalization_solution():
    """
    Show how PostToolUse normalizes all data.
    """
    print("\n" + "=" * 70)
    print("THE SOLUTION: PostToolUse Normalization")
    print("=" * 70)

    print("""
    +======================================================================+
    ||                                                                  ||
    ||  WITH PostToolUse normalization:                                  ||
    ||                                                                  ||
    ||  Tool A: {"timestamp": 1704067200} --> {"date": "2024-01-01"}    ||
    ||  Tool B: {"date": "25/12/2024"}    --> {"date": "2024-12-25"}    ||
    ||  Tool C: {"status_code": 200}      --> {"status": "success"}     ||
    ||  Tool D: {"trend": 1}             --> {"trend": "rising"}        ||
    ||                                                                  ||
    ||  Model receives CONSISTENT data format:                        ||
    ||                                                                  ||
    ||  * All dates in ISO format (YYYY-MM-DD)                        ||
    ||  * All status codes as readable strings                        ||
    ||  * No magic numbers - all values are interpretable             ||
    ||  * Consistent structure regardless of source                   ||
    ||                                                                  ||
    +======================================================================+
    """)

    print("\nWITH PostToolUse:")
    print("-" * 50)
    for source in ["weather_api", "stock_api", "calendar_api", "database"]:
        raw = simulator.tools[source]()
        normalized = post_tooluse_hook(raw)
        print(f"\n   {source} --> normalized!")


def show_code_example():
    """
    Show the actual PostToolUse hook implementation.
    """
    print("\n" + "=" * 70)
    print("POSTTOOLUSE HOOK CODE EXAMPLE")
    print("=" * 70)

    print("""
    +======================================================================+
    ||                                                                  ||
    ||  PostToolUse hook implementation:                                ||
    ||                                                                  ||
    ||  ```javascript                                                   ||
    ||  const postToolUseHook = (toolOutput) => {                      ||
    ||                                                                  ||
    ||    // Extract the raw data                                       ||
    ||    const data = toolOutput.data;                                 ||
    ||                                                                  ||
    ||    // Normalize based on tool source                             ||
    ||    if (toolOutput.source === "weather_api") {                    ||
    ||      return {                                                    ||
    ||        date: normalizeTimestamp(data.timestamp),                 ||
    ||        temperature: data.temperature + "F"                      ||
    ||      };                                                          ||
    ||    }                                                             ||
    ||                                                                  ||
    ||    if (toolOutput.source === "stock_api") {                      ||
    ||      return {                                                    ||
    ||        status: normalizeStatusCode(data.status_code),           ||
    ||        trend: normalizeTrend(data.trend)                        ||
    ||      };                                                          ||
    ||    }                                                             ||
    ||                                                                  ||
    ||    // Return normalized data                                     ||
    ||    return data;                                                  ||
    ||  };                                                              ||
    ||  ```                                                             ||
    ||                                                                  ||
    ||  This hook runs AFTER execution, BEFORE model sees results.    ||
    ||  Model never sees the raw heterogeneous format!                  ||
    ||                                                                  ||
    +======================================================================+
    """)


if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    print("\n" + "=" * 70)
    print("PRACTICE 2: POSTTOOLUSE - DATA NORMALIZATION")
    print("=" * 70)
    print("""
    This program teaches how PostToolUse hooks normalize data
    from different tools into consistent formats.
    """)

    demonstrate_normalization_problem()
    demonstrate_normalization_solution()
    show_code_example()

    print("""
    +======================================================================+
    ||                                                                  ||
    ||              WHAT WE HAVE LEARNT                                 ||
    ||              =====================                                 ||
    ||                                                                  ||
    +======================================================================+

    1. We saw the PROBLEM:
       - Different tools return data in different formats
       - Unix timestamps, DD/MM/YYYY, numeric codes, etc.
       - Model must parse each format differently

    2. We saw the SOLUTION:
       - PostToolUse hook runs AFTER tool execution
       - Transforms raw data into consistent format
       - Model sees normalized data regardless of source

    3. We saw the CODE EXAMPLE:
       - Hook checks tool source
       - Applies appropriate transformations
       - Returns normalized data

    4. KEY INSIGHT:
       PostToolUse is for TRANSFORMATION, not BLOCKING.
       The tool already executed - the hook just normalizes the output.

    5. USE CASES:
       - Convert timestamps to readable dates
       - Translate numeric codes to strings
       - Standardize date formats across tools
       - Add contextual metadata

    +======================================================================+
    ||                                                                  ||
    ||                    PROGRAM COMPLETE!                             ||
    ||                                                                  ||
    +======================================================================+
    """)

