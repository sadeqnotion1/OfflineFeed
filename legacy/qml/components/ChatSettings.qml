import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../themes"

// Chat-appearance settings (issue #7). Theme picker (Classic/Day/Tinted/Night),
// name color, auto-night mode, font family, chat wallpaper. Pure presentation;
// applies to the Theme singleton and persists through the bridge.
Rectangle {
    id: root
    color: Theme.bg

    function applyAll() {
        bridge.saveChatAppearance(Theme.variant, Theme.accentOverride,
                                  autoNight.checked, Theme.fontFamily, Theme.wallpaperMode)
    }

    ScrollView {
        anchors.fill: parent
        contentWidth: availableWidth
        clip: true

        ColumnLayout {
            width: root.width
            spacing: 18

            // ----- Theme picker -----
            Text {
                Layout.leftMargin: 20; Layout.topMargin: 20
                text: qsTr("Chat Theme")
                color: Theme.textSecondary; font.bold: true
                font.family: Theme.fontFamily; font.pixelSize: 13
            }
            RowLayout {
                Layout.leftMargin: 20; Layout.rightMargin: 20
                spacing: 12
                Repeater {
                    model: [
                        { id: "classic", label: qsTr("Classic") },
                        { id: "day",     label: qsTr("Day") },
                        { id: "tinted",  label: qsTr("Tinted") },
                        { id: "night",   label: qsTr("Night") }
                    ]
                    delegate: Rectangle {
                        required property var modelData
                        readonly property var pal: Theme.palettes[modelData.id]
                        Layout.preferredWidth: 92
                        Layout.preferredHeight: 116
                        radius: 12
                        color: pal.bg
                        border.width: Theme.variant === modelData.id ? 2 : 1
                        border.color: Theme.variant === modelData.id ? Theme.accent : Theme.divider
                        Behavior on border.color { ColorAnimation { duration: Theme.animFast } }
                        Column {
                            anchors.fill: parent
                            anchors.margins: 10
                            spacing: 6
                            Rectangle { width: parent.width * 0.7; height: 16; radius: 8; color: pal.inBubble }
                            Rectangle { width: parent.width * 0.85; height: 16; radius: 8; color: pal.inBubble; anchors.right: parent.right }
                            Rectangle { width: parent.width * 0.7; height: 16; radius: 8; color: pal.outBubble; anchors.right: parent.right }
                            Item { height: 4; width: 1 }
                            Text {
                                anchors.horizontalCenter: parent.horizontalCenter
                                text: modelData.label
                                color: pal.text
                                font.family: Theme.fontFamily; font.pixelSize: 12; font.bold: true
                            }
                        }
                        MouseArea {
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                            // Source of truth is the bridge; Main.qml's Binding
                            // pushes bridge.theme -> Theme.variant. Writing
                            // Theme.variant directly here fought that binding.
                            onClicked: bridge.setTheme(modelData.id)
                        }
                    }
                }
            }

            Rectangle { Layout.fillWidth: true; Layout.leftMargin: 20; Layout.rightMargin: 20; height: 1; color: Theme.divider }

            // ----- Accent color (actually recolors the app accent) -----
            Text {
                Layout.leftMargin: 20
                text: qsTr("Accent Color")
                color: Theme.textSecondary; font.bold: true
                font.family: Theme.fontFamily; font.pixelSize: 13
            }
            RowLayout {
                Layout.leftMargin: 20; Layout.rightMargin: 20
                spacing: 10
                // First swatch resets to the theme's default accent.
                Rectangle {
                    width: 30; height: 30; radius: 15; color: "transparent"
                    border.width: Theme.accentOverride === "" ? 3 : 1
                    border.color: Theme.accentOverride === "" ? Theme.text : Theme.divider
                    Icon { anchors.centerIn: parent; name: "refresh"; size: 14; color: Theme.textSecondary }
                    MouseArea {
                        anchors.fill: parent; cursorShape: Qt.PointingHandCursor
                        onClicked: { Theme.accentOverride = ""; root.applyAll(); }
                    }
                }
                Repeater {
                    model: ["#e0565b", "#e8a23d", "#4fae4e", "#3390ec", "#8a6df0", "#d669ed", "#37b6c4"]
                    delegate: Rectangle {
                        required property var modelData
                        width: 30; height: 30; radius: 15; color: modelData
                        border.width: Theme.accentOverride === modelData ? 3 : 0
                        border.color: Theme.text
                        MouseArea {
                            anchors.fill: parent; cursorShape: Qt.PointingHandCursor
                            onClicked: { Theme.accentOverride = modelData; root.applyAll(); }
                        }
                    }
                }
            }

            Rectangle { Layout.fillWidth: true; Layout.leftMargin: 20; Layout.rightMargin: 20; height: 1; color: Theme.divider }

            // ----- Auto-night mode -----
            RowLayout {
                Layout.leftMargin: 20; Layout.rightMargin: 20
                Layout.fillWidth: true
                Text {
                    Layout.fillWidth: true
                    text: qsTr("Auto-Night Mode")
                    color: Theme.text; font.family: Theme.fontFamily; font.pixelSize: 15
                }
                Switch {
                    id: autoNight
                    onToggled: root.applyAll()
                }
            }

            // ----- Interface direction (Persian / RTL) -----
            RowLayout {
                Layout.leftMargin: 20; Layout.rightMargin: 20
                Layout.fillWidth: true
                Text {
                    Layout.fillWidth: true
                    text: qsTr("Persian / RTL layout")
                    color: Theme.text; font.family: Theme.fontFamily; font.pixelSize: 15
                }
                Switch {
                    checked: Theme.rtl
                    onToggled: {
                        bridge.setRtl(checked)
                        Theme.fontFamily = checked ? Theme.persianFontFamily : "Roboto"
                        root.applyAll()
                    }
                }
            }

            // ----- Font family -----
            Text {
                Layout.leftMargin: 20
                text: qsTr("Font Family")
                color: Theme.textSecondary; font.bold: true
                font.family: Theme.fontFamily; font.pixelSize: 13
            }
            ComboBox {
                Layout.leftMargin: 20; Layout.rightMargin: 20
                Layout.preferredWidth: 240
                model: ["Roboto", "Vazirmatn", "Arial", "Segoe UI"]
                currentIndex: Math.max(0, model.indexOf(Theme.fontFamily))
                onActivated: { Theme.fontFamily = currentText; root.applyAll(); }
            }

            // ----- Chat wallpaper -----
            Text {
                Layout.leftMargin: 20
                text: qsTr("Chat Wallpaper")
                color: Theme.textSecondary; font.bold: true
                font.family: Theme.fontFamily; font.pixelSize: 13
            }
            RowLayout {
                Layout.leftMargin: 20; Layout.rightMargin: 20; Layout.bottomMargin: 24
                spacing: 12
                Repeater {
                    model: [
                        { id: "pattern", label: qsTr("Pattern") },
                        { id: "solid",   label: qsTr("Solid") },
                        { id: "none",    label: qsTr("None") }
                    ]
                    delegate: Rectangle {
                        required property var modelData
                        Layout.preferredWidth: 80; Layout.preferredHeight: 56
                        radius: 10
                        color: Theme.wallpaper
                        border.width: Theme.wallpaperMode === modelData.id ? 2 : 1
                        border.color: Theme.wallpaperMode === modelData.id ? Theme.accent : Theme.divider
                        Text {
                            anchors.centerIn: parent
                            text: modelData.label
                            color: Theme.text; font.family: Theme.fontFamily; font.pixelSize: 12
                        }
                        MouseArea {
                            anchors.fill: parent; cursorShape: Qt.PointingHandCursor
                            onClicked: { Theme.wallpaperMode = modelData.id; root.applyAll(); }
                        }
                    }
                }
            }
        }
    }
}
