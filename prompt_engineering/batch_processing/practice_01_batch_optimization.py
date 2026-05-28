"""
BATCH PROCESSING AND PROMPT OPTIMIZATION - Practice File 01
==========================================================

This file teaches how to:
1. Create efficient batch request patterns
2. Implement parallel processing strategies
3. Optimize token usage
4. Reduce costs while maintaining quality
5. Handle rate limiting gracefully
6. Optimize batch sizes
7. Aggregate errors from batches
8. Track progress and report results
9. Manage resources effectively

REAL-WORLD SCENARIO:
You are processing 10,000 customer support tickets to
categorize them and generate suggested responses. You need
to do this efficiently while managing API costs and rate limits.
"""

import os
import time
import json
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
import hashlib
from dotenv import load_dotenv

# Note: For production, use async for true parallelism
# This example uses threading for demonstration
import threading

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not found in .env file")

# Import would be: from anthropic import Anthropic
# For this example, we'll mock the client behavior
# client = Anthropic()

# ============================================================================
# SECTION 1: BATCH CONFIGURATION
# ============================================================================

@dataclass
class BatchConfig:
    """Configuration for batch processing."""
    max_batch_size: int = 10  # Items per batch
    max_workers: int = 3  # Parallel workers
    rate_limit_per_minute: int = 50  # API rate limit
    retry_attempts: int = 3
    retry_delay_seconds: float = 2.0
    timeout_seconds: float = 60.0
    token_budget: Optional[int] = None  # Max tokens to spend

    def __post_init__(self):
        """Validate configuration."""
        if self.max_batch_size < 1:
            raise ValueError("max_batch_size must be >= 1")
        if self.max_workers < 1:
            raise ValueError("max_workers must be >= 1")


@dataclass
class BatchResult:
    """Result of processing a batch."""
    batch_id: str
    successful: int = 0
    failed: int = 0
    results: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    total_tokens: int = 0
    execution_time_ms: float = 0


@dataclass
class ProcessingStats:
    """Statistics for batch processing."""
    total_items: int = 0
    processed_items: int = 0
    successful_items: int = 0
    failed_items: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    start_time: float = 0
    end_time: float = 0

    def progress_percentage(self) -> float:
        """Calculate progress percentage."""
        if self.total_items == 0:
            return 0.0
        return (self.processed_items / self.total_items) * 100

    def items_per_second(self) -> float:
        """Calculate processing rate."""
        elapsed = self.end_time - self.start_time if self.end_time > 0 else 1
        return self.processed_items / elapsed


# ============================================================================
# SECTION 2: BATCH CHUNKING STRATEGIES
# ============================================================================

