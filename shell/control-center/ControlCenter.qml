import QtQuick
import QtQuick.Layouts
import Quickshell
import Quickshell.Wayland
import Quickshell.Io
import "../services"
import "../components"

PanelWindow {
    id: ccWindow

    required property var screen
    property bool isOpen: false

    visible: isOpen

    anchors {
        top: true
        right: true
    }

    implicitWidth: 360
    implicitHeight: 520
    color: "transparent"

    WlrLayershell.layer: WlrLayer.Overlay
    WlrLayershell.exclusiveZone: 0

    // Hardware State Properties
    property bool wifiEnabled: true
    property string wifiSsid: "Wi-Fi"
    property bool bluetoothEnabled: true
    property bool dndEnabled: false
    property bool hotspotActive: false
    property bool nightLightEnabled: false
    property string powerProfile: "balanced"
    property real masterVolume: 0.65
    property real brightnessLevel: 0.70

    // Animation on appearance
    opacity: isOpen ? 1.0 : 0.0
    scale: isOpen ? 1.0 : 0.95

    Behavior on opacity { NumberAnimation { duration: ThemeService.effects.animationDurationMs } }
    Behavior on scale { NumberAnimation { duration: ThemeService.effects.animationDurationMs; easing.type: Easing.OutCubic } }

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
            anchors.margins: 16
            spacing: 14

            // 1. Header: Device Info & Close Button
            RowLayout {
                Layout.fillWidth: true

                ColumnLayout {
                    spacing: 2
                    Text {
                        text: "Control Center"
                        font.family: ThemeService.typography.fontFamilyUi
                        font.pixelSize: ThemeService.typography.fontSizeLarge
                        font.weight: Font.Bold
                        color: ThemeService.colors.textPrimary
                    }
                    Text {
                        text: "HP EliteBook 840 G5 • Arch Linux"
                        font.family: ThemeService.typography.fontFamilyUi
                        font.pixelSize: ThemeService.typography.fontSizeSmall
                        color: ThemeService.colors.textMuted
                    }
                }

                Item { Layout.fillWidth: true }

                Rectangle {
                    implicitWidth: 28
                    implicitHeight: 28
                    radius: 14
                    color: closeMouse.containsMouse ? ThemeService.colors.surfaceHover : ThemeService.colors.surfaceVariant

                    Text {
                        anchors.centerIn: parent
                        text: "󰅖"
                        font.family: ThemeService.typography.fontFamilyMono
                        font.pixelSize: ThemeService.typography.fontSizeSmall
                        color: ThemeService.colors.textSecondary
                    }

                    MouseArea {
                        id: closeMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: ccWindow.isOpen = false
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 1
                color: ThemeService.colors.border
            }

            // 2. Quick Toggles Grid (2x3)
            GridLayout {
                Layout.fillWidth: true
                columns: 2
                rowSpacing: 8
                columnSpacing: 8

                QuickToggle {
                    Layout.fillWidth: true
                    title: "Wi-Fi"
                    subtitle: ccWindow.wifiEnabled ? ccWindow.wifiSsid : "Disabled"
                    icon: ccWindow.wifiEnabled ? "󰤨" : "󰤮"
                    active: ccWindow.wifiEnabled
                    hasDetails: true
                    onClicked: {
                        ccWindow.wifiEnabled = !ccWindow.wifiEnabled;
                        var cmd = ccWindow.wifiEnabled ? "nmcli radio wifi on" : "nmcli radio wifi off";
                        execProc.exec(cmd);
                    }
                }

                QuickToggle {
                    Layout.fillWidth: true
                    title: "Bluetooth"
                    subtitle: ccWindow.bluetoothEnabled ? "Active" : "Disabled"
                    icon: ccWindow.bluetoothEnabled ? "󰂯" : "󰂲"
                    active: ccWindow.bluetoothEnabled
                    onClicked: {
                        ccWindow.bluetoothEnabled = !ccWindow.bluetoothEnabled;
                        var cmd = ccWindow.bluetoothEnabled ? "bluetoothctl power on" : "bluetoothctl power off";
                        execProc.exec(cmd);
                    }
                }

                QuickToggle {
                    Layout.fillWidth: true
                    title: "Do Not Disturb"
                    subtitle: ccWindow.dndEnabled ? "Silent" : "Alerts On"
                    icon: ccWindow.dndEnabled ? "󰂛" : "󰂚"
                    active: ccWindow.dndEnabled
                    onClicked: ccWindow.dndEnabled = !ccWindow.dndEnabled
                }

                QuickToggle {
                    Layout.fillWidth: true
                    title: "Theme Mode"
                    subtitle: ThemeService.isDark ? "Dark Theme" : "Light Theme"
                    icon: ThemeService.isDark ? "󰃚" : "󰃛"
                    active: ThemeService.isDark
                    onClicked: {
                        var nextTheme = ThemeService.isDark ? "Nordic Light" : "Midnight";
                        ThemeService.setPreset(nextTheme);
                    }
                }

                QuickToggle {
                    Layout.fillWidth: true
                    title: "Hotspot"
                    subtitle: ccWindow.hotspotActive ? "Sharing" : "Off"
                    icon: ccWindow.hotspotActive ? "󰖩" : "󰖪"
                    active: ccWindow.hotspotActive
                    hasDetails: true
                    onClicked: ccWindow.hotspotActive = !ccWindow.hotspotActive
                }

                QuickToggle {
                    Layout.fillWidth: true
                    title: "Night Light"
                    subtitle: ccWindow.nightLightEnabled ? "Warm (3500K)" : "Normal"
                    icon: "󰛨"
                    active: ccWindow.nightLightEnabled
                    onClicked: ccWindow.nightLightEnabled = !ccWindow.nightLightEnabled
                }
            }

            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 1
                color: ThemeService.colors.border
            }

            // 3. Audio & Brightness Sliders
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 10

                // Master Volume
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10

                    Text {
                        text: ccWindow.masterVolume > 0 ? "󰕾" : "󰝟"
                        font.family: ThemeService.typography.fontFamilyMono
                        font.pixelSize: ThemeService.typography.fontSizeNormal
                        color: ThemeService.colors.accent
                    }

                    Slider {
                        Layout.fillWidth: true
                        value: ccWindow.masterVolume
                        onValueChanged: function(v) {
                            ccWindow.masterVolume = v;
                            ccWindow.pendingVolume = v;
                            volumeDebounce.restart();
                        }
                    }

                    Text {
                        text: Math.round(ccWindow.masterVolume * 100) + "%"
                        font.family: ThemeService.typography.fontFamilyMono
                        font.pixelSize: ThemeService.typography.fontSizeSmall
                        color: ThemeService.colors.textSecondary
                        Layout.preferredWidth: 35
                    }
                }

                // Screen Brightness
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10

                    Text {
                        text: "󰃠"
                        font.family: ThemeService.typography.fontFamilyMono
                        font.pixelSize: ThemeService.typography.fontSizeNormal
                        color: ThemeService.colors.accent
                    }

                    Slider {
                        Layout.fillWidth: true
                        value: ccWindow.brightnessLevel
                        onValueChanged: function(v) {
                            ccWindow.brightnessLevel = v;
                            ccWindow.pendingBrightness = v;
                            brightnessDebounce.restart();
                        }
                    }

                    Text {
                        text: Math.round(ccWindow.brightnessLevel * 100) + "%"
                        font.family: ThemeService.typography.fontFamilyMono
                        font.pixelSize: ThemeService.typography.fontSizeSmall
                        color: ThemeService.colors.textSecondary
                        Layout.preferredWidth: 35
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 1
                color: ThemeService.colors.border
            }

            // 4. Power Profile Pills
            RowLayout {
                Layout.fillWidth: true
                spacing: 6

                Text {
                    text: "Profile:"
                    font.family: ThemeService.typography.fontFamilyUi
                    font.pixelSize: ThemeService.typography.fontSizeSmall
                    color: ThemeService.colors.textMuted
                }

                Pill {
                    text: "Battery Saver"
                    active: ccWindow.powerProfile === "power-saver"
                    onClicked: {
                        ccWindow.powerProfile = "power-saver";
                        execProc.exec("powerprofilesctl set power-saver");
                    }
                }

                Pill {
                    text: "Balanced"
                    active: ccWindow.powerProfile === "balanced"
                    onClicked: {
                        ccWindow.powerProfile = "balanced";
                        execProc.exec("powerprofilesctl set balanced");
                    }
                }

                Pill {
                    text: "Performance"
                    active: ccWindow.powerProfile === "performance"
                    onClicked: {
                        ccWindow.powerProfile = "performance";
                        execProc.exec("powerprofilesctl set performance");
                    }
                }
            }

            Item { Layout.fillHeight: true }

            // 5. Session Action Buttons (Lock, Suspend, Reboot, Shutdown)
            RowLayout {
                Layout.fillWidth: true
                spacing: 8

                Button {
                    Layout.fillWidth: true
                    variant: "secondary"
                    icon: "󰌾"
                    text: "Lock"
                    onClicked: {
                        ccWindow.isOpen = false;
                        execProc.exec("hyprlock");
                    }
                }

                Button {
                    Layout.fillWidth: true
                    variant: "secondary"
                    icon: "󰤄"
                    text: "Sleep"
                    onClicked: {
                        ccWindow.isOpen = false;
                        execProc.exec("systemctl suspend");
                    }
                }

                Button {
                    Layout.fillWidth: true
                    variant: "secondary"
                    icon: "󰑐"
                    text: "Reboot"
                    onClicked: {
                        ccWindow.isOpen = false;
                        execProc.exec("systemctl reboot");
                    }
                }

                Button {
                    Layout.fillWidth: true
                    variant: "danger"
                    icon: "󰐥"
                    text: "Power"
                    onClicked: {
                        ccWindow.isOpen = false;
                        execProc.exec("systemctl poweroff");
                    }
                }
            }
        }
    }

    // Throttling timers for volume and brightness sliders to prevent subprocess storm
    property real pendingVolume: masterVolume
    property real pendingBrightness: brightnessLevel

    Timer {
        id: volumeDebounce
        interval: 60
        repeat: false
        onTriggered: {
            execProc.exec("wpctl set-volume @DEFAULT_AUDIO_SINK@ " + ccWindow.pendingVolume.toFixed(2));
            HardwareService.refreshAudio();
        }
    }

    Timer {
        id: brightnessDebounce
        interval: 60
        repeat: false
        onTriggered: {
            var pct = Math.max(5, Math.round(ccWindow.pendingBrightness * 100));
            execProc.exec("brightnessctl set " + pct + "%");
        }
    }

    // Helper process for non-blocking shell dispatch
    Process {
        id: execProc
        function exec(shCmd) {
            command = ["sh", "-c", shCmd];
            running = true;
        }
    }
}
