import QtQuick
import QtQuick.Layouts
import "../themes"

// A single message/article bubble.
//
// FIX (known issue #1 — "smooshed" messages): the delegate's implicitHeight is
// derived from the inner Column's implicitHeight + vertical padding, so the
// ListView always allocates the correct height regardless of image/text size.
//
// ADD (06_image_overlay_scrim — media legibility): an opt-in OVERLAY mode draws
// the title + meta ON the image, lifted above a bottom-anchored gradient scrim
// so they stay readable on bright images (Telegram-style). The original layout
// (caption in a solid bubble BELOW the image) is kept as the default so nothing
// changes unless overlay mode is explicitly switched on. Toggle globally with
// Theme.postOverlayMode, or per-bubble with `overlayMode` below.
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

    // ADD (06_image_overlay_scrim): caption layout mode for this bubble.
    //   "below"   -> caption under the image (original, default, non-breaking)
    //   "overlay" -> title + meta over the image, above a gradient scrim
    // Defaults to the app-wide Theme.postOverlayMode so one flag flips them all.
    property string overlayMode: Theme.postOverlayMode

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

    // ADD (06_image_overlay_scrim): overlay is active only when explicitly
    // requested AND there is a title to place on the image; otherwise we fall
    // back to the safe below-image caption so a post never loses its title.
    readonly property bool overlayActive: overlayMode === "overlay" && root.title !== ""
    // FIX (twitter/telegram duplicate text): the backend uses the
    // first line of the body as the post `title`, so for tweets the
    // title equals (or is a prefix of) the body and the post would
    // render twice. Detect that and suppress the separate title; the
    // full text still shows once in the body below.
    function _plain(s) {
        return String(s).replace(/<[^>]*>/g, "").replace(/\s+/g, " ").trim().toLowerCase()
    }
    readonly property bool titleRedundant: {
        if (root.title === "" || root.text === "")
            return false
        var t = _plain(root.title).replace(/(\.\.\.|…)$/, "").trim()
        if (t === "")
            return false
        var b = _plain(root.text)
        return b === t || b.indexOf(t) === 0
    }


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

                // ===== 06_image_overlay_scrim — legibility layer (overlay mode) =====
                // STEP 1+3: bottom-anchored gradient scrim, clipped to the image.
                //   * It is a child of imageContainer (clip:true, mediaWidth x
                //     mediaHeight), so it is CLIPPED to the image rect; the
                //     rounded TOP corners come from imageClipContainer beneath,
                //     and the bottom meets the bubble exactly as before.
                //   * Gradient runs transparent (top) -> rgba(0,0,0,0.7)
                //     (bottom). It is sized to the caption band only, so ONLY the
                //     text region is darkened — never the whole image.
                // Z-ORDER: image (z 0, in imageClipContainer) < scrim (z 1) <
                //          caption (z 2).
                Rectangle {
                    id: scrim
                    visible: root.overlayActive
                    z: 1
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.bottom: parent.bottom
                    // Cover the caption band + a little breathing room, but never
                    // more than the image height.
                    height: Math.min(parent.height, overlayCaption.implicitHeight + 36)
                    gradient: Gradient {
                        // Vertical by default (top -> bottom). The dark floor is
                        // reached early (0.30) so the WHOLE caption band sits in
                        // the >=0.55 alpha zone -> AA contrast even for 2 lines.
                        GradientStop { position: 0.0;  color: "transparent" }
                        GradientStop { position: 0.30; color: Theme.scrimMid }   // rgba(0,0,0,0.55)
                        GradientStop { position: 1.0;  color: Theme.scrim }      // rgba(0,0,0,0.78)
                    }
                }

                // STEP 2: title (14.5px≈15, weight 700) + meta (11px, muted)
                // placed ABOVE the scrim (z 2) and anchored to the bottom band.
                Column {
                    id: overlayCaption
                    visible: root.overlayActive
                    z: 2
                    spacing: 2
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.bottom: parent.bottom
                    anchors.leftMargin: 12
                    anchors.rightMargin: 12
                    anchors.bottomMargin: 10
                    LayoutMirroring.enabled: Theme.rtl

                    Text {
                        id: overlayTitle
                        width: parent.width
                        visible: root.title !== "" && !root.titleRedundant
                        text: root.title
                        color: Theme.onMedia                 // always-light, reuse theme token
                        font.family: Theme.fontFamily
                        // QML font.pixelSize is integer; 14.5px spec ≈ 15px.
                        font.pixelSize: 15
                        font.weight: Font.Bold               // weight 700
                        // Belt-and-suspenders legibility: a subtle dark outline
                        // keeps text readable even on the lighter top of the scrim.
                        style: Text.Outline
                        styleColor: Qt.rgba(0, 0, 0, 0.55)
                        wrapMode: Text.WordWrap
                        maximumLineCount: 2
                        elide: Text.ElideRight
                        horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
                    }

                    Text {
                        id: overlayMeta
                        width: parent.width
                        visible: text !== ""
                        // topic • views • time, condensed to one muted line.
                        text: {
                            var parts = [];
                            if (root.topic !== "")
                                parts.push("#" + root.topic);
                            if (root.views > 0)
                                parts.push((root.views >= 1000
                                    ? (root.views / 1000).toFixed(1) + "K"
                                    : root.views) + " views");
                            if (root.time !== "")
                                parts.push(root.time);
                            return parts.join("  •  ");
                        }
                        color: Theme.onMediaMuted            // muted but legible on scrim
                        font.family: Theme.fontFamily
                        font.pixelSize: 11
                        style: Text.Outline
                        styleColor: Qt.rgba(0, 0, 0, 0.55)
                        elide: Text.ElideRight
                        horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
                    }
                }
            }

            // Sender / source name (Telegram colors the name per peer)
            // In overlay mode this is rendered ON the image instead (see above),
            // so hide the below-image copy to avoid duplication.
            Text {
                id: titleText
                visible: root.title !== "" && !root.overlayActive && !root.titleRedundant
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

            // Body text (kept below the image in both modes)
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

            // Meta row: topic tag, views, time, double-check ticks, forward.
            // In overlay mode the textual meta (topic / views / time) is shown
            // ON the image; the interactive action icons stay here so nothing is
            // lost. The row hides entirely only when it would be empty.
            RowLayout {
                id: metaRow
                width: parent.width
                spacing: 8
                visible: !root.overlayActive || root.url !== "" || root.outgoing
                LayoutMirroring.enabled: Theme.rtl

                Text {
                    visible: root.topic !== "" && !root.overlayActive
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
                    visible: root.views > 0 && !root.overlayActive
                    name: "eye"
                    size: 14
                    color: Theme.textSecondary
                }
                Text {
                    visible: root.views > 0 && !root.overlayActive
                    text: root.views >= 1000 ? (root.views / 1000).toFixed(1) + "K" : root.views
                    color: Theme.textSecondary
                    font.family: Theme.fontFamily
                    font.pixelSize: 12
                }

                Text {
                    visible: !root.overlayActive
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
