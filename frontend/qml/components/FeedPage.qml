import QtQuick
import "../themes"

// Feed & Chat Settings: reader behavior + scraping fallback persist in group
// "feed"; the chat wallpaper binds to the existing writable bridge.wallpaperMode
// property so it round-trips exactly like the other appearance settings.
Item {
    id: page
    property var stack: null
    anchors.fill: parent

    SettingsHeader {
        id: hd
        anchors.top: parent.top; anchors.left: parent.left; anchors.right: parent.right
        title: qsTr("Feed & Chat Settings")
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
                width: parent.width; text: qsTr("Reader")
                color: Theme.accent; font.family: Theme.fontFamily; font.pixelSize: 13; font.bold: true
                horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
            }
            Rectangle {
                width: parent.width; radius: 10; color: Theme.panel; clip: true; height: c1.implicitHeight
                Column {
                    id: c1; width: parent.width
                    SettingsSelect {
                        id: selReader
                        label: qsTr("Reader mode")
                        options: [ { value: "readable", label: qsTr("Readable") }, { value: "original", label: qsTr("Original HTML") } ]
                        onActivatedValue: bridge.settingsSetValue("feed", "reader_mode", value)
                    }
                    SettingsToggle {
                        id: tgScrape
                        label: qsTr("Scraping fallback"); description: qsTr("Fetch the full article when the RSS body is truncated")
                        onToggled: bridge.settingsSetValue("feed", "scrape_fallback", value)
                    }
                    SettingsToggle {
                        id: tgImages
                        label: qsTr("Auto-load images")
                        onToggled: bridge.settingsSetValue("feed", "images_autoload", value)
                    }
                    SettingsToggle {
                        id: tgExternal
                        label: qsTr("Open links in external browser")
                        onToggled: bridge.settingsSetValue("feed", "open_external", value)
                    }
                }
            }

            Text {
                width: parent.width; text: qsTr("Chat")
                color: Theme.accent; font.family: Theme.fontFamily; font.pixelSize: 13; font.bold: true
                horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
            }
            Rectangle {
                width: parent.width; radius: 10; color: Theme.panel; clip: true; height: c2.implicitHeight
                Column {
                    id: c2; width: parent.width
                    SettingsSelect {
                        id: selWall
                        label: qsTr("Chat wallpaper")
                        options: [ { value: "pattern", label: qsTr("Pattern") }, { value: "solid", label: qsTr("Solid") }, { value: "none", label: qsTr("None") } ]
                        value: bridge.wallpaperMode
                        onActivatedValue: bridge.wallpaperMode = value
                    }
                }
            }
        }
    }

    Component.onCompleted: {
        var g = bridge.settingsGetGroup("feed")
        selReader.value     = (g.reader_mode === undefined) ? "readable" : g.reader_mode
        tgScrape.checked    = (g.scrape_fallback === undefined) ? true : g.scrape_fallback
        tgImages.checked    = (g.images_autoload === undefined) ? true : g.images_autoload
        tgExternal.checked  = (g.open_external === undefined) ? false : g.open_external
    }
}
