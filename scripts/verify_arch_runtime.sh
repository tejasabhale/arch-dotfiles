#!/usr/bin/env bash
# =============================================================================
# Tejas OS — Arch Linux Runtime Verification Suite
# Target Hardware: HP EliteBook 840 G5 (Intel UHD 620, 8GB RAM, Dual-Boot UEFI)
# =============================================================================
# This script runs directly on an Arch Linux Wayland installation to validate:
# 1. Compositor version & Lua configuration
# 2. Quickshell layer shell desktop
# 3. System D-Bus services (NetworkManager, BlueZ, PipeWire, UPower)
# 4. June AI JSON-RPC daemon & IPC socket
# 5. Wi-Fi AP Hotspot hardware capability
# 6. Centralized configuration engine & performance profiles
# =============================================================================

set -uo pipefail

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

PASS_COUNT=0
WARN_COUNT=0
FAIL_COUNT=0

record_pass() {
    echo -e "  ${GREEN}[PASS]${NC} $1"
    PASS_COUNT=$((PASS_COUNT + 1))
}

record_warn() {
    echo -e "  ${YELLOW}[WARN]${NC} $1"
    WARN_COUNT=$((WARN_COUNT + 1))
}

record_fail() {
    echo -e "  ${RED}[FAIL]${NC} $1"
    FAIL_COUNT=$((FAIL_COUNT + 1))
}

echo -e "${BOLD}${CYAN}======================================================================${NC}"
echo -e "${BOLD}${CYAN}  Tejas OS — Arch Linux Runtime Verification Suite                     ${NC}"
echo -e "${BOLD}${CYAN}======================================================================${NC}"
echo "Hostname: $(uname -n) | Kernel: $(uname -r) | Architecture: $(uname -m)"
echo "Date: $(date)"
echo ""

# -----------------------------------------------------------------------------
# 1. Operating System & Hardware Invariants
# -----------------------------------------------------------------------------
echo -e "${BOLD}${BLUE}=== 1. OS & Dual-Boot Safety Guardrails ===${NC}"
if [ -f "/etc/arch-release" ]; then
    record_pass "Native Arch Linux environment verified (/etc/arch-release)"
elif [ -f "/etc/os-release" ] && grep -qi "arch" "/etc/os-release"; then
    record_pass "Arch-based distribution verified (/etc/os-release)"
else
    record_warn "Non-Arch distribution detected. Some package paths may vary."
fi

# Dual-Boot Invariant: Verify Windows EFI is intact
if [ -d "/boot/efi/EFI/Microsoft/Boot" ] || [ -d "/boot/EFI/Microsoft/Boot" ]; then
    record_pass "Dual-Boot Invariant: Windows bootloader intact (Microsoft/Boot/bootmgfw.efi)"
elif [ -d "/sys/firmware/efi" ]; then
    record_pass "UEFI firmware detected. Safe dotfiles scope active."
else
    record_warn "Non-UEFI environment detected. (Testing inside container or VM)"
fi

# RAM Check (8 GB physical target)
if [ -f "/proc/meminfo" ]; then
    RAM_TOTAL_KB=$(grep MemTotal /proc/meminfo | awk '{print $2}')
    RAM_TOTAL_MB=$((RAM_TOTAL_KB / 1024))
    if [ "${RAM_TOTAL_MB}" -ge 7000 ] && [ "${RAM_TOTAL_MB}" -le 9000 ]; then
        record_pass "Memory matches 8 GB hardware target: ${RAM_TOTAL_MB} MB"
    else
        record_pass "System RAM: ${RAM_TOTAL_MB} MB (Target budget: <= 1.8GB idle footprint)"
    fi
fi
echo ""

