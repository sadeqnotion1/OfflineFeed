import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../themes"

Item {
    id: root

    property var config: ({})
    Component.onCompleted: {
        root.config = bridge.getSettings("privacy")
        historyCombo.currentIndex = historyCombo.options.indexOf(root.config.keep_history || "forever")
        lockCode.value = root.config.lock_code || ""
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
                    text: qsTr("Privacy & Security")
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
                    text: qsTr("Data Retention")
                    color: Theme.accent; font.bold: true; font.family: Theme.fontFamily; font.pixelSize: 14
                }

                LabeledCombo {
                    id: historyCombo
                    label: qsTr("Keep Message History")
                    options: ["forever", "1 week", "1 month", "1 year"]
                    Layout.fillWidth: true
                }

                Rectangle { Layout.fillWidth: true; height: 1; color: Theme.divider }

                Text {
                    text: qsTr("Local Application Lock")
                    color: Theme.accent; font.bold: true; font.family: Theme.fontFamily; font.pixelSize: 14
                }

                Field {
                    id: lockCode
                    label: qsTr("Local Passcode")
                    placeholder: qsTr("Leave blank to disable lock")
                    Layout.fillWidth: true
                }

                PillButton {
                    text: qsTr("Save Privacy Settings")
                    Layout.topMargin: 10
                    onClicked: {
                        bridge.setSetting("privacy", "keep_history", historyCombo.value)
                        bridge.setSetting("privacy", "lock_code", lockCode.value)
                    }
                }
            }
        }
    }
}
