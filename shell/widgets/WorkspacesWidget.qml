import QtQuick
import QtQuick.Layouts
import Quickshell
import Quickshell.Hyprland
import "../services"
import "../components"

RowLayout {
    id: wsRoot
    spacing: 4

    // Fixed default 5 workspaces from specification
    property var workspacesList: [
        { "id": 1, "name": "1", "icon": "󰈹", "title": "Research" },
        { "id": 2, "name": "2", "icon": "󰨞", "title": "Development" },
        { "id": 3, "name": "3", "icon": "󰞷", "title": "Terminal" },
        { "id": 4, "name": "4", "icon": "󱚠", "title": "Machine Learning" },
        { "id": 5, "name": "5", "icon": "󰭹", "title": "Communication" }
    ]

    Repeater {
        model: wsRoot.workspacesList

        Rectangle {
            id: wsItem
            required property var modelData

            property bool isFocused: Hyprland.focusedWorkspace ? (Hyprland.focusedWorkspace.id === modelData.id) : (modelData.id === 1)
            property bool isHovered: wsMouse.containsMouse

            implicitWidth: isFocused ? 32 : 24
            implicitHeight: 24
            radius: 12

            color: isFocused ? ThemeService.colors.accent : (isHovered ? ThemeService.colors.surfaceHover : ThemeService.colors.surfaceVariant)
            border.color: isFocused ? ThemeService.colors.accent : ThemeService.colors.border
            border.width: ThemeService.metrics.borderWidth

            Behavior on implicitWidth {
                NumberAnimation { duration: ThemeService.effects.animationDurationMs; easing.type: Easing.OutCubic }
            }

            Behavior on color {
                ColorAnimation { duration: ThemeService.effects.animationDurationMs }
            }

            Text {
                anchors.centerIn: parent
                text: wsItem.isFocused ? modelData.icon : modelData.name
                font.family: wsItem.isFocused ? ThemeService.typography.fontFamilyMono : ThemeService.typography.fontFamilyUi
                font.pixelSize: ThemeService.typography.fontSizeSmall
                font.weight: wsItem.isFocused ? Font.Bold : Font.Normal
                color: wsItem.isFocused ? "#ffffff" : ThemeService.colors.textSecondary
            }

            MouseArea {
                id: wsMouse
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                onClicked: {
                    Hyprland.dispatch("workspace " + modelData.id);
                }
            }
        }
    }
}
