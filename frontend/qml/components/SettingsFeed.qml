import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../themes"

Item {
    id: root

    property var config: ({})
    Component.onCompleted: {
        root.config = bridge.getSettings("feed")
        readerModeCombo.currentIndex = readerModeCombo.options.indexOf(root.config.reader_mode || "rich")
        scrapingFallback.checked = root.config.scraping_fallback !== false
        wallpaperCombo.currentIndex = wallpaperCombo.options.indexOf(bridge.wallpaperMode || "pattern")
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // Header
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
                    text: qsTr("Feed / Chat Settings")
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
                spacing: 18

                Text {
                    text: qsTr("Reader Behavior")
                    color: Theme.accent; font.bold: true; font.family: Theme.fontFamily; font.pixelSize: 14
                }

                LabeledCombo {
                    id: readerModeCombo
                    label: qsTr("Reader Mode")
                    options: ["rich", "plain"]
                    Layout.fillWidth: true
                }

                CheckBox {
                    id: scrapingFallback
                    text: qsTr("Enable scraping fallback on RSS parse failures")
                    font.family: Theme.fontFamily; font.pixelSize: 14
                    contentItem: Text {
                        text: scrapingFallback.text
                        font: scrapingFallback.font
                        color: Theme.text
                        verticalAlignment: Text.AlignVCenter
                        leftPadding: scrapingFallback.indicator.width + scrapingFallback.spacing
                    }
                }

                Rectangle { Layout.fillWidth: true; height: 1; color: Theme.divider }

                Text {
                    text: qsTr("Chat Wallpaper")
                    color: Theme.accent; font.bold: true; font.family: Theme.fontFamily; font.pixelSize: 14
                }

                LabeledCombo {
                    id: wallpaperCombo
                    label: qsTr("Wallpaper Style")
                    options: ["pattern", "solid", "none"]
                    Layout.fillWidth: true
                }

                PillButton {
                    text: qsTr("Save Feed & Chat Settings")
                    Layout.topMargin: 10
                    onClicked: {
                        bridge.setSetting("feed", "reader_mode", readerModeCombo.value)
                        bridge.setSetting("feed", "scraping_fallback", scrapingFallback.checked)
                        bridge.setSetting("appearance", "wallpaper_mode", wallpaperCombo.value)
                    }
                }
            }
        }
    }
}
