import QtQuick
import QtQuick.Controls
import QtQuick.Window
import "./themes"
import "./components"

// Root window: frameless, custom title bar, 3-pane Telegram layout + slide-in
// info panel. All panes talk to the Python `bridge` and the two list models
// (`chatModel`, `messageModel`) exposed from bridge.py.
ApplicationWindow {
    id: win
    width: 1180
    height: 760
    minimumWidth: 760
    minimumHeight: 520
    visible: true
    title: "OfflineFeed"
    flags: Qt.Window | Qt.FramelessWindowHint
    color: Theme.bg

    // Keep the Theme singleton in sync with the bridge state.
    Binding { target: Theme; property: "variant"; value: bridge.theme }
    Binding { target: Theme; property: "rtl"; value: bridge.rtl }
    LayoutMirroring.enabled: Theme.rtl
    LayoutMirroring.childrenInherit: true

    Connections {
        target: bridge
        function onToastMessage(kind, message) { toast.show(kind, message) }
    }

    Column {
        anchors.fill: parent
        spacing: 0

        TitleBar {
            id: titleBar
            width: parent.width
            onRequestMinimize: win.showMinimized()
            onRequestToggleMaximize: win.visibility === Window.Maximized ? win.showNormal() : win.showMaximized()
            onRequestClose: Qt.quit()
            onStartSystemMove: win.startSystemMove()
        }

        // ---- Main body: rail | chat list | chat view | (info panel overlay) ----
        Item {
            width: parent.width
            height: parent.height - titleBar.height

            Row {
                anchors.fill: parent
                spacing: 0

                FolderRail {
                    id: rail
                    width: Theme.railWidth
                    height: parent.height
                    activeTab: bridge.activeTab
                    onTabSelected: function(tab) { bridge.setTab(tab) }
                    onSettingsRequested: bridge.setTab("settings")
                }

                // Master list (hidden when Settings is active to give it full width)
                ChatList {
                    id: chatList
                    width: bridge.activeTab === "settings" ? 0 : Theme.chatListWidth
                    height: parent.height
                    visible: width > 0
                    Behavior on width { NumberAnimation { duration: Theme.anim; easing.type: Theme.easing } }
                    onOpenChat: function(id) { bridge.openChat(id) }
                    onChatContextMenu: function(id, name, gx, gy) {
                        ctxMenu.channelId = id;
                        ctxMenu.channelName = name;
                        ctxMenu.popup();
                    }
                }

                Rectangle { width: 1; height: parent.height; color: Theme.divider; visible: chatList.visible }

                // Detail pane swaps between the chat view and the Settings page.
                Item {
                    width: parent.width - rail.width - (chatList.visible ? Theme.chatListWidth + 1 : 0)
                    height: parent.height

                    ChatView {
                        id: chatView
                        anchors.fill: parent
                        visible: bridge.activeTab !== "settings"
                        channelId: bridge.currentChannelId
                        channelName: bridge.currentChannelName
                        onInfoRequested: infoPanel.open = !infoPanel.open
                        onForwardChannelRequested: function(id) { bridge.sendChannelToTelegram(id) }
                        onReadArticleRequested: function(u, t, tx) { reader.open(u, t, tx) }
                    }

                    SettingsPage {
                        anchors.fill: parent
                        visible: bridge.activeTab === "settings"
                    }
                }
            }

            // ---- Slide-in info panel (overlays the right side) ----
            InfoPanel {
                id: infoPanel
                height: parent.height
                x: open ? parent.width - width : parent.width
                channelName: bridge.currentChannelName
                channelId: bridge.currentChannelId
                onClosed: open = false
            }

            // ---- Offline reader overlay (covers the whole body) ----
            ReaderView {
                id: reader
                anchors.fill: parent
                z: 60
            }
        }
    }

    ChatContextMenu {
        id: ctxMenu
        onOpenInNewWindow: function(id) { bridge.openInNewWindow(id) }
        onArchive: function(id) { bridge.archiveChat(id) }
        onTogglePin: function(id) { bridge.togglePin(id) }
        onToggleMute: function(id) { bridge.toggleMute(id) }
        onMarkUnread: function(id) { bridge.markUnread(id) }
        onAddToFolder: function(id) { bridge.addToFolder(id) }
        onClearHistory: function(id) { bridge.clearHistory(id) }
        onDeleteChat: function(id) { bridge.deleteChat(id) }
    }

    // ---- Lightweight toast for bridge feedback ----
    Rectangle {
        id: toast
        function show(kind, message) { toastText.text = message; toastAnim.restart(); }
        anchors.horizontalCenter: parent.horizontalCenter
        y: opacity > 0 ? parent.height - 70 : parent.height - 40
        Behavior on y { NumberAnimation { duration: Theme.anim; easing.type: Theme.easing } }
        width: toastText.implicitWidth + 36
        height: 40
        radius: 20
        color: Theme.panel
        border.width: 1; border.color: Theme.divider
        opacity: 0
        z: 1000
        Text {
            id: toastText
            anchors.centerIn: parent
            color: Theme.text
            font.family: Theme.fontFamily; font.pixelSize: 14
        }
        SequentialAnimation {
            id: toastAnim
            NumberAnimation { target: toast; property: "opacity"; to: 1; duration: Theme.anim }
            PauseAnimation { duration: 2200 }
            NumberAnimation { target: toast; property: "opacity"; to: 0; duration: Theme.anim }
        }
    }
}
