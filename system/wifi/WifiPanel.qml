import QtQuick
import QtQuick.Layouts
import Quickshell
import Quickshell.Wayland
import Quickshell.Io
import "../../shell/services"
import "../../shell/components"

PanelWindow {
    id: wifiWindow

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

    property bool isScanning: false
    property var networks: []
    property string selectedSsid: ""
    property string enteredPassword: ""

    function toggle() {
        isOpen = !isOpen;
        if (isOpen) {
            scanNetworks();
        }
    }

    function scanNetworks() {
        isScanning = true;
        scanProc.command = ["python3", "-m", "system.wifi.wifi_manager", "scan"];
        scanProc.running = true;
    }

    function connectToNetwork(ssid, pass) {
        connectProc.command = ["python3", "-m", "system.wifi.wifi_manager", "connect", ssid, pass];
        connectProc.running = true;
    }

    MouseArea {
        anchors.fill: parent
        onClicked: wifiWindow.isOpen = false
        Rectangle {
            anchors.fill: parent
            color: "#00000077"
        }
    }

    Rectangle {
        id: modalContent
        anchors.centerIn: parent
        implicitWidth: 480
        implicitHeight: 520
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
                    text: "󰤨 Wi-Fi Networks"
                    font.family: ThemeService.typography.fontFamilyUi
                    font.pixelSize: ThemeService.typography.fontSizeLarge
                    font.weight: Font.Bold
                    color: ThemeService.colors.textPrimary
                }

                Item { Layout.fillWidth: true }

                Button {
                    variant: "ghost"
                    icon: "󰑐"
                    text: "Scan"
                    onClicked: wifiWindow.scanNetworks()
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
                        onClicked: wifiWindow.isOpen = false
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 1
                color: ThemeService.colors.border
            }

            // Networks List
            ScrollView {
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true

                ListView {
                    id: netListView
                    anchors.fill: parent
                    spacing: 6
                    model: wifiWindow.networks

                    delegate: Rectangle {
                        id: netItem
                        required property var modelData

                        implicitWidth: netListView.width
                        implicitHeight: 48
                        radius: ThemeService.metrics.radiusSmall
                        color: modelData.is_active ? ThemeService.colors.surface : (itemMouse.containsMouse ? ThemeService.colors.surfaceHover : ThemeService.colors.surfaceVariant)
                        border.color: modelData.is_active ? ThemeService.colors.accent : ThemeService.colors.border
                        border.width: modelData.is_active ? 2 : 1

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 10
                            spacing: 10

                            Text {
                                text: modelData.signal_percent > 75 ? "󰤨" : (modelData.signal_percent > 45 ? "󰤥" : "󰤟")
                                font.family: ThemeService.typography.fontFamilyMono
                                font.pixelSize: 18
                                color: modelData.is_active ? ThemeService.colors.accent : ThemeService.colors.textPrimary
                            }

                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 2
                                Text {
                                    text: modelData.ssid
                                    font.family: ThemeService.typography.fontFamilyUi
                                    font.pixelSize: ThemeService.typography.fontSizeNormal
                                    font.weight: Font.Medium
                                    color: ThemeService.colors.textPrimary
                                    elide: Text.ElideRight
                                    Layout.fillWidth: true
                                }
                                Text {
                                    text: modelData.security + " • " + modelData.signal_percent + "% signal"
                                    font.family: ThemeService.typography.fontFamilyUi
                                    font.pixelSize: ThemeService.typography.fontSizeSmall
                                    color: ThemeService.colors.textMuted
                                }
                            }

                            Button {
                                variant: modelData.is_active ? "ghost" : "secondary"
                                text: modelData.is_active ? "Connected" : "Connect"
                                disabled: modelData.is_active
                                onClicked: {
                                    wifiWindow.selectedSsid = modelData.ssid;
                                    pwdModal.visible = true;
                                }
                            }
                        }

                        MouseArea {
                            id: itemMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                if (!modelData.is_active) {
                                    wifiWindow.selectedSsid = modelData.ssid;
                                    pwdModal.visible = true;
                                }
                            }
                        }
                    }
                }
            }

            // Inline Password Prompt Modal
            Rectangle {
                id: pwdModal
                visible: false
                Layout.fillWidth: true
                implicitHeight: 90
                radius: ThemeService.metrics.radiusMedium
                color: ThemeService.colors.surface
                border.color: ThemeService.colors.borderFocus
                border.width: 1

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 8

                    Text {
                        text: "Enter password for '" + wifiWindow.selectedSsid + "':"
                        font.family: ThemeService.typography.fontFamilyUi
                        font.pixelSize: ThemeService.typography.fontSizeSmall
                        font.weight: Font.Bold
                        color: ThemeService.colors.textPrimary
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 8

                        TextField {
                            id: pwdInput
                            Layout.fillWidth: true
                            placeholder: "Wi-Fi Passphrase..."
                            onTextChanged: function(t) { wifiWindow.enteredPassword = t; }
                            onAccepted: {
                                wifiWindow.connectToNetwork(wifiWindow.selectedSsid, wifiWindow.enteredPassword);
                                pwdModal.visible = false;
                            }
                        }

                        Button {
                            variant: "primary"
                            text: "Join"
                            onClicked: {
                                wifiWindow.connectToNetwork(wifiWindow.selectedSsid, wifiWindow.enteredPassword);
                                pwdModal.visible = false;
                            }
                        }

                        Button {
                            variant: "ghost"
                            text: "Cancel"
                            onClicked: pwdModal.visible = false
                        }
                    }
                }
            }
        }
    }

    Process {
        id: scanProc
        stdout: SplitParser {
            onRead: function(data) {
                wifiWindow.isScanning = false;
                try {
                    wifiWindow.networks = JSON.parse(data);
                } catch(e) {}
            }
        }
    }

    Process {
        id: connectProc
        stdout: SplitParser {
            onRead: function(data) {
                wifiWindow.scanNetworks();
            }
        }
    }
}
