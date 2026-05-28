"""
+===========================================================================+
|                                                                           |
|  PRACTICE 3: FIXED SEQUENTIAL PIPELINE IMPLEMENTATION                   |
|                                                                           |
|  When steps are known in advance, use a fixed sequential pipeline.       |
|  Best for: predictable, structured tasks like code reviews,               |
|  document processing, compliance checks.                                 |
|                                                                           |
|  + REAL-TIME SCENARIOS + MISTAKES + INTERVIEW Q&A + VISUALS             |
|                                                                           |
+===========================================================================+

This file shows how to implement and orchestrate a fixed pipeline.

REAL-TIME SCENARIO: Your company processes 1000 invoices daily.
Each invoice needs: Extract data -> Validate format -> Store in database.
What architecture ensures consistent processing?

INTERVIEW PREP: "How do you handle validation failure in the middle
of a multi-step pipeline?" Tests understanding of pipeline control flow.

===========================================================================
 VISUAL: FIXED PIPELINE ARCHITECTURE
===========================================================================

    +-----------------------------------------------------------------------+
    |  FIXED SEQUENTIAL PIPELINE                                           |
    |                                                                       |
    |  INPUT      STEP 1      STEP 2      STEP 3      STEP 4      OUTPUT  |
    |  ------+----------+----------+----------+----------+-------+         |
    |         |          |          |          |          |               |
    |         v          v          v          v          v               |
    |     [EXTRACT] -> [TRANSFORM] -> [VALIDATE] -> [STORE]                |
    |         |          |            |            |                       |
    |         v          v            v            v                       |
    |     Raw Text   Cleaned Data  Schema OK   Success!                   |
    |                                                                       |
    |  Each step takes PREVIOUS OUTPUT as input                            |
    |  Steps execute in PREDETERMINED order                                |
    |  Can STOP EARLY if validation fails                                  |
    |                                                                       |
    +-----------------------------------------------------------------------+

===========================================================================
 REAL-TIME SCENARIO 1: Invoice Processing Pipeline
===========================================================================

    CONTEXT:
    - Company processes 1000 invoices daily via AI pipeline
    - Fixed 4 steps: Extract -> Transform -> Validate -> Store

    HOW IT WORKS:
    Step 1: Extract text from PDF invoice
    Step 2: Transform into structured data (vendor, amount, date)
    Step 3: Validate against schema (required fields, formats)
    Step 4: Store in database

    THE RELIABILITY:
    - Every invoice goes through same 4 steps
    - If validation fails, data not stored
    - Can audit exactly what happened to each invoice

    WHY FIXED PIPELINE IS CORRECT:
    - Steps known in advance (extract, transform, validate, store)
    - Order is always the same
    - Can fail fast at validation step
    - Easy to audit, test, monitor

===========================================================================
 REAL-TIME SCENARIO 2: Code Review Pipeline
===========================================================================

    CONTEXT:
    - CI/CD pipeline reviews code before merge
    - Fixed steps: Lint -> Type Check -> Test -> Security Scan

    THE ORDER MATTERS:
    - Fast checks first (lint) - fail fast
    - Slower checks later (security scan)
    - Can't run security scan if type check fails
    - Sequential dependency

    WHAT HAPPENS:
    Step 1: Lint -> Fail (syntax error) -> STOP
    Step 2: Type Check -> (never reached)
    Step 3: Test -> (never reached)
    Step 4: Security Scan -> (never reached)

    THE BROKEN THING (if not using fixed pipeline):
    - Steps might run out of order
    - Expensive checks might run on invalid code
    - No clear checkpoint for "stop if earlier step failed"

===========================================================================
 REAL-TIME SCENARIO 3: Document Compliance Pipeline
===========================================================================

    CONTEXT:
    - Legal documents need compliance verification
    - 10 compliance rules must be checked

    FIXED PIPELINE APPROACH:
    Step 1: Check Rule 1 (data privacy)
    Step 2: Check Rule 2 (financial disclosure)
    Step 3: Check Rule 3 (liability clauses)
    ... (each rule is a step)
    Step 10: Generate compliance report

    WHY SEQUENTIAL MATTERS:
    - Each rule must be checked systematically
    - Order ensures nothing is skipped
    - Final report shows which rules passed/failed
    - Audit trail for legal review

"""

import os
import anthropic
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment
API_KEY = os.getenv("ANTHROPIC_API_KEY")

if not API_KEY:
    raise ValueError("ANTHROPIC_API_KEY not found in .env file")


