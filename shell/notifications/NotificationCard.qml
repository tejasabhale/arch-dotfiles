import QtQuick
import QtQuick.Layouts
import "../services"

Rectangle {
    id: cardRoot

    property string appName: "System"
    property string summary: "Notification Title"
    property string body: "Notification body description text goes here."
    property string icon: "󰂚"
    property string timeStr: "Just now"

    signal dismissed()
    signal actionTriggered()

    implicitWidth: 320
    implicitHeight: layout.implicitHeight + 20
    radius: ThemeService.metrics.radiusMedium
    color: ThemeService.colors.surface
    border.color: ThemeService.colors.border
    border.width: ThemeService.metrics.borderWidth

    ColumnLayout {
        id: layout
        anchors.fill: parent
        anchors.margins: 10
        spacing: 6

        // Header: App Icon, Name, Time, Dismiss
        RowLayout {
            Layout.fillWidth: true
            spacing: 6

            Text {
                text: cardRoot.icon
                font.family: ThemeService.typography.fontFamilyMono
                font.pixelSize: ThemeService.typography.fontSizeNormal
                color: ThemeService.colors.accent
            }

            Text {
                text: cardRoot.appName
                font.family: ThemeService.typography.fontFamilyUi
                font.pixelSize: ThemeService.typography.fontSizeSmall
                font.weight: Font.Bold
                color: ThemeService.colors.textPrimary
            }

            Item { Layout.fillWidth: true }

            Text {
                text: cardRoot.timeStr
                font.family: ThemeService.typography.fontFamilyUi
                font.pixelSize: 10
                color: ThemeService.colors.textMuted
            }

            // Dismiss Button
            Text {
                text: "󰅖"
                font.family: ThemeService.typography.fontFamilyMono
                font.pixelSize: 12
                color: dismissMouse.containsMouse ? ThemeService.colors.danger : ThemeService.colors.textMuted

                MouseArea {
                    id: dismissMouse
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: cardRoot.dismissed()
                }
            }
        }

        // Summary
        Text {
            text: cardRoot.summary
            font.family: ThemeService.typography.fontFamilyUi
            font.pixelSize: ThemeService.typography.fontSizeNormal
            font.weight: Font.Medium
            color: ThemeService.colors.textPrimary
            elide: Text.ElideRight
            Layout.fillWidth: true
        }

        // Body Text
        Text {
            text: cardRoot.body
            font.family: ThemeService.typography.fontFamilyUi
            font.pixelSize: ThemeService.typography.fontSizeSmall
            color: ThemeService.colors.textSecondary
            wrapMode: Text.Wrap
            Layout.fillWidth: true
            maximumLineCount: 3
            elide: Text.ElideRight
        }
    }
}
