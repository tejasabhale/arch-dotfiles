#!/usr/bin/env python3
"""
Google Gemini AI Provider.
Connects to Google's Generative Language REST API.
Uses Python standard library (urllib) for zero external dependencies,
ensuring low memory overhead on HP EliteBook 840 G5.
"""

import json
import os
import time
from typing import Any, Dict, Generator, List, Optional, Union
import urllib.error
import urllib.request

from assistant.providers.base import BaseProvider


class GeminiProvider(BaseProvider):
    """Google Gemini model provider using direct HTTPS REST API."""

    name: str = "gemini"
    display_name: str = "Google Gemini"

    DEFAULT_MODEL = "gemini-2.5-flash"
    MODELS = [
        "gemini-2.5-flash",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
    ]

    BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")

    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 5)

    def list_models(self) -> List[str]:
        return list(self.MODELS)

    def _convert_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        gemini_contents = []
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            g_role = "user" if role == "user" else "model"
            gemini_contents.append({
                "role": g_role,
                "parts": [{"text": content}]
            })
        return gemini_contents

    def test_connection(self) -> Dict[str, Any]:
        if not self.is_configured():
            return {
                "success": False,
                "message": "GEMINI_API_KEY environment variable is not set.",
                "latency_ms": 0.0
            }

        start = time.time()
        try:
            url = f"{self.BASE_URL}/models/{self.DEFAULT_MODEL}?key={self.api_key}"
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=10) as resp:
                latency = round((time.time() - start) * 1000, 2)
                return {
                    "success": True,
                    "message": f"Connected to Google Gemini ({self.DEFAULT_MODEL})",
                    "latency_ms": latency
                }
        except Exception as e:
            latency = round((time.time() - start) * 1000, 2)
            return {
                "success": False,
                "message": f"Gemini connection error: {str(e)}",
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
            raise ValueError("GEMINI_API_KEY is not configured.")

        selected_model = model or self.DEFAULT_MODEL
        contents = self._convert_messages(messages)

        payload: Dict[str, Any] = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            }
        }

        if system_prompt:
            payload["systemInstruction"] = {
                "parts": [{"text": system_prompt}]
            }

        data_bytes = json.dumps(payload).encode("utf-8")

        if not stream:
            url = f"{self.BASE_URL}/models/{selected_model}:generateContent?key={self.api_key}"
            req = urllib.request.Request(
                url,
                data=data_bytes,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                res_json = json.loads(resp.read().decode("utf-8"))
                try:
                    candidates = res_json.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        return "".join(p.get("text", "") for p in parts)
                    return ""
                except Exception as e:
                    raise RuntimeError(f"Error parsing Gemini response: {e}")

        # Streaming support via streamGenerateContent?alt=sse
        url = f"{self.BASE_URL}/models/{selected_model}:streamGenerateContent?alt=sse&key={self.api_key}"
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        def streamer() -> Generator[str, None, None]:
            with urllib.request.urlopen(req, timeout=30) as resp:
                for line in resp:
                    decoded = line.decode("utf-8").strip()
                    if decoded.startswith("data: "):
                        data_part = decoded[6:]
                        try:
                            chunk = json.loads(data_part)
                            candidates = chunk.get("candidates", [])
                            if candidates:
                                parts = candidates[0].get("content", {}).get("parts", [])
                                text = "".join(p.get("text", "") for p in parts)
                                if text:
                                    yield text
                        except Exception:
                            continue

        return streamer()
