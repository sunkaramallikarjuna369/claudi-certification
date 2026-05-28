"""
PRACTICE 01: RATE LIMITING & QUOTA MANAGEMENT
============================================

Rate Limiting Concepts:
- API rate limits prevent abuse and ensure fair usage
- Quotas track usage over time periods
- Backoff strategies handle rate limit errors gracefully
- Budget tracking prevents unexpected costs

Key Strategies:
1. Rate limit detection and handling
2. Exponential backoff retry
3. Quota tracking and management
4. Concurrent request limiting
5. Cost budgeting
6. Graceful degradation
"""

import os
import time
from datetime import datetime, timedelta
from anthropic import Anthropic

# =============================================================================
# SETUP: Load environment and initialize client
# =============================================================================

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(dotenv_path):
    with open(dotenv_path) as f:
        for line in f:
            if 'ANTHROPIC_API_KEY' in line and '=' in line:
                key_value = line.split('=', 1)[1].strip()
                if key_value and not key_value.startswith('#'):
                    os.environ['ANTHROPIC_API_KEY'] = key_value

client = Anthropic()
MODEL = "claude-haiku-4-5-20250601"


# =============================================================================
# SCENARIO 1: Basic Rate Limit Detection
# =============================================================================

class RateLimitError(Exception):
    """Exception raised when rate limit is hit"""
    def __init__(self, retry_after=None):
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded. Retry after {retry_after}s")


def simulate_rate_limit_check():
    """
    REAL-TIME SCENARIO: Detecting rate limit errors

    COMMON MISTAKE: Not checking for rate limit errors
    BEST PRACTICE: Check response headers and error types

    Interview Q: How do you detect rate limit errors?
    A: Check for 429 status code or rate_limit_error exception.
       Read Retry-After header to know when to retry.
    """
    print("=" * 60)
    print("SCENARIO 1: Basic Rate Limit Detection")
    print("=" * 60)

    # Simulate API response with rate limit
    class MockResponse:
        def __init__(self, status_code, headers=None):
            self.status_code = status_code
            self.headers = headers or {}

    def check_rate_limit(response):
        """Check if response indicates rate limit"""
        if response.status_code == 429:
            retry_after = response.headers.get('Retry-After', 60)
            raise RateLimitError(retry_after=int(retry_after))
        return True

    # Test with normal response
    normal_response = MockResponse(200)
    try:
        check_rate_limit(normal_response)
        print("Normal response: OK (no rate limit)")
    except RateLimitError:
        print("Normal response: Rate limited!")

    # Test with rate limited response
    limited_response = MockResponse(429, {'Retry-After': '30'})
    try:
        check_rate_limit(limited_response)
        print("Rate limited response: OK (no rate limit)")
    except RateLimitError as e:
        print(f"Rate limited response: {e}")
        print(f"  Wait {e.retry_after} seconds before retry")
    print()


# =============================================================================
# SCENARIO 2: Exponential Backoff Retry
# =============================================================================

def demonstrate_exponential_backoff():
    """
    REAL-TIME SCENARIO: Implementing retry with exponential backoff

    BEST PRACTICE: Start with small delay, double each retry
    - Retry 1: 1 second
    - Retry 2: 2 seconds
    - Retry 3: 4 seconds
    - Retry N: min(initial * 2^N, max_delay)

    Interview Q: What is exponential backoff?
    A: A retry strategy where wait time doubles with each attempt.
       Prevents hammering API during recovery periods.

    COMMON MISTAKE: Fixed interval retries (too aggressive)
    """
    print("=" * 60)
    print("SCENARIO 2: Exponential Backoff Retry")
    print("=" * 60)

    def exponential_backoff(attempt, initial_delay=1, max_delay=60):
        """Calculate delay for given attempt"""
        delay = initial_delay * (2 ** attempt)
        return min(delay, max_delay)

    print("Exponential backoff delays:")
    print("  Attempt 1: ", end="")
    delay = exponential_backoff(0)
    print(f"{delay}s (max: 60s)")

    print("  Attempt 2: ", end="")
    delay = exponential_backoff(1)
    print(f"{delay}s")

    print("  Attempt 3: ", end="")
    delay = exponential_backoff(2)
    print(f"{delay}s")

    print("  Attempt 4: ", end="")
    delay = exponential_backoff(3)
    print(f"{delay}s")

    print("  Attempt 5: ", end="")
    delay = exponential_backoff(4)
    print(f"{delay}s")

    print("\nJitter version (add randomness to prevent thundering herd):")
    import random
    for attempt in range(5):
        base_delay = exponential_backoff(attempt)
        jitter = random.uniform(0, base_delay * 0.1)
        total_delay = base_delay + jitter
        print(f"  Attempt {attempt + 1}: {total_delay:.2f}s (+ jitter)")
    print()


