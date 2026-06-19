import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import "../themes"

// Settings > News Sources
//
// Single add, batch paste add, and OPML import for custom feeds. Also lists the
// existing custom sources with a Remove action. Everything goes through the
// existing ChatBridge slots so no backend behaviour is duplicated:
//   bridge.addCustomSource(name, url, section, category)
//   bridge.addCustomSourcesBatch(blob, section, category)
//   bridge.importOpml(fileUrl)
//   bridge.deleteCustomSource(name, url)   (reused; not duplicated)
Item {
    id: root

    function _section() { return sectionCombo.value || "Entertainment" }
    function _category() { return (categoryField.text && categoryField.text.length) ? categoryField.text : "General" }

    function addSingle() {
        var u = singleUrl.text.trim()
        if (u.length === 0)
            return
        bridge.addCustomSource(singleName.text.trim(), u, root._section(), root._category())
        singleName.text = ""
        singleUrl.text = ""
    }

    function addBatch() {
        if (batchBox.text.trim().length === 0)
            return
        bridge.addCustomSourcesBatch(batchBox.text, root._section(), root._category())
        batchBox.text = ""
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // ---- Header (matches the other settings panes) ----
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: Theme.headerHeight
            color: Theme.panel

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 12
                anchors.rightMargin: 12
                spacing: 12

                Icon {
                    name: "back"
                    size: 20
                    color: Theme.text
                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: settingsStack.pop()
                    }
                }

                Text {
                    text: qsTr("News Sources")
                    color: Theme.text
                    font.family: Theme.fontFamily; font.pixelSize: 18; font.bold: true
                    Layout.fillWidth: true
                }
            }
            Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: Theme.divider }
        }

        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            contentWidth: availableWidth
            clip: true

            ColumnLayout {
                width: parent.width
                Layout.margins: 20
                spacing: 16

                // ---- shared defaults ----
                Text {
                    text: qsTr("Defaults for new sources")
                    color: Theme.accent; font.bold: true; font.family: Theme.fontFamily; font.pixelSize: 14
                }
                LabeledCombo {
                    id: sectionCombo
                    label: qsTr("Section")
                    options: ["Entertainment", "Sports", "Technology"]
                    Layout.fillWidth: true
                }
                RowLayout {
                    Layout.fillWidth: true
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
                        background: Rectangle { color: Theme.bg; radius: 6; border.color: Theme.divider; border.width: 1 }
                    }
                }

                Rectangle { Layout.fillWidth: true; height: 1; color: Theme.divider }

                // ---- single add ----
                Text {
                    text: qsTr("Add a source")
                    color: Theme.accent; font.bold: true; font.family: Theme.fontFamily; font.pixelSize: 14
                }
                Text {
                    text: qsTr("RSS URL, a site URL, a Telegram link, or a Twitter/X @handle.")
                    color: Theme.textSecondary; font.family: Theme.fontFamily; font.pixelSize: 12
                    Layout.fillWidth: true; wrapMode: Text.WordWrap
                }
                TextField {
                    id: singleName
                    Layout.fillWidth: true
                    placeholderText: qsTr("Name (optional \u2014 auto-detected if blank)")
                    color: Theme.text
                    selectByMouse: true
                    font.family: Theme.fontFamily; font.pixelSize: 14
                    background: Rectangle { color: Theme.bg; radius: 6; border.color: Theme.divider; border.width: 1 }
                }
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10
                    TextField {
                        id: singleUrl
                        Layout.fillWidth: true
                        placeholderText: qsTr("https://site.com/feed   \u00b7   @handle   \u00b7   https://t.me/s/channel")
                        color: Theme.text
                        selectByMouse: true
                        font.family: Theme.fontFamily; font.pixelSize: 14
                        background: Rectangle { color: Theme.bg; radius: 6; border.color: Theme.divider; border.width: 1 }
                        onAccepted: root.addSingle()
                    }
                    PillButton {
                        text: qsTr("Add")
                        onClicked: root.addSingle()
                    }
                }

                Rectangle { Layout.fillWidth: true; height: 1; color: Theme.divider }

                // ---- batch add ----
                Text {
                    text: qsTr("Batch add")
                    color: Theme.accent; font.bold: true; font.family: Theme.fontFamily; font.pixelSize: 14
                }
                Text {
                    text: qsTr("One feed per line. Accepts a URL/@handle, or \"Name | url\" / \"Name, url\". Lines starting with # are ignored.")
                    color: Theme.textSecondary; font.family: Theme.fontFamily; font.pixelSize: 12
                    Layout.fillWidth: true; wrapMode: Text.WordWrap
                }
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 150
                    color: Theme.bg; radius: 6; border.color: Theme.divider; border.width: 1
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
                    onClicked: root.addBatch()
                }

                Rectangle { Layout.fillWidth: true; height: 1; color: Theme.divider }

                // ---- OPML import ----
                Text {
                    text: qsTr("Import OPML")
                    color: Theme.accent; font.bold: true; font.family: Theme.fontFamily; font.pixelSize: 14
                }
                Text {
                    text: qsTr("Import every feed from an OPML file exported by another RSS reader.")
                    color: Theme.textSecondary; font.family: Theme.fontFamily; font.pixelSize: 12
                    Layout.fillWidth: true; wrapMode: Text.WordWrap
                }
                PillButton {
                    text: qsTr("Import OPML\u2026")
                    onClicked: opmlDialog.open()
                }

                Rectangle { Layout.fillWidth: true; height: 1; color: Theme.divider }

                // ---- existing custom sources ----
                Text {
                    text: qsTr("Your custom sources")
                    color: Theme.accent; font.bold: true; font.family: Theme.fontFamily; font.pixelSize: 14
                }
                Text {
                    visible: sourcesRepeater.count === 0
                    text: qsTr("No custom sources yet. Add one above.")
                    color: Theme.textSecondary; font.family: Theme.fontFamily; font.pixelSize: 13
                }
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 8
                    Repeater {
                        id: sourcesRepeater
                        model: sourcesModel
                        delegate: Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 54
                            color: Theme.panel; radius: 8
                            RowLayout {
                                anchors.fill: parent
                                anchors.leftMargin: 12
                                anchors.rightMargin: 12
                                spacing: 10
                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: 2
                                    Text {
                                        text: model.name ? model.name : ""
                                        color: Theme.text; font.family: Theme.fontFamily; font.pixelSize: 14; font.bold: true
                                        elide: Text.ElideRight; Layout.fillWidth: true
                                    }
                                    Text {
                                        text: model.url ? model.url : ""
                                        color: Theme.textSecondary; font.family: Theme.fontFamily; font.pixelSize: 11
                                        elide: Text.ElideRight; Layout.fillWidth: true
                                    }
                                }
                                PillButton {
                                    text: qsTr("Remove")
                                    onClicked: bridge.deleteCustomSource(model.name ? model.name : "", model.url ? model.url : "")
                                }
                            }
                        }
                    }
                }
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
