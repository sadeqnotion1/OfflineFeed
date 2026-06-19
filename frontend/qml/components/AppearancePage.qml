import QtQuick
import "../themes"

// Appearance binds directly to the EXISTING writable bridge properties
// (theme / accentOverride / interfaceScale / fontFamily / wallpaperMode),
// which already persist through the bridge's UI-settings store. No new
// persistence code needed here.
Item {
    id: page
    property var stack: null
    anchors.fill: parent

    // Preset accent swatches; "" means "use the theme default accent".
    property var accents: [ "", "#3390ec", "#2ea6ff", "#4dcd5e", "#f5a623", "#e8506e", "#9b6dff", "#13b9a8" ]

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
            spacing: 8

            Text {
                width: parent.width; text: qsTr("Theme")
                color: Theme.accent; font.family: Theme.fontFamily; font.pixelSize: 13; font.bold: true
                horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
            }
            Rectangle {
                width: parent.width; radius: 10; color: Theme.panel; clip: true; height: c1.implicitHeight
                Column {
                    id: c1; width: parent.width
                    SettingsSelect {
                        id: selTheme
                        label: qsTr("Color theme")
                        options: [ { value: "night", label: qsTr("Dark") }, { value: "day", label: qsTr("Light") },
                                   { value: "classic", label: qsTr("Classic") }, { value: "tinted", label: qsTr("Tinted") } ]
                        value: bridge.theme
                        onActivatedValue: bridge.theme = value
                    }
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
                width: parent.width; radius: 10; color: Theme.panel; height: wallRow.implicitHeight + 24
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
                        width: 130; height: 34; radius: 8
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
            Text {
                width: parent.width; text: qsTr("Reader")
                color: Theme.accent; font.family: Theme.fontFamily; font.pixelSize: 13; font.bold: true
                horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
            }
            Rectangle {
                width: parent.width; radius: 10; color: Theme.panel; clip: true; height: c3.implicitHeight
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

            Text {
                width: parent.width; text: qsTr("Accent color")
                color: Theme.accent; font.family: Theme.fontFamily; font.pixelSize: 13; font.bold: true
                horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
            }
            Rectangle {
                width: parent.width; radius: 10; color: Theme.panel; height: swatchFlow.implicitHeight + 24
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
                            width: 34; height: 34; radius: 17
                            color: modelData === "" ? Theme.bg : modelData
                            border.width: (bridge.accentOverride === modelData) ? 3 : 1
                            border.color: (bridge.accentOverride === modelData) ? Theme.accent : Theme.divider
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
                }
            }

            Text {
                width: parent.width; text: qsTr("Interface")
                color: Theme.accent; font.family: Theme.fontFamily; font.pixelSize: 13; font.bold: true
                horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
            }
            Rectangle {
                width: parent.width; radius: 10; color: Theme.panel; clip: true; height: c2.implicitHeight
                Column {
                    id: c2; width: parent.width
                    SettingsSelect {
                        id: selAppFont
                        label: qsTr("App font")
                        options: page.fontOptions
                        value: bridge.fontFamily
                        onActivatedValue: bridge.fontFamily = value   // whole-UI font (Theme.fontFamily)
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
}
