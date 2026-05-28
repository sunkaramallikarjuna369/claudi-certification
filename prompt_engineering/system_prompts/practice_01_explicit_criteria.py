"""
SYSTEM PROMPTS WITH EXPLICIT CRITERIA - Practice File 01
=========================================================

This file teaches how to craft effective system prompts that:
1. Define clear roles for the LLM
2. Specify exact output formats
3. Set evaluation criteria
4. Define constraints (what NOT to do)
5. Integrate examples naturally
6. Define tone and style guidelines

REAL-WORLD SCENARIO:
You are building a customer service chatbot that must:
- Always be polite and professional
- Never make up product information
- Follow a specific response format
- Escalate complex issues to humans
"""

import os
from dotenv import load_dotenv
from anthropic import Anthropic

# ============================================================================
# SECTION 1: LOAD ENVIRONMENT AND SETUP
# ============================================================================
# Load API key from .env file - this is the standard way to handle secrets
# In production, use environment variables or a secrets manager

load_dotenv()  # Loads variables from .env file in current directory

# Verify the API key is loaded - raise error if missing
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError(
        "ANTHROPIC_API_KEY not found in environment. "
        "Please create a .env file with your API key."
    )

# Initialize the Anthropic client
client = Anthropic()

# ============================================================================
# SECTION 2: THE BASIC SYSTEM PROMPT PATTERN
# ============================================================================
# A system prompt has three main parts:
# 1. ROLE DEFINITION - Who is the AI?
# 2. TASK INSTRUCTIONS - What should it do?
# 3. OUTPUT FORMAT - How should it respond?

# Example: A code reviewer system prompt
basic_system_prompt = """
You are a Python code reviewer with expertise in:
- PEP 8 style guidelines
- Security best practices
- Performance optimization
- Documentation standards

TASK: Review the provided Python code and identify issues.

OUTPUT FORMAT:
- Severity: HIGH | MEDIUM | LOW
- Line number (if applicable)
- Issue description
- Suggested fix (if applicable)

IMPORTANT CONSTRAINTS:
- Do not rewrite the entire code, only suggest specific fixes
- Do not make subjective style comments (e.g., "I prefer...")
- Always explain WHY something is an issue
"""

# ============================================================================
# SECTION 3: SYSTEM PROMPTS WITH EXPLICIT CRITERIA
# ============================================================================
# Explicit criteria make output predictable and testable

def review_code_with_explicit_criteria(code: str) -> str:
    """
    Review code using a system prompt with explicit criteria.

    Args:
        code: Python code to review

    Returns:
        Structured review output
    """
    system_prompt = """
You are a Python code reviewer specialized in security and performance.

CRITERIA FOR REVIEW (evaluate each):
1. SECURITY ISSUES (check for):
   - SQL injection vulnerabilities
   - Hardcoded credentials or secrets
   - Unsafe input validation
   - Path traversal risks

2. PERFORMANCE PROBLEMS (check for):
   - Inefficient loops
   - Unnecessary database queries
   - Missing indexes hints
   - Memory-intensive operations

3. CODE QUALITY (check for):
   - Missing docstrings
   - Unclear variable names
   - Missing error handling
   - Magic numbers without constants

OUTPUT FORMAT (strict):
[SECURITY]
- Issue: <description>
- Location: <line number or "N/A">
- Severity: HIGH/MEDIUM/LOW
- Fix: <suggested correction>

[PERFORMANCE]
- Same structure as SECURITY

[QUALITY]
- Same structure as SECURITY

[RECOMMENDATIONS]
1. <priority 1 recommendation>
2. <priority 2 recommendation>

CONSTRAINTS:
- If no issues found in a category, write "No issues found"
- Never explain what the code does, only what is wrong
- Use bullet points, never numbered lists
"""

    response = client.messages.create(
        model="claude-haiku-4-5-20250601",
        max_tokens=2048,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": f"Review this Python code:\n\n```python\n{code}\n```"
            }
        ]
    )

    return response.content[0].text


# ============================================================================
# SECTION 4: SYSTEM PROMPT WITH ROLE + CONSTRAINTS
# ============================================================================
# Combining role definition with strict constraints