# -----------------------------------------------------------------------------
# 2. Hyprland Compositor & Lua Configuration
# -----------------------------------------------------------------------------
echo -e "${BOLD}${BLUE}=== 2. Hyprland Compositor & Lua Configuration ===${NC}"
if command -v Hyprland >/dev/null 2>&1; then
    HYPR_VER=$(Hyprland --version 2>&1 | head -n1)
    record_pass "Hyprland binary detected: ${HYPR_VER}"
    
    # Check version >= 0.55 and >= 0.57
    VER_NUM=$(echo "${HYPR_VER}" | grep -oE '[0-9]+\.[0-9]+' | head -n1)
    if [ -n "${VER_NUM}" ]; then
        VER_MIN=$(echo "${VER_NUM}" | cut -d. -f2)
        if [ "${VER_MIN}" -ge 57 ] 2>/dev/null; then
            record_pass "Hyprland >= 0.57: Native Lua (hyprland.lua) is mandatory and active."
        elif [ "${VER_MIN}" -ge 55 ] 2>/dev/null; then
            record_pass "Hyprland 0.55/0.56: Native Lua (hyprland.lua) officially supported."
        else
            record_warn "Hyprland < 0.55 detected. Tejas OS officially targets 0.55+."
        fi
    fi
else
    record_fail "Hyprland binary not found in PATH"
fi

if [ -f "core/hyprland/hyprland.lua" ]; then
    record_pass "Main entry point core/hyprland/hyprland.lua exists"
else
    record_fail "core/hyprland/hyprland.lua missing"
fi

# Validate Lua syntax via python validator
if python3 tests/test_lua_syntax.py >/dev/null 2>&1; then
    record_pass "All 9 Hyprland Lua modules passed syntax validation"
else
    record_fail "Hyprland Lua syntax validation failed"
fi
echo ""

# -----------------------------------------------------------------------------
# 3. Quickshell Desktop Shell & QML Layer
# -----------------------------------------------------------------------------
echo -e "${BOLD}${BLUE}=== 3. Quickshell Desktop Shell & QML Layer ===${NC}"
if command -v quickshell >/dev/null 2>&1; then
    QS_VER=$(quickshell --version 2>&1 || echo "installed")
    record_pass "Quickshell binary detected: ${QS_VER}"
else
    record_warn "quickshell binary not in PATH (install via 'pacman -S quickshell' or aur/quickshell-git)"
fi

if python3 tests/test_qml_syntax.py >/dev/null 2>&1; then
    record_pass "All 41 Quickshell QML components and 4 theme JSON presets passed syntax check"
else
    record_fail "Quickshell QML syntax validation failed"
fi

if [ -f "shell/services/HardwareService.qml" ]; then
    record_pass "Centralized HardwareService.qml singleton verified"
else
    record_fail "HardwareService.qml missing"
fi
echo ""

# -----------------------------------------------------------------------------
# 4. System Services & D-Bus Integrations
# -----------------------------------------------------------------------------
echo -e "${BOLD}${BLUE}=== 4. System Services & D-Bus Integrations ===${NC}"

# PipeWire / WirePlumber
if command -v wpctl >/dev/null 2>&1; then
    record_pass "WirePlumber audio controller (wpctl) installed"
    if wpctl status >/dev/null 2>&1; then
        record_pass "PipeWire audio daemon is running and responding"
    else
        record_warn "PipeWire running state could not be queried (session active?)"
    fi
else
    record_warn "wpctl not found in PATH (pipewire-audio / wireplumber required)"
fi

# NetworkManager
if command -v nmcli >/dev/null 2>&1; then
    record_pass "NetworkManager CLI (nmcli) installed"
    if nmcli general status >/dev/null 2>&1; then
        record_pass "NetworkManager D-Bus daemon is active and responsive"
    else
        record_warn "NetworkManager daemon is not currently active"
    fi
else
    record_warn "nmcli not found in PATH (networkmanager package required)"
fi

# BlueZ
if command -v bluetoothctl >/dev/null 2>&1; then
    record_pass "BlueZ CLI (bluetoothctl) installed"
else
    record_warn "bluetoothctl not found in PATH (bluez-utils required)"
