"""
MULTI-INSTANCE REVIEW AND OUTPUT VALIDATION - Practice File 01
=============================================================

This file teaches how to:
1. Process requests through multiple instances
2. Validate outputs cross-instance
3. Implement consensus-based verification
4. Handle disagreements between instances
5. Set and adjust quality thresholds
6. Use redundancy patterns effectively
7. Reconcile outputs from multiple runs
8. Balance performance vs accuracy
9. Coordinate instances efficiently

REAL-WORLD SCENARIO:
You are building a content moderation system that needs
high accuracy. Rather than trusting a single LLM response,
you run multiple instances and compare their outputs to
catch errors and reduce false positives/negatives.
"""

import os
import time
import json
from typing import List, Dict, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from collections import Counter, defaultdict
from enum import Enum
from statistics import mean, stdev
from dotenv import load_dotenv

# For parallel execution
import threading

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not found in .env file")

# ============================================================================
# SECTION 1: INSTANCE OUTPUT STRUCTURE
# ============================================================================

@dataclass
class InstanceResult:
    """Result from a single instance processing."""
    instance_id: str
    output: Any
    confidence: float
    processing_time_ms: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MultiInstanceResult:
    """Aggregated result from multiple instances."""
    final_output: Any
    confidence: float
    agreement_level: float  # 0.0 to 1.0
    all_outputs: List[Any]
    disagreements: List[Dict[str, Any]]
    instances_used: int
    processing_time_ms: float


class AgreementType(Enum):
    """Level of agreement between instances."""
    FULL = "full"  # All instances agree
    MOST = "most"  # Majority agreement (e.g., 3/4)
    PARTIAL = "partial"  # Some agreement, some dissent
    SPLIT = "split"  # Complete split (e.g., 2-2)


# ============================================================================
# SECTION 2: CONSENSUS STRATEGIES
# ============================================================================

def find_majority_vote(outputs: List[Any]) -> Tuple[Any, float]:
    """
    Find the majority vote from multiple outputs.

    Args:
        outputs: List of outputs from instances

    Returns:
        Tuple of (majority_output, agreement_ratio)
    """
    if not outputs:
        return None, 0.0

    # Count occurrences
    counter = Counter(outputs)
    most_common = counter.most_common(1)[0]

    majority_value = most_common[0]
    count = most_common[1]
    agreement_ratio = count / len(outputs)

    return majority_value, agreement_ratio


def find_weighted_consensus(outputs: List[InstanceResult]) -> Any:
    """
    Find consensus weighted by confidence scores.

    Args:
        outputs: List of InstanceResult objects

    Returns:
        Weighted consensus output
    """
    if not outputs:
        return None

    # Group outputs by value
    value_weights = defaultdict(float)
    value_counts = defaultdict(int)

    for result in outputs:
        # Convert output to hashable key
        key = json.dumps(result.output, sort_keys=True)
        value_weights[key] += result.confidence
        value_counts[key] += 1

    # Find highest weighted average
    weighted_scores = {
        key: value_weights[key] / value_counts[key]  # Average confidence
        for key in value_weights
    }

    best_key = max(weighted_scores, key=weighted_scores.get)
    return json.loads(best_key)


def calculate_agreement_score(outputs: List[Any]) -> float:
    """
    Calculate how much instances agree.

    Returns:
        Agreement score from 0.0 (no agreement) to 1.0 (full agreement)
    """
    if len(outputs) <= 1:
        return 1.0

    counter = Counter(outputs)
    most_common_count = counter.most_common(1)[0][1]

    return most_common_count / len(outputs)


def detect_disagreements(outputs: List[InstanceResult],
                         threshold: float = 0.5) -> List[Dict[str, Any]]:
    """
    Identify where instances disagree and why.

    Args:
        outputs: List of InstanceResult objects
        threshold: Confidence threshold for flagging issues

    Returns:
        List of disagreement records
    """
    disagreements = []

    # Compare all pairs
    for i in range(len(outputs)):
        for j in range(i + 1, len(outputs)):
            out_i = outputs[i]
            out_j = outputs[j]

            # Check if outputs differ
            if out_i.output != out_j.output:
                disagreements.append({
                    'instance_1': out_i.instance_id,
                    'instance_2': out_j.instance_id,
                    'output_1': out_i.output,
                    'output_2': out_j.output,
                    'confidence_1': out_i.confidence,
                    'confidence_2': out_j.confidence,
                    'confidence_diff': abs(out_i.confidence - out_j.confidence)
                })

    return disagreements


