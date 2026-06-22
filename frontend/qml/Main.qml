import QtQuick
import QtQuick.Controls
import QtQuick.Window
import "./themes"
import "./components"

// Root window: frameless, custom title bar, 3-pane Telegram layout + slide-in
// info panel. All panes talk to the Python `bridge` and the two list models
// (`chatModel`, `messageModel`) exposed from bridge.py.
//
// ---------------------------------------------------------------------------
//  WINDOW-MODES PATCH (responsive + resizable, like Telegram Desktop)
//  - minimumWidth lowered so the window can shrink into a single-pane mode.
//  - toggleMaximize() maximizes into the screen's AVAILABLE area (never over
//    the taskbar) and restores cleanly, instead of a taskbar-covering fill.
//  - WindowModes controller collapses the 3-pane shell to one pane when narrow.
//  - ResizeHandles overlay restores edge/corner drag-resize on the frameless
//    window (see components/ResizeHandles.qml + components/WindowModes.qml).
//  Every edit is additive and reversible; the WIDE layout is unchanged.
// ---------------------------------------------------------------------------
ApplicationWindow {
    id: win
    width: 1180
    height: 760
    minimumWidth: 380          // PATCH: was 760 - allow Telegram-style narrow single-pane mode
    minimumHeight: 480         // PATCH: was 520
    visible: true
    title: "OfflineFeed"
    flags: Qt.Window | Qt.FramelessWindowHint
    color: Theme.bg

    // ---- Window-mode state (PATCH) ----
    // Frameless windows have no native maximize that respects the taskbar, so
    // we maximize manually into the screen's *available* geometry and keep a
    // restore rect for un-maximize. ResizeHandles clears _isMaxed when the user
    // drag-resizes, so the restore size never goes stale.
    property bool _isMaxed: false
    property rect _restoreGeom: Qt.rect(100, 100, 1180, 760)
    function toggleMaximize() {
        if (_isMaxed) {
            win.x = _restoreGeom.x
            win.y = _restoreGeom.y
            win.width = _restoreGeom.width
            win.height = _restoreGeom.height
            _isMaxed = false
        } else {
            _restoreGeom = Qt.rect(win.x, win.y, win.width, win.height)
            // FIX (high-DPI "~3x too wide" maximize/restore bug):
            // Screen.* metrics are reported in PHYSICAL device pixels, but a
            // Window's geometry is in LOGICAL (device-independent) pixels. On a
            // scaled display (e.g. 150% / 200% / 300%) feeding the physical
            // numbers straight in made the window devicePixelRatio-times too
            // large (the "3x bigger than screen" symptom). Convert to logical
            // pixels via Screen.devicePixelRatio. At 100% scale dpr == 1, so
            // this is a no-op on non-scaled displays.
            var dpr = Screen.devicePixelRatio > 0 ? Screen.devicePixelRatio : 1
            win.x = Math.round(Screen.virtualX / dpr)
            win.y = Math.round(Screen.virtualY / dpr)
            win.width = Math.round(Screen.desktopAvailableWidth / dpr)
            win.height = Math.round(Screen.desktopAvailableHeight / dpr)
            _isMaxed = true
        }
    }

    // Responsive layout controller (PATCH).
    WindowModes { id: modes; windowWidth: win.width }

    // Keep the Theme singleton in sync with the bridge state.
    Binding { target: Theme; property: "variant"; value: bridge.theme }
    Binding { target: Theme; property: "rtl"; value: bridge.rtl }
    Binding { target: Theme; property: "fontFamily"; value: bridge.fontFamily }
    Binding { target: Theme; property: "readerFontFamily"; value: bridge.readerFontFamily }
    Binding { target: Theme; property: "accentOverride"; value: bridge.accentOverride }
    Binding { target: Theme; property: "wallpaperMode"; value: bridge.wallpaperMode }
    Binding { target: Theme; property: "wallpaperImage"; value: bridge.wallpaperImage }
    LayoutMirroring.enabled: Theme.rtl
    LayoutMirroring.childrenInherit: true

    Connections {
        target: bridge
        function onToastMessage(kind, message) { toast.show(kind, message) }
    }

    // ---- Bug #3: real, live "Interface scale" ----
    // The slider writes bridge.interfaceScale (0.8-1.4) but previously NOTHING
    // consumed it. We now lay the whole UI out at a "logical" size
    // (window / scale) and scale it up to fill the real window, so the value is
    // applied as a genuine, live UI zoom. At scale 1.0 this is a no-op.
    Item {
        id: uiScaler
        anchors.fill: parent
        readonly property real s: bridge.interfaceScale > 0 ? bridge.interfaceScale : 1.0

        Item {
        id: scaledRoot
        width: uiScaler.width / uiScaler.s
        height: uiScaler.height / uiScaler.s
        scale: uiScaler.s
        transformOrigin: Item.TopLeft

    Column {
        anchors.fill: parent
        spacing: 0

        TitleBar {
            id: titleBar
            width: parent.width
            onRequestMinimize: win.showMinimized()
            onRequestToggleMaximize: win.toggleMaximize()            // PATCH: taskbar-safe maximize/restore
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

                // Hairline seam between the folder rail and the chat list.
                Rectangle { width: 1; height: parent.height; color: Theme.hairline }

                // Master list. PATCH: width is now responsive.
                //  - Settings active        -> 0 (Settings takes the detail pane)
                //  - COMPACT + chat open     -> 0 (single-pane shows the chat)
                //  - COMPACT + no chat open  -> fills the body (single-pane list)
                //  - WIDE                    -> fixed Theme.chatListWidth (unchanged)
                ChatList {
                    id: chatList
                    width: bridge.activeTab === "settings"
                           ? 0
                           : (modes.compact
                              ? (modes.detailActive ? 0 : (parent.width - rail.width - 1))
                              : Theme.chatListWidth)
                    height: parent.height
                    visible: width > 0
                    Behavior on width { NumberAnimation { duration: Theme.anim; easing.type: Theme.easing } }
                    onOpenChat: function(id) { bridge.openChat(id); if (modes.compact) modes.detailActive = true }
                    // D5: receive the row's pin/mute state and pass it to the menu so
                    // it shows the correct verb; the action still toggles real state.
                    onChatContextMenu: function(id, name, pinned, muted, gx, gy) {
                        ctxMenu.channelId = id;
                        ctxMenu.channelName = name;
                        ctxMenu.isPinned = pinned;
                        ctxMenu.isMuted = muted;
                        ctxMenu.popup();
                    }
                }

                Rectangle { width: 1; height: parent.height; color: Theme.hairline; visible: chatList.visible }

                // Detail pane swaps between the chat view and the Settings page.
                // PATCH: in COMPACT mode it is 0-width until a chat is opened.
                Item {
                    width: modes.compact
                           ? (modes.detailActive ? (parent.width - rail.width - 1) : 0)
                           : parent.width - rail.width - 1 - (chatList.visible ? Theme.chatListWidth + 1 : 0)
                    height: parent.height

                    ChatView {
                        id: chatView
                        anchors.fill: parent
                        visible: bridge.activeTab !== "settings" && bridge.currentChannelId !== "SearchResults"
                        channelId: bridge.currentChannelId
                        channelName: bridge.currentChannelName
                        compact: modes.compact && modes.detailActive   // PATCH: show Back arrow in single-pane
                        onBackRequested: modes.detailActive = false    // PATCH: return to the list
                        onInfoRequested: infoPanel.open = !infoPanel.open
                        onForwardChannelRequested: function(id) { bridge.sendChannelToTelegram(id) }
                        onReadArticleRequested: function(u, t, tx) { reader.open(u, t, tx) }
                    }

                    SearchResultsView {
                        anchors.fill: parent
                        visible: bridge.activeTab !== "settings" && bridge.currentChannelId === "SearchResults"
                        onReadArticleRequested: function(u, t, tx) { reader.open(u, t, tx) }
                    }

                    Loader {
                        anchors.fill: parent
                        active: bridge.activeTab === "settings"
                        visible: active
                        source: Qt.resolvedUrl("components/SettingsView.qml")
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
        }
    }

    // ---- Item 7: choose / create a custom folder for a channel ----
    AddToFolderDialog {
        id: addToFolderDialog
    }

    ChatContextMenu {
        id: ctxMenu
        onOpenInNewWindow: function(id) { bridge.openInNewWindow(id) }
        onArchive: function(id) { bridge.archiveChat(id) }
        onTogglePin: function(id) { bridge.togglePin(id) }
        onToggleMute: function(id) { bridge.toggleMute(id) }
        onMarkUnread: function(id) { bridge.markUnread(id) }
        onAddToFolder: function(id) { addToFolderDialog.openFor(id) }
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
        radius: Theme.radius.pill
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

    // ---- Frameless-window resize grips (PATCH) ----
    // Restores edge/corner drag-resize that Qt.FramelessWindowHint removed.
    // Lives OUTSIDE uiScaler so it maps to real window pixels (never scaled),
    // and on top (z) so the edges always win over content underneath.
    ResizeHandles {
        anchors.fill: parent
        targetWindow: win
        z: 9999
        onResizeStarted: win._isMaxed = false
    }
}
