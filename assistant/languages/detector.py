#!/usr/bin/env python3
"""
Multilingual Detector & Code-Switching Disambiguator.
Supports English, Hindi, and Marathi across all 7 language combinations.
Complies with AGENTS.md Rule 2.3:
Disambiguates Hindi vs Marathi in Devanagari script (cannot rely on script alone)
and classifies Romanized Hinglish vs Maranglish.
"""

from dataclasses import dataclass, field
import re
from typing import Any, Dict, List, Set, Tuple

# Unique Devanagari Marathi Character: Retroflex L (U+0933)
MARATHI_SPECIFIC_CHAR = "\u0933"  # ळ

# Marathi Specific Devanagari Lexicon & Grammar Particles
MARATHI_DEV_WORDS: Set[str] = {
    "आहे", "आहेत", "होतो", "होते", "होती", "करणार", "करतो", "करते", "करतात",
    "करा", "करावे", "मला", "तुला", "त्याला", "तिला", "आम्हाला", "माझं", "माझा",
    "माझी", "माझे", "तुझं", "तुझा", "तुझी", "तुझे", "काय", "कसे", "कसा",
    "कशी", "कुठे", "केव्हा", "कधी", "उघड", "उघडा", "दाखवा", "दाखव", "नाही",
    "पाहिजे", "नको", "सांगा", "सांग", "बघा", "बघ", "वेळ", "लवकर", "करायचे",
    "कसं", "आपण", "चालवा", "टाक", "झाला", "झाली", "झाले", "कशा", "कशासाठी",
    "मित्रा", "भावा", "करायचं", "नका"
}

# Hindi Specific Devanagari Lexicon & Grammar Particles
HINDI_DEV_WORDS: Set[str] = {
    "है", "हैं", "था", "थे", "थी", "करेगा", "करता", "करती", "करते", "करो",
    "कीजिए", "मुझे", "तुझे", "उसे", "हमें", "मेरा", "मेरी", "मेरे", "तेरा",
    "तेरी", "तेरे", "क्या", "कैसे", "कैसा", "कैसी", "कहाँ", "कब", "खोलो",
    "खोल", "दिखाओ", "दिखा", "नहीं", "चाहिए", "मत", "बताओ", "बता", "देखो",
    "देख", "समय", "वक्त", "जल्दी", "करना", "हाँ", "हम", "आप", "चलाओ",
    "डालो", "हुआ", "हुई", "हुए", "क्यो", "क्यों", "क्योकि", "क्योंकि", "दोस्त",
    "भाई", "कीजिये", "सकते", "सकता", "सकती"
}

# Maranglish (Romanized Marathi) Lexicon
MARANGLISH_WORDS: Set[str] = {
    "majha", "majhi", "majhe", "majh", "mala", "tula", "tyala", "tila",
    "ughad", "ughada", "daakhav", "dakhva", "dakhiv", "aahe", "aahet", "nahi",
    "pahije", "nako", "saang", "sanga", "kasa", "kase", "kashi", "kuthe",
    "kay", "kaay", "bagh", "bagha", "chalva", "kiti", "vel", "aata",
    "karuya", "karaycha", "karto", "karte", "jhala", "jhali", "bhava", "mitra"
}

# Hinglish (Romanized Hindi) Lexicon
HINGLISH_WORDS: Set[str] = {
    "mera", "meri", "mere", "mujhe", "tujhe", "usse", "humko", "kholo",
    "khol", "dikhao", "dikha", "hai", "hain", "nahi", "nahin", "chahiye",
    "mat", "batao", "bata", "kaisa", "kaise", "kaisi", "kahan", "kya",
    "dekho", "chalao", "kitna", "samay", "waqt", "aaj", "karein", "accha",
    "acha", "yaar", "theek", "bolo", "hoga", "karo", "karna", "bhai",
    "aur", "bhi", "toh", "gaana", "bajao", "pe"
}

# Common English Stopwords
ENGLISH_WORDS: Set[str] = {
    "the", "is", "at", "which", "on", "and", "a", "an", "in", "to", "for",
    "with", "it", "this", "that", "how", "what", "where", "why", "who", "can",
    "you", "please", "open", "close", "switch", "workspace", "terminal", "browser",
    "system", "settings", "volume", "sound", "screen", "wifi", "hotspot", "battery",
    "code", "file", "project", "help", "show", "launch", "start", "stop"
}


@dataclass
class LanguageProfile:
    primary_language: str              # "en", "hi", "mr"
    combination: str                   # 1 of the 7: "en", "hi", "mr", "en+hi", "en+mr", "hi+mr", "en+hi+mr"
    script: str                        # "devanagari", "latin", "mixed"
    is_code_switched: bool             # True if mid-sentence mixing detected
    languages_present: List[str]       # e.g. ["en", "mr"]
    confidence: float                  # 0.0 to 1.0
    details: Dict[str, Any] = field(default_factory=dict)


