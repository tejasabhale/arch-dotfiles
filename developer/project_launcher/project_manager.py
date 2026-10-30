#!/usr/bin/env python3
"""
Developer Project Manager & Workspace Launcher.
Discovers local code repositories, identifies project toolchains,
and opens projects in VS Code, Kitty, Dolphin, or the browser.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Dict, List, Optional


class ProjectManager:
    """Manages project discovery and one-click development workspace launches."""

    CONFIG_PATH = os.path.expanduser("~/.config/tejas-os/projects.json")

    DEFAULT_SCAN_DIRS = [
        os.path.abspath("."),
        os.path.expanduser("~/Projects"),
        os.path.expanduser("~/Work"),
        os.path.expanduser("~/Developer"),
        os.path.expanduser("~/src"),
    ]

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self.CONFIG_PATH
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        self._ensure_config()

    def _ensure_config(self):
        if not os.path.exists(self.config_path):
            initial_data = {
                "pinned": [
                    {
                        "name": "Arch Dotfiles (Tejas OS)",
                        "path": os.path.abspath("."),
                        "type": "System / Desktop",
                        "git_branch": "master",
                    }
                ]
            }
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(initial_data, f, indent=2)

    def _load_config(self) -> Dict[str, Any]:
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"pinned": []}

    def _save_config(self, data: Dict[str, Any]) -> bool:
        try:
            target_dir = os.path.dirname(self.config_path)
            with tempfile.NamedTemporaryFile("w", dir=target_dir, delete=False, encoding="utf-8") as tf:
                json.dump(data, tf, indent=2, ensure_ascii=False)
                temp_name = tf.name
            os.replace(temp_name, self.config_path)
            return True
        except Exception:
            return False

    def detect_project_type(self, path: str) -> str:
        """Identifies programming language or ecosystem from workspace files."""
        if not os.path.exists(path) or not os.path.isdir(path):
            return "Unknown"

        entries = set(os.listdir(path))

        if "pyproject.toml" in entries or "requirements.txt" in entries or "setup.py" in entries:
            return "Python"
        if "package.json" in entries:
            if "tsconfig.json" in entries:
                return "TypeScript / Node"
            return "JavaScript / Node"
        if "Cargo.toml" in entries:
            return "Rust"
        if "go.mod" in entries:
            return "Go"
        if "CMakeLists.txt" in entries or "Makefile" in entries:
            return "C / C++"
        if "hyprland.lua" in entries or "shell.qml" in entries:
            return "Arch / Hyprland Dotfiles"
        if ".git" in entries:
            return "Git Repository"
        return "Generic Project"

    def get_git_branch(self, path: str) -> Optional[str]:
        """Queries git branch name if directory is a git repository."""
        git_head = os.path.join(path, ".git", "HEAD")
        if os.path.exists(git_head):
            try:
                with open(git_head, "r", encoding="utf-8") as f:
                    ref = f.read().strip()
                if ref.startswith("ref: refs/heads/"):
                    return ref[16:]
                return ref[:7]
            except Exception:
                pass
        return None

    def scan_workspaces(
        self,
        extra_dirs: Optional[List[str]] = None,
        custom_dirs: Optional[List[str]] = None,
        max_depth: int = 1,
    ) -> List[Dict[str, Any]]:
        """Scans standard development directories for code projects."""
        scan_roots = list(self.DEFAULT_SCAN_DIRS)
        all_extras = (extra_dirs or []) + (custom_dirs or [])
        if all_extras:
            scan_roots.extend(all_extras)

        discovered = []
        seen_paths = set()

        for root in scan_roots:
            if not os.path.exists(root) or not os.path.isdir(root):
                continue

            # Check if root itself is a project
            if root not in seen_paths and (os.path.exists(os.path.join(root, ".git")) or self.detect_project_type(root) != "Unknown"):
                seen_paths.add(root)
                discovered.append({
                    "name": os.path.basename(root) or "Root Workspace",
                    "path": root,
                    "type": self.detect_project_type(root),
                    "git_branch": self.get_git_branch(root),
                })

            # Check immediate children
            try:
                for entry in os.listdir(root):
                    full_p = os.path.join(root, entry)
                    if os.path.isdir(full_p) and full_p not in seen_paths and not entry.startswith((".", "node_modules", "target")):
                        p_type = self.detect_project_type(full_p)
                        if p_type != "Unknown" or os.path.exists(os.path.join(full_p, ".git")):
                            seen_paths.add(full_p)
                            discovered.append({
                                "name": entry,
                                "path": full_p,
                                "type": p_type,
                                "git_branch": self.get_git_branch(full_p),
                            })
            except Exception:
                continue

        return discovered

    def list_projects(self) -> List[Dict[str, Any]]:
        """Returns pinned projects merged with auto-discovered projects."""
        cfg = self._load_config()
        pinned = cfg.get("pinned", [])

        # Refresh git branch on pinned projects
        for p in pinned:
            p["git_branch"] = self.get_git_branch(p["path"])
            p["is_pinned"] = True

        discovered = self.scan_workspaces()
        pinned_paths = {p["path"] for p in pinned}

        for d in discovered:
            if d["path"] not in pinned_paths:
                d["is_pinned"] = False
                pinned.append(d)

        return pinned

    def list_pinned(self) -> List[Dict[str, Any]]:
        """Returns only the list of explicitly pinned projects."""
        cfg = self._load_config()
        return cfg.get("pinned", [])

    def pin_project(self, path: str, name: Optional[str] = None, p_type: Optional[str] = None) -> bool:
        """Alias for pinning a project with optional explicit type."""
        res = self.add_pinned(path, name=name)
        if p_type and res:
            cfg = self._load_config()
            for p in cfg.get("pinned", []):
                if p["path"] == os.path.abspath(os.path.expanduser(path)):
                    p["type"] = p_type
            self._save_config(cfg)
        return bool(res)

    def unpin_project(self, path: str) -> bool:
        """Alias for removing a pinned project."""
        return self.remove_pinned(path)

    def add_pinned(self, path: str, name: Optional[str] = None) -> Dict[str, Any]:
        """Pins a new project to the launcher."""
        abs_p = os.path.abspath(os.path.expanduser(path))
        cfg = self._load_config()
        pinned = cfg.get("pinned", [])

        # Check if already pinned
        for p in pinned:
            if p["path"] == abs_p:
                return p

        item = {
            "name": name or os.path.basename(abs_p),
            "path": abs_p,
            "type": self.detect_project_type(abs_p),
            "git_branch": self.get_git_branch(abs_p),
        }
        pinned.append(item)
        cfg["pinned"] = pinned
        self._save_config(cfg)
        return item

    def remove_pinned(self, path: str) -> bool:
        abs_p = os.path.abspath(os.path.expanduser(path))
        cfg = self._load_config()
        pinned = cfg.get("pinned", [])
        initial_len = len(pinned)
        pinned = [p for p in pinned if p["path"] != abs_p]
        if len(pinned) < initial_len:
            cfg["pinned"] = pinned
            return self._save_config(cfg)
        return False

    def open_project(self, path: str, target: str = "code") -> Dict[str, Any]:
        """
        Launches project in specified tool.
        target: 'code', 'terminal', 'files'
        """
        abs_p = os.path.abspath(os.path.expanduser(path))
        if not os.path.exists(abs_p):
            return {"success": False, "error": f"Path '{abs_p}' does not exist"}

        try:
            if target == "code":
                editor = "code" if shutil.which("code") else "codium" if shutil.which("codium") else None
                if editor:
                    subprocess.Popen([editor, abs_p], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return {"success": True, "target": editor, "path": abs_p}
                return {"success": False, "error": "VS Code / Codium is not installed in PATH"}

            elif target == "terminal":
                term = "kitty" if shutil.which("kitty") else "alacritty" if shutil.which("alacritty") else None
                if term:
                    subprocess.Popen([term, "--directory", abs_p], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return {"success": True, "target": term, "path": abs_p}
                return {"success": False, "error": "Terminal emulator not found in PATH"}

            elif target == "files":
                fm = "dolphin" if shutil.which("dolphin") else "thunar" if shutil.which("thunar") else "xdg-open"
                if shutil.which(fm):
                    subprocess.Popen([fm, abs_p], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return {"success": True, "target": fm, "path": abs_p}
                return {"success": False, "error": "File manager not found in PATH"}

            return {"success": False, "error": f"Unknown target '{target}'"}
        except Exception as e:
            return {"success": False, "error": str(e)}


def main():
    pm = ProjectManager()
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == "list":
            print(json.dumps(pm.list_projects(), indent=2))
            return
        elif cmd == "add" and len(sys.argv) > 2:
            name = sys.argv[3] if len(sys.argv) > 3 else None
            print(json.dumps(pm.add_pinned(sys.argv[2], name), indent=2))
            return
        elif cmd == "open" and len(sys.argv) > 2:
            target = sys.argv[3] if len(sys.argv) > 3 else "code"
            print(json.dumps(pm.open_project(sys.argv[2], target=target), indent=2))
            return

    print(json.dumps(pm.list_projects(), indent=2))


if __name__ == "__main__":
    main()
