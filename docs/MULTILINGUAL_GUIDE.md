# Multilingual Engine Guide (English, Hindi, Marathi)

## 1. Trilingual Combinations
In accordance with **AGENTS.md Rule 2.3**, Tejas OS and June AI provide first-class support for all **7 language combinations**:

| # | Combination | Example Input |
|---|---|---|
| 1 | English | *"Open Kitty terminal and check git branch"* |
| 2 | Hindi | *"सिस्टम का वॉल्यूम 75 प्रतिशत करो"* |
| 3 | Marathi | *"माझा पायथन प्रोजेक्ट उघडा"* |
| 4 | English + Hindi | *"June, terminal open karo aur git status check karo"* |
| 5 | English + Marathi | *"June, majha VS Code project ughad"* |
| 6 | Hindi + Marathi | *"हॉटस्पॉट चालू करा aur battery check karo"* |
| 7 | English + Hindi + Marathi | *"June, please majha project open karo aur terminal suru kara"* |

---

## 2. Devanagari Script Disambiguation

Because **Hindi** and **Marathi** share the Devanagari script (`U+0900` to `U+097F`), simple Unicode character-range checks cannot distinguish them.

The Tejas OS Multilingual Detector (`assistant/languages/detector.py`) implements a two-tier disambiguation engine:

1. **Character-Level Phonetic Markers:**
   - Detects the Marathi retroflex consonant **ळ** (`U+0933`, e.g., in `सकाळ`, `वेळ`). The presence of `ळ` decisively flags Marathi.
2. **Lexical & Morphological Token Matching:**
   - **Marathi Distinctive Particles:** `आहे`, `नाही`, `पाहिजे`, `कसे`, `माझा`, `माझी`, `करा`, `उघडा`, `जा`.
   - **Hindi Distinctive Particles:** `है`, `नहीं`, `चाहिए`, `कैसे`, `मेरा`, `मेरी`, `करो`, `खोलो`, `जाओ`.
3. **Romanized Phonetic Normalization (`assistant/languages/romanized.py`):**
   - Transcribes Hinglish and Maranglish terms into canonical English commands before AST action planning.
   - Example: `"majha ... ughad"` -> `"open ..."`

---

## 3. Multilingual Speech-to-Text & Text-to-Speech

- **Speech-to-Text (`assistant/speech_to_text/`):**
  - Configured with accent adaptation for Indian English, Hindi phonetics, and Marathi retroflexes.
  - Streaming push-to-talk audio pipeline.
- **Text-to-Speech (`assistant/text_to_speech/`):**
  - Natural pronunciation across all three languages with automatic voice synthesis fallback.
