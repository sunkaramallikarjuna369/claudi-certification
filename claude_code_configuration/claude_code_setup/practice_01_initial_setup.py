# ============================================================================
# PRACTICE FILE: Claude Code Initial Setup
# Domain 3.1: Claude Code Setup and Customization
# ============================================================================
#
# PURPOSE: Learn the fundamentals of Claude Code installation, configuration,
# and initial setup for professional development environments.
#
# ============================================================================
# HOW TO USE THIS FILE
# ============================================================================
#
# 1. Read through the concepts and code examples
# 2. Run the syntax verification at the bottom (python -m py_compile)
# 3. Review the WHAT WE HAVE LEARNT section
# 4. Practice the interview questions
#
# ============================================================================
# SECTION 1: INSTALLATION AND CONFIGURATION BASICS
# ============================================================================
#
# Claude Code is installed via npm. After installation, it needs to be
# configured with your API key and preferences before first use.
#
# INSTALLATION COMMAND:
# npm install -g @anthropic-ai/claude-code
#
# ============================================================================

# --------------------------------------------------------------------------
# CONCEPT: API Key Configuration
# --------------------------------------------------------------------------
#
# The API key should NEVER be hardcoded. Use environment variables or .env files.
# Never commit API keys to version control - this is a critical security practice.
#
# WRONG (Security Risk):
#   API_KEY = "sk-ant-api03-xxxxx"  # DON'T DO THIS!
#
# RIGHT (Secure):
#   API_KEY = os.environ.get("ANTHROPIC_API_KEY")
#   # Or load from .env file

import os

# Load API key from environment variable
# This is the secure way to handle API keys
api_key = os.environ.get("ANTHROPIC_API_KEY")

if api_key is None:
    # If running locally without Claude Code CLI, we simulate the config
    # In real Claude Code, the API key is managed by the CLI itself
    print("API key not found in environment")
    print("In production, Claude Code handles this automatically")
else:
    print(f"API key loaded successfully (first 10 chars): {api_key[:10]}...")

# --------------------------------------------------------------------------
# CONCEPT: Settings Management
# --------------------------------------------------------------------------
#
# Claude Code uses JSON configuration files to store preferences.
# There are two levels of configuration:
#
# 1. USER-LEVEL: ~/.claude/settings.json
#    - Applies to all projects for this user
#    - Default model, timeout settings, global hooks
#
# 2. PROJECT-LEVEL: .claude/settings.json or CLAUDE.md
#    - Applies only to this specific project
#    - Project-specific hooks, custom settings
#
# EXAMPLE settings.json structure:
# {
#   "model": "claude-haiku-4-5-20250601",
#   "max_tokens": 8192,
#   "temperature": 0.7,
#   "timeout": 120000,
#   "permissions": {
#     "allow": ["Bash", "Read", "Write"],
#     "deny": [" Edit"]
#   }
# }

# Simulated settings structure for learning purposes
claude_settings = {
    "model": "claude-haiku-4-5-20250601",
    "max_tokens": 8192,
    "temperature": 0.7,
    "timeout_ms": 120000,
    "permissions": {
        "allow": ["Bash", "Read", "Write", "Grep", "Glob"],
        "deny": [" Edit"],
        "require_confirmation": ["Bash"],
        "max_file_size": 1000000
    },
    "hooks": {
        "before_tool": [],
        "after_tool": [],
        "on_error": []
    }
}

print("\n=== Claude Code Settings Example ===")
print(f"Model: {claude_settings['model']}")
print(f"Max Tokens: {claude_settings['max_tokens']}")
print(f"Temperature: {claude_settings['temperature']}")
print(f"Timeout: {claude_settings['timeout_ms']}ms")

# ============================================================================
# SECTION 2: ENVIRONMENT VARIABLES AND .ENV INTEGRATION
# ============================================================================
#
# Best practice: Use a .env file for local development and environment
# variables in CI/CD pipelines.
#
# .env file structure:
# ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
# CLAUDE_MODEL=claude-haiku-4-5-20250601
# CLAUDE_TIMEOUT=120000
# CLAUDE_MAX_TOKENS=8192

# Function to load and validate .env files
# (In real Claude Code, this is handled automatically)

