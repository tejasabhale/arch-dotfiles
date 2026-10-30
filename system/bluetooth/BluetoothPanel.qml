import QtQuick
import QtQuick.Layouts
import Quickshell
import Quickshell.Wayland
import Quickshell.Io
import "../../shell/services"
import "../../shell/components"

PanelWindow {
    id: btWindow

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

    property bool isPowered: true
    property var devices: []

    function toggle() {
        isOpen = !isOpen;
        if (isOpen) {
            refreshDevices();
        }
    }

    function refreshDevices() {
        listProc.command = ["python3", "-m", "system.bluetooth.bluetooth_manager", "list"];
        listProc.running = true;
    }

    function connectDevice(mac) {
        connectProc.command = ["python3", "-m", "system.bluetooth.bluetooth_manager", "connect", mac];
        connectProc.running = true;
    }

    function disconnectDevice(mac) {
        disconnectProc.command = ["python3", "-m", "system.bluetooth.bluetooth_manager", "disconnect", mac];
        disconnectProc.running = true;
    }

    MouseArea {
        anchors.fill: parent
        onClicked: btWindow.isOpen = false
        Rectangle {
            anchors.fill: parent
            color: "#00000077"
        }
    }

    Rectangle {
        id: modalContent
        anchors.centerIn: parent
        implicitWidth: 460
        implicitHeight: 480
        radius: ThemeService.metrics.radiusLarge
        color: ThemeService.colors.backgroundBlur
        border.color: ThemeService.colors.border
        border.width: ThemeService.metrics.borderWidth
        clip: true

        MouseArea {
            anchors.fill: parent
            hoverEnabled: false
        }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 20
            spacing: 12

            // Header
            RowLayout {
                Layout.fillWidth: true

                Text {
                    text: "󰂯 Bluetooth Devices"
                    font.family: ThemeService.typography.fontFamilyUi
                    font.pixelSize: ThemeService.typography.fontSizeLarge
                    font.weight: Font.Bold
                    color: ThemeService.colors.textPrimary
                }

                Item { Layout.fillWidth: true }

                Switch {
                    checked: btWindow.isPowered
                    onToggled: function(val) {
                        btWindow.isPowered = val;
                        powerProc.command = ["python3", "-m", "system.bluetooth.bluetooth_manager", "power", val ? "on" : "off"];
                        powerProc.running = true;
                    }
                }

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
                        onClicked: btWindow.isOpen = false
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 1
                color: ThemeService.colors.border
            }

            // Devices List
            ScrollView {
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true

                ListView {
                    id: btListView
                    anchors.fill: parent
                    spacing: 6
                    model: btWindow.devices

                    delegate: Rectangle {
                        required property var modelData

                        implicitWidth: btListView.width
                        implicitHeight: 48
                        radius: ThemeService.metrics.radiusSmall
                        color: itemMouse.containsMouse ? ThemeService.colors.surfaceHover : ThemeService.colors.surfaceVariant
                        border.color: ThemeService.colors.border
                        border.width: 1

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 10
                            spacing: 10

                            Text {
                                text: modelData.icon_glyph
                                font.family: ThemeService.typography.fontFamilyMono
                                font.pixelSize: 18
                                color: ThemeService.colors.accent
                            }

                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 2
                                Text {
                                    text: modelData.name
                                    font.family: ThemeService.typography.fontFamilyUi
                                    font.pixelSize: ThemeService.typography.fontSizeNormal
                                    font.weight: Font.Medium
                                    color: ThemeService.colors.textPrimary
                                    elide: Text.ElideRight
                                    Layout.fillWidth: true
                                }
                                Text {
                                    text: modelData.mac + (modelData.is_paired ? " • Paired" : "")
                                    font.family: ThemeService.typography.fontFamilyMono
                                    font.pixelSize: ThemeService.typography.fontSizeSmall
                                    color: ThemeService.colors.textMuted
                                }
                            }

                            Button {
                                variant: modelData.is_connected ? "secondary" : "primary"
                                text: modelData.is_connected ? "Disconnect" : "Connect"
                                onClicked: {
                                    if (modelData.is_connected) {
                                        btWindow.disconnectDevice(modelData.mac);
                                    } else {
                                        btWindow.connectDevice(modelData.mac);
                                    }
                                }
                            }
                        }

                        MouseArea {
                            id: itemMouse
                            anchors.fill: parent
                            hoverEnabled: true
                        }
                    }

                    Item {
                        anchors.centerIn: parent
                        visible: btWindow.devices.length === 0
                        implicitWidth: 200
                        implicitHeight: 80

                        Text {
                            anchors.centerIn: parent
                            text: "No Bluetooth devices found"
                            font.family: ThemeService.typography.fontFamilyUi
                            font.pixelSize: ThemeService.typography.fontSizeSmall
                            color: ThemeService.colors.textMuted
                        }
                    }
                }
            }
        }
    }

    Process {
        id: listProc
        stdout: SplitParser {
            onRead: function(data) {
                try {
                    btWindow.devices = JSON.parse(data);
                } catch(e) {}
            }
        }
    }

    Process {
        id: connectProc
        stdout: SplitParser {
            onRead: function(data) {
                btWindow.refreshDevices();
            }
        }
    }

    Process {
        id: disconnectProc
        stdout: SplitParser {
            onRead: function(data) {
                btWindow.refreshDevices();
            }
        }
    }

    Process {
        id: powerProc
        stdout: SplitParser {
            onRead: function(data) {
                btWindow.refreshDevices();
            }
        }
    }
}
