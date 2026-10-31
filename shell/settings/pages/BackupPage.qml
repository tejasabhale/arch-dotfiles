import QtQuick
import QtQuick.Layouts
import Quickshell
import Quickshell.Io
import "../../services"
import "../../components"

Item {
    id: backupPageRoot
    implicitWidth: 700
    implicitHeight: 550

    property var backups: []
    property string statusMessage: ""
    property bool confirmReset: false

    Component.onCompleted: refreshBackups()

    function refreshBackups() {
        backupsProc.command = ["python3", "-c", "import json; from config.manager import ConfigManager; print(json.dumps(ConfigManager().list_backups()))"];
        backupsProc.running = true;
    }

    function createBackup() {
        actionProc.command = ["python3", "-m", "config.manager", "--backup", "user_snapshot"];
        actionProc.running = true;
        backupPageRoot.statusMessage = "Creating backup snapshot...";
    }

    function restoreBackup(backupId) {
        actionProc.command = ["python3", "-m", "config.manager", "--restore", backupId];
        actionProc.running = true;
        backupPageRoot.statusMessage = "Restoring " + backupId + "...";
    }

    function resetDefaults() {
        actionProc.command = ["python3", "-m", "config.manager", "--reset-defaults"];
        actionProc.running = true;
        backupPageRoot.confirmReset = false;
        backupPageRoot.statusMessage = "Resetting configuration to defaults...";
    }

    Process {
        id: backupsProc
        stdout: SplitParser {
            splitMarker: ""
            onRead: data => {
                try {
                    backupPageRoot.backups = JSON.parse(data);
                } catch (e) {}
            }
        }
    }

    Process {
        id: actionProc
        onExited: (code, status) => {
            backupPageRoot.refreshBackups();
            backupPageRoot.statusMessage = code === 0 ? "Operation completed successfully" : "Operation failed";
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 16

        // Header Row
        RowLayout {
            Layout.fillWidth: true
            spacing: 12

            ColumnLayout {
                spacing: 4
                Text {
                    text: "Backup & Recovery"
                    font.family: ThemeService.typography.fontFamilyUi
                    font.pixelSize: ThemeService.typography.fontSizeLarge + 2
                    font.bold: true
                    color: ThemeService.colors.textPrimary
                }
                Text {
                    text: "Snapshot system preferences and modular feature configurations for safe rollback"
                    font.family: ThemeService.typography.fontFamilyUi
                    font.pixelSize: ThemeService.typography.fontSizeNormal
                    color: ThemeService.colors.textSecondary
                }
            }

            Item { Layout.fillWidth: true }

            Button {
                text: "Create Snapshot"
                icon: "\uf0c7"
                variant: "primary"
                onClicked: backupPageRoot.createBackup()
            }
        }

        // Status Banner
        Rectangle {
            visible: backupPageRoot.statusMessage !== ""
            Layout.fillWidth: true
            height: 36
            radius: ThemeService.metrics.radiusSmall
            color: ThemeService.colors.surfaceVariant
            border.color: ThemeService.colors.accent
            border.width: 1

            RowLayout {
                anchors.fill: parent
                anchors.margins: 8
                spacing: 8
                Text {
                    text: "\uf05a"
                    font.family: ThemeService.typography.fontFamilyMono
                    color: ThemeService.colors.accent
                }
                Text {
                    text: backupPageRoot.statusMessage
                    font.family: ThemeService.typography.fontFamilyUi
                    font.pixelSize: ThemeService.typography.fontSizeSmall
                    color: ThemeService.colors.textPrimary
                }
            }
        }

        // Snapshots List
        Card {
            Layout.fillWidth: true
            Layout.fillHeight: true

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 14
                spacing: 10

                Text {
                    text: "Saved Snapshots (" + backupPageRoot.backups.length + ")"
                    font.family: ThemeService.typography.fontFamilyUi
                    font.pixelSize: ThemeService.typography.fontSizeNormal + 1
                    font.bold: true
                    color: ThemeService.colors.textPrimary
                }

                ListView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true
                    spacing: 8
                    model: backupPageRoot.backups

                    delegate: Rectangle {
                        width: ListView.view.width
                        height: 54
                        radius: ThemeService.metrics.radiusSmall
                        color: ThemeService.colors.surfaceVariant
                        border.color: ThemeService.colors.border
                        border.width: ThemeService.metrics.borderWidth

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 10
                            spacing: 12

                            Text {
                                text: "\uf187"
                                font.family: ThemeService.typography.fontFamilyMono
                                font.pixelSize: ThemeService.typography.fontSizeLarge
                                color: ThemeService.colors.accent
                            }

                            ColumnLayout {
                                spacing: 2
                                Layout.fillWidth: true

                                Text {
                                    text: modelData.id || "snapshot"
                                    font.family: ThemeService.typography.fontFamilyMono
                                    font.pixelSize: ThemeService.typography.fontSizeNormal
                                    font.bold: true
                                    color: ThemeService.colors.textPrimary
                                }

                                Text {
                                    text: (modelData.timestamp || "") + " • " + (modelData.files ? modelData.files.length : 0) + " config files"
                                    font.family: ThemeService.typography.fontFamilyUi
                                    font.pixelSize: ThemeService.typography.fontSizeSmall - 1
                                    color: ThemeService.colors.textSecondary
                                }
                            }

                            Button {
                                text: "Restore"
                                icon: "\uf0e2"
                                variant: "secondary"
                                onClicked: backupPageRoot.restoreBackup(modelData.id)
                            }
                        }
                    }
                }
            }
        }

        // Factory Reset Section
        Card {
            Layout.fillWidth: true
            implicitHeight: 70
            border.color: ThemeService.colors.danger

            RowLayout {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 12

                Text {
                    text: "\uf071"
                    font.family: ThemeService.typography.fontFamilyMono
                    font.pixelSize: ThemeService.typography.fontSizeLarge
                    color: ThemeService.colors.danger
                }

                ColumnLayout {
                    spacing: 2
                    Layout.fillWidth: true

                    Text {
                        text: "Factory Reset"
                        font.family: ThemeService.typography.fontFamilyUi
                        font.bold: true
                        color: ThemeService.colors.danger
                    }
                    Text {
                        text: "Reset all themes, compositor rules, features, and shortcuts to default presets"
                        font.family: ThemeService.typography.fontFamilyUi
                        font.pixelSize: ThemeService.typography.fontSizeSmall
                        color: ThemeService.colors.textSecondary
                    }
                }

                Button {
                    visible: !backupPageRoot.confirmReset
                    text: "Reset Defaults"
                    variant: "danger"
                    onClicked: backupPageRoot.confirmReset = true
                }

                RowLayout {
                    visible: backupPageRoot.confirmReset
                    spacing: 8
                    Button {
                        text: "Confirm Reset"
                        variant: "danger"
                        onClicked: backupPageRoot.resetDefaults()
                    }
                    Button {
                        text: "Cancel"
                        variant: "ghost"
                        onClicked: backupPageRoot.confirmReset = false
                    }
                }
            }
        }
    }
}
