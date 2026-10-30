-- =============================================================================
-- HYPRLAND MODULE: LAYOUT, GAPS, DECORATION & MISC
-- Target: Intel UHD 620 GPU Performance & Crisp Aesthetics
-- =============================================================================

hl.config({
    general = {
        gaps_in = 6,
        gaps_out = 12,
        border_size = 2,

        -- Theme accent colors (Midnight theme default: Indigo/Blue)
        ["col.active_border"] = "rgba(58a6ffee) rgba(1f6febee) 45deg",
        ["col.inactive_border"] = "rgba(30363dcc)",

        layout = "dwindle",
        resize_on_border = true,
        hover_icon_on_border = true,
        allow_tearing = false,
    },

    decoration = {
        rounding = 10,

        active_opacity = 1.0,
        inactive_opacity = 0.95,
        fullscreen_opacity = 1.0,

        -- Restrained blur: passes = 2 keeps 60 FPS on Intel UHD 620
        blur = {
            enabled = true,
            size = 5,
            passes = 2,
            new_optimizations = true,
            xray = false,
            ignore_opacity = true,
        },

        -- Lightweight subtle shadow
        shadow = {
            enabled = true,
            range = 12,
            render_power = 2,
            color = "rgba(00000033)",
        },
    },

    dwindle = {
        pseudotile = true,
        preserve_split = true,
        smart_split = false,
        smart_resizing = true,
        force_split = 2,
    },

    master = {
        new_status = "master",
        mfact = 0.55,
    },

    misc = {
        disable_hyprland_logo = true,
        disable_splash_rendering = true,
        force_default_wallpaper = 0,
        vrr = 0,
        mouse_move_enables_dpms = true,
        key_press_enables_dpms = true,
        animate_manual_resizes = false,
        animate_mouse_windowdragging = false,
        enable_swallow = true,
        swallow_regex = "^(kitty)$",
    }
})