def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split a list into chunks of specified size.

    Args:
        items: List of items to chunk
        chunk_size: Maximum items per chunk

    Returns:
        List of chunks
    """
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def chunk_by_token_estimate(items: List[str],
                            max_tokens_per_chunk: int = 8000) -> List[List[str]]:
    """
    Chunk items based on estimated token count.

    This is more efficient than fixed-size chunking because
    it maximizes token usage while staying under limits.

    Args:
        items: List of text items to chunk
        max_tokens_per_chunk: Maximum tokens per chunk (estimate)

    Returns:
        List of chunked items
    """
    chunks = []
    current_chunk = []
    current_tokens = 0

    for item in items:
        # Estimate: ~4 characters per token (rough estimate)
        item_tokens = len(item) // 4

        if current_tokens + item_tokens > max_tokens_per_chunk and current_chunk:
            chunks.append(current_chunk)
            current_chunk = []
            current_tokens = 0

        current_chunk.append(item)
        current_tokens += item_tokens

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def smart_chunk_items(items: List[Dict[str, Any]],
                     prompt_template: str,
                     max_tokens: int = 100000) -> List[List[Dict[str, Any]]]:
    """
    Smart chunking that considers prompt overhead.

    Ensures each chunk (prompt + items) stays under token limit.

    Args:
        items: List of items to process
        prompt_template: The system prompt template
        max_tokens: Maximum tokens per request

    Returns:
        List of chunked items
    """
    # Estimate prompt tokens (rough: 1 token per 4 chars + buffer)
    prompt_tokens = len(prompt_template) // 4 + 500  # Add buffer

    available_tokens = max_tokens - prompt_tokens
    chunks = []
    current_chunk = []
    current_tokens = 0

    for item in items:
        item_text = json.dumps(item)
        item_tokens = len(item_text) // 4

        # Check if adding this item exceeds limit
        if current_tokens + item_tokens > available_tokens and current_chunk:
            chunks.append(current_chunk)
            current_chunk = []
            current_tokens = 0

        current_chunk.append(item)
        current_tokens += item_tokens

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


# ============================================================================
# SECTION 3: PARALLEL PROCESSING IMPLEMENTATION
# ============================================================================

class RateLimiter:
    """Thread-safe rate limiter for API calls."""

    def __init__(self, max_per_minute: int):
        self.max_per_minute = max_per_minute
        self.interval_seconds = 60.0 / max_per_minute
        self.lock = threading.Lock()
        self.last_call_time = 0.0

    def wait_if_needed(self):
        """Wait if necessary to stay within rate limit."""
        with self.lock:
            current_time = time.time()
            elapsed = current_time - self.last_call_time

            if elapsed < self.interval_seconds:
                sleep_time = self.interval_seconds - elapsed
                time.sleep(sleep_time)

            self.last_call_time = time.time()


class BatchProcessor:
    """
    Handles batch processing with parallel execution and rate limiting.
    """

    def __init__(self, config: BatchConfig):
        self.config = config
        self.rate_limiter = RateLimiter(config.rate_limit_per_minute)
        self.stats = ProcessingStats()
        self.lock = threading.Lock()

    def process_batch(self,
                     items: List[Dict[str, Any]],
                     process_fn: Callable) -> BatchResult:
        """
        Process a batch of items.

        Args:
            items: List of items to process
            process_fn: Function to process each item

        Returns:
            BatchResult with processing outcomes
        """
        batch_id = hashlib.md5(str(items).encode()).hexdigest()[:8]
        result = BatchResult(batch_id=batch_id)

        start_time = time.time()

        for item in items:
            try:
                # Apply rate limiting
                self.rate_limiter.wait_if_needed()

                # Process item
                output = process_fn(item)

                result.successful += 1
                result.results.append({
                    'item': item,
                    'output': output,
                    'success': True
                })

            except Exception as e:
                result.failed += 1
                result.errors.append({
                    'item': item,
                    'error': str(e)
                })

        result.execution_time_ms = (time.time() - start_time) * 1000

        return result

    def process_parallel(self,
                        items: List[Dict[str, Any]],
                        process_fn: Callable,
                        progress_callback: Optional[Callable] = None) -> List[BatchResult]:
        """
        Process items in parallel with multiple workers.

        Args:
            items: List of items to process
            process_fn: Function to process each item
            progress_callback: Optional callback for progress updates

        Returns:
            List of BatchResult objects
        """
        # Split into chunks for parallel processing
        chunks = chunk_list(items, self.config.max_batch_size)

        results = []

        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            # Submit all chunks
            future_to_chunk = {
                executor.submit(self.process_batch, chunk, process_fn): chunk
                for chunk in chunks
            }

            # Collect results as they complete
            for future in as_completed(future_to_chunk):
                chunk = future_to_chunk[future]
                try:
                    batch_result = future.result()
                    results.append(batch_result)

                    # Update stats
                    with self.lock:
                        self.stats.processed_items += (
                            batch_result.successful + batch_result.failed
                        )
                        self.stats.successful_items += batch_result.successful
                        self.stats.failed_items += batch_result.failed

                    # Progress callback
                    if progress_callback:
                        progress_callback(self.stats)

                except Exception as e:
                    print(f"Batch failed: {e}")

        return results


# ============================================================================
# SECTION 4: TOKEN OPTIMIZATION
# ============================================================================

def estimate_token_count(text: str) -> int:
    """
    Estimate token count for text.

    Uses simple heuristic: ~4 characters per token average.
    For accurate count, use tiktoken or similar library.

    Args:
        text: Text to estimate tokens for

    Returns:
        Estimated token count
    """
    # Simple estimate: 4 characters per token
    return len(text) // 4


def optimize_prompt_tokens(prompt_template: str,
                          examples: List[str],
                          max_tokens: int) -> List[str]:
    """
    Optimize token usage by selecting fewest examples needed.

    Args:
        prompt_template: The system prompt
        examples: List of example texts
        max_tokens: Maximum tokens allowed

    Returns:
        Subset of examples that fit within token budget
    """
    prompt_tokens = estimate_token_count(prompt_template)
    available_tokens = max_tokens - prompt_tokens - 200  # Buffer

    selected = []
    total_tokens = 0

    for example in examples:
        example_tokens = estimate_token_count(example)

        if total_tokens + example_tokens <= available_tokens:
            selected.append(example)
            total_tokens += example_tokens

    return selected


def compress_prompt(prompt: str) -> str:
    """
    Compress prompt while preserving meaning.

    Techniques:
    - Remove redundant phrases
    - Use abbreviations
    - Combine similar instructions
    - Remove filler words
    """
    # Simple compression rules
    compressions = [
        ("Please ", ""),
        ("Thank you for ", ""),
        ("I would like you to ", ""),
        ("Can you ", ""),
        ("Could you ", ""),
        ("Please note that ", "Note: "),
        ("In order to ", "To "),
        ("At this point in time", "Now"),
        ("due to the fact that", "because"),
        ("in the event that", "if"),
        (" for the purpose of ", " to "),
    ]

    compressed = prompt
    for old, new in compressions:
        compressed = compressed.replace(old, new)

    return compressed


# ============================================================================
# SECTION 5: COST REDUCTION STRATEGIES
# ============================================================================

def calculate_cost(tokens_used: int,
                  model: str = "claude-haiku-4-5-20250601") -> float:
    """
    Calculate approximate cost for token usage.

    Note: Check current pricing at anthropic.com/pricing
    """
    # Example pricing (verify current rates)
    pricing = {
        "claude-haiku-4-5-20250601": {
            "input": 0.00025 / 1000,  # $0.00025 per 1K tokens
            "output": 0.00125 / 1000,  # $0.00125 per 1K tokens
        }
    }

    rates = pricing.get(model, pricing["claude-haiku-4-5-20250601"])
    return tokens_used * rates["input"]  # Simplified - assumes equal in/out


def reduce_costs_strategies():
    """
    Display strategies for reducing API costs.
    """
    strategies = [
        {
            "name": "Batch similar requests",
            "benefit": "Reduces per-request overhead",
            "implementation": "Group items by type before processing"
        },
        {
            "name": "Use smaller models for simple tasks",
            "benefit": "Significant cost reduction",
            "implementation": "Use Haiku for classification, Opus only for complex"
        },
        {
            "name": "Optimize prompts",
            "benefit": "Fewer tokens per request",
            "implementation": "Remove filler, compress instructions"
        },
        {
            "name": "Cache common responses",
            "benefit": "Avoid redundant API calls",
            "implementation": "Hash inputs and cache outputs"
        },
        {
            "name": "Use completion hints",
            "benefit": "Shorter outputs, less generated tokens",
            "implementation": "Provide expected output format structure"
        },
        {
            "name": "Filter before processing",
            "benefit": "Skip items that don't need processing",
            "implementation": "Quick classification to determine necessity"
        },
    ]

    print("\nCOST REDUCTION STRATEGIES:")
    print("-" * 60)
    for i, s in enumerate(strategies, 1):
        print(f"{i}. {s['name']}")
        print(f"   Benefit: {s['benefit']}")
        print(f"   How: {s['implementation']}")
        print()


# ============================================================================
# SECTION 6: ERROR AGGREGATION AND HANDLING
# ============================================================================

class ErrorAggregator:
    """Aggregates and analyzes errors from batch processing."""

    def __init__(self):
        self.errors_by_type: Dict[str, List[Dict]] = defaultdict(list)
        self.total_errors = 0

    def add_error(self, error_type: str, item: Any, error_message: str):
        """Record an error."""
        self.errors_by_type[error_type].append({
            'item': item,
            'message': error_message,
            'timestamp': time.time()
        })
        self.total_errors += 1

    def get_summary(self) -> Dict[str, Any]:
        """Get error summary statistics."""
        return {
            'total_errors': self.total_errors,
            'error_types': {
                error_type: len(errors)
                for error_type, errors in self.errors_by_type.items()
            },
            'most_common': max(
                self.errors_by_type.items(),
                key=lambda x: len(x[1])
            )[0] if self.errors_by_type else None
        }

    def retry_batch(self, errors: List[Dict],
                   process_fn: Callable,
                   max_retries: int = 3) -> List[Any]:
        """Retry failed items with exponential backoff."""
        results = []

        for error_record in errors:
            item = error_record['item']

            for attempt in range(max_retries):
                try:
                    result = process_fn(item)
                    results.append({'success': True, 'result': result})
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        results.append({
                            'success': False,
                            'error': str(e),
                            'item': item
                        })
                    else:
                        # Exponential backoff
                        time.sleep(2 ** attempt)

        return results


# ============================================================================
# SECTION 7: PROGRESS TRACKING AND REPORTING
# ============================================================================

class ProgressTracker:
    """Tracks and reports batch processing progress."""

    def __init__(self, total_items: int):
        self.total_items = total_items
        self.processed = 0
        self.succeeded = 0
        self.failed = 0
        self.start_time = time.time()
        self.last_update = self.start_time

    def update(self, success: bool):
        """Update progress with new result."""
        self.processed += 1
        if success:
            self.succeeded += 1
        else:
            self.failed += 1

    def get_report(self) -> str:
        """Generate progress report."""
        elapsed = time.time() - self.start_time
        rate = self.processed / elapsed if elapsed > 0 else 0
        eta = (self.total_items - self.processed) / rate if rate > 0 else 0

        return f"""
