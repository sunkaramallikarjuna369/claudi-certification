"""
PRACTICE 6: STATEFUL AGENT
An agent that REMEMBERS things across conversations!
"""

from anthropic import Anthropic
from dotenv import load_dotenv
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY", "")
api_base = os.getenv("ANTHROPIC_API_BASE", "")

client_kwargs = {"api_key": api_key} if api_key else {}
if api_base:
    client_kwargs["base_url"] = api_base
client = Anthropic(**client_kwargs)


@dataclass
class Conversation:
    """Represents a single conversation session."""
    id: str
    created_at: datetime
    messages: List[Dict] = field(default_factory=list)
    tool_calls: List[Dict] = field(default_factory=list)
    status: str = "active"


class StatefulAgent:
    """An AI agent that maintains state across multiple conversations."""

    def __init__(self, name: str = "assistant"):
        """Initialize the agent."""
        print(f"Initializing StatefulAgent: '{name}'")

        self.name = name
        self.conversations: Dict[str, Conversation] = {}
        self.current_session_id: str | None = None
        self.global_tools = []

        print(f"   Agent '{name}' created")
        print(f"   Ready to create sessions\n")

    def add_tools(self, tools: List[Dict]):
        """Add tools that this agent can use."""
        print(f"Adding {len(tools)} tool(s) to the agent:")
        for tool in tools:
            print(f"   - {tool['name']}")

        self.global_tools.extend(tools)
        print(f"   Tools are now available to all sessions\n")

    def create_session(self, session_id: str) -> Conversation:
        """Create a new conversation session."""
        print(f"Creating session: '{session_id}'")

        new_session = Conversation(
            id=session_id,
            created_at=datetime.now()
        )

        self.conversations[session_id] = new_session
        self.current_session_id = session_id

        print(f"   Session '{session_id}' created and activated\n")

        return new_session

    def switch_session(self, session_id: str) -> bool:
        """Switch to a different conversation session."""
        if session_id in self.conversations:
            old_session = self.current_session_id
            self.current_session_id = session_id

            print(f"Switched from session '{old_session}' to '{session_id}'\n")
            return True
        else:
            print(f"Session '{session_id}' not found!\n")
            return False

    def add_message(self, role: str, content: str):
        """Add a message to the current session's history."""
        if self.current_session_id:
            self.conversations[self.current_session_id].messages.append({
                "role": role,
                "content": content
            })

    def add_tool_call(self, tool_name: str, tool_input: dict, result: str):
        """Record a tool call in the current session."""
        if self.current_session_id:
            self.conversations[self.current_session_id].tool_calls.append({
                "tool": tool_name,
                "input": tool_input,
                "result": result,
                "timestamp": datetime.now().isoformat()
            })

    def get_history(self) -> List[Dict]:
        """Get the conversation history for the current session."""
        if self.current_session_id:
            return self.conversations[self.current_session_id].messages
        return []

    def run(self, user_message: str, session_id: str = None) -> str:
        """Run the agentic loop for the current (or specified) session."""
        if session_id and session_id not in self.conversations:
            self.create_session(session_id)

        if not self.current_session_id:
            self.create_session("default")

        self.add_message("user", user_message)

        messages = self.get_history()

        print(f"Running agent in session: '{self.current_session_id}'")
        print(f"   Messages in history: {len(messages)}\n")

        while True:
            response = client.messages.create(
                model="claude-haiku-4-5-20250601",
                max_tokens=4096,
                messages=messages,
                tools=self.global_tools,
            )

            if response.stop_reason == "tool_use":
                assistant_message = {"role": "assistant", "content": []}
                tool_results_to_add = []

                for block in response.content:
                    if block.type == "text" and block.text:
                        assistant_message["content"].append({
                            "type": "text",
                            "text": block.text
                        })
                        self.add_message("assistant", block.text)

                    elif block.type == "tool_use":
                        result = execute_tool(block.name, block.input)

                        self.add_tool_call(block.name, block.input, result)

                        print(f"Tool used: {block.name}")
                        print(f"   Input: {block.input}")
                        print(f"   Result: {result}\n")

                        assistant_message["content"].append({
                            "type": "tool_use",
                            "id": block.id,
                            "name": block.name,
                            "input": block.input
                        })

                        tool_results_to_add.append({
                            "tool_use_id": block.id,
                            "content": result
                        })

                messages.append(assistant_message)

                for tool_result in tool_results_to_add:
                    messages.append({
                        "role": "user",
                        "content": [{
                            "type": "tool_result",
                            "tool_use_id": tool_result["tool_use_id"],
                            "content": tool_result["content"]
                        }]
                    })

                continue

            elif response.stop_reason == "end_turn":
                final_text = ""
                for block in response.content:
                    if block.type == "text" and block.text:
                        final_text = block.text
                        break

                self.add_message("assistant", final_text)

                print(f"Response recorded in session '{self.current_session_id}'\n")

                return final_text

    def get_session_summary(self, session_id: str = None) -> Dict:
        """Get a summary of a session."""
        sid = session_id or self.current_session_id

        if sid and sid in self.conversations:
            conv = self.conversations[sid]
            return {
                "id": conv.id,
                "created_at": conv.created_at.isoformat(),
                "message_count": len(conv.messages),
                "tool_call_count": len(conv.tool_calls),
                "status": conv.status
            }
        return {}


