import QtQuick
import "../services"

Item {
    id: sliderRoot

    property real from: 0.0
    property real to: 1.0
    property real value: 0.5
    property real stepSize: 0.01
    property bool disabled: false

    signal valueChanged(real val)
    signal moved(real val)

    implicitWidth: 160
    implicitHeight: 20

    opacity: disabled ? 0.5 : 1.0

    Rectangle {
        id: track
        anchors.verticalCenter: parent.verticalCenter
        width: parent.width
        height: 6
        radius: 3
        color: ThemeService.colors.surfaceVariant

        Rectangle {
            id: progress
            height: parent.height
            radius: parent.radius
            width: Math.max(0, Math.min(parent.width, ((sliderRoot.value - sliderRoot.from) / (sliderRoot.to - sliderRoot.from)) * parent.width))
            color: ThemeService.colors.accent

            Behavior on width {
                enabled: !mouseArea.drag.active
                NumberAnimation { duration: 100 }
            }
        }
    }

    Rectangle {
        id: handle
        width: 14
        height: 14
        radius: 7
        anchors.verticalCenter: track.verticalCenter
        x: Math.max(0, Math.min(track.width - width, ((sliderRoot.value - sliderRoot.from) / (sliderRoot.to - sliderRoot.from)) * (track.width - width)))
        color: "#ffffff"
        border.color: ThemeService.colors.accent
        border.width: 2

        Behavior on x {
            enabled: !mouseArea.drag.active
            NumberAnimation { duration: 100 }
        }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        enabled: !sliderRoot.disabled
        cursorShape: Qt.PointingHandCursor

        function updateValue(mouseX) {
            var ratio = Math.max(0.0, Math.min(1.0, mouseX / track.width));
            var newVal = sliderRoot.from + ratio * (sliderRoot.to - sliderRoot.from);
            sliderRoot.value = Math.round(newVal / sliderRoot.stepSize) * sliderRoot.stepSize;
            sliderRoot.moved(sliderRoot.value);
            sliderRoot.valueChanged(sliderRoot.value);
        }

        onPressed: function(mouse) { updateValue(mouse.x); }
        onPositionChanged: function(mouse) { if (pressed) updateValue(mouse.x); }
    }
}
