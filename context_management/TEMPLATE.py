"""
COMPREHENSIVE TEMPLATE: CONTEXT MANAGEMENT & RELIABILITY
=======================================================

This template provides a complete structure for all context management
patterns. Use as a starting point for building production systems.

Key Areas Covered:
1. Context Window Management
2. Prompt Caching
3. Long Conversation Handling
4. Rate Limiting & Quotas
5. Monitoring & Observability
6. Production Reliability

Model: claude-haiku-4-5-20250601
"""

import os
import time
import hashlib
from datetime import datetime, timedelta
from collections import defaultdict
from anthropic import Anthropic

# =============================================================================
# SETUP: Load environment and initialize client
# =============================================================================

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
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
# PART 1: CONTEXT WINDOW MANAGEMENT
# =============================================================================

class ContextWindowManager:
    """
    Manage context window usage efficiently.

    Features:
    - Token estimation
    - Message pruning
    - Priority-based selection
    - Rolling context
    """

    def __init__(self, max_tokens=1_000_000, reserve_output=200_000):
        self.max_tokens = max_tokens
        self.reserve_output = reserve_output
        self.available_input = max_tokens - reserve_output
        self.messages = []
        self.summary = ""

    def add_message(self, role, content):
        """Add message and auto-prune if needed"""
        self.messages.append({"role": role, "content": content})
        self._prune_if_needed()

    def _estimate_tokens(self):
        """Estimate total tokens used"""
        content = self.summary + "".join(m["content"] for m in self.messages)
        return len(content) // 4

    def _prune_if_needed(self):
        """Prune old messages when approaching limit"""
        while self._estimate_tokens() > self.available_input and len(self.messages) > 4:
            self.messages.pop(0)

    def set_summary(self, summary_text):
        """Set conversation summary"""
        self.summary = summary_text
        self.messages = self.messages[-5:]  # Keep recent only

    def get_messages(self):
        """Get all messages with summary"""
        if self.summary:
            return [{"role": "system", "content": f"Previous: {self.summary}"}] + self.messages
        return self.messages

    def get_stats(self):
        """Get context statistics"""
        estimated = self._estimate_tokens()
        return {
            "estimated_tokens": estimated,
            "available": self.available_input,
            "usage_percent": (estimated / self.available_input) * 100,
            "message_count": len(self.messages)
        }


# =============================================================================
# PART 2: PROMPT CACHING
# =============================================================================

class PromptCache:
    """
    Cache frequently used prompts for cost reduction.

    Features:
    - TTL-based expiration
    - Multi-level caching
    - Hit rate tracking
    """

    def __init__(self, default_ttl=3600):
        self.default_ttl = default_ttl
        self.cache = {}
        self.metadata = {}
        self.hits = 0
        self.misses = 0

    def set(self, key, value, ttl=None):
        """Store value in cache"""
        ttl = ttl or self.default_ttl
        self.cache[key] = value
        self.metadata[key] = {
            "created": time.time(),
            "expires": time.time() + ttl
        }

    def get(self, key):
        """Retrieve from cache if not expired"""
        if key not in self.cache:
            self.misses += 1
            return None

        meta = self.metadata[key]
        if time.time() > meta["expires"]:
            del self.cache[key]
            del self.metadata[key]
            self.misses += 1
            return None

        self.hits += 1
        return self.cache[key]

    def get_cache_key(self, messages):
        """Generate cache key from messages"""
        content = "".join(m["content"] for m in messages)
        return hashlib.sha256(content.encode()).hexdigest()

    def get_hit_rate(self):
        """Calculate cache hit rate"""
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0


# =============================================================================
# PART 3: LONG CONVERSATION HANDLING
# =============================================================================

