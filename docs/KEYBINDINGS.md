# Global Keybindings Cheatsheet

All keybindings use the **Super** key (Windows key on the HP EliteBook keyboard).
Defined in `core/hyprland/modules/keybindings.lua`.

## 1. System & Window Management

| Shortcut | Action | Description |
|---|---|---|
| `Super + Q` | Close Window | Gracefully close active window |
| `Super + M` | Exit Hyprland | Terminate current session |
| `Super + F` | Fullscreen | Toggle fullscreen mode |
| `Super + V` | Floating Mode | Toggle floating / tiling for active window |
| `Super + P` | Pseudo Tile | Preserve window aspect ratio in tiling |
| `Super + J` | Toggle Split | Rotate split direction (horizontal / vertical) |

---

## 2. Core Shell Applications & Overlays

| Shortcut | Action | Description |
|---|---|---|
| `Super + Return` | Open Terminal | Launches Kitty terminal with Fish shell |
| `Super + Space` | June AI Assistant | Summon floating voice/text AI assistant |
| `Super + D` | Developer Hub | Open multi-tab developer deck (Projects, Git, Ports, SSH) |
| `Super + I` | Settings App | Launch 22-category Centralized Settings App |
| `Super + A` | Application Launcher | Fuzzy search apps, web queries, math |
| `Super + Tab` | Workspace Overview | Visual expose window picker and switcher |
| `Super + C` | Control Center | Quick toggles for Wi-Fi, Bluetooth, Audio, Power |
| `Super + N` | Notification Center | View Freedesktop notification history |
| `Super + B` | Clipboard Panel | Search and paste from clipboard history |
| `Super + E` | File Manager | Open Dolphin file manager |
| `Super + Shift + T` | Cycle Theme | Toggle Midnight, Nordic Light, Forest, Violet |
| `Super + Escape` | Emergency Stop | Instantly abort any running June AI action plan |

---

## 3. Focus & Window Navigation

| Shortcut | Action |
|---|---|
| `Super + Left` / `H` | Move focus left |
| `Super + Right` / `L` | Move focus right |
| `Super + Up` / `K` | Move focus up |
| `Super + Down` / `J` | Move focus down |
| `Super + Shift + [H/J/K/L]` | Swap window in specified direction |

---

## 4. Workspace Navigation

| Shortcut | Action |
|---|---|
| `Super + 1` .. `9` | Switch to Workspace 1 through 9 |
| `Super + Shift + 1` .. `9` | Move active window to Workspace 1 through 9 |
| `Super + Mouse Scroll` | Scroll through active workspaces |

---

## 5. Media & Hardware Controls

| Key | Action |
|---|---|
| `XF86AudioRaiseVolume` | Increase volume by 5% |
| `XF86AudioLowerVolume` | Decrease volume by 5% |
| `XF86AudioMute` | Toggle audio mute |
| `XF86MonBrightnessUp` | Increase display brightness by 5% |
| `XF86MonBrightnessDown` | Decrease display brightness by 5% |
| `Print` | Interactive region screenshot (ScreenshotBar) |
| `Super + Print` | Fullscreen screenshot copied to clipboard |
