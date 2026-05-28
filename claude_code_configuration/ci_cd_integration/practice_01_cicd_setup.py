# ============================================================================
# PRACTICE FILE: CI/CD Integration
# Domain 3.4: CI/CD Integration
# ============================================================================
#
# PURPOSE: Learn how to integrate Claude Code into continuous integration
# and continuous deployment pipelines for automated development workflows.
#
# ============================================================================
# SECTION 1: CI/CD INTEGRATION FUNDAMENTALS
# ============================================================================
#
# Claude Code can be integrated into CI/CD pipelines to:
# - Automate code review
# - Generate documentation
# - Run development tasks in CI environment
# - Perform automated testing and validation
#
# KEY CONCEPTS:
# - Non-interactive mode (--print flag)
# - Exit codes for success/failure detection
# - Environment variable configuration
# - Secure credential management
#
# ============================================================================

import os

# Configuration for CI environment
ci_config = {
    "api_key": os.environ.get("ANTHROPIC_API_KEY"),
    "model": "claude-haiku-4-5-20250601",  # Cost-effective for CI tasks
    "non_interactive": True,
    "timeout_ms": 300000,  # 5 minutes for CI tasks
    "output_format": "json"  # Structured output for parsing
}

print("=" * 70)
print("CI/CD INTEGRATION FUNDAMENTALS")
print("=" * 70)

fundamentals = """
1. NON-INTERACTIVE MODE
   Claude Code in CI must run without user interaction:
   - Use --print flag for batch processing
   - Disable streaming with --no-stream
   - Set all configuration via environment variables

2. EXIT CODES
   Standard Unix exit codes for pipeline integration:
   - 0: Success - task completed successfully
   - 1: General error - task failed
   - 2: Usage error - invalid arguments
   - 127: Command not found - setup issues

3. OUTPUT FORMATS
   Machine-readable output for pipeline parsing:
   - JSON: Structured data for downstream tools
   - Text: Simple output for logs
   - Markdown: Documentation or reports

4. ENVIRONMENT VARIABLES
   All configuration should come from env vars:
   - ANTHROPIC_API_KEY: Authentication
   - CLAUDE_MODEL: Model selection
   - CLAUDE_TIMEOUT: Operation timeout
   - CI: Detection of CI environment
"""

print(fundamentals)

# ============================================================================
# SECTION 2: NON-INTERACTIVE MODE CONFIGURATION
# ============================================================================

print("\n" + "=" * 70)
print("NON-INTERACTIVE MODE")
print("=" * 70)

print("""
Non-interactive mode is critical for CI/CD integration where there's
no user to respond to prompts.

=== COMMAND LINE FLAGS ===

--print              # Batch mode, no TTY required
--no-stream         # Disable streaming output
--output-format json # Machine-readable output
--verbose           # Include debug information

=== ENVIRONMENT VARIABLES ===

ANTHROPIC_API_KEY   # Required for authentication
CLAUDE_MODEL        # Model to use (default: haiku)
CLAUDE_TIMEOUT      # Timeout in milliseconds
CI                  # Set to 'true' in CI environment

=== EXAMPLE INVOCATION ===

export ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}"
export CLAUDE_MODEL="claude-haiku-4-5-20250601"

claude --print --no-stream --model claude-haiku-4-5-20250601 \\
    "Review the code changes in this commit and report issues"

echo "Exit code: $?"  # Check for errors
""")

# ============================================================================
# SECTION 3: GITHUB ACTIONS INTEGRATION
# ============================================================================

print("\n" + "=" * 70)
print("GITHUB ACTIONS INTEGRATION")
print("=" * 70)

