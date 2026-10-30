import QtQuick
import Quickshell
import Quickshell.Io

pragma Singleton

QtObject {
    id: root

    property string activeThemeName: "Midnight"
    property bool isDark: true

    // Design Tokens: Color Palette (Default: Midnight Preset)
    property var colors: {
        "background": "#0d1117",
        "backgroundBlur": "#0d1117dd",
        "surface": "#161b22",
        "surfaceVariant": "#21262d",
        "surfaceHover": "#30363d",
        "border": "#30363d",
        "borderFocus": "#58a6ff",
        "accent": "#58a6ff",
        "accentHover": "#79b8ff",
        "accentMuted": "#1f6feb",
        "textPrimary": "#f0f6fc",
        "textSecondary": "#8b949e",
        "textMuted": "#484f58",
        "success": "#3fb950",
        "warning": "#d29922",
        "danger": "#f85149",
        "info": "#58a6ff"
    }

    // Design Tokens: Spacing & Metrics
    property var metrics: {
        "radiusSmall": 6,
        "radiusMedium": 10,
        "radiusLarge": 16,
        "borderWidth": 1,
        "barHeight": 38,
        "dockHeight": 58,
        "dockIconSize": 42
    }

    // Design Tokens: Typography
    property var typography: {
        "fontFamilyUi": "Noto Sans",
        "fontFamilyMono": "JetBrainsMono Nerd Font",
        "fontSizeSmall": 11,
        "fontSizeNormal": 13,
        "fontSizeLarge": 15,
        "fontSizeTitle": 18
    }

    // Design Tokens: Motion & Effects
    property var effects: {
        "blurEnabled": true,
        "blurRadius": 15,
        "shadowOpacity": 0.25,
        "animationDurationMs": 180
    }

    signal themeChanged(string themeName)

    // Apply a theme preset object directly
    function applyThemeObject(themeObj) {
        if (!themeObj || !themeObj.colors) return;

        if (themeObj.name) activeThemeName = themeObj.name;
        if (themeObj.type) isDark = (themeObj.type === "dark");

        var newColors = Object.assign({}, root.colors, themeObj.colors);
        var newMetrics = Object.assign({}, root.metrics, themeObj.metrics || {});
        var newTypo = Object.assign({}, root.typography, themeObj.typography || {});
        var newEffects = Object.assign({}, root.effects, themeObj.effects || {});

        root.colors = newColors;
        root.metrics = newMetrics;
        root.typography = newTypo;
        root.effects = newEffects;

        themeChanged(activeThemeName);
    }

    // Switch between presets by name
    function setPreset(name) {
        var presetMap = {
            "Midnight": "themes/midnight/theme.json",
            "Nordic Light": "themes/nordic/theme.json",
            "Forest": "themes/forest/theme.json",
            "Violet": "themes/violet/theme.json"
        };

        var filePath = presetMap[name];
        if (!filePath) {
            console.warn("[ThemeService] Unknown preset:", name);
            return;
        }

        // Read local file through XMLHttpRequest
        var xhr = new XMLHttpRequest();
        xhr.open("GET", Qt.resolvedUrl("../../" + filePath));
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200 || xhr.status === 0) {
                    try {
                        var parsed = JSON.parse(xhr.responseText);
                        applyThemeObject(parsed);
                    } catch (e) {
                        console.error("[ThemeService] Failed to parse theme JSON:", e);
                    }
                }
            }
        };
        xhr.send();
    }
}
