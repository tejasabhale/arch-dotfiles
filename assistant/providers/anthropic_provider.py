#!/usr/bin/env python3
"""
Anthropic Claude AI Provider.
Connects to Anthropic's Messages REST API.
"""

import json
import os
import time
from typing import Any, Dict, Generator, List, Optional, Union
import urllib.error
import urllib.request

from assistant.providers.base import BaseProvider


class AnthropicProvider(BaseProvider):
    """Anthropic Claude model provider adapter."""

    name: str = "anthropic"
    display_name: str = "Anthropic Claude"

    DEFAULT_MODEL = "claude-3-5-sonnet-latest"
    MODELS = [
        "claude-3-5-sonnet-latest",
        "claude-3-5-haiku-latest",
    ]

    BASE_URL = "https://api.anthropic.com/v1"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")

    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 5)

    def list_models(self) -> List[str]:
        return list(self.MODELS)

    def test_connection(self) -> Dict[str, Any]:
        if not self.is_configured():
            return {
                "success": False,
                "message": "ANTHROPIC_API_KEY environment variable is not set.",
                "latency_ms": 0.0
            }

        start = time.time()
        try:
            # Send a minimal test message
            payload = {
                "model": self.DEFAULT_MODEL,
                "max_tokens": 10,
                "messages": [{"role": "user", "content": "ping"}]
            }
            req = urllib.request.Request(
                f"{self.BASE_URL}/messages",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                latency = round((time.time() - start) * 1000, 2)
                return {
                    "success": True,
                    "message": "Connected to Anthropic Claude successfully.",
                    "latency_ms": latency
                }
        except Exception as e:
            latency = round((time.time() - start) * 1000, 2)
            return {
                "success": False,
                "message": f"Anthropic connection error: {str(e)}",
                "latency_ms": latency
            }

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        stream: bool = False,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> Union[str, Generator[str, None, None]]:
        if not self.is_configured():
            raise ValueError("ANTHROPIC_API_KEY is not configured.")

        selected_model = model or self.DEFAULT_MODEL

        # Claude requires alternating user and assistant messages; filter out system from messages
        filtered_messages = []
        for m in messages:
            if m.get("role") in ["user", "assistant"]:
                filtered_messages.append({
                    "role": m.get("role"),
                    "content": m.get("content", "")
                })

        payload: Dict[str, Any] = {
            "model": selected_model,
            "max_tokens": max_tokens,
            "messages": filtered_messages,
            "temperature": temperature,
            "stream": stream
        }

        if system_prompt:
            payload["system"] = system_prompt

        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self.BASE_URL}/messages",
            data=data_bytes,
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            method="POST"
        )

        if not stream:
            with urllib.request.urlopen(req, timeout=30) as resp:
                res_json = json.loads(resp.read().decode("utf-8"))
                content_blocks = res_json.get("content", [])
                text_parts = [b.get("text", "") for b in content_blocks if b.get("type") == "text"]
                return "".join(text_parts)

        def streamer() -> Generator[str, None, None]:
            with urllib.request.urlopen(req, timeout=30) as resp:
                for line in resp:
                    decoded = line.decode("utf-8").strip()
                    if decoded.startswith("data: "):
                        data_part = decoded[6:]
                        try:
                            chunk = json.loads(data_part)
                            if chunk.get("type") == "content_block_delta":
                                delta = chunk.get("delta", {})
                                if delta.get("type") == "text_delta":
                                    yield delta.get("text", "")
                        except Exception:
                            continue

        return streamer()