# ================================================================================
# PIPELINE STEPS: Define each step in the pipeline
# ================================================================================

class PipelineStep:
    """
    Represents a single step in the pipeline.
    Has name, description, and handler function.
    """

    def __init__(self, name: str, description: str, handler):
        self.name = name
        self.description = description
        self.handler = handler

    def execute(self, input_data: dict) -> dict:
        print(f"\n   [STEP] Executing: {self.name}")
        print(f"   [STEP] Description: {self.description}")
        result = self.handler(input_data)
        print(f"   [STEP] Complete: {self.name}")
        return result


# ================================================================================
# STEP HANDLERS: Implement each step's logic
# ================================================================================

def step_1_extract_pdf(input_data: dict) -> dict:
    """
    Step 1: Extract text from PDF document.
    Input: {"pdf_path": "document.pdf"}
    Output: {"text": "extracted text content"}
    """
    pdf_path = input_data.get("pdf_path", "")

    print(f"   Extracting text from: {pdf_path}")

    # Simulate extraction
    text = f"Extracted content from {pdf_path}: Lorem ipsum dolor sit amet..."

    return {
        "step": "extract_pdf",
        "text": text,
        "word_count": len(text.split()),
        "pages": 10
    }


def step_2_transform_data(input_data: dict) -> dict:
    """
    Step 2: Transform extracted text into structured data.
    Input: {"text": "extracted text"}
    Output: {"structured_data": {...}}
    """
    text = input_data.get("text", "")

    print(f"   Transforming {len(text)} characters of text")

    # Simulate transformation
    structured_data = {
        "sections": [
            {"title": "Introduction", "content": "Section 1 content..."},
            {"title": "Main Content", "content": "Section 2 content..."},
            {"title": "Conclusion", "content": "Section 3 content..."}
        ],
        "entities": ["Person A", "Company B", "Date C"],
        "key_terms": ["compliance", "regulation", "requirement"]
    }

    return {
        "step": "transform_data",
        "structured_data": structured_data,
        "sections_found": len(structured_data["sections"])
    }


def step_3_validate_schema(input_data: dict) -> dict:
    """
    Step 3: Validate that data matches expected schema.
    Input: {"structured_data": {...}}
    Output: {"validation": "passed" or "failed", "issues": [...]}
    """
    structured_data = input_data.get("structured_data", {})

    print(f"   Validating schema for {len(structured_data.get('sections', []))} sections")

    # Simulate validation
    issues = []
    if not structured_data.get("sections"):
        issues.append("Missing sections")
    if not structured_data.get("entities"):
        issues.append("Missing entities")

    validation_status = "passed" if len(issues) == 0 else "failed"

    return {
        "step": "validate_schema",
        "validation": validation_status,
        "issues": issues,
        "valid": validation_status == "passed"
    }


def step_4_load_to_database(input_data: dict) -> dict:
    """
    Step 4: Load validated data to database.
    Input: {"structured_data": {...}}
    Output: {"load_status": "success", "record_id": "..."}
    """
    structured_data = input_data.get("structured_data", {})

    print(f"   Loading {len(structured_data.get('sections', []))} sections to database")

    # Simulate database load
    record_id = "DOC-2024-001"

    return {
        "step": "load_to_database",
        "load_status": "success",
        "record_id": record_id,
        "records_created": len(structured_data.get("sections", []))
    }


# ================================================================================
# PIPELINE DEFINITION: Assemble the steps
# ================================================================================

def create_document_pipeline():
    """
    Create the document processing pipeline.
    """
    pipeline = [
        PipelineStep(
            name="Extract PDF",
            description="Extract text content from PDF document",
            handler=step_1_extract_pdf
        ),
        PipelineStep(
            name="Transform Data",
            description="Convert raw text into structured format",
            handler=step_2_transform_data
        ),
        PipelineStep(
            name="Validate Schema",
            description="Ensure data matches expected schema",
            handler=step_3_validate_schema
        ),
        PipelineStep(
            name="Load to Database",
            description="Store validated data in database",
            handler=step_4_load_to_database
        )
    ]

    return pipeline


