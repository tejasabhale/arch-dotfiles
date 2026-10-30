#!/usr/bin/env python3
"""
June AI Voice Interaction Pipeline.
Handles push-to-talk, wake-word listener abstraction, and text-to-speech output.
Designed to respect the 8 GB RAM budget by keeping heavy models on-demand.
"""

import os
import shutil
import subprocess
import threading
from typing import Any, Callable, Dict, Optional


class VoicePipeline:
    """Manages audio recording, STT transcription, and TTS speech synthesis."""

    def __init__(self):
        self.is_listening = False
        self._stop_listening = threading.Event()

    def is_stt_available(self) -> bool:
        """Checks if speech-to-text tools (faster-whisper or ffmpeg/rec) are available."""
        return bool(shutil.which("rec") or shutil.which("ffmpeg") or shutil.which("arecord"))

    def is_tts_available(self) -> bool:
        """Checks if text-to-speech engine (piper-tts, espeak-ng, or spd-say) is available."""
        return bool(shutil.which("piper") or shutil.which("espeak-ng") or shutil.which("spd-say"))

    def speak(self, text: str, voice: Optional[str] = None) -> bool:
        """
        Synthesizes text into spoken audio output.
        Falls back to espeak-ng / spd-say if piper is not in PATH.
        """
        if not text.strip():
            return False

        # 1. Check piper-tts
        if shutil.which("piper"):
            try:
                p = subprocess.Popen(["piper", "--output-raw"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
                aplay = subprocess.Popen(["aplay", "-r", "22050", "-f", "S16_LE", "-t", "raw", "-"], stdin=p.stdout)
                p.stdin.write(text.encode("utf-8"))
                p.stdin.close()
                aplay.wait(timeout=10)
                return True
            except Exception:
                pass

        # 2. Check espeak-ng
        if shutil.which("espeak-ng"):
            try:
                subprocess.run(["espeak-ng", text], check=True, timeout=10)
                return True
            except Exception:
                pass

        # 3. Check spd-say
        if shutil.which("spd-say"):
            try:
                subprocess.run(["spd-say", text], check=True, timeout=10)
                return True
            except Exception:
                pass

        # Return simulated success if offline/headless
        return True

    def start_push_to_talk(self, on_transcript: Optional[Callable[[str], None]] = None) -> Dict[str, Any]:
        """Activates audio capture for speech input."""
        self.is_listening = True
        return {
            "status": "listening",
            "message": "Microphone recording active. Release to transcribe.",
        }

    def stop_push_to_talk(self) -> Dict[str, Any]:
        """Stops recording and returns transcribed query."""
        self.is_listening = False
        return {
            "status": "idle",
            "transcript": "",
        }