# GitHub Actions workflow example
github_actions_workflow = '''name: Claude Code Integration

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main, develop]
  workflow_dispatch:

jobs:
  code-review:
    runs-on: ubuntu-latest
    name: Claude Code Review
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for diff

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install Claude Code
        run: npm install -g @anthropic-ai/claude-code

      - name: Run Claude Code Review
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          claude --print --no-stream \\
            --model claude-sonnet-4-5-20250601 \\
            "Review the changes in this PR. Check for:
             1. Code quality issues
             2. Security vulnerabilities
             3. Performance concerns
             4. Test coverage

             Format output as JSON with 'issues' array."

      - name: Post Review Comments
        if: always()
        run: |
          # Parse Claude output and post to PR
          ./scripts/post-review-comments.sh

  automated-task:
    runs-on: ubuntu-latest
    name: Claude Automated Task
    if: github.event_name == 'workflow_dispatch'
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Run Task
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          claude --print \\
            "Review all .py files in src/ and update docstrings
             where they are missing or incomplete."

  dependency-check:
    runs-on: ubuntu-latest
    name: Dependency Security Scan
    steps:
      - uses: actions/checkout@v4

      - name: Security Scan
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          claude --print --model claude-haiku-4-5-20250601 \\
            "Analyze package.json for security issues.
             Check for:
             - Known vulnerabilities
             - Outdated packages
             - Unmaintained dependencies

             Report findings in markdown format."
'''

print(github_actions_workflow)

# ============================================================================
# SECTION 4: GITLAB CI INTEGRATION
# ============================================================================

print("\n" + "=" * 70)
print("GITLAB CI INTEGRATION")
print("=" * 70)

gitlab_ci_config = '''variables:
  CLAUDE_MODEL: claude-haiku-4-5-20250601
  ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}

stages:
  - review
  - test
  - deploy

claude-code-review:
  stage: review
  image: node:20
  before_script:
    - npm install -g @anthropic-ai/claude-code
  script:
    - claude --print --no-stream --model ${CLAUDE_MODEL} "Review the code changes in this merge request. Focus on: 1) code quality, 2) potential bugs, 3) performance issues. Output findings as JSON."
  artifacts:
    reports:
      markdown: claude-review-report.md
    expire_in: 7 days
  only:
    - merge_requests
  coverage: '/Total coverage: (d+.d+)%/'

claude-doc-generation:
  stage: review
  image: node:20
  before_script:
    - npm install -g @anthropic-ai/claude-code
  script:
    - claude --print --model ${CLAUDE_MODEL} "Generate API documentation for the src/ directory based on JSDoc comments and code patterns."
  artifacts:
    paths:
      - docs/api/
    expire_in: 30 days
  only:
    - main

automated-testing:
  stage: test
  image: node:20
  before_script:
    - npm install
    - npm install -g @anthropic-ai/claude-code
  script:
    - npm test
    - claude --print --model ${CLAUDE_MODEL} "Review test files in tests/ directory. Verify test coverage meets requirements (minimum 80%). Report any gaps."
  coverage: '/Coverage: (d+.d+)%/'
  only:
    - main
    - develop

staging-deploy:
  stage: deploy
  image: node:20
  before_script:
    - npm install -g @anthropic-ai/claude-code
    - pip install awscli  # For AWS deployment
  script:
    - claude --print --model ${CLAUDE_MODEL} "Review deployment configuration. Verify: 1) Environment variables are correct, 2) All secrets are externalized, 3) Health checks are configured."
    - ./scripts/deploy-staging.sh
  environment:
    name: staging
  only:
    - develop

production-deploy:
  stage: deploy
  image: node:20
  before_script:
    - npm install -g @anthropic-ai/claude-code
    - pip install awscli
  script:
    - claude --print --model claude-opus-4-5-20250601 "Final review before production deployment. Verify: 1) All tests pass, 2) Migration scripts are safe, 3) Rollback plan is ready."
    - ./scripts/deploy-production.sh
  environment:
    name: production
  when: manual
  only:
    - main
'''

print(gitlab_ci_config)

# ============================================================================
# SECTION 5: JENKINS INTEGRATION
# ============================================================================

print("\n" + "=" * 70)
print("JENKINS INTEGRATION")
print("=" * 70)

