#!/usr/bin/env python3
"""
Centralized Configuration & Modular Feature Storage Engine for Tejas OS.
Manages atomic reads and writes to ~/.config/tejas-os/*.json files,
coordinates true feature process shutdowns/starts, performance profiles,
and configuration backups.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Any, Dict, List, Optional, Tuple


class ConfigManager:
    """Centralized configuration manager ensuring schema compliance and atomic writes."""

    BASE_CONFIG_DIR = os.path.expanduser("~/.config/tejas-os")

    DEFAULT_FEATURES = {
        "dock": {
            "name": "Desktop Dock",
            "description": "Floating application dock at screen bottom",
            "enabled": True,
            "daemons": [],
            "dependencies": [],
        },
        "topbar": {
            "name": "Status Top Bar",
            "description": "System status bar with clock, tray, and workspace indicators",
            "enabled": True,
            "daemons": [],
            "dependencies": [],
        },
        "notifications": {
            "name": "Notification Center & OSD",
            "description": "Freedesktop notification daemon and volume/brightness OSD",
            "enabled": True,
            "daemons": [],
            "dependencies": [],
        },
        "clipboard_history": {
            "name": "Clipboard Manager",
            "description": "Persistent clipboard history and quick picker",
            "enabled": True,
            "daemons": ["productivity.clipboard.clipboard_manager"],
            "dependencies": [],
        },
        "hotspot_gui": {
            "name": "Wi-Fi Hotspot",
            "description": "Access point manager and QR code sharing",
            "enabled": True,
            "daemons": [],
            "dependencies": [],
        },
        "june_assistant": {
            "name": "June AI Assistant",
            "description": "Independent decoupled voice/text AI assistant service",
            "enabled": True,
            "daemons": ["assistant.core.daemon"],
            "dependencies": [],
        },
        "multilingual_stt": {
            "name": "Multilingual Speech-to-Text",
            "description": "Trilingual voice transcription for English, Hindi, and Marathi",
            "enabled": True,
            "daemons": [],
            "dependencies": ["june_assistant"],
        },
        "multilingual_tts": {
            "name": "Multilingual Text-to-Speech",
            "description": "Natural pronunciation across English, Hindi, and Marathi",
            "enabled": True,
            "daemons": [],
            "dependencies": ["june_assistant"],
        },
        "developer_hub": {
            "name": "Developer Control Deck",
            "description": "Workspace manager, git tools, ports monitor, and SSH bookmarks",
            "enabled": True,
            "daemons": [],
            "dependencies": [],
        },
        "dashboard_vitals": {
            "name": "System Vitals Dashboard",
            "description": "Live CPU, RAM, battery, and thermals monitor",
            "enabled": True,
            "daemons": [],
            "dependencies": [],
        },
        "pomodoro": {
            "name": "Pomodoro Focus Timer",
            "description": "Productivity work & break session tracker",
            "enabled": True,
            "daemons": [],
            "dependencies": [],
        },
        "gamemode": {
            "name": "Game Mode Optimization",
            "description": "Suspends compositor animations and background indexing during gaming",
            "enabled": False,
            "daemons": [],
            "dependencies": [],
        },
    }

    DEFAULT_SETTINGS = {
        "version": "1.0.0",
        "theme": "midnight",
        "appearance": {
            "dark_mode": True,
            "font_family": "Inter Display",
            "font_family_mono": "JetBrainsMono Nerd Font",
            "font_size": 13,
            "border_radius": 12,
            "blur_enabled": True,
            "blur_strength": 8,
            "animations_enabled": True,
            "animation_speed": 1.0,
        },
        "compositor": {
            "gaps_in": 4,
            "gaps_out": 8,
            "border_size": 2,
            "mouse_sensitivity": 0.0,
            "natural_scroll": True,
            "tap_to_click": True,
            "touchpad_dwt": True,
        },
        "display": {
            "scale": 1.0,
            "refresh_rate": 60,
            "idle_timeout_sec": 300,
            "lock_timeout_sec": 600,
            "dpms_timeout_sec": 900,
        },
        "audio": {
            "default_volume": 65,
            "max_volume": 100,
            "feedback_sounds": True,
        },
        "performance": {
            "active_profile": "balanced",
        },
    }

    DEFAULT_PROFILES = {
        "balanced": {
            "name": "Balanced",
            "description": "Standard energy-efficient profile for daily development and multitasking",
            "cpu_governor": "powersave",
            "animations": True,
            "animation_speed": 1.0,
            "blur": True,
            "idle_timeout_sec": 300,
            "assistant_mode": "cloud_or_offline",
        },
        "performance": {
            "name": "Performance",
            "description": "Maximum CPU clock and GPU performance for compilation and heavy tasks",
            "cpu_governor": "performance",
            "animations": True,
            "animation_speed": 0.5,
            "blur": True,
            "idle_timeout_sec": 600,
            "assistant_mode": "cloud_or_local",
        },
        "battery_saver": {
            "name": "Battery Saver",
            "description": "Maximizes battery runtime by throttling CPU and turning off heavy effects",
            "cpu_governor": "powersave",
            "animations": False,
            "animation_speed": 0.0,
            "blur": False,
            "idle_timeout_sec": 120,
            "assistant_mode": "cloud_only",
        },
        "full_experience": {
            "name": "Full Experience",
            "description": "Rich desktop experience with deep blur, maximum fidelity, and full AI capabilities",
            "cpu_governor": "powersave",
            "animations": True,
            "animation_speed": 1.2,
            "blur": True,
            "idle_timeout_sec": 450,
            "assistant_mode": "full",
        },
    }

    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = os.path.abspath(config_dir or self.BASE_CONFIG_DIR)
        os.makedirs(self.config_dir, exist_ok=True)
        self.features_file = os.path.join(self.config_dir, "features.json")
        self.settings_file = os.path.join(self.config_dir, "settings.json")
        self.profiles_file = os.path.join(self.config_dir, "profiles.json")
        self.backups_dir = os.path.join(self.config_dir, "backups")
        os.makedirs(self.backups_dir, exist_ok=True)
        self._ensure_defaults()

    def _ensure_defaults(self):
        """Initializes default configuration files if not present."""
        if not os.path.exists(self.features_file):
            self.write_atomic(self.features_file, self.DEFAULT_FEATURES)
        if not os.path.exists(self.settings_file):
            self.write_atomic(self.settings_file, self.DEFAULT_SETTINGS)
        if not os.path.exists(self.profiles_file):
            self.write_atomic(self.profiles_file, self.DEFAULT_PROFILES)

    def read_json(self, file_path: str, default: Optional[Any] = None) -> Any:
        """Safely reads and parses a JSON file."""
        if not os.path.exists(file_path):
            return default if default is not None else {}
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default if default is not None else {}

    def write_atomic(self, file_path: str, data: Any) -> bool:
        """Atomically writes data to a JSON file via a temporary file."""
        target_dir = os.path.dirname(os.path.abspath(file_path))
        os.makedirs(target_dir, exist_ok=True)
        try:
            with tempfile.NamedTemporaryFile("w", dir=target_dir, delete=False, encoding="utf-8") as tf:
                json.dump(data, tf, indent=2, ensure_ascii=False)
                temp_path = tf.name
            os.replace(temp_path, file_path)
            return True
        except Exception:
            if "temp_path" in locals() and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass
            return False

    # =========================================================================
    # Feature Management & True Process Termination
    # =========================================================================

    def get_features(self) -> Dict[str, Any]:
        """Returns the dictionary of all features and their state."""
        return self.read_json(self.features_file, default=self.DEFAULT_FEATURES)

    def toggle_feature(self, feature_name: str, enable: Optional[bool] = None) -> Tuple[bool, str]:
        """
        Toggles a feature state.
        When disabling, terminates associated background processes (Rule 1.4).
        When enabling, checks dependencies and restores prior state.
        """
        features = self.get_features()
        if feature_name not in features:
            return False, f"Unknown feature: '{feature_name}'"

        feat = features[feature_name]
        current_state = feat.get("enabled", False)
        target_state = (not current_state) if enable is None else bool(enable)

        if current_state == target_state:
            return True, f"Feature '{feature_name}' is already {'enabled' if target_state else 'disabled'}"

        if target_state:
            # Check dependencies
            deps = feat.get("dependencies", [])
            for dep in deps:
                if not features.get(dep, {}).get("enabled", False):
                    dep_name = features.get(dep, {}).get("name", dep)
                    return False, f"Cannot enable '{feature_name}': depends on disabled feature '{dep_name}'"

            feat["enabled"] = True
            msg = f"Feature '{feat.get('name', feature_name)}' enabled"
        else:
            # Check dependent features
            dependent_features = [
                k for k, v in features.items()
                if v.get("enabled", False) and feature_name in v.get("dependencies", [])
            ]
            if dependent_features:
                names = [features[k].get("name", k) for k in dependent_features]
                return False, f"Cannot disable '{feature_name}': required by {', '.join(names)}"

            feat["enabled"] = False
            # Rule 1.4: True process termination
            killed_count = self._terminate_feature_processes(feat)
            msg = f"Feature '{feat.get('name', feature_name)}' disabled ({killed_count} processes terminated)"

        features[feature_name] = feat
        self.write_atomic(self.features_file, features)
        return True, msg

    def _terminate_feature_processes(self, feat: Dict[str, Any]) -> int:
        """Terminates background daemon processes associated with a feature."""
        daemons = feat.get("daemons", [])
        if not daemons:
            return 0

        terminated = 0
        for daemon_pattern in daemons:
            # Protected check: NEVER kill system daemons
            if any(protected in daemon_pattern.lower() for protected in ["networkmanager", "bluez", "systemd", "init"]):
                continue

            if sys.platform.startswith("linux"):
                try:
                    res = subprocess.run(["pkill", "-f", daemon_pattern], capture_output=True, timeout=2.0)
                    if res.returncode == 0:
                        terminated += 1
                except Exception:
                    pass
            elif sys.platform == "win32":
                # For test simulation on Windows
                pass

        return terminated

    # =========================================================================
    # Settings Management
    # =========================================================================

    def get_settings(self) -> Dict[str, Any]:
        """Returns the centralized system settings."""
        return self.read_json(self.settings_file, default=self.DEFAULT_SETTINGS)

    def update_settings(self, category: str, key: str, value: Any) -> bool:
        """Updates a specific configuration key atomically."""
        settings = self.get_settings()
        if category not in settings:
            settings[category] = {}

        if isinstance(settings[category], dict):
            settings[category][key] = value
        else:
            settings[category] = {key: value}

        return self.write_atomic(self.settings_file, settings)

    def set_theme(self, theme_name: str) -> bool:
        """Sets the active desktop theme preset (midnight, nordic, forest, violet)."""
        valid_themes = ["midnight", "nordic", "forest", "violet"]
        if theme_name.lower() not in valid_themes:
            return False
        settings = self.get_settings()
        settings["theme"] = theme_name.lower()
        return self.write_atomic(self.settings_file, settings)

    # =========================================================================
    # Performance Profiles
    # =========================================================================

    def get_profiles(self) -> Dict[str, Any]:
        """Returns all available performance profiles."""
        return self.read_json(self.profiles_file, default=self.DEFAULT_PROFILES)

    def get_active_profile(self) -> str:
        """Returns the name of the active performance profile."""
        settings = self.get_settings()
        return settings.get("performance", {}).get("active_profile", "balanced")

    def apply_profile(self, profile_name: str) -> Tuple[bool, str]:
        """
        Applies a performance profile (balanced, performance, battery_saver, full_experience).
        Synchronizes compositor animations, blur tokens, and CPU governor.
        """
        profiles = self.get_profiles()
        profile_key = profile_name.lower().replace(" ", "_")
        if profile_key not in profiles:
            return False, f"Unknown profile: '{profile_name}'"

        prof = profiles[profile_key]
        settings = self.get_settings()

        # Update settings
        settings.setdefault("performance", {})["active_profile"] = profile_key
        settings.setdefault("appearance", {})["blur_enabled"] = prof.get("blur", True)
        settings["appearance"]["animations_enabled"] = prof.get("animations", True)
        settings["appearance"]["animation_speed"] = prof.get("animation_speed", 1.0)
        settings.setdefault("display", {})["idle_timeout_sec"] = prof.get("idle_timeout_sec", 300)

        self.write_atomic(self.settings_file, settings)

        # On Linux, set CPU governor if power-profiles-daemon or cpupower exists
        if sys.platform.startswith("linux"):
            gov = prof.get("cpu_governor", "powersave")
            try:
                # Try powerprofilesctl first (standard desktop daemon)
                if shutil.which("powerprofilesctl"):
                    pp_profile = "power-saver" if gov == "powersave" and profile_key == "battery_saver" else (
                        "performance" if gov == "performance" else "balanced"
                    )
                    subprocess.run(["powerprofilesctl", "set", pp_profile], capture_output=True, timeout=2.0)
            except Exception:
                pass

        return True, f"Successfully activated '{prof['name']}' profile"

    # =========================================================================
    # Configuration Backup & Recovery
    # =========================================================================

    def create_backup(self, tag: str = "manual") -> Dict[str, Any]:
        """Creates a timestamped snapshot of current configuration files."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_id = f"backup_{timestamp}_{tag}"
        target_dir = os.path.join(self.backups_dir, backup_id)
        os.makedirs(target_dir, exist_ok=True)

        copied_files = []
        for fname in os.listdir(self.config_dir):
            src = os.path.join(self.config_dir, fname)
            if os.path.isfile(src) and fname.endswith(".json"):
                dst = os.path.join(target_dir, fname)
                shutil.copy2(src, dst)
                copied_files.append(fname)

        meta = {
            "id": backup_id,
            "timestamp": timestamp,
            "tag": tag,
            "files": copied_files,
            "path": target_dir,
        }
        with open(os.path.join(target_dir, "meta.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

        return meta

    def list_backups(self) -> List[Dict[str, Any]]:
        """Returns the list of available configuration backups."""
        backups = []
        if not os.path.exists(self.backups_dir):
            return []

        for b_name in sorted(os.listdir(self.backups_dir), reverse=True):
            b_path = os.path.join(self.backups_dir, b_name)
            meta_file = os.path.join(b_path, "meta.json")
            if os.path.isdir(b_path) and os.path.exists(meta_file):
                try:
                    with open(meta_file, "r", encoding="utf-8") as f:
                        backups.append(json.load(f))
                except Exception:
                    continue
        return backups

    def restore_backup(self, backup_id: str) -> Tuple[bool, str]:
        """Restores configuration files from a backup snapshot."""
        target_dir = os.path.join(self.backups_dir, backup_id)
        if not os.path.isdir(target_dir):
            return False, f"Backup '{backup_id}' not found"

        restored_files = []
        for fname in os.listdir(target_dir):
            if fname.endswith(".json") and fname != "meta.json":
                src = os.path.join(target_dir, fname)
                dst = os.path.join(self.config_dir, fname)
                shutil.copy2(src, dst)
                restored_files.append(fname)

        return True, f"Restored {len(restored_files)} configuration files from '{backup_id}'"

    def reset_to_defaults(self) -> bool:
        """Resets all configuration files to factory presets (creating a backup first)."""
        self.create_backup(tag="pre_reset")
        self.write_atomic(self.features_file, self.DEFAULT_FEATURES)
        self.write_atomic(self.settings_file, self.DEFAULT_SETTINGS)
        self.write_atomic(self.profiles_file, self.DEFAULT_PROFILES)
        return True


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Tejas OS Centralized Config & Feature Manager")
    parser.add_argument("--config-dir", help="Custom configuration directory")
    parser.add_argument("--list-features", action="store_true", help="List all features and their status")
    parser.add_argument("--toggle", help="Toggle a feature by name")
    parser.add_argument("--enable", help="Enable a feature by name")
    parser.add_argument("--disable", help="Disable a feature by name")
    parser.add_argument("--theme", help="Set active theme preset")
    parser.add_argument("--profile", help="Apply a performance profile")
    parser.add_argument("--backup", nargs="?", const="manual", help="Create a backup snapshot with optional tag")
    parser.add_argument("--list-backups", action="store_true", help="List available backups")
    parser.add_argument("--restore", help="Restore a backup snapshot by ID")
    parser.add_argument("--reset-defaults", action="store_true", help="Reset all configuration to defaults")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")

    args = parser.parse_args()
    mgr = ConfigManager(args.config_dir)

    if args.list_features:
        features = mgr.get_features()
        if args.json:
            print(json.dumps(features, indent=2))
        else:
            print(f"Tejas OS Features ({len(features)}):")
            for k, v in features.items():
                status = "ENABLED " if v.get("enabled") else "DISABLED"
                print(f"  [{status}] {k:<20} - {v.get('name', k)}")
        return

    if args.toggle:
        ok, msg = mgr.toggle_feature(args.toggle)
        print(f"[{'OK' if ok else 'FAIL'}] {msg}")
        return

    if args.enable:
        ok, msg = mgr.toggle_feature(args.enable, enable=True)
        print(f"[{'OK' if ok else 'FAIL'}] {msg}")
        return

    if args.disable:
        ok, msg = mgr.toggle_feature(args.disable, enable=False)
        print(f"[{'OK' if ok else 'FAIL'}] {msg}")
        return

    if args.theme:
        ok = mgr.set_theme(args.theme)
        print(f"Theme set to '{args.theme}': {ok}")
        return

    if args.profile:
        ok, msg = mgr.apply_profile(args.profile)
        print(f"[{'OK' if ok else 'FAIL'}] {msg}")
        return

    if args.backup:
        meta = mgr.create_backup(tag=args.backup)
        if args.json:
            print(json.dumps(meta, indent=2))
        else:
            print(f"Created backup: {meta['id']} ({len(meta['files'])} files)")
        return

    if args.list_backups:
        backups = mgr.list_backups()
        if args.json:
            print(json.dumps(backups, indent=2))
        else:
            print(f"Available Backups ({len(backups)}):")
            for b in backups:
                print(f"  • {b['id']} ({b.get('timestamp')}) -> {len(b.get('files', []))} files")
        return

    if args.restore:
        ok, msg = mgr.restore_backup(args.restore)
        print(f"[{'OK' if ok else 'FAIL'}] {msg}")
        return

    if args.reset_defaults:
        ok = mgr.reset_to_defaults()
        print(f"Reset to factory defaults: {ok}")
        return

    # Default: dump settings summary
    settings = mgr.get_settings()
    if args.json:
        print(json.dumps(settings, indent=2))
    else:
        print(f"Tejas OS Configuration: {mgr.config_dir}")
        print(f"Theme: {settings.get('theme')}")
        print(f"Profile: {settings.get('performance', {}).get('active_profile')}")


if __name__ == "__main__":
    main()
