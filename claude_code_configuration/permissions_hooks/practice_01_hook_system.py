# ============================================================================
# PRACTICE FILE: Hook System and Permissions
# Domain 3.2: Permissions and Hooks Configuration
# ============================================================================
#
# PURPOSE: Learn how to configure hooks, manage permissions, and implement
# security controls in Claude Code for professional development workflows.
#
# ============================================================================
# HOW TO USE THIS FILE
# ============================================================================
#
# 1. Read through the concepts and code examples
# 2. Run the syntax verification at the bottom
# 3. Review the WHAT WE HAVE LEARNT section
# 4. Practice the interview questions
#
# ============================================================================
# SECTION 1: HOOK SYSTEM ARCHITECTURE
# ============================================================================
#
# Hooks are automated actions that run at specific points in Claude Code's
# execution flow. They enable powerful customization and automation.
#
# HOOK EXECUTION FLOW:
#
# User Input -> BEFORE_HOOK -> Tool Execution -> AFTER_HOOK -> Response
#                   |                |               |
#              on_error hook      Tool Result      on_error hook
#              (on failure)       (success/fail)   (on failure)
#
# ============================================================================

# --------------------------------------------------------------------------
# CONCEPT: Hook Types
# --------------------------------------------------------------------------
#
# Claude Code supports the following hook types:
#
# 1. before_tool
#    - Runs BEFORE a tool is executed
#    - Use for: Validation, logging, preparation
#    - Can abort the operation by returning an error
#
# 2. after_tool
#    - Runs AFTER a tool completes (success or failure)
#    - Use for: Notifications, cleanup, logging
#
# 3. on_error
#    - Runs when an error occurs
#    - Use for: Error handling, notifications, recovery

# Simulating hook configuration for learning
hook_types = {
    "before_tool": {
        "description": "Runs before each tool execution",
        "use_cases": [
            "Validate input parameters",
            "Check permissions before dangerous operations",
            "Log operation details for audit",
            "Prepare environment for tool execution",
            "Backup files before modification"
        ],
        "example": "Check if file is read-only before Edit tool"
    },
    "after_tool": {
        "description": "Runs after each tool execution",
        "use_cases": [
            "Send notifications on completion",
            "Update local caches or indexes",
            "Log operation results",
            "Clean up temporary files",
            "Update progress tracking"
        ],
        "example": "Update a task management system after task completion"
    },
    "on_error": {
        "description": "Runs when an error occurs",
        "use_cases": [
            "Send error notifications",
            "Rollback incomplete operations",
            "Log error details for debugging",
            "Provide recovery instructions",
            "Create error reports"
        ],
        "example": "Rollback partial file changes if compilation fails"
    }
}

print("=" * 70)
print("HOOK TYPES")
print("=" * 70)

for hook_type, info in hook_types.items():
    print(f"\n{hook_type.upper()}:")
    print(f"  Description: {info['description']}")
    print(f"  Example: {info['example']}")
    print(f"  Use Cases:")
    for use_case in info['use_cases']:
        print(f"    - {use_case}")

# ============================================================================
# SECTION 2: HOOK CONFIGURATION IN CLAUDE.MD
# ============================================================================
#
# Hooks can be configured in CLAUDE.md using the hooks configuration section.
# This allows project-specific hooks that apply to all Claude Code sessions
# in that project.
#
# CLAUDE.md HOOKS SECTION EXAMPLE:
# ---
# hooks:
#   before_tool:
#     - name: validate-dotnet-format
#       description: Ensure code follows formatting standards
#       run: scripts/validate-format.sh
#   after_tool:
#     - name: notify-completion
#       description: Send notification when task completes
#       run: scripts/notify.sh
#   on_error:
#     - name: log-error
#       description: Log errors to centralized system
#       run: scripts/log-error.sh
# ---

# Example CLAUDE.md hooks configuration structure
claude_md_hooks_config = """
hooks:
  # Pre-operation validation hooks
  before_tool:
    - name: validate-dotnet-format
      description: Run code formatting validation
      run: scripts/validate-format.sh

    - name: check-file-permissions
      description: Verify file write permissions
      run: scripts/check-permissions.sh

    - name: backup-before-edit
      description: Create backup before file modification
      run: scripts/backup.sh

  # Post-operation hooks
  after_tool:
    - name: update-task-status
      description: Update task tracking system
      run: scripts/update-task.sh

    - name: notify-slack
      description: Send Slack notification
      run: scripts/notify-slack.sh

  # Error handling hooks
  on_error:
    - name: rollback-changes
      description: Rollback incomplete changes
      run: scripts/rollback.sh

    - name: alert-team
      description: Alert team on errors
      run: scripts/alert.sh
"""

