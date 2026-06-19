import QtQuick
import QtQuick.Layouts
import "../themes"

// Detail-page header with a back affordance + title, matching the chat header
// height/styling. The back button pops the StackView passed in via `stack`.
Rectangle {
    id: hd

    property string title: ""
    property var stack: null      // the StackView this page lives in

    height: Theme.headerHeight
    color: Theme.panel

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 6
        anchors.rightMargin: 16
        spacing: 6
        LayoutMirroring.enabled: Theme.rtl

        Rectangle {
            Layout.preferredWidth: 40
            Layout.preferredHeight: 40
            Layout.alignment: Qt.AlignVCenter
            radius: 8
            color: backMouse.containsMouse ? Theme.hover : "transparent"
            Behavior on color { ColorAnimation { duration: Theme.animFast } }

            Icon {
                anchors.centerIn: parent
                name: "back"
                size: 22
                rotation: Theme.rtl ? 180 : 0
                color: Theme.text
            }

            MouseArea {
                id: backMouse
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                onClicked: { if (hd.stack) hd.stack.pop() }
            }
        }

        Text {
            Layout.fillWidth: true
            text: hd.title
            color: Theme.text
            font.family: Theme.fontFamily
            font.pixelSize: 18
            font.bold: true
            elide: Text.ElideRight
            horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
        }
    }

    Rectangle {
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        height: 1
        color: Theme.divider
    }
}