def load_env_file(filepath=".env"):
    """
    Load environment variables from a .env file.

    This is a common pattern for local development.
    In production/CI, use actual environment variables.

    Args:
        filepath: Path to the .env file (default: .env in current dir)

    Returns:
        dict: Environment variables loaded from file
    """
    env_vars = {}

    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                # Parse KEY=VALUE format
                if '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    except FileNotFoundError:
        print(f".env file not found at {filepath}")
        return {}

    return env_vars

# Example usage
env_vars = env_vars = load_env_file()
if env_vars:
    print(f"\n=== Loaded {len(env_vars)} environment variables ===")
    for key in env_vars:
        # Don't print sensitive values!
        print(f"  {key}")

# CRITICAL SECURITY NOTE:
# Always add ..env to your .gitignore file!
#
# Correct .gitignore entry:
# .env
# .env.local
# .env.*.local
#
# Common Mistake: Forgetting to add .env to .gitignore, exposing API keys!

# ============================================================================
# SECTION 3: MODEL SELECTION
# ============================================================================
#
# Claude Code supports multiple models with different capabilities:
#
# 1. HAJKU (claude-haiku-4-5-20250601)
#    - Fastest, lowest cost
#    - Best for simple, repetitive tasks
#    - 200K context window
#    - Use for: file edits, simple queries, bulk operations
#
# 2. SONNET (claude-sonnet-4-5-20250601)
#    - Balanced performance and cost
#    - Good for most development tasks
#    - 200K context window
#    - Use for: code review, documentation, complex features
#
# 3. OPUS (claude-opus-4-5-20250601)
#    - Most capable, highest cost
#    - Best for complex reasoning and large refactors
#    - 200K context window
#    - Use for: architecture decisions, complex debugging

available_models = {
    "haiku": {
        "name": "claude-haiku-4-5-20250601",
        "speed": "Fastest",
        "cost": "Lowest",
        "use_case": "Simple tasks, file edits, bulk operations"
    },
    "sonnet": {
        "name": "claude-sonnet-4-5-20250601",
        "speed": "Medium",
        "cost": "Medium",
        "use_case": "Code review, documentation, most development"
    },
    "opus": {
        "name": "claude-opus-4-5-20250601",
        "speed": "Slowest",
        "cost": "Highest",
        "use_case": "Complex reasoning, architecture, large refactors"
    }
}

print("\n=== Available Claude Models ===")
for model_key, model_info in available_models.items():
    print(f"\n{model_key.upper()}:")
    print(f"  Name: {model_info['name']}")
    print(f"  Speed: {model_info['speed']}")
    print(f"  Cost: {model_info['cost']}")
    print(f"  Best For: {model_info['use_case']}")

# Best practice: Use Haiku for simple, repetitive tasks to save costs!
print("\n=== COST OPTIMIZATION TIP ===")
print("Use Haiku (claude-haiku-4-5-20250601) for:")
print("  - Simple file edits")
print("  - Bulk operations")
print("  - Repetitive refactoring tasks")
print("  - Documentation updates")
print("Reserve Sonnet/Opus for complex tasks that need better reasoning.")

# ============================================================================
# SECTION 4: TIME OUT AND RETRY SETTINGS
# ============================================================================
#
# Claude Code allows configuration of timeouts for long operations.
# This is important for CI/CD pipelines and large projects.
#
# Settings:
# - timeout_ms: Maximum time for a single operation (default: 120000ms = 2 min)
# - max_retries: Number of retry attempts on failure
# - retry_delay_ms: Delay between retry attempts

def create_timeout_config(timeout_ms=120000, max_retries=3, retry_delay_ms=5000):
    """
    Create a timeout configuration dictionary.

    This configuration affects how Claude Code handles long-running
    operations and failures.

    Args:
        timeout_ms: Maximum operation time in milliseconds
        max_retries: Number of retry attempts
        retry_delay_ms: Delay between retries in milliseconds

    Returns:
        dict: Timeout configuration
    """
    return {
        "timeout_ms": timeout_ms,
        "max_retries": max_retries,
        "retry_delay_ms": retry_delay_ms,
        # Computed values for convenience
        "timeout_seconds": timeout_ms / 1000,
        "total_max_time_ms": timeout_ms + (max_retries * retry_delay_ms)
    }

# Example configurations for different environments
prod_config = create_timeout_config(timeout_ms=60000, max_retries=2, retry_delay_ms=3000)
ci_config = create_timeout_config(timeout_ms=300000, max_retries=3, retry_delay_ms=10000)
dev_config = create_timeout_config(timeout_ms=120000, max_retries=5, retry_delay_ms=2000)

