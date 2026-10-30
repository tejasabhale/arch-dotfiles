# Custom Arch Linux Desktop Environment + June AI

[![Arch Linux](https://img.shields.io/badge/Arch_Linux-Wayland-1793D1?logo=arch-linux&logoColor=white)](https://archlinux.org)
[![Hyprland 0.55+](https://img.shields.io/badge/Hyprland-0.55+_Lua-00ACC1?logo=lua&logoColor=white)](https://hyprland.org)
[![Quickshell](https://img.shields.io/badge/Quickshell-QtQuick_QML-41CD52?logo=qt&logoColor=white)](https://quickshell.outfoxxed.me)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Tests Passing](https://img.shields.io/badge/Tests-70%2F70_Passed-success)](tests/)

A production-grade, modular, and intelligent Linux desktop environment engineered for **Arch Linux**, pairing **Hyprland** (0.55+ with pure Lua configuration) and **Quickshell** (QtQuick/QML) with an autonomous, decoupled AI assistant named **June**.

Engineered for the **HP EliteBook 840 G5** (8 GB RAM, Intel UHD Graphics 620, dual-booting with Windows 11 on UEFI).

---

## 🌟 Key Highlights

- **Hyprland 0.55+ Pure Lua API:** Built with the official `hl` Lua API (`hyprland.lua`), replacing outdated `hyprlang`.
- **Quickshell Desktop Shell:** Modular Top Bar, autohiding Dock, Application Launcher, Overview window picker, Control Center, OSD, and Notification Center.
- **June AI Assistant:** Independent daemon communicating via JSON-RPC 2.0 over Unix sockets. Trilingual natural language understanding across **English, Hindi, and Marathi** in all 7 combinations with mid-sentence code-switching.
- **Developer Hub (Super + D):** Unified multi-tab developer deck featuring Project Launcher, Git Dashboard, Listening Ports Inspector with PID safety guards, Python venv/Conda manager, and SSH shortcuts.
- **Centralized Settings App (Super + I):** Full-featured Quickshell application covering 22 structured categories with instant search.
- **Modular Feature Isolation (Rule 1.4):** Every feature independently toggles in `features.json`. Disabling a feature actively terminates background processes to conserve memory.
- **8 GB RAM Budget:** Idle memory footprint strictly bounded to $\le 1.5 - 2.0\text{ GB}$ with 4 dynamic performance profiles (*Balanced*, *Performance*, *Battery Saver*, *Full Experience*).
- **Dual-Boot Non-Destructive Safety (Rule 1.5):** User-space configurator only. Never touches Windows partitions (NTFS), the ESP, or the Windows bootloader (`bootmgfw.efi`).

---

## 🚀 Quick Start & Installation

```bash
# 1. Clone repository
git clone https://github.com/tejas-os/arch-dotfiles.git
cd arch-dotfiles

# 2. Pre-flight verification (Dry-run mode, no changes made)
./install.sh --dry-run

# 3. Deploy dotfiles and user configurations
./install.sh

# 4. Launch Hyprland session
Hyprland
```

To roll back or uninstall at any time:
```bash
./uninstall.sh
```

---

## ⌨️ Essential Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Super + Space` | **June AI Assistant** (Voice & text interface) |
| `Super + D` | **Developer Hub** (Projects, Git, Ports, Envs, SSH) |
| `Super + I` | **Settings App** (22 Categories & Feature Manager) |
| `Super + Return` | **Kitty Terminal** with Fish shell |
| `Super + A` | **Application Launcher** (Fuzzy search) |
| `Super + Tab` | **Workspace Overview** (Window picker) |
| `Super + C` | **Control Center** (Wi-Fi, Bluetooth, Audio, Power) |
| `Super + B` | **Clipboard History Panel** |
| `Super + Shift + T` | **Cycle Theme Preset** (Midnight, Nordic Light, Forest, Violet) |
| `Super + Escape` | **Emergency Stop** (Instantly abort running AI action plan) |
| `Print` | **Screenshot Bar** (Interactive region capture) |

Full keybinding cheatsheet available in [`docs/KEYBINDINGS.md`](file:///E:/Work/arch-dotfiles/docs/KEYBINDINGS.md).

---

## 🎨 The 4 Tokenized Theme Presets

All UI components dynamically bind to `ThemeService` tokens without hardcoded hex values:
- **Midnight (Default):** Dark indigo base with ice-blue accent.
- **Nordic Light:** Clean warm light blue with frost-blue accent.
- **Forest:** Earthy deep dark green with sage accent.
- **Violet:** Rich dark purple with luminous lavender accent.

Switch presets instantly via Settings (`Super + I`) or CLI:
```bash
python3 -m config.manager --theme forest
```

---

## 📚 Complete Documentation Suite

- [`docs/ARCHITECTURE.md`](file:///E:/Work/arch-dotfiles/docs/ARCHITECTURE.md) — System layers, Wayland compositor, and D-Bus IPC.
- [`docs/INSTALLATION.md`](file:///E:/Work/arch-dotfiles/docs/INSTALLATION.md) — Step-by-step setup, dual-boot precautions, and dependencies.
- [`docs/CONFIGURATION.md`](file:///E:/Work/arch-dotfiles/docs/CONFIGURATION.md) — Centralized `~/.config/tejas-os/` schema and theme tokens.
- [`docs/JUNE_AI_GUIDE.md`](file:///E:/Work/arch-dotfiles/docs/JUNE_AI_GUIDE.md) — Assistant capabilities, providers, and action safety model.
- [`docs/MULTILINGUAL_GUIDE.md`](file:///E:/Work/arch-dotfiles/docs/MULTILINGUAL_GUIDE.md) — Trilingual engine, Devanagari disambiguation, and STT/TTS.
- [`docs/PERFORMANCE_GUIDE.md`](file:///E:/Work/arch-dotfiles/docs/PERFORMANCE_GUIDE.md) — 8GB RAM budget and performance profiles.
- [`docs/DEVELOPER_HUB.md`](file:///E:/Work/arch-dotfiles/docs/DEVELOPER_HUB.md) — Developer tools, ports inspector, and project launcher.
- [`docs/HOTSPOT_GUIDE.md`](file:///E:/Work/arch-dotfiles/docs/HOTSPOT_GUIDE.md) — Dedicated Wi-Fi AP configuration and QR sharing.
- [`docs/KEYBINDINGS.md`](file:///E:/Work/arch-dotfiles/docs/KEYBINDINGS.md) — Complete keyboard shortcuts reference.
- [`docs/TROUBLESHOOTING.md`](file:///E:/Work/arch-dotfiles/docs/TROUBLESHOOTING.md) — Diagnostic tips for PipeWire, Wi-Fi, and bootloader.
- [`docs/CONTRIBUTING.md`](file:///E:/Work/arch-dotfiles/docs/CONTRIBUTING.md) — Code style guidelines, test execution, and PR workflow.
- [`docs/SECURITY.md`](file:///E:/Work/arch-dotfiles/docs/SECURITY.md) — Dual-boot safety invariants and secret sanitization.

---

## 🧪 Testing & Verification

Run the automated test suite locally:
```bash
# Run all 70 unit tests
python -m pytest tests/

# Statically validate QML syntax and theme JSON files
python tests/test_qml_syntax.py
```

---

## 📄 License
Released under the [MIT License](LICENSE).
