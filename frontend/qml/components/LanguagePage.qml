import QtQuick
import "../themes"

// Language. The RTL toggle binds to the EXISTING writable bridge.rtl property
// (drives LayoutMirroring app-wide). The chosen language persists in group
// "language"; selecting Persian also turns RTL on. See Notes re: translations.
Item {
    id: page
    property var stack: null
    anchors.fill: parent

    SettingsHeader {
        id: hd
        anchors.top: parent.top; anchors.left: parent.left; anchors.right: parent.right
        title: qsTr("Language")
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

            Rectangle {
                width: parent.width; radius: 10; color: Theme.panel; clip: true; height: c1.implicitHeight
                Column {
                    id: c1; width: parent.width
                    SettingsSelect {
                        id: selLang
                        label: qsTr("Interface language")
                        options: [ { value: "en", label: "English" }, { value: "fa", label: "فارسی" } ]
                        onActivatedValue: {
                            bridge.settingsSetValue("language", "lang", value)
                            if (value === "fa") { bridge.rtl = true; tgRtl.checked = true }
                        }
                    }
                    SettingsToggle {
                        id: tgRtl
                        label: qsTr("Right-to-left layout")
                        description: qsTr("Mirror the interface for Persian / Arabic")
                        onToggled: bridge.rtl = value
                    }
                }
            }
        }
    }

    Component.onCompleted: {
        var g = bridge.settingsGetGroup("language")
        selLang.value = (g.lang === undefined) ? (bridge.rtl ? "fa" : "en") : g.lang
        tgRtl.checked = bridge.rtl
    }
}
