# ============================================================================
# PRACTICE FILE: Advanced Configuration Options
# Domain 3.6: Advanced Configuration Options
# ============================================================================
#
# PURPOSE: Learn advanced Claude Code configuration options including custom
# tool development, MCP server configuration, performance tuning, and
# enterprise security features.
#
# ============================================================================
# SECTION 1: CUSTOM TOOL DEVELOPMENT
# ============================================================================
#
# Claude Code can be extended with custom tools for specialized operations.
# Custom tools allow you to integrate project-specific functionality.
#
# ============================================================================

print("=" * 70)
print("CUSTOM TOOL DEVELOPMENT")
print("=" * 70)

def create_custom_tool_spec():
    """
    Example specification for a custom tool.
    """
    tool_spec = {
        "name": "database_query",
        "description": "Execute a read-only database query",
        "category": "data",
        "input_schema": {
            "type": "object",
            "properties": {
                "sql": {
                    "type": "string",
                    "description": "SQL query to execute (SELECT only)"
                },
                "params": {
                    "type": "array",
                    "description": "Query parameters"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum rows to return",
                    "default": 100,
                    "minimum": 1,
                    "maximum": 1000
                }
            },
            "required": ["sql"]
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "rows": {"type": "array"},
                "count": {"type": "integer"},
                "execution_time_ms": {"type": "number"}
            }
        },
        "security": {
            "allowed_roles": ["developer", "analyst"],
            "read_only": True,
            "query_validation": ["no_dml", "no_ddl", "no_drop"]
        }
    }
    return tool_spec

tool_spec = create_custom_tool_spec()
print("=== Custom Tool Specification Example ===")
print(f"Name: {tool_spec['name']}")
print(f"Description: {tool_spec['description']}")
print(f"Input Schema: {tool_spec['input_schema']}")
print(f"Security: {tool_spec['security']}")

# --------------------------------------------------------------------------
# EXAMPLE: Custom Tool Implementation
# --------------------------------------------------------------------------

custom_tool_example = '''
import json
import sqlite3
import re
from datetime import datetime

class DatabaseQueryTool:
    """Custom tool for executing safe database queries."""

    name = "database_query"
    description = "Execute read-only database queries"

    # Read-only queries only - no INSERT, UPDATE, DELETE, DROP, etc.
    DDL_KEYWORDS = ["CREATE", "ALTER", "DROP", "TRUNCATE"]
    DML_KEYWORDS = ["INSERT", "UPDATE", "DELETE", "REPLACE"]
    DCL_KEYWORDS = ["GRANT", "REVOKE"]

    def __init__(self, db_path: str):
        self.db_path = db_path

    def execute(self, sql: str, params: list = None, limit: int = 100) -> dict:
        """Execute a query and return results."""
        start_time = datetime.now()

        # Validate query is read-only
        if not self._is_read_only(sql):
            return {
                "error": "Only SELECT queries are allowed",
                "rows": [],
                "count": 0
            }

        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Add LIMIT if not present
            if "LIMIT" not in sql.upper():
                sql = f"{sql} LIMIT {limit}"

            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)

            rows = [dict(row) for row in cursor.fetchall()]
            conn.close()

            execution_time = (datetime.now() - start_time).total_seconds() * 1000

            return {
                "rows": rows,
                "count": len(rows),
                "execution_time_ms": round(execution_time, 2)
            }

        except Exception as e:
            return {
                "error": str(e),
                "rows": [],
                "count": 0
            }

    def _is_read_only(self, sql: str) -> bool:
        """Validate that the query is read-only."""
        sql_upper = sql.upper().strip()

        # Must start with SELECT
        if not sql_upper.startswith("SELECT"):
            return False

        # Check for forbidden keywords
        forbidden = self.DDL_KEYWORDS + self.DML_KEYWORDS + self.DCL_KEYWORDS
        for keyword in forbidden:
            if keyword in sql_upper:
                return False

        return True


# Tool registration (simplified)
TOOL_CONFIG = {
    "name": "database_query",
    "handler": DatabaseQueryTool,
    "config": {
        "db_path": os.environ.get("DATABASE_PATH", "data/app.db")
    }
}
'''

print("\n=== Custom Tool Implementation Example ===")
print(custom_tool_example[:1000] + "\n... (truncated)")

