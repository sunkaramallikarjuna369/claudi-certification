# ============================================================================
# PRACTICE FILE: Development Best Practices
# Domain 3.5: Best Practices for Development
# ============================================================================
#
# PURPOSE: Learn the best practices for organizing projects, documenting
# with CLAUDE.md, implementing code review workflows, and optimizing
# development environments.
#
# ============================================================================
# SECTION 1: PROJECT STRUCTURE ORGANIZATION
# ============================================================================

print("=" * 70)
print("PROJECT STRUCTURE ORGANIZATION")
print("=" * 70)

project_structure_example = """
A well-organized project structure is essential for Claude Code to
understand and work effectively with your codebase.

=== RECOMMENDED STRUCTURE ===

project-root/
|
|-- CLAUDE.md              # Project documentation for Claude Code (REQUIRED)
|-- .env                   # Environment variables (NOT committed)
|-- .env.example           # Template for .env (committed)
|-- .gitignore             # Git ignore rules (include .env!)
|-- .claude/
|   |-- settings.json      # Project-level settings (optional)
|   |-- hooks/             # Custom hook scripts
|   |-- state/             # Workflow state files
|   |-- logs/              # Execution logs
|
|-- src/                   # Source code
|-- tests/                 # Test files
|-- scripts/               # Utility scripts
|-- docs/                  # Documentation
|-- configs/               # Configuration files
|-- tools/                 # Internal tools
|
|-- package.json           # Node.js dependencies
|-- pyproject.toml         # Python dependencies
|-- Dockerfile             # Container definition
|-- docker-compose.yml     # Local development environment

=== STRUCTURE PRINCIPLES ===

1. CONSISTENCY
   - Follow language-specific conventions
   - Language: src/, lib/ for source code
   - Tests: tests/, __tests__/, test/
   - Docs: docs/, doc/

2. CLAUDE.md PLACEMENT
   - Always in project root
   - First file Claude Code reads
   - Use for project context and instructions

3. SEPARATION OF CONCERNS
   - Source code separate from tests
   - Configuration separate from code
   - Secrets separate from everything

4. DISCOVERABILITY
   - Standard file names (index.js, main.py)
   - Consistent directory structure
   - README files in each major directory
"""

print(project_structure_example)

# ============================================================================
# SECTION 2: CLAUDE.MD DOCUMENTATION STANDARDS
# ============================================================================

print("\n" + "=" * 70)
print("CLAUDE.MD DOCUMENTATION STANDARDS")
print("=" * 70)

claude_md_example = '''# Project Name
Brief project description (1-2 sentences)

## Project Overview
Detailed description of what this project does.
Why it exists, who it serves, key features.

## Tech Stack
- Language: Python 3.11+
- Framework: FastAPI
- Database: PostgreSQL
- Cache: Redis
- Other tools: Docker, Kubernetes

## Project Structure
- src/ - Main application code
- tests/ - Test files
- scripts/ - Utility scripts
- docs/ - Documentation

## Development Setup
### Prerequisites
- Python 3.11 or higher
- PostgreSQL 14+
- Redis 6+

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
- Follow PEP 8 style guide
- Use type hints for all functions
- Write docstrings for public functions
- Maximum line length: 100 characters

## Testing
- Run tests: pytest tests/
- Coverage: pytest --cov=src tests/
- Minimum coverage: 80%

## Git Workflow
- Branch naming: feature/, bugfix/, hotfix/
- Commit format: type(scope): description
- Pull request requirements: 2 approvals, passing CI

## Environment Variables
| Variable | Description | Required |
|----------|-------------|----------|
| DATABASE_URL | PostgreSQL connection string | Yes |
| REDIS_URL | Redis connection string | Yes |
| API_KEY | External API key | No |

## Common Tasks
### Run tests
```bash
pytest tests/ -v
```

### Build documentation
```bash
python scripts/build-docs.py
```

### Deploy to staging
```bash
./scripts/deploy-staging.sh
```

## Architecture Decisions
- Using FastAPI for async support and OpenAPI spec generation
- PostgreSQL for relational data, Redis for caching
- Stateless design for horizontal scaling

## Gotchas / Warnings
- Do not modify files in .claude/ manually
- Environment variables must be set before running
- Database migrations run automatically on startup
'''

print("CLAUDE.md Example Content:")
print("-" * 40)
print(claude_md_example[:1500] + "\n... (truncated)")

# ============================================================================
# SECTION 3: CODE REVIEW WORKFLOWS
# ============================================================================

