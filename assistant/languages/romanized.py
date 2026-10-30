#!/usr/bin/env python3
"""
Romanized Script Parser & Transliteration Normalizer.
Translates Hinglish and Maranglish expressions and action commands into normalized intents.
Complies with AGENTS.md Rule 2.3: Mid-sentence code-switching (e.g. "June, majha VS Code project ughad").
"""

import re
from typing import Dict, Tuple

# Action keyword mappings for Marathi (Devanagari & Romanized)
MARATHI_ACTION_MAP: Dict[str, str] = {
    # Hotspot
    r"(?i)(?:hotspot|हॉटस्पॉट)\s*(?:chalu|suru|on|start|चालू|सुरू|शुरू)(?:\s*(?:kar|kara|karo|kar do|करा|करो))?": "start hotspot",
    r"(?i)(?:hotspot|हॉटस्पॉट)\s*(?:band|stop|off|बंद|थांबवा)(?:\s*(?:kar|kara|karo|kar do|करा|करो))?": "stop hotspot",
    # Workspace
    r"(?i)(?:workspace|वर्कस्पेस)\s*(\d+)(?:\s*(?:var jaa|var chal|la jaa|var|वर जा|ला जा|वर|par jao|me jao|पर जाओ))?": "switch to workspace \\1",
    r"(?i)(?:जा|chal|जाओ|chalo)\s+(?:workspace|वर्कस्पेस)\s*(\d+)": "switch to workspace \\1",
    # Volume
    r"(?i)(?:awaaj|aawaz|sound|आवाज)\s*(?:kami kar|ghatwa|कमी करा|कमी|kam karo|कम करो|धीमा)": "volume to 30%",
    r"(?i)(?:awaaj|aawaz|sound|आवाज)\s*(?:jaasta kar|vadhva|वाढवा|मोठा|badhao|tez karo|बढ़ाओ|तेज़)": "volume to 80%",
    # Screenshot
    r"(?i)(?:screenshot|स्क्रीनशॉट)\s*(?:ghe|kadha|काढा|घ्या|lo|khincho|लो|खींचो)": "take screenshot",
    # Open / Launch
    r"(?i)^(?:(?:majha|majhi|majhe|माझं|माझा|माझी|माझे)\s+)?(.+?)\s*(?:ughad|ughada|suru kar|chalu kar|उघड|उघडा|चालू करा|सुरू करा)$": "open \\1",
    r"(?i)^(?:ughad|ughada|suru kar|chalu kar|उघड|उघडा|चालू करा|सुरू करा)\s+(?:the\s+)?(.+)$": "open \\1",
}

# Action keyword mappings for Hindi (Devanagari & Romanized)
HINDI_ACTION_MAP: Dict[str, str] = {
    # Hotspot
    r"(?i)(?:hotspot|हॉटस्पॉट)\s*(?:chalu|on|start|चालू|शुरू)(?:\s*(?:karo|kar do|करो|kar|करा))?": "start hotspot",
    r"(?i)(?:hotspot|हॉटस्पॉट)\s*(?:band|off|stop|बंद)(?:\s*(?:karo|kar do|करो|kar|करा))?": "stop hotspot",
    # Workspace
    r"(?i)(?:workspace|वर्कस्पेस)\s*(\d+)(?:\s*(?:par jao|me jao|par|पर जाओ|में जाओ|पर))?": "switch to workspace \\1",
    r"(?i)(?:जाओ|chalo)\s+(?:workspace|वर्कस्पेस)\s*(\d+)": "switch to workspace \\1",
    # Volume
    r"(?i)(?:aawaz|sound|आवाज)\s*(?:kam karo|ghatao|कम करो|धीमा)": "volume to 30%",
    r"(?i)(?:aawaz|sound|आवाज)\s*(?:badhao|tez karo|बढ़ाओ|तेज़)": "volume to 80%",
    # Screenshot
    r"(?i)(?:screenshot|स्क्रीनशॉट)\s*(?:lo|khincho|लो|खींचो)": "take screenshot",
    # Open / Launch
    r"(?i)^(?:(?:mera|meri|mere|मेरा|मेरी|मेरे)\s+)?(.+?)\s*(?:kholo|khol|khol do|chalao|chalu karo|खोलो|खोल दो|चालू करो|शुरू करो)$": "open \\1",
    r"(?i)^(?:kholo|khol|chalao|chalu karo|खोलो|चालू करो)\s+(?:the\s+)?(.+)$": "open \\1",
}


class RomanizedParser:
    """Parses and normalizes Romanized and native Hindi/Marathi commands into action intents."""

    def normalize_command(self, text: str) -> Tuple[str, bool]:
        """
        Translates Hindi or Marathi phrasing into canonical desktop action commands.
        Returns: (normalized_text, was_translated: bool)
        """
        cleaned = text.strip()

        # Remove prefix address like "June, ", "Hey June, ", "मित्रा ", "भाई "
        cleaned = re.sub(
            r"^(?:june|hey june|arre june|mitra|bhava|bhai|bhaiya|dost)[,\s]+",
            "",
            cleaned,
            flags=re.IGNORECASE,
        ).strip()

        # 1. Check Marathi patterns
        for pattern, replacement in MARATHI_ACTION_MAP.items():
            if re.search(pattern, cleaned, re.IGNORECASE):
                normalized = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE).strip()
                # Clean up trailing polite particles like "bara", "na", "shakya aahe ka"
                normalized = re.sub(r"\s+(?:bara|na|re|shakya aahe ka|kar re|bghu)$", "", normalized, flags=re.IGNORECASE)
                return normalized, True

        # 2. Check Hindi patterns
        for pattern, replacement in HINDI_ACTION_MAP.items():
            if re.search(pattern, cleaned, re.IGNORECASE):
                normalized = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE).strip()
                # Clean up trailing polite particles like "yaar", "bhai", "please"
                normalized = re.sub(r"\s+(?:yaar|bhai|na|kardo|kijiye)$", "", normalized, flags=re.IGNORECASE)
                return normalized, True

        return text, False
