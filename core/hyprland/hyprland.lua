-- =============================================================================
-- CUSTOM ARCH LINUX DESKTOP ENVIRONMENT — HYPRLAND MASTER CONFIGURATION
-- Engine: Hyprland 0.55+ (Native Lua Configuration)
-- Hardware Target: HP EliteBook 840 G5 (Intel UHD 620, 8GB RAM)
-- =============================================================================

-- Ensure local module path resolution works dynamically
local script_dir = debug.getinfo(1, "S").source:sub(2):match("(.*/)")
if script_dir then
    package.path = script_dir .. "?.lua;" .. script_dir .. "?/init.lua;" .. package.path
end

-- -----------------------------------------------------------------------------
-- 1. Global Compositor Identification & Environment Variables
-- -----------------------------------------------------------------------------
hl.env("XDG_CURRENT_DESKTOP", "Hyprland")
hl.env("XDG_SESSION_TYPE", "wayland")
hl.env("XDG_SESSION_DESKTOP", "Hyprland")

-- Toolkit Backend Configuration (Native Wayland)
hl.env("GDK_BACKEND", "wayland,x11,*")
hl.env("QT_QPA_PLATFORM", "wayland;xcb")
hl.env("QT_QPA_PLATFORMTHEME", "qt6ct")
hl.env("QT_WAYLAND_DISABLE_WINDOWDECORATION", "1")
hl.env("QT_AUTO_SCREEN_SCALE_FACTOR", "1")
hl.env("SDL_VIDEODRIVER", "wayland")
hl.env("CLUTTER_BACKEND", "wayland")

-- Cursor & Scaling
hl.env("XCURSOR_SIZE", "24")
hl.env("HYPRCURSOR_SIZE", "24")
hl.env("XCURSOR_THEME", "Adwaita")

-- Hardware Acceleration (Intel 8th Gen UHD 620)
hl.env("LIBVA_DRIVER_NAME", "iHD")

-- -----------------------------------------------------------------------------
-- 2. Modular Configuration Imports
-- -----------------------------------------------------------------------------
-- Monitors & Multi-Display Setup
require("modules.monitors")

-- Input Devices, Touchpad & Gestures
require("modules.input")

-- Layouts, Gaps & Window Spacing
require("modules.layout")

-- Dynamic & Named Workspaces
require("modules.workspaces")

-- Ergonomic Keybindings & Mouse Bindings
require("modules.keybindings")

-- Window Rules & Floating Dialog Pinning
require("modules.windowrules")

-- Hardware-Restrained Animations (Intel UHD 620 Optimized)
require("modules.animations")

-- User Services & Autostart Daemons
require("modules.autostart")
