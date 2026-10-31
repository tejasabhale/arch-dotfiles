import QtQuick
import QtQuick.Layouts
import "../services"

Rectangle {
    id: audioRoot

    signal clicked()

    property int volume: HardwareService.volume
    property bool isMuted: HardwareService.isMuted
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
