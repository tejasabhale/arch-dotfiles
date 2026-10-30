import QtQuick
import QtQuick.Layouts
import Quickshell
import Quickshell.Wayland
import Quickshell.Io
import "../../shell/services"
import "../../shell/components"

PanelWindow {
    id: clipWindow

    required property var screen
    property bool isOpen: false

    visible: isOpen

    anchors {
        top: true
        bottom: true
        left: true
        right: true
    }

    color: "transparent"

    WlrLayershell.layer: WlrLayer.Overlay
    WlrLayershell.keyboardFocus: isOpen ? WlrKeyboardFocus.Exclusive : WlrKeyboardFocus.None

    property var clipboardItems: []
    property string searchQuery: ""

    function toggle() {
        isOpen = !isOpen;
        if (isOpen) {
            searchQuery = "";
            refreshHistory();
        }
    }

    function refreshHistory() {
        listProc.command = ["python3", "-m", "productivity.clipboard.clipboard_manager", "list"];
        listProc.running = true;
    }

    function copyClip(clipId) {
        copyProc.command = ["python3", "-m", "productivity.clipboard.clipboard_manager", "copy", clipId];
        copyProc.running = true;
        clipWindow.isOpen = false;
    }

    function clearAll() {
        clearProc.command = ["python3", "-m", "productivity.clipboard.clipboard_manager", "clear"];
        clearProc.running = true;
    }

    MouseArea {
        anchors.fill: parent
        onClicked: clipWindow.isOpen = false
        Rectangle {
            anchors.fill: parent
            color: "#00000077"
        }
    }

    Rectangle {
        id: modalContent
        anchors.centerIn: parent
        implicitWidth: 520
        implicitHeight: 520
        radius: ThemeService.metrics.radiusLarge
        color: ThemeService.colors.backgroundBlur
        border.color: ThemeService.colors.border
        border.width: ThemeService.metrics.borderWidth
        clip: true

        MouseArea {
            anchors.fill: parent
            hoverEnabled: false
        }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 18
            spacing: 12

            // Header
            RowLayout {
                Layout.fillWidth: true

                Text {
                    text: "󰅌 Clipboard History"
                    font.family: ThemeService.typography.fontFamilyUi
                    font.pixelSize: ThemeService.typography.fontSizeLarge
                    font.weight: Font.Bold
                    color: ThemeService.colors.textPrimary
                }

                Item { Layout.fillWidth: true }

                Button {
                    variant: "ghost"
                    text: "Wipe All"
                    onClicked: clipWindow.clearAll()
                }

                Rectangle {
                    implicitWidth: 26
                    implicitHeight: 26
                    radius: 13
                    color: closeMouse.containsMouse ? ThemeService.colors.surfaceHover : ThemeService.colors.surfaceVariant

                    Text {
                        anchors.centerIn: parent
                        text: "󰅖"
                        font.family: ThemeService.typography.fontFamilyMono
                        font.pixelSize: 11
                        color: ThemeService.colors.textSecondary
                    }

                    MouseArea {
                        id: closeMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: clipWindow.isOpen = false
                    }
                }
            }

            // Search Field
            TextField {
                id: searchInput
                Layout.fillWidth: true
                placeholder: "Search copied text, links, code..."
                leadingIcon: "󰍉"
                onTextChanged: function(t) { clipWindow.searchQuery = t.toLowerCase().trim(); }
            }

            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 1
                color: ThemeService.colors.border
            }

            // Clipboard Items List
            ScrollView {
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true

                ListView {
                    id: clipListView
                    anchors.fill: parent
                    spacing: 6
                    model: clipWindow.clipboardItems

                    delegate: Rectangle {
                        required property var modelData

                        visible: (clipWindow.searchQuery === "" || modelData.preview.toLowerCase().indexOf(clipWindow.searchQuery) !== -1)
                        implicitWidth: clipListView.width
                        implicitHeight: visible ? 50 : 0
                        radius: ThemeService.metrics.radiusSmall
                        color: itemMouse.containsMouse ? ThemeService.colors.surfaceHover : ThemeService.colors.surfaceVariant
                        border.color: modelData.is_pinned ? ThemeService.colors.accent : ThemeService.colors.border
                        border.width: 1

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 10
                            spacing: 10

                            Text {
                                text: modelData.is_image ? "󰋩" : "󰅌"
                                font.family: ThemeService.typography.fontFamilyMono
                                font.pixelSize: 16
                                color: ThemeService.colors.accent
                            }

                            Text {
                                Layout.fillWidth: true
                                text: modelData.preview
                                font.family: ThemeService.typography.fontFamilyMono
                                font.pixelSize: ThemeService.typography.fontSizeSmall
                                color: ThemeService.colors.textPrimary
                                elide: Text.ElideRight
                            }

                            Text {
                                text: modelData.is_pinned ? "󰤱" : "󰤲"
                                font.family: ThemeService.typography.fontFamilyMono
                                font.pixelSize: 14
                                color: modelData.is_pinned ? ThemeService.colors.accent : ThemeService.colors.textMuted
                            }
                        }

                        MouseArea {
                            id: itemMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: clipWindow.copyClip(modelData.id)
                        }
                    }

                    Item {
                        anchors.centerIn: parent
                        visible: clipWindow.clipboardItems.length === 0
                        implicitWidth: 200
                        implicitHeight: 80

                        Text {
                            anchors.centerIn: parent
                            text: "Clipboard history is empty"
                            font.family: ThemeService.typography.fontFamilyUi
                            font.pixelSize: ThemeService.typography.fontSizeSmall
                            color: ThemeService.colors.textMuted
                        }
                    }
                }
            }
        }
    }

    Process {
        id: listProc
        stdout: SplitParser {
            onRead: function(data) {
                try {
                    clipWindow.clipboardItems = JSON.parse(data);
                } catch(e) {}
            }
        }
    }

    Process { id: copyProc }
    Process {
        id: clearProc
        stdout: SplitParser {
            onRead: function(data) {
                clipWindow.refreshHistory();
            }
        }
    }
}
