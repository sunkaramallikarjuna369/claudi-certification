# ============================================================================
# COMPREHENSIVE TEMPLATE: Claude Code Configuration Master Reference
# Domain 3: Configuration & Workflows (20% of Certification)
# ============================================================================
#
# PURPOSE: This template serves as a comprehensive reference combining all
# patterns from Domain 3. Use it as a starting point for projects and as
# a study aid for certification.
#
# ============================================================================
# HOW TO USE THIS TEMPLATE
# ============================================================================
#
# 1. Copy sections relevant to your project
# 2. Customize with project-specific values
# 3. Update CLAUDE.md with your configuration
# 4. Test in non-production first
# 5. Share with team members
#
# ============================================================================
# SECTION 1: BASIC SETUP AND CONFIGURATION
# ============================================================================
#
# This section covers the fundamental setup required for Claude Code,
# including API key management, settings configuration, and project structure.
#
# ============================================================================

import os
import json
from typing import Dict, Any, List, Optional
from pathlib import Path

# --------------------------------------------------------------------------
# API KEY MANAGEMENT
# --------------------------------------------------------------------------
#
# CRITICAL: API keys should NEVER be hardcoded. Use environment variables.
#
# The ANTHROPIC_API_KEY environment variable is the standard way to provide
# authentication to Claude Code. For local development, use a .env file.
# For CI/CD, use environment variables injected by the CI system.
#

def load_environment_config() -> Dict[str, str]:
    """
    Load configuration from environment variables.

    This is the recommended way to configure Claude Code:
    - Production: Use CI/CD environment variables
    - Local: Use .env file loaded by your shell or a dotenv library

    Environment Variables:
    - ANTHROPIC_API_KEY: Your Anthropic API key
    - CLAUDE_MODEL: Model to use (default: haiku)
    - CLAUDE_TIMEOUT: Timeout in milliseconds

    Returns:
        dict: Configuration values from environment
    """
    config = {
        "api_key": os.environ.get("ANTHROPIC_API_KEY", ""),
        "model": os.environ.get("CLAUDE_MODEL", "claude-haiku-4-5-20250601"),
        "timeout_ms": int(os.environ.get("CLAUDE_TIMEOUT", "120000")),
        "max_tokens": int(os.environ.get("CLAUDE_MAX_TOKENS", "8192")),
        "temperature": float(os.environ.get("CLAUDE_TEMPERATURE", "0.7")),
        "is_ci": os.environ.get("CI", "false").lower() == "true"
    }

    # Validate required configuration
    if not config["api_key"] and not config["is_ci"]:
        print("WARNING: ANTHROPIC_API_KEY not set. Claude Code will prompt for authentication.")

    return config

