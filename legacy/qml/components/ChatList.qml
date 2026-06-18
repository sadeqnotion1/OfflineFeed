import QtQuick
import QtQuick.Controls
import "../themes"

// Middle pane: search field (single, consolidated settings access lives in the
// folder rail — fixing known issue #5) + the scrollable list of channels.
Rectangle {
    id: root
    color: Theme.panelAlt

    signal openChat(string channelId)
    signal chatContextMenu(string channelId, string channelName, real gx, real gy)

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
                        onTextChanged: bridge.setSearch(text)
                    }
                }
            }
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

            delegate: ChatRow {
                channelId: model.channelId
                name: model.name
                lastMessage: model.lastMessage
                time: model.time
                unread: model.unread
                avatarPath: model.avatarPath
                selected: bridge.currentChannelId === model.channelId
                onClicked: root.openChat(model.channelId)
                onRightClicked: function(gx, gy) {
                    root.chatContextMenu(model.channelId, model.name,
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
