import QtQuick
import "../themes"

// Privacy & Security. Persists in group "privacy".
Item {
    id: page
    property var stack: null
    anchors.fill: parent

    SettingsHeader {
        id: hd
        anchors.top: parent.top; anchors.left: parent.left; anchors.right: parent.right
        title: qsTr("Privacy & Security")
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
                width: parent.width; radius: Theme.radius.lg; color: Theme.panel; clip: true; height: card.implicitHeight
                Column {
                    id: card; width: parent.width
                    SettingsToggle { id: tgHistory; label: qsTr("Keep read/article history"); description: qsTr("Remember which items you have already opened")
                        onToggled: bridge.settingsSetValue("privacy", "save_history", value) }
                    SettingsToggle { id: tgClear;   label: qsTr("Clear history on exit")
                        onToggled: bridge.settingsSetValue("privacy", "clear_on_exit", value) }
                    SettingsToggle { id: tgTelemetry; label: qsTr("Anonymous usage diagnostics"); description: qsTr("Off by default. Nothing is sent unless enabled.")
                        onToggled: bridge.settingsSetValue("privacy", "telemetry", value) }
                }
            }
        }
    }

    Component.onCompleted: {
        var g = bridge.settingsGetGroup("privacy")
        tgHistory.checked   = (g.save_history === undefined) ? true  : g.save_history
        tgClear.checked     = (g.clear_on_exit === undefined) ? false : g.clear_on_exit
        tgTelemetry.checked = (g.telemetry === undefined) ? false : g.telemetry
    }
}
