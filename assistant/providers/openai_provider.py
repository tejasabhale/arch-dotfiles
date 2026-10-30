#!/usr/bin/env python3
"""
OpenAI & Compatible REST API Provider.
Supports OpenAI GPT models or any standard OpenAI-compatible API endpoint.
"""

import json
import os
import time
from typing import Any, Dict, Generator, List, Optional, Union
import urllib.error
import urllib.request

from assistant.providers.base import BaseProvider


class OpenAIProvider(BaseProvider):
    """OpenAI API provider adapter."""

    name: str = "openai"
    display_name: str = "OpenAI GPT"

    DEFAULT_MODEL = "gpt-4o-mini"
    MODELS = [
        "gpt-4o-mini",
        "gpt-4o",
        "o3-mini",
    ]

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.base_url = (base_url or os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")).rstrip("/")

    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 5)

    def list_models(self) -> List[str]:
        return list(self.MODELS)

    def test_connection(self) -> Dict[str, Any]:
        if not self.is_configured():
            return {
                "success": False,
                "message": "OPENAI_API_KEY environment variable is not set.",
                "latency_ms": 0.0
            }

        start = time.time()
        try:
            url = f"{self.base_url}/models"
            req = urllib.request.Request(
                url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                method="GET"
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                latency = round((time.time() - start) * 1000, 2)
                return {
                    "success": True,
                    "message": "Connected to OpenAI API successfully.",
                    "latency_ms": latency
                }
        except Exception as e:
            latency = round((time.time() - start) * 1000, 2)
            return {
                "success": False,
                "message": f"OpenAI connection error: {str(e)}",
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
            raise ValueError("OPENAI_API_KEY is not configured.")

        selected_model = model or self.DEFAULT_MODEL
        all_messages = []
        if system_prompt:
            all_messages.append({"role": "system", "content": system_prompt})
        all_messages.extend(messages)

        payload = {
            "model": selected_model,
            "messages": all_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }

        data_bytes = json.dumps(payload).encode("utf-8")
        url = f"{self.base_url}/chat/completions"
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            },
            method="POST"
        )

        if not stream:
            with urllib.request.urlopen(req, timeout=30) as resp:
                res_json = json.loads(resp.read().decode("utf-8"))
                choices = res_json.get("choices", [])
                if choices:
                    return choices[0].get("message", {}).get("content", "")
                return ""

        def streamer() -> Generator[str, None, None]:
            with urllib.request.urlopen(req, timeout=30) as resp:
                for line in resp:
                    decoded = line.decode("utf-8").strip()
                    if decoded.startswith("data: "):
                        data_part = decoded[6:]
                        if data_part == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data_part)
                            choices = chunk.get("choices", [])
                            if choices:
                                delta = choices[0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield content
                        except Exception:
                            continue

        return streamer()
