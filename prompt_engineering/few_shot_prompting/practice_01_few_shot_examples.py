"""
FEW-SHOT PROMPTING - Practice File 01
=====================================

This file teaches how to:
1. Select effective examples
2. Use positive and negative examples
3. Format examples properly
4. Determine optimal number of examples
5. Ensure diversity in example sets
6. Use labeled vs unlabeled examples
7. Implement chain-of-thought examples
8. Balance quality vs quantity

REAL-WORLD SCENARIO:
You are building a sentiment analysis classifier that needs
to classify product reviews as positive, negative, or neutral.
Few-shot prompting will help the model understand the task
without extensive task description.
"""

import os
import random
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
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
# SECTION 2: EXAMPLE SELECTION AND STRUCTURE
# ============================================================================

@dataclass
class Example:
    """
    A single example for few-shot prompting.

    Attributes:
        input: The input text (review, question, etc.)
        output: The expected output (label, answer, etc.)
        explanation: Optional reasoning/explanation for the output
        metadata: Additional context about this example
    """
    input: str
    output: str
    explanation: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ExampleSet:
    """
    Collection of examples with selection and diversity logic.
    """

    def __init__(self, examples: List[Example]):
        self.examples = examples
        self._index_by_label = self._build_label_index()

    def _build_label_index(self) -> Dict[str, List[int]]:
        """Index examples by their output label."""
        index = {}
        for i, ex in enumerate(self.examples):
            label = ex.output.split(':')[0] if ':' in ex.output else ex.output
            if label not in index:
                index[label] = []
            index[label].append(i)
        return index

    def get_balanced_subset(self, n: int) -> List[Example]:
        """
        Get n examples balanced across all label types.

        Args:
            n: Total number of examples to return

        Returns:
            List of n examples, balanced across labels
        """
        labels = list(self._index_by_label.keys())
        if not labels:
            return []

        # Calculate how many from each label
        per_label = max(1, n // len(labels))
        remainder = n % len(labels)

        selected = []
        for i, label in enumerate(labels):
            indices = self._index_by_index[label]
            count = per_label + (1 if i < remainder else 0)
            # Random selection from each label
            selected.extend(random.sample(indices, min(count, len(indices))))

        return selected

    @property
    def _index_by_index(self) -> Dict[str, List[int]]:
        """Alias for backward compatibility."""
        return self._index_by_label


# ============================================================================
# SECTION 3: POSITIVE AND NEGATIVE EXAMPLES
# ============================================================================

def create_sentiment_examples() -> List[Example]:
    """
    Create example set with both positive and negative examples.

    Positive examples: Show what correct behavior looks like
    Negative examples: Show common mistakes to avoid
    """

    # POSITIVE EXAMPLES: Show correct classification with reasoning
    positive_examples = [
        Example(
            input="This phone has an amazing camera and the battery lasts all day.",
            output="positive",
            explanation="Contains explicitly positive words: 'amazing', 'lasts all day'",
            metadata={"sentiment_indicators": ["amazing", "lasts all day"]}
        ),
        Example(
            input="The product arrived on time and works exactly as described. Happy with my purchase!",
            output="positive",
            explanation="Contains multiple positive signals: 'on time', 'exactly as described', 'Happy'",
            metadata={"sentiment_indicators": ["on time", "happy"]}
        ),
        Example(
            input="Terrible experience. The screen cracked after one week and support was unhelpful.",
            output="negative",
            explanation="Contains explicitly negative words: 'terrible', 'cracked', 'unhelpful'",
            metadata={"sentiment_indicators": ["terrible", "cracked", "unhelpful"]}
        ),
        Example(
            input="I ordered medium but received small. The size guide was misleading.",
            output="negative",
            explanation="Negative due to: wrong item received, misleading information",
            metadata={"sentiment_indicators": ["wrong", "misleading"]}
        ),
        Example(
            input="Package arrived, looks fine, haven't tested yet.",
            output="neutral",
            explanation="No sentiment indicators - factual statement about receiving package",
            metadata={"sentiment_indicators": []}
        ),
        Example(
            input="The item weighs about 2 pounds and is 6 inches tall.",
            output="neutral",
            explanation="Purely factual description, no opinion or sentiment expressed",
            metadata={"sentiment_indicators": []}
        ),
    ]

    # NEGATIVE EXAMPLES: Show common mistakes to avoid
    negative_examples = [
        Example(
            input="GREAT product!!! Loved it!!! Best ever!!!",
            output="positive BUT WARNING: Overly enthusiastic, may be spam",
            explanation="This looks like fake positive review - excessive caps and exclamation marks",
            metadata={"spam_indicators": ["excessive_caps", "multiple_exclamation"]}
        ),
        Example(
            input="It was okay I guess. Not bad. Not great either.",
            output="neutral (NOT positive): 'okay' and 'not great' indicate mixed/neutral, not positive",
            explanation="Contains word 'good' but context is neutral/ambivalent",
            metadata={"confusing_signals": ["okay", "not great"]}
        ),
    ]

    return positive_examples + negative_examples


# ============================================================================
# SECTION 4: FORMATTING FEW-SHOT EXAMPLES
# ============================================================================

def format_examples_simple(examples: List[Example]) -> str:
    """
    Format examples in simple input-output pairs.

    Format:
    Input: <text>
    Output: <label>
    """
    formatted = []
    for ex in examples:
        formatted.append(f"Input: {ex.input}")
        formatted.append(f"Output: {ex.output}")
        if ex.explanation:
            formatted.append(f"Reason: {ex.explanation}")
        formatted.append("")  # Empty line between examples

    return "\n".join(formatted)


def format_examples_with_thinking(examples: List[Example]) -> str:
    """
    Format examples with chain-of-thought reasoning.

    Format:
    Input: <text>
    Thinking: <step-by-step reasoning>
    Output: <final label>
    """
    formatted = []
    for ex in examples:
        formatted.append(f"Input: {ex.input}")
        if ex.explanation:
            formatted.append(f"Thinking: {ex.explanation}")
        formatted.append(f"Output: {ex.output}")
        formatted.append("")

    return "\n".join(formatted)


def format_examples_jsonl(examples: List[Example]) -> str:
    """
    Format examples in JSON lines format.

    Each line is a complete JSON object.
    """
    import json
    lines = []
    for ex in examples:
        obj = {
            "input": ex.input,
            "output": ex.output
        }
        if ex.explanation:
            obj["reasoning"] = ex.explanation
        lines.append(json.dumps(obj))

    return "\n".join(lines)


# ============================================================================
# SECTION 5: BUILDING FEW-SHOT PROMPTS
# ============================================================================

def build_sentiment_prompt(test_input: str,
                          examples: List[Example],
                          include_reasoning: bool = False) -> List[Dict[str, str]]:
    """
    Build a few-shot prompt for sentiment classification.

    Args:
        test_input: The text to classify
        examples: List of examples to include
        include_reasoning: Whether to include reasoning in examples

    Returns:
        Messages list for API call
    """
    # Format examples based on include_reasoning flag
    if include_reasoning:
        example_text = format_examples_with_thinking(examples)
    else:
        example_text = format_examples_simple(examples)

    # Build system prompt
    system_prompt = f"""You are a sentiment classifier. Analyze product reviews
and classify them as positive, negative, or neutral.

RULES:
- positive: Contains praise, satisfaction, or good experiences
- negative: Contains complaints, disappointment, or bad experiences
- neutral: Contains no sentiment, purely factual or balanced

{'-' * 50}
EXAMPLES:
{'-' * 50}
{example_text}
{'-' * 50}
"""

    # Build user message
    user_message = f"Classify this review:\n{test_input}"

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]


