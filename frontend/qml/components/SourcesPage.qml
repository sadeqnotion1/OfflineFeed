import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import "../themes"

// Settings > News Sources
//
// Single add, batch paste add, and OPML import for custom feeds. Also lists the
// existing custom sources with an inline Edit and Remove action. Everything goes
// through the existing ChatBridge slots so no backend behaviour is duplicated.
Item {
    id: page
    property var stack: null
    anchors.fill: parent

    function _section() { return sectionCombo.value || "Entertainment" }
    function _category() { return (categoryField.text && categoryField.text.length) ? categoryField.text : "General" }

    function addSingle() {
        var u = singleUrl.text.trim()
        if (u.length === 0)
            return
        bridge.addCustomSource(singleName.text.trim(), u, page._section(), page._category())
        singleName.text = ""
        singleUrl.text = ""
    }

    function addBatch() {
        if (batchBox.text.trim().length === 0)
            return
        bridge.addCustomSourcesBatch(batchBox.text, page._section(), page._category())
        batchBox.text = ""
    }

    SettingsHeader {
        id: hd
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        title: qsTr("News Sources")
        stack: page.stack
    }

    ScrollView {
        anchors.top: hd.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        contentWidth: availableWidth
        clip: true

        Column {
            id: body
            x: Math.max(16, (parent.width - width) / 2)
            width: Math.min(parent.width - 32, 620)
            y: 16
            spacing: 20

            // ---- Defaults Section ----
            Text {
                width: parent.width
                text: qsTr("Defaults for new sources")
                color: Theme.accent; font.bold: true; font.family: Theme.fontFamily; font.pixelSize: 13
                horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
            }
            Rectangle {
                width: parent.width
                radius: Theme.radius.lg
                color: Theme.panel
                height: defaultsCol.implicitHeight + 24
                Column {
                    id: defaultsCol
                    x: 16; y: 12
                    width: parent.width - 32
                    spacing: 12

                    LabeledCombo {
                        id: sectionCombo
                        label: qsTr("Section")
                        options: ["Entertainment", "Sports", "Technology"]
                        width: parent.width
                    }

                    RowLayout {
                        width: parent.width
                        spacing: 10
                        Text {
                            text: qsTr("Category")
                            color: Theme.text; font.family: Theme.fontFamily; font.pixelSize: 14
                            Layout.preferredWidth: 120
                        }
                        TextField {
                            id: categoryField
                            Layout.fillWidth: true
                            text: "General"
                            color: Theme.text
                            selectByMouse: true
                            font.family: Theme.fontFamily; font.pixelSize: 14
                            background: Rectangle { color: Theme.bg; radius: Theme.radius.md; border.color: Theme.divider; border.width: 1 }
                        }
                    }
                }
            }

            // ---- Single Add Section ----
            Text {
                width: parent.width
                text: qsTr("Add a single source")
                color: Theme.accent; font.bold: true; font.family: Theme.fontFamily; font.pixelSize: 13
                horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
            }
            Rectangle {
                width: parent.width
                radius: Theme.radius.lg
                color: Theme.panel
                height: singleCol.implicitHeight + 24
                Column {
                    id: singleCol
                    x: 16; y: 12
                    width: parent.width - 32
                    spacing: 12

                    Text {
                        width: parent.width
                        text: qsTr("RSS URL, website URL, Telegram link, or Twitter/X @handle:")
                        color: Theme.textSecondary; font.family: Theme.fontFamily; font.pixelSize: 12
                        wrapMode: Text.WordWrap
                    }

                    TextField {
                        id: singleName
                        width: parent.width
                        placeholderText: qsTr("Name (optional \u2014 auto-detected if blank)")
                        color: Theme.text
                        selectByMouse: true
                        font.family: Theme.fontFamily; font.pixelSize: 14
                        background: Rectangle { color: Theme.bg; radius: Theme.radius.md; border.color: Theme.divider; border.width: 1 }
                    }

                    RowLayout {
                        width: parent.width
                        spacing: 10
                        TextField {
                            id: singleUrl
                            Layout.fillWidth: true
                            placeholderText: qsTr("https://site.com/feed   \u00b7   @handle   \u00b7   https://t.me/s/channel")
                            color: Theme.text
                            selectByMouse: true
                            font.family: Theme.fontFamily; font.pixelSize: 14
                            background: Rectangle { color: Theme.bg; radius: Theme.radius.md; border.color: Theme.divider; border.width: 1 }
                            onAccepted: page.addSingle()
                        }
                        PillButton {
                            text: qsTr("Add")
                            onClicked: page.addSingle()
                        }
                    }
                }
            }

            // ---- Batch Add Section ----
            Text {
                width: parent.width
                text: qsTr("Batch add")
                color: Theme.accent; font.bold: true; font.family: Theme.fontFamily; font.pixelSize: 13
                horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
            }
            Rectangle {
                width: parent.width
                radius: Theme.radius.lg
                color: Theme.panel
                height: batchCol.implicitHeight + 24
                Column {
                    id: batchCol
                    x: 16; y: 12
                    width: parent.width - 32
                    spacing: 12

                    Text {
                        width: parent.width
                        text: qsTr("One feed per line. Accepts a URL/@handle, or \"Name | url\" / \"Name, url\". Lines starting with # are ignored.")
                        color: Theme.textSecondary; font.family: Theme.fontFamily; font.pixelSize: 12
                        wrapMode: Text.WordWrap
                    }

                    Rectangle {
                        width: parent.width
                        height: 120
                        color: Theme.bg; radius: Theme.radius.md; border.color: Theme.divider; border.width: 1
                        ScrollView {
                            anchors.fill: parent
                            anchors.margins: 6
                            clip: true
                            TextArea {
                                id: batchBox
                                wrapMode: TextEdit.WrapAnywhere
                                selectByMouse: true
                                placeholderText: qsTr("@FabrizioRomano\nThe Verge | https://www.theverge.com/rss/index.xml\nhttps://t.me/s/durov")
                                color: Theme.text
                                font.family: Theme.fontFamily; font.pixelSize: 13
                                background: null
                            }
                        }
                    }

                    PillButton {
                        text: qsTr("Add all")
                        onClicked: page.addBatch()
                    }
                }
            }

            // ---- OPML Import Section ----
            Text {
                width: parent.width
                text: qsTr("Import OPML")
                color: Theme.accent; font.bold: true; font.family: Theme.fontFamily; font.pixelSize: 13
                horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
            }
            Rectangle {
                width: parent.width
                radius: Theme.radius.lg
                color: Theme.panel
                height: opmlCol.implicitHeight + 24
                Column {
                    id: opmlCol
                    x: 16; y: 12
                    width: parent.width - 32
                    spacing: 12

                    Text {
                        width: parent.width
                        text: qsTr("Import every feed from an OPML file exported by another RSS reader.")
                        color: Theme.textSecondary; font.family: Theme.fontFamily; font.pixelSize: 12
                        wrapMode: Text.WordWrap
                    }

                    PillButton {
                        text: qsTr("Import OPML\u2026")
                        onClicked: opmlDialog.open()
                    }
                }
            }

            // ---- Custom Sources List Section ----
            Text {
                width: parent.width
                text: qsTr("Your custom sources")
                color: Theme.accent; font.bold: true; font.family: Theme.fontFamily; font.pixelSize: 13
                horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
            }

            Column {
                width: parent.width
                spacing: 8

                Text {
                    visible: sourcesRepeater.count === 0
                    width: parent.width
                    text: qsTr("No custom sources yet. Add one above.")
                    color: Theme.textSecondary; font.family: Theme.fontFamily; font.pixelSize: 13
                    horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
                }

                Repeater {
                    id: sourcesRepeater
                    model: sourcesModel
                    delegate: Rectangle {
                        id: row
                        width: page.width - 32 > 620 ? 620 : page.width - 32
                        color: Theme.panel; radius: Theme.radius.lg
                        implicitHeight: rowStack.implicitHeight + 20

                        property bool editing: false

                        StackLayout {
                            id: rowStack
                            anchors.fill: parent
                            anchors.margins: 10
                            currentIndex: row.editing ? 1 : 0

                            // 0: Display Mode
                            RowLayout {
                                spacing: 10
                                Rectangle {
                                    Layout.preferredWidth: 36; Layout.preferredHeight: 36
                                    radius: Theme.radius.pill; color: Theme.accent
                                    Text {
                                        anchors.centerIn: parent
                                        text: model.name ? model.name.charAt(0).toUpperCase() : "?"
                                        color: "white"; font.pixelSize: 16; font.bold: true
                                    }
                                }
                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: 2
                                    Text {
                                        text: model.name ? model.name : ""; color: Theme.text
                                        font.family: Theme.fontFamily; font.pixelSize: 14; font.bold: true
                                        elide: Text.ElideRight; Layout.fillWidth: true
                                    }
                                    Text {
                                        text: (model.section || "") +
                                              (model.category ? "  •  " + model.category : "") +
                                              "  —  " + (model.url || "")
                                        color: Theme.textSecondary; font.family: Theme.fontFamily; font.pixelSize: 11
                                        elide: Text.ElideRight; Layout.fillWidth: true
                                    }
                                }
                                PillButton {
                                    text: qsTr("Edit")
                                    onClicked: {
                                        editName.text = model.name
                                        editUrl.text = model.url
                                        editCategory.text = model.category || ""
                                        var idx = ["Entertainment", "Sports", "Technology"].indexOf(model.section)
                                        editSection.currentIndex = idx >= 0 ? idx : 0
                                        row.editing = true
                                    }
                                }
                                PillButton {
                                    text: qsTr("Remove")
                                    onClicked: bridge.deleteCustomSource(model.name ? model.name : "", model.url ? model.url : "")
                                }
                            }

                            // 1: Edit Mode
                            ColumnLayout {
                                spacing: 8
                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: 8
                                    TextField {
                                        id: editName
                                        Layout.fillWidth: true
                                        placeholderText: qsTr("Name")
                                        color: Theme.text
                                        selectByMouse: true
                                        font.family: Theme.fontFamily; font.pixelSize: 14
                                        background: Rectangle { color: Theme.bg; radius: Theme.radius.md; border.color: Theme.divider; border.width: 1 }
                                    }
                                    TextField {
                                        id: editUrl
                                        Layout.fillWidth: true
                                        placeholderText: qsTr("Feed / site URL")
                                        color: Theme.text
                                        selectByMouse: true
                                        font.family: Theme.fontFamily; font.pixelSize: 14
                                        background: Rectangle { color: Theme.bg; radius: Theme.radius.md; border.color: Theme.divider; border.width: 1 }
                                    }
                                }
                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: 8
                                    ComboBox {
                                        id: editSection
                                        model: ["Entertainment", "Sports", "Technology"]
                                    }
                                    TextField {
                                        id: editCategory
                                        Layout.fillWidth: true
                                        placeholderText: qsTr("Category (optional)")
                                        color: Theme.text
                                        selectByMouse: true
                                        font.family: Theme.fontFamily; font.pixelSize: 14
                                        background: Rectangle { color: Theme.bg; radius: Theme.radius.md; border.color: Theme.divider; border.width: 1 }
                                    }
                                    PillButton {
                                        text: qsTr("Save")
                                        enabled: editName.text.trim().length > 0 && editUrl.text.trim().length > 0
                                        onClicked: {
                                            bridge.updateCustomSource(model.name, editName.text.trim(),
                                                                      editUrl.text.trim(), editSection.currentText,
                                                                      editCategory.text.trim())
                                            row.editing = false
                                        }
                                    }
                                    PillButton {
                                        text: qsTr("Cancel")
                                        onClicked: row.editing = false
                                    }
                                }
                            }
                        }
                    }
                }
            }

            // Extra spacing at the bottom
            Item {
                width: parent.width
                height: 16
            }
        }
    }

    FileDialog {
        id: opmlDialog
        title: qsTr("Choose an OPML file")
        nameFilters: ["OPML files (*.opml *.xml)", "All files (*)"]
        onAccepted: bridge.importOpml(opmlDialog.selectedFile)
    }
}