# ============================================================================
# SECTION 2: MCP SERVER CONFIGURATION
# ============================================================================
#
# MCP (Model Context Protocol) servers extend Claude Code with additional
# capabilities. Examples include file system access, database connections,
# API integrations, and more.
#
# ============================================================================

print("\n" + "=" * 70)
print("MCP SERVER CONFIGURATION")
print("=" * 70)

mcp_config_examples = {
    "filesystem": {
        "type": "filesystem",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem"],
        "description": "File system access for reading/writing files",
        "use_cases": [
            "Read source files",
            "Write configuration files",
            "Create project structure"
        ]
    },
    "git": {
        "type": "git",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-git"],
        "description": "Git operations for version control",
        "use_cases": [
            "Git status and history",
            "Branch management",
            "Commit creation"
        ]
    },
    "postgres": {
        "type": "database",
        "command": "docker",
        "args": ["run", "--rm", "-i", "pg-mcp-server"],
        "env": {
            "DATABASE_URL": "${DATABASE_URL}"
        },
        "description": "PostgreSQL database connections",
        "use_cases": [
            "Query database",
            "Schema inspection",
            "Migration execution"
        ]
    },
    "slack": {
        "type": "messaging",
        "command": "docker",
        "args": ["run", "--rm", "-i", "slack-mcp-server"],
        "env": {
            "SLACK_BOT_TOKEN": "${SLACK_BOT_TOKEN}"
        },
        "description": "Slack messaging integration",
        "use_cases": [
            "Send notifications",
            "Read channels",
            "Create threads"
        ]
    }
}

print("=== MCP Server Options ===")
for server, config in mcp_config_examples.items():
    print(f"\n{server.upper()}:")
    print(f"  Type: {config['type']}")
    print(f"  Command: {config['command']} {' '.join(config['args'])}")
    print(f"  Description: {config['description']}")
    print(f"  Use Cases:")
    for use_case in config['use_cases']:
        print(f"    - {use_case}")

# MCP settings configuration
mcp_settings_config = '''
# MCP Server Configuration in settings.json

{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "d:/projects/src"],
      "description": "Access to source code directory",
      "enabled": true
    },
    "git": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-git"],
      "description": "Git operations",
      "enabled": true
    },
    "postgres": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "--network", "app-network", "pg-mcp"],
      "env": {
        "DATABASE_URL": "postgresql://user:pass@db:5432/app"
      },
      "description": "PostgreSQL database access",
      "enabled": true,
      "allowedDatabases": ["app_production"]
    },
    "slack": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "slack-mcp"],
      "env": {
        "SLACK_BOT_TOKEN": "xoxb-..."
      },
      "description": "Slack notifications",
      "enabled": false
    }
  }
}
'''

print("\n=== MCP Settings Configuration ===")
print(mcp_settings_config[:1500] + "\n... (truncated)")

# ============================================================================
# SECTION 3: ADVANCED HOOK SCRIPTING
# ============================================================================

print("\n" + "=" * 70)
print("ADVANCED HOOK SCRIPTING")
print("=" * 70)

print("""
=== ADVANCED HOOK PATTERNS ===

1. CONDITIONAL HOOKS
   Hooks that run only under certain conditions.

   hooks:
     before_tool:
       - name: production-safety-check
         run: scripts/production-check.sh
         condition: environment == "production"
         block_if: true

2. CHAINED HOOKS
   Multiple hooks that run in sequence.

   hooks:
     before_tool:
       - name: lint
         run: scripts/lint.sh
         continue_on_error: false
       - name: format
         run: scripts/format.sh
         require_previous: lint
         continue_on_error: true

3. PARALLEL HOOKS
   Multiple hooks that run concurrently.

   hooks:
     before_tool:
       - name: parallel-checks
       type: parallel
       hooks:
         - name: security-scan
           run: scripts/security-scan.sh
         - name: dependency-check
           run: scripts/dependency-check.sh
         - name: license-check
           run: scripts/license-check.sh

4. ASYNC HOOKS
   Hooks that don't block the main operation.

   hooks:
     after_tool:
       - name: async-notification
         run: scripts/async-notify.sh
         async: true
         fire_and_forget: true

5. HOOK ARTIFACTS
   Hooks that produce artifacts for later use.

   hooks:
     after_tool:
       - name: generate-report
         run: scripts/generate-report.sh
         produces: reports/tool-output.json
         attach_to_context: true
""")

# --------------------------------------------------------------------------
# EXAMPLE: Complex Hook Script
# --------------------------------------------------------------------------

