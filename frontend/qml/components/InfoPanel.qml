import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../themes"

// Telegram-style channel INFO / MANAGE panel.
//
// Slides in from the right edge (the x position is animated by Main.qml). It
// keeps the SAME public interface the rest of the app already relies on
// (properties: open, channelName, channelId; signal: closed) so it is a
// drop-in replacement for the previous, bare InfoPanel.
//
// What changed vs the old panel (all additive, all grounded in real data):
//   * The big avatar now uses the REAL channel image (bridge.currentChannelAvatar)
//     with the existing gradient-initials fallback - same source the chat
//     header already uses - instead of always drawing the gradient.
//   * A Telegram-style list of MANAGE actions wired to bridge slots that
//     already exist and are already called from Main.qml's context menu
//     (togglePin / toggleMute / archiveChat / clearHistory / deleteChat) plus
//     sendChannelToTelegram (already used by ChatView). No invented data, no
//     new backend endpoints.
//   * Manage actions are hidden for the special, non-manageable entries
//     (Saved / Archived / Logs / Bin / Search results).
Rectangle {
    id: root
    color: Theme.panel
    property bool open: false
    property string channelName: ""
    property string channelId: ""
    signal closed()

    width: Theme.infoPanelWidth

    Behavior on x { NumberAnimation { duration: Theme.anim; easing.type: Theme.easing } }

    // Special, system entries that are NOT user-manageable feed channels.
    readonly property bool isSpecial:
        channelId === ""
        || channelId === "SavedMessages"
        || channelId === "ArchivedMessages"
        || channelId === "SystemLogs"
        || channelId === "BinMessages"
        || channelId === "SearchResults"

    // A single tappable manage row (icon + label), Telegram-style.
    component ActionRow: Item {
        id: arow
        property string icon: ""
        property string label: ""
        property color tone: Theme.text
        signal triggered()
        Layout.fillWidth: true
        Layout.preferredHeight: 48
        Rectangle {
            anchors.fill: parent
            color: rowHover.containsMouse ? Theme.hoverFill : "transparent"
            Behavior on color { ColorAnimation { duration: Theme.animFast; easing.type: Theme.easing } }
        }
        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 18
            anchors.rightMargin: 18
            spacing: 14
            LayoutMirroring.enabled: Theme.rtl
            Icon { name: arow.icon; size: 19; color: arow.tone }
            Text {
                Layout.fillWidth: true
                text: arow.label
                color: arow.tone
                font.family: Theme.fontFamily
                font.pixelSize: 14
                elide: Text.ElideRight
                horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
            }
        }
        MouseArea {
            id: rowHover
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            onClicked: arow.triggered()
        }
    }

    Rectangle { width: 1; height: parent.height; color: Theme.divider }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // ---- header ----
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: Theme.headerHeight
            color: Theme.panel
            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 12
                anchors.rightMargin: 12
                spacing: 10
                LayoutMirroring.enabled: Theme.rtl
                Icon {
                    name: "close"; size: 20; color: Theme.textSecondary
                    MouseArea {
                        anchors.fill: parent; anchors.margins: -6
                        cursorShape: Qt.PointingHandCursor
                        onClicked: root.closed()
                    }
                }
                Text {
                    Layout.fillWidth: true
                    text: qsTr("Channel Info")
                    color: Theme.text
                    font.family: Theme.fontFamily
                    font.pixelSize: 16
                    font.bold: true
                    horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
                }
            }
            Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: Theme.divider }
        }

        // ---- big avatar + name (REAL channel image, gradient fallback) ----
        ColumnLayout {
            Layout.fillWidth: true
            Layout.topMargin: 22
            spacing: 10
            Avatar {
                Layout.alignment: Qt.AlignHCenter
                name: root.channelName
                seed: root.channelId
                avatarPath: bridge.currentChannelAvatar
                size: 96
            }
            Text {
                Layout.alignment: Qt.AlignHCenter
                Layout.fillWidth: true
                text: root.channelName
                color: Theme.text
                font.family: Theme.fontFamily
                font.pixelSize: 19
                font.bold: true
                elide: Text.ElideRight
                horizontalAlignment: Text.AlignHCenter
            }
            Text {
                Layout.alignment: Qt.AlignHCenter
                text: qsTr("news channel")
                color: Theme.textSecondary
                font.family: Theme.fontFamily
                font.pixelSize: 13
            }
        }

        Rectangle { Layout.fillWidth: true; Layout.topMargin: 18; height: 1; color: Theme.divider }

        // ---- About (real, non-interactive description) ----
        ColumnLayout {
            Layout.fillWidth: true
            Layout.leftMargin: 18; Layout.rightMargin: 18; Layout.topMargin: 16
            spacing: 6
            Text {
                text: qsTr("About")
                color: Theme.textSecondary; font.bold: true
                font.family: Theme.fontFamily; font.pixelSize: 12
                horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
                Layout.fillWidth: true
            }
            Text {
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
                text: qsTr("Offline RSS feed aggregated by OfflineFeed. Open any post to read it offline, or forward the whole channel to Telegram.")
                color: Theme.text; font.family: Theme.fontFamily; font.pixelSize: 14
                horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
            }
        }

        // ---- Manage section (hidden for special entries) ----
        Rectangle {
            Layout.fillWidth: true; Layout.topMargin: 16; height: 1
            color: Theme.divider
            visible: !root.isSpecial
        }

        ColumnLayout {
            Layout.fillWidth: true
            Layout.topMargin: 6
            spacing: 0
            visible: !root.isSpecial

            ActionRow {
                icon: "send"; label: qsTr("Forward channel to Telegram")
                onTriggered: bridge.sendChannelToTelegram(root.channelId)
            }
            ActionRow {
                icon: "pin"; label: qsTr("Pin / unpin to top")
                onTriggered: bridge.togglePin(root.channelId)
            }
            ActionRow {
                icon: "mute"; label: qsTr("Mute / unmute notifications")
                onTriggered: bridge.toggleMute(root.channelId)
            }
            ActionRow {
                icon: "archive"; label: qsTr("Archive channel")
                onTriggered: { bridge.archiveChat(root.channelId); root.closed() }
            }
            ActionRow {
                icon: "trash"; label: qsTr("Clear history")
                onTriggered: bridge.clearHistory(root.channelId)
            }
            ActionRow {
                icon: "trash"; label: qsTr("Delete channel"); tone: "#ec3942"
                onTriggered: { bridge.deleteChat(root.channelId); root.closed() }
            }
        }

        Item { Layout.fillHeight: true }
    }
}
