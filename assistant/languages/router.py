#!/usr/bin/env python3
"""
7 Language Combinations Router & Multilingual Prompt Engine.
Manages user language preferences and constructs prompts for LLM models.
Complies with AGENTS.md Rule 2.3: All 7 language combinations and trilingual code-switching.
"""

from copy import deepcopy
import json
import os
import tempfile
from typing import Any, Dict, Optional, Tuple

from assistant.languages.detector import LanguageProfile, MultilingualDetector

DEFAULT_LANGUAGES_CONFIG = {
    "primary_language": "auto",          # "auto", "en", "hi", "mr"
    "preferred_combination": "auto",     # "auto", "en", "hi", "mr", "en+hi", "en+mr", "hi+mr", "en+hi+mr"
    "script_mode": "mirror_input",       # "mirror_input", "native_devanagari", "romanized", "english"
    "code_switching_enabled": True,      # Allow mid-sentence switching
    "tts_voice_en": "en_US-lessac-medium",
    "tts_voice_hi": "hi_IN",
    "tts_voice_mr": "mr_IN",
}

# Combination instructions injected into system prompt
COMBINATION_PROMPTS = {
    "en": (
        "Respond in clear, natural, and concise English. Maintain technical precision."
    ),
    "hi": (
        "हिंदी में उत्तर दें (Respond in natural Hindi). तकनीकी शब्दों को सरल रखें. "
        "यदि उपयोगकर्ता रोमन लिपि (Hinglish) में लिखता है तो रोमन लिपि में उत्तर दें, अन्यथा देवनागरी में उत्तर दें।"
    ),
    "mr": (
        "मराठीत उत्तर द्या (Respond in fluent, natural Marathi). "
        "जर वापरकर्त्याने रोमन लिपीत (Maranglish) प्रश्न विचारला असेल, तर रोमन लिपीत उत्तर द्या, अन्यथा शुद्ध देवनागरी मराठीत उत्तर द्या."
    ),
    "en+hi": (
        "Communicate in natural Hinglish (English + Hindi mix) or standard Hindi as appropriate. "
        "Feel completely comfortable with mid-sentence code-switching (e.g. 'Maine VS Code open kar diya hai'). "
        "Keep technical computing terms in English while conversational framing is in Hindi."
    ),
    "en+mr": (
        "Communicate in natural Maranglish (English + Marathi mix) or standard Marathi as appropriate. "
        "Seamlessly handle mid-sentence code-switching (e.g. 'Mi tumcha VS Code project open kela aahe'). "
        "Preserve software and system terminology in English."
    ),
    "hi+mr": (
        "Communicate across Hindi and Marathi naturally. You understand both languages deeply "
        "and can respond or clarify in whichever language the user initiated."
    ),
    "en+hi+mr": (
        "You are fully trilingual across English, Hindi, and Marathi. "
        "You support all mid-sentence code-switching seamlessly across English, Hinglish, and Maranglish. "
        "Always match the user's primary conversational script and vocabulary naturally."
    ),
}


class LanguageRouter:
    """Routes and manages multilingual preferences and prompt synthesis."""

    CONFIG_DIR = os.path.expanduser("~/.config/tejas-os")
    CONFIG_PATH = os.path.join(CONFIG_DIR, "languages.json")

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self.CONFIG_PATH
        self._config = deepcopy(DEFAULT_LANGUAGES_CONFIG)
        self.detector = MultilingualDetector()
        self.load()

    def load(self) -> Dict[str, Any]:
        """Loads configuration from JSON file or writes defaults."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._config.update(data)
            except Exception:
                pass
        else:
            self.save()
        return deepcopy(self._config)

    def save(self) -> bool:
        """Atomically saves configuration to JSON file."""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with tempfile.NamedTemporaryFile("w", dir=os.path.dirname(self.config_path), delete=False, encoding="utf-8") as tf:
                json.dump(self._config, tf, indent=2, ensure_ascii=False)
                temp_name = tf.name
            os.replace(temp_name, self.config_path)
            return True
        except Exception:
            return False

    def get_config(self) -> Dict[str, Any]:
        return deepcopy(self._config)

    def update_config(self, updates: Dict[str, Any]) -> bool:
        for k, v in updates.items():
            if k in DEFAULT_LANGUAGES_CONFIG:
                self._config[k] = v
        return self.save()

    def resolve_effective_combination(self, user_text: str) -> Tuple[str, LanguageProfile]:
        """
        Determines the effective language combination for the turn.
        If config is set to 'auto', uses detected combination from text;
        otherwise uses user-configured preference.
        """
        profile = self.detector.analyze(user_text)
        configured_comb = self._config.get("preferred_combination", "auto")

        if configured_comb != "auto" and configured_comb in COMBINATION_PROMPTS:
            effective_comb = configured_comb
        else:
            effective_comb = profile.combination

        return effective_comb, profile

    def build_system_prompt_instruction(self, user_text: str) -> str:
        """
        Returns targeted language instruction to append to the base system prompt.
        """
        effective_comb, profile = self.resolve_effective_combination(user_text)
        instruction = COMBINATION_PROMPTS.get(effective_comb, COMBINATION_PROMPTS["en"])

        script_mode = self._config.get("script_mode", "mirror_input")
        if script_mode == "native_devanagari" and effective_comb in ("hi", "mr", "hi+mr"):
            instruction += " Answer strictly in Devanagari script."
        elif script_mode == "romanized":
            instruction += " Answer using Romanized phonetic script (Latin letters)."

        return f"\n\n[Multilingual Directive ({effective_comb.upper()})]:\n{instruction}"
