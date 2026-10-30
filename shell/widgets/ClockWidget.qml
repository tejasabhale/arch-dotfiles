import QtQuick
import QtQuick.Layouts
import "../services"

Rectangle {
    id: clockRoot

    signal clicked()

    property string timeStr: ""
    property string dateStr: ""

    implicitWidth: clockLayout.implicitWidth + 16
    implicitHeight: 28
    radius: ThemeService.metrics.radiusSmall
    color: mouseArea.containsMouse ? ThemeService.colors.surfaceHover : ThemeService.colors.surfaceVariant
    border.color: ThemeService.colors.border
    border.width: ThemeService.metrics.borderWidth

    function updateTime() {
        var d = new Date();
        var hours = String(d.getHours()).padStart(2, '0');
        var mins = String(d.getMinutes()).padStart(2, '0');
        clockRoot.timeStr = hours + ":" + mins;

        var days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
        var months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
        clockRoot.dateStr = days[d.getDay()] + ", " + months[d.getMonth()] + " " + d.getDate();
    }

    Component.onCompleted: updateTime()

    Timer {
        interval: 1000
        running: true
        repeat: true
        onTriggered: clockRoot.updateTime()
    }

    RowLayout {
        id: clockLayout
        anchors.centerIn: parent
        spacing: 6

        Text {
            text: "󰥔"
            font.family: ThemeService.typography.fontFamilyMono
            font.pixelSize: ThemeService.typography.fontSizeNormal
            color: ThemeService.colors.accent
        }

        Text {
            text: clockRoot.timeStr
            font.family: ThemeService.typography.fontFamilyMono
            font.pixelSize: ThemeService.typography.fontSizeSmall
            font.weight: Font.Bold
            color: ThemeService.colors.textPrimary
        }

        Text {
            text: "•"
            font.pixelSize: ThemeService.typography.fontSizeSmall
            color: ThemeService.colors.textMuted
        }

        Text {
            text: clockRoot.dateStr
            font.family: ThemeService.typography.fontFamilyUi
            font.pixelSize: ThemeService.typography.fontSizeSmall
            color: ThemeService.colors.textSecondary
        }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: clockRoot.clicked()
    }
}
