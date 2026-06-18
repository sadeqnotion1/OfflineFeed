import QtQuick
import "../themes"

Rectangle {
    id: root
    property string text: ""
    property bool outline: false
    property bool danger: false
    signal clicked()
    implicitHeight: 40
    implicitWidth: lbl.implicitWidth + 36
    radius: 20
    color: outline ? "transparent" : (danger ? "#ec3942" : Theme.accent)
    border.width: outline ? 1 : 0
    border.color: danger ? "#ec3942" : Theme.divider
    Text {
        id: lbl
        anchors.centerIn: parent
        text: root.text
        color: outline ? (danger ? "#ec3942" : Theme.text) : Theme.accentText
        font.family: Theme.fontFamily; font.pixelSize: 14; font.bold: true
    }
    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: root.clicked()
        onEntered: root.opacity = 0.88
        onExited: root.opacity = 1.0
    }
    Behavior on opacity { NumberAnimation { duration: Theme.animFast } }
}