def load_env_file(filepath: str = ".env") -> Dict[str, str]:
    """
    Load environment variables from a .env file.

    This function parses .env files for local development.
    In production/CI, use actual environment variables.

    Args:
        filepath: Path to the .env file

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
                    key = key.strip()
                    value = value.strip()
                    # Remove quotes from value
                    if value and value[0] in ['"', "'"]:
                        value = value[1:-1]
                    env_vars[key] = value
    except FileNotFoundError:
        print(f"INFO: .env file not found at {filepath}")

    return env_vars

# --------------------------------------------------------------------------
# MODEL SELECTION
# --------------------------------------------------------------------------
#
# Claude Code supports multiple models with different capabilities and costs.
# Use the appropriate model for each task to optimize cost and performance.
#

AVAILABLE_MODELS = {
    "haiku": {
        "name": "claude-haiku-4-5-20250601",
        "speed": "Fastest",
        "cost": "Lowest",
        "best_for": [
            "Simple file edits",
            "Documentation updates",
            "Repetitive refactoring",
            "Code formatting",
            "Bulk operations"
        ],
        "context_window": "200K tokens"
    },
    "sonnet": {
        "name": "claude-sonnet-4-5-20250601",
        "speed": "Medium",
        "cost": "Medium",
        "best_for": [
            "Code review",
            "Feature implementation",
            "Documentation generation",
            "Testing",
            "Most development tasks"
        ],
        "context_window": "200K tokens"
    },
    "opus": {
        "name": "claude-opus-4-5-20250601",
        "speed": "Slowest",
        "cost": "Highest",
        "best_for": [
            "Architecture decisions",
            "Complex debugging",
            "Large refactoring",
            "Technical design documents",
            "Complex reasoning tasks"
        ],
        "context_window": "200K tokens"
    }
}

def get_recommended_model(task_type: str) -> str:
    """
    Get the recommended model for a task type.

    Args:
        task_type: Type of task to perform

    Returns:
        str: Recommended model name
    """
    recommendations = {
        "simple_edit": "haiku",
        "documentation": "haiku",
        "code_review": "sonnet",
        "feature_implementation": "sonnet",
        "architecture": "opus",
        "complex_debugging": "opus",
        "default": "sonnet"
    }

    return AVAILABLE_MODELS[recommendations.get(task_type, "default")]["name"]

# ============================================================================
# SECTION 2: SETTINGS CONFIGURATION
# ============================================================================
#
# Claude Code uses JSON configuration files for settings. There are two
# levels: user-level (global defaults) and project-level (per-project).
#

def create_user_settings() -> Dict[str, Any]:
    """
    Create user-level settings for Claude Code.

    These settings apply to all projects for this user.
    Place in: ~/.claude/settings.json

    Returns:
        dict: User-level settings configuration
    """
    return {
        "model": "claude-sonnet-4-5-20250601",
        "max_tokens": 8192,
        "temperature": 0.7,
        "timeout_ms": 120000,
        "stream": True,
        "permissions": {
            "allow": ["Bash", "Read", "Write", "Grep", "Glob", "Edit"],
            "deny": [],
            "require_confirmation": ["Bash"]
        }
    }

def create_project_settings(project_type: str = "web") -> Dict[str, Any]:
    """
    Create project-level settings for Claude Code.

    These settings apply only to this project and override user settings.
    Place in: .claude/settings.json or configure in CLAUDE.md

    Args:
        project_type: Type of project (web, api, library, etc.)

    Returns:
        dict: Project-level settings configuration
    """
    project_configs = {
        "web": {
            "model": "claude-sonnet-4-5-20250601",
            "permissions": {
                "allow": ["Bash", "Read", "Write", "Grep", "Glob", "Edit"],
                "deny": [],
                "require_confirmation": ["Write", "Edit"]
            },
            "hooks": {
                "before_tool": ["scripts/pre-edit-lint.sh"],
                "after_tool": [],
                "on_error": ["scripts/error-notify.sh"]
            }
        },
        "api": {
            "model": "claude-sonnet-4-5-20250601",
            "permissions": {
                "allow": ["Bash", "Read", "Write", "Grep", "Glob", "Edit"],
                "deny": ["Bash"],
                "require_confirmation": ["Bash", "Write"]
            },
            "hooks": {
                "before_tool": ["scripts/security-check.sh"],
                "after_tool": ["scripts/update-api-docs.sh"],
                "on_error": ["scripts/error-notify.sh"]
            }
        },
        "production": {
            "model": "claude-opus-4-5-20250601",
            "permissions": {
                "allow": ["Read", "Grep", "Glob"],
                "deny": ["Bash", "Write", "Edit"],
                "require_confirmation": []
            },
            "hooks": {
                "before_tool": [
                    "scripts/security-scan.sh",
                    "scripts/backup.sh"
                ],
                "after_tool": ["scripts/audit-log.sh"],
                "on_error": [
                    "scripts/error-notify.sh",
                    "scripts/alert-security.sh"
                ]
            }
        }
    }

    return project_configs.get(project_type, project_configs["web"])

# ============================================================================
# SECTION 3: HOOK CONFIGURATION
# ============================================================================
#
# Hooks are automated scripts that run at specific points in Claude Code's
# execution. They enable powerful customization and automation.
#

def create_hook_configuration() -> Dict[str, List[Dict[str, Any]]]:
    """
    Create a comprehensive hook configuration.

    Hooks run automatically at specific points:
    - before_tool: Before each tool execution
    - after_tool: After each tool execution
    - on_error: When an error occurs

    Returns:
        dict: Comprehensive hook configuration
    """
    return {
        "before_tool": [
            {
                "name": "lint-check",
                "description": "Run linter before Edit operations",
                "run": "scripts/lint-check.sh",
                "condition": "tool == 'Edit'",
                "timeout_ms": 30000,
                "block_if_fails": True
            },
            {
                "name": "backup-before-edit",
                "description": "Create backup before file modification",
                "run": "scripts/backup.sh",
                "condition": "tool in ['Edit', 'Write']",
                "timeout_ms": 10000,
                "block_if_fails": False
            },
            {
                "name": "security-check",
                "description": "Check for security issues",
                "run": "scripts/security-check.sh",
                "condition": "tool in ['Edit', 'Write', 'Bash']",
                "timeout_ms": 60000,
                "block_if_fails": True
            }
        ],
        "after_tool": [
            {
                "name": "format-after-edit",
                "description": "Format code after Edit operations",
                "run": "scripts/format.sh",
                "condition": "tool == 'Edit'",
                "timeout_ms": 10000,
                "block_if_fails": False,
                "async": True
            },
            {
                "name": "update-task",
                "description": "Update task management system",
                "run": "scripts/update-task.sh",
                "condition": "always",
                "timeout_ms": 5000,
                "block_if_fails": False,
                "async": True
            },
            {
                "name": "notification",
                "description": "Send Slack notification",
                "run": "scripts/notify.sh",
                "condition": "tool in ['Bash']",
                "timeout_ms": 5000,
                "block_if_fails": False,
                "async": True
            }
        ],
        "on_error": [
            {
                "name": "error-log",
                "description": "Log error details",
                "run": "scripts/log-error.sh",
                "timeout_ms": 5000,
                "block_if_fails": False
            },
            {
                "name": "error-notify",
                "description": "Send error notification",
                "run": "scripts/error-notify.sh",
                "condition": "severity == 'high'",
                "timeout_ms": 5000,
                "block_if_fails": False
            },
            {
                "name": "rollback",
                "description": "Rollback changes on error",
                "run": "scripts/rollback.sh",
                "condition": "severity == 'critical'",
                "timeout_ms": 30000,
                "block_if_fails": False
            }
        ]
    }

def create_backup_hook_script() -> str:
    """
    Create a comprehensive backup hook script.

    This hook creates timestamped backups before file modifications.
    It also cleans up old backups to save disk space.

    Returns:
        str: Bash script content for backup hook
    """
    return '''#!/bin/bash
# backup-before-edit.sh - Create backup before file modification
# This hook runs before Edit/Write operations to create backups

FILE_PATH="$1"
OPERATION="$2"
BACKUP_DIR=".claude/backups"
MAX_BACKUPS=10

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Validate input
if [ -z "$FILE_PATH" ]; then
    echo "[HOOK ERROR] No file path provided"
    exit 1
fi

if [ ! -f "$FILE_PATH" ]; then
    echo "[HOOK INFO] File does not exist, no backup needed"
    exit 0
fi

# Create timestamped backup
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
FILENAME=$(basename "$FILE_PATH")
BACKUP_FILE="$BACKUP_DIR/${FILENAME}.${TIMESTAMP}.bak"

echo "[HOOK] Creating backup: $BACKUP_FILE"

if cp "$FILE_PATH" "$BACKUP_FILE"; then
    echo "[HOOK] Backup created successfully"

    # Clean up old backups (keep most recent)
    cd "$BACKUP_DIR" || exit 1
    BACKUPS_TO_DELETE=$(ls -t "${FILENAME}".*.bak 2>/dev/null | tail -n +$((MAX_BACKUPS + 1)))

    if [ -n "$BACKUPS_TO_DELETE" ]; then
        echo "[HOOK] Cleaning up old backups: $(echo $BACKUPS_TO_DELETE | wc -l) files"
        echo "$BACKUPS_TO_DELETE" | xargs rm -f 2>/dev/null
    fi

    exit 0
else
    echo "[HOOK ERROR] Backup failed"
    exit 0  # Don't block on backup failure
fi
'''

def create_error_notification_hook_script() -> str:
    """
    Create an error notification hook script.

    This hook sends notifications (Slack, email, etc.) when errors occur.

    Returns:
        str: Bash script content for error notification hook
    """
    return '''#!/bin/bash
# error-notify.sh - Send error notifications
# This hook runs when errors occur to alert the team

ERROR_MESSAGE="$1"
ERROR_SEVERITY="${2:-medium}"
ERROR_TOOL="$3"
ERROR_FILE="$4"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# Format message for Slack
SLACK_MESSAGE="Error in Claude Code Session
Time: $TIMESTAMP
Tool: $ERROR_TOOL
File: $ERROR_FILE
Severity: $ERROR_SEVERITY
Error: $ERROR_MESSAGE"

# Send to Slack webhook if configured
if [ -n "$SLACK_WEBHOOK_URL" ]; then
    curl -s -X POST "$SLACK_WEBHOOK_URL" \\
        -H 'Content-type: application/json' \\
        --data "{\\"text\\": \\"$SLACK_MESSAGE\\"}" > /dev/null

    if [ $? -eq 0 ]; then
        echo "[HOOK] Slack notification sent successfully"
    else
        echo "[HOOK WARNING] Failed to send Slack notification"
    fi
fi

# Log error for audit
echo "[$(date +"%Y-%m-%d %H:%M:%S")] ERROR: $ERROR_MESSAGE | Tool: $ERROR_TOOL | File: $ERROR_FILE" >> .claude/logs/errors.log

exit 0  # Always exit 0 for on_error hooks
'''

# ============================================================================
# SECTION 4: WORKFLOW AUTOMATION
# ============================================================================
#
# Workflows automate repetitive tasks and complex multi-step processes.
# They should be idempotent, well-logged, and have proper error handling.
#

def create_workflow_definition(
    name: str,
    steps: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Create a workflow definition.

    Workflows define multi-step processes with error handling,
    retry logic, and state management.

    Args:
        name: Workflow name
        steps: List of workflow steps

    Returns:
        dict: Complete workflow definition
    """
    return {
        "name": name,
        "version": "1.0",
        "description": f"Automated workflow: {name}",
        "steps": steps,
        "error_handling": {
            "retry_count": 3,
            "retry_delay_ms": 1000,
            "rollback_on_failure": True,
            "notify_on_failure": True
        },
        "logging": {
            "enabled": True,
            "log_file": f".claude/logs/workflow-{name}.log",
            "verbose": True
        },
        "timeout_ms": 600000
    }