# =============================================================================
# SCENARIO 3: Retry Decorator Implementation
# =============================================================================

def retry_with_backoff(max_retries=3, initial_delay=1):
    """
    DECORATOR: Retry function with exponential backoff

    BEST PRACTICE: Use decorators for reusable retry logic
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except RateLimitError as e:
                    if attempt == max_retries - 1:
                        raise
                    delay = exponential_backoff(attempt)
                    if e.retry_after:
                        delay = max(delay, e.retry_after)
                    print(f"  Retry {attempt + 1}/{max_retries} after {delay}s")
                    time.sleep(delay)
        return wrapper
    return decorator


def demonstrate_retry_decorator():
    """Show retry decorator usage"""
    print("=" * 60)
    print("SCENARIO 3: Retry Decorator Implementation")
    print("=" * 60)

    call_count = 0

    @retry_with_backoff(max_retries=3, initial_delay=1)
    def unreliable_api_call():
        """Simulate API that fails twice then succeeds"""
        global call_count
        call_count += 1
        if call_count < 3:
            raise RateLimitError(retry_after=1)
        return "Success!"

    print("Calling unreliable API (fails twice, succeeds on 3rd attempt):")
    result = unreliable_api_call()
    print(f"  Result: {result}")
    print(f"  Total calls made: {call_count}")
    print()


# =============================================================================
# SCENARIO 4: Quota Manager Class
# =============================================================================

class QuotaManager:
    """
    QUOTA MANAGER: Track and enforce usage quotas

    Interview Q: How do you manage API quotas?
    A: Track requests over time windows. Enforce limits by
       queuing or rejecting requests that would exceed quota.

    Features:
    - Track requests per time window
    - Warn when approaching limits
    - Reject when exceeding quota
    """

    def __init__(self, requests_per_minute=50, requests_per_day=10000):
        self.requests_per_minute = requests_per_minute
        self.requests_per_day = requests_per_day
        self.minute_requests = []
        self.day_requests = []

    def _clean_old_requests(self, requests_list, max_age_seconds):
        """Remove requests older than max_age"""
        now = time.time()
        return [r for r in requests_list if now - r < max_age_seconds]

    def check_quota(self):
        """Check if we can make a request"""
        now = time.time()

        # Clean old requests
        self.minute_requests = self._clean_old_requests(self.minute_requests, 60)
        self.day_requests = self._clean_old_requests(self.day_requests, 86400)

        # Check limits
        if len(self.minute_requests) >= self.requests_per_minute:
            return False, f"Minute limit reached ({self.requests_per_minute}/min)"

        if len(self.day_requests) >= self.requests_per_day:
            return False, f"Day limit reached ({self.requests_per_day}/day)"

        return True, "OK"

    def record_request(self):
        """Record a request for quota tracking"""
        now = time.time()
        self.minute_requests.append(now)
        self.day_requests.append(now)

    def get_stats(self):
        """Get current quota stats"""
        self.minute_requests = self._clean_old_requests(self.minute_requests, 60)
        self.day_requests = self._clean_old_requests(self.day_requests, 86400)

        return {
            "minute_used": len(self.minute_requests),
            "minute_limit": self.requests_per_minute,
            "day_used": len(self.day_requests),
            "day_limit": self.requests_per_day,
            "minute_percent": (len(self.minute_requests) / self.requests_per_minute) * 100
        }


def demonstrate_quota_manager():
    """Show quota manager in action"""
    print("=" * 60)
    print("SCENARIO 4: Quota Manager Class")
    print("=" * 60)

    quota = QuotaManager(requests_per_minute=10, requests_per_day=100)

    print("Testing quota manager (limit: 10/min, 100/day):")
    for i in range(15):
        can_proceed, status = quota.check_quota()
        if can_proceed:
            quota.record_request()
            print(f"  Request {i + 1}: Allowed")
        else:
            print(f"  Request {i + 1}: Rejected - {status}")

    stats = quota.get_stats()
    print(f"\nQuota stats: {stats['minute_used']}/{stats['minute_limit']} per minute")
    print()


# =============================================================================
# SCENARIO 5: Concurrent Request Limiting
# =============================================================================

import threading
from queue import Queue


class ConcurrentLimiter:
    """
    CONCURRENT LIMITER: Limit simultaneous API calls

    BEST PRACTICE: Use semaphore to limit concurrency
    - Prevents overwhelming the API
    - Ensures fair resource allocation
    - Reduces connection errors

    Interview Q: How do you limit concurrent API calls?
    A: Use a semaphore or token bucket. Semaphore allows
       N concurrent operations, blocks when full.
    """

    def __init__(self, max_concurrent=5):
        self.semaphore = threading.Semaphore(max_concurrent)
        self.active_count = 0
        self.lock = threading.Lock()

    def __enter__(self):
        self.semaphore.acquire()
        with self.lock:
            self.active_count += 1
        return self

    def __exit__(self, *args):
        with self.lock:
            self.active_count -= 1
        self.semaphore.release()

    def get_active_count(self):
        with self.lock:
            return self.active_count


def demonstrate_concurrent_limiter():
    """Show concurrent limiter pattern"""
    print("=" * 60)
    print("SCENARIO 5: Concurrent Request Limiting")
    print("=" * 60)

    limiter = ConcurrentLimiter(max_concurrent=3)

    print("Concurrent limiter (max 3 concurrent):")
    print("  Simulating concurrent access...")

    # Simulate acquiring slots
    for i in range(5):
        acquired = limiter.semaphore.acquire(blocking=False)
        if acquired:
            with limiter.lock:
                limiter.active_count += 1
            print(f"  Request {i + 1}: Acquired slot (active: {limiter.active_count})")
        else:
            print(f"  Request {i + 1}: No slot available (blocked)")

    print(f"\n  Total active: {limiter.active_count}")
    print()


# =============================================================================
# SCENARIO 6: Cost Budget Tracker
# =============================================================================

class CostBudgetTracker:
    """
    COST BUDGET TRACKER: Monitor and control API spending

    Interview Q: How do you prevent unexpected API costs?
    A: Implement budget tracking with warning thresholds.
       Set hard limits and alert levels (e.g., 80% warning).

    Features:
    - Track spending over time
    - Alert at thresholds
    - Stop requests when budget exhausted
    """

    def __init__(self, daily_budget=100.0, warning_percent=80):
        self.daily_budget = daily_budget
        self.warning_percent = warning_percent
        self.total_spent = 0.0
        self.requests_today = []

    def add_cost(self, tokens_used, cost_per_token=0.00001):
        """Add cost of a request"""
        cost = tokens_used * cost_per_token
        self.total_spent += cost
        self.requests_today.append({
            "cost": cost,
            "tokens": tokens_used,
            "timestamp": time.time()
        })
        return cost

    def check_budget(self):
        """Check if we can make more requests"""
        used_percent = (self.total_spent / self.daily_budget) * 100

        if self.total_spent >= self.daily_budget:
            return False, "Budget exhausted", used_percent

        if used_percent >= self.warning_percent:
            return True, f"Warning: {used_percent:.0f}% of budget used", used_percent

        return True, "OK", used_percent

    def get_stats(self):
        """Get spending statistics"""
        return {
            "total_spent": self.total_spent,
            "budget": self.daily_budget,
            "remaining": self.daily_budget - self.total_spent,
            "percent_used": (self.total_spent / self.daily_budget) * 100,
            "requests_today": len(self.requests_today)
        }


def demonstrate_cost_tracker():
    """Show cost budget tracking"""
    print("=" * 60)
    print("SCENARIO 6: Cost Budget Tracker")
    print("=" * 60)

    tracker = CostBudgetTracker(daily_budget=10.00)

    print("Budget: $10/day, Warning at 80%")
    print("\nSimulating requests:")

    for i in range(5):
        tokens = 1000 + (i * 500)
        cost = tracker.add_cost(tokens)
        can_proceed, status, percent = tracker.check_budget()

        print(f"  Request {i + 1}: {tokens} tokens, ${cost:.4f}, Status: {status}")

    stats = tracker.get_stats()
    print(f"\nBudget stats:")
    print(f"  Spent: ${stats['total_spent']:.2f} / ${stats['budget']:.2f}")
    print(f"  Remaining: ${stats['remaining']:.2f}")
    print(f"  Requests: {stats['requests_today']}")
    print()


# =============================================================================
# SCENARIO 7: Graceful Degradation
# =============================================================================

def demonstrate_graceful_degradation():
    """
    REAL-TIME SCENARIO: Handling rate limits gracefully

    BEST PRACTICE: Have fallback strategies when rate limited
    - Queue requests for later processing
    - Return cached responses when possible
    - Show user-friendly error messages
    - Implement circuit breaker pattern

    Interview Q: How do you handle rate limit errors gracefully?
    A: Implement circuit breaker and fallback. When rate limited,
       queue requests, use cache, or return degraded response.
    """
    print("=" * 60)
    print("SCENARIO 7: Graceful Degradation")
    print("=" * 60)

    class GracefulDegradationHandler:
        def __init__(self):
            self.fallback_cache = {}
            self.request_queue = []
            self.circuit_open = False

        def handle_rate_limit(self, request, retry_after=60):
            """Handle rate limit with graceful degradation"""
            print(f"  Rate limited! Waiting {retry_after}s")

            # Strategy 1: Queue for later
            self.request_queue.append(request)
            print(f"  Queued request. Queue size: {len(self.request_queue)}")

            # Strategy 2: Return fallback if available
            cache_key = str(request)[:50]
            if cache_key in self.fallback_cache:
                print(f"  Returning cached response instead")
                return self.fallback_cache[cache_key]

            # Strategy 3: Circuit breaker
            if len(self.request_queue) > 10:
                self.circuit_open = True
                print(f"  Circuit breaker OPEN - rejecting new requests")

            return None

        def add_to_cache(self, request, response):
            """Cache response for fallback"""
            cache_key = str(request)[:50]
            self.fallback_cache[cache_key] = response

    handler = GracefulDegradationHandler()

    # Simulate rate limited requests
    for i in range(3):
        request = {"user_id": i, "query": f"query_{i}"}
        result = handler.handle_rate_limit(request, retry_after=5)
        if result:
            print(f"  Got fallback: {result}")

    print(f"\n  Queue size: {len(handler.request_queue)}")
    print(f"  Cache size: {len(handler.fallback_cache)}")
    print()


# =============================================================================
# SCENARIO 8: Real API Call with Rate Limit Handling
# =============================================================================

def demonstrate_real_api_with_rate_limit():
    """Show real API call with rate limit handling"""
    print("=" * 60)
    print("SCENARIO 8: Real API with Rate Limit Handling")
    print("=" * 60)

    quota = QuotaManager(requests_per_minute=50)
    tracker = CostBudgetTracker(daily_budget=10.00)

    try:
        # Check quota first
        can_proceed, status = quota.check_quota()
        if not can_proceed:
            print(f"Quota exceeded: {status}")
            return

        # Make API call
        print("Making API call...")
        response = client.messages.create(
            model=MODEL,
            max_tokens=100,
            messages=[{"role": "user", "content": "Hello"}]
        )

        # Record usage
        quota.record_request()
        total_tokens = response.usage.input_tokens + response.usage.output_tokens
        cost = tracker.add_cost(total_tokens)

        print(f"Success!")
        print(f"  Tokens used: {total_tokens}")
        print(f"  Cost: ${cost:.6f}")
        print(f"  Quota: {quota.get_stats()['minute_used']}/50 per minute")
        print(f"  Budget: ${tracker.get_stats()['total_spent']:.2f}/$10.00")

    except Exception as e:
        error_msg = str(e)
        if "rate_limit" in error_msg.lower() or "429" in error_msg:
            print(f"Rate limit error: {e}")
            print("  Implementing backoff and retry...")
        else:
            print(f"Other error: {type(e).__name__}: {e}")
    print()


# =============================================================================
# MAIN: Run All Scenarios
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("RATE LIMITING & QUOTA MANAGEMENT - PRACTICE FILE")
    print("=" * 60 + "\n")

    simulate_rate_limit_check()
    demonstrate_exponential_backoff()
    demonstrate_retry_decorator()
    demonstrate_quota_manager()
    demonstrate_concurrent_limiter()
    demonstrate_cost_tracker()
    demonstrate_graceful_degradation()
    demonstrate_real_api_with_rate_limit()

    print("\n" + "=" * 60)
    print("WHAT WE HAVE LEARNT")
    print("=" * 60)
    print("""