print("\n" + "=" * 70)
print("CODE REVIEW WORKFLOWS")
print("=" * 70)

def create_code_review_workflow():
    """
    Demonstrates a code review workflow with Claude Code.
    """
    workflow = {
        "name": "Code Review Workflow",
        "description": "Automated and manual review steps",
        "steps": {
            "automated_checks": {
                "description": "Automated lint, type check, tests",
                "actions": [
                    "Run linter: npm run lint",
                    "Run type checker: mypy src/",
                    "Run tests: pytest tests/",
                    "Run security scan: npm audit"
                ],
                "can_block_merge": True
            },
            "claude_review": {
                "description": "Claude Code reviews code changes",
                "prompt": """Review code changes in this pull request.
                Focus on:
                1. Code quality and readability
                2. Potential bugs or logic errors
                3. Performance concerns
                4. Security vulnerabilities
                5. Test coverage

                Format output as JSON with:
                - issues: array of findings
                - severity: critical/major/minor
                - location: file and line number
                - suggestion: how to fix""",
                "model": "claude-sonnet-4-5-20250601",
                "can_block_merge": True
            },
            "peer_review": {
                "description": "Human code review",
                "actions": [
                    "Review CLAUDE.md generated report",
                    "Check architecture decisions",
                    "Approve or request changes"
                ],
                "can_block_merge": True,
                "required_approvals": 2
            },
            "merge": {
                "description": "Merge after all checks pass",
                "conditions": [
                    "All automated checks pass",
                    "Claude review findings addressed",
                    "Minimum 2 approvals"
                ]
            }
        }
    }
    return workflow

review_workflow = create_code_review_workflow()
print("=== Code Review Workflow ===")
print(f"Name: {review_workflow['name']}")
print(f"Description: {review_workflow['description']}")
print("\nSteps:")
for step_name, step_info in review_workflow['steps'].items():
    blocker = "BLOCKS MERGE" if step_info.get('can_block_merge') else "Advisory only"
    print(f"  {step_name}: {step_info['description']} [{blocker}]")

# ============================================================================
# SECTION 4: TESTING STRATEGIES
# ============================================================================

print("\n" + "=" * 70)
print("TESTING STRATEGIES")
print("=" * 70)

testing_strategies = {
    "unit_testing": {
        "description": "Test individual functions and classes",
        "focus": "Logic correctness, edge cases",
        "tools": ["pytest", "unittest", "jest"],
        "coverage_target": "80%+",
        "example": """
def test_calculate_total():
    assert calculate_total([1, 2, 3]) == 6
    assert calculate_total([]) == 0
    assert calculate_total([1, -1]) == 0
"""
    },
    "integration_testing": {
        "description": "Test component interactions",
        "focus": "API contracts, database operations",
        "tools": ["pytest", "supertest", "TestContainers"],
        "coverage_target": "60%+",
        "example": """
def test_api_endpoint():
    response = client.get("/api/users")
    assert response.status_code == 200
    assert len(response.json()) > 0
"""
    },
    "end_to_end_testing": {
        "description": "Test complete user flows",
        "focus": "User scenarios, UI interactions",
        "tools": ["Playwright", "Cypress", "Selenium"],
        "coverage_target": "Key scenarios only",
        "example": """
def test_user_registration():
    page.goto("/register")
    page.fill("#email", "test@example.com")
    page.fill("#password", "secure123")
    page.click("#submit")
    expect(page.locator(".success")).to_be_visible()
"""
    }
}

print("\n=== Testing Pyramid ===")
pyramid = """
                    /\\
                   /  \\          E2E Tests (few, comprehensive)
                  /    \\         Focus: Critical user paths
                 /------\\
                /        \\        Integration Tests (more)
               /          \\       Focus: API and component interactions
              /------------\\
             /              \\     Unit Tests (many, fast)
            /________________\\    Focus: Individual functions
"""
print(pyramid)

print("=== Testing Strategies ===")
for strategy, details in testing_strategies.items():
    print(f"\n{strategy.replace('_', ' ').upper()}:")
    print(f"  Description: {details['description']}")
    print(f"  Focus: {details['focus']}")
    print(f"  Coverage Target: {details['coverage_target']}")
    print(f"  Tools: {', '.join(details['tools'])}")

# ============================================================================
# SECTION 5: SECURITY SCANNING INTEGRATION
# ============================================================================

print("\n" + "=" * 70)
print("SECURITY SCANNING INTEGRATION")
print("=" * 70)