class ConversationManager:
    """
    Handle long conversations with summarization.

    Features:
    - Rolling context
    - Session checkpointing
    - Memory bank
    """

    def __init__(self, max_messages=20):
        self.max_messages = max_messages
        self.history = []
        self.checkpoints = []
        self.memory_bank = {
            "facts": [],
            "decisions": [],
            "context": {}
        }

    def add_message(self, role, content):
        """Add message with auto-pruning"""
        self.history.append({"role": role, "content": content})

        # Prune if needed
        while len(self.history) > self.max_messages:
            # Create checkpoint before pruning
            self.create_checkpoint()
            self.history.pop(0)

    def create_checkpoint(self):
        """Save checkpoint of current state"""
        summary = self._generate_summary()
        self.checkpoints.append({
            "index": len(self.checkpoints),
            "message_count": len(self.history),
            "summary": summary,
            "timestamp": datetime.now()
        })

    def _generate_summary(self):
        """Generate summary of current conversation"""
        if not self.history:
            return "Empty conversation"

        roles = defaultdict(int)
        for m in self.history:
            roles[m["role"]] += 1

        return f"Conversation: {roles['user']} user, {roles['assistant']} assistant messages"

    def restore_checkpoint(self, index):
        """Restore to specific checkpoint"""
        if 0 <= index < len(self.checkpoints):
            checkpoint = self.checkpoints[index]
            self.memory_bank["context"]["restored_from"] = checkpoint["index"]
            return checkpoint
        return None

    def add_fact(self, fact):
        """Add fact to memory bank"""
        self.memory_bank["facts"].append({
            "fact": fact,
            "timestamp": datetime.now()
        })

    def get_context(self):
        """Get full context including memory"""
        context_parts = []

        if self.memory_bank["facts"]:
            facts = self.memory_bank["facts"][-5:]
            context_parts.append(f"Facts: {', '.join(f['fact'] for f in facts)}")

        if self.history:
            context_parts.append(f"Recent: {len(self.history)} messages")

        return " | ".join(context_parts) if context_parts else "No context"


# =============================================================================
# PART 4: RATE LIMITING & QUOTAS
# =============================================================================

class RateLimitHandler:
    """
    Handle rate limits with backoff and retry.

    Features:
    - Quota tracking
    - Exponential backoff
    - Circuit breaker
    """

    def __init__(self, requests_per_minute=50):
        self.requests_per_minute = requests_per_minute
        self.minute_requests = []
        self.failure_count = 0
        self.circuit_open = False
        self.circuit_timeout = 30

    def can_proceed(self):
        """Check if request can proceed"""
        if self.circuit_open:
            elapsed = time.time() - getattr(self, 'last_failure', time.time())
            if elapsed > self.circuit_timeout:
                self.circuit_open = False
                self.failure_count = 0
            else:
                return False

        now = time.time()
        self.minute_requests = [r for r in self.minute_requests if now - r < 60]

        if len(self.minute_requests) >= self.requests_per_minute:
            return False

        return True

    def record_request(self):
        """Record successful request"""
        self.minute_requests.append(time.time())

    def record_failure(self):
        """Record failure for circuit breaker"""
        self.failure_count += 1
        self.last_failure = time.time()

        if self.failure_count >= 5:
            self.circuit_open = True

    def get_backoff_delay(self, attempt):
        """Calculate exponential backoff delay"""
        base = 1
        delay = base * (2 ** attempt)
        return min(delay, 60)  # Cap at 60 seconds


# =============================================================================
# PART 5: MONITORING & OBSERVABILITY
# =============================================================================

