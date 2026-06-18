import QtQuick
import QtQuick.Layouts
import "../themes"

// One Telegram-style settings row: SVG icon + label (+ optional value text and
// a chevron), with hover and selection states driven entirely by the Theme
// singleton. Reused for the root section list and as a navigable button row
// inside detail pages. RTL-safe via LayoutMirroring + Theme.rtl.
Item {
    id: row

    property string iconName: ""
    property string label: ""
    property string value: ""        // optional right-aligned value text
    property bool showChevron: false
    property bool selected: false

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
        spacing: 16
        LayoutMirroring.enabled: Theme.rtl

        Icon {
            visible: row.iconName !== ""
            name: row.iconName
            size: 22
            color: row.selected ? Theme.accentText : Theme.accent
            Layout.alignment: Qt.AlignVCenter
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
        anchors.leftMargin: 54
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