security_scan_config = {
    "static_analysis": {
        "tools": ["bandit", "semgrep", "sonarqube"],
        "checks": [
            "SQL injection vulnerabilities",
            "XSS vulnerabilities",
            "Insecure dependencies",
            "Hardcoded secrets",
            "Weak cryptography"
        ],
        "integration": "pre-commit and CI pipeline"
    },
    "dependency_scanning": {
        "tools": ["npm audit", "safety", "snyk", "dependabot"],
        "checks": [
            "Known CVEs in dependencies",
            "Outdated packages",
            "License compliance",
            "Unmaintained packages"
        ],
        "integration": "CI on every PR, daily scheduled scan"
    },
    "secret_scanning": {
        "tools": ["git-secrets", "trufflehog", "gitleaks"],
        "checks": [
            "AWS keys",
            "API keys",
            "Private keys",
            "Database passwords",
            "JWT secrets"
        ],
        "integration": "pre-commit, CI, and pre-receive"
    }
}

print("\n=== Security Scanning Configuration ===")
for category, details in security_scan_config.items():
    print(f"\n{category.replace('_', ' ').upper()}:")
    print(f"  Tools: {', '.join(details['tools'])}")
    print(f"  Checks: {', '.join(details['checks'])}")
    print(f"  Integration: {details['integration']}")

# ============================================================================
# SECTION 6: PERFORMANCE OPTIMIZATION
# ============================================================================

print("\n" + "=" * 70)
print("PERFORMANCE OPTIMIZATION")
print("=" * 70)

performance_tips = """
=== CLAUDE CODE PERFORMANCE TIPS ===

1. USE APPROPRIATE MODEL
   - Haiku for simple, repetitive tasks
   - Sonnet for most development work
   - Opus only for complex reasoning

2. CONTEXT MANAGEMENT
   - Compact conversation regularly
   - Use /compact command to save tokens
   - Focus on relevant context

3. BATCH OPERATIONS
   - Group similar operations
   - Avoid many small requests
   - Use glob patterns for file operations

4. CACHING
   - Cache lint/type check results
   - Use local caching where possible
   - Avoid redundant work

5. TIMEOUT CONFIGURATION
   - Set appropriate timeouts
   - Short for simple operations
   - Long for complex reasoning

6. PARALLEL EXECUTION
   - Run independent tasks in parallel
   - Use branching for parallel operations
   - Reduce total execution time

=== COST OPTIMIZATION ===

1. Model Selection by Task
   | Task Type              | Recommended Model |
   |------------------------|-------------------|
   | Simple file edits      | Haiku             |
   | Documentation updates   | Haiku             |
   | Code review            | Sonnet            |
   | Feature implementation | Sonnet            |
   | Architecture decisions | Opus              |
   | Complex debugging      | Opus              |

2. Token Usage
   - Use concise prompts
   - Compact frequently
   - Remove irrelevant context
   - Set max_tokens appropriately

3. Request Batching
   - Combine related operations
   - Process files in batches
   - Reduce API overhead
"""

print(performance_tips)

# ============================================================================
# SECTION 7: COLLABORATION GUIDELINES
# ============================================================================

print("\n" + "=" * 70)
print("COLLABORATION GUIDELINES")
print("=" * 70)

collaboration_guidelines = """
=== TEAM COLLABORATION PATTERNS ===

1. SHARED CLAUDE.MD
   - Document project-wide conventions
   - Update when team decides on new patterns
   - Review CLAUDE.md in code reviews

2. INDIVIDUAL CONFIGURATIONS
   - ~/.claude/settings.json for personal preferences
   - Project-level for team standards
   - .env.local for local overrides

3. WORKFLOW ORCHESTRATION
   - Use shared workflows for consistency
   - Document custom workflows in CLAUDE.md
   - Automate common tasks

4. KNOWLEDGE SHARING
   - Share Claude Code sessions that teach
   - Document clever prompting techniques
   - Create custom commands for common tasks

=== CODE REVIEW BEST PRACTICES ===

1. SELF-REVIEW BEFORE ASKING
   - Run linters and type checkers locally
   - Test your changes manually
   - Review your own diff first

2. SMALL, FOCUSED PRs
   - One feature/bug per PR
   --under 400 lines changed
   - Easy to review understand

3. RESPONSIVE REVIEW
   - Address feedback within 24 hours
   - Ask questions if unclear
   - Explain your reasoning

4. DOCUMENT DECISIONS
   - Explain non-obvious choices
   - Link to relevant docs/tickets
   - Update CLAUDE.md if needed

=== HANDLING DISAGREEMENTS ===

1. DISCUSS IN PR
   - Ask clarifying questions
   - Propose alternatives
   - Request a meeting if complex

2. DEFER TO OWNER
   - Respect code ownership
   - Domain expert has final say
   - Can escalate if unresolved

3. MEETING NOTES
   - Document agreement in PR
   - Update CLAUDE.md if pattern emerges
   - Avoid repeating resolved debates
"""

