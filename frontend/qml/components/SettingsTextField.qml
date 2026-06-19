import QtQuick
import QtQuick.Controls
import "../themes"

// Labelled text field (optionally a password field) styled with Theme tokens.
Rectangle {
    id: ctl

    property string label: ""
    property string placeholder: ""
    property alias text: field.text
    property bool password: false

    signal edited(string value)

    width: parent ? parent.width : 400
    height: 72
    color: Theme.panel

    Column {
        anchors.fill: parent
        anchors.leftMargin: 16
        anchors.rightMargin: 16
        anchors.topMargin: 10
        spacing: 6

        Text {
            width: parent.width
            text: ctl.label
            color: Theme.textSecondary
            font.family: Theme.fontFamily
            font.pixelSize: 12
            horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
        }

        Rectangle {
            width: parent.width
            height: 30
            radius: Theme.radius.md
            color: "transparent"
            border.width: 1
            border.color: field.activeFocus ? Theme.accent : Theme.divider
            Behavior on border.color { ColorAnimation { duration: Theme.animFast } }

            TextField {
                id: field
                anchors.fill: parent
                anchors.leftMargin: 8
                anchors.rightMargin: 8
                verticalAlignment: TextInput.AlignVCenter
                echoMode: ctl.password ? TextInput.Password : TextInput.Normal
                placeholderText: ctl.placeholder
                color: Theme.text
                placeholderTextColor: Theme.textSecondary
                selectionColor: Theme.accent
                selectedTextColor: Theme.accentText
                font.family: Theme.fontFamily
                font.pixelSize: 14
                background: null
                LayoutMirroring.enabled: Theme.rtl
                horizontalAlignment: Theme.rtl ? TextInput.AlignRight : TextInput.AlignLeft
                onEditingFinished: ctl.edited(text)
            }
        }
    }

    Rectangle {
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        height: 1
        color: Theme.divider
        opacity: 0.4
    }
}
