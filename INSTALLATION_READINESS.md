# Tejas OS — Installation Readiness & Deployment Guide

This document establishes the pre-flight requirements, dual-boot safety procedures, and installation instructions for deploying **Tejas OS** onto the **HP EliteBook 840 G5**.

---

## 1. Target Hardware Specifications

| Hardware Component | Target Specification |
|---|---|
| **Laptop Model** | HP EliteBook 840 G5 |
| **Processor** | Intel Core i5-8250U / i5-8350U / i7-8550U / i7-8650U (4 Cores / 8 Threads) |
| **Graphics** | Intel UHD Graphics 620 (Whiskey Lake / Kaby Lake Refresh) |
| **Memory** | 8.00 GB DDR4-2400 (Single or Dual-channel) |
| **Display** | 14.0" Full HD (1920 × 1080 @ 60 Hz) anti-glare IPS (eDP-1) |
| **Storage / Boot** | NVMe SSD — Dual-boot UEFI alongside Windows 11 |
| **Wireless / BT** | Intel Dual Band Wireless-AC 8265 (802.11ac + Bluetooth 4.2) |
| **Audio** | Intel Cannon Point-LP High Definition Audio Controller (PipeWire / ALSA) |

---

## 2. Firmware & Dual-Boot Safety Guardrails

### 2.1 BIOS / UEFI Configuration
Before booting Arch Linux, confirm the following settings in HP Sure Start BIOS setup (`F10` during boot):
- **SATA / NVMe Controller**: AHCI mode (do not use Intel RST / RAID).
- **Secure Boot**: Set to `Audit Mode` or `Disabled` if using custom kernels; if using `systemd-boot` with sbctl, enroll keys before enabling.
- **Fast Startup (Windows)**: Must be **Disabled** inside Windows Control Panel (Power Options -> Choose what the power buttons do -> Turn off fast startup). Fast Startup leaves NTFS partitions in a hibernated, dirty state that prevents clean mounting.
- **Intel Virtualization (VT-x / VT-d)**: Enabled.

### 2.2 Dual-Boot Safety Guardrails (Non-Negotiable)
The installer script [`install.sh`](file:///E:/Work/arch-dotfiles/install.sh) is strictly a **user-space dotfiles configurator**:
- It **never** formats or modifies disk partitions (`mkfs`, `fdisk`, `parted`).
- It **never** alters the Windows bootloader located at `/boot/efi/EFI/Microsoft/Boot/bootmgfw.efi`.
- It **never** touches Windows NTFS data partitions.
- It only links configurations into the user's home directory (`~/.config/`).

---

## 3. Package Prerequisites on Arch Linux

Ensure the core Arch packages and AUR packages are installed prior to deploying dotfiles:

### 3.1 Official Arch Linux Packages
```bash
sudo pacman -S --needed \
    hyprland \
    qt6-declarative \
    qt6-wayland \
    kitty \
    fish \
    python \
    python-pip \
    pipewire \
    wireplumber \
    pipewire-audio \
    pipewire-pulse \
    networkmanager \
    bluez \
    bluez-utils \
    power-profiles-daemon \
    upower \
    grim \
    slurp \
    wl-clipboard \
    brightnessctl \
    polkit-kde-agent \
    noto-fonts \
    ttf-jetbrains-mono-nerd
```

### 3.2 AUR Packages (via Paru or Yay)
```bash
paru -S --needed \
    quickshell-git \
    hypridle \
    hyprlock \
    cliphist
```

---

## 4. Step-by-Step Installation Procedure

### Step 1: Clone Repository
```bash
git clone https://github.com/tejas-os/arch-dotfiles.git ~/arch-dotfiles
cd ~/arch-dotfiles
git checkout refactor/performance-architecture
```

### Step 2: Run Pre-Flight Dry Run
Inspect all actions that will be performed without modifying any files:
```bash
./install.sh --dry-run
```
Verify that the output displays:
- Arch Linux detected.
- Target hardware: HP EliteBook 840 G5.
- Hyprland version >= 0.55 detected with Lua support.
- Summary of symlinks to be created in `~/.config/`.

### Step 3: Execute Safe Dotfiles Installation
```bash
./install.sh
```
What the installer does automatically:
1. Runs `backup/backup.sh` to snapshot existing dotfiles into `~/.config/tejas-os-backups/`.
2. Renames existing directories to `<name>.orig` if not already a symlink.
3. Symlinks repository configurations:
   - `core/hyprland` -> `~/.config/hypr`
   - `config/kitty` -> `~/.config/kitty`
   - `config/fish` -> `~/.config/fish`
   - `shell` -> `~/.config/quickshell`
   - `themes` -> `~/.config/tejas-os/themes`
4. Initializes centralized JSON settings at `~/.config/tejas-os/`.

---

## 5. Post-Installation Verification

Run the automated verification suite to validate system readiness:
```bash
bash scripts/verify_arch_runtime.sh
```
Expected output:
- `[PASS]` Hyprland >= 0.55 detected with Lua configuration.
- `[PASS]` All 9 Lua modules and 41 QML files validated.
- `[PASS]` D-Bus services active (PipeWire, NetworkManager, BlueZ).
- `[PASS]` June AI socket and multilingual engine verified.
- `[PASS]` Wi-Fi AP Hotspot mode supported by hardware.

---

## 6. Rollback & Uninstallation Procedures

If you ever wish to revert all changes and restore your prior configuration:

### Option A: Installer Rollback
```bash
./install.sh --rollback
```

### Option B: Clean Uninstaller
```bash
./uninstall.sh
```
This removes all symlinks, restores any pre-existing `<name>.orig` directories, and unpacks the timestamped backup tarball.
