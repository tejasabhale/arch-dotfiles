"""
Automated Unit Tests for June AI Multilingual Engine (Phase 8).
Verifies Language Detection across all 7 combinations, Devanagari Disambiguation,
Romanized Hinglish/Maranglish Parsing, LanguageRouter, and Daemon Integration.
Complies with AGENTS.md Rule 2.3.
"""

import json
import os
import shutil
import tempfile
import unittest

from assistant.core.daemon import JuneDaemon
from assistant.languages.detector import MultilingualDetector
from assistant.languages.romanized import RomanizedParser
from assistant.languages.router import COMBINATION_PROMPTS, LanguageRouter
from assistant.speech_to_text.stt_service import MultilingualSTT
from assistant.text_to_speech.tts_service import MultilingualTTS


class TestMultilingualEngine(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="june_lang_test_")
        self.lang_config = os.path.join(self.test_dir, "languages.json")
        self.conv_db = os.path.join(self.test_dir, "test_conv.db")
        self.assistant_config = os.path.join(self.test_dir, "assistant.json")

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    # -------------------------------------------------------------------------
    # 1. Contextual Language Detection & Disambiguation (Rule 2.3)
    # -------------------------------------------------------------------------
    def test_english_detection(self):
        detector = MultilingualDetector()
        res = detector.analyze("What is the current system RAM usage and CPU frequency?")
        self.assertEqual(res.primary_language, "en")
        self.assertEqual(res.combination, "en")
        self.assertEqual(res.script, "latin")
        self.assertFalse(res.is_code_switched)

    def test_hindi_devanagari_detection(self):
        detector = MultilingualDetector()
        res = detector.analyze("मुझे सिस्टम सेटिंग्स दिखाओ और बताओ क्या चल रहा है")
        self.assertEqual(res.primary_language, "hi")
        self.assertEqual(res.combination, "hi")
        self.assertEqual(res.script, "devanagari")
        self.assertFalse(res.is_code_switched)

    def test_marathi_devanagari_disambiguation(self):
        # Both Hindi and Marathi use Devanagari; tests proper vocabulary/grammar separation
        detector = MultilingualDetector()
        res = detector.analyze("मला सिस्टीम सेटिंग्स दाखवा आणि सांगा काय चालू आहे")
        self.assertEqual(res.primary_language, "mr")
        self.assertEqual(res.combination, "mr")
        self.assertEqual(res.script, "devanagari")
        self.assertFalse(res.is_code_switched)

    def test_marathi_specific_letter_l(self):
        # The retroflex lateral approximant ळ is unique to Marathi in Devanagari
        detector = MultilingualDetector()
        res = detector.analyze("वेळ किती झाली आहे?")
        self.assertEqual(res.primary_language, "mr")
        self.assertTrue(res.details.get("has_marathi_letter_l"))

    def test_romanized_hinglish(self):
        detector = MultilingualDetector()
        res = detector.analyze("Mera VS Code project kholo aur terminal dikhao")
        self.assertEqual(res.combination, "en+hi")
        self.assertEqual(res.script, "latin")
        self.assertTrue(res.is_code_switched)
        self.assertIn("en", res.languages_present)
        self.assertIn("hi", res.languages_present)

    def test_romanized_maranglish(self):
        detector = MultilingualDetector()
        res = detector.analyze("June, majha VS Code project ughad")
        self.assertEqual(res.combination, "en+mr")
        self.assertEqual(res.script, "latin")
        self.assertTrue(res.is_code_switched)
        self.assertIn("en", res.languages_present)
        self.assertIn("mr", res.languages_present)

    def test_trilingual_combination(self):
        detector = MultilingualDetector()
        res = detector.analyze("June, switch to workspace 2 and mala majha code dakhwa, aur gaana bajao")
        self.assertEqual(res.combination, "en+hi+mr")
        self.assertTrue(res.is_code_switched)
        self.assertEqual(set(res.languages_present), {"en", "hi", "mr"})

    def test_all_seven_combinations_covered(self):
        expected_combinations = {"en", "hi", "mr", "en+hi", "en+mr", "hi+mr", "en+hi+mr"}
        self.assertEqual(set(COMBINATION_PROMPTS.keys()), expected_combinations)

    # -------------------------------------------------------------------------
    # 2. Romanized Parser & Command Normalization
    # -------------------------------------------------------------------------
    def test_marathi_command_normalization(self):
        parser = RomanizedParser()

        # Maranglish: Open App
        cmd1, tr1 = parser.normalize_command("June, majha VS Code project ughad")
        self.assertTrue(tr1)
        self.assertIn("open", cmd1.lower())

        # Native Marathi: Hotspot
        cmd2, tr2 = parser.normalize_command("हॉटस्पॉट चालू करा")
        self.assertTrue(tr2)
        self.assertEqual(cmd2.lower(), "start hotspot")

        # Native Marathi: Workspace
        cmd3, tr3 = parser.normalize_command("वर्कस्पेस 3 वर जा")
        self.assertTrue(tr3)
        self.assertEqual(cmd3.lower(), "switch to workspace 3")

    def test_hindi_command_normalization(self):
        parser = RomanizedParser()

        # Hinglish: Open App
        cmd1, tr1 = parser.normalize_command("Mera VS Code project kholo")
        self.assertTrue(tr1)
        self.assertIn("open", cmd1.lower())

        # Native Hindi: Hotspot
        cmd2, tr2 = parser.normalize_command("हॉटस्पॉट बंद करो")
        self.assertTrue(tr2)
        self.assertEqual(cmd2.lower(), "stop hotspot")

    # -------------------------------------------------------------------------
    # 3. Language Router & Prompt Construction
    # -------------------------------------------------------------------------
    def test_language_router_config_and_prompts(self):
        router = LanguageRouter(config_path=self.lang_config)
        cfg = router.get_config()
        self.assertEqual(cfg["preferred_combination"], "auto")

        # Test prompt construction for detected Hinglish
        prompt_directive = router.build_system_prompt_instruction("Mera terminal kholo")
        self.assertIn("Hinglish", prompt_directive)

        # Update preference to Marathi
        self.assertTrue(router.update_config({"preferred_combination": "mr", "script_mode": "native_devanagari"}))
        comb, _ = router.resolve_effective_combination("any text")
        self.assertEqual(comb, "mr")

        prompt_mr = router.build_system_prompt_instruction("hello")
        self.assertIn("मराठीत उत्तर द्या", prompt_mr)
        self.assertIn("Devanagari script", prompt_mr)

    # -------------------------------------------------------------------------
    # 4. STT & TTS Adapters
    # -------------------------------------------------------------------------
    def test_stt_and_tts_services(self):
        stt = MultilingualSTT()
        # Simulated transcription with created dummy file
        dummy_wav = os.path.join(self.test_dir, "sample.wav")
        with open(dummy_wav, "wb") as f:
            f.write(b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00")
        res = stt.transcribe(dummy_wav, language="mr")
        self.assertTrue(res["success"])

        tts = MultilingualTTS()
        # Test language detection for voice synthesis
        lang_hi = tts.detect_best_language("नमस्ते, आप कैसे हैं?")
        self.assertEqual(lang_hi, "hi")

        lang_mr = tts.detect_best_language("नमस्कार, तुम्ही कसे आहात?")
        self.assertEqual(lang_mr, "mr")

        # Speak method executes cleanly
        self.assertTrue(tts.speak("Hello June", language="en"))

    # -------------------------------------------------------------------------
    # 5. Daemon Multilingual Integration
    # -------------------------------------------------------------------------
    def test_daemon_multilingual_dispatch(self):
        daemon = JuneDaemon(
            config_path=self.assistant_config,
            db_path=self.conv_db,
            lang_config_path=self.lang_config,
            tcp_port=42497,
        )

        # RPC: detect_language
        det_res = daemon.dispatch("detect_language", {"text": "June, majha VS Code project ughad"})
        self.assertEqual(det_res["combination"], "en+mr")
        self.assertTrue(det_res["is_code_switched"])

        # RPC: get_language_config
        cfg_res = daemon.dispatch("get_language_config", {})
        self.assertIn("preferred_combination", cfg_res)

        # RPC: chat response metadata includes language tags
        chat_res = daemon.dispatch("chat", {"message": "मला सिस्टीम सेटिंग्स दाखवा"})
        self.assertIn("language", chat_res)
        self.assertIn("combination", chat_res)
        self.assertEqual(chat_res["language"], "mr")


if __name__ == "__main__":
    unittest.main()
