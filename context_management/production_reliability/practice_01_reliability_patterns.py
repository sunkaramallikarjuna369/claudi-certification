"""
PRACTICE 01: PRODUCTION RELIABILITY PATTERNS
============================================

Production Patterns:
- Error handling best practices
- Circuit breaker pattern
- Fallback strategies
- Timeout configuration
- Graceful degradation
- Health checks
- Recovery mechanisms

Key Patterns:
1. Circuit breaker
2. Retry with backoff
3. Fallback responses
4. Bulkhead isolation
5. Health check endpoints
"""

import os
import time
from datetime import datetime
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
# SCENARIO 1: Circuit Breaker Pattern
# =============================================================================

class CircuitBreaker:
    """
    CIRCUIT BREAKER: Prevent cascade failures

    Interview Q: What is a circuit breaker pattern?
    A: A pattern that stops calling a failing service repeatedly.
       After enough failures, the circuit "opens" and calls fail fast.
       After a timeout, it allows a "test" call to see if service recovered.

    States:
    - CLOSED: Normal operation, calls pass through
    - OPEN: Too many failures, calls fail fast without calling service
    - HALF-OPEN: Testing if service recovered

    BEST PRACTICE: Prevent cascade failures by failing fast
    """

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

    def __init__(self, failure_threshold=5, timeout_seconds=30):
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.failure_count = 0
        self.last_failure_time = None
        self.state = self.CLOSED

    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        # Check if circuit should transition
        self._check_transition()

        # If open, fail fast
        if self.state == self.OPEN:
            raise CircuitBreakerOpenError("Circuit is OPEN - failing fast")

        # Attempt the call
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _check_transition(self):
        """Check if circuit should transition states"""
        if self.state == self.OPEN:
            # Check if timeout expired
            if self.last_failure_time:
                elapsed = time.time() - self.last_failure_time
                if elapsed >= self.timeout_seconds:
                    self.state = self.HALF_OPEN
                    print(f"  Circuit: OPEN -> HALF_OPEN (timeout expired)")

    def _on_success(self):
        """Handle successful call"""
        if self.state == self.HALF_OPEN:
            self.state = self.CLOSED
            print(f"  Circuit: HALF_OPEN -> CLOSED (success)")
        self.failure_count = 0

    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = self.OPEN
            print(f"  Circuit: CLOSED -> OPEN (failure threshold reached)")


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open"""
    pass


def demonstrate_circuit_breaker():
    """Show circuit breaker pattern"""
    print("=" * 60)
    print("SCENARIO 1: Circuit Breaker Pattern")
    print("=" * 60)

    cb = CircuitBreaker(failure_threshold=3, timeout_seconds=5)

    # Simulate failing function
    call_count = [0]

    def unreliable_function():
        call_count[0] += 1
        if call_count[0] <= 5:
            raise Exception("Service unavailable")
        return "Success!"

    print("Circuit breaker with failure_threshold=3:")
    print("\nAttempting calls:")

    for i in range(7):
        try:
            result = cb.call(unreliable_function)
            print(f"  Call {i+1}: Success - {result}")
        except CircuitBreakerOpenError:
            print(f"  Call {i+1}: Fast-fail (circuit OPEN)")
        except Exception as e:
            print(f"  Call {i+1}: Error - {e}")

    print(f"\nFinal circuit state: {cb.state}")
    print()


# =============================================================================
# SCENARIO 2: Retry with Backoff
# =============================================================================

def demonstrate_retry_pattern():
    """
    REAL-TIME SCENARIO: Retry failed operations with backoff

    Interview Q: How do you implement reliable retries?
    A: Use exponential backoff with jitter. Retry up to N times.
       Distinguish between retryable and non-retryable errors.

    BEST PRACTICE:
    - Retryable: Network errors, timeouts, rate limits
    - Non-retryable: Auth errors, bad requests, server errors (5xx)
    """
    print("=" * 60)
    print("SCENARIO 2: Retry with Backoff")
    print("=" * 60)

    def exponential_backoff(attempt, base_delay=1, max_delay=32):
        """Calculate delay with exponential backoff"""
        delay = min(base_delay * (2 ** attempt), max_delay)
        # Add jitter (0-10% of delay)
        import random
        jitter = random.uniform(0, delay * 0.1)
        return delay + jitter

    class RetryHandler:
        def __init__(self, max_attempts=3):
            self.max_attempts = max_attempts

        def retry(self, func):
            """Retry function with exponential backoff"""
            last_error = None

            for attempt in range(self.max_attempts):
                try:
                    return func()
                except Exception as e:
                    last_error = e
                    if attempt < self.max_attempts - 1:
                        delay = exponential_backoff(attempt)
                        print(f"  Attempt {attempt + 1} failed: {e}")
                        print(f"  Retrying in {delay:.2f}s...")
                        time.sleep(delay)

            raise last_error

    # Simulate unreliable operation
    attempts = [0]

    def unreliable_operation():
        attempts[0] += 1
        if attempts[0] < 3:
            raise Exception(f"Attempt {attempts[0]} failed")
        return "Operation succeeded!"

    handler = RetryHandler(max_attempts=3)

    print("Attempting unreliable operation (fails 2 times, succeeds 3rd):")
    try:
        result = handler.retry(unreliable_operation)
        print(f"\nResult: {result}")
    except Exception as e:
        print(f"Final failure: {e}")
    print()


# =============================================================================
# SCENARIO 3: Fallback Strategies
# =============================================================================

class FallbackManager:
    """
    FALLBACK MANAGER: Provide alternatives when primary fails

    Interview Q: How do you handle failures gracefully?
    A: Implement fallback strategies. When primary service fails,
       return cached response, default value, or degraded result.

    BEST PRACTICE: Always have a fallback
    """

    def __init__(self):
        self.cache = {}

    def execute_with_fallback(self, primary_func, fallback_func, cache_key=None):
        """
        Execute primary function with fallback on failure

        Args:
            primary_func: Main function to try
            fallback_func: Backup function to use on failure
            cache_key: Optional cache key for result caching
        """
        # Check cache first
        if cache_key and cache_key in self.cache:
            return self.cache[cache_key], "CACHED"

        # Try primary
        try:
            result = primary_func()
            if cache_key:
                self.cache[cache_key] = result
            return result, "PRIMARY"
        except Exception as e:
            print(f"  Primary failed: {e}")

        # Try fallback
        try:
            if cache_key and cache_key in self.cache:
                return self.cache[cache_key], "CACHED"
            result = fallback_func()
            return result, "FALLBACK"
        except Exception as e:
            print(f"  Fallback also failed: {e}")

        return None, "FAILED"


def demonstrate_fallback():
    """Show fallback strategies"""
    print("=" * 60)
    print("SCENARIO 3: Fallback Strategies")
    print("=" * 60)

    manager = FallbackManager()

    def primary_llm_call():
        raise Exception("API unavailable")

    def fallback_response():
        return "I apologize, but I'm currently experiencing technical difficulties. Please try again later."

    print("Executing with fallback:")
    result, source = manager.execute_with_fallback(
        primary_llm_call,
        fallback_response,
        cache_key="greeting"
    )

    print(f"  Result: {result}")
    print(f"  Source: {source}")
    print()


# =============================================================================
# SCENARIO 4: Timeout Configuration
# =============================================================================

def demonstrate_timeout_pattern():
    """
    REAL-TIME SCENARIO: Setting appropriate timeouts

    Interview Q: How do you set timeout values?
    A: Set timeouts based on expected response time + buffer.
       Consider: network latency, processing time, queue time.
       Too short = false failures, too long = slow recovery.

    BEST PRACTICE: Always have timeouts, never block forever
    """
    print("=" * 60)
    print("SCENARIO 4: Timeout Configuration")
    print("=" * 60)

    class TimeoutConfig:
        """Recommended timeout values for different operations"""

        # API call timeouts (in seconds)
        API_TIMEOUT = 30
        API_TIMEOUT_WITH_RETRY = 120  # With retries

        # Connection timeouts
        CONNECT_TIMEOUT = 5

        # Read timeouts
        READ_TIMEOUT = 25

        # Total budget
        TOTAL_BUDGET = 30

    config = TimeoutConfig()

    print("Recommended timeout configuration:")
    print(f"  API timeout: {config.API_TIMEOUT}s")
    print(f"  API timeout (with retry): {config.API_TIMEOUT_WITH_RETRY}s")
    print(f"  Connect timeout: {config.CONNECT_TIMEOUT}s")
    print(f"  Read timeout: {config.READ_TIMEOUT}s")
    print(f"  Total budget: {config.TOTAL_BUDGET}s")
    print()

    # Demonstrate timeout selection
    scenarios = [
        {"type": "Simple query", "timeout": 10},
        {"type": "Complex analysis", "timeout": 30},
        {"type": "Batch processing", "timeout": 120},
    ]

    print("Timeout by scenario:")
    for scenario in scenarios:
        print(f"  {scenario['type']}: {scenario['timeout']}s")
    print()


# =============================================================================
# SCENARIO 5: Graceful Degradation
# =============================================================================

class GracefulDegradationHandler:
    """
    GRACEFUL DEGRADATION: Reduce functionality instead of complete failure

    Interview Q: How do you implement graceful degradation?
    A: When full service unavailable, provide reduced functionality.
       Example: If AI unavailable, use rule-based responses.

    Levels of degradation:
    1. Cached response
    2. Simplified response
    3. Static response
    4. Error message
    """

    def __init__(self):
        self.degradation_levels = [
            {"level": 1, "name": "CACHED", "action": "Return cached response"},
            {"level": 2, "name": "SIMPLIFIED", "action": "Use simpler model"},
            {"level": 3, "name": "STATIC", "action": "Return predefined response"},
            {"level": 4, "name": "ERROR", "action": "Return user-friendly error"},
        ]

    def handle_failure(self, error, context=None):
        """Handle failure with appropriate degradation level"""
        print(f"Handling failure: {error}")

        # Try each degradation level in order
        for level in self.degradation_levels:
            print(f"  Trying: {level['name']} - {level['action']}")

            if level['name'] == 'CACHED':
                if context and 'cache' in context:
                    return context['cache'], level['name']

            elif level['name'] == 'STATIC':
                return "Thank you for your message. Our team will respond shortly.", level['name']

            elif level['name'] == 'ERROR':
                return "We encountered an issue. Please try again later.", level['name']

        return None, "COMPLETE_FAILURE"


def demonstrate_graceful_degradation():
    """Show graceful degradation"""
    print("=" * 60)
    print("SCENARIO 5: Graceful Degradation")
    print("=" * 60)

    handler = GracefulDegradationHandler()

    print("Processing request with multiple failures:")

    # Simulate context with cache
    context = {
        'cache': "Your previous order #12345 is being processed.",
        'user_id': 'user_123'
    }

    result, level = handler.handle_failure("API timeout", context)
    print(f"\nFinal result: {result}")
    print(f"Degradation level: {level}")
    print()


# =============================================================================
# SCENARIO 6: Health Check Pattern
# =============================================================================

class HealthChecker:
    """
    HEALTH CHECK: Verify system components are working

    Interview Q: How do you implement health checks?
    A: Check each component (API, cache, database) separately.
       Return status for each and overall health.

    BEST PRACTICE:
    - Liveness check: Is the process running?
    - Readiness check: Can it handle requests?
    """

    def __init__(self):
        self.checks = {
            "api": self._check_api,
            "cache": self._check_cache,
        }

    def _check_api(self):
        """Check if API is responsive"""
        try:
            # Simple API check
            return True, "API responding"
        except Exception as e:
            return False, f"API error: {e}"

    def _check_cache(self):
        """Check if cache is available"""
        try:
            return True, "Cache available"
        except Exception as e:
            return False, f"Cache error: {e}"

    def health_check(self):
        """Run all health checks"""
        results = {}
        all_healthy = True

        for name, check_func in self.checks.items():
            healthy, message = check_func()
            results[name] = {"healthy": healthy, "message": message}
            if not healthy:
                all_healthy = False

        return {
            "status": "HEALTHY" if all_healthy else "UNHEALTHY",
            "checks": results,
            "timestamp": datetime.now().isoformat()
        }

    def readiness_check(self):
        """Check if ready to serve traffic"""
        health = self.health_check()
        return health["status"] == "HEALTHY"


def demonstrate_health_check():
    """Show health check pattern"""
    print("=" * 60)
    print("SCENARIO 6: Health Check Pattern")
    print("=" * 60)

    checker = HealthChecker()

    print("Running health check:")
    result = checker.health_check()

    print(f"\nHealth Status: {result['status']}")
    print(f"Timestamp: {result['timestamp']}")
    print("\nComponent checks:")
    for component, status in result['checks'].items():
        health_icon = "[OK]" if status['healthy'] else "[FAIL]"
        print(f"  {component}: {health_icon} {status['message']}")

    print(f"\nReady to serve: {'Yes' if checker.readiness_check() else 'No'}")
    print()


# =============================================================================
# SCENARIO 7: Bulkhead Isolation
# =============================================================================

import threading


class BulkheadIsolation:
    """
    BULKHEAD ISOLATION: Limit resource usage per operation

    Interview Q: What is bulkhead isolation?
    A: Isolating different operations so one failure doesn't
       affect others. Like ship bulkheads - if one floods,
       others stay dry.

    BEST PRACTICE: Limit concurrent calls per operation type
    """

    def __init__(self):
        self.semaphores = {
            "critical": threading.Semaphore(10),   # 10 concurrent critical
            "standard": threading.Semaphore(50),   # 50 concurrent standard
            "background": threading.Semaphore(100), # 100 concurrent background
        }
        self.active_counts = {k: 0 for k in self.semaphores}
        self.lock = threading.Lock()

    def execute(self, operation_type, func):
        """Execute function with bulkhead isolation"""
        if operation_type not in self.semaphores:
            raise ValueError(f"Unknown operation type: {operation_type}")

        sem = self.semaphores[operation_type]

        # Acquire slot
        sem.acquire()
        with self.lock:
            self.active_counts[operation_type] += 1

        try:
            return func()
        finally:
            with self.lock:
                self.active_counts[operation_type] -= 1
            sem.release()

    def get_stats(self):
        """Get current bulkhead stats"""
        return dict(self.active_counts)


def demonstrate_bulkhead():
    """Show bulkhead isolation"""
    print("=" * 60)
    print("SCENARIO 7: Bulkhead Isolation")
    print("=" * 60)

    bulkhead = BulkheadIsolation()

    print("Bulkhead limits:")
    print("  Critical: 10 concurrent")
    print("  Standard: 50 concurrent")
    print("  Background: 100 concurrent")
    print()

    # Simulate acquiring slots
    operations = ["critical", "standard", "background"]

    print("Simulating concurrent operations:")
    for op_type in operations:
        count = bulkhead.semaphores[op_type]._value
        print(f"  {op_type}: {count} slots available")

    stats = bulkhead.get_stats()
    print(f"\nCurrent active: {stats}")
    print()


# =============================================================================
# SCENARIO 8: Recovery Pattern
# =============================================================================

class RecoveryManager:
    """
    RECOVERY MANAGER: Handle recovery after failures

    Interview Q: How do you implement recovery mechanisms?
    A: After failure, implement cool-down period, gradually
       increase load, verify health before full operation.

    BEST PRACTICE:
    1. Detect failure
    2. Open circuit (stop calling)
    3. Cool-down period
    4. Test with limited calls
    5. Gradually restore full capacity
    """

    def __init__(self):
        self.recovery_steps = [
            {"step": 1, "name": "COOLDOWN", "delay": 30, "limit": 1},
            {"step": 2, "name": "LIGHT_LOAD", "delay": 60, "limit": 5},
            {"step": 3, "name": "MEDIUM_LOAD", "delay": 120, "limit": 20},
            {"step": 4, "name": "FULL_RECOVERY", "delay": 0, "limit": -1},
        ]

    def get_recovery_plan(self):
        """Get step-by-step recovery plan"""
        return self.recovery_steps

    def execute_recovery(self, callback):
        """Execute recovery plan"""
        print("Executing recovery plan:")

        for step_info in self.recovery_steps:
            print(f"\n  Step {step_info['step']}: {step_info['name']}")
            print(f"    Delay: {step_info['delay']}s")

            if step_info['limit'] > 0:
                print(f"    Rate limit: {step_info['limit']} requests")
            else:
                print(f"    Rate limit: Full capacity")

            # Simulate recovery time
            if step_info['delay'] > 0:
                print(f"    (Waiting {step_info['delay']}s...)")

            # Execute callback for this step
            callback(step_info)


def demonstrate_recovery():
    """Show recovery pattern"""
    print("=" * 60)
    print("SCENARIO 8: Recovery Pattern")
    print("=" * 60)

    manager = RecoveryManager()

    print("Recovery Plan:")
    for step in manager.get_recovery_plan():
        limit_str = f"{step['limit']} req" if step['limit'] > 0 else "Full"
        print(f"  {step['step']}. {step['name']}: {step['delay']}s delay, {limit_str} rate")

    print("\nExecuting recovery (simulation):")
    def recovery_step(step_info):
        print(f"    -> Step {step_info['step']} ({step_info['name']}) completed")

    # Note: Not actually waiting in demo
    print("(Skipping delays in demo mode)")
    print()


# =============================================================================
# SCENARIO 9: Real API with Reliability Patterns
# =============================================================================

def demonstrate_real_api_reliability():
    """Show real API call with reliability patterns"""
    print("=" * 60)
    print("SCENARIO 9: Real API with Reliability Patterns")
    print("=" * 60)

    # Setup reliability components
    cb = CircuitBreaker(failure_threshold=3, timeout_seconds=10)
    fallback_manager = FallbackManager()
    health_checker = HealthChecker()

    print("Reliability components initialized:")
    print(f"  Circuit breaker: threshold=3, timeout=10s")
    print(f"  Fallback: enabled")
    print(f"  Health check: enabled")
    print()

    # Pre-flight checks
    print("Pre-flight checks:")
    health = health_checker.health_check()
    print(f"  System health: {health['status']}")

    try:
        print("\nMaking API call with reliability protection...")

        def primary_call():
            return client.messages.create(
                model=MODEL,
                max_tokens=50,
                messages=[{"role": "user", "content": "Hi"}]
            )

        response = cb.call(primary_call)
        print(f"  Success! Response: {response.content[0].text[:50]}...")

    except CircuitBreakerOpenError:
        print("  Circuit breaker open - using fallback")
        fallback_manager.execute_with_fallback(
            lambda: None,
            lambda: "Service temporarily unavailable. Please try again."
        )
    except Exception as e:
        print(f"  Error: {type(e).__name__}: {e}")
    print()


# =============================================================================
# MAIN: Run All Scenarios
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("PRODUCTION RELIABILITY PATTERNS - PRACTICE FILE")
    print("=" * 60 + "\n")

    demonstrate_circuit_breaker()
    demonstrate_retry_pattern()
    demonstrate_fallback()
    demonstrate_timeout_pattern()
    demonstrate_graceful_degradation()
    demonstrate_health_check()
    demonstrate_bulkhead()
    demonstrate_recovery()
    demonstrate_real_api_reliability()

    print("\n" + "=" * 60)
    print("WHAT WE HAVE LEARNT")
    print("=" * 60)
    print("""
