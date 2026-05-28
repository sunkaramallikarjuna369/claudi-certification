"""
PRACTICE 01: CONTEXT WINDOW MANAGEMENT
=======================================

Context Window Concepts:
- Context window is the total tokens available for input + output
- Different models have different window sizes (128K, 200K, 1M tokens)
- Efficient context usage reduces costs and improves performance

Key Strategies:
1. Token budgeting - allocate tokens wisely across system/user/assistant
2. Message pruning - remove less relevant older messages
3. Priority-based selection - keep most important context
4. Truncation strategies - smart ways to shorten context
5. Summary insertion - replace long threads with summaries
"""

import os
from anthropic import Anthropic

# =============================================================================
# SETUP: Load environment and initialize client
# =============================================================================

# Load API key from .env file (ANTHROPIC_API_KEY variable)
# In production, use proper environment variable management
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    with open(dotenv_path) as f:
        for line in f:
            if 'ANTHROPIC_API_KEY' in line and '=' in line:
                key_value = line.split('=', 1)[1].strip()
                if key_value and not key_value.startswith('#'):
                    os.environ['ANTHROPIC_API_KEY'] = key_value

# Initialize client with claude-haiku-4-5-20250601 model
# Haiku is fast and cost-effective for simple tasks
client = Anthropic()
MODEL = "claude-haiku-4-5-20250601"


# =============================================================================
# SCENARIO 1: Basic Context Window Check
# =============================================================================

def demonstrate_context_window_basics():
    """
    REAL-TIME SCENARIO: Checking available context before sending request

    COMMON MISTAKE: Not checking available context, leading to errors
    when exceeding limits. Always verify context size before sending large requests.

    Interview Q: What happens if you exceed context window?
    A: You get an error (context_overflow) and cannot complete the request.
       Must reduce context size or use larger model with bigger window.
    """
    print("=" * 60)
    print("SCENARIO 1: Context Window Basics")
    print("=" * 60)

    # Example: Calculate approximate tokens for a conversation
    # Rule of thumb: ~4 characters per token for English
    sample_messages = [
        {"role": "user", "content": "Hello, how are you?"},
        {"role": "assistant", "content": "I'm doing well, thank you for asking!"},
        {"role": "user", "content": "Can you help me with Python programming?"}
    ]

    total_chars = sum(len(m["content"]) for m in sample_messages)
    estimated_tokens = total_chars // 4  # Rough estimate

    print(f"Total characters: {total_chars}")
    print(f"Estimated tokens: {estimated_tokens}")
    print(f"Available context (1M window): plenty of room!")
    print()


# =============================================================================
# SCENARIO 2: Token Budgeting Strategy
# =============================================================================

def demonstrate_token_budgeting():
    """
    REAL-TIME SCENARIO: Allocating tokens across system, user, and assistant messages

    BEST PRACTICE: Always reserve tokens for response (output)
    Common allocation: 80% for input, 20% for output

    Interview Q: How do you budget tokens in a 1M context window?
    A: Reserve ~200K for output, use ~800K for input context.
       Keep system prompt fixed (~2K), user content varies (~798K max).
    """
    print("=" * 60)
    print("SCENARIO 2: Token Budgeting Strategy")
    print("=" * 60)

    CONTEXT_WINDOW_SIZE = 1_000_000  # 1M tokens for Haiku
    OUTPUT_RESERVATION = 200_000     # Reserve for response

    available_for_input = CONTEXT_WINDOW_SIZE - OUTPUT_RESERVATION

    print(f"Total window: {CONTEXT_WINDOW_SIZE:,} tokens")
    print(f"Reserved for output: {OUTPUT_RESERVATION:,} tokens")
    print(f"Available for input: {available_for_input:,} tokens")
    print()
    print("Budget breakdown:")
    print("  System prompt: ~2,000 tokens (fixed)")
    print("  User content: ~798,000 tokens (flexible)")
    print()


# =============================================================================
# SCENARIO 3: Message Pruning (Context Compression)
# =============================================================================

