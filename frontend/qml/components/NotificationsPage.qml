import QtQuick
import "../themes"

// Notifications & Sounds. Values persist in the existing UI-settings store via
// bridge.settingsGetGroup/settingsSetValue (group "notifications").
Item {
    id: page
    property var stack: null
    anchors.fill: parent

    SettingsHeader {
        id: hd
        anchors.top: parent.top; anchors.left: parent.left; anchors.right: parent.right
        title: qsTr("Notifications & Sounds")
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

            SettingsSectionHeader {
                width: parent.width
                iconName: "bell"; tileColor: "#e8506e"
                title: qsTr("Notifications & Sounds")
                subtitle: qsTr("Alerts and updates configuration")
            }

            Rectangle {
                width: parent.width; radius: Theme.radius.card; color: Theme.panel; clip: true; height: card.implicitHeight
                Column {
                    id: card; width: parent.width
                    SettingsToggle { id: tgEnabled; label: qsTr("Enable notifications");  description: qsTr("Show alerts when new feed items are reposted")
                        onToggled: bridge.settingsSetValue("notifications", "enabled", value) }
                    SettingsToggle { id: tgSound;   label: qsTr("Play sound")
                        onToggled: bridge.settingsSetValue("notifications", "sound", value) }
                    SettingsToggle { id: tgPreview; label: qsTr("Show message preview")
                        onToggled: bridge.settingsSetValue("notifications", "preview", value) }
                    SettingsToggle { id: tgRefresh; label: qsTr("Alert on feed refresh errors")
                        onToggled: bridge.settingsSetValue("notifications", "refresh_alerts", value) }
                }
            }
        }
    }

    Component.onCompleted: {
        var g = bridge.settingsGetGroup("notifications")
        tgEnabled.checked = (g.enabled === undefined) ? true  : g.enabled
        tgSound.checked   = (g.sound === undefined)   ? true  : g.sound
        tgPreview.checked = (g.preview === undefined) ? true  : g.preview
        tgRefresh.checked = (g.refresh_alerts === undefined) ? false : g.refresh_alerts
    }
}