Batch Processing Progress:
--------------------------
Items: {self.processed}/{self.total_items} ({self.progress():.1f}%)
Successful: {self.succeeded}
Failed: {self.failed}
Rate: {rate:.2f} items/second
Elapsed: {elapsed:.1f}s
ETA: {eta:.1f}s
        """

    def progress(self) -> float:
        """Calculate progress percentage."""
        return (self.processed / self.total_items) * 100 if self.total_items > 0 else 0


# ============================================================================
# SECTION 8: PRACTICAL BATCH PROCESSING EXAMPLE
# ============================================================================

def process_ticket_batch(tickets: List[Dict[str, Any]],
                        api_client) -> List[Dict[str, Any]]:
    """
    Process customer support tickets in batches.

    Args:
        tickets: List of ticket dictionaries
        api_client: API client for processing

    Returns:
        List of processed ticket results
    """
    config = BatchConfig(
        max_batch_size=10,
        max_workers=3,
        rate_limit_per_minute=50
    )

    processor = BatchProcessor(config)
    tracker = ProgressTracker(len(tickets))

    def process_single(ticket: Dict) -> Dict:
        """Process a single ticket."""
        # Build prompt for ticket categorization
        prompt = f"""
Categorize this support ticket and suggest a response.

Ticket:
{ticket['subject']}
{ticket['body']}

