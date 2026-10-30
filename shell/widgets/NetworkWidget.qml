import QtQuick
import QtQuick.Layouts
import Quickshell.Io
import "../services"

Rectangle {
    id: netRoot

    signal clicked()

    property bool isConnected: true
    property string ssid: "Wi-Fi"
    property string icon: isConnected ? "󰤨" : "󰤮"

    implicitWidth: netLayout.implicitWidth + 12
    implicitHeight: 28
    radius: ThemeService.metrics.radiusSmall
    color: mouseArea.containsMouse ? ThemeService.colors.surfaceHover : ThemeService.colors.surfaceVariant
    border.color: ThemeService.colors.border
    border.width: ThemeService.metrics.borderWidth

    Process {
        id: netProc
        command: ["sh", "-c", "nmcli -t -f active,ssid dev wifi | grep '^yes' | cut -d: -f2"]
        stdout: SplitParser {
            onRead: function(data) {
                var name = data.trim();
                if (name) {
                    netRoot.isConnected = true;
                    netRoot.ssid = name;
                } else {
                    netRoot.isConnected = false;
                    netRoot.ssid = "Disconnected";
                }
            }
        }
    }

    Timer {
        interval: 10000
        running: true
        repeat: true
        triggeredOnStart: true
        onTriggered: netProc.running = true
    }

    RowLayout {
        id: netLayout
        anchors.centerIn: parent
        spacing: 5

        Text {
            text: netRoot.icon
            font.family: ThemeService.typography.fontFamilyMono
            font.pixelSize: ThemeService.typography.fontSizeNormal
            color: netRoot.isConnected ? ThemeService.colors.accent : ThemeService.colors.textMuted
        }

        Text {
            text: netRoot.ssid
            font.family: ThemeService.typography.fontFamilyUi
            font.pixelSize: ThemeService.typography.fontSizeSmall
            font.weight: Font.Medium
            color: ThemeService.colors.textPrimary
            elide: Text.ElideRight
            Layout.maximumWidth: 100
        }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: netRoot.clicked()
    }
}
