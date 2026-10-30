import QtQuick
import QtQuick.Layouts
import Quickshell.Io
import "../services"

Rectangle {
    id: audioRoot

    signal clicked()

    property int volume: 65
    property bool isMuted: false
    property string icon: {
        if (isMuted) return "󰝟";
        if (volume >= 60) return "󰕾";
        if (volume >= 25) return "󰖀";
        if (volume > 0) return "󰕿";
        return "󰝟";
    }

    implicitWidth: audioLayout.implicitWidth + 12
    implicitHeight: 28
    radius: ThemeService.metrics.radiusSmall
    color: mouseArea.containsMouse ? ThemeService.colors.surfaceHover : ThemeService.colors.surfaceVariant
    border.color: ThemeService.colors.border
    border.width: ThemeService.metrics.borderWidth

    // Read volume status via wpctl
    Process {
        id: volProc
        command: ["sh", "-c", "wpctl get-volume @DEFAULT_AUDIO_SINK@"]
        stdout: SplitParser {
            onRead: function(data) {
                // Example output: "Volume: 0.65 [MUTED]" or "Volume: 0.65"
                var str = data.trim();
                audioRoot.isMuted = str.indexOf("[MUTED]") !== -1;
                var match = str.match(/Volume:\s+([0-9\.]+)/);
                if (match && match[1]) {
                    audioRoot.volume = Math.round(parseFloat(match[1]) * 100);
                }
            }
        }
    }

    Timer {
        interval: 3000
        running: true
        repeat: true
        triggeredOnStart: true
        onTriggered: volProc.running = true
    }

    RowLayout {
        id: audioLayout
        anchors.centerIn: parent
        spacing: 5

        Text {
            text: audioRoot.icon
            font.family: ThemeService.typography.fontFamilyMono
            font.pixelSize: ThemeService.typography.fontSizeNormal
            color: audioRoot.isMuted ? ThemeService.colors.danger : ThemeService.colors.accent
        }

        Text {
            text: audioRoot.isMuted ? "Muted" : (audioRoot.volume + "%")
            font.family: ThemeService.typography.fontFamilyMono
            font.pixelSize: ThemeService.typography.fontSizeSmall
            font.weight: Font.Medium
            color: ThemeService.colors.textPrimary
        }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: audioRoot.clicked()
    }
}
