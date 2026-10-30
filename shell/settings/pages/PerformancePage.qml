import QtQuick
import QtQuick.Layouts
import Quickshell
import Quickshell.Io
import "../../services"
import "../../components"

Item {
    id: perfPageRoot
    implicitWidth: 700
    implicitHeight: 550

    property string activeProfile: "balanced"
    property var profiles: ({})

    Component.onCompleted: refreshProfiles()

    function refreshProfiles() {
        profilesProc.command = ["python3", "-m", "config.manager", "--profile", "list", "--json"];
        profilesProc.running = true;
    }

    function switchProfile(profileKey) {
        setProfileProc.command = ["python3", "-m", "config.manager", "--profile", profileKey];
        setProfileProc.running = true;
        perfPageRoot.activeProfile = profileKey;
    }

    Process {
        id: profilesProc
        command: ["python3", "-c", "import json; from config.manager import ConfigManager; mgr = ConfigManager(); print(json.dumps({'active': mgr.get_active_profile(), 'profiles': mgr.get_profiles()}))"]
        running: true
        stdout: SplitParser {
            splitMarker: ""
            onRead: data => {
                try {
                    var parsed = JSON.parse(data);
                    perfPageRoot.activeProfile = parsed.active;
                    perfPageRoot.profiles = parsed.profiles;
                } catch (e) {}
            }
        }
    }

    Process {
        id: setProfileProc
        onExited: (code, status) => {
            profilesProc.running = true;
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 16

        // Header
        ColumnLayout {
            spacing: 4
            Text {
                text: "Performance Profiles"
                font.family: ThemeService.typography.fontFamilyUi
                font.pixelSize: ThemeService.typography.fontSizeLarge + 2
                font.bold: true
                color: ThemeService.colors.textPrimary
            }
            Text {
                text: "Tune CPU governor, compositor blur, animations, and power consumption for 8GB RAM budget"
                font.family: ThemeService.typography.fontFamilyUi
                font.pixelSize: ThemeService.typography.fontSizeNormal
                color: ThemeService.colors.textSecondary
            }
        }

        // Profile Cards Grid
        GridLayout {
            Layout.fillWidth: true
            columns: 2
            rowSpacing: 14
            columnSpacing: 14

            // 1. Balanced
            Card {
                Layout.fillWidth: true
                implicitHeight: 140
                border.color: perfPageRoot.activeProfile === "balanced" ? ThemeService.colors.accent : ThemeService.colors.border
                border.width: perfPageRoot.activeProfile === "balanced" ? 2 : 1

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: perfPageRoot.switchProfile("balanced")
                }

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 14
                    spacing: 6

                    RowLayout {
                        spacing: 8
                        Text {
                            text: "\uf24e"
                            font.family: ThemeService.typography.fontFamilyMono
                            font.pixelSize: ThemeService.typography.fontSizeLarge
                            color: ThemeService.colors.accent
                        }
                        Text {
                            text: "Balanced (Default)"
                            font.family: ThemeService.typography.fontFamilyUi
                            font.pixelSize: ThemeService.typography.fontSizeNormal + 1
                            font.bold: true
                            color: ThemeService.colors.textPrimary
                        }
                        Item { Layout.fillWidth: true }
                        Pill {
                            text: "Active"
                            visible: perfPageRoot.activeProfile === "balanced"
                            active: true
                        }
                    }

                    Text {
                        text: "Powersave CPU governor, full animations, compositor blur enabled. Target: <= 1.8GB idle memory."
                        font.family: ThemeService.typography.fontFamilyUi
                        font.pixelSize: ThemeService.typography.fontSizeSmall
                        color: ThemeService.colors.textSecondary
                        wrapMode: Text.WordWrap
                        Layout.fillWidth: true
                    }
                }
            }

            // 2. Performance
            Card {
                Layout.fillWidth: true
                implicitHeight: 140
                border.color: perfPageRoot.activeProfile === "performance" ? ThemeService.colors.accent : ThemeService.colors.border
                border.width: perfPageRoot.activeProfile === "performance" ? 2 : 1

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: perfPageRoot.switchProfile("performance")
                }

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 14
                    spacing: 6

                    RowLayout {
                        spacing: 8
                        Text {
                            text: "\uf0e7"
                            font.family: ThemeService.typography.fontFamilyMono
                            font.pixelSize: ThemeService.typography.fontSizeLarge
                            color: ThemeService.colors.warning || ThemeService.colors.accent
                        }
                        Text {
                            text: "High Performance"
                            font.family: ThemeService.typography.fontFamilyUi
                            font.pixelSize: ThemeService.typography.fontSizeNormal + 1
                            font.bold: true
                            color: ThemeService.colors.textPrimary
                        }
                        Item { Layout.fillWidth: true }
                        Pill {
                            text: "Active"
                            visible: perfPageRoot.activeProfile === "performance"
                            active: true
                        }
                    }

                    Text {
                        text: "Performance CPU governor, Intel UHD boosted, fast 0.5x animations. Ideal for build compilation."
                        font.family: ThemeService.typography.fontFamilyUi
                        font.pixelSize: ThemeService.typography.fontSizeSmall
                        color: ThemeService.colors.textSecondary
                        wrapMode: Text.WordWrap
                        Layout.fillWidth: true
                    }
                }
            }

            // 3. Battery Saver
            Card {
                Layout.fillWidth: true
                implicitHeight: 140
                border.color: perfPageRoot.activeProfile === "battery_saver" ? ThemeService.colors.accent : ThemeService.colors.border
                border.width: perfPageRoot.activeProfile === "battery_saver" ? 2 : 1

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: perfPageRoot.switchProfile("battery_saver")
                }

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 14
                    spacing: 6

                    RowLayout {
                        spacing: 8
                        Text {
                            text: "\uf244"
                            font.family: ThemeService.typography.fontFamilyMono
                            font.pixelSize: ThemeService.typography.fontSizeLarge
                            color: ThemeService.colors.success || ThemeService.colors.accent
                        }
                        Text {
                            text: "Battery Saver"
                            font.family: ThemeService.typography.fontFamilyUi
                            font.pixelSize: ThemeService.typography.fontSizeNormal + 1
                            font.bold: true
                            color: ThemeService.colors.textPrimary
                        }
                        Item { Layout.fillWidth: true }
                        Pill {
                            text: "Active"
                            visible: perfPageRoot.activeProfile === "battery_saver"
                            active: true
                        }
                    }

                    Text {
                        text: "Throttled CPU, compositor blur disabled, animations off, screen idle timeout 2 min. Max endurance."
                        font.family: ThemeService.typography.fontFamilyUi
                        font.pixelSize: ThemeService.typography.fontSizeSmall
                        color: ThemeService.colors.textSecondary
                        wrapMode: Text.WordWrap
                        Layout.fillWidth: true
                    }
                }
            }

            // 4. Full Experience
            Card {
                Layout.fillWidth: true
                implicitHeight: 140
                border.color: perfPageRoot.activeProfile === "full_experience" ? ThemeService.colors.accent : ThemeService.colors.border
                border.width: perfPageRoot.activeProfile === "full_experience" ? 2 : 1

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: perfPageRoot.switchProfile("full_experience")
                }

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 14
                    spacing: 6

                    RowLayout {
                        spacing: 8
                        Text {
                            text: "\uf005"
                            font.family: ThemeService.typography.fontFamilyMono
                            font.pixelSize: ThemeService.typography.fontSizeLarge
                            color: ThemeService.colors.accent
                        }
                        Text {
                            text: "Full Experience"
                            font.family: ThemeService.typography.fontFamilyUi
                            font.pixelSize: ThemeService.typography.fontSizeNormal + 1
                            font.bold: true
                            color: ThemeService.colors.textPrimary
                        }
                        Item { Layout.fillWidth: true }
                        Pill {
                            text: "Active"
                            visible: perfPageRoot.activeProfile === "full_experience"
                            active: true
                        }
                    }

                    Text {
                        text: "Maximum visual fidelity, deep acrylic blur, rich particle animations, and live telemetry vitals."
                        font.family: ThemeService.typography.fontFamilyUi
                        font.pixelSize: ThemeService.typography.fontSizeSmall
                        color: ThemeService.colors.textSecondary
                        wrapMode: Text.WordWrap
                        Layout.fillWidth: true
                    }
                }
            }
        }

        Item { Layout.fillHeight: true }
    }
}
