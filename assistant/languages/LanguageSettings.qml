import QtQuick
import QtQuick.Layouts
import Quickshell
import Quickshell.Wayland
import Quickshell.Io
import "../../shell/services"
import "../../shell/components"

PanelWindow {
    id: langWindow

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

    // Configuration state
    property string activeCombination: "auto"
    property string scriptMode: "mirror_input"
    property bool codeSwitching: true

    function toggle() {
        isOpen = !isOpen;
        if (isOpen) {
            refreshConfig();
        }
    }

    function refreshConfig() {
        loadProc.command = ["python3", "-c", "import json; from assistant.languages.router import LanguageRouter; print(json.dumps(LanguageRouter().get_config()))"];
        loadProc.running = true;
    }

    function saveConfig(updates) {
        saveProc.command = [
            "python3", "-c",
            "import sys, json; from assistant.languages.router import LanguageRouter; " +
            "r = LanguageRouter(); r.update_config(json.loads(sys.argv[1])); print('saved')",
            JSON.stringify(updates)
        ];
        saveProc.running = true;
    }

    // Dismiss Backdrop
    Rectangle {
        anchors.fill: parent
        color: "#66000000"

        MouseArea {
            anchors.fill: parent
            onClicked: langWindow.toggle()
        }
    }

    // Modal Card
    Rectangle {
        id: settingsCard
        width: Math.min(560, parent.width - 48)
        height: Math.min(680, parent.height - 80)
        anchors.centerIn: parent

        color: ThemeService.colors.surface
        radius: ThemeService.metrics.radiusLarge
        border.color: ThemeService.colors.borderFocus
        border.width: ThemeService.metrics.borderWidth

        MouseArea {
            anchors.fill: parent
            onClicked: {}
        }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 20
            spacing: 14

            // Header Row
            RowLayout {
                Layout.fillWidth: true
                spacing: 10

                Rectangle {
                    implicitWidth: 36
                    implicitHeight: 36
                    radius: 18
                    color: ThemeService.colors.accent

                    Text {
                        anchors.centerIn: parent
                        text: "󰗊"
                        font.family: ThemeService.typography.fontFamilyMono
                        font.pixelSize: ThemeService.typography.fontSizeLarge
                        color: "#ffffff"
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 2

                    Text {
                        text: "Multilingual Engine Settings"
                        font.family: ThemeService.typography.fontFamilyUi
                        font.pixelSize: ThemeService.typography.fontSizeLarge
                        font.weight: Font.Bold
                        color: ThemeService.colors.textPrimary
                    }

                    Text {
                        text: "Configure English, Hindi, and Marathi Trilingual Interaction"
                        font.family: ThemeService.typography.fontFamilyUi
                        font.pixelSize: ThemeService.typography.fontSizeSmall
                        color: ThemeService.colors.textSecondary
                    }
                }

                Rectangle {
                    implicitWidth: 30
                    implicitHeight: 30
                    radius: ThemeService.metrics.radiusSmall
                    color: closeMouse.containsMouse ? ThemeService.colors.danger : ThemeService.colors.surfaceVariant
                    border.color: ThemeService.colors.border
                    border.width: 1

                    Text {
                        anchors.centerIn: parent
                        text: "󰅖"
                        font.family: ThemeService.typography.fontFamilyMono
                        font.pixelSize: 13
                        color: closeMouse.containsMouse ? "#ffffff" : ThemeService.colors.textPrimary
                    }

                    MouseArea {
                        id: closeMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: langWindow.toggle()
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 1
                color: ThemeService.colors.border
            }

            // Section: 7 Language Combinations
            Text {
                text: "LANGUAGE COMBINATIONS"
                font.family: ThemeService.typography.fontFamilyUi
                font.pixelSize: 11
                font.weight: Font.Bold
                color: ThemeService.colors.accent
            }

            GridLayout {
                Layout.fillWidth: true
                columns: 2
                rowSpacing: 8
                columnSpacing: 8

                Repeater {
                    model: [
                        { "id": "auto", "label": "Auto-Detect", "sub": "Dynamic contextual resolution" },
                        { "id": "en", "label": "English (EN)", "sub": "Primary English reasoning" },
                        { "id": "hi", "label": "हिंदी (Hindi)", "sub": "Pure Devanagari Hindi" },
                        { "id": "mr", "label": "मराठी (Marathi)", "sub": "Pure Devanagari Marathi" },
                        { "id": "en+hi", "label": "English + Hindi", "sub": "Hinglish code-switching" },
                        { "id": "en+mr", "label": "English + Marathi", "sub": "Maranglish code-switching" },
                        { "id": "hi+mr", "label": "हिंदी + मराठी", "sub": "Bilingual Indian context" },
                        { "id": "en+hi+mr", "label": "Trilingual (All 3)", "sub": "Seamless trilingual switching" }
                    ]

                    Rectangle {
                        Layout.fillWidth: true
                        implicitHeight: 52
                        radius: ThemeService.metrics.radiusMedium
                        color: langWindow.activeCombination === modelData.id ? ThemeService.colors.surfaceHover : ThemeService.colors.surfaceVariant
                        border.color: langWindow.activeCombination === modelData.id ? ThemeService.colors.accent : ThemeService.colors.border
                        border.width: langWindow.activeCombination === modelData.id ? 2 : 1

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 10
                            spacing: 10

                            Rectangle {
                                implicitWidth: 10
                                implicitHeight: 10
                                radius: 5
                                color: langWindow.activeCombination === modelData.id ? ThemeService.colors.accent : ThemeService.colors.textMuted
                            }

                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 2

                                Text {
                                    text: modelData.label
                                    font.family: ThemeService.typography.fontFamilyUi
                                    font.pixelSize: 12
                                    font.weight: Font.Bold
                                    color: ThemeService.colors.textPrimary
                                }
                                Text {
                                    text: modelData.sub
                                    font.family: ThemeService.typography.fontFamilyUi
                                    font.pixelSize: 10
                                    color: ThemeService.colors.textSecondary
                                }
                            }
                        }

                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                langWindow.activeCombination = modelData.id;
                                langWindow.saveConfig({ "preferred_combination": modelData.id });
                            }
                        }
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 1
                color: ThemeService.colors.border
            }

            // Section: Script Output Preference
            Text {
                text: "SCRIPT PREFERENCE & PHONETICS"
                font.family: ThemeService.typography.fontFamilyUi
                font.pixelSize: 11
                font.weight: Font.Bold
                color: ThemeService.colors.accent
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 8

                Repeater {
                    model: [
                        { "id": "mirror_input", "label": "Mirror Input Script" },
                        { "id": "native_devanagari", "label": "Devanagari Only" },
                        { "id": "romanized", "label": "Romanized Only" }
                    ]

                    Rectangle {
                        Layout.fillWidth: true
                        implicitHeight: 34
                        radius: ThemeService.metrics.radiusSmall
                        color: langWindow.scriptMode === modelData.id ? ThemeService.colors.accent : ThemeService.colors.surfaceVariant
                        border.color: ThemeService.colors.border
                        border.width: 1

                        Text {
                            anchors.centerIn: parent
                            text: modelData.label
                            font.family: ThemeService.typography.fontFamilyUi
                            font.pixelSize: 11
                            font.weight: Font.Bold
                            color: langWindow.scriptMode === modelData.id ? "#ffffff" : ThemeService.colors.textPrimary
                        }

                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                langWindow.scriptMode = modelData.id;
                                langWindow.saveConfig({ "script_mode": modelData.id });
                            }
                        }
                    }
                }
            }

            // Code-Switching Toggle Card
            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 50
                radius: ThemeService.metrics.radiusMedium
                color: ThemeService.colors.surfaceVariant
                border.color: ThemeService.colors.border
                border.width: 1

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 12
                    spacing: 12

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2

                        Text {
                            text: "Mid-Sentence Code-Switching"
                            font.family: ThemeService.typography.fontFamilyUi
                            font.pixelSize: 12
                            font.weight: Font.Bold
                            color: ThemeService.colors.textPrimary
                        }
                        Text {
                            text: "Allow mixing English technical terms with Hindi and Marathi seamlessly"
                            font.family: ThemeService.typography.fontFamilyUi
                            font.pixelSize: 10
                            color: ThemeService.colors.textSecondary
                        }
                    }

                    Switch {
                        checked: langWindow.codeSwitching
                        onToggled: {
                            langWindow.codeSwitching = checked;
                            langWindow.saveConfig({ "code_switching_enabled": checked });
                        }
                    }
                }
            }
        }
    }

    Item {
        focus: true
        Keys.onEscapePressed: langWindow.toggle()
    }

    Process {
        id: loadProc
        stdout: StdioCollector {
            onCollected: function(text) {
                try {
                    var data = JSON.parse(text);
                    if (data.preferred_combination) langWindow.activeCombination = data.preferred_combination;
                    if (data.script_mode) langWindow.scriptMode = data.script_mode;
                    if (data.code_switching_enabled !== undefined) langWindow.codeSwitching = data.code_switching_enabled;
                } catch(e) {}
            }
        }
    }

    Process {
        id: saveProc
    }
}
