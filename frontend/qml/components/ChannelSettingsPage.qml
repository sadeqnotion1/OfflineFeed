import QtQuick
import QtQuick.Controls
import "../themes"

// MERGED "Channel Settings" page (the yellow group): combines the former
// Feed & Chat Settings and Folders pages into ONE screen, separated by rich
// icon section headers (SettingsSectionHeader). Every backend call is preserved
// VERBATIM from the two original pages -- no bridge behavior is changed:
//   - Feed:      bridge.settingsGetGroup("feed")    / settingsSetValue("feed", ...)
//   - Wallpaper: bridge.wallpaperMode / wallpaperImage / pickWallpaperImage()
//   - Folders:   bridge.settingsGetGroup("folders") + custom-folder bridge API
Item {
    id: page
    property var stack: null
    anchors.fill: parent

    // Custom folders that combine channels (from the former Folders page).
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
        title: qsTr("Channel Settings")
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
            spacing: 14

            // ===================== Reader =====================
            SettingsSectionHeader {
                width: parent.width
                iconName: "chat"; tileColor: "#3390ec"
                title: qsTr("Reader")
            }
            Rectangle {
                width: parent.width; radius: Theme.radius.lg; color: Theme.panel; clip: true; height: cReader.implicitHeight
                Column {
                    id: cReader; width: parent.width
                    SettingsSelect {
                        id: selReader
                        label: qsTr("Reader mode")
                        options: [ { value: "readable", label: qsTr("Readable") }, { value: "original", label: qsTr("Original HTML") } ]
                        onActivatedValue: bridge.settingsSetValue("feed", "reader_mode", value)
                    }
                    SettingsToggle {
                        id: tgScrape
                        label: qsTr("Scraping fallback"); description: qsTr("Fetch the full article when the RSS body is truncated")
                        onToggled: bridge.settingsSetValue("feed", "scrape_fallback", value)
                    }
                    SettingsToggle {
                        id: tgImages
                        label: qsTr("Auto-load images")
                        onToggled: bridge.settingsSetValue("feed", "images_autoload", value)
                    }
                    SettingsToggle {
                        id: tgExternal
                        label: qsTr("Open links in external browser")
                        onToggled: bridge.settingsSetValue("feed", "open_external", value)
                    }
                }
            }

            // ===================== Chat (wallpaper) =====================
            SettingsSectionHeader {
                width: parent.width
                iconName: "image"; tileColor: "#9b6dff"
                title: qsTr("Chat")
            }
            Rectangle {
                width: parent.width; radius: Theme.radius.lg; color: Theme.panel; clip: true; height: cChat.implicitHeight
                Column {
                    id: cChat; width: parent.width
                    SettingsSelect {
                        id: selWall
                        label: qsTr("Chat wallpaper")
                        options: [ { value: "pattern", label: qsTr("Pattern") }, { value: "solid", label: qsTr("Solid") }, { value: "image", label: qsTr("Custom image") }, { value: "none", label: qsTr("None") } ]
                        value: bridge.wallpaperMode
                        onActivatedValue: bridge.wallpaperMode = value
                    }
                }
            }
            // Chat-wallpaper image picker, wired to the SAME bridge.wallpaperMode /
            // bridge.wallpaperImage state used by Appearance.
            Rectangle {
                width: parent.width; radius: Theme.radius.lg; color: Theme.panel; height: wallRow.implicitHeight + 24
                Row {
                    id: wallRow
                    x: 16; y: 12
                    width: parent.width - 32
                    spacing: 12
                    LayoutMirroring.enabled: Theme.rtl
                    Column {
                        width: parent.width - 150
                        spacing: 2
                        Text {
                            width: parent.width
                            text: qsTr("Custom wallpaper image")
                            color: Theme.text; font.family: Theme.fontFamily; font.pixelSize: 15
                            horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
                        }
                        Text {
                            width: parent.width
                            text: bridge.wallpaperImage !== ""
                                  ? qsTr("An image is set. Pick \u201cCustom image\u201d above to show it.")
                                  : qsTr("Pick an image from your computer to use as the chat background.")
                            color: Theme.textSecondary; font.family: Theme.fontFamily; font.pixelSize: 12
                            wrapMode: Text.WordWrap
                            horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
                        }
                    }
                    Rectangle {
                        anchors.verticalCenter: parent.verticalCenter
                        width: 130; height: 34; radius: Theme.radius.sm
                        color: chooseMouse.containsMouse ? Theme.accent : Theme.bg
                        border.width: 1; border.color: Theme.accent
                        Behavior on color { ColorAnimation { duration: Theme.animFast } }
                        Row {
                            anchors.centerIn: parent
                            spacing: 6
                            Icon { anchors.verticalCenter: parent.verticalCenter; name: "image"; size: 15; color: chooseMouse.containsMouse ? Theme.accentText : Theme.accent }
                            Text {
                                anchors.verticalCenter: parent.verticalCenter
                                text: qsTr("Choose image")
                                color: chooseMouse.containsMouse ? Theme.accentText : Theme.accent
                                font.family: Theme.fontFamily; font.pixelSize: 13; font.bold: true
                            }
                        }
                        MouseArea {
                            id: chooseMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: bridge.pickWallpaperImage()
                        }
                    }
                }
            }

            // ===================== Feed folders =====================
            SettingsSectionHeader {
                width: parent.width
                iconName: "folder"; tileColor: "#4dcd5e"
                title: qsTr("Feed folders")
                subtitle: qsTr("Show these feed folders in the sidebar")
            }
            Rectangle {
                width: parent.width; radius: Theme.radius.lg; color: Theme.panel; clip: true; height: cFolders.implicitHeight
                Column {
                    id: cFolders; width: parent.width
                    SettingsToggle { id: tgEntertainment; label: qsTr("Entertainment")
                        onToggled: bridge.settingsSetValue("folders", "show_entertainment", value) }
                    SettingsToggle { id: tgSports; label: qsTr("Sports")
                        onToggled: bridge.settingsSetValue("folders", "show_sports", value) }
                    SettingsToggle { id: tgTech;   label: qsTr("Technology")
                        onToggled: bridge.settingsSetValue("folders", "show_technology", value) }
                }
            }

            // ===================== Custom folders =====================
            SettingsSectionHeader {
                width: parent.width
                iconName: "folder"; tileColor: "#f5a623"
                title: qsTr("Custom folders")
                subtitle: qsTr("Combine any channels into your own folder. Assign channels from a channel\u2019s right-click menu \u2192 \u201cAdd to folder\u201d.")
            }
            // Create-folder row
            Rectangle {
                width: parent.width; radius: Theme.radius.lg; color: Theme.panel; height: 56
                Row {
                    anchors.fill: parent
                    anchors.leftMargin: 16; anchors.rightMargin: 12
                    spacing: 10
                    LayoutMirroring.enabled: Theme.rtl
                    Rectangle {
                        anchors.verticalCenter: parent.verticalCenter
                        width: parent.width - 118; height: 34; radius: Theme.radius.md
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
                        width: 96; height: 34; radius: Theme.radius.sm
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
                width: parent.width; radius: Theme.radius.lg; color: Theme.panel; clip: true
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
                                        width: parent.width - 70; height: 32; radius: Theme.radius.md
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
                                            height: 26; radius: Theme.radius.pill
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
        var g = bridge.settingsGetGroup("feed")
        selReader.value     = (g.reader_mode === undefined) ? "readable" : g.reader_mode
        tgScrape.checked    = (g.scrape_fallback === undefined) ? true : g.scrape_fallback
        tgImages.checked    = (g.images_autoload === undefined) ? true : g.images_autoload
        tgExternal.checked  = (g.open_external === undefined) ? false : g.open_external
        var f = bridge.settingsGetGroup("folders")
        tgEntertainment.checked = (f.show_entertainment === undefined) ? true : f.show_entertainment
        tgSports.checked = (f.show_sports === undefined) ? true : f.show_sports
        tgTech.checked   = (f.show_technology === undefined) ? true : f.show_technology
        page.refreshFolders()
    }
}
