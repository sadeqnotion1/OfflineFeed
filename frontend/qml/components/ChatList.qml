import QtQuick
import QtQuick.Controls
import "../themes"

// Middle pane: search field (single, consolidated settings access lives in the
// folder rail — fixing known issue #5) + the scrollable list of channels.
Rectangle {
    id: root
    color: Theme.listBg

    Timer {
        id: searchDebounceTimer
        interval: 200
        repeat: false
        property string pendingText: ""
        onTriggered: {
            bridge.setSearch(pendingText)
        }
    }

    signal openChat(string channelId)
    // D5: carry the row's real pin/mute state to the opener so the context menu
    // can show "Pin" vs "Unpin" (and "Mute" vs "Unmute") correctly.
    signal chatContextMenu(string channelId, string channelName, bool pinned, bool muted, real gx, real gy)

    Column {
        anchors.fill: parent
        spacing: 0

        // ---- Search bar ----
        Rectangle {
            width: parent.width
            height: 54
            color: Theme.panel
            Rectangle {
                anchors.fill: parent
                anchors.margins: 8
                radius: 18
                color: Theme.panelAlt
                Row {
                    anchors.fill: parent
                    anchors.leftMargin: 12
                    anchors.rightMargin: 12
                    spacing: 8
                    LayoutMirroring.enabled: Theme.rtl
                    Icon {
                        anchors.verticalCenter: parent.verticalCenter
                        name: "search"; size: 18; color: Theme.textSecondary
                    }
                    TextField {
                        id: searchField
                        anchors.verticalCenter: parent.verticalCenter
                        width: parent.width - 36
                        placeholderText: qsTr("Search")
                        placeholderTextColor: Theme.textSecondary
                        color: Theme.text
                        font.family: Theme.fontFamily
                        font.pixelSize: 14
                        background: Item {}
                        horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
                        onTextChanged: {
                            searchDebounceTimer.pendingText = text
                            searchDebounceTimer.restart()
                        }
                    }
                }
            }
            // Hairline under the sticky search header so it separates crisply
            // from the scrolling channel list below.
            Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: Theme.hairline }
        }

        // ---- Channel list ----
        ListView {
            id: list
            width: parent.width
            height: parent.height - 54
            clip: true
            model: chatModel
            boundsBehavior: Flickable.StopAtBounds
            ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }

            // Keyboard navigation: let the list take focus so arrow keys move the
            // current item (which draws the focus ring in ChatRow) and Enter opens
            // it. Mouse selection still drives `selected` via bridge.currentChannelId.
            focus: true
            keyNavigationEnabled: true
            highlightFollowsCurrentItem: true
            Keys.onReturnPressed: if (list.currentItem) root.openChat(list.currentItem.channelId)
            Keys.onEnterPressed: if (list.currentItem) root.openChat(list.currentItem.channelId)

            delegate: ChatRow {
                channelId: model.channelId
                name: model.name
                lastMessage: model.lastMessage
                time: model.time
                unread: model.unread
                matchCount: model.matchCount || 0
                avatarPath: model.avatarPath
                selected: bridge.currentChannelId === model.channelId
                onClicked: {
                    list.currentIndex = index
                    root.openChat(model.channelId)
                }
                onRightClicked: function(gx, gy) {
                    list.currentIndex = index
                    root.chatContextMenu(model.channelId, model.name,
                                         model.pinned === true, model.muted === true,
                                         mapToItem(root, gx, gy).x,
                                         mapToItem(root, gx, gy).y)
                }
            }

            // Empty state
            Text {
                anchors.centerIn: parent
                visible: list.count === 0
                text: qsTr("No channels yet.\nRefresh feeds or add a source in Settings.")
                horizontalAlignment: Text.AlignHCenter
                color: Theme.textSecondary
                font.family: Theme.fontFamily
                font.pixelSize: 13
            }
        }
    }
}