print("\n=== CLAUDE.md Hooks Configuration Example ===")
print(claude_md_hooks_config)

# ============================================================================
# SECTION 3: PERMISSION SYSTEM
# ============================================================================
#
# The permission system controls which tools Claude Code can execute.
# This is critical for security in professional environments.
#
# PERMISSION LEVELS:
# - allow: Tool can execute without confirmation
# - deny: Tool is blocked from execution
# - require_confirmation: Tool asks for user confirmation first
#
# CONFIGURATION SCOPE:
# - Global (user-level settings)
# - Project (project-level settings)
# - Directory-specific (scoped permissions)

# Example permission configuration
permission_config = {
    "global": {
        # Global defaults for all operations
        "allow": ["Bash", "Read", "Write", "Grep", "Glob", "WebFetch", "WebSearch"],
        "deny": ["Edit"],
        "require_confirmation": ["Bash"],
        "description": "Default permissions with confirmation for Bash"
    },
    "production": {
        # Stricter permissions for production
        "allow": ["Read", "Grep", "Glob"],
        "deny": ["Bash", "Write", "Edit"],
        "require_confirmation": [],
        "description": "Strict permissions - read-only access only"
    },
    "development": {
        # More permissive for development
        "allow": ["Bash", "Read", "Write", "Grep", "Glob", "Edit"],
        "deny": [],
        "require_confirmation": ["Write", "Edit"],
        "description": "Development permissions - basic write access with confirmation"
    }
}

print("\n=== Permission Configuration Examples ===")

for env, config in permission_config.items():
    print(f"\n{env.upper()} Environment:")
    print(f"  Description: {config['description']}")
    print(f"  Allow: {', '.join(config['allow']) if config['allow'] else 'None'}")
    print(f"  Deny: {', '.join(config['deny']) if config['deny'] else 'None'}")
    print(f"  Require Confirmation: {', '.join(config['require_confirmation']) if config['require_confirmation'] else 'None'}")

# ============================================================================
# SECTION 4: PRACTICAL HOOK EXAMPLES
# ============================================================================

print("\n" + "=" * 70)
print("PRACTICAL HOOK EXAMPLES")
print("=" * 70)

# --------------------------------------------------------------------------
# EXAMPLE 1: Pre-commit Lint Check Hook
# --------------------------------------------------------------------------
print("\n--- EXAMPLE 1: Pre-commit Lint Check Hook ---")

def create_lint_hook():
    """
    Create a before_tool hook that validates code before modification.

    This hook:
    1. Runs a linter on files before Edit operations
    2. Prevents edits if linting would fail
    3. Logs the validation attempt

    In real Claude Code, this would be a shell script or Python file
    that gets executed automatically.
    """
    hook_script = '''#!/bin/bash
# pre-lint-check.sh - Run before Edit operations

FILE_PATH=$1
TOOL_NAME=$2

echo "[HOOK] Running pre-lint check on $FILE_PATH"

# Only check code files
if [[ "$FILE_PATH" == *.py ]]; then
    # Run Python linter
    if ! python -m flake8 "$FILE_PATH" --select=E,F,W; then
        echo "[HOOK ERROR] Linting failed. Edit blocked."
        exit 1  # Exit 1 blocks the operation
    fi
elif [[ "$FILE_PATH" == *.js ]]; then
    # Run JavaScript linter
    if ! npm run lint -- "$FILE_PATH"; then
        echo "[HOOK ERROR] JavaScript linting failed. Edit blocked."
        exit 1
    fi
fi

echo "[HOOK] Pre-lint check passed."
exit 0  # Exit 0 allows the operation to proceed
'''
    return hook_script

lint_hook = create_lint_hook()
print("\nHook Script:")
print(lint_hook)
print("\nConfiguration in CLAUDE.md:")
print("""
hooks:
  before_tool:
    - name: pre-lint-check
      run: scripts/pre-lint-check.sh
      description: Run linter before Edit operations
""")

# --------------------------------------------------------------------------
# EXAMPLE 2: Backup Before Destructive Operations Hook
# --------------------------------------------------------------------------
print("\n--- EXAMPLE 2: Backup Before Destructive Operations Hook ---")

