import QtQuick
import QtQuick.Layouts
import Quickshell
import Quickshell.Wayland
import "../services"
import "../components"

PanelWindow {
    id: osdWindow

    required property var screen
    property bool isVisible: false

    visible: isVisible

    anchors {
        bottom: true
    }

    implicitWidth: 260
    implicitHeight: 70
    color: "transparent"

    WlrLayershell.layer: WlrLayer.Overlay
    WlrLayershell.exclusiveZone: 0

    property string osdIcon: "󰕾"
    property string osdTitle: "Volume"
    property real osdValue: 0.65

    function showOsd(icon, title, value) {
        osdIcon = icon;
        osdTitle = title;
        osdValue = Math.max(0.0, Math.min(1.0, value));
        isVisible = true;
        hideTimer.restart();
    }

    Timer {
        id: hideTimer
        interval: 1600
        running: false
        onTriggered: osdWindow.isVisible = false
    }

    Rectangle {
        anchors.fill: parent
        anchors.bottomMargin: ThemeService.metrics.dockHeight + 20
        radius: ThemeService.metrics.radiusMedium
        color: ThemeService.colors.backgroundBlur
        border.color: ThemeService.colors.border
        border.width: ThemeService.metrics.borderWidth

        RowLayout {
            anchors.fill: parent
            anchors.margins: 14
            spacing: 12

            Text {
                text: osdWindow.osdIcon
                font.family: ThemeService.typography.fontFamilyMono
                font.pixelSize: 22
                color: ThemeService.colors.accent
            }

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 6

                RowLayout {
                    Layout.fillWidth: true
                    Text {
                        text: osdWindow.osdTitle
                        font.family: ThemeService.typography.fontFamilyUi
                        font.pixelSize: ThemeService.typography.fontSizeSmall
                        font.weight: Font.Medium
                        color: ThemeService.colors.textPrimary
                    }
                    Item { Layout.fillWidth: true }
                    Text {
                        text: Math.round(osdWindow.osdValue * 100) + "%"
                        font.family: ThemeService.typography.fontFamilyMono
                        font.pixelSize: ThemeService.typography.fontSizeSmall
                        color: ThemeService.colors.textSecondary
                    }
                }

                // Progress Bar
                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: 6
                    radius: 3
                    color: ThemeService.colors.surfaceVariant

                    Rectangle {
                        height: parent.height
                        radius: parent.radius
                        width: parent.width * osdWindow.osdValue
                        color: ThemeService.colors.accent
                    }
                }
            }
        }
    }
}
