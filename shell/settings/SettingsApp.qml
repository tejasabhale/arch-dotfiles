import QtQuick
import QtQuick.Layouts
import Quickshell
import Quickshell.Wayland
import Quickshell.Io
import "../services"
import "../components"
import "pages"

PanelWindow {
    id: settingsWindow

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

    property string activeCategory: "overview"
    property string searchQuery: ""

    function toggle() {
        isOpen = !isOpen;
    }

    // 22 Categories metadata
    property var categories: [
        { id: "overview", name: "System Overview", icon: "\uf108", keywords: "system cpu ram hardware specs arch elitebook" },
        { id: "features", name: "Features & Daemons", icon: "\uf085", keywords: "modules daemons toggles isolation services kill" },
        { id: "appearance", name: "Appearance & Themes", icon: "\uf53f", keywords: "theme colors midnight nordic forest violet font blur radius" },
        { id: "compositor", name: "Compositor & Window", icon: "\uf2d0", keywords: "hyprland gaps borders animations sensitivity touchpad" },
        { id: "performance", name: "Performance Profiles", icon: "\uf0e7", keywords: "cpu battery governor balanced performance ram power" },
        { id: "assistant", name: "June AI Assistant", icon: "\uf544", keywords: "ai june provider gemini openai ollama voice identity" },
        { id: "languages", name: "Languages & STT/TTS", icon: "\uf1ab", keywords: "multilingual hindi marathi english hinglish devanagari voice" },
        { id: "network", name: "Network & Hotspot", icon: "\uf1eb", keywords: "wifi hotspot ap networkmanager wlan qr internet" },
        { id: "bluetooth", name: "Bluetooth Devices", icon: "\uf294", keywords: "bluez bluetooth pair connect devices audio" },
        { id: "audio", name: "Audio & Sound", icon: "\uf028", keywords: "volume sound pipewire speaker mic levels" },
        { id: "display", name: "Display & Scaling", icon: "\uf26c", keywords: "screen monitor scale resolution refresh rate idle" },
        { id: "workspaces", name: "Workspaces & Gestures", icon: "\uf009", keywords: "hyprland workspace gestures swipe layout" },
        { id: "productivity", name: "Productivity Suite", icon: "\uf0cb", keywords: "clipboard screenshot notes pomodoro dashboard" },
        { id: "developer", name: "Developer Tools", icon: "\uf121", keywords: "git ports python node code kitty ssh workspaces" },
        { id: "shortcuts", name: "Keybindings", icon: "\uf11c", keywords: "keyboard shortcuts bindings super mod hotkeys" },
        { id: "notifications", name: "Notifications & DND", icon: "\uf0f3", keywords: "alerts do not disturb dnd popups osd sound" },
        { id: "security", name: "Security & Safety", icon: "\uf023", keywords: "lockscreen password safety dualboot efi credentials" },
        { id: "power", name: "Power & Sleep", icon: "\uf011", keywords: "battery suspend lid sleep charge governor" },
        { id: "storage", name: "Storage & Cache", icon: "\uf0a0", keywords: "disk space clean cache dotfiles logs" },
        { id: "accessibility", name: "Accessibility", icon: "\uf29a", keywords: "contrast large font zoom cursor" },
        { id: "backup", name: "Backup & Recovery", icon: "\uf1da", keywords: "snapshots rollback reset factory defaults recovery" },
        { id: "about", name: "About Tejas OS", icon: "\uf05a", keywords: "about version release arch linux hyprland author" }
    ]

    function getFilteredCategories() {
        if (!searchQuery || searchQuery.trim() === "") {
            return categories;
        }
        var q = searchQuery.toLowerCase().trim();
        return categories.filter(c => c.name.toLowerCase().indexOf(q) !== -1 || c.keywords.indexOf(q) !== -1);
    }

    // Background Backdrop
    MouseArea {
        anchors.fill: parent
        onClicked: settingsWindow.isOpen = false

        Rectangle {
            anchors.fill: parent
            color: "#000000"
            opacity: 0.6
        }
    }

    // Main Settings Window Card
    Card {
        id: settingsCard
        width: Math.min(1080, parent.width - 60)
        height: Math.min(740, parent.height - 60)
        anchors.centerIn: parent

        MouseArea {
            anchors.fill: parent
            // Prevent clicks from dismissing
        }

        RowLayout {
            anchors.fill: parent
            spacing: 0

            // Left Navigation Sidebar
            Rectangle {
                Layout.fillHeight: true
                Layout.preferredWidth: 260
                color: ThemeService.colors.surfaceVariant
                border.color: ThemeService.colors.border
                border.width: ThemeService.metrics.borderWidth

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 14
                    spacing: 12

                    // Title
                    RowLayout {
                        spacing: 10
                        Text {
                            text: "\uf013"
                            font.family: ThemeService.typography.fontFamilyMono
                            font.pixelSize: ThemeService.typography.fontSizeLarge + 2
                            color: ThemeService.colors.accent
                        }
                        Text {
                            text: "Settings"
                            font.family: ThemeService.typography.fontFamilyUi
                            font.pixelSize: ThemeService.typography.fontSizeLarge
                            font.bold: true
                            color: ThemeService.colors.textPrimary
                        }
                    }

                    // Search Input
                    TextField {
                        Layout.fillWidth: true
                        placeholderText: "Search 22 categories..."
                        onTextChanged: settingsWindow.searchQuery = text
                    }

                    // Categories Navigation List
                    ListView {
                        id: catList
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true
                        spacing: 4
                        model: settingsWindow.getFilteredCategories()

                        delegate: Rectangle {
                            width: ListView.view.width
                            height: 38
                            radius: ThemeService.metrics.radiusSmall
                            color: settingsWindow.activeCategory === modelData.id ? ThemeService.colors.surface : (mouseArea.containsMouse ? ThemeService.colors.surfaceHover : "transparent")
                            border.color: settingsWindow.activeCategory === modelData.id ? ThemeService.colors.borderFocus : "transparent"
                            border.width: 1

                            MouseArea {
                                id: mouseArea
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: settingsWindow.activeCategory = modelData.id
                            }

                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 8
                                spacing: 10

                                Text {
                                    text: modelData.icon
                                    font.family: ThemeService.typography.fontFamilyMono
                                    font.pixelSize: ThemeService.typography.fontSizeNormal
                                    color: settingsWindow.activeCategory === modelData.id ? ThemeService.colors.accent : ThemeService.colors.textSecondary
                                }

                                Text {
                                    text: modelData.name
                                    font.family: ThemeService.typography.fontFamilyUi
                                    font.pixelSize: ThemeService.typography.fontSizeSmall + 1
                                    font.bold: settingsWindow.activeCategory === modelData.id
                                    color: settingsWindow.activeCategory === modelData.id ? ThemeService.colors.textPrimary : ThemeService.colors.textSecondary
                                    Layout.fillWidth: true
                                    elide: Text.ElideRight
                                }
                            }
                        }
                    }
                }
            }

            // Right Category Content View
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: ThemeService.colors.surface

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 16

                    // Top Bar with Close button
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 12

                        Text {
                            text: {
                                var cat = settingsWindow.categories.find(c => c.id === settingsWindow.activeCategory);
                                return cat ? cat.name : "Settings";
                            }
                            font.family: ThemeService.typography.fontFamilyUi
                            font.pixelSize: ThemeService.typography.fontSizeLarge + 2
                            font.bold: true
                            color: ThemeService.colors.textPrimary
                        }

                        Item { Layout.fillWidth: true }

                        Button {
                            icon: "\uf00d"
                            variant: "ghost"
                            onClicked: settingsWindow.isOpen = false
                        }
                    }

                    // Content Switcher
                    Item {
                        Layout.fillWidth: true
                        Layout.fillHeight: true

                        // 1. OVERVIEW
                        ColumnLayout {
                            anchors.fill: parent
                            visible: settingsWindow.activeCategory === "overview"
                            spacing: 14

                            Card {
                                Layout.fillWidth: true
                                implicitHeight: 160

                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: 16
                                    spacing: 18

                                    Text {
                                        text: "\uf303"
                                        font.family: ThemeService.typography.fontFamilyMono
                                        font.pixelSize: 48
                                        color: ThemeService.colors.accent
                                    }

                                    ColumnLayout {
                                        spacing: 4
                                        Text {
                                            text: "HP EliteBook 840 G5"
                                            font.family: ThemeService.typography.fontFamilyUi
                                            font.pixelSize: ThemeService.typography.fontSizeLarge
                                            font.bold: true
                                            color: ThemeService.colors.textPrimary
                                        }
                                        Text {
                                            text: "Intel Core i5/i7 8th Gen • Intel UHD Graphics 620 • 8 GB RAM"
                                            font.family: ThemeService.typography.fontFamilyUi
                                            font.pixelSize: ThemeService.typography.fontSizeNormal
                                            color: ThemeService.colors.textSecondary
                                        }
                                        Text {
                                            text: "Arch Linux (Rolling) • Hyprland 0.55+ (Lua) • Quickshell Wayland"
                                            font.family: ThemeService.typography.fontFamilyUi
                                            font.pixelSize: ThemeService.typography.fontSizeSmall
                                            color: ThemeService.colors.accent
                                        }
                                        Text {
                                            text: "Dual-Boot UEFI (Windows 11 + Arch Linux) • Protected ESP & NTFS"
                                            font.family: ThemeService.typography.fontFamilyUi
                                            font.pixelSize: ThemeService.typography.fontSizeSmall
                                            color: ThemeService.colors.textSecondary
                                        }
                                    }
                                }
                            }

                            // Quick stats grid
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 12

                                Card {
                                    Layout.fillWidth: true
                                    implicitHeight: 90
                                    ColumnLayout {
                                        anchors.centerIn: parent
                                        spacing: 4
                                        Text { text: "RAM Target"; font.pixelSize: 11; color: ThemeService.colors.textSecondary }
                                        Text { text: "<= 1.8 GB Idle"; font.bold: true; color: ThemeService.colors.accent }
                                    }
                                }

                                Card {
                                    Layout.fillWidth: true
                                    implicitHeight: 90
                                    ColumnLayout {
                                        anchors.centerIn: parent
                                        spacing: 4
                                        Text { text: "Active Theme"; font.pixelSize: 11; color: ThemeService.colors.textSecondary }
                                        Text { text: ThemeService.activePreset; font.bold: true; color: ThemeService.colors.textPrimary }
                                    }
                                }

                                Card {
                                    Layout.fillWidth: true
                                    implicitHeight: 90
                                    ColumnLayout {
                                        anchors.centerIn: parent
                                        spacing: 4
                                        Text { text: "June AI Service"; font.pixelSize: 11; color: ThemeService.colors.textSecondary }
                                        Text { text: "Decoupled IPC"; font.bold: true; color: ThemeService.colors.textPrimary }
                                    }
                                }
                            }

                            Item { Layout.fillHeight: true }
                        }

                        // 2. FEATURES & DAEMONS (Lazy loaded on tab activation)
                        Loader {
                            anchors.fill: parent
                            active: settingsWindow.activeCategory === "features"
                            visible: active
                            sourceComponent: FeatureManager {}
                        }

                        // 3. APPEARANCE & THEMES
                        ColumnLayout {
                            anchors.fill: parent
                            visible: settingsWindow.activeCategory === "appearance"
                            spacing: 14

                            Text {
                                text: "Select Theme Preset"
                                font.family: ThemeService.typography.fontFamilyUi
                                font.bold: true
                                color: ThemeService.colors.textPrimary
                            }

                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 12

                                Card {
                                    Layout.fillWidth: true
                                    implicitHeight: 80
                                    border.color: ThemeService.activePreset === "midnight" ? ThemeService.colors.accent : ThemeService.colors.border
                                    border.width: ThemeService.activePreset === "midnight" ? 2 : 1
                                    MouseArea {
                                        anchors.fill: parent
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: ThemeService.loadPreset("midnight")
                                    }
                                    ColumnLayout {
                                        anchors.centerIn: parent
                                        Text { text: "Midnight"; font.bold: true; color: "#7aa2f7" }
                                        Text { text: "Dark Indigo"; font.pixelSize: 11; color: ThemeService.colors.textSecondary }
                                    }
                                }

                                Card {
                                    Layout.fillWidth: true
                                    implicitHeight: 80
                                    border.color: ThemeService.activePreset === "nordic" ? ThemeService.colors.accent : ThemeService.colors.border
                                    border.width: ThemeService.activePreset === "nordic" ? 2 : 1
                                    MouseArea {
                                        anchors.fill: parent
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: ThemeService.loadPreset("nordic")
                                    }
                                    ColumnLayout {
                                        anchors.centerIn: parent
                                        Text { text: "Nordic Light"; font.bold: true; color: "#5e81ac" }
                                        Text { text: "Warm Light Blue"; font.pixelSize: 11; color: ThemeService.colors.textSecondary }
                                    }
                                }

                                Card {
                                    Layout.fillWidth: true
                                    implicitHeight: 80
                                    border.color: ThemeService.activePreset === "forest" ? ThemeService.colors.accent : ThemeService.colors.border
                                    border.width: ThemeService.activePreset === "forest" ? 2 : 1
                                    MouseArea {
                                        anchors.fill: parent
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: ThemeService.loadPreset("forest")
                                    }
                                    ColumnLayout {
                                        anchors.centerIn: parent
                                        Text { text: "Forest"; font.bold: true; color: "#a3be8c" }
                                        Text { text: "Earthy Dark Green"; font.pixelSize: 11; color: ThemeService.colors.textSecondary }
                                    }
                                }

                                Card {
                                    Layout.fillWidth: true
                                    implicitHeight: 80
                                    border.color: ThemeService.activePreset === "violet" ? ThemeService.colors.accent : ThemeService.colors.border
                                    border.width: ThemeService.activePreset === "violet" ? 2 : 1
                                    MouseArea {
                                        anchors.fill: parent
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: ThemeService.loadPreset("violet")
                                    }
                                    ColumnLayout {
                                        anchors.centerIn: parent
                                        Text { text: "Violet"; font.bold: true; color: "#bb9af7" }
                                        Text { text: "Dark Purple"; font.pixelSize: 11; color: ThemeService.colors.textSecondary }
                                    }
                                }
                            }

                            Item { Layout.fillHeight: true }
                        }

                        // 5. PERFORMANCE PROFILES (Lazy loaded)
                        Loader {
                            anchors.fill: parent
                            active: settingsWindow.activeCategory === "performance"
                            visible: active
                            sourceComponent: PerformancePage {}
                        }

                        // 21. BACKUP & RECOVERY (Lazy loaded)
                        Loader {
                            anchors.fill: parent
                            active: settingsWindow.activeCategory === "backup"
                            visible: active
                            sourceComponent: BackupPage {}
                        }

                        // DEFAULT / FALLBACK FOR OTHER CATEGORIES
                        ColumnLayout {
                            anchors.fill: parent
                            visible: ["overview", "features", "appearance", "performance", "backup"].indexOf(settingsWindow.activeCategory) === -1
                            spacing: 12

                            Card {
                                Layout.fillWidth: true
                                Layout.fillHeight: true

                                ColumnLayout {
                                    anchors.centerIn: parent
                                    spacing: 12

                                    Text {
                                        anchors.horizontalCenter: parent.horizontalCenter
                                        text: "\uf085"
                                        font.family: ThemeService.typography.fontFamilyMono
                                        font.pixelSize: 42
                                        color: ThemeService.colors.accent
                                    }

                                    Text {
                                        anchors.horizontalCenter: parent.horizontalCenter
                                        text: {
                                            var cat = settingsWindow.categories.find(c => c.id === settingsWindow.activeCategory);
                                            return cat ? cat.name : "Module Configuration";
                                        }
                                        font.family: ThemeService.typography.fontFamilyUi
                                        font.pixelSize: ThemeService.typography.fontSizeLarge
                                        font.bold: true
                                        color: ThemeService.colors.textPrimary
                                    }

                                    Text {
                                        anchors.horizontalCenter: parent.horizontalCenter
                                        text: "Configured via ~/.config/tejas-os/settings.json"
                                        font.family: ThemeService.typography.fontFamilyMono
                                        font.pixelSize: ThemeService.typography.fontSizeSmall
                                        color: ThemeService.colors.textSecondary
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
