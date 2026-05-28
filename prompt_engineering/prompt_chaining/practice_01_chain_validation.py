"""
PROMPT CHAINING AND VALIDATION-RETRY LOOPS - Practice File 01
=============================================================

This file teaches how to:
1. Create multi-step prompt sequences
2. Validate output between steps
3. Implement retry logic for failed validations
4. Handle errors and recover gracefully
5. Manage state across chain steps
6. Define chain termination conditions
7. Handle partial results
8. Optimize efficiency in chains

REAL-WORLD SCENARIO:
You are building a document processing pipeline that:
1. Extracts text from uploaded documents
2. Identifies the document type
3. Parses relevant information based on type
4. Validates extracted data
5. Generates a summary report
"""

import os
import time
import json
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from dotenv import load_dotenv
from anthropic import Anthropic

# ============================================================================
# SECTION 1: SETUP AND CONFIGURATION
# ============================================================================

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not found in .env file")

client = Anthropic()

# ============================================================================
# SECTION 2: CHAIN STATE MANAGEMENT
# ============================================================================

class ChainStatus(Enum):
    """Status of a chain execution step."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    SKIPPED = "skipped"


@dataclass
class StepResult:
    """Result of a single chain step execution."""
    step_name: str
    status: ChainStatus
    output: Optional[Any] = None
    error: Optional[str] = None
    retry_count: int = 0
    execution_time_ms: float = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChainContext:
    """
    Maintains state across all steps in a prompt chain.
    Each step can read from and write to this context.
    """
    original_input: str
    steps: List[StepResult] = field(default_factory=list)
    shared_data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_step(self, result: StepResult):
        """Add a completed step to the chain."""
        self.steps.append(result)

    def get_step_output(self, step_name: str) -> Optional[Any]:
        """Retrieve output from a specific step."""
        for step in reversed(self.steps):
            if step.step_name == step_name and step.status == ChainStatus.COMPLETED:
                return step.output
        return None

    def has_errors(self) -> bool:
        """Check if any steps have failed."""
        return any(s.status == ChainStatus.FAILED for s in self.steps)


# ============================================================================
# SECTION 3: VALIDATION FUNCTIONS
# ============================================================================

class ValidationError(Exception):
    """Raised when output validation fails."""
    pass


def validate_extracted_text(text: str) -> bool:
    """
    Validate that extracted text meets minimum requirements.

    Args:
        text: Extracted text to validate

    Returns:
        True if valid, raises ValidationError otherwise
    """
    if not text or len(text.strip()) == 0:
        raise ValidationError("Extracted text is empty")

    if len(text.strip()) < 50:
        raise ValidationError(
            f"Extracted text too short ({len(text)} chars). "
            "May indicate extraction failure."
        )

    # Check for common corruption patterns
    if text.count('\x00') > 0:
        raise ValidationError("Text contains null bytes - possible encoding error")

    # Check for reasonable character distribution
    alpha_ratio = sum(c.isalpha() for c in text) / max(len(text), 1)
    if alpha_ratio < 0.3:
        raise ValidationError(
            f"Text has too few alphabetic characters ({alpha_ratio:.1%}). "
            "May be corrupted or binary data."
        )

    return True


def validate_document_type(doc_type: str, allowed_types: List[str]) -> bool:
    """
    Validate detected document type against allowed types.

    Args:
        doc_type: Detected document type
        allowed_types: List of acceptable document types

    Returns:
        True if valid, raises ValidationError otherwise
    """
    doc_type_lower = doc_type.lower().strip()

    if doc_type_lower not in [t.lower() for t in allowed_types]:
        raise ValidationError(
            f"Document type '{doc_type}' not in allowed types: {allowed_types}"
        )

    return True


def validate_parsed_data(data: Dict[str, Any], required_fields: List[str]) -> bool:
    """
    Validate parsed data contains required fields.

    Args:
        data: Parsed data dictionary
        required_fields: List of required field names

    Returns:
        True if valid, raises ValidationError otherwise
    """
    missing = [f for f in required_fields if f not in data or data[f] is None]

    if missing:
        raise ValidationError(f"Missing required fields: {missing}")

    # Type-specific validations
    if 'amount' in data and isinstance(data['amount'], (int, float)):
        if data['amount'] < 0:
            raise ValidationError("Amount cannot be negative")

    if 'date' in data and data['date']:
        # Basic date format validation
        if not isinstance(data['date'], str):
            raise ValidationError("Date must be a string")

    return True


# ============================================================================
# SECTION 4: CHAIN STEP DEFINITIONS
# ============================================================================

@dataclass
class ChainStep:
    """
    Definition of a single step in a prompt chain.
    """
    name: str
    prompt_template: str
    validation_fn: Optional[Callable] = None
    max_retries: int = 3
    retry_delay_seconds: float = 1.0
    timeout_seconds: float = 30.0
    required: bool = True

    def execute(self, client: Anthropic, context: ChainContext) -> StepResult:
        """
        Execute this chain step with retry logic.

        Args:
            client: Anthropic client instance
            context: Chain context with shared state

        Returns:
            StepResult with execution outcome
        """
        start_time = time.time()
        step_context = self._build_context(context)

        for attempt in range(self.max_retries + 1):
            try:
                # Format the prompt with current context
                formatted_prompt = self.prompt_template.format(**step_context)

                # Execute the step
                response = client.messages.create(
                    model="claude-haiku-4-5-20250601",
                    max_tokens=1024,
                    system=self._get_system_prompt(),
                    messages=[
                        {"role": "user", "content": formatted_prompt}
                    ]
                )

                output = response.content[0].text.strip()

                # Validate output if validator provided
                if self.validation_fn:
                    self.validation_fn(output)

                # Success - return result
                return StepResult(
                    step_name=self.name,
                    status=ChainStatus.COMPLETED,
                    output=output,
                    retry_count=attempt,
                    execution_time_ms=(time.time() - start_time) * 1000
                )

            except ValidationError as e:
                # Validation failed - retry if attempts remain
                if attempt < self.max_retries:
                    context.errors.append(f"{self.name}: {str(e)} - Retrying...")
                    time.sleep(self.retry_delay_seconds * (attempt + 1))
                else:
                    # All retries exhausted
                    return StepResult(
                        step_name=self.name,
                        status=ChainStatus.FAILED,
                        error=str(e),
                        retry_count=attempt,
                        execution_time_ms=(time.time() - start_time) * 1000
                    )

            except Exception as e:
                # Unexpected error
                return StepResult(
                    step_name=self.name,
                    status=ChainStatus.FAILED,
                    error=f"Unexpected error: {str(e)}",
                    retry_count=attempt,
                    execution_time_ms=(time.time() - start_time) * 1000
                )

        # Should not reach here, but safety return
        return StepResult(
            step_name=self.name,
            status=ChainStatus.FAILED,
            error="Max retries exceeded",
            retry_count=self.max_retries
        )

    def _build_context(self, context: ChainContext) -> Dict[str, Any]:
        """Build variable context for prompt formatting."""
        return {
            'original_input': context.original_input,
            'shared_data': context.shared_data,
            **context.shared_data  # Flatten shared data for easy access
        }

    def _get_system_prompt(self) -> str:
        """Override in subclasses for step-specific system prompts."""
        return "You are a helpful assistant that follows instructions precisely."


# ============================================================================
# SECTION 5: DOCUMENT PROCESSING CHAIN EXAMPLE
# ============================================================================

class DocumentExtractionStep(ChainStep):
    """Step 1: Extract text from document."""

    def __init__(self):
        super().__init__(
            name="text_extraction",
            prompt_template="Extract all text content from the following document. "
                           "Preserve paragraphs and formatting as much as possible.\n\n"
                           "Document:\n{original_input}",
            validation_fn=self._validate,
            max_retries=2
        )

    def _validate(self, output: str):
        validate_extracted_text(output)


class DocumentClassificationStep(ChainStep):
    """Step 2: Classify document type."""

    def __init__(self):
        super().__init__(
            name="document_classification",
            prompt_template="Based on the following text, determine the document type. "
                           "Choose from: invoice, contract, report, letter, form, other\n\n"
                           "Text:\n{extracted_text}\n\n"
                           "Respond with only the document type, nothing else.",
            validation_fn=self._validate,
            max_retries=3
        )

    def _validate(self, output: str):
        allowed_types = ['invoice', 'contract', 'report', 'letter', 'form', 'other']
        validate_document_type(output, allowed_types)

    def _build_context(self, context: ChainContext) -> Dict[str, Any]:
        """Include previous step's output."""
        extracted_text = context.get_step_output("text_extraction") or ""
        return {
            'original_input': context.original_input,
            'extracted_text': extracted_text[:5000]  # Limit to prevent token overflow
        }


