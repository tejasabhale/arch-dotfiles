#!/usr/bin/env python3
"""
Node.js & NPM Scripts Inspector.
Reads package.json, identifies active package manager (npm, pnpm, yarn, bun),
inspects dev dependencies, and generates/executes scripts.
"""

import json
import os
import shutil
import subprocess
import sys
from typing import Any, Dict, List, Optional, Tuple


class NodeManager:
    """Inspects Node.js projects, package.json files, dependencies, and scripts."""

    LOCKFILE_MAP = {
        "pnpm-lock.yaml": "pnpm",
        "yarn.lock": "yarn",
        "bun.lockb": "bun",
        "bun.lock": "bun",
        "package-lock.json": "npm",
    }

    DEV_SCRIPT_KEYWORDS = ["dev", "start", "serve", "watch", "build", "test", "lint", "preview"]

    def __init__(self, workspace_path: Optional[str] = None):
        self.workspace_path = os.path.abspath(workspace_path or ".")

    def get_runtime_versions(self) -> Dict[str, Optional[str]]:
        """Returns detected versions of Node, npm, pnpm, yarn, and bun on the system."""
        tools = ["node", "npm", "pnpm", "yarn", "bun"]
        versions: Dict[str, Optional[str]] = {}

        for tool in tools:
            bin_path = shutil.which(tool)
            if not bin_path:
                versions[tool] = None
                continue
            try:
                res = subprocess.run(
                    [bin_path, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=2.0,
                )
                if res.returncode == 0:
                    versions[tool] = res.stdout.strip()
                else:
                    versions[tool] = "installed"
            except Exception:
                versions[tool] = "error"

        return versions

    def is_node_project(self, target_dir: Optional[str] = None) -> bool:
        """Checks if a directory contains a package.json file."""
        pkg_path = os.path.join(target_dir or self.workspace_path, "package.json")
        return os.path.isfile(pkg_path)

    def detect_package_manager(self, target_dir: Optional[str] = None) -> str:
        """Determines the appropriate package manager based on lockfiles present."""
        base_dir = os.path.abspath(target_dir or self.workspace_path)
        for lockfile, pm in self.LOCKFILE_MAP.items():
            if os.path.isfile(os.path.join(base_dir, lockfile)):
                if shutil.which(pm):
                    return pm
                return f"{pm} (not installed)"

        # Check if project specifies "packageManager" in package.json
        pkg_data = self.read_package_json(base_dir)
        if pkg_data and "packageManager" in pkg_data:
            pm_spec = pkg_data["packageManager"].split("@")[0]
            if shutil.which(pm_spec):
                return pm_spec
            return f"{pm_spec} (not installed)"

        # Default fallback
        if shutil.which("pnpm"):
            return "pnpm"
        if shutil.which("npm"):
            return "npm"
        if shutil.which("yarn"):
            return "yarn"
        if shutil.which("bun"):
            return "bun"
        return "npm"

    def read_package_json(self, target_dir: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Reads and parses package.json."""
        base_dir = os.path.abspath(target_dir or self.workspace_path)
        pkg_path = os.path.join(base_dir, "package.json")
        if not os.path.isfile(pkg_path):
            return None

        try:
            with open(pkg_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def get_project_summary(self, target_dir: Optional[str] = None) -> Dict[str, Any]:
        """Provides a comprehensive summary of the Node project."""
        base_dir = os.path.abspath(target_dir or self.workspace_path)
        pkg = self.read_package_json(base_dir)

        if not pkg:
            return {
                "is_node_project": False,
                "workspace": base_dir,
                "package_manager": None,
                "scripts": {},
                "dependencies_count": 0,
                "dev_dependencies_count": 0,
            }

        scripts = pkg.get("scripts", {})
        dependencies = pkg.get("dependencies", {})
        dev_dependencies = pkg.get("devDependencies", {})
        pm = self.detect_package_manager(base_dir)

        # Categorize scripts
        dev_scripts = {k: v for k, v in scripts.items() if any(kw in k.lower() for kw in self.DEV_SCRIPT_KEYWORDS)}

        return {
            "is_node_project": True,
            "workspace": base_dir,
            "name": pkg.get("name", os.path.basename(base_dir)),
            "version": pkg.get("version", "0.0.0"),
            "description": pkg.get("description", ""),
            "package_manager": pm,
            "scripts": scripts,
            "dev_scripts": dev_scripts,
            "dependencies_count": len(dependencies),
            "dev_dependencies_count": len(dev_dependencies),
            "dependencies": list(dependencies.keys()),
            "dev_dependencies": list(dev_dependencies.keys()),
            "node_modules_present": os.path.isdir(os.path.join(base_dir, "node_modules")),
        }

    def get_run_command(self, script_name: str, target_dir: Optional[str] = None) -> List[str]:
        """Generates the command list to run a script with the detected package manager."""
        pm = self.detect_package_manager(target_dir).split()[0]  # strip "(not installed)" if any
        if pm == "npm":
            return ["npm", "run", script_name]
        if pm in ["pnpm", "yarn", "bun"]:
            return [pm, script_name]
        return ["npm", "run", script_name]

    def run_script(
        self,
        script_name: str,
        target_dir: Optional[str] = None,
        timeout: float = 60.0,
    ) -> Tuple[bool, str]:
        """Executes a package script synchronously."""
        base_dir = os.path.abspath(target_dir or self.workspace_path)
        cmd = self.get_run_command(script_name, base_dir)

        if not shutil.which(cmd[0]):
            return False, f"Package manager binary '{cmd[0]}' not found in PATH"

        try:
            res = subprocess.run(
                cmd,
                cwd=base_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            if res.returncode == 0:
                return True, res.stdout.strip()
            return False, res.stderr.strip() or res.stdout.strip()
        except subprocess.TimeoutExpired:
            return False, f"Script execution timed out after {timeout}s"
        except Exception as e:
            return False, str(e)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Developer Node.js & NPM Scripts Inspector")
    parser.add_argument("--workspace", "-w", default=".", help="Project workspace path")
    parser.add_argument("--info", action="store_true", help="Display project summary")
    parser.add_argument("--scripts", action="store_true", help="List runnable scripts")
    parser.add_argument("--run", help="Run a specific script")
    parser.add_argument("--runtimes", action="store_true", help="List detected Node runtime versions")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")

    args = parser.parse_args()
    mgr = NodeManager(args.workspace)

    if args.runtimes:
        versions = mgr.get_runtime_versions()
        if args.json:
            print(json.dumps(versions, indent=2))
        else:
            print("Detected Node runtimes:")
            for tool, ver in versions.items():
                print(f"  • {tool}: {ver or 'Not installed'}")
        return

    if args.run:
        ok, out = mgr.run_script(args.run)
        if args.json:
            print(json.dumps({"success": ok, "output": out}, indent=2))
        else:
            status = "SUCCESS" if ok else "FAILED"
            print(f"[{status}] Script '{args.run}':\n{out}")
        sys.exit(0 if ok else 1)

    summary = mgr.get_project_summary()

    if args.scripts:
        if args.json:
            print(json.dumps(summary.get("scripts", {}), indent=2))
        else:
            print(f"Scripts in {summary.get('name', 'project')}:")
            for k, v in summary.get("scripts", {}).items():
                print(f"  • {k}: {v}")
        return

    # Default / Info
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        if not summary["is_node_project"]:
            print(f"No package.json found in {mgr.workspace_path}")
            return
        print(f"Node Project: {summary['name']} v{summary['version']}")
        print(f"Package Manager: {summary['package_manager']}")
        print(f"Dependencies: {summary['dependencies_count']} prod, {summary['dev_dependencies_count']} dev")
        print(f"Scripts ({len(summary['scripts'])}): {', '.join(list(summary['scripts'].keys())[:8])}")


if __name__ == "__main__":
    main()
