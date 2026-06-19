import QtQuick
import QtQuick.Layouts
import "../themes"

// A label (+ optional description) with a custom Theme-driven switch.
// No hardcoded colors; fully RTL-safe.
Rectangle {
    id: ctl

    property string label: ""
    property string description: ""
    property bool checked: false

    signal toggled(bool value)

    width: parent ? parent.width : 400
    height: description !== "" ? 64 : 52
    color: mouse.containsMouse ? Theme.hover : Theme.panel
    Behavior on color { ColorAnimation { duration: Theme.animFast } }

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 16
        anchors.rightMargin: 16
        spacing: 12
        LayoutMirroring.enabled: Theme.rtl

        ColumnLayout {
            Layout.fillWidth: true
            spacing: 2
            Text {
                Layout.fillWidth: true
                text: ctl.label
                color: Theme.text
                font.family: Theme.fontFamily
                font.pixelSize: 15
                horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
            }
            Text {
                visible: ctl.description !== ""
                Layout.fillWidth: true
                text: ctl.description
                color: Theme.textSecondary
                font.family: Theme.fontFamily
                font.pixelSize: 12
                wrapMode: Text.WordWrap
                horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
            }
        }

        Rectangle {
            id: track
            Layout.alignment: Qt.AlignVCenter
            width: 42
            height: 24
            radius: 12
            color: ctl.checked ? Theme.accent : Theme.divider
            Behavior on color { ColorAnimation { duration: Theme.animFast } }

            Rectangle {
                width: 18
                height: 18
                radius: 9
                color: Theme.accentText
                y: 3
                // Knob slides to the trailing edge when checked, mirrored under RTL.
                x: (ctl.checked !== Theme.rtl) ? track.width - width - 3 : 3
                Behavior on x { NumberAnimation { duration: Theme.animFast; easing.type: Theme.easing } }
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

    MouseArea {
        id: mouse
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: { ctl.checked = !ctl.checked; ctl.toggled(ctl.checked) }
    }
}
