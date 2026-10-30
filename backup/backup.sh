#!/usr/bin/env bash
# =============================================================================
# Tejas OS - Dotfiles Configuration Backup Engine
# Target: Arch Linux / HP EliteBook 840 G5
# Safety: Strictly user-space configuration archiver.
# =============================================================================

set -euo pipefail

BACKUP_ROOT="${HOME}/.config/tejas-os-backups"
TIMESTAMP="$(date +'%Y%m%d_%H%M%S')"
BACKUP_DIR="${BACKUP_ROOT}/backup_${TIMESTAMP}"
ARCHIVE_FILE="${BACKUP_ROOT}/backup_${TIMESTAMP}.tar.gz"

echo "========================================================"
echo "  Tejas OS - Configuration Backup Engine"
echo "========================================================"

mkdir -p "${BACKUP_ROOT}"
mkdir -p "${BACKUP_DIR}"

CONFIG_DIRS=(
    "hypr"
    "kitty"
    "fish"
    "quickshell"
    "tejas-os"
)

BACKED_UP_COUNT=0

for dir in "${CONFIG_DIRS[@]}"; do
    TARGET_PATH="${HOME}/.config/${dir}"
    if [ -d "${TARGET_PATH}" ] || [ -f "${TARGET_PATH}" ]; then
        echo "  [+] Backing up ~/.config/${dir}..."
        cp -a "${TARGET_PATH}" "${BACKUP_DIR}/"
        BACKED_UP_COUNT=$((BACKED_UP_COUNT + 1))
    fi
done

# Create manifest
cat <<EOF > "${BACKUP_DIR}/manifest.txt"
Tejas OS Configuration Backup Manifest
Timestamp: ${TIMESTAMP}
Date: $(date)
Hostname: $(uname -n)
User: ${USER}
Directories: ${BACKED_UP_COUNT}
EOF

# Create compressed tarball
tar -czf "${ARCHIVE_FILE}" -C "${BACKUP_ROOT}" "backup_${TIMESTAMP}"
rm -rf "${BACKUP_DIR}"

echo ""
echo "  [OK] Successfully archived ${BACKED_UP_COUNT} configuration targets to:"
echo "       ${ARCHIVE_FILE}"
echo ""

# Prune old backups, keeping latest 5
BACKUP_COUNT=$(find "${BACKUP_ROOT}" -name "backup_*.tar.gz" | wc -l)
if [ "${BACKUP_COUNT}" -gt 5 ]; then
    echo "  [*] Pruning older backups (retaining 5 most recent)..."
    find "${BACKUP_ROOT}" -name "backup_*.tar.gz" -type f | sort | head -n -5 | xargs -r rm -f
fi

echo "Backup complete."
exit 0
