#!/usr/bin/env python3
"""
Developer SSH Connection Shortcuts & Config Inspector.
Parses ~/.ssh/config, extracts host aliases, generates terminal commands,
and checks remote host reachability.
"""

import json
import os
import re
import shutil
import socket
import subprocess
import sys
from typing import Any, Dict, List, Optional, Tuple


class SSHManager:
    """Manages SSH bookmarks, config parsing, and terminal connection commands."""

    DEFAULT_CONFIG_PATH = os.path.expanduser("~/.ssh/config")

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH

    def list_hosts(self) -> List[Dict[str, Any]]:
        """Parses ~/.ssh/config and returns a list of configured host shortcuts."""
        if not os.path.isfile(self.config_path):
            return []

        hosts: List[Dict[str, Any]] = []
        global_defaults: Dict[str, Any] = {}
        current_host: Optional[Dict[str, Any]] = None

        try:
            with open(self.config_path, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue

                    # Match keyword and value
                    parts = re.split(r"\s+|=|\t+", line, maxsplit=1)
                    if len(parts) < 2:
                        continue

                    key = parts[0].strip().lower()
                    val = parts[1].strip().strip('"')

                    if key == "host":
                        # If we have an existing host entry, save it
                        if current_host:
                            if current_host["alias"] == "*":
                                global_defaults.update(current_host)
                            else:
                                hosts.append(current_host)

                        # New host block
                        current_host = {
                            "alias": val,
                            "hostname": val,
                            "user": global_defaults.get("user", os.environ.get("USER", "root")),
                            "port": int(global_defaults.get("port", 22)),
                            "identity_file": global_defaults.get("identity_file", None),
                        }
                    elif current_host:
                        if key == "hostname":
                            current_host["hostname"] = val
                        elif key == "user":
                            current_host["user"] = val
                        elif key == "port":
                            try:
                                current_host["port"] = int(val)
                            except ValueError:
                                pass
                        elif key == "identityfile":
                            current_host["identity_file"] = os.path.expanduser(val)

            # Append the last host
            if current_host:
                if current_host["alias"] == "*":
                    global_defaults.update(current_host)
                else:
                    hosts.append(current_host)

        except Exception:
            return []

        # Filter out patterns or wildcards
        valid_hosts = []
        for h in hosts:
            if "*" in h["alias"] or "?" in h["alias"]:
                continue
            # Build connection string and launch command
            h["connection_string"] = f"ssh {h['alias']}"
            h["terminal_command"] = f"kitty --title 'SSH: {h['alias']}' ssh {h['alias']}"
            valid_hosts.append(h)

        return valid_hosts

    def test_reachability(self, host_alias_or_name: str, timeout: float = 1.0) -> Dict[str, Any]:
        """Performs a quick TCP socket connection check to test if the SSH port is reachable."""
        hosts = self.list_hosts()
        target = next((h for h in hosts if h["alias"] == host_alias_or_name), None)

        hostname = target["hostname"] if target else host_alias_or_name
        port = target["port"] if target else 22

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)

        try:
            s.connect((hostname, port))
            s.close()
            return {
                "host": host_alias_or_name,
                "hostname": hostname,
                "port": port,
                "reachable": True,
                "error": None,
            }
        except socket.timeout:
            return {
                "host": host_alias_or_name,
                "hostname": hostname,
                "port": port,
                "reachable": False,
                "error": "Connection timed out",
            }
        except Exception as e:
            return {
                "host": host_alias_or_name,
                "hostname": hostname,
                "port": port,
                "reachable": False,
                "error": str(e),
            }

    def get_launch_command(self, host_alias: str, terminal: str = "kitty") -> List[str]:
        """Returns the process argument list to open an interactive SSH session in a terminal."""
        if terminal == "kitty":
            return ["kitty", "--title", f"SSH: {host_alias}", "ssh", host_alias]
        return ["ssh", host_alias]

    def add_host_entry(
        self,
        alias: str,
        hostname: str,
        user: Optional[str] = None,
        port: int = 22,
        identity_file: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """Safely appends a new host entry to ~/.ssh/config."""
        try:
            os.makedirs(os.path.dirname(self.config_path), mode=0o700, exist_ok=True)

            # Backup existing
            if os.path.exists(self.config_path):
                shutil.copy2(self.config_path, f"{self.config_path}.bak")

            entry_lines = [
                f"\nHost {alias}",
                f"    HostName {hostname}",
                f"    Port {port}",
            ]
            if user:
                entry_lines.append(f"    User {user}")
            if identity_file:
                entry_lines.append(f"    IdentityFile {identity_file}")

            entry_lines.append("")

            with open(self.config_path, "a", encoding="utf-8") as f:
                f.write("\n".join(entry_lines))

            # Set correct permissions on Linux
            if sys.platform.startswith("linux"):
                os.chmod(self.config_path, 0o600)

            return True, f"Host '{alias}' successfully added to {self.config_path}"
        except Exception as e:
            return False, f"Failed to add host entry: {e}"


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Developer SSH Connection Shortcuts")
    parser.add_argument("--list", action="store_true", help="List configured SSH hosts")
    parser.add_argument("--test", help="Test reachability for a host alias")
    parser.add_argument("--launch", help="Print launch command for host")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")

    args = parser.parse_args()
    mgr = SSHManager()

    if args.test:
        res = mgr.test_reachability(args.test)
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            status = "ONLINE" if res["reachable"] else "OFFLINE"
            print(f"[{status}] {res['host']} ({res['hostname']}:{res['port']})")
            if res["error"]:
                print(f"  Error: {res['error']}")
        return

    if args.launch:
        cmd = mgr.get_launch_command(args.launch)
        print(" ".join(cmd))
        return

    hosts = mgr.list_hosts()
    if args.json:
        print(json.dumps(hosts, indent=2))
    else:
        print(f"Configured SSH Hosts ({len(hosts)}):")
        print(f"{'ALIAS':<18} {'USER':<12} {'HOSTNAME':<25} {'PORT'}")
        print("-" * 65)
        for h in hosts:
            print(f"{h['alias']:<18} {h.get('user', '-'):<12} {h['hostname']:<25} {h['port']}")


if __name__ == "__main__":
    main()
