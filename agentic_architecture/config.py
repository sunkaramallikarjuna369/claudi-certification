"""
Shared Configuration for Agentic Projects
=========================================
This module handles API client setup with proper .env loading.
All practice files should import from here instead of creating their own client.
"""

from dotenv import load_dotenv
from anthropic import Anthropic
import os

load_dotenv()


def get_client():
    """
    Create and return a configured Anthropic client.

    Reads from .env file:
    - ANTHROPIC_API_KEY: Your API key (required)
    - ANTHROPIC_API_BASE: Custom API endpoint (optional)

    Returns:
    Anthropic: Configured client instance
    """
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    api_base = os.getenv("ANTHROPIC_API_BASE", "")

    client_kwargs = {}
    if api_key:
        client_kwargs["api_key"] = api_key
    if api_base:
        client_kwargs["base_url"] = api_base

    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY not found in .env file!\n"
            "Please create a .env file with your API key:\n"
            "ANTHROPIC_API_KEY=sk-ant-your-key-here"
        )

    return Anthropic(**client_kwargs)


_client = None


def client():
    """Get or create the shared client instance."""
    global _client
    if _client is None:
        _client = get_client()
    return _client