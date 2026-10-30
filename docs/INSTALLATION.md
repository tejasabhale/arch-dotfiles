# Installation Guide — Tejas OS

## 1. System Requirements & Hardware Target
- **Target Laptop:** HP EliteBook 840 G5 (or compatible x86_64 laptop).
- **CPU:** Intel Core i5-8250U / i5-8350U / i7-8550U / i7-8650U (4 Cores / 8 Threads).
- **GPU:** Intel UHD Graphics 620.
- **RAM:** Minimum 8 GB DDR4 (1.8 GB idle footprint target).
- **Firmware:** UEFI mode with Secure Boot disabled or keys enrolled.
- **Operating System:** Arch Linux (rolling release) dual-booted with Windows 11.

---

## 2. Safety Invariants (Dual-Boot Protection)
> [!IMPORTANT]
> The installation script is **strictly a user-space dotfiles configurator and package installer**.
> - It will **never** partition or format your hard drive (`mkfs`, `fdisk`, `parted`).
> - It will **never** alter or delete the Windows partition (NTFS).
> - It will **never** touch or overwrite the Windows EFI bootloader (`bootmgfw.efi`).

---

## 3. Pre-Requisites & Base Packages

Ensure your Arch Linux base system is running and connected to the internet.

```bash
# Update package databases
sudo pacman -Syu

# Install git and base tools
sudo pacman -S --needed git base-devel python
```

---

## 4. Step-by-Step Installation

### Step 4.1: Clone the Repository
```bash
cd ~
git clone https://github.com/tejas-os/arch-dotfiles.git
cd arch-dotfiles
```

### Step 4.2: Run Pre-Flight Verification (Dry-Run)
Before modifying any configurations, verify your system compatibility using the dry-run mode:
```bash
./install.sh --dry-run
```
This inspects CPU, GPU, memory, missing packages, and target symlinks without modifying any files.

### Step 4.3: Execute Installation
```bash
./install.sh
```
The installer will:
1. Create a timestamped backup of your current configurations to `~/.config/tejas-os-backups/`.
2. Offer to install any missing required packages via `pacman`.
3. Create symlinks for Hyprland (`core/hyprland`), Kitty, Fish, Quickshell, and Themes.
4. Initialize `~/.config/tejas-os/` centralized configuration.
5. Set execution permissions on Python daemons.

---

## 5. Starting the Desktop Environment

After installation completes, launch Hyprland:
```bash
Hyprland
```

Once inside Hyprland:
- Press **Super + Space** to summon June AI Assistant.
- Press **Super + D** to open the Developer Hub.
- Press **Super + I** to launch the Settings application.
- Press **Super + Shift + T** to cycle themes (Midnight, Nordic Light, Forest, Violet).

---

## 6. Rollback & Uninstallation

If you ever wish to revert your configuration to the state prior to installation:
```bash
# Quick rollback from latest backup
./install.sh --rollback

# Or run full uninstaller
./uninstall.sh
```