def run_pipeline(pipeline: list, initial_input: dict) -> dict:
    """
    Execute the pipeline with error handling.
    Handles validation failures and exceptions properly.
    """
    print("\n" + "=" * 70)
    print("PIPELINE EXECUTION")
    print("=" * 70)

    context = initial_input.copy()
    results = []

    for i, step in enumerate(pipeline):
        print(f"\n[STEP {i + 1}/{len(pipeline)}] {step.name}")

        try:
            # Execute step with previous output as input
            step_output = step.execute(context)

            # Pass output to next step
            context.update(step_output)
            results.append({
                "step": step.name,
                "status": "success",
                "output": step_output
            })

            # Check for validation failure - STOP PIPELINE
            if step_output.get("step") == "validate_schema":
                if step_output.get("validation") == "failed":
                    print("\n   [PIPELINE] Validation failed! Stopping pipeline.")
                    return {
                        "status": "failed",
                        "failed_at": step.name,
                        "issues": step_output.get("issues", []),
                        "results": results
                    }

        except Exception as e:
            print(f"\n   [ERROR] Step {step.name} failed: {e}")
            results.append({
                "step": step.name,
                "status": "failed",
                "error": str(e)
            })
            return {
                "status": "failed",
                "failed_at": step.name,
                "error": str(e),
                "results": results
            }

    print("\n" + "=" * 70)
    print("PIPELINE COMPLETE!")
    print("=" * 70)

    return {
        "status": "success",
        "results": results,
        "final_output": context
    }


def demonstrate_pipeline():
    """
    Demonstrate the fixed pipeline execution.
    """
    print("\n" + "=" * 70)
    print("FIXED SEQUENTIAL PIPELINE EXAMPLE")
    print("=" * 70)

    print("""
    +======================================================================+
    ||  DOCUMENT PROCESSING PIPELINE                                      ||
    ||                                                                      ||
    ||  PDF File --> [EXTRACT] --> [TRANSFORM] --> [VALIDATE] --> [LOAD]  ||
    ||                 |            |            |            |             ||
    ||                 v            v            v            v             ||
    ||            Raw Text     Structured    Schema      Database          ||
    ||                          Data          Check       Success!          ||
    ||                                                                      ||
    ||  Each step takes previous output as input.                          ||
    ||  Steps are fixed in advance - no adaptation.                        ||
    +======================================================================+
    """)

    # Create and run pipeline
    pipeline = create_document_pipeline()

    initial_input = {
        "pdf_path": "documents/annual_report.pdf",
        "document_type": "annual_report"
    }

    result = run_pipeline(pipeline, initial_input)

    print(f"\n   Pipeline Status: {result['status'].upper()}")
    if result["status"] == "success":
        print(f"   Final Record ID: {result['final_output'].get('record_id')}")
    else:
        print(f"   Failed at: {result.get('failed_at')}")


def show_real_time_mistakes():
    """
    Shows REAL mistakes developers make with fixed pipelines.
    """
    print("\n" + "=" * 70)
    print("REAL MISTAKES DEVELOPERS MAKE - EXPERT WARNINGS")
    print("=" * 70)

    print("""
    +======================================================================+
    ||                                                                      ||
    ||  MISTAKE #1: Not handling validation failure properly                ||
    ||  =================================================================   ||
    ||                                                                      ||
    ||  WHAT HAPPENS IN PRODUCTION:                                        ||
    ||  - Pipeline has validation step                                      ||
    ||  - Validation fails but pipeline CONTINUES                          ||
    ||  - Bad data gets stored in database                                  ||
    ||  - "But the AI returned something..."                               ||
    ||                                                                      ||
    ||  REAL CONSEQUENCE:                                                   ||
    ||  - Invoice stored with invalid vendor name                           ||
    ||  - Cannot process payment                                           ||
    ||  - Must manually fix database                                       ||
    ||  - Audit shows "validation ran, result ignored"                     ||
    ||                                                                      ||
    ||  CORRECT APPROACH:                                                   ||
    ||  - Check validation result after step                                ||
    ||  - If failed: return immediately, don't run next step              ||
    ||  - Return failure status with issues found                          ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  MISTAKE #2: Using fixed pipeline for open-ended tasks               ||
    ||  =================================================================   ||
    ||                                                                      ||
    ||  WHAT HAPPENS:                                                       ||
    ||  - Developer building investigation pipeline                          ||
    ||  - Uses "fixed" because it seems simpler                             ||
    ||  - Discovers security issue but pipeline doesn't have step for it   ||
    ||  - Must either skip the finding or force it into wrong step          ||
    ||                                                                      ||
    ||  REAL CONSEQUENCE:                                                   ||
    ||  - Security audit is incomplete                                      ||
    ||  - "We found X but couldn't investigate Y"                          ||
    ||  - Missed critical vulnerability                                      ||
    ||                                                                      ||
    ||  CORRECT APPROACH:                                                   ||
    ||  - Use DYNAMIC DECOMPOSITION for investigation                       ||
    ||  - Steps emerge based on discoveries                                 ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||                                                                      ||
    ||  MISTAKE #3: No error handling for exceptions                       ||
    ||  =================================================================   ||
    ||                                                                      ||
    ||  WHAT HAPPENS:                                                       ||
    ||  - Pipeline step throws exception                                     ||
    ||  - No try/catch handling                                             ||
    ||  - Entire pipeline crashes                                           ||
    ||  - No record of partial progress                                     ||
    ||                                                                      ||
    ||  REAL CONSEQUENCE:                                                   ||
    ||  - 1000 invoices in queue                                            ||
    ||  - Step 3 fails on invoice #5                                        ||
    ||  - Pipeline crashes, all 1000 stuck                                  ||
    ||  - Must restart from beginning, lose progress                        ||
    ||                                                                      ||
    ||  CORRECT APPROACH:                                                   ||
    ||  - Wrap each step in try/catch                                       ||
    ||  - Return failure with error details                                 ||
    ||  - Track which step failed, what was completed                      ||
    ||  - Can resume from checkpoint                                        ||
    ||                                                                      ||
    +======================================================================+
    """)