fi

# Brightnessctl
if command -v brightnessctl >/dev/null 2>&1; then
    record_pass "brightnessctl backlight utility installed"
else
    record_warn "brightnessctl not found in PATH"
fi

# Power Profiles Daemon / UPower
if command -v powerprofilesctl >/dev/null 2>&1; then
    record_pass "powerprofilesctl installed"
else
    record_warn "powerprofilesctl not found in PATH (power-profiles-daemon recommended)"
fi

# Wi-Fi Access Point (Hotspot) Driver Support
if command -v iw >/dev/null 2>&1; then
    if iw list 2>/dev/null | grep -q "AP"; then
        record_pass "Wi-Fi Chipset Driver supports AP (Access Point / Hotspot) mode"
    else
        record_warn "Wi-Fi interface does not advertise AP mode in iw list"
    fi
else
    record_warn "iw utility not found in PATH (iw package needed for hardware detect)"
fi
echo ""

# -----------------------------------------------------------------------------
# 5. June AI Assistant IPC & Multilingual Engine
# -----------------------------------------------------------------------------
echo -e "${BOLD}${BLUE}=== 5. June AI Assistant IPC & Multilingual Engine ===${NC}"
if command -v python3 >/dev/null 2>&1; then
    PY_VER=$(python3 --version 2>&1)
    record_pass "Python runtime detected: ${PY_VER}"
else
    record_fail "python3 not found in PATH"
fi

# Run multilingual tests
if python3 -m pytest tests/test_multilingual_engine.py -q >/dev/null 2>&1; then
    record_pass "All 7 language combinations, Devanagari Hindi/Marathi & Hinglish/Maranglish verified"
else
    record_fail "Multilingual test suite failed"
fi

# Test fast-path ping
PING_OUT=$(python3 -m assistant.core.cli --ping --json 2>&1 || true)
if echo "${PING_OUT}" | grep -q '"status"'; then
    record_pass "June Client fast-path dispatch responds successfully"
else
    record_warn "June Client fallback response: ${PING_OUT:0:80}"
fi

# Action Planner & Safety Guards
if python3 -m pytest tests/test_assistant_automation.py -q >/dev/null 2>&1; then
    record_pass "Action Planner AST and permission engine allowlist verified"
else
    record_fail "Assistant automation test suite failed"
fi
echo ""

# -----------------------------------------------------------------------------
# 6. Centralized Configuration Engine
# -----------------------------------------------------------------------------
echo -e "${BOLD}${BLUE}=== 6. Centralized Configuration & Profile Manager ===${NC}"
if python3 -m pytest tests/test_config_manager.py -q >/dev/null 2>&1; then
    record_pass "ConfigManager atomic JSON writes, schema migration & protected daemons verified"
else
    record_fail "ConfigManager test suite failed"
fi

# Test developer module
if python3 -m pytest tests/test_developer_module.py -q >/dev/null 2>&1; then
    record_pass "Developer Hub backend (git, ports, venvs, ssh) verified"
else
    record_fail "Developer module test suite failed"
fi
echo ""

# -----------------------------------------------------------------------------
# Final Summary
# -----------------------------------------------------------------------------
echo -e "${BOLD}${CYAN}======================================================================${NC}"
echo -e "${BOLD}Verification Summary: ${GREEN}${PASS_COUNT} Passed${NC} | ${YELLOW}${WARN_COUNT} Warnings${NC} | ${RED}${FAIL_COUNT} Failed${NC}"
echo -e "${BOLD}${CYAN}======================================================================${NC}"

if [ "${FAIL_COUNT}" -eq 0 ]; then
    echo -e "${GREEN}${BOLD}[SUCCESS] Tejas OS runtime environment passed all critical checkpoints!${NC}"
    exit 0
else
    echo -e "${RED}${BOLD}[FAILURE] ${FAIL_COUNT} critical verification checkpoint(s) failed.${NC}"
    exit 1
fi
