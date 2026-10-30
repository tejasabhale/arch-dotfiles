-- =============================================================================
-- HYPRLAND MODULE: HARDWARE-OPTIMIZED ANIMATIONS
-- Target: Intel UHD 620 GPU (Restrained, responsive, zero-stutter)
-- =============================================================================

hl.config({
    animations = {
        enabled = true,

        -- Custom bezier curves for crisp, elegant physics
        bezier = {
            easeOutCubic = "0.33, 1, 0.68, 1",
            easeOutExpo = "0.16, 1, 0.3, 1",
            easeInOut = "0.65, 0, 0.35, 1",
        },

        -- Restrained duration (3-4 ticks ~ 150-200ms) to preserve battery and 60fps
        animation = {
            "windows, 1, 4, easeOutExpo, popin 85%",
            "windowsIn, 1, 4, easeOutExpo, popin 85%",
            "windowsOut, 1, 3, easeOutCubic, popin 90%",
            "windowsMove, 1, 4, easeOutExpo",
            "fade, 1, 3, easeOutCubic",
            "fadeIn, 1, 3, easeOutCubic",
            "fadeOut, 1, 2, easeOutCubic",
            "workspaces, 1, 4, easeOutExpo, slide",
            "specialWorkspace, 1, 4, easeOutExpo, slidevert",
            -- Disable expensive continuous border angle rotation on Intel UHD 620
            "border, 1, 4, easeOutCubic",
            "borderangle, 0",
        }
    }
})