def create_complex_hook_script():
    """
    Example of a sophisticated hook with validation and rollback.
    """
    script = '''#!/usr/bin/env python3
"""Advanced pre-edit hook with validation and rollback."""

import sys
import os
import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

class PreEditHook:
    """Pre-edit hook with comprehensive validation."""

    def __init__(self):
        self.file_path = sys.argv[1] if len(sys.argv) > 1 else None
        self.operation = sys.argv[2] if len(sys.argv) > 2 else "edit"
        self.backup_dir = Path(".claude/backups")
        self.config_file = Path(".claude/hooks/config.json")

        # Load hook configuration
        self.config = self.load_config()

    def load_config(self) -> dict:
        """Load hook configuration."""
        if self.config_file.exists():
            with open(self.config_file) as f:
                return json.load(f)
        return {"enabled": True, "max_backup_age_days": 7}

    def run(self):
        """Main hook execution."""
        if not self.config.get("enabled", True):
            print("[HOOK] Hook disabled, allowing operation")
            return True

        if not self.file_path:
            print("[HOOK] No file specified, allowing operation")
            return True

        # Step 1: Validate file exists
        if not self.validate_file():
            return False

        # Step 2: Check file permissions
        if not self.check_permissions():
            return False

        # Step 3: Run validation scripts
        if not self.run_validation():
            return False

        # Step 4: Create backup
        if not self.create_backup():
            print("[HOOK WARNING] Backup failed, continuing anyway")
            # Don't block on backup failure

        # Step 5: Log operation
        self.log_operation()

        return True

    def validate_file(self) -> bool:
        """Validate file exists and is appropriate for editing."""
        file_path = Path(self.file_path)

        if not file_path.exists():
            print(f"[HOOK ERROR] File does not exist: {self.file_path}")
            return False

        # Check if file is in a protected directory
        protected_dirs = [".git", ".claude", "node_modules", "__pycache__"]
        if any(part in file_path.parts for part in protected_dirs):
            print(f"[HOOK ERROR] Cannot edit files in protected directories")
            return False

        # Check file size
        if file_path.stat().st_size > 10_000_000:  # 10MB
            print(f"[HOOK ERROR] File too large: {self.file_path}")
            return False

        return True

    def check_permissions(self) -> bool:
        """Check if we have permission to edit the file."""
        file_path = Path(self.file_path)

        # Check write permission
        if not os.access(file_path, os.W_OK):
            print(f"[HOOK ERROR] No write permission for: {self.file_path}")
            return False

        return True

    def run_validation(self) -> bool:
        """Run validation scripts on the file."""
        file_path = Path(self.file_path)

        validations = {
            ".py": ["python", "-m", "py_compile"],
            ".js": ["npm", "run", "lint:check"],
            ".ts": ["npx", "tsc", "--noEmit"],
        }

        ext = file_path.suffix
        if ext in validations:
            cmd = validations[ext] + [str(file_path)]
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=file_path.parent,
                    timeout=30
                )
                if result.returncode != 0:
                    print(f"[HOOK ERROR] Validation failed: {result.stderr}")
                    return False
            except subprocess.TimeoutExpired:
                print("[HOOK ERROR] Validation timed out")
                return False

        return True

    def create_backup(self) -> bool:
        """Create a timestamped backup of the file."""
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        file_path = Path(self.file_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"{file_path.name}.{timestamp}.bak"

        try:
            shutil.copy2(file_path, backup_path)
            print(f"[HOOK] Backup created: {backup_path}")

            # Clean up old backups
            self.cleanup_old_backups(file_path.name)

            return True
        except Exception as e:
            print(f"[HOOK ERROR] Backup failed: {e}")
            return False

    def cleanup_old_backups(self, filename: str):
        """Clean up backups older than configured age."""
        pattern = f"{filename}.*.bak"
        max_age_days = self.config.get("max_backup_age_days", 7)

        for backup in self.backup_dir.glob(pattern):
            age_days = (datetime.now() - datetime.fromtimestamp(
                backup.stat().st_mtime
            )).days

            if age_days > max_age_days:
                backup.unlink()
                print(f"[HOOK] Removed old backup: {backup}")

    def log_operation(self):
        """Log the operation for audit purposes."""
        log_dir = Path(".claude/logs")
        log_dir.mkdir(parents=True, exist_ok=True)

        log_file = log_dir / "pre-edit-hooks.log"
        entry = {
            "timestamp": datetime.now().isoformat(),
            "file_path": self.file_path,
            "operation": self.operation,
            "status": "allowed"
        }

        with open(log_file, "a") as f:
            f.write(json.dumps(entry) + "\\n")


if __name__ == "__main__":
    hook = PreEditHook()
    success = hook.run()
    sys.exit(0 if success else 1)
'''
    return script

