import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../themes"

Item {
    id: root

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
                    text: qsTr("Appearance")
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
                Layout.topMargin: 12; Layout.bottomMargin: 30

                // Embed the standard ChatSettings component
                ChatSettings {
                    id: chatSettings
                    Layout.fillWidth: true
                    Layout.preferredHeight: 470
                }

                Rectangle { Layout.fillWidth: true; height: 1; color: Theme.divider; Layout.leftMargin: 20; Layout.rightMargin: 20; Layout.topMargin: 16; Layout.bottomMargin: 16 }

                // Interface Scale
                ColumnLayout {
                    Layout.leftMargin: 20; Layout.rightMargin: 20
                    spacing: 8
                    Layout.fillWidth: true

                    Text {
                        text: qsTr("Interface Scale")
                        color: Theme.textSecondary; font.bold: true
                        font.family: Theme.fontFamily; font.pixelSize: 13
                    }

                    RowLayout {
                        spacing: 12
                        Layout.fillWidth: true

                        Slider {
                            id: scaleSlider
                            from: 1.0
                            to: 1.5
                            stepSize: 0.05
                            value: bridge.interfaceScale || 1.0
                            Layout.fillWidth: true
                            onMoved: {
                                bridge.setSetting("appearance", "interface_scale", scaleSlider.value)
                            }
                        }

                        Text {
                            text: Math.round(scaleSlider.value * 100) + "%"
                            color: Theme.text
                            font.family: Theme.fontFamily; font.pixelSize: 14; font.bold: true
                            Layout.preferredWidth: 40
                        }
                    }
                }
            }
        }
    }
}
