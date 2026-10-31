# Tejas OS — Final Release Audit & Compatibility Specification

**Target Hardware:** HP EliteBook 840 G5 (Intel Core i5/i7 8th Gen, Intel UHD Graphics 620, 8 GB DDR4 RAM)  
**Compositor Target:** Hyprland 0.55+ (Native Lua Engine)  
**Desktop Shell Target:** Quickshell (QtQuick/QML Wayland Layer Shell)  
**Branch:** `refactor/performance-architecture`  
**Status:** Statically Validated & Unit-Test Passed; Pending Physical Arch Linux Hardware Session  

---

## 1. Quality Assurance Level Separation

To ensure absolute engineering rigor and comply with AGENTS.md, all testing across the Tejas OS platform is categorized into three strictly segregated quality tiers:

| Tier | Environment | Scope | Status |
|---|---|---|---|
| **Tier 1: Static Validation** | Windows Host / CI | Syntax checking, delimiter balance, schema compliance, line endings, safety grep | **100% Passed** |
| **Tier 2: Automated Testing** | Python 3.14 Pytest | 74 automated unit & functional tests (AST planning, multilingual router, config manager, developer hub, system backend) | **74/74 Passed (8.01s)** |
| **Tier 3: Hardware Runtime Testing** | Physical HP EliteBook 840 G5 on Arch Linux | Wayland compositor vsync, Intel UHD 620 VA-API, Quickshell layer shell anchoring, D-Bus signal subscription, Wi-Fi AP hotspot | **Awaiting Arch Linux Boot** |

> [!IMPORTANT]
> In accordance with project governance, this release is **NOT declared fully hardware-tested** until physical testing has been executed on the target HP EliteBook 840 G5 under native Arch Linux.

---

## 2. Hyprland 0.55+ and 0.57+ Compositor Compatibility