1. RATE LIMIT DETECTION
   - Check for 429 status codes
   - Read Retry-After header
   - Handle rate_limit_error exceptions

2. EXPONENTIAL BACKOFF
   - Delay doubles with each retry: 1s, 2s, 4s, 8s...
   - Cap at maximum delay (e.g., 60s)
   - Add jitter to prevent thundering herd

3. RETRY DECORATORS
   - Reusable retry logic with decorators
   - Integrate backoff and rate limit handling
   - Clean error propagation

4. QUOTA MANAGEMENT
   - Track requests over time windows
   - Enforce per-minute and per-day limits
   - Reject or queue excess requests

5. CONCURRENT LIMITING
   - Use semaphore to limit simultaneous calls
   - Prevents overwhelming API
   - Ensures fair resource allocation

6. COST BUDGET TRACKING
   - Monitor spending against budget
   - Alert at warning thresholds (80%)
   - Stop requests when exhausted

7. GRACEFUL DEGRADATION
   - Queue requests when rate limited
   - Use cached responses as fallback
   - Implement circuit breaker for sustained failures

INTERVIEW QUESTIONS & ANSWERS:
------------------------------
Q: What is exponential backoff?
A: Retry strategy where wait time doubles with each attempt
   (1s, 2s, 4s, 8s...). Prevents hammering API during recovery.

Q: How do you handle rate limit errors?
A: Catch error, read Retry-After, implement exponential backoff
   retry. Queue excess requests for later processing.

Q: How do you prevent unexpected API costs?
A: Implement budget tracking with warning thresholds (80%).
   Set hard limits and stop requests when budget exhausted.

Q: How do you limit concurrent API calls?
A: Use semaphore to limit simultaneous operations.
   Blocks when max concurrent reached.
""")