print("\n=== Timeout Configurations ===")
print("\nDevelopment (longer timeouts for exploration):")
print(f"  Timeout: {dev_config['timeout_seconds']}s")
print(f"  Max Retries: {dev_config['max_retries']}")

print("\nCI/CD (moderate timeouts with more retries):")
print(f"  Timeout: {ci_config['timeout_seconds']}s")
print(f"  Max Retries: {ci_config['max_retries']}")

print("\nProduction (shorter timeouts for quick failures):")
print(f"  Timeout: {prod_config['timeout_seconds']}s")
print(f"  Max Retries: {prod_config['max_retries']}")

# ============================================================================
# SECTION 5: FIRST-TIME SETUP WORKFLOW
# ============================================================================
#
# A typical first-time setup workflow:
#
# 1. Install Claude Code: npm install -g @anthropic-ai/claude-code
# 2. Authenticate: claudeauth (or set ANTHROPIC_API_KEY env var)
# 3. Create .env file with API key
# 4. Initialize project: claude --init
# 5. Create CLAUDE.md for project documentation
# 6. Configure settings as needed

def mock_first_time_setup():
    """
    Mock function demonstrating the first-time setup workflow.

    In real Claude Code, many of these steps are handled automatically
    or through CLI commands.
    """
    setup_steps = [
        "Step 1: Install Claude Code via npm",
        "Step 2: Authenticate with API key",
        "Step 3: Create .env file with ANTHROPIC_API_KEY",
        "Step 4: Initialize project with CLAUDE.md",
        "Step 5: Configure model and permissions",
        "Step 6: Test with a simple command"
    ]

    print("\n=== First-Time Setup Workflow ===")
    for i, step in enumerate(setup_steps, 1):
        print(f"  {i}. {step}")

    # After setup, the directory structure should look like:
    expected_structure = """
    your-project/
    ├── .env                    # API key (DONT COMMIT!)
    ├── .gitignore              # Should include .env
    ├── CLAUDE.md               # Project documentation
    ├── .claude/
    │   └── settings.json       # Project settings (optional)
    └── src/                    # Your source code
    """

    print(f"\n=== Expected Project Structure ==={expected_structure}")

mock_first_time_setup()

# ============================================================================
# SECTION 6: REAL-TIME SCENARIOS
# ============================================================================

print("\n" + "=" * 70)
print("REAL-TIME SCENARIOS")
print("=" * 70)

# --------------------------------------------------------------------------
# SCENARIO 1: New Developer Onboarding
# --------------------------------------------------------------------------
print("\n--- SCENARIO 1: New Developer Onboarding ---")
print("""
Situation: A new developer joins your team and needs to set up Claude Code.

Task: Guide them through the setup process.

Solution:
1. Share the project's .env.template (without real API key)
2. Have them create a .env file from the template
3. Point them to CLAUDE.md for project-specific instructions
4. Verify their setup by having them run: claude --version

Key config for new developers:
- Model: claude-haiku-4-5-20250601 (for cost savings on simple tasks)
- Timeout: 120000ms (2 minutes, reasonable for exploration)
- Permissions: Ask for confirmation on Bash commands
""")

# --------------------------------------------------------------------------
# SCENARIO 2: Switching Between Projects
# --------------------------------------------------------------------------
print("\n--- SCENARIO 2: Switching Between Projects ---")
print("""
Situation: You work on multiple projects with different Claude Code configs.

Challenge: Each project may have different settings (models, hooks, permissions).

Solution:
- User-level settings serve as defaults
- Project-level CLAUDE.md overrides for project-specific needs
- Use the --model flag to override when needed: claude --model claude-haiku-4-5-20250601

Example project switch:
  Project A (simple): claude-haiku-4-5-20250601, no hooks
  Project B (complex): claude-opus-4-5-20250601, security hooks enabled
""")

# ============================================================================
# SECTION 7: COMMON MISTAKES
# ============================================================================

print("\n" + "=" * 70)
print("COMMON MISTAKES TO AVOID")
print("=" * 70)

