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
                        radius: Theme.radius.lg
                        color: pal.bg
                        border.width: Theme.variant === modelData.id ? 2 : 1
                        border.color: Theme.variant === modelData.id ? Theme.accent : Theme.divider
                        Behavior on border.color { ColorAnimation { duration: Theme.animFast } }
                        Column {
                            anchors.fill: parent
                            anchors.margins: 10
                            spacing: 6
                            Rectangle { width: parent.width * 0.7; height: 16; radius: Theme.radius.sm; color: pal.inBubble }
                            Rectangle { width: parent.width * 0.85; height: 16; radius: Theme.radius.sm; color: pal.inBubble; anchors.right: parent.right }
                            Rectangle { width: parent.width * 0.7; height: 16; radius: Theme.radius.sm; color: pal.outBubble; anchors.right: parent.right }
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
                    width: 30; height: 30; radius: Theme.radius.pill; color: "transparent"
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
                        width: 30; height: 30; radius: Theme.radius.pill; color: modelData
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
                        // RTL behavior intact: turning Persian on falls back to the
                        // Persian font family, off restores the default family.
                        bridge.setRtl(checked)
                        Theme.fontFamily = checked ? Theme.persianFontFamily : Theme.fallbackFontFamily
                        root.applyAll()
                    }
                }
            }

            // ----- Font family (full installed-system list, searchable, live preview) -----
            Text {
                Layout.leftMargin: 20
                text: qsTr("Font Family")
                color: Theme.textSecondary; font.bold: true
                font.family: Theme.fontFamily; font.pixelSize: 13
            }

            // Searchable selector backed by bridge.systemFonts (every installed
            // family). Falls back to the previous hardcoded names if enumeration
            // returned nothing, so this control always works.
            ColumnLayout {
                id: fontPicker
                Layout.leftMargin: 20; Layout.rightMargin: 20
                Layout.fillWidth: true
                spacing: 8

                readonly property var fallbackFonts: ["Roboto", "Vazirmatn", "Arial", "Segoe UI"]
                readonly property var allFonts: (bridge.systemFonts && bridge.systemFonts.length > 0)
                                                ? bridge.systemFonts : fallbackFonts

                // True if `name` is present in the installed list.
                function isInstalled(name) {
                    for (var i = 0; i < allFonts.length; i++)
                        if (allFonts[i] === name) return true
                    return false
                }

                // Safe default: if the saved family is no longer installed, show
                // the first available family (or the theme fallback).
                readonly property string safeCurrent: isInstalled(Theme.fontFamily)
                    ? Theme.fontFamily
                    : (allFonts.length > 0 ? allFonts[0] : Theme.fallbackFontFamily)

                // The field that opens the picker; previews the current font.
                Rectangle {
                    id: fontField
                    Layout.preferredWidth: 260
                    Layout.preferredHeight: 40
                    radius: Theme.radius.md
                    color: Theme.panelAlt
                    border.width: 1
                    border.color: fontPopup.visible ? Theme.accent : Theme.divider
                    Behavior on border.color { ColorAnimation { duration: Theme.animFast } }

                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: 12; anchors.rightMargin: 12
                        spacing: 8
                        Text {
                            Layout.fillWidth: true
                            elide: Text.ElideRight
                            text: fontPicker.safeCurrent
                            color: Theme.text
                            // Preview the selected family in its own font.
                            font.family: fontPicker.safeCurrent
                            font.pixelSize: 15
                        }
                        Text {
                            text: "\u25BE"   // ▾ downward triangle
                            color: Theme.textSecondary
                            font.pixelSize: 12
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            fontSearch.text = ""
                            fontPopup.open()
                        }
                    }
                }

                Popup {
                    id: fontPopup
                    parent: fontField                 // anchor to the trigger field
                    x: 0
                    y: fontField.height + 4
                    width: fontField.width            // always match the field width
                    // Size to content (search box + rows), capped so it never
                    // overflows small windows or leaves a large empty area.
                    height: Math.min(360, 52 + Math.max(fontList.count, 1) * 36)
                    padding: 6
                    modal: false
                    focus: true
                    closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside

                    background: Rectangle {
                        color: Theme.panel
                        border.color: Theme.divider
                        border.width: 1
                        radius: Theme.radius.lg
                    }

                    contentItem: ColumnLayout {
                        spacing: 6

                        // Search box to filter the (potentially huge) family list.
                        TextField {
                            id: fontSearch
                            Layout.fillWidth: true
                            placeholderText: qsTr("Search fonts\u2026")
                            color: Theme.text
                            font.family: Theme.fontFamily
                            font.pixelSize: 14
                            background: Rectangle {
                                color: Theme.panelAlt
                                radius: Theme.radius.md
                                border.color: Theme.divider
                                border.width: 1
                            }
                        }

                        ListView {
                            id: fontList
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            clip: true
                            // Filter the full family list by the search text.
                            model: {
                                var q = fontSearch.text.toLowerCase()
                                if (!q) return fontPicker.allFonts
                                var out = []
                                for (var i = 0; i < fontPicker.allFonts.length; i++) {
                                    if (fontPicker.allFonts[i].toLowerCase().indexOf(q) !== -1)
                                        out.push(fontPicker.allFonts[i])
                                }
                                return out
                            }
                            ScrollBar.vertical: ScrollBar { }

                            delegate: Rectangle {
                                required property var modelData
                                width: fontList.width
                                height: 36
                                radius: Theme.radius.sm
                                color: modelData === fontPicker.safeCurrent ? Theme.hover : "transparent"
                                Text {
                                    anchors.verticalCenter: parent.verticalCenter
                                    anchors.left: parent.left
                                    anchors.leftMargin: 10
                                    anchors.right: parent.right
                                    anchors.rightMargin: 10
                                    elide: Text.ElideRight
                                    text: modelData
                                    color: Theme.text
                                    // Render EVERY item in its own font as a live preview.
                                    font.family: modelData
                                    font.pixelSize: 15
                                }
                                MouseArea {
                                    anchors.fill: parent
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: {
                                        // Persist exactly as before via saveChatAppearance(...).
                                        Theme.fontFamily = modelData
                                        root.applyAll()
                                        fontPopup.close()
                                    }
                                }
                            }
                        }
                    }
                }
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
                        radius: Theme.radius.lg
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
