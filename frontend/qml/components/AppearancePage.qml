import QtQuick
import "../themes"

// Appearance binds directly to the EXISTING writable bridge properties
// (theme / accentOverride / interfaceScale / fontFamily / wallpaperMode),
// which already persist through the bridge's UI-settings store. No new
// persistence code needed here.
//
// ---------------------------------------------------------------------------
//  TELEGRAM-STYLE APPEARANCE PATCH
//  - The plain "Color theme" dropdown is replaced with visual THEME CARDS
//    (Classic / Day / Tinted / Night) that preview each palette, like
//    Telegram Desktop.
//  - The accent row keeps the preset swatches AND adds a "+" custom swatch
//    that opens a full color picker (AccentPickerDialog) so ANY accent color
//    can be chosen — the missing "color palette change".
//  Everything else (wallpaper, reader font, app font, interface scale) is
//  unchanged. The picker writes the same `bridge.accentOverride` the presets
//  already use, so persistence + app-wide re-tint work with no backend edits.
// ---------------------------------------------------------------------------
Item {
    id: page
    property var stack: null
    anchors.fill: parent

    // Preset accent swatches; "" means "use the theme default accent".
    property var accents: [ "", "#3390ec", "#2ea6ff", "#4dcd5e", "#f5a623", "#e8506e", "#9b6dff", "#13b9a8" ]

    // Theme preview cards. Colors mirror the stock per-variant palettes in
    // Theme.qml so each card previews that theme's look (order matches Telegram).
    property var themeCards: [
        { v: "classic", label: qsTr("Classic"), bg: "#18222d", panel: "#222e3a", accent: "#56a3eb" },
        { v: "day",     label: qsTr("Day"),     bg: "#ffffff", panel: "#f4f4f5", accent: "#3390ec" },
        { v: "tinted",  label: qsTr("Tinted"),  bg: "#1a1a2e", panel: "#24243e", accent: "#7a8cff" },
        { v: "night",   label: qsTr("Night"),   bg: "#17212b", panel: "#232e3c", accent: "#5288c1" }
    ]

    // True when the active accent is a custom color (not a preset, not default).
    readonly property bool customAccentActive: bridge.accentOverride !== "" && page.accents.indexOf(bridge.accentOverride) === -1

    property var fontOptions: getFontOptions()
    function getFontOptions() {
        var arr = bridge.systemFonts || []
        var out = []
        var hasCurrentFamily = false
        var hasCurrentReaderFamily = false
        for (var i = 0; i < arr.length; i++) {
            var f = String(arr[i])
            out.push({ value: f, label: f })
            if (f === bridge.fontFamily) hasCurrentFamily = true
            if (f === bridge.readerFontFamily) hasCurrentReaderFamily = true
        }
        if (!hasCurrentFamily && bridge.fontFamily) {
            out.push({ value: bridge.fontFamily, label: bridge.fontFamily })
        }
        if (!hasCurrentReaderFamily && bridge.readerFontFamily && bridge.readerFontFamily !== bridge.fontFamily) {
            out.push({ value: bridge.readerFontFamily, label: bridge.readerFontFamily })
        }
        out.sort(function(a, b) {
            return a.label.localeCompare(b.label, undefined, { sensitivity: 'base' })
        })
        return out
    }

    SettingsHeader {
        id: hd
        anchors.top: parent.top; anchors.left: parent.left; anchors.right: parent.right
        title: qsTr("Appearance")
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

            // ===== Theme (visual cards) =====
            SettingsSectionHeader {
                width: parent.width
                iconName: "palette"; tileColor: "#9b6dff"
                title: qsTr("Theme")
                subtitle: qsTr("Personalize the application look")
            }
            Rectangle {
                width: parent.width; radius: Theme.radius.card; color: Theme.panel; height: cardFlow.implicitHeight + 24
                Flow {
                    id: cardFlow
                    x: 16; y: 12
                    width: parent.width - 32
                    spacing: 14
                    layoutDirection: Theme.rtl ? Qt.RightToLeft : Qt.LeftToRight
                    Repeater {
                        model: page.themeCards
                        delegate: Item {
                            id: card
                            required property var modelData
                            readonly property bool selected: bridge.theme === modelData.v
                            width: 128; height: 116
                            Column {
                                anchors.top: parent.top; anchors.horizontalCenter: parent.horizontalCenter
                                spacing: 8
                                // Mini chat preview
                                Rectangle {
                                    width: 128; height: 84; radius: Theme.radius.md
                                    color: card.modelData.bg
                                    border.width: card.selected ? 2 : 1
                                    border.color: card.selected ? Theme.accent : Theme.divider
                                    clip: true
                                    Rectangle { x: 8; y: 8; width: parent.width - 16; height: 15; radius: 5; color: card.modelData.panel }
                                    Rectangle { x: 8; y: 32; width: 62; height: 13; radius: 6; color: card.modelData.panel }
                                    Rectangle { x: 8; y: 49; width: 44; height: 13; radius: 6; color: card.modelData.panel }
                                    Rectangle { x: parent.width - 8 - 58; y: 64; width: 58; height: 13; radius: 6; color: card.modelData.accent }
                                }
                                // Radio + label
                                Row {
                                    anchors.horizontalCenter: parent.horizontalCenter
                                    spacing: 6
                                    Rectangle {
                                        anchors.verticalCenter: parent.verticalCenter
                                        width: 16; height: 16; radius: 8
                                        color: "transparent"; border.width: 2
                                        border.color: card.selected ? Theme.accent : Theme.textSecondary
                                        Rectangle { anchors.centerIn: parent; width: 8; height: 8; radius: 4; color: Theme.accent; visible: card.selected }
                                    }
                                    Text {
                                        anchors.verticalCenter: parent.verticalCenter
                                        text: card.modelData.label
                                        color: Theme.text; font.family: Theme.fontFamily; font.pixelSize: 13
                                        font.bold: card.selected
                                    }
                                }
                            }
                            MouseArea {
                                anchors.fill: parent
                                cursorShape: Qt.PointingHandCursor
                                onClicked: bridge.theme = card.modelData.v
                            }
                        }
                    }
                }
            }

            // ===== Chat wallpaper =====
            SettingsSectionHeader {
                width: parent.width
                iconName: "image"; tileColor: "#3390ec"
                title: qsTr("Chat Wallpaper")
                subtitle: qsTr("Background for conversation views")
            }
            Rectangle {
                width: parent.width; radius: Theme.radius.card; color: Theme.panel; clip: true; height: c1.implicitHeight
                Column {
                    id: c1; width: parent.width
                    SettingsSelect {
                        id: selWall
                        label: qsTr("Chat wallpaper")
                        options: [ { value: "pattern", label: qsTr("Pattern") }, { value: "solid", label: qsTr("Solid") }, { value: "image", label: qsTr("Custom image") }, { value: "none", label: qsTr("None") } ]
                        value: bridge.wallpaperMode
                        onActivatedValue: bridge.wallpaperMode = value
                    }
                }
            }

            // ---- Item 8: custom wallpaper image ----
            Rectangle {
                width: parent.width; radius: Theme.radius.card; color: Theme.panel; height: wallRow.implicitHeight + 24
                Row {
                    id: wallRow
                    x: 16; y: 12
                    width: parent.width - 32
                    spacing: 12
                    LayoutMirroring.enabled: Theme.rtl
                    Column {
                        width: parent.width - 150
                        spacing: 2
                        Text {
                            width: parent.width
                            text: qsTr("Custom wallpaper image")
                            color: Theme.text; font.family: Theme.fontFamily; font.pixelSize: 15
                            horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
                        }
                        Text {
                            width: parent.width
                            text: bridge.wallpaperImage !== ""
                                ? qsTr("An image is set. Pick \u201cCustom image\u201d above to show it.")
                                : qsTr("Pick an image from your computer to use as the chat background.")
                            color: Theme.textSecondary; font.family: Theme.fontFamily; font.pixelSize: 12
                            wrapMode: Text.WordWrap
                            horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
                        }
                    }
                    Rectangle {
                        anchors.verticalCenter: parent.verticalCenter
                        width: 130; height: 34; radius: Theme.radius.sm
                        color: chooseMouse.containsMouse ? Theme.accent : Theme.bg
                        border.width: 1; border.color: Theme.accent
                        Behavior on color { ColorAnimation { duration: Theme.animFast } }
                        Row {
                            anchors.centerIn: parent
                            spacing: 6
                            Icon { anchors.verticalCenter: parent.verticalCenter; name: "image"; size: 15; color: chooseMouse.containsMouse ? Theme.accentText : Theme.accent }
                            Text {
                                anchors.verticalCenter: parent.verticalCenter
                                text: qsTr("Choose image")
                                color: chooseMouse.containsMouse ? Theme.accentText : Theme.accent
                                font.family: Theme.fontFamily; font.pixelSize: 13; font.bold: true
                            }
                        }
                        MouseArea {
                            id: chooseMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: bridge.pickWallpaperImage()
                        }
                    }
                }
            }

            // ---- Item 1: independent offline-reader font ----
            SettingsSectionHeader {
                width: parent.width
                iconName: "web-viewer"; tileColor: "#e8506e"
                title: qsTr("Reader Font")
                subtitle: qsTr("Offline article text style")
            }
            Rectangle {
                width: parent.width; radius: Theme.radius.card; color: Theme.panel; clip: true; height: c3.implicitHeight
                Column {
                    id: c3; width: parent.width
                    SettingsSelect {
                        id: selReaderFont
                        label: qsTr("Reader font (offline viewer)")
                        options: page.fontOptions
                        value: bridge.readerFontFamily
                        onActivatedValue: bridge.setReaderFont(value)
                    }
                }
            }

            // ===== Accent color (presets + custom picker) =====
            SettingsSectionHeader {
                width: parent.width
                iconName: "palette"; tileColor: "#13b9a8"
                title: qsTr("Accent Color")
                subtitle: qsTr("Custom tint for buttons and highlights")
            }
            Rectangle {
                width: parent.width; radius: Theme.radius.card; color: Theme.panel; height: swatchFlow.implicitHeight + 24
                Flow {
                    id: swatchFlow
                    x: 16; y: 12
                    width: parent.width - 32
                    spacing: 12
                    layoutDirection: Theme.rtl ? Qt.RightToLeft : Qt.LeftToRight
                    Repeater {
                        model: page.accents
                        delegate: Rectangle {
                            required property var modelData
                            width: 34; height: 34; radius: Theme.radius.pill
                            // Bug #2: the default/reset swatch ("") was painted with the
                            // page background and a faint divider border, making it nearly
                            // invisible on dark themes (looked like 7 swatches, not 8).
                            // Give it a clearly visible border (and keep the palette glyph
                            // below) so it reads as a real, clickable "reset to default".
                            color: modelData === "" ? Theme.bg : modelData
                            border.width: (bridge.accentOverride === modelData) ? 3 : (modelData === "" ? 2 : 1)
                            border.color: (bridge.accentOverride === modelData)
                                          ? Theme.accent
                                          : (modelData === "" ? Theme.textSecondary : Theme.divider)
                            Icon {
                                visible: modelData === ""
                                anchors.centerIn: parent; name: "palette"; size: 18; color: Theme.textSecondary
                            }
                            MouseArea {
                                anchors.fill: parent
                                cursorShape: Qt.PointingHandCursor
                                onClicked: bridge.accentOverride = modelData
                            }
                        }
                    }
                    // ---- Custom color swatch (opens the picker) ----
                    Rectangle {
                        id: customSwatch
                        width: 34; height: 34; radius: Theme.radius.pill
                        color: page.customAccentActive ? bridge.accentOverride : Theme.bg
                        border.width: page.customAccentActive ? 3 : 2
                        border.color: page.customAccentActive ? Theme.accent : Theme.divider
                        Icon {
                            visible: !page.customAccentActive
                            anchors.centerIn: parent; name: "plus"; size: 16; color: Theme.textSecondary
                        }
                        MouseArea {
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                            onClicked: accentPicker.openWith(bridge.accentOverride)
                        }
                    }
                }
            }
            Text {
                width: parent.width
                text: qsTr("Tap + to choose any custom color. The accent re-tints the whole app.")
                color: Theme.textSecondary; font.family: Theme.fontFamily; font.pixelSize: 12
                wrapMode: Text.WordWrap
                horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
            }

            // ===== Interface =====
            SettingsSectionHeader {
                width: parent.width
                iconName: "settings"; tileColor: "#2ea6ff"
                title: qsTr("Interface")
                subtitle: qsTr("Font sizes and display scaling")
            }
            Rectangle {
                width: parent.width; radius: Theme.radius.card; color: Theme.panel; clip: true; height: c2.implicitHeight
                Column {
                    id: c2; width: parent.width
                    SettingsSelect {
                        id: selAppFont
                        label: qsTr("App font")
                        options: page.fontOptions
                        value: bridge.fontFamily
                        onActivatedValue: bridge.fontFamily = value // whole-UI font (Theme.fontFamily)
                    }
                    SettingsSlider {
                        id: slScale
                        label: qsTr("Interface scale")
                        from: 0.8; to: 1.4; stepSize: 0.05; suffix: "%"
                        value: bridge.interfaceScale
                        onMoved: bridge.interfaceScale = value
                    }
                }
            }
        }
    }

    // Custom accent color picker (Telegram-style). Writes bridge.accentOverride.
    AccentPickerDialog {
        id: accentPicker
        onAccepted: function(hex) { bridge.accentOverride = hex }
    }
}
