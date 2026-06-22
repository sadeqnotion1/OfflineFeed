import QtQuick
import QtQuick.Layouts
import "../themes"

// Left rail: labeled folder tabs with unread badges, plus the single Settings
// entry (consolidation fix, issue #5). Telegram's vertical folder strip.
//
// Bug #6 (rail icons/labels invisible): inactive tabs painted their icon with
// Icon.Tint.Default and their label with Theme.textSecondary. On the dark rail
// (Theme.railBg) that secondary tone has almost no contrast, so every inactive
// icon AND the "Settings" label disappeared while only the active (accent)
// item showed. Fix is rail-local: inactive icons/labels now use Theme.text at
// 62% opacity -> clearly legible, still subordinate to the active accent.
// We intentionally do NOT touch the global Theme.textSecondary token, because
// it is correct for body/preview text elsewhere (e.g. channel snippets).
Rectangle {
 id: root
 color: Theme.railBg

 property string activeTab: "all"
 signal tabSelected(string tab)
 signal settingsRequested()

 // Bug #6: legible resting color for inactive rail icons & labels.
 readonly property color inactiveRail: Qt.rgba(Theme.text.r, Theme.text.g, Theme.text.b, 0.62)

 // tab metadata
 property var tabs: [
 { id: "all", label: qsTr("All"), icon: "chats" },
 { id: "entertainment", label: qsTr("Entertainment"), icon: "film" },
 { id: "sports", label: qsTr("Sports"), icon: "soccer" },
 { id: "technology", label: qsTr("Tech"), icon: "cpu" }
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
 radius: Theme.radius.md
 color: parent.active ? Theme.selection : (tabMouse.containsMouse ? Theme.hover : "transparent")
 Behavior on color { ColorAnimation { duration: Theme.animFast } }
 }

 Column {
 anchors.centerIn: parent
 spacing: 4
 Icon {
 anchors.horizontalCenter: parent.horizontalCenter
 name: modelData.icon
 size: Icon.Size.Large
 // Bug #6: inactive used Icon.Tint.Default (Theme.textSecondary,
 // near-invisible on the rail). Use Inherit + a legible color.
 tint: parent.parent.active ? Icon.Tint.Active : Icon.Tint.Inherit
 color: root.inactiveRail
 }
 Text {
 anchors.horizontalCenter: parent.horizontalCenter
 // Bug #5: built-in tab labels (Entertainment/Sports/Tech) had no
 // width/elide, so they overflowed the 72px rail. Mirror the
 // custom-folder label treatment so they fit Theme.railWidth.
 width: root.width - 8
 text: modelData.label
 // Bug #6: inactive label was Theme.textSecondary (invisible).
 color: parent.parent.active ? Theme.accent : root.inactiveRail
 font.family: Theme.fontFamily
 font.pixelSize: 11
 elide: Text.ElideRight
 horizontalAlignment: Text.AlignHCenter
 }
 }

 // Unread badge
 Badge {
 anchors.top: parent.top
 anchors.right: parent.right
 anchors.topMargin: 8
 anchors.rightMargin: 14
 count: root.unreadByTab[modelData.id] || 0
 muted: false
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
 radius: Theme.radius.md
 color: parent.active ? Theme.selection : (folderMouse.containsMouse ? Theme.hover : "transparent")
 Behavior on color { ColorAnimation { duration: Theme.animFast } }
 }
 Column {
 anchors.centerIn: parent
 spacing: 4
 Icon {
 anchors.horizontalCenter: parent.horizontalCenter
 name: "folder"
 size: Icon.Size.Large
 // Bug #6: legible inactive tint (was Icon.Tint.Default).
 tint: parent.parent.active ? Icon.Tint.Active : Icon.Tint.Inherit
 color: root.inactiveRail
 }
 Text {
 anchors.horizontalCenter: parent.horizontalCenter
 width: root.width - 8
 text: modelData.name || qsTr("Folder")
 // Bug #6: legible inactive label (was Theme.textSecondary).
 color: parent.parent.active ? Theme.accent : root.inactiveRail
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
 radius: Theme.radius.md
 color: parent.active ? Theme.selection : (setMouse.containsMouse ? Theme.hover : "transparent")
 Behavior on color { ColorAnimation { duration: Theme.animFast } }
 }
 Column {
 anchors.centerIn: parent
 spacing: 4
 Icon {
 anchors.horizontalCenter: parent.horizontalCenter
 name: "settings"; size: Icon.Size.Large
 // Bug #6: legible inactive tint (was Icon.Tint.Default).
 tint: parent.parent.active ? Icon.Tint.Active : Icon.Tint.Inherit
 color: root.inactiveRail
 }
 Text {
 anchors.horizontalCenter: parent.horizontalCenter
 // Bug #5/#6: give the Settings label the same width/elide as the
 // other rail labels, and a legible inactive color (was
 // Theme.textSecondary, which made "Settings" invisible).
 width: root.width - 8
 text: qsTr("Settings")
 color: parent.parent.active ? Theme.accent : root.inactiveRail
 font.family: Theme.fontFamily
 font.pixelSize: 11
 elide: Text.ElideRight
 horizontalAlignment: Text.AlignHCenter
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

 // Right-edge hairline so the rail still reads as a distinct plane even when
 // the chat list is collapsed (e.g. Settings is open).
 Rectangle {
 anchors.right: parent.right
 anchors.top: parent.top
 anchors.bottom: parent.bottom
 width: 1
 color: Theme.hairline
 }
}
