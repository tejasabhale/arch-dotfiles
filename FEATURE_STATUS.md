# Feature Status Matrix — Custom Arch Linux Desktop + June AI

> **Status Legend:**
> - ⚪ **Not Started**: Specification defined; implementation not yet begun.
> - 🟡 **In Development**: Code authored; active work underway.
> - 🔵 **Implemented**: Code written, statically validated; awaiting runtime hardware testing.
> - 🟣 **Tested**: Verified on Arch Linux runtime environment (or VM/container where applicable).
> - 🟢 **Completed**: Fully implemented, tested, verified on target hardware, and documented.

---

## 1. Core Compositor Layer (Hyprland 0.55+ Lua)

| Feature | Status | Target Path | Notes |
|---|---|---|---|
| Main Entry Point (`hyprland.lua`) | 🔵 Implemented | `core/hyprland/hyprland.lua` | Uses global `hl` table API |
| Monitor Detection & Scaling | 🔵 Implemented | `core/hyprland/modules/monitors.lua` | HP EliteBook 840 G5 (eDP-1) + Hotplug |
| Input & Touchpad Gestures | 🔵 Implemented | `core/hyprland/modules/input.lua` | Natural scroll, tap-to-click, gestures |
| Keybindings System | 🔵 Implemented | `core/hyprland/modules/keybindings.lua` | Keyboard-driven ergonomics |
| Layout Configuration (Dwindle/Master) | 🔵 Implemented | `core/hyprland/modules/layout.lua` | Gaps, borders, split ratios |
| Window Rules & Floating Dialogs | 🔵 Implemented | `core/hyprland/modules/windowrules.lua` | Proper classes, PiP, dialog pins |
| Hardware-Optimized Animations | 🔵 Implemented | `core/hyprland/modules/animations.lua` | Restrained curves for Intel iGPU |
| Autostart Services & Daemons | 🔵 Implemented | `core/hyprland/modules/autostart.lua` | Quickshell, Polkit, PipeWire, Daemons |
| Kitty Terminal Configuration | 🔵 Implemented | `config/kitty/kitty.conf` | Theme-linked, fast GPU rendering |
| Fish Shell Environment | 🔵 Implemented | `config/fish/config.fish` | Interactive prompt, aliases, paths |

---

## 2. Desktop Shell Layer (Quickshell / QML)

| Feature | Status | Target Path | Notes |
|---|---|---|---|
| Shell Root & Multi-Monitor Anchor | 🔵 Implemented | `shell/shell.qml` | `ShellRoot`, `Variants` across screens |
| Centralized Theme Token Engine | 🔵 Implemented | `shell/services/ThemeService.qml` | Reactive palette & design tokens |
| Theme Presets (Midnight, Nordic, Forest, Violet) | 🔵 Implemented | `themes/*.json` | High contrast, accessible color ramps |
| Reusable UI Primitives | 🔵 Implemented | `shell/components/` | Button, Card, Switch, Slider, Pill, etc. |
| Top Bar (Status, Clock, Indicators) | 🔵 Implemented | `shell/panels/TopBar.qml` | Fully modular widget ordering |
| Application Dock | 🔵 Implemented | `shell/dock/Dock.qml` | Pinned apps, running state, autohide |
| Workspace Overview & Window Picker | 🔵 Implemented | `shell/overview/Overview.qml` | Live previews via `Quickshell.Hyprland` |
| Application Launcher (Fuzzy Search) | 🔵 Implemented | `shell/launcher/Launcher.qml` | Apps, math, web, files, commands |
| Quick-Settings Control Center | 🔵 Implemented | `shell/control-center/ControlCenter.qml` | Toggles for Wi-Fi, BT, Audio, Power |
| Notification Center & OSD | 🔵 Implemented | `shell/notifications/` | Freedesktop spec, history, DND mode |
| System Tray Widget | 🔵 Implemented | `shell/widgets/SystemTrayWidget.qml` | SNI protocol support |

---

## 3. System Integration & Hardware Controls

