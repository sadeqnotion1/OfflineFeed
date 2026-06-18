import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../themes"

Item {
    id: root

    property var logs: []
    property var config: ({})
    Component.onCompleted: {
        root.config = bridge.getSettings("advanced")
        backendPort.value = (root.config.backend_port || 8080).toString()
        cacheLimit.value = (root.config.cache_limit_mb || 500).toString()
        reloadLogs()
        bridge.loadLogs()
    }

    function reloadLogs() {
        root.logs = bridge.getActivityLog()
    }

    Connections {
        target: bridge
        function onLogsUpdated() { root.reloadLogs() }
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
                    text: qsTr("Advanced Settings")
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
                spacing: 0
                Layout.leftMargin: 20; Layout.rightMargin: 20; Layout.topMargin: 12; Layout.bottomMargin: 30

                Text {
                    text: qsTr("Connection & Storage")
                    color: Theme.accent; font.bold: true; font.family: Theme.fontFamily; font.pixelSize: 14
                    Layout.bottomMargin: 10
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 16
                    Field {
                        id: backendPort
                        label: qsTr("Backend Port")
                        placeholder: "8080"
                        Layout.fillWidth: true
                    }
                    Field {
                        id: cacheLimit
                        label: qsTr("Cache Limit (MB)")
                        placeholder: "500"
                        Layout.fillWidth: true
                    }
                }

                PillButton {
                    text: qsTr("Save Advanced Configuration")
                    Layout.topMargin: 10
                    Layout.bottomMargin: 20
                    onClicked: {
                        bridge.setSetting("advanced", "backend_port", parseInt(backendPort.value) || 8080)
                        bridge.setSetting("advanced", "cache_limit_mb", parseInt(cacheLimit.value) || 500)
                    }
                }

                Rectangle { Layout.fillWidth: true; height: 1; color: Theme.divider; Layout.bottomMargin: 16 }

                // System utilities
                Text {
                    text: qsTr("System Utilities")
                    color: Theme.accent; font.bold: true; font.family: Theme.fontFamily; font.pixelSize: 14
                    Layout.bottomMargin: 10
                }

                RowLayout {
                    spacing: 10
                    Layout.bottomMargin: 20
                    PillButton { text: qsTr("Refresh Feeds");  outline: true; onClicked: bridge.refreshNews(true) }
                    PillButton { text: qsTr("Clear Cache");    outline: true; onClicked: bridge.clearCache() }
                    PillButton { text: qsTr("Reset TG History"); outline: true; danger: true; onClicked: bridge.resetTelegramHistory() }
                }

                Rectangle { Layout.fillWidth: true; height: 1; color: Theme.divider; Layout.bottomMargin: 16 }

                // System Logs panel
                RowLayout {
                    Layout.fillWidth: true
                    Layout.bottomMargin: 8
                    Text {
                        Layout.fillWidth: true
                        text: qsTr("System Logs")
                        color: Theme.accent
                        font.family: Theme.fontFamily; font.pixelSize: 14; font.bold: true
                    }
                    Icon {
                        name: "refresh"
                        size: 16
                        color: Theme.textSecondary
                        MouseArea {
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                            onClicked: bridge.loadLogs()
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
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
                            width: logList.width - 24
                            property var entry: modelData
                            spacing: 1
                            Text {
                                text: (entry && entry.section ? entry.section : "Log") + "  ·  " + (entry && entry.time ? entry.time : "")
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
    }
}