def create_backup_hook():
    """
    Create a before_tool hook that backs up files before Edit operations.

    This hook:
    1. Creates a timestamped backup before file modification
    2. Stores backups in a designated backup directory
    3. Keeps only recent backups (cleanup old ones)
    """
    hook_script = '''#!/bin/bash
# backup-before-edit.sh - Create backup before Edit operations

FILE_PATH=$1
BACKUP_DIR=".backups"

echo "[HOOK] Creating backup of $FILE_PATH"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Create timestamped backup
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/$(basename $FILE_PATH).$TIMESTAMP.bak"

if cp "$FILE_PATH" "$BACKUP_FILE"; then
    echo "[HOOK] Backup created: $BACKUP_FILE"

    # Cleanup old backups (keep last 10)
    cd "$BACKUP_DIR" && ls -t $(basename $FILE_PATH)*.bak | tail -n +11 | xargs rm -f 2>/dev/null

    exit 0
else
    echo "[HOOK WARNING] Backup failed. Continuing anyway..."
    exit 0  # Don't block on backup failure
fi
'''
    return hook_script

backup_hook = create_backup_hook()
print("\nHook Script:")
print(backup_hook)
print("\nConfiguration in CLAUDE.md:")
print("""
hooks:
  before_tool:
    - name: backup-before-edit
      run: scripts/backup-before-edit.sh
      description: Backup files before Edit operations
""")

# --------------------------------------------------------------------------
# EXAMPLE 3: Error Notification Hook
# --------------------------------------------------------------------------
print("\n--- EXAMPLE 3: Error Notification Hook ---")

def create_error_notification_hook():
    """
    Create an on_error hook that sends notifications when errors occur.

    This hook:
    1. Captures error details
    2. Formats a notification message
    3. Sends to Slack/Teams/Email
    """
    hook_script = '''#!/bin/bash
# error-notification.sh - Send error notification

ERROR_MESSAGE=$1
TOOL_NAME=$2
FILE_PATH=$3

echo "[HOOK] Sending error notification..."

# Format message for Slack
MESSAGE="Error in Claude Code session
Tool: $TOOL_NAME
File: $FILE_PATH
Error: $ERROR_MESSAGE
Time: $(date)"

# Send to Slack webhook (set SLACK_WEBHOOK_URL environment variable)
if [ -n "$SLACK_WEBHOOK_URL" ]; then
    curl -s -X POST "$SLACK_WEBHOOK_URL" \\
        -H 'Content-type: application/json' \\
        --data "{\\"text\\": \\"$MESSAGE\\"}"
    echo "[HOOK] Slack notification sent"
else
    echo "[HOOK WARNING] SLACK_WEBHOOK_URL not set, skipping notification"
fi

exit 0  # Always exit 0 for on_error hooks
'''
    return hook_script

error_hook = create_error_notification_hook()
print("\nHook Script:")
print(error_hook)
print("\nConfiguration in CLAUDE.md:")
print("""
hooks:
  on_error:
    - name: error-notification
      run: scripts/error-notification.sh
      description: Send notifications on errors
""")

# ============================================================================
# SECTION 5: ENVIRONMENT-SPECIFIC HOOK CONFIGURATIONS
# ============================================================================
#
# Hooks can be configured differently based on the environment.
# This allows for stricter controls in production while maintaining
# developer-friendly settings in development.

def create_environment_hooks(environment="development"):
    """
    Create hook configuration based on environment.

    Args:
        environment: development, staging, or production

    Returns:
        dict: Hook configuration for the environment
    """
    configs = {
        "development": {
            "hooks": [
                {
                    "name": "lint-check",
                    "type": "before_tool",
                    "run": "scripts/lint.sh",
                    "timeout_ms": 30000,
                    "continue_on_error": True
                }
            ],
            "permissions": {
                "allow": ["Bash", "Read", "Write", "Grep", "Glob", "Edit"],
                "deny": [],
                "require_confirmation": ["Bash"]
            }
        },
        "staging": {
            "hooks": [
                {
                    "name": "lint-check",
                    "type": "before_tool",
                    "run": "scripts/lint.sh",
                    "timeout_ms": 30000,
                    "continue_on_error": False
                },
                {
                    "name": "backup",
                    "type": "before_tool",
                    "run": "scripts/backup.sh",
                    "timeout_ms": 10000,
                    "continue_on_error": True
                },
                {
                    "name": "notify",
                    "type": "after_tool",
                    "run": "scripts/notify.sh",
                    "timeout_ms": 5000,
                    "continue_on_error": True
                }
            ],
            "permissions": {
                "allow": ["Bash", "Read", "Write", "Grep", "Glob", "Edit"],
                "deny": [],
                "require_confirmation": ["Write", "Edit", "Bash"]
            }
        },
        "production": {
            "hooks": [
                {
                    "name": "security-scan",
                    "type": "before_tool",
                    "run": "scripts/security-scan.sh",
                    "timeout_ms": 60000,
                    "continue_on_error": False
                },
                {
                    "name": "backup",
                    "type": "before_tool",
                    "run": "scripts/backup.sh",
                    "timeout_ms": 30000,
                    "continue_on_error": False
                },
                {
                    "name": "audit-log",
                    "type": "after_tool",
                    "run": "scripts/audit-log.sh",
                    "timeout_ms": 5000,
                    "continue_on_error": True
                },
                {
                    "name": "error-alert",
                    "type": "on_error",
                    "run": "scripts/error-alert.sh",
                    "timeout_ms": 5000,
                    "continue_on_error": True
                }
            ],
            "permissions": {
                "allow": ["Read", "Grep", "Glob"],
                "deny": ["Bash", "Write", "Edit"],
                "require_confirmation": [],
                "description": "Production: Read-only access"
            }
        }
    }

    print(f"\n=== Environment: {environment.upper()} ===")
    print(f"Number of hooks: {len(configs[environment]['hooks'])}")
    for hook in configs[environment]['hooks']:
        print(f"  - {hook['name']} ({hook['type']})")
    return configs[environment]

