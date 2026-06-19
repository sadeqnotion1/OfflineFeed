import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt5Compat.GraphicalEffects
import "../themes"

// Right pane: chat header, pinned-message bar, wallpaper, message list with
// day-separator pills, and a bottom action bar (forward channel to Telegram).
Rectangle {
    id: root
    color: Theme.bg

    property string channelId: ""
    property string channelName: ""
    property bool searchActive: false
    onChannelIdChanged: { searchActive = false; if (typeof chSearch !== 'undefined') chSearch.text = "" }
    signal infoRequested()
    signal forwardChannelRequested(string channelId)
    signal readArticleRequested(string url, string title, string fallback)  // -> opens reader overlay

    // Item 2: pinned posts for the open channel (kept in sync with the bridge).
    property var pinnedPosts: []
    function refreshPinned() { root.pinnedPosts = bridge.currentPinnedPosts() }
    Connections {
        target: bridge
        function onPinnedPostsChanged() { root.refreshPinned() }
        function onCurrentChannelIdChanged() { root.refreshPinned() }
    }
    Component.onCompleted: root.refreshPinned()

    // ---- Chat wallpaper ----
    Rectangle {
        anchors.fill: parent
        color: Theme.wallpaper
        visible: Theme.wallpaperMode !== "none"
        Image {
            anchors.fill: parent
            visible: Theme.wallpaperMode === "pattern"
            fillMode: Image.Tile
            opacity: 0.05
            source: Qt.resolvedUrl("../assets/logo.svg")
            sourceSize.width: 130
            sourceSize.height: 130
        }
        // Item 8: user-selected custom wallpaper image.
        Image {
            anchors.fill: parent
            visible: Theme.wallpaperMode === "image" && Theme.wallpaperImage !== ""
            source: Theme.wallpaperImage
            fillMode: Image.PreserveAspectCrop
            asynchronous: true
            cache: true
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // ---- Header ----
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: Theme.headerHeight
            color: Theme.panel
            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 14
                anchors.rightMargin: 14
                spacing: 0                       // RULE 1: no uniform gaps
                LayoutMirroring.enabled: Theme.rtl

                Avatar {
                    // Item 5: reuse the same avatar resolution as the list row
                    // (real channel image when available; gradient fallback).
                    name: root.channelName
                    seed: root.channelId
                    avatarPath: bridge.currentChannelAvatar
                    size: 40
                    Layout.alignment: Qt.AlignVCenter
                }

                ColumnLayout {
                    Layout.fillWidth: true       // RULE 2: the ONLY stretchy element
                    Layout.leftMargin: 10        // the single avatar -> name gap
                    Layout.alignment: Qt.AlignVCenter
                    spacing: 0
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 6
                        Text {
                            id: headerTitleText
                            Layout.fillWidth: true
                            text: {
                                var n = root.channelName;
                                if (n.endsWith(" (X)")) return n.substring(0, n.length - 4);
                                if (n.endsWith("(X)")) return n.substring(0, n.length - 3);
                                return n !== "" ? n : qsTr("OfflineFeed");
                            }
                            color: Theme.text
                            font.family: Theme.fontFamily
                            font.pixelSize: 16
                            font.bold: true
                            elide: Text.ElideRight
                        }
                        Icon {
                            visible: root.channelName.endsWith("(X)") || root.channelName.endsWith(" (X)")
                            name: "brand-x"
                            size: 15
                            color: Theme.textSecondary
                            Layout.alignment: Qt.AlignVCenter
                        }
                    }
                    Text {
                        // Telegram shows a live status line under the title.
                        // Use the real post count when a channel is open, else
                        // fall back to the generic "news channel" label.
                        text: messages.count > 0 ? qsTr("%1 posts").arg(messages.count)
                                                 : qsTr("news channel")
                        color: Theme.textSecondary
                        font.family: Theme.fontFamily
                        font.pixelSize: 13
                    }
                }

                // Tight right-side icon cluster (preserve real names + handlers)
                RowLayout {
                    Layout.alignment: Qt.AlignVCenter
                    spacing: 6                    // small, consistent inter-icon gap
                    LayoutMirroring.enabled: Theme.rtl

                    Icon {
                        name: "refresh"; size: 19
                        color: bridge.newsRefreshing ? Theme.accent : Theme.textSecondary
                        // Spin while a refresh is in flight (loading state).
                        RotationAnimation on rotation {
                            from: 0; to: 360; duration: 900
                            loops: Animation.Infinite
                            running: bridge.newsRefreshing
                        }
                        MouseArea {
                            anchors.fill: parent; anchors.margins: -6
                            cursorShape: Qt.PointingHandCursor
                            enabled: !bridge.newsRefreshing
                            onClicked: bridge.refreshNews(true)
                        }
                    }
                    Icon {
                        name: "search"; size: 20
                        color: root.searchActive ? Theme.accent : Theme.textSecondary
                        MouseArea {
                            anchors.fill: parent; anchors.margins: -6
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                root.searchActive = !root.searchActive
                                if (!root.searchActive) { chSearch.text = ""; bridge.setChannelSearch("") }
                                else chSearch.forceActiveFocus()
                            }
                        }
                    }
                    Icon {
                        name: "menu"; size: 20; color: Theme.textSecondary
                        MouseArea {
                            anchors.fill: parent; anchors.margins: -10
                            cursorShape: Qt.PointingHandCursor
                            onClicked: root.infoRequested()
                        }
                    }
                }
            }
            Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: Theme.divider }
        }

        // ---- Item 2: pinned posts bar (sits below the header) ----
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: (root.pinnedPosts && root.pinnedPosts.length > 0)
                                    ? Math.min(root.pinnedPosts.length, 3) * 30 + 8 : 0
            visible: root.pinnedPosts && root.pinnedPosts.length > 0
            color: Theme.panel
            clip: true
            Column {
                anchors.fill: parent
                anchors.leftMargin: 14
                anchors.rightMargin: 14
                anchors.topMargin: 4
                Repeater {
                    model: root.pinnedPosts
                    delegate: Item {
                        width: parent ? parent.width : 0
                        height: 30
                        MouseArea {
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                            onClicked: root.readArticleRequested(modelData.url, modelData.title || "", "")
                        }
                        Row {
                            anchors.fill: parent
                            spacing: 8
                            LayoutMirroring.enabled: Theme.rtl
                            Rectangle { width: 2; height: 18; radius: 1; color: Theme.accent; anchors.verticalCenter: parent.verticalCenter }
                            Icon { anchors.verticalCenter: parent.verticalCenter; name: "pin"; size: 14; color: Theme.accent }
                            Text {
                                anchors.verticalCenter: parent.verticalCenter
                                width: parent.width - 90
                                text: modelData.title || modelData.url || ""
                                color: Theme.text
                                font.family: Theme.fontFamily
                                font.pixelSize: 13
                                elide: Text.ElideRight
                                horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
                            }
                            Item { width: 1; height: 1 }
                        }
                        Icon {
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.right: parent.right
                            name: "close"; size: 13; color: Theme.textSecondary
                            MouseArea {
                                anchors.fill: parent; anchors.margins: -6
                                cursorShape: Qt.PointingHandCursor
                                onClicked: bridge.toggleMessagePin(modelData.url)
                            }
                        }
                    }
                }
            }
            Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: Theme.divider }
        }

        // ---- In-channel search bar (toggled by the header search icon) ----
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: root.searchActive ? 48 : 0
            visible: root.searchActive
            color: Theme.panel
            Rectangle {
                anchors.fill: parent; anchors.margins: 8
                radius: 18; color: Theme.panelAlt
                Row {
                    anchors.fill: parent
                    anchors.leftMargin: 12; anchors.rightMargin: 12; spacing: 8
                    LayoutMirroring.enabled: Theme.rtl
                    Icon { anchors.verticalCenter: parent.verticalCenter; name: "search"; size: 16; color: Theme.textSecondary }
                    TextField {
                        id: chSearch
                        anchors.verticalCenter: parent.verticalCenter
                        width: parent.width - 36
                        placeholderText: qsTr("Search this channel")
                        placeholderTextColor: Theme.textSecondary
                        color: Theme.text
                        font.family: Theme.fontFamily; font.pixelSize: 14
                        background: Item {}
                        horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
                        onTextChanged: bridge.setChannelSearch(text)
                    }
                }
            }
            Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: Theme.divider }
        }

        // ---- Messages ----
        ListView {
            id: messages
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            model: messageModel
            spacing: 2
            // Item 4: the bridge now sorts posts oldest -> newest, so render
            // top-to-bottom (default). Oldest sits at the top; newest at the
            // bottom. Jump to the newest post whenever the list (re)loads.
            cacheBuffer: 800
            onCountChanged: if (count > 0) Qt.callLater(positionViewAtEnd)
            ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
            boundsBehavior: Flickable.StopAtBounds
            leftMargin: 6
            rightMargin: 6
            topMargin: 10
            bottomMargin: 10

            delegate: Column {
                width: messages.width
                MessageBubble {
                    listWidth: messages.width
                    title: model.title
                    text: model.text
                    url: model.url
                    thumbnail: model.thumbnail
                    time: model.time
                    outgoing: model.outgoing
                    read: model.read
                    views: model.views
                    source: model.source
                    topic: model.topic
                    pinned: model.pinned
                    onTogglePinRequested: function(u) { bridge.toggleMessagePin(u) }
                    onReadRequested: function(u, t, tx) { root.readArticleRequested(u, t, tx) }
                    onOpenExternalRequested: function(u) { bridge.openExternal(u) }
                    onOpenInViewerRequested: function(u) { bridge.openInOfflineViewer(u, model.title) }
                    onForwardRequested: function(t) { bridge.forwardToSaved(t) }
                    onCopyRequested: function(u) { bridge.copyLink(u) }
                    onIgnoreRequested: function(u) { bridge.ignorePost(u) }
                }
            }

            // Empty / placeholder state
            Column {
                anchors.centerIn: parent
                spacing: 12
                visible: messages.count === 0
                Avatar {
                    anchors.horizontalCenter: parent.horizontalCenter
                    name: root.channelName !== "" ? root.channelName : "OfflineFeed"
                    seed: root.channelId
                    size: 84
                }
                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: root.channelId === "" ? qsTr("Select a channel to read its feed")
                                                : qsTr("No messages here yet")
                    color: Theme.textSecondary
                    font.family: Theme.fontFamily
                    font.pixelSize: 14
                }
            }
        }

        // ---- Bottom action bar: forward this channel to Telegram ----
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: visible ? 58 : 0
            visible: root.channelId !== "" && root.channelId !== "SavedMessages" && root.channelId !== "ArchivedMessages" && root.channelId !== "SystemLogs" && root.channelId !== "BinMessages"
            color: Theme.panel
            Rectangle { anchors.top: parent.top; width: parent.width; height: 1; color: Theme.divider }
            RowLayout {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 10
                LayoutMirroring.enabled: Theme.rtl
                Item { Layout.fillWidth: true }
                Rectangle {
                    Layout.preferredHeight: 38
                    Layout.preferredWidth: fwdRow.implicitWidth + 28
                    radius: 19
                    color: fwdMouse.containsMouse ? Qt.lighter(Theme.accent, 1.1) : Theme.accent
                    Behavior on color { ColorAnimation { duration: Theme.animFast } }
                    Row {
                        id: fwdRow
                        anchors.centerIn: parent
                        spacing: 8
                        Icon { anchors.verticalCenter: parent.verticalCenter; name: "send"; size: 17; color: Theme.accentText }
                        Text {
                            anchors.verticalCenter: parent.verticalCenter
                            text: qsTr("Forward channel to Telegram")
                            color: Theme.accentText
                            font.family: Theme.fontFamily
                            font.pixelSize: 14
                            font.bold: true
                        }
                    }
                    MouseArea {
                        id: fwdMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: root.forwardChannelRequested(root.channelId)
                    }
                }
            }
        }

        // ---- Bin action bar: empty the Bin ----
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: visible ? 58 : 0
            visible: root.channelId === "BinMessages" && messages.count > 0
            color: Theme.panel
            Rectangle { anchors.top: parent.top; width: parent.width; height: 1; color: Theme.divider }
            RowLayout {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 10
                LayoutMirroring.enabled: Theme.rtl
                Item { Layout.fillWidth: true }
                Rectangle {
                    Layout.preferredHeight: 38
                    Layout.preferredWidth: binRow.implicitWidth + 28
                    radius: 19
                    color: binMouse.containsMouse ? "#d34b52" : "#ec3942"
                    Behavior on color { ColorAnimation { duration: Theme.animFast } }
                    Row {
                        id: binRow
                        anchors.centerIn: parent
                        spacing: 8
                        Icon { anchors.verticalCenter: parent.verticalCenter; name: "trash"; size: 17; color: "#ffffff" }
                        Text {
                            anchors.verticalCenter: parent.verticalCenter
                            text: qsTr("Empty Bin")
                            color: "#ffffff"
                            font.family: Theme.fontFamily
                            font.pixelSize: 14
                            font.bold: true
                        }
                    }
                    MouseArea {
                        id: binMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: bridge.emptyBin()
                    }
                }
            }
        }
    }
}