def demonstrate_message_pruning():
    """
    REAL-TIME SCENARIO: Pruning older messages to make room for new content

    COMMON MISTAKE: Keeping all messages, causing context overflow
    SOLUTION: Implement rolling context - keep recent, summarize old

    Interview Q: How do you handle a conversation that exceeds context?
    A: Prune older messages or replace them with a summary.
       Keep last N messages + system prompt + new user input.
    """
    print("=" * 60)
    print("SCENARIO 3: Message Pruning")
    print("=" * 60)

    # Example conversation history
    conversation_history = [
        {"role": "user", "content": "What's Python?"},
        {"role": "assistant", "content": "Python is a programming language."},
        {"role": "user", "content": "What are its main features?"},
        {"role": "assistant", "content": "It's interpreted, high-level, dynamically typed."},
        {"role": "user", "content": "Who created it?"},
        {"role": "assistant", "content": "Guido van Rossum created it in 1991."},
        {"role": "user", "content": "What's the latest version?"},
        {"role": "assistant", "content": "Python 3.12 is recent."},
    ]

    MAX_MESSAGES = 4  # Keep only last 4 messages

    # Pruning strategy: Keep system + recent messages
    pruned_history = conversation_history[-MAX_MESSAGES:]

    print(f"Original messages: {len(conversation_history)}")
    print(f"After pruning: {len(pruned_history)}")
    print()

    # More advanced: Summarize and replace old messages
    print("Advanced strategy: Summarize old context")
    print("  Original context -> Summary -> Current query")
    print()


# =============================================================================
# SCENARIO 4: Priority-Based Context Selection
# =============================================================================

def demonstrate_priority_based_selection():
    """
    REAL-TIME SCENARIO: Select most relevant context when window is limited

    BEST PRACTICE: Not all context is equal - prioritize by relevance
    Techniques:
    1. Keep recent messages (recency priority)
    2. Keep relevant domain messages (topic priority)
    3. Keep system instructions (functionality priority)

    Interview Q: How do you decide what to keep in limited context?
    A: Priority order: System instructions > Recent user messages >
       Relevant code > Historical context
    """
    print("=" * 60)
    print("SCENARIO 4: Priority-Based Selection")
    print("=" * 60)

    # Priority levels for context items
    context_items = [
        {"type": "system_prompt", "content": "You are a helpful assistant", "priority": 1},
        {"type": "user_message", "content": "Fix this bug in my code", "priority": 2},
        {"type": "relevant_code", "content": "function calculate() {...}", "priority": 3},
        {"type": "history", "content": "Earlier conversation about bugs", "priority": 4},
        {"type": "general_knowledge", "content": "Python basics info", "priority": 5},
    ]

    # Sort by priority (lower number = higher priority)
    sorted_context = sorted(context_items, key=lambda x: x["priority"])

    print("Context priority order (highest to lowest):")
    for i, item in enumerate(sorted_context, 1):
        print(f"  {i}. {item['type']}: {item['content'][:30]}...")
    print()


# =============================================================================
# SCENARIO 5: Truncation Strategies
# =============================================================================

def demonstrate_truncation_strategies():
    """
    REAL-TIME SCENARIO: Smart truncation when context exceeds limit

    COMMON MISTAKE: Blindly truncating from the start
    BETTER APPROACH: Truncate from middle, keep start and end (R优化)

    Interview Q: What's the best way to truncate long context?
    A: Keep beginning (instructions) and end (recent content).
       Truncate middle portion. This preserves context structure.
    """
    print("=" * 60)
    print("SCENARIO 5: Truncation Strategies")
    print("=" * 60)

    # Example: Long context that needs truncation
    long_content = """
    Introduction part with important setup instructions...
    [Middle content - detailed but less critical]
    More detailed explanations and examples...
    [Even more middle content]
    Final critical information and conclusions...
    """

    MAX_LENGTH = 100  # Maximum allowed length

    # Strategy 1: Simple truncation (bad - loses end)
    simple_truncated = long_content[:MAX_LENGTH]

    # Strategy 2: Keep start + end (better - preserves structure)
    keep_start = 40
    keep_end = 40
    middle_truncated = (
        long_content[:keep_start] +
        "\n... [content truncated for brevity] ...\n" +
        long_content[-keep_end:]
    )

    print("Simple truncation (loses end):")
    print(f"  {simple_truncated[:50]}...")
    print()
    print("Smart truncation (keep start + end):")
    print(middle_truncated)
    print()


# =============================================================================
# SCENARIO 6: Building a Context Manager Class
# =============================================================================

class ContextManager:
    """
    PRACTICAL PATTERN: Context Manager for tracking and optimizing usage

    Features:
    - Track token usage
    - Auto-prune when approaching limits
    - Priority-based content retention
    """

    def __init__(self, max_tokens=1_000_000, reserve_output=200_000):
        self.max_tokens = max_tokens
        self.reserve_output = reserve_output
        self.available_input = max_tokens - reserve_output
        self.messages = []

    def add_message(self, role, content):
        """Add message to context, auto-prune if needed"""
        self.messages.append({"role": role, "content": content})
        self._auto_prune()

    def estimate_tokens(self):
        """Rough token estimation"""
        total_chars = sum(len(m["content"]) for m in self.messages)
        return total_chars // 4

    def _auto_prune(self):
        """Remove old messages if approaching limit"""
        estimated = self.estimate_tokens()
        while estimated > self.available_input and len(self.messages) > 4:
            self.messages.pop(0)  # Remove oldest
            estimated = self.estimate_tokens()

    def get_context(self):
        """Return current context for API call"""
        return self.messages

    def get_usage_stats(self):
        """Return usage statistics"""
        estimated = self.estimate_tokens()
        return {
            "estimated_tokens": estimated,
            "available": self.available_input,
            "usage_percent": (estimated / self.available_input) * 100,
            "message_count": len(self.messages)
        }


