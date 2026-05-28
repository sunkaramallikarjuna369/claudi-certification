# ============================================================================
# PRACTICE FILE: Workflow Automation Patterns
# Domain 3.3: Workflow Automation Patterns
# ============================================================================
#
# PURPOSE: Learn how to automate repetitive tasks, create script-based
# workflows, and implement multi-step task automation with Claude Code.
#
# ============================================================================
# SECTION 1: AUTOMATING REPETITIVE TASKS
# ============================================================================
#
# Repetitive tasks are prime candidates for automation. Common examples:
# - Code formatting and linting
# - Running test suites
# - Building documentation
# - Deploying to staging environments
# - Generating boilerplate code
#
# ============================================================================

print("=" * 70)
print("WORKFLOW AUTOMATION FUNDAMENTALS")
print("=" * 70)

# --------------------------------------------------------------------------
# CONCEPT: Workflow Design Principles
# --------------------------------------------------------------------------

workflow_principles = """
1. IDEMPOTENCY
   - Same input = Same output (no matter how many times run)
   - Safe to retry without side effects
   - Example: Running formatter on already-formatted code

2. SINGLE RESPONSIBILITY
   - Each automation step should do one thing well
   - Easier to debug and maintain
   - Example: Separate steps for lint, test, build

3. ERROR HANDLING
   - Detect failures early and clearly
   - Provide meaningful error messages
   - Implement rollback where possible

4. LOGGING AND REPORTING
   - Log all operations with timestamps
   - Report progress at key milestones
   - Include success/failure metrics

5. COMPOSABILITY
   - Small steps can be combined into complex workflows
   - Reuse common patterns across projects
   - Build libraries of automation components

6. CONFIGURABILITY
   - Externalize constants and paths
   - Environment-specific configurations
   - Make behavior adjustable without code changes
"""

print(workflow_principles)

# ============================================================================
# SECTION 2: TASK DEFINITION AND STRUCTURE
# ============================================================================
#
# A well-defined task structure makes automation reliable and maintainable.

# Example task definition
task_structure = {
    "name": "full-stack-feature",
    "description": "Complete feature development workflow",
    "steps": [
        {
            "id": 1,
            "name": "validate-prerequisites",
            "tool": "Bash",
            "command": "scripts/check-prerequisites.sh",
            "continue_on_failure": False,
            "retry_count": 1,
            "timeout_ms": 30000
        },
        {
            "id": 2,
            "name": "create-branch",
            "tool": "Bash",
            "command": "git checkout -b feature/${TICKET_ID}",
            "continue_on_failure": False,
            "retry_count": 0,
            "timeout_ms": 5000
        },
        {
            "id": 3,
            "name": "implement-feature",
            "tool": "Edit",
            "description": "Implement feature code based on requirements",
            "continue_on_failure": False,
            "retry_count": 1,
            "timeout_ms": 300000
        },
        {
            "id": 4,
            "name": "run-tests",
            "tool": "Bash",
            "command": "npm test",
            "continue_on_failure": False,
            "retry_count": 2,
            "timeout_ms": 120000
        },
        {
            "id": 5,
            "name": "commit-changes",
            "tool": "Bash",
            "command": "git add . && git commit -m '${COMMIT_MESSAGE}'",
            "continue_on_failure": True,
            "retry_count": 0,
            "timeout_ms": 10000
        }
    ],
    "error_recovery": {
        "rollback_branch": True,
        "notify_on_failure": True,
        "preserve_logs": True
    }
}

print("\n=== Task Definition Example ===")
print(f"Task: {task_structure['name']}")
print(f"Description: {task_structure['description']}")
print(f"\nSteps ({len(task_structure['steps'])} total):")

for step in task_structure['steps']:
    print(f"\n  Step {step['id']}: {step['name']}")
    if 'tool' in step:
        print(f"    Tool: {step['tool']}")
        if 'command' in step:
            print(f"    Command: {step['command']}")
    print(f"    Continue on failure: {step['continue_on_failure']}")
    print(f"    Retry count: {step['retry_count']}")

# ============================================================================
# SECTION 3: SCRIPT-BASED WORKFLOWS
# ============================================================================
#
# Bash and Python scripts are the foundation of workflow automation.
# Here are patterns for creating effective automation scripts.