def create_technical_writer_system_prompt(topic: str, audience: str,
                                          technical_level: str) -> str:
    """
    Create a system prompt for technical writing with all constraints.

    Args:
        topic: The subject matter to write about
        audience: Who will read the content
        technical_level: beginner/intermediate/advanced

    Returns:
        Complete system prompt string
    """
    # Role definition
    role = """
You are a technical documentation writer with 15 years of experience
creating clear, accurate documentation for software products.
"""

    # Tone and style guidelines
    style = """
STYLE GUIDE:
- Use active voice ("The function processes data" not "Data is processed")
- Keep sentences under 25 words
- Define technical terms on first use
- Use "you" and "your" when addressing readers
- Avoid jargon without explanation
- Use code blocks for all code examples
- Add comments in code examples to explain each step
"""

    # Audience-specific adjustments
    audience_guidance = {
        "beginner": """
AUDIENCE ADJUSTMENT (Beginner):
- Explain every technical term
- Provide step-by-step instructions
- Include real-world analogies
- Add troubleshooting sections
- Use extensive code comments
""",
        "intermediate": """
AUDIENCE ADJUSTMENT (Intermediate):
- Assume basic knowledge of the topic
- Focus on practical applications
- Include advanced tips in separate sections
- Moderate code comment density
""",
        "advanced": """
AUDIENCE ADJUSTMENT (Advanced):
- Use technical terminology freely
- Focus on edge cases and optimizations
- Include performance comparisons
- Minimal code comments needed
"""
    }

    # Output format specification
    output_format = """
OUTPUT FORMAT:
1. Title (H1)
2. Introduction (2-3 paragraphs)
3. Main Content (sections with H2 headers)
4. Code Examples (with explanations)
5. Common Mistakes section
6. Summary (bullet points)

FORMATTING RULES:
- Use ### for section headers
- Use > for important notes
- Use ``` for code blocks
- Never use emoji in technical content
- Maximum 80 characters per line
"""

    # Constraints - what NOT to do
    constraints = """
FORBIDDEN:
- Do not invent API parameters or methods
- Do not include placeholder text like "[insert example here]"
- Do not use marketing language ("amazing", "revolutionary")
- Do not skip error handling explanations
- Do not assume latest framework versions without verification
"""

    # Combine all parts
    system_prompt = (
        role + style +
        audience_guidance.get(technical_level, audience_guidance["intermediate"]) +
        output_format + constraints
    )

    return system_prompt


# ============================================================================
# SECTION 5: ITERATIVE SYSTEM PROMPT IMPROVEMENT
# ============================================================================
# System prompts often need iteration to work correctly

def iterative_prompt_development():
    """
    Demonstrate how system prompts evolve through iteration.

    Iteration pattern:
    1. Start with basic prompt
    2. Test with edge cases
    3. Identify failures
    4. Add constraints for failures
    5. Repeat until reliable
    """

    # Version 1: Basic prompt (often fails)
    v1_prompt = "You are a helpful assistant that summarizes articles."

    # Version 2: Added format (better but incomplete)
    v2_prompt = """
You are a helpful assistant that summarizes articles.
Format your response as:
- Main topic:
- Key points (3-5 bullets):
- Conclusion:
"""

    # Version 3: Added constraints (more reliable)
    v3_prompt = """
You are a helpful assistant that summarizes articles accurately.

FORMAT (mandatory):
## Summary
<2 paragraph summary>

## Key Points
- <point 1>
- <point 2>
- <point 3>

## Keywords
<5 important terms>

CONSTRAINTS:
- Never invent information not in the article
- If the article doesn't contain enough info, say so
- Keep summaries under 300 words
- Use neutral language, never hype
"""

    # Version 4: Added evaluation criteria
    v4_prompt = """
You are a helpful assistant that summarizes articles accurately.

QUALITY CRITERIA (your output will be evaluated on):
1. ACCURACY: Does summary reflect actual article content?
2. COMPLETENESS: Are key points covered?
3. CONCISENESS: Is irrelevant information excluded?
4. CLARITY: Is the summary easy to understand?

FORMAT:
## Summary
[2 paragraphs max]

## Key Points
- [Bullet points, 3-5 items]

## Keywords
[Comma-separated, 5 terms]

CONSTRAINTS:
- Never hallucinate or add information not in source
- If article is too short for meaningful summary, say "Article too brief"
- Use same language as article
"""

    print("Iteration demonstrates progressive improvement:")
    print("v1: Basic role -> v2: Format added -> v3: Constraints -> v4: Quality criteria")
    return v4_prompt