def demonstrate_context_manager():
    """Show the ContextManager class in action"""
    print("=" * 60)
    print("SCENARIO 6: Context Manager Class")
    print("=" * 60)

    manager = ContextManager(max_tokens=1_000_000, reserve_output=200_000)

    # Add some messages
    manager.add_message("user", "Hello, how are you?")
    manager.add_message("assistant", "I'm doing great!")
    manager.add_message("user", "Tell me about Python")
    manager.add_message("assistant", "Python is a programming language...")

    stats = manager.get_usage_stats()
    print("Context Manager Stats:")
    print(f"  Estimated tokens: {stats['estimated_tokens']}")
    print(f"  Available: {stats['available']:,}")
    print(f"  Usage: {stats['usage_percent']:.1f}%")
    print(f"  Messages: {stats['message_count']}")
    print()


# =============================================================================
# SCENARIO 7: Real API Call with Context Management
# =============================================================================

def demonstrate_real_api_call():
    """
    REAL-TIME SCENARIO: Making an API call with proper context management

    Interview Q: How do you prevent context overflow in production?
    A: Implement pre-flight checks, auto-pruning, and graceful fallbacks.
    """
    print("=" * 60)
    print("SCENARIO 7: Real API Call with Context Management")
    print("=" * 60)

    try:
        # Create context manager
        manager = ContextManager()

        # Add conversation
        manager.add_message("system", "You are a helpful coding assistant.")
        manager.add_message("user", "Help me write a function to add numbers.")

        # Check usage before making call
        stats = manager.get_usage_stats()
        print(f"Pre-call check: {stats['usage_percent']:.1f}% of context used")

        if stats['usage_percent'] > 90:
            print("WARNING: Context nearly full! Consider pruning.")
        else:
            print("Context OK - proceeding with call")

        # Make actual API call
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            messages=manager.get_context()
        )

        print(f"\nAPI Response received!")
        print(f"Output tokens: {response.usage.output_tokens}")
        print(f"Content: {response.content[0].text[:100]}...")

    except Exception as e:
        print(f"Error occurred: {type(e).__name__}: {e}")
    print()


# =============================================================================
# MAIN: Run All Scenarios
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("CONTEXT WINDOW MANAGEMENT - PRACTICE FILE")
    print("=" * 60 + "\n")

    demonstrate_context_window_basics()
    demonstrate_token_budgeting()
    demonstrate_message_pruning()
    demonstrate_priority_based_selection()
    demonstrate_truncation_strategies()
    demonstrate_context_manager()
    demonstrate_real_api_call()

    print("\n" + "=" * 60)
    print("WHAT WE HAVE LEARNT")
    print("=" * 60)
    print("""
1. CONTEXT WINDOW BASICS
   - Context window is the total token capacity (input + output)
   - Different models have different window sizes
   - Always reserve tokens for the response

2. TOKEN BUDGETING
   - Reserve ~20% for output, use ~80% for input
   - Keep system prompt minimal and fixed
   - Maximize user content within budget

3. MESSAGE PRUNING
   - Implement rolling context (keep recent, prune old)
   - Common strategy: Keep last N messages
   - Can replace old messages with summary

4. PRIORITY-BASED SELECTION
   - System instructions > Recent user > Relevant code > History
   - Not all context has equal importance
   - Prioritize by relevance to current task

5. SMART TRUNCATION
   - Keep start (instructions) and end (recent content)
   - Truncate middle - preserves context structure
   - Avoid simple start-only truncation

6. CONTEXT MANAGER PATTERN
   - Build reusable context management class
   - Auto-prune when approaching limits
   - Track usage statistics for monitoring

7. PRODUCTION BEST PRACTICES
   - Pre-flight checks before API calls
   - Graceful fallbacks when context full
   - Monitor token usage in production

INTERVIEW QUESTIONS & ANSWERS:
------------------------------
Q: What is a context window?
A: The total token capacity available for input + output in a model.

Q: How do you prevent context overflow?
A: By implementing token budgeting, message pruning, and
   priority-based selection strategies.

Q: What's the best truncation strategy?
A: Keep beginning (instructions) and end (recent content),
   truncate middle - preserves structure and relevance.

Q: How do you budget a 1M token window?
A: Reserve 200K for output, use 800K for input. Keep system
   prompt minimal (~2K) to maximize available content.
""")