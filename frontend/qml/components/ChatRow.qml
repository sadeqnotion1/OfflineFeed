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
    property int matchCount: 0
    property string avatarPath: ""
    property bool selected: false
    property bool muted: false
    property bool pinned: false

    signal clicked()
    signal rightClicked(real gx, real gy)

    width: ListView.view ? ListView.view.width : 320
    height: Theme.rowHeight

    // Row-state background: subtle accent washes layered over the panel.
    // Precedence (selected > hover > default) is encoded in the conditional;
    // colour changes are eased so states fade in/out instead of snapping.
    Rectangle {
        anchors.fill: parent
        color: row.selected ? Theme.selectionFill
                            : (mouse.containsMouse ? Theme.hoverFill : "transparent")
        Behavior on color { ColorAnimation { duration: Theme.animFast; easing.type: Theme.easing } }

        // Accent left-edge indicator on the active row (flips side for RTL).
        Rectangle {
            width: 3
            color: Theme.accent
            opacity: row.selected ? 1 : 0
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.left: Theme.rtl ? undefined : parent.left
            anchors.right: Theme.rtl ? parent.right : undefined
            Behavior on opacity { NumberAnimation { duration: Theme.animFast; easing.type: Theme.easing } }
        }
    }

    // Keyboard-focus ring — visible only while the list has active focus and
    // this is the current item, so keyboard navigation is always visible.
    Rectangle {
        anchors.fill: parent
        color: "transparent"
        border.width: 2
        border.color: Theme.accentBorder
        visible: row.ListView.isCurrentItem
                 && row.ListView.view !== null
                 && row.ListView.view.activeFocus
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
                    id: nameText
                    Layout.fillWidth: true
                    text: {
                        var n = row.name;
                        if (n.endsWith(" (X)")) return n.substring(0, n.length - 4);
                        if (n.endsWith("(X)")) return n.substring(0, n.length - 3);
                        return n;
                    }
                    color: Theme.text
                    font.family: Theme.fontFamily
                    font.pixelSize: 15
                    font.bold: true
                    elide: Text.ElideRight
                    horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
                }
                Icon {
                    visible: row.name.endsWith("(X)") || row.name.endsWith(" (X)")
                    name: "brand-x"
                    size: 13
                    color: Theme.textSecondary
                    Layout.alignment: Qt.AlignVCenter
                }
                Text {
                    text: row.time
                    color: Theme.textSecondary
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
                    color: Theme.textSecondary
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
                // Match count or Unread badge
                Badge {
                    count: row.matchCount > 0 ? row.matchCount : row.unread
                    muted: row.matchCount > 0 ? false : row.muted
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
