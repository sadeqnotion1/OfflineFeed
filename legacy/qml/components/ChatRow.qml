import QtQuick
import QtQuick.Layouts
import "../themes"

// A single row in the chat list (one feed channel / Saved / Logs).
Item {
    id: row
    property string channelId: ""
    property string name: ""
    property string lastMessage: ""
    property string time: ""
    property int unread: 0
    property string avatarPath: ""
    property bool selected: false
    property bool muted: false
    property bool pinned: false

    signal clicked()
    signal rightClicked(real gx, real gy)

    width: ListView.view ? ListView.view.width : 320
    height: Theme.rowHeight

    Rectangle {
        anchors.fill: parent
        color: row.selected ? Theme.selection : (mouse.containsMouse ? Theme.hover : "transparent")
        Behavior on color { ColorAnimation { duration: Theme.animFast } }
    }

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 12
        anchors.rightMargin: 12
        spacing: 11
        LayoutMirroring.enabled: Theme.rtl

        Avatar {
            name: row.name
            avatarPath: row.avatarPath
            seed: row.channelId
            size: Theme.avatarSize
            Layout.alignment: Qt.AlignVCenter
        }

        ColumnLayout {
            Layout.fillWidth: true
            spacing: 3

            RowLayout {
                Layout.fillWidth: true
                spacing: 6
                Icon {
                    visible: row.pinned
                    name: "pin"; size: 13; color: Theme.textSecondary
                }
                Text {
                    Layout.fillWidth: true
                    text: row.name
                    color: row.selected ? Theme.accentText : Theme.text
                    font.family: Theme.fontFamily
                    font.pixelSize: 15
                    font.bold: true
                    elide: Text.ElideRight
                    horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
                }
                Text {
                    text: row.time
                    color: row.selected ? Theme.accentText : Theme.textSecondary
                    font.family: Theme.fontFamily
                    font.pixelSize: 12
                }
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 6
                Text {
                    Layout.fillWidth: true
                    text: row.lastMessage
                    color: row.selected ? Qt.rgba(1,1,1,0.85) : Theme.textSecondary
                    font.family: Theme.fontFamily
                    font.pixelSize: 14
                    elide: Text.ElideRight
                    maximumLineCount: 1
                    horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
                }
                Icon {
                    visible: row.muted
                    name: "mute"; size: 14; color: Theme.textSecondary
                }
                // Unread badge
                Rectangle {
                    visible: row.unread > 0
                    radius: height / 2
                    height: 20
                    width: Math.max(20, badge.implicitWidth + 12)
                    color: row.muted ? Theme.badgeMuted : Theme.badge
                    Text {
                        id: badge
                        anchors.centerIn: parent
                        text: row.unread
                        color: "#ffffff"
                        font.family: Theme.fontFamily
                        font.pixelSize: 12
                        font.bold: true
                    }
                }
            }
        }
    }

    // Bottom divider
    Rectangle {
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.leftMargin: 70
        height: 1
        color: Theme.divider
        opacity: 0.5
        visible: !row.selected
    }

    MouseArea {
        id: mouse
        anchors.fill: parent
        hoverEnabled: true
        acceptedButtons: Qt.LeftButton | Qt.RightButton
        cursorShape: Qt.PointingHandCursor
        onClicked: function(e) {
            if (e.button === Qt.RightButton) {
                var g = mapToGlobalPoint(e.x, e.y);
                row.rightClicked(e.x, e.y);
            } else {
                row.clicked();
            }
        }
        function mapToGlobalPoint(x, y) { return Qt.point(x, y) }
    }
}