# ============================================================================
# SECTION 3: QUALITY THRESHOLDS
# ============================================================================

@dataclass
class QualityThresholds:
    """Thresholds for accepting/rejecting multi-instance results."""
    min_agreement: float = 0.66  # Minimum 2/3 agreement
    min_confidence: float = 0.7  # Minimum confidence
    min_instances: int = 2  # Minimum instances to run

    # For classification: minimum votes for a category
    majority_threshold: float = 0.5  # >50% to accept

    # For continuous values: max standard deviation
    max_std_dev: float = 0.1  # For regression-type tasks

    def should_accept(self, result: MultiInstanceResult) -> Tuple[bool, str]:
        """Determine if result meets quality thresholds."""
        reasons = []

        if result.agreement_level < self.min_agreement:
            reasons.append(
                f"Agreement {result.agreement_level:.2f} < {self.min_agreement}"
            )

        if result.confidence < self.min_confidence:
            reasons.append(
                f"Confidence {result.confidence:.2f} < {self.min_confidence}"
            )

        if result.instances_used < self.min_instances:
            reasons.append(
                f"Instances {result.instances_used} < {self.min_instances}"
            )

        if reasons:
            return False, "; ".join(reasons)

        return True, "Passed all thresholds"


# ============================================================================
# SECTION 4: CROSS-VALIDATION LOGIC
# ============================================================================

class CrossValidator:
    """Validates outputs by comparing multiple instances."""

    def __init__(self, num_instances: int = 3):
        self.num_instances = num_instances

    def validate_classification(self,
                               outputs: List[InstanceResult],
                               thresholds: QualityThresholds) -> MultiInstanceResult:
        """
        Validate classification outputs from multiple instances.

        Args:
            outputs: List of InstanceResult from each instance
            thresholds: Quality thresholds to apply

        Returns:
            MultiInstanceResult with validated output
        """
        start_time = time.time()

        if len(outputs) < thresholds.min_instances:
            return MultiInstanceResult(
                final_output=None,
                confidence=0.0,
                agreement_level=0.0,
                all_outputs=[o.output for o in outputs],
                disagreements=[],
                instances_used=len(outputs),
                processing_time_ms=(time.time() - start_time) * 1000
            )

        # Find majority vote
        raw_outputs = [o.output for o in outputs]
        final_output, agreement_level = find_majority_vote(raw_outputs)

        # Calculate average confidence
        confidence = mean([o.confidence for o in outputs])

        # Detect disagreements
        disagreements = detect_disagreements(outputs)

        result = MultiInstanceResult(
            final_output=final_output,
            confidence=confidence,
            agreement_level=agreement_level,
            all_outputs=raw_outputs,
            disagreements=disagreements,
            instances_used=len(outputs),
            processing_time_ms=(time.time() - start_time) * 1000
        )

        # Apply thresholds
        should_accept, reason = thresholds.should_accept(result)

        return result

    def validate_extraction(self,
                           outputs: List[InstanceResult],
                           thresholds: QualityThresholds) -> MultiInstanceResult:
        """
        Validate structured extraction outputs.

        For extraction, check field-by-field agreement.
        """
        start_time = time.time()

        if not outputs:
            return MultiInstanceResult(
                final_output=None, confidence=0.0,
                agreement_level=0.0, all_outputs=[],
                disagreements=[], instances_used=0,
                processing_time_ms=0
            )

        # Convert outputs to comparable format
        all_outputs = [o.output for o in outputs]

        # Find common fields across all outputs
        all_fields = set()
        for output in all_outputs:
            if isinstance(output, dict):
                all_fields.update(output.keys())

        # For each field, check agreement
        field_agreements = {}
        for field in all_fields:
            field_values = []
            for output in all_outputs:
                if isinstance(output, dict) and field in output:
                    field_values.append(output[field])

            if field_values:
                # Calculate agreement for this field
                if len(field_values) > 1:
                    agreement = calculate_agreement_score(field_values)
                else:
                    agreement = 1.0
                field_agreements[field] = agreement

        # Build consensus output
        consensus_output = {}
        for field in all_fields:
            field_values = []
            for output in all_outputs:
                if isinstance(output, dict) and field in output:
                    field_values.append(output[field])

            if field_values:
                # Use most common value weighted by confidence
                counter = Counter(field_values)
                consensus_output[field] = counter.most_common(1)[0][0]

        # Overall agreement is average of field agreements
        overall_agreement = mean(field_agreements.values()) if field_agreements else 0.0
        confidence = mean([o.confidence for o in outputs])

        return MultiInstanceResult(
            final_output=consensus_output,
            confidence=confidence,
            agreement_level=overall_agreement,
            all_outputs=all_outputs,
            disagreements=[],  # Field-level disagreements could be tracked
            instances_used=len(outputs),
            processing_time_ms=(time.time() - start_time) * 1000
        )


