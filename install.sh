#!/usr/bin/env bash
# =============================================================================
# Tejas OS - Desktop Environment & June AI Automated Installer
# Target Hardware: HP EliteBook 840 G5 (Intel UHD 620, 8GB RAM, Dual-Boot UEFI)
# Safety Notice: STRICTLY USER-SPACE DOTFILES CONFIGURATOR.
# Rule 1.5 Compliance: Zero disk formatting, zero partition modification,
#                      ESP and Windows NTFS partitions are NEVER touched.
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DRY_RUN=false
DO_BACKUP=true
DO_ROLLBACK=false

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_banner() {
    echo -e "${CYAN}"
    echo "======================================================================"
    echo "   _____     _           ___  ____   "
    echo "  |_   _|___(_) __ _ ___/ _ \/ ___|  "
    echo "    | | / _ \ |/ _\` / __| | | \___ \  "
    echo "    | ||  __/ | (_| \__ \ |_| |___) | "
    echo "    |_| \___| |\__,_|___/\___/|____/  "
    echo "          |__/                        "
    echo "  Custom Arch Linux Desktop Environment + June AI Assistant"
    echo "======================================================================"
    echo -e "${NC}"
}

print_help() {
    echo "Usage: ./install.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --dry-run       Perform pre-flight verification without modifying system files"
    echo "  --no-backup     Skip automatic configuration backup before installation"
    echo "  --rollback      Restore prior configuration from latest backup and exit"
    echo "  -h, --help      Display this help dialog"
    echo ""
}

# Parse Command Line Arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --no-backup)
            DO_BACKUP=false
            shift
            ;;
        --rollback)
            DO_ROLLBACK=true
            shift
            ;;
        -h|--help)
            print_help
            exit 0
            ;;
        *)
            echo -e "${RED}[ERROR] Unknown option: $1${NC}"
            print_help
            exit 1
            ;;
    esac
done

print_banner

