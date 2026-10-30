#!/usr/bin/env python3
"""
Assistant Identity Customization Service.
Manages display name (default: "June"), avatar, personality presets,
system prompts, and provider preferences in ~/.config/tejas-os/assistant.json.

Complies with AGENTS.md Rule 2.1:
Renaming the assistant updates display names cleanly without breaking internal
service identifiers.
"""

from copy import deepcopy
import json
import os
import sys
import tempfile
from typing import Any, Dict, Optional

DEFAULT_IDENTITY_CONFIG = {
    "name": "June",
    "avatar": "󱚣",
    "tagline": "Personal Desktop Intelligence",
    "personality": "helpful",  # helpful, coder, concise, creative
    "system_prompt": (
        "You are June, an intelligent, high-performance personal AI desktop companion "
        "integrated into Arch Linux on an HP EliteBook 840 G5 running Hyprland and Quickshell. "
        "You communicate clearly, concisely, and helpfully. You respect system security, "
        "protect dual-boot safety, and assist with coding, system administration, and daily tasks."
    ),
    "provider": "mock",  # gemini, openai, anthropic, ollama, mock
    "model": "mock-smart",
    "temperature": 0.7,
    "max_tokens": 2048,
    "stream": True,
    "voice_enabled": False,
    "tts_voice": "en_US-lessac-medium"
}

PERSONALITY_PRESETS = {
    "helpful": (
        "You are June, a friendly, insightful, and adaptable desktop assistant. "
        "Provide direct answers with helpful explanations when appropriate."
    ),
    "coder": (
        "You are June, an expert software engineer and Linux systems specialist. "
        "Focus on correct code snippets, terminal commands, architecture, and debugging. "
        "Avoid unnecessary fluff."
    ),
    "concise": (
        "You are June, an ultra-concise assistant. Give brief, direct answers, commands, "
        "or summaries without preamble or repetitive disclaimers."
    ),
    "creative": (
        "You are June, an imaginative brainstorming partner and creative writer. "
        "Offer inventive ideas, nuanced prose, and varied perspectives."
    )
}


class IdentityManager:
    """Manages the assistant's identity, display name, and personality profile."""

    CONFIG_DIR = os.path.expanduser("~/.config/tejas-os")
    CONFIG_PATH = os.path.join(CONFIG_DIR, "assistant.json")

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self.CONFIG_PATH
        self._config = deepcopy(DEFAULT_IDENTITY_CONFIG)
        self.load()

    def load(self) -> Dict[str, Any]:
        """Loads configuration from JSON file or initializes with defaults."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._config.update(data)
            except Exception as e:
                print(f"[IdentityManager] Warning loading {self.config_path}: {e}", file=sys.stderr)
        else:
            self.save()
        return deepcopy(self._config)

    def save(self) -> bool:
        """Atomically saves configuration to JSON file."""
        try:
            target_dir = os.path.dirname(self.config_path)
            os.makedirs(target_dir, exist_ok=True)

            # Atomic write via temporary file
            with tempfile.NamedTemporaryFile("w", dir=target_dir, delete=False, encoding="utf-8") as tf:
                json.dump(self._config, tf, indent=2, ensure_ascii=False)
                temp_name = tf.name

            # Atomic replace
            os.replace(temp_name, self.config_path)
            return True
        except Exception as e:
            print(f"[IdentityManager] Error saving {self.config_path}: {e}", file=sys.stderr)
            return False

    def get_display_name(self) -> str:
        """Returns the user-configured display name (e.g. 'June')."""
        return self._config.get("name", "June")

    def set_display_name(self, name: str) -> bool:
        """Sets the user-configured display name without altering internal service IDs."""
        cleaned = name.strip()
        if not cleaned:
            return False
        self._config["name"] = cleaned
        return self.save()

    def get_avatar(self) -> str:
        """Returns the avatar glyph or icon path."""
        return self._config.get("avatar", "󱚣")

    def set_avatar(self, avatar: str) -> bool:
        """Sets the avatar glyph or image path."""
        self._config["avatar"] = avatar.strip()
        return self.save()

    def get_personality(self) -> str:
        """Returns the active personality preset name."""
        return self._config.get("personality", "helpful")

    def set_personality(self, preset_name: str) -> bool:
        """Sets personality preset and updates the base system prompt."""
        if preset_name in PERSONALITY_PRESETS:
            self._config["personality"] = preset_name
            self._config["system_prompt"] = PERSONALITY_PRESETS[preset_name]
            return self.save()
        return False

    def get_system_prompt(self) -> str:
        """Returns full effective system prompt incorporating identity and personality."""
        base_prompt = self._config.get("system_prompt") or PERSONALITY_PRESETS.get(self.get_personality(), "")
        name = self.get_display_name()
        # Ensure display name is reflected in the prompt
        if "June" in base_prompt and name != "June":
            base_prompt = base_prompt.replace("June", name)
        return base_prompt

    def set_custom_prompt(self, prompt: str) -> bool:
        """Sets custom user instructions."""
        self._config["system_prompt"] = prompt.strip()
        self._config["personality"] = "custom"
        return self.save()

    def get_provider(self) -> str:
        """Returns the active provider identifier."""
        return self._config.get("provider", "mock")

    def set_provider(self, provider_id: str, model_id: Optional[str] = None) -> bool:
        """Sets the active AI provider and optional model."""
        self._config["provider"] = provider_id.lower().strip()
        if model_id:
            self._config["model"] = model_id.strip()
        return self.save()

    def get_model(self) -> str:
        """Returns the active model name."""
        return self._config.get("model", "mock-smart")

    def set_model(self, model_id: str) -> bool:
        """Sets active model name."""
        self._config["model"] = model_id.strip()
        return self.save()

    def get_config(self) -> Dict[str, Any]:
        """Returns a snapshot of the full identity configuration."""
        return deepcopy(self._config)

    def update_config(self, updates: Dict[str, Any]) -> bool:
        """Updates multiple configuration properties."""
        for k, v in updates.items():
            if k in DEFAULT_IDENTITY_CONFIG:
                self._config[k] = v
        return self.save()