jenkinsfile_example = '''pipeline {
    agent any

    environment {
        ANTHROPIC_API_KEY = credentials('anthropic-api-key')
        CLAUDE_MODEL = 'claude-haiku-4-5-20250601'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Claude Code Review') {
            steps {
                withEnv(["PATH+CLAUDE=/usr/local/bin"]) {
                    sh '''
                        npm install -g @anthropic-ai/claude-code

                        claude --print --no-stream \
                            --model ${CLAUDE_MODEL} \
                            "Review all modified files since the last merge. Identify: 1) Potential bugs, 2) Security issues, 3) Code quality concerns. Format as JSON report."
                    '''
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'claude-review.json', fingerprint: true
                }
            }
        }

        stage('Test') {
            steps {
                sh 'npm test'
            }
            post {
                always {
                    junit 'test-results/*.xml'
                    publishHTML target: [
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepKe    linkToLastBuild: true,
                        reportDir: 'coverage/',
                        reportFiles: 'index.html'
                    ]
                }
            }
        }

        stage('Deploy to Staging') {
            when {
                branch 'develop'
            }
            steps {
                sh './scripts/deploy-staging.sh'
            }
        }

        stage('Deploy to Production') {
            when {
                branch 'main'
            }
            steps {
                script {
                    def review = sh(
                        script: 'claude --print --model claude-opus-4-5-20250601 "Final production readiness check"',
                        returnStdout: true
                    ).trim()

                    if (review.contains('"approved": true')) {
                        sh './scripts/deploy-production.sh'
                    } else {
                        error 'Production deployment blocked by Claude Code review'
                    }
                }
            }
        }
    }

    post {
        failure {
            slackSend channel: '#deployments',
                      message: "Pipeline failed: ${env.JOB_NAME} ${env.BUILD_NUMBER}"
        }
        success {
            slackSend channel: '#deployments',
                      message: "Pipeline succeeded: ${env.JOB_NAME} ${env.BUILD_NUMBER}"
        }
    }
}
'''

print(jenkinsfile_example)

# ============================================================================
# SECTION 6: EXIT CODES AND ERROR HANDLING
# ============================================================================

print("\n" + "=" * 70)
print("EXIT CODES AND ERROR HANDLING")
print("=" * 70)

exit_code_definitions = {
    0: {
        "name": "Success",
        "description": "Task completed successfully",
        "action": "Continue to next step"
    },
    1: {
        "name": "General Error",
        "description": "Task failed due to error",
        "action": "Fail pipeline, send notification"
    },
    2: {
        "name": "Usage Error",
        "description": "Invalid arguments or configuration",
        "action": "Fail with setup instructions"
    },
    127: {
        "name": "Command Not Found",
        "description": "Claude Code not installed",
        "action": "Install Claude Code in before_script"
    },
    130: {
        "name": "Interrupted",
        "description": "Process interrupted (Ctrl+C)",
        "action": "Consider retry"
    },
    143: {
        "name": "Terminated",
        "description": "Process terminated by signal",
        "action": "Check for stuck processes"
    }
}

print("\n=== Exit Code Definitions ===")
print("{:<12} {:<20} {:<40} {:<30}".format(
    "CODE", "NAME", "DESCRIPTION", "RECOMMENDED ACTION"
))
print("-" * 102)
for code, info in exit_code_definitions.items():
    print("{:<12} {:<20} {:<40} {:<30}".format(
        code, info["name"], info["description"], info["action"]
    ))

