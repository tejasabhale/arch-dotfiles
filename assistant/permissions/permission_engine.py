#!/usr/bin/env python3
"""
Permission Engine & Security Sandbox for June AI.
Enforces AGENTS.md Rule 1.5 (Dual-Boot & System Safety) and Rule 2.2 (Security & Controlled Execution).
Prevents shell injection and validates action primitives against strict allowlists.
"""

import re
from typing import Any, Dict, List, Optional, Set, Tuple

from assistant.action_planner.models import ActionPlan, ActionStep, RiskLevel

# Primitives allowlist and their baseline risk tier
PRIMITIVE_RISK_MAP = {
    # Desktop navigation & controls (LOW risk - auto-executable)
    "workspace.switch": RiskLevel.LOW,
    "app.launch": RiskLevel.LOW,
    "audio.set_volume": RiskLevel.LOW,
    "audio.toggle_mute": RiskLevel.LOW,
    "brightness.set": RiskLevel.LOW,
    "screenshot.capture": RiskLevel.LOW,
    "clipboard.copy": RiskLevel.LOW,
    "notification.send": RiskLevel.LOW,
    "theme.switch": RiskLevel.LOW,
    "note.create": RiskLevel.LOW,
    "file.read_scoped": RiskLevel.LOW,
    "web.search": RiskLevel.LOW,

    # System & Hardware State Modifiers (MEDIUM risk - user visibility / confirmation)
    "hotspot.toggle": RiskLevel.MEDIUM,
    "wifi.toggle": RiskLevel.MEDIUM,
    "bluetooth.toggle": RiskLevel.MEDIUM,
    "power.set_profile": RiskLevel.MEDIUM,

    # Potentially disruptive actions (HIGH risk - explicit user confirmation required)
    "process.kill": RiskLevel.HIGH,
    "file.delete_scoped": RiskLevel.HIGH,
}

# Allowlisted Applications for app.launch
ALLOWLISTED_APPS = {
    "kitty",
    "dolphin",
    "firefox",
    "chromium",
    "google-chrome",
    "code",
    "vscodium",
    "obsidian",
    "spotify",
    "gnome-calculator",
    "kcalc",
    "pavucontrol",
    "thunar",
}

# Forbidden command patterns (Strict non-negotiable safety guardrails)
FORBIDDEN_PATTERNS = [
    re.compile(r"\b(mkfs|fdisk|parted|gdisk|cfdisk|sfdisk|wipefs|badblocks)\b", re.IGNORECASE),
    re.compile(r"\b(dd|shred)\s+.*if=", re.IGNORECASE),
    re.compile(r"\bbootmgfw\.efi\b", re.IGNORECASE),
    re.compile(r"/boot/efi", re.IGNORECASE),
    re.compile(r"\b(sudo\s+rm\s+-rf\s+/|rm\s+-rf\s+/\*)\b", re.IGNORECASE),
    re.compile(r"\b(format|mount|umount)\b", re.IGNORECASE),
]


class PermissionEngine:
    """Validates action primitives and protects system integrity."""

    def is_forbidden(self, text: str) -> Tuple[bool, Optional[str]]:
        """Scans input text or arguments for forbidden destructive patterns."""
        for pattern in FORBIDDEN_PATTERNS:
            if pattern.search(text):
                return True, f"Security Violation: Matched forbidden safety pattern '{pattern.pattern}'"
        return False, None

    def validate_step(self, step: ActionStep) -> Tuple[bool, RiskLevel, Optional[str]]:
        """
        Validates an individual action step.
        Returns: (is_valid: bool, effective_risk: RiskLevel, reason: Optional[str])
        """
        prim = step.primitive.strip()

        # Check primitive against allowlist
        if prim not in PRIMITIVE_RISK_MAP:
            return False, RiskLevel.BLOCKED, f"Unrecognized or un-allowlisted primitive: '{prim}'"

        # Check all string parameters for destructive keywords
        for key, val in step.params.items():
            if isinstance(val, str):
                forbidden, reason = self.is_forbidden(val)
                if forbidden:
                    return False, RiskLevel.BLOCKED, reason

        # Specific primitive validation rules
        if prim == "workspace.switch":
            ws = step.params.get("workspace_id")
            if not isinstance(ws, int) or ws < 1 or ws > 20:
                return False, RiskLevel.BLOCKED, f"Invalid workspace_id '{ws}'. Must be an integer between 1 and 20."

        elif prim == "app.launch":
            app = str(step.params.get("app", "")).lower().strip()
            if app not in ALLOWLISTED_APPS:
                return False, RiskLevel.BLOCKED, f"App '{app}' is not in the desktop application allowlist."

        elif prim == "power.set_profile":
            prof = str(step.params.get("profile", "")).lower().strip()
            if prof not in ["balanced", "performance", "power-saver"]:
                return False, RiskLevel.BLOCKED, f"Invalid power profile '{prof}'. Must be balanced, performance, or power-saver."

        elif prim == "theme.switch":
            theme = str(step.params.get("name", "")).strip()
            if theme not in ["Midnight", "Nordic Light", "Forest", "Violet"]:
                return False, RiskLevel.BLOCKED, f"Unknown theme preset '{theme}'."

        elif prim == "audio.set_volume":
            vol = step.params.get("volume")
            if vol is not None and (not isinstance(vol, (int, float)) or vol < 0.0 or vol > 1.5):
                return False, RiskLevel.BLOCKED, "Volume must be a number between 0.0 and 1.5."

        elif prim == "brightness.set":
            b = step.params.get("brightness")
            if not isinstance(b, int) or b < 0 or b > 100:
                return False, RiskLevel.BLOCKED, "Brightness must be an integer between 0 and 100."

        effective_risk = PRIMITIVE_RISK_MAP[prim]
        step.risk_level = effective_risk
        return True, effective_risk, None

    def validate_plan(self, plan: ActionPlan) -> Tuple[bool, ActionPlan, Optional[str]]:
        """
        Validates all steps in an action plan.
        Flags requires_confirmation if any step is MEDIUM or HIGH risk.
        Rejects immediately if any step is BLOCKED.
        """
        requires_conf = False

        for step in plan.steps:
            valid, risk, err = self.validate_step(step)
            if not valid or risk == RiskLevel.BLOCKED:
                plan.status = "aborted"
                return False, plan, f"Action Plan blocked at step '{step.primitive}': {err}"

            if risk in (RiskLevel.MEDIUM, RiskLevel.HIGH):
                requires_conf = True

        plan.requires_confirmation = requires_conf
        plan.status = "pending_approval" if requires_conf else "approved"
        return True, plan, None