class MultilingualDetector:
    """Disambiguates Hindi, Marathi, and English in Devanagari and Latin scripts."""

    def detect_script(self, text: str) -> str:
        """Determines if text is in Devanagari, Latin, or mixed scripts."""
        has_devanagari = bool(re.search(r"[\u0900-\u097F]", text))
        has_latin = bool(re.search(r"[a-zA-Z]", text))

        if has_devanagari and has_latin:
            return "mixed"
        if has_devanagari:
            return "devanagari"
        if has_latin:
            return "latin"
        return "other"

    def disambiguate_devanagari(self, text: str) -> Tuple[int, int, bool]:
        """
        Disambiguates between Hindi and Marathi in Devanagari script.
        Returns: (marathi_score, hindi_score, has_marathi_specific_letter)
        """
        has_retroflex_l = MARATHI_SPECIFIC_CHAR in text
        marathi_score = 3 if has_retroflex_l else 0
        hindi_score = 0

        # Tokenize Devanagari words
        tokens = re.findall(r"[\u0900-\u097F]+", text)
        for t in tokens:
            if t in MARATHI_DEV_WORDS:
                marathi_score += 1
            if t in HINDI_DEV_WORDS:
                hindi_score += 1

        return marathi_score, hindi_score, has_retroflex_l

    def classify_romanized(self, text: str) -> Tuple[int, int, int]:
        """
        Classifies Latin words into Maranglish, Hinglish, and English scores.
        Returns: (maranglish_score, hinglish_score, english_score)
        """
        words = [w.lower() for w in re.findall(r"\b[a-zA-Z]+\b", text)]
        marathi_score = 0
        hindi_score = 0
        english_score = 0

        for w in words:
            if w in MARANGLISH_WORDS:
                marathi_score += 1
            if w in HINGLISH_WORDS:
                hindi_score += 1
            if w in ENGLISH_WORDS:
                english_score += 1

        return marathi_score, hindi_score, english_score

    def analyze(self, text: str) -> LanguageProfile:
        """
        Full contextual analysis of the input text.
        Resolves to one of the 7 supported language combinations.
        """
        clean_text = text.strip()
        if not clean_text:
            return LanguageProfile(
                primary_language="en",
                combination="en",
                script="latin",
                is_code_switched=False,
                languages_present=["en"],
                confidence=1.0
            )

        script_type = self.detect_script(clean_text)
        dev_mr_score, dev_hi_score, has_l = self.disambiguate_devanagari(clean_text)
        rom_mr_score, rom_hi_score, en_score = self.classify_romanized(clean_text)

        total_mr = dev_mr_score + rom_mr_score
        total_hi = dev_hi_score + rom_hi_score
        total_en = en_score

        # Identify languages present
        languages_present = []
        if total_en > 0 or (script_type == "latin" and total_mr == 0 and total_hi == 0):
            languages_present.append("en")
        if total_hi > 0:
            languages_present.append("hi")
        if total_mr > 0:
            languages_present.append("mr")

        # Fallback if no specific lexicon matched
        if not languages_present:
            if script_type == "devanagari":
                # Default to Hindi if general Devanagari without distinctive Marathi markers
                languages_present = ["hi"]
            else:
                languages_present = ["en"]

        # Resolve primary language
        scores = {"en": total_en, "hi": total_hi, "mr": total_mr}
        if script_type == "devanagari":
            scores["en"] = -1
            if dev_mr_score > dev_hi_score or has_l:
                primary = "mr"
            else:
                primary = "hi"
        else:
            primary = max(scores, key=lambda k: scores[k])
            # If scores tie at 0 in Latin script, default to English
            if scores[primary] == 0:
                primary = "en"

        # Determine which of the 7 language combinations this matches
        is_code_switched = len(languages_present) > 1

        langs_set = set(languages_present)
        if langs_set == {"en"}:
            combination = "en"
        elif langs_set == {"hi"}:
            combination = "hi"
        elif langs_set == {"mr"}:
            combination = "mr"
        elif langs_set == {"en", "hi"}:
            combination = "en+hi"
        elif langs_set == {"en", "mr"}:
            combination = "en+mr"
        elif langs_set == {"hi", "mr"}:
            combination = "hi+mr"
        elif langs_set == {"en", "hi", "mr"}:
            combination = "en+hi+mr"
        else:
            combination = primary

        return LanguageProfile(
            primary_language=primary,
            combination=combination,
            script=script_type,
            is_code_switched=is_code_switched,
            languages_present=sorted(languages_present),
            confidence=0.9 if (dev_mr_score or dev_hi_score or rom_mr_score or rom_hi_score) else 0.7,
            details={
                "marathi_score": total_mr,
                "hindi_score": total_hi,
                "english_score": total_en,
                "has_marathi_letter_l": has_l,
            }
        )
