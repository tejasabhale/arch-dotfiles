import QtQuick
import QtQuick.Layouts
import Quickshell
import Quickshell.Io
import "../services"
import "../components"

Item {
    id: featManagerRoot
    implicitWidth: 700
    implicitHeight: 550

    property var features: ({})
    property var featureKeys: []
    property string statusMessage: ""
    property bool isError: false

    Component.onCompleted: refreshFeatures()

    function refreshFeatures() {
        featuresProc.command = ["python3", "-m", "config.manager", "--list-features", "--json"];
        featuresProc.running = true;
    }

    function toggleFeature(featKey, newState) {
        var arg = newState ? "--enable" : "--disable";
        toggleProc.command = ["python3", "-m", "config.manager", arg, featKey];
        toggleProc.running = true;
        featManagerRoot.statusMessage = (newState ? "Enabling " : "Disabling ") + featKey + "...";
    }

    Process {
        id: featuresProc
        stdout: SplitParser {
            splitMarker: ""
            onRead: data => {
                try {
                    var parsed = JSON.parse(data);
                    featManagerRoot.features = parsed;
                    featManagerRoot.featureKeys = Object.keys(parsed);
                } catch (e) {}
            }
        }
    }

    Process {
        id: toggleProc
        stdout: SplitParser {
            splitMarker: ""
            onRead: data => {
                featManagerRoot.statusMessage = data.trim();
                featManagerRoot.isError = data.indexOf("[FAIL]") !== -1;
            }
        }
        onExited: (code, status) => {
            featManagerRoot.refreshFeatures();
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 16

        // Header
        ColumnLayout {
            spacing: 4
            Text {
                text: "Modular Feature Isolation"
                font.family: ThemeService.typography.fontFamilyUi
                font.pixelSize: ThemeService.typography.fontSizeLarge + 2
                font.bold: true
                color: ThemeService.colors.textPrimary
            }
            Text {
                text: "Every desktop module operates independently. Disabling terminates background daemons (Rule 1.4)."
                font.family: ThemeService.typography.fontFamilyUi
                font.pixelSize: ThemeService.typography.fontSizeNormal
                color: ThemeService.colors.textSecondary
            }
        }

        // Status Toast
        Rectangle {
            visible: featManagerRoot.statusMessage !== ""
            Layout.fillWidth: true
            height: 36
            radius: ThemeService.metrics.radiusSmall
            color: featManagerRoot.isError ? ThemeService.colors.danger : ThemeService.colors.surfaceVariant
            border.color: featManagerRoot.isError ? ThemeService.colors.danger : ThemeService.colors.accent
            border.width: 1

            RowLayout {
                anchors.fill: parent
                anchors.margins: 8
                spacing: 8
                Text {
                    text: featManagerRoot.isError ? "\uf071" : "\uf05a"
                    font.family: ThemeService.typography.fontFamilyMono
                    color: "#ffffff"
                }
                Text {
                    text: featManagerRoot.statusMessage
                    font.family: ThemeService.typography.fontFamilyUi
                    font.pixelSize: ThemeService.typography.fontSizeSmall
                    color: "#ffffff"
                    Layout.fillWidth: true
                    elide: Text.ElideRight
                }
            }
        }

        // Features List
        ListView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            spacing: 8
            model: featManagerRoot.featureKeys

            delegate: Card {
                width: ListView.view.width
                implicitHeight: 74

                property var featData: featManagerRoot.features[modelData] || ({})

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 12
                    spacing: 14

                    Rectangle {
                        implicitWidth: 36
                        implicitHeight: 36
                        radius: ThemeService.metrics.radiusSmall
                        color: featData.enabled ? ThemeService.colors.accent : ThemeService.colors.surfaceVariant

                        Text {
                            anchors.centerIn: parent
                            text: featData.enabled ? "\uf00c" : "\uf00d"
                            font.family: ThemeService.typography.fontFamilyMono
                            font.pixelSize: ThemeService.typography.fontSizeNormal
                            color: featData.enabled ? "#ffffff" : ThemeService.colors.textSecondary
                        }
                    }

                    ColumnLayout {
                        spacing: 2
                        Layout.fillWidth: true

                        RowLayout {
                            spacing: 8
                            Text {
                                text: featData.name || modelData
                                font.family: ThemeService.typography.fontFamilyUi
                                font.pixelSize: ThemeService.typography.fontSizeNormal
                                font.bold: true
                                color: ThemeService.colors.textPrimary
                            }

                            // Dependencies Pill
                            Rectangle {
                                visible: featData.dependencies && featData.dependencies.length > 0
                                implicitWidth: depText.implicitWidth + 8
                                implicitHeight: 18
                                radius: 4
                                color: ThemeService.colors.surface
                                border.color: ThemeService.colors.border

                                Text {
                                    id: depText
                                    anchors.centerIn: parent
                                    text: "Requires: " + (featData.dependencies ? featData.dependencies.join(", ") : "")
                                    font.pixelSize: 10
                                    color: ThemeService.colors.textSecondary
                                }
                            }
                        }

                        Text {
                            text: featData.description || ""
                            font.family: ThemeService.typography.fontFamilyUi
                            font.pixelSize: ThemeService.typography.fontSizeSmall
                            color: ThemeService.colors.textSecondary
                            elide: Text.ElideRight
                            Layout.fillWidth: true
                        }
                    }

                    Switch {
                        checked: !!featData.enabled
                        onToggled: state => {
                            featManagerRoot.toggleFeature(modelData, state);
                        }
                    }
                }
            }
        }
    }
}
