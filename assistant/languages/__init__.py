"""Multilingual Engine Package for English, Hindi, and Marathi."""
from assistant.languages.detector import LanguageProfile, MultilingualDetector
from assistant.languages.romanized import RomanizedParser
from assistant.languages.router import LanguageRouter

__all__ = ["LanguageProfile", "MultilingualDetector", "RomanizedParser", "LanguageRouter"]
