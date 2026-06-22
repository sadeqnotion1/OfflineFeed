import QtQuick
import QtQuick.Controls
import "../themes"

// MERGED "Advanced" page (the purple group): combines the former Account,
// Privacy & Security, and Advanced pages into ONE screen, separated by rich
// icon section headers (SettingsSectionHeader). Every backend call is preserved
// VERBATIM from the three original pages -- no bridge behavior is changed:
//   - Account:  bridge.settingsGetTelegram() / bridge.settingsSaveTelegram()
//   - Privacy:  bridge.settingsGetGroup("privacy")  / settingsSetValue("privacy", ...)
//   - Advanced: bridge.settingsGetGroup("advanced") / settingsSetValue("advanced", ...)
Item {
    id: page
    property var stack: null
    anchors.fill: parent

    property var _cfg: ({})

    SettingsHeader {
        id: hd
        anchors.top: parent.top; anchors.left: parent.left; anchors.right: parent.right
        title: qsTr("Advanced")
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

            // ===================== Account =====================
            SettingsSectionHeader {
                width: parent.width
                iconName: "user"; tileColor: "#3390ec"
                title: qsTr("Account")
                subtitle: qsTr("Telegram repost target")
            }
            Rectangle {
                width: parent.width; radius: Theme.radius.card; color: Theme.panel; clip: true; height: cAccount.implicitHeight
                Column {
                    id: cAccount; width: parent.width
                    SettingsTextField { id: tfBot;    label: qsTr("Bot token");                placeholder: "123456:ABC-DEF..."; password: true }
                    SettingsTextField { id: tfEnt;    label: qsTr("Entertainment chat ID (default)"); placeholder: "-1001234567890" }
                    SettingsTextField { id: tfSports; label: qsTr("Sports chat ID");           placeholder: "-1001234567890" }
                    SettingsTextField { id: tfTech;   label: qsTr("Tech chat ID");             placeholder: "-1001234567890" }
                }
            }
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
                    onClicked: page.loadAccount()
                }
            }
            Text {
                width: parent.width; wrapMode: Text.WordWrap
                text: qsTr("These values are stored by the backend (gui_server.py) via its existing /api/telegram/config endpoint and are used to repost feeds to Telegram.")
                color: Theme.textSecondary; font.family: Theme.fontFamily; font.pixelSize: 12
                horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
            }

            // ===================== Privacy & Security =====================
            SettingsSectionHeader {
                width: parent.width
                iconName: "shield"; tileColor: "#4dcd5e"
                title: qsTr("Privacy & Security")
            }
            Rectangle {
                width: parent.width; radius: Theme.radius.card; color: Theme.panel; clip: true; height: cPrivacy.implicitHeight
                Column {
                    id: cPrivacy; width: parent.width
                    SettingsToggle { id: tgHistory; label: qsTr("Keep read/article history"); description: qsTr("Remember which items you have already opened")
                        onToggled: bridge.settingsSetValue("privacy", "save_history", value) }
                    SettingsToggle { id: tgClear;   label: qsTr("Clear history on exit")
                        onToggled: bridge.settingsSetValue("privacy", "clear_on_exit", value) }
                    SettingsToggle { id: tgTelemetry; label: qsTr("Anonymous usage diagnostics"); description: qsTr("Off by default. Nothing is sent unless enabled.")
                        onToggled: bridge.settingsSetValue("privacy", "telemetry", value) }
                }
            }

            // ===================== Advanced =====================
            SettingsSectionHeader {
                width: parent.width
                iconName: "wrench"; tileColor: "#13b9a8"
                title: qsTr("Advanced")
                subtitle: qsTr("Backend & diagnostics")
            }
            Rectangle {
                width: parent.width; radius: Theme.radius.card; color: Theme.panel; clip: true; height: cBackend.implicitHeight
                Column {
                    id: cBackend; width: parent.width
                    SettingsTextField {
                        id: tfPort
                        label: qsTr("Backend port (applies on next launch)")
                        placeholder: "8080"
                        onEdited: bridge.settingsSetValue("advanced", "backend_port", value)
                    }
                    SettingsToggle {
                        id: tgVerbose
                        label: qsTr("Verbose logging")
                        onToggled: bridge.settingsSetValue("advanced", "verbose_logging", value)
                    }
                }
            }
            Rectangle {
                width: parent.width; radius: Theme.radius.card; color: Theme.panel; height: diagCol.implicitHeight + 24
                Column {
                    id: diagCol
                    x: 16; y: 12; width: parent.width - 32; spacing: 12
                    Text {
                        width: parent.width; wrapMode: Text.WordWrap
                        text: qsTr("Open the System Logs channel to inspect backend activity, or run 'python -m frontend.doctor' from a terminal for a full diagnostic report.")
                        color: Theme.textSecondary; font.family: Theme.fontFamily; font.pixelSize: 13
                        horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
                    }
                    SettingsButton {
                        text: qsTr("Open System Logs")
                        primary: false
                        onClicked: {
                            bridge.setTab("entertainment")
                            bridge.openChat("SystemLogs")
                        }
                    }
                }
            }
        }
    }

    function loadAccount() {
        var cfg = bridge.settingsGetTelegram()
        page._cfg = cfg ? cfg : ({})
        tfBot.text    = (page._cfg.bot_token !== undefined && page._cfg.bot_token !== null) ? page._cfg.bot_token : ""
        tfEnt.text    = (page._cfg.default_chat_id !== undefined && page._cfg.default_chat_id !== null) ? page._cfg.default_chat_id : ""
        tfSports.text = (page._cfg.sports_chat_id !== undefined && page._cfg.sports_chat_id !== null) ? page._cfg.sports_chat_id : ""
        tfTech.text   = (page._cfg.technology_chat_id !== undefined && page._cfg.technology_chat_id !== null) ? page._cfg.technology_chat_id : ""
    }

    Component.onCompleted: {
        loadAccount()
        var p = bridge.settingsGetGroup("privacy")
        tgHistory.checked   = (p.save_history === undefined) ? true  : p.save_history
        tgClear.checked     = (p.clear_on_exit === undefined) ? false : p.clear_on_exit
        tgTelemetry.checked = (p.telemetry === undefined) ? false : p.telemetry
        var a = bridge.settingsGetGroup("advanced")
        tfPort.text = (a.backend_port === undefined || a.backend_port === null) ? "8080" : a.backend_port
        tgVerbose.checked = (a.verbose_logging === undefined) ? false : a.verbose_logging
    }
}
