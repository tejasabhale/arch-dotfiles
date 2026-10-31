import QtQuick
import Quickshell
import Quickshell.Io

pragma Singleton

QtObject {
    id: root

    // Audio State
    property int volume: 65
    property bool isMuted: false

    // Network State
    property bool wifiConnected: true
    property string wifiSsid: "Wi-Fi"

    // Battery State
    property int batteryPercentage: 85
    property bool isCharging: false

    // Power Profile
    property string powerProfile: "balanced"

    // Display Brightness (0.0 to 1.0)
    property real brightness: 0.70

    // Signals for UI notification
    signal audioChanged(int vol, bool muted)
    signal networkChanged(bool connected, string ssid)
    signal batteryChanged(int pct, bool charging)

    // Single consolidated audio process
    property var volProc: Process {
        command: ["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"]
        stdout: SplitParser {
            onRead: function(data) {
                var str = data.trim();
                root.isMuted = (str.indexOf("[MUTED]") !== -1);
                var match = str.match(/Volume:\s+([0-9\.]+)/);
                if (match && match[1]) {
                    root.volume = Math.round(parseFloat(match[1]) * 100);
                }
                root.audioChanged(root.volume, root.isMuted);
            }
        }
    }

    // Consolidated network status process
    property var netProc: Process {
        command: ["nmcli", "-t", "-f", "ACTIVE,SSID", "dev", "wifi"]
        stdout: SplitParser {
            onRead: function(data) {
                var lines = data.trim().split("\n");
                var activeFound = false;
                for (var i = 0; i < lines.length; i++) {
                    var parts = lines[i].split(":");
                    if (parts.length >= 2 && parts[0] === "yes" && parts[1]) {
                        root.wifiConnected = true;
                        root.wifiSsid = parts[1];
                        activeFound = true;
                        break;
                    }
                }
                if (!activeFound) {
                    root.wifiConnected = false;
                    root.wifiSsid = "Disconnected";
                }
                root.networkChanged(root.wifiConnected, root.wifiSsid);
            }
        }
    }

    // Consolidated battery status process (direct read without shell pipe)
    property var battProc: Process {
        command: ["cat", "/sys/class/power_supply/BAT0/capacity", "/sys/class/power_supply/BAT0/status"]
        stdout: SplitParser {
            onRead: function(data) {
                var lines = data.trim().split("\n");
                if (lines.length >= 1 && lines[0]) {
                    var cap = parseInt(lines[0]);
                    if (!isNaN(cap)) root.batteryPercentage = cap;
                }
                if (lines.length >= 2) {
                    root.isCharging = (lines[1].trim() === "Charging");
                }
                root.batteryChanged(root.batteryPercentage, root.isCharging);
            }
        }
    }

    // Refresh functions
    function refreshAudio() {
        if (!volProc.running) volProc.running = true;
    }

    function refreshNetwork() {
        if (!netProc.running) netProc.running = true;
    }

    function refreshBattery() {
        if (!battProc.running) battProc.running = true;
    }

    function refreshAll() {
        refreshAudio();
        refreshNetwork();
        refreshBattery();
    }

    // Timers: Centralized, single instance for the whole desktop shell
    // Audio: 5s interval (and refreshed immediately on volume adjustments)
    property var audioTimer: Timer {
        interval: 5000
        running: true
        repeat: true
        triggeredOnStart: true
        onTriggered: root.refreshAudio()
    }

    // Network: 15s interval
    property var netTimer: Timer {
        interval: 15000
        running: true
        repeat: true
        triggeredOnStart: true
        onTriggered: root.refreshNetwork()
    }

    // Battery: 30s interval
    property var battTimer: Timer {
        interval: 30000
        running: true
        repeat: true
        triggeredOnStart: true
        onTriggered: root.refreshBattery()
    }
}
