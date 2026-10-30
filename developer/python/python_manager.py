#!/usr/bin/env python3
"""
Python Environment & Toolchain Manager.
Detects virtual environments (.venv, venv, conda, uv), inspects installed packages,
and manages Jupyter Notebook/Lab instances.
"""

import json
import os
import shutil
import subprocess
import sys
from typing import Any, Dict, List, Optional, Tuple


class PythonManager:
    """Manages Python virtual environments, package inspection, and Jupyter sessions."""

    COMMON_VENV_NAMES = [".venv", "venv", "env", ".env", "virtualenv"]

    def __init__(self, workspace_path: Optional[str] = None):
        self.workspace_path = os.path.abspath(workspace_path or ".")

    def get_system_python(self) -> Dict[str, Any]:
        """Returns details about the default system Python interpreter."""
        py_bin = shutil.which("python3") or shutil.which("python") or sys.executable
        version_str = sys.version.split()[0]
        return {
            "executable": py_bin,
            "version": version_str,
            "is_system": True,
        }

    def detect_local_venvs(self, target_dir: Optional[str] = None) -> List[Dict[str, Any]]:
        """Detects virtual environments in the target directory or its immediate subdirectories."""
        base_dir = os.path.abspath(target_dir or self.workspace_path)
        venvs = []

        # 1. Check common venv folders in project root
        for name in self.COMMON_VENV_NAMES:
            candidate = os.path.join(base_dir, name)
            if self._is_valid_venv(candidate):
                venvs.append(self._inspect_venv(candidate, f"Local ({name})"))

        # 2. Check pyproject.toml / uv venv indicators
        uv_cache_dir = os.path.join(base_dir, ".venv")
        if os.path.exists(os.path.join(base_dir, "uv.lock")) and self._is_valid_venv(uv_cache_dir):
            if not any(v["path"] == uv_cache_dir for v in venvs):
                venvs.append(self._inspect_venv(uv_cache_dir, "uv venv"))

        # 3. Check poetry environment if applicable
        poetry_bin = shutil.which("poetry")
        if poetry_bin and os.path.exists(os.path.join(base_dir, "poetry.lock")):
            try:
                res = subprocess.run(
                    [poetry_bin, "env", "info", "--path"],
                    cwd=base_dir,
                    capture_output=True,
                    text=True,
                    timeout=3.0,
                )
                if res.returncode == 0 and res.stdout.strip():
                    p_path = res.stdout.strip()
                    if self._is_valid_venv(p_path) and not any(v["path"] == p_path for v in venvs):
                        venvs.append(self._inspect_venv(p_path, "Poetry"))
            except Exception:
                pass

        return venvs

    def detect_conda_envs(self) -> List[Dict[str, Any]]:
        """Detects Conda/Mamba environments if installed."""
        conda_bin = shutil.which("conda") or shutil.which("mamba")
        envs = []

        if conda_bin:
            try:
                res = subprocess.run(
                    [conda_bin, "info", "--envs", "--json"],
                    capture_output=True,
                    text=True,
                    timeout=5.0,
                )
                if res.returncode == 0:
                    data = json.loads(res.stdout)
                    for env_path in data.get("envs", []):
                        name = os.path.basename(env_path)
                        if env_path == data.get("default_prefix"):
                            name = f"{name} (base)"
                        envs.append({
                            "name": name,
                            "type": "Conda",
                            "path": env_path,
                            "executable": self._get_venv_python(env_path),
                            "version": self._get_env_python_version(env_path),
                        })
            except Exception:
                pass

        # Fallback: Check ~/.conda/environments.txt
        env_file = os.path.expanduser("~/.conda/environments.txt")
        if not envs and os.path.isfile(env_file):
            try:
                with open(env_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and os.path.isdir(line) and not any(e["path"] == line for e in envs):
                            envs.append({
                                "name": os.path.basename(line),
                                "type": "Conda",
                                "path": line,
                                "executable": self._get_venv_python(line),
                                "version": self._get_env_python_version(line),
                            })
            except Exception:
                pass

        return envs

    def get_all_environments(self) -> List[Dict[str, Any]]:
        """Collects local project virtualenvs, Conda environments, and system Python."""
        all_envs = []
        # Local project environments
        all_envs.extend(self.detect_local_venvs())
        # Conda environments
        all_envs.extend(self.detect_conda_envs())
        # System interpreter
        sys_py = self.get_system_python()
        all_envs.append({
            "name": f"System Python ({sys_py['version']})",
            "type": "System",
            "path": os.path.dirname(os.path.dirname(sys_py["executable"] or "")),
            "executable": sys_py["executable"],
            "version": sys_py["version"],
        })
        return all_envs

    def list_installed_packages(self, venv_path: Optional[str] = None) -> List[Dict[str, str]]:
        """Lists packages installed in the virtual environment or system Python."""
        py_exe = self._get_venv_python(venv_path) if venv_path else sys.executable
        if not py_exe or not os.path.exists(py_exe):
            return []

        try:
            res = subprocess.run(
                [py_exe, "-m", "pip", "list", "--format=json"],
                capture_output=True,
                text=True,
                timeout=6.0,
            )
            if res.returncode == 0:
                return json.loads(res.stdout)
        except Exception:
            pass

        return []

    def inspect_jupyter_status(self) -> Dict[str, Any]:
        """Checks if Jupyter is available and lists any active notebook/lab servers."""
        jupyter_bin = shutil.which("jupyter")
        status = {
            "installed": bool(jupyter_bin),
            "executable": jupyter_bin,
            "running_servers": [],
        }

        if not jupyter_bin:
            return status

        # Try 'jupyter server list --json' or 'jupyter notebook list --json'
        for subcommand in ["server", "notebook"]:
            try:
                res = subprocess.run(
                    [jupyter_bin, subcommand, "list", "--json"],
                    capture_output=True,
                    text=True,
                    timeout=3.0,
                )
                if res.returncode == 0 and res.stdout.strip():
                    for line in res.stdout.strip().splitlines():
                        try:
                            server_info = json.loads(line)
                            status["running_servers"].append(server_info)
                        except json.JSONDecodeError:
                            continue
                    if status["running_servers"]:
                        break
            except Exception:
                continue

        return status

    def get_jupyter_launch_command(
        self,
        port: int = 8888,
        workspace_dir: Optional[str] = None,
        use_lab: bool = True,
    ) -> List[str]:
        """Generates a command list to launch Jupyter Lab or Notebook."""
        cmd = "jupyter-lab" if (use_lab and shutil.which("jupyter-lab")) else "jupyter"
        target_dir = workspace_dir or self.workspace_path

        if cmd == "jupyter-lab":
            return [cmd, f"--port={port}", f"--notebook-dir={target_dir}", "--no-browser"]
        return ["jupyter", "notebook", f"--port={port}", f"--notebook-dir={target_dir}", "--no-browser"]

    def create_venv(
        self,
        target_path: str,
        with_uv: bool = True,
    ) -> Tuple[bool, str]:
        """Creates a new virtual environment using uv or standard venv."""
        target_path = os.path.abspath(target_path)
        uv_bin = shutil.which("uv") if with_uv else None

        if uv_bin:
            try:
                res = subprocess.run(
                    [uv_bin, "venv", target_path],
                    capture_output=True,
                    text=True,
                    timeout=15.0,
                )
                if res.returncode == 0:
                    return True, f"Virtual environment created with uv at {target_path}"
            except Exception as e:
                pass

        # Fallback to standard python -m venv
        try:
            res = subprocess.run(
                [sys.executable, "-m", "venv", target_path],
                capture_output=True,
                text=True,
                timeout=30.0,
            )
            if res.returncode == 0:
                return True, f"Virtual environment created at {target_path}"
            return False, res.stderr.strip()
        except Exception as e:
            return False, str(e)

    def _is_valid_venv(self, path: str) -> bool:
        if not os.path.isdir(path):
            return False
        cfg = os.path.join(path, "pyvenv.cfg")
        if os.path.isfile(cfg):
            return True
        py_bin = self._get_venv_python(path)
        return bool(py_bin and os.path.exists(py_bin))

    def _get_venv_python(self, venv_path: Optional[str]) -> Optional[str]:
        if not venv_path:
            return None
        # Linux / Unix bin/python
        unix_py = os.path.join(venv_path, "bin", "python")
        if os.path.exists(unix_py):
            return unix_py
        # Windows Scripts/python.exe
        win_py = os.path.join(venv_path, "Scripts", "python.exe")
        if os.path.exists(win_py):
            return win_py
        # Windows conda root python.exe
        win_root = os.path.join(venv_path, "python.exe")
        if os.path.exists(win_root):
            return win_root
        return None

    def _get_env_python_version(self, env_path: str) -> str:
        py_exe = self._get_venv_python(env_path)
        if not py_exe or not os.path.exists(py_exe):
            return "unknown"
        try:
            res = subprocess.run(
                [py_exe, "--version"],
                capture_output=True,
                text=True,
                timeout=2.0,
            )
            if res.returncode == 0:
                return res.stdout.strip().replace("Python ", "")
        except Exception:
            pass
        return "unknown"

    def _inspect_venv(self, path: str, label: str) -> Dict[str, Any]:
        return {
            "name": os.path.basename(path),
            "label": label,
            "type": "venv",
            "path": path,
            "executable": self._get_venv_python(path),
            "version": self._get_env_python_version(path),
        }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Developer Python Environment Manager")
    parser.add_argument("--workspace", "-w", default=".", help="Project workspace path")
    parser.add_argument("--list-envs", action="store_true", help="List detected Python environments")
    parser.add_argument("--packages", action="store_true", help="List packages installed in active/local venv")
    parser.add_argument("--venv-path", help="Path to specific venv to inspect packages")
    parser.add_argument("--jupyter-status", action="store_true", help="Check Jupyter installation and servers")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")

    args = parser.parse_args()
    mgr = PythonManager(args.workspace)

    if args.list_envs:
        envs = mgr.get_all_environments()
        if args.json:
            print(json.dumps(envs, indent=2))
        else:
            print(f"Detected {len(envs)} Python environment(s):")
            for e in envs:
                print(f"  • {e['name']} [{e.get('type', 'venv')}] -> {e.get('path', 'unknown')} (v{e.get('version', '?')})")
        return

    if args.packages:
        pkgs = mgr.list_installed_packages(args.venv_path)
        if args.json:
            print(json.dumps(pkgs, indent=2))
        else:
            print(f"Installed packages ({len(pkgs)}):")
            for p in pkgs[:25]:
                print(f"  {p.get('name', '')}=={p.get('version', '')}")
            if len(pkgs) > 25:
                print(f"  ... and {len(pkgs) - 25} more")
        return

    if args.jupyter_status:
        status = mgr.inspect_jupyter_status()
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            print(f"Jupyter Installed: {status['installed']}")
            if status["installed"]:
                print(f"Jupyter Executable: {status['executable']}")
                print(f"Running Servers: {len(status['running_servers'])}")
        return

    # Default: brief summary
    envs = mgr.get_all_environments()
    j_status = mgr.inspect_jupyter_status()
    out = {
        "workspace": mgr.workspace_path,
        "environments_count": len(envs),
        "environments": envs,
        "jupyter": j_status,
    }
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(f"Python Manager for {mgr.workspace_path}")
        print(f"Environments: {len(envs)} found")
        print(f"Jupyter Available: {j_status['installed']}")


if __name__ == "__main__":
    main()
