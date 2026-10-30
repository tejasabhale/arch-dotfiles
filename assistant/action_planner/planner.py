#!/usr/bin/env python3
"""
June AI Action Planning Engine.
Translates high-level natural language user goals and tool-calling intents
into discrete, validated ActionPlan AST structures.
"""

import json
import re
from typing import Any, Dict, List, Optional, Tuple

from assistant.action_planner.models import ActionPlan, ActionStep, RiskLevel
from assistant.languages.romanized import RomanizedParser
from assistant.permissions.permission_engine import PermissionEngine


class ActionPlanner:
    """Parses intent and constructs validated multi-step ActionPlans."""

    def __init__(self, permission_engine: Optional[PermissionEngine] = None):
        self.permissions = permission_engine or PermissionEngine()
        self.romanized = RomanizedParser()

    def parse_natural_intent(self, text: str) -> ActionPlan:
        """
        Extracts discrete allowlisted steps from natural language requests.
        Supports single-action and chained multi-action phrases across EN, HI, and MR.
        """
        # Multilingual normalization: Convert Hinglish/Maranglish and Devanagari commands
        normalized, was_translated = self.romanized.normalize_command(text)
        text_lower = (normalized if was_translated else text).lower().strip()

        plan = ActionPlan(goal=text)
        steps: List[ActionStep] = []

        # 1. Workspace Switch
        ws_match = re.search(r"\b(?:workspace|ws)\s+(\d{1,2})\b", text_lower) or re.search(r"\bswitch to\s+(\d{1,2})\b", text_lower)
        if ws_match:
            ws_id = int(ws_match.group(1))
            steps.append(
                ActionStep(
                    primitive="workspace.switch",
                    params={"workspace_id": ws_id},
                    description=f"Switch desktop view to Workspace {ws_id}",
                )
            )

        # 2. Application Launch
        app_keywords = {
            "kitty": ("kitty", "Terminal (Kitty)"),
            "terminal": ("kitty", "Terminal (Kitty)"),
            "dolphin": ("dolphin", "File Manager (Dolphin)"),
            "files": ("dolphin", "File Manager (Dolphin)"),
            "firefox": ("firefox", "Web Browser (Firefox)"),
            "browser": ("firefox", "Web Browser (Firefox)"),
            "chromium": ("chromium", "Chromium Browser"),
            "chrome": ("google-chrome", "Google Chrome"),
            "code": ("code", "VS Code"),
            "vs code": ("code", "VS Code"),
            "vscode": ("code", "VS Code"),
            "obsidian": ("obsidian", "Obsidian Notes"),
            "spotify": ("spotify", "Spotify"),
            "calculator": ("gnome-calculator", "Calculator"),
        }
        for kw, (app_cmd, app_desc) in app_keywords.items():
            if re.search(rf"\b(?:open|launch|start)\s+(?:the\s+)?{kw}\b", text_lower) or text_lower == f"open {kw}":
                steps.append(
                    ActionStep(
                        primitive="app.launch",
                        params={"app": app_cmd},
                        description=f"Launch {app_desc}",
                    )
                )

        # 3. Audio Volume Control
        vol_match = re.search(r"\b(?:volume|sound)\s+(?:to\s+)?(\d{1,3})%?\b", text_lower) or re.search(r"\bset volume\s+(\d{1,3})\b", text_lower)
        if vol_match:
            pct = max(0, min(100, int(vol_match.group(1))))
            steps.append(
                ActionStep(
                    primitive="audio.set_volume",
                    params={"volume": pct / 100.0},
                    description=f"Set master audio volume to {pct}%",
                )
            )
        elif "mute audio" in text_lower or "mute volume" in text_lower or "unmute" in text_lower:
            steps.append(
                ActionStep(
                    primitive="audio.toggle_mute",
                    params={},
                    description="Toggle audio mute state",
                )
            )

        # 4. Brightness Control
        bright_match = re.search(r"\b(?:brightness|backlight)\s+(?:to\s+)?(\d{1,3})%?\b", text_lower)
        if bright_match:
            b_pct = max(0, min(100, int(bright_match.group(1))))
            steps.append(
                ActionStep(
                    primitive="brightness.set",
                    params={"brightness": b_pct},
                    description=f"Set display brightness to {b_pct}%",
                )
            )

        # 5. Wi-Fi Hotspot Toggle
        if re.search(r"\b(?:enable|start|turn on|activate)\s+(?:the\s+)?(?:wifi\s+)?hotspot\b", text_lower):
            steps.append(
                ActionStep(
                    primitive="hotspot.toggle",
                    params={"enable": True},
                    description="Activate local Wi-Fi Hotspot with QR code sharing",
                )
            )
        elif re.search(r"\b(?:disable|stop|turn off|deactivate)\s+(?:the\s+)?(?:wifi\s+)?hotspot\b", text_lower):
            steps.append(
                ActionStep(
                    primitive="hotspot.toggle",
                    params={"enable": False},
                    description="Deactivate local Wi-Fi Hotspot",
                )
            )

        # 6. Power Profile Switch
        if "battery saver" in text_lower or "power saver" in text_lower or "save battery" in text_lower:
            steps.append(
                ActionStep(
                    primitive="power.set_profile",
                    params={"profile": "power-saver"},
                    description="Switch power profile to Power Saver",
                )
            )
        elif "performance mode" in text_lower or "max performance" in text_lower:
            steps.append(
                ActionStep(
                    primitive="power.set_profile",
                    params={"profile": "performance"},
                    description="Switch power profile to Performance",
                )
            )
        elif "balanced profile" in text_lower or "balanced mode" in text_lower:
            steps.append(
                ActionStep(
                    primitive="power.set_profile",
                    params={"profile": "balanced"},
                    description="Switch power profile to Balanced",
                )
            )

        # 7. Screenshot Capture
        if "screenshot" in text_lower or "screen capture" in text_lower:
            mode = "region" if "region" in text_lower or "area" in text_lower else "window" if "window" in text_lower else "full"
            steps.append(
                ActionStep(
                    primitive="screenshot.capture",
                    params={"mode": mode},
                    description=f"Capture {mode} Wayland screenshot",
                )
            )

        # 8. Theme Switch
        theme_names = ["Midnight", "Nordic Light", "Forest", "Violet"]
        for th in theme_names:
            if th.lower() in text_lower and "theme" in text_lower:
                steps.append(
                    ActionStep(
                        primitive="theme.switch",
                        params={"name": th},
                        description=f"Switch desktop theme preset to '{th}'",
                    )
                )

        # 9. Web Search
        search_match = re.search(r"\b(?:search (?:the )?web for|google|web search)\s+(.+)", text, re.IGNORECASE)
        if search_match:
            q = search_match.group(1).strip()
            steps.append(
                ActionStep(
                    primitive="web.search",
                    params={"query": q},
                    description=f"Perform web research for '{q}'",
                )
            )

        plan.steps = steps
        # Validate plan through PermissionEngine
        self.permissions.validate_plan(plan)
        return plan

    def create_plan_from_json(self, raw_json: str) -> Tuple[bool, ActionPlan, Optional[str]]:
        """Parses a structured JSON action plan from an LLM tool call or API client."""
        try:
            data = json.loads(raw_json) if isinstance(raw_json, str) else raw_json
            goal = data.get("goal", "Execute actions")
            plan = ActionPlan(goal=goal)

            raw_steps = data.get("steps", [])
            for s in raw_steps:
                step = ActionStep(
                    primitive=s.get("primitive", ""),
                    params=s.get("params", {}),
                    description=s.get("description", ""),
                )
                plan.steps.append(step)

            valid, validated_plan, err = self.permissions.validate_plan(plan)
            return valid, validated_plan, err
        except Exception as e:
            plan = ActionPlan(goal="Parse error")
            plan.status = "failed"
            return False, plan, f"JSON parsing error: {e}"
