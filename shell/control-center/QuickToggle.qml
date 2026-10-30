import QtQuick
import QtQuick.Layouts
import "../services"

Rectangle {
    id: toggleRoot

    property string title: ""
    property string subtitle: ""
    property string icon: ""
    property bool active: false
    property bool hasDetails: false

    signal clicked()
    signal detailsClicked()

    implicitWidth: 160
    implicitHeight: 56
    radius: ThemeService.metrics.radiusMedium

    color: active ? ThemeService.colors.accent : (mouseArea.containsMouse ? ThemeService.colors.surfaceHover : ThemeService.colors.surfaceVariant)
    border.color: active ? ThemeService.colors.accent : ThemeService.colors.border
    border.width: ThemeService.metrics.borderWidth

    Behavior on color {
        ColorAnimation { duration: ThemeService.effects.animationDurationMs }
    }

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 12
        anchors.rightMargin: 12
        spacing: 10

        // Toggle Icon
        Rectangle {
            implicitWidth: 34
            implicitHeight: 34
            radius: 17
            color: toggleRoot.active ? "#ffffff22" : ThemeService.colors.surface
            border.color: toggleRoot.active ? "#ffffff44" : ThemeService.colors.border
            border.width: 1

            Text {
                anchors.centerIn: parent
                text: toggleRoot.icon
                font.family: ThemeService.typography.fontFamilyMono
                font.pixelSize: 16
                color: toggleRoot.active ? "#ffffff" : ThemeService.colors.accent
            }
        }

        // Title and Subtitle
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 2

            Text {
                text: toggleRoot.title
                font.family: ThemeService.typography.fontFamilyUi
                font.pixelSize: ThemeService.typography.fontSizeNormal
                font.weight: Font.Medium
                color: toggleRoot.active ? "#ffffff" : ThemeService.colors.textPrimary
                elide: Text.ElideRight
                Layout.fillWidth: true
            }

            Text {
                visible: toggleRoot.subtitle !== ""
                text: toggleRoot.subtitle
                font.family: ThemeService.typography.fontFamilyUi
                font.pixelSize: ThemeService.typography.fontSizeSmall
                color: toggleRoot.active ? "#ffffffcc" : ThemeService.colors.textMuted
                elide: Text.ElideRight
                Layout.fillWidth: true
            }
        }

        // Optional Chevron for opening details / settings
        Text {
            visible: toggleRoot.hasDetails
            text: "󰅂"
            font.family: ThemeService.typography.fontFamilyMono
            font.pixelSize: ThemeService.typography.fontSizeSmall
            color: toggleRoot.active ? "#ffffffaa" : ThemeService.colors.textMuted
        }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: toggleRoot.clicked()
    }
}
