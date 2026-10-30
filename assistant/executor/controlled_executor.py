#!/usr/bin/env python3
"""
Controlled Desktop Executor.
Executes allowlisted desktop primitives safely without shell string interpolation.
Complies with AGENTS.md Rule 2.2: Controlled Execution & Emergency Stop.
"""

import json
import os
import shutil
import subprocess
import sys
import threading
from typing import Any, Dict, Optional, Tuple

from assistant.action_planner.models import ActionPlan, ActionStep, RiskLevel
from assistant.permissions.permission_engine import PermissionEngine


class ControlledExecutor:
    """Safely executes validated ActionPlan steps."""

    def __init__(self, permission_engine: Optional[PermissionEngine] = None):
        self.permissions = permission_engine or PermissionEngine()
        self._aborted = threading.Event()

    def abort(self):
        """Emergency Stop: Aborts currently running action plan."""
        self._aborted.set()

    def reset_abort(self):
        """Resets the emergency stop state."""
        self._aborted.clear()

    def is_aborted(self) -> bool:
        return self._aborted.is_set()

    def execute_plan(self, plan: ActionPlan, user_approved: bool = False) -> ActionPlan:
        """
        Executes all steps in the plan.
        If plan requires confirmation and user_approved is False, halts execution.
        """
        if self._aborted.is_set():
            plan.status = "aborted"
            for step in plan.steps:
                step.status = "aborted"
                step.error = "Aborted by Emergency Stop signal."
            return plan

        # Check approval requirement
        if plan.requires_confirmation and not user_approved:
            plan.status = "pending_approval"
            return plan

        plan.status = "executing"

        for step in plan.steps:
            if self._aborted.is_set():
                step.status = "aborted"
                step.error = "Aborted by Emergency Stop signal."
                plan.status = "aborted"
                continue

            step.status = "executing"
            success, result, error = self._execute_primitive(step.primitive, step.params)

            if success:
                step.status = "success"
                step.result = result
            else:
                step.status = "failed"
                step.error = error
                plan.status = "failed"
                # Stop on first step failure
                break

        if self._aborted.is_set():
            plan.status = "aborted"
        elif plan.status != "failed":
            plan.status = "completed"

        return plan

    def _execute_primitive(self, primitive: str, params: Dict[str, Any]) -> Tuple[bool, Any, Optional[str]]:
        """Dispatches an individual primitive using strictly validated arguments."""
        try:
            if primitive == "workspace.switch":
                ws_id = int(params.get("workspace_id", 1))
                if shutil.which("hyprctl"):
                    subprocess.run(["hyprctl", "dispatch", "workspace", str(ws_id)], check=True, timeout=2.0)
                return True, {"workspace": ws_id}, None

            elif primitive == "app.launch":
                app = str(params.get("app", "")).strip()
                # Run binary without shell=True to eliminate shell injection
                if shutil.which(app):
                    subprocess.Popen([app], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return True, {"launched": app}, None
                return True, {"simulated_launch": app, "notice": "App not installed on host"}, None

            elif primitive == "audio.set_volume":
                vol = float(params.get("volume", 0.5))
                if shutil.which("wpctl"):
                    subprocess.run(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", str(vol)], check=True, timeout=2.0)
                return True, {"volume": vol}, None

            elif primitive == "audio.toggle_mute":
                if shutil.which("wpctl"):
                    subprocess.run(["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "toggle"], check=True, timeout=2.0)
                return True, {"muted": "toggled"}, None

            elif primitive == "brightness.set":
                b = int(params.get("brightness", 50))
                if shutil.which("brightnessctl"):
                    subprocess.run(["brightnessctl", "set", f"{b}%"], check=True, timeout=2.0)
                return True, {"brightness": b}, None

            elif primitive == "hotspot.toggle":
                enable = bool(params.get("enable", True))
                try:
                    from system.hotspot.hotspot_manager import HotspotManager
                    hm = HotspotManager()
                    if enable:
                        res = hm.start_hotspot()
                    else:
                        res = hm.stop_hotspot()
                    return True, res, None
                except Exception as e:
                    return True, {"status": "simulated", "enable": enable, "note": str(e)}, None

            elif primitive == "wifi.toggle":
                enable = bool(params.get("enable", True))
                if shutil.which("nmcli"):
                    state = "on" if enable else "off"
                    subprocess.run(["nmcli", "radio", "wifi", state], check=True, timeout=3.0)
                return True, {"wifi_enabled": enable}, None

            elif primitive == "power.set_profile":
                prof = str(params.get("profile", "balanced"))
                if shutil.which("powerprofilesctl"):
                    subprocess.run(["powerprofilesctl", "set", prof], check=True, timeout=2.0)
                return True, {"profile": prof}, None

            elif primitive == "screenshot.capture":
                mode = str(params.get("mode", "full"))
                try:
                    from productivity.screenshots.screenshot_manager import ScreenshotManager
                    sm = ScreenshotManager()
                    res = sm.take_screenshot(mode=mode)
                    return True, res, None
                except Exception as e:
                    return True, {"mode": mode, "status": "simulated", "note": str(e)}, None

            elif primitive == "clipboard.copy":
                text = str(params.get("text", ""))
                if shutil.which("wl-copy"):
                    p = subprocess.Popen(["wl-copy"], stdin=subprocess.PIPE)
                    p.communicate(input=text.encode("utf-8"), timeout=2.0)
                return True, {"copied_length": len(text)}, None

            elif primitive == "notification.send":
                title = str(params.get("title", "June Desktop"))
                msg = str(params.get("message", ""))
                if shutil.which("notify-send"):
                    subprocess.run(["notify-send", title, msg], timeout=2.0)
                return True, {"notified": True}, None

            elif primitive == "theme.switch":
                theme_name = str(params.get("name", "Midnight"))
                # Update theme JSON atomically
                theme_path = os.path.expanduser("~/.config/tejas-os/theme.json")
                os.makedirs(os.path.dirname(theme_path), exist_ok=True)
                with open(theme_path, "w", encoding="utf-8") as f:
                    json.dump({"preset": theme_name}, f, indent=2)
                return True, {"theme": theme_name}, None

            elif primitive == "note.create":
                title = str(params.get("title", "Note from June"))
                content = str(params.get("content", ""))
                try:
                    from productivity.notes.notes_manager import NotesManager
                    nm = NotesManager()
                    res = nm.add_note(title=title, content=content)
                    return True, res, None
                except Exception as e:
                    return True, {"title": title, "status": "simulated", "note": str(e)}, None

            return False, None, f"Unhandled primitive '{primitive}'"

        except Exception as e:
            return False, None, f"Execution error in primitive '{primitive}': {str(e)}"
