import QtQuick
import QtQuick.Layouts
import Quickshell
import Quickshell.Wayland
import Quickshell.Io
import "../../shell/services"
import "../../shell/components"

PanelWindow {
    id: hotspotWindow

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

    // Hotspot State
    property bool isHotspotRunning: false
    property bool isSupported: true
    property string ssid: "Arch-EliteBook"
    property string password: ""
    property bool showPassword: false
    property string selectedBand: "2.4 GHz"
    property string qrImagePath: ""
    property var clientList: []

    function toggle() {
        isOpen = !isOpen;
        if (isOpen) {
            checkHardwareSupport();
        }
    }

    function checkHardwareSupport() {
        detectProc.command = ["python3", "-m", "system.hotspot.hotspot_manager", "detect"];
        detectProc.running = true;
    }

    function startHotspot() {
        startProc.command = ["python3", "-m", "system.hotspot.hotspot_manager", "start", ssid, password];
        startProc.running = true;
    }

    function stopHotspot() {
        stopProc.command = ["python3", "-m", "system.hotspot.hotspot_manager", "stop"];
        stopProc.running = true;
    }

    function generateNewPassword() {
        genPassProc.command = ["python3", "-m", "system.hotspot.hotspot_manager", "genpass"];
        genPassProc.running = true;
    }

    // Dismiss when clicking outside modal card
    MouseArea {
        anchors.fill: parent
        onClicked: hotspotWindow.isOpen = false

        Rectangle {
            anchors.fill: parent
            color: "#00000077"
        }
    }

    // Centered Dialog Window
    Rectangle {
        id: modalContent
        anchors.centerIn: parent
        implicitWidth: 620
        implicitHeight: 560
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
            spacing: 14

            // 1. Header with Close and Hardware Badge
            RowLayout {
                Layout.fillWidth: true

                ColumnLayout {
                    spacing: 2
                    Text {
                        text: "󰖩 Wi-Fi Hotspot Manager"
                        font.family: ThemeService.typography.fontFamilyUi
                        font.pixelSize: ThemeService.typography.fontSizeLarge
                        font.weight: Font.Bold
                        color: ThemeService.colors.textPrimary
                    }
                    Text {
                        text: "Broadcast an encrypted Access Point using HP EliteBook Wi-Fi"
                        font.family: ThemeService.typography.fontFamilyUi
                        font.pixelSize: ThemeService.typography.fontSizeSmall
                        color: ThemeService.colors.textMuted
                    }
                }

                Item { Layout.fillWidth: true }

                Pill {
                    text: hotspotWindow.isSupported ? "AP Mode Supported" : "AP Mode Unsupported"
                    icon: hotspotWindow.isSupported ? "󰄲" : "󰅖"
                    active: hotspotWindow.isSupported
                    activeColor: ThemeService.colors.success
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
                        onClicked: hotspotWindow.isOpen = false
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 1
                color: ThemeService.colors.border
            }

            // 2. Master Activation Switch Banner
            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 64
                radius: ThemeService.metrics.radiusMedium
                color: hotspotWindow.isHotspotRunning ? ThemeService.colors.surface : ThemeService.colors.surfaceVariant
                border.color: hotspotWindow.isHotspotRunning ? ThemeService.colors.accent : ThemeService.colors.border
                border.width: 1

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 14
                    spacing: 12

                    Text {
                        text: hotspotWindow.isHotspotRunning ? "󰖩" : "󰖪"
                        font.family: ThemeService.typography.fontFamilyMono
                        font.pixelSize: 26
                        color: hotspotWindow.isHotspotRunning ? ThemeService.colors.success : ThemeService.colors.textMuted
                    }

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2
                        Text {
                            text: hotspotWindow.isHotspotRunning ? "Hotspot is Broadcasting" : "Hotspot is Inactive"
                            font.family: ThemeService.typography.fontFamilyUi
                            font.pixelSize: ThemeService.typography.fontSizeNormal
                            font.weight: Font.Bold
                            color: ThemeService.colors.textPrimary
                        }
                        Text {
                            text: hotspotWindow.isHotspotRunning ? ("SSID: " + hotspotWindow.ssid) : "Enable to share internet with devices"
                            font.family: ThemeService.typography.fontFamilyUi
                            font.pixelSize: ThemeService.typography.fontSizeSmall
                            color: ThemeService.colors.textMuted
                        }
                    }

                    Switch {
                        checked: hotspotWindow.isHotspotRunning
                        onToggled: function(val) {
                            if (val) hotspotWindow.startHotspot();
                            else hotspotWindow.stopHotspot();
                        }
                    }
                }
            }

            // 3. Hotspot Configuration Fields
            RowLayout {
                Layout.fillWidth: true
                spacing: 16

                // Left Column: Credentials & Band
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 10

                    // Network Name (SSID)
                    ColumnLayout {
                        spacing: 4
                        Text {
                            text: "Network Name (SSID)"
                            font.family: ThemeService.typography.fontFamilyUi
                            font.pixelSize: ThemeService.typography.fontSizeSmall
                            color: ThemeService.colors.textSecondary
                        }
                        TextField {
                            Layout.fillWidth: true
                            text: hotspotWindow.ssid
                            onTextChanged: function(t) { hotspotWindow.ssid = t; }
                        }
                    }

                    // Password with Show/Hide & Generate
                    ColumnLayout {
                        spacing: 4
                        Text {
                            text: "Security Password (WPA2/WPA3 AES)"
                            font.family: ThemeService.typography.fontFamilyUi
                            font.pixelSize: ThemeService.typography.fontSizeSmall
                            color: ThemeService.colors.textSecondary
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8

                            TextField {
                                Layout.fillWidth: true
                                text: hotspotWindow.password
                                onTextChanged: function(t) { hotspotWindow.password = t; }
                            }

                            Button {
                                variant: "secondary"
                                icon: "󰑐"
                                text: "Random"
                                onClicked: hotspotWindow.generateNewPassword()
                            }
                        }
                    }

                    // Band Selection
                    ColumnLayout {
                        spacing: 4
                        Text {
                            text: "Frequency Band"
                            font.family: ThemeService.typography.fontFamilyUi
                            font.pixelSize: ThemeService.typography.fontSizeSmall
                            color: ThemeService.colors.textSecondary
                        }

                        RowLayout {
                            spacing: 8
                            Pill {
                                text: "2.4 GHz (Long Range)"
                                active: hotspotWindow.selectedBand === "2.4 GHz"
                                onClicked: hotspotWindow.selectedBand = "2.4 GHz"
                            }
                            Pill {
                                text: "5 GHz (High Speed)"
                                active: hotspotWindow.selectedBand === "5 GHz"
                                onClicked: hotspotWindow.selectedBand = "5 GHz"
                            }
                        }
                    }
                }

                // Right Column: Instant QR Code Scanner Box
                Rectangle {
                    implicitWidth: 170
                    implicitHeight: 180
                    radius: ThemeService.metrics.radiusMedium
                    color: ThemeService.colors.surface
                    border.color: ThemeService.colors.border
                    border.width: 1

                    ColumnLayout {
                        anchors.centerIn: parent
                        spacing: 8

                        Rectangle {
                            Layout.alignment: Qt.AlignHCenter
                            implicitWidth: 120
                            implicitHeight: 120
                            color: "#ffffff"
                            radius: 8

                            Image {
                                anchors.centerIn: parent
                                width: 110
                                height: 110
                                source: hotspotWindow.qrImagePath || ""
                                fillMode: Image.PreserveAspectFit
                            }

                            Text {
                                anchors.centerIn: parent
                                visible: !hotspotWindow.qrImagePath
                                text: "󰅖\nNo QR"
                                horizontalAlignment: Text.AlignHCenter
                                font.family: ThemeService.typography.fontFamilyMono
                                font.pixelSize: 14
                                color: "#888888"
                            }
                        }

                        Text {
                            Layout.alignment: Qt.AlignHCenter
                            text: "Scan with Phone"
                            font.family: ThemeService.typography.fontFamilyUi
                            font.pixelSize: ThemeService.typography.fontSizeSmall
                            color: ThemeService.colors.textMuted
                        }
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 1
                color: ThemeService.colors.border
            }

            // 4. Connected Devices Section
            ColumnLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: 6

                RowLayout {
                    Layout.fillWidth: true
                    Text {
                        text: "Connected Clients"
                        font.family: ThemeService.typography.fontFamilyUi
                        font.pixelSize: ThemeService.typography.fontSizeNormal
                        font.weight: Font.Bold
                        color: ThemeService.colors.textPrimary
                    }
                    Item { Layout.fillWidth: true }
                    Text {
                        text: hotspotWindow.clientList.length + " device(s)"
                        font.family: ThemeService.typography.fontFamilyMono
                        font.pixelSize: ThemeService.typography.fontSizeSmall
                        color: ThemeService.colors.textSecondary
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    radius: ThemeService.metrics.radiusSmall
                    color: ThemeService.colors.surface
                    border.color: ThemeService.colors.border
                    border.width: 1

                    Text {
                        anchors.centerIn: parent
                        visible: hotspotWindow.clientList.length === 0
                        text: "No clients currently connected to this hotspot"
                        font.family: ThemeService.typography.fontFamilyUi
                        font.pixelSize: ThemeService.typography.fontSizeSmall
                        color: ThemeService.colors.textMuted
                    }
                }
            }
        }
    }

    // Backend Execution Processes
    Process {
        id: detectProc
        stdout: SplitParser {
            onRead: function(data) {
                try {
                    var parsed = JSON.parse(data);
                    hotspotWindow.isSupported = parsed.ap_mode_supported;
                } catch(e) {}
            }
        }
    }

    Process {
        id: startProc
        stdout: SplitParser {
            onRead: function(data) {
                try {
                    var parsed = JSON.parse(data);
                    if (parsed.success) {
                        hotspotWindow.isHotspotRunning = true;
                        hotspotWindow.qrImagePath = parsed.qr_path ? ("file://" + parsed.qr_path) : "";
                    }
                } catch(e) {}
            }
        }
    }

    Process {
        id: stopProc
        stdout: SplitParser {
            onRead: function(data) {
                hotspotWindow.isHotspotRunning = false;
                hotspotWindow.clientList = [];
            }
        }
    }

    Process {
        id: genPassProc
        stdout: SplitParser {
            onRead: function(data) {
                hotspotWindow.password = data.trim();
            }
        }
    }

    Component.onCompleted: {
        generateNewPassword();
    }
}
