import QtQuick
import QtQuick.Controls
import "../themes"

// Folders: OfflineFeed groups feeds into the categories shown in the folder
// rail (Movies / Sports / Tech). Visibility preferences persist in group
// "folders". See Notes: persisting works today; making FolderRail honor these
// flags live is a small additive follow-up.
Item {
    id: page
    property var stack: null
    anchors.fill: parent

    // Item 7: user-defined folders that combine channels.
    property var customFolders: []
    function refreshFolders() { page.customFolders = bridge.getCustomFolders() }
    function doCreateFolder() {
        var n = newFolderField.text.trim()
        if (n === "") return
        bridge.createFolder(n)
        newFolderField.text = ""
    }
    Connections { target: bridge; function onCustomFoldersChanged() { page.refreshFolders() } }

    SettingsHeader {
        id: hd
        anchors.top: parent.top; anchors.left: parent.left; anchors.right: parent.right
        title: qsTr("Folders")
        stack: page.stack
    }

    Flickable {
        anchors.top: hd.bottom; anchors.left: parent.left; anchors.right: parent.right; anchors.bottom: parent.bottom
        clip: true; contentWidth: width; contentHeight: body.implicitHeight + 32
        Column {
            id: body
            x: Math.max(16, (parent.width - width) / 2)
            width: Math.min(parent.width - 32, 620)
            y: 16
            spacing: 8

            Text {
                width: parent.width
                text: qsTr("Show these feed folders in the sidebar")
                color: Theme.accent; font.family: Theme.fontFamily; font.pixelSize: 13; font.bold: true
                wrapMode: Text.WordWrap
                horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
            }
            Rectangle {
                width: parent.width; radius: 10; color: Theme.panel; clip: true; height: c1.implicitHeight
                Column {
                    id: c1; width: parent.width
                    SettingsToggle { id: tgEntertainment; label: qsTr("Entertainment")
                        onToggled: bridge.settingsSetValue("folders", "show_entertainment", value) }
                    SettingsToggle { id: tgSports; label: qsTr("Sports")
                        onToggled: bridge.settingsSetValue("folders", "show_sports", value) }
                    SettingsToggle { id: tgTech;   label: qsTr("Technology")
                        onToggled: bridge.settingsSetValue("folders", "show_technology", value) }
                }
            }

            // ---- Item 7: custom folders that combine channels ----
            Text {
                width: parent.width
                text: qsTr("Custom folders")
                color: Theme.accent; font.family: Theme.fontFamily; font.pixelSize: 13; font.bold: true
                horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
            }
            Text {
                width: parent.width
                text: qsTr("Combine any channels into your own folder. Assign channels from a channel\u2019s right-click menu \u2192 \u201cAdd to folder\u201d.")
                color: Theme.textSecondary; font.family: Theme.fontFamily; font.pixelSize: 12
                wrapMode: Text.WordWrap
                horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
            }

            // Create-folder row
            Rectangle {
                width: parent.width; radius: 10; color: Theme.panel; height: 56
                Row {
                    anchors.fill: parent
                    anchors.leftMargin: 16; anchors.rightMargin: 12
                    spacing: 10
                    LayoutMirroring.enabled: Theme.rtl
                    Rectangle {
                        anchors.verticalCenter: parent.verticalCenter
                        width: parent.width - 118; height: 34; radius: 6
                        color: "transparent"; border.width: 1
                        border.color: newFolderField.activeFocus ? Theme.accent : Theme.divider
                        Behavior on border.color { ColorAnimation { duration: Theme.animFast } }
                        TextField {
                            id: newFolderField
                            anchors.fill: parent; anchors.leftMargin: 8; anchors.rightMargin: 8
                            verticalAlignment: TextInput.AlignVCenter
                            placeholderText: qsTr("New folder name")
                            placeholderTextColor: Theme.textSecondary
                            color: Theme.text; selectionColor: Theme.accent; selectedTextColor: Theme.accentText
                            font.family: Theme.fontFamily; font.pixelSize: 14
                            background: null
                            horizontalAlignment: Theme.rtl ? TextInput.AlignRight : TextInput.AlignLeft
                            onAccepted: page.doCreateFolder()
                        }
                    }
                    Rectangle {
                        anchors.verticalCenter: parent.verticalCenter
                        width: 96; height: 34; radius: 8
                        color: createFolderMouse.containsMouse ? Theme.accent : Theme.bg
                        border.width: 1; border.color: Theme.accent
                        Behavior on color { ColorAnimation { duration: Theme.animFast } }
                        Row {
                            anchors.centerIn: parent; spacing: 6
                            Icon { anchors.verticalCenter: parent.verticalCenter; name: "plus"; size: 14; color: createFolderMouse.containsMouse ? Theme.accentText : Theme.accent }
                            Text { anchors.verticalCenter: parent.verticalCenter; text: qsTr("Create"); color: createFolderMouse.containsMouse ? Theme.accentText : Theme.accent; font.family: Theme.fontFamily; font.pixelSize: 13; font.bold: true }
                        }
                        MouseArea { id: createFolderMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: page.doCreateFolder() }
                    }
                }
            }

            // Existing custom folders
            Rectangle {
                visible: page.customFolders.length > 0
                width: parent.width; radius: 10; color: Theme.panel; clip: true
                height: folderCol.implicitHeight
                Column {
                    id: folderCol; width: parent.width
                    Repeater {
                        model: page.customFolders
                        delegate: Item {
                            required property var modelData
                            readonly property var folder: modelData
                            width: folderCol.width
                            height: fCol.implicitHeight + 16
                            Column {
                                id: fCol
                                x: 16; y: 8
                                width: parent.width - 32
                                spacing: 8
                                Row {
                                    width: parent.width
                                    spacing: 10
                                    LayoutMirroring.enabled: Theme.rtl
                                    Icon { anchors.verticalCenter: parent.verticalCenter; name: "folder"; size: 18; color: Theme.accent }
                                    Rectangle {
                                        anchors.verticalCenter: parent.verticalCenter
                                        width: parent.width - 70; height: 32; radius: 6
                                        color: "transparent"; border.width: 1
                                        border.color: nameField.activeFocus ? Theme.accent : Theme.divider
                                        Behavior on border.color { ColorAnimation { duration: Theme.animFast } }
                                        TextField {
                                            id: nameField
                                            anchors.fill: parent; anchors.leftMargin: 8; anchors.rightMargin: 8
                                            verticalAlignment: TextInput.AlignVCenter
                                            text: folder.name || ""
                                            color: Theme.text; selectionColor: Theme.accent; selectedTextColor: Theme.accentText
                                            font.family: Theme.fontFamily; font.pixelSize: 14
                                            background: null
                                            horizontalAlignment: Theme.rtl ? TextInput.AlignRight : TextInput.AlignLeft
                                            onEditingFinished: if (text.trim() !== "" && text !== folder.name) bridge.renameFolder(folder.id, text.trim())
                                        }
                                    }
                                    Icon {
                                        anchors.verticalCenter: parent.verticalCenter
                                        name: "trash"; size: 16; color: "#ec3942"
                                        MouseArea { anchors.fill: parent; anchors.margins: -6; cursorShape: Qt.PointingHandCursor; onClicked: bridge.deleteFolder(folder.id) }
                                    }
                                }
                                Flow {
                                    width: parent.width
                                    spacing: 6
                                    visible: (folder.channels || []).length > 0
                                    Repeater {
                                        model: folder.channels || []
                                        delegate: Rectangle {
                                            required property var modelData
                                            height: 26; radius: 13
                                            width: chipRow.implicitWidth + 18
                                            color: Theme.bg; border.width: 1; border.color: Theme.divider
                                            Row {
                                                id: chipRow
                                                anchors.centerIn: parent
                                                spacing: 6
                                                Text { anchors.verticalCenter: parent.verticalCenter; text: modelData; color: Theme.text; font.family: Theme.fontFamily; font.pixelSize: 12 }
                                                Icon {
                                                    anchors.verticalCenter: parent.verticalCenter
                                                    name: "close"; size: 11; color: Theme.textSecondary
                                                    MouseArea { anchors.fill: parent; anchors.margins: -4; cursorShape: Qt.PointingHandCursor; onClicked: bridge.removeChannelFromFolder(folder.id, modelData) }
                                                }
                                            }
                                        }
                                    }
                                }
                                Text {
                                    visible: (folder.channels || []).length === 0
                                    width: parent.width
                                    text: qsTr("No channels yet \u2014 add some from a channel\u2019s right-click menu.")
                                    color: Theme.textSecondary; font.family: Theme.fontFamily; font.pixelSize: 12
                                    wrapMode: Text.WordWrap
                                    horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
                                }
                            }
                            Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: Theme.divider; opacity: 0.4 }
                        }
                    }
                }
            }
        }
    }

    Component.onCompleted: {
        var g = bridge.settingsGetGroup("folders")
        tgEntertainment.checked = (g.show_entertainment === undefined) ? true : g.show_entertainment
        tgSports.checked = (g.show_sports === undefined) ? true : g.show_sports
        tgTech.checked   = (g.show_technology === undefined) ? true : g.show_technology
        page.refreshFolders()
    }
}
