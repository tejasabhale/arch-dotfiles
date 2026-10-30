import QtQuick
import QtQuick.Layouts
import Quickshell
import Quickshell.Wayland
import Quickshell.Hyprland
import "../services"
import "../components"

PanelWindow {
    id: overviewWindow

    required property var screen
    property bool isOpen: false

    visible: isOpen

    anchors {
        top: true
        bottom: true
        left: true
        right: true
    }

    color: "transparent"

    WlrLayershell.layer: WlrLayer.Overlay
    WlrLayershell.keyboardFocus: isOpen ? WlrKeyboardFocus.Exclusive : WlrKeyboardFocus.None

    property var workspaceProfiles: [
        { "id": 1, "name": "Research", "icon": "󰈹", "color": "#58a6ff" },
        { "id": 2, "name": "Development", "icon": "󰨞", "color": "#3fb950" },
        { "id": 3, "name": "Terminal", "icon": "󰞷", "color": "#d29922" },
        { "id": 4, "name": "Machine Learning", "icon": "󱚠", "color": "#bc8cff" },
        { "id": 5, "name": "Communication", "icon": "󰭹", "color": "#39c5cf" }
    ]

    function toggle() {
        isOpen = !isOpen;
    }

    // Dismiss when clicking outside workspace cards
    MouseArea {
        anchors.fill: parent
        onClicked: overviewWindow.isOpen = false

        Rectangle {
            anchors.fill: parent
            color: "#00000077"
        }
    }

    ColumnLayout {
        anchors.centerIn: parent
        spacing: 24

        // Overview Header
        RowLayout {
            Layout.alignment: Qt.AlignHCenter
            spacing: 12

            Text {
                text: "󰕰 Workspace Overview"
                font.family: ThemeService.typography.fontFamilyUi
                font.pixelSize: ThemeService.typography.fontSizeTitle
                font.weight: Font.Bold
                color: "#ffffff"
            }
        }

        // Horizontal Row of 5 Workspaces
        RowLayout {
            Layout.alignment: Qt.AlignHCenter
            spacing: 16

            Repeater {
                model: overviewWindow.workspaceProfiles

                Rectangle {
                    id: wsCard
                    required property var modelData

                    property bool isCurrent: Hyprland.focusedWorkspace ? (Hyprland.focusedWorkspace.id === modelData.id) : (modelData.id === 1)
                    property bool hovered: cardMouse.containsMouse

                    implicitWidth: 210
                    implicitHeight: 280
                    radius: ThemeService.metrics.radiusLarge
                    color: isCurrent ? ThemeService.colors.surface : ThemeService.colors.surfaceVariant
                    border.color: isCurrent ? ThemeService.colors.accent : (hovered ? ThemeService.colors.borderFocus : ThemeService.colors.border)
                    border.width: isCurrent ? 2 : 1
                    scale: hovered ? 1.04 : 1.0

                    Behavior on scale {
                        NumberAnimation { duration: ThemeService.effects.animationDurationMs; easing.type: Easing.OutCubic }
                    }

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 14
                        spacing: 10

                        // Workspace Header
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8

                            Rectangle {
                                implicitWidth: 26
                                implicitHeight: 26
                                radius: 13
                                color: modelData.color + "22"
                                border.color: modelData.color
                                border.width: 1

                                Text {
                                    anchors.centerIn: parent
                                    text: modelData.icon
                                    font.family: ThemeService.typography.fontFamilyMono
                                    font.pixelSize: 13
                                    color: modelData.color
                                }
                            }

                            Text {
                                text: modelData.id + ": " + modelData.name
                                font.family: ThemeService.typography.fontFamilyUi
                                font.pixelSize: ThemeService.typography.fontSizeNormal
                                font.weight: Font.Bold
                                color: wsCard.isCurrent ? ThemeService.colors.accent : ThemeService.colors.textPrimary
                            }

                            Item { Layout.fillWidth: true }

                            Rectangle {
                                visible: wsCard.isCurrent
                                implicitWidth: 8
                                implicitHeight: 8
                                radius: 4
                                color: ThemeService.colors.accent
                            }
                        }

                        // Simulated Window Workspace Canvas
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            radius: ThemeService.metrics.radiusMedium
                            color: ThemeService.colors.background
                            border.color: ThemeService.colors.border
                            border.width: 1

                            ColumnLayout {
                                anchors.centerIn: parent
                                spacing: 8

                                Text {
                                    Layout.alignment: Qt.AlignHCenter
                                    text: modelData.icon
                                    font.family: ThemeService.typography.fontFamilyMono
                                    font.pixelSize: 32
                                    color: wsCard.isCurrent ? modelData.color : ThemeService.colors.textMuted
                                    opacity: wsCard.isCurrent ? 0.9 : 0.4
                                }

                                Text {
                                    Layout.alignment: Qt.AlignHCenter
                                    text: wsCard.isCurrent ? "Active Workspace" : "Click to Switch"
                                    font.family: ThemeService.typography.fontFamilyUi
                                    font.pixelSize: ThemeService.typography.fontSizeSmall
                                    color: ThemeService.colors.textMuted
                                }
                            }
                        }
                    }

                    MouseArea {
                        id: cardMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            Hyprland.dispatch("workspace " + modelData.id);
                            overviewWindow.isOpen = false;
                        }
                    }
                }
            }
        }

        Text {
            Layout.alignment: Qt.AlignHCenter
            text: "Press Escape to close • Super+1..5 to switch directly"
            font.family: ThemeService.typography.fontFamilyUi
            font.pixelSize: ThemeService.typography.fontSizeSmall
            color: "#ffffff88"
        }
    }

    Keys.onEscapePressed: overviewWindow.isOpen = false
}
