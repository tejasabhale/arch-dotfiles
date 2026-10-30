import QtQuick
import QtQuick.Layouts
import Quickshell
import Quickshell.Wayland
import "../services"
import "../components"

PanelWindow {
    id: notifWindow

    required property var screen
    property bool isOpen: false

    visible: isOpen

    anchors {
        top: true
        right: true
    }

    implicitWidth: 360
    implicitHeight: 480
    color: "transparent"

    WlrLayershell.layer: WlrLayer.Overlay
    WlrLayershell.exclusiveZone: 0

    property bool dndEnabled: false

    ListModel {
        id: notifModel

        ListElement {
            appName: "June AI"
            summary: "Assistant Ready"
            body: "June is online and listening. Press Super+J or speak to interact."
            icon: "󱚣"
            timeStr: "2m ago"
        }
        ListElement {
            appName: "System"
            summary: "Wi-Fi Connected"
            body: "Successfully established connection with encrypted network."
            icon: "󰤨"
            timeStr: "15m ago"
        }
        ListElement {
            appName: "Battery"
            summary: "AC Adapter Plugged In"
            body: "Device is now charging at full rate."
            icon: "󰂄"
            timeStr: "1h ago"
        }
    }

    function toggle() {
        isOpen = !isOpen;
    }

    Rectangle {
        anchors.fill: parent
        anchors.topMargin: ThemeService.metrics.barHeight + 8
        anchors.rightMargin: 12
        anchors.bottomMargin: 8
        radius: ThemeService.metrics.radiusLarge
        color: ThemeService.colors.backgroundBlur
        border.color: ThemeService.colors.border
        border.width: ThemeService.metrics.borderWidth
        clip: true

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 14
            spacing: 12

            // Header
            RowLayout {
                Layout.fillWidth: true

                Text {
                    text: "󰂚 Notifications"
                    font.family: ThemeService.typography.fontFamilyUi
                    font.pixelSize: ThemeService.typography.fontSizeLarge
                    font.weight: Font.Bold
                    color: ThemeService.colors.textPrimary
                }

                Item { Layout.fillWidth: true }

                // Clear All Button
                Button {
                    variant: "ghost"
                    text: "Clear All"
                    visible: notifModel.count > 0
                    onClicked: notifModel.clear()
                }

                // Close Button
                Rectangle {
                    implicitWidth: 26
                    implicitHeight: 26
                    radius: 13
                    color: closeMouse.containsMouse ? ThemeService.colors.surfaceHover : ThemeService.colors.surfaceVariant

                    Text {
                        anchors.centerIn: parent
                        text: "󰅖"
                        font.family: ThemeService.typography.fontFamilyMono
                        font.pixelSize: 11
                        color: ThemeService.colors.textSecondary
                    }

                    MouseArea {
                        id: closeMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: notifWindow.isOpen = false
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 1
                color: ThemeService.colors.border
            }

            // Notification Cards List
            ScrollView {
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true

                ListView {
                    id: listView
                    anchors.fill: parent
                    spacing: 8
                    model: notifModel

                    delegate: NotificationCard {
                        appName: model.appName
                        summary: model.summary
                        body: model.body
                        icon: model.icon
                        timeStr: model.timeStr
                        onDismissed: notifModel.remove(index)
                    }

                    // Empty State Display
                    Item {
                        anchors.centerIn: parent
                        visible: notifModel.count === 0
                        implicitWidth: 200
                        implicitHeight: 100

                        ColumnLayout {
                            anchors.centerIn: parent
                            spacing: 8

                            Text {
                                Layout.alignment: Qt.AlignHCenter
                                text: "󰂛"
                                font.family: ThemeService.typography.fontFamilyMono
                                font.pixelSize: 36
                                color: ThemeService.colors.textMuted
                            }

                            Text {
                                Layout.alignment: Qt.AlignHCenter
                                text: "No notifications"
                                font.family: ThemeService.typography.fontFamilyUi
                                font.pixelSize: ThemeService.typography.fontSizeNormal
                                color: ThemeService.colors.textMuted
                            }
                        }
                    }
                }
            }
        }
    }
}
