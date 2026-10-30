import QtQuick
import QtQuick.Layouts
import "../services"

Rectangle {
    id: fieldRoot

    property alias text: textInput.text
    property string placeholder: "Search or enter command..."
    property string leadingIcon: ""
    property bool readOnly: false
    property int customRadius: ThemeService.metrics.radiusSmall

    signal accepted()
    signal textChanged(string newText)

    implicitWidth: 260
    implicitHeight: 36
    radius: customRadius

    color: ThemeService.colors.surface
    border.color: textInput.activeFocus ? ThemeService.colors.borderFocus : ThemeService.colors.border
    border.width: ThemeService.metrics.borderWidth

    Behavior on border.color {
        ColorAnimation { duration: ThemeService.effects.animationDurationMs }
    }

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 10
        anchors.rightMargin: 10
        spacing: 8

        Text {
            visible: fieldRoot.leadingIcon !== ""
            text: fieldRoot.leadingIcon
            font.family: ThemeService.typography.fontFamilyMono
            font.pixelSize: ThemeService.typography.fontSizeNormal
            color: ThemeService.colors.textMuted
            Layout.alignment: Qt.AlignVCenter
        }

        TextInput {
            id: textInput
            Layout.fillWidth: true
            Layout.alignment: Qt.AlignVCenter
            readOnly: fieldRoot.readOnly
            color: ThemeService.colors.textPrimary
            font.family: ThemeService.typography.fontFamilyUi
            font.pixelSize: ThemeService.typography.fontSizeNormal
            clip: true

            Text {
                text: fieldRoot.placeholder
                color: ThemeService.colors.textMuted
                font: textInput.font
                visible: !textInput.text && !textInput.activeFocus
            }

            onAccepted: fieldRoot.accepted()
            onTextChanged: fieldRoot.textChanged(textInput.text)
        }

        Text {
            visible: textInput.text.length > 0
            text: "󰅖"
            font.family: ThemeService.typography.fontFamilyMono
            font.pixelSize: ThemeService.typography.fontSizeSmall
            color: clearMouse.containsMouse ? ThemeService.colors.textPrimary : ThemeService.colors.textMuted
            Layout.alignment: Qt.AlignVCenter

            MouseArea {
                id: clearMouse
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                onClicked: {
                    textInput.text = "";
                    textInput.forceActiveFocus();
                }
            }
        }
    }
}
