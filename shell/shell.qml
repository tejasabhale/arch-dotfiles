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

    // Multi-Monitor Screen Loop: Spawns desktop components across active displays
    Variants {
        model: Quickshell.screens

        Scope {
            required property var modelData

            TopBar {
                screen: modelData
                onOpenLauncher: launcherComp.toggle()
                onOpenAssistant: ipcBridge.toggleAssistant()
                onOpenControlCenter: ccComp.toggle()
                onOpenDashboard: dashComp.toggle()
            }

            Dock {
                screen: modelData
            }

            Launcher {
                id: launcherComp
                screen: modelData
            }

            Overview {
                id: overviewComp
                screen: modelData
            }

            ControlCenter {
                id: ccComp
                screen: modelData
            }

            NotificationCenter {
                id: notifComp
                screen: modelData
            }

            OsdOverlay {
                id: osdComp
                screen: modelData
            }

            Dashboard {
                id: dashComp
                screen: modelData
            }

            ClipboardPanel {
                id: clipComp
                screen: modelData
            }

            ScreenshotBar {
                id: screenComp
                screen: modelData
            }

            AssistantWindow {
                id: assistantComp
                screen: modelData
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
