import QtQuick
import "../themes"

// Advanced: backend info, verbose logging (persists in group "advanced"), and a
// shortcut into the System Logs chat (the backend's existing SystemLogs channel).
Item {
    id: page
    property var stack: null
    anchors.fill: parent

    SettingsHeader {
        id: hd
        anchors.top: parent.top; anchors.left: parent.left; anchors.right: parent.right
        title: qsTr("Advanced")
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
                width: parent.width; text: qsTr("Backend")
                color: Theme.accent; font.family: Theme.fontFamily; font.pixelSize: 13; font.bold: true
                horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
            }
            Rectangle {
                width: parent.width; radius: 10; color: Theme.panel; clip: true; height: c1.implicitHeight
                Column {
                    id: c1; width: parent.width
                    SettingsTextField {
                        id: tfPort
                        label: qsTr("Backend port (applies on next launch)")
                        placeholder: "8080"
                        onEdited: bridge.settingsSetValue("advanced", "backend_port", value)
                    }
                    SettingsToggle {
                        id: tgVerbose
                        label: qsTr("Verbose logging")
                        onToggled: bridge.settingsSetValue("advanced", "verbose_logging", value)
                    }
                }
            }

            Text {
                width: parent.width; text: qsTr("Diagnostics")
                color: Theme.accent; font.family: Theme.fontFamily; font.pixelSize: 13; font.bold: true
                horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
            }
            Rectangle {
                width: parent.width; radius: 10; color: Theme.panel; height: diagCol.implicitHeight + 24
                Column {
                    id: diagCol
                    x: 16; y: 12; width: parent.width - 32; spacing: 12
                    Text {
                        width: parent.width; wrapMode: Text.WordWrap
                        text: qsTr("Open the System Logs channel to inspect backend activity, or run 'python -m frontend.doctor' from a terminal for a full diagnostic report.")
                        color: Theme.textSecondary; font.family: Theme.fontFamily; font.pixelSize: 13
                        horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
                    }
                    SettingsButton {
                        text: qsTr("Open System Logs")
                        primary: false
                        onClicked: {
                            bridge.setTab("entertainment")
                            bridge.openChat("SystemLogs")
                        }
                    }
                }
            }
        }
    }

    Component.onCompleted: {
        var g = bridge.settingsGetGroup("advanced")
        tfPort.text = (g.backend_port === undefined || g.backend_port === null) ? "8080" : g.backend_port
        tgVerbose.checked = (g.verbose_logging === undefined) ? false : g.verbose_logging
    }
}
