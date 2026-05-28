"""
SETUP HELPER - Test your API connection
==========================================
Run this to verify your .env is configured correctly.

+------------------------------------------------------------------+
|                   ENVIRONMENT CHECK FLOW                         |
+------------------------------------------------------------------+
|                                                                    |
|   +------------------+                                           |
|   | Load .env file   |  <-- Read API key and base URL             |
|   +------------------+                                           |
|          |                                                        |
|          v                                                        |
|   +------------------+                                           |
|   | Check API Key    |  <-- Validate key exists                   |
|   +------------------+                                           |
|          |                                                        |
|          v                                                        |
|   +------------------+                                           |
|   | Test Connection  |  <-- Make a simple API call               |
|   +------------------+                                           |
|          |                                                        |
|          v                                                        |
|   +------------------+                                           |
|   | Report Status    |  <-- Show success or failure              |
|   +------------------+                                           |
|                                                                    |
+------------------------------------------------------------------+

WHY THIS MATTERS:
- API key is required for all multi-agent systems
- Wrong API base URL causes connection failures
- Testing early prevents debugging issues later
- Validates .env file format is correct
"""

from dotenv import load_dotenv
import os

# Load .env
load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY", "")
api_base = os.getenv("ANTHROPIC_API_BASE", "https://api.anthropic.com")

print("=" * 60)
print("ENVIRONMENT CHECK")
print("=" * 60)

# ============================================================================
# CHECK 1: API Key Presence
# ============================================================================
print("\nCHECK 1: API Key")
print("-" * 40)

if api_key:
    # Show first 10 and last 5 characters (don't reveal full key)
    key_preview = f"{api_key[:10]}...{api_key[-5:]}"
    print(f"   [OK] API Key found")
    print(f"   Key preview: {key_preview}")
else:
    print("   [FAIL] NO API KEY FOUND!")
    print("   Please add ANTHROPIC_API_KEY to your .env file")

# ============================================================================
# CHECK 2: API Base URL
# ============================================================================
print("\nCHECK 2: API Base URL")
print("-" * 40)
print(f"   API Base: {api_base}")

# ============================================================================
# CHECK 3: Connection Test
# ============================================================================
print("\nCHECK 3: Connection Test")
print("-" * 40)
print("   Testing connection to API...")

try:
    from anthropic import Anthropic

    # Build client kwargs
    client_kwargs = {"api_key": api_key} if api_key else {}
    if api_base and api_base != "https://api.anthropic.com":
        client_kwargs["base_url"] = api_base

    # Create client
    client = Anthropic(**client_kwargs)

    # Make a simple test call
    print("   Making test API call...")
    response = client.messages.create(
        model="claude-haiku-4-5-20250601",
        max_tokens=10,
        messages=[{"role": "user", "content": "Hi"}]
    )

    print("\n   [SUCCESS] Connection successful!")
    print(f"   Model responded: '{response.content[0].text}'")
    print(f"   Model: {response.model}")
    print(f"   Stop reason: {response.stop_reason}")

except Exception as e:
    error_type = type(e).__name__
    print(f"\n   [FAIL] Connection failed!")
    print(f"   Error: {error_type}")
    print(f"   Message: {str(e)}")

# ============================================================================
# REAL-TIME SCENARIO: First-Time Setup
# ============================================================================
"""
PRODUCTION SCENARIO: New Developer Onboarding

When a new developer joins the team:

1. They clone the repository
2. They need to set up their .env file
3. Running this test_connection.py validates:
   - .env file exists and is formatted correctly
   - API key is valid (not expired)
   - API base URL is correct (or default is used)
   - Network can reach the API endpoint

If any check fails, the error message guides them to fix it.
This prevents "API key not working" questions in team chat.
"""

# ============================================================================
# MISTAKE #1: Using Wrong API Base for Custom Providers
# ============================================================================
"""
COMMON ERROR: Setting API base to wrong endpoint

WRONG:
    ANTHROPIC_API_BASE=https://api.anthropic.com/v1
    # Should be: https://api.anthropic.com (no /v1)

WHY THIS BREAKS:
- Wrong path returns 404 or auth errors
- The SDK adds the version path internally
- Manual path causes duplication

CORRECT:
    ANTHROPIC_API_BASE=https://api.anthropic.com
    # Or leave empty for default

FOR CUSTOM PROVIDERS (like opusmax.pro):
    ANTHROPIC_API_BASE=https://opusmax.pro/api
    # Must include full path the provider uses
"""

# ============================================================================
# MISTAKE #2: API Key with Leading/Trailing Spaces
# ============================================================================
"""
COMMON ERROR: Spaces in .env values

WRONG in .env:
    ANTHROPIC_API_KEY= sk-ant-api03-abc123...

The leading space becomes part of the key!

CORRECT in .env:
    ANTHROPIC_API_KEY=sk-ant-api03-abc123...

Or in Python (trim whitespace):
    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
"""

