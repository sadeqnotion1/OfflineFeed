import QtQuick
import QtQuick.Layouts
import "../themes"

// Rich, icon-led section separator used inside the merged settings pages.
// Renders a ROUNDED-SQUARE colored icon tile + bold title (+ optional subtitle),
// matching the Telegram Desktop "grouped settings" look. RTL-safe.
//
// Usage:
//   SettingsSectionHeader {
//       width: parent.width
//       iconName: "user"; tileColor: "#3390ec"
//       title: qsTr("Account"); subtitle: qsTr("Telegram repost target")
//   }
Item {
    id: sh

    property string iconName: ""
    property string title: ""
    property string subtitle: ""
    property color tileColor: Theme.accent

    width: parent ? parent.width : 360
    implicitHeight: rowL.implicitHeight
    height: implicitHeight

    RowLayout {
        id: rowL
        width: parent.width
        spacing: 12
        LayoutMirroring.enabled: Theme.rtl

        Rectangle {
            Layout.preferredWidth: 34
            Layout.preferredHeight: 34
            Layout.alignment: Qt.AlignTop
            radius: Theme.radius.md
            color: sh.tileColor
            Icon {
                anchors.centerIn: parent
                name: sh.iconName
                size: 19
                color: "#ffffff"
            }
        }

        ColumnLayout {
            Layout.fillWidth: true
            Layout.alignment: Qt.AlignVCenter
            spacing: 2

            Text {
                Layout.fillWidth: true
                text: sh.title
                color: Theme.text
                font.family: Theme.fontFamily
                font.pixelSize: 15
                font.bold: true
                elide: Text.ElideRight
                horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
            }

            Text {
                visible: sh.subtitle !== ""
                Layout.fillWidth: true
                text: sh.subtitle
                color: Theme.textSecondary
                font.family: Theme.fontFamily
                font.pixelSize: 12
                wrapMode: Text.WordWrap
                horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
            }
        }
    }
}
