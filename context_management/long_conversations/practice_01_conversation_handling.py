"""
PRACTICE 01: LONG CONVERSATION HANDLING
=======================================

Long Conversation Concepts:
- Conversations grow over time, consuming context
- Need strategies to maintain context without overflow
- Message summarization techniques
- Progressive context pruning
- Session resumption strategies

Key Strategies:
1. Rolling context (keep recent, prune old)
2. Summarization-based compression
3. Memory bank patterns
4. Context refresh techniques
5. Session checkpointing
"""

import os
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
# SCENARIO 1: Rolling Context Pattern
# =============================================================================

class RollingContextManager:
    """
    ROLLING CONTEXT: Keep only recent messages within limit

    Interview Q: How do you handle conversations that grow too long?
    A: Implement rolling context - keep only the most recent messages
       that fit within the token budget. Discard older messages.

    BEST PRACTICE:
    - Keep last N messages (configurable)
    - Add summary of discarded messages
    - Maintain conversation continuity
    """

    def __init__(self, max_messages=20, token_budget=800000):
        self.max_messages = max_messages
        self.token_budget = token_budget
        self.history = []
        self.summary = ""

    def add_message(self, role, content):
        """Add message to conversation"""
        self.history.append({"role": role, "content": content})
        self._prune_if_needed()

    def _prune_if_needed(self):
        """Prune old messages if exceeding limits"""
        # Check message count limit
        while len(self.history) > self.max_messages:
            # Remove oldest non-system message
            for i, msg in enumerate(self.history):
                if msg["role"] != "system":
                    self.history.pop(i)
                    break

    def _estimate_tokens(self):
        """Estimate token count"""
        total_chars = sum(len(m["content"]) for m in self.history)
        return total_chars // 4

    def get_messages(self):
        """Get current messages (with summary if exists)"""
        if self.summary:
            return [{"role": "system", "content": f"Previous conversation summary: {self.summary}"}] + self.history
        return self.history

    def set_summary(self, summary_text):
        """Set conversation summary (called by summarizer)"""
        self.summary = summary_text
        # After summarizing, we can prune old messages
        self.history = self.history[-5:]  # Keep only recent


def demonstrate_rolling_context():
    """Show rolling context in action"""
    print("=" * 60)
    print("SCENARIO 1: Rolling Context Pattern")
    print("=" * 60)

    manager = RollingContextManager(max_messages=5)

    # Simulate long conversation
    conversation = [
        ("user", "Hi, I want to learn Python"),
        ("assistant", "Great! Python is a beginner-friendly language."),
        ("user", "What's the difference between lists and tuples?"),
        ("assistant", "Lists are mutable, tuples are immutable."),
        ("user", "Can you show me an example?"),
        ("assistant", "Sure! List: [1,2,3], Tuple: (1,2,3)"),
        ("user", "What about dictionaries?"),
        ("assistant", "Dictionaries store key-value pairs."),
        ("user", "Show me dictionary example"),
        ("assistant", "{'name': 'John', 'age': 30}"),
    ]

    print("Adding messages to conversation:")
    for role, content in conversation:
        manager.add_message(role, content)
        print(f"  {role}: {content[:40]}...")

    print(f"\nCurrent history length: {len(manager.history)}")
    print(f"Estimated tokens: {manager._estimate_tokens()}")
    print()


# =============================================================================
# SCENARIO 2: Summarization-Based Compression
# =============================================================================

def demonstrate_summarization():
    """
    REAL-TIME SCENARIO: Summarize old conversation to save space

    COMMON MISTAKE: Losing important context when pruning
    BEST PRACTICE: Summarize before pruning to preserve key information

    Interview Q: How do you preserve context when pruning?
    A: Summarize the conversation first, then replace old messages
       with a summary. This preserves key facts and decisions.
    """
    print("=" * 60)
    print("SCENARIO 2: Summarization-Based Compression")
    print("=" * 60)

    # Simulate old conversation that needs summarization
    old_messages = [
        {"role": "user", "content": "I need to build a web scraper"},
        {"role": "assistant", "content": "What website do you want to scrape?"},
        {"role": "user", "content": "News websites for articles"},
        {"role": "assistant", "content": "You'll need BeautifulSoup and requests libraries."},
        {"role": "user", "content": "How do I handle rate limiting?"},
        {"role": "assistant", "content": "Add delays between requests and respect robots.txt."},
        {"role": "user", "content": "What about JavaScript-rendered pages?"},
        {"role": "assistant", "content": "Use Selenium or Playwright for JS-heavy sites."},
    ]

    print("Original conversation (8 messages):")
    for msg in old_messages:
        print(f"  {msg['role']}: {msg['content'][:50]}...")

    # Generate summary
    summary_prompt = """Summarize this conversation briefly, keeping key facts:
- User is building a web scraper
- Target: News websites for articles
- Libraries mentioned: BeautifulSoup, requests
- Tools for JS: Selenium, Playwright
- Rate limiting handling required"""

    print("\n" + "-" * 40)
    print("Generated Summary:")
    print(summary_prompt)
    print("-" * 40)

    print("\nCompressed version (1 message instead of 8):")
    compressed = [{"role": "system", "content": f"Previous context summary: {summary_prompt}"}]
    print(f"  Messages: {len(old_messages)} -> {len(compressed)}")
    print(f"  Token reduction: ~90%")
    print()


