# Changelog — Tejas OS

All notable changes, optimizations, and architectural refactorings for the **Tejas OS** desktop environment and **June AI** assistant will be documented in this file.

---

## [Refactor] Performance & Language Architecture Optimization — 2026-10-31

### Desktop Shell & UI (Quickshell / QML)
- **Centralized Hardware Status Bridge (`shell/services/HardwareService.qml`)**:
  - Implemented a unified singleton service providing reactive bindings for Audio Volume, Network Wi-Fi status/SSID, Battery percentage/state, and display Brightness.
  - Replaced individual polling loops across `AudioWidget.qml` (previously 3s), `NetworkWidget.qml` (previously 10s), and `BatteryWidget.qml` (previously 15s) with single-source property bindings.
  - Eliminated process timer duplication on multi-monitor configurations.
- **Hardware Slider Debouncing (`shell/control-center/ControlCenter.qml`)**:
  - Implemented 60ms debouncing timers for Volume and Brightness sliders.
  - Eliminates command dispatch storms (reducing subprocess executions from 40-60/sec to <= 16/sec during mouse drags).
- **Developer Hub Lazy Tab Loading (`developer/DeveloperHub.qml`)**:
  - Replaced eager `refreshAll()` with `refreshCurrentTab(activeTab)`.
  - Opening Developer Hub now triggers only 1 background process instead of 6 concurrent Python processes.
  - Added safe post-action callbacks in `actionProc` to prevent asynchronous race conditions.
- **Settings App Lazy Loading (`shell/settings/SettingsApp.qml`)**:
  - Converted heavy settings pages (`FeatureManager`, `PerformancePage`, `BackupPage`) to dynamic QML `Loader` components.
  - Opening the Settings App on the Overview tab now launches zero background processes (was previously spawning 6 Python processes).
- **Feature Manager Double Execution Fix (`shell/settings/FeatureManager.qml`)**:
  - Removed redundant `running: true` on `featuresProc`.
  - Switched from inline Python string execution to direct CLI option `["python3", "-m", "config.manager", "--list-features", "--json"]`.
- **Multi-Monitor Modal Overlay Scoping (`shell/shell.qml`)**:
  - Scoped centered dialogs (`Launcher`, `ControlCenter`, `NotificationCenter`, `AssistantWindow`, `Dashboard`, `ClipboardPanel`, `ScreenshotBar`) to the primary screen.
  - Preserved multi-screen `Variants` for `TopBar` and `Dock` while eliminating 100% duplicate dialog instantiation on secondary monitors.

### Compositor & Window Manager (Hyprland)
- **Compositor Compatibility Bridge (`core/hyprland/hyprland.conf`)**:
  - Added a complete fallback configuration bridge for Hyprland versions < 0.55 while native `hyprland.lua` remains active for Hyprland 0.55+.
- **Automated Version Detection (`install.sh`)**:
  - Added pre-flight Hyprland version detection logic to identify installed release and select appropriate configuration format.

### June AI Backend (Python)
- **Lazy Engine Initializations (`assistant/core/daemon.py`)**:
  - Converted `ScreenIntelligence`, `FileIntelligence`, `ResearchEngine`, and `VoicePipeline` into lazy-initialized property getters with setters.
  - Eliminates startup heap allocation and background model loads for unused intelligence submodules.
- **Fast-Path IPC Dispatch (`assistant/core/cli.py`)**:
  - Implemented direct argument inspection fast-path for `--ping`, `--history`, and `--stop`.
  - Bypasses full `argparse` construction and heavy provider imports for common IPC pings.
- **Lazy Direct Dispatch Fallbacks (`assistant/core/client.py`)**:
  - Moved heavy fallback imports (`ProviderRegistry`, `ConversationStore`, `IdentityManager`) inside `_direct_dispatch`.
  - Sockets clients now import only minimal networking abstractions when communicating with the active daemon.

### Quality Assurance & Benchmarking
- **Automated Syntax Test Coverage**:
  - Integrated `tests/test_lua_syntax.py` and `tests/test_qml_syntax.py` into pytest test suite.
  - Full test suite expanded from 71 to 74 tests, all passing cleanly in 8.01s.
- **Documentation**:
  - Created `PERFORMANCE_AUDIT.md` (in-depth audit of subprocesses, polling loops, memory).
  - Created `LANGUAGE_MAPPING.md` (221-file inventory with language justifications and actions).
  - Created `MIGRATION_PLAN.md` (phased migration roadmap).
  - Created `PERFORMANCE_REPORT.md` (benchmark measurements pre- and post-refactor).
  - Updated `ARCHITECTURE.md`, `FEATURE_STATUS.md`, `TESTING.md`.