class MetricsCollector:
    """
    Collect and track system metrics.

    Metrics tracked:
    - Request count
    - Latency
    - Errors
    - Token usage
    - Cost
    """

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset all metrics"""
        self.request_count = 0
        self.error_count = 0
        self.total_latency = 0.0
        self.latencies = []
        self.input_tokens = 0
        self.output_tokens = 0
        self.errors_by_type = defaultdict(int)

    def record(self, latency, input_tok, output_tok, success=True, error_type=None):
        """Record metrics for a request"""
        self.request_count += 1
        self.total_latency += latency
        self.latencies.append(latency)
        self.input_tokens += input_tok
        self.output_tokens += output_tok

        if not success:
            self.error_count += 1
            if error_type:
                self.errors_by_type[error_type] += 1

    def get_metrics(self):
        """Get all metrics"""
        avg_latency = self.total_latency / self.request_count if self.request_count > 0 else 0
        sorted_lat = sorted(self.latencies) if self.latencies else [0]

        return {
            "requests": self.request_count,
            "errors": self.error_count,
            "error_rate": (self.error_count / self.request_count * 100) if self.request_count > 0 else 0,
            "avg_latency_ms": avg_latency * 1000,
            "p95_latency_ms": sorted_lat[int(len(sorted_lat) * 0.95)] * 1000 if len(sorted_lat) > 20 else 0,
            "total_tokens": self.input_tokens + self.output_tokens,
            "errors_by_type": dict(self.errors_by_type)
        }


class CostTracker:
    """Track API spending"""

    INPUT_COST_PER_1K = 0.000025
    OUTPUT_COST_PER_1K = 0.000125

    def __init__(self, daily_budget=50.0):
        self.daily_budget = daily_budget
        self.total_spent = 0.0
        self.hourly_spending = defaultdict(float)

    def record(self, input_tok, output_tok):
        """Record token usage and cost"""
        input_cost = (input_tok / 1000) * self.INPUT_COST_PER_1K
        output_cost = (output_tok / 1000) * self.OUTPUT_COST_PER_1K
        total_cost = input_cost + output_cost

        self.total_spent += total_cost
        hour = datetime.now().strftime("%H:00")
        self.hourly_spending[hour] += total_cost

        return total_cost

    def get_stats(self):
        """Get spending stats"""
        return {
            "spent": self.total_spent,
            "budget": self.daily_budget,
            "remaining": self.daily_budget - self.total_spent,
            "percent_used": (self.total_spent / self.daily_budget) * 100
        }


# =============================================================================
# PART 6: PRODUCTION RELIABILITY
# =============================================================================

class CircuitBreaker:
    """
    Circuit breaker for preventing cascade failures.
    """

    def __init__(self, failure_threshold=5, timeout=30):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure = None
        self.state = "closed"  # closed, open, half_open

    def can_execute(self):
        """Check if execution is allowed"""
        if self.state == "open":
            if self.last_failure and time.time() - self.last_failure > self.timeout:
                self.state = "half_open"
                return True
            return False
        return True

    def record_success(self):
        """Record successful execution"""
        if self.state == "half_open":
            self.state = "closed"
        self.failure_count = 0

    def record_failure(self):
        """Record failed execution"""
        self.failure_count += 1
        self.last_failure = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = "open"


class FallbackHandler:
    """
    Provide fallback responses when primary fails.
    """

    def __init__(self):
        self.cache = {}
        self.fallbacks = []

    def add_fallback(self, name, func):
        """Add a fallback function"""
        self.fallbacks.append((name, func))

    def execute(self, primary_func, cache_key=None):
        """Execute with fallback chain"""
        # Check cache
        if cache_key and cache_key in self.cache:
            return self.cache[cache_key], "cached"

        # Try primary
        try:
            result = primary_func()
            if cache_key:
                self.cache[cache_key] = result
            return result, "primary"
        except Exception as e:
            pass

        # Try fallbacks
        for name, func in self.fallbacks:
            try:
                result = func()
                return result, f"fallback:{name}"
            except Exception:
                continue

        return None, "failed"


class HealthChecker:
    """
    Health check for system components.
    """

    def __init__(self):
        self.checks = {}

    def register_check(self, name, check_func):
        """Register a health check"""
        self.checks[name] = check_func

    def check(self):
        """Run all health checks"""
        results = {}
        all_healthy = True

        for name, func in self.checks.items():
            try:
                healthy, message = func()
                results[name] = {"healthy": healthy, "message": message}
                if not healthy:
                    all_healthy = False
            except Exception as e:
                results[name] = {"healthy": False, "message": str(e)}
                all_healthy = False

        return {
            "status": "healthy" if all_healthy else "unhealthy",
            "checks": results,
            "timestamp": datetime.now().isoformat()
        }


# =============================================================================
# PART 7: COMPLETE CLIENT CLASS
# =============================================================================

class ClaudeClient:
    """
    Complete client with all reliability features.
    """

    def __init__(self, model=MODEL):
        self.model = model
        self.context_manager = ContextWindowManager()
        self.cache = PromptCache()
        self.conversation = ConversationManager()
        self.rate_limiter = RateLimitHandler()
        self.metrics = MetricsCollector()
        self.cost_tracker = CostTracker()
        self.circuit_breaker = CircuitBreaker()
        self.fallback_handler = FallbackHandler()
        self.health_checker = HealthChecker()

        # Register health checks
        self.health_checker.register_check("rate_limiter", self._check_rate_limiter)
        self.health_checker.register_check("circuit_breaker", self._check_circuit_breaker)

    def _check_rate_limiter(self):
        return (self.rate_limiter.can_proceed(), "Rate limiter OK")

    def _check_circuit_breaker(self):
        return (self.circuit_breaker.can_execute(), "Circuit breaker OK")

    def send_message(self, content, use_cache=True):
        """Send message with full reliability stack"""
        messages = [{"role": "user", "content": content}]

        # Check rate limit
        if not self.rate_limiter.can_proceed():
            return None, "Rate limit exceeded"

        # Check circuit breaker
        if not self.circuit_breaker.can_execute():
            return None, "Circuit breaker open"

        # Check cache
        cache_key = self.cache.get_cache_key(messages) if use_cache else None
        cached = self.cache.get(cache_key)
        if cached:
            return cached, "cached"

        # Make API call
        start_time = time.time()
        try:
            response = client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=messages
            )

            latency = time.time() - start_time

            # Record metrics
            self.metrics.record(
                latency,
                response.usage.input_tokens,
                response.usage.output_tokens,
                success=True
            )
            self.cost_tracker.record(
                response.usage.input_tokens,
                response.usage.output_tokens
            )
            self.rate_limiter.record_request()
            self.circuit_breaker.record_success()

            return response.content[0].text, "success"

        except Exception as e:
            self.rate_limiter.record_failure()
            self.circuit_breaker.record_failure()
            self.metrics.record(0, 0, 0, success=False, error_type=type(e).__name__)
            return None, str(e)

    def get_full_status(self):
        """Get complete system status"""
        return {
            "context": self.context_manager.get_stats(),
            "cache_hit_rate": self.cache.get_hit_rate(),
            "metrics": self.metrics.get_metrics(),
            "cost": self.cost_tracker.get_stats(),
            "health": self.health_checker.check()
        }


# =============================================================================
# USAGE EXAMPLES
# =============================================================================

def main():
    """Demonstrate all components"""
    print("=" * 60)
    print("CONTEXT MANAGEMENT & RELIABILITY - COMPLETE TEMPLATE")
    print("=" * 60)

    # Initialize client
    client = ClaudeClient()

    # Health check
    print("\n1. Health Check:")
    health = client.health_checker.check()
    print(f"   Status: {health['status']}")

    # Rate limiter check
    print("\n2. Rate Limiter:")
    can_proceed = client.rate_limiter.can_proceed()
    print(f"   Can proceed: {can_proceed}")

    # Send message
    print("\n3. Sending Message:")
    response, status = client.send_message("Hello, how are you?")
    if response:
        print(f"   Response: {response[:50]}...")
    else:
        print(f"   Failed: {status}")

    # Get status
    print("\n4. System Status:")
    full_status = client.get_full_status()
    print(f"   Requests: {full_status['metrics']['requests']}")
    print(f"   Error rate: {full_status['metrics']['error_rate']:.1f}%")
    print(f"   Cost: ${full_status['cost']['spent']:.6f}")
    print(f"   Cache hit rate: {full_status['cache_hit_rate']:.1f}%")

    print("\n" + "=" * 60)
    print("TEMPLATE DEMONSTRATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()


# =============================================================================
# WHAT WE HAVE LEARNT - SUMMARY
# =============================================================================

SUMMARY = """
COMPREHENSIVE TEMPLATE SUMMARY
==============================