# =============================================================================
# SCENARIO 3: Memory Bank Pattern
# =============================================================================

class MemoryBank:
    """
    MEMORY BANK: Long-term storage for conversation facts

    BEST PRACTICE: Store important facts in persistent memory
    Separate from short-term conversation context

    Structure:
    - Semantic memory: Facts learned
    - Episodic memory: Key events
    - Working memory: Current task context
    """

    def __init__(self):
        self.semantic = []   # Facts and knowledge
        self.episodic = []  # Key events/decisions
        self.working = {}   # Current context

    def add_fact(self, category, fact):
        """Add fact to semantic memory"""
        self.semantic.append({
            "category": category,
            "fact": fact,
            "timestamp": "now"  # Simplified
        })

    def add_event(self, event):
        """Add event to episodic memory"""
        self.episodic.append(event)

    def set_working(self, key, value):
        """Set working memory item"""
        self.working[key] = value

    def get_context(self):
        """Get formatted context for prompt"""
        context_parts = []

        if self.semantic:
            facts = "; ".join([f"{f['category']}: {f['fact']}" for f in self.semantic[-5:]])
            context_parts.append(f"Facts: {facts}")

        if self.working:
            work = "; ".join([f"{k}: {v}" for k, v in self.working.items()])
            context_parts.append(f"Current: {work}")

        return "; ".join(context_parts) if context_parts else ""

    def prune_old(self, keep_count=10):
        """Prune old semantic memories"""
        self.semantic = self.semantic[-keep_count:]


def demonstrate_memory_bank():
    """Show memory bank pattern"""
    print("=" * 60)
    print("SCENARIO 3: Memory Bank Pattern")
    print("=" * 60)

    memory = MemoryBank()

    # Add facts during conversation
    memory.add_fact("project", "Building a web scraper")
    memory.add_fact("tech", "Using Python, BeautifulSoup, requests")
    memory.add_fact("target", "News websites for articles")
    memory.add_fact("constraints", "Must handle rate limiting")

    # Set working context
    memory.set_working("current_task", "Writing spider.py")
    memory.set_working("status", "Debugging CSS selectors")

    print("Memory Bank Contents:")
    print(f"  Semantic memories: {len(memory.semantic)}")
    print(f"  Working context: {memory.working}")

    context = memory.get_context()
    print(f"\nFormatted context for prompt:")
    print(f"  '{context}'")
    print()


# =============================================================================
# SCENARIO 4: Session Checkpointing
# =============================================================================

class SessionCheckpointer:
    """
    SESSION CHECKPOINTING: Save and resume conversation state

    Interview Q: How do you handle session resumption?
    A: Implement checkpointing - save conversation state at key points.
       When resuming, load checkpoint and continue from there.

    BEST PRACTICE:
    - Save checkpoints at natural break points
    - Store summary of conversation so far
    - Enable resumption without full history reload
    """

    def __init__(self):
        self.checkpoints = []
        self.current_index = 0

    def create_checkpoint(self, messages, summary=""):
        """Create a checkpoint of current state"""
        checkpoint = {
            "index": len(self.checkpoints),
            "message_count": len(messages),
            "summary": summary or self._generate_summary(messages),
            "timestamp": "now"  # Simplified
        }
        self.checkpoints.append(checkpoint)
        self.current_index = len(self.checkpoints) - 1
        return checkpoint

    def _generate_summary(self, messages):
        """Generate brief summary of messages"""
        if not messages:
            return "Empty conversation"
        # Simple summary: count by role
        roles = {}
        for m in messages:
            roles[m["role"]] = roles.get(m["role"], 0) + 1
        return f"Conversation with {roles.get('user', 0)} user messages, {roles.get('assistant', 0)} assistant responses"

    def restore_checkpoint(self, index):
        """Restore to a specific checkpoint"""
        if 0 <= index < len(self.checkpoints):
            self.current_index = index
            return self.checkpoints[index]
        return None

    def get_latest_checkpoint(self):
        """Get the most recent checkpoint"""
        if self.checkpoints:
            return self.checkpoints[-1]
        return None