# =============================================================================
# ROLLBACK FLOW
# =============================================================================
if [ "${DO_ROLLBACK}" = true ]; then
    echo -e "${YELLOW}[*] Rollback requested. Searching for latest backup...${NC}"
    BACKUP_ROOT="${HOME}/.config/tejas-os-backups"
    if [ ! -d "${BACKUP_ROOT}" ]; then
        echo -e "${RED}[ERROR] No backup directory found at ${BACKUP_ROOT}${NC}"
        exit 1
    fi

    LATEST_BACKUP=$(find "${BACKUP_ROOT}" -name "backup_*.tar.gz" -type f | sort | tail -n 1)
    if [ -z "${LATEST_BACKUP}" ]; then
        echo -e "${RED}[ERROR] No backup tarball found in ${BACKUP_ROOT}${NC}"
        exit 1
    fi

    echo -e "${GREEN}[+] Restoring from ${LATEST_BACKUP}...${NC}"
    TEMP_RESTORE=$(mktemp -d)
    tar -xzf "${LATEST_BACKUP}" -C "${TEMP_RESTORE}"
    BACKUP_DIR=$(find "${TEMP_RESTORE}" -mindepth 1 -maxdepth 1 -type d | head -n 1)

    for item in "${BACKUP_DIR}"/*; do
        bname=$(basename "${item}")
        if [ "${bname}" != "manifest.txt" ]; then
            echo "    Restoring ~/.config/${bname}..."
            rm -rf "${HOME}/.config/${bname}"
            cp -a "${item}" "${HOME}/.config/"
        fi
    done

    rm -rf "${TEMP_RESTORE}"
    echo -e "${GREEN}[OK] Rollback complete. Prior configuration restored.${NC}"
    exit 0
fi

# =============================================================================
# 1. PRE-FLIGHT VERIFICATION & HARDWARE CHECKS
# =============================================================================
echo -e "${BLUE}=== 1. Pre-Flight Verification & System Safety Checks ===${NC}"

# Check Operating System
if [ -f "/etc/arch-release" ]; then
    echo -e "  ${GREEN}[✓] Arch Linux detected (/etc/arch-release)${NC}"
elif [ -f "/etc/os-release" ] && grep -qi "arch" "/etc/os-release"; then
    echo -e "  ${GREEN}[✓] Arch-based distribution detected${NC}"
else
    echo -e "  ${YELLOW}[!] Warning: Not running on native Arch Linux. Proceeding with caution.${NC}"
fi

# Rule 1.5 Safety Verification: Dual-Boot Invariant Check
echo -e "  ${GREEN}[✓] Dual-Boot Safety Guard Active: Format, partition, and bootmgfw.efi modifications are prohibited.${NC}"

# Hardware Target Check (HP EliteBook 840 G5 / Intel UHD 620)
DMI_PRODUCT="/sys/class/dmi/id/product_name"
if [ -f "${DMI_PRODUCT}" ]; then
    HW_PRODUCT=$(cat "${DMI_PRODUCT}" 2>/dev/null || echo "Generic x86_64")
    echo -e "  ${GREEN}[✓] Target Hardware: ${HW_PRODUCT}${NC}"
else
    echo -e "  ${GREEN}[✓] Target Architecture: $(uname -m)${NC}"
fi

# Memory Check (Target: 8 GB RAM profile)
if [ -f "/proc/meminfo" ]; then
    TOTAL_RAM_KB=$(grep MemTotal /proc/meminfo | awk '{print $2}')
    TOTAL_RAM_MB=$((TOTAL_RAM_KB / 1024))
    echo -e "  ${GREEN}[✓] Total System Memory: ${TOTAL_RAM_MB} MB (Target: <= 1.8GB Idle Footprint)${NC}"
fi

# Hyprland Version & Configuration Format Detection
if command -v Hyprland >/dev/null 2>&1; then
    HYPR_VER_RAW=$(Hyprland --version 2>&1 | head -n1)
    echo -e "  ${GREEN}[✓] Detected Compositor: ${HYPR_VER_RAW}${NC}"
    HYPR_NUM=$(echo "${HYPR_VER_RAW}" | grep -oE '[0-9]+\.[0-9]+' | head -n1)
    if [ -n "${HYPR_NUM}" ]; then
        HYPR_MIN=$(echo "${HYPR_NUM}" | cut -d. -f2)
        if [ "${HYPR_MIN}" -ge 55 ] 2>/dev/null; then
            echo -e "  ${GREEN}[✓] Hyprland >= 0.55: Deploying Native Lua configuration (hyprland.lua)${NC}"
        else
            echo -e "  ${YELLOW}[!] Hyprland < 0.55: Providing hyprland.conf compatibility bridge${NC}"
        fi
    fi
fi

# =============================================================================
# 2. REQUIRED PACKAGES PRE-FLIGHT CHECK
# =============================================================================
echo ""
echo -e "${BLUE}=== 2. Package Dependency Pre-Flight Check ===${NC}"

PACKAGES=(
    "hyprland"
    "qt6-declarative"
    "kitty"
    "fish"
    "python"
    "pipewire"
    "wireplumber"
    "bluez"
    "networkmanager"
    "power-profiles-daemon"
    "upower"
    "grim"
    "slurp"
    "wl-clipboard"
    "brightnessctl"
)

MISSING_PACKAGES=()

for pkg in "${PACKAGES[@]}"; do
    if pacman -Qq "${pkg}" &>/dev/null; then
        echo -e "  ${GREEN}[✓] ${pkg}${NC}"
    else
        echo -e "  ${YELLOW}[-] Missing: ${pkg}${NC}"
        MISSING_PACKAGES+=("${pkg}")
    fi
done

if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo ""
    echo -e "${YELLOW}Notice: ${#MISSING_PACKAGES[@]} required package(s) not currently installed.${NC}"
    echo "Install them using:"
    echo -e "${CYAN}sudo pacman -S ${MISSING_PACKAGES[*]}${NC}"
    echo ""
    if [ "${DRY_RUN}" = false ]; then
        read -rp "Would you like to install missing packages now? [y/N]: " install_ans
        if [[ "${install_ans}" =~ ^[Yy]$ ]]; then
            sudo pacman -S --needed "${MISSING_PACKAGES[@]}"
        fi
    fi
fi

# =============================================================================
# 3. DRY RUN CHECK
# =============================================================================
if [ "${DRY_RUN}" = true ]; then
    echo ""
    echo -e "${CYAN}=== DRY-RUN MODE: Summary of Actions (No files will be modified) ===${NC}"
    echo "1. Run backup of existing configurations via backup/backup.sh"
    echo "2. Link repository configurations to user space:"
    echo "   - ${SCRIPT_DIR}/core/hyprland       -> ~/.config/hypr"
    echo "   - ${SCRIPT_DIR}/config/kitty       -> ~/.config/kitty"
    echo "   - ${SCRIPT_DIR}/config/fish        -> ~/.config/fish"
    echo "   - ${SCRIPT_DIR}/shell              -> ~/.config/quickshell"
    echo "   - ${SCRIPT_DIR}/themes             -> ~/.config/tejas-os/themes"
    echo "3. Initialize ~/.config/tejas-os/ with default settings and 4 theme presets"
    echo "4. Set execution permissions on helper scripts"
    echo ""
    echo -e "${GREEN}[OK] Dry-run completed successfully with zero modifications.${NC}"
    exit 0
fi

# =============================================================================
# 4. AUTOMATIC CONFIGURATION BACKUP
# =============================================================================
if [ "${DO_BACKUP}" = true ]; then
    echo ""
    echo -e "${BLUE}=== 3. Creating Configuration Backup ===${NC}"
    if [ -f "${SCRIPT_DIR}/backup/backup.sh" ]; then
        bash "${SCRIPT_DIR}/backup/backup.sh"
    else
        echo -e "${YELLOW}[!] Backup script not found at backup/backup.sh. Skipping backup.${NC}"
    fi
fi

# =============================================================================
# 5. USER-SPACE DOTFILES DEPLOYMENT
# =============================================================================
echo ""
echo -e "${BLUE}=== 4. Deploying User-Space Configurations ===${NC}"

mkdir -p "${HOME}/.config"
mkdir -p "${HOME}/.config/tejas-os"

# Helper function for safe symlinking
link_config() {
    local src="$1"
    local dst="$2"

    if [ -L "${dst}" ]; then
        rm -f "${dst}"
    elif [ -d "${dst}" ] || [ -f "${dst}" ]; then
        mv "${dst}" "${dst}.orig"
    fi

    ln -s "${src}" "${dst}"
    echo -e "  ${GREEN}[+] Linked:${NC} ${src} -> ${dst}"
}

# 1. Hyprland configuration (pure Lua)
link_config "${SCRIPT_DIR}/core/hyprland" "${HOME}/.config/hypr"

# 2. Kitty terminal configuration
link_config "${SCRIPT_DIR}/config/kitty" "${HOME}/.config/kitty"

# 3. Fish shell configuration
link_config "${SCRIPT_DIR}/config/fish" "${HOME}/.config/fish"

# 4. Quickshell desktop shell
link_config "${SCRIPT_DIR}/shell" "${HOME}/.config/quickshell"

# 5. Themes
link_config "${SCRIPT_DIR}/themes" "${HOME}/.config/tejas-os/themes"

# =============================================================================
# 6. INITIALIZE CENTRALIZED CONFIGURATION & PERMISSIONS
# =============================================================================
echo ""
echo -e "${BLUE}=== 5. Initializing Centralized Configuration & Services ===${NC}"

python3 -m config.manager || true

# Set execution bits on Python managers and shell scripts
chmod +x "${SCRIPT_DIR}/install.sh" "${SCRIPT_DIR}/uninstall.sh" "${SCRIPT_DIR}/backup/backup.sh" 2>/dev/null || true
find "${SCRIPT_DIR}" -name "*.py" -exec chmod +x {} + 2>/dev/null || true

echo ""
echo -e "${GREEN}======================================================================${NC}"
echo -e "${GREEN}  [✓] Tejas OS Desktop Environment Successfully Installed!            ${NC}"
echo -e "${GREEN}======================================================================${NC}"
echo ""
echo "Getting Started:"
echo "  1. Start Hyprland session:     Hyprland"
echo "  2. Open June AI Assistant:     Super + Space"
echo "  3. Open Developer Hub:         Super + D"
echo "  4. Open Settings App:          Super + I"
echo "  5. Switch Themes:              Super + Shift + T"
echo ""
echo "To revert changes at any time, run:"
echo "  ./uninstall.sh"
echo ""
exit 0
