import QtQuick
import QtQuick.Layouts
import "../services"

Rectangle {
    id: battRoot

    property int percentage: HardwareService.batteryPercentage
    property bool isCharging: HardwareService.isCharging
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
