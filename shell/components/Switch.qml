import QtQuick
import "../services"

Item {
    id: switchRoot

    property bool checked: false
    property bool disabled: false

    signal toggled(bool state)

    implicitWidth: 44
    implicitHeight: 24

    opacity: disabled ? 0.5 : 1.0

    Rectangle {
        id: track
        anchors.fill: parent
        radius: height / 2
        color: switchRoot.checked ? ThemeService.colors.accent : ThemeService.colors.surfaceVariant
        border.color: ThemeService.colors.border
        border.width: ThemeService.metrics.borderWidth

        Behavior on color {
            ColorAnimation { duration: ThemeService.effects.animationDurationMs }
        }

        Rectangle {
            id: thumb
            width: parent.height - 6
            height: width
            radius: width / 2
            anchors.verticalCenter: parent.verticalCenter
            x: switchRoot.checked ? (parent.width - width - 3) : 3
            color: "#ffffff"

            Behavior on x {
                NumberAnimation {
                    duration: ThemeService.effects.animationDurationMs
                    easing.type: Easing.OutCubic
                }
            }
        }
    }

    MouseArea {
        anchors.fill: parent
        enabled: !switchRoot.disabled
        cursorShape: Qt.PointingHandCursor
        onClicked: {
            switchRoot.checked = !switchRoot.checked;
            switchRoot.toggled(switchRoot.checked);
        }
    }
}
