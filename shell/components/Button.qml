import QtQuick
import QtQuick.Layouts
import "../services"

Rectangle {
    id: btnRoot

    property string text: ""
    property string icon: ""
    property string variant: "primary" // "primary", "secondary", "ghost", "danger"
    property bool disabled: false
    property int customRadius: ThemeService.metrics.radiusSmall
    property int horizontalPadding: 14
    property int verticalPadding: 8

    signal clicked()

    implicitWidth: contentRow.implicitWidth + (horizontalPadding * 2)
    implicitHeight: Math.max(34, contentRow.implicitHeight + (verticalPadding * 2))

    radius: customRadius
    border.width: variant === "secondary" ? ThemeService.metrics.borderWidth : 0
    border.color: mouseArea.containsMouse ? ThemeService.colors.borderFocus : ThemeService.colors.border

    opacity: disabled ? 0.5 : (mouseArea.pressed ? 0.85 : 1.0)

    color: {
        if (variant === "primary") {
            return mouseArea.containsMouse ? ThemeService.colors.accentHover : ThemeService.colors.accent;
        } else if (variant === "secondary") {
            return mouseArea.containsMouse ? ThemeService.colors.surfaceHover : ThemeService.colors.surface;
        } else if (variant === "danger") {
            return ThemeService.colors.danger;
        } else { // ghost
            return mouseArea.containsMouse ? ThemeService.colors.surfaceVariant : "transparent";
        }
    }

    Behavior on color {
        ColorAnimation { duration: ThemeService.effects.animationDurationMs }
    }

    RowLayout {
        id: contentRow
        anchors.centerIn: parent
        spacing: 8

        Text {
            visible: btnRoot.icon !== ""
            text: btnRoot.icon
            font.family: ThemeService.typography.fontFamilyMono
            font.pixelSize: ThemeService.typography.fontSizeLarge
            color: btnRoot.variant === "primary" ? "#ffffff" : ThemeService.colors.textPrimary
            verticalAlignment: Text.AlignVCenter
        }

        Text {
            visible: btnRoot.text !== ""
            text: btnRoot.text
            font.family: ThemeService.typography.fontFamilyUi
            font.pixelSize: ThemeService.typography.fontSizeNormal
            font.weight: Font.Medium
            color: btnRoot.variant === "primary" ? "#ffffff" : ThemeService.colors.textPrimary
            verticalAlignment: Text.AlignVCenter
        }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        enabled: !btnRoot.disabled
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: btnRoot.clicked()
    }
}
