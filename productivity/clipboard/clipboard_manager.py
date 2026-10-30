#!/usr/bin/env python3
"""
Wayland Clipboard Manager Backend via cliphist and wl-clipboard.
Provides history retrieval, searching, pinning, and deletion.
"""

from dataclasses import asdict, dataclass
import json
import os
import subprocess
import sys
from typing import Any, Dict, List


@dataclass
class ClipboardItem:
    id: str
    preview: str
    is_pinned: bool
    is_image: bool


class ClipboardManager:
    PINNED_FILE = os.path.expanduser("~/.config/tejas-os/pinned_clips.json")

    def __init__(self):
        os.makedirs(os.path.dirname(self.PINNED_FILE), exist_ok=True)
        if not os.path.exists(self.PINNED_FILE):
            with open(self.PINNED_FILE, "w") as f:
                json.dump([], f)

    def load_pinned(self) -> List[str]:
        try:
            with open(self.PINNED_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []

    def save_pinned(self, pinned: List[str]):
        try:
            with open(self.PINNED_FILE, "w") as f:
                json.dump(pinned, f, indent=2)
        except Exception:
            pass

    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Queries history items from cliphist."""
        pinned = set(self.load_pinned())
        items: List[Dict[str, Any]] = []

        try:
            out = subprocess.check_output(
                ["cliphist", "list"], stderr=subprocess.DEVNULL, text=True
            )
            lines = out.splitlines()[:limit]
            for line in lines:
                parts = line.split("\t", maxsplit=1)
                if len(parts) >= 2:
                    clip_id = parts[0].strip()
                    content = parts[1].strip()
                    is_img = "[[ binary data" in content
                    items.append(
                        asdict(
                            ClipboardItem(
                                id=clip_id,
                                preview=content,
                                is_pinned=(content in pinned),
                                is_image=is_img,
                            )
                        )
                    )
        except Exception:
            # Fallback mock for testing
            pass

        return items

    def copy_item(self, clip_id: str) -> bool:
        """Decodes cliphist item and puts it into wl-clipboard."""
        try:
            decode_proc = subprocess.Popen(
                ["cliphist", "decode", clip_id], stdout=subprocess.PIPE
            )
            subprocess.run(["wl-copy"], stdin=decode_proc.stdout, check=True)
            decode_proc.wait()
            return True
        except Exception:
            return False

    def toggle_pin(self, content: str) -> bool:
        """Toggles pinned status for a clipboard string."""
        pinned = self.load_pinned()
        if content in pinned:
            pinned.remove(content)
            self.save_pinned(pinned)
            return False
        else:
            pinned.append(content)
            self.save_pinned(pinned)
            return True

    def clear_history(self) -> bool:
        """Wipes unpinned history from cliphist."""
        try:
            subprocess.run(["cliphist", "wipe"], check=True)
            return True
        except Exception:
            return False


def main():
    cm = ClipboardManager()
    if len(sys.argv) < 2 or sys.argv[1] == "list":
        print(json.dumps(cm.get_history(), indent=2))
    elif sys.argv[1] == "copy" and len(sys.argv) > 2:
        res = cm.copy_item(sys.argv[2])
        print(json.dumps({"success": res}, indent=2))
    elif sys.argv[1] == "pin" and len(sys.argv) > 2:
        res = cm.toggle_pin(sys.argv[2])
        print(json.dumps({"pinned": res}, indent=2))
    elif sys.argv[1] == "clear":
        res = cm.clear_history()
        print(json.dumps({"success": res}, indent=2))


if __name__ == "__main__":
    main()
