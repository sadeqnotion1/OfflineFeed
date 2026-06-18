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
                spacing: 11
                LayoutMirroring.enabled: Theme.rtl
                Avatar { name: root.channelName; seed: root.channelId; size: 40 }
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 0
                    Text {
                        text: root.channelName !== "" ? root.channelName : qsTr("OfflineFeed")
                        color: Theme.text
                        font.family: Theme.fontFamily
                        font.pixelSize: 16
                        font.bold: true
                        elide: Text.ElideRight
                    }
                    Text {
                        text: qsTr("news channel")
                        color: Theme.textSecondary
                        font.family: Theme.fontFamily
                        font.pixelSize: 13
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
                    name: "info"; size: 20; color: Theme.textSecondary
                    MouseArea {
                        anchors.fill: parent; cursorShape: Qt.PointingHandCursor
                        onClicked: root.infoRequested()
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
            // Telegram lays newest at the bottom; bridge sorts newest-first and
            // we render bottom-to-top so index 0 sits at the bottom.
            verticalLayoutDirection: ListView.BottomToTop
            cacheBuffer: 800
            ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
            boundsBehavior: Flickable.StopAtBounds
            leftMargin: 6
            rightMargin: 6
            topMargin: 10
            bottomMargin: 10

            delegate: Column {
                width: messages.width
                // Day separator pill (shown above the oldest message of a day).
                // Because layout is bottom-to-top, the separator sits visually
                // on top of the bubble it precedes.
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
                    onReadRequested: function(u, t, tx) { root.readArticleRequested(u, t, tx) }
                    onOpenExternalRequested: function(u) { bridge.openExternal(u) }
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
            visible: root.channelId !== "" && root.channelId !== "SavedMessages" && root.channelId !== "SystemLogs"
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
    }
}