def create_feature_workflow() -> Dict[str, Any]:
    """
    Create a complete feature development workflow.

    This workflow covers the full feature development process
    from branch creation to pull request.

    Returns:
        dict: Feature development workflow definition
    """
    return create_workflow_definition(
        name="feature-development",
        steps=[
            {
                "id": 1,
                "name": "prerequisite-check",
                "description": "Verify Git is available and working directory is clean",
                "tool": "Bash",
                "command": "git status --porcelain",
                "validation": "output is empty",
                "continue_on_failure": False
            },
            {
                "id": 2,
                "name": "create-branch",
                "description": "Create feature branch",
                "tool": "Bash",
                "command": "git checkout -b feature/${TICKET_ID}-${FEATURE_NAME}",
                "continue_on_failure": False
            },
            {
                "id": 3,
                "name": "implement-feature",
                "description": "Implement the feature",
                "tool": "Edit",
                "instruction": "Implement the ${FEATURE_NAME} feature based on ${TICKET_ID}",
                "continue_on_failure": False,
                "timeout_ms": 300000
            },
            {
                "id": 4,
                "name": "run-tests",
                "description": "Run test suite",
                "tool": "Bash",
                "command": "npm test",
                "continue_on_failure": False,
                "retry_count": 2
            },
            {
                "id": 5,
                "name": "commit-changes",
                "description": "Commit changes with conventional format",
                "tool": "Bash",
                "command": "git add -A && git commit -m '${COMMIT_MESSAGE}'",
                "continue_on_failure": False
            },
            {
                "id": 6,
                "name": "push-branch",
                "description": "Push branch to remote",
                "tool": "Bash",
                "command": "git push -u origin HEAD",
                "continue_on_failure": False
            },
            {
                "id": 7,
                "name": "create-pr",
                "description": "Create pull request",
                "tool": "Bash",
                "command": "gh pr create --fill",
                "continue_on_failure": False
            }
        ]
    )