class DataParsingStep(ChainStep):
    """Step 3: Parse data based on document type."""

    def __init__(self, doc_type: str):
        self.doc_type = doc_type
        super().__init__(
            name=f"data_parsing_{doc_type}",
            prompt_template=self._get_template(),
            validation_fn=self._validate,
            max_retries=3
        )

    def _get_template(self) -> str:
        templates = {
            'invoice': "Extract from this invoice: vendor name, invoice number, date, "
                      "line items (description, quantity, unit price, total), total amount. "
                      "Format as JSON.\n\nInvoice:\n{extracted_text}",
            'contract': "Extract from this contract: parties involved, contract date, "
                       "effective date, key terms, termination clause. "
                       "Format as JSON.\n\nContract:\n{extracted_text}",
            'report': "Extract from this report: title, author, date, main sections, "
                      "key findings, conclusions. Format as JSON.\n\nReport:\n{extracted_text}",
            'other': "Extract all structured information from this document. "
                     "Identify headers, key-value pairs, and important facts. "
                     "Format as JSON.\n\nDocument:\n{extracted_text}"
        }
        return templates.get(self.doc_type, templates['other'])

    def _validate(self, output: str):
        # Try to parse as JSON
        try:
            data = json.loads(output)
            required = ['extracted_data']  # Minimal requirement
        except json.JSONDecodeError:
            raise ValidationError("Output is not valid JSON")


