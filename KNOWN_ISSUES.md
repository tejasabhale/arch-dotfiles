# Tejas OS — Known Issues, Upstream Considerations & Hardware Constraints

This document catalogs technical limitations, upstream compositor changes, and hardware considerations for **Tejas OS** running on the **HP EliteBook 840 G5**.

---

## 1. Upstream Hyprland Compositor Architecture

### 1.1 Complete Removal of Legacy `.conf` in Hyprland 0.57+
- **Upstream Change**: Starting with Hyprland version 0.57, upstream Hyprland completely removed support for legacy `.conf` (hyprlang) compositor configurations.
- **Impact**: Any attempt to start Hyprland 0.57+ using a legacy `hyprland.conf` will fail or throw errors.
- **Tejas OS Mitigation**: Tejas OS has officially standardized on native Lua configurations (`core/hyprland/hyprland.lua` and `core/hyprland/modules/*.lua`). [`install.sh`](file:///E:/Work/arch-dotfiles/install.sh) enforces Lua configuration on 0.55+ and specifically warns that `.conf` is deprecated and dropped on 0.57+.
- **Legacy Fallback Note**: The [`core/hyprland/hyprland.conf`](file:///E:/Work/arch-dotfiles/core/hyprland/hyprland.conf) bridge is strictly for legacy installations (< 0.55). It is **not compatible with Hyprland 0.57+**.

---

## 2. Hardware Constraints (HP EliteBook 840 G5)

### 2.1 Intel UHD Graphics 620 & Compositor Blur
- **Constraint**: The Intel UHD Graphics 620 has no dedicated VRAM and shares system memory through dynamic allocation (UMA).
- **Behavior**: Excessive blur passes (> 3 passes) combined with large blur radii (> 8px) across multiple transparent layer shell windows can increase GPU memory bus pressure and cause transient frame drops below 60 FPS.
- **Mitigation**: The default `balanced` performance profile enforces restrained blur parameters (`passes: 2`, `size: 4`) and hardware-optimized cubic Bezier curves in [`core/hyprland/modules/animations.lua`](file:///E:/Work/arch-dotfiles/core/hyprland/modules/animations.lua). Users experiencing battery drain should switch to the `battery_saver` profile, which disables blur entirely.

### 2.2 Wi-Fi Hotspot on 5 GHz Band (Regulatory DFS)
- **Constraint**: The Intel Dual Band Wireless-AC 8265 chipset supports Access Point (AP) mode on 2.4 GHz unconditionally. However, creating a 5 GHz hotspot in Linux is subject to Dynamic Frequency Selection (DFS) radar detection regulations.
- **Behavior**: If no valid regulatory country domain is set (`CRDA`), the kernel driver may reject starting a hostapd / NetworkManager AP connection on 5 GHz channels.
- **Mitigation**: [`HotspotPanel.qml`](file:///E:/Work/arch-dotfiles/system/hotspot/HotspotPanel.qml) defaults to the 2.4 GHz band, ensuring 100% reliable connection with all smartphones without regulatory failure. To enable 5 GHz AP mode, set your country code via `sudo iw reg set <COUNTRY_CODE>` (e.g. `IN`, `US`).

### 2.3 8 GB RAM Limit & Local AI Model Inference
- **Constraint**: The physical RAM is 8.00 GB.
- **Behavior**: Loading a quantized 7B or 8B local language model via Ollama allocates 4.5 GB to 5.8 GB resident memory. Running this simultaneously with a modern web browser and VS Code can trigger kernel out-of-memory (OOM) killer invocations.
- **Mitigation**: In accordance with AGENTS.md Rule 3:
  1. Cloud API providers (Google Gemini, OpenAI) are the official, pre-configured default for June AI.
  2. Local SLM inference via Ollama is strictly opt-in and is never autostarted on boot.
  3. When local SLM is enabled, users should use lightweight 1B to 3B models (e.g., `qwen2.5:1.5b` or `llama3.2:3b`).

---

## 3. Platform & Testing Boundary

### 3.1 Static Windows Validation vs. Native Linux Runtime
- **Static Validation**: Code authored on Windows undergoes strict static analysis (LF line endings, syntax checking for Lua and QML, pytest unit tests).
- **Runtime Testing Requirement**: Wayland protocol interactions (`wlr-layer-shell`, PipeWire node negotiation, D-Bus property watches) cannot be executed under Windows.
- **Status Policy**: Features are categorized as `Implemented` after static and unit-test validation, and are only marked `Tested / Completed` after physical verification on Arch Linux using [`scripts/verify_arch_runtime.sh`](file:///E:/Work/arch-dotfiles/scripts/verify_arch_runtime.sh).
