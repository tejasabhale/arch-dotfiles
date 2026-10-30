import QtQuick
import QtQuick.Layouts
import Quickshell.Services.SystemTray
import "../services"

RowLayout {
    id: trayRoot
    spacing: 6

    Repeater {
        model: SystemTray.items

        Rectangle {
            id: trayItem
            required property var modelData

            implicitWidth: 24
            implicitHeight: 24
            radius: ThemeService.metrics.radiusSmall
            color: itemMouse.containsMouse ? ThemeService.colors.surfaceHover : "transparent"

            Image {
                anchors.centerIn: parent
                width: 18
                height: 18
                source: modelData.icon || ""
                smooth: true
            }

            MouseArea {
                id: itemMouse
                anchors.fill: parent
                hoverEnabled: true
                acceptedButtons: Qt.LeftButton | Qt.RightButton
                cursorShape: Qt.PointingHandCursor
                onClicked: function(mouse) {
                    if (mouse.button === Qt.LeftButton) {
                        modelData.activate();
                    } else if (mouse.button === Qt.RightButton) {
                        modelData.secondaryActivate();
                    }
                }
            }
        }
    }
}