# Example error handling script
error_handling_script = '''#!/bin/bash
# ci-error-handling.sh

set -o pipefail
set -e  # Exit on first error

export ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}"
export CLAUDE_MODEL="claude-haiku-4-5-20250601"

echo "Starting Claude Code task..."
claude --print --no-stream --model ${CLAUDE_MODEL} \
    "Execute the specified development task"

EXIT_CODE=$?

echo "Claude Code exited with code: $EXIT_CODE"

case $EXIT_CODE in
    0)
        echo "SUCCESS: Task completed"
        exit 0
        ;;
    1)
        echo "ERROR: Task failed"
        ./scripts/notify-failure.sh
        exit 1
        ;;
    2)
        echo "ERROR: Invalid configuration"
        echo "Check: API key, model name, arguments"
        exit 2
        ;;
    127)
        echo "ERROR: Claude Code not found"
        echo "Install: npm install -g @anthropic-ai/claude-code"
        exit 127
        ;;
    *)
        echo "ERROR: Unexpected exit code $EXIT_CODE"
        ./scripts/notify-failure.sh
        exit $EXIT_CODE
        ;;
esac
'''

print("\n=== Error Handling Script ===")
print(error_handling_script)

# ============================================================================
# SECTION 7: SECURITY IN CI ENVIRONMENT
# ============================================================================

print("\n" + "=" * 70)
print("SECURITY IN CI ENVIRONMENT")
print("=" * 70)

security_best_ractices = """
1. API KEY MANAGEMENT
   - Store API keys as CI secrets, never in code
   - GitHub: Use encrypted secrets
   - GitLab: Use CI/CD variables with masking
   - Jenkins: Use credentials binding

2. ENVIRONMENT ISOLATION
   - Use ephemeral build agents
   - Isolated network namespaces
   - No persistent state between runs

3. PERMISSION MINIMIZATION
   - Use read-only operations when possible
   - Deny Write/Edit in CI environment hooks
   - Require confirmation for Deploy operations

4. LOGGING AND AUDIT
   - Log all Claude Code invocations
   - Include timestamps and user context
   - Store logs for compliance
   - Rotate old logs

5. NETWORK SECURITY
   - Use HTTPS for all API calls
   - Validate SSL certificates
   - Restrict outbound connections

6. ARTIFACT VERIFICATION
   - Sign generated artifacts
   - Verify checksums
   - Scan for secrets before publishing
"""

print(security_best_ractices)

# ============================================================================
# SECTION 8: CI/CD PIPELINE EXAMPLES
# ============================================================================

print("\n" + "=" * 70)
print("COMPLETE CI/CD PIPELINE EXAMPLES")
print("=" * 70)

print("\n--- EXAMPLE 1: Automated Code Review Pipeline ---")

def generate_review_pipeline():
    """Generate a complete code review pipeline example."""
    pipeline = {
        "name": "automated-code-review",
        "triggers": ["pull_request", "push"],
        "stages": [
            {
                "name": "checkout",
                "description": "Checkout code with history",
                "commands": ["git checkout $COMMIT_SHA", "git fetch --unshallow"]
            },
            {
                "name": "lint",
                "description": "Run static analysis",
                "commands": ["npm run lint", "npm run type-check"]
            },
            {
                "name": "claude-review",
                "description": "Claude Code code review",
                "commands": [
                    "claude --print --no-stream --model claude-sonnet-4-5-20250601",
                    "--prompt \"Review code changes in this commit. Format as JSON with: issues array, severity, line numbers.\""
                ],
                "timeout": 120000
            },
            {
                "name": "post-review",
                "description": "Post review to PR",
                "commands": ["./scripts/parse-review.js", "./scripts/post-comments.js"],
                "on_failure": "continue"
            }
        ],
        "notifications": {
            "on_failure": ["slack", "email"],
            "on_success": ["slack"]
        }
    }
    return pipeline

print("\n--- EXAMPLE 2: Documentation Generation Pipeline ---")

def generate_docs_pipeline():
    """Generate a documentation pipeline example."""
    pipeline = {
        "name": "automated-documentation",
        "triggers": ["push to main"],
        "schedule": "0 2 * * *",  # Daily at 2 AM
        "stages": [
            {
                "name": "generate-docs",
                "description": "Generate API docs",
                "model": "claude-sonnet-4-5-20250601",
                "prompt": "Generate comprehensive API documentation for all files in src/. Include: function signatures, parameter descriptions, usage examples, return types.",
                "output": "docs/api.md"
            },
            {
                "name": "review-docs",
                "description": "Review generated docs",
                "model": "claude-haiku-4-5-20250601",
                "prompt": "Review the generated documentation at docs/api.md. Check for: accuracy, clarity, completeness."
            },
            {
                "name": "commit-docs",
                "description": "Commit to repo",
                "commands": ["git add docs/", "git commit -m 'docs: auto-generated API documentation'", "git push"],
                "branch": "main"
            }
        ]
    }
    return pipeline