tools = [
    {
        "name": "search",
        "description": "Search for information on the web",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "calculator",
        "description": "Perform mathematical calculations",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "Math expression"}
            },
            "required": ["expression"]
        }
    }
]


def execute_tool(name: str, tool_input: dict) -> str:
    """Execute a tool (mock implementation)."""
    if name == "search":
        return f"Search results for '{tool_input['query']}': [mock results]"
    elif name == "calculator":
        try:
            return str(eval(tool_input["expression"]))
        except:
            return "Error in calculation"
    return "Unknown tool"


if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    print("\n" + "="*60)
    print("PRACTICE 6: STATEFUL AGENT")
    print("="*60)

    agent = StatefulAgent(name="research-assistant")
    agent.add_tools(tools)

    print("="*60)
    print("STEP 1: Create the Stateful Agent")
    print("="*60)

    print("\nUser: 'What is the capital of France?'\n")
    response = agent.run(
        "What is the capital of France?",
        session_id="research-1"
    )
    print(f"Agent: {response[:100]}...")

    print("\n" + "="*60)
    print("STEP 2: Start Math Session (Different conversation!)")
    print("="*60)

    print("\nUser: 'What is 25 * 48?'\n")
    response = agent.run(
        "What is 25 * 48?",
        session_id="math-1"
    )
    print(f"Agent: {response[:100]}...")

    print("\n" + "="*60)
    print("STEP 3: Switch back to Research Session")
    print("="*60)

    print("\nAgent.switch_session('research-1')\n")

    agent.switch_session("research-1")

    print("\nUser: 'What about Germany?'\n")
    response = agent.run(
        "What about Germany?",
        session_id="research-1"
    )
    print(f"Agent: {response[:100]}...")

    print("\n" + "="*60)
    print("STEP 4: Session Summaries")
    print("="*60)

    print("\nSESSION SUMMARIES:\n")

    for sid in ["research-1", "math-1"]:
        summary = agent.get_session_summary(sid)
        print(f"   Session '{sid}':")
        print(f"      - Created: {summary.get('created_at', 'N/A')}")
        print(f"      - Messages: {summary.get('message_count', 0)}")
        print(f"      - Tool calls: {summary.get('tool_call_count', 0)}")
        print(f"      - Status: {summary.get('status', 'unknown')}")
        print()

    print("""
================================================================================
WHAT JUST HAPPENED?
================================================================================

    1. We created a StatefulAgent that REMEMBERS conversations
    2. Session "research-1": Asked about France, then Germany (context preserved!)
    3. Session "math-1": Separate conversation about 25 * 48
    4. We SWITCHED back to research-1 and Claude remembered the France topic!
    5. Each session maintains its own history of messages and tool calls
    6. Sessions can run independently or be switched between

    KEY INSIGHT: Stateful agents maintain CONTEXT across interactions!
    This is essential for long-running tasks and multi-turn conversations.
    Without state, each query is isolated - with state, the agent learns.
================================================================================
""")
    print("="*60)
    print("PROGRAM COMPLETE!")
    print("="*60)