# --------------------------------------------------------------------------
# PATTERN 1: Configuration-Driven Script
# --------------------------------------------------------------------------
print("\n" + "=" * 70)
print("PATTERN 1: Configuration-Driven Script")
print("=" * 70)

def generate_config_driven_script():
    """
    This pattern externalizes configuration to make scripts reusable.
    """
    script_template = '''#!/bin/bash
# config-driven-workflow.sh

# Load configuration from file or environment
CONFIG_FILE="${CONFIG_FILE:-config/default.yaml}"
ENVIRONMENT="${ENVIRONMENT:-development}"

# Load environment-specific settings
source "config/environments/${ENVIRONMENT}.sh"

echo "[WORKFLOW] Starting ${WORKFLOW_NAME} in ${ENVIRONMENT} mode"
echo "[WORKFLOW] Config file: ${CONFIG_FILE}"

# Step 1: Validate prerequisites
echo "[STEP 1/4] Validating prerequisites..."
if ! ./scripts/check-prerequisites.sh; then
    echo "[ERROR] Prerequisites check failed"
    exit 1
fi

# Step 2: Setup environment
echo "[STEP 2/4] Setting up environment..."
./scripts/setup-${ENVIRONMENT}.sh
if [ $? -ne 0 ]; then
    echo "[ERROR] Environment setup failed"
    exit 1
fi

# Step 3: Run main task
echo "[STEP 3/4] Running main task..."
case "${TASK}" in
    "lint") ./scripts/run-lint.sh ;;
    "test") ./scripts/run-tests.sh ;;
    "build") ./scripts/build.sh ;;
    "deploy") ./scripts/deploy.sh ;;
    *) echo "[ERROR] Unknown task: ${TASK}" ;;
esac

# Step 4: Cleanup and report
echo "[STEP 4/4] Finalizing..."
./scripts/cleanup.sh

echo "[WORKFLOW] Complete!"
'''

    return script_template

print(generate_config_driven_script())

# --------------------------------------------------------------------------
# PATTERN 2: Progress Tracking Workflow
# --------------------------------------------------------------------------
print("\n" + "=" * 70)
print("PATTERN 2: Progress Tracking Workflow")
print("=" * 70)

def generate_progress_tracking_script():
    """
    This pattern tracks workflow state for resumable operations.
    """
    script_template = '''#!/bin/bash
# progress-tracking-workflow.sh

WORKFLOW_ID="${WORKFLOW_ID:-$(date +%s)}"
STATE_FILE=".workflow-state/${WORKFLOW_ID}.json"
TOTAL_STEPS=5

# Initialize state file
init_state() {
    mkdir -p ".workflow-state"
    echo "{
        \\"workflow_id\\": \\"${WORKFLOW_ID}\\"",
        \\"status\\": \\"running\\"",
        \\"current_step\\": 1,
        \\"total_steps\\": ${TOTAL_STEPS},
        \\"started_at\\": \\"$(date -Iseconds)\\"",
        \\"completed_steps\\": []
    }" > "${STATE_FILE}"
}

# Update progress
update_progress() {
    local step=$1
    local status=$2
    local message=$3

    echo "[$(date +%H:%M:%S)] Step ${step}/${TOTAL_STEPS}: ${status}"

    # Update JSON state (simplified)
    # In production, use jq for proper JSON manipulation
    echo "[PROGRESS] ${step}/${TOTAL_STEPS} - ${message}" >> "${STATE_FILE}.log"
}

# Mark step complete
complete_step() {
    local step=$1
    echo "[COMPLETE] Step ${step} finished successfully"
}

# Main execution
main() {
    init_state

    for step in 1 2 3 4 5; do
        update_progress ${step} "running" "Executing step ${step}"

        case ${step} in
            1) ./scripts/step-1.sh ;;
            2) ./scripts/step-2.sh ;;
            3) ./scripts/step-3.sh ;;
            4) ./scripts/step-4.sh ;;
            5) ./scripts/step-5.sh ;;
        esac

        if [ $? -eq 0 ]; then
            complete_step ${step}
        else
            echo "[ERROR] Step ${step} failed"
            echo "{\\"status\\": \\"failed\\", \\"failed_step\\": ${step}}" > "${STATE_FILE}"
            exit 1
        fi
    done

    echo "{\\"status\\": \\"complete\\", \\"completed_at\\": \\"$(date -Iseconds)\\"}" > "${STATE_FILE}"
    echo "[SUCCESS] Workflow ${WORKFLOW_ID} complete!"
}

main "$@"
'''

    return script_template