# ============================================================================
# SECTION 5: CI/CD INTEGRATION
# ============================================================================
#
# Claude Code integrates with CI/CD pipelines for automated development tasks.
# Key considerations: non-interactive mode, exit codes, and secure credential
# management.
#

def create_ci_environment_config() -> Dict[str, Any]:
    """
    Create configuration for CI/CD environment.

    CI environments require special handling:
    - Non-interactive mode
    - Structured output for parsing
    - Proper exit codes
    - Secure credential management

    Returns:
        dict: CI environment configuration
    """
    return {
        "mode": "non-interactive",
        "model": "claude-haiku-4-5-20250601",  # Cost-effective for CI
        "stream": False,
        "output_format": "json",
        "timeout_ms": 300000,  # 5 minutes
        "retry_count": 3,
        "retry_delay_ms": 5000,
        "error_handling": {
            "fail_on_error": True,
            "log_level": "debug",
            "save_artifacts": True,
            "artifact_dir": ".claude/artifacts"
        }
    }

def create_github_actions_workflow() -> str:
    """
    Create a GitHub Actions workflow for Claude Code integration.

    Returns:
        str: GitHub Actions workflow YAML
    """
    return '''name: Claude Code Integration

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main, develop]
  workflow_dispatch:

env:
  CLAUDE_MODEL: claude-haiku-4-5-20250601
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

jobs:
  code-review:
    runs-on: ubuntu-latest
    name: Claude Code Review
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Install Claude Code
        run: npm install -g @anthropic-ai/claude-code

      - name: Run Code Review
        run: |
          claude --print --no-stream --model $CLAUDE_MODEL \\
            --prompt "Review code changes in this PR. Format output as JSON with issues array."

      - name: Parse and Post Review
        if: always()
        run: ./scripts/parse-review.js

  automated-task:
    runs-on: ubuntu-latest
    name: Claude Automated Task
    if: github.event_name == 'workflow_dispatch'
    steps:
      - uses: actions/checkout@v4

      - name: Run Automated Task
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          claude --print --model $CLAUDE_MODEL \\
            --prompt "Update all docstrings in src/ where missing."
'''