print("\n=== Advanced Hook Script Example ===")
print(create_complex_hook_script()[:2000] + "\n... (truncated)")

# ============================================================================
# SECTION 4: PERFORMANCE TUNING
# ============================================================================

print("\n" + "=" * 70)
print("PERFORMANCE TUNING")
print("=" * 70)

performance_tuning_config = {
    "context_management": {
        "max_tokens": 100000,
        "compact_threshold": 0.8,
        "auto_compact": True,
        "description": "Control context window usage"
    },
    "request_optimization": {
        "batch_size": 10,
        "parallel_requests": 3,
        "cache_enabled": True,
        "cache_ttl_seconds": 3600,
        "description": "Optimize API request patterns"
    },
    "tool_execution": {
        "parallel_tools": True,
        "tool_timeout_seconds": 60,
        "retry_attempts": 3,
        "retry_backoff_ms": 1000,
        "description": "Optimize tool execution"
    },
    "model_selection": {
        "auto_select_by_task": True,
        "task_rules": {
            "simple_edit": "claude-haiku-4-5-20250601",
            "code_review": "claude-sonnet-4-5-20250601",
            "complex_reasoning": "claude-opus-4-5-20250601"
        },
        "description": "Automatically select optimal model"
    }
}

print("\n=== Performance Tuning Configuration ===")
for category, config in performance_tuning_config.items():
    print(f"\n{category.upper()}:")
    print(f"  Description: {config['description']}")
    if "task_rules" in config:
        print(f"  Task Rules:")
        for task, model in config["task_rules"].items():
            print(f"    {task}: {model}")
    else:
        for key, value in config.items():
            if key != "description":
                print(f"  {key}: {value}")

# ============================================================================
# SECTION 5: COST OPTIMIZATION STRATEGIES
# ============================================================================

print("\n" + "=" * 70)
print("COST OPTIMIZATION STRATEGIES")
print("=" * 70)

cost_optimization = """
=== COST OPTIMIZATION STRATEGIES ===

1. MODEL SELECTION BY TASK
   Use the most cost-effective model for each task type:

   | Task Type                  | Model                | Cost Ratio |
   |----------------------------|---------------------|------------|
   | Simple file edits          | claude-haiku-4-5-20250601   | 1x        |
   | Documentation updates      | claude-haiku-4-5-20250601   | 1x        |
   | Repetitive refactoring     | claude-haiku-4-5-20250601   | 1x        |
   | Code review                | claude-sonnet-4-5-20250601  | 4x        |
   | Feature implementation     | claude-sonnet-4-5-20250601  | 4x        |
   | Architecture decisions     | claude-opus-4-5-20250601    | 15x       |
   | Complex debugging          | claude-opus-4-5-20250601    | 15x       |

2. CONTEXT OPTIMIZATION
   - Compact conversation regularly
   - Remove unnecessary context
   - Use focused, specific prompts
   - Set appropriate max_tokens

3. BATCHING OPERATIONS
   - Group similar operations
   - Process multiple files in one request
   - Avoid per-file requests

4. CACHING COMMON OPERATIONS
   - Cache lint results
   - Cache type check results
   - Use local processing where possible

5. TIMEOUT SETTINGS
   - Short timeouts for simple tasks
   - Longer for complex reasoning
   - Prevent runaway operations

6. MONITORING AND ALERTING
   - Set usage budgets
   - Alert on unusual spending
   - Track cost per task type

7. AUTO-ROUTING
   Automatically route tasks to appropriate model:

   settings.json:
   {
     "costOptimization": {
       "enabled": true,
       "rules": [
         {
           "match": "Simple edit pattern",
           "model": "claude-haiku-4-5-20250601",
           "maxTokens": 500
         },
         {
           "match": "Code review pattern",
           "model": "claude-sonnet-4-5-20250601",
           "maxTokens": 2000
         },
         {
           "match": "Complex reasoning pattern",
           "model": "claude-opus-4-5-20250601",
           "maxTokens": 8000
         }
       ]
     }
   }
"""