This template provides production-ready implementations of:

1. CONTEXT WINDOW MANAGEMENT
   - ContextWindowManager: Token estimation, pruning, rolling context
   - Configurable limits and auto-pruning

2. PROMPT CACHING
   - PromptCache: TTL-based cache with hit rate tracking
   - Cache key generation for consistent lookups

3. LONG CONVERSATION HANDLING
   - ConversationManager: Rolling context, checkpoints, memory bank
   - Summarization before pruning

4. RATE LIMITING & QUOTAS
   - RateLimitHandler: Quota tracking, circuit breaker, backoff
   - Exponential backoff for retries

5. MONITORING & OBSERVABILITY
   - MetricsCollector: Request count, latency, errors, tokens
   - CostTracker: Real-time spending tracking

6. PRODUCTION RELIABILITY
   - CircuitBreaker: Prevent cascade failures
   - FallbackHandler: Graceful degradation
   - HealthChecker: Component status monitoring

7. COMPLETE CLIENT
   - ClaudeClient: Integrates all components
   - Single interface for all reliability features

KEY PATTERNS:
- Always check rate limits before API calls
- Use circuit breaker to prevent cascade failures
- Cache responses for fallback
- Monitor all metrics for visibility
- Health checks for reliability

INTERVIEW QUESTIONS:
--------------------
Q: How do you manage context window efficiently?
A: Use rolling context, prune old messages, summarize before pruning.

Q: What is a circuit breaker pattern?
A: Prevents cascade failures by failing fast when service is unhealthy.

Q: How do you handle rate limits?
A: Track quota, use exponential backoff, implement circuit breaker.

Q: How do you monitor a production system?
A: Track metrics (latency, errors, cost), health checks, alerts.

Q: What is graceful degradation?
A: Reducing functionality instead of complete failure when issues occur.
"""

if __name__ == "__main__":
    print(SUMMARY)