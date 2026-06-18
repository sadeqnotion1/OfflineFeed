import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../themes"

Item {
    id: root

    property var config: ({})
    Component.onCompleted: {
        root.config = bridge.getSettings("language")
        langCombo.currentIndex = langCombo.options.indexOf(root.config.language || "en")
        rtlSwitch.checked = bridge.rtl
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
                    text: qsTr("Language & RTL")
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
                    text: qsTr("Interface Language")
                    color: Theme.accent; font.bold: true; font.family: Theme.fontFamily; font.pixelSize: 14
                }

                LabeledCombo {
                    id: langCombo
                    label: qsTr("Choose Language")
                    options: ["en", "fa", "ru", "ar"]
                    Layout.fillWidth: true
                }

                Rectangle { Layout.fillWidth: true; height: 1; color: Theme.divider }

                Text {
                    text: qsTr("Right-to-Left Layout (RTL)")
                    color: Theme.accent; font.bold: true; font.family: Theme.fontFamily; font.pixelSize: 14
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 12

                    Text {
                        text: qsTr("Force Right-to-Left (Persian/Arabic Mode)")
                        color: Theme.text
                        font.family: Theme.fontFamily; font.pixelSize: 14
                        Layout.fillWidth: true
                    }

                    Switch {
                        id: rtlSwitch
                        checked: bridge.rtl
                        onToggled: {
                            bridge.setSetting("language", "rtl", checked)
                        }
                    }
                }

                PillButton {
                    text: qsTr("Save Language Settings")
                    Layout.topMargin: 10
                    onClicked: {
                        bridge.setSetting("language", "language", langCombo.value)
                        bridge.setSetting("language", "rtl", rtlSwitch.checked)
                    }
                }
            }
        }
    }
}
