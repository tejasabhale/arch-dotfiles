#!/usr/bin/env python3
"""
Power & Battery Manager for HP EliteBook 840 G5.
Interacts with UPower and power-profiles-daemon for energy optimization.
"""

from dataclasses import asdict, dataclass
import json
import os
import subprocess
import sys
from typing import Any, Dict, List


@dataclass
class BatteryStatus:
    capacity_percent: int
    state: str  # "Charging", "Discharging", "Full"
    is_ac_online: bool
    active_profile: str


class PowerManager:

    def get_status(self) -> Dict[str, Any]:
        """Queries battery capacity and AC state via sysfs."""
        capacity = 85
        state = "Discharging"
        ac_online = False

        # Read Battery Capacity
        cap_file = "/sys/class/power_supply/BAT0/capacity"
        if os.path.exists(cap_file):
            try:
                with open(cap_file, "r") as f:
                    capacity = int(f.read().strip())
            except Exception:
                pass

        # Read Battery Status
        stat_file = "/sys/class/power_supply/BAT0/status"
        if os.path.exists(stat_file):
            try:
                with open(stat_file, "r") as f:
                    state = f.read().strip()
            except Exception:
                pass

        # Read AC Adapter
        ac_file = "/sys/class/power_supply/AC/online"
        if os.path.exists(ac_file):
            try:
                with open(ac_file, "r") as f:
                    ac_online = f.read().strip() == "1"
            except Exception:
                pass

        # Read Active Power Profile
        active_prof = "balanced"
        try:
            out = subprocess.check_output(
                ["powerprofilesctl", "get"], stderr=subprocess.DEVNULL, text=True
            )
            active_prof = out.strip()
        except Exception:
            pass

        return asdict(
            BatteryStatus(
                capacity_percent=capacity,
                state=state,
                is_ac_online=ac_online,
                active_profile=active_prof,
            )
        )

    def set_profile(self, profile: str) -> bool:
        """Sets power profile: 'power-saver', 'balanced', or 'performance'."""
        if profile not in ["power-saver", "balanced", "performance"]:
            return False
        try:
            subprocess.run(["powerprofilesctl", "set", profile], check=True)
            return True
        except Exception:
            return False


def main():
    pm = PowerManager()
    if len(sys.argv) < 2 or sys.argv[1] == "status":
        print(json.dumps(pm.get_status(), indent=2))
    elif sys.argv[1] == "set" and len(sys.argv) > 2:
        res = pm.set_profile(sys.argv[2])
        print(json.dumps({"success": res, "profile": sys.argv[2]}, indent=2))


if __name__ == "__main__":
    main()