# ============================================================================
# SECTION 6: ERROR HANDLING AND RECOVERY
# ============================================================================

def create_error_handlingStrategies() -> Dict[str, Dict[str, Any]]:
    """
    Create error handling strategies for different scenarios.

    Returns:
        dict: Error handling strategies
    """
    return {
        "retry_with_backoff": {
            "type": "retry",
            "max_attempts": 3,
            "initial_delay_ms": 1000,
            "multiplier": 2,
            "max_delay_ms": 30000,
            "use_case": "Network timeouts, transient failures",
            "example": """
for attempt in range(max_attempts):
    try:
        result = execute_operation()
        break
    except TransientError as e:
        if attempt == max_attempts - 1:
            raise
        delay = min(initial_delay * (multiplier ** attempt), max_delay)
        time.sleep(delay / 1000)
"""
        },
        "rollback": {
            "type": "rollback",
            "checkpoint_frequency": 5,
            "use_case": "Deployments, database operations",
            "example": """
# Save checkpoint before operation
save_checkpoint(state)

try:
    execute_operation()
except:
    rollback_to_checkpoint(state)
    raise
"""
        },
        "skip_continue": {
            "type": "skip_on_failure",
            "use_case": "Non-critical cleanup, optional features",
            "example": """
try:
    execute_optional_task()
except:
    log_warning("Optional task failed, continuing")
    # Continue with main operation
"""
        },
        "fail_fast": {
            "type": "fail_immediately",
            "use_case": "Critical validation, security checks",
            "example": """
if not critical_validation():
    raise CriticalError("Validation failed - aborting")
"""
        }
    }

