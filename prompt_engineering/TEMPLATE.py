"""
PROMPT ENGINEERING TEMPLATE - Comprehensive Reference
=====================================================

This template provides a complete reference for all prompt engineering
patterns covered in Domain 4. Use it as a starting point for your
projects and customize as needed.

KEY PATTERNS COVERED:
1. System Prompts with Explicit Criteria
2. Structured Output with Tool Use
3. Prompt Chaining and Validation-Retry Loops
4. Few-Shot Prompting
5. Batch Processing and Prompt Optimization
6. Multi-Instance Review and Output Validation
"""

import os
import json
import time
from typing import List, Dict, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import Counter, defaultdict
from dotenv import load_dotenv

# ============================================================================
# SECTION 1: IMPORTS AND CONFIGURATION
# ============================================================================

load_dotenv()

# Verify API key is available
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not found in .env file")

# Model configuration
MODEL_NAME = "claude-haiku-4-5-20250601"
MAX_TOKENS = 2048

# ============================================================================
# SECTION 2: SYSTEM PROMPT BUILDER
# ============================================================================

class SystemPromptBuilder:
    """
    Builder class for creating comprehensive system prompts.

    Usage:
        builder = SystemPromptBuilder()
        prompt = builder.set_role("You are a code reviewer...")
                .set_instructions("Review code for...")
                .set_output_format("Output JSON with...")
                .set_constraints("Never...")
                .set_examples("Example: ...")
                .build()
    """

    def __init__(self):
        self.parts = []

    def set_role(self, role: str) -> 'SystemPromptBuilder':
        """Set the role definition."""
        self.parts.append(f"ROLE:\n{role}")
        return self

    def set_instructions(self, instructions: str) -> 'SystemPromptBuilder':
        """Set task instructions."""
        self.parts.append(f"INSTRUCTIONS:\n{instructions}")
        return self

    def set_output_format(self, format_spec: str) -> 'SystemPromptBuilder':
        """Set expected output format."""
        self.parts.append(f"OUTPUT FORMAT:\n{format_spec}")
        return self

    def set_constraints(self, constraints: str) -> 'SystemPromptBuilder':
        """Set what NOT to do."""
        self.parts.append(f"CONSTRAINTS:\n{constraints}")
        return self

    def set_quality_criteria(self, criteria: str) -> 'SystemPromptBuilder':
        """Set quality evaluation criteria."""
        self.parts.append(f"QUALITY CRITERIA:\n{criteria}")
        return self

    def add_section(self, title: str, content: str) -> 'SystemPromptBuilder':
        """Add a custom section."""
        self.parts.append(f"{title.upper()}:\n{content}")
        return self

    def build(self) -> str:
        """Build the final system prompt."""
        return "\n\n".join(self.parts)


# ============================================================================
# SECTION 3: STRUCTURED OUTPUT SCHEMA
# ============================================================================

