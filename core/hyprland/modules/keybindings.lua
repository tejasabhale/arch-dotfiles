-- =============================================================================
-- HYPRLAND MODULE: KEYBOARD SHORTCUTS & MOUSE BINDINGS
-- Target: Fast, keyboard-driven navigation + HP EliteBook 840 G5 Fn Keys
-- =============================================================================

hl.config({
    bind = {
        -- Core Application Launchers
        "SUPER, Return, exec, kitty",
        "SUPER SHIFT, Return, exec, kitty --class kitty-float",
        "SUPER, E, exec, dolphin",
        "SUPER, B, exec, xdg-open https://",

        -- Shell Overlays & Assistant Interactions (Quickshell Integration)
        "SUPER, Space, exec, quickshell ipc call launcher toggle || fuzzel",
        "SUPER, J, exec, quickshell ipc call assistant toggle",
        "SUPER, C, exec, quickshell ipc call controlCenter toggle",
        "SUPER, Tab, exec, quickshell ipc call overview toggle",
        "SUPER, D, exec, quickshell ipc call dashboard toggle",
        "SUPER, N, exec, quickshell ipc call notifications toggle",

        -- Window Management & State
        "SUPER, Q, killactive,",
        "SUPER, V, togglefloating,",
        "SUPER, F, fullscreen, 0",
        "SUPER, M, fullscreen, 1",
        "SUPER, P, pseudo,",
        "SUPER, S, togglesplit,",
        "SUPER, G, togglegroup,",

        -- Window Focus Movement (Vim + Arrow Keys)
        "SUPER, left, movefocus, l",
        "SUPER, right, movefocus, r",
        "SUPER, up, movefocus, u",
        "SUPER, down, movefocus, d",
        "SUPER, H, movefocus, l",
        "SUPER, L, movefocus, r",
        "SUPER, K, movefocus, u",
        "SUPER, J, movefocus, d",

        -- Window Position Movement
        "SUPER SHIFT, left, movewindow, l",
        "SUPER SHIFT, right, movewindow, r",
        "SUPER SHIFT, up, movewindow, u",
        "SUPER SHIFT, down, movewindow, d",
        "SUPER SHIFT, H, movewindow, l",
        "SUPER SHIFT, L, movewindow, r",
        "SUPER SHIFT, K, movewindow, u",
        "SUPER SHIFT, J, movewindow, d",

        -- Switch Workspaces 1-5 (Primary Laptop Profiles)
        "SUPER, 1, workspace, 1",
        "SUPER, 2, workspace, 2",
        "SUPER, 3, workspace, 3",
        "SUPER, 4, workspace, 4",
        "SUPER, 5, workspace, 5",
        "SUPER, 6, workspace, 6",
        "SUPER, 7, workspace, 7",
        "SUPER, 8, workspace, 8",
        "SUPER, 9, workspace, 9",
        "SUPER, 0, workspace, 10",

        -- Move Active Window to Workspace
        "SUPER SHIFT, 1, movetoworkspace, 1",
        "SUPER SHIFT, 2, movetoworkspace, 2",
        "SUPER SHIFT, 3, movetoworkspace, 3",
        "SUPER SHIFT, 4, movetoworkspace, 4",
        "SUPER SHIFT, 5, movetoworkspace, 5",
        "SUPER SHIFT, 6, movetoworkspace, 6",
        "SUPER SHIFT, 7, movetoworkspace, 7",
        "SUPER SHIFT, 8, movetoworkspace, 8",
        "SUPER SHIFT, 9, movetoworkspace, 9",
        "SUPER SHIFT, 0, movetoworkspace, 10",

        -- Move Active Window Silently (Without switching focus)
        "SUPER CTRL, 1, movetoworkspacesilent, 1",
        "SUPER CTRL, 2, movetoworkspacesilent, 2",
        "SUPER CTRL, 3, movetoworkspacesilent, 3",
        "SUPER CTRL, 4, movetoworkspacesilent, 4",
        "SUPER CTRL, 5, movetoworkspacesilent, 5",

        -- Screenshots & Screen Capture
        ", Print, exec, grim - | wl-copy && notify-send 'Screenshot' 'Fullscreen copied to clipboard'",
        "SUPER SHIFT, S, exec, grim -g \"$(slurp)\" - | wl-copy && notify-send 'Screenshot' 'Selection copied to clipboard'",
        "SUPER CTRL, S, exec, grim -g \"$(slurp)\" ~/Pictures/Screenshots/$(date +'%Y-%m-%d_%H-%M-%S').png && notify-send 'Screenshot' 'Saved to ~/Pictures/Screenshots'",

        -- Lock & Session Management
        "SUPER, Escape, exec, hyprlock",
        "SUPER SHIFT, Escape, exit,"
    },

    -- Repeating Keys (e.g. Volume and Brightness adjustment)
    binde = {
        -- Audio Volume via PipeWire / WirePlumber
        ", XF86AudioRaiseVolume, exec, wpctl set-volume -l 1.5 @DEFAULT_AUDIO_SINK@ 5%+",
        ", XF86AudioLowerVolume, exec, wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-",

        -- Display Backlight via brightnessctl
        ", XF86MonBrightnessUp, exec, brightnessctl set +5%",
        ", XF86MonBrightnessDown, exec, brightnessctl set 5%-"
    },

    -- Locked / Lid Keys (Can trigger while screen is locked)
    bindl = {
        -- Audio Mute
        ", XF86AudioMute, exec, wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle",
        ", XF86AudioMicMute, exec, wpctl set-mute @DEFAULT_AUDIO_SOURCE@ toggle",

        -- Media Playback via MPRIS
        ", XF86AudioPlay, exec, playerctl play-pause",
        ", XF86AudioNext, exec, playerctl next",
        ", XF86AudioPrev, exec, playerctl previous",
        ", XF86AudioStop, exec, playerctl stop"
    },

    -- Mouse Binds (Move & Resize Floating Windows)
    bindm = {
        "SUPER, mouse:272, movewindow",
        "SUPER, mouse:273, resizewindow"
    }
})
