import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../themes"

Item {
    id: root

    property var config: ({})
    Component.onCompleted: {
        root.config = bridge.getSettings("notifications")
        enabledCheck.checked = root.config.enabled !== false
        soundCombo.currentIndex = soundCombo.options.indexOf(root.config.sound || "default")
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
                    text: qsTr("Notifications & Sounds")
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
                    text: qsTr("System Notifications")
                    color: Theme.accent; font.bold: true; font.family: Theme.fontFamily; font.pixelSize: 14
                }

                CheckBox {
                    id: enabledCheck
                    text: qsTr("Enable Desktop Notifications")
                    font.family: Theme.fontFamily; font.pixelSize: 14
                    contentItem: Text {
                        text: enabledCheck.text
                        font: enabledCheck.font
                        color: Theme.text
                        verticalAlignment: Text.AlignVCenter
                        leftPadding: enabledCheck.indicator.width + enabledCheck.spacing
                    }
                }

                LabeledCombo {
                    id: soundCombo
                    label: qsTr("Notification Sound")
                    options: ["default", "mute", "beep", "chime"]
                    Layout.fillWidth: true
                }

                PillButton {
                    text: qsTr("Save Notification Settings")
                    Layout.topMargin: 10
                    onClicked: {
                        bridge.setSetting("notifications", "enabled", enabledCheck.checked)
                        bridge.setSetting("notifications", "sound", soundCombo.value)
                    }
                }
            }
        }
    }
}
