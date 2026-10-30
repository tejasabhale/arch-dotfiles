#!/usr/bin/env python3
"""
Intelligent Mock & Offline Fallback AI Provider.
Provides context-aware desktop responses offline, simulates streaming,
and guarantees that June is fully functional without requiring immediate API keys.
"""

import time
from typing import Any, Dict, Generator, List, Optional, Union

from assistant.providers.base import BaseProvider


class MockProvider(BaseProvider):
    """Offline contextual mock provider for June Assistant."""

    name: str = "mock"
    display_name: str = "June Offline Intelligence"

    MODELS = [
        "mock-smart",
        "mock-fast",
        "mock-system"
    ]

    def is_configured(self) -> bool:
        return True

    def list_models(self) -> List[str]:
        return list(self.MODELS)

    def test_connection(self) -> Dict[str, Any]:
        return {
            "success": True,
            "message": "June Offline Intelligence is active and ready.",
            "latency_ms": 1.2
        }

    def _generate_response(self, user_text: str, system_prompt: Optional[str] = None) -> str:
        prompt_lower = user_text.lower()

        if any(w in prompt_lower for w in ["shortcut", "keybind", "hotkey"]):
            return (
                "### 󰌌 Key Desktop Shortcuts\n\n"
                "- **Super + Space**: Application Launcher (Fuzzel / Quickshell)\n"
                "- **Super + J**: Toggle June AI Assistant\n"
                "- **Super + C**: Quick-Settings Control Center\n"
                "- **Super + D**: Productivity Dashboard (Clock, Tasks, Vitals)\n"
                "- **Super + Tab**: Workspace & Window Overview\n"
                "- **Super + N**: Notification Center\n"
                "- **Super + Return**: Kitty Terminal\n"
                "- **Super + Q**: Close Active Window\n"
                "- **Super + 1..5**: Switch Workspaces"
            )

        if any(w in prompt_lower for w in ["wifi", "wi-fi", "hotspot", "network"]):
            return (
                "### 󰖩 Networking & Wi-Fi Hotspot\n\n"
                "Your HP EliteBook 840 G5 supports Access Point (AP) mode on Intel Wi-Fi.\n"
                "- **Wi-Fi Manager**: Managed via NetworkManager D-Bus.\n"
                "- **Dedicated Hotspot**: Open Control Center (`Super+C`) -> Hotspot to generate an instant QR code for mobile devices.\n"
                "- **WPA Standard**: WPA2-Personal (AES) and WPA3-SAE are supported."
            )

        if any(w in prompt_lower for w in ["battery", "power", "charge"]):
            return (
                "### 󰁹 Power & Battery Profiles\n\n"
                "- Managed via UPower and `powerprofilesctl`.\n"
                "- Three power profiles are configured: **Balanced** (default), **Performance**, and **Power Saver**.\n"
                "- On battery discharge, backlight curves and compositor animation timings throttle automatically to conserve energy."
            )

        if any(w in prompt_lower for w in ["theme", "color", "midnight", "nordic", "forest", "violet"]):
            return (
                "### 󰔎 Centralized Theming Engine\n\n"
                "June Desktop supports 4 tokenized presets:\n"
                "1. **Midnight**: Dark indigo palette with crisp contrast.\n"
                "2. **Nordic Light**: Clean, warm daylight blue palette.\n"
                "3. **Forest**: Earthy dark pine green with gold accents.\n"
                "4. **Violet**: Dark amethyst purple with neon highlights.\n\n"
                "Switch themes instantly in Control Center (`Super+C`)."
            )

        if any(w in prompt_lower for w in ["hardware", "specs", "ram", "cpu", "laptop"]):
            return (
                "### 󰌢 Target Hardware Profile\n\n"
                "- **Machine**: HP EliteBook 840 G5\n"
                "- **CPU**: Intel Core 8th Gen (4 cores / 8 threads)\n"
                "- **GPU**: Intel UHD Graphics 620\n"
                "- **Memory**: 8 GB DDR4 (Idle footprint strictly budget-constrained under 1.5 - 2.0 GB)\n"
                "- **Boot Mode**: UEFI Dual-boot alongside Windows 11."
            )

        if any(w in prompt_lower for w in ["hello", "hi", "hey"]):
            return (
                "Hello! I am **June**, your personal desktop assistant for Arch Linux.\n\n"
                "I am integrated with your Hyprland compositor, system controls, and development tools. "
                "How can I help you today? You can ask about system shortcuts, hardware controls, "
                "or write code."
            )

        # Default intelligent response
        return (
            f"I have received your request:\n> *\"{user_text}\"*\n\n"
            "I am currently operating in **June Offline Mode**. All desktop shell features, "
            "shortcuts, theme customization, and system controls are fully accessible.\n\n"
            "To connect cloud reasoning (Google Gemini, OpenAI, Anthropic) or local models (Ollama), "
            "configure your API keys or run `ollama serve`."
        )

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
        # Extract the latest user message
        user_text = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_text = msg.get("content", "")
                break

        full_reply = self._generate_response(user_text, system_prompt=system_prompt)

        if not stream:
            return full_reply

        def streamer() -> Generator[str, None, None]:
            words = full_reply.split(" ")
            for i, word in enumerate(words):
                yield word + (" " if i < len(words) - 1 else "")
                time.sleep(0.015)

        return streamer()