print(collaboration_guidelines)

# ============================================================================
# SECTION 8: VERSION CONTROL BEST PRACTICES
# ============================================================================

print("\n" + "=" * 70)
print("VERSION CONTROL BEST PRACTICES")
print("=" * 70)

def create_git_best_practices():
    """Git best practices for team development."""
    practices = [
        {
            "category": "Branch Naming",
            "rules": [
                "feature/<ticket-id>-description",
                "bugfix/<ticket-id>-description",
                "hotfix/<ticket-id>-description",
                "release/<version>"
            ],
            "example": "feature/ABC-123-user-authentication"
        },
        {
            "category": "Commit Messages",
            "format": "type(scope): description",
            "types": ["feat", "fix", "docs", "style", "refactor", "test", "chore"],
            "rules": [
                "Subject line under 72 characters",
                "Use imperative mood (Add, not Added)",
                "Reference ticket in ticket number",
                "Explain body for non-obvious changes"
            ]
        },
        {
            "category": "Pull Requests",
            "requirements": [
                "Descriptive title",
                "Summary of changes",
                "Linked ticket",
                "Testing instructions",
                "Screenshots for UI changes"
            ],
            "checks": [
                "CI passes",
                "Reviewed by required approvers",
                "No merge conflicts"
            ]
        }
    ]
    return practices

git_practices = create_git_best_practices()
for practice in git_practices:
    print(f"\n{practice['category'].upper()}:")
    if "format" in practice:
        print(f"  Format: {practice['format']}")
    if "types" in practice:
        print(f"  Types: {', '.join(practice['types'])}")
    if "rules" in practice:
        print(f"  Rules:")
        for rule in practice['rules']:
            print(f"    - {rule}")

# ============================================================================
# SECTION 9: REAL-TIME SCENARIOS
# ============================================================================

print("\n" + "=" * 70)
print("REAL-TIME SCENARIOS")
print("=" * 70)

print("\n--- SCENARIO 1: New Team Member Onboarding ---")
print("""
Situation: New developer joins the team, needs to understand project.

Best Practices:
1. Point them to CLAUDE.md first
2. Explain the project structure
3. Show how to set up local environment
4. Demonstrate basic Claude Code usage
5. Pair on first task

Key documents to share:
- CLAUDE.md (with project conventions)
- README.md (with setup instructions)
- CONTRIBUTING.md (if exists)
- Architecture docs
""")

print("\n--- SCENARIO 2: Refactoring Large Module ---")
print("""
Situation: Need to refactor a 10,000-line module.

Best Practices:
1. Create feature branch
2. Review current code with Claude Code
3. Plan refactoring in small steps
4. Implement incrementally with tests
5. Review each piece before moving on
6. Update CLAUDE.md if patterns change

Keep refactors small and reviewable.
""")

print("\n--- SCENARIO 3: Performance Optimization Sprint ---")
print("""
Situation: Application is slow, need to optimize.

Best Practices:
1. Profile first - don't guess
2. Identify top bottlenecks
3. Create tickets for each issue
4. Claude Code can help analyze code paths
5. Verify improvements with benchmarks
6. Document performance-sensitive areas in CLAUDE.md
""")

# ============================================================================
# SECTION 10: COMMON MISTAKES
# ============================================================================

print("\n" + "=" * 70)
print("COMMON MISTAKES TO AVOID")
print("=" * 70)

mistakes = [
    ("No CLAUDE.md", "Claude Code lacks context", "Create CLAUDE.md in root"),
    ("Outdated docs", "Wrong information", "Update docs with changes"),
    ("Huge PRs", "Hard to review properly", "Keep PRs under 400 lines"),
    ("Missing tests", "No regression protection", "Write tests for new code"),
    ("No type hints", "Hard to understand types", "Add type annotations"),
    ("Ignored linter", "Style inconsistencies", "Fix linting issues"),
    ("No rollback plan", "Deploy failures", "Always have rollback"),
    ("Forgotten .env", "Secrets exposed", "Use .env.example")
]

