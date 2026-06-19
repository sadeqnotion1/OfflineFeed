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
    property bool pinned: false

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
    signal openInViewerRequested(string url)          // NEW: open this post in the offline viewer
    signal togglePinRequested(string url)

    // Right-click context menu (issue: right-click was only on chat rows).
    MessageContextMenu {
        id: msgMenu
        url: root.url
        messageTitle: root.title
        canIgnore: root.url !== ""
        pinned: root.pinned        // Item 2: drives the Pin/Unpin label
        onReadArticle: function(u, t) { root.readRequested(u, t, root.text) }
        onOpenLink: function(u) { root.openExternalRequested(u) }
        onOpenInViewer: function(u) { root.openInViewerRequested(u) }
        onForward: function(t) { root.forwardRequested(t) }
        onCopyLink: function(u) { root.copyRequested(u) }
        onIgnore: function(u) { root.ignoreRequested(u) }
        onTogglePin: function(u) { root.togglePinRequested(u) }
    }

    readonly property real maxBubbleWidth: Math.min(listWidth * 0.74, 560)
    readonly property real hPad: 10
    readonly property real vPad: 7
    readonly property real mediaWidth: root.maxBubbleWidth - hPad * 2
    readonly property real mediaHeight: Math.round(mediaWidth * 9 / 16)

    // ---- The height fix: implicitHeight follows the content Column ----
    implicitHeight: bubble.height + (lastInGroup ? 10 : 3)
    implicitWidth: listWidth
    width: listWidth
    height: implicitHeight

    Rectangle {
        id: bubble
        width: contentCol.width + hPad * 2
        height: contentCol.implicitHeight + vPad * 2
        color: root.outgoing ? Theme.outBubble : Theme.inBubble

        // Telegram tail / grouping: square the corner nearest the tail only on
        // the last bubble of a group.
        radius: Theme.radius.lg
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
            width: {
                if (imageContainer.visible) {
                    return mediaWidth;
                }
                var maxW = Math.max(
                    textBlock.implicitWidth,
                    titleText.visible ? titleText.implicitWidth : 0,
                    metaRow.implicitWidth
                );
                return Math.min(maxW, root.maxBubbleWidth - hPad * 2);
            }

            // Article image (optional) with rounded top corners and fixed aspect ratio
            // Phase 2 - Task 3 (missing thumbnail fallback): always render the
            // media slot; when a post has no thumbnail (or it fails to load) we
            // show a bundled placeholder instead of an empty/broken box. Mirrors
            // the web viewer for cross-client consistency.
            Item {
                id: imageContainer
                readonly property string placeholderSource: Qt.resolvedUrl("../assets/placeholder-thumb.svg")
                visible: true
                width: mediaWidth
                height: mediaHeight
                clip: true

                Rectangle {
                    id: imageClipContainer
                    width: parent.width
                    height: mediaHeight + Theme.bubbleRadius
                    radius: Theme.radius.lg
                    color: Qt.darker(Theme.inBubble, 1.15)
                    clip: true

                    Image {
                        id: image
                        visible: true
                        source: root.thumbnail !== "" ? root.thumbnail : imageContainer.placeholderSource
                        width: mediaWidth
                        height: mediaHeight
                        fillMode: Image.PreserveAspectCrop
                        clip: true
                        asynchronous: true
                        cache: true
                        smooth: true
                        sourceSize.width: mediaWidth
                        sourceSize.height: mediaHeight
                        // Swap to the placeholder if the real thumbnail 404s / fails to load.
                        onStatusChanged: if (status === Image.Error) source = imageContainer.placeholderSource
                    }
                }
            }

            // Sender / source name (Telegram colors the name per peer)
            Text {
                id: titleText
                visible: root.title !== ""
                text: root.title
                width: parent.width
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
                width: parent.width
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
                width: parent.width
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

                // NEW: open this single post in the offline viewer (browser)
                Icon {
                    visible: root.url !== ""
                    name: "browser"
                    size: 14
                    color: Theme.textSecondary
                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: root.openInViewerRequested(root.url)
                        hoverEnabled: true
                    }
                }

                Icon {
                    visible: root.url !== ""
                    name: bridge.currentChannelId === "SavedMessages" ? "trash" : "forward"
                    size: 14
                    color: bridge.currentChannelId === "SavedMessages" ? "#ec3942" : Theme.textSecondary
                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            if (bridge.currentChannelId === "SavedMessages") {
                                bridge.unsaveArticle(root.url, root.title)
                            } else {
                                root.forwardRequested(root.title)
                            }
                        }
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
