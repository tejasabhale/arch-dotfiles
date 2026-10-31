import QtQuick
import Quickshell
import Quickshell.Wayland
import Quickshell.Hyprland
import "services"
import "panels"
import "dock"
import "launcher"
import "overview"
import "control-center"
import "notifications"
import "dashboard"
import "../productivity/clipboard"
import "../productivity/screenshots"
import "../assistant/interface"

ShellRoot {
    id: shellRoot

    // Multi-Monitor Screen Loop: Spawns TopBar and Dock across all active displays
    Variants {
        model: Quickshell.screens

        Scope {
            required property var modelData

            TopBar {
                screen: modelData
                onOpenLauncher: ipcBridge.toggleLauncher()
                onOpenAssistant: ipcBridge.toggleAssistant()
                onOpenControlCenter: ipcBridge.toggleControlCenter()
                onOpenDashboard: ipcBridge.toggleDashboard()
            }

            Dock {
                screen: modelData
            }
        }
    }

    // Modal Overlays & Centered Windows: Instantiated as Singletons on the Primary Screen
    Scope {
        property var primaryScreen: (Quickshell.screens && Quickshell.screens.length > 0) ? Quickshell.screens[0] : null

        Launcher {
            id: launcherComp
            screen: primaryScreen
        }

        Overview {
            id: overviewComp
            screen: primaryScreen
        }

        ControlCenter {
            id: ccComp
            screen: primaryScreen
        }

        NotificationCenter {
            id: notifComp
            screen: primaryScreen
        }

        OsdOverlay {
            id: osdComp
            screen: primaryScreen
        }

        Dashboard {
            id: dashComp
            screen: primaryScreen
        }

        ClipboardPanel {
            id: clipComp
            screen: primaryScreen
        }

        ScreenshotBar {
            id: screenComp
            screen: primaryScreen
        }

        AssistantWindow {
            id: assistantComp
            screen: primaryScreen
        }

        Connections {
            target: ipcBridge
            function onLauncherToggled() { launcherComp.toggle(); }
            function onAssistantToggled() { assistantComp.toggle(); }
            function onOverviewToggled() { overviewComp.toggle(); }
            function onControlCenterToggled() { ccComp.toggle(); }
            function onNotificationsToggled() { notifComp.toggle(); }
            function onDashboardToggled() { dashComp.toggle(); }
            function onClipboardToggled() { clipComp.toggle(); }
            function onScreenshotToggled() { screenComp.toggle(); }
        }
    }

    // Centralized Desktop IPC Bridge for Hyprland Keybindings & External Scripts
    Item {
        id: ipcBridge

        signal launcherToggled()
        signal assistantToggled()
        signal controlCenterToggled()
        signal notificationsToggled()
        signal dashboardToggled()
        signal overviewToggled()
        signal clipboardToggled()
        signal screenshotToggled()

        function toggleLauncher() {
            launcherToggled();
        }

        function toggleAssistant() {
            assistantToggled();
        }

        function toggleControlCenter() {
            controlCenterToggled();
        }

        function toggleNotifications() {
            notificationsToggled();
        }

        function toggleDashboard() {
            dashboardToggled();
        }

        function toggleOverview() {
            overviewToggled();
        }

        function toggleClipboard() {
            clipboardToggled();
        }

        function toggleScreenshot() {
            screenshotToggled();
        }

        function switchTheme(themeName) {
            ThemeService.setPreset(themeName);
        }
    }

    Component.onCompleted: {
        console.log("[Quickshell] Desktop Shell initialized successfully with Theme:", ThemeService.activeThemeName);
    }
}