1. CIRCUIT BREAKER PATTERN
   - States: CLOSED (normal) -> OPEN (failing fast) -> HALF_OPEN (testing)
   - Prevents cascade failures by failing fast
   - Transitions back to CLOSED after successful test

2. RETRY WITH BACKOFF
   - Exponential backoff: 1s, 2s, 4s, 8s...
   - Add jitter to prevent thundering herd
   - Distinguish retryable vs non-retryable errors

3. FALLBACK STRATEGIES
   - Primary fails -> Try cached -> Try fallback -> Return error
   - Always have a fallback ready
   - Cache successful responses for fallback use

4. TIMEOUT CONFIGURATION
   - Set timeouts based on expected response time + buffer
   - Connect timeout: ~5s
   - API timeout: ~30s (with retries: ~120s)
   - Never block forever

5. GRACEFUL DEGRADATION
   - Levels: Cached -> Simplified -> Static -> Error
   - Reduce functionality instead of complete failure
   - Always provide user-friendly error message

6. HEALTH CHECKS
   - Liveness: Is process running?
   - Readiness: Can it handle requests?
   - Check each component separately

7. BULKHEAD ISOLATION
   - Limit concurrent calls per operation type
   - Critical: 10, Standard: 50, Background: 100
   - One operation failure doesn't affect others

8. RECOVERY MECHANISMS
   - Cool-down period after failure
   - Gradually restore capacity (1 -> 5 -> 20 -> full)
   - Verify health before full operation

INTERVIEW QUESTIONS & ANSWERS:
------------------------------
Q: What is a circuit breaker pattern?
A: A pattern that stops calling a failing service repeatedly.
   After failures, circuit "opens" and calls fail fast.
   After timeout, allows test call to check recovery.

Q: How do you handle failures gracefully?
A: Implement fallback strategies. When primary fails,
   return cached response, default value, or degraded result.

Q: How do you set timeout values?
A: Set based on expected response + buffer. Consider network
   latency, processing time, queue time. Never block forever.

Q: What is bulkhead isolation?
A: Isolating operations so one failure doesn't affect others.
   Limit concurrent calls per operation type.

Q: How do you implement recovery mechanisms?
A: After failure: cool-down -> test with limited calls ->
   gradually increase load -> verify health -> full recovery.
""")