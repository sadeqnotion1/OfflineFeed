import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../themes"

Item {
    id: root
    signal sectionSelected(string sectionId)

    ScrollView {
        anchors.fill: parent
        contentWidth: availableWidth
        clip: true

        ColumnLayout {
            width: parent.width
            spacing: 0

            // User Info header (Telegram style)
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 120
                color: "transparent"

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 16

                    Avatar {
                        name: "OfflineFeed"
                        size: 64
                        seed: "OfflineFeed"
                    }

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2
                        Text {
                            text: "OfflineFeed"
                            color: Theme.text
                            font.family: Theme.fontFamily; font.pixelSize: 18; font.bold: true
                        }
                        Text {
                            text: qsTr("News aggregator & Telegram poster")
                            color: Theme.textSecondary
                            font.family: Theme.fontFamily; font.pixelSize: 13
                        }
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                height: 1
                color: Theme.divider
            }

            // List of rows
            SettingsRow {
                iconName: "bots"
                label: qsTr("Account & Credentials")
                onClicked: root.sectionSelected("account")
            }

            SettingsRow {
                iconName: "mute"
                label: qsTr("Notifications & Sounds")
                onClicked: root.sectionSelected("notifications")
            }

            SettingsRow {
                iconName: "eye"
                label: qsTr("Privacy & Security")
                onClicked: root.sectionSelected("privacy")
            }

            SettingsRow {
                iconName: "chats"
                label: qsTr("Feed / Chat Settings")
                onClicked: root.sectionSelected("feed")
            }

            // --- News Sources (custom feeds: single / batch / OPML) ---
            SettingsRow {
                iconName: "external"
                label: qsTr("News Sources")
                onClicked: root.sectionSelected("sources")
            }

            SettingsRow {
                iconName: "folder"
                label: qsTr("Folders & News Sources")
                onClicked: root.sectionSelected("folders")
            }

            SettingsRow {
                iconName: "cpu"
                label: qsTr("Advanced Settings")
                onClicked: root.sectionSelected("advanced")
            }

            SettingsRow {
                iconName: "sun"
                label: qsTr("Appearance")
                onClicked: root.sectionSelected("appearance")
            }

            SettingsRow {
                iconName: "external"
                label: qsTr("Language & RTL")
                onClicked: root.sectionSelected("language")
            }

            SettingsRow {
                iconName: "info"
                label: qsTr("Help & System Logs")
                onClicked: root.sectionSelected("help")
            }
        }
    }
}