Categories: billing, technical, shipping, general, complaint

Output JSON:
{{"category": "<category>", "priority": "<low/medium/high>", "suggested_response": "<response>"}}
"""
        # In real implementation, call API here
        # response = api_client.messages.create(...)
        return {"ticket_id": ticket['id'], "status": "processed"}

    # Process with progress callback
    def progress_callback(stats: ProcessingStats):
        if tracker.processed % 10 == 0:
            print(f"Progress: {tracker.get_report()}")

    # Execute batch processing
    results = processor.process_parallel(
        tickets,
        process_single,
        progress_callback
    )

    return results


# ============================================================================
# SECTION 9: DEMONSTRATION
# ============================================================================

def demonstrate_batch_processing():
    """Demonstrate batch processing patterns."""

    print("=" * 60)
    print("BATCH PROCESSING - PRACTICE 01: OPTIMIZATION")
    print("=" * 60)

    # Demo chunking
    print("\n[DEMO] Chunking strategies...")
    items = [f"item_{i}" for i in range(100)]
    chunks = chunk_list(items, 10)
    print(f"  100 items -> {len(chunks)} chunks of 10")

    # Token-aware chunking
    long_items = ["word " * 100 for _ in range(50)]
    token_chunks = chunk_by_token_estimate(long_items, max_tokens_per_chunk=5000)
    print(f"  50 long items -> {len(token_chunks)} token-aware chunks")

    # Smart chunking
    dict_items = [{"id": i, "text": f"content for item {i}" * 10} for i in range(20)]
    smart_chunks = smart_chunk_items(dict_items, "System prompt here...", max_tokens=5000)
    print(f"  20 dict items -> {len(smart_chunks)} smart chunks")

    # Cost reduction strategies
    reduce_costs_strategies()

    # Progress tracking demo
    print("\n[DEMO] Progress tracking...")
    tracker = ProgressTracker(100)
    for i in range(25):
        tracker.update(success=(i % 10 != 0))  # 90% success rate
    print(tracker.get_report())

    print("\n" + "=" * 60)
    print("WHAT WE HAVE LEARNT:")
    print("=" * 60)
    print("""