print(generate_progress_tracking_script())

# ============================================================================
# SECTION 4: MULTI-STEP TASK AUTOMATION
# ============================================================================

print("\n" + "=" * 70)
print("MULTI-STEP TASK AUTOMATION")
print("=" * 70)

# --------------------------------------------------------------------------
# EXAMPLE: Complete Feature Development Workflow
# --------------------------------------------------------------------------

feature_workflow_steps = """
WORKFLOW: Automated Feature Development

This workflow demonstrates a complete feature development process
from branch creation to pull request.

STEP 1: PREREQUISITE CHECK
------------------------
Actions:
  - Verify Git is available
  - Check for uncommitted changes
  - Validate branch name format
  - Ensure clean working directory

Commands:
  $ git status
  $ ./scripts/validate-branch-name.sh ${FEATURE_NAME}

STEP 2: BRANCH CREATION
----------------------
Actions:
  - Create feature branch
  - Set up branch protection (optional)
  - Track branch in task management

Commands:
  $ git checkout -b feature/${TICKET_ID}-${FEATURE_NAME}

STEP 3: IMPLEMENTATION
---------------------
Actions:
  - Create/update feature files
  - Run linters and formatters
  - Implement tests
  - Update documentation

Commands:
  $ claude "Implement the ${FEATURE_NAME} feature"
  $ npm run lint && npm test

STEP 4: CODE REVIEW PREP
---------------------
Actions:
  - Self-review changes
  - Run security scans
  - Check test coverage
  - Generate changelog

Commands:
  $ git diff --stat
  $ npm run security-scan
  $ npm run coverage

STEP 5: COMMIT AND PUSH
----------------------
Actions:
  - Commit with conventional format
  - Push to remote
  - Create/update pull request

Commands:
  $ git add -A
  $ git commit -m "feat(${COMPONENT}): ${FEATURE_NAME} - ${DESCRIPTION}"
  $ git push -u origin feature/${TICKET_ID}-${FEATURE_NAME}
  $ gh pr create --fill

STEP 6: NOTIFICATION
------------------
Actions:
  - Notify team of PR
  - Request reviews
  - Update task status

Commands:
  $ ./scripts/notify-reviewers.sh
  $ ./scripts/update-task-status.sh ${TICKET_ID} "In Review"
"""

print(feature_workflow_steps)

# ============================================================================
# SECTION 5: ERROR RECOVERY IN AUTOMATED WORKFLOWS
# ============================================================================

print("=" * 70)
print("ERROR RECOVERY STRATEGIES")
print("=" * 70)

# Error recovery strategies
recovery_strategies = {
    "retry": {
        "description": "Retry failed operations with exponential backoff",
        "use_case": "Network timeouts, transient failures",
        "implementation": """
# Retry with exponential backoff
max_retries=3
retry_delay=1000
for attempt in $(seq 1 $max_retries); do
    if ./operation.sh; then
        echo "Success on attempt $attempt"
        exit 0
    fi
    echo "Attempt $attempt failed, retrying in ${retry_delay}ms..."
    sleep $((retry_delay / 1000))
    retry_delay=$((retry_delay * 2))
done
echo "All retries exhausted"
exit 1
"""
    },
    "rollback": {
        "description": "Rollback changes on failure",
        "use_case": "Deployments, database operations",
        "implementation": """
# Rollback on failure
cleanup() {
    echo "Rolling back changes..."
    git checkout -- .
    echo "Rollback complete"
}

trap cleanup EXIT
./deploy.sh
"""
    },
    "skip_and_continue": {
        "description": "Skip optional steps on failure",
        "use_case": "Non-critical cleanup tasks",
        "implementation": """
# Non-critical step - continue even on failure
if ./optional-task.sh; then
    echo "Optional task completed"
else
    echo "Optional task failed (continuing anyway)"
fi
./critical-task.sh
"""
    },
    "fail_fast": {
        "description": "Fail immediately on errors",
        "use_case": "Critical validation, security checks",
        "implementation": """
# Critical validation - fail immediately
if ./critical-validation.sh; then
    echo "Validation passed"
else
    echo "CRITICAL: Validation failed - aborting"
    exit 1
fi
"""
    }
}