# ============================================================================
# SECTION 7: DEVELOPMENT BEST PRACTICES
# ============================================================================

def create_project_documentation() -> str:
    """
    Create comprehensive project documentation for CLAUDE.md.

    This should be the content of your CLAUDE.md file, customized
    for your specific project.

    Returns:
        str: CLAUDE.md content
    """
    return '''# Project Name

Brief description of what this project does.

## Project Overview
- **Purpose**: Why this project exists
- **Users**: Who this project serves
- **Key Features**: Main capabilities

## Tech Stack
- Language: [e.g., Python 3.11+]
- Framework: [e.g., FastAPI]
- Database: [e.g., PostgreSQL]
- Other: [List key tools]

## Project Structure
```
project-root/
|-- src/           # Source code
|-- tests/         # Test files
|-- configs/       # Configuration
|-- scripts/       # Utility scripts
|-- docs/         # Documentation
|-- .claude/       # Claude Code config (hooks, state)
```

## Development Setup

### Prerequisites
- List required tools and versions

### Installation
```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configuration
```

### Running Locally
```bash
python src/main.py
```

## Coding Standards
- Follow [style guide]
- Use type hints for all functions
- Maximum line length: 100 characters
- Write docstrings for public functions

## Testing
- Run tests: `pytest tests/`
- Coverage: `pytest --cov=src tests/`
- Minimum coverage: 80%

## Git Workflow
- Branch: `feature/<id>-description`
- Commit: `type(scope): description`
- PR requires: 2 approvals, passing CI

## Common Tasks
### Run all tests
```bash
pytest tests/ -v
```

### Build documentation
```bash
python scripts/build-docs.py
```

## Gotchas
- List common pitfalls and important notes
'''

# ============================================================================
# SECTION 8: MCP SERVER CONFIGURATION
# ============================================================================

def create_mcp_server_config() -> Dict[str, Dict[str, Any]]:
    """
    Create MCP server configurations.

    MCP (Model Context Protocol) servers extend Claude Code with
    additional capabilities.

    Returns:
        dict: MCP server configurations
    """
    return {
        "filesystem": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "./src"],
            "type": "filesystem",
            "description": "File system access",
            "enabled": True,
            "security": {
                "allowed_directories": ["./src", "./tests"],
                "read_only": False
            }
        },
        "git": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-git"],
            "type": "git",
            "description": "Git version control",
            "enabled": True,
            "security": {
                "readonly_operations": True
            }
        },
        "postgres": {
            "command": "docker",
            "args": ["run", "--rm", "-i", "pg-mcp-server"],
            "type": "database",
            "description": "PostgreSQL access",
            "enabled": False,
            "env": {
                "DATABASE_URL": "postgresql://user:pass@host:5432/db"
            },
            "security": {
                "readonly": True,
                "allowed_tables": ["users", "products"]
            }
        }
    }

# ============================================================================
# SECTION 9: SECURITY CONFIGURATION
# ============================================================================

