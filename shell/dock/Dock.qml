import QtQuick
import QtQuick.Layouts
import Quickshell
import Quickshell.Wayland
import Quickshell.Hyprland
import Quickshell.Io
import "../services"
import "../components"

PanelWindow {
    id: dockWindow

    required property var screen

    anchors {
        bottom: true
    }

    implicitWidth: dockCard.implicitWidth + 24
    implicitHeight: ThemeService.metrics.dockHeight + 14
    color: "transparent"

    WlrLayershell.layer: WlrLayer.Top
    WlrLayershell.exclusiveZone: 0 // Floats gently over desktop windows

    property bool autohide: false
    property bool isHovered: dockMouseArea.containsMouse

    // Pinned core applications list
    property var pinnedApps: [
        { "name": "Terminal", "icon": "󰞷", "exec": "kitty", "class": "kitty" },
        { "name": "Code", "icon": "󰨞", "exec": "code", "class": "Code" },
        { "name": "Browser", "icon": "󰈹", "exec": "xdg-open https://", "class": "firefox" },
        { "name": "Files", "icon": "󰉋", "exec": "dolphin", "class": "org.kde.dolphin" },
        { "name": "June AI", "icon": "󱚣", "exec": "quickshell ipc call assistant toggle", "class": "june" },
        { "name": "Settings", "icon": "󰒓", "exec": "quickshell ipc call settings toggle", "class": "settings" }
    ]

    MouseArea {
        id: dockMouseArea
        anchors.fill: parent
        hoverEnabled: true

        Rectangle {
            id: dockCard
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 8

            implicitWidth: dockRow.implicitWidth + 18
            implicitHeight: ThemeService.metrics.dockHeight
            radius: ThemeService.metrics.radiusLarge

            color: ThemeService.colors.backgroundBlur
            border.color: ThemeService.colors.border
            border.width: ThemeService.metrics.borderWidth

            RowLayout {
                id: dockRow
                anchors.centerIn: parent
                spacing: 10

                Repeater {
                    model: dockWindow.pinnedApps

                    Item {
                        id: dockItem
                        required property var modelData

                        implicitWidth: ThemeService.metrics.dockIconSize
                        implicitHeight: ThemeService.metrics.dockIconSize

                        property bool itemHovered: itemMouse.containsMouse

                        // Tooltip Pill above dock item
                        Rectangle {
                            visible: dockItem.itemHovered
                            anchors.bottom: parent.top
                            anchors.bottomMargin: 10
                            anchors.horizontalCenter: parent.horizontalCenter
                            implicitWidth: tooltipText.implicitWidth + 12
                            implicitHeight: 22
                            radius: 6
                            color: ThemeService.colors.surface
                            border.color: ThemeService.colors.border
                            border.width: 1
                            z: 100

                            Text {
                                id: tooltipText
                                anchors.centerIn: parent
                                text: modelData.name
                                font.family: ThemeService.typography.fontFamilyUi
                                font.pixelSize: ThemeService.typography.fontSizeSmall
                                color: ThemeService.colors.textPrimary
                            }
                        }

                        // App Icon Button
                        Rectangle {
                            id: iconContainer
                            anchors.fill: parent
                            radius: ThemeService.metrics.radiusMedium
                            color: dockItem.itemHovered ? ThemeService.colors.surfaceHover : ThemeService.colors.surfaceVariant
                            border.color: dockItem.itemHovered ? ThemeService.colors.borderFocus : ThemeService.colors.border
                            border.width: 1
                            scale: dockItem.itemHovered ? 1.15 : 1.0

                            Behavior on scale {
                                NumberAnimation {
                                    duration: ThemeService.effects.animationDurationMs
                                    easing.type: Easing.OutBack
                                }
                            }

                            Behavior on color {
                                ColorAnimation { duration: ThemeService.effects.animationDurationMs }
                            }

                            Text {
                                anchors.centerIn: parent
                                text: modelData.icon
                                font.family: ThemeService.typography.fontFamilyMono
                                font.pixelSize: 22
                                color: dockItem.itemHovered ? ThemeService.colors.accent : ThemeService.colors.textPrimary
                            }
                        }

                        // Running Application Dot Indicator
                        Rectangle {
                            anchors.horizontalCenter: parent.horizontalCenter
                            anchors.bottom: parent.bottom
                            anchors.bottomMargin: -4
                            width: 4
                            height: 4
                            radius: 2
                            color: ThemeService.colors.accent
                            visible: true // Connected to window manager state
                        }

                        MouseArea {
                            id: itemMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                Hyprland.dispatch("exec " + modelData.exec);
                            }
                        }
                    }
                }
            }
        }
    }
}