def build_summarization_prompt(test_input: str,
                               examples: List[Example]) -> List[Dict[str, str]]:
    """
    Build few-shot prompt for text summarization.
    """
    # Format examples
    example_text = format_examples_simple(examples)

    system_prompt = f"""You are a text summarizer. Create concise summaries
that capture the main points.

RULES:
- Summaries should be 2-3 sentences
- Include the main topic and key points
- Exclude minor details
- Use your own words, don't copy

{'-' * 50}
EXAMPLES:
{'-' * 50}
{example_text}
{'-' * 50}
"""

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Summarize this:\n\n{test_input}"}
    ]


# ============================================================================
# SECTION 6: OPTIMAL EXAMPLE SELECTION
# ============================================================================

def select_optimal_examples(examples: List[Example],
                           task_type: str,
                           max_examples: int = 5) -> List[Example]:
    """
    Select optimal examples based on task requirements.

    Args:
        examples: Full pool of available examples
        task_type: Type of task (sentiment, classification, generation)
        max_examples: Maximum examples to include

    Returns:
        Selected subset of examples
    """
    # For classification, ensure all labels are represented
    if task_type == "classification":
        labels = set(ex.output for ex in examples)
        selected = []

        # Add at least one from each label
        for label in labels:
            label_examples = [ex for ex in examples if ex.output == label]
            if label_examples:
                # Add best example for this label (first one as default)
                selected.append(label_examples[0])

        # Fill remaining slots with diverse examples
        remaining = max_examples - len(selected)
        if remaining > 0:
            other_examples = [ex for ex in examples
                            if ex not in selected]
            selected.extend(other_examples[:remaining])

        return selected[:max_examples]

    # For generation tasks, use diverse inputs
    elif task_type == "generation":
        # Select varied examples across different styles/topics
        return examples[:min(max_examples, len(examples))]

    # Default: return first n examples
    return examples[:max_examples]