| Feature | Status | Target Path | Notes |
|---|---|---|---|
| Wi-Fi Manager (NetworkManager D-Bus) | 🔵 Implemented | `system/wifi/` | Scan, connect, disconnect, signal stats |
| Dedicated Wi-Fi Hotspot GUI | 🔵 Implemented | `system/hotspot/` | AP mode check, QR code, WPA2/3, clients |
| Bluetooth Manager (BlueZ D-Bus) | 🔵 Implemented | `system/bluetooth/` | Scan, pair, disconnect, battery info |
| Audio Control (PipeWire / WirePlumber) | 🔵 Implemented | `system/audio/` | Sinks, sources, per-application streams |
| Brightness Controls (`brightnessctl`) | 🔵 Implemented | `system/brightness/` | Backlight curve, smooth transitions |
| Battery & Power Profiles (UPower) | 🔵 Implemented | `system/battery/`, `system/power/` | Health, remaining time, power-profiles |
| Idle & Lock Management (`hyprlock`/`hypridle`) | 🔵 Implemented | `core/services/idle/` | Timeout dimming, secure locking |
| Touchpad & Lid-Close Behavior | ⚪ Not Started | `system/power/lid.lua` | Suspend on lid close, disable screen |

---

## 4. Productivity Suite

| Feature | Status | Target Path | Notes |
|---|---|---|---|
| Clipboard Manager (`cliphist`) | 🔵 Implemented | `productivity/clipboard/` | History, search, pinned clips, clear |
| Productivity Dashboard | 🔵 Implemented | `shell/dashboard/Dashboard.qml` | Clock, tasks, calendar, system vitals |
| Screenshot Utility (`grim` + `slurp`) | 🔵 Implemented | `productivity/screenshots/` | Region, window, full, copy/save |
| Screen Recording (`wf-recorder`) | 🔵 Implemented | `productivity/screenshots/` | Full desktop/region capture with audio |
| Quick Notes & Tasks | 🔵 Implemented | `productivity/notes/` | Markdown notes with local JSON |
| Pomodoro Timer | 🔵 Implemented | `shell/dashboard/Dashboard.qml` | Work/break intervals, countdown |
| Calculator & Unit Converter | ⚪ Not Started | `productivity/calculator/` | Expression evaluation, currency/unit math |

---

## 5. Developer Tools Module

| Feature | Status | Target Path | Notes |
|---|---|---|---|
| Project Launcher | 🔵 Implemented | `developer/project_launcher/` | Fast open in VS Code, Kitty, browser |
| Git Status & Commit Helper | 🔵 Implemented | `developer/git/` | Current branch, diff check, safe staging |
| Python / Virtualenv Manager | 🔵 Implemented | `developer/python/` | Detect venv, conda, uv, launch Jupyter |
| Node.js / NPM Scripts Runner | 🔵 Implemented | `developer/node/` | Read package.json, run dev servers |
| Listening Ports Inspector | 🔵 Implemented | `developer/ports/` | Live TCP/UDP socket & process viewer |
| SSH Connection Shortcuts | 🔵 Implemented | `developer/ssh/` | Parse `~/.ssh/config`, quick terminal connect |
| Developer Hub UI | 🔵 Implemented | `developer/DeveloperHub.qml` | Unified multi-tab developer control deck |

---

## 6. June AI Assistant