def create_security_config() -> Dict[str, Any]:
    """
    Create comprehensive security configuration.

    Returns:
        dict: Security configuration
    """
    return {
        "api_key": {
            "rotation_days": 90,
            "storage": "environment_variable",
            "never_log": True
        },
        "permissions": {
            "default_policy": "deny",
            "explicit_require": True,
            "directory_scopes": {
                "src": ["Read", "Write", "Edit"],
                "tests": ["Read", "Write"],
                "configs": ["Read"],
                ".env": ["Deny"],
                "production": ["Read"]
            }
        },
        "hooks": {
            "require_review": True,
            "audit_all": True,
            "timeout_max": 60000
        },
        "audit": {
            "log_all_operations": True,
            "log_file": ".claude/logs/audit.log",
            "retention_days": 365,
            "alert_on_anomalies": True
        },
        "network": {
            "allowed_endpoints": ["api.anthropic.com"],
            "ssl_verify": True,
            "proxy": None
        }
    }

# ============================================================================
# SECTION 10: PERFORMANCE AND COST OPTIMIZATION
# ============================================================================

def create_optimization_config() -> Dict[str, Any]:
    """
    Create performance and cost optimization configuration.

    Returns:
        dict: Optimization configuration
    """
    return {
        "model_selection": {
            "auto_route": True,
            "rules": [
                {
                    "pattern": "Simple edit, format, lint",
                    "model": "claude-haiku-4-5-20250601",
                    "max_tokens": 500
                },
                {
                    "pattern": "Code review, testing, documentation",
                    "model": "claude-sonnet-4-5-20250601",
                    "max_tokens": 2000
                },
                {
                    "pattern": "Architecture, complex debugging",
                    "model": "claude-opus-4-5-20250601",
                    "max_tokens": 8000
                }
            ]
        },
        "context_management": {
            "auto_compact": True,
            "compact_threshold": 0.8,
            "max_context_tokens": 100000
        },
        "cost_monitoring": {
            "budget_alert": {
                "monthly_limit": 1000,
                "alert_threshold": 0.8
            },
            "track_by_project": True,
            "track_by_user": True
        },
        "batching": {
            "enabled": True,
            "max_batch_size": 10,
            "batch_timeout_ms": 5000
        }
    }

# ============================================================================
# SECTION 11: REAL-TIME SCENARIOS
# ============================================================================

SCENARIOS = {
    "new_project": {
        "title": "Setting Up a New Project",
        "steps": [
            "Create basic project structure",
            "Create CLAUDE.md with project documentation",
            "Configure .claude/settings.json with project-specific settings",
            "Add hooks for code quality",
            "Set up CI/CD pipeline",
            "Test with simple task"
        ]
    },
    "production_fix": {
        "title": "Emergency Production Fix",
        "steps": [
            "Verify production environment permissions are strict",
            "Create hotfix branch",
            "Run security validation",
            "Implement minimal fix",
            "Comprehensive testing",
            "Rollback plan ready",
            "Multi-approval required",
            "Notify team of changes"
        ]
    },
    "team_onboarding": {
        "title": "Onboarding New Team Member",
        "steps": [
            "Share CLAUDE.md for context",
            "Provide .env.example template",
            "Explain project structure",
            "Demonstrate Claude Code usage",
            "Review coding standards",
            "Shadow first task"
        ]
    }
}

# ============================================================================
# SECTION 12: INTERVIEW Q&A REFERENCE
# ============================================================================

