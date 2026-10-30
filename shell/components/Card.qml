import QtQuick
import QtQuick.Layouts
import "../services"

Rectangle {
    id: cardRoot

    property bool interactive: false
    property bool hovered: mouseArea.containsMouse
    property color cardColor: ThemeService.colors.surface
    property color hoverColor: ThemeService.colors.surfaceHover
    property color borderColor: hovered && interactive ? ThemeService.colors.borderFocus : ThemeService.colors.border
    property int customRadius: ThemeService.metrics.radiusMedium
    property int padding: 12

    signal clicked()

    color: (interactive && hovered) ? hoverColor : cardColor
    border.color: borderColor
    border.width: ThemeService.metrics.borderWidth
    radius: customRadius

    Behavior on color {
        ColorAnimation { duration: ThemeService.effects.animationDurationMs }
    }

    Behavior on border.color {
        ColorAnimation { duration: ThemeService.effects.animationDurationMs }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        enabled: cardRoot.interactive
        hoverEnabled: cardRoot.interactive
        cursorShape: cardRoot.interactive ? Qt.PointingHandCursor : Qt.ArrowCursor
        onClicked: cardRoot.clicked()
    }
}