print(cost_optimization)

# ============================================================================
# SECTION 6: MULTI-PROJECT MANAGEMENT
# ============================================================================

print("\n" + "=" * 70)
print("MULTI-PROJECT MANAGEMENT")
print("=" * 70)

multi_project_setup = """
=== MULTI-PROJECT CONFIGURATION ===

When working across multiple projects, organize configurations:

project-root/
|
|-- .claude/
|   |-- settings.json          # Project-specific settings
|   |-- settings.local.json   # Local overrides (not committed)
|   |-- hooks/
|   |   |-- project-a.sh
|   |   |-- project-b.sh
|   |-- aliases.json           # Project-specific aliases
|
|-- CLAUDE.md                  # Project documentation

=== GLOBAL CONFIGURATION ===

~/.claude/settings.json:
{
  "defaultModel": "claude-sonnet-4-5-20250601",
  "globalHooks": {
    "before_tool": ["scripts/global-pre-hook.sh"]
  },
  "aliases": {
    "review": "claude --model claude-sonnet-4-5-20250601 --print",
    "quick": "claude --model claude-haiku-4-5-20250601 --print"
  }
}

=== PROJECT-SPECIFIC MODELS ===

Project A (simple Python scripts):
CLAUDE.md:
  model: claude-haiku-4-5-20250601
  permissions: permissive

Project B (complex ML system):
CLAUDE.md:
  model: claude-opus-4-5-20250601
  permissions: strict

=== WORKSPACE MANAGEMENT ===

Use workspace configurations to manage multiple projects:

~/.claude/workspaces.json:
{
  "currentWorkspace": "project-a",
  "workspaces": {
    "project-a": {
      "path": "d:/projects/project-a",
      "model": "claude-haiku-4-5-20250601",
      "hooks": [".claude/hooks/project-a.sh"]
    },
    "project-b": {
      "path": "d:/projects/project-b",
      "model": "claude-opus-4-5-20250601",
      "hooks": [".claude/hooks/project-b.sh"]
    }
  }
}
"""

print(multi_project_setup)

# ============================================================================
# SECTION 7: TEAM-WIDE CONFIGURATIONS
# ============================================================================

print("\n" + "=" * 70)
print("TEAM-WIDE CONFIGURATIONS")
print("=" * 70)

team_config_example = '''
=== TEAM CONFIGURATION SHARING ===

1. SHARED CLAUDE.MD
   Place in repository root, cloned with project:

   CLAUDE.md:
   ---
   # Project conventions shared by all team members

   ## Code Style
   - 100 character line limit
   - Type hints required
   - Docstrings for public functions

   ## Testing Requirements
   - Minimum 80% coverage
   - Unit tests for all new functions
   - Integration tests for APIs

   ## Git Workflow
   - Branch: feature/<id>-description
   - Commit: type(scope): description
   - PR requires 2 approvals
   ---

2. TEAM SETTINGS REPOSITORY
   Centralized configuration repository:

   team-config/
   |
   |-- shared/
   |   |-- claude.md          # Master documentation
   |   |-- hooks/             # Shared hooks
   |   |-- mcp-servers/       # Team MCP configs
   |
   |-- departments/
   |   |-- engineering/
   |   |-- data-science/
   |   |-- DevOps/

3. ENFORCEMENT
   Use pre-commit hooks to enforce team standards:

   hooks:
     before_tool:
       - name: team-style-check
         run: team-config/scripts/style-check.sh
       - name: test-coverage
         run: team-config/scripts/coverage-check.sh
'''

print(team_config_example)

# ============================================================================
# SECTION 8: SECURITY HARDENING
# ============================================================================

print("\n" + "=" * 70)
print("SECURITY HARDENING")
print("=" * 70)

security_hardening_config = {
    "authentication": {
        "api_key_rotation_days": 90,
        "require_mfa": True,
        "session_timeout_minutes": 60,
        "audit_log_retention_days": 365
    },
    "permissions": {
        "default_policy": "deny",
        "allow_by_default": False,
        "require_explicit_permission": True,
        "directory_scopes": {
            "src": ["Read", "Write", "Edit"],
            "tests": ["Read", "Write"],
            "configs": ["Read"],
            ".env": ["Deny"]
        }
    },
    "network": {
        "allowed_api_endpoints": ["api.anthropic.com"],
        "ssl_verify": True,
        "proxy_required": False
    },
    "audit": {
        "log_all_requests": True,
        "log_all_file_access": True,
        "log_tool_executions": True,
        "mask_sensitive_data": True
    }
}

