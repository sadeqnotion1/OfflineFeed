import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../themes"

Item {
    id: root

    property var config: ({})
    Component.onCompleted: {
        root.config = bridge.getSettings("account")
        botToken.value = root.config.bot_token || ""
        defaultChatId.value = root.config.default_chat_id || ""
        sportsChatId.value = root.config.sports_chat_id || ""
        techChatId.value = root.config.technology_chat_id || ""
        threads.value = root.config.channel_threads || "{}"
        apiId.value = root.config.api_id || ""
        apiHash.value = root.config.api_hash || ""
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
                    text: qsTr("Account & Credentials")
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
                spacing: 14

                Text {
                    text: qsTr("Telegram API Credentials")
                    color: Theme.accent; font.bold: true; font.family: Theme.fontFamily; font.pixelSize: 14
                }

                Field {
                    id: apiId
                    label: qsTr("API ID")
                    placeholder: qsTr("e.g. 123456")
                    Layout.fillWidth: true
                }

                Field {
                    id: apiHash
                    label: qsTr("API Hash")
                    placeholder: qsTr("e.g. abcdef1234567890abcdef1234567890")
                    Layout.fillWidth: true
                }

                Rectangle { Layout.fillWidth: true; height: 1; color: Theme.divider }

                Text {
                    text: qsTr("Telegram Poster Settings")
                    color: Theme.accent; font.bold: true; font.family: Theme.fontFamily; font.pixelSize: 14
                }

                Field {
                    id: botToken
                    label: qsTr("Bot Token")
                    placeholder: qsTr("e.g. 123456789:ABCdefGhI...")
                    Layout.fillWidth: true
                }

                Field {
                    id: defaultChatId
                    label: qsTr("Default Chat ID (Entertainment)")
                    placeholder: qsTr("e.g. -1001234567890")
                    Layout.fillWidth: true
                }

                Field {
                    id: sportsChatId
                    label: qsTr("Sports Chat ID")
                    placeholder: qsTr("e.g. -1001234567890")
                    Layout.fillWidth: true
                }

                Field {
                    id: techChatId
                    label: qsTr("Technology Chat ID")
                    placeholder: qsTr("e.g. -1001234567890")
                    Layout.fillWidth: true
                }

                Field {
                    id: threads
                    label: qsTr("Channel-to-Topic Thread IDs (JSON)")
                    placeholder: qsTr('{"channel_name": 123}')
                    Layout.fillWidth: true
                }

                PillButton {
                    text: qsTr("Save Config & Credentials")
                    Layout.topMargin: 10
                    onClicked: {
                        bridge.setSetting("account", "api_id", apiId.value)
                        bridge.setSetting("account", "api_hash", apiHash.value)
                        bridge.setSetting("account", "bot_token", botToken.value)
                        bridge.setSetting("account", "default_chat_id", defaultChatId.value)
                        bridge.setSetting("account", "sports_chat_id", sportsChatId.value)
                        bridge.setSetting("account", "technology_chat_id", techChatId.value)
                        bridge.setSetting("account", "channel_threads", threads.value)
                    }
                }
            }
        }
    }
}
