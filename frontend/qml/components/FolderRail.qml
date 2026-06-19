import QtQuick
import QtQuick.Layouts
import "../themes"

// Left rail: labeled folder tabs with unread badges, plus the single Settings
// entry (consolidation fix, issue #5). Telegram's vertical folder strip.
Rectangle {
    id: root
    color: Theme.panel

    property string activeTab: "entertainment"
    signal tabSelected(string tab)
    signal settingsRequested()

    // tab metadata
    property var tabs: [
        { id: "entertainment", label: qsTr("Entertainment"),     icon: "film"   },
        { id: "sports",        label: qsTr("Sports"),            icon: "soccer" },
        { id: "technology",    label: qsTr("Tech"),              icon: "cpu"    }
    ]
    property var unreadByTab: ({})

    // Item 7: user-defined folders that combine channels (from the bridge).
    property var customFolders: []
    function refreshFolders() { root.customFolders = bridge.getCustomFolders() }
    Connections {
        target: bridge
        function onCustomFoldersChanged() { root.refreshFolders() }
    }
    Component.onCompleted: root.refreshFolders()

    ColumnLayout {
        anchors.fill: parent
        anchors.topMargin: 8
        spacing: 2

        Repeater {
            model: root.tabs
            delegate: Item {
                required property var modelData
                Layout.fillWidth: true
                Layout.preferredHeight: 64
                readonly property bool active: root.activeTab === modelData.id

                Rectangle {
                    anchors.fill: parent
                    anchors.margins: 4
                    radius: 10
                    color: parent.active ? Theme.selection : (tabMouse.containsMouse ? Theme.hover : "transparent")
                    Behavior on color { ColorAnimation { duration: Theme.animFast } }
                }

                Column {
                    anchors.centerIn: parent
                    spacing: 4
                    Icon {
                        anchors.horizontalCenter: parent.horizontalCenter
                        name: modelData.icon
                        size: 26
                        color: parent.parent.active ? Theme.accentText : Theme.textSecondary
                    }
                    Text {
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: modelData.label
                        color: parent.parent.active ? Theme.accentText : Theme.textSecondary
                        font.family: Theme.fontFamily
                        font.pixelSize: 11
                    }
                }

                // Unread badge
                Rectangle {
                    visible: (root.unreadByTab[modelData.id] || 0) > 0
                    anchors.top: parent.top
                    anchors.right: parent.right
                    anchors.topMargin: 8
                    anchors.rightMargin: 14
                    radius: height / 2
                    height: 18
                    width: Math.max(18, b.implicitWidth + 10)
                    color: Theme.badge
                    Text {
                        id: b
                        anchors.centerIn: parent
                        text: root.unreadByTab[modelData.id] || 0
                        color: Theme.accentText
                        font.pixelSize: 11
                        font.bold: true
                        font.family: Theme.fontFamily
                    }
                }

                MouseArea {
                    id: tabMouse
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: root.tabSelected(modelData.id)
                }
            }
        }

        // ---- Item 7: custom folder tabs (after the built-in folders) ----
        Repeater {
            model: root.customFolders
            delegate: Item {
                required property var modelData
                Layout.fillWidth: true
                Layout.preferredHeight: 64
                readonly property bool active: root.activeTab === modelData.id

                Rectangle {
                    anchors.fill: parent
                    anchors.margins: 4
                    radius: 10
                    color: parent.active ? Theme.selection : (folderMouse.containsMouse ? Theme.hover : "transparent")
                    Behavior on color { ColorAnimation { duration: Theme.animFast } }
                }
                Column {
                    anchors.centerIn: parent
                    spacing: 4
                    Icon {
                        anchors.horizontalCenter: parent.horizontalCenter
                        name: "folder"
                        size: 26
                        color: parent.parent.active ? Theme.accentText : Theme.textSecondary
                    }
                    Text {
                        anchors.horizontalCenter: parent.horizontalCenter
                        width: root.width - 8
                        text: modelData.name || qsTr("Folder")
                        color: parent.parent.active ? Theme.accentText : Theme.textSecondary
                        font.family: Theme.fontFamily
                        font.pixelSize: 11
                        elide: Text.ElideRight
                        horizontalAlignment: Text.AlignHCenter
                    }
                }
                MouseArea {
                    id: folderMouse
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: root.tabSelected(modelData.id)
                }
            }
        }

        Item { Layout.fillHeight: true }

        // ---- Single Settings entry (issue #5) ----
        Item {
            Layout.fillWidth: true
            Layout.preferredHeight: 64
            readonly property bool active: root.activeTab === "settings"
            Rectangle {
                anchors.fill: parent
                anchors.margins: 4
                radius: 10
                color: parent.active ? Theme.selection : (setMouse.containsMouse ? Theme.hover : "transparent")
                Behavior on color { ColorAnimation { duration: Theme.animFast } }
            }
            Column {
                anchors.centerIn: parent
                spacing: 4
                Icon {
                    anchors.horizontalCenter: parent.horizontalCenter
                    name: "settings"; size: 26
                    color: parent.parent.active ? Theme.accentText : Theme.textSecondary
                }
                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: qsTr("Settings")
                    color: parent.parent.active ? Theme.accentText : Theme.textSecondary
                    font.family: Theme.fontFamily
                    font.pixelSize: 11
                }
            }
            MouseArea {
                id: setMouse
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                onClicked: root.settingsRequested()
            }
        }
    }
}
