import QtQuick
import QtQuick.Controls
import Qt5Compat.GraphicalEffects
import "../themes"

// Right-click context menu for a chat row. Mirrors Telegram Desktop's chat
// context menu. Items are data-driven so icons stay crisp (SVG, no emoji).
Menu {
    id: menu
    property string channelId: ""
    property string channelName: ""
    // D5: the opener sets these from the row's real model state so the Pin/Mute
    // rows can show the correct verb instead of a hardcoded "Unpin"/"Unmute".
    property bool isPinned: false
    property bool isMuted: false

    signal openInNewWindow(string id)
    signal archive(string id)
    signal togglePin(string id)
    signal toggleMute(string id)
    signal markUnread(string id)
    signal addToFolder(string id)
    signal clearHistory(string id)
    signal deleteChat(string id)

    width: 224
    padding: 6

    background: Rectangle {
        color: Theme.panel
        radius: Theme.radius.lg
        border.width: 1
        border.color: Theme.divider
        layer.enabled: true
        layer.effect: DropShadow {
            transparentBorder: true
            radius: 22
            samples: 33
            color: "#66000000"
            verticalOffset: 6
        }
    }

    component MenuRow: MenuItem {
        id: mi
        property string iconName: ""
        property bool danger: false
        height: 38
        contentItem: Row {
            spacing: 12
            leftPadding: 10
            Icon {
                anchors.verticalCenter: parent.verticalCenter
                name: mi.iconName
                size: 18
                color: mi.danger ? "#ec3942" : Theme.textSecondary
            }
            Text {
                anchors.verticalCenter: parent.verticalCenter
                text: mi.text
                color: mi.danger ? "#ec3942" : Theme.text
                font.family: Theme.fontFamily
                font.pixelSize: 14
            }
        }
        background: Rectangle {
            radius: Theme.radius.sm
            color: mi.highlighted ? Theme.hover : "transparent"
        }
    }

    MenuRow { text: qsTr("Open in new window"); iconName: "window";  onTriggered: menu.openInNewWindow(menu.channelId) }
    MenuRow { text: qsTr("Archive");            iconName: "archive"; onTriggered: menu.archive(menu.channelId) }
    // D5: conditional verb + the action still toggles the real pin state via bridge.togglePin.
    MenuRow { text: menu.isPinned ? qsTr("Unpin") : qsTr("Pin");    iconName: "pin";  onTriggered: menu.togglePin(menu.channelId) }
    MenuRow { text: menu.isMuted ? qsTr("Unmute") : qsTr("Mute");   iconName: "mute"; onTriggered: menu.toggleMute(menu.channelId) }
    MenuRow { text: qsTr("Mark as unread");     iconName: "unread";  onTriggered: menu.markUnread(menu.channelId) }
    MenuRow { text: qsTr("Add to folder");      iconName: "folder";  onTriggered: menu.addToFolder(menu.channelId) }
    MenuSeparator {
        contentItem: Rectangle { implicitHeight: 1; color: Theme.divider }
    }
    MenuRow { text: qsTr("Clear history");      iconName: "trash";  danger: false; onTriggered: menu.clearHistory(menu.channelId) }
    MenuRow { text: qsTr("Delete chat");        iconName: "trash";  danger: true;  onTriggered: menu.deleteChat(menu.channelId) }
}
