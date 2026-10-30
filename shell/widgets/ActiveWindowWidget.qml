import QtQuick
import QtQuick.Layouts
import Quickshell
import Quickshell.Hyprland
import "../services"

RowLayout {
    id: activeWinRoot
    spacing: 6

    property string windowTitle: "Desktop"
    property string appClass: ""

    // Listen to Hyprland raw events for instantaneous window focus updates
    Connections {
        target: Hyprland

        function onRawEvent(name, data) {
            if (name === "activewindow" || name === "activewindowv2") {
                var parts = data.split(",");
                if (parts.length >= 2) {
                    activeWinRoot.appClass = parts[0];
                    activeWinRoot.windowTitle = parts.slice(1).join(",");
                } else {
                    activeWinRoot.windowTitle = data || "Desktop";
                }
            }
        }
    }

    Text {
        text: "󰍹"
        font.family: ThemeService.typography.fontFamilyMono
        font.pixelSize: ThemeService.typography.fontSizeNormal
        color: ThemeService.colors.accent
    }

    Text {
        text: activeWinRoot.windowTitle
        font.family: ThemeService.typography.fontFamilyUi
        font.pixelSize: ThemeService.typography.fontSizeSmall
        font.weight: Font.Medium
        color: ThemeService.colors.textPrimary
        elide: Text.ElideRight
        Layout.maximumWidth: 260
    }
}
