import QtQuick
import QtQuick.Controls
import Qt5Compat.GraphicalEffects
import "../themes"

// Right-click context menu for a message/article bubble (issue: right-click was
// only available on chat rows). Mirrors Telegram Desktop's message menu. Items
// are data-driven so icons stay crisp (SVG, no emoji).
Menu {
    id: menu
    property string url: ""
    property string messageTitle: ""
    property bool canIgnore: true
    property bool pinned: false        // Item 2: whether this post is currently pinned

    signal readArticle(string url, string title)
    signal openLink(string url)
    signal openInViewer(string url)        // NEW: open this post in the offline viewer
    signal forward(string title)
    signal copyLink(string url)
    signal ignore(string url)
    signal togglePin(string url)

    width: 230
    padding: 6

    background: Rectangle {
        color: Theme.panel
        radius: 10
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
            radius: 7
            color: mi.highlighted ? Theme.hover : "transparent"
        }
    }

    MenuRow { text: qsTr("Read offline");            iconName: "eye";      onTriggered: menu.readArticle(menu.url, menu.messageTitle) }
    MenuRow { text: qsTr("Open in offline viewer");  iconName: "window";   onTriggered: menu.openInViewer(menu.url) }
    MenuRow { text: qsTr("Open original link");      iconName: "external"; onTriggered: menu.openLink(menu.url) }
    MenuRow {
        // Item 2: pin / unpin this individual post. The pinned state is keyed by
        // url in the bridge and surfaces in the pinned bar at the top of ChatView.
        text: menu.pinned ? qsTr("Unpin post") : qsTr("Pin post")
        iconName: "pin"
        onTriggered: menu.togglePin(menu.url)
    }
    MenuRow {
        text: qsTr("Remove from Saved Messages")
        iconName: "trash"
        danger: true
        visible: bridge.currentChannelId === "SavedMessages"
        height: visible ? 38 : 0
        onTriggered: bridge.unsaveArticle(menu.url, menu.messageTitle)
    }
    MenuRow {
        text: qsTr("Forward to Saved Messages")
        iconName: "forward"
        visible: bridge.currentChannelId !== "SavedMessages"
        height: visible ? 38 : 0
        onTriggered: menu.forward(menu.messageTitle)
    }
    MenuRow { text: qsTr("Copy link");               iconName: "copy";     onTriggered: menu.copyLink(menu.url) }
    MenuSeparator {
        padding: 6
        contentItem: Rectangle { implicitHeight: 1; color: Theme.divider }
    }
    MenuRow {
        text: qsTr("Hide this post")
        iconName: "trash"
        danger: true
        visible: menu.canIgnore
        height: visible ? 38 : 0
        onTriggered: menu.ignore(menu.url)
    }
    MenuSeparator {
        padding: 6
        contentItem: Rectangle { implicitHeight: 1; color: Theme.divider }
    }
    MenuRow {
        text: qsTr("Delete post")
        iconName: "trash"
        danger: true
        visible: bridge.currentChannelId !== "BinMessages"
        height: visible ? 38 : 0
        onTriggered: bridge.deletePost(menu.url, menu.messageTitle)
    }
    MenuRow {
        text: qsTr("Restore from Bin")
        iconName: "refresh"
        visible: bridge.currentChannelId === "BinMessages"
        height: visible ? 38 : 0
        onTriggered: bridge.restorePost(menu.url, menu.messageTitle)
    }
    MenuRow {
        text: qsTr("Delete permanently")
        iconName: "trash"
        danger: true
        visible: bridge.currentChannelId === "BinMessages"
        height: visible ? 38 : 0
        onTriggered: bridge.purgePost(menu.url, menu.messageTitle)
    }
}