print("\n=== Security Hardening Configuration ===")
for category, config in security_hardening_config.items():
    print(f"\n{category.upper()}:")
    for key, value in config.items():
        print(f"  {key}: {value}")

security_hardening_guide = """
=== ENTERPRISE SECURITY BEST PRACTICES ===

1. API KEY MANAGEMENT
   - Rotate keys every 90 days
   - Use read-only keys for CI
   - Separate keys per environment
   - Store in secure credential manager

2. PERMISSION PRINCIPLES
   - Deny by default
   - Explicit allow only where needed
   - Minimum required scope
   - Directory-based restrictions

3. NETWORK SECURITY
   - Verify SSL certificates
   - Restrict to known endpoints
   - Use network policies
   - Implement egress filtering

4. AUDIT AND COMPLIANCE
   - Log all operations
   - Retain logs per policy
   - Regular access reviews
   - Incident response plan

5. HOOK SECURITY
   - Review all hook scripts
   - Validate all inputs
   - Set timeouts
   - No credentials in scripts

6. SECRETS MANAGEMENT
   - Never hardcode secrets
   - Use environment variables
   - Rotate regularly
   - Audit access
"""

print(security_hardening_guide)

# ============================================================================
# SECTION 9: MONITORING AND OBSERVABILITY
# ============================================================================

print("\n" + "=" * 70)
print("MONITORING AND OBSERVABILITY")
print("=" * 70)

observability_config = {
    "metrics": {
        "request_count": True,
        "token_usage": True,
        "request_duration_ms": True,
        "error_count": True,
        "cache_hit_rate": True
    },
    "logs": {
        "level": "info",
        "format": "json",
        "output": ["file", "stdout", "remote"],
        "rotation": {
            "max_size_mb": 100,
            "max_age_days": 30,
            "compress": True
        }
    },
    "alerts": {
        "high_error_rate": {
            "threshold": 0.05,
            "window_minutes": 15,
            "notify": ["slack", "email"]
        },
        "high_token_usage": {
            "threshold": 100000,
            "window_minutes": 60,
            "notify": ["slack"]
        },
        "unusual_activity": {
            "pattern": "unusual",
            "notify": ["security-team"]
        }
    }
}

print("\n=== Observability Configuration ===")
for category, config in observability_config.items():
    print(f"\n{category.upper()}:")
    if isinstance(config, dict):
        for key, value in config.items():
            print(f"  {key}: {value}")
    else:
        print(f"  {config}")

# ============================================================================
# SECTION 10: REAL-TIME SCENARIOS
# ============================================================================

print("\n" + "=" * 70)
print("REAL-TIME SCENARIOS")
print("=" * 70)

print("\n--- SCENARIO 1: Enterprise MCP Integration ---")
print("""
Situation: Need to integrate Claude Code with enterprise systems.
  - Jira for issue tracking
  - Confluence for documentation
  - Internal code repositories

Implementation:
1. Deploy MCP servers in secure network
2. Configure authentication with enterprise SSO
3. Set up permission scopes for each integration
4. Monitor all API calls for compliance
5. Regular security audits
""")

print("\n--- SCENARIO 2: Cost Control for Large Team ---")
print("""
Situation: Team of 50 developers, need to control costs.

Implementation:
1. Implement auto-routing to appropriate models
2. Set monthly budget alerts per team
3. Monitor usage by project and developer
4. Use Haiku for routine tasks (90% of requests)
5. Reserve Opus for complex architecture decisions
6. Quarterly cost review meetings

Results: 60% cost reduction with same productivity
""")

print("\n--- SCENARIO 3: Critical ")
print("""
Situation: Claude Code is used for production infrastructure.
  - Cannot allow direct production edits
  - Require multiple approvals
  - Full audit trail
  - Rollback capability

Implementation:
1. Strict permission model (read-only for production)
2. Multi-gate workflow for any change
3. All operations logged with timestamps
4. Pre-change backups mandatory
5. Automated rollback on failure
6. Daily audit report to security team
""")

# ============================================================================
# SECTION 11: INTERVIEW Q&A
# ============================================================================

print("\n" + "=" * 70)
print("INTERVIEW QUESTIONS AND ANSWERS")
print("=" * 70)