print("\n=== Error Recovery Strategies ===")

for strategy, details in recovery_strategies.items():
    print(f"\n{strategy.upper()}:")
    print(f"  Description: {details['description']}")
    print(f"  Use Case: {details['use_case']}")
    print(f"  Implementation:")
    for line in details['implementation'].strip().split('\n'):
        print(f"    {line}")

# ============================================================================
# SECTION 6: WORKFLOW STATE MANAGEMENT
# ============================================================================

print("\n" + "=" * 70)
print("WORKFLOW STATE MANAGEMENT")
print("=" * 70)

# State management patterns
def create_state_manager():
    """
    Demonstrates workflow state persistence for resumable operations.
    """
    state_manager_code = '''#!/usr/bin/env python3
"""State manager for resumable workflows."""

import json
import os
from datetime import datetime
from pathlib import Path

class WorkflowState:
    """Manages workflow execution state for resumability."""

    def __init__(self, workflow_id: str, state_dir: str = ".workflow-state"):
        self.workflow_id = workflow_id
        self.state_file = Path(state_dir) / f"{workflow_id}.json"
        self.state_dir = Path(state_dir)
        self.state = self._load_or_init()

    def _load_or_init(self) -> dict:
        """Load existing state or create new state."""
        if self.state_file.exists():
            with open(self.state_file) as f:
                return json.load(f)

        return {
            "workflow_id": self.workflow_id,
            "version": 1,
            "status": "initialized",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "steps": [],
            "completed_steps": [],
            "failed_steps": [],
            "metadata": {}
        }

    def save(self):
        """Persist state to disk."""
        self.state["updated_at"] = datetime.now().isoformat()
        self.state_dir.mkdir(parents=True, exist_ok=True)

        # Write atomically
        temp_file = self.state_file.with_suffix('.tmp')
        with open(temp_file, 'w') as f:
            json.dump(self.state, f, indent=2)
        temp_file.rename(self.state_file)

    def mark_step_start(self, step_id: str, step_name: str):
        """Mark a step as started."""
        self.state["status"] = "running"
        self.state["steps"].append({
            "id": step_id,
            "name": step_name,
            "started_at": datetime.now().isoformat()
        })
        self.save()

    def mark_step_complete(self, step_id: str, result: dict = None):
        """Mark a step as completed."""
        self.state["completed_steps"].append(step_id)
        if result:
            self.state["metadata"][step_id] = result
        self.save()

    def mark_step_failed(self, step_id: str, error: str):
        """Mark a step as failed."""
        self.state["failed_steps"].append(step_id)
        self.state["status"] = "failed"
        self.state["metadata"][f"{step_id}_error"] = error
        self.save()

    def is_step_completed(self, step_id: str) -> bool:
        """Check if a step has already been completed."""
        return step_id in self.state["completed_steps"]

    def get_next_step(self) -> str:
        """Get the next uncompleted step."""
        for step in self.state["steps"]:
            if step["id"] not in self.state["completed_steps"]:
                return step["id"]
        return None

# Usage example:
def run_workflow():
    state = WorkflowState("feature-123")

    steps = ["validate", "implement", "test", "deploy"]

    for step_id in steps:
        if state.is_step_completed(step_id):
            print(f"Skipping completed step: {step_id}")
            continue

        state.mark_step_start(step_id, step_id)

        # Simulate step execution
        if step_id == "deploy":
            raise Exception("Deploy failed!")

        state.mark_step_complete(step_id, {"output": "success"})

    print(f"Workflow complete! Status: {state.state['status']}")
    state.save()
'''
    return state_manager_code

print(create_state_manager())

# ============================================================================
# SECTION 7: BRANCH-SPECIFIC WORKFLOWS
# ============================================================================

print("\n" + "=" * 70)
print("BRANCH-SPECIFIC WORKFLOWS")
print("=" * 70)