INTERVIEW_QA = [
    {
        "question": "How do you configure Claude Code for a new project?",
        "answer": """Configuration involves:
1. API key setup via ANTHROPIC_API_KEY env var
2. Create CLAUDE.md with project documentation
3. Optionally create .claude/settings.json
4. Configure hooks for project needs
5. Test with simple task"""
    },
    {
        "question": "Explain the hook system in Claude Code.",
        "answer": """Hooks execute at specific points:
- before_tool: Pre-validation, preparation
- after_tool: Notifications, cleanup
- on_error: Error handling, recovery
Each can be configured with conditions, timeouts, and continue_on_error flag."""
    },
    {
        "question": "How do you integrate Claude Code in CI/CD?",
        "answer": """CI integration requires:
1. Non-interactive mode: --print --no-stream
2. Environment variables for config:
   - ANTHROPIC_API_KEY from secrets
   - CLAUDE_MODEL selection
3. Proper exit code handling
4. Structured output for parsing
5. Timeout configuration"""
    },
    {
        "question": "What security considerations apply?",
        "answer": """Security requires:
1. API key rotation, never hardcode
2. Permission model (deny by default)
3. Hook script validation
4. Audit logging
5. Network restrictions
6. Secret management"""
    },
    {
        "question": "How do you optimize costs?",
        "answer": """Cost optimization strategies:
1. Use Haiku for simple tasks
2. Auto-routing based on task complexity
3. Context optimization and compacting
4. Batch operations where possible
5. Set monitoring and alerts"""
    }
]

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Demonstrate all configuration components."""
    print("=" * 70)
    print("CLAUDE CODE CONFIGURATION TEMPLATE")
    print("=" * 70)

    # Load configuration
    env_config = load_environment_config()
    print(f"\nEnvironment Config:")
    print(f"  Model: {env_config['model']}")
    print(f"  Timeout: {env_config['timeout_ms']}ms")
    print(f"  CI Mode: {env_config['is_ci']}")

    # Show available models
    print(f"\nAvailable Models:")
    for name, info in AVAILABLE_MODELS.items():
        print(f"  {name}: {info['name']} ({info['cost']})")

    # Show scenarios
    print(f"\nReal-Time Scenarios:")
    for key, scenario in SCENARIOS.items():
        print(f"  {key}: {scenario['title']}")

    print(f"\nConfiguration template loaded successfully!")
    print("Copy relevant sections to your project.")
    print("=" * 70)

if __name__ == "__main__":
    main()

# ============================================================================
# WHAT WE HAVE LEARNT - MASTER SUMMARY
# ============================================================================

"""
DOMAIN 3: CLAUDE CODE CONFIGURATION & WORKFLOWS - MASTER SUMMARY

1. BASIC SETUP
   - API key via environment variables
   - Model selection (Haiku/Sonnet/Opus)
   - Settings hierarchy (user > project)

2. HOOK SYSTEM
   - before_tool: Pre-validation, preparation
   - after_tool: Notifications, cleanup
   - on_error: Error handling, recovery
   - Conditions and timeouts for each

3. PERMISSIONS
   - allow, deny, require_confirmation
   - Deny by default (security)
   - Directory-based scoping

4. WORKFLOW AUTOMATION
   - Idempotent operations
   - Error recovery strategies
   - State management
   - Progress tracking

5. CI/CD INTEGRATION
   - Non-interactive mode (--print)
   - Exit code handling
   - GitHub Actions, GitLab, Jenkins
   - Secure credential management

6. DEVELOPMENT BEST PRACTICES
   - Project structure organization
   - CLAUDE.md documentation
   - Code review workflows
   - Testing strategies

7. ADVANCED CONFIGURATION
   - Custom tools development
   - MCP server integration
   - Performance tuning
   - Cost optimization

8. SECURITY HARDENING
   - API key rotation
   - Permission model
   - Audit logging
   - Network restrictions

9. REAL-TIME SCENARIOS
   - New project setup
   - Production fixes
   - Team onboarding
   - CI automation

10. INTERVIEW PREPARATION
    - Configuration questions
    - Hook system explanation
    - CI/CD integration
    - Security considerations
    - Cost optimization strategies
"""

# ============================================================================
# SYNTAX VERIFICATION
# ============================================================================

print("\n=== Template File Verification ===")
print("This template demonstrates all Domain 3 concepts.")
print("Run: python -m py_compile TEMPLATE.py to verify syntax.")
print("=" * 70)
