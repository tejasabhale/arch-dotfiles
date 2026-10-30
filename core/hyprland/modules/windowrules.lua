-- =============================================================================
-- HYPRLAND MODULE: WINDOW RULES & APPLICATION BINDINGS
-- Target: Precision floating dialogs, scratchpads, and workspace assignments
-- =============================================================================

hl.config({
    windowrulev2 = {
        -- Global: Suppress unwanted maximize events from legacy XWayland/Wayland clients
        "suppressevent maximize, class:.*",

        -- Floating System Dialogs & Utilities
        "float, class:^(pavucontrol|org.pulseaudio.pavucontrol)$",
        "size 700 500, class:^(pavucontrol|org.pulseaudio.pavucontrol)$",
        "center, class:^(pavucontrol|org.pulseaudio.pavucontrol)$",

        "float, class:^(nm-connection-editor)$",
        "float, class:^(blueman-manager)$",
        "float, class:^(org.kde.polkit-kde-authentication-agent-1)$",
        "pin, class:^(org.kde.polkit-kde-authentication-agent-1)$",

        -- Floating File Pickers & Browser Dialogs
        "float, title:^(Open File|Save File|Select Folder|Open Folder|Choose Files|File Upload)$",
        "size 900 600, title:^(Open File|Save File|Select Folder|Open Folder|Choose Files|File Upload)$",
        "center, title:^(Open File|Save File|Select Folder|Open Folder|Choose Files|File Upload)$",

        -- Floating Terminal Utility Window
        "float, class:^(kitty-float)$",
        "size 850 550, class:^(kitty-float)$",
        "center, class:^(kitty-float)$",

        -- Picture-in-Picture (PiP) Configuration
        "float, title:^(Picture-in-Picture|Picture in picture)$",
        "pin, title:^(Picture-in-Picture|Picture in picture)$",
        "size 580 326, title:^(Picture-in-Picture|Picture in picture)$",
        "move 100%-600 100%-346, title:^(Picture-in-Picture|Picture in picture)$",

        -- Fullscreen Video Idle Inhibit (Prevent screen sleeping while watching video)
        "idleinhibit fullscreen, class:^(firefox|chromium|zen-browser|google-chrome|brave-browser|mpv)$",

        -- Workspace Application Assignments
        -- Workspace 1: Research (Browsers & Documentation)
        "workspace 1, class:^(firefox|chromium|zen-browser|google-chrome|brave-browser)$",

        -- Workspace 2: Development (Editors & IDEs)
        "workspace 2, class:^(Code|code-oss|vscodium|cursor|jetbrains-.+)$",

        -- Workspace 3: Terminal (Interactive Kitty)
        "workspace 3, class:^(kitty)$",

        -- Workspace 4: Machine Learning (Jupyter, Data tools)
        "workspace 4, class:^(jupyter-notebook|gephi)$",

        -- Workspace 5: Communication (Chat, Meetings, Email)
        "workspace 5, class:^(discord|Slack|TelegramDesktop|thunderbird)$",

        -- Quickshell Windows: Layer Shell Rules
        "noborder, class:^(quickshell.*)$",
        "noshadow, class:^(quickshell.*)$",
    }
})
