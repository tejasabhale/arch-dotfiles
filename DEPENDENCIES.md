# Technical Dependency Catalog — Custom Arch Linux Desktop + June AI

This document enumerates all system packages, fonts, libraries, and utilities required to run the desktop environment. Dependencies are cleanly partitioned into **Official Arch Packages**, **AUR Packages**, and **Optional Packages**, ensuring total transparency during installation.

---

## 1. Official Arch Linux Packages (`pacman -S`)

### 1.1 Core Compositor & Wayland Infrastructure
| Package | Role | Necessity |
|---|---|---|
| `hyprland` | Dynamic tiling Wayland compositor (v0.55+ with Lua support) | **Mandatory** |
| `hyprlock` | Fast, GPU-accelerated Wayland screen locker | **Mandatory** |
| `hypridle` | Wayland idle daemon for screen sleep and auto-lock | **Mandatory** |
| `xdg-desktop-portal-hyprland` | Desktop portal backend for Wayland screen sharing and file dialogues | **Mandatory** |
| `xdg-desktop-portal-gtk` | Fallback portal for file picker and GTK integrations | Recommended |
| `polkit-kde-agent` | Polkit authentication agent for privileged system prompts | **Mandatory** |
| `qt5-wayland` | Qt5 Wayland windowing system plugin | Recommended |
| `qt6-wayland` | Qt6 Wayland windowing system plugin (Quickshell compatibility) | **Mandatory** |

### 1.2 Audio & Multimedia Subsystem
| Package | Role | Necessity |
|---|---|---|
| `pipewire` | Modern multimedia and low-latency audio server | **Mandatory** |
| `pipewire-audio` | PipeWire audio client libraries | **Mandatory** |
| `pipewire-pulse` | PulseAudio replacement daemon for application compatibility | **Mandatory** |
| `pipewire-alsa` | ALSA audio routing into PipeWire | **Mandatory** |
| `wireplumber` | Session and policy manager for PipeWire | **Mandatory** |
| `playerctl` | Command-line MPRIS controller for media players | Recommended |

### 1.3 Networking, Hotspot & Bluetooth
| Package | Role | Necessity |
|---|---|---|
| `networkmanager` | Network connection daemon (Wi-Fi, Ethernet, Hotspot AP) | **Mandatory** |
| `bluez` | Bluetooth protocol stack daemon | **Mandatory** |
| `bluez-utils` | Bluetooth control utilities (`bluetoothctl`) | **Mandatory** |
| `iw` | CLI tool for wireless devices (AP mode capability inspection) | **Mandatory** |
| `wireless_tools` | Legacy wireless manipulation tools (`iwconfig`) | Recommended |
| `dnsmasq` | Lightweight DHCP and caching DNS server (for Hotspot internet sharing) | **Mandatory for Hotspot** |
| `iptables` | Packet filtering and NAT forwarding (used by NetworkManager for sharing) | **Mandatory for Hotspot** |
| `qrencode` | QR Code generator for instantaneous Wi-Fi hotspot sharing | Recommended |

### 1.4 Hardware Acceleration & Laptop Support (HP EliteBook 840 G5)
| Package | Role | Necessity |
|---|---|---|
| `mesa` | Open-source OpenGL and Vulkan drivers | **Mandatory** |
| `vulkan-intel` | Intel Vulkan driver for UHD Graphics 620 | **Mandatory** |
| `intel-media-driver` | VA-API hardware video acceleration for Intel 8th Gen | Recommended |
| `brightnessctl` | Lightweight backlight and keyboard LED controller | **Mandatory** |
| `upower` | Power management service and battery level abstraction | **Mandatory** |
| `power-profiles-daemon` | DBus daemon for switching performance/balanced/power-saver modes | Recommended |

### 1.5 Terminal, Shell & Core Utilities
| Package | Role | Necessity |
|---|---|---|
| `kitty` | Fast, GPU-accelerated terminal emulator | **Mandatory** |
| `fish` | Smart, user-friendly interactive command-line shell | **Mandatory** |
| `dolphin` | Full-featured KDE file manager | **Mandatory** |
| `wl-clipboard` | Wayland command-line clipboard utility (`wl-copy`, `wl-paste`) | **Mandatory** |
| `cliphist` | Wayland clipboard history manager (text + images) | Recommended |
| `grim` | Wayland screenshot utility | **Mandatory for Screenshots** |
| `slurp` | Interactive region selector for Wayland | **Mandatory for Screenshots** |
| `wf-recorder` | Wayland screen recording tool | Recommended |
| `jq` | Lightweight command-line JSON processor | **Mandatory** |
| `socat` | Multipurpose relay tool for Hyprland UNIX socket IPC | **Mandatory** |

### 1.6 Typography & Multilingual Fonts (English, Hindi, Marathi)
| Package | Role | Necessity |
|---|---|---|
| `ttf-jetbrains-mono-nerd` | Primary monospace font with programming ligatures & glyphs | **Mandatory** |
| `noto-fonts` | Google Noto standard sans-serif and serif fonts | **Mandatory** |
| `noto-fonts-cjk` | Noto fonts for Asian glyphs and symbols | Recommended |
| `noto-fonts-emoji` | Full-color emoji font | **Mandatory** |
| `noto-fonts-extra` | Extended scripts including high-fidelity Devanagari | **Mandatory for Hindi/Marathi** |

---

## 2. AUR Packages (`yay -S` / `paru -S`)

| Package | Role | Necessity |
|---|---|---|
| `quickshell` (or `quickshell-git`) | QtQuick desktop shell engine powered by QML | **Mandatory** |
| `swww` (or `hyprpaper`) | Efficient, animated Wayland wallpaper daemon | Recommended |
| `fuzzel` | Fast Wayland application launcher (lightweight fallback) | Recommended |
| `libsecret` | Desktop Secret Service provider for secure API key storage | **Mandatory for June AI** |

---

## 3. Python Environment & June AI Dependencies

The June assistant runtime operates under Python 3.12+ (isolated venv or system packages):

```text
# Core Assistant Runtime
python >= 3.12
python-gobject         # DBus and system signal bindings
python-dbus            # Desktop integration
sqlite3                # Persistent memory and message cache

# Cloud AI Provider Adapters (Installed via pip inside June venv)
google-genai           # Google Gemini API client
openai                 # OpenAI compatible API client
anthropic              # Claude API client
requests               # HTTP networking
pydantic               # Action planner schema validation

# Optional Voice & Multilingual Libraries (On-demand)
faster-whisper         # Lightweight local Speech-To-Text (optional local inference)
sounddevice            # Audio recording and playback
piper-tts              # Fast, lightweight neural Text-To-Speech
```

---

## 4. Verification Check Commands

To verify installed status on an Arch Linux system:
```bash
# Check official packages
pacman -Q hyprland quickshell kitty fish pipewire networkmanager bluez

# Check hardware video acceleration
vainfo

# Check wireless AP capability
iw list | grep -A 10 "Supported interface modes" | grep "AP"
```
