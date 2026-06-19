import QtQuick
import QtQuick.Controls
import "../themes"

// Item 7: pick (or create) a custom folder to add a channel to. Opened from
// the chat-row right-click menu via openFor(channelId). Toggling a folder adds
// or removes the channel; the create field makes a new folder and assigns it.
Popup {
    id: dlg
    property string channelId: ""
    property var folders: []

    function openFor(cid) {
        dlg.channelId = cid
        dlg.folders = bridge.getCustomFolders()
        newField.text = ""
        dlg.open()
    }

    function _refresh() { dlg.folders = bridge.getCustomFolders() }

    function _createAndAdd() {
        var n = newField.text.trim()
        if (n === "") return
        var fid = bridge.createFolder(n)
        bridge.addChannelToFolder(fid, dlg.channelId)
        newField.text = ""
        dlg._refresh()
    }

    modal: true
    focus: true
    anchors.centerIn: Overlay.overlay
    width: 360
    padding: 0
    closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside

    background: Rectangle { radius: Theme.radius.lg; color: Theme.panel; border.width: 1; border.color: Theme.divider }

    Connections { target: bridge; function onCustomFoldersChanged() { dlg._refresh() } }

    contentItem: Column {
        spacing: 0

        // Header
        Item {
            width: parent.width; height: 50
            Text {
                anchors.left: parent.left; anchors.leftMargin: 16; anchors.verticalCenter: parent.verticalCenter
                text: qsTr("Add to folder")
                color: Theme.text; font.family: Theme.fontFamily; font.pixelSize: 16; font.bold: true
            }
            Icon {
                anchors.right: parent.right; anchors.rightMargin: 14; anchors.verticalCenter: parent.verticalCenter
                name: "close"; size: 16; color: Theme.textSecondary
                MouseArea { anchors.fill: parent; anchors.margins: -6; cursorShape: Qt.PointingHandCursor; onClicked: dlg.close() }
            }
        }
        Rectangle { width: parent.width; height: 1; color: Theme.divider }

        // Empty hint
        Text {
            visible: dlg.folders.length === 0
            width: parent.width - 32
            x: 16
            topPadding: 12; bottomPadding: 4
            text: qsTr("No folders yet. Create one below.")
            color: Theme.textSecondary; font.family: Theme.fontFamily; font.pixelSize: 13
            wrapMode: Text.WordWrap
            horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
        }

        // Existing folders
        ListView {
            id: lv
            width: parent.width
            height: Math.min(dlg.folders.length, 5) * 44
            visible: dlg.folders.length > 0
            clip: true
            model: dlg.folders
            boundsBehavior: Flickable.StopAtBounds
            ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
            delegate: Item {
                required property var modelData
                width: lv.width
                height: 44
                readonly property bool isIn: (modelData.channels || []).indexOf(dlg.channelId) !== -1
                Rectangle {
                    anchors.fill: parent
                    color: rowMouse.containsMouse ? Theme.hover : "transparent"
                    Behavior on color { ColorAnimation { duration: Theme.animFast } }
                }
                Row {
                    anchors.fill: parent
                    anchors.leftMargin: 16; anchors.rightMargin: 16
                    spacing: 10
                    LayoutMirroring.enabled: Theme.rtl
                    Icon { anchors.verticalCenter: parent.verticalCenter; name: "folder"; size: 16; color: Theme.accent }
                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        width: parent.width - 70
                        text: modelData.name || qsTr("Folder")
                        color: Theme.text; font.family: Theme.fontFamily; font.pixelSize: 14
                        elide: Text.ElideRight
                        horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
                    }
                    Icon {
                        anchors.verticalCenter: parent.verticalCenter
                        visible: parent.parent.isIn
                        name: "check"; size: 16; color: Theme.accent
                    }
                }
                MouseArea {
                    id: rowMouse
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        if (parent.isIn) bridge.removeChannelFromFolder(modelData.id, dlg.channelId)
                        else bridge.addChannelToFolder(modelData.id, dlg.channelId)
                        dlg._refresh()
                    }
                }
            }
        }

        Rectangle { visible: dlg.folders.length > 0; width: parent.width; height: 1; color: Theme.divider }

        // Create new folder
        Item {
            width: parent.width; height: 60
            Row {
                anchors.fill: parent
                anchors.leftMargin: 16; anchors.rightMargin: 16
                spacing: 10
                LayoutMirroring.enabled: Theme.rtl
                Rectangle {
                    anchors.verticalCenter: parent.verticalCenter
                    width: parent.width - 92; height: 34; radius: Theme.radius.md
                    color: "transparent"; border.width: 1
                    border.color: newField.activeFocus ? Theme.accent : Theme.divider
                    Behavior on border.color { ColorAnimation { duration: Theme.animFast } }
                    TextField {
                        id: newField
                        anchors.fill: parent; anchors.leftMargin: 8; anchors.rightMargin: 8
                        verticalAlignment: TextInput.AlignVCenter
                        placeholderText: qsTr("New folder\u2026")
                        placeholderTextColor: Theme.textSecondary
                        color: Theme.text; selectionColor: Theme.accent; selectedTextColor: Theme.accentText
                        font.family: Theme.fontFamily; font.pixelSize: 14
                        background: null
                        horizontalAlignment: Theme.rtl ? TextInput.AlignRight : TextInput.AlignLeft
                        onAccepted: dlg._createAndAdd()
                    }
                }
                Rectangle {
                    anchors.verticalCenter: parent.verticalCenter
                    width: 76; height: 34; radius: Theme.radius.sm
                    color: createMouse.containsMouse ? Theme.accent : Theme.bg
                    border.width: 1; border.color: Theme.accent
                    Behavior on color { ColorAnimation { duration: Theme.animFast } }
                    Row {
                        anchors.centerIn: parent; spacing: 6
                        Icon { anchors.verticalCenter: parent.verticalCenter; name: "plus"; size: 14; color: createMouse.containsMouse ? Theme.accentText : Theme.accent }
                        Text { anchors.verticalCenter: parent.verticalCenter; text: qsTr("Add"); color: createMouse.containsMouse ? Theme.accentText : Theme.accent; font.family: Theme.fontFamily; font.pixelSize: 13; font.bold: true }
                    }
                    MouseArea { id: createMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: dlg._createAndAdd() }
                }
            }
        }
    }
}