mistakes = [
    ("Hardcoding API keys", "API_KEY = 'sk-ant-xxx'", "Use environment variables!"),
    ("Missing .env gitignore", "No .env in .gitignore", "Always add .env to .gitignore"),
    ("Wrong model for task", "Using Opus for simple edits", "Use Haiku for simple, repetitive tasks"),
    ("No timeout configured", "Operations run forever", "Set appropriate timeouts"),
    ("No retry logic", "Single failure = complete failure", "Configure retries for robustness"),
    ("Ignoring permission prompts", "Bypassing security", "Respect permission configurations"),
    ("No project documentation", "Unclear project structure", "Create CLAUDE.md with project info")
]

print("\n{:<30} {:<30} {:<20}".format("MISTAKE", "WRONG", "RIGHT"))
print("-" * 80)
for mistake, wrong, right in mistakes:
    print(f"{mistake:<30} {wrong:<30} {right:<20}")

# ============================================================================
# SECTION 8: INTERVIEW Q&A
# ============================================================================

print("\n" + "=" * 70)
print("INTERVIEW QUESTIONS AND ANSWERS")
print("=" * 70)

qa_pairs = [
    (
        "Q: How do you configure Claude Code for a new project?",
        """
A: 1. Create a .env file with ANTHROPIC_API_KEY
   2. Create CLAUDE.md documenting project structure and conventions
   3. Optionally create .claude/settings.json for project-specific config
   4. Test with a simple command to verify setup
   5. Document any special hooks or workflows in CLAUDE.md
        """
    ),
    (
        "Q: What is the difference between project-level and user-level settings?",
        """
A: User-level settings (~/.claude/settings.json) apply to all projects for
   a given user. Project-level settings (.claude/settings.json or CLAUDE.md)
   apply only to that specific project. Project settings override user
   settings for that project.
        """
    ),
    (
        "Q: How do you optimize costs when using Claude Code?",
        """
A: 1. Use the appropriate model - Haiku for simple tasks, Sonnet for most
      development, Opus only for complex reasoning
   2. Set reasonable timeouts to prevent runaway operations
   3. Configure permission prompts to avoid accidental expensive operations
   4. Use streaming (--no-stream only when necessary)
   5. Implement hooks to validate inputs before expensive operations
        """
    ),
    (
        "Q: How do you handle API key rotation?",
        """
A: 1. Store API keys in environment variables, never hardcode
   2. For rotation: update the environment variable/.env file
   3. Claude Code will pick up the new key on next invocation
   4. Ensure .env file is in .gitignore to prevent accidental commits
   5. Consider using a secrets manager for production environments
        """
    )
]

for question, answer in qa_pairs:
    print(f"\n{question}")
    print(answer)

# ============================================================================
# WHAT WE HAVE LEARNT
# ============================================================================

print("\n" + "=" * 70)
print("WHAT WE HAVE LEARNT")
print("=" * 70)

lessons = """
1. API KEY SECURITY
   - Never hardcode API keys in source files
   - Use environment variables or .env files
   - Always add .env to .gitignore

2. CONFIGURATION HIERARCHY
   - User-level settings (~/.claude/settings.json) are defaults
   - Project-level settings override user settings
   - CLAUDE.md hooks provide project-specific automation

3. MODEL SELECTION
   - Haiku (claude-haiku-4-5-20250601): Fast, cheap, simple tasks
   - Sonnet: Balanced for most development work
   - Opus: Expensive, capable, complex reasoning only

4. TIMEOUT CONFIGURATION
   - timeout_ms controls maximum operation time
   - Configure max_retries and retry_delay_ms for robustness
   - Different environments need different timeout values

5. FIRST-TIME SETUP WORKFLOW
   - Install via npm
   - Authenticate with API key
   - Create .env file
   - Initialize with CLAUDE.md
   - Test and verify

6. PROJECT STRUCTURE
   - .env for secrets
   - CLAUDE.md for project documentation
   - .claude/ for project settings
   - Proper .gitignore configuration

7. COST OPTIMIZATION
   - Use appropriate model for task complexity
   - Set reasonable timeouts
   - Configure permission prompts
   - Implement validation hooks
"""

print(lessons)

# ============================================================================
# SYNTAX VERIFICATION
# ============================================================================
#
# This file should compile without errors. To verify manually:
# python -m py_compile d:/peaceofcode/code/claude_code_configuration/claude_code_setup/practice_01_initial_setup.py
#
# If you see no errors, the file is syntactically correct.
# ============================================================================

print("\n=== File Syntax Verification ===")
print("This file has been created successfully.")
print("Run: python -m py_compile <file_path> to verify syntax.")
print("=" * 70)
