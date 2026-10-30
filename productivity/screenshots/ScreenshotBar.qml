import QtQuick
import QtQuick.Layouts
import Quickshell
import Quickshell.Wayland
import Quickshell.Io
import "../../shell/services"
import "../../shell/components"

PanelWindow {
    id: screenshotWindow

    required property var screen
    property bool isOpen: false

    visible: isOpen

    anchors {
        top: true
    }

    implicitWidth: 320
    implicitHeight: 60
    color: "transparent"

    WlrLayershell.layer: WlrLayer.Overlay
    WlrLayershell.exclusiveZone: 0

    property bool isRecording: false

    function toggle() {
        isOpen = !isOpen;
    }

    function capture(mode) {
        screenshotWindow.isOpen = false;
        capProc.command = ["python3", "-m", "productivity.screenshots.screenshot_manager", mode];
        capProc.running = true;
    }

    function toggleRecording() {
        if (isRecording) {
            recProc.command = ["python3", "-m", "productivity.screenshots.screenshot_manager", "record-stop"];
            isRecording = false;
        } else {
            recProc.command = ["python3", "-m", "productivity.screenshots.screenshot_manager", "record-start"];
            isRecording = true;
        }
        recProc.running = true;
    }

    Rectangle {
        anchors.fill: parent
        anchors.topMargin: ThemeService.metrics.barHeight + 12
        radius: ThemeService.metrics.radiusLarge
        color: ThemeService.colors.backgroundBlur
        border.color: ThemeService.colors.border
        border.width: ThemeService.metrics.borderWidth

        RowLayout {
            anchors.centerIn: parent
            spacing: 8

            Button {
                variant: "secondary"
                icon: "󰒉"
                text: "Region"
                onClicked: screenshotWindow.capture("region")
            }

            Button {
                variant: "secondary"
                icon: "󰍹"
                text: "Window"
                onClicked: screenshotWindow.capture("window")
            }

            Button {
                variant: "secondary"
                icon: "󰹑"
                text: "Screen"
                onClicked: screenshotWindow.capture("screen")
            }

            Button {
                variant: screenshotWindow.isRecording ? "danger" : "ghost"
                icon: "󰕧"
                text: screenshotWindow.isRecording ? "Stop Rec" : "Record"
                onClicked: screenshotWindow.toggleRecording()
            }

            Rectangle {
                implicitWidth: 24
                implicitHeight: 24
                radius: 12
                color: closeMouse.containsMouse ? ThemeService.colors.surfaceHover : ThemeService.colors.surfaceVariant

                Text {
                    anchors.centerIn: parent
                    text: "󰅖"
                    font.family: ThemeService.typography.fontFamilyMono
                    font.pixelSize: 10
                    color: ThemeService.colors.textSecondary
                }

                MouseArea {
                    id: closeMouse
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: screenshotWindow.isOpen = false
                }
            }
        }
    }

    Process { id: capProc }
    Process { id: recProc }
}
