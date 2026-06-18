import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../themes"

// Slide-in info panel anchored to the right edge. Shows channel details,
// shared-media counts and quick actions. Animated with OutCubic (issue: smooth
// ~150-200ms animations).
Rectangle {
    id: root
    color: Theme.panel
    property bool open: false
    property string channelName: ""
    property string channelId: ""
    signal closed()

    width: Theme.infoPanelWidth

    Behavior on x { NumberAnimation { duration: Theme.anim; easing.type: Theme.easing } }

    Rectangle { width: 1; height: parent.height; color: Theme.divider }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // header
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: Theme.headerHeight
            color: Theme.panel
            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 12
                anchors.rightMargin: 12
                spacing: 10
                Icon {
                    name: "close"; size: 20; color: Theme.textSecondary
                    MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: root.closed() }
                }
                Text {
                    Layout.fillWidth: true
                    text: qsTr("Channel Info")
                    color: Theme.text
                    font.family: Theme.fontFamily
                    font.pixelSize: 16
                    font.bold: true
                }
            }
            Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: Theme.divider }
        }

        // big avatar + name
        ColumnLayout {
            Layout.fillWidth: true
            Layout.topMargin: 22
            spacing: 10
            Avatar {
                Layout.alignment: Qt.AlignHCenter
                name: root.channelName; seed: root.channelId; size: 96
            }
            Text {
                Layout.alignment: Qt.AlignHCenter
                text: root.channelName
                color: Theme.text
                font.family: Theme.fontFamily
                font.pixelSize: 19
                font.bold: true
            }
            Text {
                Layout.alignment: Qt.AlignHCenter
                text: qsTr("news channel")
                color: Theme.textSecondary
                font.family: Theme.fontFamily
                font.pixelSize: 13
            }
        }

        Rectangle { Layout.fillWidth: true; Layout.topMargin: 18; height: 1; color: Theme.divider }

        // About / description (real, non-interactive info — no fake actions)
        ColumnLayout {
            Layout.fillWidth: true
            Layout.leftMargin: 18; Layout.rightMargin: 18; Layout.topMargin: 16
            spacing: 6
            Text {
                text: qsTr("About")
                color: Theme.textSecondary; font.bold: true
                font.family: Theme.fontFamily; font.pixelSize: 12
            }
            Text {
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
                text: qsTr("Offline RSS feed aggregated by OfflineFeed. Open any post to read it offline, or forward the whole channel to Telegram.")
                color: Theme.text; font.family: Theme.fontFamily; font.pixelSize: 14
            }
        }

        Item { Layout.fillHeight: true }
    }
}