# ============================================================================
# SECTION 5: INSTANCE COORDINATION
# ============================================================================

class InstanceCoordinator:
    """Coordinates execution across multiple LLM instances."""

    def __init__(self,
                 num_instances: int = 3,
                 timeout_seconds: float = 30.0):
        self.num_instances = num_instances
        self.timeout_seconds = timeout_seconds
        self.results: Dict[str, List[InstanceResult]] = {}

    def run_parallel_instances(self,
                              process_fn: Callable,
                              inputs: List[Any]) -> List[List[InstanceResult]]:
        """
        Run multiple instances in parallel for each input.

        Args:
            process_fn: Function to process each input
            inputs: List of inputs to process

        Returns:
            List of lists of InstanceResult (one list per input)
        """
        all_results = []
        lock = threading.Lock()

        def run_single_instance(instance_id: int, input_item: Any) -> InstanceResult:
            """Run a single instance for an input."""
            start_time = time.time()

            try:
                output = process_fn(input_item)

                return InstanceResult(
                    instance_id=f"instance_{instance_id}",
                    output=output,
                    confidence=0.9,  # Would be extracted from actual response
                    processing_time_ms=(time.time() - start_time) * 1000
                )
            except Exception as e:
                return InstanceResult(
                    instance_id=f"instance_{instance_id}",
                    output=None,
                    confidence=0.0,
                    processing_time_ms=(time.time() - start_time) * 1000,
                    metadata={'error': str(e)}
                )

        # Process each input through all instances
        for input_item in inputs:
            results = []

            with threading.ThreadPoolExecutor(max_workers=self.num_instances) as executor:
                futures = [
                    executor.submit(run_single_instance, i, input_item)
                    for i in range(self.num_instances)
                ]

                for future in futures:
                    try:
                        result = future.result(timeout=self.timeout_seconds)
                        results.append(result)
                    except Exception as e:
                        # Handle timeout or other errors
                        results.append(InstanceResult(
                            instance_id="unknown",
                            output=None,
                            confidence=0.0,
                            processing_time_ms=0,
                            metadata={'error': str(e)}
                        ))

            all_results.append(results)

        return all_results


# ============================================================================
# SECTION 6: OUTPUT RECONCILIATION
# ============================================================================

def reconcile_outputs(outputs: List[InstanceResult],
                     strategy: str = "confidence") -> Any:
    """
    Reconcile multiple outputs into a single final output.

    Args:
        outputs: List of InstanceResult objects
        strategy: Reconciliation strategy to use

    Returns:
        Reconciled output
    """
    if not outputs:
        return None

    # Filter out failed instances
    valid_outputs = [o for o in outputs if o.output is not None]
    if not valid_outputs:
        return None

    if strategy == "majority":
        raw_outputs = [o.output for o in valid_outputs]
        final_output, _ = find_majority_vote(raw_outputs)
        return final_output

    elif strategy == "confidence":
        return find_weighted_consensus(valid_outputs)

    elif strategy == "highest_confidence":
        best = max(valid_outputs, key=lambda x: x.confidence)
        return best.output

    elif strategy == "average":
        # For numeric outputs
        numeric_outputs = [o.output for o in valid_outputs
                         if isinstance(o.output, (int, float))]
        if numeric_outputs:
            return mean(numeric_outputs)
        return valid_outputs[0].output

    else:
        # Default: return first valid output
        return valid_outputs[0].output


def handle_split_decision(outputs: List[InstanceResult],
                          tie_breaker: Callable = None) -> Any:
    """
    Handle cases where instances are completely split.

    Args:
        outputs: List of outputs with disagreement
        tie_breaker: Optional function to break ties

    Returns:
        Resolved output
    """
    # Count occurrences
    counter = Counter([json.dumps(o.output, sort_keys=True) for o in outputs])
    max_count = counter.most_common(1)[0][1]

    # If there's a clear winner, use it
    if max_count > len(outputs) / 2:
        winning_json = counter.most_common(1)[0][0]
        return json.loads(winning_json)

    # Otherwise, use tie-breaker or highest confidence
    if tie_breaker:
        return tie_breaker(outputs)

    # Default: highest confidence wins
    best = max(outputs, key=lambda x: x.confidence)
    return best.output