| Feature | Status | Target Path | Notes |
|---|---|---|---|
| Core Daemon & IPC Protocol | 🔵 Implemented | `assistant/core/daemon.py` | Standalone Python daemon, Unix socket & JSON-RPC |
| Assistant Floating UI Window | 🔵 Implemented | `assistant/interface/AssistantWindow.qml` | Markdown, streaming tokens, prompt chips |
| Provider Engine (OpenAI, Gemini, Ollama) | 🔵 Implemented | `assistant/providers/` | Modular adapter pattern + offline fallback |
| Identity & Display Name Customizer | 🔵 Implemented | `assistant/core/identity.py` | Configurable name (default "June"), presets |
| Action Planning Engine | 🔵 Implemented | `assistant/action_planner/planner.py` | Step decomposition, AST, risk tiers |
| Controlled Desktop Executor | 🔵 Implemented | `assistant/executor/controlled_executor.py` | Strict allowlisted command dispatcher |
| Security Approval Flow & Emergency Stop | 🔵 Implemented | `assistant/permissions/` / `daemon.py` | Confirmation dialogs, abort execution |
| Screen Intelligence (OCR / Multimodal) | 🔵 Implemented | `assistant/screen_intelligence/` | Opt-in screen capture, vision analysis |
| Scoped File Intelligence | 🔵 Implemented | `assistant/file_intelligence/` | User-approved folder indexing & search |
| Local AI Memory Engine (SQLite) | 🔵 Implemented | `assistant/memory/memory_manager.py` | Preference tracking, credential sanitization |
| Web Research & Summarization | 🔵 Implemented | `assistant/research/` | Autonomous search & citation engine |
| Voice Engine (Push-to-talk & Wake Word) | 🔵 Implemented | `assistant/voice/` | Opt-in microphone listener & TTS |

---

## 7. Multilingual Engine (English, Hindi, Marathi)

| Feature | Status | Target Path | Notes |
|---|---|---|---|
| 7 Language Combinations Router | 🔵 Implemented | `assistant/languages/router.py` | EN, HI, MR and all pairwise/triplet mixes |
| Code-Switching Detection | 🔵 Implemented | `assistant/languages/detector.py` | Disambiguates Devanagari Hindi/Marathi |
| Romanized Script Support (Hinglish/Maranglish) | 🔵 Implemented | `assistant/languages/romanized.py` | Transliteration and phonetic command parsing |
| Multilingual Speech-to-Text | 🔵 Implemented | `assistant/speech_to_text/stt_service.py` | Whisper / Cloud STT for Indian accents |
| Multilingual Text-to-Speech | 🔵 Implemented | `assistant/text_to_speech/tts_service.py` | Natural intonation across EN, HI, MR |
| Language Settings GUI | 🔵 Implemented | `assistant/languages/LanguageSettings.qml` | 7 combination presets & mirror modes |

---

## 8. Centralized Settings & Feature Management

| Feature | Status | Target Path | Notes |
|---|---|---|---|
| Settings Application Shell | 🔵 Implemented | `shell/settings/SettingsApp.qml` | 22 categories, search bar, clean nav |
| Modular Feature Manager | 🔵 Implemented | `shell/settings/FeatureManager.qml` | True process shutdown on toggle |
| Centralized JSON Storage Engine | 🔵 Implemented | `config/manager.py` / QML binding | `~/.config/tejas-os/` atomic writes |
| Performance Profile Switcher | 🔵 Implemented | `shell/settings/pages/PerformancePage.qml` | Balanced, Performance, Battery, Full |
| Backup & Recovery Panel | 🔵 Implemented | `shell/settings/pages/BackupPage.qml` | Snapshot, restore, reset defaults |

---

## 9. Installer, Backup & Documentation

| Feature | Status | Target Path | Notes |
|---|---|---|---|
| Non-destructive Installer Script | 🔵 Implemented | `install.sh` | Safe dual-boot, no partition touches |
| Dry-Run Mode & Dependency Pre-flight | 🔵 Implemented | `install.sh --dry-run` | Validates packages before installation |
| Configuration Backup Engine | 🔵 Implemented | `backup/backup.sh` | Timestamped tarball of existing dotfiles |
| Uninstaller & Rollback | 🔵 Implemented | `uninstall.sh` | Cleanly restores prior configuration |
| Project Plan & Status Documents | 🟢 Completed | Root directory | `PROJECT_PLAN.md`, `FEATURE_STATUS.md` |
| Master Architecture Specification | 🟢 Completed | `ARCHITECTURE.md` | In-depth architecture specification |
| Technical Dependency Catalog | 🟢 Completed | `DEPENDENCIES.md` | Complete Arch package catalog |
| Testing Strategy & Matrix | 🟢 Completed | `TESTING.md` | Verification matrix & test strategy |
| Full Suite of Docs (12 Guides + README) | 🟢 Completed | `docs/` | Comprehensive, zero-placeholder guides |
