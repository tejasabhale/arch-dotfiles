-- =============================================================================
-- HYPRLAND MODULE: MONITORS & DISPLAY PROFILES
-- Target: HP EliteBook 840 G5 + Hotpluggable External Displays
-- =============================================================================

-- Internal laptop display (HP EliteBook 840 G5: 14" FHD IPS panel)
hl.monitor({
    output = "eDP-1",
    mode = "1920x1080@60",
    position = "0x0",
    scale = "1"
})

-- External HDMI output (typically on the right of the laptop)
hl.monitor({
    output = "HDMI-A-1",
    mode = "preferred",
    position = "auto-right",
    scale = "1"
})

-- External DisplayPort output via USB-C dock or dongle
hl.monitor({
    output = "DP-1",
    mode = "preferred",
    position = "auto-right",
    scale = "1"
})

hl.monitor({
    output = "DP-2",
    mode = "preferred",
    position = "auto-right",
    scale = "1"
})

-- Generic fallback for any newly plugged or unrecognized monitor
hl.monitor({
    output = "",
    mode = "preferred",
    position = "auto",
    scale = "1"
})
