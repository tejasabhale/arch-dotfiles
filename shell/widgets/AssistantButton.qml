import QtQuick
import QtQuick.Layouts
import Quickshell.Io
import "../services"

Rectangle {
    id: assistantBtnRoot

    signal clicked()

    property string assistantName: "June"
    property string assistantAvatar: "󱚣"
    property bool isActive: false

    implicitWidth: btnLayout.implicitWidth + 12
    implicitHeight: 28
    radius: ThemeService.metrics.radiusSmall

    color: mouseArea.containsMouse ? ThemeService.colors.accentHover : (isActive ? ThemeService.colors.accent : ThemeService.colors.surfaceVariant)
    border.color: ThemeService.colors.borderFocus
    border.width: ThemeService.metrics.borderWidth

    Behavior on color {
        ColorAnimation { duration: ThemeService.effects.animationDurationMs }
    }

    RowLayout {
        id: btnLayout
        anchors.centerIn: parent
        spacing: 5

        Text {
            text: assistantBtnRoot.assistantAvatar
            font.family: ThemeService.typography.fontFamilyMono
            font.pixelSize: ThemeService.typography.fontSizeNormal
            color: assistantBtnRoot.isActive || mouseArea.containsMouse ? "#ffffff" : ThemeService.colors.accent
        }

        Text {
            text: assistantBtnRoot.assistantName
            font.family: ThemeService.typography.fontFamilyUi
            font.pixelSize: ThemeService.typography.fontSizeSmall
            font.weight: Font.Bold
            color: assistantBtnRoot.isActive || mouseArea.containsMouse ? "#ffffff" : ThemeService.colors.textPrimary
        }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: assistantBtnRoot.clicked()
    }

    Process {
        id: nameProc
        command: ["python3", "-m", "assistant.core.cli", "--ping", "--json"]
        running: true
        stdout: StdioCollector {
            onCollected: function(text) {
                try {
                    var data = JSON.parse(text);
                    if (data.name) assistantBtnRoot.assistantName = data.name;
                    if (data.avatar) assistantBtnRoot.assistantAvatar = data.avatar;
                } catch(e) {}
            }
        }
    }
}
