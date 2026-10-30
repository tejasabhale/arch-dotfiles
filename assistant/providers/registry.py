#!/usr/bin/env python3
"""
Provider Registry & Factory.
Central manager for AI model providers with intelligent fallback.
"""

from typing import Any, Dict, List, Optional

from assistant.providers.anthropic_provider import AnthropicProvider
from assistant.providers.base import BaseProvider
from assistant.providers.gemini_provider import GeminiProvider
from assistant.providers.mock_provider import MockProvider
from assistant.providers.ollama_provider import OllamaProvider
from assistant.providers.openai_provider import OpenAIProvider


class ProviderRegistry:
    """Registry maintaining active LLM providers and fallback logic."""

    def __init__(self):
        self._providers: Dict[str, BaseProvider] = {}
        self._register_default_providers()

    def _register_default_providers(self):
        self.register(MockProvider())
        self.register(GeminiProvider())
        self.register(OpenAIProvider())
        self.register(AnthropicProvider())
        self.register(OllamaProvider())

    def register(self, provider: BaseProvider):
        self._providers[provider.name.lower()] = provider

    def get_provider(self, name: Optional[str] = None) -> BaseProvider:
        """
        Retrieves provider by name.
        Falls back to MockProvider if requested provider is unknown or unconfigured.
        """
        if name:
            p_name = name.lower().strip()
            if p_name in self._providers:
                target = self._providers[p_name]
                if target.is_configured():
                    return target
                # If target is not configured, check if user specifically asked for mock
                if p_name == "mock":
                    return target

        # If gemini is configured, prefer it as default cloud
        gemini = self._providers.get("gemini")
        if gemini and gemini.is_configured():
            return gemini

        # Fallback to offline mock provider
        return self._providers.get("mock", MockProvider())

    def list_providers(self) -> List[Dict[str, Any]]:
        """Returns metadata and configuration status for all registered providers."""
        results = []
        for name, p in self._providers.items():
            results.append({
                "id": p.name,
                "display_name": p.display_name,
                "configured": p.is_configured(),
                "models": p.list_models(),
                "is_local": p.name in ["mock", "ollama"]
            })
        return results
