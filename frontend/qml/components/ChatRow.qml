import QtQuick
import QtQuick.Layouts
import "../themes"

// A single row in the chat list (one feed channel / Saved / Logs).
//
// 09_spacing_density: every margin / gap / avatar size here is now driven by
// the Theme spacing scale (Theme.space.*) and the list-row density tokens
// (Theme.row*). There are NO stray literal margins or spacings left in this
// delegate. Colors and radii are untouched.
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

    width: ListView.view ? ListView.view.width : Theme.chatListWidth
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
        anchors.leftMargin: Theme.rowPadding      // leading inset (12)
        anchors.rightMargin: Theme.rowPadding     // trailing inset (12)
        spacing: Theme.rowGap                     // avatar <-> text gap (12)
        LayoutMirroring.enabled: Theme.rtl

        Avatar {
            name: row.name
            avatarPath: row.avatarPath
            seed: row.channelId
            size: Theme.rowAvatarSize             // list-row avatar (54)
            Layout.alignment: Qt.AlignVCenter
        }

        ColumnLayout {
            Layout.fillWidth: true
            Layout.alignment: Qt.AlignVCenter
            spacing: Theme.rowLineGap             // name <-> preview vertical gap (4)

            // Top line: name (left, grows) + timestamp pinned top-right.
            RowLayout {
                Layout.fillWidth: true
                spacing: Theme.rowInlineGap       // inline gap (8)
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

            // Bottom line: preview (left, grows) + mute/badge pinned bottom-right.
            RowLayout {
                Layout.fillWidth: true
                spacing: Theme.rowInlineGap       // inline gap (8)
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

    // Bottom divider — starts under the text block (aligned to the text inset)
    // so it never runs under the avatar.
    Rectangle {
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.leftMargin: Theme.rowTextInset    // = rowPadding + rowAvatarSize + rowGap (78)
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