def show_interview_qa():
    """
    Shows common interview questions and expert answers.
    """
    print("\n" + "=" * 70)
    print("INTERVIEW QUESTIONS & EXPERT ANSWERS GUIDE")
    print("=" * 70)

    # Q1
    print("""
    ======================================================================
    INTERVIEW Q1: "How do you handle validation failure in the middle
                  of a multi-step pipeline?"
    ======================================================================

    EXPECTED ANSWER:
    After the validation step completes, I check the result immediately.
    If validation failed, I return from the pipeline function right away
    without executing subsequent steps. The return object includes which
    step failed, what issues were found, and the results of completed steps
    for debugging.

    RED FLAGS IN ANSWERS:
    - "Continue anyway, validation is just a warning" -> Wrong
    - "Restart from beginning" -> No checkpoint handling
    - "Ignore the failure" -> Data quality issue

    +-----------------------------------------------------------------------+
    | EXPERT TIP: Show you understand "fail fast" pattern                   |
    | "Validation exists to prevent bad data from reaching the database"    |
    +-----------------------------------------------------------------------+
    """)

    # Q2
    print("""
    ======================================================================
    INTERVIEW Q2: "Why use a fixed pipeline instead of dynamic?"
    ======================================================================

    EXPECTED ANSWER:
    Fixed pipeline when steps are known in advance and task is structured.
    The order matters - each step may depend on previous output. Predictable
    execution makes testing, auditing, and monitoring easier. You know
    exactly what will happen and can guarantee consistency.

    Examples: document processing (extract -> transform -> validate -> store),
    code review (lint -> test -> scan), compliance checks.

    +-----------------------------------------------------------------------+
    | EXPERT TIP: Give concrete use cases                                    |
    | "I use fixed pipeline for our invoice processing - 4 steps, same      |
    | order, every time. Easy to audit, test, and monitor."                |
    +-----------------------------------------------------------------------+
    """)

    # Q3
    print("""
    ======================================================================
    INTERVIEW Q3: "How do you test a fixed pipeline?"
    ======================================================================

    EXPECTED ANSWER:
    Test each step independently first, then test the full pipeline.
    For each step: unit test with various inputs including error cases.
    For the pipeline: test success path, test validation failure path,
    test exception handling. Mock dependencies (database, file system).

    +-----------------------------------------------------------------------+
    | EXPERT TIP: Mention testing both positive and negative cases          |
    | "Test what happens when validation fails at step 3"                   |
    +-----------------------------------------------------------------------+
    """)


