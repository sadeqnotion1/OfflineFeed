import QtQuick
import "../themes"

// Help: FAQ / features text, a link to open the System Logs channel, and an
// 'Ask a question' button that opens the repository issues page externally.
Item {
    id: page
    property var stack: null
    anchors.fill: parent

    SettingsHeader {
        id: hd
        anchors.top: parent.top; anchors.left: parent.left; anchors.right: parent.right
        title: qsTr("Help")
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

            SettingsSectionHeader {
                width: parent.width
                iconName: "help"; tileColor: "#f5a623"
                title: qsTr("Help")
                subtitle: qsTr("Frequently asked questions and support")
            }

            Rectangle {
                width: parent.width; radius: Theme.radius.card; color: Theme.panel; height: infoCol.implicitHeight + 28
                Column {
                    id: infoCol
                    x: 16; y: 14; width: parent.width - 32; spacing: 10
                    Text {
                        width: parent.width; text: qsTr("OfflineFeed")
                        color: Theme.text; font.family: Theme.fontFamily; font.pixelSize: 16; font.bold: true
                        horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
                    }
                    Text {
                        width: parent.width; wrapMode: Text.WordWrap
                        text: qsTr("A desktop news/RSS aggregator that reposts feeds to Telegram. Configure your bot and target chats in Account, choose how articles are fetched in Feed & Chat Settings, and personalize the look in Appearance.")
                        color: Theme.textSecondary; font.family: Theme.fontFamily; font.pixelSize: 13
                        horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
                    }
                    Text {
                        width: parent.width; wrapMode: Text.WordWrap
                        text: qsTr("FAQ: If reposting fails, check the bot token and chat IDs in Account, then watch the System Logs channel for backend errors.")
                        color: Theme.textSecondary; font.family: Theme.fontFamily; font.pixelSize: 13
                        horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
                    }
                }
            }

            Item { width: parent.width; height: 4 }

            Row {
                width: parent.width
                layoutDirection: Theme.rtl ? Qt.RightToLeft : Qt.LeftToRight
                spacing: 10
                SettingsButton {
                    text: qsTr("Open System Logs")
                    primary: false
                    onClicked: { bridge.setTab("entertainment"); bridge.openChat("SystemLogs") }
                }
                SettingsButton {
                    text: qsTr("Ask a Question")
                    primary: true
                    onClicked: Qt.openUrlExternally("https://github.com/sadeqnotion1/OfflineFeed/issues")
                }
            }
        }
    }
}
