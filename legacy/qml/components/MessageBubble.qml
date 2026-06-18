import QtQuick
import QtQuick.Layouts
import "../themes"

// A single message/article bubble.
//
// FIX (known issue #1 — "smooshed" messages): the delegate's implicitHeight is
// derived from the inner Column's implicitHeight + vertical padding, so the
// ListView always allocates the correct height regardless of image/text size.
Item {
    id: root

    // model roles (from MessageModel in bridge.py)
    property string title: ""
    property string text: ""
    property string url: ""
    property string thumbnail: ""
    property string time: ""
    property bool outgoing: false
    property bool read: true
    property int views: 0
    property var reactions: []
    property string source: ""
    property string topic: ""

    // grouping flags (set by ChatView delegate)
    property bool firstInGroup: true
    property bool lastInGroup: true
    property real listWidth: 600

    signal readRequested(string url, string title, string fallback)   // open offline reader
    signal openExternalRequested(string url)          // open original in browser
    signal forwardRequested(string title)             // forward to Saved Messages
    signal copyRequested(string url)                  // copy link to clipboard
    signal ignoreRequested(string url)                // hide this post
    signal reactedAt(string url, int index)

    // Right-click context menu (issue: right-click was only on chat rows).
    MessageContextMenu {
        id: msgMenu
        url: root.url
        messageTitle: root.title
        canIgnore: root.url !== ""
        onReadArticle: function(u, t) { root.readRequested(u, t, root.text) }
        onOpenLink: function(u) { root.openExternalRequested(u) }
        onForward: function(t) { root.forwardRequested(t) }
        onCopyLink: function(u) { root.copyRequested(u) }
        onIgnore: function(u) { root.ignoreRequested(u) }
    }

    readonly property real maxBubbleWidth: Math.min(listWidth * 0.74, 560)
    readonly property real hPad: 10
    readonly property real vPad: 7

    // ---- The height fix: implicitHeight follows the content Column ----
    implicitHeight: bubble.height + (lastInGroup ? 10 : 3)
    implicitWidth: listWidth
    width: listWidth
    height: implicitHeight

    Rectangle {
        id: bubble
        width: contentCol.implicitWidth + hPad * 2
        height: contentCol.implicitHeight + vPad * 2
        color: root.outgoing ? Theme.outBubble : Theme.inBubble

        // Telegram tail / grouping: square the corner nearest the tail only on
        // the last bubble of a group.
        radius: Theme.bubbleRadius
        anchors.right: root.outgoing ? parent.right : undefined
        anchors.left: root.outgoing ? undefined : parent.left
        anchors.rightMargin: root.outgoing ? 14 : 0
        anchors.leftMargin: root.outgoing ? 0 : 14

        // Tail corner squaring
        Rectangle {
            visible: root.lastInGroup
            width: Theme.bubbleRadius
            height: Theme.bubbleRadius
            color: bubble.color
            anchors.bottom: parent.bottom
            anchors.left: root.outgoing ? undefined : parent.left
            anchors.right: root.outgoing ? parent.right : undefined
        }

        Column {
            id: contentCol
            x: hPad
            y: vPad
            spacing: 4
            width: Math.max(textBlock.implicitWidth,
                            titleText.visible ? titleText.implicitWidth : 0,
                            image.visible ? image.width : 0,
                            metaRow.implicitWidth)
            // clamp to a sane max width
            onWidthChanged: if (width > root.maxBubbleWidth - hPad * 2)
                                width = root.maxBubbleWidth - hPad * 2

            // Article image (optional)
            Image {
                id: image
                visible: root.thumbnail !== ""
                source: root.thumbnail
                width: Math.min(root.maxBubbleWidth - hPad * 2, 360)
                height: status === Image.Ready ? width * (sourceSize.height / Math.max(1, sourceSize.width)) : (visible ? 140 : 0)
                fillMode: Image.PreserveAspectCrop
                clip: true
                smooth: true
                asynchronous: true
                cache: true
            }

            // Sender / source name (Telegram colors the name per peer)
            Text {
                id: titleText
                visible: root.title !== ""
                text: root.title
                width: Math.min(implicitWidth, root.maxBubbleWidth - hPad * 2)
                wrapMode: Text.WordWrap
                color: Theme.text
                font.family: Theme.fontFamily
                font.pixelSize: 15
                font.bold: true
                horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
                LayoutMirroring.enabled: Theme.rtl
            }

            // Body text
            Text {
                id: textBlock
                visible: root.text !== ""
                text: root.text
                width: Math.min(implicitWidth, root.maxBubbleWidth - hPad * 2)
                wrapMode: Text.WordWrap
                textFormat: Text.StyledText
                color: Theme.text
                font.family: Theme.fontFamily
                font.pixelSize: 14
                lineHeight: 1.15
                horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
                LayoutMirroring.enabled: Theme.rtl
                onLinkActivated: function(link) { root.openExternalRequested(link) }
            }

            // Meta row: topic tag, views, time, double-check ticks, forward
            RowLayout {
                id: metaRow
                spacing: 8
                LayoutMirroring.enabled: Theme.rtl

                Text {
                    visible: root.topic !== ""
                    text: "#" + root.topic
                    color: Theme.link
                    font.family: Theme.fontFamily
                    font.pixelSize: 12
                }

                Item { Layout.fillWidth: true }

                Icon {
                    visible: root.url !== ""
                    name: "forward"
                    size: 14
                    color: Theme.textSecondary
                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: root.forwardRequested(root.title)
                        hoverEnabled: true
                    }
                }

                Icon {
                    visible: root.views > 0
                    name: "eye"
                    size: 14
                    color: Theme.textSecondary
                }
                Text {
                    visible: root.views > 0
                    text: root.views >= 1000 ? (root.views / 1000).toFixed(1) + "K" : root.views
                    color: Theme.textSecondary
                    font.family: Theme.fontFamily
                    font.pixelSize: 12
                }

                Text {
                    text: root.time
                    color: Theme.textSecondary
                    font.family: Theme.fontFamily
                    font.pixelSize: 12
                }

                Icon {
                    visible: root.outgoing
                    name: root.read ? "check-double" : "check"
                    size: 15
                    color: root.read ? Theme.tick : Theme.textSecondary
                }
            }
        }

        // Left-click body opens the offline reader; right-click opens the menu.
        MouseArea {
            anchors.fill: parent
            acceptedButtons: Qt.LeftButton | Qt.RightButton
            cursorShape: root.url !== "" ? Qt.PointingHandCursor : Qt.ArrowCursor
            z: -1
            onClicked: function(mouse) {
                if (root.url === "")
                    return
                if (mouse.button === Qt.RightButton)
                    msgMenu.popup()
                else
                    root.readRequested(root.url, root.title, root.text)
            }
        }
    }
}
