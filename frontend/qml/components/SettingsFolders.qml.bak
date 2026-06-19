import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
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
                    text: qsTr("Folders & News Sources")
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

                // Add source form
                Text {
                    text: qsTr("Add News Source")
                    color: Theme.accent; font.bold: true; font.family: Theme.fontFamily; font.pixelSize: 14
                    Layout.bottomMargin: 10
                }

                GridLayout {
                    Layout.fillWidth: true
                    columns: 2
                    columnSpacing: 12
                    rowSpacing: 10
                    Field { id: srcName;    label: qsTr("Name");      placeholder: qsTr("e.g. Variety") }
                    Field { id: srcUrl;     label: qsTr("Feed URL");  placeholder: qsTr("https://...") }
                    LabeledCombo { id: srcSection;  label: qsTr("Section");  options: ["Entertainment", "Sports", "Technology"] }
                    Field { id: srcCategory; label: qsTr("Category"); placeholder: qsTr("e.g. Entertainment") }
                }

                RowLayout {
                    Layout.topMargin: 10
                    Layout.bottomMargin: 20
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

                Rectangle { Layout.fillWidth: true; height: 1; color: Theme.divider; Layout.bottomMargin: 16 }

                // Existing custom sources list
                Text {
                    text: qsTr("Your custom sources")
                    color: Theme.textSecondary; font.bold: true
                    font.family: Theme.fontFamily; font.pixelSize: 13
                    Layout.bottomMargin: 8
                }

                ColumnLayout {
                    Layout.fillWidth: true
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
                                    name: "image"; size: 18; color: Theme.accent
                                    MouseArea {
                                        anchors.fill: parent; cursorShape: Qt.PointingHandCursor
                                        onClicked: {
                                            avatarFileDialog.targetSourceName = model.name
                                            avatarFileDialog.open()
                                        }
                                    }
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
            }
        }
    }

    FileDialog {
        id: avatarFileDialog
        title: qsTr("Select Channel Avatar")
        nameFilters: [ "Image files (*.png *.jpg *.jpeg *.gif *.webp *.ico)" ]
        property string targetSourceName: ""
        onAccepted: {
            if (selectedFile !== "") {
                bridge.setSourceAvatar(targetSourceName, selectedFile.toString())
            }
        }
    }
}
