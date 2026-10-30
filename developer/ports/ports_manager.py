#!/usr/bin/env python3
"""
Developer Listening Ports Inspector.
Inspects active TCP/UDP listening sockets, identifies well-known dev services
(Vite, Next.js, Django, Ollama, Jupyter, June IPC), and provides safe process management.
"""

import json
import os
import re
import shutil
import signal
import subprocess
import sys
from typing import Any, Dict, List, Optional, Tuple


class PortsManager:
    """Monitors and inspects network sockets currently listening on the local machine."""

    KNOWN_DEV_PORTS = {
        3000: "React / Next.js / Node",
        3001: "Dev Server Alt",
        4000: "GraphQL / Hexo / Dev",
        5000: "Flask / ASP.NET",
        5173: "Vite / Svelte / Vue",
        8000: "FastAPI / Django / Python HTTP",
        8080: "Tomcat / Web Server Alt",
        8888: "Jupyter Notebook / Lab",
        5432: "PostgreSQL Database",
        3306: "MySQL / MariaDB",
        6379: "Redis Cache",
        27017: "MongoDB",
        9000: "SonarQube / PHP-FPM / MinIO",
        11434: "Ollama LLM Daemon",
        42421: "June AI IPC Daemon",
    }

    PROTECTED_PIDS = {0, 1, 2, 3, 4}  # Init, kernel, system idle, etc.
    PROTECTED_PROCESS_NAMES = {
        "systemd", "init", "launchd", "kernel", "kthreadd",
        "system", "services.exe", "lsass.exe", "csrss.exe", "smss.exe",
    }

    def __init__(self):
        pass

    def get_known_service_name(self, port: int) -> str:
        """Returns the description for well-known developer ports."""
        return self.KNOWN_DEV_PORTS.get(port, "Custom Service")

    def list_listening_ports(self) -> List[Dict[str, Any]]:
        """Scans and returns active listening ports."""
        if sys.platform.startswith("linux"):
            ports = self._scan_linux_ss()
            if not ports:
                ports = self._scan_linux_lsof()
            return ports
        elif sys.platform == "win32":
            return self._scan_windows_netstat()
        else:
            # Fallback for macOS or generic BSD
            return self._scan_linux_lsof()

    def _scan_linux_ss(self) -> List[Dict[str, Any]]:
        """Parses output from `ss -tulnp` on Linux."""
        ss_bin = shutil.which("ss")
        if not ss_bin:
            return []

        try:
            res = subprocess.run(
                [ss_bin, "-tulnp"],
                capture_output=True,
                text=True,
                timeout=4.0,
            )
            if res.returncode != 0:
                return []
            return self.parse_ss_output(res.stdout)
        except Exception:
            return []

    def parse_ss_output(self, raw_output: str) -> List[Dict[str, Any]]:
        """Parses ss -tulnp formatted table output."""
        results = []
        lines = raw_output.strip().splitlines()

        for line in lines:
            line = line.strip()
            if not line or line.startswith("Netid") or line.startswith("State"):
                continue

            parts = line.split()
            if len(parts) < 5:
                continue

            proto = parts[0].upper()
            state = parts[1].upper()

            if "LISTEN" not in state and "UNCONN" not in state:
                continue

            # Local address:port is usually column 4 (0-indexed)
            local_addr_str = parts[4]
            port = None
            host = ""

            # Format can be *:8080, 0.0.0.0:8000, 127.0.0.1:5173, [::]:3000
            if ":" in local_addr_str:
                r_idx = local_addr_str.rfind(":")
                host = local_addr_str[:r_idx].strip("[]")
                try:
                    port = int(local_addr_str[r_idx + 1:])
                except ValueError:
                    continue

            if port is None:
                continue

            # Process info: users:(("process_name",pid=1234,fd=3))
            pid = None
            proc_name = "unknown"
            if len(parts) >= 6:
                proc_str = " ".join(parts[5:])
                p_match = re.search(r'users:\(\("([^"]+)",pid=(\d+)', proc_str)
                if p_match:
                    proc_name = p_match.group(1)
                    try:
                        pid = int(p_match.group(2))
                    except ValueError:
                        pass

            results.append({
                "protocol": proto,
                "host": host or "0.0.0.0",
                "port": port,
                "pid": pid,
                "process": proc_name,
                "service": self.get_known_service_name(port),
            })

        # Deduplicate by protocol and port
        deduped = []
        seen = set()
        for r in results:
            key = (r["protocol"], r["port"])
            if key not in seen:
                seen.add(key)
                deduped.append(r)

        return sorted(deduped, key=lambda x: x["port"])

    def _scan_linux_lsof(self) -> List[Dict[str, Any]]:
        """Parses output from `lsof -iTCP -sTCP:LISTEN -n -P`."""
        lsof_bin = shutil.which("lsof")
        if not lsof_bin:
            return []

        try:
            res = subprocess.run(
                [lsof_bin, "-iTCP", "-sTCP:LISTEN", "-n", "-P"],
                capture_output=True,
                text=True,
                timeout=4.0,
            )
            if res.returncode != 0:
                return []
            return self.parse_lsof_output(res.stdout)
        except Exception:
            return []

    def parse_lsof_output(self, raw_output: str) -> List[Dict[str, Any]]:
        """Parses lsof table output."""
        results = []
        lines = raw_output.strip().splitlines()

        for line in lines:
            line = line.strip()
            if not line or line.startswith("COMMAND"):
                continue

            parts = line.split()
            if len(parts) < 9:
                continue

            proc_name = parts[0]
            try:
                pid = int(parts[1])
            except ValueError:
                pid = None

            proto = parts[7].upper()
            addr_info = parts[8]

            if ":" in addr_info:
                r_idx = addr_info.rfind(":")
                host = addr_info[:r_idx].strip("[]")
                try:
                    port = int(addr_info[r_idx + 1:])
                    results.append({
                        "protocol": proto,
                        "host": host or "0.0.0.0",
                        "port": port,
                        "pid": pid,
                        "process": proc_name,
                        "service": self.get_known_service_name(port),
                    })
                except ValueError:
                    continue

        return results

    def _scan_windows_netstat(self) -> List[Dict[str, Any]]:
        """Parses output from `netstat -ano -p tcp` on Windows."""
        try:
            res = subprocess.run(
                ["netstat", "-ano", "-p", "tcp"],
                capture_output=True,
                text=True,
                timeout=5.0,
            )
            if res.returncode != 0:
                return []
            return self.parse_windows_netstat(res.stdout)
        except Exception:
            return []

    def parse_windows_netstat(self, raw_output: str) -> List[Dict[str, Any]]:
        """Parses Windows netstat output."""
        results = []
        lines = raw_output.strip().splitlines()

        for line in lines:
            line = line.strip()
            if not line or not line.startswith("TCP"):
                continue

            parts = line.split()
            if len(parts) < 5:
                continue

            proto = parts[0]
            local_addr = parts[1]
            state = parts[3]
            pid_str = parts[4]

            if state != "LISTENING":
                continue

            if ":" in local_addr:
                r_idx = local_addr.rfind(":")
                host = local_addr[:r_idx].strip("[]")
                try:
                    port = int(local_addr[r_idx + 1:])
                    pid = int(pid_str) if pid_str.isdigit() else None
                    proc_name = self._resolve_pid_name(pid) if pid else "unknown"

                    results.append({
                        "protocol": proto,
                        "host": host or "0.0.0.0",
                        "port": port,
                        "pid": pid,
                        "process": proc_name,
                        "service": self.get_known_service_name(port),
                    })
                except ValueError:
                    continue

        # Deduplicate
        deduped = []
        seen = set()
        for r in results:
            if r["port"] not in seen:
                seen.add(r["port"])
                deduped.append(r)

        return sorted(deduped, key=lambda x: x["port"])

    def _resolve_pid_name(self, pid: int) -> str:
        """Attempts to resolve process name from PID."""
        if sys.platform == "win32":
            try:
                res = subprocess.run(
                    ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
                    capture_output=True,
                    text=True,
                    timeout=2.0,
                )
                if res.returncode == 0 and res.stdout.strip():
                    parts = res.stdout.strip().replace('"', '').split(",")
                    if parts and parts[0]:
                        return parts[0]
            except Exception:
                pass
        elif sys.platform.startswith("linux"):
            try:
                with open(f"/proc/{pid}/comm", "r") as f:
                    return f.read().strip()
            except Exception:
                pass
        return "unknown"

    def kill_port(self, port: int, force: bool = False) -> Tuple[bool, str]:
        """
        Safely terminates the process listening on the specified port.
        Protects system processes and PID 0-4.
        """
        ports = self.list_listening_ports()
        target = next((p for p in ports if p["port"] == port), None)

        if not target:
            return False, f"No active listening service found on port {port}"

        pid = target.get("pid")
        proc_name = target.get("process", "unknown").lower()

        if not pid:
            return False, f"Could not determine process ID for port {port} (permission required)"

        # SAFETY CHECKS
        if pid in self.PROTECTED_PIDS or pid <= 100:
            return False, f"Refusing to kill critical system PID {pid}"

        if any(protected in proc_name for protected in self.PROTECTED_PROCESS_NAMES):
            return False, f"Refusing to kill protected system daemon '{proc_name}' (PID {pid})"

        # Execution
        if sys.platform == "win32":
            args = ["taskkill", "/PID", str(pid)]
            if force:
                args.append("/F")
            try:
                res = subprocess.run(args, capture_output=True, text=True, timeout=5.0)
                if res.returncode == 0:
                    return True, f"Successfully terminated {proc_name} (PID {pid}) on port {port}"
                return False, res.stderr.strip() or res.stdout.strip()
            except Exception as e:
                return False, str(e)
        else:
            # Unix / Linux
            try:
                sig = signal.SIGKILL if force else signal.SIGTERM
                os.kill(pid, sig)
                return True, f"Sent signal {sig.name} to {proc_name} (PID {pid}) on port {port}"
            except ProcessLookupError:
                return True, f"Process {pid} already terminated"
            except PermissionError:
                return False, f"Insufficient permissions to terminate PID {pid}"
            except Exception as e:
                return False, str(e)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Developer Listening Ports Inspector")
    parser.add_argument("--list", action="store_true", help="List all active listening ports")
    parser.add_argument("--kill", type=int, help="Kill process listening on specified port")
    parser.add_argument("--force", action="store_true", help="Force terminate process (SIGKILL / /F)")
    parser.add_argument("--filter", help="Filter by port or process name")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")

    args = parser.parse_args()
    mgr = PortsManager()

    if args.kill:
        ok, msg = mgr.kill_port(args.kill, force=args.force)
        if args.json:
            print(json.dumps({"success": ok, "message": msg}, indent=2))
        else:
            status = "SUCCESS" if ok else "FAILED"
            print(f"[{status}] {msg}")
        sys.exit(0 if ok else 1)

    ports = mgr.list_listening_ports()

    if args.filter:
        filt = args.filter.lower()
        ports = [
            p for p in ports
            if filt in str(p["port"]) or filt in p["process"].lower() or filt in p["service"].lower()
        ]

    if args.json:
        print(json.dumps(ports, indent=2))
    else:
        print(f"Active Listening Ports ({len(ports)}):")
        print(f"{'PORT':<8} {'PROTO':<6} {'PID':<8} {'PROCESS':<18} {'SERVICE'}")
        print("-" * 65)
        for p in ports:
            pid_str = str(p['pid']) if p['pid'] else "-"
            print(f"{p['port']:<8} {p['protocol']:<6} {pid_str:<8} {p['process']:<18} {p['service']}")


if __name__ == "__main__":
    main()
