# load .env values if present
import os
import sys
from dotenv import load_dotenv
import anthropic

load_dotenv()

# Read API key from environment or first CLI arg (safer than hardcoding)
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key and len(sys.argv) > 1:
    api_key = sys.argv[1]

if not api_key:
    print("Error: ANTHROPIC_API_KEY not set. Set env var, .env, or pass key as first arg.")
    sys.exit(1)

# Use the custom base URL required
base_url = os.getenv("ANTHROPIC_API_BASE", "https://api.opusmax.pro")

# Instantiate client explicitly with the key and base URL
client = anthropic.Anthropic(api_key=api_key, base_url=base_url)

response = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=100,
    messages=[
        {"role": "user", "content": "Say hello in one word."}
    ]
)

print(response.content[1].text)  # Index 1 = text block, 0 = thinking block