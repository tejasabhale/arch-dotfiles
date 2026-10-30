#!/usr/bin/env python3
"""
Local Ollama AI Provider.
Connects to local Ollama daemon at http://localhost:11434.
Opt-in privacy-first local SLM inference (e.g. Llama 3.2 1B, Qwen 2.5 1.5B).
"""

import json
import os
import time
from typing import Any, Dict, Generator, List, Optional, Union
import urllib.error
import urllib.request

from assistant.providers.base import BaseProvider


class OllamaProvider(BaseProvider):
    """Local Ollama model provider adapter."""

    name: str = "ollama"
    display_name: str = "Local Ollama"

    DEFAULT_MODEL = "llama3.2:1b"
    FALLBACK_MODELS = [
        "llama3.2:1b",
        "qwen2.5:1.5b",
        "mistral:latest",
    ]

    def __init__(self, host: Optional[str] = None):
        self.host = (host or os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")).rstrip("/")

    def is_configured(self) -> bool:
        try:
            req = urllib.request.Request(f"{self.host}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=0.3) as resp:
                return resp.status == 200
        except Exception:
            return False

    def list_models(self) -> List[str]:
        try:
            req = urllib.request.Request(f"{self.host}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                models = [m.get("name") for m in data.get("models", []) if "name" in m]
                return models if models else self.FALLBACK_MODELS
        except Exception:
            return self.FALLBACK_MODELS

    def test_connection(self) -> Dict[str, Any]:
        start = time.time()
        try:
            req = urllib.request.Request(f"{self.host}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                latency = round((time.time() - start) * 1000, 2)
                data = json.loads(resp.read().decode("utf-8"))
                models = [m.get("name") for m in data.get("models", [])]
                return {
                    "success": True,
                    "message": f"Connected to local Ollama ({len(models)} models available).",
                    "latency_ms": latency,
                    "models": models
                }
        except Exception as e:
            latency = round((time.time() - start) * 1000, 2)
            return {
                "success": False,
                "message": f"Ollama daemon not reachable at {self.host} (Start with 'ollama serve').",
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
        selected_model = model or self.DEFAULT_MODEL
        all_messages = []
        if system_prompt:
            all_messages.append({"role": "system", "content": system_prompt})
        all_messages.extend(messages)

        payload = {
            "model": selected_model,
            "messages": all_messages,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self.host}/api/chat",
            data=data_bytes,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        if not stream:
            with urllib.request.urlopen(req, timeout=60) as resp:
                res_json = json.loads(resp.read().decode("utf-8"))
                return res_json.get("message", {}).get("content", "")

        def streamer() -> Generator[str, None, None]:
            with urllib.request.urlopen(req, timeout=60) as resp:
                for line in resp:
                    if line:
                        try:
                            chunk = json.loads(line.decode("utf-8"))
                            content = chunk.get("message", {}).get("content", "")
                            if content:
                                yield content
                        except Exception:
                            continue

        return streamer()
