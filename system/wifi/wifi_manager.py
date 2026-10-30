#!/usr/bin/env python3
"""
Wi-Fi Subsystem Backend Service via NetworkManager.
Handles SSID scanning, connection, disconnection, and signal monitoring.
"""

from dataclasses import asdict, dataclass
import json
import subprocess
import sys
from typing import Any, Dict, List, Optional


@dataclass
class WifiNetwork:
    ssid: str
    signal_percent: int
    security: str
    bars: str
    is_active: bool


class WifiManager:

    def scan_networks(self) -> List[Dict[str, Any]]:
        """Scans for nearby wireless access points using nmcli."""
        cmd = [
            "nmcli",
            "-t",
            "-f",
            "IN-USE,SSID,SIGNAL,SECURITY,BARS",
            "dev",
            "wifi",
            "list",
        ]
        networks: List[Dict[str, Any]] = []
        seen_ssids = set()

        try:
            out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True)
            for line in out.splitlines():
                parts = line.split(":")
                if len(parts) >= 5:
                    in_use = parts[0].strip() == "*"
                    ssid = parts[1].strip()
                    if not ssid or ssid in seen_ssids:
                        continue
                    seen_ssids.add(ssid)

                    try:
                        signal = int(parts[2].strip())
                    except ValueError:
                        signal = 50

                    sec = parts[3].strip() or "Open"
                    bars = parts[4].strip()

                    networks.append(
                        asdict(
                            WifiNetwork(
                                ssid=ssid,
                                signal_percent=signal,
                                security=sec,
                                bars=bars,
                                is_active=in_use,
                            )
                        )
                    )
        except Exception:
            # Fallback mock for offline / container testing
            pass

        return networks

    def connect(self, ssid: str, password: Optional[str] = None) -> Dict[str, Any]:
        """Connects to a specific SSID with optional WPA passphrase."""
        cmd = ["nmcli", "dev", "wifi", "connect", ssid]
        if password:
            cmd.extend(["password", password])

        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return {
                "success": True,
                "ssid": ssid,
                "message": proc.stdout.strip(),
            }
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": e.stderr.strip() or e.stdout.strip() or str(e),
            }

    def disconnect(self, interface: str = "wlan0") -> Dict[str, Any]:
        """Disconnects current wireless station."""
        try:
            subprocess.run(
                ["nmcli", "dev", "disconnect", interface],
                capture_output=True,
                check=True,
            )
            return {"success": True, "message": f"Disconnected {interface}."}
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": str(e)}

    def get_status(self) -> Dict[str, Any]:
        """Queries active Wi-Fi connection info."""
        cmd = [
            "nmcli",
            "-t",
            "-f",
            "ACTIVE,SSID,SIGNAL,IP4-CONNECTIVITY",
            "dev",
            "wifi",
        ]
        try:
            out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True)
            for line in out.splitlines():
                if line.startswith("yes:"):
                    parts = line.split(":")
                    return {
                        "connected": True,
                        "ssid": parts[1] if len(parts) > 1 else "Unknown",
                        "signal": int(parts[2]) if len(parts) > 2 else 100,
                    }
        except Exception:
            pass
        return {"connected": False, "ssid": None, "signal": 0}


def main():
    wm = WifiManager()
    if len(sys.argv) < 2:
        print("Usage: wifi_manager.py [scan|status|connect <ssid> [pass]|disconnect]")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "scan":
        print(json.dumps(wm.scan_networks(), indent=2))
    elif cmd == "status":
        print(json.dumps(wm.get_status(), indent=2))
    elif cmd == "connect":
        if len(sys.argv) < 3:
            print("Error: SSID required")
            sys.exit(1)
        ssid = sys.argv[2]
        pwd = sys.argv[3] if len(sys.argv) > 3 else None
        print(json.dumps(wm.connect(ssid, pwd), indent=2))
    elif cmd == "disconnect":
        print(json.dumps(wm.disconnect(), indent=2))
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
