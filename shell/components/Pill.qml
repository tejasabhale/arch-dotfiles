import QtQuick
import QtQuick.Layouts
import "../services"

Rectangle {
    id: pillRoot

    property string text: ""
    property string icon: ""
    property bool active: false
    property color activeColor: ThemeService.colors.accent
    property color inactiveColor: ThemeService.colors.surfaceVariant

    signal clicked()

    implicitWidth: pillLayout.implicitWidth + 16
    implicitHeight: 26
    radius: height / 2

    color: active ? activeColor : (mouseArea.containsMouse ? ThemeService.colors.surfaceHover : inactiveColor)
    border.color: active ? activeColor : ThemeService.colors.border
    border.width: ThemeService.metrics.borderWidth

    Behavior on color {
        ColorAnimation { duration: ThemeService.effects.animationDurationMs }
    }

    RowLayout {
        id: pillLayout
        anchors.centerIn: parent
        spacing: 6

        Text {
            visible: pillRoot.icon !== ""
            text: pillRoot.icon
            font.family: ThemeService.typography.fontFamilyMono
            font.pixelSize: ThemeService.typography.fontSizeNormal
            color: pillRoot.active ? "#ffffff" : ThemeService.colors.textPrimary
            verticalAlignment: Text.AlignVCenter
        }

        Text {
            visible: pillRoot.text !== ""
            text: pillRoot.text
            font.family: ThemeService.typography.fontFamilyUi
            font.pixelSize: ThemeService.typography.fontSizeSmall
            font.weight: Font.Medium
            color: pillRoot.active ? "#ffffff" : ThemeService.colors.textSecondary
            verticalAlignment: Text.AlignVCenter
        }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: pillRoot.clicked()
    }
}
