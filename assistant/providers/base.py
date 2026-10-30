#!/usr/bin/env python3
"""
Base AI Provider Interface.
Defines standard contract for LLM provider adapters.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generator, List, Optional, Union


class BaseProvider(ABC):
    """Abstract base class for all AI model providers."""

    name: str = "base"
    display_name: str = "Base Provider"

    @abstractmethod
    def is_configured(self) -> bool:
        """Returns True if the required API keys or local services are available."""
        pass

    @abstractmethod
    def list_models(self) -> List[str]:
        """Returns list of supported/available model identifiers."""
        pass

    @abstractmethod
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
        """
        Executes a multi-turn chat completion.
        If stream is True, yields chunks of text as they arrive.
        Otherwise returns the full response string.
        """
        pass

    @abstractmethod
    def test_connection(self) -> Dict[str, Any]:
        """
        Verifies API connectivity or service availability.
        Returns a dictionary with 'success': bool, 'message': str, 'latency_ms': float.
        """
        pass
