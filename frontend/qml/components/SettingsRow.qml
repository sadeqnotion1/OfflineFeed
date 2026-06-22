import QtQuick
import QtQuick.Layouts
import "../themes"

// One Telegram-style settings row: a ROUNDED-SQUARE colored icon tile + label
// (+ optional value text and a chevron), with hover and selection states driven
// entirely by the Theme singleton. Reused for the root section list and as a
// navigable button row inside detail pages. RTL-safe via LayoutMirroring + Theme.rtl.
//
// CHANGE vs original: the bare Icon is now wrapped in a rounded-square colored
// tile (Telegram Desktop style). Callers may set `tileColor` per row; it
// defaults to Theme.accent so any existing usage keeps working.
Item {
    id: row

    property string iconName: ""
    property string label: ""
    property string value: ""        // optional right-aligned value text
    property bool showChevron: false
    property bool selected: false
    property color tileColor: Theme.accent   // NEW: rounded-square icon tile color

    signal clicked()

    width: ListView.view ? ListView.view.width : 360
    height: 56

    Rectangle {
        anchors.fill: parent
        color: row.selected ? Theme.selection
                            : (mouse.containsMouse ? Theme.hover : "transparent")
        Behavior on color { ColorAnimation { duration: Theme.animFast } }
    }

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 16
        anchors.rightMargin: 16
        spacing: 14
        LayoutMirroring.enabled: Theme.rtl

        // NEW: Telegram-style rounded-square colored icon tile.
        Rectangle {
            visible: row.iconName !== ""
            Layout.preferredWidth: 30
            Layout.preferredHeight: 30
            Layout.alignment: Qt.AlignVCenter
            radius: Theme.radius.md
            color: row.tileColor
            Icon {
                anchors.centerIn: parent
                name: row.iconName
                size: 18
                color: "#ffffff"
            }
        }

        Text {
            Layout.fillWidth: true
            text: row.label
            color: row.selected ? Theme.accentText : Theme.text
            font.family: Theme.fontFamily
            font.pixelSize: 15
            elide: Text.ElideRight
            horizontalAlignment: Theme.rtl ? Text.AlignRight : Text.AlignLeft
        }

        Text {
            visible: row.value !== ""
            text: row.value
            color: row.selected ? Theme.accentText : Theme.textSecondary
            font.family: Theme.fontFamily
            font.pixelSize: 14
            elide: Text.ElideRight
            Layout.maximumWidth: 160
        }

        Icon {
            visible: row.showChevron
            name: "chevron"
            size: 16
            rotation: Theme.rtl ? 180 : 0
            color: Theme.textSecondary
            Layout.alignment: Qt.AlignVCenter
        }
    }

    Rectangle {
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.leftMargin: 60
        height: 1
        color: Theme.divider
        opacity: 0.5
    }

    MouseArea {
        id: mouse
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: row.clicked()
    }
}
