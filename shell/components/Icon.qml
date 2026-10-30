import QtQuick
import "../services"

Item {
    id: iconRoot

    property string name: "" // Glyph character or Nerd Font icon
    property int size: ThemeService.typography.fontSizeLarge
    property color iconColor: ThemeService.colors.textPrimary

    implicitWidth: size
    implicitHeight: size

    Text {
        anchors.centerIn: parent
        text: iconRoot.name
        font.family: ThemeService.typography.fontFamilyMono
        font.pixelSize: iconRoot.size
        color: iconRoot.iconColor
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }
}
