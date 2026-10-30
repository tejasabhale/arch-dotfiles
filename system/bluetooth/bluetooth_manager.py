#!/usr/bin/env python3
"""
Bluetooth Subsystem Backend Service via BlueZ / bluetoothctl.
Handles scanning, pairing, connection, and disconnection of devices.
"""

from dataclasses import asdict, dataclass
import json
import re
import subprocess
import sys
from typing import Any, Dict, List


@dataclass
class BluetoothDevice:
    mac: str
    name: str
    is_connected: bool
    is_paired: bool
    icon_glyph: str


class BluetoothManager:

    def get_devices(self) -> List[Dict[str, Any]]:
        """Queries paired and discovered Bluetooth devices via bluetoothctl."""
        devices: List[Dict[str, Any]] = []
        try:
            out = subprocess.check_output(
                ["bluetoothctl", "devices"], stderr=subprocess.DEVNULL, text=True
            )
            paired_out = subprocess.check_output(
                ["bluetoothctl", "paired-devices"],
                stderr=subprocess.DEVNULL,
                text=True,
            )
            paired_macs = {
                line.split()[1] for line in paired_out.splitlines() if len(line.split()) >= 2
            }

            for line in out.splitlines():
                parts = line.split(maxsplit=2)
                if len(parts) >= 3 and parts[0] == "Device":
                    mac = parts[1]
                    name = parts[2]
                    is_paired = mac in paired_macs

                    # Infer device type from name
                    lower_name = name.lower()
                    if any(
                        k in lower_name
                        for k in ["audio", "headset", "earbuds", "headphones", "buds"]
                    ):
                        icon = "󰋋"
                    elif any(k in lower_name for k in ["mouse", "touchpad"]):
                        icon = "󰍽"
                    elif any(k in lower_name for k in ["keyboard", "keychron"]):
                        icon = "󰌌"
                    elif any(k in lower_name for k in ["phone", "galaxy", "iphone"]):
                        icon = "󰄡"
                    else:
                        icon = "󰂯"

                    devices.append(
                        asdict(
                            BluetoothDevice(
                                mac=mac,
                                name=name,
                                is_connected=False,
                                is_paired=is_paired,
                                icon_glyph=icon,
                            )
                        )
                    )
        except Exception:
            pass

        return devices

    def connect(self, mac: str) -> Dict[str, Any]:
        """Connects to a Bluetooth MAC address."""
        try:
            proc = subprocess.run(
                ["bluetoothctl", "connect", mac],
                capture_output=True,
                text=True,
                check=True,
            )
            return {"success": True, "message": proc.stdout.strip()}
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": e.stderr.strip() or str(e)}

    def disconnect(self, mac: str) -> Dict[str, Any]:
        """Disconnects a Bluetooth device."""
        try:
            proc = subprocess.run(
                ["bluetoothctl", "disconnect", mac],
                capture_output=True,
                text=True,
                check=True,
            )
            return {"success": True, "message": proc.stdout.strip()}
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": str(e)}

    def toggle_power(self, power_on: bool) -> Dict[str, Any]:
        """Turns Bluetooth controller power on or off."""
        state = "on" if power_on else "off"
        try:
            subprocess.run(
                ["bluetoothctl", "power", state], capture_output=True, check=True
            )
            return {"success": True, "powered": power_on}
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": str(e)}


def main():
    bm = BluetoothManager()
    if len(sys.argv) < 2:
        print("Usage: bluetooth_manager.py [list|connect <mac>|disconnect <mac>|power <on|off>]")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "list":
        print(json.dumps(bm.get_devices(), indent=2))
    elif cmd == "connect":
        if len(sys.argv) < 3:
            sys.exit(1)
        print(json.dumps(bm.connect(sys.argv[2]), indent=2))
    elif cmd == "disconnect":
        if len(sys.argv) < 3:
            sys.exit(1)
        print(json.dumps(bm.disconnect(sys.argv[2]), indent=2))
    elif cmd == "power":
        power_on = sys.argv[2] == "on" if len(sys.argv) > 2 else True
        print(json.dumps(bm.toggle_power(power_on), indent=2))
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
