"""
Common Ollama/Gemma 4 Client Utility
Shared across all 90 projects for consistent LLM interaction.
"""

import requests
import json
import sys
from typing import Optional, Generator


OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "gemma4"


def check_ollama_running() -> bool:
    """Check if Ollama server is running."""
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        return resp.status_code == 200
    except requests.ConnectionError:
        return False


def list_models() -> list:
    """List available Ollama models."""
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        data = resp.json()
        return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []


def chat(
    messages: list[dict],
    model: str = DEFAULT_MODEL,
    system_prompt: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 2048,
) -> str:
    """
    Send a chat request to Ollama and return the full response.

    Args:
        messages: List of {"role": "user"|"assistant", "content": "..."} dicts
        model: Model name (default: gemma4)
        system_prompt: Optional system prompt
        temperature: Creativity (0.0-1.0)
        max_tokens: Max response tokens

    Returns:
        The assistant's response text
    """
    if system_prompt:
        messages = [{"role": "system", "content": system_prompt}] + messages

    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
        },
    }

    try:
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json=payload,
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()["message"]["content"]
    except requests.exceptions.ConnectionError:
        print("Error: Ollama is not running. Start it with: ollama serve")
        sys.exit(1)
    except Exception as e:
        print(f"Error communicating with Ollama: {e}")
        sys.exit(1)


def chat_stream(
    messages: list[dict],
    model: str = DEFAULT_MODEL,
    system_prompt: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 2048,
) -> Generator[str, None, None]:
    """
    Stream a chat response from Ollama token by token.

    Yields:
        Individual tokens as they arrive
    """
    if system_prompt:
        messages = [{"role": "system", "content": system_prompt}] + messages

    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
        },
    }

    try:
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json=payload,
            stream=True,
            timeout=120,
        )
        resp.raise_for_status()
        for line in resp.iter_lines():
            if line:
                data = json.loads(line)
                token = data.get("message", {}).get("content", "")
                if token:
                    yield token
                if data.get("done", False):
                    break
    except requests.exceptions.ConnectionError:
        print("Error: Ollama is not running. Start it with: ollama serve")
        sys.exit(1)


def generate(
    prompt: str,
    model: str = DEFAULT_MODEL,
    system_prompt: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 2048,
) -> str:
    """
    Simple single-turn generation (non-chat API).

    Args:
        prompt: The input prompt
        model: Model name
        system_prompt: Optional system instruction
        temperature: Creativity level
        max_tokens: Max response tokens

    Returns:
        Generated text
    """
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
        },
    }
    if system_prompt:
        payload["system"] = system_prompt

    try:
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()["response"]
    except requests.exceptions.ConnectionError:
        print("Error: Ollama is not running. Start it with: ollama serve")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def embed(text: str, model: str = DEFAULT_MODEL) -> list[float]:
    """
    Get embeddings for text using Ollama.

    Args:
        text: Input text to embed
        model: Model name

    Returns:
        List of floats (embedding vector)
    """
    payload = {"model": model, "input": text}
    try:
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/embed",
            json=payload,
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()["embeddings"][0]
    except Exception as e:
        print(f"Error getting embeddings: {e}")
        return []
