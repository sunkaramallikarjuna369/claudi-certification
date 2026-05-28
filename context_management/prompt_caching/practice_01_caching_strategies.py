"""
PRACTICE 01: PROMPT CACHING STRATEGIES
=======================================

Prompt Caching Concepts:
- Cache repeatedly used content (system prompts, instructions)
- Reduce API costs by caching static content
- Improve response times for repeated queries
- Cache invalidation when content changes

Key Strategies:
1. Static content caching (system prompts)
2. Repeated query caching
3. Cache hit optimization
4. TTL (time-to-live) configuration
5. Partial cache usage
6. Cache warming strategies
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
# SCENARIO 1: Basic Cache Implementation
# =============================================================================

class PromptCache:
    """
    BASIC CACHE: Store and retrieve cached prompts

    Interview Q: Why use prompt caching?
    A: To reduce costs and improve latency for repeated content.
       Static prompts (system instructions) are ideal candidates.
    """

    def __init__(self):
        self._cache = {}
        self._access_count = {}
        self._last_access = {}

    def set(self, key, value, ttl_seconds=None):
        """Store value in cache with optional TTL"""
        self._cache[key] = value
        self._access_count[key] = 0
        self._last_access[key] = time.time()

        if ttl_seconds:
            self._cache[f"{key}_expires"] = time.time() + ttl_seconds

    def get(self, key):
        """Retrieve value from cache if not expired"""
        # Check expiration
        expires_key = f"{key}_expires"
        if expires_key in self._cache:
            if time.time() > self._cache[expires_key]:
                self.invalidate(key)
                return None

        if key in self._cache:
            self._access_count[key] = self._access_count.get(key, 0) + 1
            self._last_access[key] = time.time()
            return self._cache[key]
        return None

    def invalidate(self, key):
        """Remove key from cache"""
        if key in self._cache:
            del self._cache[key]
        if f"{key}_expires" in self._cache:
            del self._cache[f"{key}_expires"]

    def get_stats(self):
        """Return cache statistics"""
        return {
            "size": len(self._cache) // 2,  # Divided by 2 for value+expires
            "total_accesses": sum(self._access_count.values()),
            "most_accessed": max(self._access_count.items(), key=lambda x: x[1]) if self._access_count else None
        }


def demonstrate_basic_cache():
    """Show basic cache implementation"""
    print("=" * 60)
    print("SCENARIO 1: Basic Cache Implementation")
    print("=" * 60)

    cache = PromptCache()

    # Cache static system prompts
    system_prompt = "You are a helpful coding assistant specializing in Python."
    cache.set("system_coding", system_prompt, ttl_seconds=3600)

    # Retrieve from cache
    cached_prompt = cache.get("system_coding")
    print(f"Cached system prompt: {cached_prompt}")

    # Cache statistics
    stats = cache.get_stats()
    print(f"\nCache stats: {stats}")
    print()


# =============================================================================
# SCENARIO 2: Cache Hit Optimization
# =============================================================================

def demonstrate_cache_hit_optimization():
    """
    REAL-TIME SCENARIO: Optimizing for cache hits with smart key generation

    COMMON MISTAKE: Using complex keys, making cache misses common
    BEST PRACTICE: Normalize keys for consistent cache lookups

    Interview Q: How do you maximize cache hit rate?
    A: Use consistent, normalized keys. Hash content for large prompts.
       Group similar requests under same cache key.
    """
    print("=" * 60)
    print("SCENARIO 2: Cache Hit Optimization")
    print("=" * 60)

    import hashlib

    def normalize_key(text):
        """Normalize text for consistent cache keys"""
        # Lowercase, strip whitespace, remove extra spaces
        normalized = ' '.join(text.lower().split())
        return hashlib.md5(normalized.encode()).hexdigest()

    # Example queries that should hit cache
    queries = [
        "  Hello, how are you?  ",
        "hello, how are you?",
        "Hello,    how are   you?"
    ]

    print("Normalized keys for similar queries:")
    keys = []
    for q in queries:
        key = normalize_key(q)
        keys.append(key)
        print(f"  '{q}' -> {key}")

    # All queries generate same key -> cache hit!
    print(f"\nAll keys identical: {len(set(keys)) == 1}")
    print()


# =============================================================================
# SCENARIO 3: Multi-Level Cache Strategy
# =============================================================================

class MultiLevelCache:
    """
    MULTI-LEVEL CACHE: L1 (memory) + L2 (persistent)

    BEST PRACTICE: Use multiple cache levels for performance
    L1: Fast in-memory cache for hot data
    L2: Slower but persistent cache for durability
    """

    def __init__(self):
        self.l1_cache = {}  # In-memory, fast
        self.l2_cache = {}  # Persistent, slower
        self.l1_max_size = 100
        self.l2_max_size = 1000

    def put(self, key, value):
        """Put value in L1 cache"""
        # Add to L1
        self.l1_cache[key] = value

        # If L1 is full, move oldest to L2
        if len(self.l1_cache) > self.l1_max_size:
            oldest_key = next(iter(self.l1_cache))
            self.l2_cache[oldest_key] = self.l1_cache.pop(oldest_key)

    def get(self, key):
        """Get value from L1, fallback to L2"""
        # Check L1 first (fast)
        if key in self.l1_cache:
            return self.l1_cache[key]

        # Check L2 (slower but still faster than API call)
        if key in self.l2_cache:
            value = self.l2_cache.pop(key)
            self.put(key, value)  # Promote to L1
            return value

        return None

    def get_stats(self):
        """Return cache statistics"""
        return {
            "l1_size": len(self.l1_cache),
            "l2_size": len(self.l2_cache),
            "total_items": len(self.l1_cache) + len(self.l2_cache)
        }


def demonstrate_multi_level_cache():
    """Show multi-level cache behavior"""
    print("=" * 60)
    print("SCENARIO 3: Multi-Level Cache Strategy")
    print("=" * 60)

    cache = MultiLevelCache()

    # Add items
    for i in range(150):
        cache.put(f"key_{i}", f"value_{i}")

    stats = cache.get_stats()
    print(f"Cache stats after adding 150 items:")
    print(f"  L1 (memory): {stats['l1_size']} items")
    print(f"  L2 (persistent): {stats['l2_size']} items")
    print(f"  Total: {stats['total_items']} items")
    print()


# =============================================================================
# SCENARIO 4: Cache Invalidation Strategies
# =============================================================================

def demonstrate_cache_invalidation():
    """
    REAL-TIME SCENARIO: Invalidating stale cache entries

    COMMON MISTAKE: Never invalidating cache, leading to stale data
    BEST PRACTICE: Implement proper invalidation based on:
    - Time-based (TTL)
    - Event-based (content changes)
    - Manual (explicit invalidation)

    Interview Q: How do you handle cache invalidation?
    A: Use TTL for time-based invalidation. Implement event-based
       invalidation when source content changes. Allow manual
       invalidation for critical updates.
    """
    print("=" * 60)
    print("SCENARIO 4: Cache Invalidation Strategies")
    print("=" * 60)

    class SmartCache:
        def __init__(self, default_ttl=3600):
            self.default_ttl = default_ttl
            self._cache = {}
            self._metadata = {}

        def set(self, key, value, ttl=None):
            ttl = ttl or self.default_ttl
            self._cache[key] = value
            self._metadata[key] = {
                "created": time.time(),
                "expires": time.time() + ttl,
                "version": 1
            }

        def get(self, key):
            if key not in self._cache:
                return None, "MISS"

            meta = self._metadata[key]
            if time.time() > meta["expires"]:
                del self._cache[key]
                del self._metadata[key]
                return None, "EXPIRED"

            return self._cache[key], "HIT"

        def invalidate(self, key):
            """Manual invalidation"""
            if key in self._cache:
                del self._cache[key]
                del self._metadata[key]
                return True
            return False

        def invalidate_pattern(self, pattern):
            """Invalidate all keys matching pattern"""
            keys_to_remove = [k for k in self._cache.keys() if pattern in k]
            for key in keys_to_remove:
                self.invalidate(key)
            return len(keys_to_remove)

    cache = SmartCache(default_ttl=10)  # 10 second TTL for demo

    # Add items
    cache.set("user_123_profile", {"name": "John", "age": 30})
    cache.set("user_123_settings", {"theme": "dark"})

    # Check initial hit
    value, status = cache.get("user_123_profile")
    print(f"Initial get: {status}, value: {value}")

    # Manual invalidation
    removed = cache.invalidate_pattern("profile")
    print(f"Invalidated {removed} keys matching 'profile'")

    # Check after invalidation
    value, status = cache.get("user_123_profile")
    print(f"After invalidation: {status}")
    print()


# =============================================================================
# SCENARIO 5: Cache Warming Strategy
# =============================================================================

def demonstrate_cache_warming():
    """
    REAL-TIME SCENARIO: Pre-warming cache with common queries

    BEST PRACTICE: Warm cache before peak usage times
    Common scenarios:
    - EOD batch processing
    - Morning peak usage
    - Pre-scheduled reports

    Interview Q: What is cache warming and when to use it?
    A: Pre-loading cache with frequently accessed data before
       it's needed. Use before known high-traffic periods.
    """
    print("=" * 60)
    print("SCENARIO 5: Cache Warming Strategy")
    print("=" * 60)

    # Common system prompts that get reused
    common_prompts = [
        {"task": "code_review", "prompt": "You are a code reviewer."},
        {"task": "debugging", "prompt": "You are a debugging assistant."},
        {"task": "documentation", "prompt": "You are a technical writer."},
    ]

    cache = PromptCache()

    print("Cache warming with common prompts:")
    for item in common_prompts:
        cache.set(f"system_{item['task']}", item['prompt'], ttl_seconds=7200)
        print(f"  Cached: system_{item['task']}")

    print(f"\nCache ready for {cache.get_stats()['size']} warm items")
    print()


# =============================================================================
# SCENARIO 6: Cache with API Response
# =============================================================================

def demonstrate_cache_with_api():
    """
    REAL-TIME SCENARIO: Caching API responses for repeated queries

    Interview Q: How do you cache API responses effectively?
    A: Hash the request parameters as cache key. Store response.
       Check cache before making API call. Invalidate on data changes.
    """
    print("=" * 60)
    print("SCENARIO 6: Cache with API Response")
    print("=" * 60)

    import hashlib
    import json

    class APIResponseCache:
        def __init__(self):
            self.cache = {}

        def get_cache_key(self, messages):
            """Generate cache key from messages"""
            content = json.dumps(messages, sort_keys=True)
            return hashlib.sha256(content.encode()).hexdigest()

        def cached_call(self, client, model, messages, max_tokens=1024):
            """Make API call with caching"""
            cache_key = self.get_cache_key(messages)

            # Check cache
            if cache_key in self.cache:
                print(f"  Cache HIT for this request!")
                return self.cache[cache_key]

            # Cache miss - make API call
            print(f"  Cache MISS - making API call...")
            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=messages
            )

            result = {
                "content": response.content[0].text,
                "usage": {
                    "input": response.usage.input_tokens,
                    "output": response.usage.output_tokens
                }
            }

            # Store in cache
            self.cache[cache_key] = result
            return result

    api_cache = APIResponseCache()

    messages = [
        {"role": "user", "content": "What is Python?"}
    ]

    # First call - cache miss
    print("First call (expected cache miss):")
    result1 = api_cache.cached_call(client, MODEL, messages)
    print(f"  Input tokens: {result1['usage']['input']}")

    # Second call - cache hit
    print("\nSecond call (expected cache hit):")
    result2 = api_cache.cached_call(client, MODEL, messages)
    print(f"  Input tokens: {result2['usage']['input']}")

    print(f"\nTotal cached responses: {len(api_cache.cache)}")
    print()


# =============================================================================
# SCENARIO 7: Cost Reduction Through Caching
# =============================================================================

def demonstrate_cost_reduction():
    """
    REAL-TIME SCENARIO: Calculating cost savings from caching

    COMMON MISTAKE: Not tracking cache effectiveness
    BEST PRACTICE: Monitor cache hit rate and calculate savings

    Interview Q: How much can caching reduce costs?
    A: Depends on query patterns. For static prompts (system instructions),
       cache hit rate can be 90%+, reducing costs significantly.
       Example: 1000 requests with same system prompt = 1 cache hit + 999 saves.
    """
    print("=" * 60)
    print("SCENARIO 7: Cost Reduction Through Caching")
    print("=" * 60)

    # Example: Calculate savings
    total_requests = 1000
    cache_hit_rate = 0.85  # 85% cache hit rate

    # Assume each request costs 100 tokens (system prompt)
    tokens_per_request = 100
    cost_per_token = 0.00001  # Example cost

    # Without caching
    total_tokens_without = total_requests * tokens_per_request
    cost_without = total_tokens_without * cost_per_token

    # With caching
    cache_hits = int(total_requests * cache_hit_rate)
    cache_misses = total_requests - cache_hits
    total_tokens_with = (cache_hits * 0) + (cache_misses * tokens_per_request)
    cost_with = total_tokens_with * cost_per_token

    savings = cost_without - cost_with
    savings_percent = (savings / cost_without) * 100

    print(f"Cost analysis for {total_requests} requests:")
    print(f"  Cache hit rate: {cache_hit_rate * 100}%")
    print(f"  Cache hits: {cache_hits}")
    print(f"  Cache misses: {cache_misses}")
    print(f"\n  Cost without cache: ${cost_without:.4f}")
    print(f"  Cost with cache: ${cost_with:.4f}")
    print(f"  Savings: ${savings:.4f} ({savings_percent:.1f}%)")
    print()


# =============================================================================
# MAIN: Run All Scenarios
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("PROMPT CACHING STRATEGIES - PRACTICE FILE")
    print("=" * 60 + "\n")

    demonstrate_basic_cache()
    demonstrate_cache_hit_optimization()
    demonstrate_multi_level_cache()
    demonstrate_cache_invalidation()
    demonstrate_cache_warming()
    demonstrate_cache_with_api()
    demonstrate_cost_reduction()

    print("\n" + "=" * 60)
    print("WHAT WE HAVE LEARNT")
    print("=" * 60)
    print("""
