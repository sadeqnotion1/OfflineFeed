import QtQuick
import "../themes"

// Small action button (primary accent fill or neutral outline) used inside
// detail pages (Save, Open System Logs, etc.).
Rectangle {
    id: btn

    property string text: ""
    property bool primary: true

    signal clicked()

    implicitWidth: Math.max(120, t.implicitWidth + 32)
    implicitHeight: 38
    radius: Theme.radius.sm
    color: primary ? (mouse.containsMouse ? Theme.accentHover : Theme.accent)
                   : (mouse.containsMouse ? Theme.hover : Theme.panel)
    border.width: primary ? 0 : 1
    border.color: Theme.divider
    Behavior on color { ColorAnimation { duration: Theme.animFast } }

    Text {
        id: t
        anchors.centerIn: parent
        text: btn.text
        color: btn.primary ? Theme.accentText : Theme.text
        font.family: Theme.fontFamily
        font.pixelSize: 14
        font.bold: true
    }

    MouseArea {
        id: mouse
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: btn.clicked()
    }
}