# ============================================================================
# SECTION 7: PERFORMANCE VS ACCURACY TRADE-OFFS
# ============================================================================

def analyze_performance_accuracy_tradeoff(num_instances: int,
                                          expected_accuracy: float) -> Dict[str, Any]:
    """
    Analyze trade-offs between performance and accuracy.

    Args:
        num_instances: Number of instances to run
        expected_accuracy: Expected accuracy per instance

    Returns:
        Analysis of trade-offs
    """
    # With multiple instances, accuracy increases but linearly with cost
    # Agreement-based selection effectively filters out bad outputs

    accuracy_with_review = 1 - (1 - expected_accuracy) ** num_instances

    return {
        'num_instances': num_instances,
        'single_accuracy': expected_accuracy,
        'combined_accuracy': accuracy_with_review,
        'cost_increase': num_instances,
        'time_increase': num_instances,
        'recommendation': (
            'Use 3 instances for critical tasks' if num_instances == 3
            else 'Consider 3 instances for better reliability'
        )
    }


def adaptive_instance_selection(agreement_level: float,
                               confidence: float) -> int:
    """
    Adaptively select number of instances based on result characteristics.

    Args:
        agreement_level: Current agreement between instances
        confidence: Average confidence of instances

    Returns:
        Recommended number of instances for next run
    """
    # High agreement and confidence: fewer instances needed
    if agreement_level > 0.9 and confidence > 0.9:
        return 1  # Single instance sufficient

    # Good agreement: 2 instances enough
    if agreement_level > 0.7:
        return 2

    # Low agreement: need more instances
    if agreement_level < 0.5:
        return 4

    # Default: 3 instances
    return 3


# ============================================================================
# SECTION 8: PRACTICAL EXAMPLE - CONTENT MODERATION
# ============================================================================

class ContentModerator:
    """Multi-instance content moderation system."""

    def __init__(self, num_instances: int = 3):
        self.num_instances = num_instances
        self.validator = CrossValidator(num_instances)
        self.thresholds = QualityThresholds(
            min_agreement=0.66,
            min_confidence=0.7,
            min_instances=2
        )

    def moderate_content(self, content: str, api_client) -> Dict[str, Any]:
        """
        Moderate content using multiple instances.

        Args:
            content: Content to moderate
            api_client: API client for LLM calls

        Returns:
            Moderation result with confidence
        """
        def single_instance_moderation(instance_id: int) -> InstanceResult:
            """Run moderation on single instance."""
            start_time = time.time()

            try:
                # Build moderation prompt
                prompt = f"""Classify this content as: safe, potentially_harmful,
or harmful. Consider: hate speech, violence, adult content, harassment.

Content: {content}

Respond with only the classification, nothing else."""

                # Call API (simplified)
                # response = api_client.messages.create(
                #     model="claude-haiku-4-5-20250601",
                #     messages=[{"role": "user", "content": prompt}]
                # )

                # Simulated response
                output = "safe"
                confidence = 0.85

                return InstanceResult(
                    instance_id=f"mod_{instance_id}",
                    output=output,
                    confidence=confidence,
                    processing_time_ms=(time.time() - start_time) * 1000
                )

            except Exception as e:
                return InstanceResult(
                    instance_id=f"mod_{instance_id}",
                    output=None,
                    confidence=0.0,
                    processing_time_ms=0,
                    metadata={'error': str(e)}
                )

        # Run multiple instances
        outputs = [
            single_instance_moderation(i)
            for i in range(self.num_instances)
        ]

        # Validate with cross-validation
        result = self.validator.validate_classification(outputs, self.thresholds)

        # Determine if human review needed
        needs_human_review = not self.thresholds.should_accept(result)[0]

        return {
            'decision': result.final_output,
            'confidence': result.confidence,
            'agreement': result.agreement_level,
            'needs_human_review': needs_human_review,
            'all_outputs': result.all_outputs,
            'disagreements': result.disagreements
        }


# ============================================================================
# SECTION 9: DEMONSTRATION
# ============================================================================

