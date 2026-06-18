import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../themes"

// The single, consolidated Settings surface (issue #5 + #8). Three sections:
//   1. Appearance  (theme variant toggle moved here from the title bar)
//   2. News Sources (add / delete custom feeds: name, url, section, category)
//   3. Telegram Poster (bot token, per-category chat IDs, channel->topic thread IDs)
// Plus System utilities (refresh, clear cache, reset Telegram history) and the
// embedded ChatSettings appearance editor.
Rectangle {
    id: root
    color: Theme.bg

    property var telegramConfig: ({})
    property var logs: []
    Component.onCompleted: { reloadConfig(); bridge.loadLogs() }
    function reloadConfig() { root.telegramConfig = bridge.getTelegramConfig(); }
    function reloadLogs() { root.logs = bridge.getActivityLog(); }

    Connections {
        target: bridge
        function onTelegramConfigChanged() { root.reloadConfig() }
        function onLogsUpdated() { root.reloadLogs() }
    }

    ScrollView {
        anchors.fill: parent
        contentWidth: availableWidth
        clip: true

        ColumnLayout {
            width: root.width
            spacing: 0

            // ===== Header =====
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: Theme.headerHeight
                color: Theme.panel
                Text {
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.left: parent.left
                    anchors.leftMargin: 20
                    text: qsTr("Settings")
                    color: Theme.text
                    font.family: Theme.fontFamily; font.pixelSize: 18; font.bold: true
                }
                Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: Theme.divider }
            }

            // ===== 1. Appearance (theme toggle moved out of titlebar) =====
            SectionHeader { text: qsTr("Appearance") }
            ChatSettings {
                Layout.fillWidth: true
                Layout.preferredHeight: 470
            }

            // ===== 2. News Sources =====
            SectionHeader { text: qsTr("News Sources") }

            // add-source form
            GridLayout {
                Layout.fillWidth: true
                Layout.leftMargin: 20; Layout.rightMargin: 20
                columns: 2
                columnSpacing: 12
                rowSpacing: 10
                Field { id: srcName;    label: qsTr("Name");      placeholder: qsTr("e.g. Variety") }
                Field { id: srcUrl;     label: qsTr("Feed URL");  placeholder: qsTr("https://...") }
                LabeledCombo { id: srcSection;  label: qsTr("Section");  options: ["Entertainment", "Sports", "Technology"] }
                Field { id: srcCategory; label: qsTr("Category"); placeholder: qsTr("e.g. Movies") }
            }
            RowLayout {
                Layout.leftMargin: 20; Layout.rightMargin: 20; Layout.topMargin: 10
                spacing: 10
                PillButton {
                    text: qsTr("Analyze URL")
                    outline: true
                    onClicked: bridge.analyzeSource(srcUrl.value)
                }
                PillButton {
                    text: qsTr("Add Source")
                    onClicked: {
                        bridge.addCustomSource(srcName.value, srcUrl.value,
                                               srcSection.value.toLowerCase(), srcCategory.value);
                        srcName.value = ""; srcUrl.value = ""; srcCategory.value = "";
                    }
                }
            }

            // existing sources list
            Text {
                Layout.leftMargin: 20; Layout.topMargin: 16
                text: qsTr("Your custom sources")
                color: Theme.textSecondary; font.bold: true
                font.family: Theme.fontFamily; font.pixelSize: 13
            }
            ColumnLayout {
                Layout.fillWidth: true
                Layout.leftMargin: 20; Layout.rightMargin: 20; Layout.topMargin: 6
                spacing: 8
                Repeater {
                    model: sourcesModel
                    delegate: Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 54
                        radius: 10
                        color: Theme.panel
                        RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 12; anchors.rightMargin: 12
                            spacing: 12
                            Avatar { name: model.name; avatarPath: model.avatarPath; seed: model.name; size: 34 }
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 1
                                Text { text: model.name; color: Theme.text; font.bold: true; font.family: Theme.fontFamily; font.pixelSize: 14 }
                                Text { text: model.section + "  ·  " + model.category; color: Theme.textSecondary; font.family: Theme.fontFamily; font.pixelSize: 12 }
                            }
                            Icon {
                                name: "trash"; size: 18; color: "#ec3942"
                                MouseArea {
                                    anchors.fill: parent; cursorShape: Qt.PointingHandCursor
                                    onClicked: bridge.deleteCustomSource(model.name, model.url)
                                }
                            }
                        }
                    }
                }
                Text {
                    visible: sourcesModel.rowCount() === 0
                    text: qsTr("No custom sources added yet.")
                    color: Theme.textSecondary; font.family: Theme.fontFamily; font.pixelSize: 13
                }
            }

            // ===== 3. Telegram Poster =====
            SectionHeader { text: qsTr("Telegram Channel Poster") }
            ColumnLayout {
                Layout.fillWidth: true
                Layout.leftMargin: 20; Layout.rightMargin: 20
                spacing: 10
                Field { id: botToken;  label: qsTr("Bot Token");                  value: root.telegramConfig.bot_token || "";          Layout.fillWidth: true }
                Field { id: entId;     label: qsTr("Entertainment Chat ID");      value: root.telegramConfig.default_chat_id || "";     Layout.fillWidth: true }
                Field { id: sportsId;  label: qsTr("Sports Chat ID");             value: root.telegramConfig.sports_chat_id || "";      Layout.fillWidth: true }
                Field { id: techId;    label: qsTr("Technology Chat ID");         value: root.telegramConfig.technology_chat_id || "";  Layout.fillWidth: true }
                Field { id: threads;   label: qsTr("Channel→Topic thread IDs (JSON)"); value: JSON.stringify(root.telegramConfig.channel_threads || {}); Layout.fillWidth: true }
                PillButton {
                    text: qsTr("Save Telegram Config")
                    Layout.topMargin: 4
                    onClicked: bridge.saveTelegramConfig(botToken.value, entId.value,
                                                         sportsId.value, techId.value, threads.value)
                }
            }

            // ===== System utilities =====
            SectionHeader { text: qsTr("System") }
            RowLayout {
                Layout.leftMargin: 20; Layout.rightMargin: 20
                spacing: 10
                PillButton { text: qsTr("Refresh Feeds");  outline: true; onClicked: bridge.refreshNews(true) }
                PillButton { text: qsTr("Clear Cache");    outline: true; onClicked: bridge.clearCache() }
                PillButton { text: qsTr("Reset TG History"); outline: true; danger: true; onClicked: bridge.resetTelegramHistory() }
            }

            // ===== System Logs (moved here from the chat list, issue #7) =====
            RowLayout {
                Layout.leftMargin: 20; Layout.rightMargin: 20; Layout.topMargin: 18
                Layout.fillWidth: true
                Text {
                    Layout.fillWidth: true
                    text: qsTr("System Logs")
                    color: Theme.accent
                    font.family: Theme.fontFamily; font.pixelSize: 14; font.bold: true
                }
                Icon {
                    name: "refresh"; size: 16; color: Theme.textSecondary
                    MouseArea { anchors.fill: parent; anchors.margins: -6; cursorShape: Qt.PointingHandCursor; onClicked: bridge.loadLogs() }
                }
            }
            Rectangle {
                Layout.fillWidth: true
                Layout.leftMargin: 20; Layout.rightMargin: 20; Layout.topMargin: 8; Layout.bottomMargin: 30
                Layout.preferredHeight: 220
                radius: 10
                color: Theme.panel
                ListView {
                    id: logList
                    anchors.fill: parent
                    anchors.margins: 12
                    clip: true
                    model: root.logs
                    spacing: 8
                    ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
                    delegate: ColumnLayout {
                        width: logList.width
                        property var entry: modelData
                        spacing: 1
                        Text {
                            text: (entry && entry.section ? entry.section : "Log") + "  \u00b7  " + (entry && entry.time ? entry.time : "")
                            color: Theme.textSecondary
                            font.family: Theme.fontFamily; font.pixelSize: 11
                        }
                        Text {
                            Layout.fillWidth: true
                            text: entry && entry.message ? entry.message : ""
                            wrapMode: Text.WordWrap
                            color: Theme.text
                            font.family: Theme.fontFamily; font.pixelSize: 13
                        }
                    }
                    Text {
                        anchors.centerIn: parent
                        visible: logList.count === 0
                        text: qsTr("No log entries yet.")
                        color: Theme.textSecondary; font.family: Theme.fontFamily; font.pixelSize: 13
                    }
                }
            }
        }
    }

    // ---- small reusable inline components ----
    component SectionHeader: Rectangle {
        property string text: ""
        Layout.fillWidth: true
        Layout.preferredHeight: 44
        Layout.topMargin: 10
        color: "transparent"
        Text {
            anchors.left: parent.left; anchors.leftMargin: 20
            anchors.verticalCenter: parent.verticalCenter
            text: parent.text
            color: Theme.accent
            font.family: Theme.fontFamily; font.pixelSize: 14; font.bold: true
        }
    }

    component Field: ColumnLayout {
        property string label: ""
        property string placeholder: ""
        property alias value: input.text
        spacing: 4
        Text { text: parent.label; color: Theme.textSecondary; font.family: Theme.fontFamily; font.pixelSize: 12 }
        Rectangle {
            Layout.fillWidth: true
            implicitWidth: 240
            height: 40; radius: 9
            color: Theme.panel
            border.width: input.activeFocus ? 1 : 0
            border.color: Theme.accent
            TextField {
                id: input
                anchors.fill: parent
                anchors.leftMargin: 12; anchors.rightMargin: 12
                placeholderText: parent.parent.placeholder
                placeholderTextColor: Theme.textSecondary
                color: Theme.text
                font.family: Theme.fontFamily; font.pixelSize: 14
                verticalAlignment: Text.AlignVCenter
                background: Item {}
                horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
            }
        }
    }

    component LabeledCombo: ColumnLayout {
        property string label: ""
        property var options: []
        property string value: comboBox.currentText
        spacing: 4
        Text { text: parent.label; color: Theme.textSecondary; font.family: Theme.fontFamily; font.pixelSize: 12 }
        ComboBox {
            id: comboBox
            Layout.fillWidth: true
            implicitWidth: 240
            model: parent.options
            font.family: Theme.fontFamily
        }
    }

    component PillButton: Rectangle {
        property string text: ""
        property bool outline: false
        property bool danger: false
        signal clicked()
        implicitHeight: 40
        implicitWidth: lbl.implicitWidth + 36
        radius: 20
        color: outline ? "transparent" : (danger ? "#ec3942" : Theme.accent)
        border.width: outline ? 1 : 0
        border.color: danger ? "#ec3942" : Theme.divider
        Text {
            id: lbl
            anchors.centerIn: parent
            text: parent.text
            color: outline ? (danger ? "#ec3942" : Theme.text) : Theme.accentText
            font.family: Theme.fontFamily; font.pixelSize: 14; font.bold: true
        }
        MouseArea {
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            onClicked: parent.clicked()
            onEntered: parent.opacity = 0.88
            onExited: parent.opacity = 1.0
        }
        Behavior on opacity { NumberAnimation { duration: Theme.animFast } }
    }
}