class SummaryGenerationStep(ChainStep):
    """Step 4: Generate summary report."""

    def __init__(self):
        super().__init__(
            name="summary_generation",
            prompt_template="Create a summary of the processed document. "
                           "Include: document type, key information, "
                           "any warnings or issues encountered.\n\n"
                           "Extracted Data:\n{parsed_data}\n\n"
                           "Processing Log:\n{error_log}",
            max_retries=2
        )

    def _build_context(self, context: ChainContext) -> Dict[str, Any]:
        parsed_data = context.get_step_output("data_parsing_invoice") or \
                     context.get_step_output("data_parsing_contract") or \
                     context.get_step_output("data_parsing_report") or \
                     context.get_step_output("data_parsing_other") or "No data parsed"
        return {
            'parsed_data': parsed_data,
            'error_log': '\n'.join(context.errors) if context.errors else "No errors"
        }


# ============================================================================
# SECTION 6: CHAIN EXECUTOR
# ============================================================================

class PromptChainExecutor:
    """
    Executes a chain of prompt steps with validation and retry logic.
    """

    def __init__(self, client: Anthropic, max_total_time: float = 120.0):
        self.client = client
        self.max_total_time = max_total_time

    def execute(self, steps: List[ChainStep], initial_input: str) -> ChainContext:
        """
        Execute a chain of steps.

        Args:
            steps: List of ChainStep objects to execute in order
            initial_input: The initial input to the chain

        Returns:
            ChainContext containing all results and state
        """
        context = ChainContext(original_input=initial_input)
        start_time = time.time()

        for step in steps:
            # Check timeout
            elapsed = time.time() - start_time
            if elapsed > self.max_total_time:
                context.errors.append(
                    f"Chain timeout after {elapsed:.1f}s. "
                    f"Stopped before step: {step.name}"
                )
                break

            # Execute step
            print(f"  Executing step: {step.name}...")
            result = step.execute(self.client, context)

            # Store result
            context.add_step(result)

            # Handle non-required step failure
            if result.status == ChainStatus.FAILED and not step.required:
                print(f"    Non-critical step failed: {result.error}")
                continue

            # Handle required step failure
            if result.status == ChainStatus.FAILED:
                print(f"    Step failed: {result.error}")
                # Continue to allow partial results

            # Store output in shared data for next steps
            if result.output:
                context.shared_data[step.name] = result.output

        return context


# ============================================================================
# SECTION 7: PARTIAL RESULT HANDLING
# ============================================================================

def handle_partial_results(context: ChainContext) -> Dict[str, Any]:
    """
    Extract results even when chain fails partially.

    Args:
        context: Chain context with partial results

    Returns:
        Dictionary with available results and failure info
    """
    result = {
        'complete': True,
        'steps_completed': [],
        'steps_failed': [],
        'data': {},
        'errors': []
    }

    for step in context.steps:
        if step.status == ChainStatus.COMPLETED:
            result['steps_completed'].append(step.step_name)
            result['data'][step.step_name] = step.output
        else:
            result['steps_failed'].append(step.step_name)
            if step.error:
                result['errors'].append(f"{step.step_name}: {step.error}")

    result['complete'] = len(result['steps_failed']) == 0

    return result


# ============================================================================
# SECTION 8: EFFICIENCY OPTIMIZATION
# ============================================================================

