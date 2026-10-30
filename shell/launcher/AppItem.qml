import QtQuick
import QtQuick.Layouts
import "../services"

Rectangle {
    id: itemRoot

    property string name: ""
    property string category: ""
    property string execCmd: ""
    property string iconGlyph: "󰣇"
    property bool isSelected: false

    signal clicked()

    implicitWidth: 140
    implicitHeight: 88
    radius: ThemeService.metrics.radiusMedium

    color: isSelected ? ThemeService.colors.accent : (mouseArea.containsMouse ? ThemeService.colors.surfaceHover : ThemeService.colors.surfaceVariant)
    border.color: isSelected ? ThemeService.colors.accent : ThemeService.colors.border
    border.width: ThemeService.metrics.borderWidth

    Behavior on color {
        ColorAnimation { duration: ThemeService.effects.animationDurationMs }
    }

    ColumnLayout {
        anchors.centerIn: parent
        spacing: 6

        // Application Icon Container
        Rectangle {
            Layout.alignment: Qt.AlignHCenter
            implicitWidth: 40
            implicitHeight: 40
            radius: ThemeService.metrics.radiusSmall
            color: itemRoot.isSelected ? "#ffffff22" : ThemeService.colors.surface
            border.color: itemRoot.isSelected ? "#ffffff44" : ThemeService.colors.border
            border.width: 1

            Text {
                anchors.centerIn: parent
                text: itemRoot.iconGlyph
                font.family: ThemeService.typography.fontFamilyMono
                font.pixelSize: 20
                color: itemRoot.isSelected ? "#ffffff" : ThemeService.colors.accent
            }
        }

        // Application Name
        Text {
            Layout.alignment: Qt.AlignHCenter
            text: itemRoot.name
            font.family: ThemeService.typography.fontFamilyUi
            font.pixelSize: ThemeService.typography.fontSizeSmall
            font.weight: Font.Medium
            color: itemRoot.isSelected ? "#ffffff" : ThemeService.colors.textPrimary
            elide: Text.ElideRight
            Layout.maximumWidth: 125
        }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: itemRoot.clicked()
    }
}