# Branch-specific workflow configuration
branch_workflows = {
    "feature/": {
        "description": "Feature development branch",
        "hooks": ["validate-code", "run-tests", "update-task"],
        "model": "claude-sonnet-4-5-20250601",
        "permissions": "development"
    },
    "bugfix/": {
        "description": "Bug fix branch",
        "hooks": ["validate-code", "run-tests", "notify-on-fix"],
        "model": "claude-haiku-4-5-20250601",
        "permissions": "development"
    },
    "release/": {
        "description": "Release branch",
        "hooks": ["security-scan", "full-test-suite", "changelog"],
        "model": "claude-opus-4-5-20250601",
        "permissions": "staging"
    },
    "hotfix/": {
        "description": "Emergency production fix",
        "hooks": ["minimal-changes", "quick-test", "notify-slack"],
        "model": "claude-haiku-4-5-20250601",
        "permissions": "production"
    }
}

print("\n=== Branch-Specific Configurations ===")
for branch_pattern, config in branch_workflows.items():
    print(f"\nPattern: {branch_pattern}*")
    print(f"  Description: {config['description']}")
    print(f"  Model: {config['model']}")
    print(f"  Hooks: {', '.join(config['hooks'])}")
    print(f"  Permissions: {config['permissions']}")

# ============================================================================
# SECTION 8: CUSTOM COMMAND DEFINITIONS
# ============================================================================

print("\n" + "=" * 70)
print("CUSTOM COMMAND DEFINITIONS")
print("=" * 70)

custom_commands = '''
Custom commands extend Claude Code with project-specific operations.
These are defined in CLAUDE.md and allow complex operations to be
invoked with simple commands.

=== CLAUDE.md Custom Commands ===

You can define custom commands in CLAUDE.md:

/compact          # Compact the conversation context
/summarize         # Summarize recent changes
/review-pr <num>  # Review pull request by number

--- custom-commands:
  lint-and-fix:
    description: Run linter and auto-fix issues
    command: npm run lint:fix
    confirm: false

  test-coverage:
    description: Run tests with coverage report
    command: npm run test:coverage
    confirm: false

  deploy-staging:
    description: Deploy current branch to staging
    command: scripts/deploy-staging.sh
    confirm: true

  full-release:
    description: Complete release workflow
    command: |
      echo "Starting release workflow..."
      scripts/run-tests.sh
      scripts/build.sh
      scripts/deploy-prod.sh
      scripts/notify-release.sh
    confirm: true
    multi-step: true

--- dependencies:
  - hooks: [lint-and-fix]
  - hooks: [test-coverage]
  - scripts: [deploy-staging]
'''

print(custom_commands)

# ============================================================================
# SECTION 9: REAL-TIME SCENARIOS
# ============================================================================

print("\n" + "=" * 70)
print("REAL-TIME SCENARIOS")
print("=" * 70)

print("\n--- SCENARIO 1: Automated Code Review Pipeline ---")
print("""
Situation: Your team wants automated code review for every PR.

Workflow Implementation:
1. CI triggers on PR creation/update
2. Checkout PR branch
3. Run lint, type check, tests
4. Claude Code performs code review
5. Post review comments to PR
6. Update CI status based on findings

Tools: GitHub Actions, Claude Code, PR comment API
""")

print("\n--- SCENARIO 2: Continuous Deployment ---")
print("""
Situation: Automate deployment from merge to production.

Workflow Implementation:
1. PR merged to main
2. CI runs tests and builds
3. Claude Code runs additional checks
4. Deploy to staging environment
5. Run integration tests
6. Deploy to production
7. Send deployment notifications

Tools: GitHub Actions, AWS/GCP deployments, Slack webhooks
""")

print("\n--- SCENARIO 3: Bulk Refactoring ---")
print("""
Situation: Need to update 100+ files with consistent changes.

Workflow Implementation:
1. Create a list of files to update
2. Group files by type or location
3. Process in batches (10 files at a time)
4. Verify each batch compiles/passes tests
5. Commit changes progressively
6. Final verification run

Tools: Claude Code, parallel execution, progress tracking
""")

# ============================================================================
# SECTION 10: INTERVIEW Q&A
# ============================================================================

print("\n" + "=" * 70)
print("INTERVIEW QUESTIONS AND ANSWERS")
print("=" * 70)