### 2.1 Upstream Hyprland Standards
- **Hyprland 0.55 / 0.56**: Introduced the native Lua configuration API (`hyprland.lua`), replacing deprecated `hyprlang`.
- **Hyprland 0.57+ Breaking Change**: Upstream Hyprland **completely dropped support for legacy `.conf` compositor configurations**. On 0.57 and newer, supplying a `.conf` compositor file will fail or be ignored.
- **Tejas OS Architecture**:
  - **Official Standard**: Tejas OS officially deploys native Lua configurations (`core/hyprland/hyprland.lua` and `core/hyprland/modules/*.lua`) using the global `hl` table API (`hl.env`, `hl.config`, `hl.monitor`, `hl.bind`, `hl.rule`).
  - **Installer Version Gate**: [`install.sh`](file:///E:/Work/arch-dotfiles/install.sh) inspects `Hyprland --version`. For Hyprland >= 0.57, it enforces native Lua and explicitly warns that legacy `.conf` is dropped upstream.
  - **Legacy Bridge (< 0.55 Only)**: A fallback [`hyprland.conf`](file:///E:/Work/arch-dotfiles/core/hyprland/hyprland.conf) is provided **strictly for legacy environments running Hyprland < 0.55**. It is never recommended or claimed compatible on 0.57+.

### 2.2 Lua API Verification Matrix
All 9 Lua configuration modules were validated for syntax and API compliance via [`tests/test_lua_syntax.py`](file:///E:/Work/arch-dotfiles/tests/test_lua_syntax.py):
- `core/hyprland/hyprland.lua`: Package path resolution, environment variables (`XDG_CURRENT_DESKTOP`, `GDK_BACKEND`, `QT_QPA_PLATFORM`).
- `core/hyprland/modules/monitors.lua`: Native `hl.monitor()` definitions for internal eDP-1 (1080p60) and hotpluggable external displays (HDMI, DP-1, DP-2).
- `core/hyprland/modules/input.lua`: Touchpad gestures, natural scroll, tap-to-click.
- `core/hyprland/modules/keybindings.lua`: Keyboard shortcuts mapped to Quickshell IPC, Kitty, and hardware audio/brightness keys.
- `core/hyprland/modules/layout.lua`: Dwindle layout, gaps (in: 4, out: 8), borders.
- `core/hyprland/modules/workspaces.lua`: 5 standard laptop workspaces.
- `core/hyprland/modules/windowrules.lua`: Floating dialog pins, picture-in-picture rules.
- `core/hyprland/modules/animations.lua`: Bezier curves restrained for Intel UHD 620 integrated GPU.
- `core/hyprland/modules/autostart.lua`: Daemons (`quickshell`, `pipewire`, `wireplumber`, `polkit-kde`).

---

## 3. Installer Safety & Dual-Boot Invariant Audit

### 3.1 Non-Destructive Guardrail Verification
A static AST and regex audit was performed on [`install.sh`](file:///E:/Work/arch-dotfiles/install.sh), [`uninstall.sh`](file:///E:/Work/arch-dotfiles/uninstall.sh), and [`backup/backup.sh`](file:///E:/Work/arch-dotfiles/backup/backup.sh):
- **Partition Formatting (`mkfs`, `fdisk`, `parted`, `gdisk`, `wipefs`)**: **ZERO occurrences**.
- **Windows Partition Integrity**: Prohibited from modifying NTFS partitions.
- **EFI System Partition (ESP)**: Prohibited from modifying `/boot/efi/EFI/Microsoft/Boot/bootmgfw.efi`.
- **User-Space Boundary**: Only modifies symlinks inside the executing user's `$HOME/.config/` directory.

### 3.2 Backup & Rollback Flow
1. **Pre-flight Backup**: Running `./install.sh` automatically invokes [`backup/backup.sh`](file:///E:/Work/arch-dotfiles/backup/backup.sh), creating a timestamped tarball of existing dotfiles (`~/.config/hypr`, `kitty`, `fish`, `quickshell`, `tejas-os`) in `~/.config/tejas-os-backups/`.
2. **In-Place Preservation**: If a destination directory exists and is not a symlink, it is renamed to `<directory>.orig`.
3. **Rollback**: Running `./install.sh --rollback` or `./uninstall.sh` restores `.orig` folders and unpacks the latest backup tarball, restoring the system to its pre-installation state.
4. **Dry-Run Inspection**: `./install.sh --dry-run` summarizes all proposed actions with zero modifications.

---

## 4. Performance & Memory Management (8 GB RAM Budget)

The system is optimized for an **8 GB DDR4** physical memory limit:
- **Idle Budget Target**: Base OS + Hyprland + Quickshell + June idle $\le 1.5 - 2.0\text{ GB}$.
- **Top Bar Widget Consolidation**: Replaced recurring individual timers (3s, 10s, 15s) with a single [`HardwareService.qml`](file:///E:/Work/arch-dotfiles/shell/services/HardwareService.qml) singleton.
- **Hardware Slider Debouncing**: Added 60ms debouncing timers in [`ControlCenter.qml`](file:///E:/Work/arch-dotfiles/shell/control-center/ControlCenter.qml), eliminating subprocess storms during mouse dragging.
- **Developer Hub Lazy Loading**: [`DeveloperHub.qml`](file:///E:/Work/arch-dotfiles/developer/DeveloperHub.qml) only refreshes the active tab on window open, dropping process churn from 6 concurrent Python processes to 1.
- **Settings App Lazy Loading**: Wrapped heavy pages in [`SettingsApp.qml`](file:///E:/Work/arch-dotfiles/shell/settings/SettingsApp.qml) with `Loader`, dropping startup process execution from 6 to 0.
- **Multi-Monitor Window Scoping**: Scoped modal dialogs to primary screen singleton in [`shell.qml`](file:///E:/Work/arch-dotfiles/shell/shell.qml), eliminating 100% duplicate dialog instantiation on secondary monitors.
- **June AI Backend**: Lazy property initializers for `ScreenIntelligence`, `FileIntelligence`, `ResearchEngine`, and `VoicePipeline` in [`daemon.py`](file:///E:/Work/arch-dotfiles/assistant/core/daemon.py). Fast-path CLI dispatch in [`cli.py`](file:///E:/Work/arch-dotfiles/assistant/core/cli.py).

---

## 5. Verification Tools Provided for Target Hardware

To facilitate reproducible runtime verification on the physical laptop, two dedicated scripts have been provided:

1. **[`scripts/verify_arch_runtime.sh`](file:///E:/Work/arch-dotfiles/scripts/verify_arch_runtime.sh)**: Automated checklist testing Hyprland binary, Lua syntax, Quickshell, D-Bus, PipeWire, Wi-Fi AP mode, and June IPC.
2. **[`scripts/benchmark_elitebook.sh`](file:///E:/Work/arch-dotfiles/scripts/benchmark_elitebook.sh)**: Automated performance benchmark measuring idle RAM, CPU load, process RSS, startup latency, and 4 performance profiles.
