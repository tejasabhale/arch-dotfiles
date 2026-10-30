import QtQuick
import QtQuick.Layouts
import Quickshell
import Quickshell.Wayland
import Quickshell.Hyprland
import Quickshell.Io
import "../services"
import "../components"

PanelWindow {
    id: launcherWindow

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

    property string activeCategory: "All"
    property string searchQuery: ""
    property int selectedIndex: 0

    // Master Application Registry (Fallback offline catalog + desktop entries)
    property var allApps: [
        { "name": "Kitty Terminal", "category": "Development", "exec": "kitty", "icon": "󰞷", "keywords": "terminal bash fish cli" },
        { "name": "Visual Studio Code", "category": "Development", "exec": "code", "icon": "󰨞", "keywords": "code editor programming dev" },
        { "name": "Firefox Browser", "category": "Internet", "exec": "firefox", "icon": "󰈹", "keywords": "web internet browser firefox" },
        { "name": "Dolphin File Manager", "category": "System", "exec": "dolphin", "icon": "󰉋", "keywords": "files folder explorer storage" },
        { "name": "June AI Assistant", "category": "Tools", "exec": "quickshell ipc call assistant toggle", "icon": "󱚣", "keywords": "ai june assistant llm voice" },
        { "name": "Settings", "category": "System", "exec": "quickshell ipc call settings toggle", "icon": "󰒓", "keywords": "settings preferences config options" },
        { "name": "Jupyter Lab", "category": "Development", "exec": "jupyter-lab", "icon": "󱚠", "keywords": "jupyter python ml machine learning notebook" },
        { "name": "PipeWire Volume Control", "category": "Media", "exec": "pavucontrol", "icon": "󰕾", "keywords": "audio volume sound mixer" },
        { "name": "Bluetooth Manager", "category": "System", "exec": "blueman-manager", "icon": "󰂯", "keywords": "bluetooth bt devices wireless" },
        { "name": "Network Connections", "category": "System", "exec": "nm-connection-editor", "icon": "󰤨", "keywords": "network wifi ethernet hotspot" },
        { "name": "Discord", "category": "Internet", "exec": "discord", "icon": "󰙯", "keywords": "chat discord comms talk" },
        { "name": "Telegram", "category": "Internet", "exec": "telegram-desktop", "icon": "󰭹", "keywords": "telegram messenger chat" },
        { "name": "System Monitor", "category": "System", "exec": "kitty -e btop", "icon": "󰍹", "keywords": "btop htop task manager monitor ram cpu" },
        { "name": "Calculator", "category": "Tools", "exec": "kcalc", "icon": "󰪚", "keywords": "calculator math calculation" }
    ]

    function toggle() {
        isOpen = !isOpen;
        if (isOpen) {
            searchQuery = "";
            activeCategory = "All";
            selectedIndex = 0;
            searchInput.forceActiveFocus();
        }
    }

    function launchApp(execCmd) {
        if (!execCmd) return;
        launcherWindow.isOpen = false;

        // Check if web search
        if (execCmd.startsWith("http://") || execCmd.startsWith("https://")) {
            Hyprland.dispatch("exec xdg-open " + execCmd);
        } else {
            Hyprland.dispatch("exec " + execCmd);
        }
    }

    // Dismiss when clicking outside modal card
    MouseArea {
        anchors.fill: parent
        onClicked: launcherWindow.isOpen = false

        // Semi-transparent dimming backdrop
        Rectangle {
            anchors.fill: parent
            color: "#00000066"
        }
    }

    // Centered Floating Search Card
    Rectangle {
        id: modalCard
        anchors.centerIn: parent
        implicitWidth: 640
        implicitHeight: 480
        radius: ThemeService.metrics.radiusLarge
        color: ThemeService.colors.backgroundBlur
        border.color: ThemeService.colors.border
        border.width: ThemeService.metrics.borderWidth
        clip: true

        // Stop clicks inside modal from dismissing
        MouseArea {
            anchors.fill: parent
            hoverEnabled: false
        }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 18
            spacing: 12

            // 1. Search Bar
            TextField {
                id: searchInput
                Layout.fillWidth: true
                placeholder: "Type to search apps, '= 42*2' for math, '? query' for web..."
                leadingIcon: "󰍉"
                text: launcherWindow.searchQuery
                onTextChanged: function(val) {
                    launcherWindow.searchQuery = val.trim();
                    launcherWindow.selectedIndex = 0;
                }
                onAccepted: {
                    if (filteredModel.count > 0) {
                        var firstItem = filteredModel.get(0);
                        launcherWindow.launchApp(firstItem.exec);
                    }
                }
            }

            // 2. Category Filter Pills
            RowLayout {
                Layout.fillWidth: true
                spacing: 6

                property var categories: ["All", "Development", "Internet", "System", "Media", "Tools"]

                Repeater {
                    model: parent.categories

                    Pill {
                        required property string modelData
                        text: modelData
                        active: launcherWindow.activeCategory === modelData
                        onClicked: {
                            launcherWindow.activeCategory = modelData;
                            launcherWindow.selectedIndex = 0;
                        }
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 1
                color: ThemeService.colors.border
            }

            // 3. Application Grid View
            ScrollView {
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true

                GridView {
                    id: appGrid
                    cellWidth: 150
                    cellHeight: 96
                    anchors.fill: parent
                    model: ListModel { id: filteredModel }

                    delegate: AppItem {
                        name: model.name
                        category: model.category
                        execCmd: model.exec
                        iconGlyph: model.icon
                        isSelected: index === launcherWindow.selectedIndex
                        onClicked: launcherWindow.launchApp(model.exec)
                    }
                }
            }
        }
    }

    // Filter Logic: Updates filteredModel whenever searchQuery or activeCategory changes
    function updateFilteredList() {
        filteredModel.clear();
        var q = searchQuery.toLowerCase();

        // 1. Math calculation helper (= 25 * 4)
        if (q.startsWith("=")) {
            var expr = q.substring(1).trim();
            try {
                // Safe numeric evaluation
                if (/^[0-9\.\+\-\*\/\(\)\s]+$/.test(expr)) {
                    var result = Function("return (" + expr + ")")();
                    filteredModel.append({
                        "name": "= " + result,
                        "category": "Calculator",
                        "exec": "wl-copy " + result,
                        "icon": "󰪚"
                    });
                    return;
                }
            } catch (e) {}
        }

        // 2. Web search helper (? search query)
        if (q.startsWith("?")) {
            var webQuery = q.substring(1).trim();
            if (webQuery) {
                filteredModel.append({
                    "name": "Search: " + webQuery,
                    "category": "Web Search",
                    "exec": "https://duckduckgo.com/?q=" + encodeURIComponent(webQuery),
                    "icon": "󰈹"
                });
            }
        }

        // 3. Filter apps by category & query
        for (var i = 0; i < allApps.length; i++) {
            var app = allApps[i];
            var matchesCategory = (activeCategory === "All" || app.category === activeCategory);
            var matchesQuery = (q === "" || app.name.toLowerCase().indexOf(q) !== -1 || app.keywords.toLowerCase().indexOf(q) !== -1);

            if (matchesCategory && matchesQuery) {
                filteredModel.append(app);
            }
        }
    }

    onSearchQueryChanged: updateFilteredList()
    onActiveCategoryChanged: updateFilteredList()
    Component.onCompleted: updateFilteredList()

    // Keyboard Navigation Handlers
    Keys.onEscapePressed: launcherWindow.isOpen = false
}
