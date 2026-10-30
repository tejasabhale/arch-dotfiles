import QtQuick
import QtQuick.Layouts
import Quickshell
import Quickshell.Wayland
import Quickshell.Io
import "../../shell/services"
import "../../shell/components"

PanelWindow {
    id: assistantWindow

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

    // Assistant State
    property string assistantName: "June"
    property string assistantAvatar: "󱚣"
    property string activeProvider: "Mock"
    property string activeModel: "mock-smart"
    property bool isGenerating: false
    property bool isListening: false
    property var pendingPlan: null
    property var messagesList: []

    function toggle() {
        isOpen = !isOpen;
        if (isOpen) {
            pingService();
            loadHistory();
            chatInput.forceActiveFocus();
        }
    }

    function diagnoseScreen() {
        if (isGenerating) return;
        isGenerating = true;
        screenProc.command = ["python3", "-m", "assistant.core.cli", "--screen", "--json"];
        screenProc.running = true;
    }

    function toggleVoice() {
        isListening = !isListening;
    }

    function approvePlan() {
        if (!pendingPlan) return;
        var p = pendingPlan;
        pendingPlan = null;
        sendMessage("Confirmed: execute plan " + p.goal);
    }

    function cancelPlan() {
        pendingPlan = null;
    }

    function pingService() {
        pingProc.command = ["python3", "-m", "assistant.core.cli", "--ping", "--json"];
        pingProc.running = true;
    }

    function loadHistory() {
        historyProc.command = ["python3", "-m", "assistant.core.cli", "--history", "--json"];
        historyProc.running = true;
    }

    function sendMessage(text) {
        var query = text.trim();
        if (query === "" || isGenerating) return;

        // Optimistically add user message to list
        var updated = messagesList.slice();
        updated.push({
            "role": "user",
            "content": query,
            "timestamp": new Date().toLocaleTimeString()
        });
        messagesList = updated;

        chatInput.text = "";
        isGenerating = true;

        chatProc.command = ["python3", "-m", "assistant.core.cli", "--chat", query, "--json"];
        chatProc.running = true;

        msgView.positionViewAtEnd();
    }

    function clearChat() {
        clearProc.command = ["python3", "-m", "assistant.core.cli", "--clear", "--json"];
        clearProc.running = true;
    }

    function emergencyStop() {
        stopProc.command = ["python3", "-m", "assistant.core.cli", "--stop", "--json"];
        stopProc.running = true;
        isGenerating = false;
    }

    // Dismiss Backdrop
    Rectangle {
        anchors.fill: parent
        color: "#66000000"

        MouseArea {
            anchors.fill: parent
            onClicked: assistantWindow.toggle()
        }
    }

    // Main Floating Chat Container
    Rectangle {
        id: mainCard
        width: Math.min(620, parent.width - 48)
        height: Math.min(740, parent.height - 80)
        anchors.centerIn: parent

        color: ThemeService.colors.surface
        radius: ThemeService.metrics.radiusLarge
        border.color: ThemeService.colors.borderFocus
        border.width: ThemeService.metrics.borderWidth

        // Block clicks from hitting backdrop
        MouseArea {
            anchors.fill: parent
            onClicked: {}
        }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 16
            spacing: 12

            // Header Bar
            RowLayout {
                Layout.fillWidth: true
                spacing: 12

                // Avatar Icon
                Rectangle {
                    implicitWidth: 38
                    implicitHeight: 38
                    radius: 19
                    color: ThemeService.colors.accent

                    Text {
                        anchors.centerIn: parent
                        text: assistantWindow.assistantAvatar
                        font.family: ThemeService.typography.fontFamilyMono
                        font.pixelSize: ThemeService.typography.fontSizeLarge
                        color: "#ffffff"
                    }
                }

                // Title & Provider Subtitle
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 2

                    Text {
                        text: assistantWindow.assistantName
                        font.family: ThemeService.typography.fontFamilyUi
                        font.pixelSize: ThemeService.typography.fontSizeLarge
                        font.weight: Font.Bold
                        color: ThemeService.colors.textPrimary
                    }

                    RowLayout {
                        spacing: 6

                        Rectangle {
                            implicitWidth: 7
                            implicitHeight: 7
                            radius: 3.5
                            color: assistantWindow.isGenerating ? ThemeService.colors.warning : ThemeService.colors.success
                        }

                        Text {
                            text: (assistantWindow.isGenerating ? "Reasoning with " : "Active: ") + assistantWindow.activeProvider + " (" + assistantWindow.activeModel + ")"
                            font.family: ThemeService.typography.fontFamilyUi
                            font.pixelSize: ThemeService.typography.fontSizeSmall
                            color: ThemeService.colors.textSecondary
                        }
                    }
                }

                // Emergency Stop Button
                Rectangle {
                    implicitWidth: 78
                    implicitHeight: 30
                    radius: ThemeService.metrics.radiusSmall
                    color: stopMouse.containsMouse ? ThemeService.colors.danger : ThemeService.colors.surfaceVariant
                    border.color: assistantWindow.isGenerating ? ThemeService.colors.danger : ThemeService.colors.border
                    border.width: 1

                    RowLayout {
                        anchors.centerIn: parent
                        spacing: 4

                        Text {
                            text: "󰓛"
                            font.family: ThemeService.typography.fontFamilyMono
                            font.pixelSize: 11
                            color: stopMouse.containsMouse || assistantWindow.isGenerating ? "#ffffff" : ThemeService.colors.danger
                        }
                        Text {
                            text: "Stop"
                            font.family: ThemeService.typography.fontFamilyUi
                            font.pixelSize: 11
                            font.weight: Font.Bold
                            color: stopMouse.containsMouse || assistantWindow.isGenerating ? "#ffffff" : ThemeService.colors.textPrimary
                        }
                    }

                    MouseArea {
                        id: stopMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: assistantWindow.emergencyStop()
                    }
                }

                // Clear Chat History Button
                Rectangle {
                    implicitWidth: 30
                    implicitHeight: 30
                    radius: ThemeService.metrics.radiusSmall
                    color: clearMouse.containsMouse ? ThemeService.colors.surfaceHover : ThemeService.colors.surfaceVariant
                    border.color: ThemeService.colors.border
                    border.width: 1

                    Text {
                        anchors.centerIn: parent
                        text: "󰃢"
                        font.family: ThemeService.typography.fontFamilyMono
                        font.pixelSize: 14
                        color: clearMouse.containsMouse ? ThemeService.colors.accent : ThemeService.colors.textSecondary
                    }

                    MouseArea {
                        id: clearMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: assistantWindow.clearChat()
                    }
                }

                // Close Button
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
                        font.pixelSize: 14
                        color: closeMouse.containsMouse ? "#ffffff" : ThemeService.colors.textPrimary
                    }

                    MouseArea {
                        id: closeMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: assistantWindow.toggle()
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 1
                color: ThemeService.colors.border
            }

            // Quick Prompt Chips
            RowLayout {
                Layout.fillWidth: true
                spacing: 8

                Repeater {
                    model: [
                        { "label": "󰌌 Shortcuts", "query": "What are the primary Hyprland shortcuts?" },
                        { "label": "󱘖 System Vitals", "query": "Explain system memory and CPU budget" },
                        { "label": "󰖩 Hotspot", "query": "How do I configure the Wi-Fi hotspot?" },
                        { "label": "󰁹 Battery", "query": "What power profiles are active?" },
                        { "label": "󰔎 Themes", "query": "What theme presets are available?" }
                    ]

                    Rectangle {
                        implicitHeight: 26
                        implicitWidth: chipLabel.implicitWidth + 14
                        radius: 13
                        color: chipMouse.containsMouse ? ThemeService.colors.accentHover : ThemeService.colors.surfaceVariant
                        border.color: ThemeService.colors.border
                        border.width: 1

                        Text {
                            id: chipLabel
                            anchors.centerIn: parent
                            text: modelData.label
                            font.family: ThemeService.typography.fontFamilyUi
                            font.pixelSize: 11
                            color: chipMouse.containsMouse ? "#ffffff" : ThemeService.colors.textSecondary
                        }

                        MouseArea {
                            id: chipMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: assistantWindow.sendMessage(modelData.query)
                        }
                    }
                }
            }

            // Chat Messages View
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: ThemeService.colors.background
                radius: ThemeService.metrics.radiusMedium
                border.color: ThemeService.colors.border
                border.width: 1
                clip: true

                ListView {
                    id: msgView
                    anchors.fill: parent
                    anchors.margins: 12
                    spacing: 12
                    model: assistantWindow.messagesList

                    delegate: ColumnLayout {
                        width: msgView.width
                        spacing: 4

                        // Speaker and Timestamp Header
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 6
                            layoutDirection: modelData.role === "user" ? Qt.RightToLeft : Qt.LeftToRight

                            Text {
                                text: modelData.role === "user" ? "You" : assistantWindow.assistantName
                                font.family: ThemeService.typography.fontFamilyUi
                                font.pixelSize: 11
                                font.weight: Font.Bold
                                color: modelData.role === "user" ? ThemeService.colors.accent : ThemeService.colors.textPrimary
                            }

                            Text {
                                text: modelData.timestamp ? String(modelData.timestamp).substring(11, 16) : ""
                                font.family: ThemeService.typography.fontFamilyUi
                                font.pixelSize: 10
                                color: ThemeService.colors.textMuted
                            }
                        }

                        // Message Bubble
                        RowLayout {
                            Layout.fillWidth: true
                            layoutDirection: modelData.role === "user" ? Qt.RightToLeft : Qt.LeftToRight

                            Rectangle {
                                implicitWidth: Math.min(msgText.implicitWidth + 24, msgView.width * 0.85)
                                implicitHeight: msgText.implicitHeight + 18
                                radius: ThemeService.metrics.radiusMedium

                                color: modelData.role === "user" ? ThemeService.colors.accent : ThemeService.colors.surfaceVariant
                                border.color: modelData.role === "user" ? ThemeService.colors.accentHover : ThemeService.colors.border
                                border.width: 1

                                Text {
                                    id: msgText
                                    anchors.fill: parent
                                    anchors.margins: 9
                                    text: modelData.content || ""
                                    textFormat: Text.MarkdownText
                                    wrapMode: Text.Wrap
                                    font.family: ThemeService.typography.fontFamilyUi
                                    font.pixelSize: ThemeService.typography.fontSizeNormal
                                    color: modelData.role === "user" ? "#ffffff" : ThemeService.colors.textPrimary
                                }
                            }
                        }
                    }

                    // Empty State Placeholder
                    Text {
                        anchors.centerIn: parent
                        visible: assistantWindow.messagesList.length === 0 && !assistantWindow.isGenerating
                        text: "How can I help you today?\nAsk anything about Arch Linux, code, or desktop controls."
                        horizontalAlignment: Text.AlignHCenter
                        font.family: ThemeService.typography.fontFamilyUi
                        font.pixelSize: ThemeService.typography.fontSizeNormal
                        color: ThemeService.colors.textMuted
                    }
                }
            }

            // Action Plan Approval Dialog Card
            Rectangle {
                Layout.fillWidth: true
                visible: assistantWindow.pendingPlan !== null
                implicitHeight: 90
                radius: ThemeService.metrics.radiusMedium
                color: ThemeService.colors.surfaceVariant
                border.color: ThemeService.colors.warning
                border.width: 1

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 6

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 6

                        Text {
                            text: "󰀦"
                            font.family: ThemeService.typography.fontFamilyMono
                            font.pixelSize: 13
                            color: ThemeService.colors.warning
                        }

                        Text {
                            text: "Action Plan Approval Required"
                            font.family: ThemeService.typography.fontFamilyUi
                            font.pixelSize: 12
                            font.weight: Font.Bold
                            color: ThemeService.colors.textPrimary
                        }
                    }

                    Text {
                        Layout.fillWidth: true
                        text: assistantWindow.pendingPlan ? assistantWindow.pendingPlan.goal : ""
                        font.family: ThemeService.typography.fontFamilyUi
                        font.pixelSize: 11
                        color: ThemeService.colors.textSecondary
                        elide: Text.ElideRight
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 8

                        Rectangle {
                            implicitWidth: 100
                            implicitHeight: 26
                            radius: ThemeService.metrics.radiusSmall
                            color: ThemeService.colors.accent

                            Text {
                                anchors.centerIn: parent
                                text: "Approve & Run"
                                font.family: ThemeService.typography.fontFamilyUi
                                font.pixelSize: 11
                                font.weight: Font.Bold
                                color: "#ffffff"
                            }

                            MouseArea {
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: assistantWindow.approvePlan()
                            }
                        }

                        Rectangle {
                            implicitWidth: 70
                            implicitHeight: 26
                            radius: ThemeService.metrics.radiusSmall
                            color: ThemeService.colors.surface
                            border.color: ThemeService.colors.border
                            border.width: 1

                            Text {
                                anchors.centerIn: parent
                                text: "Reject"
                                font.family: ThemeService.typography.fontFamilyUi
                                font.pixelSize: 11
                                color: ThemeService.colors.textPrimary
                            }

                            MouseArea {
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: assistantWindow.cancelPlan()
                            }
                        }
                    }
                }
            }

            // Reasoning / Thinking Indicator
            RowLayout {
                Layout.fillWidth: true
                visible: assistantWindow.isGenerating
                spacing: 8

                Text {
                    text: "󱚣"
                    font.family: ThemeService.typography.fontFamilyMono
                    font.pixelSize: 14
                    color: ThemeService.colors.accent
                }

                Text {
                    text: assistantWindow.assistantName + " is thinking..."
                    font.family: ThemeService.typography.fontFamilyUi
                    font.pixelSize: 12
                    font.italic: true
                    color: ThemeService.colors.textSecondary
                }
            }

            // Bottom Input Row
            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 46
                radius: ThemeService.metrics.radiusMedium
                color: ThemeService.colors.surfaceVariant
                border.color: chatInput.activeFocus ? ThemeService.colors.borderFocus : ThemeService.colors.border
                border.width: 1

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 12
                    anchors.rightMargin: 8
                    spacing: 8

                    TextInput {
                        id: chatInput
                        Layout.fillWidth: true
                        font.family: ThemeService.typography.fontFamilyUi
                        font.pixelSize: ThemeService.typography.fontSizeNormal
                        color: ThemeService.colors.textPrimary
                        selectByMouse: true

                        Text {
                            anchors.fill: parent
                            visible: !chatInput.text && !chatInput.activeFocus
                            text: "Ask " + assistantWindow.assistantName + " anything... (Press Enter to send)"
                            font.family: ThemeService.typography.fontFamilyUi
                            font.pixelSize: ThemeService.typography.fontSizeNormal
                            color: ThemeService.colors.textMuted
                        }

                        Keys.onReturnPressed: {
                            assistantWindow.sendMessage(chatInput.text);
                        }
                    }

                    // Screen Diagnostics Button
                    Rectangle {
                        implicitWidth: 32
                        implicitHeight: 32
                        radius: ThemeService.metrics.radiusSmall
                        color: screenBtnMouse.containsMouse ? ThemeService.colors.surfaceHover : ThemeService.colors.surface
                        border.color: ThemeService.colors.border
                        border.width: 1

                        Text {
                            anchors.centerIn: parent
                            text: "󰹑"
                            font.family: ThemeService.typography.fontFamilyMono
                            font.pixelSize: 14
                            color: ThemeService.colors.accent
                        }

                        MouseArea {
                            id: screenBtnMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: assistantWindow.diagnoseScreen()
                        }
                    }

                    // Voice Push-to-Talk Button
                    Rectangle {
                        implicitWidth: 32
                        implicitHeight: 32
                        radius: ThemeService.metrics.radiusSmall
                        color: assistantWindow.isListening ? ThemeService.colors.danger : (voiceBtnMouse.containsMouse ? ThemeService.colors.surfaceHover : ThemeService.colors.surface)
                        border.color: ThemeService.colors.border
                        border.width: 1

                        Text {
                            anchors.centerIn: parent
                            text: "󰍬"
                            font.family: ThemeService.typography.fontFamilyMono
                            font.pixelSize: 14
                            color: assistantWindow.isListening ? "#ffffff" : ThemeService.colors.textSecondary
                        }

                        MouseArea {
                            id: voiceBtnMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: assistantWindow.toggleVoice()
                        }
                    }

                    // Send Button
                    Rectangle {
                        implicitWidth: 32
                        implicitHeight: 32
                        radius: ThemeService.metrics.radiusSmall
                        color: chatInput.text.trim().length > 0 ? ThemeService.colors.accent : ThemeService.colors.surface

                        Text {
                            anchors.centerIn: parent
                            text: "󰒭"
                            font.family: ThemeService.typography.fontFamilyMono
                            font.pixelSize: 14
                            color: chatInput.text.trim().length > 0 ? "#ffffff" : ThemeService.colors.textMuted
                        }

                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: assistantWindow.sendMessage(chatInput.text)
                        }
                    }
                }
            }
        }
    }

    // Escape Key Listener
    Item {
        focus: true
        Keys.onEscapePressed: {
            assistantWindow.toggle();
        }
    }

    // -------------------------------------------------------------------------
    // Backend Processes (Quickshell.Io.Process)
    // -------------------------------------------------------------------------
    Process {
        id: pingProc
        stdout: StdioCollector {
            onCollected: function(text) {
                try {
                    var data = JSON.parse(text);
                    if (data.name) assistantWindow.assistantName = data.name;
                    if (data.avatar) assistantWindow.assistantAvatar = data.avatar;
                    if (data.active_provider) assistantWindow.activeProvider = data.active_provider;
                    if (data.active_model) assistantWindow.activeModel = data.active_model;
                } catch(e) {}
            }
        }
    }

    Process {
        id: historyProc
        stdout: StdioCollector {
            onCollected: function(text) {
                try {
                    var data = JSON.parse(text);
                    if (Array.isArray(data)) {
                        assistantWindow.messagesList = data;
                        msgView.positionViewAtEnd();
                    }
                } catch(e) {}
            }
        }
    }

    Process {
        id: chatProc
        stdout: StdioCollector {
            onCollected: function(text) {
                assistantWindow.isGenerating = false;
                try {
                    var res = JSON.parse(text);
                    var updated = assistantWindow.messagesList.slice();
                    updated.push({
                        "role": "assistant",
                        "content": res.content,
                        "timestamp": res.timestamp || new Date().toLocaleTimeString()
                    });
                    assistantWindow.messagesList = updated;
                    msgView.positionViewAtEnd();
                } catch(e) {
                    var fallbackList = assistantWindow.messagesList.slice();
                    fallbackList.push({
                        "role": "assistant",
                        "content": text.trim(),
                        "timestamp": new Date().toLocaleTimeString()
                    });
                    assistantWindow.messagesList = fallbackList;
                    msgView.positionViewAtEnd();
                }
            }
        }
        stderr: StdioCollector {
            onCollected: function(err) {
                if (assistantWindow.isGenerating) {
                    assistantWindow.isGenerating = false;
                }
            }
        }
    }

    Process {
        id: clearProc
        stdout: StdioCollector {
            onCollected: function(text) {
                assistantWindow.messagesList = [];
            }
        }
    }

    Process {
        id: screenProc
        stdout: StdioCollector {
            onCollected: function(text) {
                assistantWindow.isGenerating = false;
                try {
                    var diag = JSON.parse(text);
                    var updated = assistantWindow.messagesList.slice();
                    var contentStr = "### 󰹑 Screen Diagnostics (" + diag.window_title + ")\n\n" + diag.findings + "\n\n**Suggestions:**\n";
                    if (diag.suggestions) {
                        for (var i = 0; i < diag.suggestions.length; i++) {
                            contentStr += "- " + diag.suggestions[i] + "\n";
                        }
                    }
                    updated.push({
                        "role": "assistant",
                        "content": contentStr,
                        "timestamp": new Date().toLocaleTimeString()
                    });
                    assistantWindow.messagesList = updated;
                    msgView.positionViewAtEnd();
                } catch(e) {}
            }
        }
        stderr: StdioCollector {
            onCollected: function(err) {
                assistantWindow.isGenerating = false;
            }
        }
    }

    Process {
        id: stopProc
    }
}
