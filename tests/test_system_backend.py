"""
Unit tests for system subsystem backend services (Hotspot, Wi-Fi, Bluetooth, Audio, Power).
"""

import json
import unittest
from unittest.mock import MagicMock, patch

from system.audio.audio_manager import AudioManager
from system.bluetooth.bluetooth_manager import BluetoothManager
from system.hotspot.hotspot_manager import HotspotManager
from system.power.power_manager import PowerManager
from system.power.profile_daemon import PerformanceProfileDaemon
from system.wifi.wifi_manager import WifiManager


class TestSystemBackends(unittest.TestCase):

    def test_hotspot_password_generator(self):
        hm = HotspotManager()
        pwd = hm.generate_password(length=14)
        self.assertEqual(len(pwd), 14)
        # Ensure no ambiguous characters
        for char in "l1I0O":
            self.assertNotIn(char, pwd)

    def test_hotspot_detect_hardware_fallback(self):
        hm = HotspotManager()
        # When iw is not present on Windows, it returns clean fallback dataclass
        caps = hm.detect_hardware()
        self.assertIsInstance(caps.ap_mode_supported, bool)
        self.assertIsInstance(caps.interface, str)

    def test_wifi_scan_fallback(self):
        wm = WifiManager()
        nets = wm.scan_networks()
        self.assertIsInstance(nets, list)

    def test_bluetooth_device_listing(self):
        bm = BluetoothManager()
        devices = bm.get_devices()
        self.assertIsInstance(devices, list)

    def test_audio_status_fallback(self):
        am = AudioManager()
        status = am.get_status()
        self.assertIn("volume", status)
        self.assertIn("muted", status)

    def test_power_status_fallback(self):
        pm = PowerManager()
        status = pm.get_status()
        self.assertIn("capacity_percent", status)
        self.assertIn("state", status)
        self.assertIn("active_profile", status)

    def test_performance_profile_daemon(self):
        daemon = PerformanceProfileDaemon()
        mem = daemon.get_memory_usage()
        self.assertIn("total_mb", mem)
        self.assertIn("used_mb", mem)
        self.assertIn("within_budget", mem)
        self.assertTrue(mem["within_budget"])


if __name__ == "__main__":
    unittest.main()