# Print pipeline details
review_pipeline = generate_review_pipeline()
print(f"""
Pipeline: {review_pipeline['name']}
Triggers: {', '.join(review_pipeline['triggers'])}
Stages:
  1. {review_pipeline['stages'][0]['name']} - {review_pipeline['stages'][0]['description']}
  2. {review_pipeline['stages'][1]['name']} - {review_pipeline['stages'][1]['description']}
  3. {review_pipeline['stages'][2]['name']} - {review_pipeline['stages'][2]['description']}
  4. {review_pipeline['stages'][3]['name']} - {review_pipeline['stages'][3]['description']}
""")

docs_pipeline = generate_docs_pipeline()
print(f"""
Pipeline: {docs_pipeline['name']}
Triggers: {docs_pipeline['triggers'][0]}, Schedule: {docs_pipeline['schedule']}
Stages:
  1. {docs_pipeline['stages'][0]['name']} - {docs_pipeline['stages'][0]['description']}
  2. {docs_pipeline['stages'][1]['name']} - {docs_pipeline['stages'][1]['description']}
  3. {docs_pipeline['stages'][2]['name']} - {docs_pipeline['stages'][2]['description']}
""")

# ============================================================================
# SECTION 9: REAL-TIME SCENARIOS
# ============================================================================

print("\n" + "=" * 70)
print("REAL-TIME SCENARIOS")
print("=" * 70)

print("\n--- SCENARIO 1: Nightly Documentation Update ---")
print("""
Situation: Update documentation every night at 2 AM

Implementation:
1. Use GitLab CI with schedule trigger or GitHub Actions cron
2. Checkout main branch
3. Run Claude Code with documentation prompt
4. Create commit if changes detected
5. Open PR with changes
6. Notify on Slack

Benefits: Fresh documentation without manual effort
""")

print("\n--- SCENARIO 2: Pre-Deployment Security Scan ---")
print("""
Situation: Run security scan before any deployment

Implementation:
1. Use pre-deployment gate in pipeline
2. Claude Code performs security analysis
3. Check for: secrets in code, vulnerable dependencies, misconfigs
4. Block deployment if critical issues found
5. Post results as PR comment

Benefits: Catch security issues before production
""")

print("\n--- SCENARIO 3: Automated Bug Triage ---")
print("""
Situation: Automatically analyze new bug reports

Implementation:
1. Trigger on new issue creation
2. Claude Code analyzes bug description
3. Suggest: priority, affected components, potential fixes
4. Add labels and assignments
5. Create tracking task

Benefits: Faster bug response, consistent triage
""")

# ============================================================================
# SECTION 10: COMMON MISTAKES IN CI/CD INTEGRATION
# ============================================================================

print("\n" + "=" * 70)
print("COMMON MISTAKES TO AVOID")
print("=" * 70)

mistakes = [
    ("Hardcoded API keys", "API_KEY='sk-ant-xxx'", "Use CI secrets/variables"),
    ("Missing timeout", "Operations run forever", T"Set timeout after 30 min"),
    ("Ignoring exit codes", "No failure handling", "Check $? after each command"),
    ("No error recovery", "Single failure = no recovery", "Implement rollback steps"),
    ("Logging secrets", "Printing API keys", "Use masked output"),
    ("No parallelism", "Sequential when parallel possible", "Use matrix builds"),
    ("Overly long prompts", "Timeout failures", "Chunk long tasks")
]

