-- =============================================================================
-- HYPRLAND MODULE: INPUT DEVICES, KEYBOARD & TOUCHPAD
-- Target: HP EliteBook 840 G5 Precision Touchpad & Ergonomics
-- =============================================================================

hl.config({
    input = {
        kb_layout = "us",
        kb_variant = "",
        kb_model = "",
        kb_options = "",
        kb_rules = "",

        -- Fast key repeat rates for developer productivity
        repeat_rate = 50,
        repeat_delay = 300,

        -- Focus follows cursor movement
        follow_mouse = 1,
        float_switch_override_focus = 2,
        mouse_refocus = true,

        -- HP EliteBook Precision Clickpad Configuration
        touchpad = {
            natural_scroll = true,
            tap_to_click = true,
            clickfinger_behavior = true,
            drag_lock = false,
            scroll_factor = 0.85,
            middle_button_emulation = false,
        },

        -- Standard mouse pointer sensitivity (neutral)
        sensitivity = 0,
        accel_profile = "adaptive",
    },

    -- 3-Finger Touchpad Workspace Gestures
    gestures = {
        workspace_swipe = true,
        workspace_swipe_fingers = 3,
        workspace_swipe_distance = 280,
        workspace_swipe_invert = true,
        workspace_swipe_min_speed_to_force = 30,
        workspace_swipe_cancel_ratio = 0.4,
        workspace_swipe_create_new = false,
        workspace_swipe_forever = true,
    }
})
