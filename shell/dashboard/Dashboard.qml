import QtQuick
import QtQuick.Layouts
import Quickshell
import Quickshell.Wayland
import Quickshell.Io
import "../services"
import "../components"

PanelWindow {
    id: dashWindow

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

    // Time & Date State
    property string clockTime: "12:00"
    property string clockDate: "Monday, January 1"

    // System Vitals State
    property int cpuPercent: 12
    property int ramPercent: 24
    property int diskPercent: 42

    // Pomodoro Timer State
    property int pomoSecondsLeft: 25 * 60
    property bool pomoRunning: false
    property string pomoMode: "Focus" // "Focus" or "Break"

    // Notes and Tasks Data
    property var notesList: []
    property var tasksList: []

    function toggle() {
        isOpen = !isOpen;
        if (isOpen) {
            updateTime();
            refreshVitals();
            refreshNotes();
        }
    }

    function updateTime() {
        var d = new Date();
        var h = String(d.getHours()).padStart(2, '0');
        var m = String(d.getMinutes()).padStart(2, '0');
        clockTime = h + ":" + m;

        var days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
        var months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
        clockDate = days[d.getDay()] + ", " + months[d.getMonth()] + " " + d.getDate();
    }

    function refreshVitals() {
        vitalsProc.command = ["sh", "-c", "free -m | awk '/Mem:/ { printf(\"%d\", ($3/$2)*100) }'"];
        vitalsProc.running = true;
    }

    function refreshNotes() {
        notesProc.command = ["python3", "-m", "productivity.notes.notes_manager", "get"];
        notesProc.running = true;
    }

    function toggleTask(taskId) {
        taskToggleProc.command = ["python3", "-m", "productivity.notes.notes_manager", "toggle-task", taskId];
        taskToggleProc.running = true;
    }

    // Pomodoro Timer Interval
    Timer {
        interval: 1000
        running: dashWindow.pomoRunning
        repeat: true
        onTriggered: {
            if (dashWindow.pomoSecondsLeft > 0) {
                dashWindow.pomoSecondsLeft--;
            } else {
                dashWindow.pomoRunning = false;
                dashWindow.pomoMode = (dashWindow.pomoMode === "Focus") ? "Break" : "Focus";
                dashWindow.pomoSecondsLeft = (dashWindow.pomoMode === "Focus") ? (25 * 60) : (5 * 60);
            }
        }
    }

    MouseArea {
        anchors.fill: parent
        onClicked: dashWindow.isOpen = false
        Rectangle {
            anchors.fill: parent
            color: "#00000077"
        }
    }

    // Centered Master Dashboard Card
    Rectangle {
        id: modalContent
        anchors.centerIn: parent
        implicitWidth: 840
        implicitHeight: 560
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
            anchors.margins: 22
            spacing: 16

            // 1. Header: Big Clock, Date, and Close Button
            RowLayout {
                Layout.fillWidth: true

                ColumnLayout {
                    spacing: 2
                    Text {
                        text: dashWindow.clockTime
                        font.family: ThemeService.typography.fontFamilyMono
                        font.pixelSize: 42
                        font.weight: Font.Bold
                        color: ThemeService.colors.accent
                    }
                    Text {
                        text: dashWindow.clockDate
                        font.family: ThemeService.typography.fontFamilyUi
                        font.pixelSize: ThemeService.typography.fontSizeNormal
                        color: ThemeService.colors.textSecondary
                    }
                }

                Item { Layout.fillWidth: true }

                Rectangle {
                    implicitWidth: 32
                    implicitHeight: 32
                    radius: 16
                    color: closeMouse.containsMouse ? ThemeService.colors.surfaceHover : ThemeService.colors.surfaceVariant

                    Text {
                        anchors.centerIn: parent
                        text: "󰅖"
                        font.family: ThemeService.typography.fontFamilyMono
                        font.pixelSize: 14
                        color: ThemeService.colors.textSecondary
                    }

                    MouseArea {
                        id: closeMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: dashWindow.isOpen = false
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 1
                color: ThemeService.colors.border
            }

            // 2. 3-Column Layout: (System Vitals) | (Pomodoro & Notes) | (Tasks List)
            RowLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: 16

                // Column 1: Hardware Vitals (RAM, CPU, Disk)
                Card {
                    Layout.fillHeight: true
                    Layout.preferredWidth: 240

                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 12

                        Text {
                            text: "󰍹 System Vitals"
                            font.family: ThemeService.typography.fontFamilyUi
                            font.pixelSize: ThemeService.typography.fontSizeNormal
                            font.weight: Font.Bold
                            color: ThemeService.colors.textPrimary
                        }

                        // RAM Gauge
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 4
                            RowLayout {
                                Layout.fillWidth: true
                                Text { text: "RAM (8 GB)"; font.pixelSize: 11; color: ThemeService.colors.textMuted }
                                Item { Layout.fillWidth: true }
                                Text { text: dashWindow.ramPercent + "%"; font.pixelSize: 11; font.weight: Font.Bold; color: ThemeService.colors.textPrimary }
                            }
                            Rectangle {
                                Layout.fillWidth: true; implicitHeight: 6; radius: 3; color: ThemeService.colors.surfaceVariant
                                Rectangle { width: parent.width * (dashWindow.ramPercent / 100); height: parent.height; radius: parent.radius; color: ThemeService.colors.accent }
                            }
                        }

                        // CPU Gauge
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 4
                            RowLayout {
                                Layout.fillWidth: true
                                Text { text: "CPU Load"; font.pixelSize: 11; color: ThemeService.colors.textMuted }
                                Item { Layout.fillWidth: true }
                                Text { text: dashWindow.cpuPercent + "%"; font.pixelSize: 11; font.weight: Font.Bold; color: ThemeService.colors.textPrimary }
                            }
                            Rectangle {
                                Layout.fillWidth: true; implicitHeight: 6; radius: 3; color: ThemeService.colors.surfaceVariant
                                Rectangle { width: parent.width * (dashWindow.cpuPercent / 100); height: parent.height; radius: parent.radius; color: ThemeService.colors.success }
                            }
                        }

                        // Disk Free Gauge
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 4
                            RowLayout {
                                Layout.fillWidth: true
                                Text { text: "NVMe Root (/)"; font.pixelSize: 11; color: ThemeService.colors.textMuted }
                                Item { Layout.fillWidth: true }
                                Text { text: dashWindow.diskPercent + "%"; font.pixelSize: 11; font.weight: Font.Bold; color: ThemeService.colors.textPrimary }
                            }
                            Rectangle {
                                Layout.fillWidth: true; implicitHeight: 6; radius: 3; color: ThemeService.colors.surfaceVariant
                                Rectangle { width: parent.width * (dashWindow.diskPercent / 100); height: parent.height; radius: parent.radius; color: ThemeService.colors.warning }
                            }
                        }

                        Item { Layout.fillHeight: true }

                        Text {
                            text: "HP EliteBook 840 G5\nIdle Footprint: ~1.4 GB"
                            font.family: ThemeService.typography.fontFamilyUi
                            font.pixelSize: 10
                            color: ThemeService.colors.textMuted
                        }
                    }
                }

                // Column 2: Pomodoro Focus Timer & Scratchpad
                Card {
                    Layout.fillHeight: true
                    Layout.preferredWidth: 260

                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 12

                        // Pomodoro Header
                        RowLayout {
                            Layout.fillWidth: true
                            Text {
                                text: "󱫌 Pomodoro"
                                font.family: ThemeService.typography.fontFamilyUi
                                font.pixelSize: ThemeService.typography.fontSizeNormal
                                font.weight: Font.Bold
                                color: ThemeService.colors.textPrimary
                            }
                            Item { Layout.fillWidth: true }
                            Pill {
                                text: dashWindow.pomoMode
                                active: dashWindow.pomoMode === "Focus"
                            }
                        }

                        // Big Timer Clock readout
                        Text {
                            Layout.alignment: Qt.AlignHCenter
                            text: {
                                var m = Math.floor(dashWindow.pomoSecondsLeft / 60);
                                var s = dashWindow.pomoSecondsLeft % 60;
                                return String(m).padStart(2, '0') + ":" + String(s).padStart(2, '0');
                            }
                            font.family: ThemeService.typography.fontFamilyMono
                            font.pixelSize: 34
                            font.weight: Font.Bold
                            color: ThemeService.colors.textPrimary
                        }

                        // Timer Controls
                        RowLayout {
                            Layout.alignment: Qt.AlignHCenter
                            spacing: 8

                            Button {
                                variant: dashWindow.pomoRunning ? "secondary" : "primary"
                                text: dashWindow.pomoRunning ? "Pause" : "Start"
                                onClicked: dashWindow.pomoRunning = !dashWindow.pomoRunning
                            }

                            Button {
                                variant: "ghost"
                                text: "Reset"
                                onClicked: {
                                    dashWindow.pomoRunning = false;
                                    dashWindow.pomoSecondsLeft = 25 * 60;
                                    dashWindow.pomoMode = "Focus";
                                }
                            }
                        }

                        Rectangle { Layout.fillWidth: true; implicitHeight: 1; color: ThemeService.colors.border }

                        Text {
                            text: "󰠮 Quick Scratchpad"
                            font.family: ThemeService.typography.fontFamilyUi
                            font.pixelSize: ThemeService.typography.fontSizeSmall
                            font.weight: Font.Bold
                            color: ThemeService.colors.textPrimary
                        }

                        // Scratchpad text input
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            radius: ThemeService.metrics.radiusSmall
                            color: ThemeService.colors.surfaceVariant
                            border.color: ThemeService.colors.border
                            border.width: 1

                            TextEdit {
                                anchors.fill: parent
                                anchors.margins: 8
                                text: "Draft ideas, meeting notes, code snippets here..."
                                font.family: ThemeService.typography.fontFamilyUi
                                font.pixelSize: ThemeService.typography.fontSizeSmall
                                color: ThemeService.colors.textSecondary
                                wrapMode: TextEdit.Wrap
                            }
                        }
                    }
                }

                // Column 3: Task To-Do List
                Card {
                    Layout.fillHeight: true
                    Layout.fillWidth: true

                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 10

                        RowLayout {
                            Layout.fillWidth: true
                            Text {
                                text: "󰄲 Task List"
                                font.family: ThemeService.typography.fontFamilyUi
                                font.pixelSize: ThemeService.typography.fontSizeNormal
                                font.weight: Font.Bold
                                color: ThemeService.colors.textPrimary
                            }
                            Item { Layout.fillWidth: true }
                            Text {
                                text: dashWindow.tasksList.length + " tasks"
                                font.pixelSize: 11
                                color: ThemeService.colors.textMuted
                            }
                        }

                        ScrollView {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            clip: true

                            ListView {
                                anchors.fill: parent
                                spacing: 6
                                model: dashWindow.tasksList

                                delegate: Rectangle {
                                    required property var modelData

                                    implicitWidth: parent.width
                                    implicitHeight: 38
                                    radius: ThemeService.metrics.radiusSmall
                                    color: ThemeService.colors.surfaceVariant
                                    border.color: ThemeService.colors.border
                                    border.width: 1

                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.margins: 8
                                        spacing: 8

                                        // Checkbox Icon
                                        Text {
                                            text: modelData.completed ? "󰄲" : "󰄱"
                                            font.family: ThemeService.typography.fontFamilyMono
                                            font.pixelSize: 16
                                            color: modelData.completed ? ThemeService.colors.success : ThemeService.colors.textMuted
                                        }

                                        Text {
                                            Layout.fillWidth: true
                                            text: modelData.text
                                            font.family: ThemeService.typography.fontFamilyUi
                                            font.pixelSize: ThemeService.typography.fontSizeSmall
                                            color: modelData.completed ? ThemeService.colors.textMuted : ThemeService.colors.textPrimary
                                            elide: Text.ElideRight
                                        }
                                    }

                                    MouseArea {
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: dashWindow.toggleTask(modelData.id)
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    Process {
        id: vitalsProc
        stdout: SplitParser {
            onRead: function(data) {
                var p = parseInt(data.trim());
                if (!isNaN(p)) dashWindow.ramPercent = p;
            }
        }
    }

    Process {
        id: notesProc
        stdout: SplitParser {
            onRead: function(data) {
                try {
                    var parsed = JSON.parse(data);
                    dashWindow.notesList = parsed.notes || [];
                    dashWindow.tasksList = parsed.tasks || [];
                } catch(e) {}
            }
        }
    }

    Process {
        id: taskToggleProc
        stdout: SplitParser {
            onRead: function(data) {
                dashWindow.refreshNotes();
            }
        }
    }

    Keys.onEscapePressed: dashWindow.isOpen = false
}
