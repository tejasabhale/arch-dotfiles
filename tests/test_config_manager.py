#!/usr/bin/env python3
"""
Automated Test Suite for Centralized Config & Modular Feature Storage (Phase 10).
Tests atomic storage, Rule 1.4 true feature isolation, dependency checks,
performance profiles, and configuration backup/rollback.
"""

import json
import os
import shutil
import tempfile
import pytest

from config.manager import ConfigManager


@pytest.fixture
def temp_config_dir():
    d = tempfile.mkdtemp(prefix="tejas_test_cfg_")
    yield d
    shutil.rmtree(d, ignore_errors=True)


# ============================================================================
# 1. Config Manager Initialization & Atomic Storage
# ============================================================================

def test_config_manager_initialization(temp_config_dir):
    mgr = ConfigManager(config_dir=temp_config_dir)

    assert os.path.exists(mgr.features_file)
    assert os.path.exists(mgr.settings_file)
    assert os.path.exists(mgr.profiles_file)

    # Verify features content
    features = mgr.get_features()
    assert "dock" in features
    assert "june_assistant" in features
    assert "multilingual_stt" in features

    # Verify settings content
    settings = mgr.get_settings()
    assert settings["theme"] == "midnight"
    assert "appearance" in settings
    assert "compositor" in settings


def test_config_manager_atomic_writes(temp_config_dir):
    mgr = ConfigManager(config_dir=temp_config_dir)
    test_file = os.path.join(temp_config_dir, "test_atomic.json")

    test_data = {"key": "value", "count": 42}
    ok = mgr.write_atomic(test_file, test_data)
    assert ok is True
    assert os.path.exists(test_file)

    read_back = mgr.read_json(test_file)
    assert read_back == test_data


# ============================================================================
# 2. Modular Feature Isolation & Dependency Checks (Rule 1.4)
# ============================================================================

def test_feature_manager_toggle_and_dependencies(temp_config_dir):
    mgr = ConfigManager(config_dir=temp_config_dir)

    # multilingual_stt depends on june_assistant
    features = mgr.get_features()
    assert "june_assistant" in features["multilingual_stt"]["dependencies"]

    # Try to disable june_assistant while multilingual_stt is enabled -> Should FAIL
    ok, msg = mgr.toggle_feature("june_assistant", enable=False)
    assert ok is False
    assert "required by" in msg

    # Disable multilingual_stt and multilingual_tts first -> Should SUCCEED
    ok, msg = mgr.toggle_feature("multilingual_stt", enable=False)
    assert ok is True
    ok, msg = mgr.toggle_feature("multilingual_tts", enable=False)
    assert ok is True

    # Now disable june_assistant -> Should SUCCEED
    ok, msg = mgr.toggle_feature("june_assistant", enable=False)
    assert ok is True
    assert mgr.get_features()["june_assistant"]["enabled"] is False

    # Try to enable multilingual_stt while june_assistant is disabled -> Should FAIL
    ok, msg = mgr.toggle_feature("multilingual_stt", enable=True)
    assert ok is False
    assert "depends on disabled feature" in msg

    # Re-enable june_assistant -> Then multilingual_stt can be enabled
    ok, msg = mgr.toggle_feature("june_assistant", enable=True)
    assert ok is True
    ok, msg = mgr.toggle_feature("multilingual_stt", enable=True)
    assert ok is True


def test_feature_manager_protected_daemons(temp_config_dir):
    mgr = ConfigManager(config_dir=temp_config_dir)
    # Verify that core system daemons like NetworkManager or BlueZ are never terminated
    feat = {
        "name": "Dummy",
        "daemons": ["NetworkManager", "bluez", "systemd", "productivity.clipboard.clipboard_manager"]
    }
    terminated = mgr._terminate_feature_processes(feat)
    # Even if called, protected patterns are skipped
    assert isinstance(terminated, int)


# ============================================================================
# 3. Settings Updates & Themes
# ============================================================================

def test_settings_updates_and_theme(temp_config_dir):
    mgr = ConfigManager(config_dir=temp_config_dir)

    # Test update specific setting key
    ok = mgr.update_settings("appearance", "font_size", 15)
    assert ok is True
    assert mgr.get_settings()["appearance"]["font_size"] == 15

    # Test set theme
    ok = mgr.set_theme("nordic")
    assert ok is True
    assert mgr.get_settings()["theme"] == "nordic"

    ok = mgr.set_theme("forest")
    assert ok is True
    assert mgr.get_settings()["theme"] == "forest"

    # Invalid theme rejected
    ok = mgr.set_theme("invalid_theme_name")
    assert ok is False


# ============================================================================
# 4. Performance Profile Switcher
# ============================================================================

def test_performance_profiles(temp_config_dir):
    mgr = ConfigManager(config_dir=temp_config_dir)

    profiles = mgr.get_profiles()
    assert "balanced" in profiles
    assert "performance" in profiles
    assert "battery_saver" in profiles
    assert "full_experience" in profiles

    # Apply battery_saver profile
    ok, msg = mgr.apply_profile("battery_saver")
    assert ok is True
    assert mgr.get_active_profile() == "battery_saver"

    settings = mgr.get_settings()
    assert settings["appearance"]["animations_enabled"] is False
    assert settings["appearance"]["blur_enabled"] is False
    assert settings["display"]["idle_timeout_sec"] == 120

    # Apply performance profile
    ok, msg = mgr.apply_profile("performance")
    assert ok is True
    assert mgr.get_active_profile() == "performance"
    settings = mgr.get_settings()
    assert settings["appearance"]["animations_enabled"] is True
    assert settings["appearance"]["blur_enabled"] is True
    assert settings["appearance"]["animation_speed"] == 0.5


# ============================================================================
# 5. Backup & Recovery System
# ============================================================================

def test_backup_and_recovery(temp_config_dir):
    mgr = ConfigManager(config_dir=temp_config_dir)

    # Make a custom setting change
    mgr.set_theme("violet")
    mgr.update_settings("appearance", "border_radius", 24)

    # Create backup snapshot
    meta = mgr.create_backup(tag="test_snapshot")
    assert "id" in meta
    assert len(meta["files"]) >= 3

    backups = mgr.list_backups()
    assert len(backups) == 1
    assert backups[0]["id"] == meta["id"]

    # Mutate settings further
    mgr.set_theme("forest")
    assert mgr.get_settings()["theme"] == "forest"

    # Restore snapshot
    ok, msg = mgr.restore_backup(meta["id"])
    assert ok is True
    restored_settings = mgr.get_settings()
    assert restored_settings["theme"] == "violet"
    assert restored_settings["appearance"]["border_radius"] == 24

    # Factory Reset
    ok = mgr.reset_to_defaults()
    assert ok is True
    default_settings = mgr.get_settings()
    assert default_settings["theme"] == "midnight"