# Show configurations for each environment
for env in ["development", "staging", "production"]:
    create_environment_hooks(env)

# ============================================================================
# SECTION 6: SECURITY CONSIDERATIONS
# ============================================================================

print("\n" + "=" * 70)
print("SECURITY CONSIDERATIONS FOR HOOK SCRIPTS")
print("=" * 70)

security_considerations = """
1. INPUT VALIDATION
   - Always validate inputs in hook scripts
   - Never trust file paths without validation
   - Sanitize all user-provided data

2. TIMEOUT LIMITS
   - Set reasonable timeouts for hook scripts
   - Prevents runaway hooks from blocking operations
   - Consider max_timeout of 60 seconds for most hooks

3. ERROR HANDLING
   - Hook failures should not necessarily block operations
   - Consider continue_on_error flag appropriately
   - Log all hook errors for debugging

4. CREDENTIAL SECURITY
   - Never hardcode credentials in hook scripts
   - Use environment variables for sensitive data
   - Store secrets in secure credential managers

5. FILE PERMISSIONS
   - Hook scripts should have minimal permissions (644)
   - Consider restricting who can modify hook scripts
   - Review hooks before adding to CLAUDE.md

6. LOGGING AND AUDITING
   - Log all hook executions
   - Include timestamps and user information
   - Store logs for compliance requirements

7. SANDBOXING
   - Consider running hooks in restricted environments
   - Limit filesystem access to necessary directories
   - Use containers or chroot where possible

CRITICAL: Hooks run with the same permissions as Claude Code itself.
A compromised hook can execute arbitrary code!
"""

print(security_considerations)

# ============================================================================
# SECTION 7: REAL-TIME SCENARIOS
# ============================================================================

print("\n" + "=" * 70)
print("REAL-TIME SCENARIOS")
print("=" * 70)

print("\n--- SCENARIO 1: Enforcing Code Quality Standards ---")
print("""
Situation: Your team wants to ensure all code changes meet quality standards.

Implementation:
1. Create a pre-edit hook that runs linters
2. Configure the hook to block edits on lint failure
3. Add appropriate error messages for developers

Result: Better code quality without manual review for simple issues.
""")

print("\n--- SCENARIO 2: Production Safety Controls ---")
print("""
Situation: You need to prevent accidental production deployments.

Implementation:
1. Configure production permissions to read-only
2. Add backup hooks before any write operations
3. Require multi-factor confirmation for production edits
4. Log all operations for audit trail

Result: Production changes require explicit approval and are always logged.
""")

print("\n--- SCENARIO 3: Developer Onboarding ---")
print("""
Situation: New developers need guidance on project conventions.

Implementation:
1. Create informational before_tool hooks
2. Hooks provide hints and best practices
3. Link to CLAUDE.md documentation

Result: Self-documenting development environment.
""")

# ============================================================================
# SECTION 8: COMMON MISTAKES
# ============================================================================

print("\n" + "=" * 70)
print("COMMON MISTAKES TO AVOID")
print("=" * 100)

