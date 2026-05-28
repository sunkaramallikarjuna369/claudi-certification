"""
DOMAIN 4: PROMPT ENGINEERING & STRUCTURED OUTPUT (20%)
=======================================================

This domain covers six core subtopics essential for building robust
LLM-powered applications:

1. SYSTEM PROMPTS WITH EXPLICIT CRITERIA (4.1)
   - Crafting clear role definitions
   - Specifying output format requirements
   - Defining evaluation criteria
   - Setting constraints and boundaries

2. STRUCTURED OUTPUT WITH TOOL USE (4.2)
   - JSON schema definitions
   - Type specifications and validation
   - Tool output formatting patterns
   - Nested object structures

3. PROMPT CHAINING AND VALIDATION-RETRY LOOPS (4.3)
   - Multi-step prompt sequences
   - Output validation between steps
   - Retry logic for failed validations
   - Error recovery strategies

4. FEW-SHOT PROMPTING (4.4)
   - Example selection and formatting
   - Positive vs negative examples
   - Chain-of-thought demonstrations
   - Optimal example count

5. BATCH PROCESSING AND PROMPT OPTIMIZATION (4.5)
   - Batch request patterns
   - Parallel processing strategies
   - Token and cost optimization
   - Rate limiting handling

6. MULTI-INSTANCE REVIEW AND OUTPUT VALIDATION (4.6)
   - Parallel instance processing
   - Cross-instance validation
   - Consensus-based verification
   - Output reconciliation

KEY CONCEPTS:
-------------
- System prompts define the "personality" and capabilities of the LLM
- Structured outputs enable reliable integration with other systems
- Validation and retry loops ensure output quality
- Few-shot examples teach patterns without explicit instruction
- Batch processing improves efficiency and throughput
- Multi-instance review catches errors through redundancy

INTERVIEW QUESTIONS:
--------------------
Q: How do you prevent LLM outputs from being cut off?
A: Use explicit format markers (e.g., "Output must end with </output>")
   and validate output completeness before processing.

Q: When should you prefer few-shot over zero-shot prompting?
A: When the task requires specific output format or nuanced reasoning
   that is difficult to describe in instructions alone.

Q: What is the biggest mistake in system prompt design?
A: Mixing role definition with task instructions - separate these concerns
   for clearer, more maintainable prompts.

Q: How do you handle API rate limits in batch processing?
A: Implement exponential backoff with jitter, track remaining quota,
   and use async processing to maximize throughput within limits.

GETTING STARTED:
----------------
1. Start with system_prompts/ to understand role definition
2. Move to structured_output/ for reliable data extraction
3. Learn prompt_chaining/ for complex workflows
4. Practice few_shot_prompting/ for pattern learning
5. Optimize with batch_processing/ for scale
6. Implement multi_instance_review/ for quality assurance

Each subdirectory contains:
- practice_01_*.py: Main practice file with examples
- Conceptual explanations and real-world scenarios
- Common mistakes and how to avoid them
- Interview preparation questions
- "What We Have Learnt" summary sections
"""

# Quick reference for model configuration
MODEL_NAME = "claude-haiku-4-5-20250601"

# Required environment variable
ENV_FILE = ".env"  # Must contain ANTHROPIC_API_KEY

# Common patterns used across this domain
COMMON_PATTERNS = {
    "system_prompt": "Define role -> Define format -> Define constraints",
    "structured_output": "Define schema -> Validate response -> Parse output",
    "prompt_chaining": "Step 1 -> Validate -> Step 2 -> Validate -> ... -> Final",
    "few_shot": "0 examples (zero-shot) -> 1-3 examples -> 5+ examples (many-shot)",
    "batch_processing": "Chunk data -> Process in parallel -> Aggregate results",
    "multi_instance": "Generate N -> Validate each -> Reconcile -> Final",
}