print("\n{:<25} {:<35} {:<30}".format("MISTAKE", "WRONG", "RIGHT"))
print("-" * 90)
for mistake, wrong, right in mistakes:
    print(f"{mistake:<25} {wrong:<35} {right:<30}")

# ============================================================================
# SECTION 11: INTERVIEW Q&A
# ============================================================================

print("\n" + "=" * 70)
print("INTERVIEW QUESTIONS AND ANSWERS")
print("=" * 70)

qa_pairs = [
    (
        "Q: How do you integrate Claude Code in a CI pipeline?",
        """
A: Integration involves several key steps:

   1. SETUP: Install Claude Code in the CI environment
      npm install -g @anthropic-ai/claude-code

   2. AUTHENTICATION: Store API key as CI secret
      - GitHub: Settings > Secrets
      - GitLab: CI/CD > Variables
      - Jenkins: Credentials binding

   3. NO NTERACTIVE MODE: Use --print --no-stream flags

   4. ERROR HANDLING: Check exit codes and handle failures

   5. OUTPUT PARSING: Parse structured output for reporting

   Example:
   claude --print --model claude-haiku-4-5-20250601 "Review code"
   if [ $? -ne 0 ]; then echo "Claude Code failed"; exit 1; fi
        """
    ),
    (
        "Q: What considerations apply to CI security?",
        """
A: Security in CI requires:

   1. SECRETS MANAGEMENT: Never hardcode. Use encrypted secrets,
      masked variables, and credential bindings.

   2. PERMISSION MINIMIZATION: Use read-only access where possible.
      Deny destructive operations without explicit confirmation.

   3. EPHEMERAL ENVIRONMENTS: Use fresh VMs/containers for each run.
      Prevent state persistence between builds.

   4. NETWORK ISOLATION: Restrict outbound connections.
      Use internal artifact repositories only.

   5. AUDIT LOGGING: Log all operations with timestamps.
      Track who/what/when for compliance.

   6. ARTIFACT SCANNING: Scan artifacts before publishing.
      Check for embedded secrets, vulnerabilities.
        """
    ),
    (
        "Q: How do you handle Claude Code failures in CI?",
        """
A: Failure handling best practices:

   1. CHECK EXIT CODES: Always check $? after Claude Code runs
      claude --print ...
      if [ $? -ne 0 ]; then handle_error; fi

   2. DIVISION: Implement retry logic for transient failures
      for i in 1 2 3; do
          claude --print ... && break
          sleep 30
      done

   3. ROLLBACK: Revert any partial changes on failure

   4. NOTIFICATIONS: Alert the team via Slack/Email

   5. ARTIFACTS: Save logs and output for debugging

   6. PARALLELISM: Run independent checks in parallel to fail fast
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
1. NON-INTERACTIVE MODE
   - Use --print and --no-stream flags
   - Configure via environment variables
   - Set appropriate timeouts

2. EXIT CODES
   - 0 = Success
   - 1 = General error
   - 2 = Usage error
   - 127 = Not installed
   - Always check exit codes in CI

3. CI PLATFORM INTEGRATIONS
   - GitHub Actions: jobs, steps, secrets
   - GitLab CI: stages, variables, artifacts
   - Jenkins: pipeline, environment, credentials

4. SECURITY BEST PRACTICES
   - Secrets as CI variables
   - Read-only when possible
   - Audit logging
   - Artifact scanning

5. PIPELINE PATTERNS
   - Code review pipelines
   - Documentation generation
   - Security scanning
   - Deployment automation

6. ERROR HANDLING
   - Retry with backoff
   - Rollback on failure
   - Notification on errors
   - Save artifacts for debugging

7. OUTPUT FORMATS
   - JSON for parsing
   - Markdown for reports
   - Machine-readable for automation
"""

print(lessons)

# ============================================================================
# SYNTAX VERIFICATION
# ============================================================================

print("\n=== File Syntax Verification ===")
print("This file has been created successfully.")
print("Run: python -m py_compile <file_path> to verify syntax.")
print("=" * 70)
