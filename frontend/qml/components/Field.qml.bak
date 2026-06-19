import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import "../themes"

ColumnLayout {
    id: root
    property string label: ""
    property string placeholder: ""
    property alias value: input.text
    spacing: 4
    Text { text: root.label; color: Theme.textSecondary; font.family: Theme.fontFamily; font.pixelSize: 12 }
    Rectangle {
        Layout.fillWidth: true
        implicitWidth: 240
        height: 40; radius: 9
        color: Theme.panel
        border.width: input.activeFocus ? 1 : 0
        border.color: Theme.accent
        TextField {
            id: input
            anchors.fill: parent
            anchors.leftMargin: 12; anchors.rightMargin: 12
            placeholderText: root.placeholder
            placeholderTextColor: Theme.textSecondary
            color: Theme.text
            font.family: Theme.fontFamily; font.pixelSize: 14
            verticalAlignment: Text.AlignVCenter
            background: Item {}
            horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
        }
    }
}
