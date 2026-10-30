# AGENTS.md — Master Project Guidelines & Rules

## Project Identity
**Project:** Custom Arch Linux Desktop Environment + June AI
**Target Host Hardware:** HP EliteBook 840 G5 (8GB RAM, Intel Core i5/i7 8th Gen, Intel UHD Graphics 620, Dual-boot UEFI with Windows)
**Primary Stack:** Arch Linux, Hyprland (0.55+ with Lua configuration), Quickshell (QtQuick/QML), Python 3.12+, Bash, Fish, Kitty.

---

## 1. Architectural Invariants & Rules

### Rule 1.1 — Hyprland Configuration Standard
- Hyprland 0.55+ uses Lua (`hyprland.lua`), replacing deprecated `hyprlang`.
- Use the official global `hl` table API: `hl.config()`, `hl.monitor()`, `hl.bind()`, `hl.env()`, `hl.on()`, `hl.dispatch()`, etc.
- Modularize Hyprland configurations using standard Lua `require("modules.<module_name>")`.
- Never generate deprecated `hyprland.conf` files or copy outdated tutorials.

### Rule 1.2 — Quickshell & QML Standard
- Build desktop shell components using verified Quickshell types: `ShellRoot`, `PanelWindow`, `Variants`, `Quickshell.screens`, `Quickshell.Hyprland`, `Quickshell.Wayland`, `Quickshell.Io.Process`.
- Do not invent nonexistent QML types or fake properties.
- Keep components modular and single-responsibility. Never cram the entire shell into one massive QML file.
- Separate view presentation (QML) from system logic (D-Bus, helper services, and shell scripts).

### Rule 1.3 — Centralized Configuration & Tokenized Theming
- All persistent configuration must live under `~/.config/tejas-os/` in structured JSON files (`features.json`, `settings.json`, `assistant.json`, `theme.json`, etc.).
- Never hardcode color hex codes, margins, or fonts in individual components.
- All UI components must read from centralized theme tokens (`Theme.accent`, `Theme.background`, `Theme.surface`, `Theme.text`, `Theme.radius`, `Theme.blur`).
- Four initial presets must be supported: **Midnight** (Dark Indigo), **Nordic Light** (Warm Light Blue), **Forest** (Earthy Dark Green), and **Violet** (Dark Purple).

### Rule 1.4 — Modular Feature Isolation & True Disabling
- Every feature must have an independent toggle in `features.json`.
- Disabling a feature MUST terminate or suspend its background processes and release system resources. Never just hide a button while leaving a daemon running.
- Re-enabling a feature must restore its prior state without data loss.
- Core system daemons (NetworkManager, BlueZ) must not be terminated when desktop graphical widgets are disabled.

### Rule 1.5 — Dual-Boot & System Safety (Non-Negotiable)
- The target system is dual-booted with Windows on UEFI.
- Under NO circumstance may any script, tool, or assistant action:
  - Format disks or partitions (`mkfs`, `fdisk`, `parted`).
  - Modify or wipe the Windows partition (NTFS).
  - Format or damage the EFI System Partition (ESP).
  - Alter the Windows bootloader (`bootmgfw.efi`).
  - Silently execute `sudo` or package manager commands without explicit user authorization.
- The installer is strictly a user-space dotfiles configurator and package installer. It is NOT an OS installer.

---

## 2. June AI Assistant Principles

### Rule 2.1 — Decoupling & Independent Operation
- June is an independent service communicating via local IPC (D-Bus / Unix socket / HTTP).
- The desktop shell must remain 100% operational when June is disabled or offline.
- Renaming the assistant (default: "June") via Settings must update display names cleanly without breaking internal service identifiers.

### Rule 2.2 — Security & Controlled Execution
- AI-generated commands must be treated as untrusted input.
- Execution must run through a strictly allowlisted `ActionPlanner` and `ControlledExecutor`.
- Any system-modifying or potentially destructive action must request explicit user approval before execution.
- Provide an instantaneous "Emergency Stop" button to abort running action plans.
- Never store API keys, tokens, or passwords in plain files or Git. Use system secret services (e.g., `libsecret` / `secret-tool`).

### Rule 2.3 — Multilingual Support (English, Hindi, Marathi)
- Full natural communication across English, Hindi, and Marathi in all 7 combinations (individual, pairwise, trilingual).
- Seamless mid-sentence code-switching (e.g., "June, majha VS Code project ughad").
- Handle both native Devanagari script and Romanized phonetics (Hinglish, Maranglish).
- Do not use simple script-based language identification because Hindi and Marathi share the Devanagari script; use context-aware N-gram or LLM-based identification.

---

## 3. Performance & Memory Management (8 GB RAM Budget)

- **Idle Budget:** Base desktop + shell idle memory must target $\le 1.5 - 2.0\text{ GB}$.
- **Event-Driven Architecture:** Avoid high-frequency polling loops (e.g. `setInterval(..., 100)`). Use D-Bus signal subscriptions, UDev events, and file watchers.
- **AI Inference Model:** Heavy LLM reasoning and multilingual generation default to cloud API providers. Local SLM/LLM inference is strictly opt-in, on-demand, and never autostarted on boot.
- **Performance Profiles:** Balanced (default), Performance, Battery Saver, Full Experience.

---

## 4. Development Workflow & Cross-Platform Rules

- **Authoring Platform:** Windows (Antigravity IDE / PowerShell / Git).
- **Runtime Platform:** Arch Linux (Wayland / Hyprland 0.55+).
- **Line Endings:** All shell scripts, Lua configs, QML files, and JSON schemas MUST use LF line endings (`eol=lf`).
- **Clean Commits:** Maintain clean, atomic commits for each completed phase.
- **Testing Verification:** Distinguish clearly between static verification (Windows syntax linting, schema validation) and runtime verification (Arch Linux Wayland session testing). Never claim a feature is complete until verified on real hardware.