1. BATCH CHUNKING STRATEGIES
   - Fixed size: Simple but may waste tokens
   - Token-aware: Maximizes token usage
   - Smart: Considers prompt overhead

2. PARALLEL PROCESSING
   - Use ThreadPoolExecutor for I/O bound tasks
   - Balance workers vs rate limits
   - Monitor for thread safety issues

3. RATE LIMITING
   - Implement token bucket algorithm
   - Add jitter to prevent thundering herd
   - Track remaining quota

4. TOKEN OPTIMIZATION
   - Estimate with 4 chars/token heuristic
   - Remove filler phrases
   - Use abbreviations where appropriate

5. COST REDUCTION
   - Batch similar requests
   - Use smaller models for simple tasks
   - Cache common responses
   - Filter before processing

6. ERROR AGGREGATION
   - Categorize errors by type
   - Track error patterns
   - Implement retry with backoff
   - Never lose failed item info

7. PROGRESS TRACKING
   - Calculate rate (items/second)
   - Estimate time remaining
   - Report success/failure ratio
   - Log for debugging

8. BEST PRACTICES
   - Start with smaller batches for testing
   - Monitor token usage closely
   - Implement proper error handling
   - Save intermediate results
   - Use idempotent operations
""")


if __name__ == "__main__":
    demonstrate_batch_processing()


# ============================================================================
# INTERVIEW Q&A PREP
# ============================================================================
"""
Q: How do you handle API rate limits in batch processing?
A: Implement exponential backoff with jitter, track remaining
   quota, batch requests strategically, and use async processing
   to maximize throughput within limits.

Q: What is the optimal batch size?
A: Depends on: average item size, rate limits, timeout settings.
   Start with 10-20 items, adjust based on performance and errors.

Q: How do you reduce API costs?
A: Use smaller models for simple tasks, cache responses, optimize
   prompts to use fewer tokens, batch requests efficiently.

Q: What happens when a batch item fails?
A: Log the error, continue processing remaining items, aggregate
   errors for later retry, never let one failure stop the batch.

Q: How do you estimate token usage?
A: Use ~4 characters per token as rough estimate. For accurate
   count, use tiktoken or similar library. Account for prompt
   overhead in batch calculations.
"""