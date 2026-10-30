-- =============================================================================
-- HYPRLAND MODULE: WORKSPACES & WORKSPACE PROFILES
-- Default Profiles: 1: Research, 2: Dev, 3: Terminal, 4: ML, 5: Comm
-- =============================================================================

-- Default workspace profiles as defined in Section 10 of specification
local workspace_profiles = {
    { id = 1, name = "Research", icon = "󰈹" },
    { id = 2, name = "Development", icon = "󰨞" },
    { id = 3, name = "Terminal", icon = "󰞷" },
    { id = 4, name = "Machine Learning", icon = "󱚠" },
    { id = 5, name = "Communication", icon = "󰭹" },
}

-- Bind default workspaces to primary display (eDP-1)
for _, ws in ipairs(workspace_profiles) do
    hl.workspace({
        name = tostring(ws.id),
        monitor = "eDP-1",
        default = (ws.id == 1)
    })
end

-- Workspaces 6-10 for secondary displays or dynamic spillover
for i = 6, 10 do
    hl.workspace({
        name = tostring(i),
        monitor = "HDMI-A-1",
        default = false
    })
end

return workspace_profiles