@dataclass
class OutputSchema:
    """Schema for structured output definition."""

    name: str
    description: str
    fields: Dict[str, Dict[str, Any]]

    def to_prompt_text(self) -> str:
        """Convert schema to prompt-friendly text."""
        lines = [f"{self.name}:"]
        lines.append(f"  Description: {self.description}")
        lines.append("  Fields:")

        for field_name, field_spec in self.fields.items():
            field_type = field_spec.get('type', 'string')
            required = field_spec.get('required', False)
            description = field_spec.get('description', '')
            enum_values = field_spec.get('enum', [])

            required_marker = "[REQUIRED]" if required else "[OPTIONAL]"
            lines.append(f"    - {field_name} ({field_type}) {required_marker}")
            if description:
                lines.append(f"      Description: {description}")
            if enum_values:
                lines.append(f"      Allowed values: {', '.join(enum_values)}")

        return "\n".join(lines)

    def validate(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate data against schema."""
        errors = []

        for field_name, field_spec in self.fields.items():
            # Check required fields
            if field_spec.get('required', False) and field_name not in data:
                errors.append(f"Missing required field: {field_name}")

            # Check type
            if field_name in data:
                value = data[field_name]
                expected_type = field_spec.get('type', 'string')

                type_valid = self._check_type(value, expected_type)
                if not type_valid:
                    errors.append(
                        f"Field '{field_name}' should be {expected_type}, "
                        f"got {type(value).__name__}"
                    )

                # Check enum values
                enum_values = field_spec.get('enum', [])
                if enum_values and value not in enum_values:
                    errors.append(
                        f"Field '{field_name}' must be one of: {enum_values}"
                    )

        return len(errors) == 0, errors

    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Check if value matches expected type."""
        if expected_type == 'string':
            return isinstance(value, str)
        elif expected_type == 'integer':
            return isinstance(value, int)
        elif expected_type == 'number':
            return isinstance(value, (int, float))
        elif expected_type == 'boolean':
            return isinstance(value, bool)
        elif expected_type == 'array':
            return isinstance(value, list)
        elif expected_type == 'object':
            return isinstance(value, dict)
        return True


# ============================================================================
# SECTION 4: CHAIN STEP DEFINITION
# ============================================================================

class ChainStepStatus(Enum):
    """Status of a chain step."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ChainStepResult:
    """Result from executing a chain step."""
    step_name: str
    status: ChainStepStatus
    output: Optional[Any] = None
    error: Optional[str] = None
    retry_count: int = 0
    execution_time_ms: float = 0


class ChainStep:
    """A single step in a prompt chain."""

    def __init__(self,
                 name: str,
                 prompt_template: str,
                 validation_fn: Optional[Callable] = None,
                 max_retries: int = 3,
                 required: bool = True):
        self.name = name
        self.prompt_template = prompt_template
        self.validation_fn = validation_fn
        self.max_retries = max_retries
        self.required = required

    def execute(self, context: Dict[str, Any], execute_fn: Callable) -> ChainStepResult:
        """Execute this step with retry logic."""
        start_time = time.time()

        for attempt in range(self.max_retries + 1):
            try:
                # Format prompt with context
                prompt = self.prompt_template.format(**context)

                # Execute the prompt
                output = execute_fn(prompt)

                # Validate output
                if self.validation_fn:
                    self.validation_fn(output)

                return ChainStepResult(
                    step_name=self.name,
                    status=ChainStepStatus.COMPLETED,
                    output=output,
                    retry_count=attempt,
                    execution_time_ms=(time.time() - start_time) * 1000
                )

            except Exception as e:
                if attempt < self.max_retries:
                    continue
                return ChainStepResult(
                    step_name=self.name,
                    status=ChainStepStatus.FAILED,
                    error=str(e),
                    retry_count=attempt,
                    execution_time_ms=(time.time() - start_time) * 1000
                )

        return ChainStepResult(
            step_name=self.name,
            status=ChainStepStatus.FAILED,
            error="Max retries exceeded",
            retry_count=self.max_retries,
            execution_time_ms=(time.time() - start_time) * 1000
        )


# ============================================================================
# SECTION 5: FEW-SHOT EXAMPLE MANAGER
# ============================================================================

@dataclass
class FewShotExample:
    """A single few-shot example."""
    input_text: str
    output_text: str
    reasoning: Optional[str] = None
    category: Optional[str] = None


class FewShotManager:
    """Manages few-shot examples for prompting."""

    def __init__(self):
        self.examples: List[FewShotExample] = []

    def add_example(self,
                   input_text: str,
                   output_text: str,
                   reasoning: Optional[str] = None,
                   category: Optional[str] = None):
        """Add an example."""
        self.examples.append(FewShotExample(
            input_text=input_text,
            output_text=output_text,
            reasoning=reasoning,
            category=category
        ))

    def get_balanced_subset(self, n: int) -> List[FewShotExample]:
        """Get n examples balanced across categories."""
        if not self.examples:
            return []

        categories = set(e.category for e in self.examples if e.category)
        if not categories:
            return self.examples[:n]

        per_category = max(1, n // len(categories))
        selected = []

        for cat in categories:
            cat_examples = [e for e in self.examples if e.category == cat]
            selected.extend(cat_examples[:per_category])

        return selected[:n]

    def format_for_prompt(self,
                         examples: List[FewShotExample],
                         include_reasoning: bool = False) -> str:
        """Format examples for inclusion in prompt."""
        lines = []

        for ex in examples:
            lines.append(f"Input: {ex.input_text}")
            if include_reasoning and ex.reasoning:
                lines.append(f"Thinking: {ex.reasoning}")
            lines.append(f"Output: {ex.output_text}")
            lines.append("")

        return "\n".join(lines)


# ============================================================================
# SECTION 6: BATCH PROCESSOR
# ============================================================================

@dataclass
class BatchConfig:
    """Configuration for batch processing."""
    max_batch_size: int = 10
    max_workers: int = 3
    rate_limit_per_minute: int = 50
    retry_attempts: int = 3


@dataclass
class BatchResult:
    """Result of processing a batch."""
    successful: int = 0
    failed: int = 0
    results: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)


def chunk_items(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split items into chunks."""
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


# ============================================================================
# SECTION 7: MULTI-INSTANCE VALIDATOR
# ============================================================================

@dataclass
class InstanceResult:
    """Result from a single instance."""
    instance_id: str
    output: Any
    confidence: float
    processing_time_ms: float


class MultiInstanceValidator:
    """Validates outputs using multiple instances."""

    def __init__(self, num_instances: int = 3):
        self.num_instances = num_instances

    def validate(self,
                outputs: List[InstanceResult],
                thresholds: Dict[str, float]) -> Dict[str, Any]:
        """Validate multiple instance outputs."""

        if not outputs:
            return {'valid': False, 'error': 'No outputs provided'}

        # Calculate agreement
        output_values = [o.output for o in outputs]
        counter = Counter(output_values)
        most_common = counter.most_common(1)[0]
        agreement = most_common[1] / len(outputs)

        # Calculate confidence
        avg_confidence = sum(o.confidence for o in outputs) / len(outputs)

        # Apply thresholds
        valid = True
        reasons = []

        if agreement < thresholds.get('min_agreement', 0.66):
            valid = False
            reasons.append(f"Agreement {agreement:.2f} below threshold")

        if avg_confidence < thresholds.get('min_confidence', 0.7):
            valid = False
            reasons.append(f"Confidence {avg_confidence:.2f} below threshold")

        return {
            'valid': valid,
            'final_output': most_common[0],
            'agreement': agreement,
            'confidence': avg_confidence,
            'reasons': reasons,
            'all_outputs': output_values
        }


# ============================================================================
# SECTION 8: EXAMPLE USAGE
# ============================================================================

def demonstrate_template():
    """Demonstrate all template components."""

    print("=" * 60)
    print("PROMPT ENGINEERING TEMPLATE - DEMONSTRATION")
    print("=" * 60)

    # 1. System Prompt Builder
    print("\n1. System Prompt Builder:")
    builder = SystemPromptBuilder()
    prompt = (
        builder
        .set_role("You are a code reviewer.")
        .set_instructions("Review code for bugs and security issues.")
        .set_output_format("Output JSON with findings.")
        .set_constraints("Do not modify code, only report issues.")
        .build()
    )
    print(f"   Created prompt ({len(prompt)} chars)")

    # 2. Output Schema
    print("\n2. Output Schema:")
    schema = OutputSchema(
        name="code_review",
        description="Code review findings",
        fields={
            "severity": {
                "type": "string",
                "required": True,
                "enum": ["HIGH", "MEDIUM", "LOW"]
            },
            "issue": {
                "type": "string",
                "required": True
            },
            "line_number": {
                "type": "integer",
                "required": False
            }
        }
    )
    print(schema.to_prompt_text()[:200] + "...")

    # 3. Chain Step
    print("\n3. Chain Step:")
    step = ChainStep(
        name="extract_code",
        prompt_template="Extract code from: {input_text}",
        max_retries=3
    )
    print(f"   Created step: {step.name}")

    # 4. Few-Shot Manager
    print("\n4. Few-Shot Manager:")
    manager = FewShotManager()
    manager.add_example("Great product!", "positive", category="sentiment")
    manager.add_example("Terrible experience", "negative", category="sentiment")
    print(f"   Added {len(manager.examples)} examples")

    # 5. Batch Processing
    print("\n5. Batch Processing:")
    items = list(range(100))
    chunks = chunk_items(items, 10)
    print(f"   100 items -> {len(chunks)} chunks")

    # 6. Multi-Instance Validator
    print("\n6. Multi-Instance Validator:")
    validator = MultiInstanceValidator(num_instances=3)
    print(f"   Initialized with {validator.num_instances} instances")

    print("\n" + "=" * 60)
    print("TEMPLATE FEATURES:")
    print("=" * 60)
    print("""
- SystemPromptBuilder: Fluent API for building system prompts
- OutputSchema: Define and validate structured outputs
- ChainStep: Reusable step with retry logic
- FewShotManager: Manage and select few-shot examples
- BatchConfig/BatchResult: Batch processing configuration
- MultiInstanceValidator: Multi-instance output validation

Each component can be customized and combined as needed.
""")


if __name__ == "__main__":
    demonstrate_template()


# ============================================================================
# QUICK REFERENCE
# ============================================================================

"""
PATTERN QUICK REFERENCE:

SYSTEM PROMPT STRUCTURE:
------------------------
1. Role definition - Who is the AI?
2. Task instructions - What to do?
3. Output format - How to respond?
4. Constraints - What NOT to do?
5. Examples (optional) - Show expected behavior

STRUCTURED OUTPUT:
------------------
- Define JSON schema explicitly
- Use required vs optional fields
- Include enum for controlled values
- Validate output before use

PROMPT CHAINING:
----------------
- Define each step as ChainStep
- Validate output between steps
- Implement retry with backoff
- Handle partial results gracefully

FEW-SHOT PROMPTING:
-------------------
- 3-5 examples for classification
- Cover all output categories
- Include reasoning for complex tasks
- Quality > quantity

BATCH PROCESSING:
----------------
- Chunk items based on token limit
- Use parallel workers (3-5)
- Implement rate limiting
- Track progress and errors

MULTI-INSTANCE:
---------------
- Run 3 instances for critical tasks
- Use majority vote for consensus
- Set quality thresholds
- Flag low-agreement for review
"""