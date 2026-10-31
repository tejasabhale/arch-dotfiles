import QtQuick
import QtQuick.Layouts
import Quickshell
import Quickshell.Wayland
import Quickshell.Io
import "../shell/services"
import "../shell/components"

PanelWindow {
    id: devWindow

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

    property int activeTab: 0 // 0: Projects, 1: Git, 2: Ports, 3: Envs, 4: SSH

    property var projectList: []
    property var gitStatus: ({ "is_repo": false, "branch": "", "commit": "", "staged": [], "unstaged": [], "untracked": [] })
    property var listeningPorts: []
    property var pythonEnvs: []
    property var sshHosts: []
    property var nodeInfo: ({ "is_node_project": false, "name": "", "scripts": {} })

    function toggle() {
        isOpen = !isOpen;
        if (isOpen) {
            refreshCurrentTab();
        }
    }

    function refreshCurrentTab() {
        if (activeTab === 0) refreshProjects();
        else if (activeTab === 1) refreshGit();
        else if (activeTab === 2) refreshPorts();
        else if (activeTab === 3) refreshEnvs();
        else if (activeTab === 4) refreshSSH();
    }

    onActiveTabChanged: {
        if (isOpen) {
            refreshCurrentTab();
        }
    }

    function refreshAll() {
        refreshProjects();
        refreshGit();
        refreshPorts();
        refreshEnvs();
        refreshSSH();
    }

    function refreshProjects() {
        projProc.command = ["python3", "-m", "developer.project_launcher.project_manager", "--list", "--json"];
        projProc.running = true;
    }

    function refreshGit() {
        gitProc.command = ["python3", "-m", "developer.git.git_manager", "--status", "--json"];
        gitProc.running = true;
    }

    function refreshPorts() {
        portsProc.command = ["python3", "-m", "developer.ports.ports_manager", "--list", "--json"];
        portsProc.running = true;
    }

    function refreshEnvs() {
        envProc.command = ["python3", "-m", "developer.python.python_manager", "--list-envs", "--json"];
        envProc.running = true;
        nodeProc.command = ["python3", "-m", "developer.node.node_manager", "--info", "--json"];
        nodeProc.running = true;
    }

    function refreshSSH() {
        sshProc.command = ["python3", "-m", "developer.ssh.ssh_manager", "--list", "--json"];
        sshProc.running = true;
    }

    function launchProject(path, target) {
        actionProc.command = ["python3", "-m", "developer.project_launcher.project_manager", "--launch", path, "--target", target];
        actionProc.running = true;
    }

    function killPort(port) {
        actionProc.command = ["python3", "-m", "developer.ports.ports_manager", "--kill", port.toString()];
        actionProc.postActionCallback = refreshPorts;
        actionProc.running = true;
    }

    function stageAll() {
        actionProc.command = ["python3", "-m", "developer.git.git_manager", "--stage-all"];
        actionProc.postActionCallback = refreshGit;
        actionProc.running = true;
    }

    function commitGit(msg) {
        if (!msg) return;
        actionProc.command = ["python3", "-m", "developer.git.git_manager", "--commit", msg];
        actionProc.postActionCallback = refreshGit;
        actionProc.running = true;
    }

    function connectSSH(alias) {
        actionProc.command = ["kitty", "--title", "SSH: " + alias, "ssh", alias];
        actionProc.running = true;
        devWindow.isOpen = false;
    }

    // Process runners
    Process {
        id: projProc
        stdout: SplitParser {
            splitMarker: ""
            onRead: data => {
                try {
                    devWindow.projectList = JSON.parse(data);
                } catch (e) {}
            }
        }
    }

    Process {
        id: gitProc
        stdout: SplitParser {
            splitMarker: ""
            onRead: data => {
                try {
                    devWindow.gitStatus = JSON.parse(data);
                } catch (e) {}
            }
        }
    }

    Process {
        id: portsProc
        stdout: SplitParser {
            splitMarker: ""
            onRead: data => {
                try {
                    devWindow.listeningPorts = JSON.parse(data);
                } catch (e) {}
            }
        }
    }

    Process {
        id: envProc
        stdout: SplitParser {
            splitMarker: ""
            onRead: data => {
                try {
                    devWindow.pythonEnvs = JSON.parse(data);
                } catch (e) {}
            }
        }
    }

    Process {
        id: nodeProc
        stdout: SplitParser {
            splitMarker: ""
            onRead: data => {
                try {
                    devWindow.nodeInfo = JSON.parse(data);
                } catch (e) {}
            }
        }
    }

    Process {
        id: sshProc
        stdout: SplitParser {
            splitMarker: ""
            onRead: data => {
                try {
                    devWindow.sshHosts = JSON.parse(data);
                } catch (e) {}
            }
        }
    }

    Process {
        id: actionProc
        property var postActionCallback: null
        onExited: (code, status) => {
            if (postActionCallback) {
                var cb = postActionCallback;
                postActionCallback = null;
                cb();
            }
        }
    }

    // Background Backdrop
    MouseArea {
        anchors.fill: parent
        onClicked: devWindow.isOpen = false

        Rectangle {
            anchors.fill: parent
            color: "#000000"
            opacity: 0.55
        }
    }

    // Centered Control Deck Modal
    Card {
        id: mainCard
        width: Math.min(1000, parent.width - 80)
        height: Math.min(680, parent.height - 80)
        anchors.centerIn: parent

        MouseArea {
            anchors.fill: parent
            // Prevent clicks from dismissing modal
        }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 20
            spacing: 16

            // Header Row
            RowLayout {
                Layout.fillWidth: true
                spacing: 12

                Text {
                    text: "\uf121"
                    font.family: ThemeService.typography.fontFamilyMono
                    font.pixelSize: ThemeService.typography.fontSizeLarge + 4
                    color: ThemeService.colors.accent
                }

                ColumnLayout {
                    spacing: 2
                    Text {
                        text: "Developer Hub"
                        font.family: ThemeService.typography.fontFamilyUi
                        font.pixelSize: ThemeService.typography.fontSizeLarge
                        font.bold: true
                        color: ThemeService.colors.textPrimary
                    }
                    Text {
                        text: "Workspaces, Git, Local Sockets, Envs & SSH"
                        font.family: ThemeService.typography.fontFamilyUi
                        font.pixelSize: ThemeService.typography.fontSizeSmall
                        color: ThemeService.colors.textSecondary
                    }
                }

                Item { Layout.fillWidth: true }

                Button {
                    icon: "\uf021"
                    text: "Refresh"
                    variant: "secondary"
                    onClicked: devWindow.refreshAll()
                }

                Button {
                    icon: "\uf00d"
                    variant: "ghost"
                    onClicked: devWindow.isOpen = false
                }
            }

            // Tab Bar Navigation
            RowLayout {
                Layout.fillWidth: true
                spacing: 8

                Pill {
                    icon: "\uf07b"
                    text: "Projects"
                    active: devWindow.activeTab === 0
                    onClicked: devWindow.activeTab = 0
                }

                Pill {
                    icon: "\uf126"
                    text: "Git Dashboard"
                    active: devWindow.activeTab === 1
                    onClicked: devWindow.activeTab = 1
                }

                Pill {
                    icon: "\uf1e0"
                    text: "Listening Ports"
                    active: devWindow.activeTab === 2
                    onClicked: devWindow.activeTab = 2
                }

                Pill {
                    icon: "\uf3e2"
                    text: "Python & Node"
                    active: devWindow.activeTab === 3
                    onClicked: devWindow.activeTab = 3
                }

                Pill {
                    icon: "\uf489"
                    text: "SSH Shortcuts"
                    active: devWindow.activeTab === 4
                    onClicked: devWindow.activeTab = 4
                }

                Item { Layout.fillWidth: true }
            }

            // Tab Content Switcher
            Item {
                Layout.fillWidth: true
                Layout.fillHeight: true

                // TAB 0: PROJECTS
                ColumnLayout {
                    anchors.fill: parent
                    visible: devWindow.activeTab === 0
                    spacing: 12

                    ListView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true
                        spacing: 8
                        model: devWindow.projectList

                        delegate: Rectangle {
                            width: ListView.view.width
                            height: 64
                            radius: ThemeService.metrics.radiusSmall
                            color: ThemeService.colors.surfaceVariant
                            border.color: ThemeService.colors.border
                            border.width: ThemeService.metrics.borderWidth

                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 12
                                spacing: 12

                                Text {
                                    text: "\uf07b"
                                    font.family: ThemeService.typography.fontFamilyMono
                                    font.pixelSize: ThemeService.typography.fontSizeNormal + 2
                                    color: ThemeService.colors.accent
                                }

                                ColumnLayout {
                                    spacing: 2
                                    Layout.fillWidth: true

                                    RowLayout {
                                        spacing: 8
                                        Text {
                                            text: modelData.name || "Project"
                                            font.family: ThemeService.typography.fontFamilyUi
                                            font.pixelSize: ThemeService.typography.fontSizeNormal
                                            font.bold: true
                                            color: ThemeService.colors.textPrimary
                                        }
                                        Rectangle {
                                            implicitWidth: typeText.implicitWidth + 8
                                            implicitHeight: 18
                                            radius: 4
                                            color: ThemeService.colors.surface
                                            border.color: ThemeService.colors.border
                                            Text {
                                                id: typeText
                                                anchors.centerIn: parent
                                                text: modelData.type || "Code"
                                                font.pixelSize: ThemeService.typography.fontSizeSmall - 2
                                                color: ThemeService.colors.accent
                                            }
                                        }
                                        Text {
                                            visible: !!modelData.git_branch
                                            text: "\uf126 " + (modelData.git_branch || "")
                                            font.family: ThemeService.typography.fontFamilyMono
                                            font.pixelSize: ThemeService.typography.fontSizeSmall - 1
                                            color: ThemeService.colors.textSecondary
                                        }
                                    }

                                    Text {
                                        text: modelData.path || ""
                                        font.family: ThemeService.typography.fontFamilyMono
                                        font.pixelSize: ThemeService.typography.fontSizeSmall - 1
                                        color: ThemeService.colors.textSecondary
                                        elide: Text.ElideMiddle
                                        Layout.fillWidth: true
                                    }
                                }

                                Button {
                                    text: "Code"
                                    variant: "primary"
                                    onClicked: devWindow.launchProject(modelData.path, "code")
                                }

                                Button {
                                    text: "Kitty"
                                    variant: "secondary"
                                    onClicked: devWindow.launchProject(modelData.path, "kitty")
                                }

                                Button {
                                    text: "Files"
                                    variant: "ghost"
                                    onClicked: devWindow.launchProject(modelData.path, "dolphin")
                                }
                            }
                        }
                    }
                }

                // TAB 1: GIT DASHBOARD
                ColumnLayout {
                    anchors.fill: parent
                    visible: devWindow.activeTab === 1
                    spacing: 14

                    Card {
                        Layout.fillWidth: true
                        implicitHeight: 90

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 14
                            spacing: 20

                            ColumnLayout {
                                spacing: 4
                                Text {
                                    text: "Active Branch"
                                    font.pixelSize: ThemeService.typography.fontSizeSmall
                                    color: ThemeService.colors.textSecondary
                                }
                                RowLayout {
                                    spacing: 8
                                    Text {
                                        text: "\uf126"
                                        font.family: ThemeService.typography.fontFamilyMono
                                        font.pixelSize: ThemeService.typography.fontSizeLarge
                                        color: ThemeService.colors.accent
                                    }
                                    Text {
                                        text: devWindow.gitStatus.branch || "master"
                                        font.family: ThemeService.typography.fontFamilyUi
                                        font.pixelSize: ThemeService.typography.fontSizeLarge
                                        font.bold: true
                                        color: ThemeService.colors.textPrimary
                                    }
                                }
                            }

                            Rectangle {
                                width: 1
                                Layout.fillHeight: true
                                color: ThemeService.colors.border
                            }

                            ColumnLayout {
                                spacing: 4
                                Text {
                                    text: "Commit & Sync"
                                    font.pixelSize: ThemeService.typography.fontSizeSmall
                                    color: ThemeService.colors.textSecondary
                                }
                                Text {
                                    text: (devWindow.gitStatus.commit || "none") + " (" + (devWindow.gitStatus.ahead || 0) + " ahead, " + (devWindow.gitStatus.behind || 0) + " behind)"
                                    font.family: ThemeService.typography.fontFamilyMono
                                    font.pixelSize: ThemeService.typography.fontSizeNormal
                                    color: ThemeService.colors.textPrimary
                                }
                            }

                            Item { Layout.fillWidth: true }

                            Button {
                                text: "Stage All"
                                icon: "\uf067"
                                variant: "secondary"
                                onClicked: devWindow.stageAll()
                            }
                        }
                    }

                    // Staged and Unstaged Files View
                    RowLayout {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        spacing: 12

                        // Staged Files
                        Card {
                            Layout.fillWidth: true
                            Layout.fillHeight: true

                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 12
                                spacing: 8

                                Text {
                                    text: "Staged Changes (" + (devWindow.gitStatus.staged ? devWindow.gitStatus.staged.length : 0) + ")"
                                    font.family: ThemeService.typography.fontFamilyUi
                                    font.bold: true
                                    color: ThemeService.colors.success || ThemeService.colors.accent
                                }

                                ListView {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    clip: true
                                    model: devWindow.gitStatus.staged || []
                                    delegate: Text {
                                        text: "\uf00c  " + modelData
                                        font.family: ThemeService.typography.fontFamilyMono
                                        font.pixelSize: ThemeService.typography.fontSizeSmall
                                        color: ThemeService.colors.textPrimary
                                    }
                                }
                            }
                        }

                        // Unstaged Files
                        Card {
                            Layout.fillWidth: true
                            Layout.fillHeight: true

                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 12
                                spacing: 8

                                Text {
                                    text: "Unstaged / Untracked (" + ((devWindow.gitStatus.unstaged ? devWindow.gitStatus.unstaged.length : 0) + (devWindow.gitStatus.untracked ? devWindow.gitStatus.untracked.length : 0)) + ")"
                                    font.family: ThemeService.typography.fontFamilyUi
                                    font.bold: true
                                    color: ThemeService.colors.warning || ThemeService.colors.textSecondary
                                }

                                ListView {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    clip: true
                                    model: (devWindow.gitStatus.unstaged || []).concat(devWindow.gitStatus.untracked || [])
                                    delegate: Text {
                                        text: "\uf044  " + modelData
                                        font.family: ThemeService.typography.fontFamilyMono
                                        font.pixelSize: ThemeService.typography.fontSizeSmall
                                        color: ThemeService.colors.textPrimary
                                    }
                                }
                            }
                        }
                    }

                    // Commit input row
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 10

                        TextField {
                            id: commitInput
                            Layout.fillWidth: true
                            placeholderText: "Commit message (e.g. feat: implement auth flow)"
                        }

                        Button {
                            text: "Commit"
                            icon: "\uf0c7"
                            variant: "primary"
                            onClicked: {
                                devWindow.commitGit(commitInput.text);
                                commitInput.text = "";
                            }
                        }
                    }
                }

                // TAB 2: LISTENING PORTS
                ColumnLayout {
                    anchors.fill: parent
                    visible: devWindow.activeTab === 2
                    spacing: 12

                    ListView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true
                        spacing: 6
                        model: devWindow.listeningPorts

                        delegate: Rectangle {
                            width: ListView.view.width
                            height: 48
                            radius: ThemeService.metrics.radiusSmall
                            color: ThemeService.colors.surfaceVariant
                            border.color: ThemeService.colors.border
                            border.width: ThemeService.metrics.borderWidth

                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 10
                                spacing: 14

                                Rectangle {
                                    implicitWidth: 64
                                    implicitHeight: 26
                                    radius: 4
                                    color: ThemeService.colors.surface
                                    border.color: ThemeService.colors.border
                                    Text {
                                        anchors.centerIn: parent
                                        text: ":" + modelData.port
                                        font.family: ThemeService.typography.fontFamilyMono
                                        font.bold: true
                                        color: ThemeService.colors.accent
                                    }
                                }

                                Text {
                                    text: modelData.protocol || "TCP"
                                    font.family: ThemeService.typography.fontFamilyMono
                                    font.pixelSize: ThemeService.typography.fontSizeSmall
                                    color: ThemeService.colors.textSecondary
                                }

                                Text {
                                    text: modelData.process + (modelData.pid ? " (PID " + modelData.pid + ")" : "")
                                    font.family: ThemeService.typography.fontFamilyMono
                                    font.pixelSize: ThemeService.typography.fontSizeNormal
                                    font.bold: true
                                    color: ThemeService.colors.textPrimary
                                    Layout.preferredWidth: 200
                                    elide: Text.ElideRight
                                }

                                Text {
                                    text: modelData.service || "Service"
                                    font.family: ThemeService.typography.fontFamilyUi
                                    font.pixelSize: ThemeService.typography.fontSizeSmall
                                    color: ThemeService.colors.textSecondary
                                    Layout.fillWidth: true
                                    elide: Text.ElideRight
                                }

                                Button {
                                    text: "Kill"
                                    icon: "\uf1f8"
                                    variant: "danger"
                                    onClicked: devWindow.killPort(modelData.port)
                                }
                            }
                        }
                    }
                }

                // TAB 3: PYTHON & NODE ENVIRONMENTS
                RowLayout {
                    anchors.fill: parent
                    visible: devWindow.activeTab === 3
                    spacing: 14

                    // Python environments column
                    Card {
                        Layout.fillWidth: true
                        Layout.fillHeight: true

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 14
                            spacing: 10

                            RowLayout {
                                Text {
                                    text: "\uf3e2  Python Toolchain"
                                    font.family: ThemeService.typography.fontFamilyUi
                                    font.pixelSize: ThemeService.typography.fontSizeNormal + 1
                                    font.bold: true
                                    color: ThemeService.colors.textPrimary
                                }
                                Item { Layout.fillWidth: true }
                                Button {
                                    text: "Jupyter"
                                    icon: "\uf02d"
                                    variant: "secondary"
                                    onClicked: {
                                        actionProc.command = ["jupyter-lab", "--notebook-dir=."];
                                        actionProc.running = true;
                                    }
                                }
                            }

                            ListView {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                clip: true
                                spacing: 6
                                model: devWindow.pythonEnvs

                                delegate: Rectangle {
                                    width: ListView.view.width
                                    height: 52
                                    radius: ThemeService.metrics.radiusSmall
                                    color: ThemeService.colors.surfaceVariant
                                    border.color: ThemeService.colors.border
                                    border.width: ThemeService.metrics.borderWidth

                                    ColumnLayout {
                                        anchors.fill: parent
                                        anchors.margins: 8
                                        spacing: 2
                                        RowLayout {
                                            Text {
                                                text: modelData.name || "env"
                                                font.family: ThemeService.typography.fontFamilyUi
                                                font.bold: true
                                                color: ThemeService.colors.textPrimary
                                            }
                                            Rectangle {
                                                implicitWidth: envBadgeText.implicitWidth + 8
                                                implicitHeight: 16
                                                radius: 4
                                                color: ThemeService.colors.surface
                                                Text {
                                                    id: envBadgeText
                                                    anchors.centerIn: parent
                                                    text: modelData.type || "venv"
                                                    font.pixelSize: 10
                                                    color: ThemeService.colors.accent
                                                }
                                            }
                                        }
                                        Text {
                                            text: modelData.path || ""
                                            font.family: ThemeService.typography.fontFamilyMono
                                            font.pixelSize: 11
                                            color: ThemeService.colors.textSecondary
                                            elide: Text.ElideMiddle
                                            Layout.fillWidth: true
                                        }
                                    }
                                }
                            }
                        }
                    }

                    // Node column
                    Card {
                        Layout.fillWidth: true
                        Layout.fillHeight: true

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 14
                            spacing: 10

                            Text {
                                text: "\uf898  Node.js & Package Scripts"
                                font.family: ThemeService.typography.fontFamilyUi
                                font.pixelSize: ThemeService.typography.fontSizeNormal + 1
                                font.bold: true
                                color: ThemeService.colors.textPrimary
                            }

                            Text {
                                text: devWindow.nodeInfo.is_node_project ? (devWindow.nodeInfo.name + " (" + devWindow.nodeInfo.package_manager + ")") : "No package.json in current directory"
                                font.family: ThemeService.typography.fontFamilyUi
                                font.pixelSize: ThemeService.typography.fontSizeSmall
                                color: ThemeService.colors.textSecondary
                            }

                            ListView {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                clip: true
                                spacing: 6
                                model: Object.keys(devWindow.nodeInfo.scripts || {})

                                delegate: Rectangle {
                                    width: ListView.view.width
                                    height: 44
                                    radius: ThemeService.metrics.radiusSmall
                                    color: ThemeService.colors.surfaceVariant
                                    border.color: ThemeService.colors.border
                                    border.width: ThemeService.metrics.borderWidth

                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.margins: 8
                                        spacing: 10

                                        Text {
                                            text: modelData
                                            font.family: ThemeService.typography.fontFamilyMono
                                            font.bold: true
                                            color: ThemeService.colors.textPrimary
                                        }

                                        Text {
                                            text: devWindow.nodeInfo.scripts[modelData] || ""
                                            font.family: ThemeService.typography.fontFamilyMono
                                            font.pixelSize: 11
                                            color: ThemeService.colors.textSecondary
                                            elide: Text.ElideRight
                                            Layout.fillWidth: true
                                        }

                                        Button {
                                            text: "Run"
                                            variant: "secondary"
                                            onClicked: {
                                                actionProc.command = ["python3", "-m", "developer.node.node_manager", "--run", modelData];
                                                actionProc.running = true;
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                // TAB 4: SSH SHORTCUTS
                ColumnLayout {
                    anchors.fill: parent
                    visible: devWindow.activeTab === 4
                    spacing: 12

                    ListView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true
                        spacing: 8
                        model: devWindow.sshHosts

                        delegate: Rectangle {
                            width: ListView.view.width
                            height: 56
                            radius: ThemeService.metrics.radiusSmall
                            color: ThemeService.colors.surfaceVariant
                            border.color: ThemeService.colors.border
                            border.width: ThemeService.metrics.borderWidth

                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 12
                                spacing: 14

                                Text {
                                    text: "\uf489"
                                    font.family: ThemeService.typography.fontFamilyMono
                                    font.pixelSize: ThemeService.typography.fontSizeNormal + 2
                                    color: ThemeService.colors.accent
                                }

                                ColumnLayout {
                                    spacing: 2
                                    Layout.fillWidth: true

                                    Text {
                                        text: modelData.alias || "host"
                                        font.family: ThemeService.typography.fontFamilyUi
                                        font.pixelSize: ThemeService.typography.fontSizeNormal
                                        font.bold: true
                                        color: ThemeService.colors.textPrimary
                                    }

                                    Text {
                                        text: (modelData.user ? modelData.user + "@" : "") + modelData.hostname + ":" + modelData.port
                                        font.family: ThemeService.typography.fontFamilyMono
                                        font.pixelSize: ThemeService.typography.fontSizeSmall - 1
                                        color: ThemeService.colors.textSecondary
                                    }
                                }

                                Button {
                                    text: "Connect"
                                    icon: "\uf120"
                                    variant: "primary"
                                    onClicked: devWindow.connectSSH(modelData.alias)
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