1. BASIC CACHE IMPLEMENTATION
   - Store key-value pairs with optional TTL
   - Track access patterns for optimization
   - Simple but effective for repeated content

2. CACHE HIT OPTIMIZATION
   - Normalize keys for consistent lookups
   - Hash content for large prompts
   - Group similar requests under same key

3. MULTI-LEVEL CACHE STRATEGY
   - L1: Fast in-memory for hot data
   - L2: Persistent for durability
   - Promote items on L2 hit to L1

4. CACHE INVALIDATION STRATEGIES
   - Time-based: TTL expiration
   - Event-based: Content changes trigger invalidation
   - Manual: Explicit invalidation when needed
   - Pattern-based: Invalidate multiple related keys

5. CACHE WARMING
   - Pre-load cache before high-traffic periods
   - Warm with common/frequently used prompts
   - Reduces initial latency for new requests

6. API RESPONSE CACHING
   - Hash request parameters as cache key
   - Store full response in cache
   - Check cache before API calls

7. COST REDUCTION
   - Track cache hit rate
   - Calculate token savings
   - Monitor cost per request

INTERVIEW QUESTIONS & ANSWERS:
------------------------------
Q: Why use prompt caching?
A: To reduce API costs and improve response latency for
   repeated content. Static prompts are ideal candidates.

Q: How do you maximize cache hit rate?
A: Use consistent, normalized keys. Hash content for large
   prompts. Group similar requests under same cache key.

Q: What is cache warming?
A: Pre-loading cache with frequently accessed data before
   it's needed, typically before known high-traffic periods.

Q: How do you handle cache invalidation?
A: Use TTL for time-based invalidation, event-based when
   content changes, and allow manual invalidation for
   critical updates.
""")