mistakes = [
    ("No error handling", "Hook failure crashes the session", "Use try/catch and continue_on_error"),
    ("No timeout", "Hooks run forever", "Always set reasonable timeouts"),
    ("Hardcoded paths", "Fails on different systems", "Use relative paths or env vars"),
    ("Overly permissive", "Security bypass", "Use minimal permissions"),
    ("No logging", "No visibility into failures", "Always log hook activity"),
    ("Missing input validation", "Security vulnerability", "Validate all inputs"),
    ("No rollback", "Partial failures leave bad state", "Implement rollback on error")
]

print("\n{:<30} {:<35} {:<35}".format("MISTAKE", "WRONG", "RIGHT"))
print("-" * 100)
for mistake, wrong, right in mistakes:
    print(f"{mistake:<30} {wrong:<35} {right:<35}")

# ============================================================================
# SECTION 9: INTERVIEW Q&A
# ============================================================================

print("\n" + "=" * 70)
print("INTERVIEW QUESTIONS AND ANSWERS")
print("=" * 70)

qa_pairs = [
    (
        "Q: Explain the hook system in Claude Code.",
        """
A: Hooks are automated actions that execute at specific points in Claude Code's
   workflow. There are three types:

   1. before_tool: Runs before a tool executes, can validate inputs,
      check permissions, or prepare the environment.

   2. after_tool: Runs after a tool completes, useful for notifications,
      cleanup, or updating external systems.

   3. on_error: Runs when an error occurs, for error handling,
      notifications, or rollback operations.

   Hooks are configured in CLAUDE.md and can be scoped to specific
   environments or directories.
        """
    ),
    (
        "Q: How do you configure permissions in Claude Code?",
        """
A: Permissions are configured in settings.json or via CLAUDE.md hooks.
   The three permission levels are:

   1. allow: Tool executes without confirmation
   2. deny: Tool is blocked entirely
   3. require_confirmation: User must approve before execution

   Permissions can be set at user level (defaults) or project level
   (overrides). The syntax is:

   "permissions": {
     "allow": ["Read", "Grep", "Glob"],
     "deny": ["Edit", "Bash"],
     "require_confirmation": ["Write"]
   }
        """
    ),
    (
        "Q: How do you create a backup hook before destructive operations?",
        """
A: Create a before_tool hook that:
   1. Takes the file path as an argument
   2. Creates a timestamped backup copy
   3. Stores backups in a designated directory
   4. Cleans up old backups to save space
   5. Exits 0 to allow the operation to proceed

   The hook script would be something like:
   #!/bin/bash
   cp $1 .backups/$(basename $1).$(date +%Y%m%d_%H%M%S).bak
   exit 0
        """
    ),
    (
        "Q: What security considerations apply to hooks?",
        """
A: Security considerations include:
   1. INPUT VALIDATION: Always validate inputs, never trust paths
   2. TIMEOUTS: Set limits to prevent runaway hooks
   3. CREDENTIALS: Use env vars, never hardcode secrets
   4. PERMISSIONS: Run hooks with minimal required permissions
   5. LOGGING: Log all hook executions for audit
   6. SANDBOXING: Consider restricted execution environments

   Remember: Hooks run with Claude Code's permissions, so a compromised
   hook can execute arbitrary code!
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
1. HOOK TYPES
   - before_tool: Pre-validation, preparation
   - after_tool: Notifications, cleanup
   - on_error: Error handling, recovery

2. HOOK CONFIGURATION
   - Configured in CLAUDE.md hooks section
   - Can be scoped to environments
   - Supports timeout and error handling options

3. PERMISSION SYSTEM
   - allow: Execute without confirmation
   - deny: Block execution
   - require_confirmation: Ask first
   - Hierarchical: Project > User

4. PRACTICAL HOOK EXAMPLES
   - Pre-edit lint check
   - Backup before modification
   - Error notifications
   - Security scanning

5. ENVIRONMENT-SPECIFIC CONFIGURATION
   - Development: Lighter controls, faster iteration
   - Staging: Moderate controls, testing
   - Production: Strict controls, maximum auditing

6. SECURITY BEST PRACTICES
   - Validate all inputs
   - Set reasonable timeouts
   - Use environment variables for secrets
   - Log all hook executions
   - Review hooks before deployment

7. COMMON PATTERNS
   - Validation hooks before operations
   - Backup hooks for destructive operations
   - Notification hooks for completion/errors
   - Audit hooks for compliance
"""

print(lessons)

# ============================================================================
# SYNTAX VERIFICATION
# ============================================================================

print("\n=== File Syntax Verification ===")
print("This file has been created successfully.")
print("Run: python -m py_compile <file_path> to verify syntax.")
print("=" * 70)
