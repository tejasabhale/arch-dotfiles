#!/usr/bin/env python3
"""
Screenshot & Screen Recording Utility Backend via grim, slurp, and wf-recorder.
"""

from datetime import datetime
import json
import os
import subprocess
import sys
from typing import Any, Dict


class ScreenshotManager:
    SAVE_DIR = os.path.expanduser("~/Pictures/Screenshots")

    def __init__(self):
        os.makedirs(self.SAVE_DIR, exist_ok=True)

    def _get_timestamp_filename(self, ext: str = "png") -> str:
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return os.path.join(self.SAVE_DIR, f"screenshot_{ts}.{ext}")

    def capture_fullscreen(self) -> Dict[str, Any]:
        """Captures complete active display, copies to clipboard and saves to file."""
        filepath = self._get_timestamp_filename()
        cmd = f"grim '{filepath}' && wl-copy < '{filepath}'"
        try:
            subprocess.run(["sh", "-c", cmd], check=True)
            return {
                "success": True,
                "path": filepath,
                "message": f"Fullscreen saved to {filepath}",
            }
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": str(e)}

    def capture_region(self) -> Dict[str, Any]:
        """Interactive interactive selection capture via slurp."""
        filepath = self._get_timestamp_filename()
        cmd = f"grim -g \"$(slurp)\" '{filepath}' && wl-copy < '{filepath}'"
        try:
            subprocess.run(["sh", "-c", cmd], check=True)
            return {
                "success": True,
                "path": filepath,
                "message": f"Region saved to {filepath}",
            }
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": str(e)}

    def capture_active_window(self) -> Dict[str, Any]:
        """Captures geometry of currently focused Hyprland window."""
        filepath = self._get_timestamp_filename()
        # Query active window coordinates via hyprctl
        cmd = (
            "hyprctl activewindow -j | jq -r '\"\\(.at[0]),\\(.at[1]) \\(.size[0])x\\(.size[1])\"' | "
            f"xargs -I {{}} grim -g {{}} '{filepath}' && wl-copy < '{filepath}'"
        )
        try:
            subprocess.run(["sh", "-c", cmd], check=True)
            return {
                "success": True,
                "path": filepath,
                "message": f"Window saved to {filepath}",
            }
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": str(e)}

    def start_recording(self) -> Dict[str, Any]:
        """Starts screen recording via wf-recorder."""
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filepath = os.path.join(self.SAVE_DIR, f"recording_{ts}.mp4")
        cmd = ["wf-recorder", "-f", filepath, "-a"]
        try:
            subprocess.Popen(
                cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            return {
                "success": True,
                "recording": True,
                "path": filepath,
                "message": "Screen recording started.",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def stop_recording(self) -> Dict[str, Any]:
        """Stops active screen recording."""
        try:
            subprocess.run(["killall", "-SIGINT", "wf-recorder"], check=True)
            return {"success": True, "recording": False}
        except Exception as e:
            return {"success": False, "error": str(e)}


def main():
    sm = ScreenshotManager()
    if len(sys.argv) < 2:
        print("Usage: screenshot_manager.py [screen|region|window|record-start|record-stop]")
        sys.exit(1)

    action = sys.argv[1]
    if action == "screen":
        print(json.dumps(sm.capture_fullscreen(), indent=2))
    elif action == "region":
        print(json.dumps(sm.capture_region(), indent=2))
    elif action == "window":
        print(json.dumps(sm.capture_active_window(), indent=2))
    elif action == "record-start":
        print(json.dumps(sm.start_recording(), indent=2))
    elif action == "record-stop":
        print(json.dumps(sm.stop_recording(), indent=2))
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)


if __name__ == "__main__":
    main()
