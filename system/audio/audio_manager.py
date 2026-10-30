#!/usr/bin/env python3
"""
PipeWire & WirePlumber Audio Manager.
Exposes sink control, volume adjustment, and stream management.
"""

from dataclasses import asdict, dataclass
import json
import re
import subprocess
import sys
from typing import Any, Dict, List


@dataclass
class AudioSink:
    id: int
    name: str
    is_default: bool
    volume: float
    is_muted: bool


class AudioManager:

    def get_status(self) -> Dict[str, Any]:
        """Queries master audio sink status via wpctl."""
        try:
            out = subprocess.check_output(
                ["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"],
                stderr=subprocess.DEVNULL,
                text=True,
            )
            is_muted = "[MUTED]" in out
            match = re.search(r"Volume:\s+([0-9\.]+)", out)
            vol = float(match.group(1)) if match else 0.5
            return {"volume": vol, "muted": is_muted}
        except Exception:
            return {"volume": 0.5, "muted": False}

    def set_volume(self, volume: float) -> bool:
        """Sets master output volume (0.0 to 1.5)."""
        vol = max(0.0, min(1.5, volume))
        try:
            subprocess.run(
                ["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", f"{vol:.2f}"],
                check=True,
            )
            return True
        except Exception:
            return False

    def toggle_mute(self) -> bool:
        """Toggles audio mute state."""
        try:
            subprocess.run(
                ["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "toggle"],
                check=True,
            )
            return True
        except Exception:
            return False


def main():
    am = AudioManager()
    if len(sys.argv) < 2:
        print(json.dumps(am.get_status(), indent=2))
        return

    cmd = sys.argv[1]
    if cmd == "status":
        print(json.dumps(am.get_status(), indent=2))
    elif cmd == "set":
        if len(sys.argv) > 2:
            vol = float(sys.argv[2])
            am.set_volume(vol)
            print(json.dumps(am.get_status(), indent=2))
    elif cmd == "mute":
        am.toggle_mute()
        print(json.dumps(am.get_status(), indent=2))


if __name__ == "__main__":
    main()