def demonstrate_multi_instance_review():
    """Demonstrate multi-instance review patterns."""

    print("=" * 60)
    print("MULTI-INSTANCE REVIEW - PRACTICE 01: VALIDATION")
    print("=" * 60)

    # Create sample instance results
    sample_outputs = [
        InstanceResult("inst_1", "positive", 0.85, 150),
        InstanceResult("inst_2", "positive", 0.90, 140),
        InstanceResult("inst_3", "negative", 0.75, 160),
    ]

    # Calculate agreement
    print("\n[DEMO] Instance agreement analysis...")
    agreement = calculate_agreement_score([o.output for o in sample_outputs])
    print(f"  Agreement score: {agreement:.2f} ({agreement * 100:.0f}%)")

    # Find majority vote
    majority, ratio = find_majority_vote([o.output for o in sample_outputs])
    print(f"  Majority vote: {majority} ({ratio * 100:.0f}% agreement)")

    # Detect disagreements
    print("\n[DEMO] Disagreement detection...")
    disagreements = detect_disagreements(sample_outputs)
    print(f"  Found {len(disagreements)} disagreements")
    for d in disagreements:
        print(f"    - {d['instance_1']} vs {d['instance_2']}")
        print(f"      Output: {d['output_1']} vs {d['output_2']}")

    # Quality thresholds
    print("\n[DEMO] Quality threshold application...")
    thresholds = QualityThresholds()
    print(f"  Min agreement: {thresholds.min_agreement}")
    print(f"  Min confidence: {thresholds.min_confidence}")
    print(f"  Min instances: {thresholds.min_instances}")

    # Cross-validation
    print("\n[DEMO] Cross-validation...")
    validator = CrossValidator(num_instances=3)
    result = validator.validate_classification(sample_outputs, thresholds)
    print(f"  Final output: {result.final_output}")
    print(f"  Confidence: {result.confidence:.2f}")
    print(f"  Agreement: {result.agreement_level:.2f}")
    print(f"  Processing time: {result.processing_time_ms:.1f}ms")

    # Adaptive selection
    print("\n[DEMO] Adaptive instance selection...")
    recommended = adaptive_instance_selection(0.75, 0.82)
    print(f"  Recommended instances for similar task: {recommended}")

    print("\n" + "=" * 60)
    print("WHAT WE HAVE LEARNT:")
    print("=" * 60)
    print("""
1. MULTI-INSTANCE PROCESSING
   - Run same input through multiple LLM instances
   - Compare outputs for agreement
   - Flag disagreements for review

2. CONSENSUS STRATEGIES
   - Majority vote: Use most common output
   - Weighted by confidence: Higher confidence wins
   - Highest confidence: Use single best result

3. AGREEMENT MEASUREMENT
   - Calculate agreement ratio (0.0 to 1.0)
   - Full agreement: All outputs identical
   - Partial agreement: Some outputs differ
   - Split decision: Equal split

4. QUALITY THRESHOLDS
   - Set minimum agreement level (e.g., 66%)
   - Set minimum confidence level (e.g., 70%)
   - Require minimum instances (e.g., 2+)
   - Reject results below thresholds

5. CROSS-VALIDATION
   - Compare outputs field-by-field for structured data
   - Track disagreements per field
   - Build consensus output from agreement

6. OUTPUT RECONCILIATION
   - Use tie-breaker functions for splits
   - Filter failed instances first
   - Consider confidence weights

7. PERFORMANCE VS ACCURACY
   - More instances = higher accuracy but higher cost
   - Use adaptive selection based on task difficulty
   - High agreement allows fewer instances

8. REDUNDANCY PATTERNS
   - Critical tasks: 3-5 instances
   - Standard tasks: 2-3 instances
   - Simple tasks: 1 instance sufficient

9. COMMON MISTAKES
   - Running too many instances (wasteful)
   - Not checking agreement (miss errors)
   - Ignoring low-confidence outputs
   - No threshold for human review
""")

    return {
        'majority_vote': majority,
        'agreement_level': agreement,
        'disagreements_found': len(disagreements)
    }


if __name__ == "__main__":
    demonstrate_multi_instance_review()


# ============================================================================
# INTERVIEW Q&A PREP
# ============================================================================
"""
Q: When should you use multi-instance review?
A: Use it for critical decisions where errors are costly:
   - Content moderation
   - Financial transactions
   - Medical diagnoses
   - Legal document review

Q: How many instances should you run?
A: Depends on task criticality:
   - Low risk: 1-2 instances
   - Medium risk: 2-3 instances
   - High risk: 3-5 instances

Q: What is consensus-based verification?
A: Taking the output that the majority of instances agree on.
   If 3/4 instances output "safe", use "safe" as final answer.

Q: How do you handle complete splits?
A: Use tie-breaker logic (highest confidence wins), escalate
   to human review, or run additional instances.

Q: What is the trade-off between performance and accuracy?
A: More instances = more accurate but slower and costlier.
   Use adaptive selection to run more instances only when
   initial results show disagreement or low confidence.
"""