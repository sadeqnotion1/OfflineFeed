import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../themes"

// Offline reader overlay (restores the old web app's "Read Offline" mode).
//
// Flow: open(url, title) makes the overlay visible in a loading state and asks
// the bridge to fetch the cached/scraped article. bridge.articleBlocksLoaded
// then arrives with { title, blocks:[{type:'p'|'h'|'img'|'quote', content, level?}] }
// (or { error }). We render the blocks into a scrollable, readable column.
Rectangle {
    id: reader
    color: Theme.bg
    visible: opacity > 0.001
    opacity: shown ? 1 : 0
    Behavior on opacity { NumberAnimation { duration: Theme.anim; easing.type: Theme.easing } }

    property bool shown: false
    property string currentUrl: ""
    property string articleTitle: ""
    property string fallbackText: ""
    property bool loading: false
    property string errorText: ""
    property var blocks: []

    function open(url, title, fallback) {
        reader.currentUrl = url
        reader.articleTitle = title || ""
        reader.fallbackText = fallback || ""
        reader.blocks = []
        reader.errorText = ""
        reader.loading = true
        reader.shown = true
        bridge.openArticle(url)
    }
    function close() { reader.shown = false }

    // Block incoming clicks from reaching the panes underneath.
    MouseArea { anchors.fill: parent; hoverEnabled: true; acceptedButtons: Qt.AllButtons }

    Connections {
        target: bridge
        function onArticleBlocksLoaded(url, data) {
            if (!reader.shown || url !== reader.currentUrl)
                return
            reader.loading = false
            if (data && data.error) {
                // Fall back to the post's own text so there is always something
                // readable in-app, even when the backend can't scrape the page.
                if (reader.fallbackText !== "") {
                    reader.errorText = ""
                    reader.blocks = [{ "type": "p", "content": reader.fallbackText }]
                } else {
                    reader.errorText = data.error
                    reader.blocks = []
                }
                return
            }
            if (data && data.title && reader.articleTitle === "")
                reader.articleTitle = data.title
            var bl = (data && data.blocks) ? data.blocks : []
            if (bl.length === 0 && reader.fallbackText !== "")
                bl = [{ "type": "p", "content": reader.fallbackText }]
            reader.blocks = bl
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // ---- Header ----
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: Theme.headerHeight
            color: Theme.panel
            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 14
                anchors.rightMargin: 14
                spacing: 12
                LayoutMirroring.enabled: Theme.rtl

                Icon {
                    name: "back"; size: 20; color: Theme.textSecondary
                    MouseArea {
                        anchors.fill: parent; anchors.margins: -8
                        cursorShape: Qt.PointingHandCursor
                        onClicked: reader.close()
                    }
                }
                Text {
                    Layout.fillWidth: true
                    text: reader.articleTitle !== "" ? reader.articleTitle : qsTr("Offline reader")
                    color: Theme.text
                    font.family: Theme.fontFamily
                    font.pixelSize: 16
                    font.bold: true
                    elide: Text.ElideRight
                }
                Icon {
                    name: "external"; size: 19; color: Theme.textSecondary
                    visible: reader.currentUrl !== ""
                    MouseArea {
                        anchors.fill: parent; anchors.margins: -8
                        cursorShape: Qt.PointingHandCursor
                        onClicked: bridge.openExternal(reader.currentUrl)
                    }
                }
                Icon {
                    name: "close"; size: 19; color: Theme.textSecondary
                    MouseArea {
                        anchors.fill: parent; anchors.margins: -8
                        cursorShape: Qt.PointingHandCursor
                        onClicked: reader.close()
                    }
                }
            }
            Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: Theme.divider }
        }

        // ---- Body ----
        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true

            // Loading state
            ColumnLayout {
                anchors.centerIn: parent
                spacing: 14
                visible: reader.loading
                BusyIndicator { Layout.alignment: Qt.AlignHCenter; running: reader.loading }
                Text {
                    Layout.alignment: Qt.AlignHCenter
                    text: qsTr("Loading article\u2026")
                    color: Theme.textSecondary
                    font.family: Theme.fontFamily
                    font.pixelSize: 14
                }
            }

            // Error state
            ColumnLayout {
                anchors.centerIn: parent
                width: Math.min(parent.width - 80, 420)
                spacing: 10
                visible: !reader.loading && reader.errorText !== ""
                Icon { Layout.alignment: Qt.AlignHCenter; name: "info"; size: 30; color: Theme.textSecondary }
                Text {
                    Layout.alignment: Qt.AlignHCenter
                    text: qsTr("Offline reader error")
                    color: Theme.text
                    font.family: Theme.fontFamily
                    font.pixelSize: 15
                    font.bold: true
                }
                Text {
                    Layout.fillWidth: true
                    horizontalAlignment: Text.AlignHCenter
                    text: reader.errorText
                    color: Theme.textSecondary
                    font.family: Theme.fontFamily
                    font.pixelSize: 13
                    wrapMode: Text.WordWrap
                }
                Button {
                    Layout.alignment: Qt.AlignHCenter
                    text: qsTr("Open in browser")
                    onClicked: bridge.openExternal(reader.currentUrl)
                }
            }

            // Article content
            Flickable {
                id: flick
                anchors.fill: parent
                contentWidth: width
                contentHeight: bodyCol.implicitHeight + 80
                clip: true
                boundsBehavior: Flickable.StopAtBounds
                visible: !reader.loading && reader.errorText === ""
                ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }

                Column {
                    id: bodyCol
                    x: Math.max(20, (flick.width - 720) / 2)
                    y: 28
                    width: Math.min(flick.width - 40, 720)
                    spacing: 16

                    Text {
                        width: parent.width
                        visible: reader.articleTitle !== ""
                        text: reader.articleTitle
                        color: Theme.text
                        font.family: Theme.readerFontFamily
                        font.pixelSize: 26
                        font.bold: true
                        wrapMode: Text.WordWrap
                        horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
                    }

                    Repeater {
                        model: reader.blocks
                        delegate: Column {
                            width: bodyCol.width
                            property var block: modelData

                            // Heading
                            Text {
                                width: parent.width
                                visible: block && block.type === "h"
                                text: block ? (block.content || "") : ""
                                textFormat: Text.RichText
                                color: Theme.text
                                font.family: Theme.readerFontFamily
                                font.pixelSize: 20
                                font.bold: true
                                wrapMode: Text.WordWrap
                                horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
                            }
                            // Paragraph
                            Text {
                                width: parent.width
                                visible: block && block.type === "p"
                                text: block ? (block.content || "") : ""
                                textFormat: Text.RichText
                                color: Qt.rgba(Theme.text.r, Theme.text.g, Theme.text.b, 0.92)
                                font.family: Theme.readerFontFamily
                                font.pixelSize: 17
                                lineHeight: 1.55
                                wrapMode: Text.WordWrap
                                horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
                                onLinkActivated: function(link) { bridge.openExternal(link) }
                            }
                            // Image
                            Image {
                                visible: block && block.type === "img" && status === Image.Ready
                                source: (block && block.type === "img") ? (block.content || "") : ""
                                width: parent.width
                                fillMode: Image.PreserveAspectFit
                                asynchronous: true
                                cache: true
                            }
                            // Quote
                            Row {
                                width: parent.width
                                spacing: 12
                                visible: block && block.type === "quote"
                                Rectangle { width: 3; height: parent.height; radius: 2; color: Theme.accent }
                                Text {
                                    width: parent.width - 15
                                    text: block ? (block.content || "") : ""
                                    textFormat: Text.RichText
                                    color: Theme.textSecondary
                                    font.family: Theme.readerFontFamily
                                    font.pixelSize: 16
                                    font.italic: true
                                    lineHeight: 1.5
                                    wrapMode: Text.WordWrap
                                }
                            }
                        }
                    }

                    // Empty state (loaded but no extractable blocks)
                    Text {
                        width: parent.width
                        visible: !reader.loading && reader.errorText === "" && (!reader.blocks || reader.blocks.length === 0)
                        text: qsTr("No readable content was extracted for this article. Try opening it in your browser.")
                        color: Theme.textSecondary
                        font.family: Theme.fontFamily
                        font.pixelSize: 15
                        wrapMode: Text.WordWrap
                    }
                }
            }
        }
    }
}