def optimize_chain_efficiency(steps: List[ChainStep]) -> List[ChainStep]:
    """
    Optimize chain by identifying opportunities for:
    - Parallel execution of independent steps
    - Early termination when conditions are met
    - Caching repeated computations
    """
    # Identify parallelizable steps
    # (In this example, steps are sequential by design,
    # but the function demonstrates the concept)

    optimizations = []

    # Check for steps that don't depend on previous output
    for i, step in enumerate(steps):
        if i > 0:
            prev_step = steps[i - 1]
            # If previous step output is not referenced, could run parallel
            if '{' not in step.prompt_template or \
               prev_step.name not in step.prompt_template:
                optimizations.append({
                    'step': step.name,
                    'optimization': 'may_parallelize_with_previous'
                })

    return steps  # Return unchanged in this implementation


# ============================================================================
# SECTION 9: DEMONSTRATION
# ============================================================================

def demonstrate_prompt_chaining():
    """Demonstrate prompt chaining patterns."""

    print("=" * 60)
    print("PROMPT CHAINING - PRACTICE 01: CHAIN VALIDATION")
    print("=" * 60)

    # Create chain executor
    executor = PromptChainExecutor(client)

    # Define a simple chain for demonstration
    print("\n[DEMO] Creating document processing chain...")
    steps = [
        DocumentExtractionStep(),
        DocumentClassificationStep(),
    ]

    print(f"Chain has {len(steps)} steps")
    for i, step in enumerate(steps):
        print(f"  Step {i+1}: {step.name}")
        print(f"    Max retries: {step.max_retries}")
        print(f"    Required: {step.required}")

    # Demonstrate chain execution with mock data
    print("\n[DEMO] Chain execution would process:")
    print("  1. Extract text from document")
    print("  2. Validate extracted text quality")
    print("  3. Classify document type")
    print("  4. Parse data based on type")
    print("  5. Generate summary report")

    # Show partial result handling
    print("\n[DEMO] Handling partial results...")
    partial_context = ChainContext(
        original_input="Sample invoice text...",
        steps=[
            StepResult("text_extraction", ChainStatus.COMPLETED,
                      "Extracted text here..."),
            StepResult("classification", ChainStatus.FAILED,
                      error="Could not determine document type")
        ]
    )

    results = handle_partial_results(partial_context)
    print(f"  Steps completed: {results['steps_completed']}")
    print(f"  Steps failed: {results['steps_failed']}")
    print(f"  Chain complete: {results['complete']}")

    print("\n" + "=" * 60)
    print("WHAT WE HAVE LEARNT:")
    print("=" * 60)
    print("""
1. CHAIN STRUCTURE
   - Define steps as reusable ChainStep objects
   - Each step has: name, prompt, validation, retry config
   - Steps share state through ChainContext
   - Order matters for dependent steps

2. VALIDATION BETWEEN STEPS
   - Each step validates output before passing to next
   - Validation failures trigger retry logic
   - Clear error messages help debugging
   - Validation functions are reusable

3. RETRY LOGIC
   - Configure max_retries per step
   - Implement exponential backoff
   - Track retry count for analysis
   - Distinguish between validation and system errors

4. STATE MANAGEMENT
   - ChainContext holds all shared state
   - Steps read previous outputs from context
   - Shared data prevents redundant calls
   - Errors accumulated for final report

5. PARTIAL RESULT HANDLING
   - Continue even when optional steps fail
   - Provide best-effort results
   - Track which steps succeeded/failed
   - Never lose successfully extracted data

6. EFFICIENCY CONSIDERATIONS
   - Identify independent steps for parallel execution
   - Implement timeout per step and total chain
   - Cache repeated computations
   - Skip unnecessary steps when possible

7. ERROR RECOVERY
   - Catch specific exception types
   - Provide context for debugging
   - Allow graceful degradation
   - Generate useful error summaries
""")


if __name__ == "__main__":
    demonstrate_prompt_chaining()


# ============================================================================
# INTERVIEW Q&A PREP
# ============================================================================
"""
Q: How do you prevent infinite loops in prompt chains?
A: Implement loop detection by tracking visited states, set maximum
   iteration counts, define clear termination conditions, and
   monitor for repetitive output patterns.

Q: When should you continue a chain vs abort?
A: Continue for non-critical steps with graceful degradation.
   Abort when required steps fail or timeout is reached.
   Always preserve partial results.

Q: How do you handle dependencies between chain steps?
A: Use the ChainContext to pass outputs between steps.
   Validate inputs at each step. Build context gradually
   as steps complete.

Q: What is the difference between validation and error handling?
A: Validation checks if output meets requirements (retry-able).
   Error handling manages unexpected exceptions (fallback logic).
"""