# ============================================================================
# SECTION 7: CHAIN-OF-THOUGHT FEW-SHOT
# ============================================================================

def create_cot_examples() -> List[Example]:
    """
    Create examples with chain-of-thought reasoning.

    Chain-of-thought shows the reasoning process, not just input-output.
    """
    return [
        Example(
            input="If a store has 50 apples and sells 23 apples on Monday, "
                  "then sells 15 apples on Tuesday, how many apples remain?",
            output="12 apples remain",
            explanation="Step 1: 50 - 23 = 27 apples after Monday. "
                        "Step 2: 27 - 15 = 12 apples after Tuesday. "
                        "Answer: 12 apples"
        ),
        Example(
            input="A train travels 60 miles per hour for 2.5 hours. "
                  "How far does it travel?",
            output="150 miles",
            explanation="Step 1: Identify formula - distance = speed * time. "
                        "Step 2: Plug in values - 60 mph * 2.5 hours. "
                        "Step 3: Calculate - 60 * 2.5 = 150. "
                        "Answer: 150 miles"
        ),
        Example(
            input="Which is larger: 3/7 or 4/9?",
            output="3/7 is larger",
            explanation="Step 1: Find common denominator - 7 * 9 = 63. "
                        "Step 2: Convert - 3/7 = 27/63, 4/9 = 28/63. "
                        "Step 3: Compare - 27/63 < 28/63, so 3/7 < 4/9. "
                        "Therefore 4/9 is larger. Wait, let me recheck: 28/63 > 27/63, "
                        "so 4/9 (28/63) is larger. Answer: 4/9 is larger"
        ),
    ]


def build_cot_prompt(test_input: str, examples: List[Example]) -> List[Dict[str, str]]:
    """
    Build a chain-of-thought few-shot prompt.
    """
    example_text = format_examples_with_thinking(examples)

    system_prompt = f"""You are a reasoning assistant. Show your step-by-step
thinking before giving the final answer.

FORMAT:
Input: <problem>
Thinking: <your step-by-step reasoning>
Output: <final answer>

{'-' * 50}
EXAMPLES:
{'-' * 50}
{example_text}
{'-' * 50}
"""

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Input: {test_input}"}
    ]


# ============================================================================
# SECTION 8: DYNAMIC FEW-SHOT SELECTION
# ============================================================================

def select_examples_by_similarity(test_input: str,
                                  examples: List[Example],
                                  metric: str = "length") -> List[Example]:
    """
    Select examples similar to the test input.

    This dynamic selection ensures examples are relevant to the
    specific input being processed.

    Args:
        test_input: The input to classify/generate for
        examples: Pool of available examples
        metric: Similarity metric to use

    Returns:
        Examples sorted by relevance to test_input
    """
    scored = []

    for ex in examples:
        if metric == "length":
            # Score by length similarity
            test_len = len(test_input.split())
            ex_len = len(ex.input.split())
            similarity = 1 - abs(test_len - ex_len) / max(test_len, ex_len)
        elif metric == "topic":
            # Simple topic matching (word overlap)
            test_words = set(test_input.lower().split())
            ex_words = set(ex.input.lower().split())
            overlap = len(test_words & ex_words)
            similarity = overlap / max(len(test_words), len(ex_words))
        else:
            similarity = 0.5  # Default

        scored.append((similarity, ex))

    # Sort by similarity descending
    scored.sort(key=lambda x: x[0], reverse=True)
    return [ex for _, ex in scored]


# ============================================================================
# SECTION 9: EXAMPLE QUALITY VS QUANTITY
# ============================================================================

