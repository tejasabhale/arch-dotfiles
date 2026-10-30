-- =============================================================================
-- HYPRLAND MODULE: USER SERVICES & AUTOSTART DAEMONS
-- Target: Zero-redundancy, battery-conscious startup services
-- =============================================================================

hl.config({
    exec_once = {
        -- 1. Wayland & D-Bus Environment Propagation
        "dbus-update-activation-environment --systemd WAYLAND_DISPLAY XDG_CURRENT_DESKTOP=Hyprland",
        "systemctl --user import-environment WAYLAND_DISPLAY XDG_CURRENT_DESKTOP",

        -- 2. Polkit Authentication Agent (KDE / Qt6)
        "/usr/lib/polkit-kde-authentication-agent-1",

        -- 3. Quickshell Desktop Shell
        "quickshell",

        -- 4. Idle & Screen Lock Management
        "hypridle",

        -- 5. Animated Wallpaper Daemon
        "swww-daemon --format xrgb",

        -- 6. Clipboard History Persistence (Text & Images)
        "wl-paste --type text --watch cliphist store",
        "wl-paste --type image --watch cliphist store",

        -- 7. June AI Personal Assistant Core Daemon (Background Service)
        "python3 -m assistant.core.daemon"
    }
})
