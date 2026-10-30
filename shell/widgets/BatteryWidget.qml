import QtQuick
import QtQuick.Layouts
import Quickshell.Io
import "../services"

Rectangle {
    id: battRoot

    property int percentage: 85
    property bool isCharging: false
    property string icon: {
        if (isCharging) return "󰂄";
        if (percentage >= 90) return "󰁹";
        if (percentage >= 70) return "󰂀";
        if (percentage >= 50) return "󰁾";
        if (percentage >= 30) return "󰁼";
        if (percentage >= 15) return "󰁺";
        return "󰂃";
    }

    implicitWidth: battLayout.implicitWidth + 12
    implicitHeight: 28
    radius: ThemeService.metrics.radiusSmall
    color: ThemeService.colors.surfaceVariant
    border.color: ThemeService.colors.border
    border.width: ThemeService.metrics.borderWidth

    // Read battery status via Process (battery-friendly interval: every 15s)
    Process {
        id: battProc
        command: ["sh", "-c", "cat /sys/class/power_supply/BAT0/capacity 2>/dev/null; cat /sys/class/power_supply/BAT0/status 2>/dev/null"]
        stdout: SplitParser {
            onRead: function(data) {
                var lines = data.trim().split("\n");
                if (lines.length >= 1 && lines[0]) {
                    var cap = parseInt(lines[0]);
                    if (!isNaN(cap)) battRoot.percentage = cap;
                }
                if (lines.length >= 2) {
                    battRoot.isCharging = (lines[1].trim() === "Charging");
                }
            }
        }
    }

    Timer {
        interval: 15000
        running: true
        repeat: true
        triggeredOnStart: true
        onTriggered: battProc.running = true
    }

    RowLayout {
        id: battLayout
        anchors.centerIn: parent
        spacing: 5

        Text {
            text: battRoot.icon
            font.family: ThemeService.typography.fontFamilyMono
            font.pixelSize: ThemeService.typography.fontSizeNormal
            color: battRoot.percentage <= 15 ? ThemeService.colors.danger : (battRoot.isCharging ? ThemeService.colors.success : ThemeService.colors.accent)
        }

        Text {
            text: battRoot.percentage + "%"
            font.family: ThemeService.typography.fontFamilyMono
            font.pixelSize: ThemeService.typography.fontSizeSmall
            font.weight: Font.Medium
            color: ThemeService.colors.textPrimary
        }
    }
}