def demonstrate_quality_vs_quantity():
    """
    Demonstrate the trade-off between example quality and quantity.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE QUALITY VS QUANTITY ANALYSIS")
    print("=" * 60)

    # Quality factors
    quality_factors = [
        "Representative: Examples cover typical cases",
        "Diverse: Examples show variation in inputs",
        "Clear: Labels and explanations are unambiguous",
        "Correct: Outputs are accurate and verified",
        "Relevant: Examples match the test distribution",
    ]

    print("\nQUALITY FACTORS (more important than quantity):")
    for factor in quality_factors:
        print(f"  - {factor}")

    # Quantity guidelines
    print("\nQUANTITY GUIDELINES:")
    guidelines = [
        "1-2 examples: Good for simple, consistent tasks",
        "3-5 examples: Standard for most classification tasks",
        "5-10 examples: Complex tasks with multiple categories",
        "10+ examples: Very complex tasks or diverse domains",
    ]
    for guide in guidelines:
        print(f"  - {guide}")

    # Common mistake
    print("\nCOMMON MISTAKE: Including too many examples")
    print("  Bad: 20 diverse examples - model gets confused")
    print("  Good: 5 well-chosen, representative examples")


# ============================================================================
# SECTION 10: DEMONSTRATION
# ============================================================================

def demonstrate_few_shot():
    """Demonstrate few-shot prompting patterns."""

    print("=" * 60)
    print("FEW-SHOT PROMPTING - PRACTICE 01: EXAMPLES")
    print("=" * 60)

    # Create examples
    examples = create_sentiment_examples()

    print(f"\n[DEMO] Created {len(examples)} examples")
    labels = set(ex.output for ex in examples)
    print(f"Labels covered: {', '.join(labels)}")

    # Format examples
    print("\n[DEMO] Simple format:")
    simple_formatted = format_examples_simple(examples[:2])
    print(simple_formatted[:300] + "...")

    print("\n[DEMO] With reasoning format:")
    reasoning_formatted = format_examples_with_thinking(examples[:2])
    print(reasoning_formatted[:300] + "...")

    # Build a prompt
    print("\n[DEMO] Building few-shot prompt...")
    test_review = "The wireless headphones work great and battery life is excellent."
    prompt = build_sentiment_prompt(test_review, examples[:3], include_reasoning=False)
    print(f"System prompt length: {len(prompt[0]['content'])} chars")
    print(f"User prompt: {prompt[1]['content'][:100]}...")

    # Chain-of-thought examples
    print("\n[DEMO] Chain-of-thought examples:")
    cot_examples = create_cot_examples()
    for ex in cot_examples[:1]:
        print(f"  Input: {ex.input[:50]}...")
        print(f"  Output: {ex.output}")
        print(f"  Reasoning: {ex.explanation}")

    # Demonstrate quality vs quantity
    demonstrate_quality_vs_quantity()

    print("\n" + "=" * 60)
    print("WHAT WE HAVE LEARNT:")
    print("=" * 60)
    print("""
1. EXAMPLE SELECTION
   - Choose representative examples
   - Cover all output categories/label types
   - Include edge cases and variations
   - Ensure examples match test distribution

2. POSITIVE VS NEGATIVE EXAMPLES
   - Positive: Show correct behavior
   - Negative: Show common mistakes to avoid
   - Mix both for robust learning

3. FORMATTING TECHNIQUES
   - Simple: Input -> Output pairs
   - With reasoning: Input -> Thinking -> Output
   - JSON lines: Structured machine-readable format

4. OPTIMAL NUMBER OF EXAMPLES
   - 1-2: Simple, consistent tasks
   - 3-5: Standard classification
   - 5-10: Complex multi-category tasks
   - Quality > quantity - 5 good > 20 mediocre

5. DIVERSITY IN EXAMPLE SETS
   - Cover different input styles
   - Include various difficulty levels
   - Balance across all output categories
   - Represent edge cases

6. CHAIN-OF-THOUGHT
   - Include step-by-step reasoning
   - Show work before final answer
   - Helps model understand process
   - Particularly useful for reasoning tasks

7. DYNAMIC SELECTION
   - Select examples similar to test input
   - Use similarity metrics (length, topic)
   - Relevance > random selection

8. COMMON MISTAKES
   - Too many examples (confuses model)
   - All positive examples (no learning about errors)
   - Unclear or ambiguous labels
   - Examples don't match test distribution
""")


if __name__ == "__main__":
    demonstrate_few_shot()


# ============================================================================
# INTERVIEW Q&A PREP
# ============================================================================
"""
Q: How many few-shot examples should you use?
A: Start with 3-5 examples. More isn't always better - quality and
   diversity matter more than quantity. For simple tasks, 1-2 is enough.

Q: When should you use chain-of-thought examples?
A: Use CoT for complex reasoning tasks (math, logic, analysis).
   For simple classification, reasoning steps are unnecessary.

Q: How do you select good examples?
A: Choose examples that are: representative of test data,
   cover all output categories, include edge cases, and have
   clear unambiguous labels.

Q: What's the difference between few-shot and zero-shot?
A: Zero-shot relies on instructions only. Few-shot provides
   examples that demonstrate the pattern to follow. Few-shot
   generally produces more reliable results for specific formats.

Q: Should examples be labeled or unlabeled?
A: For learning a pattern, labeled examples (with output) are
   essential. Unlabeled examples are only useful for showing
   input structure, not output expectations.
"""