import QtQuick
import QtQuick.Controls
import "../themes"

// Account: the Telegram repost target. OfflineFeed reposts via a BOT token +
// per-category chat IDs (NOT API id/hash), so we round-trip the real backend
// endpoint GET/POST /api/telegram/config through bridge.settingsGetTelegram()
// and bridge.settingsSaveTelegram(). See Notes for the deviation.
Item {
    id: page
    property var stack: null
    anchors.fill: parent

    property var _cfg: ({})

    SettingsHeader {
        id: hd
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        title: qsTr("Account")
        stack: page.stack
    }

    Flickable {
        anchors.top: hd.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        clip: true
        contentWidth: width
        contentHeight: body.implicitHeight + 32

        Column {
            id: body
            x: Math.max(16, (parent.width - width) / 2)
            width: Math.min(parent.width - 32, 620)
            y: 16
            spacing: 8

            Text {
                width: parent.width
                text: qsTr("Telegram repost target")
                color: Theme.accent
                font.family: Theme.fontFamily; font.pixelSize: 13; font.bold: true
                horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
            }

            Rectangle {
                width: parent.width
                radius: Theme.radius.lg
                color: Theme.panel
                clip: true
                height: card.implicitHeight
                Column {
                    id: card
                    width: parent.width
                    SettingsTextField { id: tfBot;    label: qsTr("Bot token");                placeholder: "123456:ABC-DEF..."; password: true }
                    SettingsTextField { id: tfEnt;    label: qsTr("Entertainment chat ID (default)"); placeholder: "-1001234567890" }
                    SettingsTextField { id: tfSports; label: qsTr("Sports chat ID");           placeholder: "-1001234567890" }
                    SettingsTextField { id: tfTech;   label: qsTr("Tech chat ID");             placeholder: "-1001234567890" }
                }
            }

            Item { width: parent.width; height: 8 }

            Row {
                width: parent.width
                layoutDirection: Theme.rtl ? Qt.RightToLeft : Qt.LeftToRight
                spacing: 10
                SettingsButton {
                    text: qsTr("Save")
                    primary: true
                    onClicked: {
                        var out = page._cfg ? page._cfg : {}
                        out.bot_token = tfBot.text
                        out.default_chat_id = tfEnt.text
                        out.sports_chat_id = tfSports.text
                        out.technology_chat_id = tfTech.text
                        bridge.settingsSaveTelegram(out)
                    }
                }
                SettingsButton {
                    text: qsTr("Reload")
                    primary: false
                    onClicked: page.load()
                }
            }

            Text {
                width: parent.width
                wrapMode: Text.WordWrap
                text: qsTr("These values are stored by the backend (gui_server.py) via its existing /api/telegram/config endpoint and are used to repost feeds to Telegram.")
                color: Theme.textSecondary
                font.family: Theme.fontFamily; font.pixelSize: 12
                horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
            }
        }
    }

    function load() {
        var cfg = bridge.settingsGetTelegram()
        page._cfg = cfg ? cfg : ({})
        tfBot.text    = (page._cfg.bot_token !== undefined && page._cfg.bot_token !== null) ? page._cfg.bot_token : ""
        tfEnt.text    = (page._cfg.default_chat_id !== undefined && page._cfg.default_chat_id !== null) ? page._cfg.default_chat_id : ""
        tfSports.text = (page._cfg.sports_chat_id !== undefined && page._cfg.sports_chat_id !== null) ? page._cfg.sports_chat_id : ""
        tfTech.text   = (page._cfg.technology_chat_id !== undefined && page._cfg.technology_chat_id !== null) ? page._cfg.technology_chat_id : ""
    }

    Component.onCompleted: load()
}