def show_benefits():
    """
    Show benefits of fixed pipeline approach.
    """
    print("\n" + "=" * 70)
    print("BENEFITS OF FIXED PIPELINE")
    print("=" * 70)

    print("""
    +======================================================================+
    ||  BENEFIT 1: PREDICTABLE                                             ||
    ||                                                                      ||
    ||  - Steps are known and documented                                   ||
    ||  - Execution order is clear                                         ||
    ||  - Can tell stakeholders exactly what will happen                    ||
    +======================================================================+

    +======================================================================+
    ||  BENEFIT 2: DEBUGGABLE                                              ||
    ||                                                                      ||
    ||  - Easy to identify which step failed                                ||
    ||  - Can run each step independently to test                           ||
    ||  - Can add checkpoints and logging at each step                     ||
    +======================================================================+

    +======================================================================+
    ||  BENEFIT 3: MONITORABLE                                             ||
    ||                                                                      ||
    ||  - Track progress at each stage                                     ||
    ||  - Know exactly where bottlenecks are                               ||
    ||  - Measure throughput per step                                     ||
    +======================================================================+

    +======================================================================+
    ||  BENEFIT 4: CONSISTENT                                              ||
    ||                                                                      ||
    ||  - Same input --> same output every time                            ||
    ||  - Results are reproducible                                         ||
    ||  - Quality is uniform across runs                                   ||
    +======================================================================+

    +======================================================================+
    ||  BENEFIT 5: ERROR HANDLING                                           ||
    ||                                                                      ||
    ||  - Can fail fast at validation step                                  ||
    ||  - Don't load bad data to database                                   ||
    ||  - Clear error messages at each step                                ||
    +======================================================================+
    """)


def show_when_to_use():
    """
    Show when to use fixed pipeline.
    """
    print("\n" + "=" * 70)
    print("WHEN TO USE FIXED PIPELINE")
    print("=" * 70)

    use_cases = [
        ("Code Review", "Lint -> Type Check -> Test -> Security Scan"),
        ("Document Processing", "Extract -> Transform -> Validate -> Store"),
        ("Compliance Checks", "Check Rule 1 -> Rule 2 -> Rule 3 -> Report"),
        ("Data Pipeline", "Fetch -> Clean -> Transform -> Load"),
        ("Form Processing", "Parse -> Validate -> Normalize -> Store"),
        ("Report Generation", "Collect Data -> Calculate -> Format -> Export"),
    ]

    print("\n" + "-" * 60)
    print(f"{'Use Case':<25} {'Pipeline Steps':<35}")
    print("-" * 60)
    for case, steps in use_cases:
        print(f"{case:<25} {steps:<35}")