# ============================================================================
# SECTION 6: COMMON MISTAKES AND HOW TO AVOID THEM
# ============================================================================
"""
COMMON MISTAKE 1: Overloading the system prompt
Bad: "You are helpful, smart, friendly, professional, efficient,
     thorough, detailed, accurate..." - Too many adjectives
Good: "You are a technical writer focused on clarity and accuracy."

COMMON MISTAKE 2: Vague constraints
Bad: "Don't make mistakes" - What constitutes a mistake?
Good: "Never include information not present in the source material."

COMMON MISTAKE 3: Contradictory instructions
Bad: "Be concise BUT include all details" - Impossible to satisfy
Good: "Summarize in 3 sentences, covering only the top 3 points."

COMMON MISTAKE 4: No output format specification
Bad: "Explain how the code works" - Unpredictable length/style
Good: "Explain in 2-3 paragraphs, covering: input, process, output"
"""

# ============================================================================
# SECTION 7: EXAMPLE USAGE
# ============================================================================

# Example Python code to review
sample_code = """
def get_user_data(username):
    query = f"SELECT * FROM users WHERE name = '{username}'"
    return execute_query(query)

def calculate_total(items):
    total = 0
    for item in items:
        total += item['price'] * item['qty']
    return total

def send_email(to, subject, body):
    import smtplib
    server = smtplib.SMTP('smtp.example.com')
    server.sendmail('app@example.com', to, body)
"""

# Run the code review example
if __name__ == "__main__":
    print("=" * 60)
    print("SYSTEM PROMPTS - PRACTICE 01: EXPLICIT CRITERIA")
    print("=" * 60)

    # Demo: Generate a system prompt
    print("\n[DEMO] Generating technical writer system prompt...")
    writer_prompt = create_technical_writer_system_prompt(
        topic="Python Decorators",
        audience="Software developers",
        technical_level="intermediate"
    )
    print(f"System prompt created (length: {len(writer_prompt)} chars)")

    # Demo: Show iterative improvement
    print("\n[DEMO] Iterative prompt development...")
    final_prompt = iterative_prompt_development()
    print("Final optimized prompt ready for use")

    # Note: Full review would require API call
    print("\n[DEMO] Code review would analyze:")
    for line in sample_code.split('\n'):
        if line.strip() and not line.strip().startswith('#'):
            print(f"  - {line.strip()[:50]}...")

    print("\n" + "=" * 60)
    print("WHAT WE HAVE LEARNT:")
    print("=" * 60)
    print("""
1. SYSTEM PROMPT STRUCTURE
   - Role definition: Who is the AI?
   - Task instructions: What to do
   - Output format: How to respond
   - Constraints: What NOT to do

2. EXPLICIT CRITERIA
   - Make requirements specific and measurable
   - Define success/failure conditions
   - Specify exact output formats with examples
   - List forbidden behaviors clearly

3. ITERATIVE IMPROVEMENT
   - Start simple, then add constraints
   - Test with edge cases
   - Identify and fix failures
   - Repeat until reliable

4. COMMON PATTERNS
   - Separate role from instructions
   - Use sections for clarity
   - Add examples within system prompt
   - Include "what not to do" explicitly

5. TONE AND STYLE
   - Define voice (formal/casual)
   - Set length constraints
   - Specify terminology usage
   - Guide audience adaptation

6. AVOID THESE MISTAKES
   - Vague role definitions
   - Contradictory instructions
   - Overloading with adjectives
   - Missing output format
   - No evaluation criteria
""")

# ============================================================================
# INTERVIEW Q&A PREP
# ============================================================================
"""
Q: How do you make LLM outputs consistent?
A: Use explicit output format specifications in system prompt with
   examples. Include validation criteria and forbidden behaviors.

Q: What makes a good system prompt?
A: Clear role, specific instructions, exact output format, explicit
   constraints, and testable quality criteria.

Q: How do you handle conflicting instructions in system prompts?
A: Prioritize constraints, clarify ambiguous terms, and test with
   edge cases to identify conflicts early.

Q: Should system prompts be long or short?
A: As short as possible while being complete. Long prompts don't
   necessarily improve results - clarity and specificity do.
"""