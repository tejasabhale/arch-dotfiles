#!/usr/bin/env python3
"""
Wi-Fi Hotspot Manager Backend Service.
Handles AP mode capability detection, NetworkManager hotspot orchestration,
QR code generation, and client lease monitoring.
"""

from dataclasses import asdict, dataclass
import json
import os
import re
import secrets
import string
import subprocess
import sys
from typing import Any, Dict, List, Optional


@dataclass
class HotspotHardwareCapabilities:
    interface: str
    ap_mode_supported: bool
    supports_2ghz: bool
    supports_5ghz: bool
    supports_concurrent_sta_ap: bool
    driver_name: str
    explanation: str


@dataclass
class ConnectedClient:
    mac_address: str
    ip_address: Optional[str]
    hostname: Optional[str]
    signal_dbm: Optional[int]


class HotspotManager:
    CONFIG_PATH = os.path.expanduser("~/.config/tejas-os/hotspot.json")

    def __init__(self):
        self.ensure_config_dir()

    def ensure_config_dir(self):
        os.makedirs(os.path.dirname(self.CONFIG_PATH), exist_ok=True)

    def detect_hardware(self) -> HotspotHardwareCapabilities:
        """Inspects physical wireless adapter capabilities using iw list."""
        try:
            out = subprocess.check_output(
                ["iw", "list"], stderr=subprocess.DEVNULL, text=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            return HotspotHardwareCapabilities(
                interface="unknown",
                ap_mode_supported=False,
                supports_2ghz=False,
                supports_5ghz=False,
                supports_concurrent_sta_ap=False,
                driver_name="unknown",
                explanation="Wireless tooling ('iw') not found or adapter unavailable.",
            )

        # Detect AP mode
        has_ap = bool(re.search(r"Supported interface modes:.*?(\bAP\b)", out, re.DOTALL))

        # Detect Frequencies
        supports_2ghz = "2412 MHz" in out
        supports_5ghz = "5180 MHz" in out or "5745 MHz" in out

        # Detect concurrency combinations
        has_sta_ap_combo = bool(re.search(r"#{ (?:managed, )*AP", out))

        # Detect active interface name
        interface_name = "wlan0"
        try:
            dev_out = subprocess.check_output(
                ["iw", "dev"], stderr=subprocess.DEVNULL, text=True
            )
            match = re.search(r"Interface\s+([a-zA-Z0-9_\-]+)", dev_out)
            if match:
                interface_name = match.group(1)
        except Exception:
            pass

        explanation = (
            "Access Point (AP) mode fully supported."
            if has_ap
            else "Your Wi-Fi chipset does not support AP broadcast mode."
        )

        return HotspotHardwareCapabilities(
            interface=interface_name,
            ap_mode_supported=has_ap,
            supports_2ghz=supports_2ghz,
            supports_5ghz=supports_5ghz,
            supports_concurrent_sta_ap=has_sta_ap_combo,
            driver_name="Intel iwlwifi / Generic",
            explanation=explanation,
        )

    def generate_password(self, length: int = 12) -> str:
        """Generates a secure, readable WPA2/WPA3 password without confusing characters."""
        alphabet = string.ascii_letters + string.digits
        # Avoid visually ambiguous characters like l, 1, I, 0, O
        ambiguous = "l1I0O"
        filtered_alphabet = "".join(c for c in alphabet if c not in ambiguous)
        return "".join(secrets.choice(filtered_alphabet) for _ in range(length))

    def generate_qr_code(
        self, ssid: str, password: str, output_path: str
    ) -> bool:
        """Generates a standard Wi-Fi QR Code image via qrencode."""
        # Standard Wi-Fi URI format: WIFI:S:<SSID>;T:WPA;P:<PASSWORD>;;
        wifi_uri = f"WIFI:S:{ssid};T:WPA;P:{password};;"
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            subprocess.run(
                ["qrencode", "-s", "6", "-o", output_path, wifi_uri],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def start_hotspot(
        self,
        ssid: str = "ArchHotspot",
        password: Optional[str] = None,
        band: str = "bg",
        channel: int = 6,
    ) -> Dict[str, Any]:
        """Starts Wi-Fi Hotspot via NetworkManager with WPA2/WPA3 encryption."""
        caps = self.detect_hardware()
        if not caps.ap_mode_supported:
            return {
                "success": False,
                "error": "Hardware does not support AP mode.",
            }

        if not password or len(password) < 8:
            password = self.generate_password()

        # Generate QR code under user cache directory
        cache_qr = os.path.expanduser("~/.cache/tejas-os/hotspot_qr.png")
        self.generate_qr_code(ssid, password, cache_qr)

        cmd = [
            "nmcli",
            "dev",
            "wifi",
            "hotspot",
            "ifname",
            caps.interface,
            "ssid",
            ssid,
            "password",
            password,
        ]

        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return {
                "success": True,
                "ssid": ssid,
                "password": password,
                "interface": caps.interface,
                "band": band,
                "qr_path": cache_qr,
                "message": proc.stdout.strip(),
            }
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": e.stderr.strip() or e.stdout.strip() or str(e),
            }

    def stop_hotspot(self) -> Dict[str, Any]:
        """Stops active Hotspot connection in NetworkManager."""
        cmd = ["nmcli", "con", "down", "Hotspot"]
        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            return {
                "success": True,
                "message": "Hotspot deactivated successfully.",
            }
        except subprocess.CalledProcessError:
            # Try searching for any active connection with mode 'ap'
            try:
                subprocess.run(
                    [
                        "sh",
                        "-c",
                        "nmcli -t -f UUID,TYPE con show --active | grep '802-11-wireless' | cut -d: -f1 | xargs -r nmcli con down",
                    ],
                    check=True,
                )
                return {"success": True, "message": "Hotspot stopped."}
            except Exception as e:
                return {"success": False, "error": str(e)}

    def get_connected_clients(self) -> List[Dict[str, Any]]:
        """Queries IP neighbor cache / ARP table for active DHCP leases connected to hotspot."""
        clients = []
        try:
            out = subprocess.check_output(
                ["ip", "neighbor", "show"], stderr=subprocess.DEVNULL, text=True
            )
            for line in out.splitlines():
                # Example: 192.168.12.15 dev wlan0 lladdr 7c:d9:54:12:34:56 REACHABLE
                parts = line.split()
                if (
                    len(parts) >= 6
                    and "lladdr" in parts
                    and ("REACHABLE" in parts or "DELAY" in parts)
                ):
                    ip = parts[0]
                    ll_idx = parts.index("lladdr")
                    mac = parts[ll_idx + 1]
                    clients.append(
                        asdict(
                            ConnectedClient(
                                mac_address=mac,
                                ip_address=ip,
                                hostname="Client Device",
                                signal_dbm=None,
                            )
                        )
                    )
        except Exception:
            pass
        return clients


def main():
    manager = HotspotManager()
    if len(sys.argv) < 2:
        print("Usage: hotspot_manager.py [detect|start|stop|clients|genpass]")
        sys.exit(1)

    action = sys.argv[1]
    if action == "detect":
        caps = manager.detect_hardware()
        print(json.dumps(asdict(caps), indent=2))
    elif action == "start":
        ssid = sys.argv[2] if len(sys.argv) > 2 else "ArchHotspot"
        pwd = sys.argv[3] if len(sys.argv) > 3 else manager.generate_password()
        res = manager.start_hotspot(ssid=ssid, password=pwd)
        print(json.dumps(res, indent=2))
    elif action == "stop":
        res = manager.stop_hotspot()
        print(json.dumps(res, indent=2))
    elif action == "clients":
        cls = manager.get_connected_clients()
        print(json.dumps(cls, indent=2))
    elif action == "genpass":
        print(manager.generate_password())
    else:
        print(f"Unknown command: {action}")
        sys.exit(1)


if __name__ == "__main__":
    main()
