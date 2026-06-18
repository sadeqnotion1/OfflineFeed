import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../themes"

Item {
    id: root

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
                    text: qsTr("Help & About")
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
                    text: qsTr("About OfflineFeed")
                    color: Theme.accent; font.bold: true; font.family: Theme.fontFamily; font.pixelSize: 14
                }

                Text {
                    Layout.fillWidth: true
                    text: qsTr("OfflineFeed is a lightweight, local-first Windows news client and RSS aggregator. It mirrors select feeds to Telegram channels using a background worker thread, ensuring real-time syndication even when the main desktop app is closed.")
                    color: Theme.text
                    wrapMode: Text.WordWrap
                    font.family: Theme.fontFamily; font.pixelSize: 13
                }

                Rectangle { Layout.fillWidth: true; height: 1; color: Theme.divider }

                Text {
                    text: qsTr("Frequently Asked Questions")
                    color: Theme.accent; font.bold: true; font.family: Theme.fontFamily; font.pixelSize: 14
                }

                ColumnLayout {
                    spacing: 10
                    Layout.fillWidth: true

                    Text {
                        text: qsTr("Q: How do I add a new RSS source?")
                        color: Theme.text; font.bold: true
                        font.family: Theme.fontFamily; font.pixelSize: 13
                    }
                    Text {
                        Layout.fillWidth: true
                        text: qsTr("A: Navigate to Settings -> Folders & News Sources. Enter the URL, Name, and choose a category, then click Add Source.")
                        color: Theme.textSecondary
                        wrapMode: Text.WordWrap
                        font.family: Theme.fontFamily; font.pixelSize: 13
                    }

                    Text {
                        text: qsTr("Q: How does the Telegram posting work?")
                        color: Theme.text; font.bold: true
                        font.family: Theme.fontFamily; font.pixelSize: 13
                    }
                    Text {
                        Layout.fillWidth: true
                        text: qsTr("A: You must enter a Telegram Bot Token and Chat ID under Settings -> Account & Credentials. Newly fetched articles will then be forwarded automatically.")
                        color: Theme.textSecondary
                        wrapMode: Text.WordWrap
                        font.family: Theme.fontFamily; font.pixelSize: 13
                    }
                }

                Rectangle { Layout.fillWidth: true; height: 1; color: Theme.divider }

                Text {
                    text: qsTr("Troubleshooting & Support")
                    color: Theme.accent; font.bold: true; font.family: Theme.fontFamily; font.pixelSize: 14
                }

                RowLayout {
                    spacing: 10
                    PillButton {
                        text: qsTr("Open System Logs")
                        onClicked: {
                            // Pop current page and push advanced settings
                            settingsStack.pop()
                            settingsStack.push(Qt.resolvedUrl("SettingsAdvanced.qml"))
                        }
                    }
                    PillButton {
                        text: qsTr("GitHub Repository")
                        outline: true
                        onClicked: {
                            bridge.openExternal("https://github.com/sadeqnotion1/OfflineFeed")
                        }
                    }
                }
            }
        }
    }
}