# ============================================================================
# MISTAKE #3: Not Handling Missing .env File
# ============================================================================
"""
COMMON ERROR: Assuming .env always exists

CODE:
    load_dotenv()  # Does nothing if file missing!
    api_key = os.getenv("ANTHROPIC_API_KEY")

ROBUST CODE:
    if not os.path.exists(".env"):
        print("WARNING: .env file not found!")
        print("Creating template .env file...")

    load_dotenv()  # Safe to call, does nothing if missing

    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment")
"""

# ============================================================================
# INTERVIEW Q&A: Environment Configuration
# ============================================================================
"""
Q: How do you handle API key management in production?
A: Multi-layer approach:

   1. DEVELOPMENT
   - Use .env file (gitignored)
   - Never commit real keys

   2. STAGING/PRODUCTION
   - Use environment variables set by infrastructure
   - Secrets manager (AWS Secrets Manager, HashiCorp Vault)
   - Rotate keys regularly

   3. KEY VALIDATION
   - Check format matches expected pattern
   - Validate key prefix (sk-ant-)
   - Test connection before use

Q: What if someone uses the wrong model name?
A: Handle gracefully:

   - Catch InvalidRequestError
   - Parse error message for "model not found"
   - Suggest correct model names
   - Log the attempt for security monitoring

Q: How do you handle API provider changes?
A: Strategy:

   - Abstract API client creation in one function
   - Use provider configuration (not hardcoded)
   - Environment-based provider selection
   - Support fallback providers
"""

# ============================================================================
# TROUBLESHOOTING GUIDE
# ============================================================================

print("\n" + "=" * 60)
print("TROUBLESHOOTING GUIDE")
print("=" * 60)
print("""
If connection failed, check these common issues:

1. MISSING API KEY
   - Create .env file in project root
   - Add: ANTHROPIC_API_KEY=sk-ant-your-key-here

2. WRONG API BASE
   - Default: https://api.anthropic.com
   - Leave blank or remove line for default
   - For custom providers (opusmax.pro), enter their URL

3. NETWORK ISSUES
   - Check firewall/proxy settings
   - Verify internet connection
   - Try: curl https://api.anthropic.com (should return 401)

4. KEY EXPIRED/INVALID
   - Get new key from: https://console.anthropic.com/
   - Check if key is active in dashboard
   - Keys can be revoked or expired

5. WRONG KEY FORMAT
   - Should start with: sk-ant-
   - Should be ~100+ characters
   - No newlines or spaces
""")

# ============================================================================
# WHAT WE HAVE LEARNT
# ============================================================================
"""
=============================================================================
WHAT WE HAVE LEARNT: Environment Configuration
=============================================================================

1. IMPORTANCE OF VALIDATION
   -----------------------
   - Environment issues cause silent failures
   - Validate early, fail fast, error clearly
   - Test connection before running orchestrator

2. COMMON ISSUES AND FIXES
   -----------------------

   | Issue                  | Fix                              |
   |------------------------|---------------------------------|
   | Missing API key        | Add to .env file                |
   | Wrong API base         | Use default or correct URL      |
   | Key with spaces        | Strip whitespace                |
   | .env not found         | Create file or use env vars     |
   | Expired key            | Get new key from dashboard      |
   | Network blocked        | Check firewall/proxy            |

3. SECURE CONFIGURATION
   --------------------

   DO:
   +------------------------+
   | .env file (gitignored) |  Dev: local credentials
   | Environment variables  |  CI/CD: injected by system
   | Secrets manager        |  Production: AWS Secrets, etc.
   +------------------------+

   DON'T:
   +------------------------+
   | Hardcode keys in code  |  Easy to commit accidentally
   | Log full API keys      |  Security risk
   | Share keys in Slack    |  Untracked, unsecure
   +------------------------+

4. TESTING STRATEGY
   ----------------

   ALWAYS TEST:
   - API key is present (not empty)
   - API base URL is valid
   - Connection can be established
   - Simple API call succeeds

   This single file can save hours of debugging later!

5. INTERVIEW ANSWER FRAMEWORK
   --------------------------

   "How do you handle API key configuration?"

   Step 1: Development setup
   "We use .env files for local development, which are gitignored
    so keys never get committed to source control."

   Step 2: Production approach
   "In production, keys come from environment variables or secrets
    managers like AWS Secrets Manager. Never hardcoded."

   Step 3: Validation
   "Before any API call, we validate the key exists and test the
    connection. This fails fast with clear error messages."

   Step 4: Error handling
   "If key is missing or invalid, we provide actionable guidance
    on what to check and how to fix it."

6. TROUBLESHOOTING CHECKLIST
   -------------------------

   When a user reports "API not working":

   [ ] Step 1: Run test_connection.py
   [ ] Step 2: Check if .env file exists
   [ ] Step 3: Verify API key format (starts with sk-ant-)
   [ ] Step 4: Confirm API base URL (or use default)
   [ ] Step 5: Test network connectivity
   [ ] Step 6: Check if key is active in dashboard
   [ ] Step 7: Look for rate limit errors

   Each step eliminates a potential cause.

=============================================================================
"""

print("\n" + "=" * 60)
print("ENVIRONMENT CHECK COMPLETE")
print("=" * 60)