qa_pairs = [
    (
        "Q: How do you create a custom tool for Claude Code?",
        """
A: Custom tools extend Claude Code with project-specific functionality:

   1. DEFINE TOOL SPECIFICATION
      - Name and description
      - Input/output schemas
      - Security constraints
      - Permission requirements

   2. IMPLEMENT THE TOOL
      - Create handler class or function
      - Validate inputs
      - Execute logic
      - Return structured output

   3. REGISTER THE TOOL
      - Add to settings.json
      - Configure permissions
      - Test in isolation

   4. DOCUMENT USAGE
      - Add to CLAUDE.md
      - Provide examples
      - Document constraints

   Best Practices:
   - Always validate inputs
   - Implement timeouts
   - Handle errors gracefully
   - Log operations
   - Provide meaningful error messages
        """
    ),
    (
        "Q: How do you configure MCP servers?",
        """
A: MCP (Model Context Protocol) servers add external capabilities:

   1. INSTALL SERVER
      Some servers available via npm:
      npx -y @modelcontextprotocol/server-filesystem

   2. CONFIGURE IN SETTINGS.JSON
      {
        "mcpServers": {
          "filesystem": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path"],
            "enabled": true
          }
        }
      }

   3. SECURE THE CONNECTION
      - Limit directory access
      - Use environment variables for credentials
      - Set appropriate timeouts

   4. TEST AND MONITOR
      - Verify functionality
      - Monitor API usage
      - Log all operations
        """
    ),
    (
        "Q: How do you optimize costs in a large team?",
        """
A: Cost optimization requires multiple strategies:

   1. MODEL SELECTION RULES
      - Auto-route simple tasks to Haiku
      - Reserve Sonnet/Opus for complex work
      - Set default to most cost-effective

   2. BUDGET CONTROLS
      - Set per-team spending limits
      - Alert before hitting limits
      - Regular usage reviews

   3. USAGE MONITORING
      - Track by project/developer
      - Identify optimization opportunities
      - Share best practices

   4. TECHNICAL OPTIMIZATIONS
      - Batch operations
      - Compact context frequently
      - Cache common operations

   5. PATTERN ANALYSIS
      - Identify high-cost workflows
      - Recommend alternatives
      - Automate optimizations
        """
    ),
    (
        "Q: How do you implement security hardening?",
        """
A: Security hardening involves multiple layers:

   1. AUTHENTICATION
      - Rotate API keys regularly
      - Require MFA for admin access
      - Session timeouts
      - Audit trail

   2. PERMISSIONS
      - Deny by default
      - Explicit allow only where needed
      - Directory-based restrictions
      - Principle of least privilege

   3. NETWORK SECURITY
      - SSL verification
      - Endpoint allowlisting
      - Proxy configuration
      - Network policies

   4. HOOK SECURITY
      - Review all hooks
      - Validate inputs
      - Set timeouts
      - No credentials in scripts

   5. MONITORING
      - Log all operations
      - Alert on anomalies
      - Regular audits
      - Incident response plan
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
1. CUSTOM TOOL DEVELOPMENT
   - Define tool specification
   - Implement handler
   - Register and configure
   - Document usage

2. MCP SERVER CONFIGURATION
   - Install servers via npm/docker
   - Configure in settings.json
   - Secure connections
   - Monitor usage

3. ADVANCED HOOK SCRIPTING
   - Conditional hooks
   - Chained hooks
   - Async hooks
   - Artifact production

4. PERFORMANCE TUNING
   - Context management
   - Request optimization
   - Tool execution tuning
   - Auto model selection

5. COST OPTIMIZATION
   - Model selection by task
   - Context optimization
   - Batching operations
   - Usage monitoring

6. MULTI-PROJECT MANAGEMENT
   - Workspace configurations
   - Project-specific settings
   - Shared configurations

7. TEAM-WIDE CONFIGURATIONS
   - Shared CLAUDE.md
   - Team settings repository
   - Enforcement hooks

8. SECURITY HARDENING
   - API key rotation
   - Permission model
   - Network security
   - Audit logging

9. MONITORING AND OBSERVABILITY
   - Metrics collection
   - Log management
   - Alert configuration
"""

print(lessons)

# ============================================================================
# SYNTAX VERIFICATION
# ============================================================================

print("\n=== File Syntax Verification ===")
print("This file has been created successfully.")
print("Run: python -m py_compile <file_path> to verify syntax.")
print("=" * 70)
