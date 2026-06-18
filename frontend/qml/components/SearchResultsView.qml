import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../themes"

Rectangle {
    id: root
    color: Theme.bg

    signal readArticleRequested(string url, string title, string fallbackText)

    ColumnLayout {
        anchors.fill: parent
        spacing: 0
        LayoutMirroring.enabled: Theme.rtl

        // ---- Header Bar ----
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 64
            color: Theme.panel
            Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: Theme.divider }

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 20
                anchors.rightMargin: 20
                spacing: 12
                LayoutMirroring.enabled: Theme.rtl

                Icon {
                    name: "search"
                    size: 22
                    color: Theme.accent
                }

                Column {
                    Layout.fillWidth: true
                    spacing: 2
                    Text {
                        text: qsTr("Search Results")
                        color: Theme.text
                        font.family: Theme.fontFamily
                        font.pixelSize: 16
                        font.bold: true
                    }
                    Text {
                        text: searchResultsModel.rowCount() > 0 
                            ? qsTr("Found %1 matching post%2 across all channels").arg(searchResultsModel.rowCount()).arg(searchResultsModel.rowCount() === 1 ? "" : "s")
                            : qsTr("No matching posts found")
                        color: Theme.textSecondary
                        font.family: Theme.fontFamily
                        font.pixelSize: 12
                    }
                }
            }
        }

        // ---- Results list ----
        ListView {
            id: resultsList
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            model: searchResultsModel
            boundsBehavior: Flickable.StopAtBounds
            ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }

            delegate: Rectangle {
                id: itemCard
                width: ListView.view.width
                implicitHeight: cardCol.implicitHeight + 30
                color: itemMouse.containsMouse ? Theme.hover : "transparent"
                Behavior on color { ColorAnimation { duration: Theme.animFast } }

                ColumnLayout {
                    id: cardCol
                    anchors.fill: parent
                    anchors.margins: 15
                    spacing: 8

                    // Source and time row
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 8
                        LayoutMirroring.enabled: Theme.rtl

                        // Channel source pill
                        Rectangle {
                            height: 20
                            width: sourceLabel.implicitWidth + 16
                            radius: 10
                            color: Theme.panelAlt
                            border.width: 1
                            border.color: Theme.divider
                            Text {
                                id: sourceLabel
                                anchors.centerIn: parent
                                text: model.source
                                color: Theme.accent
                                font.family: Theme.fontFamily; font.pixelSize: 11; font.bold: true
                            }
                        }

                        // Section pill
                        Rectangle {
                            height: 20
                            width: sectionLabel.implicitWidth + 16
                            radius: 10
                            color: Theme.panelAlt
                            border.width: 1
                            border.color: Theme.divider
                            Text {
                                id: sectionLabel
                                anchors.centerIn: parent
                                text: model.section
                                color: Theme.textSecondary
                                font.family: Theme.fontFamily; font.pixelSize: 11
                            }
                        }

                        Item { Layout.fillWidth: true }

                        Text {
                            text: model.time
                            color: Theme.textSecondary
                            font.family: Theme.fontFamily; font.pixelSize: 12
                        }
                    }

                    // Title
                    Text {
                        Layout.fillWidth: true
                        text: model.title
                        color: Theme.text
                        font.family: Theme.fontFamily
                        font.pixelSize: 15
                        font.bold: true
                        textFormat: Text.RichText
                        elide: Text.ElideRight
                        maximumLineCount: 1
                        horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
                    }

                    // Snippet / Text
                    Text {
                        Layout.fillWidth: true
                        text: model.snippet
                        color: Theme.textSecondary
                        font.family: Theme.fontFamily
                        font.pixelSize: 13
                        textFormat: Text.RichText
                        wrapMode: Text.Wrap
                        maximumLineCount: 2
                        elide: Text.ElideRight
                        horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
                    }

                    // Action buttons
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 12
                        LayoutMirroring.enabled: Theme.rtl
                        visible: model.url !== ""

                        Rectangle {
                            height: 28
                            width: btnRow1.implicitWidth + 16
                            radius: 14
                            color: btnMouse1.containsMouse ? Theme.panelAlt : "transparent"
                            border.width: 1
                            border.color: Theme.divider
                            Row {
                                id: btnRow1
                                anchors.centerIn: parent
                                spacing: 6
                                Icon { anchors.verticalCenter: parent.verticalCenter; name: "eye"; size: 13; color: Theme.textSecondary }
                                Text { anchors.verticalCenter: parent.verticalCenter; text: qsTr("Read offline"); color: Theme.text; font.family: Theme.fontFamily; font.pixelSize: 12 }
                            }
                            MouseArea {
                                id: btnMouse1
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: root.readArticleRequested(model.url, model.title, model.snippet)
                            }
                        }

                        Rectangle {
                            height: 28
                            width: btnRow2.implicitWidth + 16
                            radius: 14
                            color: btnMouse2.containsMouse ? Theme.panelAlt : "transparent"
                            border.width: 1
                            border.color: Theme.divider
                            Row {
                                id: btnRow2
                                anchors.centerIn: parent
                                spacing: 6
                                Icon { anchors.verticalCenter: parent.verticalCenter; name: "window"; size: 13; color: Theme.textSecondary }
                                Text { anchors.verticalCenter: parent.verticalCenter; text: qsTr("Open in offline viewer"); color: Theme.text; font.family: Theme.fontFamily; font.pixelSize: 12 }
                            }
                            MouseArea {
                                id: btnMouse2
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: bridge.openInOfflineViewer(model.url, model.title)
                            }
                        }

                        Rectangle {
                            height: 28
                            width: btnRow3.implicitWidth + 16
                            radius: 14
                            color: btnMouse3.containsMouse ? Theme.panelAlt : "transparent"
                            border.width: 1
                            border.color: Theme.divider
                            Row {
                                id: btnRow3
                                anchors.centerIn: parent
                                spacing: 6
                                Icon { anchors.verticalCenter: parent.verticalCenter; name: "external"; size: 13; color: Theme.textSecondary }
                                Text { anchors.verticalCenter: parent.verticalCenter; text: qsTr("Open original link"); color: Theme.text; font.family: Theme.fontFamily; font.pixelSize: 12 }
                            }
                            MouseArea {
                                id: btnMouse3
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: bridge.openExternal(model.url)
                            }
                        }
                    }
                }

                // Bottom divider
                Rectangle {
                    anchors.bottom: parent.bottom
                    anchors.left: parent.left
                    anchors.right: parent.right
                    height: 1
                    color: Theme.divider
                    opacity: 0.5
                }

                MouseArea {
                    id: itemMouse
                    anchors.fill: parent
                    hoverEnabled: true
                    acceptedButtons: Qt.LeftButton
                    cursorShape: model.url !== "" ? Qt.PointingHandCursor : Qt.ArrowCursor
                    z: -1
                    onClicked: {
                        if (model.url !== "") {
                            root.readArticleRequested(model.url, model.title, model.snippet)
                        }
                    }
                }
            }

            // Empty state placeholder
            Column {
                anchors.centerIn: parent
                spacing: 12
                visible: resultsList.count === 0
                Icon {
                    anchors.horizontalCenter: parent.horizontalCenter
                    name: "search"
                    size: 48
                    color: Theme.textSecondary
                }
                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: qsTr("No matching posts found.\nTry searching with different terms.")
                    horizontalAlignment: Text.AlignHCenter
                    color: Theme.textSecondary
                    font.family: Theme.fontFamily
                    font.pixelSize: 13
                }
            }
        }
    }
}
