#!/usr/bin/env bash
# =============================================================================
# Tejas OS - Desktop Environment Uninstaller & Rollback
# Safety Notice: Strictly user-space dotfiles uninstaller.
# Removes symlinks and restores previous configuration from backups.
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_ROOT="${HOME}/.config/tejas-os-backups"

echo "======================================================================"
echo "  Tejas OS Desktop Environment - Uninstaller"
echo "======================================================================"
echo ""

read -rp "Are you sure you want to uninstall Tejas OS dotfiles and restore previous configs? [y/N]: " confirm
if [[ ! "${confirm}" =~ ^[Yy]$ ]]; then
    echo "Uninstallation cancelled."
    exit 0
fi

echo ""
echo "[*] Removing desktop environment symlinks..."

TARGETS=(
    "${HOME}/.config/hypr"
    "${HOME}/.config/kitty"
    "${HOME}/.config/fish"
    "${HOME}/.config/quickshell"
    "${HOME}/.config/tejas-os/themes"
)

for target in "${TARGETS[@]}"; do
    if [ -L "${target}" ]; then
        rm -f "${target}"
        echo "  [-] Removed symlink: ${target}"
    fi
    # If a pre-existing backup directory existed with .orig extension, restore it
    if [ -d "${target}.orig" ] || [ -f "${target}.orig" ]; then
        mv "${target}.orig" "${target}"
        echo "  [+] Restored original: ${target}"
    fi
done

# Check if a tarball backup exists to restore
if [ -d "${BACKUP_ROOT}" ]; then
    LATEST_BACKUP=$(find "${BACKUP_ROOT}" -name "backup_*.tar.gz" -type f | sort | tail -n 1)
    if [ -n "${LATEST_BACKUP}" ]; then
        echo ""
        read -rp "Found backup ${LATEST_BACKUP}. Restore original configurations now? [Y/n]: " restore_ans
        if [[ ! "${restore_ans}" =~ ^[Nn]$ ]]; then
            echo "[*] Restoring configurations from backup..."
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
            echo "[OK] Restored backup configurations."
        fi
    fi
fi

echo ""
echo "======================================================================"
echo "  [✓] Tejas OS uninstallation complete. System restored to prior state."
echo "======================================================================"
exit 0