def demonstrate_checkpointing():
    """Show session checkpointing"""
    print("=" * 60)
    print("SCENARIO 4: Session Checkpointing")
    print("=" * 60)

    checkpointer = SessionCheckpointer()

    # Simulate conversation progress
    messages_phase1 = [
        {"role": "user", "content": "I want to learn Python"},
        {"role": "assistant", "content": "Great! Let's start with basics."},
    ]
    cp1 = checkpointer.create_checkpoint(messages_phase1, "Started Python basics")
    print(f"Checkpoint 1: {cp1['summary']}")

    messages_phase2 = [
        {"role": "user", "content": "What's a variable?"},
        {"role": "assistant", "content": "A variable stores data."},
    ]
    cp2 = checkpointer.create_checkpoint(messages_phase2, "Covered variables")
    print(f"Checkpoint 2: {cp2['summary']}")

    messages_phase3 = [
        {"role": "user", "content": "Show me an example"},
        {"role": "assistant", "content": "name = 'John'"},
    ]
    cp3 = checkpointer.create_checkpoint(messages_phase3, "Showed variable example")
    print(f"Checkpoint 3: {cp3['summary']}")

    print(f"\nTotal checkpoints: {len(checkpointer.checkpoints)}")
    print(f"Latest checkpoint: {checkpointer.get_latest_checkpoint()['summary']}")

    # Simulate session resumption
    print("\nResuming session...")
    restored = checkpointer.restore_checkpoint(1)
    print(f"Restored to: {restored['summary']}")
    print()


# =============================================================================
# SCENARIO 5: Progressive Context Pruning
# =============================================================================

def demonstrate_progressive_pruning():
    """
    REAL-TIME SCENARIO: Progressive pruning as conversation grows

    BEST PRACTICE: Prune gradually, not all at once
    - At 50% capacity: Note that pruning may be needed
    - At 75% capacity: Start light pruning
    - At 90% capacity: Aggressive pruning or summarization

    Interview Q: When should you start pruning context?
    A: Start before hitting limits. At 75% capacity, begin light
       pruning. At 90%, aggressively prune or summarize.
    """
    print("=" * 60)
    print("SCENARIO 5: Progressive Context Pruning")
    print("=" * 60)

    class ProgressivePruner:
        def __init__(self, max_tokens):
            self.max_tokens = max_tokens
            self.messages = []

        def add(self, role, content):
            self.messages.append({"role": role, "content": content})
            self._check_and_prune()

        def _estimate_tokens(self):
            return sum(len(m["content"]) for m in self.messages) // 4

        def _check_and_prune(self):
            current = self._estimate_tokens()
            usage_percent = (current / self.max_tokens) * 100

            if usage_percent > 90:
                # Aggressive pruning
                self.messages = self.messages[-3:]
                print(f"  [90%+] Aggressive prune: {len(self.messages)} msgs")
            elif usage_percent > 75:
                # Light pruning
                if len(self.messages) > 8:
                    self.messages = self.messages[-8:]
                    print(f"  [75%+] Light prune: {len(self.messages)} msgs")
            elif usage_percent > 50:
                print(f"  [50%+] Monitor: {usage_percent:.0f}% usage")
            else:
                print(f"  OK: {usage_percent:.0f}% usage")

    pruner = ProgressivePruner(max_tokens=1000)

    print("Adding messages and monitoring usage:")
    messages = [
        ("user", "Message 1"),
        ("assistant", "Response 1"),
        ("user", "Message 2"),
        ("assistant", "Response 2"),
        ("user", "Message 3"),
        ("assistant", "Response 3"),
        ("user", "Message 4"),
        ("assistant", "Response 4"),
        ("user", "Message 5 - This is getting long"),
        ("assistant", "Response 5 - Also long"),
        ("user", "Message 6 - Even longer content here"),
        ("assistant", "Response 6 - More content"),
        ("user", "Message 7 - Approaching limit"),
        ("assistant", "Response 7 - Almost there"),
        ("user", "Message 8 - At the limit now"),
    ]

    for role, content in messages:
        pruner.add(role, content)

    print()


# =============================================================================
# SCENARIO 6: Context Refresh Pattern
# =============================================================================