print("\n{:<25} {:<35} {:<35}".format("MISTAKE", "WRONG", "RIGHT"))
print("-" * 95)
for mistake, wrong, right in mistakes:
    print(f"{mistake:<25} {wrong:<35} {right:<35}")

# ============================================================================
# SECTION 11: INTERVIEW Q&A
# ============================================================================

print("\n" + "=" * 70)
print("INTERVIEW QUESTIONS AND ANSWERS")
print("=" * 70)

qa_pairs = [
    (
        "Q: How do you organize a new project for Claude Code?",
        """
A: Organization best practices:

   1. CREATE BASIC STRUCTURE
      - src/ for source code
      - tests/ for test files
      - docs/ for documentation
      - scripts/ for utilities

   2. CREATE CLAUDE.MD
      - Project overview and purpose
      - Tech stack and architecture
      - Development setup instructions
      - Coding standards
      - Common tasks
      - Gotchas and warnings

   3. SET UP CONFIGURATION
      - .env.example for required variables
      - .gitignore include .env
      - .claude/settings.json if needed

   4. ESTABLISH CONVENTIONS
      - Coding standards
      - Git workflow
      - Testing requirements
      - Code review process

   5. VERIFY CLAUDE CODE WORKS
      - Run a simple task
      - Verify it understands the project
      - Update documentation as needed
        """
    ),
    (
        "Q: What should be in CLAUDE.md?",
        """
A: A comprehensive CLAUDE.md includes:

   1. PROJECT OVERVIEW
      - What the project does
      - Who it serves
      - Key features

   2. TECH STACK
      - Languages, frameworks, databases
      - Tooling and build systems

   3. PROJECT STRUCTURE
      - Directory layout
      - File naming conventions

   4. DEVELOPMENT SETUP
      - Prerequisites
      - Installation steps
      - How to run locally

   5. CODING STANDARDS
      - Style guide to follow
      - Type hinting requirements
      - Documentation requirements

   6. TESTING STANDARDS
      - How to run tests
      - Coverage requirements
      - Testing patterns

   7. GIT WORKFLOW
      - Branch naming
      - Commit message format
      - PR requirements

   8. COMMON TASKS
      - How to do frequent operations
      - Scripts and commands

   9. ARCHITECTURE DECISIONS
      - Key design choices
      - Why decisions were made

   10. GOTCHAS
       - Common pitfalls to avoid
       - Important warnings
        """
    ),
    (
        "Q: How do you ensure code quality in your team?",
        """
A: Multi-layered approach to code quality:

   1. PREVENTIVE MEASURES
      - Linting (automatic style enforcement)
      - Type checking (mypy, TypeScript)
      - Pre-commit hooks

   2. DETECTIVE MEASURES
      - Code review by peers
      - Claude Code automated review
      - Static analysis tools

   3. CORRECTIVE MEASURES
      - Test coverage requirements
      - CI pipeline gates
      - Security scanning

   4. CULTURAL ELEMENTS
      - Code review as learning opportunity
      - Documentation of decisions
      - Retrospectives on quality issues

   5. TOOLS AND AUTOMATION
      - Automated testing
      - Automated documentation generation
      - Automated dependency updates
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
1. PROJECT STRUCTURE
   - Standard directory layout
   - CLAUDE.md in root
   - Separate configs, secrets, source

2. CLAUDE.MD DOCUMENTATION
   - Project overview
   - Tech stack and structure
   - Development setup
   - Coding standards
   - Common tasks

3. CODE REVIEW WORKFLOWS
   - Automated checks first
   - Claude Code review
   - Human review
   - Clear merge requirements

4. TESTING STRATEGIES
   - Unit tests for functions
   - Integration tests for APIs
   - E2E tests for critical paths
   - Testing pyramid

5. SECURITY SCANNING
   - Static analysis
   - Dependency scanning
   - Secret detection
   - Integrate in CI

6. PERFORMANCE
   - Use appropriate model
   - Manage context
   - Batch operations
   - Set timeouts

7. COLLABORATION
   - Shared CLAUDE.md
   - Small, focused PRs
   - Responsive review
   - Document decisions

8. VERSION CONTROL
   - Branch naming conventions
   - Commit message format
   - PR requirements
"""

print(lessons)

# ============================================================================
# SYNTAX VERIFICATION
# ============================================================================

print("\n=== File Syntax Verification ===")
print("This file has been created successfully.")
print("Run: python -m py_compile <file_path> to verify syntax.")
print("=" * 70)
