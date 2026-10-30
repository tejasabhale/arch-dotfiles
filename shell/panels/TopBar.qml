import QtQuick
import QtQuick.Layouts
import Quickshell
import Quickshell.Wayland
import "../services"
import "../widgets"

PanelWindow {
    id: topBarRoot

    required property var screen

    anchors {
        top: true
        left: true
        right: true
    }

    implicitHeight: ThemeService.metrics.barHeight
    color: "transparent"

    WlrLayershell.layer: WlrLayer.Top
    WlrLayershell.exclusiveZone: ThemeService.metrics.barHeight

    signal openLauncher()
    signal openAssistant()
    signal openControlCenter()
    signal openDashboard()

    Rectangle {
        anchors.fill: parent
        color: ThemeService.colors.backgroundBlur
        border.color: ThemeService.colors.border
        border.width: ThemeService.metrics.borderWidth

        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 12
            anchors.rightMargin: 12
            spacing: 12

            // Left: Workspaces & Active Window Title
            RowLayout {
                Layout.alignment: Qt.AlignLeft | Qt.AlignVCenter
                spacing: 10

                // App launcher trigger icon
                Rectangle {
                    implicitWidth: 28
                    implicitHeight: 28
                    radius: ThemeService.metrics.radiusSmall
                    color: launcherMouse.containsMouse ? ThemeService.colors.surfaceHover : ThemeService.colors.surfaceVariant

                    Text {
                        anchors.centerIn: parent
                        text: "󰣇" // Arch Linux glyph
                        font.family: ThemeService.typography.fontFamilyMono
                        font.pixelSize: ThemeService.typography.fontSizeNormal
                        color: ThemeService.colors.accent
                    }

                    MouseArea {
                        id: launcherMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: topBarRoot.openLauncher()
                    }
                }

                WorkspacesWidget {}

                Rectangle {
                    implicitWidth: 1
                    implicitHeight: 18
                    color: ThemeService.colors.border
                }

                ActiveWindowWidget {}
            }

            // Center: Clock & Calendar Widget
            RowLayout {
                Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                ClockWidget {
                    onClicked: topBarRoot.openDashboard()
                }
            }

            // Right: System Vitals, Hardware Status, Tray & June
            RowLayout {
                Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                spacing: 8

                SystemTrayWidget {}

                AudioWidget {
                    onClicked: topBarRoot.openControlCenter()
                }

                NetworkWidget {
                    onClicked: topBarRoot.openControlCenter()
                }

                BatteryWidget {}

                AssistantButton {
                    onClicked: topBarRoot.openAssistant()
                }

                // Control Center Trigger Button
                Rectangle {
                    implicitWidth: 28
                    implicitHeight: 28
                    radius: ThemeService.metrics.radiusSmall
                    color: ccMouse.containsMouse ? ThemeService.colors.surfaceHover : ThemeService.colors.surfaceVariant

                    Text {
                        anchors.centerIn: parent
                        text: "󰍜"
                        font.family: ThemeService.typography.fontFamilyMono
                        font.pixelSize: ThemeService.typography.fontSizeNormal
                        color: ThemeService.colors.textPrimary
                    }

                    MouseArea {
                        id: ccMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: topBarRoot.openControlCenter()
                    }
                }
            }
        }
    }
}