def demonstrate_context_refresh():
    """
    REAL-TIME SCENARIO: Refreshing context with new system prompt

    BEST PRACTICE: When context gets stale:
    1. Save checkpoint
    2. Create new conversation with refreshed context
    3. Include summary of previous conversation

    Interview Q: How do you handle context that has gone stale?
    A: Refresh by creating a new session context with summary
       of previous conversation. Old context is summarized,
       not lost.
    """
    print("=" * 60)
    print("SCENARIO 6: Context Refresh Pattern")
    print("=" * 60)

    # Old conversation context (simulated)
    old_conversation_summary = """
    User is building a Python web scraper.
    Discussed: BeautifulSoup, requests, rate limiting.
    Current task: Debugging CSS selectors.
    User's skill level: Intermediate Python.
    """

    # New fresh context for continuation
    new_system_prompt = """You are continuing a conversation about building a web scraper.
Previous context summary:
{old_summary}

Guidelines:
- Reference previous decisions and agreements
- Don't repeat explanations already given
- Build on established context
""".format(old_summary=old_conversation_summary)

    print("Original context (summarized):")
    print(old_conversation_summary[:200])
    print("\n" + "-" * 40)
    print("\nNew refreshed context:")
    print(new_system_prompt[:300])
    print("\nKey benefit: Fresh start with preserved context")
    print()


# =============================================================================
# SCENARIO 7: Long Conversation with API Call
# =============================================================================

def demonstrate_long_conversation_api():
    """Show handling long conversation with actual API call"""
    print("=" * 60)
    print("SCENARIO 7: Long Conversation API Call")
    print("=" * 60)

    try:
        # Simulate a long conversation
        conversation = [
            {"role": "system", "content": "You are a helpful Python teaching assistant."},
            {"role": "user", "content": "What are Python lists?"},
            {"role": "assistant", "content": "Lists are ordered, mutable collections that can hold items of different types."},
            {"role": "user", "content": "Give me an example."},
            {"role": "assistant", "content": "my_list = [1, 'hello', 3.14, True]"},
            {"role": "user", "content": "How do I add items?"},
            {"role": "assistant", "content": "Use append() to add to end, insert() to add at position."},
        ]

        print(f"Sending {len(conversation)} messages to API...")
        print(f"Estimated tokens: {sum(len(m['content']) for m in conversation) // 4}")

        # Make API call
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            messages=conversation
        )

        print(f"\nResponse received!")
        print(f"Output tokens: {response.usage.output_tokens}")
        print(f"Content: {response.content[0].text[:100]}...")

    except Exception as e:
        print(f"Note: API call skipped or failed - {type(e).__name__}")
        print("This is expected if API key is not configured.")
    print()


# =============================================================================
# MAIN: Run All Scenarios
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("LONG CONVERSATION HANDLING - PRACTICE FILE")
    print("=" * 60 + "\n")

    demonstrate_rolling_context()
    demonstrate_summarization()
    demonstrate_memory_bank()
    demonstrate_checkpointing()
    demonstrate_progressive_pruning()
    demonstrate_context_refresh()
    demonstrate_long_conversation_api()

    print("\n" + "=" * 60)
    print("WHAT WE HAVE LEARNT")
    print("=" * 60)
    print("""
1. ROLLING CONTEXT PATTERN
   - Keep only recent messages within limit
   - Remove oldest non-system messages when full
   - Add summary before pruning to preserve context

2. SUMMARIZATION-BASED COMPRESSION
   - Summarize old conversation before pruning
   - Replace many messages with single summary
   - Preserve key facts and decisions

3. MEMORY BANK PATTERN
   - Separate long-term facts from short-term context
   - Semantic memory: persistent facts
   - Working memory: current task context
   - Episodic memory: key events

4. SESSION CHECKPOINTING
   - Save checkpoints at natural break points
   - Store summary with checkpoint
   - Enable resumption without full reload

5. PROGRESSIVE PRUNING
   - Start pruning before hitting limits (75%)
   - More aggressive as usage increases
   - Monitor and adjust thresholds

6. CONTEXT REFRESH
   - Create fresh context with summary of old
   - Preserve continuity while resetting
   - Reference previous decisions

INTERVIEW QUESTIONS & ANSWERS:
------------------------------
Q: How do you handle conversations that grow too long?
A: Implement rolling context - keep recent messages,
   summarize old ones, prune when approaching limits.

Q: How do you preserve context when pruning?
A: Summarize the conversation first, then replace
   old messages with the summary to preserve key facts.

Q: What is session checkpointing?
A: Saving conversation state at key points to enable
   resumption later without reloading full history.

Q: When should you start pruning context?
A: Start before hitting limits - at 75% capacity begin
   light pruning, at 90% be more aggressive.
""")