qa_pairs = [
    (
        "Q: How do you handle errors in automated workflows?",
        """
A: Error handling is critical for robust workflows. Key strategies:

   1. DEFENSIVE CHECKING: Validate inputs and preconditions before
      executing each step.

   2. GRADUATED RESPONSES:
      - Fail fast for critical errors (immediate abort)
      - Retry with backoff for transient errors
      - Skip optional steps with warnings
      - Rollback on unrecoverable errors

   3. LOGGING AND RECOVERY: Log all errors with context for debugging.
      Implement state management for resumable workflows.

   4. NOTIFICATION: Alert appropriate team members on failures.

   5. TESTING: Test the error paths, not just success paths.
        """
    ),
    (
        "Q: Explain idempotency in workflow automation.",
        """
A: Idempotency means an operation produces the same result regardless of
   how many times it's executed.

   Example: Running a formatter on already-formatted code should produce
   the exact same output as running it on unformatted code.

   Why it matters:
   - Safe to retry on failures
   - Workflows can be restarted without side effects
   - Easier to reason about automation behavior

   How to achieve:
   - Check for existing state before creating
   - Use UPSERT patterns (update or insert)
   - Make operations additive rather than destructive
        """
    ),
    (
        "Q: How do you manage long-running workflows?",
        """
A: For long-running workflows:

   1. STATE PERSISTENCE: Save workflow state to disk after each step.
      This allows resumption after crashes.

   2. PROGRESS TRACKING: Report progress at each step milestone.
      Include completed and remaining steps.

   3. TIMEOUT MANAGEMENT: Set appropriate timeouts for each step.
      Implement polling for operations that complete asynchronously.

   4. CHECKPOINTING: Save intermediate results at key points.
      Enable rollback to last checkpoint on failure.

   5. NOTIFICATIONS: Send progress updates for long operations.
      Alert on completion or failure.
        """
    ),
    (
        "Q: What patterns make automation scripts reusable?",
        """
A: To make scripts reusable:

   1. CONFIGURATION EXTERNALIZATION: Use config files/env vars instead
      of hardcoded values.

   2. MODULAR DESIGN: Break into small, single-purpose functions.

   3. ERROR HANDLING: Every function handles errors consistently.

   4. LOGGING AND DEBUGGING: Include debug output and logging.

   5. DOCUMENTATION: Document inputs, outputs, and side effects.

   6. TESTABILITY: Structure code to be easily testable.

   7. DEPENDENCY MANAGEMENT: Check prerequisites before executing.
        """
    )
]

for question, answer in qa_pairs:
    print(f"\n{question}")
    print(answer)

# ============================================================================
# WHAT WE HAVE LEARNT
# ============================================================================

print("\n" + * 70)
print("WHAT WE HAVE LEARNT")
print("=" * 70)

lessons = """
1. WORKFLOW PRINCIPLES
   - Idempotency: Safe to retry
   - Single responsibility: One step, one purpose
   - Error handling: Fail fast, retry, rollback
   - Logging and reporting: Track all operations

2. TASK DEFINITION
   - Structured tasks with clear steps
   - Configurable per step: timeout, retry, continue_on_failure
   - State management for resumable workflows

3. SCRIPT PATTERNS
   - Configuration-driven scripts
   - Progress tracking
   - Error recovery strategies

4. ERROR RECOVERY
   - Retry with exponential backoff
   - Rollback on failure
   - Skip optional steps
   - Fail fast for critical errors

5. STATE MANAGEMENT
   - Persist state to disk
   - Resume from checkpoints
   - Track completed/failed steps

6. BRANCH-SPECIFIC WORKFLOWS
   - Different configs for feature/release/hotfix
   - Environment-appropriate settings

7. CUSTOM COMMANDS
   - Define complex operations in CLAUDE.md
   - Enable single-command execution

8. PROGRESS TRACKING
   - Log milestones
   - Report completion percentage
   - Enable resumption after failures
"""

print(lessons)

# ============================================================================
# SYNTAX VERIFICATION
# ============================================================================

print("\n=== File Syntax Verification ===")
print("This file has been created successfully.")
print("Run: python -m py_compile <file_path> to verify syntax.")
print("=" * 70)