def show_visual_architecture():
    """
    Show visual architecture diagram.
    """
    print("\n" + "=" * 70)
    print("VISUAL: PIPELINE ARCHITECTURE")
    print("=" * 70)

    print("""
    +======================================================================+
    ||  FIXED SEQUENTIAL PIPELINE                                          ||
    ||                                                                      ||
    ||  INITIAL INPUT                                                       ||
    ||       |                                                              ||
    ||       v                                                              ||
    ||  +-----------+                                                       ||
    ||  |  STEP 1   | --> Output becomes input for Step 2                  ||
    ||  |  Extract  |                                                       ||
    ||  +-----------+                                                       ||
    ||       |                                                              ||
    ||       v                                                              ||
    ||  +-----------+                                                       ||
    ||  |  STEP 2   | --> Output becomes input for Step 3                  ||
    ||  | Transform |                                                       ||
    ||  +-----------+                                                       ||
    ||       |                                                              ||
    ||       v                                                              ||
    ||  +-----------+                                                       ||
    ||  |  STEP 3   | --> If VALIDATION FAILED, STOP here!                  ||
    ||  | Validate  |       Don't run Step 4                                 ||
    ||  +-----------+                                                       ||
    ||       |                                                              ||
    ||       v                                                              ||
    ||  +-----------+                                                       ||
    ||  |  STEP 4   | --> Final output                                      ||
    ||  |   Store   |                                                       ||
    ||  +-----------+                                                       ||
    ||       |                                                              ||
    ||       v                                                              ||
    ||  FINAL OUTPUT                                                        ||
    ||                                                                      ||
    +======================================================================+
    """)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("""
+===========================================================================+
|                                                                           |
|  PRACTICE 3: FIXED SEQUENTIAL PIPELINE IMPLEMENTATION                    |
|  + REAL-TIME SCENARIOS + MISTAKES + INTERVIEW Q&A + VISUALS              |
|                                                                           |
|  This program teaches:                                                   |
|  1. How to implement a fixed sequential pipeline                        |
|  2. Real production scenarios for each use case                         |
|  3. Common mistakes and how to avoid them                                |
|  4. Interview Q&A with expert answer frameworks                         |
|                                                                           |
+===========================================================================+
    """)

    demonstrate_pipeline()
    show_visual_architecture()
    show_benefits()
    show_when_to_use()
    show_real_time_mistakes()
    show_interview_qa()

    print("\n" + "=" * 70)
    print("WHAT WE HAVE LEARNT")
    print("=" * 70)
    print("""
    +======================================================================+
    ||  1. HOW TO IMPLEMENT FIXED PIPELINE:                                ||
    ||                                                                      ||
    ||  - Define PipelineStep class (name, description, handler)           ||
    ||  - Implement each step as a handler function                         ||
    ||  - Each handler takes input_data dict, returns output dict          ||
    ||  - Pipeline executes steps in order, passing output to next step      ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  2. REAL-TIME SCENARIOS:                                            ||
    ||                                                                      ||
    ||  SCENARIO 1: Invoice Processing                                      ||
    ||  - Extract -> Transform -> Validate -> Store                        ||
    ||  - 1000 invoices daily, consistent processing                       ||
    ||                                                                      ||
    ||  SCENARIO 2: Code Review Pipeline                                    ||
    ||  - Lint -> Type Check -> Test -> Security Scan                      ||
    ||  - Sequential dependency, fail fast                                  ||
    ||                                                                      ||
    ||  SCENARIO 3: Compliance Checks                                      ||
    ||  - 10 rules checked in order                                        │
    ||  - Audit trail for legal review                                     ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  3. COMMON MISTAKES (EXPERT WARNINGS):                               ||
    ||                                                                      ||
    ||  MISTAKE #1: Not handling validation failure                        ||
    ||  - Continue pipeline even when validation fails                     ||
    ||  - Bad data stored in database                                       ||
    ||  - FIX: Check result and return immediately on failure              ||
    ||                                                                      ||
    ||  MISTAKE #2: Fixed for open-ended tasks                             ||
    ||  - Cannot adapt when discoveries require new steps                  ||
    ||  - FIX: Use dynamic decomposition instead                            ||
    ||                                                                      ||
    ||  MISTAKE #3: No exception handling                                   ||
    ||  - Pipeline crashes, loses all progress                             ||
    ||  - FIX: Try/catch each step, track partial results                 ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  4. INTERVIEW TIPS:                                                 ||
    ||                                                                      ||
    ||  - Understand "fail fast" pattern for validation                     ||
    ||  - Know when to use fixed vs dynamic (known steps vs unknown)       ||
    ||  - Can explain error handling and checkpoint strategies              ||
    ||                                                                      ||
    ||  EXPECTED ANSWER STRUCTURE:                                          ||
    ||  1. What happens in the step                                         ||
    ||  2. How to handle failures                                           ||
    ||  3. Why this approach is correct                                     ||
    ||                                                                      ||
    +======================================================================+

    +======================================================================+
    ||  5. KEY RULES TO MEMORIZE:                                          ||
    ||                                                                      ||
    ||  RULE #1: Check validation result after validation step              ||
    ||  RULE #2: Return immediately on failure (fail fast)                  ||
    ||  RULE #3: Wrap steps in try/catch for exception handling            ||
    ||  RULE #4: Return partial results when pipeline fails                ||
    ||                                                                      ||
    +======================================================================+

    Next: practice_04_dynamic_decomposition.py shows when and how
    to use dynamic decomposition for open-ended investigation!
    """)


"""
+===========================================================================+
|                                                                           |
|  KEY CONCEPTS FROM THIS FILE:                                           |
|                                                                           |
|  IMPLEMENTATION:                                                         |
|  - PipelineStep class with name, description, handler                   |
|  - Each step handler takes input_data, returns output_data              |
|  - Pipeline executes in order, passing output to next step               |
|                                                                           |
|  ERROR HANDLING:                                                         |
|  - Check validation result after validation step                         |
|  - Return immediately on failure (don't continue)                       |
|  - Wrap each step in try/catch                                          |
|  - Track partial results for debugging                                   |
|                                                                           |
|  USE CASES:                                                              |
|  - Document processing: extract -> transform -> validate -> store        |
|  - Code review: lint -> type check -> test -> scan                       |
|  - Compliance: rule 1 -> rule 2 -> ... -> report                        |
|                                                                           |
|  EXAM TIPS:                                                              |
|  - "Fail fast" at validation step                                        |
|  - Don't load bad data to database                                      |
|  - Track partial results for debugging                                   |
|                                                                           |
|  INTERVIEW PREP:                                                        |
|  - "How do you handle validation failure?"                              |
|  - "Why use fixed over dynamic?"                                         |
|  - "How do you test a pipeline?"                                         |
|                                                                           |
+===========================================================================+
"""